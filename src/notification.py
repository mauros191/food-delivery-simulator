from __future__ import annotations
from dataclasses import dataclass, field
from delivery import (
    Action,
    Delivery,
    Direction,
    OrderInstruction,
    RestaurantInstruction,
)
from geo.models import Position
from models import Bundle, Order, Restaurant
from typing import TYPE_CHECKING, List


if TYPE_CHECKING:
    from rider import Rider


@dataclass
class Notification:
    pass


# Notification from RIDER
@dataclass
class NotificationFromRider(Notification):
    rider: Rider = field(init=False)

    def set_rider(self, r: Rider):
        self.rider = r


@dataclass
class GoOnlineNotification(NotificationFromRider):
    pass


@dataclass
class GoOfflineNotification(NotificationFromRider):
    pass


@dataclass
class DeliveryCompleted(NotificationFromRider):
    delivery: Delivery


# Notification from SYSTEM
@dataclass
class NotificationFromSystem(Notification):
    rider: Rider
    response: bool = field(init=False)

    def accept(self) -> None:
        self.response = True

    def reject(self) -> None:
        self.response = False


class DeliveryNotification(NotificationFromSystem):
    def __init__(self, rider: Rider, content: Order | Bundle) -> None:
        self.rider: Rider = rider
        self.delivery: Delivery = Delivery(rider.id, content)

        if type(content) is Order:
            content.waiting_reply = 1

    def accept(self, time: int, position: Position) -> None:
        super().accept()

        # Update delivery information
        self.delivery.accept_at = time
        self.delivery.accepted_from = position

        # Add instruction
        self.delivery.add_instruction(
            RestaurantInstruction(self.delivery.content.restaurant)
        )

        if type(self.delivery.content) is Order:
            self.delivery.add_instruction(
                OrderInstruction(self.delivery.content, Action.PICKUP)
            )
            self.delivery.add_instruction(
                RestaurantInstruction(self.delivery.content.restaurant, Direction.EXIT)
            )
            self.delivery.add_instruction(
                OrderInstruction(self.delivery.content, Action.DROPOFF)
            )

        elif type(self.delivery.content) is Bundle:
            for o in sorted(self.delivery.content.orders, key=lambda f: f.ready_time):
                self.delivery.add_instruction(OrderInstruction(o, Action.PICKUP))

            self.delivery.add_instruction(
                RestaurantInstruction(self.delivery.content.restaurant, Direction.EXIT)
            )

            for o in self.delivery.content.orders:
                self.delivery.add_instruction(OrderInstruction(o, Action.DROPOFF))

        else:
            raise TypeError("Accept DeliveryNotification TypeError")


class UpdateDeliveryNotification(NotificationFromSystem):
    def __init__(self, rider: Rider, content: Bundle) -> None:
        self.rider: Rider = rider
        self.content: Bundle = content

    def accept(self) -> None:
        super().accept()

        if self.rider.queue_delivery is not None:
            raise Exception("A rider with busy queue cannot receive UpdateNotification")

        # Set delivery
        delivery: Delivery = self.rider.delivery

        # Update bundle
        delivery.content = self.content

        # Set new free_at
        self.rider.set_free_at()

        # Remove OrderInstruction with Action.dropoff and RestaurantInstraction with Direction.EXIT
        INDEX_DEL = -1

        for i, j in enumerate(delivery.instructions):
            if type(j) is RestaurantInstruction and j.direction == Direction.EXIT:
                INDEX_DEL = i

        if INDEX_DEL == -1:
            raise Exception("No RestaurantInstruction found in Update!")
        else:
            del delivery.instructions[INDEX_DEL:]

        # Add OrderInstruction PICKUP for new orders
        for o in delivery.content.orders:
            if OrderInstruction(o, action=Action.PICKUP) not in delivery.instructions:
                delivery.instructions.append(OrderInstruction(o, action=Action.PICKUP))

        # Add RestaurantInstruction with Direction.EXIT
        delivery.instructions.append(
            RestaurantInstruction(delivery.restaurant, Direction.EXIT)
        )

        # Add Action.dropoff
        for o in delivery.content.orders:
            delivery.instructions.append(OrderInstruction(o, action=Action.DROPOFF))

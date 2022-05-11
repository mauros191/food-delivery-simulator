from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from geo.models import Position
from models import Bundle, Order, Restaurant
from typing import ClassVar, List, TYPE_CHECKING

if TYPE_CHECKING:
    from rider import Rider


class Instruction:
    pass


class Action(Enum):
    PICKUP = 1
    DROPOFF = 2


@dataclass
class OrderInstruction(Instruction):
    order: Order
    action: Action


class Direction(Enum):
    GO = 1
    EXIT = 2


@dataclass
class RestaurantInstruction(Instruction):
    restaurant: Restaurant
    direction: Direction = Direction.GO


@dataclass
class Delivery:
    rider_id: int
    content: Order | Bundle
    id: int = field(init=False)
    instructions: List[Instruction] = field(default_factory=lambda: list())
    accept_at: int = -1
    accepted_from: Position = Position()
    start_at: int = -1
    start_from: Position = Position()
    pickup_at: int = -1
    exp_at_restaurant: int = -1
    leave_restaurant_at: int = -1
    at_restaurant: int = -1
    completed_at: int = -1
    wait_time: int = 0
    COUNTER: ClassVar[int] = 1

    def __hash__(self):
        return hash(self.id)

    @property
    def bundle(self):
        if type(self.content) is Bundle:
            return self.content
        else:
            raise ValueError("Delivery contain Order")

    @property
    def order(self):
        if type(self.content) is Order:
            return self.content
        else:
            raise ValueError("Delivery contain Bundle")

    @property
    def restaurant(self):
        return self.content.restaurant

    @property
    def leave_restaurant(self) -> bool:
        if type(self.content) is Order:
            if self.content.pickup_at != -1:
                return True

        elif type(self.content) is Bundle:
            for o in self.content.orders:
                if o.pickup_at != -1:
                    return True

        return False

    def is_queue(self):
        if self.accept_at + 1 != self.start_at:
            return True
        else:
            return False

    def start(self, t: int, p: Position) -> None:
        self.start_at = t
        self.start_from = p

    def __post_init__(self):
        self.id = Delivery.COUNTER
        Delivery.COUNTER += 1

    def add_instruction(self, i: Instruction) -> None:
        self.instructions.append(i)

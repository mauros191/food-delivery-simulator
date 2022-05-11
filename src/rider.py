import config.config as config
from config.utils import MovementStrategy, MovementType
from events.manager import LaunchFunctionIn
import events.manager as EventManager
import random
import system.manager as SystemManager
import log.build as BuildLog
from delivery import Action, Direction, Instruction, RestaurantInstruction
from dataclasses import dataclass, field
from geo.models import Position, PositionTime
from models import NotificationStatus, Order, Restaurant, Status
from notification import *
from system.system import System
from typing import List
import algorithms.utils as AlgUtils
import area.area as AreaManager


@dataclass
class Rider:
    id: int
    position_at_start: Position
    start_in_seconds: int
    end_in_seconds: int
    positions: List[PositionTime] = field(init=False)
    current_delivery: Delivery | None = None
    queue_delivery: Delivery | None = None
    delivery_completed: List[Delivery] = field(default_factory=lambda: list())
    free_at_position_: PositionTime | None = None
    P_N: float = config.P_N
    P_M: float = config.P_M
    status: Status = Status.IDLE
    status_notification: NotificationStatus = NotificationStatus.OFF
    checksum: int = 0

    def __post_init__(self):
        random.seed(config.SEED)

    ##############################
    # 		  PROPERTY	         #
    ##############################

    @property
    def delivery(self) -> Delivery:
        if self.current_delivery is None:
            raise TypeError(f"Delivery of Rider {self.id} is None")
        return self.current_delivery

    @property
    def qdelivery(self) -> Delivery:
        if self.queue_delivery is None:
            raise TypeError(f"QueueDelivery of Rider {self.id} is None")
        return self.queue_delivery

    @property
    def free_at_position(self) -> PositionTime:
        if self.free_at_position_ is None:
            raise TypeError(f"FreeAtPosition of Rider {self.id} is None")
        return self.free_at_position_

    @property
    def position(self) -> Position:
        if len(self.positions) == 0:
            raise ValueError("The rider position history is empty")
        return self.positions[-1].position

    @property
    def instruction(self) -> Instruction:
        if len(self.delivery.instructions) == 0:
            raise ValueError("Delivery instructions is empty")
        return self.delivery.instructions.pop(0)

    ##############################
    # 		 ONLINE/OFFLINE	     #
    ##############################

    def go_online(self) -> None:
        self.positions = [PositionTime(self.position_at_start, self.start_in_seconds)]
        n: GoOnlineNotification = GoOnlineNotification()
        self.send(n)

        if config.MOVEMENT_TYPE == MovementType.RANDOM:
            if config.MOVEMENT_STRATEGY == MovementStrategy.B:
                self.random_movement(1)
            else:
                self.random_movement()

        elif config.MOVEMENT_TYPE == MovementType.MAP:
            self.follow_map()

    def go_offline(self) -> None:
        n: GoOfflineNotification = GoOfflineNotification()
        self.send(n)

    ##############################
    # 		  NOTIFICATION	     #
    ##############################

    def send(self, n: Notification) -> None:
        if isinstance(n, NotificationFromRider):
            n.set_rider(self)
        SystemManager.update(n)

    # REQUEST
    def update(self, n: NotificationFromSystem) -> None:
        if type(n) is DeliveryNotification:
            System.log(BuildLog.receive_delivery(n))
            self.status_notification = NotificationStatus.ON
            reply_in: int = random.randint(5, 29)
            LaunchFunctionIn(self.reply_delivery_notification, n, seconds=reply_in)

        elif type(n) is UpdateDeliveryNotification:
            System.log(BuildLog.receive_update(n))
            self.reply_update_notification(n)

        else:
            raise Exception("Update rider")

    # ACCEPT
    def accept_delivery(self, n: DeliveryNotification) -> None:
        n.accept(System.TIME, self.position)
        self.update_position()
        self.checksum = System.TIME
        self.status = Status.BUSY

    # RESPONSE UPDATE NOTIFICATION
    def reply_update_notification(self, n: UpdateDeliveryNotification) -> None:
        r: float = random.uniform(0, 1)

        if r <= self.P_N:
            n.accept()
            self.send(n)

        else:
            n.reject()
            self.send(n)

    # RESPONSE DELIVERY NOTIFICATION
    def reply_delivery_notification(self, n: DeliveryNotification) -> None:
        r: float = random.uniform(0, 1)

        if r <= self.P_N:
            self.accept_delivery(n)

            # Set delivery
            if self.current_delivery is None:
                self.current_delivery = n.delivery
                LaunchFunctionIn(self.start_delivery)
            else:
                if self.queue_delivery is None:
                    self.queue_delivery = n.delivery
                else:
                    raise Exception(
                        "Try to assign a delivery to a rider with queue busy"
                    )

            self.send(n)

        else:
            n.reject()
            self.send(n)

        self.status_notification = NotificationStatus.OFF

    ##############################
    # 		  INSTRUCTION	     #
    ##############################

    def run_instruction(self) -> None:
        i: Instruction = self.instruction

        if type(i) is RestaurantInstruction:
            if i.direction is Direction.GO:
                self.to_restaurant(i.restaurant)
            else:
                # Exit from restaurant
                self.delivery.pickup_at = System.TIME
                self.deparking(i.restaurant)

        elif type(i) is OrderInstruction:
            if i.action is Action.PICKUP:
                if System.TIME < i.order.ready_time:
                    waiting_time: int = i.order.ready_time - System.TIME
                    System.log(BuildLog.wait(self, i.order, waiting_time))
                    self.delivery.wait_time += waiting_time
                    LaunchFunctionIn(self.pickup, i.order, seconds=waiting_time)
                else:
                    self.pickup(i.order)

            elif i.action is Action.DROPOFF:
                self.start_dropoff(i.order)

        else:
            raise Exception("Instruction unknown")

    ##############################
    # 		   ACTION	         #
    ##############################

    # Create MoveEvents and return the travel time
    def move(self, destination: Position) -> int:
        start: Position = self.position
        return EventManager.BuildMoveEvents(start, destination, self)

    def update_position(self) -> None:
        self.positions.append(PositionTime(self.position, System.TIME))

    def pickup(self, o: Order) -> None:
        # Update position
        self.update_position()

        # Pickup order
        o.pickup()

        # Log pickup
        System.log(BuildLog.pickup(self, o))

        # Go to the next instruction
        self.run_instruction()

    def dropoff(self, o: Order):
        # Update position
        self.update_position()

        # Drop-off order
        o.dropoff()

        # Log dropoff
        System.log(BuildLog.dropoff(self, o))

        # Deparking
        self.deparking(o)

    ##############################
    # 		   FREE_AT	         #
    ##############################

    def set_free_at(self) -> None:
        if config.ALGORITHM.value <= 3:
            AlgUtils.FAO(self, self.delivery.order)

        else:
            AlgUtils.FAB(self, self.delivery.bundle)

    # Update free_at
    def update_free_at(self) -> None:
        AlgUtils.FAB(self, self.delivery.bundle)

    def check_free_at(self) -> None:
        assert System.TIME + 1 == self.free_at_position.time
        assert self.position == self.free_at_position.position

    ##############################
    # 		   DELIVERY	         #
    ##############################

    def start_delivery(self) -> None:
        # Update position
        self.update_position()

        # Start delivery
        self.delivery.start(System.TIME, self.position)
        System.log(BuildLog.start_delivery(self.delivery, self))

        i: Instruction = self.instruction
        if type(i) is not RestaurantInstruction:
            raise TypeError("The delivery must start with RestaurantInstruction")
        self.to_restaurant(i.restaurant)

    def to_restaurant(self, r: Restaurant) -> None:
        System.log(BuildLog.start_travel(self, r))

        # Move to restaurant
        travel_time: int = self.move(r.position)

        # Set expected delivery at restaurant
        self.delivery.exp_at_restaurant = (
            System.TIME + travel_time + int(config.PST / 2)
        )

        # Set FREE_AT
        self.set_free_at()

        # Parking
        LaunchFunctionIn(self.parking, r, seconds=max(travel_time, 1))

    def at_restaurant(self, r: Restaurant) -> None:
        # Update position
        self.update_position()

        assert self.delivery.exp_at_restaurant == System.TIME

        self.delivery.at_restaurant = System.TIME
        System.log(f"RIDER {self.id} ARRIVED @ R{r.id} {(r.position.X, r.position.Y)}")

        # Go to the next instruction
        self.run_instruction()

    def start_dropoff(self, o: Order) -> None:
        # Update position
        self.update_position()

        System.log(BuildLog.start_travel(self, o))

        # Move to customer
        travel_time: int = self.move(o.customer.position)

        # Parking
        LaunchFunctionIn(self.parking, o, seconds=max(travel_time, 1))

    def continue_delivery(self) -> None:
        # Update position
        self.update_position()

        if len(self.delivery.instructions) == 0:
            self.complete_delivery()
        else:
            self.run_instruction()

    def complete_delivery(self) -> None:
        # Update position
        self.update_position()

        System.log(f"RIDER {self.id} COMPLETED DELIVERY {self.delivery.id}")

        # Check FREE_AT
        self.check_free_at()

        # Reset FREE_AT
        self.free_at_position_ = None

        # Send DeliveryCompleted notification
        self.send(DeliveryCompleted(self.delivery))
        self.current_delivery = None

        # Continue with other delivery if queue is not empty
        if self.queue_delivery is not None:
            self.current_delivery, self.queue_delivery = (
                self.queue_delivery,
                self.current_delivery,
            )
            LaunchFunctionIn(self.start_delivery)

        else:
            self.status = Status.IDLE

            if config.MOVEMENT_TYPE == MovementType.RANDOM:
                if config.MOVEMENT_STRATEGY == MovementStrategy.B:
                    self.random_movement(1)
                else:
                    self.random_movement()

            elif config.MOVEMENT_TYPE == MovementType.MAP:
                self.follow_map()

    ##############################
    # 	   PARKING/DEPARKING     #
    ##############################

    def parking(self, place: Restaurant | Order):
        if type(place) is Restaurant:
            System.log(BuildLog.parking(self, place))
            LaunchFunctionIn(self.at_restaurant, place, seconds=int(config.PST / 2))
        else:
            System.log(BuildLog.parking(self, place))
            LaunchFunctionIn(self.dropoff, place, seconds=int(config.DST / 2))

    def deparking(self, place: Restaurant | Order):
        if type(place) is Restaurant:
            System.log(BuildLog.deparking(self, place))
            LaunchFunctionIn(self.run_instruction, seconds=int(config.PST / 2))
        else:
            System.log(BuildLog.deparking(self, place))
            LaunchFunctionIn(self.continue_delivery, seconds=int(config.DST / 2))

    ##############################
    # 	     FREE MOVEMENT       #
    ##############################

    def random_movement(self, probability: float = config.P_M) -> None:
        if System.TIME < self.end_in_seconds and self.status == Status.IDLE:
            r: float = random.uniform(0, 1)

            if r < probability:
                self.status = Status.FREE_MOVEMENT
                random_position = AreaManager.random_point(self.position)

                # Create FreeMoveEvents and route
                end_at = EventManager.BuildFreeMoveEvents(
                    self.position, random_position, self, self.checksum
                )
                LaunchFunctionIn(self.random_movement, seconds=end_at)

            else:
                sleep_for = max(1, int(random.gauss(6, 2) * 60))
                System.log(BuildLog.hold_position(self.id, sleep_for, System.TIME))
                LaunchFunctionIn(self.random_movement, seconds=sleep_for)

    ##############################
    # 	         MAP             #
    ##############################
    def follow_map(self, l: bool = False) -> None:
        if System.TIME < self.end_in_seconds and self.status == Status.IDLE:
            if not l:
                destination: Position = AreaManager.give_me_direction(self.position)
                self.status = Status.FREE_MOVEMENT
                end_at = EventManager.BuildFreeMoveEvents(
                    self.position, destination, self, self.checksum
                )
                LaunchFunctionIn(self.follow_map, True, seconds=end_at)

            else:
                r: float = random.uniform(0, 1)

                if r < config.P_M:
                    destination: Position = AreaManager.give_me_direction(self.position)
                    self.status = Status.FREE_MOVEMENT
                    end_at = EventManager.BuildFreeMoveEvents(
                        self.position, destination, self, self.checksum
                    )
                    LaunchFunctionIn(self.follow_map, True, seconds=end_at)

                else:
                    sleep_for = max(1, int(random.gauss(6, 2) * 60))
                    System.log(BuildLog.hold_position(self.id, sleep_for, System.TIME))
                    LaunchFunctionIn(self.follow_map, True, seconds=sleep_for)

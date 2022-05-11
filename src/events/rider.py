from __future__ import annotations
from events.event import Event
from geo.models import Position, PositionTime
from models import Status
from system.system import System
from typing import TYPE_CHECKING
import config.config as config
import log.build as BuildLog

if TYPE_CHECKING:
    from rider import Rider


class MoveEvent(Event):
    def __init__(self, rider: Rider, position: Position) -> None:
        self.rider: Rider = rider
        self.position: Position = position
        self.priority: int = 2

    def run(self) -> None:
        # Previous position
        previous_position: Position = self.rider.position

        # Add new position
        self.rider.positions.append(PositionTime(self.position, self.time))

        # Log
        if config.LOG_MOVE:
            System.log(BuildLog.move(self.rider.id, previous_position, self.position))


class RiderGoOnlineEvent(Event):
    def __init__(self, rider: Rider) -> None:
        self.rider: Rider = rider
        self.schedule_for(rider.start_in_seconds)
        self.priority: int = 2

    def run(self) -> None:
        self.rider.go_online()


class RiderGoOfflineEvent(Event):
    def __init__(self, rider: Rider) -> None:
        self.rider: Rider = rider
        self.schedule_for(rider.end_in_seconds)
        self.priority: int = 2

    def run(self) -> None:
        self.rider.go_offline()


class FreeMoveEvent(MoveEvent):
    def __init__(
        self,
        rider: Rider,
        position: Position,
        checksum: int,
        change_status: bool = False,
    ) -> None:
        self.rider: Rider = rider
        self.position: Position = position
        self.priority: int = 2
        self.checksum: int = checksum
        self.change_status: bool = change_status

    def run(self) -> None:
        if (
            self.rider.checksum == self.checksum
            and self.time < self.rider.end_in_seconds
        ):
            # Previous position
            previous_position: Position = self.rider.position

            # Add new position
            self.rider.positions.append(
                PositionTime(self.position, self.time, free_movement=True)
            )

            # Log
            if config.LOG_MOVE:
                System.log(
                    BuildLog.free_move(self.rider.id, previous_position, self.position)
                )

            # Change status
            if self.change_status:
                self.rider.status = Status.IDLE

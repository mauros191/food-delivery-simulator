import config.config as config
from system.system import System
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Event(ABC):
    time: int = -1
    priority: int = 1

    @abstractmethod
    def run(self) -> None:
        pass

    # Schedule event into the timeline at time
    def schedule_for(self, time: int) -> None:
        if time <= System.TIME:
            raise ValueError("Time of event is <= System.TIME")
        elif time > config.MAX_TIME:
            raise ValueError("Time of event is > MAX_TIME")

        # Set time
        self.time = time

        # Add event
        System.add_event(self)

    # Schedule event into the timeline in dtime
    def schedule_in(self, dtime: int) -> None:
        current_time = System.TIME
        if current_time + dtime > config.MAX_TIME:
            raise ValueError("Time of event is > MAX_TIME")
        if dtime <= 0:
            raise ValueError("dtime must be > 0")

        # Set time
        self.time = current_time + dtime

        # Add event
        System.add_event(self)

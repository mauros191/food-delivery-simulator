from __future__ import annotations
from typing import List, TYPE_CHECKING
from config.utils import AlgorithmType
from config.utils import SimulatorSpeed
from threading import Thread
import config.config as config
import log.log as Log
import time
import utils
import sys


if TYPE_CHECKING:
    from algorithms.algorithm import Algorithm
    from events.event import Event


class System:
    TIME: int = -1
    EVENTS: dict[int, List[Event]] = {}
    ALGORITHM: Algorithm
    VALUE_VARIABLE_SPEED: int = 1

    @staticmethod
    def run() -> None:
        # Set speed simulator
        set_speed_simulator()

        # Init
        System.TIME += 1

        # Run
        while System.TIME <= config.MAX_TIME:
            # Sort events for priority (from MAX to MIN)
            System.EVENTS[System.TIME].sort(key=lambda f: f.priority, reverse=True)

            # Run Events
            for e in System.EVENTS[System.TIME]:
                e.run()

            # Run Algorithm
            System.ALGORITHM.set_time(System.TIME)

            if System.ALGORITHM.type == AlgorithmType.SIMPLE_DISPATCH:
                if System.TIME % 10 == 0:
                    System.ALGORITHM.run()

            else:
                if System.TIME % config.F == 0 or (
                    System.ALGORITHM.retryBool and System.TIME % 30 == 0
                ):
                    System.ALGORITHM.run()

            # Increase counter
            System.TIME += 1

            # Speed of simulator
            if config.SPEED != SimulatorSpeed.MAX:
                if config.SPEED == SimulatorSpeed.VARIABLE:
                    time.sleep(1 / System.VALUE_VARIABLE_SPEED)
                else:
                    raise TypeError("SimulatorSpeed TypeError")

        # Show log after simulation if log is enabled and real_time is disabled
        if config.SHOW_LOG and not config.LOG_REAL_TIME:
            Log.show_after_simulation()

        # Stop thread
        if config.SPEED is SimulatorSpeed.VARIABLE:
            sys.exit()

    @staticmethod
    def add_event(e: Event) -> None:
        System.EVENTS[e.time].append(e)

    @staticmethod
    def log(event: str) -> None:
        time = utils.show_time(System.TIME)
        msg: str = f"[{time}] {event}"

        # Show log in real time
        if config.SHOW_LOG and config.LOG_REAL_TIME:
            Log.show(msg)

        # Save log
        Log.save(msg)


# Set simulator speed
def set_speed_simulator() -> Thread | None:
    if config.SPEED == SimulatorSpeed.VARIABLE:
        from blessed import Terminal

        term = Terminal()

        def func():
            while True:
                with term.cbreak():
                    inp = term.inkey()
                    config.SPEED = SimulatorSpeed.VARIABLE
                    if inp.name == "KEY_UP":
                        System.VALUE_VARIABLE_SPEED *= 2
                    elif inp.name == "KEY_DOWN":
                        if System.VALUE_VARIABLE_SPEED > 0:
                            System.VALUE_VARIABLE_SPEED = max(
                                1, int(System.VALUE_VARIABLE_SPEED / 2)
                            )
                    elif inp.name == "KEY_RIGHT":
                        config.SPEED = SimulatorSpeed.MAX
                    elif inp.name == "KEY_LEFT":
                        System.VALUE_VARIABLE_SPEED = 1

        t: Thread = Thread(target=func)
        t.daemon = True
        t.start()
        return t

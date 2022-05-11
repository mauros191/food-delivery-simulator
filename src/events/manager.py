from __future__ import annotations
from config.utils import DistanceType
from events.event import Event
from events.rider import FreeMoveEvent, MoveEvent
from geo.models import Position, RealPosition, Route, SimplePosition
from system.system import System
from typing import TYPE_CHECKING
import geo.manager as GeoManager
from utils import show_time
import config.config as config

if TYPE_CHECKING:
    from rider import Rider


# Launch function after some time (default 1 second)
class LaunchFunctionIn(Event):
    def __init__(self, func, *args, seconds: int = 1) -> None:
        self.func = func
        self.args = list(args)
        self.schedule_in(seconds)

    def run(self) -> None:
        self.func(*self.args)

    def __repr__(self) -> str:
        return f"LaunchFunctionIn(time={self.time}, priority={self.priority}, func={self.func}"


# Build events of type MoveEvent and return the time at destination
def BuildMoveEvents(start: Position, end: Position, rider: Rider) -> int:
    t_start: int = System.TIME

    if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
        t_end: int = t_start + GeoManager.travel_time(start, end)

    elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
        t_end: int = t_start + GeoManager.travel_time(start, end, True)

    else:
        raise Exception("BuildMoveEvents error")

    if t_end - t_start > 0:
        route: Route = GeoManager.generate_route(start, end, t_start, t_end)

        # Create MoveEvent(s)
        for s in route.stops:
            m: MoveEvent = MoveEvent(rider, s.position)
            m.schedule_for(s.time)

    return t_end - t_start


# Build events of type MoveEvent and return the time at destination
def BuildFreeMoveEvents(
    start: Position, end: Position, rider: Rider, checksum: int
) -> int:
    t_start: int = System.TIME

    if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
        t_end: int = t_start + GeoManager.travel_time(start, end)

    elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
        t_end: int = t_start + GeoManager.travel_time(start, end, True)

    else:
        raise Exception("BuildFreeMoveEvents error")

    if t_end - t_start > 0:
        route: Route = GeoManager.generate_route(start, end, t_start, t_end)

        # Create MoveEvent(s)
        N: int = len(route.stops)
        for i, s in enumerate(route.stops):
            if i != N - 1:
                m: FreeMoveEvent = FreeMoveEvent(rider, s.position, checksum)
            else:
                m: FreeMoveEvent = FreeMoveEvent(
                    rider, s.position, checksum, change_status=True
                )
            m.schedule_for(s.time)

    return t_end - t_start

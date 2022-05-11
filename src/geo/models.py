from dataclasses import dataclass, field
from geojson import Point, Feature
from typing import List, Tuple
import config.config as config
import utm


class Position:
    x: int
    y: int
    area: Tuple = field(init=False)

    @property
    def X(self) -> int:
        return -1

    @property
    def Y(self) -> int:
        return -1

    def set_area(self) -> None:
        pass


@dataclass
class SimplePosition(Position):
    x: int
    y: int

    @property
    def X(self) -> int:
        return self.x

    @property
    def Y(self) -> int:
        return self.y

    def set_area(self) -> None:
        x: int = int(self.x / config.DIM_AREA)
        y: int = int(self.y / config.DIM_AREA)
        self.area = (x, y)


@dataclass
class RealPosition(Position):
    latitude: float
    longitude: float
    x: int = -1
    y: int = -1
    x_utm: int = -1
    y_utm: int = -1
    point: Feature = field(init=False)

    def __post_init__(self) -> None:
        self.point = Feature(geometry=Point([self.longitude, self.latitude]))
        if self.x != -1 and self.y != -1:
            self.x_utm = (
                config.START_POINTS[config.INSTANCE_GRUBHUB]["START_X"] + self.x
            )
            self.y_utm = (
                config.START_POINTS[config.INSTANCE_GRUBHUB]["START_Y"] + self.y
            )

    def set_utm(self) -> None:
        if self.x == -1 and self.y == -1:
            C_UTM = utm.from_latlon(self.latitude, self.longitude)
            self.x_utm = int(C_UTM[0])
            self.y_utm = int(C_UTM[1])
            self.x = (
                self.x_utm - config.START_POINTS[config.INSTANCE_GRUBHUB]["START_X"]
            )
            self.y = (
                self.y_utm - config.START_POINTS[config.INSTANCE_GRUBHUB]["START_Y"]
            )

            if self.x == -1:
                self.x = 0

            if self.y == -1:
                self.y = 0

            if self.x < 0 or self.x > config.MAX_X:
                raise Exception("set_utm: x < 0 or x > config.MAX_X")
            if self.y < 0 or self.y > config.MAX_Y:
                raise Exception("set_utm: y < 0 or y > config.MAX_Y")

    def set_area(self) -> None:
        self.set_utm()
        x: int = int(self.x / config.DIM_AREA)
        y: int = int(self.y / config.DIM_AREA)
        self.area = (x, y)

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    @property
    def X(self) -> float:
        return self.latitude

    @property
    def Y(self) -> float:
        return self.longitude


@dataclass
class PositionTime:
    position: Position
    time: int
    free_movement: bool = False


@dataclass
class Route:
    stops: List[PositionTime] = field(default_factory=lambda: list())

    def insert(self, p: PositionTime) -> None:
        self.stops.append(p)

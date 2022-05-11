from config.utils import DistanceType
from data import Data
from dataclasses import dataclass, field
from geo.models import Position, RealPosition, SimplePosition
from models import Order
from typing import List, Tuple
import config.config as config
import geo.manager as GeoManager
from system.system import System
import random
import math


@dataclass
class Area:
    area: Tuple[int, int]
    value: int = 0
    position: Position = field(init=False)

    def __post_init__(self) -> None:
        x: int = self.area[0] * 1000 + int(config.DIM_AREA / 2)
        y: int = self.area[1] * 1000 + int(config.DIM_AREA / 2)

        if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
            self.position = SimplePosition(x, y)

        elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
            real_pos: RealPosition = GeoManager.generate_real_position(x, y)
            real_pos.set_utm()
            self.position = real_pos

    def increase(self) -> None:
        self.value += 1

    def reset(self) -> None:
        self.value = 0


def reset():
    for b in Data.RECOMMENDED_AREAS:
        b.reset()

    for b in Data.RECOMMENDED_AREAS:
        assert b.value == 0


def init():
    for r in Data.RESTAURANTS:
        area: Tuple[int, int] = r.area
        found = False

        for b in Data.RECOMMENDED_AREAS:
            if b.area == area:
                found = True
                b.increase()

        if not found:
            b: Area = Area(area)
            b.increase()
            Data.RECOMMENDED_AREAS.append(b)

    count = 0
    for b in Data.RECOMMENDED_AREAS:
        count += b.value

    assert count == len(Data.RESTAURANTS)


def add_order(o: Order) -> None:
    area: Tuple[int, int] = o.restaurant.area

    found = False
    for b in Data.RECOMMENDED_AREAS:
        if b.area == area:
            b.increase()
            found = True

    if not found:
        raise Exception("Area not found")


def is_in_restaurant_area(p: Position) -> bool:
    for b in Data.RECOMMENDED_AREAS:
        if b.area == p.area:
            return True

    return False


def nearest_restaurant_area(p: Position) -> Position:
    shortest_d: float = config.OMEGA
    n_rest: int = -1
    i_best_area: int = -1

    for (i, a) in enumerate(Data.RECOMMENDED_AREAS):
        d: float = GeoManager.straight_line_distance(p, a.position)
        if d < shortest_d:
            shortest_d = d
            n_rest: int = Data.RECOMMENDED_AREAS[i].value
            i_best_area = i

    for (i, a) in enumerate(Data.RECOMMENDED_AREAS):
        d: float = GeoManager.straight_line_distance(p, a.position)
        if abs(d - shortest_d) < 200:
            if Data.RECOMMENDED_AREAS[i].value > n_rest:
                n_rest: int = Data.RECOMMENDED_AREAS[i].value
                i_best_area = i

    return Data.RECOMMENDED_AREAS[i_best_area].position


def random_point(p: Position) -> Position:
    found: bool = False

    if type(p) is SimplePosition:
        random_position = SimplePosition(p.x, p.y)

    elif type(p) is RealPosition:
        p.set_utm()
        random_position = SimplePosition(p.x, p.y)

    else:
        raise Exception("WTF?")

    original_position = SimplePosition(p.x, p.y)

    while not found:
        random_distance: float = random.uniform(
            config.D_min_r * 1000, config.D_max_r * 1000
        )
        random_teta: float = random.uniform(0, 2 * math.pi)
        dx: int = round(random_distance * math.cos(random_teta))
        dy: int = round(random_distance * math.sin(random_teta))

        if (
            config.MIN_X <= original_position.x + dx <= config.MAX_X
            and config.MIN_Y <= original_position.y + dy <= config.MAX_Y
        ):
            found = True
            random_position.x += dx
            random_position.y += dy

    if random_position.x > config.MAX_X:
        assert 1 == 2
    if random_position.x < config.MIN_X:
        assert 1 == 2
    if random_position.y > config.MAX_Y:
        assert 1 == 2
    if random_position.y < config.MIN_Y:
        assert 1 == 2

    if type(p) is SimplePosition:
        return random_position

    elif type(p) is RealPosition:
        return GeoManager.generate_real_position(random_position.x, random_position.y)

    else:
        raise Exception("WTF?")


def good_position(p: Position) -> Position:
    N = 25
    while N >= 0:
        r_point: Position = random_point(p)
        r_point.set_area()

        for a in Data.RECOMMENDED_AREAS:
            if a.area == r_point.area:
                return r_point

        N -= 1

    r_point: Position = random_point(p)
    return r_point


def good_area(p: Position) -> Position:
    if System.TIME < config.CHECK_AREA_EVERY_MIN:
        raise Exception("Good area only after 60 minutes")

    AREA: List[Area] = []

    for a in Data.RECOMMENDED_AREAS:
        if GeoManager.straight_line_distance(p, a.position) <= config.D_max:
            if a.value > 0:
                AREA.append(a)

    if len(AREA) > 0:
        area = random.choices(AREA, weights=[a.value for a in AREA])[0]
        if p.area == area.area:
            return good_position(p)

        else:
            return area.position

    else:
        return good_position(p)


def give_me_direction(p: Position) -> Position:
    p.set_area()

    if not is_in_restaurant_area(p):
        return nearest_restaurant_area(p)

    # BEFORE F_A
    if System.TIME < config.CHECK_AREA_EVERY_MIN:
        return good_position(p)

    # AFTER F_A
    else:
        return good_area(p)

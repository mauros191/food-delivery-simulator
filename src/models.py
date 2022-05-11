from dataclasses import dataclass, field
from config.utils import DistanceType
from geo.models import Position
from system.system import System
from typing import List, Set, Tuple
import algorithms.utils as AlgUtils
import config.config as config
import itertools
from enum import Enum


class Status(Enum):
    IDLE = 1
    BUSY = 2
    MOVEMENT = 3
    FREE_MOVEMENT = 4


class NotificationStatus(Enum):
    ON = 1
    OFF = 2


@dataclass
class Restaurant:
    id: int
    position: Position
    area: Tuple[int, int] = field(init=False)

    def __post_init__(self) -> None:
        x: int = int(self.position.x / config.DIM_AREA)
        y: int = int(self.position.y / config.DIM_AREA)
        self.area = (x, y)


@dataclass
class Customer:
    position: Position


@dataclass
class Order:
    id: int
    restaurant: Restaurant
    customer: Customer
    placement_time: int
    ready_time: int
    best_delivery_time: int = -1
    real_best_delivery_time: int = -1
    blacklist_riders: List[int] = field(default_factory=lambda: list())
    pickup_at: int = -1
    dropoff_at: int = -1
    cancel_at: int = -1
    waiting_reply: int = 0

    def pickup(self) -> None:
        if System.TIME < self.ready_time:
            raise Exception("Try to pickup order before ready_time")
        self.pickup_at = System.TIME

    def dropoff(self) -> None:
        if config.DISTANCE in [
            DistanceType.EUCLIDEAN,
            DistanceType.MANHATTAN,
            DistanceType.ROUTE,
        ]:
            if System.TIME < self.best_delivery_time:
                raise Exception("Order delivered before BDT")
            self.dropoff_at = System.TIME

        elif config.DISTANCE == DistanceType.HAVERSINE:
            if System.TIME < self.real_best_delivery_time:
                raise Exception("Order delivered before BDT")
            self.dropoff_at = System.TIME


@dataclass
class Bundle:
    id: str = ""
    orders: List[Order] = field(default_factory=lambda: list())

    def __repr__(self) -> str:
        return f"Bundle {self.id} with orders {[o.id for o in self.orders]}"

    def __post_init__(self) -> None:
        self.update_id()

    def __hash__(self):
        return hash(self.id)

    ##############################
    # 		  PROPERTY	         #
    ##############################

    @property
    def priority(self) -> int:
        if len(self.orders) == 0:
            raise ValueError("Bundle is empty. Priority error")
        return len(self.orders)

    @property
    def restaurant(self) -> Restaurant:
        if len(self.orders) > 0:
            return self.orders[0].restaurant
        else:
            raise ValueError("Bundle is empty. Restaurant property error")

    @property
    def ready_time(self) -> int:
        if len(self.orders) > 0:
            return max([o.ready_time for o in self.orders])
        else:
            raise ValueError("Bundle is empty. Ready time property error")

    @property
    def cost(self) -> int:
        if len(self.orders) > 0:
            return AlgUtils.BC(self)
        else:
            raise ValueError("No cost if bundle is empty")

    @property
    def size(self):
        if len(self.orders) == 0 or len(self.orders) > config.MAX_ORDERS_FOR_BUNDLE:
            raise Exception("Bundle size Exception")
        return len(self.orders)

    ##############################
    # 		    FUNC	         #
    ##############################

    def cost_at(self, position: int) -> int:
        if len(self.orders) > 0:
            order: Order = self.orders[position]
            return AlgUtils.OD(order, self)
        else:
            raise ValueError("No cost if bundle is empty")

    def check_bundle(self) -> None:
        set_restaurants: Set[int] = set([o.restaurant.id for o in self.orders])
        if len(set_restaurants) > 1:
            raise ValueError("Bundle composed of orders from different restaurants")
        if len(self.orders) > config.MAX_ORDERS_FOR_BUNDLE:
            raise ValueError("Bundle size exceeded")

    def find_index(self, o: Order) -> int:
        for i, v in enumerate(self.orders):
            if v == o:
                return i
        raise Exception(f"Order {o.id} not in bundle {self.id}")

    def update_id(self) -> None:
        for i, v in enumerate(self.orders):
            if i == 0:
                self.id = f"{v.id}"
            else:
                self.id += f"_{v.id}"

    def add_order(self, order: Order) -> None:
        self.orders.append(order)
        self.check_bundle()
        self.update_id()

    def add_orders(self, orders: List[Order]) -> None:
        self.orders += orders
        self.check_bundle()
        self.update_id()

    def set_best_perm(self) -> None:
        if len(self.orders) == 0:
            raise Exception("No best permutation if bundle is empty")
        if len(self.orders) >= 2:
            m_cost: int = self.cost

            for p in itertools.permutations(self.orders):
                b: Bundle = Bundle()
                b.add_orders(list(p))
                b_cost: int = b.cost
                if b_cost < m_cost:
                    self.orders = list(p)
                    m_cost = b_cost

            self.update_id()

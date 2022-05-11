from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from area.area import Area
    from delivery import Delivery
    from models import Order, Restaurant
    from rider import Rider


class Data:
    ORDERS: List[Order] = []
    ORDERS_ASSIGNED: List[Order] = []
    ORDERS_DELETED: List[Order] = []
    RIDERS: List[Rider] = []
    RESTAURANTS: List[Restaurant] = []
    DELIVERY: List[Delivery] = []
    DELIVERY_COMPLETED: List[Delivery] = []
    NO_RIDERS_AT: List[int] = []
    NO_RIDERS_FOR_O: Dict[int, List[Order]] = {}
    BLACKLIST_BUNDLE: Dict[int, List[str]] = {}
    RECOMMENDED_AREAS: List[Area] = []

    @staticmethod
    def clear() -> None:
        Data.ORDERS.clear()
        Data.ORDERS_ASSIGNED.clear()
        Data.ORDERS_DELETED.clear()
        Data.RIDERS.clear()
        Data.RESTAURANTS.clear()
        Data.DELIVERY.clear()
        Data.DELIVERY_COMPLETED.clear()
        Data.NO_RIDERS_AT.clear()
        Data.NO_RIDERS_FOR_O.clear()
        Data.BLACKLIST_BUNDLE.clear()
        Data.RECOMMENDED_AREAS.clear()

    @staticmethod
    def search_restaurant(id_rest: int) -> Restaurant:
        for r in Data.RESTAURANTS:
            if r.id == id_rest:
                return r

        raise ValueError("Restaurant searched by Data.search_restaurant not found")

from __future__ import annotations
from rider import Rider
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models import Order


class Dataset:
    TOTAL_ORDERS: List[Order] = []
    TOTAL_RIDERS: List[Rider] = []

    @staticmethod
    def clear() -> None:
        Dataset.TOTAL_ORDERS.clear()
        Dataset.TOTAL_RIDERS.clear()


def search_order(id_order: int) -> Order:
    for o in Dataset.TOTAL_ORDERS:
        if o.id == id_order:
            return o

    raise ValueError("Order searched by Dataset.search_order not found")


def search_rider(id_rider: int) -> Rider:
    for r in Dataset.TOTAL_RIDERS:
        if r.id == id_rider:
            return r

    raise ValueError("Rider searched by Dataset.search_rider not found")

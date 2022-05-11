from __future__ import annotations
from algorithms.algorithm import Algorithm
from config.utils import AlgorithmType
from data import Data
from models import Order
from notification import DeliveryNotification
from typing import TYPE_CHECKING, List
import algorithms.utils as AlgUtils
import config.config as config
import system.manager as SystemManager


if TYPE_CHECKING:
    from rider import Rider


class Greedy(Algorithm):
    def __init__(self):
        super().__init__(AlgorithmType.GREEDY)

    def run(self):
        super().run()

        # Clear excluded riders
        self.excluded_riders = []

        # Orders to check
        ORDERS: List[Order] = list(
            filter(lambda o: o.ready_time <= self.TIME + config.DELTA_U, Data.ORDERS)
        )

        # Sort Orders to check
        ORDERS.sort(key=lambda f: f.ready_time)

        for o in ORDERS:
            self.dispatch(o)

    def dispatch(self, o: Order) -> None:
        # Search rider with empty delivery
        R1 = [
            (r, AlgUtils.AR(o.restaurant, r, self.TIME))
            for r in Data.RIDERS
            if r not in self.excluded_riders
            and AlgUtils.IRN(o.restaurant, r)
            and r.id not in o.blacklist_riders
            and r.current_delivery is None
        ]

        R2 = []

        # Search rider with busy delivery but empty queue
        if config.QUEUE:
            R2 = [
                (r, AlgUtils.AR(o.restaurant, r, r.free_at_position))
                for r in Data.RIDERS
                if r not in self.excluded_riders
                and r.free_at_position_ is not None
                and AlgUtils.IRN(o.restaurant, r, r.free_at_position)
                and r.id not in o.blacklist_riders
                and r.current_delivery is not None
                and r.queue_delivery is None
            ]

        R = R1 + R2

        # Order by closest rider
        R.sort(key=lambda f: f[1])

        if len(R) > 0:
            # Rider selected
            r_selected = R[0][0]

            # Add r_selected to excluded_riders
            self.excluded_riders.append(r_selected)

            # Create and send notification
            notification = DeliveryNotification(r_selected, o)
            SystemManager.send(notification)

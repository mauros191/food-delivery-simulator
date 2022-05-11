from __future__ import annotations
from algorithms.algorithm import Algorithm
from config.utils import AlgorithmType
from data import Data
from models import Order, NotificationStatus
from notification import DeliveryNotification
from typing import TYPE_CHECKING, List
import algorithms.utils as AlgUtils
import config.config as config
import system.manager as SystemManager


if TYPE_CHECKING:
    from rider import Rider


class SimpleDispatch(Algorithm):
    def __init__(self):
        super().__init__(AlgorithmType.SIMPLE_DISPATCH)

    def run(self):
        super().run()

        # Orders to check
        ORDERS: List[Order] = list(
            filter(
                lambda o: o.ready_time <= self.TIME + config.DELTA_U
                and o.waiting_reply == 0,
                Data.ORDERS,
            )
        )

        for o in ORDERS:
            self.dispatch(o)

    def dispatch(self, o: Order) -> None:
        # Search rider free
        R1 = [
            (r, AlgUtils.AR(o.restaurant, r, self.TIME + 1))
            for r in Data.RIDERS
            if r.status_notification == NotificationStatus.OFF
            and AlgUtils.IRN(o.restaurant, r)
            and r.id not in o.blacklist_riders
            and r.current_delivery is None
        ]

        R2 = []

        # Search rider busy with empty queue
        if config.QUEUE:
            R2 = [
                (r, AlgUtils.AR(o.restaurant, r, r.free_at_position))
                for r in Data.RIDERS
                if r.free_at_position_ is not None
                and r.status_notification == NotificationStatus.OFF
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

            # Set order waiting reply
            o.waiting_reply = 1

            # Send notification
            notification = DeliveryNotification(r_selected, o)
            SystemManager.send(notification)

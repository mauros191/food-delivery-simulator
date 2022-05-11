from typing import Dict, List, Tuple
from data import Data
import config.config as config
from models import Bundle, Order
from notification import UpdateDeliveryNotification
from rider import Rider


class Update:
    def __init__(self, restaurant_id: int, orders: List[Order], time: int):
        self.time = time
        self.riders: List[Rider] = []
        self.orders: List[Order] = orders
        self.found: bool = False
        self.restaurant_id: int = restaurant_id
        self.N: List[UpdateDeliveryNotification] = []
        self.exclude_orders = []

    def search_incoming_riders(self) -> None:
        R: List[Rider] = [
            r
            for r in Data.RIDERS
            if r.current_delivery is not None
            and r.delivery.restaurant.id == self.restaurant_id
            and r.queue_delivery is None
            and r.delivery.start_at != -1
            and not r.delivery.leave_restaurant
            and r.delivery.bundle.size < 2
        ]
        self.riders = R

    def check(self) -> bool:
        self.search_incoming_riders()
        if len(self.riders) > 0:
            return True
        return False

    def try_update(self) -> None:
        BUN_RIDER: Dict[str, Rider] = {}
        C: List[Tuple[Bundle, int, Rider]] = []
        B_t_r: List[Bundle] = []

        for r in self.riders:
            if type(r.delivery.content) is Bundle:
                b_u: Bundle = r.delivery.content
                assert b_u.size == 1

                B_t_r.append(b_u)
                BUN_RIDER[b_u.id] = r

        for b in B_t_r:
            for o in self.orders:
                b_n: Bundle = Bundle()
                b_n.add_order(b.orders[0])
                b_n.add_order(o)
                b_n.set_best_perm()

                assert b_n.size == 2

                v: Rider = BUN_RIDER[b.id]
                if not v.id in Data.BLACKLIST_BUNDLE:
                    if o.ready_time <= self.time:
                        DELAY = config.d_max * 2
                    else:
                        DELAY = config.d_max

                    if b_n.cost_at(0) <= DELAY and b_n.cost_at(1) <= DELAY:
                        c: int = b.cost
                        v: Rider = BUN_RIDER[b.id]
                        C.append((b_n, c, v))

        C.sort(key=lambda f: f[1])
        W: List[int] = []

        for (b_n, c, v) in C:
            o1: int = b_n.orders[0].id
            o2: int = b_n.orders[1].id
            if o1 not in W and o2 not in W:
                W.append(o1)
                W.append(o2)
                notification: UpdateDeliveryNotification = UpdateDeliveryNotification(
                    v, b_n
                )
                self.N.append(notification)
                self.found = True

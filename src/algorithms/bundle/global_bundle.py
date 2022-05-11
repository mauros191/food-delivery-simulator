from __future__ import annotations
from algorithms.algorithm import Algorithm
from algorithms.bundle.update import Update
from config.utils import AlgorithmType
from data import Data
from models import Bundle
from notification import (
    DeliveryNotification,
    NotificationFromSystem,
    UpdateDeliveryNotification,
)
from typing import List, Dict, Tuple, TYPE_CHECKING
import algorithms.utils as AlgUtils
import algorithms.solver as Solver
import config.config as config
import system.manager as SystemManager


if TYPE_CHECKING:
    from models import Order
    from rider import Rider


class GlobalBundle(Algorithm):
    def __init__(self):
        super().__init__(AlgorithmType.GLOBAL_BUNDLE)

    def delay_R(self, r: Rider, b: Bundle) -> int:
        if AlgUtils.IRN(b.restaurant, r):
            AR: int = AlgUtils.AR(b.restaurant, r, self.TIME)
            return max(0, AR - b.ready_time)

        return -1

    def delay_R_Q(self, r: Rider, b: Bundle) -> int:
        if AlgUtils.IRN(b.restaurant, r, r.free_at_position):
            AR: int = AlgUtils.AR(b.restaurant, r, r.free_at_position)
            return max(0, AR - b.ready_time)

        return -1

    def check_matrix(self, M: List[List[int]]) -> bool:
        for m in M:
            for n in m:
                if n != "NA":
                    return True

        return False

    # Generate bundles
    def aggregate(self, bundles: List[Bundle]) -> List[Bundle]:
        for b in bundles:
            assert b.size == 1

        B_r: List[Bundle] = []
        C: List[Tuple[Bundle, int]] = []

        n: int = len(bundles)

        for i in range(0, n - 1):
            for j in range(i + 1, n):
                b: Bundle = Bundle()
                b.add_order(bundles[i].orders[0])
                b.add_order(bundles[j].orders[0])
                b.set_best_perm()

                assert b.size == 2

                if b.cost_at(0) <= config.d_max and b.cost_at(1) <= config.d_max:
                    c: int = b.cost
                    C.append((b, c))

        C.sort(key=lambda f: f[1])
        W: List[int] = []

        for (b, c) in C:
            o1: int = b.orders[0].id
            o2: int = b.orders[1].id

            if o1 not in W and o2 not in W:
                W.append(o1)
                W.append(o2)
                B_r.append(b)

        for b in bundles:
            if b.orders[0].id not in W:
                B_r.append(b)

        return B_r

    def run(self):
        super().run()

        # Orders to check
        ORDERS: List[Order] = list(
            filter(lambda o: o.ready_time <= self.TIME + config.DELTA_U, Data.ORDERS)
        )

        # Group order by restaurant
        PROB_ORDERS_UPDATE: Dict[int, List[Order]] = {}
        for o in ORDERS:
            try:
                PROB_ORDERS_UPDATE[o.restaurant.id].append(o)
            except KeyError:
                PROB_ORDERS_UPDATE[o.restaurant.id] = [o]

        N_U: List[UpdateDeliveryNotification] = []
        O_EXCLUDE: List[Order] = []

        for id_r, orders in PROB_ORDERS_UPDATE.items():
            u: Update = Update(id_r, orders, self.TIME)
            if u.check():
                u.try_update()
                if u.found:
                    N_U += u.N

        for n in N_U:
            content = n.content.orders
            for o in content:
                if o in ORDERS:
                    O_EXCLUDE.append(o)

        ORDERS: List[Order] = [o for o in ORDERS if o not in O_EXCLUDE]
        R_U_EXCLUDE: List[Rider] = [n.rider for n in N_U]

        # Send UpdateNotification
        for n in N_U:
            SystemManager.send(n)

        # Find riders
        R1: List[Rider] = [
            r
            for r in Data.RIDERS
            if r.current_delivery is None and r not in R_U_EXCLUDE
        ]
        R2: List[Rider] = []

        if config.QUEUE:
            R2 = [
                r
                for r in Data.RIDERS
                if r.free_at_position_ is not None
                and r.current_delivery is not None
                and r.queue_delivery is None
                and r not in R_U_EXCLUDE
            ]

        R: List[Rider] = R1 + R2

        # Number of riders
        N_RIDERS: int = len(R)

        # Number of orders
        N_ORDERS: int = len(ORDERS)

        # Create bundles
        BUNDLES_: List[Bundle] = []

        if N_ORDERS > 0:
            # Group order by restaurant creating bundles
            UTR: Dict[int, List[Bundle]] = {}
            for b in ORDERS:
                try:
                    UTR[b.restaurant.id].append(Bundle(orders=[b]))
                except KeyError:
                    UTR[b.restaurant.id] = [Bundle(orders=[b])]

            # Aggregate when it's allowed
            for (k, v) in UTR.items():
                if len(v) == 1:
                    BUNDLES_.append(v[0])

                else:
                    for b in self.aggregate(v):
                        BUNDLES_.append(b)

            # Test for bundle
            for b in BUNDLES_:
                NX = len(b.orders)
                if NX == 1:
                    assert b.cost == 0
                else:
                    assert b.cost >= config.DST

        BUNDLES: List[Bundle] = list(
            filter(lambda b: b.ready_time <= self.TIME + config.DELTA_U, BUNDLES_)
        )

        # Number of orders
        N_BUNDLES: int = len(BUNDLES)

        # Check condition
        if N_BUNDLES > 0 and N_RIDERS > 0:

            # Priority
            if config.PRIORITY == 0:
                BUNDLES_GROUP_BY_PRIORITY: Dict[int, List[Bundle]] = {
                    0: [b for b in BUNDLES]
                }

            elif config.PRIORITY == 1:
                BUNDLES_GROUP_BY_PRIORITY: Dict[int, List[Bundle]] = {
                    0: [
                        b
                        for b in BUNDLES
                        if b.priority == 2 or self.TIME >= b.ready_time
                    ],
                    1: [
                        b
                        for b in BUNDLES
                        if b.priority == 1
                        and self.TIME < b.ready_time <= self.TIME + config.DELTA_U
                    ],
                }

            elif config.PRIORITY == 2:
                BUNDLES_GROUP_BY_PRIORITY: Dict[int, List[Bundle]] = {
                    0: [b for b in BUNDLES if b.priority == 2],
                    1: [b for b in BUNDLES if b.priority == 1],
                }

            elif config.PRIORITY == 3:
                BUNDLES_GROUP_BY_PRIORITY: Dict[int, List[Bundle]] = {
                    0: [b for b in BUNDLES if self.TIME >= b.ready_time],
                    1: [
                        b
                        for b in BUNDLES
                        if self.TIME < b.ready_time <= self.TIME + config.DELTA_U
                    ],
                }

            # Test (no intersection in groups)
            TTT = []
            for k, v in BUNDLES_GROUP_BY_PRIORITY.items():
                for o in v:
                    TTT.append(o.id)
            assert len(TTT) == len(set(TTT))

            R_EXCLUDE: List[Rider] = []
            N: List[NotificationFromSystem] = []

            for k_priority in BUNDLES_GROUP_BY_PRIORITY.keys():
                bundles_priority: List[Bundle] = BUNDLES_GROUP_BY_PRIORITY[k_priority]
                if len(bundles_priority) > 0:

                    # Solve assignment problem
                    M = []
                    for r in R:
                        K = []
                        BL_R = []

                        if r.id in Data.BLACKLIST_BUNDLE:
                            BL_R += Data.BLACKLIST_BUNDLE[r.id]

                        for b in bundles_priority:
                            if r in R_EXCLUDE or b.id in BL_R:
                                K.append("NA")

                            else:
                                if r in R1:
                                    cost: float = self.delay_R(r, b)
                                else:
                                    cost: float = self.delay_R_Q(r, b)

                                if cost != -1:
                                    R_COST = cost / 60.0 + (
                                        (b.ready_time - self.TIME) / 60.0
                                    )
                                    K.append(R_COST)

                                else:
                                    K.append("NA")

                        M.append(K)

                    if self.check_matrix(M):
                        result: Tuple[Dict[int, int], float] = Solver.solve(M)

                        # Expressed as dictionary {index rider in R: index order in orders_priority}
                        solution = result[0]

                        for k, v in solution.items():
                            rider: Rider = R[k]
                            bundle: Bundle = bundles_priority[v]

                            # Create notification
                            notification = DeliveryNotification(rider, bundle)

                            # Add notification
                            N.append(notification)

                            # Exclude rider from other notification
                            R_EXCLUDE.append(rider)

            # Send DeliveryNotification
            for n in N:
                SystemManager.send(n)

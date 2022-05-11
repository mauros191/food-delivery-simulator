from __future__ import annotations
from config.utils import AlgorithmType
from algorithms.algorithm import Algorithm
from data import Data
from notification import DeliveryNotification, NotificationFromSystem
from typing import List, Dict, Tuple, TYPE_CHECKING
import algorithms.utils as AlgUtils
import algorithms.solver as Solver
import config.config as config
import system.manager as SystemManager


if TYPE_CHECKING:
    from models import Order
    from rider import Rider


class Global(Algorithm):
    def __init__(self):
        super().__init__(AlgorithmType.GLOBAL)

    def delay_R(self, r: Rider, o: Order) -> int:
        if AlgUtils.IRN(o.restaurant, r):
            AR: int = AlgUtils.AR(o.restaurant, r, self.TIME)
            return max(0, AR - o.ready_time)

        return -1

    def delay_R_Q(self, r: Rider, o: Order) -> int:
        if AlgUtils.IRN(o.restaurant, r, r.free_at_position):
            AR: int = AlgUtils.AR(o.restaurant, r, r.free_at_position)
            return max(0, AR - o.ready_time)

        return -1

    def check_matrix(self, M: List[List[int]]) -> bool:
        for m in M:
            for n in m:
                if n != "NA":
                    return True

        return False

    def run(self):
        super().run()

        if self.retryBool and self.TIME % config.F != 0:
            ORDERS_COPY: List[Order] = self.retry_orders.copy()
            ORDERS: List[Order] = [o for o in ORDERS_COPY if o in Data.ORDERS]
            self.reset_retry()

        else:
            self.reset_retry()
            ORDERS: List[Order] = list(
                filter(
                    lambda o: o.ready_time <= self.TIME + config.DELTA_U, Data.ORDERS
                )
            )

        # Find riders
        R1: List[Rider] = [r for r in Data.RIDERS if r.current_delivery is None]
        R2: List[Rider] = []

        if config.QUEUE:
            R2 = [
                r
                for r in Data.RIDERS
                if r.free_at_position_ is not None
                and r.current_delivery is not None
                and r.queue_delivery is None
            ]

        R: List[Rider] = R1 + R2

        # Number of riders
        N_RIDERS: int = len(R)

        # Number of orders
        N_ORDERS: int = len(ORDERS)

        N: List[NotificationFromSystem] = []

        # Check condition
        if N_ORDERS > 0 and N_RIDERS > 0:
            # Solve assignment problem
            M = []
            for r in R:
                K = []
                for o in ORDERS:
                    if r.id not in o.blacklist_riders:
                        if r in R1:
                            cost: float = self.delay_R(r, o)
                        else:
                            cost: float = self.delay_R_Q(r, o)

                        if cost != -1:
                            R_COST = cost / 60.0 + ((o.ready_time - self.TIME) / 60.0)
                            K.append(R_COST)

                        else:
                            K.append("NA")
                    else:
                        K.append("NA")

                M.append(K)

            if self.check_matrix(M):
                result: Tuple[Dict[int, int], float] = Solver.solve(M)

                # Expressed as dictionary {index rider in R: index order in orders_priority}
                solution = result[0]

                for k, v in solution.items():
                    rider: Rider = R[k]
                    order: Order = ORDERS[v]

                    # Create notification
                    notification = DeliveryNotification(rider, order)

                    # Add notification
                    N.append(notification)

        # Send notification
        for n in N:
            SystemManager.send(n)

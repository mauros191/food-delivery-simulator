from typing import List
from data import Data
import config.config as config
from models import Order
from system.system import System
import log.build as BuildLog


# Class Algorithm
class Algorithm:
    def __init__(self, type_alg):
        self.type = type_alg
        self.retry_orders: List[Order] = []
        self.retryBool = False

    def run(self):
        self.cancel_orders()

    def set_time(self, time: int) -> None:
        self.TIME: int = time

    def cancel_orders(self):
        for o in Data.ORDERS:
            if self.TIME > o.ready_time + config.A_max * 60 and o.waiting_reply == 0:
                o.cancel_at = self.TIME
                System.log(BuildLog.order_canceled(o))
                Data.ORDERS_DELETED.append(o)
                Data.ORDERS.remove(o)

    def retry(self, o: Order) -> None:
        self.retry_orders.append(o)
        self.retryBool = True

    def reset_retry(self) -> None:
        self.retryBool = False
        self.retry_orders.clear()

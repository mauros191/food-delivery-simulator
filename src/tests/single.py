from data import Data
from unittest.case import TestCase


class SingleTest(TestCase):
    def test_1(self):
        """|Completed delivered| == |Assigned orders|"""
        assert len(Data.DELIVERY_COMPLETED) == len(Data.ORDERS_ASSIGNED)

    def test_2(self):
        """Pickup delay == Drop-off delay"""
        for o in Data.ORDERS_ASSIGNED:
            assert (o.pickup_at - o.ready_time) == (o.dropoff_at - o.best_delivery_time)

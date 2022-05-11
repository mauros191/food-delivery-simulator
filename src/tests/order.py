import config.config as config
from config.utils import DistanceType
from data import Data
from dataset import Dataset
from unittest.case import TestCase


class OrderTest(TestCase):
    def test_1(self):
        """|Not delivered orders| == |Deleted orders|"""
        n1 = len([x for x in Dataset.TOTAL_ORDERS if x.pickup_at == -1])
        n2 = len(Data.ORDERS_DELETED)

        assert n1 == n2

    def test_2(self):
        """|Delivered orders| == |Assigned orders|"""
        n1 = len([x for x in Dataset.TOTAL_ORDERS if x.dropoff_at != -1])
        n2 = len(Dataset.TOTAL_ORDERS) - len(Data.ORDERS_DELETED)
        n3 = len(Data.ORDERS_ASSIGNED)

        assert n1 == n2 == n3

    def test_3(self):
        """Check orders"""
        for x in Dataset.TOTAL_ORDERS:
            if x in Data.ORDERS_ASSIGNED:
                assert x.pickup_at != -1 and x.dropoff_at != -1
                assert x.pickup_at < x.dropoff_at
                assert x.ready_time <= x.pickup_at
                assert x.best_delivery_time <= x.dropoff_at
                assert x.placement_time <= x.ready_time < x.best_delivery_time

            else:
                assert x in Data.ORDERS_DELETED
                assert x.pickup_at == -1 and x.dropoff_at == -1

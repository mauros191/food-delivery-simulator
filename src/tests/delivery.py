import algorithms.utils as AlgUtils
import config.config as config
from config.utils import DistanceType
import dataset
import geo.manager as GeoManager
from data import Data
from dataset import Dataset
from models import Bundle, Order
from unittest.case import TestCase


class DeliveryTest(TestCase):
    def test_1(self):
        """No pending deliveries"""
        assert len(Data.DELIVERY) == 0

    def test_2(self):
        """Check deliveries"""
        for x in Data.DELIVERY:
            rider = dataset.search_rider(x.rider_id)
            pos_at_rest = AlgUtils.position_at(rider, x.at_restaurant)

            if type(x.content) is Order:
                assert x.accept_at <= x.content.ready_time + config.A_max * 60 + 30

            elif type(x.content) is Bundle:
                assert x.accept_at <= x.content.ready_time + config.A_max * 60 + 30

            assert x.accept_at < rider.end_in_seconds

            if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
                real: bool = False

            elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
                real: bool = True

            else:
                raise Exception("Check Delivery Test real distance")

            assert (
                x.start_at
                + max(
                    1,
                    GeoManager.travel_time(
                        x.start_from, x.content.restaurant.position, real
                    ),
                )
                + int(config.PST / 2)
                == x.at_restaurant
            )

            if type(x.content) is Bundle:
                W = x.content.orders

            elif type(x.content) is Order:
                W = [x.content]

            else:
                raise Exception("Exception at test")

            for o in W:
                assert pos_at_rest == o.restaurant.position
                assert o in Data.ORDERS_ASSIGNED
                assert o not in Data.ORDERS
                assert x.at_restaurant <= o.pickup_at

                # Position of the riders
                assert AlgUtils.position_at(rider, o.pickup_at) == o.restaurant.position
                assert AlgUtils.position_at(rider, o.dropoff_at) == o.customer.position
                assert AlgUtils.position_at(rider, x.accept_at) == x.accepted_from
                assert AlgUtils.position_at(rider, x.start_at) == x.start_from

    def test_3(self):
        """Check deliveries"""
        TOT: int = 0

        for r in Dataset.TOTAL_RIDERS:
            for (i, v) in enumerate(r.delivery_completed):
                TOT += 1

                # Delivery v accepted and add in queue
                if v.accept_at + 1 != v.start_at:
                    assert config.QUEUE is True
                    assert r.delivery_completed[i - 1].accept_at < v.accept_at

                    if i > 0:
                        assert (
                            r.delivery_completed[i - 1].completed_at + 1 == v.start_at
                        )

                        # Delivery accepted and started immediately => rider was free
                if v.accept_at + 1 == v.start_at:
                    if i > 0:
                        assert r.delivery_completed[i - 1].completed_at < v.start_at

        assert TOT == len(Data.DELIVERY_COMPLETED)

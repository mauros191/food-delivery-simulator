from config.utils import DistanceType
from data import Data
from dataset import Dataset
from unittest.case import TestCase
import config.config as config
from geo.models import RealPosition, SimplePosition


class ConfigurationTest(TestCase):
    def test_1(self):
        """If we use EUCLIDEAN or MANHATTAN DISTANCE => SimplePosition"""
        if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
            for r in Data.RESTAURANTS:
                assert type(r.position) is SimplePosition

            for c in Dataset.TOTAL_ORDERS:
                assert type(c.customer.position) is SimplePosition

            for c in Dataset.TOTAL_RIDERS:
                assert type(c.position_at_start) is SimplePosition

    def test_2(self):
        """If we use HAVERSINE or ROUTE DISTANCE => RealPosition"""
        if config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
            for r in Data.RESTAURANTS:
                assert type(r.position) is RealPosition

            for c in Dataset.TOTAL_ORDERS:
                assert type(c.customer.position) is RealPosition

            for c in Dataset.TOTAL_RIDERS:
                assert type(c.position_at_start) is RealPosition

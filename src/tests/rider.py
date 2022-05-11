import config.config as config
from unittest.case import TestCase
from config.utils import DistanceType, MovementType
from dataset import Dataset
from geo.models import RealPosition, SimplePosition


class RiderTest(TestCase):
    def test_1(self):
        """If a rider is handling a delivery he cannot move randomly"""
        for r in Dataset.TOTAL_RIDERS:
            for move in r.positions:

                if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
                    assert type(move.position) is SimplePosition
                    assert 0 <= move.position.x <= config.MAX_X
                    assert 0 <= move.position.y <= config.MAX_Y

                if config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
                    assert type(move.position) is RealPosition
                    r_pos = move.position
                    r_pos.set_utm()
                    assert 0 <= r_pos.x <= config.MAX_X
                    assert 0 <= r_pos.y <= config.MAX_Y

                if move.free_movement:
                    time: int = move.time
                    for d in r.delivery_completed:
                        assert not (d.start_at <= time <= d.completed_at)

    def test_2(self):
        """If MovementType is STILL, a rider cannot move randomly"""
        if config.MOVEMENT_TYPE == MovementType.STILL:
            found = False
            for r in Dataset.TOTAL_RIDERS:
                for move in r.positions:
                    if move.free_movement:
                        found = True

            assert found == False

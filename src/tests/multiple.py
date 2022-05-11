from data import Data
from unittest.case import TestCase


class MultipleTest(TestCase):
    def test_1(self):
        """No duplicates in bundle blacklist"""

        for (k, v) in Data.BLACKLIST_BUNDLE.items():
            if len(v) != len(set(v)):
                assert False

        assert True

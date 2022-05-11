import config.config as config
import unittest
import utils
from colour_runner.runner import ColourTextTestRunner
from tests.delivery import DeliveryTest
from tests.multiple import MultipleTest
from tests.order import OrderTest
from tests.rider import RiderTest
from tests.single import SingleTest
from tests.configuration import ConfigurationTest


def run():
    utils.show_test()
    runner = ColourTextTestRunner(verbosity=2)
    runner.run(unittest.makeSuite(OrderTest))
    runner.run(unittest.makeSuite(DeliveryTest))
    runner.run(unittest.makeSuite(RiderTest))
    runner.run(unittest.makeSuite(ConfigurationTest))

    if config.ALGORITHM.value <= 3:
        runner.run(unittest.makeSuite(SingleTest))
    else:
        runner.run(unittest.makeSuite(MultipleTest))

import benchmarks as Benchmarks
import config.config as config
import random
import starter as Starter
import tests.test as Test
import utils as Utils
from system.system import System


def app():
    # Set seed
    random.seed(config.SEED)

    # Run
    Starter.init()
    Utils.show_config()
    System.run()
    Test.run()
    Benchmarks.run()


if __name__ == "__main__":
    app()

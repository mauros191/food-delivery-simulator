import config.config as config
import time
from datetime import datetime, timedelta


# CONSTANT
T = datetime.strptime(config.START_TIME, "%H:%M:%S")


def show_time(time: int) -> str:
    dtime = timedelta(0, time)
    return str((T + dtime).time())


def to_time(t: int) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(t))


def show_benchmarks() -> None:
    print("\n****************************")
    print("*        BENCHMARKS        *")
    print("****************************\n")


def show_test() -> None:
    print("\n\n****************************")
    print("*           TEST           *")
    print("****************************")


def show_config() -> None:
    print("\n****************************")
    print("*          CONFIG          *")
    print("****************************\n")
    print(f"Instance: {config.INSTANCE_GRUBHUB}")
    print(
        f"Algorithm: {config.ALGORITHM.name} with F = {config.F} and DELTA_U = {config.DELTA_U/60}"
    )
    print(f"DistanceType: {config.DISTANCE.name}")
    print(f"Movement: {config.MOVEMENT_TYPE.name}")
    print(f"Probability: {config.P_N}")
    print(f"Seed: {config.SEED}")

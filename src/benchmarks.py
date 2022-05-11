import utils
import statistics
from data import Data
from dataset import Dataset
from models import Order
from typing import List


def run() -> None:
    # Show benchmark
    utils.show_benchmarks()
    delivered_orders()
    avg_pickup_delay()
    avg_dropoff_delay()
    avg_waiting_time_riders()


# Number of orders delivered
def delivered_orders() -> None:
    N_TOT: int = len(Dataset.TOTAL_ORDERS)
    N_DROPOFF: int = len([x for x in Dataset.TOTAL_ORDERS if x.pickup_at != -1])
    NOT_DROPOFF: int = len([x for x in Dataset.TOTAL_ORDERS if x.pickup_at == -1])

    print(f"Total orders -> {N_TOT}")
    print(f"Orders delivered -> {N_DROPOFF}/{N_TOT}")
    print(f"Orders not delivered -> {N_TOT - N_DROPOFF}/{N_TOT}")

    assert N_TOT - N_DROPOFF == NOT_DROPOFF

    dev_perc: str = str(round((N_DROPOFF / N_TOT), 3) * 100)
    not_dev_perc: str = str(round(((N_TOT - N_DROPOFF) / N_TOT), 3) * 100)

    print(f"Orders delivered {dev_perc}%")
    print(f"Orders not delivered {not_dev_perc}%")


# Average pickup delay
def avg_pickup_delay() -> None:
    ORDERS_CHECK: List[Order] = [x for x in Dataset.TOTAL_ORDERS if x.pickup_at != -1]
    N: int = len(ORDERS_CHECK)

    T = []
    for o in ORDERS_CHECK:
        T.append(o.pickup_at - o.ready_time)
        assert o.pickup_at - o.ready_time >= 0

    avg_time = statistics.mean(T)
    std_time = statistics.stdev(T)
    print(
        f"Average pickup delay -> {utils.to_time(avg_time)} with std {utils.to_time(std_time)}"
    )


# Average drop-off delay
def avg_dropoff_delay() -> None:
    ORDERS_CHECK: List[Order] = [x for x in Dataset.TOTAL_ORDERS if x.dropoff_at != -1]

    T = []
    for o in ORDERS_CHECK:
        T.append(o.dropoff_at - o.best_delivery_time)
        assert o.dropoff_at - o.best_delivery_time >= 0

    avg_time = statistics.mean(T)
    std_time = statistics.stdev(T)

    print(
        f"Average drop-off delay -> {utils.to_time(avg_time)} with std {utils.to_time(std_time)}"
    )


# Average waiting time for riders
def avg_waiting_time_riders() -> None:
    T = []
    for d in Data.DELIVERY_COMPLETED:
        T.append(d.pickup_at - d.at_restaurant)
        assert d.pickup_at - d.at_restaurant == d.wait_time
        assert d.wait_time >= 0

    avg_time = statistics.mean(T)
    std_time = statistics.stdev(T)

    print(
        f"Average waiting time for riders -> {utils.to_time(avg_time)} with std {utils.to_time(std_time)}"
    )

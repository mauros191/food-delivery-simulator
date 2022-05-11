from typing import List
import config.config as config
import os
import algorithms.utils as AlgorithmUtils

from algorithms.bundle.global_bundle import GlobalBundle
from algorithms.order.greedy import Greedy
from algorithms.order.simple_dispatch import SimpleDispatch
from algorithms.order.global_order import Global

from config.utils import AlgorithmType
from data import Data
from dataset import Dataset
from events.rider import RiderGoOnlineEvent, RiderGoOfflineEvent
from events.system import CheckBenchmarks, OrderIncomingEvent
from geo.models import Position, RealPosition, SimplePosition
from models import Customer, Order, Restaurant
from rider import Rider
from system.system import System
import geo.manager as GeoManager
import config.config as config


# Init
def init() -> None:
    Dataset.clear()
    Data.clear()
    set_algorithm()
    init_dataset()
    set_min_max_map()
    init_events()
    init_event_benchmark()


# Set area
def init_event_benchmark():
    n = 0
    while n * config.CHECK_AREA_EVERY_MIN < config.MAX_TIME:
        CheckBenchmarks(config.CHECK_AREA_EVERY_MIN * n)
        n += 1


# Set MIN, MAX for MAP
def set_min_max_map():
    positions: List[Position] = []

    for r in Data.RESTAURANTS:
        positions.append(r.position)
    for o in Dataset.TOTAL_ORDERS:
        positions.append(o.customer.position)
    for v in Dataset.TOTAL_RIDERS:
        positions.append(v.position_at_start)

    # Sort by X
    positions.sort(key=lambda f: f.x)
    if positions[0].x < 0:
        raise Exception("X position < 0")
    assert config.PROJECTION[config.INSTANCE_GRUBHUB]["MAX_X"] >= positions[-1].x

    # Sort by Y
    positions.sort(key=lambda f: f.y)
    if positions[0].y < 0:
        raise Exception("Y position < 0")
    assert config.PROJECTION[config.INSTANCE_GRUBHUB]["MAX_Y"] >= positions[-1].y

    # Set max and min according to DIM_AREA
    current_MAX_X = config.PROJECTION[config.INSTANCE_GRUBHUB]["MAX_X"]
    current_MAX_Y = config.PROJECTION[config.INSTANCE_GRUBHUB]["MAX_Y"]

    config.MAX_X = (config.DIM_AREA - current_MAX_X % config.DIM_AREA) + current_MAX_X
    config.MAX_Y = (config.DIM_AREA - current_MAX_Y % config.DIM_AREA) + current_MAX_Y


# Set algorithm for system
def set_algorithm():
    if config.ALGORITHM == AlgorithmType.SIMPLE_DISPATCH:
        System.ALGORITHM = SimpleDispatch()

    elif config.ALGORITHM == AlgorithmType.GREEDY:
        System.ALGORITHM = Greedy()

    elif config.ALGORITHM == AlgorithmType.GLOBAL:
        System.ALGORITHM = Global()

    elif config.ALGORITHM == AlgorithmType.GLOBAL_BUNDLE:
        System.ALGORITHM = GlobalBundle()

    else:
        raise Exception("Algorithm selected unknown")


# Init events
def init_events() -> None:
    System.TIME = -1
    System.EVENTS.clear()
    # Init System.EVENTS
    for i in range(config.MAX_TIME + 1):
        System.EVENTS[i] = []
    create_orders_events()
    create_riders_events()


def create_orders_events() -> None:
    for o in Dataset.TOTAL_ORDERS:
        OrderIncomingEvent(o)


def create_riders_events() -> None:
    for r in Dataset.TOTAL_RIDERS:
        RiderGoOnlineEvent(r)
        RiderGoOfflineEvent(r)


# Load dataset
def init_dataset() -> None:
    if config.INSTANCE_GRUBHUB not in list(range(0, 10)):
        raise Exception("Instance Grubhub not found. Insert an instance in [0,9]")

    main_path: str = os.path.abspath(f"dataset/Grubhub/{config.INSTANCE_GRUBHUB}")
    orders_path: str = main_path + "/orders.txt"
    riders_path: str = main_path + "/couriers.txt"
    restaurants_path: str = main_path + "/restaurants.txt"

    # Load restaurants
    load_restaurants_grubhub(restaurants_path)

    # Load orders
    load_orders_grubhub(orders_path)

    # Load riders
    load_riders_grubhub(riders_path)


##################
#     GRUBHUB    #
##################


def load_restaurants_grubhub(restaurants_path: str) -> None:
    with open(restaurants_path) as f:
        data = f.readlines()
        for i in range(1, len(data)):
            content = data[i].split("\t")

            # Decoding txt file
            id_rest: int = int(content[0][1:])
            x_rest: int = int(content[1])
            y_rest: int = int(content[2][:-1])

            if config.DISTANCE.value <= 2:
                r: Restaurant = Restaurant(id_rest, SimplePosition(x_rest, y_rest))

            else:
                position_restaurant: RealPosition = GeoManager.generate_real_position(
                    x_rest, y_rest
                )
                r: Restaurant = Restaurant(id_rest, position_restaurant)

            # Add in Data
            Data.RESTAURANTS.append(r)


def load_orders_grubhub(orders_path: str) -> None:
    # Enable all orders
    all_orders: bool = True if len(config.ENABLE_ONLY_ORDERS) == 0 else False

    with open(orders_path) as f:
        data = f.readlines()
        for i in range(1, len(data)):
            content = data[i].split("\t")

            # Decoding txt file
            id_ord: int = int(content[0][1:])
            x_ord: int = int(content[1])
            y_ord: int = int(content[2])
            placement_time: int = int(content[3]) * 60
            r_id: int = int(content[4][1:])
            ready_time: int = int(content[5][:-1]) * 60

            # Find restaurant by id
            r: Restaurant = Data.search_restaurant(r_id)

            # Create customer
            if config.DISTANCE.value <= 2:
                c: Customer = Customer(SimplePosition(x_ord, y_ord))
            else:
                c_p: RealPosition = GeoManager.generate_real_position(x_ord, y_ord)
                c: Customer = Customer(c_p)

            # Create order
            o: Order = Order(id_ord, r, c, placement_time, ready_time)

            # Set BDT for o
            AlgorithmUtils.set_BDT(o)

            # Add in Dataset
            if all_orders:
                Dataset.TOTAL_ORDERS.append(o)
            else:
                if o.id in config.ENABLE_ONLY_ORDERS:
                    Dataset.TOTAL_ORDERS.append(o)


def load_riders_grubhub(riders_path: str) -> None:
    # Enable all riders
    all_riders: bool = len(config.ENABLE_ONLY_RIDERS) == 0

    with open(riders_path) as f:
        data = f.readlines()
        for i in range(1, len(data)):
            content = data[i].split("\t")

            # Decoding txt file
            id_r: int = int(content[0][1:])
            x_r: int = int(content[1])
            y_r: int = int(content[2])
            start: int = int(content[3]) * 60
            end: int = int(content[4][:-1]) * 60

            # Create position at start
            if config.DISTANCE.value <= 2:
                pos_1: SimplePosition = SimplePosition(x_r, y_r)
                r: Rider = Rider(id_r, pos_1, start, end)

            else:
                pos_2: RealPosition = GeoManager.generate_real_position(x_r, y_r)
                r: Rider = Rider(id_r, pos_2, start, end)

            # Add in Dataset
            if all_riders:
                Dataset.TOTAL_RIDERS.append(r)
            else:
                if r.id in config.ENABLE_ONLY_RIDERS:
                    Dataset.TOTAL_RIDERS.append(r)

from __future__ import annotations
from typing import TYPE_CHECKING
import config.config as config
from config.utils import DistanceType
import geo.manager as GeoManager
from geo.models import Position, PositionTime

if TYPE_CHECKING:
    from models import Bundle, Order, Restaurant
    from rider import Rider


# Search position of a rider at time t
def position_at(r: Rider, t: int) -> Position:
    if t < 0:
        raise ValueError("t < 0")

    N = len(r.positions)
    T_MAX: int = r.positions[N - 1].time

    if t > T_MAX:
        raise ValueError("I can't predict the future...")

    for i in range(N):
        if r.positions[i].time == t:
            return r.positions[i].position

    raise Exception("Position_at Exception")


# FreeAt Func for Order
def FAO(r: Rider, content: Order) -> None:
    if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
        real: bool = False
    elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
        real: bool = True
    else:
        raise Exception("FAO REAL EXCEPTION")

    s1: int = max(content.ready_time, r.delivery.exp_at_restaurant) + int(
        config.PST / 2
    )
    s1 += (
        GeoManager.travel_time(
            content.restaurant.position, content.customer.position, real
        )
        + config.DST
        + 1
    )
    r.free_at_position_ = PositionTime(content.customer.position, s1)


# FreeAt Func for Bundle
def FAB(r: Rider, content: Bundle) -> None:
    if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
        real: bool = False
    elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
        real: bool = True
    else:
        raise Exception("FAB REAL EXCEPTION")

    s1: int = max(content.ready_time, r.delivery.exp_at_restaurant) + int(
        config.PST / 2
    )

    for (i, v) in enumerate(content.orders):
        if i == 0:
            s1 += (
                GeoManager.travel_time(
                    content.restaurant.position, v.customer.position, real
                )
                + config.DST
            )
        else:
            s1 += (
                GeoManager.travel_time(
                    content.orders[i - 1].customer.position, v.customer.position, real
                )
                + config.DST
            )

    r.free_at_position_ = PositionTime(content.orders[-1].customer.position, s1 + 1)


# AR Func
def AR(restaurant: Restaurant, r: Rider, t: int | PositionTime) -> int:
    if config.DISTANCE in [
        DistanceType.EUCLIDEAN,
        DistanceType.MANHATTAN,
        DistanceType.HAVERSINE,
    ]:
        real: bool = False
    elif config.DISTANCE in [DistanceType.ROUTE]:
        real: bool = True
    else:
        raise Exception("AR REAL EXCEPTION")

    if type(t) is int:
        r_pos_t: Position = r.position
        return (
            t
            + GeoManager.travel_time(r_pos_t, restaurant.position, real)
            + int(config.PST / 2)
        )

    elif type(t) is PositionTime:
        r_pos_t: Position = t.position
        return (
            t.time
            + GeoManager.travel_time(r_pos_t, restaurant.position, real)
            + int(config.PST / 2)
        )

    else:
        raise ValueError("AR Exception")


# Set BDT
def set_BDT(o: Order) -> None:
    if config.DISTANCE in [DistanceType.EUCLIDEAN, DistanceType.MANHATTAN]:
        # Set dummy best delivery time
        time_rest_customer: int = GeoManager.travel_time(
            o.restaurant.position, o.customer.position
        )
        o.best_delivery_time = (
            o.ready_time
            + int(config.PST / 2)
            + time_rest_customer
            + int(config.DST / 2)
        )

    elif config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
        # Set real best delivery time
        time_rest_customer_real: int = GeoManager.travel_time(
            o.restaurant.position, o.customer.position, True
        )
        o.real_best_delivery_time = (
            o.ready_time
            + int(config.PST / 2)
            + time_rest_customer_real
            + int(config.DST / 2)
        )

        # Set dummy best delivery time
        if config.DISTANCE == DistanceType.HAVERSINE:
            time_rest_customer: int = GeoManager.travel_time(
                o.restaurant.position, o.customer.position, False
            )
            o.best_delivery_time = (
                o.ready_time
                + int(config.PST / 2)
                + time_rest_customer
                + int(config.DST / 2)
            )

        elif config.DISTANCE == DistanceType.ROUTE:
            o.best_delivery_time = o.real_best_delivery_time


# Expected Dropoff Time of Order o in Bundle b. Default delay in pickup of rider = 0
def EDT(o: Order, b: Bundle) -> int:
    if config.DISTANCE in [
        DistanceType.EUCLIDEAN,
        DistanceType.MANHATTAN,
        DistanceType.HAVERSINE,
    ]:
        real: bool = False
    elif config.DISTANCE in [DistanceType.ROUTE]:
        real: bool = True
    else:
        raise Exception("EDT REAL EXCEPTION")

    i: int = b.find_index(o)
    TT: int = GeoManager.travel_time(
        b.restaurant.position, b.orders[0].customer.position, real
    )
    s: int = b.ready_time + int(config.PST / 2) + TT + int(config.DST / 2)

    if i == 0:
        return s
    else:
        for j in range(1, i + 1):
            s += (
                GeoManager.travel_time(
                    b.orders[i - 1].customer.position,
                    b.orders[i].customer.position,
                    real,
                )
                + config.DST
            )
        return s


# OD (Order delay)
def OD(o: Order, b: Bundle) -> int:
    return EDT(o, b) - o.best_delivery_time


# BC (Bundle Cost)
def BC(b: Bundle) -> int:
    bc: int = 0
    for i in range(len(b.orders)):
        bc += OD(b.orders[i], b)
    return bc


# IRF (Is Rider Free)
def IRF(v: Rider) -> bool:
    return v.current_delivery is None and v.queue_delivery is None


# IRN (Is Rider Near)
def IRN(r: Restaurant, v: Rider, t: int | PositionTime = False) -> bool:
    if t is False:
        return GeoManager.straight_line_distance(v.position, r.position) <= config.D_max

    elif type(t) is PositionTime:
        return GeoManager.straight_line_distance(t.position, r.position) <= config.D_max

    else:
        raise ValueError("IRN Exception")

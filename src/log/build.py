from __future__ import annotations
from geo.models import Position
from models import Order, Restaurant
from notification import DeliveryNotification, UpdateDeliveryNotification
from typing import TYPE_CHECKING
import utils

if TYPE_CHECKING:
    from delivery import Delivery
    from rider import Rider


# COLORS
NEW_ORDER = "\033[93m"
ERROR = "\033[91m"
DROPOFF = "\033[92m"
NOTIFICATION = "\033[94m"
PICKUP = "\033[95m"
ENDC = "\033[0m"


# Func log message
def new_order(msg: str) -> str:
    return f"{NEW_ORDER}{msg}{ENDC}"


def mdropoff(msg: str) -> str:
    return f"{DROPOFF}{msg}{ENDC}"


def mpickup(msg: str) -> str:
    return f"{PICKUP}{msg}{ENDC}"


def error(msg: str) -> str:
    return f"{ERROR}{msg}{ENDC}"


def notification(msg: str) -> str:
    return f"{NOTIFICATION}{msg}{ENDC}"


# LOG MESSAGE
def move(rider_id: int, start: Position, end: Position) -> str:
    x1, y1 = start.X, start.Y
    x2, y2 = end.X, end.Y
    return f"RIDER {rider_id} MOVES FROM {(x1, y1)} TO {(x2, y2)}"


def free_move(rider_id: int, start: Position, end: Position) -> str:
    x1, y1 = start.X, start.Y
    x2, y2 = end.X, end.Y
    return f"RIDER {rider_id} MOVES RANDOMLY FROM {(x1, y1)} TO {(x2, y2)}"


def hold_position(rider_id: int, seconds: int, ct: int) -> str:
    return f"RIDER {rider_id} HOLDS ITS POSITION FOR {seconds} SECONDS"


def order(o: Order) -> str:
    x_r, y_r = o.restaurant.position.X, o.restaurant.position.Y
    x_c, y_c = o.customer.position.X, o.customer.position.Y
    id_r: int = o.restaurant.id
    rt: int = o.ready_time
    bdt: int = o.best_delivery_time
    msg: str = f"ORDER {o.id} @ R{id_r} {(x_r, y_r)} => {(x_c, y_c)}. PT: {utils.show_time(rt)} - BDT: {utils.show_time(bdt)}"
    return new_order(msg)


def go_online(r: Rider) -> str:
    x_r, y_r = r.position_at_start.X, r.position_at_start.Y
    return f"RIDER {r.id} IS ONLINE @ {(x_r, y_r)}"


def go_offline(r: Rider) -> str:
    x_r, y_r = r.position.X, r.position.Y
    return f"RIDER {r.id} IS OFFLINE @ {(x_r, y_r)}"


def receive_delivery(n: DeliveryNotification) -> str:
    if type(n.delivery.content) is Order:
        S = "ORDER"
    else:
        S = "BUNDLE"
    return notification(
        f"RIDER {n.rider.id} RECEIVES AN OFFER FOR DELIVERY {n.delivery.id} FOR {S} {n.delivery.content.id} @ R{n.delivery.content.restaurant.id}"
    )


def receive_update(n: UpdateDeliveryNotification) -> str:
    return notification(
        f"RIDER {n.rider.id} RECEIVES UPDATE_NOTIFICATION {n.content.id} @ R{n.content.restaurant.id}"
    )


def accept_delivery(n: DeliveryNotification) -> str:
    Q = "" if n.rider.queue_delivery is None else ". ADD IN QUEUE"
    if type(n.delivery.content) is Order:
        S = "ORDER"
    else:
        S = "BUNDLE"
    return notification(
        f"RIDER {n.rider.id} ACCEPTS DELIVERY {n.delivery.id} FOR {S} {n.delivery.content.id} @ R{n.delivery.content.restaurant.id}{Q}"
    )


def accept_update(n: UpdateDeliveryNotification) -> str:
    return notification(f"RIDER {n.rider.id} ACCEPTS UPDATE_NOTIFICATION {n.content.id}")


def reject_update(n: UpdateDeliveryNotification) -> str:
    return error(f"RIDER {n.rider.id} REJECTS UPDATE_NOTIFICATION {n.content.id}")


def order_canceled(o: Order) -> str:
    return error(f"ORDER {o.id} CANCELED")


def reject_delivery(n: DeliveryNotification) -> str:
    if type(n.delivery.content) is Order:
        S = "ORDER"
    else:
        S = "BUNDLE"
    return error(
        f"RIDER {n.rider.id} REJECTS OFFER FOR DELIVERY {n.delivery.id} WITH {S} {n.delivery.content.id} @ R{n.delivery.content.restaurant.id}"
    )


def start_delivery(delivery: Delivery, rider: Rider) -> str:
    return f"RIDER {rider.id} STARTS DELIVERY {delivery.id}"


def start_travel(rider: Rider, location: Restaurant | Order):
    if type(location) is Restaurant:
        x_r, y_r = location.position.X, location.position.Y
        return f"RIDER {rider.id} STARTS TRAVEL TO R{location.id} @ {(x_r, y_r)}"

    elif type(location) is Order:
        x_r, y_r = location.customer.position.X, location.customer.position.Y
        return f"RIDER {rider.id} STARTS TRAVEL TO DROP-OFF ORDER {location.id} @ {(x_r, y_r)}"

    else:
        raise TypeError("Log error start_travel")


def pickup(rider: Rider, o: Order) -> str:
    x_r, y_r = o.restaurant.position.X, o.restaurant.position.Y
    msg: str = (
        f"RIDER {rider.id} PICKS UP ORDER {o.id} @ R{o.restaurant.id} {(x_r, y_r)} "
    )
    if o.pickup_at == o.ready_time:
        msg += "WITHOUT DELAY"
    else:
        msg += f"WITH A DELAY OF {utils.to_time(o.pickup_at - o.ready_time)}"
    return mpickup(msg)


def dropoff(rider: Rider, o: Order) -> str:
    msg: str = f"RIDER {rider.id} DROPPED OFF ORDER {o.id} "
    if o.real_best_delivery_time == o.dropoff_at:
        msg += "WITHOUT DELAY"
    else:
        msg += (
            f"WITH A DELAY OF {utils.to_time(o.dropoff_at - o.real_best_delivery_time)}"
        )
    return mdropoff(msg)


def wait(rider: Rider, order: Order, time: int) -> str:
    x_r, y_r = order.restaurant.position.X, order.restaurant.position.Y
    msg: str = f"RIDER {rider.id} WILL WAIT {utils.to_time(time)} @ R{order.restaurant.id} {(x_r, y_r)}"
    return msg


def parking(rider: Rider, location: Restaurant | Order) -> str:
    if type(location) is Restaurant:
        return f"RIDER {rider.id} IS PARKING @ R{location.id} {(location.position.X, location.position.Y)}"

    elif type(location) is Order:
        return f"RIDER {rider.id} IS PARKING @ {(location.customer.position.X, location.customer.position.Y)} TO DROPOFF O{location.id}"

    else:
        raise TypeError("Log error parking")


def deparking(rider: Rider, location: Restaurant | Order) -> str:
    if type(location) is Restaurant:
        return f"RIDER {rider.id} IS RETURNING TO HIS VEHICLE @ R{location.id} {(location.position.X, location.position.Y)}"

    elif type(location) is Order:
        return f"RIDER {rider.id} IS RETURNING TO HIS VEHICLE @ {(location.customer.position.X, location.customer.position.Y)} AFTER DROPPED OFF O{location.id}"

    else:
        raise TypeError("Log error deparking")

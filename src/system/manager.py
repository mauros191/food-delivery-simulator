from data import Data
from models import Order
from notification import *
from system.system import System
import config.config as config
import log.build as BuildLog
import area.area as AreaManager
from config.utils import RetryStrategy


# Send notification to rider
def send(n: NotificationFromSystem) -> None:
    n.rider.update(n)


# Receive notification from rider
def update(n: Notification) -> None:
    if type(n) is GoOnlineNotification:
        go_online_notification(n)

    elif type(n) is GoOfflineNotification:
        go_offline_notification(n)

    elif type(n) is DeliveryNotification:
        if n.response is True:
            accept_offer(n)
        else:
            reject_offer(n)
            if config.RETRY == RetryStrategy.FORCE:
                print("RETRY!")
                if type(n.delivery.content) is Order:
                    order_rejected: Order = n.delivery.content
                    System.ALGORITHM.retry(order_rejected)

    elif type(n) is UpdateDeliveryNotification:
        if n.response is True:
            for o in n.content.orders:
                if o not in Data.ORDERS_ASSIGNED:
                    Data.ORDERS_ASSIGNED.append(o)
                    Data.ORDERS.remove(o)

            System.log(BuildLog.accept_update(n))

        else:
            System.log(BuildLog.reject_update(n))
            try:
                Data.BLACKLIST_BUNDLE[n.rider.id].append(n.content.id)
            except KeyError:
                Data.BLACKLIST_BUNDLE[n.rider.id] = [n.content.id]

    elif type(n) is DeliveryCompleted:
        d: Delivery = n.delivery
        d.completed_at = System.TIME
        n.rider.delivery_completed.append(d)
        Data.DELIVERY_COMPLETED.append(d)
        Data.DELIVERY.remove(d)


# New order
def new_order(order: Order) -> None:
    Data.ORDERS.append(order)
    System.log(BuildLog.order(order))


# A rider go online
def go_online_notification(notification: GoOnlineNotification) -> None:
    Data.RIDERS.append(notification.rider)
    System.log(BuildLog.go_online(notification.rider))


# A rider go offline
def go_offline_notification(notification: GoOfflineNotification) -> None:
    Data.RIDERS.remove(notification.rider)
    System.log(BuildLog.go_offline(notification.rider))


# Rider accepts offer
def accept_offer(notification: DeliveryNotification) -> None:

    if type(notification.delivery.content) is Order:
        order: Order = notification.delivery.content
        order.waiting_reply = 0
        Data.ORDERS_ASSIGNED.append(order)
        Data.ORDERS.remove(order)

    elif type(notification.delivery.content) is Bundle:
        bundle: Bundle = notification.delivery.content

        for o in bundle.orders:
            Data.ORDERS_ASSIGNED.append(o)
            Data.ORDERS.remove(o)

    Data.DELIVERY.append(notification.delivery)
    System.log(BuildLog.accept_delivery(notification))


# Rider rejects offer
def reject_offer(notification: DeliveryNotification) -> None:

    if type(notification.delivery.content) is Order:
        notification.delivery.content.blacklist_riders.append(notification.rider.id)
        notification.delivery.content.waiting_reply = 0

    elif type(notification.delivery.content) is Bundle:
        try:
            Data.BLACKLIST_BUNDLE[notification.rider.id].append(
                notification.delivery.content.id
            )
        except KeyError:
            Data.BLACKLIST_BUNDLE[notification.rider.id] = [
                notification.delivery.content.id
            ]

    System.log(BuildLog.reject_delivery(notification))


# Check
def check_benchmarks(init=False) -> None:
    AreaManager.reset()

    if init:
        AreaManager.init()

    else:
        TOTAL_ORDERS: List[Order] = (
            Data.ORDERS + Data.ORDERS_ASSIGNED + Data.ORDERS_DELETED
        )
        for o in TOTAL_ORDERS:
            if (
                System.TIME - config.CHECK_AREA_EVERY_MIN
                <= o.placement_time
                <= System.TIME
            ):
                AreaManager.add_order(o)

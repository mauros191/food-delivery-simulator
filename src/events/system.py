import system.manager as SystemManager
from events.event import Event
from models import Order


class OrderIncomingEvent(Event):
    def __init__(self, order: Order) -> None:
        self.order: Order = order
        self.schedule_for(order.placement_time)

    def run(self) -> None:
        SystemManager.new_order(self.order)


class CheckBenchmarks(Event):
    def __init__(self, time: int) -> None:
        self.priority: int = 3
        self.schedule_for(time)

    def run(self) -> None:
        if self.time == 0:
            SystemManager.check_benchmarks(init=True)
        else:
            SystemManager.check_benchmarks()

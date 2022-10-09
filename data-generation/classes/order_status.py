from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    DELAYED = 1
    PENDING = 2
    CONFIRMED = 3
    IN_PROGRESS = 4
    OTHER = 5

    def __str__(self):
        return self.name


@dataclass
class OrderStatus:
    order_id: int
    status: Status


@dataclass
class OrderStatusA:
    order_id: int
    status: Status


@dataclass
class OrderStatusB:
    order_id: int
    status: Status

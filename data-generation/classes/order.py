from dataclasses import dataclass
from enum import Enum


class Article(Enum):
    BOOK = 1
    PENCIL = 2
    INK = 3

    def __str__(self):
        return self.name


@dataclass
class Order:
    order_id: int
    article: Article
    quantity: int
    address: str
    date: int


@dataclass
class OrderA:
    order_id: int
    quantity: int
    date: int


@dataclass
class OrderB:
    id: int
    quantity: int
    date: int


@dataclass
class OrderC:
    order_id: int
    quantity: int
    customer: str
    date: int

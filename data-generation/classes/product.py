from dataclasses import dataclass


@dataclass
class Product:
    order_id: int
    price: str


@dataclass
class ProductA:
    order_id: int
    address: str
    price: str

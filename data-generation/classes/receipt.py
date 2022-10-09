from dataclasses import dataclass


@dataclass
class Receipt:
    order_id: int
    buyer: str
    total_cost: str

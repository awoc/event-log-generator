from dataclasses import dataclass


@dataclass
class Initiate:
    id: int
    sender: str
    date: int

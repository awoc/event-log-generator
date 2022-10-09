"""
Describes the `Activity` class.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .message import Message


@dataclass(order=True)
class Activity:
    """
    Intermediate representation of an activity with messages, date, and other attributes.
    """

    message: Message = None
    date: datetime = None
    attributes: dict = field(default_factory=dict)

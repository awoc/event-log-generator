"""
Describes the `Trace` class.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .activity import Activity


@dataclass(order=True)
class Trace:
    """
    Intermediate representation of a trace that consists of activities and attributes.
    Traces are sorted by the timestamp of the first activity.
    """

    sort_index: datetime = field(init=False, repr=False)

    activities: list[Activity]
    first_activity: datetime
    attributes: dict

    def __post_init__(self) -> None:
        """
        Sets the sort index of a trace.
        All traces are sorted by the timestamp of the first activity
        Returns
        -------

        """
        self.sort_index = self.first_activity

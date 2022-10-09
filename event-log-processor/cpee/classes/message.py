"""
Describes `Message` classes of events.
"""

from dataclasses import dataclass


@dataclass
class Message:
    """
    Class to describe a list of messages received or sent.
    """

    content: list[str]


@dataclass
class MessageSent(Message):
    """
    Class that extends `Message` to signal all messages were sent.
    """


@dataclass
class MessageReceived(Message):
    """
    Class that extends `Message` to signal all messages were received.
    """

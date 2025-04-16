from enum import Enum


class MessageType(Enum):
    """Enum of message types with their CAN ID offsets."""

    STATUS = 0x00
    HEARTBEAT = 0xFF
    # Additional message types can be added here

"""
Defines the Heartbeat CAN message structure and creation function.
"""

import time
from typing import Optional

import cantools

from platform_dbc.message_types import MessageType
from platform_dbc.modules import Module


def create_message(module: Module) -> cantools.database.can.Message:
    """Create a heartbeat message definition for a specific module."""
    BROADCAST_ID = 15  # Standard broadcast destination ID
    frame_id = module.get_message_id(BROADCAST_ID, MessageType.HEARTBEAT)

    timestamp_signal = cantools.database.can.Signal(
        name="unix_timestamp",
        start=0,  # Start bit
        length=32,  # 32 bits for Unix timestamp (second precision)
        byte_order="little_endian",
        is_signed=False,
        unit="s",  # seconds
        comment="Unix timestamp in seconds",
    )

    heartbeat_message = cantools.database.can.Message(
        frame_id=frame_id,
        name=f"{module.name}_Heartbeat",
        length=4,  # 4 bytes for the 32-bit timestamp
        senders=[module.name],
        comment=f"Heartbeat from {module.description}",
        signals=[timestamp_signal],
        is_extended_frame=True,
    )

    return heartbeat_message


def encode_data(timestamp: Optional[int] = None) -> dict[str, int]:
    """
    Prepare the data dictionary for encoding a heartbeat message.

    Args:
        timestamp: The Unix timestamp in seconds. If None, the current time
                   is used.

    Returns:
        A dictionary containing the signal name and value.
    """
    if timestamp is None:
        timestamp = int(time.time())  # Current Unix timestamp in seconds
    return {"unix_timestamp": timestamp}

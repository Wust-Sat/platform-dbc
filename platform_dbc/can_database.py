"""
Satellite CAN Database Generator

This module provides the core functionality for generating CAN databases
based on the module definitions. It handles the creation of message definitions
and database export, but doesn't include command-line functionality.
"""

import os
import time
import cantools
from typing import Dict, List, Optional, Tuple, Union

from platform_dbc.modules import (
	Module,
	MessageType,
	MODULES,
	get_active_modules,
	get_module_by_name,
)


def create_heartbeat_message(module: Module) -> cantools.database.can.Message:
    """Create a heartbeat message definition for a specific module."""
    frame_id = module.get_message_id(MessageType.HEARTBEAT)
    
    timestamp_signal = cantools.database.can.Signal(
        name='unix_timestamp',
        start=0,  # Start bit
        length=32,  # 32 bits for Unix timestamp (second precision)
        byte_order='little_endian',
        is_signed=False,
        unit='s',  # seconds
        comment='Unix timestamp in seconds',
    )
    
    heartbeat_message = cantools.database.can.Message(
        frame_id=frame_id,
        name=f'{module.name}_Heartbeat',
        length=4,
        senders=[module.name],
        comment=f'Heartbeat from {module.description}',
		signals=[timestamp_signal],
    )

    return heartbeat_message


def create_can_database(include_inactive: bool = False) -> cantools.database.Database:
    """Create a CAN database with messages for specified modules."""
    db = cantools.database.Database()
    modules_to_include = MODULES if include_inactive else get_active_modules()
    
    for module in modules_to_include:
        heartbeat_message = create_heartbeat_message(module)
        db.messages.append(heartbeat_message)
    
    return db


def save_database(db: cantools.database.Database, output_file: str) -> bool:
    """Save a CAN database to a DBC file."""
    try:
        with open(output_file, 'w') as f:
            f.write(db.as_dbc_string())
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False


def get_database_info(db: cantools.database.Database) -> Dict:
    """Get information about a CAN database."""
    messages_by_sender = {}
    for message in db.messages:
        for sender in message.senders:
            if sender not in messages_by_sender:
                messages_by_sender[sender] = []
            messages_by_sender[sender].append(message.name)
    
    return {
        "total_messages": len(db.messages),
        "messages_by_sender": messages_by_sender,
        "message_names": [message.name for message in db.messages],
        "message_ids": [(message.name, f"0x{message.frame_id:X}") for message in db.messages]
    }


def encode_heartbeat(
    db: cantools.database.Database,
    module_name: str, 
    timestamp: Optional[int] = None,
) -> Optional[bytes]:
    """
    Encode a heartbeat message for a specific module.
    Returns None if encoding failed.
    """
    if timestamp is None:
        timestamp = int(time.time())  # Current Unix timestamp in seconds 
    try:
        data = db.encode_message(
            f'{module_name}_Heartbeat',
            {'unix_timestamp': current_time}
        )
        
        return data
    except Exception as e:
        print(f"Error encoding heartbeat for {module_name}: {e}")
        return None


def decode_message(
    db: cantools.database.Database,
    message_name: str, 
    data: bytes
) -> Optional[Dict]:
    """
    Decode a CAN message.
    Returns dictionary with decoded signal values, or None if decoding failed.
    """
    try:
        return db.decode_message(message_name, data)
    except Exception as e:
        print(f"Error decoding message {message_name}: {e}")
        return None


if __name__ == "__main__":
    db = create_can_database()
    save_database(db, "wust-sat.dbc")
    get_database_info(db)

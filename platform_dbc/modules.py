"""
Satellite Module Definitions

This file defines all modules in the satellite CAN network, their IDs,
and other module-specific configuration.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class MessageType(Enum):
    """Enum of message types with their CAN ID offsets."""
    STATUS = 0x00
    HEARTBEAT = 0x01
    # Additional message types can be added here


@dataclass
class Module:
    """Satellite module definition."""
    id: int  # Number of modules is limited to 16
    name: str
    description: str
    active: bool = True
    
    def get_message_id(self, message_type: MessageType) -> int:
        "Return the CAN ID for a specific message type from this module."
        return self.id * 0x10 + message_type.value


# Define all modules
MODULES: list[Module] = [
    Module(
        id=0x0,
        name="EPS",
        description="Electrical Power System",
		active=False,
    ),
    Module(
        id=0x1,
        name="COMM",
        description="UHF Communication System",
    ),
    Module(
        id=0x3,
        name="LORA",
        description="LoRa Communication System",
		active=False,
    ),
    Module(
        id=0x4,
        name="SBAND",
        description="S-Band Communication System",
		active=False,
    ),
	Module(
		id=0x5,
		name="MB",
		description="On-Board Computer Motherboard",
		active=False,
    ),
    Module(
        id=0x6,
        name="OBC",
        description="On-Board Computer Compute Module",
    ),
    Module(
        id=0x7,
        name="ADCS",
        description="Attitude Determination and Control System",
		active=False,
    ),
]

# lookup dictionaries for efficient access
_MODULE_BY_NAME: dict[str, Module] = {module.name: module for module in MODULES}
_MODULE_BY_ID: dict[int, Module] = {module.id: module for module in MODULES}


def get_active_modules() -> list[Module]:
    "Return only the active modules from the MODULES list."
    return [module for module in MODULES if module.active]


def get_module_by_name(name: str) -> Optional[Module]:
    "Get a module definition by its name."
    return _MODULE_BY_NAME.get(name)


def get_module_by_id(module_id: int) -> Optional[Module]:
    "Get a module definition by its ID."
    return _MODULE_BY_ID.get(module_id)

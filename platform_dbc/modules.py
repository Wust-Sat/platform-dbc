"""
Satellite Module Definitions

This file defines all modules in the satellite CAN network, their IDs,
and other module-specific configuration.
"""

from dataclasses import dataclass
from typing import Optional

from platform_dbc.message_types import MessageType


@dataclass(frozen=True)
class Module:
    """Satellite module definition."""

    id: int
    name: str
    description: str
    active: bool = True

    def get_message_id(
        self,
        destination_id: int,
        message_type: MessageType,
        # ground_station_flag: bool = False,
    ) -> int:
        """
        Calculate the 29-bit CAN ID.
        """
        if not (0 <= self.id <= 15):
            raise ValueError(f"Source ID {self.id} out of range (0-15)")
        if not (0 <= destination_id <= 15):
            raise ValueError(
                f"Destination ID {destination_id} out of range (0-15)"
            )
        if not (0 <= message_type.value <= 255):
            raise ValueError(
                f"Message Type value {message_type.value} out of range (0-255)"
            )

        # Construct the ID according to the specification:
        # Bits 0-3:   Source ID
        # Bits 4-7:   Destination ID
        # Bits 8-15:  Message Type
        # Bit 16:     Ground Station Flag
        # Bits 17-28: Reserved (implicitly 0)

        can_id = (
            (self.id & 0x0F)
            | ((destination_id & 0x0F) << 4)
            | ((message_type.value & 0xFF) << 8)
            # | ((1 if ground_station_flag else 0) << 16)
        )
        return can_id


# Define all modules
MODULES: list[Module] = [
    Module(
        id=0x0,
        name="EPS_1",
        description="Electrical Power System - 1",
        active=False,
    ),
    Module(
        id=0x1,
        name="EPS_2",
        description="Electrical Power System - 2",
        active=False,
    ),
    Module(
        id=0x2,
        name="EPS_3",
        description="Electrical Power System - 3",
        active=False,
    ),
    Module(
        id=0x3,
        name="LORA",
        description="LoRa Communication System",
        active=True,
    ),
    Module(
        id=0x4,
        name="COMM",
        description="UHF Communication System",
        active=False,
    ),
    Module(
        id=0x5,
        name="SBAND",
        description="S-Band Communication System",
        active=False,
    ),
    Module(
        id=0x6,
        name="OBC_MB",
        description="On-Board Computer Motherboard",
        active=False,
    ),
    Module(
        id=0xB,
        name="ADCS",
        description="Attitude Determination and Control System",
        active=False,
    ),
    Module(
        id=0xC,
        name="OBC_CM",
        description="On-Board Computer Compute Module",
        active=True,
    ),
    Module(
        id=0xE,
        name="PAYLOAD",
        description="Payload handler module",
        active=False,
    ),
]

# lookup dictionaries
_MODULE_BY_NAME: dict[str, Module] = {module.name: module for module in MODULES}
_MODULE_BY_ID: dict[int, Module] = {module.id: module for module in MODULES}


def get_active_modules() -> list[Module]:
    """Return only the active modules from the MODULES list."""
    return [module for module in MODULES if module.active]


def get_module_by_name(name: str) -> Optional[Module]:
    """Get a module definition by its name."""
    return _MODULE_BY_NAME.get(name)


def get_module_by_id(module_id: int) -> Optional[Module]:
    """Get a module definition by its ID."""
    return _MODULE_BY_ID.get(module_id)

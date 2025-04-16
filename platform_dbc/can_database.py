"""
Satellite CAN Database Generator

This module orchestrates the generation of the CAN database (.dbc file)
by collecting message definitions from the 'messages' package.
"""

from typing import Any, Optional

import cantools

from platform_dbc.modules import MODULES, get_active_modules
from platform_dbc import messages


WUST_DB_VERSION = "0.1.0"


def create_can_database(include_inactive: bool = False) -> cantools.database.Database:
    """
    Create a CAN database by collecting messages for specified modules.
    """
    db = cantools.database.Database(version=WUST_DB_VERSION)
    modules_to_include = MODULES if include_inactive else get_active_modules()

    for module in modules_to_include:
        heartbeat_msg = messages.heartbeat.create_message(module)
        db.messages.append(heartbeat_msg)

    return db


def save_database(db: cantools.database.Database, output_file: str) -> None:
    """Save a CAN database to a DBC file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(db.as_dbc_string())


def get_database_info(db: cantools.database.Database) -> dict[str, Any]:
    """Get summary information about a CAN database."""
    messages_by_sender = {}
    for message in db.messages:
        # cantools message.senders is a list, handle multiple senders if needed
        sender_name = message.senders[0] if message.senders else "Unknown"
        if sender_name not in messages_by_sender:
            messages_by_sender[sender_name] = []
        messages_by_sender[sender_name].append(message.name)

    return {
        "dbc_version": db.version,
        "total_messages": len(db.messages),
        "messages_by_sender": messages_by_sender,
        "message_names": [message.name for message in db.messages],
        "message_ids": [
            (message.name, f"0x{message.frame_id:X}") for message in db.messages
        ],
        "nodes": [node.name for node in db.nodes],
    }


def encode_message(
    db: cantools.database.Database, message_name: str, data: dict
) -> Optional[bytes]:
    """
    Encode data for a given message name using the database definition.

    Args:
        db: The cantools Database object.
        message_name: The name of the message to encode (e.g., "LORA_Heartbeat").
        data: A dictionary mapping signal names to their values.

    Returns:
        The encoded message payload as bytes, or None if encoding fails.
    """
    try:
        message = db.get_message_by_name(message_name)
        return message.encode(data)
    except KeyError:
        print(f"Error encoding: Message '{message_name}' not found in database.")
        return None
    except Exception as e:
        print(f"Error encoding message {message_name}: {e}")
        return None


def decode_message(
    db: cantools.database.Database, frame_id: int, data: bytes
) -> Optional[dict]:
    """
    Decode CAN message data using its frame ID.

    Args:
        db: The cantools Database object.
        frame_id: The 29-bit CAN frame ID of the received message.
        data: The data payload bytes of the received message.

    Returns:
        A dictionary with decoded signal names and values, or None if decoding fails.
    """
    try:
        # Use decode_message which handles finding the message by ID
        decoded_data = db.decode_message(frame_id, data, decode_choices=False)
        return decoded_data
    except KeyError:
        # This happens if the frame_id is not found in the DBC
        print(f"Error decoding: Frame ID 0x{frame_id:X} not found in database.")
        return None
    except Exception as e:
        # Catches other potential errors during decoding (e.g., data length mismatch)
        print(f"Error decoding message with Frame ID 0x{frame_id:X}: {e}")
        return None



if __name__ == "__main__":
    # 1. Create the database object programmatically
    wust_db_programmatic = create_can_database(include_inactive=False)

    # 2. Save the database to a .dbc file (uses the programmatic object)
    dbc_filename = "wust-sat.dbc"
    save_database(wust_db_programmatic, dbc_filename)

    # 3. Display info about the generated database (uses programmatic)
    db_info = get_database_info(wust_db_programmatic)
    print("\n--- Database Info ---")
    print(f"DBC Version: {db_info['dbc_version']}")
    print(f"Total Messages: {db_info['total_messages']}")
    print("Messages by Sender:")
    for sender, msgs in db_info["messages_by_sender"].items():
        print(f"  {sender}: {len(msgs)} messages")
    print("Message IDs:")
    for name, msg_id in db_info["message_ids"]:
        print(f"  {name}: {msg_id}")
    print("---------------------\n")

    # --- Reload Database from String for Reliable Lookups ---
    print("--- Reloading DB from generated string ---")
    try:
        # Generate the DBC string from the programmatically created object
        dbc_string_content = wust_db_programmatic.as_dbc_string()
        # Load the database using cantools.db.load_string
        # This ensures internal lookup tables (_name_to_message, etc.) are built
        wust_db = cantools.db.load_string(dbc_string_content)
        print("Database reloaded successfully for encoding/decoding.")
    except Exception as e:
        print(f"Error reloading database from string: {e}")
        # Handle error appropriately, maybe exit or skip encode/decode
        wust_db = None # Ensure wust_db is None if reload fails
    print("----------------------------------------\n")
    # --- End Reload Step ---

    # 4. Example Usage: Encode and Decode a Heartbeat
    #    IMPORTANT: Use the reloaded 'wust_db' object from now on
    if wust_db:
        print("--- Encoding/Decoding Example ---")
        active_modules = get_active_modules()
        if active_modules:
            example_module_name = active_modules[0].name  # e.g., LORA
            heartbeat_message_name = f"{example_module_name}_Heartbeat"

            # Prepare data using the helper from heartbeat.py
            heartbeat_data_dict = messages.heartbeat.encode_data()
            print(
                f"Encoding {heartbeat_message_name} with data: {heartbeat_data_dict}"
            )

            # Encode using the generic encode function with the RELOADED DB
            encoded_payload = encode_message(
                wust_db, heartbeat_message_name, heartbeat_data_dict
            )

            if encoded_payload:
                print(f"Encoded Payload (bytes): {encoded_payload.hex()}")

                # Get the frame ID from the RELOADED DB to simulate receiving
                try:
                    message_def = wust_db.get_message_by_name(
                        heartbeat_message_name
                    )
                    frame_id_to_decode = message_def.frame_id

                    # Decode using the generic decode function with the RELOADED DB
                    print(
                        f"Decoding message with Frame ID: 0x{frame_id_to_decode:X}"
                    )
                    decoded_data = decode_message(
                        wust_db, frame_id_to_decode, encoded_payload
                    )

                    if decoded_data:
                        print(f"Decoded Data: {decoded_data}")
                    else:
                        print("Decoding failed.")
                except KeyError:
                    print(
                        f"Error during decode: Message '{heartbeat_message_name}'"
                        " not found in reloaded DB (should not happen here)."
                    )
                except Exception as e:
                    print(f"An unexpected error occurred during decoding: {e}")

            else:
                print("Encoding failed.")
        else:
            print("No active modules found for encoding/decoding example.")
        print("-----------------------------\n")
    else:
        print("Skipping encoding/decoding example due to DB reload failure.")


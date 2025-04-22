import canopen
import time
import logging
import os
import threading # Import threading

log = logging.getLogger(__name__)

# Map NMT state strings to their byte values for heartbeat
NMT_STATE_TO_BYTE = {
    'INITIALISING': 0x00, # Should not happen in heartbeat normally
    'DISCONNECTED': 0x01, # Should not happen in heartbeat normally
    'CONNECTING': 0x02, # Should not happen in heartbeat normally
    'PREPARING': 0x03, # Should not happen in heartbeat normally
    'STOPPED': 0x04,
    'OPERATIONAL': 0x05,
    'PRE-OPERATIONAL': 0x7F,
    'RESETTING': 0x80, # Should not happen in heartbeat normally
    'RESET COMMUNICATION': 0x81, # Should not happen in heartbeat normally
    'RESET NODE': 0x82, # Should not happen in heartbeat normally
    # Add others if needed, but these cover the main ones
}


class SimulatedCanopenNode:
    """
    Base class for simulating a CANopen node using python-canopen.
    Includes manual heartbeat generation.
    """

    def __init__(self, node_id: int, od_path: str, channel: str = 'vcan0'):
        """
        Initializes the simulated node.

        :param node_id: The CANopen Node ID for this device.
        :param od_path: Path to the OD file (EDS/DCF/EPF) describing the node.
        :param channel: The socketcan channel to use (e.g., 'vcan0').
        """
        if not os.path.exists(od_path):
            raise FileNotFoundError(f"OD file not found: {od_path}")

        self.node_id = node_id
        self.od_path = od_path
        self.channel = channel
        self.network = None
        self.node = None

        # Heartbeat control
        self.heartbeat_ms = 0
        self.heartbeat_thread = None
        self.stop_event = threading.Event() # Event to signal thread termination

        log.info(
            f"Initializing Node ID {self.node_id} with {self.od_path} on {self.channel}"
        )

    def _heartbeat_producer_task(self):
        """Task executed by the heartbeat thread."""
        log.info(f"Node ID {self.node_id}: Heartbeat thread started (Interval: {self.heartbeat_ms} ms).")
        heartbeat_cob_id = 0x700 + self.node_id
        interval_sec = self.heartbeat_ms / 1000.0

        while not self.stop_event.is_set():
            try:
                # Get current NMT state byte
                current_state_str = self.node.nmt_state
                state_byte = NMT_STATE_TO_BYTE.get(current_state_str, 0x00) # Default to 0 if unknown

                # Send heartbeat message
                if self.network: # and self.network.is_connected:
                     self.network.send_message(heartbeat_cob_id, [state_byte])
                     # log.debug(f"Node ID {self.node_id}: Sent heartbeat (State: {current_state_str} / 0x{state_byte:02X})")
                else:
                    log.warning(f"Node ID {self.node_id}: Network not connected, skipping heartbeat.")
                    # Avoid busy-loop if network disconnects unexpectedly
                    self.stop_event.wait(interval_sec)
                    continue

            except Exception as e:
                log.error(f"Node ID {self.node_id}: Error in heartbeat thread: {e}", exc_info=True)
                # Avoid busy-loop on repeated errors
                self.stop_event.wait(interval_sec)

            # Wait for the next interval, checking stop_event periodically
            self.stop_event.wait(interval_sec)

        log.info(f"Node ID {self.node_id}: Heartbeat thread stopped.")


    def start(self):
        """
        Connects to the CAN network and starts the CANopen node.
        """
        log.info(f"Starting Node ID {self.node_id}...")
        self.network = canopen.Network()
        self.stop_event.clear() # Ensure event is clear before starting

        try:
            # Add the local node using the OD file
            self.node = self.network.add_node(self.node_id, self.od_path)
            log.info(f"Node ID {self.node_id} added to network.")

            # Connect to the CAN bus
            self.network.connect(bustype='socketcan', channel=self.channel)
            log.info(f"Node ID {self.node_id} connected to {self.channel}.")

            # Set the NMT state of the local node to OPERATIONAL
            self.node.nmt_state = 'OPERATIONAL'
            log.info(f"Node ID {self.node_id} NMT state set to OPERATIONAL.")

            # Read heartbeat time from OD and start thread if needed
            try:
                # Get the OD entry for heartbeat time
                od_entry = self.node.object_dictionary[0x1017]
                od_value = od_entry.value # Check current value

                # If the current value is None, try to apply the DefaultValue from EDS
                if od_value is None:
                    log.warning(f"Node ID {self.node_id}: OD 1017 value is None. Attempting to apply DefaultValue from EDS.")
                    try:
                        # Access the default value stored in the definition
                        default_value_str = od_entry.default
                        if default_value_str:
                             # Convert default value string (e.g., "1000") to int
                             od_value = int(default_value_str)
                             # Explicitly set the .value attribute
                             od_entry.value = od_value
                             log.info(f"Node ID {self.node_id}: Applied DefaultValue {od_value} to OD 1017.")
                        else:
                             log.warning(f"Node ID {self.node_id}: No DefaultValue found in EDS for OD 1017.")
                             od_value = 0 # Fallback to 0 if no default specified
                    except (AttributeError, ValueError, TypeError) as e:
                         log.error(f"Node ID {self.node_id}: Error applying DefaultValue for OD 1017: {e}. Defaulting to 0.")
                         od_value = 0 # Fallback to 0 on error

                # Ensure heartbeat_ms is an integer (should be after the logic above)
                self.heartbeat_ms = int(od_value) if od_value is not None else 0

                # Now check the potentially updated self.heartbeat_ms
                if self.heartbeat_ms > 0:
                    log.info(f"Node ID {self.node_id}: Starting heartbeat thread with interval {self.heartbeat_ms} ms.")
                    self.heartbeat_thread = threading.Thread(
                        target=self._heartbeat_producer_task, daemon=True
                    )
                    self.heartbeat_thread.start()
                else:
                    log.info(f"Node ID {self.node_id}: Heartbeat disabled (Effective value for OD 1017 is {self.heartbeat_ms}).")

            except KeyError:
                 log.warning(f"Node ID {self.node_id}: OD entry 0x1017 (Heartbeat Time) not found. Heartbeat disabled.")
            except Exception as e:
                 log.error(f"Node ID {self.node_id}: Error starting heartbeat thread: {e}", exc_info=True)

            # Setup any specific callbacks or initial values after node is ready
            self._post_start_setup()

        except Exception as e:
            log.error(f"Error starting Node ID {self.node_id}: {e}", exc_info=True) # Log traceback
            if self.network:
                self.network.disconnect()
            raise

    def _post_start_setup(self):
        """
        Placeholder for derived classes to add specific setup logic
        after the node is connected and started (e.g., adding callbacks).
        """
        pass

    def run(self):
        """
        Runs the main loop, keeping the node alive.
        """
        if not self.network or not self.node:
            log.error(f"Node ID {self.node_id} not started. Call start() first.")
            return

        log.info(f"Node ID {self.node_id} running. Press Ctrl+C to stop.")
        try:
            # Keep main thread alive. Heartbeat runs in separate thread.
            while not self.stop_event.is_set():
                # Can add other periodic checks here if needed
                time.sleep(0.5) # Sleep a bit, but check stop_event reasonably often
        except KeyboardInterrupt:
            log.info(f"Stopping Node ID {self.node_id} (KeyboardInterrupt)...")
        finally:
            self.stop()

    def stop(self):
        """
        Stops the CANopen node and disconnects from the network.
        """
        log.info(f"Initiating stop sequence for Node ID {self.node_id}...")
        # Signal the heartbeat thread to stop
        self.stop_event.set()

        # Wait for the heartbeat thread to finish
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            log.debug(f"Node ID {self.node_id}: Waiting for heartbeat thread to join...")
            self.heartbeat_thread.join(timeout=2.0) # Wait max 2 seconds
            if self.heartbeat_thread.is_alive():
                log.warning(f"Node ID {self.node_id}: Heartbeat thread did not join cleanly.")
            else:
                log.debug(f"Node ID {self.node_id}: Heartbeat thread joined.")
        self.heartbeat_thread = None # Clear the thread object

        # Disconnect from network
        if self.network and self.network.is_connected:
            log.info(f"Disconnecting Node ID {self.node_id} from CAN bus...")
            # Optionally send NMT Reset Node before disconnecting (as was happening before)
            # Note: Sending requires the network to be connected.
            if self.node:
                 try:
                     # Set state locally first
                     self.node.nmt_state = 'RESETTING' # Or 'STOPPED' / 'PRE-OPERATIONAL'
                     # Send NMT Reset command (0x81) or Stop (0x02) etc.
                     # self.node.nmt.send_command(0x81) # Reset Node
                     # self.node.nmt.send_command(0x02) # Stop Node
                     # Let's skip sending NMT command here to avoid complexity during shutdown
                     log.debug(f"Node ID {self.node_id}: NMT state set to {self.node.nmt_state} locally.")
                 except Exception as e:
                     log.warning(f"Node ID {self.node_id}: Error setting NMT state during stop: {e}")

            self.network.disconnect()
            log.info(f"Node ID {self.node_id}: Disconnected.")
        else:
             log.info(f"Node ID {self.node_id}: Already disconnected or network not initialized.")

        self.network = None
        self.node = None
        log.info(f"Node ID {self.node_id} stop sequence complete.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

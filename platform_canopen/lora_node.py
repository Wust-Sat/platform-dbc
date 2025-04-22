import logging
from platform_canopen.simulated_node import SimulatedCanopenNode

log = logging.getLogger(__name__)

# Constants from XDC/Platform Docs
LORA_HW_ID = 4
LORA_NODE_ID = 16 + LORA_HW_ID  # 20
LORA_XDC_PATH = 'platform_canopen/lora.xdc'
LORA_EDS_PATH = 'platform_canopen/lora.eds'
LORA_CONTROL_REGISTER_IDX = 0x2000

class LoraNode(SimulatedCanopenNode):
    """
    Simulates the WUST-Sat LoRa Module.
    Node ID: 20
    Listens for writes to Object 0x2000 (LoRa Control Register).
    """

    def __init__(self, channel: str = 'vcan0'):
        super().__init__(
            node_id=LORA_NODE_ID, od_path=LORA_EDS_PATH, channel=channel
        )
        self.control_value = 0 # Internal state

    def _on_control_write(self, new_value):
        """Callback triggered when Object 0x2000 is written via SDO."""
        log.info(
            f"LoRa Node (ID {self.node_id}): Control Register (0x{LORA_CONTROL_REGISTER_IDX:04X}) "
            f"written via SDO. Old value: {self.control_value}, New value: {new_value}"
        )
        self.control_value = new_value
        # Add any logic here to react to the control value change

    def _post_start_setup(self):
        """Set up the SDO write callback for the control register."""
        try:
            control_reg_var = self.node.object_dictionary[LORA_CONTROL_REGISTER_IDX]
            # Store the initial value from OD
            self.control_value = control_reg_var.value
            # Add the callback
            control_reg_var.add_callback(self._on_control_write)
            log.info(
                f"LoRa Node (ID {self.node_id}): Callback added for Control Register (0x{LORA_CONTROL_REGISTER_IDX:04X})"
            )
        except KeyError:
            log.error(
                f"LoRa Node (ID {self.node_id}): Object 0x{LORA_CONTROL_REGISTER_IDX:04X} not found in OD. Check XDC."
            )
        except Exception as e:
            log.error(
                f"LoRa Node (ID {self.node_id}): Error setting up callback: {e}"
            )


if __name__ == "__main__":
    # Example of how to run this specific node directly
    # In the final setup, run_simulation.py will handle this.
    import argparse
    parser = argparse.ArgumentParser(description="Run LoRa Node Simulation")
    parser.add_argument('--channel', default='vcan0', help='CAN channel (default: vcan0)')
    args = parser.parse_args()

    lora_sim = LoraNode(channel=args.channel)
    try:
        lora_sim.start()
        lora_sim.run()
    except Exception as e:
        log.error(f"LoRa simulation failed: {e}")
    finally:
        lora_sim.stop() # Ensure cleanup happens

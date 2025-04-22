import logging
from platform_canopen.simulated_node import SimulatedCanopenNode

log = logging.getLogger(__name__)

OBC_HW_ID = 13
OBC_NODE_ID = 16 + OBC_HW_ID  # 29
OBC_XDC_PATH = 'platform_canopen/obc.xdc'
OBC_EDS_PATH = 'platform_canopen/obc.eds' 
OBC_STATUS_REGISTER_IDX = 0x2000

class ObcNode(SimulatedCanopenNode):
    """
    Simulates the WUST-Sat OBC Module.
    Node ID: 29
    Provides a readable status register (Object 0x2000).
    """

    def __init__(self, channel: str = 'vcan0'):
        super().__init__(
            node_id=OBC_NODE_ID, od_path=OBC_EDS_PATH, channel=channel
        )
        # Internal state for the status register (can be updated if needed)
        self._status_value = 1 # Default to 1 (OK) as per XDC

    def _post_start_setup(self):
        """Set the initial value of the status register if needed."""
        try:
            status_reg_var = self.node.object_dictionary[OBC_STATUS_REGISTER_IDX]
            # Set the initial value in the live OD based on our internal state
            # (or read it from XDC's default if preferred)
            status_reg_var.value = self._status_value
            log.info(
                f"OBC Node (ID {self.node_id}): Status Register (0x{OBC_STATUS_REGISTER_IDX:04X}) initialized to {self._status_value}"
            )
        except KeyError:
            log.error(
                f"OBC Node (ID {self.node_id}): Object 0x{OBC_STATUS_REGISTER_IDX:04X} not found in OD. Check XDC."
            )
        except Exception as e:
            log.error(
                f"OBC Node (ID {self.node_id}): Error setting initial status: {e}"
            )

    # Example method to potentially change the status later
    def set_status(self, new_status: int):
        """Updates the internal status and the OD value."""
        if self.node:
            try:
                self._status_value = new_status
                status_reg_var = self.node.object_dictionary[OBC_STATUS_REGISTER_IDX]
                status_reg_var.value = self._status_value
                log.info(
                    f"OBC Node (ID {self.node_id}): Status Register (0x{OBC_STATUS_REGISTER_IDX:04X}) updated to {new_status}"
                )
            except Exception as e:
                 log.error(
                    f"OBC Node (ID {self.node_id}): Failed to update status register: {e}"
                )
        else:
            log.warning("Cannot set status, node not started.")


if __name__ == "__main__":
    # Example of how to run this specific node directly
    import argparse
    parser = argparse.ArgumentParser(description="Run OBC Node Simulation")
    parser.add_argument('--channel', default='vcan0', help='CAN channel (default: vcan0)')
    args = parser.parse_args()

    obc_sim = ObcNode(channel=args.channel)
    try:
        obc_sim.start()
        # Example: Change status after a delay
        # import time
        # time.sleep(10)
        # obc_sim.set_status(5) # Example: Set status to 'Error'
        obc_sim.run()
    except Exception as e:
        log.error(f"OBC simulation failed: {e}")
    finally:
        obc_sim.stop()

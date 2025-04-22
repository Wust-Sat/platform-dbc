import argparse
import logging
import sys

from platform_canopen.obc_node import ObcNode
from platform_canopen.lora_node import LoraNode

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

def main():
    parser = argparse.ArgumentParser(description="Run WUST-Sat CANopen Node Simulation")
    parser.add_argument(
        'module',
        choices=['obc', 'lora'],
        help='Which module simulation to run.'
    )
    parser.add_argument(
        '--channel',
        default='vcan0',
        help='SocketCAN channel to use (default: vcan0)'
    )
    args = parser.parse_args()

    log.info(f"Attempting to start simulation for: {args.module} on {args.channel}")

    node_instance = None
    try:
        if args.module == 'obc':
            node_instance = ObcNode(channel=args.channel)
        elif args.module == 'lora':
            node_instance = LoraNode(channel=args.channel)
        else:
            # Should be caught by argparse choices, but belt-and-suspenders
            log.error(f"Unknown module type: {args.module}")
            sys.exit(1)

        node_instance.start()
        node_instance.run() # This blocks until Ctrl+C

    except FileNotFoundError as e:
        log.error(f"Configuration file error: {e}")
        log.error("Make sure the XDC files (obc.xdc, lora.xdc) are present.")
    except ImportError as e:
         log.error(f"Import error: {e}")
         log.error("Check dependencies and file structure.")
    except Exception as e:
        log.error(f"An unexpected error occurred during simulation: {e}", exc_info=True) # Log traceback
    finally:
        if node_instance:
            # run() handles calling stop() on KeyboardInterrupt,
            # but call it here again just in case of other exceptions
            # where run() might not have been reached or exited cleanly.
            node_instance.stop()
        log.info(f"Simulation for {args.module} finished.")

if __name__ == "__main__":
    main()

# Platform CAN database

CAN message definition used in WUST-Sat.


## Instalation

1. Install [Poetry](https://python-poetry.org/docs/main/#installing-with-the-official-installer)
2. Run `poetry install --no-root`
3. Enter the virtualenv: `$(poerty env activate)`


## CAN Message Format

A CAN message consists of two main elements: an ID and a payload.

### Message ID

Each message type has a unique ID. We're using the 11-bit standard (rather
than 29-bit). Lower ID numbers have higher priority on the network.

The ID encodes two pieces of information:
- Last 4 bits: Module identifier
- Remaining bits: Message type

Example: An s-band module (ID: 3) sending a heartbeat message (type: 1) would
have frame ID 0x013 in hexadecimal or 20 in decimal.

### Message Payload

Using CAN-DF the payload can range from 0 to 64 bytes in length.

# Platform CAN database

CAN message definition used in WUST-Sat.


## Instalation

1. Install [Poetry](https://python-poetry.org/docs/main/#installing-with-the-official-installer)
2. Run `poetry install --no-root`
3. Enter the virtualenv: `$(poerty env activate)`


## CAN Message Format

A CAN message consists of two main elements: an ID and a payload.


### Message ID

Each message type has a unique ID. We're using the 29-bit standard. Lower ID
numbers have higher priority on the network.

ID structure is described in the [WUST-Sat Platform Communication Architecture](https://github.com/Wust-Sat/architecture/blob/master/docs/platform-communication.md)


### Message Payload

Using CAN-DF the payload can range from 0 to 64 bytes in length.

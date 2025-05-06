# Transceiver TJA1145

## Key features

1. **CAN Partial Networking** Support

2. CAN FD support

3. Low energy consumption - Standby and Sleep modes

4. Protection against overvoltages and short circuits on CAN lines.

5. SPI interface

## Modes of operation

### Normal Mode

Full functionality, the transceiver transmits and receives data, communicates with the bus

### Standy Mode

Power consumption reduction, the transceiver does not actively participate in communication, but still monitors the CAN bus. It can be woken up by special CAN frames or an external control signal

### Sleep Mode

Lowest power saving, the transceiver is practically turned off and wakes up only in case of an external signal or specific CAN events.

### Overtemperature Mode

If the transceiver temperature exceeds a safe level, the transceiver limits its functionality to protect against destruction.

### Off Mode

Off is off.

The transitions between modes are illustrated in Fig. 4 in the data sheet [TJA1145](https://www.nxp.com/docs/en/data-sheet/TJA1145.pdf).

![alt text](tr_image.png)

## Important registers

1. Bit responsible for 29-bit frames register 2Fh bit 7 -> 1
2. ID Registers 27h to 2Ah
3. ID Mask Registers 2Bh to 2Eh (where 1 means don't care)

## Waking up individual transceivers

The description of the wake-up process is explained in the datasheet [TJA1145](https://www.nxp.com/docs/en/data-sheet/TJA1145.pdf).
Wake-up frame - **Chapter 7.3.1. Wake-up frames (WUF)**.

### Format of the wake-up frame (WUF)

The wake-up frame is structured as:\
... d4 d3 d2 d1 | i8 i7 i6 i5 i4 i3 i2 i1

Where:

- d = DLC bit coding
- i = ID mask bit coding

DLC is responsible for registers to be considered when applying the ID mask. In this case, one register is sufficient-8 devices.

### Wake-up

1. Set the registers **DM7 (Addr. 6Fh)** on individual transceivers, assigning unique numbers (00000001, 00000010, 00000100, ...).

2. In the wake-up frame, set DLC to 0001.

3. To wake up a specific device, assign 1 to the bit corresponding to its address.\
\
If you want to wake up device 00000001, send the frame 0001|00000001.\
\
If you want to wake up devices 00001000 and 00000010, send the frame 0001|00001010.

![alt text](tr_image-1.png)

The transiver does not have a sleep frame - analogous to the wake-up frame - so it usually goes into sleep/stanby mode due to lack of communication.

#### Alternatively

Alternatively, you can set DLC to 0 and then select the device you want to wake up, for example for device with ID=1:\
d4 d3 d2 d1 | i8 i7 i6 i5 i4 i3 i2 i1\
0 0 0 0 | 0 0 0 0 0 0 0 1

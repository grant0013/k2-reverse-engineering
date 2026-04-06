# Creality K2 Communication Architecture
# Reverse-engineered 2026-04-05

## Hardware Communication Paths

```
                    +------------------+
                    |  Host CPU        |
                    |  (Allwinner T113)|
                    +--------+---------+
                             |
            +----------------+----------------+
            |                |                |
       /dev/ttyS7      /dev/ttyS1       /dev/ttyS5
       (230400 baud)   (230400 baud)    (230400 baud)
            |                |                |
    +-------+-------+ +-----+------+   +-----+-----+
    |  Main MCU     | | Nozzle MCU |   | RS-485 Bus|
    | GD32F303RET6  | | GD32F303CBT6|  | (chelper) |
    +-------+-------+ +------------+   +-----+-----+
            |                                 |
     Internal UART                      +-----+-----+
     (transparent)                      |  CFS/Box  |
            |                           | (Material |
    +-------+-------+                  |  System)  |
    | Motor X (0x81)|                  +-----------+
    | Motor Y (0x82)|
    | Motor Z (0x83)|
    | Motor Z1(0x84)|
    +---------------+

    Extruder Motor (0x85) → via Nozzle MCU
```

## Communication Protocols

### Path 1: Host → Main MCU → Motor Controllers (TRANSPARENT)
- Used for: Motor control, parameter read/write, stall mode, protection
- Protocol: Klipper MCU command → config_transparent → MCU internal UART → RS-485 to motors
- Commands: transparent_send oid=%c write=%*s timeout_ms=%u
- Response: transparent_response oid=%c read=%*s
- Frame: HEAD(0xF7) + ADDR + LEN + STATE + CMD + DATA + CRC8
- CRC8 computed over: LEN + STATE + CMD + DATA

### Path 2: Host → serial_485 (ttyS5) → CFS/Box
- Used for: Material box communication, auto address discovery
- Protocol: chelper serial_485_queue → RS-485 transceiver → CFS devices
- Commands: cmd_send_data_with_response(data, timeout, retries_en)
- Data format: ADDR + LEN + STATE + CMD + DATA (chelper adds HEAD + CRC)
- Auto-addr: broadcast 0xFE/0xFF, discovery 0xA1, address set 0xA0

### Path 3: Host → Nozzle MCU → Extruder Motor
- Used for: Extruder motor stall mode, encoder calibration
- Protocol: Klipper MCU command → transparent on nozzle_mcu
- Address: 0x85 (via nozzle_mcu transparent, not serial_485)

## Motor Controller Protocol

### Device Addresses
| Motor | Address | Bus |
|-------|---------|-----|
| X     | 0x81    | Main MCU transparent |
| Y     | 0x82    | Main MCU transparent |
| Z     | 0x83    | Main MCU transparent |
| Z1    | 0x84    | Main MCU transparent |
| E     | 0x85    | Nozzle MCU transparent |

### Command Bytes
| Command | Byte | Description |
|---------|------|-------------|
| reboot  | 0x01 | Reboot motor MCU |
| encoder_cal | 0x03 | Encoder calibration |
| elec_offset_cal | 0x04 | Electrical offset calibration |
| control | 0x05 | Direct motor control |
| sys_param | 0x06 | System parameter read/write |
| flash_param | 0x07 | Flash parameter read/write |
| get | 0x08 | Get motor feedback data |
| boot | 0x0B | Boot motor MCU |
| protection | 0x0C | Protection status |
| systemid | 0x0D | System identification |
| read/set_addr | 0x0E | Read/set RS-485 address |
| version | 0x0F | Firmware version |
| stall_mode | 0x11 | Stall detection mode |
| dev_uuid | 0x12 | Device UUID query |

### Stock Boot Sequence (from log analysis)
1. MCU config phase: register config_transparent oid=1
2. MCU connect: all 3 MCUs configured
3. _connect:
   a. GPIO pin check (PB9, PB10, PB7, PB8) via MCU
   b. Broadcast addr set (0xFF 0x0E 0x01) via serial_485 — times out, normal
   c. Extruder stall state set
   d. UUID query X (0x81 0x12 0x02) via serial_485 — responds!
   e. UUID query Y (0x82 0x12 0x02) via serial_485 — responds!
   f. UUID query Z, Z1 — no response (not closed-loop on this model)
   g. Broadcast retry via transparent — empty response
   h. Address read X (0x81 0x0E 0x02) via serial_485 — responds!
   i. Address read Y (0x82 0x0E 0x02) via serial_485 — responds!
   j. Address read extruder via transparent — responds!
   k. "All motors are normal"
   l. Stall mode X, Y via transparent — responds!
   m. Protection check X, Y via transparent — responds!
   n. GPIO pin restore
   o. Flash param update: read all 226 params from each motor
4. Printer is ready
5. auto_addr starts in reactor callback (CFS discovery)

## Key Observations
- Stock code uses BOTH serial_485 AND transparent paths for motors
- Motors only respond AFTER stock _build_config configures MCU transparent UART
- Our code gets transparent_response from MCU but motors return empty data
- The MCU firmware's config_transparent likely needs specific UART initialization
- MCU firmware is in GD32 .bin files — needs decompilation to understand

# Creality K2 RS-485 Serial Protocol - Reverse Engineered

## Frame Format

| Position | Name  | Description |
|----------|-------|-------------|
| 0        | HEAD  | Frame header byte |
| 1        | ADDR  | Device address (motor 1-5, CFS, etc.) |
| 2        | LEN   | Data length |
| 3        | STATE | Status/state byte |
| 4        | CMD   | Command byte |
| 5+       | DATA  | Payload data (variable length) |

## Device Addresses (from MOTOR_NAME_TO_NUM)

| Device | Address |
|--------|---------|
| X motor | 1 |
| Y motor | 2 |
| Z motor | 3 |
| Z1 motor | 4 |
| E extruder | 5 |

## Classes

### Serialhdl_485 (Low-level serial handler)
- `connect_uart(serialport, baud, rts)` - Opens serial port
- `raw_send(cmd)` - Send raw data
- `raw_send_wait_ack(cmd, notifications, timeout)` - Send and wait for ACK
- `get_response(cmd, timeout, notifications_addr, notifications_cmd, retries_en)` - Send command and get response
- `register_response(callback, notifications_addr, notifications_cmd)` - Register response handler
- `_bg_thread()` - Background thread for receiving data
- `disconnect()` - Close connection

### Serial_485_Wrapper (High-level wrapper for Klipper)
- `cmd_send_data_with_response(data, timeout, retries_en)` - Send command and get response
- `cmd_485_send_data(gcmd)` - Send data from GCode command
- `register_response(cb, notifications_addr, notifications_cmd)` - Register callback
- `handle_callback(params)` - Handle incoming data callback
- `send_queue_process(eventtime)` - Process send queue (timer callback)
- `add_send_data()` / `remove_send_data(args)` - Manage send queue

## Dependencies
- chelper: serial_485_queue_alloc, serial_485_queue_exit, serial_485_queue_free, serial_485_queue_get_stats, serial_485_queue_pull, serial_485_queue_send
- pyserial: For UART communication
- Klipper reactor: For timer-based queue processing

## Motor Control Protocol

### MOTOR_SYS_PARAM Command
Format: `MOTOR_SYS_PARAM NUM=<axis> DATA=1 ID=<param_id> PARAMS=<value> PARAMS_TYPE=float`

### Full Parameter ID Map (226 parameters)

See motor_params_map.md for the complete mapping extracted from klippy.log flash_param enumeration.

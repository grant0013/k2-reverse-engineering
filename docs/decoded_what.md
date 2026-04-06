# What we know about Creality's K2 software stack

A field guide to the proprietary Creality components on the K2 — what each one
does, where it lives, and what gcode commands or behaviors it controls. This
is the index that points you at the right place when you're trying to figure
out **why** the K2 is doing something Klipper-on-Voron wouldn't.

All paths refer to the K2 standard with stock January 2026 firmware. K2 Plus,
K1, K1C are similar but path/build details may differ.

## Daemons (running processes)

| Process | Path | Role |
|---|---|---|
| `master-server` | `/usr/bin/master-server` | The big one. C++ daemon that drives the touchscreen UI, manages the print pipeline, fires `G29` and `BED_MESH_CALIBRATE` during print prep, parses `[G29_TIME]` responses, handles error codes, talks to Klipper via the Moonraker WebSocket. Also runs `AiDetectForeignBodyRun` for AI failure detection. |
| `app-server` | `/usr/bin/app-server` | Bridges the touchscreen UI to master-server. Smaller, mostly serialisation/transport. |
| `cam_app` / `cam_sub_app` | `/usr/bin/cam_*` | Camera streaming + AI inference for the foreign-body / spaghetti detection. |
| `mdns` | `/usr/bin/mdns` | Advertises `_Creality-<serial>._udp.local` for the Creality app to find the printer. |
| `moonraker` | `/usr/share/moonraker-env/bin/python` | Standard Moonraker, mostly unmodified by Creality. |
| `klipper` (`klippy.py`) | `/usr/share/klipper/klippy/` | Modified Klipper — see Klipper section below. |

## Klipper modifications

Creality's Klipper tree is mostly upstream code with these additions:

### Compiled `.cpython-39.so` extras (binary, in `klippy/extras/`)

These are the things that make K2 prints actually happen, and the things you
will fight if you want to behave differently. Each `_wrapper.so` is paired
with a tiny Python `.py` shim that loads it.

| File | Loaded by | Hijacks / provides |
|---|---|---|
| `prtouch_v3_wrapper.cpython-39.so` | `prtouch_v3.py` (31-line shim) | Strain-gauge probe driver. **Hijacks `BED_MESH_CALIBRATE`** with a non-adaptive implementation that crashes on `MESH_MIN`/`MESH_MAX`/`PROBE_COUNT`. Provides the `[probe]` object and registers as `axis_twist_compensation`. |
| `prtouch_v2_wrapper.cpython-39.so` | `prtouch_v2.py` | Older probe driver, kept for backwards compatibility. |
| `prtouch_v1_wrapper.cpython-39.so` | (unused) | Even older. |
| `box_wrapper.cpython-39.so` | `box.py` | CFS multi-material system. Imports `ModuleCommandError` from `gcode.py` (Creality-only symbol). |
| `motor_control_wrapper.cpython-39.so` | `motor_control.py` | Closed-loop servo control for the X/Y/E motors. Talks to motor MCUs via the transparent UART path. |
| `serial_485_wrapper.cpython-39.so` | `serial_485.py` | RS-485 transport for the CFS box. Registered as `[serial_485 serial485]`. |
| `filament_rack_wrapper.cpython-39.so` | `filament_rack.py` | CFS filament rack management. |

### Python extras (`klippy/extras/*.py`, source visible)

The interesting ones — these are how Creality glues things together and where
you can read the logic without decompilation.

| File | Purpose |
|---|---|
| `prtouch_v3.py` | 31-line shim. `load_config` instantiates `PRTouchEndstopWrapper(config)` and registers it as both `probe` and `axis_twist_compensation`. |
| `auto_addr.py` / `auto_addr_wrapper.py` | RS-485 device auto-discovery for CFS. Sends `0xFE 0xFF` broadcast then `0xA1` discovery. |
| `box.py` | CFS material system Python side. |
| `motor_control.py` | Closed-loop servo PID/LESO config and `[motor_control]` section parsing. |
| `belt_mdl.py` | Belt tension model — used by `BELT_TENSION` macro. |
| `bl24c16f.py` | EEPROM driver for the bl24c16f I²C chip on the printer board. |
| `base_info.py` | Reads/writes the printer's serial number and basic identity from EEPROM. |
| `custom_macro.py` | Loads default temperatures (bed/extruder/G28) into a macro-accessible scope. |
| `load_ai.py` | Hooks for the AI failure detection. |
| `z_align.py` | Z-axis alignment using the optical endstop on PA15 (single Z on K2 standard, dual on K2 Plus). |
| `statistics_ext.py` | Custom statistics module. **Watch out:** if you ship the upstream Klipper `statistics.py` it shadows the Python stdlib `statistics` module and breaks `.so` wrappers that call `statistics.median()`. |
| `dirzctl.py` | Z direction control helper. |
| `fan_feedback.py` | Fan tachometer feedback. |
| `filter.py` | Filter/digital signal helpers. |
| `tool.py` | Tool change support. |

### Modified core files

Creality patched some upstream Klipper files. **DO NOT replace these with
upstream versions** — the `.so` wrappers depend on Creality-specific symbols
and method signatures.

| File | What's different |
|---|---|
| `klippy/gcode.py` | Adds `ModuleCommandError` (subclass of `CommandError`), `CommandWarning`, `base_info` imports, `cProfile` hooks. `box_wrapper.so` imports `ModuleCommandError` at module load. |
| `klippy/toolhead.py` | ~804 lines vs upstream ~614. Adds `record_z_pos`, `check_move_out_of_range`, `simple_move`, modified `move()`. `.so` wrappers call into these. |
| `klippy/mcu.py` | Old `setup_adc_callback(report_time, callback)` signature. Upstream changed to `setup_adc_callback(callback)`. |
| `klippy/extras/adc_temperature.py` and `temperature_mcu.py` | Use the old ADC callback signature. |
| `klippy/extras/buttons.py` | Lacks upstream's `register_debounce_button`. |
| `klippy/extras/bed_mesh.py` | **Adaptive support stripped** — no `ADAPTIVE` parameter, no `exclude_object` integration. The native `cmd_BED_MESH_CALIBRATE` is still inside `BedMeshCalibrate` though, just unregistered. |

### Stripped from extras (compared to upstream Klipper)

| Missing module | Replacement on K2 | Note |
|---|---|---|
| `screws_tilt_adjust.py` | None — must drop in upstream version | Easy to add back, see [k2-adaptive-bedmesh](https://github.com/grant0013/k2-adaptive-bedmesh) for the manual leveling integration |
| `bed_screws.py` | None | Same |
| Adaptive bed mesh logic in `bed_mesh.py` | Hijacked by `prtouch_v3_wrapper.so` | Restore via `restore_bed_mesh.py` extras module — see `k2-adaptive-bedmesh` |

## Hardware

| MCU | Chip | Role |
|---|---|---|
| Main MCU | GD32F303RET6 | Closed-loop servo control for X/Y, RS-485 host for CFS, main GPIO |
| Nozzle MCU | GD32F303CBT6 | Hotend, extruder motor, strain-gauge probe, fan PWMs |
| Host CPU | Allwinner T113-i (ARM Cortex-A7 dual-core) | Linux + Klipper + Creality daemons |

## Communication paths

See [`k2_architecture.md`](k2_architecture.md) for the full diagram. The
short version:

- **Host → Main MCU → motor controllers**: closed-loop servo commands via
  the MCU's "transparent" UART pass-through. Used for XY motor PID, stall
  mode, parameter read/write.
- **Host → `serial_485` → CFS box**: RS-485 bus for the multi-material system.
  Auto-discovery uses broadcast addresses; each device gets a unique address.
- **Host → Nozzle MCU → extruder motor**: same transparent path but on the
  nozzle MCU's UART. The extruder is also a closed-loop servo on K2.

## Configurable motor parameters

The motor controllers have **226 parameters** in their flash. About 50 of
them are runtime-configurable from Klipper config; the rest are
firmware-locked. See [`motor_params_map.md`](motor_params_map.md) for the
full table.

The configurable ones are mostly:

- Position/speed/current loop PID gains
- LESO (Linear Extended State Observer) bandwidths
- Stall detection thresholds
- "Zazen" idle current reduction
- Protection limits (peak current, over-speed, tracking error)
- Subdivision (microstepping)

The rest (R, L, Ke, electrical offsets, encoder calibration constants) are
calibrated at the factory and locked.

## Where Creality's binaries call into Klipper

A handful of magic incantations from `master-server` worth knowing about:

| Master-server call | Source location | What it does |
|---|---|---|
| `G29 BED_TEMP=NN` | `Control/PrintfManager.c:604` | Triggered before print start. Calls Klipper's G29 macro which historically did a full bed mesh. **Intercept this** if you want adaptive mesh — see `k2-adaptive-bedmesh`. |
| `BED_MESH_CALIBRATE GCODE_FILE='...'` | `Control/AppModeSdPrint.c:1992` | Alternate mesh trigger. The wrapper accepts the param but ignores it for adaptivity. |
| `BED_MESH_PROFILE LOAD=default` | `Control/AppFuncModule.c:2516` | Loads the saved mesh from the previous calibration. |
| `BED_MESH_CLEAR` | (multiple) | Clears any active mesh. |
| `BED_MESH_CALIBRATE_START_PRINT` | `Control/AppModeSdPrint.c` | Called from the touchscreen print pipeline. Wraps `BED_MESH_CALIBRATE`. |
| `RESTORE_LIMITS` / `SET_LIMITS` | (multiple) | Push/pop velocity/accel limits around prep moves. |
| `MOTOR_CONTROL NUM=2 DATA=2` | `AppFuncModule.c` | Toggles motor enable/disable. |
| `[G29_TIME]Execution time: NN seconds` | `GcodeCmdResAnl.c:5345` | The response handshake master-server scans for after firing G29. **You must emit this** if you intercept G29 with a no-op, or master-server will stall waiting forever. |

The state variable `bed_mesh_calibate_state` (typo is in the binary, not
mine) at `GcodeCmdResAnl.c:5345` controls whether master-server skips
calibration on the next print. Setting it via reverse-engineered means is
a TODO.

## Files NOT in this repo (but worth knowing about)

For copyright reasons we don't ship Creality's binaries. If you want to
look at them yourself, here's where to find each on the printer:

- `/usr/bin/master-server` — the C++ daemon
- `/usr/bin/app-server` — touchscreen bridge
- `/usr/share/klipper/klippy/extras/*_wrapper.cpython-39.so` — the Klipper hijack binaries
- `/usr/data/creality/` — Creality's userdata, config, log files
- `/etc/init.d/klipper`, `/etc/init.d/master-server` — service scripts

`strings /usr/bin/master-server | less` will get you very far without any
decompilation. `objdump -d` works for the deeper dives. The `.so` files
are stripped Cython modules — `cython -3 --convert-range` reverse mode
helps a little but expect to spend time matching against upstream Klipper
to figure out which symbols map where.

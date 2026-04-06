# k2-reverse-engineering

Research notes, protocol documentation, and tooling from reverse-engineering the Creality K2 (and related K1/K1C) firmware. Focused on understanding **what Creality changed in the otherwise-open Klipper stack** and how to work with or around it without flashing custom firmware.

This repo is the **upstream research** for [`k2-adaptive-bedmesh`](https://github.com/grant0013/k2-adaptive-bedmesh) (the production tool that uses these notes to unlock real adaptive bed mesh). If you're a K2 owner who just wants better prints, start there. If you're a developer / hacker who wants to know **how** any of this works or **why** Creality's stack does what it does, you're in the right place.

## What's in the repo

```
docs/
  k2_architecture.md         Communication paths, MCU layout, RS-485 motor protocol
  motor_params_map.md        All 226 motor controller params with configurability flags
  rs485_protocol.md          RS-485 frame format, device addresses, class API
  decoded_what.md            Field guide to every Creality binary, daemon, and Klipper hijack
tools/
  k2ssh.py                   Shared SSH helper - reads K2_HOST/K2_PASS env vars
  ssh_enum.py                Initial recon - OS, Klipper version, extras dir, daemon list
  backup_printer.py          Snapshot Klipper + Moonraker + config trees on the printer
  download_files.py          Pull Creality's modified .py shims and configs locally
  tail_klippy.py             Live log streamer with smart filtering for macro/mesh events
  deploy_extras.py           Generic deploy helper for custom Klipper extras modules
README.md
LICENSE                      GPL v3 (matches Klipper)
.gitignore
```

## Scope

**In scope:**

- Documenting Creality's modifications to the upstream Klipper stack — what they added, what they replaced, what they stripped
- Reverse-engineering the proprietary daemons (`master-server`, `app-server`) to understand the print pipeline
- Mapping the closed-loop servo motor controller protocol (226 parameters, RS-485 + transparent UART transport)
- Tools that let you SSH into a stock K2, take backups, pull files, and tail logs without rooting or reflashing
- Documenting which gcode commands are intercepted by which `.so` wrapper

**Out of scope:**

- Hosting Creality's binaries (the `.so` wrappers, master-server, app-server) — copyright concerns
- Decompiled `.so` artifacts in any form
- Anything that requires flashing custom firmware
- Hosting Klipper itself (clone upstream — see [klipper3d.org](https://www.klipper3d.org/))
- Cloud / Creality account integration

## What we figured out (highlights)

**The big one** — Creality's `prtouch_v3_wrapper.cpython-39.so` hijacks `BED_MESH_CALIBRATE` with a non-adaptive implementation that crashes (`IndexError` at line 1922) when you pass `MESH_MIN`/`MESH_MAX`/`PROBE_COUNT`. The upstream `bed_mesh.BedMeshCalibrate.cmd_BED_MESH_CALIBRATE` is still alive in memory at `printer.lookup_object('bed_mesh').bmc.cmd_BED_MESH_CALIBRATE` — you can re-register it from a custom extras module on `klippy:connect` and adaptive mesh just works. See [`k2-adaptive-bedmesh`](https://github.com/grant0013/k2-adaptive-bedmesh) for the full implementation.

**Master-server independently triggers full meshes.** Even if your slicer + macro are perfect, `/usr/bin/master-server` fires `G29 BED_TEMP=NN` and `BED_MESH_CALIBRATE GCODE_FILE='...'` from `Control/AppModeSdPrint.c:1992` and `Control/PrintfManager.c:604` during print prep, and it doesn't care which slicer or upload path you used. Hijacking the Klipper-side `G29` macro to be a no-op (while emitting a fake `[G29_TIME]` response handshake) is the bypass.

**The closed-loop servo motors are tunable.** X/Y/E motors on the K2 are not standard steppers — they're closed-loop servos with their own MCUs running cascaded position/speed/current PID loops, plus a LESO observer and "zazen" idle current reduction. About 50 of the 226 controller parameters are runtime-configurable from Klipper config; the rest are factory-locked. See [`docs/motor_params_map.md`](docs/motor_params_map.md) for the full map.

**Strain-gauge probe via `prtouch_v3`.** The K2's "probe" is the entire toolhead — it presses down on the bed and measures strain in the gantry to detect contact. There's no Z endstop in the traditional sense; the optical endstop on PA15 is only used for Z-max safety. This is why the wrapper is so deeply integrated: probing is a multi-MCU dance involving the nozzle MCU's strain ADC and the main MCU's stepping engine.

**Section-name footgun.** Klipper's `bed_mesh.ProfileManager` does `config.get_prefix_sections('bed_mesh')` and `name.split(' ', 1)[1]` on every match. A custom config section called `[bed_mesh_override]` will crash Klipper at startup with `IndexError: list index out of range`. Use a name that doesn't start with `bed_mesh`.

There's a lot more in [`docs/decoded_what.md`](docs/decoded_what.md).

## Using the tools

All scripts read connection details from environment variables so credentials never end up in the repo:

```sh
export K2_HOST=192.168.x.x
export K2_PASS=your_root_password
# optional:
export K2_USER=root           # default
export K2_KEY=~/.ssh/k2_key   # use SSH key instead of password
```

Then:

```sh
# Recon a freshly-accessed K2
python tools/ssh_enum.py

# Take a full backup before any patching
python tools/backup_printer.py

# Pull the Creality-modified extras and configs to a local dir for inspection
python tools/download_files.py --out ./k2_dump

# Live-tail the log, filtered for macro/mesh events
python tools/tail_klippy.py

# Tail the raw log
python tools/tail_klippy.py --raw

# Drop a custom Klipper extras module onto the printer
python tools/deploy_extras.py path/to/my_module.py --restart
```

## Ethics

**This repo is research, not piracy.** Everything here was learned by reading freely-readable Python source on the printer, observing live gcode/log traffic, running `strings` and `grep` over binaries we have legitimate access to (i.e. on hardware we own), and cross-referencing against upstream Klipper. We do not host any of Creality's compiled binaries, decompiled artifacts, or copyrighted source.

If you're at Creality and you'd like to chat: please consider open-sourcing your Klipper modifications under GPL like the rest of the project. The reason this repo exists is that we can't yet — your closed wrappers actively prevent K2 owners from using bed mesh features that have been free in upstream Klipper since 2022.

## Contributing

Issues and PRs welcome. Particularly interested in:

- Compatibility reports on K1, K1C, K1 SE, K2 Plus
- More entries for `decoded_what.md` — especially correlating `master-server` strings to behaviors
- Clean dumps of the motor controller parameter values from a stock printer (so we can verify factory defaults)
- Decompilation/disassembly notes (text-only, no binaries)
- Better tools — particularly anything that automates capturing the call sequence master-server uses during print prep

## Related projects

- [k2-adaptive-bedmesh](https://github.com/grant0013/k2-adaptive-bedmesh) — drop-in adaptive bed mesh for K2 (production output of this research)
- [Klipper](https://www.klipper3d.org/) — upstream
- [pellcorp/creality](https://github.com/pellcorp/creality) — earlier K1 reverse-engineering work that mapped a lot of the Creality directory layout

## Licence

GPL v3, matching Klipper. See [`LICENSE`](LICENSE).

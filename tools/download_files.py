"""Pull a list of files from the K2 to a local directory.

Useful for grabbing klippy/extras .py files, .cfg files, decompiled .so
artifacts, log files, or anything else you want to inspect locally.

Default file list grabs the interesting Creality-modified Klipper extras
plus the main config files. Override with --files / --out from CLI.

Set K2_HOST and K2_PASS environment variables.

Usage:
    python download_files.py
    python download_files.py --out C:/k2_dump
    python download_files.py --files /usr/share/klipper/klippy/extras/box.py /etc/passwd
"""
import argparse
import os
import sys
from k2ssh import connect

DEFAULT_FILES = [
    # Klipper extras (the Python shims that wrap Creality's compiled .so files
    # and the supporting modules - useful for understanding what's hooked
    # where without touching the binaries themselves)
    "/usr/share/klipper/klippy/extras/prtouch_v3.py",
    "/usr/share/klipper/klippy/extras/prtouch_v2.py",
    "/usr/share/klipper/klippy/extras/auto_addr_wrapper.py",
    "/usr/share/klipper/klippy/extras/serial_485.py",
    "/usr/share/klipper/klippy/extras/motor_control.py",
    "/usr/share/klipper/klippy/extras/box.py",
    "/usr/share/klipper/klippy/extras/load_ai.py",
    "/usr/share/klipper/klippy/extras/belt_mdl.py",
    "/usr/share/klipper/klippy/extras/bl24c16f.py",
    "/usr/share/klipper/klippy/extras/base_info.py",
    "/usr/share/klipper/klippy/extras/custom_macro.py",
    "/usr/share/klipper/klippy/extras/z_align.py",
    # Creality's modified core files
    "/usr/share/klipper/klippy/extras/bed_mesh.py",
    "/usr/share/klipper/klippy/extras/probe.py",
    "/usr/share/klipper/klippy/extras/exclude_object.py",
    "/usr/share/klipper/klippy/gcode.py",
    "/usr/share/klipper/klippy/mcu.py",
    "/usr/share/klipper/klippy/toolhead.py",
    # Configs
    "/mnt/UDISK/printer_data/config/printer.cfg",
    "/mnt/UDISK/printer_data/config/gcode_macro.cfg",
    "/mnt/UDISK/printer_data/config/sensorless.cfg",
    "/mnt/UDISK/printer_data/config/box.cfg",
    "/mnt/UDISK/printer_data/config/motor_control.cfg",
    "/mnt/UDISK/printer_data/config/printer_params.cfg",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="./k2_files",
                        help="Local directory to save files into")
    parser.add_argument("--files", nargs="+",
                        help="Override the default file list")
    args = parser.parse_args()

    files = args.files or DEFAULT_FILES
    os.makedirs(args.out, exist_ok=True)

    cli = connect()
    sftp = cli.open_sftp()

    ok = 0
    failed = 0
    for remote in files:
        name = os.path.basename(remote)
        local = os.path.join(args.out, name)
        try:
            stat = sftp.stat(remote)
            sys.stdout.write("  %s (%d bytes) ... " % (name, stat.st_size))
            sys.stdout.flush()
            sftp.get(remote, local)
            print("OK")
            ok += 1
        except Exception as e:
            print("FAIL: %s" % e)
            failed += 1

    sftp.close()
    cli.close()
    print("\nDownloaded %d files, %d failed. Saved to %s" %
          (ok, failed, args.out))


if __name__ == "__main__":
    main()

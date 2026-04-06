"""Initial reconnaissance of a Creality K2 over SSH.

Reports OpenWrt build, Klipper version, the full klippy/extras tree, any
non-standard directories under klippy/, and a hash of master-server (the
Creality C++ daemon - useful as a firmware-version fingerprint).

Useful as the very first thing to run on a freshly accessed K2 to confirm
which firmware version you're dealing with before applying any patches.

Set K2_HOST, K2_PASS (and optionally K2_USER) environment variables.
"""
import sys
from k2ssh import connect, run

cli = connect()


def section(title, cmd):
    print("\n=== %s ===" % title)
    print(run(cli, cmd))


section("System / OS",
        "uname -a; cat /etc/openwrt_release 2>/dev/null | head -5; "
        "cat /usr/data/creality/factory_data 2>/dev/null | head -5")

section("Klipper version",
        "cat /usr/share/klipper/.git/HEAD 2>/dev/null; "
        "cat /usr/share/klipper/klippy/.version 2>/dev/null; "
        "cat /usr/share/klipper/.version 2>/dev/null")

section("klippy/ top level",
        "ls -la /usr/share/klipper/klippy/")

section("klippy/extras files",
        "ls /usr/share/klipper/klippy/extras/ | sort")

section("Compiled .so wrappers in extras",
        "ls -la /usr/share/klipper/klippy/extras/*.so 2>/dev/null")

section("Non-standard klippy/ subdirs (e.g. mymodule)",
        "find /usr/share/klipper/klippy/ -maxdepth 1 -type d")

section("master-server fingerprint (firmware version marker)",
        "md5sum /usr/bin/master-server /usr/bin/app-server 2>/dev/null")

section("Running Creality daemons",
        "ps | grep -i -E 'master|app-server|c440x|moonraker|nginx' | "
        "grep -v grep")

section("Klipper config files",
        "ls -la /mnt/UDISK/printer_data/config/")

cli.close()

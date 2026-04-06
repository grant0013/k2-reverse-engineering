"""Make a full point-in-time backup of the K2's Klipper, Moonraker, and config trees.

Stores everything under /mnt/UDISK/backup/{klipper,moonraker,config}_<DATE>
on the printer itself - keeps the backup local to the printer's storage,
which survives Klipper restarts but NOT a factory reset.

Run this BEFORE applying any of the patches in k2-adaptive-bedmesh or
before any other major change. Cheap insurance.

Set K2_HOST and K2_PASS environment variables.
"""
import sys
import datetime
from k2ssh import connect, run

cli = connect()

stamp = datetime.date.today().strftime("%Y%m%d")
backup_root = "/mnt/UDISK/backup"

script = (
    "set -e\n"
    f"STAMP={stamp}\n"
    f"BACKUP={backup_root}\n"
    "mkdir -p $BACKUP\n"
    "\n"
    "echo '=== Backing up Klipper (/usr/share/klipper) ==='\n"
    "if [ ! -d $BACKUP/klipper_$STAMP ]; then\n"
    "    cp -a /usr/share/klipper $BACKUP/klipper_$STAMP\n"
    "    echo 'Klipper backup done'\n"
    "else\n"
    "    echo 'Klipper backup for today already exists - skipping'\n"
    "fi\n"
    "\n"
    "echo '=== Backing up Moonraker (/usr/share/moonraker) ==='\n"
    "if [ ! -d $BACKUP/moonraker_$STAMP ]; then\n"
    "    cp -a /usr/share/moonraker $BACKUP/moonraker_$STAMP\n"
    "    echo 'Moonraker backup done'\n"
    "else\n"
    "    echo 'Moonraker backup for today already exists - skipping'\n"
    "fi\n"
    "\n"
    "echo '=== Backing up configs (/mnt/UDISK/printer_data/config) ==='\n"
    "if [ ! -d $BACKUP/config_$STAMP ]; then\n"
    "    cp -a /mnt/UDISK/printer_data/config $BACKUP/config_$STAMP\n"
    "    echo 'Config backup done'\n"
    "else\n"
    "    echo 'Config backup for today already exists - skipping'\n"
    "fi\n"
    "\n"
    "echo '=== Backup sizes ==='\n"
    "du -sh $BACKUP/klipper_$STAMP $BACKUP/moonraker_$STAMP $BACKUP/config_$STAMP 2>/dev/null\n"
    "echo '=== Free space remaining on /mnt/UDISK ==='\n"
    "df -h /mnt/UDISK\n"
)

print(run(cli, script, timeout=300))
cli.close()
print("Backup complete.")

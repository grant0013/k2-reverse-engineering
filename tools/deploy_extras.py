"""Deploy a Python file into the K2's klippy/extras/ directory.

Generic helper for installing a custom Klipper extras module on the K2.
Backs up the existing extras directory first (as a tar.gz under /tmp),
SCPs the new file in, runs an ast.parse syntax check on the printer to
catch typos before restart, and optionally restarts Klipper.

Used by k2-adaptive-bedmesh and similar projects to install drop-in
extras modules.

Set K2_HOST and K2_PASS environment variables.

Usage:
    python deploy_extras.py path/to/restore_bed_mesh.py
    python deploy_extras.py path/to/my_module.py --restart
    python deploy_extras.py path/to/my_module.py --no-backup
"""
import argparse
import os
import sys
import time
import py_compile
from k2ssh import connect, run

EXTRAS_DIR = "/usr/share/klipper/klippy/extras"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("local_file", help="Local .py file to deploy")
    p.add_argument("--name", default=None,
                   help="Override remote filename (default: basename)")
    p.add_argument("--no-backup", action="store_true",
                   help="Skip the tar.gz backup of the extras dir")
    p.add_argument("--restart", action="store_true",
                   help="Restart Klipper service after deploy")
    args = p.parse_args()

    if not os.path.exists(args.local_file):
        sys.exit("ERROR: %s not found" % args.local_file)
    if not args.local_file.endswith(".py"):
        sys.exit("ERROR: only .py files are supported")

    print("== Local syntax check ==")
    try:
        py_compile.compile(args.local_file, doraise=True)
        print("  OK")
    except py_compile.PyCompileError as e:
        sys.exit("FAIL: %s" % e)

    name = args.name or os.path.basename(args.local_file)
    remote = "%s/%s" % (EXTRAS_DIR, name)

    cli = connect()

    if not args.no_backup:
        ts = time.strftime("%Y%m%d_%H%M%S")
        print("\n== Backing up %s to /tmp/extras_backup_%s.tar.gz ==" %
              (EXTRAS_DIR, ts))
        print(run(cli,
                  "tar -czf /tmp/extras_backup_%s.tar.gz "
                  "-C /usr/share/klipper/klippy extras 2>&1 | tail" % ts))
        print(run(cli, "ls -lh /tmp/extras_backup_%s.tar.gz" % ts))

    print("\n== Uploading %s -> %s ==" % (args.local_file, remote))
    sftp = cli.open_sftp()
    sftp.put(args.local_file, remote)
    sftp.chmod(remote, 0o644)
    sftp.close()
    print(run(cli, "ls -la %s; md5sum %s" % (remote, remote)))

    print("\n== Remote syntax check ==")
    out = run(cli,
              "python3 -c \"import ast; "
              "ast.parse(open('%s').read()); print('parse OK')\"" % remote)
    print(out)
    if "parse OK" not in out:
        sys.exit("FAIL: remote ast.parse did not return OK")

    if args.restart:
        print("\n== Restarting Klipper ==")
        print(run(cli, "/etc/init.d/klipper restart 2>&1 | tail -5"))
        time.sleep(6)
        log = "/mnt/UDISK/printer_data/logs/klippy.log"
        print(run(cli,
                  "awk '/Start printer at/{n=NR} END{print n}' " + log))
        # Show any errors after the latest restart
        print(run(cli,
                  "awk '/Start printer at/{n=NR} END{print n}' " + log +
                  " | xargs -I{} awk 'NR>={}' " + log +
                  " | grep -nE 'ERROR|Traceback|Config error|"
                  "\"code\":\"key[0-9]+\"' | grep -vE "
                  "'extrude_below|buf_len' | head -10"))

    cli.close()
    print("\nDone.")


if __name__ == "__main__":
    main()

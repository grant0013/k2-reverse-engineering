"""Live-tail /tmp/klippy.log on the K2 with smart filtering.

The K2's klippy.log is extremely chatty - thousands of lines per minute of
RS-485 traffic, ADC samples, and motor controller heartbeats. This script
tails it and only prints lines matching events you care about: macro fires,
mesh probes, errors, key3xx codes, BED_MESH activity, etc.

Set K2_HOST and K2_PASS environment variables. Optionally K2_LOG to override
the log path.

Usage:
    python tail_klippy.py
    python tail_klippy.py --pattern 'BED_MESH|adaptive|G29'
    python tail_klippy.py --raw    # don't filter, just stream everything
"""
import argparse
import re
import sys
import time
from k2ssh import connect

# Default log path on the K2 (OpenWrt build)
DEFAULT_LOG = "/mnt/UDISK/printer_data/logs/klippy.log"

# Lines we want to see
DEFAULT_INTERESTING = re.compile(
    r"(START_PRINT|ADAPTIVE_MESH|BED_MESH|EXCLUDE_OBJECT|HEAT_SOAK|"
    r"M118|RESPOND|G28|Generating new points|Mesh Bed|"
    r"Traceback|ERROR|Config error|\"code\":\"key[0-9]+\"|"
    r"respond_info|probe at|samples_tolerance|key3[4-9]|"
    r"register_command|prepare|nozzle_clean|tilt_calculate|"
    r"shutdown|invoke_shutdown|state_message)",
    re.IGNORECASE)

# Lines we DON'T want even if they match the above (low-signal noise)
DEFAULT_NOISE = re.compile(
    r"(buf_len|buf\[|extrude_below_min_temp|webhooks:_handle_query|"
    r"data_send|cmd_485|reactor:invoke|sysparam|auto_addr|reactor:_check|"
    r"485_send|extrude_below|stat_msg|register_command:|generate_stats|"
    r"485:|adc_callback|temp_callback|gcodein=|cputime=|memavail|sysload=)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log",
                   default=__import__('os').environ.get('K2_LOG', DEFAULT_LOG),
                   help="Remote log path")
    p.add_argument("--pattern", default=None,
                   help="Custom regex of lines to KEEP (overrides default)")
    p.add_argument("--noise", default=None,
                   help="Custom regex of lines to DROP (overrides default)")
    p.add_argument("--raw", action="store_true",
                   help="Don't filter, stream the raw log")
    p.add_argument("--from-start", action="store_true",
                   help="Start from beginning of file (default: only new lines)")
    args = p.parse_args()

    interesting = (re.compile(args.pattern, re.IGNORECASE)
                   if args.pattern else DEFAULT_INTERESTING)
    noise = (re.compile(args.noise, re.IGNORECASE)
             if args.noise else DEFAULT_NOISE)

    cli = connect()
    print("Tailing %s on K2 (Ctrl-C to exit)..." % args.log,
          file=sys.stderr)

    cmd = "tail -F %s %s" % (
        "-n +1" if args.from_start else "-n 0",
        args.log)
    chan = cli.get_transport().open_session()
    chan.exec_command(cmd)
    chan.settimeout(0.5)

    buf = b""
    try:
        while True:
            try:
                chunk = chan.recv(4096)
                if not chunk:
                    time.sleep(0.2)
                    continue
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    s = line.decode("utf-8", errors="replace")
                    if args.raw:
                        print(s)
                        continue
                    if noise.search(s):
                        continue
                    if interesting.search(s):
                        print(s)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(0.2)
                continue
    finally:
        chan.close()
        cli.close()
        print("\nDisconnected.", file=sys.stderr)


if __name__ == "__main__":
    main()

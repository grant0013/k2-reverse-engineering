"""Shared SSH helper for the k2-reverse-engineering tool collection.

Reads connection details from environment variables so credentials never
land in the repo:

    K2_HOST    - printer IP or hostname (required)
    K2_USER    - SSH username (default: root)
    K2_PASS    - SSH password (required unless using --key)
    K2_KEY     - path to private key file (alternative to K2_PASS)

Usage from another script:

    from k2ssh import connect, run
    cli = connect()
    out = run(cli, "uname -a")
    print(out)
    cli.close()
"""
import os
import sys
import paramiko

DEFAULT_USER = "root"
DEFAULT_TIMEOUT = 15


def _env_or_die(name, default=None):
    val = os.environ.get(name, default)
    if val is None:
        sys.stderr.write(
            "ERROR: required environment variable %s is not set.\n" % name)
        sys.stderr.write(
            "Set it before running: export %s=...\n" % name)
        sys.exit(2)
    return val


def connect(host=None, user=None, password=None, key_filename=None,
            timeout=DEFAULT_TIMEOUT):
    """Open an SSH connection to the K2 and return the SSHClient.

    All args optional - falls back to K2_HOST / K2_USER / K2_PASS / K2_KEY
    environment variables. Caller is responsible for cli.close().
    """
    host = host or _env_or_die("K2_HOST")
    user = user or os.environ.get("K2_USER", DEFAULT_USER)
    if key_filename is None:
        key_filename = os.environ.get("K2_KEY")
    if password is None and key_filename is None:
        password = _env_or_die("K2_PASS")
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(
        hostname=host,
        username=user,
        password=password,
        key_filename=key_filename,
        timeout=timeout,
        banner_timeout=timeout,
        auth_timeout=timeout,
    )
    return cli


def run(cli, cmd, timeout=30):
    """Run a single shell command on the printer and return stdout text.

    stderr is appended (prefixed) if non-empty. Use this for one-shot
    commands; for streaming output use cli.exec_command directly.
    """
    si, so, se = cli.exec_command(cmd, timeout=timeout)
    out = so.read().decode("utf-8", errors="replace")
    err = se.read().decode("utf-8", errors="replace")
    if err.strip():
        out = out + "\n[stderr] " + err
    return out


if __name__ == "__main__":
    # Smoke test: connect, print uname, disconnect.
    cli = connect()
    print(run(cli, "uname -a; cat /etc/openwrt_release 2>/dev/null | head -3"))
    cli.close()

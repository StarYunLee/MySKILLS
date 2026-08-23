#!/usr/bin/env python3
"""Sign Apple Shortcuts files on user's Mac via SSH.

Usage:
  scripts/sign-shortcut-via-mac /path/to/draft.xml --name "My Shortcut" \
    --host user@MacBook-Pro.local

Environment defaults:
  SHORTCUTS_SIGN_MAC_HOST=user@MacBook-Pro.local
  SHORTCUTS_SIGN_MAC_TMP=/tmp/minis-shortcuts-sign
  SHORTCUTS_SIGN_MODE=anyone|people-who-know-me|local
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_OUTPUT_DIR = "/var/minis/attachments/shortcut"
SAFE_NAME_RE = re.compile(r"[\\/:*?\"<>|]+")
ASCII_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_name(name: str) -> str:
    cleaned = SAFE_NAME_RE.sub("-", name).strip().strip(".")
    return cleaned or "Shortcut"


def ascii_remote_name(name: str) -> str:
    cleaned = ASCII_SAFE_RE.sub("-", name).strip("-.")
    return cleaned or "shortcut"


def run(cmd: list[str], *, timeout: int, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=capture, timeout=timeout)


def shell_quote_single(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign Shortcuts XML/plist on macOS via ssh/scp")
    parser.add_argument("input_path")
    parser.add_argument("--name", help="Final shortcut display/file name")
    parser.add_argument("--host", default=os.environ.get("SHORTCUTS_SIGN_MAC_HOST"), help="SSH host, e.g. user@MacBook-Pro.local")
    parser.add_argument("--remote-dir", default=os.environ.get("SHORTCUTS_SIGN_MAC_TMP", "/tmp/minis-shortcuts-sign"))
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", default=os.environ.get("SHORTCUTS_SIGN_MODE", "anyone"), help="macOS shortcuts sign mode, default: anyone")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--keep-remote", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2
    if not args.host:
        print("Missing Mac SSH host. Pass --host user@Mac.local or set SHORTCUTS_SIGN_MAC_HOST.", file=sys.stderr)
        return 2
    for tool in ("ssh", "scp"):
        if shutil.which(tool) is None:
            print(f"{tool} not found on PATH", file=sys.stderr)
            return 127

    shortcut_name = safe_name(args.name or input_path.stem)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    remote_dir = args.remote_dir.rstrip("/") + f"/{stamp}-{os.getpid()}"
    remote_base = ascii_remote_name(input_path.stem)
    remote_input = f"{remote_dir}/{remote_base}{input_path.suffix or '.xml'}"
    remote_output = f"{remote_dir}/{remote_base}.shortcut"

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "drafts").mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "archive" / dt.datetime.now().strftime("%Y-%m-%d")
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{shortcut_name}-{dt.datetime.now().strftime('%H%M%S')}{input_path.suffix or '.xml'}"
    archive_path.write_bytes(input_path.read_bytes())

    try:
        proc = run(["ssh", args.host, "mkdir", "-p", remote_dir], timeout=args.timeout)
        if proc.returncode != 0:
            print(f"ssh mkdir failed: {(proc.stderr or proc.stdout).strip()}", file=sys.stderr)
            return 3

        proc = run(["scp", str(input_path), f"{args.host}:{remote_input}"], timeout=args.timeout)
        if proc.returncode != 0:
            print(f"scp upload failed: {(proc.stderr or proc.stdout).strip()}", file=sys.stderr)
            return 4

        # macOS shortcuts sign requires explicit --input/--output.
        q_in = shell_quote_single(remote_input)
        q_bin = shell_quote_single(remote_input + '.binary.shortcut')
        q_out = shell_quote_single(remote_output)
        q_mode = shell_quote_single(args.mode)
        remote_script = (
            "set -e; "
            "command -v shortcuts >/dev/null; "
            f"plutil -convert binary1 {q_in} -o {q_bin} >/tmp/minis-shortcuts-sign.log 2>&1; "
            f"shortcuts sign --mode {q_mode} --input {q_bin} --output {q_out} >>/tmp/minis-shortcuts-sign.log 2>&1"
        )
        proc = run(["ssh", args.host, remote_script], timeout=args.timeout)
        if proc.returncode != 0:
            log = run(["ssh", args.host, "cat /tmp/minis-shortcuts-sign.log 2>/dev/null || true"], timeout=20)
            detail = (log.stdout or proc.stderr or proc.stdout or "shortcuts sign failed").strip()
            print(f"Mac shortcuts sign failed: {detail}", file=sys.stderr)
            return 5

        local_output = output_dir / f"{shortcut_name}.shortcut"
        proc = run(["scp", f"{args.host}:{remote_output}", str(local_output)], timeout=args.timeout)
        if proc.returncode != 0:
            print(f"scp download failed: {(proc.stderr or proc.stdout).strip()}", file=sys.stderr)
            return 6

        data = local_output.read_bytes()
        if len(data) == 0:
            print("Signed shortcut is empty", file=sys.stderr)
            return 7
        # Apple signed shortcuts commonly begin with AEA1. Keep this as warning-compatible metadata,
        # because macOS version behavior may vary.
        header = data[:4].decode("latin1", "replace")
        result = {
            "ok": True,
            "method": "mac-ssh-shortcuts-sign",
            "host": args.host,
            "mode": args.mode,
            "input_path": str(input_path),
            "archive_path": str(archive_path),
            "output_path": str(local_output),
            "size": local_output.stat().st_size,
            "header4": header,
            "aea1_header": data[:4] == b"AEA1",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        if args.host and not args.keep_remote:
            subprocess.run(["ssh", args.host, "rm", "-rf", remote_dir], text=True, capture_output=True, timeout=20)


if __name__ == "__main__":
    raise SystemExit(main())

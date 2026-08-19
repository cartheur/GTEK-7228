#!/usr/bin/env python3
"""Program one or more Intel HEX files with a reset/select step between files."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send single-record Intel HEX files with a clean reselect between each file."
    )
    parser.add_argument("device", help="Serial device such as /dev/ttyUSB0")
    parser.add_argument("hex_files", nargs="+", help="Intel HEX files to send in order")
    parser.add_argument("--baud", type=int, default=2400, help="Baud rate, default 2400")
    parser.add_argument(
        "--select-code",
        default="MF",
        help="Selection command to return to the target device prompt, default MF",
    )
    parser.add_argument(
        "--manual-reset-between-files",
        action="store_true",
        help="Prompt for a manual reset/power-cycle between files before re-selecting the device",
    )
    parser.add_argument(
        "--handshake",
        choices=("none", "xonxoff", "rtscts"),
        default="none",
        help="Handshake for the Intel HEX sender, default none",
    )
    parser.add_argument(
        "--char-delay-ms",
        type=float,
        default=10.0,
        help="Character delay for Intel HEX sender, default 10 ms",
    )
    parser.add_argument(
        "--record-timeout-ms",
        type=float,
        default=8000.0,
        help="Record timeout for Intel HEX sender, default 8000 ms",
    )
    parser.add_argument(
        "--idle-timeout-ms",
        type=float,
        default=500.0,
        help="Idle timeout for Intel HEX sender, default 500 ms",
    )
    parser.add_argument(
        "--record-delay-ms",
        type=float,
        default=0.0,
        help="Extra delay after a record in one file send, default 0 ms",
    )
    parser.add_argument(
        "--between-files-ms",
        type=float,
        default=300.0,
        help="Pause after reselection before the next file, default 300 ms",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Pass verbose mode through to the Intel HEX sender",
    )
    return parser.parse_args()


def run_command(args: list[str]) -> None:
    result = subprocess.run(args, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    raw_sender = root / "gtek-send-raw.py"
    hex_sender = root / "gtek-send-intel-hex.py"

    for index, hex_file in enumerate(args.hex_files, start=1):
        print(f"== file {index}/{len(args.hex_files)}: {hex_file}")
        run_command(
            [
                sys.executable,
                str(hex_sender),
                args.device,
                hex_file,
                "--baud",
                str(args.baud),
                "--handshake",
                args.handshake,
                "--char-delay-ms",
                str(args.char_delay_ms),
                "--record-timeout-ms",
                str(args.record_timeout_ms),
                "--idle-timeout-ms",
                str(args.idle_timeout_ms),
                "--record-delay-ms",
                str(args.record_delay_ms),
                *(["--verbose"] if args.verbose else []),
            ]
        )
        if index < len(args.hex_files):
            if args.manual_reset_between_files:
                print(
                    "Reset the 7228 to a clean prompt now "
                    "(power-cycle if needed), then press Enter to continue...",
                    flush=True,
                )
                input()
            run_command(
                [
                    sys.executable,
                    str(raw_sender),
                    args.device,
                    args.select_code,
                    "--baud",
                    str(args.baud),
                    "--handshake",
                    "none",
                    "--append-cr",
                ]
            )
            time.sleep(args.between_files_ms / 1000.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

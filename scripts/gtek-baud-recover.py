#!/usr/bin/env python3
"""Perform the documented GTEK 7228 break + 0x80 + space baud recovery."""

from __future__ import annotations

import argparse
import os
import select
import sys
import termios
import time


def configure_port(fd: int, baud: int) -> None:
    attrs = termios.tcgetattr(fd)
    attrs[0] = termios.IGNPAR | termios.IXON | termios.IXOFF
    attrs[1] = 0
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0
    attrs[4] = baud_constant(baud)
    attrs[5] = baud_constant(baud)
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, attrs)


def baud_constant(baud: int) -> int:
    name = f"B{baud}"
    if not hasattr(termios, name):
        raise ValueError(f"Unsupported baud rate on this system: {baud}")
    return getattr(termios, name)


def send_break_sequence(fd: int, break_ms: int) -> None:
    termios.tcdrain(fd)
    termios.tcsendbreak(fd, 0)
    time.sleep(max(break_ms, 100) / 1000.0)
    time.sleep(0.010)
    os.write(fd, b"\x80")
    time.sleep(0.010)
    os.write(fd, b" ")
    termios.tcdrain(fd)


def read_response(fd: int, seconds: float) -> bytes:
    deadline = time.monotonic() + seconds
    chunks: list[bytes] = []
    while time.monotonic() < deadline:
        remaining = max(0.0, deadline - time.monotonic())
        ready, _, _ = select.select([fd], [], [], remaining)
        if not ready:
            break
        data = os.read(fd, 4096)
        if data:
            chunks.append(data)
    return b"".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Perform the GTEK 7228 documented baud recovery sequence."
    )
    parser.add_argument("device", help="Serial device such as /dev/ttyUSB0")
    parser.add_argument(
        "--baud",
        type=int,
        default=19200,
        help="Baud rate to use for the recovery sequence (default: 19200)",
    )
    parser.add_argument(
        "--break-ms",
        type=int,
        default=150,
        help="Break duration in milliseconds (default: 150)",
    )
    parser.add_argument(
        "--read-seconds",
        type=float,
        default=3.0,
        help="How long to read after sending the sequence (default: 3.0)",
    )
    args = parser.parse_args()

    try:
        fd = os.open(args.device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError as exc:
        print(f"Failed to open {args.device}: {exc}", file=sys.stderr)
        return 1

    try:
        configure_port(fd, args.baud)
        print(
            f"Sending break + 0x80 + space on {args.device} at {args.baud} baud...",
            file=sys.stderr,
        )
        send_break_sequence(fd, args.break_ms)
        response = read_response(fd, args.read_seconds)
    except Exception as exc:  # pragma: no cover
        print(f"Serial recovery failed: {exc}", file=sys.stderr)
        return 1
    finally:
        os.close(fd)

    if response:
        sys.stdout.buffer.write(response)
        if not response.endswith(b"\n"):
            sys.stdout.buffer.write(b"\n")
        return 0

    print("No readable response captured after recovery sequence.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

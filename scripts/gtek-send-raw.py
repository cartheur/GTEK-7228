#!/usr/bin/env python3
"""Send a short raw command string to a GTEK 7228 serial port."""

from __future__ import annotations

import argparse
import os
import select
import sys
import termios
import time


BAUD_MAP = {
    2400: termios.B2400,
    4800: termios.B4800,
    9600: termios.B9600,
    19200: termios.B19200,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a short raw command to a GTEK 7228.")
    parser.add_argument("device", help="Serial device such as /dev/ttyUSB0")
    parser.add_argument("text", help="Text to send, for example MF")
    parser.add_argument("--baud", type=int, default=2400, choices=sorted(BAUD_MAP))
    parser.add_argument(
        "--handshake",
        choices=("none", "xonxoff", "rtscts"),
        default="none",
        help="Host serial handshake setting, default none",
    )
    parser.add_argument(
        "--append-cr",
        action="store_true",
        help="Append carriage return after the text",
    )
    parser.add_argument(
        "--char-delay-ms",
        type=float,
        default=2.0,
        help="Delay between characters, default 2 ms",
    )
    parser.add_argument(
        "--read-ms",
        type=float,
        default=1500.0,
        help="How long to read response after sending, default 1500 ms",
    )
    return parser.parse_args()


def configure_port(fd: int, baud: int, handshake: str) -> None:
    attrs = termios.tcgetattr(fd)
    attrs[0] = termios.IGNPAR
    attrs[1] = 0
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0
    attrs[4] = BAUD_MAP[baud]
    attrs[5] = BAUD_MAP[baud]
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 1

    if hasattr(termios, "CRTSCTS"):
        attrs[2] &= ~termios.CRTSCTS
        if handshake == "rtscts":
            attrs[2] |= termios.CRTSCTS

    if hasattr(termios, "IXON"):
        attrs[0] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)
        if handshake == "xonxoff":
            attrs[0] |= termios.IXON | termios.IXOFF

    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIFLUSH)


def main() -> int:
    args = parse_args()
    fd = os.open(args.device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        configure_port(fd, args.baud, args.handshake)
        payload = args.text.encode("ascii")
        if args.append_cr:
            payload += b"\r"
        delay = args.char_delay_ms / 1000.0
        for byte in payload:
            os.write(fd, bytes([byte]))
            if delay > 0:
                time.sleep(delay)

        deadline = time.monotonic() + (args.read_ms / 1000.0)
        chunks: list[bytes] = []
        while time.monotonic() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if not ready:
                continue
            data = os.read(fd, 4096)
            if not data:
                continue
            chunks.append(data)

        sys.stdout.write(b"".join(chunks).decode("ascii", errors="replace"))
        sys.stdout.flush()
        return 0
    finally:
        os.close(fd)


if __name__ == "__main__":
    raise SystemExit(main())

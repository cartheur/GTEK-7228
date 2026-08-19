#!/usr/bin/env python3
"""Send Intel HEX records to a GTEK 7228 with explicit record pacing."""

from __future__ import annotations

import argparse
import os
import select
import sys
import termios
import time
from pathlib import Path


BAUD_MAP = {
    2400: termios.B2400,
    4800: termios.B4800,
    9600: termios.B9600,
    19200: termios.B19200,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send Intel HEX to a GTEK 7228 one record at a time."
    )
    parser.add_argument("device", help="Serial device such as /dev/ttyUSB0")
    parser.add_argument("hex_file", help="Intel HEX file to send")
    parser.add_argument(
        "--baud",
        type=int,
        default=2400,
        choices=sorted(BAUD_MAP),
        help="Baud rate, default 2400",
    )
    parser.add_argument(
        "--handshake",
        choices=("none", "xonxoff", "rtscts"),
        default="none",
        help="Host serial handshake setting, default none",
    )
    parser.add_argument(
        "--char-delay-ms",
        type=float,
        default=2.0,
        help="Delay between transmitted characters, default 2 ms",
    )
    parser.add_argument(
        "--record-timeout-ms",
        type=float,
        default=4000.0,
        help="Overall timeout waiting for one record response, default 4000 ms",
    )
    parser.add_argument(
        "--idle-timeout-ms",
        type=float,
        default=500.0,
        help="Consider a record complete after this much quiet time, default 500 ms",
    )
    parser.add_argument(
        "--record-delay-ms",
        type=float,
        default=0.0,
        help="Extra pause after a successfully echoed record, default 0 ms",
    )
    parser.add_argument(
        "--start-record",
        type=int,
        default=1,
        help="1-based record number to start sending from, default 1",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=0,
        help="Maximum number of records to send, default 0 for all",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print record progress and received data",
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


def read_hex_records(path: Path) -> list[str]:
    records = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise SystemExit(f"Not an Intel HEX record: {line!r}")
        records.append(line)
    if not records:
        raise SystemExit("No Intel HEX records found.")
    return records


def read_available(fd: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        ready, _, _ = select.select([fd], [], [], 0)
        if not ready:
            break
        data = os.read(fd, 4096)
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks)


def wait_for_any_feedback(
    fd: int,
    timeout_s: float,
    verbose: bool,
) -> bytes:
    deadline = time.monotonic() + timeout_s
    received = bytearray()
    while time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if not ready:
            continue
        data = os.read(fd, 4096)
        if not data:
            continue
        received.extend(data)
        if verbose:
            sys.stdout.write(data.decode("ascii", errors="replace"))
            sys.stdout.flush()
        if received:
            return bytes(received)
    return bytes(received)


def wait_for_record_response(
    fd: int,
    timeout_s: float,
    idle_timeout_s: float,
    verbose: bool,
) -> bytes:
    deadline = time.monotonic() + timeout_s
    last_data_at: float | None = None
    received = bytearray()
    while time.monotonic() < deadline:
        now = time.monotonic()
        if last_data_at is not None and (now - last_data_at) >= idle_timeout_s:
            return bytes(received)
        wait_s = 0.05
        if last_data_at is not None:
            wait_s = min(wait_s, max(idle_timeout_s - (now - last_data_at), 0.0))
        ready, _, _ = select.select([fd], [], [], wait_s)
        if not ready:
            continue
        data = os.read(fd, 4096)
        if not data:
            continue
        received.extend(data)
        last_data_at = time.monotonic()
        if verbose:
            sys.stdout.write(data.decode("ascii", errors="replace"))
            sys.stdout.flush()
    return bytes(received)


def has_error_marker(response: bytes) -> bool:
    upper = response.decode("ascii", errors="replace").upper()
    return "*DT ERR" in upper or "*ST ERR" in upper or "*SN ERR" in upper or "*NE ERR" in upper or "*CS ERR" in upper


def send_record(
    fd: int,
    record: str,
    char_delay_s: float,
    timeout_s: float,
    idle_timeout_s: float,
    verbose: bool,
) -> tuple[bool, bytes]:
    payload = record.encode("ascii")
    received = bytearray()
    for byte in payload:
        os.write(fd, bytes([byte]))
        feedback = wait_for_any_feedback(fd, timeout_s, verbose)
        received.extend(feedback)
        if not feedback:
            return False, bytes(received)
        if char_delay_s > 0:
            time.sleep(char_delay_s)
    os.write(fd, b"\r")
    response = bytes(received) + wait_for_record_response(fd, timeout_s, idle_timeout_s, verbose)
    if has_error_marker(response):
        return False, response
    return True, response


def main() -> int:
    args = parse_args()
    records = read_hex_records(Path(args.hex_file))
    start_index = max(args.start_record - 1, 0)
    if start_index >= len(records):
        raise SystemExit("start-record is past the end of the file")

    selected = records[start_index:]
    if args.max_records > 0:
        selected = selected[: args.max_records]

    fd = os.open(args.device, os.O_RDWR | os.O_NOCTTY)
    try:
        configure_port(fd, args.baud, args.handshake)
        char_delay_s = args.char_delay_ms / 1000.0
        timeout_s = args.record_timeout_ms / 1000.0
        idle_timeout_s = args.idle_timeout_ms / 1000.0
        record_delay_s = args.record_delay_ms / 1000.0

        stale = read_available(fd)
        if stale and args.verbose:
            sys.stdout.write(stale.decode("ascii", errors="replace"))
            sys.stdout.flush()

        for index, record in enumerate(selected, start=args.start_record):
            print(f"[record {index}] {record}")
            ok, response = send_record(
                fd,
                record,
                char_delay_s,
                timeout_s,
                idle_timeout_s,
                args.verbose,
            )
            if not ok:
                print("\nERROR: record did not complete cleanly.", file=sys.stderr)
                if response:
                    print(
                        response.decode("ascii", errors="replace"),
                        file=sys.stderr,
                    )
                return 1
            if record_delay_s > 0:
                time.sleep(record_delay_s)
            else:
                time.sleep(0.05)
        return 0
    finally:
        os.close(fd)


if __name__ == "__main__":
    raise SystemExit(main())

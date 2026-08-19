#!/usr/bin/env python3
"""Send a short raw command string to a GTEK 7228 serial port."""

from __future__ import annotations

import argparse
import array
import fcntl
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

MODEM_MASKS = {
    "CTS": getattr(termios, "TIOCM_CTS", 0),
    "DTR": getattr(termios, "TIOCM_DTR", 0),
    "RTS": getattr(termios, "TIOCM_RTS", 0),
    "DSR": getattr(termios, "TIOCM_DSR", 0),
    "CD": getattr(termios, "TIOCM_CAR", getattr(termios, "TIOCM_CD", 0)),
    "RI": getattr(termios, "TIOCM_RI", 0),
}


class ModemControlUnavailable(RuntimeError):
    """Raised when the current serial device does not support modem-line ioctls."""


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
    parser.add_argument(
        "--drive-dtr",
        choices=("keep", "high", "low"),
        default="keep",
        help="Drive host DTR intentionally. With the 5-wire cable, host DTR feeds 7228 CTS. Default keep",
    )
    parser.add_argument(
        "--wait-cts",
        choices=("ignore", "high", "low"),
        default="ignore",
        help="Wait on host CTS before each byte. With the 5-wire cable, host CTS reflects 7228 DTR. Default ignore",
    )
    parser.add_argument(
        "--cts-timeout-ms",
        type=float,
        default=3000.0,
        help="Timeout while waiting for CTS state, default 3000 ms",
    )
    parser.add_argument(
        "--show-modem",
        action="store_true",
        help="Print modem-line state before sending",
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


def get_modem_bits(fd: int) -> int:
    bits = array.array("i", [0])
    try:
        fcntl.ioctl(fd, termios.TIOCMGET, bits, True)
    except OSError as exc:
        raise ModemControlUnavailable(str(exc)) from exc
    return int(bits[0])


def set_modem_bit(fd: int, mask: int, enabled: bool) -> None:
    bits = array.array("i", [mask])
    request = termios.TIOCMBIS if enabled else termios.TIOCMBIC
    try:
        fcntl.ioctl(fd, request, bits)
    except OSError as exc:
        raise ModemControlUnavailable(str(exc)) from exc


def format_modem_bits(bits: int) -> str:
    names = [name for name, mask in MODEM_MASKS.items() if mask and (bits & mask)]
    if not names:
        return "(none)"
    return " ".join(names)


def apply_dtr_policy(fd: int, drive_dtr: str) -> None:
    if drive_dtr == "keep":
        return
    set_modem_bit(fd, MODEM_MASKS["DTR"], enabled=(drive_dtr == "high"))


def wait_for_cts_state(fd: int, desired: str, timeout_s: float, show_modem: bool) -> None:
    if desired == "ignore":
        return
    want_high = desired == "high"
    deadline = time.monotonic() + timeout_s
    last_report = None
    while time.monotonic() < deadline:
        bits = get_modem_bits(fd)
        cts_high = bool(bits & MODEM_MASKS["CTS"])
        if cts_high == want_high:
            if show_modem:
                print(f"[modem] ready CTS={'HIGH' if cts_high else 'LOW'} {format_modem_bits(bits)}")
            return
        if show_modem:
            report = f"CTS={'HIGH' if cts_high else 'LOW'} {format_modem_bits(bits)}"
            if report != last_report:
                print(f"[modem] waiting for CTS {'HIGH' if want_high else 'LOW'}; saw {report}")
                last_report = report
        time.sleep(0.01)
    raise TimeoutError(f"timed out waiting for CTS {desired}")


def main() -> int:
    args = parse_args()
    fd = os.open(args.device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        configure_port(fd, args.baud, args.handshake)
        try:
            apply_dtr_policy(fd, args.drive_dtr)
            if args.show_modem:
                print(f"[modem] {format_modem_bits(get_modem_bits(fd))}")
        except ModemControlUnavailable as exc:
            if args.drive_dtr != "keep" or args.wait_cts != "ignore" or args.show_modem:
                print(
                    f"ERROR: modem-line control unavailable on {args.device}: {exc}",
                    file=sys.stderr,
                )
                return 2
        payload = args.text.encode("ascii")
        if args.append_cr:
            payload += b"\r"
        delay = args.char_delay_ms / 1000.0
        for byte in payload:
            try:
                wait_for_cts_state(
                    fd,
                    args.wait_cts,
                    args.cts_timeout_ms / 1000.0,
                    args.show_modem,
                )
            except ModemControlUnavailable as exc:
                print(
                    f"ERROR: modem-line wait failed on {args.device}: {exc}",
                    file=sys.stderr,
                )
                return 2
            except TimeoutError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 3
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

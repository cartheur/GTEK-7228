#!/usr/bin/env python3
"""Build a padded 27128 image and Intel HEX from a smaller ROM payload."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_int(value: str) -> int:
    return int(value, 0)


def emit_intel_hex(image: bytes, start_offset: int = 0, width: int = 16) -> str:
    lines: list[str] = []
    for offset in range(start_offset, len(image), width):
        chunk = image[offset : offset + width]
        count = len(chunk)
        address = offset & 0xFFFF
        record_type = 0
        body = bytes([count, (address >> 8) & 0xFF, address & 0xFF, record_type]) + chunk
        checksum = (-sum(body)) & 0xFF
        lines.append(":" + (body + bytes([checksum])).hex().upper())
    lines.append(":00000001FF")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pad a ROM payload into a 27128-sized image and emit Intel HEX."
    )
    parser.add_argument("input_bin", help="Source binary payload")
    parser.add_argument("output_prefix", help="Output path prefix without extension")
    parser.add_argument(
        "--cpu-base",
        type=parse_int,
        required=True,
        help="CPU address where the payload is assembled to run, e.g. 0xF800",
    )
    parser.add_argument(
        "--eprom-base",
        type=parse_int,
        default=0xC000,
        help="CPU address of EPROM offset 0x0000, default 0xC000",
    )
    parser.add_argument(
        "--eprom-size",
        type=parse_int,
        default=0x4000,
        help="EPROM size in bytes, default 0x4000 for 27128",
    )
    args = parser.parse_args()

    input_path = Path(args.input_bin)
    output_prefix = Path(args.output_prefix)
    payload = input_path.read_bytes()

    offset = args.cpu_base - args.eprom_base
    if offset < 0:
        raise SystemExit("cpu-base is below eprom-base; cannot place payload")
    if offset + len(payload) > args.eprom_size:
        raise SystemExit("payload does not fit inside EPROM image")

    image = bytearray([0xFF] * args.eprom_size)
    image[offset : offset + len(payload)] = payload

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    bin_path = output_prefix.with_suffix(".bin")
    hex_path = output_prefix.with_suffix(".hex")
    meta_path = output_prefix.with_suffix(".txt")

    bin_path.write_bytes(image)
    hex_path.write_text(emit_intel_hex(bytes(image)))
    meta_path.write_text(
        "\n".join(
            [
                f"source={input_path}",
                f"payload_bytes=0x{len(payload):X}",
                f"eprom_size=0x{args.eprom_size:X}",
                f"eprom_base=0x{args.eprom_base:04X}",
                f"cpu_base=0x{args.cpu_base:04X}",
                f"payload_offset=0x{offset:04X}",
                "",
            ]
        )
    )

    print(f"wrote {bin_path}")
    print(f"wrote {hex_path}")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

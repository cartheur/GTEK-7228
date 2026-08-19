#!/usr/bin/env python3
"""Inspect an Intel HEX capture saved from the GTEK terminal."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Record:
    line_number: int
    address: int
    record_type: int
    data: bytes


def parse_record(line: str, line_number: int) -> Record | None:
    line = line.strip()
    if not line.startswith(":"):
        return None

    payload = line[1:]
    if len(payload) < 10 or len(payload) % 2:
        raise ValueError(f"line {line_number}: malformed Intel HEX record")

    try:
        raw = bytes.fromhex(payload)
    except ValueError as exc:
        raise ValueError(f"line {line_number}: non-hex content in record") from exc

    length = raw[0]
    if len(raw) != length + 5:
        raise ValueError(
            f"line {line_number}: byte count {length} does not match record length"
        )

    checksum = sum(raw) & 0xFF
    if checksum != 0:
        raise ValueError(f"line {line_number}: checksum mismatch")

    address = (raw[1] << 8) | raw[2]
    record_type = raw[3]
    data = raw[4:-1]
    return Record(line_number=line_number, address=address, record_type=record_type, data=data)


def expected_size(value: str) -> int:
    aliases = {
        "2716": 0x800,
        "2732": 0x1000,
        "2764": 0x2000,
        "27128": 0x4000,
        "27256": 0x8000,
        "27512": 0x10000,
    }
    lowered = value.lower()
    if lowered in aliases:
        return aliases[lowered]
    return int(value, 0)


def summarize(path: Path, expected_bytes: int | None) -> int:
    records: list[Record] = []
    ignored_lines = 0

    for line_number, raw_line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        record = parse_record(stripped, line_number)
        if record is None:
            ignored_lines += 1
            continue
        records.append(record)

    if not records:
        print(f"{path}: no Intel HEX records found", file=sys.stderr)
        return 1

    data_records = [
        record for record in records if record.record_type == 0 and len(record.data) > 0
    ]
    eof_records = [record for record in records if record.record_type == 1]
    zero_length_data_records = [
        record for record in records if record.record_type == 0 and len(record.data) == 0
    ]
    unsupported = [record for record in records if record.record_type not in (0, 1)]

    if unsupported:
        print(
            f"{path}: unsupported record types present: "
            + ", ".join(str(record.record_type) for record in unsupported[:5]),
            file=sys.stderr,
        )
        return 1

    if not data_records:
        print(f"{path}: no data records found", file=sys.stderr)
        return 1

    ranges: list[tuple[int, int]] = []
    for record in data_records:
        start = record.address
        end = record.address + len(record.data) - 1
        ranges.append((start, end))

    ranges.sort()
    first_address = ranges[0][0]
    last_address = max(end for _, end in ranges)

    gaps: list[tuple[int, int]] = []
    cursor = ranges[0][1] + 1
    for start, end in ranges[1:]:
        if start > cursor:
            gaps.append((cursor, start - 1))
        cursor = max(cursor, end + 1)

    total_data_bytes = sum(len(record.data) for record in data_records)

    print(f"file: {path}")
    print(f"data records: {len(data_records)}")
    print(f"ignored non-record lines: {ignored_lines}")
    print(f"eof records: {len(eof_records)}")
    print(f"zero-length data records: {len(zero_length_data_records)}")
    print(f"address range: 0x{first_address:04X}-0x{last_address:04X}")
    print(f"data bytes captured: 0x{total_data_bytes:X} ({total_data_bytes})")

    if gaps:
        print("internal gaps: yes")
        for gap_start, gap_end in gaps[:10]:
            print(f"gap: 0x{gap_start:04X}-0x{gap_end:04X}")
        if len(gaps) > 10:
            print(f"additional gaps not shown: {len(gaps) - 10}")
    else:
        print("internal gaps: no")

    if expected_bytes is not None:
        expected_last = expected_bytes - 1
        print(f"expected size: 0x{expected_bytes:X} ({expected_bytes})")
        if first_address > 0:
            print(f"missing leading range: 0x0000-0x{first_address - 1:04X}")
        else:
            print("missing leading range: none")
        if last_address < expected_last:
            print(f"missing trailing range: 0x{last_address + 1:04X}-0x{expected_last:04X}")
        else:
            print("missing trailing range: none")
        if not gaps and first_address == 0 and last_address == expected_last:
            print("status: complete contiguous dump")
        else:
            print("status: incomplete or non-contiguous dump")
    else:
        print("status: parsed capture without expected-size check")

    if not eof_records:
        print("warning: no standard Intel HEX EOF record found")
    if zero_length_data_records:
        print("warning: zero-length data records found; capture may contain a non-standard terminator")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a saved GTEK terminal capture containing Intel HEX output."
    )
    parser.add_argument("capture", help="Path to the saved terminal capture")
    parser.add_argument(
        "--expected-size",
        type=expected_size,
        help="Expected ROM size in bytes or chip alias such as 27128",
    )
    args = parser.parse_args()

    return summarize(Path(args.capture), args.expected_size)


if __name__ == "__main__":
    raise SystemExit(main())

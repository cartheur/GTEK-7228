# ROM Test Patterns

These tiny files are for transport diagnostics with the `GTEK 7228`.

## `27128-one-record-0000.hex`

Contains exactly one Intel HEX data record:

- address `0x0000`
- `16` bytes of `FF`

Use this file to answer one narrow question:

- can the current serial path get through one Intel HEX record cleanly before the 7228 faults?

Observed result on Wednesday, August 19, 2026:

- this one-line file still produced `*DT ERR @ 0010` on the `MODEL 7228 V7.07` under test
- that means the problem is not limited to a second Intel HEX record or to the EOF record
- the `P` path is already unstable within a single 16-byte data record

Expected follow-up on the programmer:

1. Send this one-line file only.
2. The `7228` may not reissue the prompt because no Intel HEX end record is included.
3. Use `Device -> Send Space (<space>)` to try to reissue the prompt.
4. Read back the first 16 bytes with `R0,0F` or `OI0,0F`.

This is a transport test, not a final burn file.

## `27128-one-record-0000-distinct.hex`

Contains exactly one Intel HEX data record:

- address `0x0000`
- bytes `00` through `0F`

Use this file to answer:

- can the current path program a single non-`FF` Intel HEX record at `0x0000`?

## `27128-two-records-0000-0010.hex`

Contains:

- one Intel HEX data record for `0x0000-0x000F`
- one Intel HEX data record for `0x0010-0x001F`
- the Intel HEX EOF record

Use this file to answer the next question:

- once single-record `P`-mode pacing is understood, can the current serial path handle a controlled two-record Intel HEX transfer when the file ends cleanly with EOF?

Expected follow-up on the programmer:

1. Send this file.
2. Wait for the `7228` to finish the transfer.
3. Read back `R0,1F` or `OI0,1F`.

This is still a transport test, not a final burn file.

## `27128-two-records-distinct.hex`

Contains:

- one Intel HEX data record for `0x0000-0x000F` with bytes `00` through `0F`
- one Intel HEX data record for `0x0010-0x001F` with bytes `F0` through `FF`
- the Intel HEX EOF record

Use this file when a blank-`FF` test is too ambiguous.

Expected follow-up on the programmer:

1. Send this file.
2. Wait for the `7228` to finish the transfer.
3. Read back `R0,1F`.

Expected readback if programming succeeds:

- `000102030405060708090A0B0C0D0E0FF0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF`

## `27128-one-record-0010.hex`

Contains exactly one Intel HEX data record:

- address `0x0010`
- bytes `F0` through `FF`

Use this only after a clean first-record `P`-mode test to answer:

- can the current serial path program the second record when it is sent as its own file action?

## `intel-hex-eof-only.hex`

Contains only the Intel HEX EOF record.

Use this after separate one-record file sends to close the Intel HEX session cleanly.

Do not assume the EOF record is the source of `*DT ERR @ 0010`.
The August 19, 2026 single-record test showed that the fault can happen before any EOF record is sent.

## Dedicated sender script

For transport tests outside the Tcl/Tk app, use:

```bash
./scripts/gtek-send-intel-hex.py DEVICE FILE.hex --baud 2400 --handshake none --verbose
```

The sender currently treats a record as successful when:

- the `7228` provides feedback during the record
- the line then goes quiet for the configured idle timeout
- no explicit `*.. ERR` marker is seen

This is intentional. On this `MODEL 7228 V7.07` unit, successful one-record programming was confirmed by readback even when a perfect full-record echo was not always observed.

Example sequence for controlled multi-step tests:

```bash
./scripts/gtek-send-intel-hex.py /dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0 ROMs/test-patterns/27128-one-record-0000.hex --baud 2400 --handshake none --verbose
./scripts/gtek-send-intel-hex.py /dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0 ROMs/test-patterns/27128-one-record-0010.hex --baud 2400 --handshake none --verbose
./scripts/gtek-send-intel-hex.py /dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0 ROMs/test-patterns/intel-hex-eof-only.hex --baud 2400 --handshake none --verbose
```

## Separated-record helper

For the currently proven fallback workflow on the `MODEL 7228 V7.07` unit, use:

```bash
./scripts/gtek-send-separated-records.py /dev/ttyUSB0 \
  ROMs/test-patterns/27128-one-record-0000-distinct.hex \
  ROMs/test-patterns/27128-one-record-0010.hex \
  --baud 2400 --handshake none --char-delay-ms 10 --record-timeout-ms 8000 \
  --manual-reset-between-files
```

This helper:

- sends one Intel HEX file
- lets you reset the `7228` to a clean prompt between files when requested
- then re-selects the target device with `MF`
- sends the next Intel HEX file

Use it when continued multi-record Intel HEX sessions fail.

As of Wednesday, August 19, 2026, the stronger bench conclusion is that even single-record Intel HEX `P` transfers are still pacing-sensitive on this `MODEL 7228 V7.07` unit.

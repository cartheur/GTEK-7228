# First Bring-Up On Debian

This is the practical first-pass workflow for diagnosing a dusty GTEK 7228 on a modern Debian machine.

For this repo's current bring-up plan, the preferred host adapter is the `Eminent EM1016 USB-to-RS232` device.

Use this document when the goal is:

- confirm the serial adapter and cable are electrically correct
- confirm the Linux host can talk to the 7228
- recover an unknown baud rate
- capture the first visible prompt or output

This guide is intentionally biased toward first contact, not high-speed production transfers.

## 1. What "success" looks like

For the first session, success is any one of these:

- the 7228 emits readable serial text
- a prompt reappears after the baud recovery sequence
- the unit reacts consistently to a space character or other terminal input

Do not make EPROM programming the first goal. First prove that the serial path is alive.

## 2. Hardware baseline

Start with the simplest known-good wiring:

- `TXD`
- `RXD`
- `GND`

If you have the `Eminent EM1016`, start there. It is the preferred path because it is already `RS-232`.

If you are using a TTL USB UART instead, it must go through an RS-232 transceiver first.

Allowed:

- `Eminent EM1016 USB-to-RS232` adapter with the correct cable
- another real `USB-to-RS232` adapter with the correct cable
- `USB TTL UART -> MAX232/MAX233/MAX3232 -> GTEK 7228`

Do not connect a TTL UART directly to the 7228 DB25 port.
Do not use a `USB-parallel` adapter here either, even if it has a similar connector shell.

More wiring detail is in [serial-adapter-guide.md](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/docs/serial-adapter-guide.md).
The preferred cable build is in [cable-build.md](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/docs/cable-build.md).

## 3. Debian host prerequisites

This workflow uses only standard local tools:

- `bash`
- `stty`
- `dd`
- `timeout`
- `python3`

You do not need `minicom`, `picocom`, or `pyserial` for the first pass in this repo.

For a richer future interactive interface, this repo also includes `terminal/gtek-terminal.tcl`, which uses the system `wish` Tcl/Tk runtime.

## 4. Find the serial device

Plug in the adapter, then check:

```bash
ls -l /dev/serial/by-id
```

If that directory is empty, also check:

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Use the stable `/dev/serial/by-id/...` path when possible.

## 5. Check permissions

You need read/write access to the serial device.

Quick check:

```bash
id
```

If you are not in `dialout` or the equivalent serial-access group for your system, fix that before spending time on higher-level debugging.

## 6. Configure the port

The safest first-pass configuration is:

- `19200`
- `8n1`
- no hardware flow control at first
- software flow control enabled

That means we deliberately begin with:

- `TXD`
- `RXD`
- `GND`
- `XON/XOFF`

and not with extra handshake wires.

Important observed exception for this repo's current bench unit:

- on `2026-08-19`, the specific `MODEL 7228 V7.07` unit under test responded repeatably after cold power-up at `2400 8n1 xonxoff`
- for this unit, treat `2400` as the first manual fallback when a fresh power-cycle gives no prompt at the higher default probing rates

Use:

```bash
./scripts/gtek-serial-setup.sh /dev/ttyUSB0
```

If your adapter path is different, replace `/dev/ttyUSB0` with the actual device.

To force hardware flow control later:

```bash
./scripts/gtek-serial-setup.sh --hwflow /dev/ttyUSB0
```

Use that only after the simpler 3-wire path is proven.

## 7. Capture output during power-up

This is the simplest first observation:

1. Configure the port.
2. Start a capture.
3. Power-cycle or reset the 7228.

Example:

```bash
timeout 10s dd if=/dev/ttyUSB0 bs=1 status=none | tee first-contact.log
```

If you see readable ASCII, you already have enough evidence to keep going.

If you see nothing, continue with baud recovery.

## 8. Recover an unknown baud rate

The repo documentation says the 7228 can be reinitialized by:

1. sending a break for more than `100 ms`
2. waiting at least `5 ms`
3. sending byte `0x80` at the target baud rate
4. sending a space character to reissue the prompt

This repo now includes a helper for that:

```bash
./scripts/gtek-baud-recover.py /dev/ttyUSB0
```

By default it uses `19200` baud and reads back for a few seconds after the sequence.

To try another baud:

```bash
./scripts/gtek-baud-recover.py --baud 9600 /dev/ttyUSB0
```

## 8a. Interactive terminal option

Once the serial path is stable, you can also use the Tcl/Tk terminal in this repo:

```bash
./terminal/gtek-terminal.tcl
```

Or specify the exact device explicitly:

```bash
./terminal/gtek-terminal.tcl -device /dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0
```

The script defaults to:

- `19200`
- `8n1`
- `xonxoff`
- EM1016-style `/dev/serial/by-id/...` naming

It is intended for stable interactive use after first contact is proven.

## 9. Interpreting first results

Readable text:

- cable polarity is likely correct
- voltage translation is likely correct
- baud is likely correct or close enough

No output at all:

- check TX/RX crossover
- check that the adapter is really RS-232 level on the 7228 side
- check common ground
- try power-cycle while capture is already running
- try baud recovery

Garbled text:

- likely wrong baud rate
- sometimes wrong flow control choice
- occasionally marginal voltage conversion or grounding

Output appears only briefly:

- keep capture running before power-up
- try software flow control first
- add handshake lines only after the 3-wire path is proven

## 10. Recommended first bench sequence

Use this exact order:

1. Verify the EM1016 adapter path and cable wiring.
2. Use a 3-wire connection first.
3. Find the Debian serial device.
4. Run `gtek-serial-setup.sh`.
5. Capture while powering the 7228 on.
6. If silent, run `gtek-baud-recover.py`.
7. If still silent, revisit electrical assumptions before chasing software.
8. Only then fall back to a TTL-plus-transceiver path if needed.

## 11. What this repo does not prove yet

This repo does not yet prove:

- the exact software workflow for full device programming on Debian
- the exact preferred transfer format for every operation
- whether the historical DOS bundle is required for a later stage

For first bring-up, that is fine. The immediate goal is serial life signs and a stable prompt.

## 12. Historical software bundle

The `80s-software/pgmx7.zip` archive contains period GTEK software and documents, including:

- `PGMX7.COM`
- `PGMX7.DOC`
- `README.DOC`
- `SEARCHER.EXE`
- format-fix tools such as `FIXHEX.EXE`

Treat that bundle as a preserved historical reference for later exploration, not the first dependency for initial diagnosis on Debian.

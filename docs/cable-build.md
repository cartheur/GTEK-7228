# GTEK 7228 Cable Build

This is the shortest path to a working cable between a modern Debian box and a GTEK 7228.

The rear-panel photo in [images/back.jpg](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/images/back.jpg) shows the connector that often gets mistaken for a parallel port. For first bring-up, treat it as a `DB25 RS-232 serial` connector and ignore the fact that many physical positions exist on the shell.

## Recommended approach

Use a real `USB-to-RS232` adapter if you can. It is the simplest and least error-prone path.

If you only have a `USB-to-TTL UART`, you must add an `RS-232` transceiver stage such as:

- `MAX232`
- `MAX233`
- `MAX3232`

Do not connect a TTL serial adapter directly to the 7228 DB25 port.

## Option A: simplest cable

Recommended parts:

- `1x` Debian box with `USB`
- `1x` real `USB-to-RS232` adapter
- `1x` `DB25 female` connector for the 7228 side
- cable, hood, solder cups, heatshrink

### Finished wiring map: USB-RS232 DB9 to 7228 DB25

This is the cleanest first cable if your USB serial adapter ends in a standard PC-style `DB9 male`.

Build this exact cable first:

| USB-RS232 adapter `DB9 male` | 7228 `DB25 female` | Purpose |
| --- | --- | --- |
| pin `2` `RXD` | pin `2` `TXD` | receive data from the 7228 |
| pin `3` `TXD` | pin `3` `RXD` | send data to the 7228 |
| pin `5` `GND` | pin `7` `SG` | signal ground |

Leave the other pins open for the first pass.

### Minimal 3-wire pinout

This is the best first-pass cable for bring-up.

| Host side | 7228 DB25 | Meaning |
| --- | --- | --- |
| `TXD` | pin `3` | host sends data to 7228 `RXD` |
| `RXD` | pin `2` | host receives data from 7228 `TXD` |
| `GND` | pin `7` | signal ground |

Those three pins are the only ones you need to prove first contact.

Everything else can be left unconnected for the first pass.

If your adapter presents a `DB9` male PC-style serial connector, the usual mapping is:

| DB9 male | 7228 DB25 female | Meaning |
| --- | --- | --- |
| pin `2` `RXD` | pin `2` `TXD` | receive from 7228 |
| pin `3` `TXD` | pin `3` `RXD` | send to 7228 |
| pin `5` `GND` | pin `7` `SG` | common ground |

### Optional handshake lines

Only add these after the 3-wire cable works.

| Host side | 7228 DB25 | Meaning |
| --- | --- | --- |
| `DTR` | pin `5` | drives 7228 `CTS` |
| `CTS` | pin `20` | reads 7228 `DTR` |

If your adapter is a standard `DB9 male`, that usually means:

| USB-RS232 adapter `DB9 male` | 7228 `DB25 female` | Purpose |
| --- | --- | --- |
| pin `4` `DTR` | pin `5` `CTS` | optional host-to-7228 flow control |
| pin `8` `CTS` | pin `20` `DTR` | optional 7228-to-host flow control |

For clarity, that means the first useful pins on the 7228 side are:

- pin `2` = data out of the 7228
- pin `3` = data into the 7228
- pin `7` = signal ground
- pin `5` = optional flow-control input
- pin `20` = optional flow-control output

All other DB25 positions can be ignored unless later testing proves you need them.

## Option B: TTL adapter plus transceiver

Recommended parts:

- `1x` USB TTL serial adapter
- `1x` `MAX232`, `MAX233`, or `MAX3232`
- `1x` `DB25 female` connector
- perfboard or module wiring

If your TTL adapter is the `DSD TECH SH-U09C5` already mentioned elsewhere in this repo, use the exact map below.

Minimal signal chain:

`Debian box -> USB TTL UART -> RS-232 transceiver -> GTEK 7228`

### Minimal 3-wire mapping through the transceiver

TTL side:

- USB UART `TXD` -> transceiver TTL input
- USB UART `RXD` <- transceiver TTL output
- USB UART `GND` -> transceiver `GND`

RS-232 side:

- transceiver RS-232 `TX` -> 7228 DB25 pin `3`
- 7228 DB25 pin `2` -> transceiver RS-232 `RX`
- transceiver `GND` -> 7228 DB25 pin `7`

If you are using a classic `MAX232`, remember it normally needs the charge-pump capacitors from the datasheet.

### Finished wiring map: SH-U09C5 to MAX233 to 7228 DB25

This is the exact build if you are using the `SH-U09C5` plus a `MAX233`.

| From | To | Purpose |
| --- | --- | --- |
| `SH-U09C5 TXD` | `MAX233 pin 2` `T1IN` | TTL transmit into the transceiver |
| `SH-U09C5 RXD` | `MAX233 pin 3` `R1OUT` | TTL receive from the transceiver |
| `SH-U09C5 GND` | `MAX233 pin 6` `GND` | common ground |
| `SH-U09C5 5V` | `MAX233 pin 7` `VCC` | power the transceiver |
| `MAX233 pin 5` `T1OUT` | 7228 `DB25 pin 3` `RXD` | RS-232 transmit into the 7228 |
| 7228 `DB25 pin 2` `TXD` | `MAX233 pin 4` `R1IN` | RS-232 receive from the 7228 |
| 7228 `DB25 pin 7` `SG` | `MAX233 pin 6` `GND` | common ground |

That is enough for first contact.

Do not add handshake wiring until this 3-wire path works.

### Optional handshake map: SH-U09C5 to MAX233 to 7228 DB25

Only if your adapter exposes usable control pins and you actually need them later:

| From | To | Purpose |
| --- | --- | --- |
| host-side `DTR` | `MAX233 pin 1` `T2IN` | optional TTL-side control input |
| `MAX233 pin 18` `T2OUT` | 7228 `DB25 pin 5` `CTS` | optional RS-232 control to the 7228 |
| 7228 `DB25 pin 20` `DTR` | `MAX233 pin 19` `R2IN` | optional RS-232 control from the 7228 |
| `MAX233 pin 20` `R2OUT` | host-side `CTS` | optional TTL-side control back to the host |

## Parts checklist

Minimum build:

- `DB25 female` connector
- connector hood
- 3-conductor cable
- soldering tools
- continuity meter

If using TTL plus transceiver:

- transceiver IC or module
- stable `5V` supply where required
- capacitor set required by the exact transceiver

## Bench checks before plugging in

Use a meter before powering anything:

1. Confirm host `TXD` reaches 7228 `RXD`.
2. Confirm host `RXD` reaches 7228 `TXD`.
3. Confirm ground is continuous end to end.
4. Confirm there is no short between pins `2`, `3`, and `7`.
5. If handshake is wired, confirm `DTR -> 5` and `CTS <- 20`.

## First-use settings on Debian

Start with:

- `19200`
- `8n1`
- software flow control first
- no hardware flow control until the 3-wire path is proven

Use:

```bash
./scripts/gtek-serial-setup.sh /dev/ttyUSB0
```

Then try capture or recovery using [first-bringup-debian.md](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/docs/first-bringup-debian.md).

## Strong recommendation

If you have a choice, build the `USB-to-RS232 -> DB25 female` cable first.

It removes the biggest source of avoidable mistakes:

- wrong voltage standard
- wrong polarity assumption
- extra transceiver wiring errors

The TTL-plus-transceiver path is valid, but it should be plan B, not plan A.

## Build choice

If you are deciding what to fabricate today:

1. Build `USB-RS232 DB9 male -> 7228 DB25 female` first if you have the adapter.
2. Build `SH-U09C5 -> MAX233 -> 7228 DB25 female` only if a real USB-RS232 adapter is not available.

# GTEK 7228 Serial Adapter Guide

This note collects the practical hardware details for connecting a modern USB serial adapter to the GTEK 7228 programmer. For the current experimental work in this repo, assume a `MAX232`-based interface is the default DIY path unless noted otherwise.

## Summary

The GTEK 7228 programmer interface is a `DB25` **RS-232 serial** port configured as `DTE`.

That means:

- A `USB-to-TTL UART` adapter does **not** connect directly to the programmer.
- A `USB-to-RS232` adapter can connect with the proper cable pinout.
- A `USB-to-TTL UART` adapter can still be used if it is followed by an `RS-232 transceiver` such as a `MAX232`, `MAX233`, or `MAX3232`.

For this project's hands-on experiments, the working assumption is:

`PC -> USB TTL UART -> MAX232 -> GTEK 7228`

## The Main Compatibility Rule

The important distinction is not the connector shell. It is the signaling standard.

- `TTL UART`: low-voltage logic serial, typically `0 V / 3.3 V` or `0 V / 5 V`
- `RS-232`: serial signaling with different voltage levels and polarity

A `DB25` connector does **not** automatically mean parallel port, and it does **not** automatically mean TTL serial. On the 7228, the `DB25` is used for an `RS-232` serial port.

## GTEK 7228 Programmer Port

The rear-panel connector visible in [images/back.jpg](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/images/back.jpg) is physically a `DB25`, but for first bring-up only a few serial pins matter. Do not assume every visible position is used.

From the programmer interface documentation in the repo:

| Pin | Signal | Direction | Notes |
| --- | --- | --- | --- |
| 1 | EG | <--> | Equipment ground |
| 2 | TXD | --> | Data transmitted by the 7228 |
| 3 | RXD | <-- | Data received by the 7228 |
| 4 | RTS | --> | Always active when power is on |
| 5 | CTS | <-- | High enables 7228 to transmit |
| 6 | DSR | <-- | Not used |
| 7 | SG | <--> | Signal ground |
| 20 | DTR | --> | High when programmer is willing to accept data |

## Using a USB-to-RS232 Adapter

This is the simplest modern solution.

Use a real `USB-to-RS232` adapter and wire it like a PC serial port:

- host `RXD` <- 7228 `TXD` (`DB25 pin 2`)
- host `TXD` -> 7228 `RXD` (`DB25 pin 3`)
- host `GND` -> 7228 `SG` (`DB25 pin 7`)

Optional hardware flow control:

- host `CTS` <- 7228 `DTR` (`DB25 pin 20`)
- host `DTR` -> 7228 `CTS` (`DB25 pin 5`)

## Using a USB-to-TTL UART Adapter

This is possible, but only if you add an `RS-232` transceiver stage.

Correct signal chain:

`PC -> USB TTL UART -> RS-232 transceiver -> GTEK 7228`

Examples of suitable transceivers:

- `MAX232` (`5V` logic-side supply, classic choice for this repo's experimental setup)
- `MAX233`
- `MAX3232`
- compatible `TTL <-> RS-232` modules

Examples of parts that are **not** suitable for this conversion:

- `TXS1008`
- `TXB0108`
- generic logic level shifters

Those parts only translate logic voltage levels such as `3.3 V <-> 5 V`. They do not generate RS-232 signaling.

## SH-U09C5 USB-to-TTL UART Adapter

The `DSD TECH SH-U09C5` can be used only on the TTL side of the interface.

Important points:

- Its `3.3 V / 5 V` setting controls `TTL` logic behavior and/or the exposed VCC level.
- Setting it to `5 V` does **not** make it an `RS-232` adapter.
- It should not be wired directly to the 7228 `DB25` serial pins.

Correct usage:

`SH-U09C5 -> MAX232/MAX233/MAX3232 -> GTEK 7228`

## Minimal 3-Wire Build

For first bring-up, start with only:

- `TXD`
- `RXD`
- `GND`

Wiring:

- USB-TTL adapter `TXD` -> transceiver TTL receive input
- USB-TTL adapter `RXD` <- transceiver TTL transmit output
- USB-TTL adapter `GND` -> transceiver `GND`

Then connect the RS-232 side to the 7228:

- transceiver RS-232 `TX` -> 7228 `DB25 pin 3` (`RXD`)
- transceiver RS-232 `RX` <- 7228 `DB25 pin 2` (`TXD`)
- transceiver `GND` -> 7228 `DB25 pin 7` (`SG`)

This is enough to start testing communications.

## Optional Hardware Flow Control

The 7228 also exposes handshake behavior on:

- `DB25 pin 5` = `CTS` input to the programmer
- `DB25 pin 20` = `DTR` output from the programmer

If your adapter and software support it, you can also wire:

- host-side `DTR` -> 7228 `CTS` (`DB25 pin 5`)
- host-side `CTS` <- 7228 `DTR` (`DB25 pin 20`)

For early testing, it is reasonable to begin without these lines.

## XON/XOFF and Software Handshaking

The 7228 documentation also describes software flow control:

- the programmer may use `XON/XOFF`
- the programmer accepts `XON/XOFF`
- this can be useful if hardware flow control is not wired

For initial experiments, software flow control is often the easiest place to start.

## Baud Rate Recovery

If the 7228 is at an unknown baud rate, the documented reinitialization method is:

1. Send a `break` signal for more than `100 ms`.
2. Wait at least `5 ms` after releasing the break.
3. Send byte `0x80` at the baud rate you want to use.
4. Send a space character to cause the prompt to be reissued.

## DIY Circuit with a MAX232

If you are building from parts, a `MAX232` is the primary documented solution for the current experimental work.

Important practical note:

- A classic `MAX232` is normally a `5V` part.
- It needs the charge-pump capacitors shown in its datasheet.
- If your USB UART only exposes `3.3V` logic, do not assume that is a drop-in match for a classic `MAX232` build without checking the exact module and transceiver variant.

Typical parts:

- `1x MAX232`
- `4x 1 uF` charge-pump capacitors
- `1x 0.1 uF` supply decoupling capacitor
- `1x DB25 female` connector
- header or jumper wires for the USB-TTL adapter
- small perfboard or prototype PCB

Minimal connection concept:

- USB-TTL `TXD` -> `MAX232 T1IN`
- `MAX232 R1OUT` -> USB-TTL `RXD`
- USB-TTL `5V` -> `MAX232 VCC`
- USB-TTL `GND` -> `MAX232 GND`

RS-232 side:

- `MAX232 T1OUT` -> 7228 `DB25 pin 3`
- 7228 `DB25 pin 2` -> `MAX232 R1IN`
- `GND` -> 7228 `DB25 pin 7`

This `3-wire` arrangement is the baseline bring-up configuration for the `MAX232` experiment.

## DIY Circuit with a MAX233

The `MAX233` is also suitable and can simplify the build because it typically integrates the charge-pump capacitors internally.

That means the wiring idea is similar to the `MAX232` build, but with fewer external support parts.

Typical parts:

- `1x MAX233`
- `1x 0.1 uF` supply decoupling capacitor
- `1x DB25 female` connector
- header or jumper wires for the USB-TTL adapter
- small perfboard or prototype PCB

For the `MAX233CPP` `DIP-20` package, the useful pins for this project are:

| Pin | Name | Side | Use in this build |
| --- | --- | --- | --- |
| 2 | `T1IN` | TTL input | Connect from USB-TTL adapter `TXD` |
| 3 | `R1OUT` | TTL output | Connect to USB-TTL adapter `RXD` |
| 4 | `R1IN` | RS-232 input | Connect from 7228 `DB25 pin 2` (`TXD`) |
| 5 | `T1OUT` | RS-232 output | Connect to 7228 `DB25 pin 3` (`RXD`) |
| 6 | `GND` | Power | Common ground |
| 7 | `VCC` | Power | `+5V` supply |
| 1 | `T2IN` | TTL input | Optional second channel for handshake |
| 18 | `T2OUT` | RS-232 output | Optional second channel for handshake |
| 19 | `R2IN` | RS-232 input | Optional second channel for handshake |
| 20 | `R2OUT` | TTL output | Optional second channel for handshake |

The local datasheet in this repo should be treated as the primary pinout reference for the `MAX233CPP` package:

- `docs/MAX220.PDF`

The Futurlec page for `MAX233CPP` is also useful as a quick secondary reference and identifies it as a `+5V` `RS-232` transceiver with integrated charge pump and no external capacitors:

- https://www.futurlec.com/Maxim/MAX233CPP.shtml

### MAX233CPP Minimal Wiring Table

This is the simplest working `3-wire` arrangement with the `SH-U09C5`:

| From | To | Notes |
| --- | --- | --- |
| `SH-U09C5 TXD` | `MAX233 pin 2` (`T1IN`) | TTL transmit into the transceiver |
| `SH-U09C5 RXD` | `MAX233 pin 3` (`R1OUT`) | TTL receive from the transceiver |
| `SH-U09C5 GND` | `MAX233 pin 6` (`GND`) | Common ground |
| `SH-U09C5 5V` | `MAX233 pin 7` (`VCC`) | Power the `MAX233` from `+5V` |
| `MAX233 pin 5` (`T1OUT`) | 7228 `DB25 pin 3` (`RXD`) | RS-232 transmit into the programmer |
| 7228 `DB25 pin 2` (`TXD`) | `MAX233 pin 4` (`R1IN`) | RS-232 receive from the programmer |
| 7228 `DB25 pin 7` (`SG`) | `MAX233 pin 6` (`GND`) | Common ground |

### Optional MAX233CPP Handshake Wiring

If you want to experiment with the second channel for handshaking, these are the relevant pins:

| Purpose | Connection |
| --- | --- |
| host-side `DTR` into transceiver | `MAX233 pin 1` (`T2IN`) |
| transceiver RS-232 output to 7228 `CTS` | `MAX233 pin 18` (`T2OUT`) -> 7228 `DB25 pin 5` |
| 7228 `DTR` into transceiver | 7228 `DB25 pin 20` -> `MAX233 pin 19` (`R2IN`) |
| transceiver TTL output to host-side `CTS` | `MAX233 pin 20` (`R2OUT`) |

If your USB-TTL adapter does not expose usable `DTR` and `CTS` pins, skip this section and start with the minimal `3-wire` build.

## What Not to Do

Do not connect any of these directly to the 7228 `DB25` serial port:

- `FT232`-style TTL boards
- `CH340` TTL UART boards
- `CP2102` TTL UART boards
- `TXS1008` logic translators
- generic `3.3 V / 5 V` logic shifters

They are the wrong electrical interface unless an `RS-232` transceiver stage is added.

## Recommended Bring-Up Order

1. Start with a `3-wire` connection: `TXD`, `RXD`, `GND`.
2. Use a proper `RS-232` transceiver or a real `USB-to-RS232` adapter.
3. Try software flow control first.
4. If needed, add the `CTS/DTR` handshake wiring.
5. If the baud rate is unknown, use the documented `break + 0x80` recovery sequence.

## References

- Main project README: `README.md`
- GTEK manual in this repo: `docs/users-manual.pdf`
- MAX220/MAX233 family datasheet in this repo: `docs/MAX220.PDF`

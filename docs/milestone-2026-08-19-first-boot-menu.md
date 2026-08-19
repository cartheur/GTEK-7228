# Milestone - 2026-08-19 First Boot To Menu

This note records the first confirmed successful interactive boot of the `GTEK 7228` over the serial link.

## Status

As of `2026-08-19`, the programmer powers correctly, communicates over serial, and reaches the interactive EPROM selection menu.

Observed prompt and interaction sequence:

- power-up prompt appears as `xxxx>`
- sending `M` followed by `Enter` returns the full `EPROM SELECTION MENU`
- the unit is therefore alive, running firmware, and responding normally to terminal commands

This closes the main bring-up uncertainty that originally presented as "system does not power up."

## Working serial wiring

The current successful link uses only the minimal `3-wire` serial connection:

- `DB9 pin 2` -> `GTEK DB25 pin 2`
- `DB9 pin 3` -> `GTEK DB25 pin 3`
- `DB9 pin 5` -> `GTEK DB25 pin 7`

This is sufficient for power-up prompt, menu access, and basic interactive terminal use.

## Extra wires present but not currently used

Two additional wires were prepared in the cable but are not required for the current successful bring-up state.

Those are the optional hardware-flow-control lines:

- `DB9 pin 4` -> `GTEK DB25 pin 5`
- `DB9 pin 8` -> `GTEK DB25 pin 20`

They are intentionally left disconnected for now.

At the current stage, there is no demonstrated need to use them. They may become useful later for:

- hardware handshaking experiments
- higher-speed transfer stability
- behavior that benefits from explicit `CTS/DTR` flow control

For now, the repo's confirmed working baseline remains the `3-wire` serial hookup.

## Practical conclusion

The repo now has a verified end-to-end path for:

- power-up
- terminal connection
- prompt capture
- menu interaction

The next work, if any, is no longer first bring-up. It is operational exploration and device-specific use.

For saved terminal captures of ROM reads, the repo also includes `scripts/check-intel-hex-capture.py` to verify whether an Intel HEX dump is complete or begins partway through.

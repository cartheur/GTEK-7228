# 1980s Software Findings - 2026-08-19

This note captures the most useful findings from the original `GTEK` software bundle now stored under:

- `80s-software/gtek/`

The goal is to preserve the software-era facts that still matter for the `MODEL 7228` without mixing them with later experiments.

## Key Findings

### 1. Continued Intel HEX records are expected

The original docs treat Intel HEX as a continued stream of records, not a one-record-only operation.

From `README.DOC`:

- `OI` is the Intel HEX output command
- `P` is the ASCII-hex program command
- Intel HEX files are expected as a normal interchange format

This matches the programmer manual's description that the `7228` accepts one Intel HEX record and then remains ready for another until the end record arrives.

### 2. The 7228 is still a 2400-baud class device

From `PGMX7.DOC`:

- the `7128` is limited to `1200`
- the `7228` and `7956` are limited to `2400`

That reinforces the current August 19, 2026 bench observation that `2400` remains the conservative starting point for this `V7.xx` unit.

### 3. PGMX7 is not actually for the 7228

The clearest software-era warning is explicit in `PGMX7.DOC`:

- `PGMX IS NOT AVAILABLE FOR THE 7128, 7228, 7956.`

That matters because it means later `PGMX7` behavior should not be treated as the canonical host model for a `7228`.

### 4. The old cable mapping is DTR/CTS-oriented, not generic RTS/CTS

From `README.DOC`, the cable table for a `GTEK` programmer to a PC-style DTE says:

- `GTEK TXD 2 -> PC RXD 3`
- `GTEK RXD 3 -> PC TXD 2`
- `GTEK CTS 5 -> PC DTR 20`
- `GTEK DTR 20 -> PC CTS 5`

It also lists:

- `GTEK RTS 4 -> PC DSR 6`
- `GTEK DSR 6 -> PC RTS 4`

This is a strong reminder that the original hardware flow-control expectations are built around the programmer's `CTS` input and `DTR` output, not the simpler modern assumption that `rtscts` on a host OS is automatically the exact same thing.

### 5. The original DOS host software also waits on CTS before sending

A light inspection of `PGMX7.COM` and `PGMX7A.COM` adds one useful software-era clue:

- the binaries contain the literal message `Hardware error - Cant send. CTS low. ESCAPE to abort.`
- they also log `Sending record at address` and `Reading record at address`
- `PGMX7.COM` identifies its configured serial path as `2400 bps`

That does not prove the exact byte-for-byte transport algorithm used by the original host, but it does confirm that the shipping DOS-side tooling treated `CTS` as a hard gate on transmit, not as an optional status bit.

### 6. Repeated syntax errors can kick the programmer into baud recovery

From `README.DOC`:

- three syntax errors in a row can cause the programmer to go looking for a new baud rate
- recovery then involves aborting the send and transmitting spaces so the unit locks back onto the baud rate

That explains why failed programming sessions can leave the unit appearing confused or out of phase even when the cable is still physically correct.

## Current Interpretation For This Repo

As of Wednesday, August 19, 2026, the strongest repo-supported interpretation is:

- the `7228` can program single Intel HEX records correctly on the modern Debian path
- continued multi-record Intel HEX sessions are still not behaving like the original software/manual path expects
- the original host software expected a real `CTS`-gated send path, while our present Linux/Tcl path only approximates that behavior
- generic host `rtscts` should be treated as an approximation, not a proven implementation of the original `7228` flow-control model

## Practical Takeaway

The original software bundle is worth keeping because it preserves:

- period-correct cable expectations
- the intended baud-rate envelope
- the fact that the original DOS-side sender explicitly checked `CTS` before transmit
- the warning that `PGMX7` is not the right mental model for the `7228`
- the clue that bad command sequences can kick the unit into baud-recovery behavior

Those points are more valuable than any individual experimental workaround attempted on August 19, 2026.

# PGMX7 Send Loop Notes - 2026-08-19

This note captures the most useful serial-send-loop clues recovered from the original `PGMX7.COM` DOS binary on Wednesday, August 19, 2026.

The goal is not a perfect decompilation. The goal is to preserve the parts that are strong enough to guide a modern reimplementation of the `7228` programming transport.

## Why This Matters

The live `MODEL 7228 V7.07` unit still reports `*DT ERR @ 0010` during Intel HEX `P` transfers even after the modern Tcl sender was corrected to stop relying on echo matching.

At this point, the highest-value next step is to mimic the original DOS sender more faithfully.

One caution for the next session:

- the manual's `P` command description is for raw ASCII-hex byte data terminated by `$`
- that is not the same thing as Intel HEX `:` records
- the manual also states that a leading `:` in command state is itself a valid direct Intel HEX programming path
- any transliteration of the DOS sender must preserve that distinction instead of collapsing everything into raw `P ... $`

## Strong Findings From `PGMX7.COM`

These are directly supported by string extraction and disassembly.

- `PGMX7.COM` is not just a generic terminal wrapper. It programs the UART directly with `out` instructions.
- It installs an interrupt-driven serial path.
- It uses buffered receive logic rather than simple blocking character-at-a-time reads.
- It explicitly checks a modem-control condition associated with `CTS` before transmit.
- It contains the message:
  - `Hardware error - Cant send. CTS low. ESCAPE to abort.`
- It also contains:
  - `Sending record at address`
  - `Reading record at address`
  - `Warning - RS232 Receiver Overrun. Reduce baud rate.`
  - `Warning - RS232 Framing Error.`

## Most Interesting Code Regions

### 1. Transmit gate around `0x11f`

The code at about `0x11f` appears to inspect UART/modem status before allowing transmit.

The rough behavior is:

- load UART-related base from memory
- step to a control/status register
- read a status byte
- test a modem-control-related bit
- if that bit indicates not-ready, do not transmit
- otherwise allow transmit to proceed

The wrapper around it at about `0x112` calls this gate and only performs the `out` to the transmit register if the gate says it is OK.

Practical interpretation:

- the original sender did not just dump characters blindly
- it had a real transmit-ready gate before putting bytes on the wire

### 2. Interrupt-driven receive path around `0x1f2`

The interrupt routine around `0x1f2`:

- reads a received byte from the UART
- appends it into a ring buffer
- maintains a byte count
- when the count reaches a threshold, writes back to a control register

The threshold compare near `0x21e` checks for `0x1e` bytes in the buffer.

Practical interpretation:

- the host software was designed around asynchronous buffered receive, not synchronous "send one char, wait for exact echo" logic
- this fits the manual's statement that echoed characters reflect FIFO drain, not programming success

### 3. UART initialization around `0x13b`

The setup code around `0x13b`:

- initializes UART registers directly
- installs an interrupt vector
- unmasks the proper IRQ
- appears to use a COM-port base stored in memory

Practical interpretation:

- `PGMX7` expected a specific serial configuration and controlled it tightly
- modern generic channel/terminal settings may still be close, but they are not obviously identical

### 4. Error inspection around `0x23c`

The routine around `0x23c` reads a UART status register and prints warnings for:

- receiver overrun
- framing error

Practical interpretation:

- the original software explicitly watched serial error bits during operation
- a modern sender should probably log transport-state clues much more explicitly than our current tools do

## Best Current Mental Model

The old DOS sender likely behaved more like this:

1. Configure the UART directly.
2. Enable interrupt-driven receive into a ring buffer.
3. Before each transmitted byte, check whether the line is clear to send.
4. Transmit only when the gate allows it.
5. Let received bytes accumulate asynchronously.
6. Watch the receive stream for the programmer's real outcomes:
   - prompt return
   - error replies beginning with `*`
   - flow-control behavior
7. Also watch the UART for host-side framing/overrun trouble.

That is much closer to a small state machine than to a terminal paste operation.

## Modern Reimplementation Sketch

If we transliterate this behavior into Python for the `7228`, the first serious attempt should probably look like:

```text
open serial port at 2400 8N1
configure chosen host flow-control mode
start a background receive buffer

for each outgoing character in one Intel HEX record:
    wait until host-side transmit gate says "ready"
    write one character
    allow receive side to process XON/XOFF, prompt, and error text asynchronously
    if receive side reports '*' error:
        abort the record immediately

send CR at end of record

then wait for one of:
    explicit '*...ERR'
    returned '>' prompt
    quiet period that the manual-consistent state machine accepts as "record drained"
```

## What This Does And Does Not Prove

What it supports strongly:

- the original host software had a real transmit gate
- it was interrupt/buffer driven
- it watched serial health explicitly

What it does not yet prove:

- the exact bit meanings for every register without a fuller reverse-engineering pass
- the exact byte pacing delay constants used by the DOS program
- whether `PGMX7` is fully representative of the `7228` path in every detail

## Best Next Step

The best next engineering task is:

- separate the manual's raw `P ... $` ascii-hex path from the Intel HEX record path before implementing anything else
- treat direct colon-led Intel HEX records from command state as a first-class programming path
- extract the `PGMX7` transmit/receive state machine more carefully
- write the resulting behavior down as tighter pseudocode
- then implement that state machine in a dedicated Python sender for the `7228`

The Tcl app should remain the interactive terminal, not the primary burn workflow.

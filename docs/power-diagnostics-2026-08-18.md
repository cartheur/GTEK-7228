# Power Diagnostics - 2026-08-18

This note records the first successful power-supply measurements taken during bench bring-up of the `GTEK 7228`.

## Symptom

Initial symptom was that the unit appeared not to power up and showed no obvious activity.

## Fuse finding

The input fuse was physically worn and "beat up" even though it still had continuity.

It was replaced with a fresh `1 A fast-blow` fuse on a like-for-like basis.

Do not substitute a `slow-blow` fuse unless the chassis or original power documentation explicitly requires it.

## Transformer identification

The transformer in [parts/XC-600058.pdf](/home/cartheur/ame/aiventure/aiventure-github/cartheur/GTEK-7228/parts/XC-600058.pdf) is specified as:

- primary `115 VAC`, `60 Hz`
- secondary `27.9 VAC CT` no-load
- secondary `24.0 VAC CT` full-load
- rated secondary current `0.6 A AC`

That means the expected secondary is approximately:

- `27.9 VAC` end-to-end
- `13.95 VAC` from either end to the center tap

## Bench measurements

After replacing the fuse and applying approximately `115 VAC` to the primary:

- transformer secondary measured `27 VAC` across `red` to `red`
- transformer secondary measured `13.7 VAC` across `red` to `white`
- a `7805` regulator measured approximately `15 VDC` input
- the same `7805` measured approximately `4.92 VDC` output

These readings are consistent with a healthy transformer and a functioning `+5 V` logic regulator path.

Additional variac measurement:

- at `100 VAC` primary input, the transformer secondary measured `23.7 VAC`
- at that same `100 VAC` input, the logic rail still measured `4.92 VDC`

## Variac note

The `100 VAC` variac setting was used deliberately because of other Japanese-based power-supply requirements on the bench.

For this transformer specifically, the nominal intended input remains `115 VAC`.

The `100 VAC` result is useful as a diagnostic observation showing that the logic rail still regulates at that reduced input, but it should not be treated as proof that all startup, timing, serial, or programming-voltage behavior is valid at reduced mains.

## Practical conclusion

The original "dead unit" symptom was at least partly due to the degraded input fuse.

After fuse replacement, the transformer secondary and `7805` regulator readings show that the power supply is alive and the main `+5 V` logic rail is present.

Further troubleshooting should proceed as functional bring-up:

- serial output at power-up
- reset behavior
- clock activity
- socketed IC contact integrity

# Goal Note - 2026-08-19

The current project goal is:

- create a working `27128` EPROM containing `ASSIST09`
- use that EPROM to test bring-up in the sister `M6809-SBC` project

## What Is Already Ready

- the padded `27128` `ASSIST09` image has already been built
- the placement assumption for the sister board is documented and plausible
- the `GTEK 7228` is proven to:
  - power up
  - communicate over serial
  - read EPROM contents

## What Is Still Blocking Final Completion

The remaining blocker is not the `ASSIST09` image itself.

The remaining blocker is the modern host-to-`7228` transport path for Intel HEX programming in `P` mode.

As of Wednesday, August 19, 2026:

- raw serial interactivity is confirmed working
- readback commands are confirmed working
- a stricter one-line single-record Intel HEX `P` test still fails with `*DT ERR @ 0010`
- the blocker is therefore narrower and uglier than first thought: the `P` transfer path itself is not yet trustworthy enough for a full `ASSIST09` burn

## Practical Interpretation

This means the repo has already advanced past the image-building stage.

The active problem is now:

- finish a trustworthy burn workflow on the `7228`

so that the already-prepared `ASSIST09` image can be committed to a real `27128` EPROM for the sister `M6809-SBC`.

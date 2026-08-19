# 27128 Image Layout Notes

These notes document the current assumptions used to build padded `27128` images from smaller ROM payloads for the M6x09-II SBC sister repo.

## Working Assumption

Assume a `27128` EPROM is mapped into the CPU address space as:

- EPROM offset `0x0000` -> CPU address `0xC000`
- EPROM offset `0x3FFF` -> CPU address `0xFFFF`

That gives a contiguous `16 KB` ROM window from `0xC000` to `0xFFFF`.

## ASSIST09 Placement

From the sister repo:

- `ROMBEG EQU $F800`
- payload size is `0x0800` bytes (`2 KB`)

So `assist09.bin` is placed at:

- CPU address `0xF800`
- EPROM offset `0x3800`

## forth09 Placement

From the sister repo:

- `ORG $E000`
- payload size is `0x164F` bytes (`5711` bytes observed on 2026-08-19)

So `forth09.bin` is placed at:

- CPU address `0xE000`
- EPROM offset `0x2000`

## Important Caveat

These placements are only correct if the target board really maps the full `27128` into `0xC000-0xFFFF`.

Do not burn from these images blindly if the target hardware decodes ROM differently.

## Builder

The repo helper used for these images is:

- `scripts/build-27128-image.py`

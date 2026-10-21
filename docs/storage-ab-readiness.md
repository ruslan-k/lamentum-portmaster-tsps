# Storage A/B readiness: a frame comparison that can prove "identical"

The next candidate from `docs/menu-target-inventory.md` is reducing the three
1920×1080 colour targets (and their depth) to 1280×720. That is a **quality-changing**
change, and this project's own rule is that texture-storage policy changes need
explicit approval plus UV/wrap/LOD/pixel parity. This document is the measurement
half that can be prepared without touching the renderer.

`tools/frame_diff.py` compares two decoded frames of the same geometry:

- differing-pixel count and ratio beyond a tolerance (default 2/255);
- maximum and mean channel delta;
- per-horizontal-band ratios, so "only the text moved" is distinguishable from
  "the whole picture shifted";
- refusals for geometry or size mismatches, and an `identical()` gate that is only
  true when the comparison ran and no pixel exceeded the **configured tolerance**. The default tolerance is 2/255, so this is **not necessarily byte-identical** output; use tolerance=0 for an exact equality claim.

6 tests cover identity, in-tolerance noise, a real difference, a localised change
found in the correct band, size/geometry refusal and single-channel frames.

## What is still blocked, and on what

The storage change itself is **not implemented**: it would alter sampling for
targets the game reads with its own UVs, and approving that is the user's call, not
an autonomous one. When approved the plan is: default-off switch, one factor,
strict GL, 300 MiB texture budget unchanged, capture the same menu screen with the
switch off and on, and require `identical()` — otherwise revert.

Measured context for the decision: those four images are **31.64 MiB** charged before scaling; at 1280×720 they would require **14.06 MiB**, giving at most **17.58 MiB nominal storage reduction**, not a proven Mali physical-memory win. The menu loses around 76 MiB of available RAM and drains a roughly 28 MiB CMA pool in ~4.5 s.

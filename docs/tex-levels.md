# M1: the 2.09x texture gap is decoded-vs-compressed, not mip chains

Reviewed 2aba2d3 / owner §48.5. Answers the open question from §68 by splitting
the declared texture payload instead of guessing. Observation only: no
admission, budget, format, deletion or quality change.

## What was added (build247, still default off)

The opt-in ledger now classifies each texture request without adding any GL
change:

- `tex-l0` / `tex-mips`: level 0 versus additional mip levels;
- `tex-scaled` / `tex-half`: the host-reduced variants;
- `tex-charged` / `tex-uncharged`: requests whose texture carries a budget
  charge (`t2_budget_bytes != 0`) versus those outside the budget;
- `tex-guest`: for charged textures, the guest-side storage (`t->size`, i.e. the
  compressed BC payload for BC formats).

Host fixture asserts each bucket and keeps the stop-path formatter equal to
snprintf across all fields.

## Measured arm tex-levels-02

ELF ecef4ba2075946095e69120137366850c41184d26e3e82c995cdd98995bd6575, floor96/
cap300/strict GL, principal flow, no input:

    tex-bytes=241485104 tex-live=90      (230.30 MiB live, decoded)
    tex-l0=247062780  tex-mips=713780    (0.68 MiB of extra levels)
    tex-scaled=0      tex-half=0
    tex-charged=247776560  tex-uncharged=0
    tex-guest=107024384                  (102.07 MiB guest/compressed)
    budget charge at the last interval: 115278848 (109.94 MiB), 93 live

Conclusions that follow directly:

1. **Mip chains do not explain the gap.** Extra levels total 0.68 MiB
   (0.29 % of the payload). The earlier hypotheses "budget counts level 0 only"
   and "multi-mip undercharge" are both refuted for this phase.
2. **Scope does not explain the gap.** Every declared texture request belongs to
   a charged texture (`tex-uncharged=0`); nothing bypasses the budget.
3. **The basis explains it.** The budget is denominated in the guest/compressed
   storage (102.07 MiB), while GL holds the decoded pixels (230.30 MiB live,
   241.72 MiB including depth). Decoded/guest = 2.256; declared/charge = 2.095.
   The small residual between `tex-guest` (107.02 MB) and the charge
   (115.28 MB, 7.7 %) is **not** explained by this arm and is recorded as open.

This matters for the memory wall: a 300 MiB texture cap is expressed in
compressed guest bytes, so it does not bound GL residency — at this measured
ratio the cap corresponds to roughly 675 MiB of decoded storage on a 963 MiB
board. That is a statement about accounting, not yet about a fix; no cap,
admission or format policy was changed.

## Device result

STOP `T2_MEMORY_FLOOR`, no OOM receipt, cleanup `[]`; game0, MainUI/principal/
runtime1, CPU4-7, no pending launch, debugfs unmounted; DRM capture shows the
Spruce home. Build247 deployed by staged write + fsync + atomic replace with
independent hash read-back, build246 kept as `.before-247`. Host 273 tests PASS
in a clean index export; build247 435/435.

## Next

The residual 7.7 % and the physical side are what remain: either the charge
includes textures created just after the last interval line, or it uses a
slightly different size rule. Next step is a per-texture pairing (guest size,
decoded size, charge) for a bounded set, then the same comparison against
`gpu_memory` once its unit is derived. Menu headroom, world and 30 FPS remain
OPEN.

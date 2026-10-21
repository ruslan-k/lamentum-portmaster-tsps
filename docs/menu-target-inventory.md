# Menu colour-target inventory (owner §40.6 / B2-lite, second step)

Build232 `a9b516e0…8957` (435/435) emits a bounded per-target receipt
(`LC2_MENU_TARGET`, at most 32 lines, once per run, when `MemAvailable` first drops
below 64 MiB). One arm `menu-targets-01`: `T2_MEMORY_FLOOR` stop, verified identity,
zero cleanup errors, **19 targets listed**, total charged **43.39 MiB** — matching
the independently measured colour-target estimate of 43.4 MiB in `menu-ledger-02`.

## What the menu actually holds

| class | count | charged | ids | draws |
|---|---|---|---|---|
| **1920×1080** (colour ×3 + depth ×1) | 4 | **31.64 MiB** | 2, 3, 4, 28 | 200 |
| 1280×720 (colour ×2 + depth ×1) | 3 | 10.55 MiB | 172, 173, 206 | 534 |
| post-chain cascade 640×360 → 1×1 | 12 | 1.21 MiB | 211…225, 260 | 231 |

Details worth naming:

- **Three 1920×1080 RGBA8 colour targets (7.91 MiB each) plus a 1920×1080 depth
  target** exist although the panel is 1280×720. Their 31.64 MiB is the largest
  single class in the menu and it is *larger than the panel*, so it cannot be
  explained by presentation size.
- The busiest target is **id 172 (1280×720, 513 draws)**, with its depth at id 173 —
  that is the on-screen menu work; the 1920 trio carries 200 draws total.
- The cascade is a mip-like chain (640×360, 320×180, 160×90, 80×45, … 1×1) with 21
  draws each; because the allocator charges a 4 KiB floor per image, its twelve
  entries cost only 1.21 MiB — a real but minor class.
- Every listed target has `target-seen=1`, and `references` is 1–2, so none of them
  is obviously orphaned *by this counter*; `last-used-serial` does not exist yet,
  which is exactly what the §40.6 B2 ledger must add before anything may be freed.

## Why this matters for 30 FPS and for memory

The 1920×1080 targets are the same class the owner's §32.9 table lists under GPU
fill: internal render targets at a resolution above the panel. Their 31.64 MiB is
also the largest reclaimable-looking class in a menu that loses 76 MiB of available
RAM and drains CMA.

## Limits

Charged values are the adapter's budget charge (format-defined), not Mali physical
residency; a target's presence does not prove it is still read, and no last-reader
epoch exists yet. One arm, one build. No scene, id295 or FPS claim.

## Next (guarded, one factor)

Two candidate A/Bs, in this order, each with the same guard (identical visible
output, strict GL, 300 MiB budget, no floor change):

1. **1920×1080 → 1280×720 storage for the three colour targets and their depth**,
   opt-in behind a default-off switch, accepting the documented UV/tiling risk and
   verifying pixels before/after.
2. If that is not pixel-safe, **fence-based release** of any target that is
   provably unreferenced after the menu stops drawing — which first requires the
   B2 last-reader epoch, so (2) is blocked on instrumentation, not on a guess.

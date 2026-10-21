# Class attribution of the menu-phase loss (owner roadmap 40.6 / B2-lite)

Second ledger arm on build231 `41d6b4f8…c682`, same opts as `menu-ledger-01`
(strict GL, 300 MiB texture budget, diagnostic floor 32 MiB), with per-class
estimates added to the ledger. One line per second plus `arm-start`.

## Measured at the low point (frame 31)

| class | start | low | delta |
|---|---|---|---|
| `MemAvailable` | 126.8 MiB | **50.5 MiB** | **−76.3 MiB** |
| `CmaFree` | 27.3 MiB | **0.83 MiB** | exhausted |
| game `VmSwap` | 0 | **407.4 MiB** | guest pages to swap |
| charged texture storage | 107.1 MiB | 157.3 MiB | +50.2 MiB |
| depth renderbuffers | 2 / 22.9 MiB | 2 / 22.9 MiB | **constant** |
| colour targets (estimate) | 16 / 27.5 MiB | 19 / 43.4 MiB | +3 targets, +15.9 MiB |

`scaled-textures`, `half-textures`, `bc-pending` and `joined-views` are all **0** in
the menu, so none of those experiment paths is responsible.

## What this buys

- The loss is **not** the depth/stencil renderbuffer pair: it is allocated once
  (2 buffers, 22.9 MiB) and stays constant while 78 MiB of available RAM disappears.
- The growth that is visible to the adapter is **textures (+50.1 MiB)** plus
  **three more colour targets (+15.9 MiB)** — about 66 MiB of format-defined
  estimate against a 78 MiB loss, with the remainder in classes the adapter cannot
  see (`buffers`, `egl-surfaces`, `driver-retained`, all labelled untracked).
- **CMA is a 28 MiB pool and it is fully drained** (28.0 → 0.85 MiB) while ~66 MiB
  of estimated GL storage appears. CMA capacity is therefore a real constraint on
  this board's GPU path, and the menu is enough to exhaust it — the earlier
  `CmaFree` collapse is reproduced on a second build.

## Limits

Format-defined estimates are not Mali residency; a colour target "estimate" is
width×height×4 for a texture the adapter marked as drawn/composited, not a measured
dma-buf. No pre-launch baseline. One arm. No scene, id295 or FPS claim.

## Next

Identify which of the 19 colour targets are retained after the menu stops needing
them, and whether the two depth renderbuffers are reallocated per target elsewhere.
That requires the transactional ownership ledger (owner §40.6 B2), which is the next
real step.

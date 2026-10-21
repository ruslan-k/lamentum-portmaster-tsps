# The menu's big drawdown is the guest heap, and CMA is exhausted before our GL work

Build234 `571463a494a9` moves the first ledger record to **GL/texture initialisation**
(`why=gl-init`) and adds retire receipts for the instrumented classes. Arm
`menu-early-01`: `T2_MEMORY_FLOOR`, verified identity, zero cleanup errors.

## Ordering (log line → measurement)

| line | event | available | CMA free | charged textures |
|---|---|---|---|---|
| 860 | `gl-init` | **568.7 MiB** | **0.75 MiB** | 0 |
| 993 | alloc renderbuffer 1920×1080 (8,294,400 B) | — | — | — |
| 3507 | alloc renderbuffer 1280×720 (3,686,400 B) | — | — | — |
| 3981 | `first-present` | **134.9 MiB** | **23.5 MiB** | 107.1 MiB |

## Two conclusions that change the earlier story

1. **CMA is already exhausted at `gl-init`** (0.75 MiB), *before* any of our textures
   or renderbuffers exist. It then **recovers** to 23.5 MiB by the first present and
   churns afterwards (0.3 → 13.7 → 19.5 MiB in the first seconds). So "the menu drains
   the CMA pool" was an inference from a series that started too late: CMA is
   contended at process start (MainUI hand-off / DRM+EGL init), not allocated away by
   the 1080p family.
2. **The dominant drawdown happens before the first frame**: available falls from
   **568.7 → 134.9 MiB = −433.8 MiB** between `gl-init` and `first-present`, while the
   three 1080p colour targets and two depth buffers account for ~36.8 MB (35 MiB) of
   format-defined GL storage. The rest of that step is the guest's own reservation —
   the number the earlier 1 Hz series could not see because its first record was
   already after the reservation.

## What this means for M1 and the 30 FPS path

- The earlier "16.46 MiB/s menu drawdown" describes the *post-reservation* phase only.
  The bigger, earlier step is a one-time guest/heap reservation of ~434 MiB; the later
  churn (~75 MiB) sits on top of it.
- Any intervention aimed at the menu must be aimed at that reservation or at what the
  guest keeps resident, not at 36 MB of GL images — consistent with the 17.58 MiB
  nominal ceiling of the 720p experiment.
- CMA is a contended resource from the start, so attributing CMA loss to specific GL
  allocations needs the pre-GL state (now measured) rather than post-hoc correlation.

## Still open

- Retire receipts exist but the menu produced no retire events, so allocate/free
  balance is unproven for this phase.
- The EGL surface stays unaccounted (SDL owns the surface path) and buffers are
  unexercised (no vertex-stream draws in the menu).
- Guest reservation identity (which pool/allocator, VAMM quirk) is not established; the
  number is a delta, not an owner.

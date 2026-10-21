# Menu-phase memory waterfall (owner roadmap 40.5, M0)

First measurement of the new bottleneck: the menu itself, not the world atlas.
`LC2_MENU_LEDGER=1` is opt-in, emits at most one line per second plus the first
presented frame, reads only `/proc` and in-process counters, and changes no
admission, budget, floor or swap policy.

## Measured (build230 arm `menu-ledger-01`, 41 presents in 20.5 s)

| quantity | start | low / end | delta |
|---|---|---|---|
| `MemAvailable` | 129.3 MiB | **54.7 MiB at frame 16 (4.5 s)** / 71.7 MiB | **−74.6 MiB** |
| `CmaFree` | 24.3 MiB | **1.0 MiB** (end 12.5 MiB) | exhausted within the menu |
| game `VmSwap` | 0 MiB | **422.4 MiB** | guest pages moved to swap |
| charged texture storage | 107.1 MiB (91 textures) | 157.3 MiB (101) | **+52.6 MiB** |
| game `VmRSS` | 714.9 MiB | 719.6 MiB | +4.7 MiB |

## What the waterfall says

1. The menu halves available RAM **in 4.5 seconds**, before any world content is
   requested — this is the §40.5 bottleneck, now with a timeline.
2. **CMA is exhausted almost immediately** (24.3 MiB → 1.0 MiB). CMA is the
   contiguous pool the GPU path allocates from, so this is the first measured
   candidate for the dominant class, not the charged texture ledger.
3. Charged texture storage grows by only **+52.6 MiB** over 10 textures, one fifth
   of the available-RAM loss; the rest is guest pages going to swap (**+422 MiB
   VmSwap**) and non-texture host/driver memory.
4. RSS barely moves, so the loss is *not* the game's resident set: it is
   memory that left the reclaimable pool. A ledger that only watches textures
   would have reported "nothing much happened".

## Honest limits

- Renderbuffers, buffer objects, EGL surfaces/images and driver-retained storage
  are **untracked** in this build and are labelled so in every line; format-defined
  bytes are an estimate, not Mali residency.
- No baseline snapshot from *just before* launch: the first line is `arm-start`,
  taken at the first ledger tick, so absolute deltas are relative to that point.
- The pre-floor line did not fire (the floor decides inside the memwatch path); the
  last interval line plus `T2_MEMORY_FLOOR_HIT` bracket the refusal.
- One arm, one build, one diagnostic floor. No scene, id295 or FPS claim.

## Next

Attribute the CMA exhaustion: which GL/EGL class allocates it (renderbuffers,
window targets, MSAA, transient FBOs) and whether any of it is retained menu-only
storage that can be released after a proved last reader. That needs the B2 ledger
class (owner §40.6), not another press experiment.

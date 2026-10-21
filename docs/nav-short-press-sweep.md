# Short-press sweep: 80/150 ms do not register, and the arm is too short to finish

Owner roadmap **§40.3 item 5** (bounded short-press sweep) and the first evidence
for **§40.5** (the menu itself is the bottleneck).

## What ran

`tools/nav_chain.py --sweep --sweep-values 80,150,250` against one build229 arm
(`COTM_GL_ERROR_IGNORE=0`, `T2_TEXTURE_BUDGET_MIB=300`, diagnostic floor 32 MiB).
One press per attempt, a new present serial required for each, overshoot refused.

| tap | serial | rows moved | verdict |
|---|---|---|---|
| **80 ms** | 17 → 21 (4 frames) | 0 | qualified: press did not move the selection |
| **150 ms** | 21 → 45 (24 frames) | 0 | qualified: press did not move the selection |
| 250 ms | — | — | **not reached**: arm ended (`owned process unavailable`), recorded as `arm_ended` |

Combined with the earlier arms: **350 ms → 0 rows**, **900 ms → 2 rows**. So the
one-row window is above 400 ms and below 900 ms, and every value at or below
350 ms is simply lost between guest samples.

## Why the sweep could not finish

The arm ends at the memory floor after roughly 30–55 presents (~40 s). Each attempt
costs one kmsgrab plus a base64 transfer and a wait for a newer frame, and the
150 ms attempt alone spanned 24 frames between its before/after serials. Four
attempts do not fit in the run the menu actually survives.

That is not a tooling annoyance; it is the §40.5 finding in its sharpest form:
**the menu cannot stay alive long enough to characterise its own input.** No further
press-only experiment can answer the remaining question until the menu's memory
consumption is explained.

## Tooling changes that came out of this

- `--sweep` / `--sweep-values` with a pure `sweep_decision()`: one row ends the
  sweep as success, a two-row move ends it immediately as overshoot, no movement
  advances to the next declared value only.
- An arm that dies before the press is now a recorded outcome (`arm_ended`) instead
  of a traceback.
- **210 host tests PASS** (4 new sweep tests).

## Next step (owner §40.5, not another press)

Instrument the menu-phase memory waterfall: absolute deltas from before the launch,
1 Hz snapshots plus first-menu-frame and pre-refusal points, GL/RB/buffer/EGL
storage with live-vs-deferred and generation, and a per-event waterfall naming the
top storage lifetimes of the first 55 presents. Only with a longer-lived menu can
the 500–600 ms tap be measured and a New Game arm be attempted.

No scene, id295 or FPS claim.

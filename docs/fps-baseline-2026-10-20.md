# FPS baseline and first measurements (2026-10-20)

Numbers here come from the runtime's own `T2P_SLOW_FRAME` records, parsed by
`tools/analyze_perf.py` (the parser the 30 FPS roadmap §3 asks for). Frames 250–500
are used for like-for-like comparison because every run in this set reaches them;
later windows contain too few samples to compare.

| Run | Env | Window | period P50 | replay P50 | unattributed P50 |
|---|---|---|---:|---:|---:|
| `ui-cbuf-fixed-01` | full diagnostics | 500–709 | 512.5 ms | 96.9 ms | 402.5 ms |
| `perf-quiet-b0` | diagnostics off | 500–691 | 452.6 ms | 150.2 ms | 226.8 ms |
| `perf-quiet-b202` | diagnostics off, build202 | 250–500 (n=251) | 609.2 ms | 274.8 ms | 362.8 ms |
| `perf-sub-on` | diagnostics off, build208 | 250–500 (n=251) | 629.0 ms | 297.7 ms | 350.7 ms |

"Unattributed" is period minus replay, finish, present, swap and readback per frame —
it is not attributed to any subsystem yet. Target is 33.33 ms per frame, so the current
gap is roughly 15–19×.

## What was actually changed and measured

**Constant buffers (roadmap §6 C1).** `nvn_render.h` used to call `glTexImage2D(GL_RGBA32F)`
for every active uniform block on every draw, redefining 16–368 bytes of image storage
20+ times per frame. It now allocates once per (width,height) and refreshes with
`glTexSubImage2D`, gated by `LC2_CBUF_SUBIMAGE` (default on, `=0` restores the old path).

Measured effect on the same binary, same env, frames 250–500: period P50 609.2 → 629.0 ms,
replay P50 274.8 → 297.7 ms. **No win; the change is not justified by this measurement**
and must not be presented as an optimization. The tiny payload size means driver-side
reallocation was not the bottleneck.

**Compression attribution (roadmap §5).** `t2_guest_memory.h` now times the compress and
restore paths and prints `cpu-compress-ms` / `cpu-restore-ms` in the periodic `T2_GZRAM`
line. This is what decides whether the unattributed time is the codec or guest logic.

**Tap latch (input).** `lc2_input_latch.h` holds a released bit for one measured guest
frame interval, because a human tap is shorter than the ~600–870 ms frame. It is now
**opt-in** (`LC2_INPUT_LATCH=1`); default off until a device A/B on a real menu proves it.

## Regression found and isolated

Builds 204 and 205 stopped deterministically with `ZERO_SHADER_NOT_PINNED`
(`pc=main.text.seg+0x542b68`) after ~670 frames, in both the diagnostic and the quiet
environment. The unmodified build202 under the identical quiet environment reached
`TIME_LIMIT`. Build208 (latch off by default, cbuf subimage on, zram counters on) also
reached `TIME_LIMIT`, so the early stop is not present there. The shader tail is still
real; a `ZERO_SHADER_NOT_PINNED` must be handled by `tools/append_program.py`, never by
regenerating the catalogue.

## Not established

- Where the unattributed 350 ms goes (guest IL2CPP, page faults, compression, thread waits).
- Whether any 30 FPS path exists: the biggest known structural candidate (internal
  1920×1080 targets, roadmap §8) has not been attributed to an owner in this title.
- Gameplay FPS: no New Game run has reached verifiable gameplay yet.

## Two measured arm results on build208 (same binary, same quiet env, frames 250–500)

| Arm | period P50 | replay P50 | unattributed P50 | zram CPU/frame |
|---|---:|---:|---:|---:|
| `T2_GZRAM_COLD_MS=10` (diagnostic default) | 629.0 ms | 297.7 ms | 350.7 ms | 138 ms |
| `T2_GZRAM_COLD_MS=250` | 579.3 ms | 240.8 ms | 345.4 ms | 59 ms |
| plus `MOMO_SUBMIT_FINISH=0` (flush, no glFinish) | 557.1 ms | 185.4 ms | 337.9 ms | — |

Reading: raising the cold threshold cut zram CPU from 138 to 59 ms/frame and compressions
from 566 to 248 per frame; replay fell 19% and the frame period 7.9%. Replacing the
per-submit `glFinish` with `glFlush` cut replay another 23% and the period 3.8%, which
also proves the old "glFinish dominates the frame" reading is no longer true on this build.

Neither arm is a fix. The remaining gap to 33.33 ms is ~17x, and after these changes the
frame is still split roughly replay 185 ms / unattributed 338 ms. The next measurement must
attribute the 338 ms per thread (guest main loop vs our worker), not another GL tweak.

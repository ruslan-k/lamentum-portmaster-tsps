# Storage-class allocation receipts (owner §48 / M1)

Build233 `4c818517…b80c` adds `LC2_ALLOC_LEDGER=1`: bounded receipts (first 64
lines) for the storage classes the adapter creates outside the texture path —
depth/stencil renderbuffers, stream/stable VBOs, EGL window surface. Opt-in by
value, no GL call added or removed, sizes format-defined and physical commitment
labelled `unknown`.

## Measured (arm `alloc-ledger-01`, one arm, `T2_MEMORY_FLOOR`, clean cleanup)

| seq | class | bytes | dims | running class total |
|---|---|---|---|---|
| 1 | renderbuffer | 8,294,400 | 1920×1080 | 8.29 MB / 1 |
| 2 | renderbuffer | 3,686,400 | 1280×720 | 11.98 MB / 2 |
| — | buffer | — | — | 0 / 0 |
| — | egl-surface | — | — | 0 / 0 (SDL owns the surface path here) |

Two facts follow immediately.

**1. My earlier depth estimate was 2× too high.** `GL_DEPTH24_STENCIL8_OES` (0x88f0)
is **4 bytes per pixel**, but `lc2_menu_ledger` used 8 for format 0x35. The true depth
class is **11.98 MB (11.4 MiB)**, not the 22.9 MiB I reported in §45/§46. The source is
corrected (effective next build) and the alloc receipts are now the authoritative
number.

**2. The 1080p family is allocated before the first observation.** Both depth buffers
appear at log lines 1013 and 3686, while the first `LC2_MENU_LEDGER` line is at 4167.
The three 1080p colour targets are texture-path objects (`NVN_TEXTURE_REAL`) created in
the same pre-observation window. So roughly **33 MB of 1080p GL images** (3 × 8.29 MB
colour + 8.29 MB depth) plus 3.69 MB of 720p depth exist *before* the ledger's
`arm-start`, which is exactly why `arm-start` already shows CMA down to ~20 MiB.

**3. CMA churns at the bottom rather than sliding monotonically.** After `arm-start`
the series reads 27.0 → 8.2 → 0.01 → 16.0 → 8.9 → 6.9 → 0.2 → 0.05 → 0.78 MiB: the
pool is repeatedly drained and partly recovered. That is consistent with per-frame
allocation/free churn near exhaustion, but it is a **hypothesis**: no per-allocation
timestamp or free receipt exists yet, and `serial=none physical=unknown` is printed on
every line for that reason.

## Gaps this experiment exposes

- `arm-start` is too late: the biggest GL allocations happen before the first present.
  The ledger must emit from an earlier hook (texture/GL init) to cover the pre-window.
- The EGL window surface is **not** accounted: in this configuration the surface comes
  from the SDL path, so the `eglCreateWindowSurface` branch never runs. Reporting 0 is
  honest but leaves a class unmeasured.
- Buffers show 0 because the menu issues no vertex-stream draws; the class is
  instrumented but unexercised.
- No free/retire receipts, so "churn" cannot yet be attributed to specific objects.

## Next

1. Move the first ledger record to GL/texture init so the pre-observation window is
   covered, then re-run: the 33 MB 1080p family should appear as a step in the series
   instead of being pasted on as a baseline.
2. Add retire receipts (delete/realloc) for the same classes, which is the minimum
   needed before any "release retained targets" claim (owner §48 B2).
3. Only then decide the 720p storage question, whose nominal upper bound stays
   **17.58 MiB**.

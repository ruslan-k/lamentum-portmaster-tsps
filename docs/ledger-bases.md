# M1: reconciling declared payload, budget charge and gpu_memory (build245)

Reviewed 4c91bbe / owner §48.5. Device-only arm plus one host tool; no runtime
change, no build, no policy.

## Method

A device-side sampler (0.3 s loop, `/tmp/ge_samples.jsonl`, explicit pid
termination) recorded for each sample: the game pid/starttime, its
`LAMENTUM_RUN_UUID`, boot id, VmRSS, and `mali0/gpu_memory` — while a
principal-flow arm ran build245 with LC2_LIFE_EVENTS=1 and LC2_MENU_LEDGER=1
(floor96/cap300/strict GL, no input). debugfs was mounted only for the arm and
unmounted afterwards; the mount state was checked before and after.

New host tool `tools/ledger_bases.py` pairs the three bases from ONE run. It
refuses foreign or mixed pid/starttime/UUID/boot series (an idle sample with no
pid asserts nothing and is ignored), refuses a log without a menu-ledger line or
a life summary, and refuses a window with no gpu_memory reading. It reports
`units_verified=false` and `physical_attribution=false` by construction.

## Result (arm ge-ledger-04)

Run 70d73d87-bc79-4616-9fbb-4e81f09ead61, game PID26543 detected in 31 samples,
run held to its stop:

| base | textures | depth |
|---|---|---|
| declared payload (per-level requests) | **230.2981 MiB** (90 live) | **11.4258 MiB** (2 live) |
| budget charge (menu ledger) | **109.9385 MiB** (93 live) | **11.4258 MiB** |
| `gpu_memory` in the game window | min 0, max **84900** (units unverified) | — |

- **Depth agrees exactly**: 11980800 B in both independent accounts. The
  renderbuffer instrumentation and the menu ledger's depth estimate measure the
  same thing, so the depth class is the first storage class whose two
  independent accounts reconcile to the byte.
- **Textures differ by 2.0948x** (230.30 vs 109.94 MiB). Both are accounting
  figures; the declared side sums every requested level while the charge is a
  budget figure. The ratio is measured; the cause is **not** established, and no
  waste is implied.
- `gpu_memory` reaches 84900 units while declared total payload is ~241.7 MiB.
  If those units are KiB the counter would read ~331 MiB, i.e. above both
  accounts — but the unit is not derived from driver source, so this is recorded
  as an open question, not as a physical total. gpu_memory may include tiling,
  alignment, framebuffer and non-texture storage.
- Total declared payload at stop: 253465904 B (241.72 MiB), peak equal, 24
  deletes, `delete-with-views=0`, 24 name reuses — the same shape as §66/§67.

## Discarded attempts (not results)

1. Sampler in one long SSH call → SSH 45 s timeout, no samples.
2. Reused evidence directory → harness correctly refused a second run.
3. Sampler read `gpu_memory`'s first token (`mali0`) → units never parsed.
4. Samples without `LAMENTUM_RUN_UUID` → the pairing tool refused them as
   unowned. These arms are kept owner-local under `private-backups/ge-invalid/`
   and are not published as measurements.

## Device result

STOP `T2_MEMORY_FLOOR`, no OOM receipt, cleanup `[]`. Final snapshot: game0,
MainUI1, principal1, runtime1, CPU4-7, no pending launch, debugfs unmounted,
sampler files and process removed; DRM capture shows the Spruce home.

Host: 7 tool tests added (273 total PASS in a clean index export). No memory
was freed and no performance claim is made; menu headroom, world and 30 FPS
remain OPEN.

## Next

Split the declared texture payload per texture (level-0 vs full chain vs
scaled/half variants) to explain the 2.0948x without guessing, and derive
`gpu_memory`'s unit from the driver source or a calibrated allocation fixture so
the counter can be used instead of merely quoted.

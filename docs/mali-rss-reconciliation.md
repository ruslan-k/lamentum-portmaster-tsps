# M1: same-window Mali metadata and status/smaps reconciliation

Roadmap reviewed at 7a5b8cb, owner §48.4–48.5; continuation of §57.
No runtime patch, data change, quality change, drop hint or admission change.

## Instrument access

Debugfs existed as an empty directory but was not mounted. Temporarily mounted
it at /sys/kernel/debug, read Mali metadata, then unmounted it and verified the
original unmounted state. Did not change Mali knobs. The useful readouts are
mali0/gpu_memory and mali0/ctx/<PID>_<generation>/mem_allocs, mem_pool_size,
mem_jit_phys. Do NOT use mem_view for accounting: it emits memory CONTENTS,
not allocation metadata (the discovery probe touched it; not used in results).

## Owned arm mali-reconcile-01

Installed build239 unchanged, 96 MiB floor / 300 MiB texture cap / strict GL.
UUID adfc2d2e-6b18-49f9-8612-419ea16c0ea7, PID 8368, context 8368_54.
Five samples; process identity verified before/after each collection. Per-sample
smaps/status/Mali read windows 3.83–20.42 ms, sequential not atomic. Probe overhead
has NOT been qualified by an A/B. No menu navigation or world attempt.

| sample | VmRSS - smaps Rss (KiB) | gpu_memory raw count | Native commit descriptor sum (bytes) |
|---|---:|---:|---:|
| 0 | -284 | 0 | 0 |
| 1 | 45384 | 11546 | 47169536 |
| 2 | 141068 | 35368 | 144543744 |
| 3 | 246112 | 60555 | 253177856 |
| 4 | 299832 | 74855 | 335257600 |

Last sample additionally has Imported UMM descriptors totaling 11059200 bytes.
These descriptor totals are NOT proven alias-deduplicated physical memory.
The raw gpu_memory units/semantics have not been checked against this exact
firmware's kernel source. If interpreted as 4 KiB pages, the last raw count is
299420 KiB, close to the observed 299832 KiB RSS gap. This numerical correspondence
and co-growth are strong evidence to investigate Mali accounting, not proof of
an exact equality or a specific GL allocation owner. Do not add these quantities
on top of status RSS: doing so may double-count the very discrepancy under study.

Largest two Native descriptors in last sample commit 55984128 and 32821248 bytes;
several others commit 8990720 bytes each. No GL texture/renderbuffer name or guest
NVN ID has been bound to those addresses. Dimensions/lifetime must not be guessed
from sizes alone. Reconciliation JSON preserves the top 16 descriptors and all raw
context metadata remains in samples.json. Raw smaps remain owner-local.

## Result and cleanup

Verified runtime STOP T2_MEMORY_FLOOR at frame 16, no kernel-OOM attribution,
cleanup_errors=[]. No FPS claim and no comparison to prior run duration as a gain.
Final: runtime/principal/MainUI each one, game zero, CPU mask 4-7 restored, no pending
command, debugfs unmounted. DRM capture shows Spruce's charging clock screen,
not gameplay (and not the home-icon screen).

Parser tools/mali_allocs.py has 3 host tests; full host suite 230 PASS.

## Next actionable boundary

Bind the large Native descriptors to GL storage generations/owners and verify the
firmware gpu_memory/RSS-accounting implementation. A transactional lifecycle or
admission change requires this ownership, not a heuristic delete/drop. The fresh
metadata supports the §57 retraction of the image-cache theory; it does not yet
provide a safe memory reduction or a playable world/30 FPS result.

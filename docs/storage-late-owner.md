# M1: late GL brackets locate the remaining large Mali descriptor

Reviewed f3a0c11, owner §48.5; continuation of §§61–62.

## Diagnostic-only change

Build241 adds LC2_STORAGE_PROBE_WINDOW=late: observe eligible large-storage
calls 13..24 instead of 1..12. Main probe remains off unless LC2_STORAGE_PROBE=1.
Unknown window strings select no calls. Default window is unchanged. The header
fixture exhaustively checks ticket boundaries 0..39 and verifies =0 disables the
probe. No GL size/format, content, synchronization, budget, floor or lifetime change.

Pinned build241 SHA256 b4c8df27e5c9ea18d2dac8a13f563863844b2e311d6ee0282256923e488c47e5;
435 baseline checks PASS. Staged atomic deployment, full hash comparison plus
independent target read-back; build240 backup retained under .before-241/.

## Measured arm storage-late-01

Original floor96/cap300/strict GL; principal flow, no controller injection.
Six eligible calls (tickets13..18) observed, all with complete valid metadata,
no detail overflow. Ticket13 is NVN92 / GL texture47 / 3600x3600 / format0x44.
Its upload bracket reports new Native descriptors:

- VA0x5ef0c00000: 51847168 B (49.4453125 MiB).
- VA0x5ef3e00000: 55984128 B (53.390625 MiB).
- Two smaller descriptors at 421888 B each.

Thus the previously unexplained 55984128-byte allocation is directly observed
inside NVN92's storage call bracket. This is a narrowed CALL WINDOW, not exclusive
or permanent resource ownership; staging/background allocation/shared pools are
still possible. Do not add both large descriptors as permanent texture cost.

Five same-run post-marker snapshots:

| relative process-snapshot time | VA0x5ef0c00000 commit | VA0x5ef3e00000 commit |
|---|---:|---:|
| 5.853 s | absent | 55984128 |
| 6.705 s | 4263936 | 55984128 |
| 7.548 s | 4263936 | 55984128 |
| 8.446 s | 4263936 | 55984128 |
| 9.337 s | 4263936 | 55984128 |

This is direct evidence that an address is not a generation identity: the first
VA's large descriptor disappears, then the address is reused/reappears with a
much smaller commit. Continuous allocation identity, GPU completion, physical
refund and last-reader lifetime remain unproven. The second descriptor remains
observed at the same size at all five points; this alone does not authorize free.

Ticket13 bracket duration is 168798038 ns, including GL upload AND both metadata
reads; it is not isolated probe overhead or a whole-frame timing. Later brackets
also carry metadata. No performance comparison is claimed across differently
instrumented runs.

## Result / publication verification / cleanup

12 owned process samples; matching run UUID/boot/PID/starttime/ELF. Runtime STOP
T2_MEMORY_FLOOR at frame4, cleanup_errors=[]. No OOM or gameplay success claimed.
Temporary debugfs mount removed, no pending launch, game zero, MainUI and both
supervisors one each, CPU mask4-7 restored; DRM final-menu.png shows Spruce home.
Build241 remains installed, diagnostics default-off. Host suite258 PASS;
clean-export tests/rebuild and executable comparison recorded before publication.
Raw smaps remain owner-local, no game data is published.

## Next

The two large recurring Native descriptors now have measured upload windows
(NVN81 and NVN92), but not fence-qualified resource lifetimes. Next attribution
must bind actual GL storage generation, draws/readers, retirement and physical
counters before proposing any lossless release. Quality-changing scaling/reformat
and alias-policy changes still require the existing explicit approval. M1 safe
headroom, controllable world and 30 FPS remain OPEN.

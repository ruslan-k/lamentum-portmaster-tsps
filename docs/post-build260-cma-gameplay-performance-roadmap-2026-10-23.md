# Lamentum TSPS — build260 / CMA-to-gameplay execution roadmap

> **LATEST EXECUTION PLAN — post-build262 (2026-10-23):** [new evidence-led recovery roadmap](post-build262-gameplay-recovery-roadmap-2026-10-23.md) supersedes the *next-action sequence* here; §§1–17 remain source/history/evidence. Existing §15 H/S/D/W operation and fresh-preflight safety gates still apply. M4-A and build262's static 77-site/2,048-history host work are complete at their stated scope; next: *compiled* reach, transactional GL/EGL lifetimes, separate memory-class waterfall and K1-B; only then qualified W0/W1/F1. No new device run, and not playable.

**CURRENT EXECUTION POLICY (2026-10-23, M4-A merged at main@509cc985):** [§15 — host publication independent of CMA; separate safe staging and fresh-preflight runtime gates](#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go). M4-A host work/source is **DONE**; build261 is a host-built, not device-qualified candidate. Historical low CMA is **not** a permanent ban on publishing or safely staging files; a runtime start still requires a fresh positive preflight and otherwise stays on HOLD. §15 supersedes conflicting older blanket prohibitions without changing measured evidence.

**Historical evidence-first reassessment (2026-10-23, source main@1604ed9):** [§13 — measured facts, exact next host PRs, CMA/device NO-GO, true gameplay/FPS gates](#13-evidence-first-execution-gates-after-the-main1604ed9-re-audit-2026-10-23). This is an audit/documentation-only continuation: no fresh device launch or FPS measurement. §13 should be read before implementing the older queues below.

**Additional post-A1 audit (2026-10-23):** §§11–12 below adds exact host-only M4-A implementation steps, an allocation-callsite census, further exact-firmware CMA investigation, a ranked sustained atlas-memory strategy, and evidence gates for W0/W1/F1. As of this review main is `c05f879`; nothing was run or deployed on TSPS and the CMA safety NO-GO is unchanged.


> **K1/A1 checkpoint — reviewed `main@c05f879` (2026-10-23):** [K1 firmware/CMA evidence](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md) pins the exact firmware kernel and validates order-4 fallback semantics but does not identify retained CMA pages or historical ioctl completion. [A1 replay evidence](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md) reproduces all four build259 denials with 15 focused/359 overall host tests; type-specific physical backing remains unknown. At that review, M4-A was the next host-only step. Do not repeat K1/A1 acquisition or deploy build260 while the CMA safety gate is closed; implementation details are in §11.

**Audit date:** 2026-10-23. **Reviewed main:** [518603a](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/518603a043dab93554765d4d791517966a4b31e8). **Scope:** source, current docs, published evidence and upstream kernel behavior; **no new TSPS run, reboot, instrumented build, or benchmark was performed in this audit**. This document supersedes the *next-action queue*, not historical measurements, in [the post-build251 plan](post-build251-device-audit-roadmap-2026-10-23.md) and [the cumulative roadmap](performance-roadmap-30fps.md) §§78–89.

**Later K1 follow-up (2026-10-23):** an exact firmware-build match and two fresh read-only CMA snapshots are recorded in [the K1 receipt](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md). No device write, install, reboot, or game launch occurred; the hard stop remains. See cumulative roadmap §91.

**A1 follow-up (2026-10-23):** the host-only offline replay reproduced all four build259 denials, with no policy relaxation or device action. Physical CMA backing and driver margin remain unknown; see cumulative roadmap §92 and the [A1 evidence receipt](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md).

**M4-A follow-up (2026-10-23):** host acceptance is complete and recorded in cumulative roadmap §94, detailed §14, and the [M4-A receipt](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md). The unskipped native fixture, pinned-container ASan/UBSan, 359-test suite and AArch64 cross-build passed. Candidate build261 remains local-only; scratch request sizing is not physical CMA proof. Device NO-GO persists; next host-only work is M4-B allocation-lifetime coverage and K1-B exact-kernel DMA/CMA backing classification.

> **STOP / NOT PLAYABLE.** The current boot's idle `CmaFree` was **15,456 KiB** out of 131,072 KiB and stable in read-only observations. Build259 is the last *reported installed* ELF (SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`). Build260 (SHA-256 `f2930135ecc431ffab92595b6324486cbf5df0b6484138d9dcf33d8cc1c680af`) is **host-built only**. Do **not** install or launch build260 or any subsequent candidate (including build261), repeat the margin sweep, lower the 24 MiB tested margin, enter New Game, reboot automatically, or change CMA/sysctl/driver configuration under the existing hard-stop decision. Read-only investigation and host-only fixtures are safe next work. Reopening on-device tests requires separately documented adequate headroom and explicit device go/no-go.

## 1. Evidence ledger: what is implemented, what was observed, what remains unproven

| Area | Actual status / pinned evidence | Not established |
| --- | --- | --- |
| Runtime/title bridge | Switch ARM64 guest NSOs, Horizon SVC bridge, NVN-to-GLES, 1280×720 KMS output, owned Spruce launch/cleanup, verified 435-file recovered baseline; historical title/menu/Loading captures | Correct sustained world, physical controller, audible sound, cold save/load |
| Shaders | 46 indexed entries (0–45), including seven explicitly TEST-only substitutes; historical shader45 work and New Game navigation | Actual first-world draw/pixel correctness; semantic safety of TEST substitutes |
| Build251 M3-A1 | Three OFF/ON pairs; BC3 1920×1080 owner105 known overlapping CPU scratch per upload **10,368,000 → 1,228,800 B**; largest known scratch **64,800,000 → 2,304,000 B**; all six `T2_MEMORY_FLOOR` before menu | Persistent physical-RAM saving, ON/OFF pixel parity or improved floor; stripes remain OFF |
| Build253/254/256b M3-B | Same-binary OFF/ON observer controls, one-shot floor snapshots and 41 BC/non-BC/depth owner windows on build256b; owner92 64,800,000 B, owner81 38,880,000 B requested scratch overlap; build254 owner92 decode ~528 ms and GL upload ~198 ms | Full system/request waterfall, buffer/EGL/driver storage owner, completed periodic timelines, unique Mali physical bytes |
| Build259 E3 | GL subresource name/generation accounting, pre-allocation admission wrappers, 4 tested margins **64/48/32/24 MiB**, all denied by `cmafree-margin` before menu; no new OOM warning and unchanged SwapFree in each arm | A deployable memory margin, corrected menu visuals, whether every charged byte really demands contiguous CMA |
| CMA audit | Idle `CmaFree=15,456 KiB`, `nr_free_cma=3864` pages, `cma_alloc_success=36`, `cma_alloc_fail=0`, two 20.4 s reads plus post-readback; eight historical order-4 warnings via `system_heap_allocate -> dma_heap_ioctl`; MainUI owns 11,075,584 B of *system-exporter* DMA-BUF descriptors | Source of CMA occupancy, pinned/unmovable versus reclaimable use, actual DMA-buffer physical CMA backing, whether each order-4 warning led to final allocation failure |
| Build260 E4 | Fixed 512-event owner ring and strict ledger classifier; 317 host Python tests / 45 focused tests / 435 baseline files; old build251 logs: 2 reconciled, 1 ID280 pair arrives 71.920625 ms after floor, 3 ID280/288 unresolved | Device owner-event traces or zero-overhead observer comparison |
| FPS | Historical menu/Loading gross rates and CPU/swap samples; target 33.333 ms per *correct live world* frame | Any qualified gameplay FPS, let alone steady 30 FPS |

Sources: [M3-A1](../evidence/m3a-bcstripe-b251-01/README.md), [M3-B/256b](../evidence/m3b-build256b-pair-20261022-01/README.md), [build259 margins](../evidence/m2b-e3-build259-margin-sweep/README.md), [read-only CMA](../evidence/m2b-e3-build259-cma-readonly-2026-10-23/README.md), [build260 E4](../evidence/e4-owner-pair-host-2026-10-23/README.md). Raw logs and pixels are intentionally owner-local. No aggregate of figures from different run phases constitutes an allocation ledger.

## 2. Corrected dependency order (avoid optimizing the wrong bottleneck)

1. **GATE-0 / K1: read-only CMA accounting and exact-kernel source provenance.** Exact firmware-build identity and allocator retry behavior are established; free-CMA ownership/backing remains unknown and the device gate stays NO-GO.
2. **GATE-1 / A1: admission-policy model OFFLINE.** Completed: four build259 denials replay exactly; unknown physical backing and driver margin remain fail-closed. No production policy changed.
3. **GATE-2 / M4: isolate a real retained footprint.** M4-A's host stripe-capacity correction and equivalence fixtures are complete; next is M4b host-only allocation-lifetime coverage. No candidate is device-qualified, and physical headroom/device go-no-go remain separate requirements.
4. **GATE-3 / E4 and V1: run a *short*, safe diagnostic only once device gating reopens.** Validate owner-pair joins and live KMS OFF/ON pixel parity with pinned PID, run UUID, ELF and present serial. Diagnostic-safe stopping is not successful menu admission.
5. **GATE-4 / W0: three true-menu safety passes**, then **W1: live first world + interaction + audio + save/cold-load**, then **F1: qualified 30-FPS optimization**. No shader/perf or gameplay claiming before the prior gate.

A typed `T2_STORAGE_ADMISSION` or `T2_MEMORY_FLOOR` means safe refusal, not successful playable progress. A current-game-owned image must be captured while its PID/starttime lives; a publisher splash or Spruce home is not the title menu or the world.

## 3. K1 (P0): exact kernel / CMA owner, READ-ONLY

### K1.1 Identify the *target* kernel and allocator, not merely a version-compatible analogy

The earlier public Linux 5.15.147 T527 tree was only an analogue. The subsequent user-provided SpruceOS link points to the TG5050 firmware updater, which downloads `trimui_tg5050.awimg.7z` from `spruceSource`; the pinned `SmartProS.cfg` sets firmware `1.0.1`, matching the live target. That inspected repository tree contains the firmware asset but not the vendor kernel source.

**Implemented:** `tools/kernel_source_match.py` consumes pinned host/device receipts and emits a sanitized match report; raw kallsyms addresses remain out of committed evidence. The released vmlinux banner/compiler and four symbol layouts match the live kernel under one consistent `0x80000` relocation; the logged stack extents and return offset also match. The result is an **exact firmware-build match**, while a whole-live-image hash and the original source tree remain unavailable. The compiled `system_heap_allocate` retries orders `{8,4,0}` after a null `__alloc_pages` result; request completion from the historical warning remains unknown.

The binary proves the retry branch and order table, but it does not recover source text or settle the complete GFP/CMA allocation and page-pool free paths. Continue only with read-only allocator accounting; do not infer physical backing from the heap name `system`.

**K1.1 result:** exact firmware-build match published; source tree and historical request completion remain unavailable. The order-4 warning is classified as a nonterminal allocation attempt, not a confirmed whole-request failure. This closes warning semantics, not the CMA owner or device go/no-go.

### K1.2 Explain the 87–103 MiB → ~15 MiB idle CMA drop without declaring a leak

Linux can lend CMA-designated pages to movable consumers, so **`CmaTotal-CmaFree` is not automatically pinned GPU memory or a permanent leak**. A contiguous CMA request depends on mobility, fragmentation, page pinning, migratability and allocator selection. Conversely, the refreshed `MemAvailable=676,316 KiB` does **not** prove that a required DMA or GPU allocation can succeed. Treat the two uncertainties separately.

**Implemented and exercised read-only:** `tools/cma_readonly_snapshot.py` captures bounded JSON without writes; `tools/cma_readonly_compare.py` compares two or three same-boot receipts, treats `nr_free_cma` as a gauge, and fails closed on missing scalar deltas/histograms, counter resets, non-increasing monotonic times, or MainUI/runtime identity drift. The refreshed 22.178 s pair retained `CmaFree=15,456 KiB`, `nr_free_cma=3,864`, counters `36/0`, and a stable MainUI PID/starttime/FD set. The exact installed-runtime inode scan found no running target instance. A second pair returned comparator status `ok`, with unchanged CMA gauges/counters, histogram and runtime/MainUI identities. `MIGRATE_CMA` orders 0–10 had `571,71,9,3,1,0,0,0,0,0,3` blocks (derived 3,861 pages); the separately read `nr_free_cma` was 3,864. The 3-page difference is explicitly unresolved due to sequential proc reads. System-exporter DMA-BUF inodes/sizes match MainUI's FDs but do not establish CMA backing.

Check `CONFIG_PAGE_OWNER`, `CONFIG_CMA_DEBUGFS`, `CONFIG_DEBUG_FS`, `CONFIG_COMPACTION` and tracepoint availability **without mounting or enabling anything**; an unmounted debugfs or missing `CONFIG_CMA_DEBUGFS` means unavailable, not zero. Do not write drop_caches, trigger compaction, allocate test DMA-BUFs, alter `vm.watermark_scale_factor`, load modules, kill MainUI or reboot as part of this phase. If `/proc/pagetypeinfo` is unavailable or invasive to sample, make the result `unavailable` and explain why.

The new pair is an updated free-page baseline, **not** evidence of which pages were pinned. A comparison across a reboot is optional **only with separate operator approval**, full before/after state and awareness that boot state, caches and MainUI can change; never auto-reboot to “fix” the measurements.

**Pass:** classify `reclaimable/movable hypothesis`, `pinned/unmovable evidence`, `DMA-heap page-pool candidate`, `GL/Mali lifetime candidate`, or `unattributed`, always with source and confidence. Distinguish old WARN lines from a **new** kernel delta. Do not promote a CMA theory without at least one matching owner/lifetime observation.

### K1.3 Device go/no-go decision

**NO-GO remains in force now.** Reassess only after operator-reviewed fresh read-only data, no game/other conflicting process, same expected boot/firmware identity, a defensible actual allocator margin for the *next* proposed operation and an independent rollback. A single scalar threshold cannot be deduced from the one warning snapshot at `free_cma=4122` pages. Do not use “order-4 did not kill the process” as permission to lower the memory safety gate.

## 4. A1 (P0): prove/fix the admission accounting model before tuning margins

**Exact source:** `runtime/lamentum-adapter.patch`, `native/lc2_gl_storage.h::lc2_gl_storage_admission`, `native/t2_memwatch.h::t2_storage_admit`, and `tools/test_t2_storage_admission.py`.

Current checked arithmetic remains `required_available = 96 MiB + (GL + scratch + margin)` and `required_cma = GL + scratch + margin`. CPU `malloc` scratch, declared GL storage, and DMA-heap allocations are not established as the same physical accounting class.

**A1 result (2026-10-23): host-only replay complete.** [`tools/admission_offline_replay.py`](../tools/admission_offline_replay.py) and its 15 focused tests define a typed `AdmissionRequest` with unknown backing retained as `null`, validate build259/per-run-only input, and replay the existing policy from the sanitized margin summary plus locally held source logs. The four source-bound denials reproduced exactly: owner61 scratch 5,400,000 B; owner77 scratch 10,368,000 B; owner0 GL 512,000 B; owner0 GL 8,294,400 B. No event timestamp was synthesized. The owner77 CPU-stage peak is supported by an untimed `LC2_BC_FULL_STAGE` record joined by same-run/owner log order only.

The 15 focused A1 tests and the full 359-test tools suite pass; Python compilation passes. The host-only actual-log replay completes with zero device actions.

The non-deployable `proven_CMA_only` and `mixed_two_ledger` alternatives deny with `qualification=unknown`; their missing proof fields are explicit. GL subtype, physical CMA bytes and a separate driver margin remain unknown. The 64 MiB source timeline remains incomplete. Existing T2/ledger tests retain overflow, GL re-specification and mip/subresource coverage; A1 adds fail-closed unknown-backing, direct-DMA-heap, composite/mixed, timestamp, run-identity and bounded-log checks. See the [A1 evidence report](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md) and [machine-readable receipt](../evidence/a1-storage-admission-offline-replay-2026-10-23/summary.json).

No production policy, 96 MiB floor, 300 MiB texture cap, strict-GL setting, launcher margin default, or device state changed. This host replay is not a build/deployment/gameplay result; the independent CMA go/no-go remains NO-GO.

**Pass:** old denials replay exactly without claiming physical backing; alternatives preserve unknowns and fail closed. **Not passed:** source-backed physical CMA ownership, driver uncertainty margin, or permission to weaken the runtime guard. Do not set a new `T2_STORAGE_MARGIN_MIB` production default.


## 5. M4 (P0): complete the retained-memory waterfall and select a single lossless reduction

**Instrument only when GATE-0 reopens; prepare on host meanwhile.** Extend `tools/proc_metrics.py` and a bounded `tools/peak_memory_waterfall.py` reducer with dry-run fixtures. Reuse, do not reinvent, `LC2_M3B_WINDOW`, the exact `LC2_MENU_FLOOR_MEMORY` snapshot and `LC2_GL_STORAGE_EVENT`/owner events. The 100 ms periodic sampler had missing rows; mark its `complete=false` and do not interpolate the missing floor. For every owner: build/run UUID, NVN ID, GL name and storage generation, stage, first/last use, requested CPU scratch, GL declared payload, retired bytes, `VmRSS/VmHWM/VmSwap`, sampled `CmaFree`, fault/swap deltas and unobserved driver bytes.

**Close the known coverage holes:** the build256b ring covers BC, non-BC and depth but *not every buffer/EGL/driver allocation*. `nvn_present.h`'s direct `glBufferData` was not included in that ring's buffer-lifetime receipt, despite later GL admission wrapping of direct storage calls. Audit each named VBO/IBO, `glBufferData` re-spec, any EGL/KMS buffer, `glRenderbufferStorage` and `glTexImage2D`, with proper context and generation identity. Report source hook coverage separately from observation of device events.

### Ranked candidates and discriminating tests

**M4-A — BC CPU scratch and row staging (lowest semantics risk).** The original uploader reserved `width*128*bpp` even when the mip height was below 128. Checked `zero_bc_stripe_geometry()` and `zero_bc_full_geometry()` now provide the per-mip byte plans; `zero_bc_select_stripe()` uses medium stripes only for a strict requested-scratch reduction. Both first-use admission and actual upload use these shared calculations. Each stripe passes only its actual pixel bytes to decode and keeps the corresponding row count in the upload bounds. `LC2_BC_STRIPE_MEDIUM` remains default-OFF; no resolution, format or mip semantics changed.

**M4-A host result (2026-10-23):** the required native BC fixture passed with zero skips and produced 86 full-vs-stripe parity cases, 86 source-preservation checks, 258 guarded-buffer checks, 244 contiguous exactly-once row regions, 28 metadata-only 8192×8192 mip checks, 18 in-place cases and 15 rejected inputs. The pinned-container ASan/UBSan run passed; the reservation fixture passed 14 tests; the full suite passed 359/359 with no skips. Baseline 435/435, patch apply, Python compilation and `git diff --check` passed. The pinned AArch64 build is ELF64 PIE, 2,206,776 B, GLIBC ≤2.27, Build ID `43aa590ec1209841671e9ad0d8de726d9f5f90a2`, SHA-256 `0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332`; see the [M4-A evidence receipt](../evidence/m4a-bc-stripe-capacity-2026-10-23/summary.json).

**Not qualified:** no live `glTexSubImage2D` call, alias-view semantics, KMS pixel parity, retained RSS/CMA, gameplay or FPS was measured. The correction is a more accurate scratch request, not proven physical savings. Keep the device hard NO-GO and do not install the host candidate.

**M4-B — optional in-place BC decode and persistent mirror lifetimes.** `LC2_BC_INPLACE_DECODE` already exists (default OFF), so don't implement a duplicate algorithm. Verify byte-exact BC1/BC3 colour+alpha, block row order, edge tiles, sRGB sampling and source byte preservation where required. Test aliasing, content-generation changes, CPU readback, refresh after guest write, cancellation during materialization and GL error cleanup. If snapshots/linear decode mirrors remain live after GL upload, prove their last legitimate consumer and storage generation before reducing retention. One flag, one atlas class, one measurable **sustained** headroom improvement; no blind same-ID skip.

**M4-C — retained GL atlases.** Owner92 `3600×3600` and owner81 `3600×2160` have large decoded RGBA requests; identify exact materialized levels, actual live set and known/unknown Mali driver descriptors. Compressing BC3 to ETC2/ASTC is **transcoding**, not native BC3 upload; only evaluate after querying *this device's* live GLES extensions, alpha/sRGB and mip parity. A cache needs verified immutable source/write generation (currently untracked) and cannot include owner game data in git. Reject if texture fidelity or mip filtering is not acceptable.

**M4-D — optional 1080p composition targets.** Guest hardcodes 3 colour plus 1 depth-equivalent `1920×1080` targets while scanout is 1280×720. The maximum nominal saving from downscaling *that family* is **17.58 MiB** (31.64→14.06 MiB), not the 31.64 MiB before figure, and not proven physical CMA. `ZERO_RENDER_SCALE=2` already exists and was historically performance-negative; re-open only with evidence that *those live targets* dominate persistent allocation. Check framebuffer completeness, depth/viewport/scissor, UVs, blending, pixel-perfect UI and valid world captures.

**M4-E — CPU scheduling and command replay, DEFERRED.** Prior `LC2_CBUF_SUBIMAGE` and generic render scale failed to show useful previous gains. A ~528 ms BC decode or 198 ms upload on an early allocation window is not a steady-world frame cost. After safe playability, profile whether repeated per-frame texture refresh, GL state churn, SVC, major faults, thread starvation or shader compilation causes *exclusive* frame delay; only then optimize the top measured owner. Don't enable unsafe async replay, deletion/pageout without completion fences, or swap/timing hacks as substitutes for physical headroom.

**M4 pass:** at least three qualifying, phase-matched A/B pairs with the same pixels and request class show **higher minimum** `MemAvailable` and `CmaFree`, **lower** `VmHWM`, `VmSwap` and swap/fault pressure outside control variability, without new kernel warnings or GL errors. Treat differences in CMA-movable pages and driver allocations as separately uncertain unless K1 establishes their semantics. A merely lower requested scratch count is a hypothesis, not acceptance.

## 6. E4: finish the ID280/288 owner-pair investigation without falsifying old logs

Build260 has the 512-entry default-off ring (enabled by `LC2_LIFE_EVENTS=1`) and `tools/ledger_bases.py::replay_texture_budget` now classifies `pair_not_yet_emitted`, `missing_owner_path`, `generation_mismatch`, `alias_scope_mismatch`, `log_truncated`, `over_capacity` and `unresolved`. The six build251 logs have **no** new owner-event records. Old baseline03's ID280 pair arrived **71.920625 ms after** the snapshot; candidate01/baseline02 ID288 and candidate03 ID280 remain unresolved. These observations are not four proved leaks.

**Before any device run:** fixtures for charge-without-pair, late pair, reordered clocks, reused NVN ID, alias owner, duplicate BC first-use, retirement, nonzero overflow, incomplete EOF and multi-run mixing. Validate `owner_events_expected=true` on build260 schema, false only for real historical recordings. A prospective on-device E4 arm is allowed **only after GATE-0** and should have one observer-OFF control on an identical binary, floor/cap/GL unchanged, short time bound, exact log/boot/PID/build identity and clean MainUI/CPU state. Fail closed if any active charge lacks a qualified owner before the floor snapshot or the ring reports overflow. Do not fabricate a storage generation from an NVN object ID or infer physical refund from deleting a GL name.

## 7. V1 / W0 / W1: correct owned pixels, stable menu and *functional* gameplay

**V1 image qualification:** use `tools/load_metrics.py::OwnedSerial`, `tools/owned_navigation.py` and `tools/frame_diff.py`; do not use the legacy unqualified `tools/newgame_navigate.py` algorithm for acceptance. Add a live, event-triggered KMS probe: attach to a current-run `NVN_PRESENT_PIXELS` serial, verify `boot-id + PID + starttime + ELF hash + run UUID` before/after image and require a later distinct serial while the game remains alive. Reject if the PID exited, serial repeated, KMS captured the home overlay or a timed capture missed the game. Compare same **publisher/menu/world phase** at 1280×720; `tolerance=0` for exact deterministic pixels; separately report animation/temporal differences. Build251 stripe ON still lacks such a capture.

**W0 menu safety:** only after GATE-0/1/2, achieve **three independent 120 s current-game-owned menu sessions** with a real `LC2_MENU_EVENT`, two+ distinct KMS frames, no memory floor/admission refusal, kernel OOM, GL errors, swap growth or unsafe CMA transition; verified Spruce cleanup after each. The 160 MiB `MemAvailable` target from the old plan is a *design goal*, not a proved required world-set size. A publisher image or complete diagnostic log never passes W0.

**W1 first world:** use a semantic finite-state page oracle: `MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> WORLD_VISIBLE`. Issue each directional/confirm press only after an acknowledged release, matching newer presented serial and two independent consistent page/cursor observations. Historical taps can miss or overshoot when a menu is presenting only 1–2 fps. Record owner-qualified transitions, exact shader **draw** counts (not just shader creation), new scene ROMFS/texture load, framebuffer attachments and actual character/world pixels; keep all seven TEST-only shader substitutes visible in the audit. If a new shader is unpinned, dump/pin only the encountered program with owner-private blobs; do not add a fake shader or regenerate catalogue prefix 0–45.

W1 acceptance matrix: title/menu selection; player movement in **two directions** on a physical pad; **one interaction**, dialogue or inventory/back; audible ALSA output; controlled save with owner-backup; clean quit and **cold reload of same progress**; three owner-qualified clean loops. Protect existing saves. A still-visible Loading sprite, agent-only input, nonzero AudioOut PCM counters or a home screenshot does not substitute for these tests.

## 8. F1: only after W1, measured 30 FPS

Budget: **33.333 ms per correct physically presented world frame**. Build three stable `>=60 s` world routes (idle, movement/interaction, busy lighting/effects), plus separately measured transitions. For each, record warm-up, scene, exact build, governor/temperature, run/PID/starttime and frame serial, P50/P95/P99 complete interval, duplicates/drops, correct KMS pixels, audible audio, physical input, `VmRSS/VmHWM/VmSwap`, CPU ticks from **target HZ**, system stalls/faults and wall/CPU/GPU-wait attribution. `tools/perf_sample.py` now uses `proc_metrics.cpu_delta` with target HZ; **do not reopen the old HZ bug** without contrary evidence. `tools/analyze_perf.py` must reject skipped serials, missing endpoints, mixed identities, observer overhead above 5% and slow-frame-only percentile inference.

Measure and rank mutually exclusive time **before** optimizing: guest Unity/IL2CPP and SVC, NVN command replay/GL submissions, BC decode/texture refresh, GPU waits/fill, swap/major faults, and SDL/KMS present. Sample threads with stable TID+starttime; a hot TID is not automatically guest main thread. Current Loading measurements and ~709 historical presents do not establish world FPS.

**Promotion rule:** at least three one-variable A/B pairs on the same scene with corrected visuals and functional tests; improved **whole-frame P95** outside control noise with no memory regression. 30-FPS acceptance requires P95 `<=33.33 ms` on each required playable route (P99 reported), not a count of presents over a Loading interval. Intermediate verified 5/10/15/20 FPS world targets are valid checkpoints. If hardware cannot meet the safe working set or scene cost, publish a bounded feasibility result and identify explicit quality/architecture trade-offs instead of endless spinner testing.

## 9. Implementation-ready PR queue, owner files, tests and abort rules

| Order / PR | Files to change | Required proof | Stop/rollback |
| --- | --- | --- | --- |
| **K1 / `audit/cma-source-readonly`** | New `tools/kernel_source_match.py`, `tools/cma_readonly_snapshot.py`, `tools/cma_readonly_compare.py`, tests; new redacted evidence README | Firmware-source confidence, CMA migratetype and counter deltas, non-invasive identity | Missing identity, mutating/proprietary memory reads, unjustified leak attribution |
| **A1 / `audit/storage-admission-bases` — HOST COMPLETE** | `tools/admission_offline_replay.py`, 15 focused tests, [A1 receipt](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md) | Four build259 refusals replayed exactly; unknown backing/margins fail closed; zero device actions | No production policy relaxation; no device launch until an independent safe-CMA go/no-go is documented |
| **M4a / `perf/bc-short-mip-bounds` — HOST COMPLETE** | `runtime/lamentum-adapter.patch`, `tools/test_bc_layout.py`, `tools/test_gl_storage_layout.py`, [M4-A receipt](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md) | Checked stripe capacities in uploader/reservation, odd-mip byte equivalence, 359-test suite, host AArch64 build | No claim of physical CMA/RSS saving; no device launch before independent safe-CMA go/no-go |
| **M4b / `audit/allocation-lifetime-coverage`** | `runtime/lamentum-adapter.patch`, `tools/ledger_bases.py`, reducer/tests | Full observed buffer/texture/renderbuffer/EGL class coverage or explicit unknown | Incomplete ring treated as complete, GL-context generation confusion |
| **E4 / `test/owner-pair-device-qualification`** | Existing build260 source + owner harness/tests | Only after GATE-0: qualified OFF/ON, complete live owner joins | unsafe CMA, source/event truncation, incomplete cleanup |
| **V1 / `test/live-owned-kms-parity`** | `tools/owned_nav_chain.py`, `tools/load_metrics.py`, `tools/frame_diff.py` + fixtures | Same-stage current-PID OFF/ON pixels / explicit refusal | stale present or home/publisher masquerading as menu |
| **W0/W1 / `feat/semantic-gameplay-gates`** | Page-oracle/harness, shader draw census, audio/save checks | 3 true-menu and 3 genuine playable loops | wrong page, missing release, incorrect pixels, saves at risk |
| **F1 / `perf/world-exclusive-time`** | `tools/perf_sample.py`, `tools/analyze_perf.py`, bounded per-stage profiler | 3 independent per-scene runs and P95 full-frame proof | incomplete identity, >5% probe overhead, no world |

**Host-first test contract** (the following does **not** execute a TSPS device arm):

```sh
python3 -m py_compile tools/ledger_bases.py tools/proc_metrics.py \
    tools/load_metrics.py tools/device_principal_test.py tools/perf_sample.py
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
git apply --check runtime/lamentum-adapter.patch   # run in the pinned recovered source tree, NOT repo root
git diff --check
```

New scripts need negative fixtures for absent/unreadable proc files, bogus paths, inconsistent pagesize, boot/PID/starttime drift, partial stdout/invalid JSON, time-of-check/time-of-use race, kernel counter reset, buffer inode reuse, log truncation, overflow, integer arithmetic errors and unknown Mali/CMA allocation basis. Fail closed and record `not_observed` rather than zero. Preserve baseline hashes (435/435), pinned compiler, AArch64/GLIBC check and source-overlay equivalence before any future build.

**Future device evidence contract, not permission to run now:** one variable per arm; record build and launcher/helper hashes, boot ID, PID/starttime, run UUID and CPU mode; snapshot preflight kernel & device state, concurrent pressure, owner-specific GL/CPU/request events, complete run log, end/stop status, live pixel hashes and restored Spruce; keep full logs, owner game assets, disassembly blobs and PNGs local-only. Reject any unqualified arm and restore the known working executable by readback SHA. A safe stop is useful information, not gameplay or a performance gain.

## 10. Feasibility checkpoints and explicit non-goals

After K1+ A1 classify the CMA policy and **two distinct source/evidence-selected structural memory candidates** have been qualified or safely rejected, decide if the observed active set can fit TSPS's ~1 GiB RAM plus the actual driver/CMA constraints. Publish an uncertainty interval instead of subtracting unrelated logical ledgers (`budget-live`, GL-declared bytes, DMA exporter size, Mali descriptors, RSS, CMA free). A policy that permits progress only by exhausting CMA is **not** a win. A quality reduction, selective asset transcode, different backend, more capable handheld, or a lower attainable world FPS can be a legitimate explicit conclusion, but must be labelled and tested separately.

**Do not:** change the 96 MiB floor merely to bypass a stop; increase swap/cap as substitute for residency; clear caches or force compaction on the target; leak private owner data; claim a warning equals a failed ioctl; claim all CMA used is Mali memory; silently admit UNKNOWN physical allocation; downgrade image quality unannounced; regenerate shader catalogue; claim FPS from Loading/publisher frames; allow long unbounded device runs during the hard stop.

### Sources and prior decisions

- Device-specific reports: [K1 kernel/CMA follow-up](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md), [build259 margin sweep](../evidence/m2b-e3-build259-margin-sweep/README.md), [prior CMA read-only audit](../evidence/m2b-e3-build259-cma-readonly-2026-10-23/README.md), [M3-B allocation windows](../evidence/m3b-build256b-pair-20261022-01/README.md), [E4 host source/replay](../evidence/e4-owner-pair-host-2026-10-23/README.md).
- Adapter code: [`runtime/lamentum-adapter.patch`](../runtime/lamentum-adapter.patch), current [30-FPS roadmap §§86–89](performance-roadmap-30fps.md), [1080p composition origin](1080p-origin.md).
- Linux upstream reading (context, **not** exact firmware source): [kernel /proc buddyinfo/pagetypeinfo documentation](https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst), [kernel physical memory/CMA pages](https://www.kernel.org/doc/html/latest/mm/physical_memory.html), [DMA-heap high-order fallback discussion](https://lkml.rescloud.iu.edu/2102.1/05202.html), [existing project's version-matched T527 source analogue](https://github.com/REG-Linux/linux-t527/tree/9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed).

## 11. Post-K1/A1 re-audit at main c05f879 (2026-10-23)

**Nature of this checkpoint:** review of the exact public `main` tree at `c05f879873392787d0157186679e31f973a73ecc`, published evidence, and the current `runtime/lamentum-adapter.patch` / tool implementation. **No new build, local host suite, TSPS memory sampling, deployment, reboot, game launch, screenshot or FPS measurement was done in this review.** Refer to the linked K1/A1 receipts for work already actually executed. Prior sections retain technical history and may contain *planned* K1/A1 steps; this section is the authoritative implementation queue.

### 11.1 Evidence disposition — close work already completed before creating another PR

| Workstream | Verified as completed in source/evidence | Still not complete | New action |
| --- | --- | --- | --- |
| K1 exact kernel | SpruceOS firmware `1.0.1`, extracted unstripped AArch64 `vmlinux`, consistent live symbol relocation and callsite `system_heap_allocate+0x120`. Kernel orders `{8,4,0}` and failed order-4 retry behavior verified from **this firmware's binary**, not merely a public analogue | Final outcome of old `dma_heap_ioctl` calls, CMA-backed request class and free-CMA page owner unknown; whole live kernel not hashed | **Do not redo firmware download/extraction**. Investigate exact binary's GFP/heap/page-pool/Mali paths on host (K1.4) |
| K1 CMA snapshots | Two qualified pairs on the same boot, unchanged `CmaFree=15,456 KiB` / `nr_free_cma=3864`; stable MainUI/DMA-BUF identities; `MIGRATE_CMA` free-block histogram recorded; no device writes | Whether pages are movable/pinned, why idle CMA remains low; a safe launch margin | Keep hard NO-GO; use read-only evidence and optional separately approved comparisons |
| A1 policy replay | All **four** build259 denial records, original timestamps and owned-log identities validated; existing `GL + scratch + margin` arithmetic reproduces all refusals; 15 focused + **359 suite** host tests | `proven_cma_bytes` and driver uncertainty, GL subtype for owner0, CPU peak for owner61 | **Close “replay the four logs”**; add request taxonomy/provenance for *future* instrumentation only |
| E4 owner lifecycle | Build260 observer, strict time-filtered owner join and 317-host-test checkpoint; old ID280's pair-after-floor is classified | Other ID280/288 causes, device event coverage and observer OFF cost | Keep default OFF; device qualification behind GO gate |
| BC/M3-B | Larger texture request windows and staging reductions, exact owner92/81 windows; BC in-place implementation exists and test fixture compares CPU outputs | GL upload/full-mip parity, persistent RAM/CMA savings, high-resolution gameplay and work-set | M4-A/M4-B offline source/test work first |
| Actual gameplay | Historical title/config/Loading traversal, numbered shader catalogue 0–45 and physical KMS mechanism | Qualified live world, correct seven TEST shader semantics, controller/audio/save and world FPS | W0 → W1 → F1 **only after safe memory gate** |

**Important correction to older §3 instructions:** the exact firmware binary **has already been matched** by K1. The available kernel source is still missing, but “identify whether the order-4 warning can retry” is no longer an open task. An order-4 warning does not establish *final* DMA-heap allocation failure; neither does it establish success. There is no justified standalone numerical “safe CMA” threshold in the current evidence.

### 11.2 Source-level audit: concrete implementation risks and status of each claim

1. **Confirmed source-level over-allocation of short-stripe scratch:** in the patched `native/nvn_textures.h::lc2_bc_upload_stripes`, `capacity=(size_t)width*128*bpp` even when `first_rows=min(height,128)` is smaller than 128; `linear_capacity` already uses `first_rows`. `lc2_bc_reserve_first_use` independently estimates `stripe_bytes=width*128*output_bpp`. Both must use a single checked shared calculation. This is a **request-size bug/inefficiency**, not proof of a persistent leak or a DMA/CMA win.
2. **Multiplication before validation:** the same `size_t` products are constructed before the checked addition. A later `UINT64_MAX - capacity` check cannot detect a prior wrapped multiplication. Return a typed allocation/layout refusal *before* malloc or GL for 0/oversized/overflow geometry. Distinguish `size_t` and `uint64_t` limits.
3. **Admission policy does not carry physical origin:** `lc2_gl_storage_admission` conservatively requires `CmaFree >= GL + CPU scratch + margin`. A1 proves the arithmetic and four denials, **not that an ordinary host `malloc` spends that much CMA**. Do not “fix” it by setting `proven_cma_bytes=0` or lowering margins. The missing field is the real allocator/memory class and its uncertainty.
4. **Owner zero is often not a useful attribution:** A1's two GL-denial cases were `owner=0` with subtype and GL generation unknown. The admission macro `glTexImage2D/glRenderbufferStorage/glBufferData` does not by itself convey the exact NVN owner of the currently bound GL object. A later trace must resolve (context/share-group epoch, binding target, bound GL name, generation, NVN owner) *without* holding resource locks across `/proc` I/O. A guessed NVN ID is worse than `owner=unknown`.
5. **Finite generation-history capacity is an unverified exhaustion risk:** `lc2_life_generation_next` stores (share-group, GL name, kind) in the 512-entry `generations` array and selects a fresh slot only with `!h->name`; seen history is not recycled. The live storage table can recycle deleted objects, but 513+ *distinct historical names* may exhaust the history and yield generation=0. This is **code-review risk, not an observed device fault**. Add a synthetic 1024-distinct-name test and refuse unsupported history eviction unless uniqueness is maintained independently (e.g. one monotonic lifetime ticket tied to current GL context/owner). Never silently recycle an ambiguous generation.
6. **Completeness != attribution:** the M3-B build256b 41/41 windows cover BC/non-BC/depth but not every EGL/KMS/buffer/driver allocation. A later wrapper scan reports direct `glBufferData` sites, but wrapper coverage is not a device-observed lifetime receipt. Require source hook/GL binding inventories and actual event completeness separately.
7. **A passing Python suite may not execute the native BC fixture:** `tools/test_bc_layout.py` explicitly calls `skipTest` when the pinned adapter/bcdec source is unavailable. The 359-test A1 figure must **not** be cited as a successful execution of this particular native geometry fixture without a separate unskipped receipt. Add a required-build profile that fails closed if the test's source/fixture is missing, records skip counts, and runs the real native BC implementation under ASan/UBSan when supported.
8. **Recent host navigation improvements already exist:** `tools/owned_navigation.py`, `tools/owned_nav_chain.py`, `tools/load_metrics.py::OwnedSerial`, and exact `tools/frame_diff.py::identical` exist; do **not** rebuild an unowned polling/navigation stack. Their current success is unit-level wiring, not proof of physical input or correct scene pixels.
9. **No evidence for a 30 FPS target yet:** earlier ~1–2 presents/s and hundreds of Loading presents mix shader/asset work, long CPU stalls and swapping. `tools/perf_sample.py` now obtains CPU deltas from target HZ; do not resurrect the historic host-HZ issue absent a regression. Profile real gameplay only after world pixels are established.

### 11.3 PR M4-A / `fix/bc-stripe-checked-small-mips` — implementable host-only patch

**Goal:** eliminate provably excessive scratch *requests*, maintain exact BC decode and preserve existing default behavior for full 128-row stripes. No device actions in this PR.

**Edit sites:** `runtime/lamentum-adapter.patch` (applied `native/nvn_textures.h`, optionally one new self-contained `native/lc2_bc_stripe_size.h`), existing `zero_bc_layout.h`, `tools/test_bc_layout.c`, `tools/test_bc_layout.py`, and a new independent bounds/overflow fixture. Because this repository stores an overlay, edit the manifest-verified recovered native source **and regenerate the overlay deterministically**; never patch the overlay by hand and forget to verify source–patch SHA parity.

1. Define one pure `lc2_bc_stripe_geometry(width,height,bpp,bc_block_bytes,max_rows)` with `max_rows=128`. Reject zero width/height, invalid `bpp`, unsupported BC formats, invalid `max_rows`, dimensions beyond proven NVN/GL limits, and every checked multiplication/addition failure. Calculate `rows=min(height,max_rows)`, `pixel_capacity=width*rows*bpp`, `blocks_x=(width+3)/4`, `blocks_y=(rows+3)/4`, `linear_capacity=blocks_x*blocks_y*block_bytes`, `scratch_peak=pixel_capacity+linear_capacity` in the correct integer width. Reject an input for which the index/stride conversion to `size_t` is unsafe. Do not use `width*128` at any of these sites.
2. Reuse this checked result in **both** `lc2_bc_reserve_first_use` (preallocation scratch estimate) and `lc2_bc_upload_stripes` (actual allocation and diagnostic event). Assert they agree: `preflight_scratch_bytes == actual_requested_peak`. Avoid a one-byte or one-block mismatch that allows the admission check to underestimate the later malloc.
3. For each loop iteration, compute `rows=min(height-y,128)` and `current_bytes=width*rows*bpp` with the same bounds checks; pass `current_bytes` into `zero_texture_bc_pixels`. Do **not** submit `pixel_capacity` bytes for a short final stripe, and keep `glTexSubImage2D` height equal to the actual rows. Keep BC row/block offsets correct for `y/4`, including final non-multiple-of-four rows. Distinguish compressed input capacity from decoded output capacity; never overwrite guest source.
4. Make `zero_bc_should_stripe` a **pure eligibility** decision and separately compute `full_scratch` and `stripe_scratch` with checked arithmetic for the *same mip*. Only choose medium stripes when measured/nominal reduction is **strictly positive** and the existing format, scaling, target and host fallback contracts permit it. Avoid auto-switching default flags; code should be lossless and off by default where required. Preserve direct unstriped upload for ineligible mips and non-BC formats.
5. Native fixture matrix (at minimum): BC1/BC3, unusual/float BC formats already accepted by `zero_bc_bytes`, `1×1`, `7×5`, `16×1`, `127×127`, `128×128`, `129×129`, `1023×63`, `1024×64`, `1920×1080`, `3600×2160`, `3600×3600`, `4096×1`, `4097×9`, `8192×132`, and **every** legal mip in the 1920×1080 and 8192×8192 chains. Host test should compare full-vs-stripe *decoded byte output*, source-block preservation, alpha, tail rows, GL subimage region coverage and exactly-once pixel coverage. Bound test memory so 8192² does not force an unsafe multi-hundred-MiB allocation on CI: validate metadata for that case and use chunked/fixture-only data for pixel parity.
6. Run C fixture `-std=c11 -Wall -Wextra -Werror`, sanitizer build `-fsanitize=address,undefined -fno-omit-frame-pointer` when available, Python tests plus pinned AArch64 build. The dedicated BC fixture **must run**, not `skipTest`. Report geometry parity counts, failure cases, feature flags, compiled overlay hash, target ABI and raw test return statuses.
7. Admit this PR as **host-correctness only**. A shorter `malloc` request at a tiny mip does not fix build259's low idle CMA. Defer performance promotion until a later qualified, same-phase device A/B plus valid pixel capture.

**Acceptance contract:** no integer overflow; no out-of-range read/write; exact all-mip decode bytes, identical upload rectangles and unchanged 128-row results; new code is reversible behind existing controls; zero device execution while NO-GO.

### 11.4 PR M4-B / `audit/owner-generation-and-memory-bases` — close accounting blind spots

**Objective:** account for *logical* storage correctly and only then attempt to correlate it with system residency. Never subtract raw GL declared bytes, DMA-BUF exported sizes, process RSS and Mali descriptors as if they were independent physical allocators.

1. Recovered native implementation: instrument `glBufferData`, `glTexImage2D`, `glRenderbufferStorage`, `glDelete*`, NVN texture pool owner transitions, and EGL/KMS buffer creation paths with a **stable owner tuple**: `run_uuid, context_epoch, share_group, GL_target, GL_name, storage_generation, NVN_id, NVN_storage_owner, guest_pool_generation`. Keep separate `unknown` vs zero. Maintain correct per-(name,face,mip,layer,samples) redefinition, context loss and lazy BC materialization; `glTexSubImage2D` updates content, not nominal storage.
2. Add a **binding provenance** interface used by admission hooks: read current context's bound GL texture/buffer/renderbuffer name and the real generation **without guest memory reads or allocating log memory in the GL hot path**. If an owner cannot be resolved, emit `attribution=unknown` and retain fail-closed safety; do not map owner0 by heuristic.
3. Reproduce the 512-entry history-risk on host: cycle 1024 unique GL names, 1024 create/delete pairs, 24 same-name reuses, two share groups with identical GLuint values, GL context teardown/recreation, one unfreed alias/view, and an event-ring overflow. An independent monotonic generation source for **live** identities (bounded/overflow checked) or a proven recycling scheme is necessary; retired-history loss must be explicitly detectable, not silently joined to a new allocation. No tight loop should accidentally cost quadratic work per draw.
4. For each GL operation emit request `kind` (`cpu_malloc | gl_tex | gl_rb | gl_buffer | egl | dma_heap | unknown`), requested bytes and actual API error/result. A `glTexImage2D(...,NULL)` allocates storage; `glTexSubImage2D` normally does not redefine it. A buffer `glBufferData` re-spec replaces its old declared value, potentially with asynchronous driver retention. Record known CPU live-range overlap separately from GL declared bytes and deferred driver physical state.
5. Build an OFFLINE `tools/peak_memory_waterfall.py` reducer with explicit quality fields `event_complete, sample_complete, identity_complete, owner_known, physical_backing_known`. Reconstruct event lifetimes and top-N overlapping **requested** peaks from run-owned records; compare independently sampled `VmHWM, VmRSS, VmSwap, CmaFree, SwapFree, pgmajfault, pswpin/out`. Report a residual `unattributed` row rather than forcing mismatched totals to reconcile. Missing 100 ms samples are not interpolation candidates.
6. On host, replay known ID280/288 owner cases plus logs whose owner0 GL objects are deliberately ambiguous. Reject phase/time mismatches, reused names, duplicate ID with new generation, incomplete ring, unflushed final event and separate-run mixing. Do not count completed host tests as proof of future device log completeness.
7. The existing **build260** default-off owner ring is a suitable future observer, not a new task to reimplement. Its device qualification is blocked by low CMA; when independent GO arrives, pair observer OFF/ON on the **same binary**, fresh full run identity, bounded runtime, and producer-consumer ring completeness. Stop at unknown owner coverage; don't incorrectly call a `safe_stop` menu success.

**Output:** a source coverage manifest, a replay schema and negative fixtures, a separately versioned host evidence README. CPU/GL logical numbers must stay separate from Mali physical commit/address-space numbers.

### 11.5 K1.4 / `audit/firmware-allocator-backing` — host work made possible by exact ELF match

Do **not** repeat K1's archive extraction, 4-symbol match, or 22-s idle pair. Reuse its pinned SHA/BuildID, DWARF and callsite provenance:

1. From owner-local firmware ELF disassembly/DWARF, map the **caller/callee paths** of `system_heap_allocate`, `alloc_largest_available`, page pools/order fallback, `dma_heap_ioctl`, memory pin/unpin, DMA mapping and any Mali/DRM/display-specific allocator using the matching firmware—not a substitute kernel. Record source paths and relevant GFP/migratetype flags. The `{8,4,0}` table proves order fallback, not that every page comes from CMA.
2. Classify likely *per-operation* backing: normal movable pages, CMA, pinned DMA, driver-private allocations or indeterminate, with `exact_binary` / `source_matched` / `inferred` / `unknown` tags. Trace MainUI's known DMA-BUF exporter **identity** separately from its CMA backing.
3. Read K1's existing histogram correctly: `MIGRATE_CMA` 571 order-0, 71 order-1, 9 order-2, 3 order-3, 1 order-4 and **3 order-10** free blocks; 3,861 derived pages versus 3,864 reported. This is a real *free-buddy histogram*, not a success oracle for an unknown-flag DMA allocation, and not evidence that the remaining 112+ MiB of CMA is pinned GPU data.
4. Publish a decision table for each admission `request_kind`: `proven_cma_bytes?`, `needs_contiguous_order?`, `eligible_zone?`, `driver_uncertainty?` and `can_admit_without_new_device_risk?`. At present, unknown backing must remain `unknown`. Use offline counterfactual A1 models and compare them against the existing 4 exact refused inputs, without manufacturing a safe threshold.
5. **Optional separately approved** non-invasive comparison on a newly established good baseline can evaluate whether boot/idle/movable pages change; do not reboot automatically or trigger synthetic allocations/compaction/pressure. If no owner can be attributed from safe evidence, keep K1.4 as `unknown` and pursue structural host memory reduction rather than endless read-only repetition.

**Stop:** no device launch, lowering `T2_STORAGE_MARGIN_MIB`, disabling the CMA check, forced compaction, GPU buffer allocation, unsafe debugfs mounts, overwriting saves or inferring a kernel leak from `CmaTotal-CmaFree`.

### 11.6 P1 structural memory candidates — rank by *persistent saved bytes*, not apparent fast benchmark numbers

| Candidate | Working hypothesis and baseline | Host proof first | Future on-device qualification | Risk / decision |
| --- | --- | --- | --- | --- |
| **S1: eliminate retained duplicate decoded mirrors** | Original BC3 blocks + linear copy + decoded RGBA + guest image pools may overlap; owner92 requests 64.8 MB CPU scratch, but duration/lifetime unknown | Prove exact guest/source write generation, distinct backing aliases, last reader, snapshot fileback effects, and lossless regeneration after access | Repeated equal-phase RSS/HWM, swap/CMA minima + correct live pixels; one owner family only | **Best lossless option if mirrors truly survive uploads**; temporary scratch alone may have no durable impact |
| **S2: selective large-atlas GPU compression** | 3600² RGBA decoded payload 51,840,000 B and 3600×2160 31,104,000 B; 8192² BC path can request 256 MiB when reached | Query actual TSPS GLES formats/extensions, test BC→ETC2/EAC/ASTC transcoding and alpha/sRGB/mip equivalence with owner-provided assets on host, preserve source generation | Driver memory/CMA after identical owner life stages, rendering/alpha and reupload cost, no unreported quality loss | Largest potential, but format/transcoding changes are **not** bit-exact and physical savings unproven |
| **S3: 1080p composition family only** | Guest has three colour + one depth-equivalent 1920×1080 targets despite 1280×720 output; nominal max saving **17.58 MiB** if reduced to panel size | Target last-reader/viewport/depth/UI mapping and nominal GL storage | Exact content/ROI KMS images, GPU fill and storage, three matched pairs | Existing `ZERO_RENDER_SCALE=2` historically negative; do not reopen without live target attribution |
| **S4: safe unused storage retirement** | GL/NVN objects may outlive last consumer | Prove last NVN reference, GL fence/completion, EGL context and restoration semantics | Actual physical refunds and page fault/reupload churn (not just decreasing logical ledger) | Do not delete resources based on texture ID or Mali VA reuse; unsafe without fences |
| **S5: runtime/Unity CPU-path optimization** | Historical Loading includes high CPU/replay wall and swap stalls | Reject input/sampler/log overhead; attribute **exclusive** owner PCs and SVC/page stalls | Correct-world 60 s P95 improvement after safety | **Not a solution** for a game that cannot enter stable menu |

**Decision checkpoint:** if two genuinely independent, evidence-selected lossless strategies cannot create a safe, non-swapping menu, publish a feasibility report with a lower bound on *required simultaneous* owner-pinned allocations and unknown driver bytes. Consider optional explicit image-quality compromises or different backend only with exact acceptance. The ~1 GiB device cannot be treated as having an extra 128 MiB of dedicated free CMA on top of normal RAM; CMA accounting overlaps system RAM.

### 11.7 Conditional device experiment matrix — NEVER run under the current NO-GO

**Precondition**: documented operator-approved recovery of a safe device baseline; freshly qualified `boot-id, MainUI PID/starttime, ELF dev/inode/SHA, CPU mode, CMA/order distribution, SwapFree, active processes`; a margin derived from the exact allocator's expected request (not from the historical warning alone); clean independent rollback. Without **all** preconditions, continue host-only.

1. **V1 short pixel proof**, before a large performance sweep: event-trigger on a current-run `NVN_PRESENT_PIXELS frame=N`, capture physical 1280×720 KMS while correct PID lives, recheck owner and capture a newer serial. Capture owner-qualified OFF and ON of any lossless texture candidate at the *same semantic phase*. If candidate dies before capture, report `NOT_CAPTURED`, not parity success. Use `frame_diff.py` tolerance=0 for deterministic frames; animation differences get a separately defined ROI/timing verdict. Sprite/title/logo/home captures are not world pixels.
2. **E4 owner logs**, paired observer OFF/ON on the same exact binary with `LC2_LIFE_EVENTS=1` as the sole switch. Assert no overflow, all budget owners joined by snapshot time, accurate generations and negligible observer wall/RSS penalty. Old ID280/288 gaps must remain unresolved historically if source evidence is absent.
3. **M4 one-factor A/B** for the selected, already host-tested mechanism. Keep `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL, conservative admission and independent stop. Require >=3 useful same-scene pairs with completed frame identity, process/driver/kernel delta and correct image. Accept **higher minimum** MemAvailable/CmaFree, lower HWM/VmSwap/fault pressure, no new kernel/GL errors and unchanged cleanup; meaningful progress beyond normal variability. Fast first-present timestamps do not override a worsening floor.
4. **W0 menu gate:** 3 independent game-owned **120-s true-menu** sessions, `LC2_MENU_EVENT`, fresh owned KMS serials, no memory/admission stop, no sustained swapping, no unsafe CMA, correct Spruce MainUI and sysfs after exit. Publisher splash does not qualify.
5. **W1 world functionality gate:** from a checked page oracle issue released/acknowledged input through `MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> WORLD`, with no frame-serial reuse or blind 600-ms holds. Once real world pixels appear, test two-direction movement, interaction, inventory/dialogue, audible audio, owner's backed-up save and cold reload. Confirm shader draw semantics, especially all seven TEST substitutes, framebuffer/depth/scissor and no unpinned shaders. Three clean loops.
6. **F1 performance gate:** idle, movement, busy/effects scenes each >=60 s with 3 runs. Whole-world-frame P50/P95/P99 in monotonic time and unique presented serials, exclusive guest/bridge/GL/GPU-wait/fault timings, target Hz, thermal/governor, input/audio/save and memory. Report 5/10/15/20 FPS checkpoints honestly. 30 FPS requires per-scene P95 <=33.33 ms **with correct world and healthy memory**, not merely a fast Loading animation.

**No-Go interpretation:** an owner-verified `T2_STORAGE_ADMISSION` or `T2_MEMORY_FLOOR` safe stop can validate instrumentation and cleanup; it cannot pass V1 image parity, W0 menu, W1 gameplay or F1 FPS.

### 11.8 Exact next PRs and unambiguous done conditions

| Order | Suggested PR | Implementation file(s) | Required check | Gate |
| --- | --- | --- | --- | --- |
| **1 (host)** | `fix/bc-stripe-checked-small-mips` | `runtime/lamentum-adapter.patch`, `tools/test_bc_layout.c/.py`, optional pure size header | All legal mip paths, NPOT/tails/overflow, exact decode, forced **unskipped** C/ASan fixture, manifest/build pin | Host only |
| **2 (host)** | `audit/owner-generation-and-memory-bases` | overlay life-events GL/buffer/owner paths; `tools/ledger_bases.py` and new waterfall tests | 1024 unique names, 24 reuses, multi-context, incomplete ring negative tests, per-class owner0 case | Host only |
| **3 (host)** | `audit/firmware-allocator-backing` | host-only DWARF/disassembly reducer + source confidence receipt, A1 policy metadata | Exact firmware-based GFP/heap/CMA class facts or explicit `unknown`, no “warning=failed ioctl” | Host only |
| **4 (host, conditional)** | `perf/one-retained-owner` | exactly one BC mirror/GL representation candidate + fixtures | Correct bytes and consumer lifetime, stable source generation, rollback hash, no quality change | Host preparation |
| **5 (device GO required)** | `test/live-pixel-and-e4-qualification` | existing owned capture/navigation, E4 ring, pixel comparison | Identical semantic scene and genuinely live candidate image; all active texture IDs joined; one-variable control | Blocked |
| **6 (device GO required)** | `feat/world-playability-acceptance` | owned page/input oracle, draw census, audio/save probes | 3 W0 passes then 3 full W1 gameplay loops | Blocked |
| **7 (gameplay required)** | `perf/scene-p95-30fps` | exclusive CPU/GL/renderer profiling + `tools/analyze_perf.py` | Whole-frame P95 and P99 with three replayed 60-s gameplay routes | Blocked |

**Suggested host verification** (after implementing a PR; no device launch):

```sh
python3 -m py_compile tools/admission_offline_replay.py \
  tools/kernel_source_match.py tools/cma_readonly_snapshot.py \
  tools/cma_readonly_compare.py tools/ledger_bases.py
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
# IMPORTANT: inspect unittest SKIP counts. The native BC fixture depends on
# the pinned recovered native adapter + bcdec, and a default skip is NOT a pass.
# Execute the actual C geometry fixture with the pinned adapter source and
# ASan/UBSan where available; fail the PR if the fixture could not run.
# Separately verify 435/435 source hashes, overlay apply/diff parity,
# AArch64 ELF/GLIBC and reproducible manifest/build hashes.
```

**Evidence publishing contract:** one redacted README + machine-readable summary per PR (source/ELF and tools hashes, UUID when applicable, exact inputs, pass/fail/skip, strict identity, observer completeness, rejected hypotheses and rollback). Raw NSO/ROMFS, firmware ELF, game data, owned screenshots and full device memory/logs remain local-only. Only update the “latest” README/cumulative-roadmap pointer after those receipts actually exist. No new device result or FPS claim is created by writing this roadmap.


---

## 12. Post-A1 source re-audit: exact host-first work packages (2026-10-23)

**Reviewed main:** `c05f879` (A1 offline replay), exact checked adapter patch and existing host fixtures; no new target run, source build, game install or measured FPS in this review. This appendix complements the §11 source audit and refines §§2, 5 and 9, and supersedes suggestions to deploy M4 merely because a host fixture passes. The prior audit already covered many alternatives; below are the *specific remaining correctness gaps, their potential effect and falsifiable tests*.

### 12.1 Updated verdict, progress and priority distinctions

- **K1 is partially solved, not "CMA solved".** The exact firmware-kernel binary and order {8,4,0} retry path are established, but nobody has attributed the missing idle CMA pages to reclaimable movable allocations versus pinned CMA consumers. Idle `CmaFree=15,456 KiB` remains a **NO-GO**. A single `nr_free_cma` scalar cannot predict a future higher-order contiguous allocation; `MemAvailable` is a separate resource.
- **A1 is COMPLETE as a formula replay**, not an admissible new allocator policy. Its 359-test host suite reproduced all four build259 denials; no tested option identifies proven CMA backing or an uncertainty allowance. Do not deploy its `proven_CMA_only`/mixed model, choose a margin by trial, or present the denial as a GPU-allocation failure.
- **M3-A / BC stripes are a temporary-memory improvement**, not a sustained-residency result. The source currently takes `capacity = width * 128 * bpp` before computing `first_rows = min(height,128)`; short mips can be over-allocated. However, `LC2_BC_STRIPE_MEDIUM` is OFF in the default launcher and the persistent GPU atlas is still allocated by `glTexImage2D`. Fixing a small-mip malloc can produce *zero improvement to peak GPU residency or to the current device gate*. Treat it as a bounded correctness/low-risk preparatory PR, not the headline solution.
- **Persistent-resource candidates have more headroom potential but much higher correctness risk.** The source/evidence identifies BC3 atlas owners 92 (3600×3600) and 81 (3600×2160), roughly **49.44 MiB + 29.66 MiB of level-0 RGBA8 payload** respectively, before mips/driver overhead; these are nominal GL payloads, not physical CMA bytes. The 1920×1080 composition family can save at most 17.58 MiB nominal when scaled to 720p; it previously regressed performance and is not the first option.
- **F1 remains blocked by W1.** A ~528-ms first BC decode, ~198-ms first GL upload, ~0.836-s historical Loading-main-thread interval, 709-MiB historical Mali/OOM report, or number of menu presents is *not* a steady playable-world frame benchmark. The first target is a correct, memory-safe, interactable world, not synthetic "30 FPS".

### 12.2 PR M4-A — fix the actual stripe allocator contract (HOST ONLY, P0 preparatory)

**Owner source:** `runtime/lamentum-adapter.patch` → both `native/nvn_textures.h::lc2_bc_upload_stripes` **and** `lc2_bc_reserve_first_use` (the latter independently calculates `width*128*output_bpp` for admission); related `native/zero_bc_layout.h`, `zero_bc_decode`, `zero_texture_bc_pixels`, `tools/test_bc_layout.c`, `tools/test_bc_layout.py`. Modify the overlay source in the pinned, clean, **435/435** recovered tree and regenerate the patch, not a second runtime copy.

1. First add a *pure, overflow-checked* `lc2_bc_stripe_plan(format,width,height,bpp,block_bytes,rows_limit)` helper or equivalent testable calculation in an adapter-owned header. Validate width/height, format, bpp and rows_limit against the actual texture/backend limits before arithmetic. Derive `rows = min(height,128)`; `rgba_capacity = checked_mul(checked_mul(width,rows),bpp)`, `linear_capacity = checked_mul(checked_mul(ceil_div4(width),ceil_div4(rows)),block_bytes)`. Use non-overflowing `(width/4)+(width%4!=0)`, not the pre-division `(width+3)` on unvalidated unsigned values. Require `rgba_capacity + linear_capacity` to be checked and representable as both `size_t` and `uint64_t`. Invalid geometry must STOP **before** malloc/GL calls.
2. Replace **both** fixed `width*128*bpp` and `width*128*output_bpp` reservations (the upload scratch and first-use admission estimate) with the **same checked helper**; assert the estimate is consistent for identical level/format/flag inputs. Replace only these staging bounds, not any texture dimensions. Do **not** shrink the full `glTexImage2D(width,height)` storage, the original guest extent, the `t2_texture_budget` charge, the shader catalogue or the frame dimensions. Pass exactly the same peak to the M3-B descriptor, `t2_storage_admit`, the allocated byte count and `LC2_BC_STRIPED_UPLOAD` receipt; no disagreement between claimed and actually requested CPU scratch.
3. For every `y += 128`, derive `rows = min(128,height-y)` safely; independently prove `width*rows*bpp <= rgba_capacity` and the corresponding block-byte range fits its source. Non-multiple-of-four width/height and the final partial stripe need explicit BC block rounding, source offsets, alpha preservation and no write outside the destination. Retain pixel-store alignment save/restore and surface `glGetError()` after each bounded upload where diagnostic mode supports it. Record level, origin, row count and source span only in default-OFF bounded diagnostics.
4. Extend **the existing self-authored** `tools/test_bc_layout.c` fixture rather than adding an unrelated decoder: test BC1/BC3 as supported by this overlay, random-but-reproducible compressed blocks, full-decode-versus-stripe **byte equality** and unchanged compressed source across **all valid mip levels**. Mandatory dimensions: `1×1`, `3×5`, `7×5`, `63×1`, `127×129`, `128×128`, `129×129`, `1023×63`, `1920×1080`, `3600×2160`, `3600×3600`, `4096×1`, `4097×9` (only if admitted by the *real* device limit), plus last-tile cases and invalid/overflow geometry. Assert byte-canaries or guard allocations and no GL calls after rejected planning. **Do not** force the runtime to admit 4097 if the backend limit rejects it.
5. Run host ASan/UBSan where supported and the pinned fixture build; separately compile the production AArch64 overlay with unchanged compiler/ABI and `git apply --check` against the recovered tree. Keep `LC2_BC_STRIPE_MEDIUM` OFF. A host PASS is **not** permission to run build261 on current low-CMA device.

**Acceptance:** identical decoded bytes for admitted formats/levels; accurate max simultaneous *requested* CPU scratch and checked bounds; prior tests, 435-file source baseline and compile unchanged; fail-closed negative tests. **Expected scope:** mostly short-mip scratch; no claim of persistent headroom or pass at the existing 24-MiB CMA gate. **Abort:** decoder corruption, format mismatch, unsupported height/stride, overflow, new allocation/free asymmetry, unexpected change to GL/depth geometry.

### 12.3 PR M4-B — prove allocation coverage, not merely that hooks exist (HOST ONLY)

**Owner source:** `native/nvn_present.h` (previously uncovered direct `glBufferData`), `native/nvn_vertex_stream.h`, `native/nvn_textures.h`, `native/lc2_gl_admission.h`, `native/lc2_life_events.h`, and EGL/KMS initialization; tests in `tools/test_gl_storage_layout.py`, `tools/test_ledger_bases.py` and a new pure reducer if necessary.

1. Build a machine-checked *callsite inventory* in `tools/gl_allocation_inventory.py` with columns `file:function:GL_API`, target/context, logical owner, backing class `CPU/GL_texture/GL_renderbuffer/GL_buffer/EGL_surface/DMA_heap/unknown`, creation, respecification, retirement and existing admission/event hook. Scan direct and macro-wrapped invocations of `glBufferData`, `glBufferStorage` (if present), `glTexImage*`, `glTexStorage*`, `glRenderbufferStorage*`, `eglCreate*`, `gbm_*` and DMA-BUF allocation/import paths. Include uninstrumented paths as `unobserved`, never as zero.
2. For `nvn_present.h` VBO and all `nvn_vertex_stream.h` paths, distinguish ***declared bytes*** from *respecification* and *in-flight old backing*. Never add `glBufferData` to a lifetime total as if every respec persisted forever. Use context+GL-name+generation; don't infer allocation from a reused GL name. For EGL/KMS, capture the format, width/height, buffer count and backing **hypothesis** separately; don't infer physical DMA/CMA from descriptor size.
3. Add unit tests that deliberately insert an unwrapped GL storage call into a sample fixture and require the coverage audit to fail. Also inspect `lc2_life_generation_next`: its 512-entry historical name table can run out after >512 distinct GL name keys even if live entries retire. Exercise >=1024 unique names and reuse with bounded, non-aliased generation identity; report history exhaustion separately from live residency, and never recycle an identity while an old generation remains observable. Host tests must also reject double charge, missing deletion, context switch, GLuint reuse, incomplete ring, missing storage generation and partial final event. One owned event log is not a census when coverage can be incomplete.
4. Derive `peak_memory_waterfall.py` from known logs only: request/retire per storage generation + non-additive resident process totals + memory-sample timestamps. Flag missing rows, owner-less buffers, host-pool aliases and unknown driver bytes. Never sum `VmRSS + Mali descriptor total + GL-declared` into a purported physical-memory total; they may overlap.

**Acceptance:** every source storage allocation site accounted for *or explicitly marked unknown*, exact ledger replay on synthetic fixtures, zero false claims of physical equivalence. **No new device run until GATE-0 is independently reopened**. Discovered hook omission is not itself measured CMA recovery.

### 12.4 PR K1-B — host static CMA provenance before new risky TSPS tests (P0 safety dependency)

The exact extracted TG5050 vmlinux already matches the observed firmware layout. Work next from this **exact release image**, not a generic Linux 5.15 tree. Keep all firmware and proprietary extracts outside Git.

1. On the host, inventory the boot image's **DTB/DTBO** and effective `/reserved-memory`, `linux,cma-default`, `reusable`, `no-map`, `alloc-ranges`, `memory-region`, `cma=` boot argument, IOMMU and display/GPU reserved carve-outs. Use read-only image/dtb decoding and record region addresses/sizes only if legitimately published; do not infer runtime pinned use from a static reservation.
2. From the matching vmlinux, map `system_heap_allocate`, page-pool setup, `dma_heap_ioctl`, `cma_alloc`, GBM/EGL-related driver interfaces and Mali memory allocators; preserve branch behavior and which allocator *may* use MIGRATE_CMA/movable pages. Confirm compile options and call-chain membership; DWARF paths are build provenance, not access to the full vendor source.
3. Classify the missing idle 115,616 KiB of `CmaTotal-CmaFree` as **unattributed**, not "stolen GPU memory"; enumerated MainUI system-exporter DMA-BUF sizes (~10.56 MiB) are not a physical backing map. The three-page difference between non-atomic `/proc/pagetypeinfo` and `nr_free_cma` is not a leak. Describe precisely what evidence would distinguish movable allocation from unmovable/pinned pages.
4. The only target continuation under the current stop is *read-only*, scoped, same-boot snapshots through existing `cma_readonly_snapshot.py` / `cma_readonly_compare.py`: identity, CMA migratetype histogram, `MemAvailable`, `CmaFree`, buddyinfo/order histogram, MainUI/FD inventory and deltas. No new debugfs mount, page-owner toggles, compaction, `drop_caches`, automatic reboot, kernel patch, GPU knob, memory allocator probe or game launch. A later operator-approved reboot comparison is a **separate study**, with its own confounders and rollback, not a default suggestion.

**Acceptance:** an auditable backing/owner hypothesis with a falsifiable non-mutating check, or an explicit `unknown`. An exact kernel match alone is not a go/no-go pass. An order-4 warning followed by a possible order-0 retry is not confirmed success, nor is `cma_alloc_fail=0` sufficient to permit launch.

### 12.5 PR M4-C — qualify one *persistent* atlas/storage reduction (conditional P0, not deployable now)

M4-A primarily reduces peak CPU staging. **To unlock gameplay the stronger hypothesis is removal of actual retained, unreclaimable GPU/guest memory**, while keeping semantic equivalence. Use M4-B owner generations and K1 backing evidence to select **one** of these mutually exclusive branches:

**C1 — lossless first:**
1. For owners 81 and 92 and their exact mip/storage generations, prove from traces whether guest BC source, CPU tiled copy, linear BC intermediate, decoded RGBA buffer, GL storage and file-backed mirror coexist; record creation and *last real consumer* (CPU refresh, texture readback, alias view, sampler, in-flight GPU draw). Show which parts are merely temporary and already freed.
2. Only if a duplicate buffer outlives its last consumer and no generation/write dependency exists, remove or reuse **that one backing** under a default-OFF flag. Preserve compressed guest data and CPU texel-write semantics; ensure source-write generation, alias scope, texture view, context loss and GL fence retirement are correct. Explicitly refuse uncertain immutable-source assumptions.
3. On host, induce a write between two reads and confirm the cache invalidates; test texture name reuse, mip changes, cancellation, alias overlap, stale write-generation, GL resource retirement and process-cleanup leakage. Compare exact bytes/GL pixels before marking quality-neutral. Without a measured retained duplication this candidate is **rejected**, not an optimization.

**C2 — compressed GPU textures: quality trade-off requiring separate opt-in:**
1. Mali GLES3 can in principle support formats different from desktop BC3, but **do not assume** a particular S3TC/ETC2/ASTC extension/profile works on the live target. After device safety opens, query GL version, compressed format list, sRGB/alpha support, `GL_MAX_TEXTURE_SIZE`, block alignment, mip and `glCompressedTexImage2D` outcomes on a small bounded synthetic fixture before committing to a format.
2. A 3600×3600 RGBA8 level-zero atlas nominally uses 51,840,000 bytes; 3600×2160 uses 31,104,000 bytes. An 8-bit-per-pixel BC3/ETC2-RGBA representation would be 12,960,000 and 7,776,000 bytes *if* an allowed compressed format is supported and the whole asset fits. The level-zero declared reduction is **62,208,000 bytes** for both; extra levels, driver allocation and actual CMA changes are unknown. BC3 bytes cannot simply be uploaded as ETC2/ASTC: transcoding/encoding is necessary and usually lossy, with CPU/IO cost.
3. Prototype BC3→target compressed form with synthetic assets **on the host**, preserving block padding and alpha/sRGB metadata, tracking source content generation, filtering/mips and sampler behavior. Never ship a proprietary converted atlas in Git; cache validation must use game-owned data locally. Benchmark cold/warm encode cost and saved live bytes; encode-on-every-load could trade OOM for intolerable launch times.
4. Maintain separate labeled modes **quality-neutral** versus **compressed/quality-changed**. For a changed format compare correct world/publisher/menu images both perceptually and pixel-wise; report the trade-off, do not claim `tolerance=0` equality if conversion cannot meet it. Only the owner can accept visible degradation.

**C3 — smaller composition targets:** `ZERO_RENDER_SCALE=2` already exists, was performance-negative and at best saves 17.58 MiB of **nominal** 1080p-family storage. Test only after data proves those specific allocations are retained and blocking the next gate. The guest's 1080p literals are hardcoded; the panel is already 720p. No blanket docking-mode fix is needed.

**C4 — cheap diagnostic control:** `LC2_BC_INPLACE_DECODE=1` already exists. Host-test byte-equivalence for BC1/BC3 level tails and alias/readback; conditionally A/B on exact device scene *only after go/no-go*. It eliminates an overlapping linear decode allocation, not the persistent GPU texture. If the retention waterfall shows no long-lived effect, stop spending cycles here.

**Pass to promote any C branch:** 3 phase-matched, single-toggle device A/B pairs **after explicit go**, complete run/pixel identity, no new order warnings or GL errors, lower *measured* persistent footprint at the same semantic point, improved minimum headroom across CMA and `MemAvailable` outside control variability, and unchanged required input/audio/save workflow. Any candidate that saves only the allocation-request counter remains unqualified.

### 12.6 W0/W1 game-enablement checklist (blocked, but host testable)

**Do not conflate launch, title UI, "Loading", and game world.** The original game reached a New Game/Controls/Loading sequence historically, but later builds 251/256b/259 stopped before the menu. Resume at the *latest safe executable* only after GATE-0; avoid trying to find a shader in an unsafe test.

1. Add host test vectors to `tools/page_oracle.py` and `tools/owned_navigation.py` for `MAIN_MENU→NEWGAME_CONFIG→CONTROLS→LOADING→WORLD_VISIBLE`, including 1–2 FPS missed taps, long taps skipping rows, repeated serials, disappeared PID, stale capture, HOME overlay, incomplete logs, and no acknowledged button release. The page oracle must report an **ambiguous/refused** state rather than advancing on a plausible screenshot.
2. On future safe W0 runs, require *current-game-owned* frame (boot+UUID+PID+starttime+ELF hash+present serial), not just a logo or Spruce UI. Three **120 s** stable real-menu sessions and clean CPU/SDL/DRM restore without admission stop, OOM, rising unsafe pressure, or new GL errors are required before any New Game command.
3. For W1, add a bounded **per-draw** census to distinguish program linked from program actually used. Audit the **seven TEST-only shader substitutions** against visible scene attachments; don't regenerate IDs 0–45 or invent a substitute on a missing shader. Verify viewport/scissor/depth/blend, FBO completeness, texture format, GL error and final KMS pixels in the same owned frame.
4. Follow actual physical gamepad press+release and character movement in **two directions**, one world interaction/dialogue/inventory return, audible audio (not only a nonzero queued PCM count), protected save+clean quit+cold-load of same checkpoint. Verify all three loops with separate run identities, no damaged existing saves and real scene progress. Loading spinner or automaton-injected input does not pass.
5. A post-gate game run must use strict bounded watchdog and pre/post pinned kernel pressure+MainUI identity; abort on any CMA unsafe change, new allocator warning, storage refusal, OOM/kill, run identity drift, lost KMS present serial, missing cleanup or unexpected writes. Do not silently weaken floor96/cap300/GL policy as a workaround.

### 12.7 F1 instrumentation and 30-FPS decision (only after W1)

Use an FPS **budget ledger per accepted world present**, not gross presents or an averaged Loading frame:

| Independent frame component | What to instrument | Error to avoid |
| --- | --- | --- |
| Guest IL2CPP/Horizon/SVC | TID+starttime-pinned CPU sample, call site, guest PC, exclusive interval | Mistaking a hot native thread for the guest main thread |
| NVN→GL replay | CPU submission and command translation, per-frame GL-call volume | Double-counting CPU work and GPU wait |
| Texture/materialization | BC decode, copies, repeated `glTexSubImage2D`, shaders compiled this frame | Treating cold first-load cost as steady FPS |
| GPU completion/present | EGL swap, actual KMS serial delta, blocked/duplicate presents, optional reliable GPU timestamp | Equating fast CPU submit with a physically displayed frame |
| Memory/IO | major faults, `VmSwap`, reclaim/compaction stalls, data-load IO and change in CMA | Attributing unrelated background-system pressure to the game |

Keep `tools/perf_sample.py`'s already-fixed **target HZ** accounting. Require intact `boot,run,PID,starttime,build,serial` everywhere; use two distinct serial endpoints for an interval. Report P50/P95/P99 and **P95 ≤ 33.333 ms** on each of three ≥60-s routes (idle, motion+interaction, busy light/effects), after warm-up, plus drop ratio and cold scene-transition duration. Separate GPU-vsync multiples 16.67/33.33/50 ms from true CPU/GPU work. Qualify observer-OFF cost (<5%) and three reproducible one-variable A/B pairs before promotion.

**Feasibility stop:** after M4-A/B and two source-selected structural memory candidates, if there is no safe, repeatable W0→W1 path or recovered sustained margin, report `not feasible with current backend and measured safety envelope` with reasons and confidence; possible next branches are target quality trade-off, independent texture backend, or a device with more RAM. Do not indefinitely repeat unsafe margin tests.

### 12.8 Exact PR order and reproducibility receipts

| Sequence | Proposed branch / smallest review unit | Files, proof and decision |
| --- | --- | --- |
| **1** | `perf/m4a-bc-stripe-small-mips` | `runtime/lamentum-adapter.patch`, `tools/test_bc_layout.c/.py`, host byte-equality/overflow/ASan, **no device** |
| **2** | `audit/m4b-gl-buffer-egl-census` | New inventory tool+fixtures, `tools/test_gl_storage_layout.py`, ledger reducer; host-only source coverage or explicit unknown |
| **3** | `audit/k1b-firmware-memory-topology` | Read-only offline vmlinux/DTB provenance, existing CMA reducer tests; **no target mutations** |
| **4** | `perf/m4c-retained-atlas-candidate` | Exactly one lossless source-identified retention change, or separately labeled compressed quality experiment; no deploy until device gate |
| **5** | `test/e4-v1-device-qualification` | Only after independently documented go: short one-factor observer and pixel parity tests; refuse if unsafe |
| **6** | `test/w0-w1-owned-gameplay` | Three true-menu passes then three playable loops with audio and save/cold-load |
| **7** | `perf/f1-world-frame-budget` | Exclusive stage timing, 3 world routes, three per-toggle A/B pairs and P95 proof |

Host commands (no TSPS access needed):

```sh
# Inside this public port repository
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m py_compile tools/admission_offline_replay.py \
  tools/cma_readonly_compare.py tools/ledger_bases.py tools/perf_sample.py
git diff --check

# With the independently recovered, pinned 435-file adapter source tree:
# verify tools/baseline-manifest.sha256 first using its existing project contract,
# then run:
git apply --check /path/to/lamentum-portmaster-tsps/runtime/lamentum-adapter.patch
# Rebuild with the pinned GCC10 AArch64 container; do not deploy under NO-GO.
```

Every report must include `phase`, run/build hash, exact flag delta, capability/allocator provenance, complete/partial observation flags, safety disposition, pixel oracle status, and `host_only / device_qualified / gameplay_qualified` scope. **The absence of new target measurements in this roadmap is explicit; none of its proposed savings are established FPS or memory gains.**


---

## 13. Evidence-first execution gates after the main@1604ed9 re-audit (2026-10-23)

**Scope and precedence.** This review examined the current checked adapter patch (blob 91ebbfd), the latest README/roadmap, committed evidence and the host fixture source. It did **not** compile native code, execute a host suite, install or run the game, or perform a fresh device measurement. It refines the implementation/verification order in §§11–12; it does not replace their full file-level instructions. Source has not acquired new runtime changes since A1 at c05f879; commits c05f879..1604ed9 are documentation-only.

**Decision:** the next deliverable is *not* an FPS tweak, an increased timeout, a new emulator, or another progressively smaller CMA margin. First close (a) testable scratch-planner correctness and (b) retained-memory/allocator attribution, then qualify one high-impact memory reduction. W0/W1 and measured gameplay FPS remain blocked by the independent device safety gate.

### 13.1 Verified evidence versus hypotheses: do not promote one into the other

| Claim / observation | Evidence and status | Consequence |
| --- | --- | --- |
| build259 tested at 64, 48, 32, 24 MiB admission margins | [device matrix](../evidence/m2b-e3-build259-margin-sweep/README.md): all four stop with cmafree-margin, no menu/presents | **DONE as a bounded refusal-path test**; do not retry a lower margin |
| Idle post-run CMA remains low | [K1 exact-kernel investigation](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md): CmaTotal 131,072 KiB, CmaFree 15,456 KiB in read-only pairs | **NO-GO for game launch**; the owner/physical backing remains unknown |
| Kernel order-4 warning establishes failed DMA-heap request | **NOT proven**: firmware order {8,4,0} can retry smaller orders; no request-completion receipt | Keep allocator completion and pinned CMA bytes **unknown** |
| Four denials follow the implementation's GL+scratch+margin arithmetic | [A1 replay](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md): four owned records match; 359 host tests reported | **DONE as formula replay**, **NOT** proof all requested GL/scratch bytes are physical CMA |
| Medium BC stripes improve temporary requested memory | [build251 A/B](../evidence/m3a-bcstripe-b251-01/README.md): one 1920x1080 owner stages 10,368,000 B versus 1,228,800 B; all six arms still hit floor | Host-fix correctness; **no persistent-memory or playable-world claim** |
| Lifetime and GL windows are completely attributed | **NOT proven**: [build256b M3B](../evidence/m3b-build256b-pair-20261022-01/README.md) misses buffer/EGL/driver backing; [E4](../evidence/e4-owner-pair-host-2026-10-23/README.md) leaves old IDs 280/288 partly unresolved | M4-B must establish callsite completeness, context/generation and unknowns |
| build260 is a verified TSPS playable build | **False**: build260 is host-built and not installed; build259 is the last reported installed binary | Never label build260 device-qualified or infer world FPS |
| 30 FPS is achievable or impossible | **Unproven**: historical Loading/main-thread measurements are not qualified steady world frames | Defer performance verdict until W1/F1, or state a bounded feasibility stop |

**Important cross-resource distinction:** 128 MiB CMA is not interchangeable with around 600–700 MiB reported MemAvailable, compressed texture-budget bytes, GPU virtual/driver payload bytes, guest heap RSS or swap. Never sum those non-independent gauges, or convert an observed GL payload saving directly to reclaimed CMA.

### 13.2 PR gate A — M4-A production-safe BC planner (first host-only change)

**Implement in:** the pinned adapter overlay; patch sites **native/nvn_textures.h::lc2_bc_upload_stripes** and **lc2_bc_reserve_first_use**, shared checked geometry in an adapter-owned pure header, **tools/test_bc_layout.c** and **tools/test_bc_layout.py**.

**Exact source defect to remove:** the checked patch still computes upload capacity as (size_t)width * 128 * bpp, while first_rows is min(height,128); first-use reservation separately computes (uint64_t)width * 128 * output_bpp. For height < 128, this requests and admits scratch that cannot be used by that mip. The two paths can also diverge if edited independently. The source's (width+3)/4 block-count expression should not be used as a general unchecked integer formula.

**Ordered changes:**

1. Create one pure plan(width,height,level,format,output_bpp,max_rows) routine, with checked width/height/format/device-limit, size_t/uint64_t multiplication, block ceil division, total sum, and explicit invalid-geometry result. Use row_count = min(height,128). Return decoded_stripe_capacity, BC_linear_capacity, required_peak and per-stripe source extent. Reject arithmetic overflow *before* a log begins or any GL, malloc, or guest state changes.
2. Route both the advance first-use admission and real upload scratch through the **same plan output** for each mip. Do not change GL texture dimensions, mip count, the 300 MiB budget, game render scale or texture data. If the admission guard is conservative for unknown actual driver allocations, preserve that separate uncertainty; do not disguise it as staging bytes.
3. Verify the partial last stripe: width/height not divisible by four, height 1/5/63/129, small mip chains, both allocate and refresh, save/restore GL_UNPACK_ALIGNMENT, and source block boundary. Test BC1/BC3 and other formats only where the overlay already implements them correctly; reject unsupported formats.
4. Add randomized immutable-source decode comparisons with full reference decode and guard-canaries; exact byte equality and nonmutation. Include invalid width, zero height, UINT_MAX overflow, out-of-bounds source stride, unsupported 4097 width, repeated materialization, error/cleanup path and mip/cubemap negative cases. Compile/run the **native C fixture**, not merely its Python wrapper.
5. Make a missing native baseline or bcdec an explicit verification failure in the PR job; **tools/test_bc_layout.py currently calls skipTest when the pinned adapter is absent**. A 359-test suite with skipped native BC checks is not M4-A acceptance. Publish discovered skip count, native stdout, optional ASan/UBSan result, source hashes and actual rebuilt ELF identity.

**Accept:** exactly equal decoded bytes in supported cases, shared admission-vs-actual scratch bound, no new ownership/lifetime change, native C suite actually executed and passed, clean baseline 435/435, strict GL build and existing host tests pass. **Reject:** unknown compressed formats auto-coerced, lost source-write coherency, changed final pixels, under-admission or implicit margin relaxation. **Impact classification:** peak host CPU scratch only; potentially negligible effect on persistent GPU CMA or first-world access.

### 13.3 PR gate B — M4-B: complete the allocation census before choosing what to free

**Implement in:** a new static source inventory/reducer plus **native/nvn_present.h**, **native/nvn_vertex_stream.h**, **native/nvn_textures.h**, life-event/generation code and their existing fixtures.

1. Scan patched, actual compiled sources in the pinned tree, not only changed patch lines. Inventory direct and indirect glTexImage*, glTexStorage*, glCompressedTexImage*, glRenderbufferStorage*, glBufferData/glBufferStorage, framebuffer attachment, EGL/GBM surface creation and dma-buf import/allocation. Mark each as wrapped+measured, wrapped+unmeasured, not reached, or unknown; do not equate an absent event with an absent allocation. A fixture introducing an unwrapped glBufferData must fail CI.
2. Implement **context/share-group + GL object name + object generation + storage/subresource generation** keys. Verify fresh creation, realloc/respec, deletion, reuse, alias views, context loss and deferred GPU completion. In the current adapter, lc2_life_generation_next's historical key table is fixed to 512 entries and can exhaust on >512 distinct names; distinguish full history from live-owner exhaustion and fail closed rather than reuse an observable generation. Test >1024 distinct/reused keys.
3. Give the directly created VBO in nvn_present.h and all other buffer-store paths the same generation-aware observed ledger as textures/renderbuffers. Include EGL surface/buffer count as a separate uncertainty class; never charge a full EGL scanout surface as if its backing were proven CMA.
4. Separate **new requested GL bytes**, **old live backing**, **potential overlap on re-spec**, **short-lived decode/linear scratch**, **fileback mirror**, **guest committed bytes**, **process RSS**, **Mali driver metadata**, and **CMA free**. Preserve sample time, run UUID/boot/PID/starttime/ELF, completion confidence, known/unknown flag and source line; sums of overlapping bases are forbidden.
5. Re-run the old build251 missing-owner replay without retroactively adding fabricated events. New E4 events in build260 are capability only, **not** a measured fix until an actual device-qualified future run under GATE-0. For any incomplete ring, generation conflict, or absent source-write epoch, output inconclusive.

**Accept:** mechanical inventory of all compiled storage paths or explicit unknowns, fail-on-new-callsite regression test, exhaustive synthetic generation and transactional-lifetime cases, no claims of measured physical refund. **Priority:** this work is more important to gameplay than optimizing individual ms of BC staging, because it identifies *retained* memory candidates.

### 13.4 PR gate C — K1-B: exact-kernel DMA/CMA backing, without target stress

**Only host analysis of the already identified exact firmware image**, plus the previously permitted read-only device snapshot protocol if it remains safe. Keep vendor binaries/local dumps outside the public repo.

1. Extract the effective DTB + bootargs memory topology offline; locate reusable CMA reservations and all display/GPU regions, DMA heaps, IOMMU paths and their declared sizes. Distinguish a static reserved-memory layout from current allocation occupancy.
2. Disassemble/trace the **exact firmware** system_heap_allocate and candidate-order {8,4,0} return paths, DMA-heap ioctl completion/errno, page-pool allocations, and potential CMA pages. Map Mali/GBM/EGL/display consumers where symbol/driver evidence exists. Record whether backing is *proved*, *possible* or *unknown*, with the precise evidence that would falsify the classification.
3. Compare stable same-boot read-only snapshots of CMA free **and free-by-order histogram**, plus MemAvailable, vmstat allocations/faults/migration, MainUI identity and DMA-BUF inode/FD census. Preserve non-atomic observation differences. Never label the observed 115,616 KiB unavailable CMA as leaked GPU memory or assume that listed ~10.56 MiB of MainUI DMA-BUFs explain it.
4. Define a conservative operator-reviewed launch prerequisite based on **repeatable free headroom, order/fragmentation risk, known minimum allocation envelope, stable idle background state and a proven rollback**. No arbitrary fixed CmaFree threshold, no unilateral reboot, force-reclaim, drop_caches, CMA knobs, reduced floor or lower margin.

**Accept:** grounded backing/topology map and a defensible read-only go/no-go *decision*. If backing or minimum headroom cannot be established, return **UNKNOWN / NO-GO**. Do not manufacture a green gate from kernel module version or no increment of cma_alloc_fail.

### 13.5 PR gate D — M4-C: optimize retained bytes, not only upload requests

Select **one** candidate from the complete M4-B/K1-B waterfall. The large BC3 atlas owners 92 (3600x3600) and 81 (3600x2160) correspond to **82,944,000 B (~79.1 MiB) nominal RGBA8 level-zero storage combined**, not proven pinned CMA. Source and device measurements must show *how much of this survives at the same phase* before promising a benefit.

1. **First candidate, lossless duplicate lifetime:** correlate a texture's guest BC source, source-write epoch, linear temporary, RGBA staging, GL allocation, alternate CPU view, fileback mirror, aliases, shader last-read and GPU fence. If two identical buffers coexist after a confirmed last consumer, eliminate one under a default-OFF option. Test mutation after first upload, context recreation, texture name reuse, CPU readback and GL fence delay. If lifetime cannot be proved, **do not free**.
2. **Second candidate, same-format residency:** when a GL image is retained unnecessarily, investigate safe deferred materialization or true late release with exact revalidation; reject visible flicker, repeated expensive re-upload, or unsignalled GPU use. BC stripe and in-place paths are peak-scratch controls and should not be counted as persistent storage savings.
3. **Conditional trade-off:** hardware compressed ETC2/ASTC must first be verified from *real device extension/format queries after the safety gate opens*. BC3 bitstream is not binary-compatible with ETC2/ASTC; conversion would require an encoder/transcoder, could be lossy and could make scene loads slower. Preserve separate opt-in quality-changed results and cold/warm encode cost. A theoretical 8-bpp target yields 20,736,000 B for the two atlases, saving 62,208,000 B **nominal level-zero payload**, not established CMA or performance.
4. **Lower-return controls:** 720p composition-scale reductions historically offered no demonstrated frame-time gain and at most 17.58 MiB nominal for the four 1080p targets; shader catalogue generation or blank-frame bypass cannot replace semantic world correctness. Reassess only against a verified retained owner/last reader.

**Accept lossless:** byte-identical host fixtures, unchanged required game pixels, lower verified *same-phase retained physical pressure/headroom* in future qualified paired runs, no new fault/reclaim churn or lifetime corruption. **Reject:** “requested scratch -60 MiB” advertised as “CMA recovered -60 MiB”, swapped-away CPU pages mistaken for actual GPU reclaim, lower resolution silently described as lossless, or single post-run gauge comparison.

### 13.6 W0 -> W1 -> F1: gameplay and FPS qualification, in that order

**GATE-0 independent stop remains active.** The following are test specifications and host preparations, *not authorization to launch now*.

- **W0: stable title/menu.** After explicit safety GO and installed ELF+launcher+helper hashes, require three separate ≥120 s owner-qualified sessions with a real game-owned KMS frame, responsive physical press/release, working options/back navigation, zero allocator/GL errors, and consistent cleanup. Spruce clock/home pictures never count as game frames. The new E4 ring should be tested observer OFF/ON, same binary and one flag delta, only if CMA conditions permit.
- **W1: first real world.** Drive MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> WORLD_VISIBLE with UUID, monotonic present serial, boot/PID/starttime and owned capture bound at each transition. The game must draw verified non-spinner world pixels through actual shader draw calls and correct FBO, depth, blend, scissor, sampler, viewport and render-target state. Audit all seven TEST-only shader substitutes on executed world draws; shader *link* or arbitrary non-black pixels are insufficient.
- **W1 functional:** move in two directions using the physical pad, interact with one item/NPC and return from dialogue/inventory, confirm audible output, save to an owner-protected checkpoint, quit cleanly and cold-reload to the same world state. Run three independent loops; protect original saves and confirm input release.
- **F1 baseline:** only after W1, capture ≥60 s per route (idle, walking/interacting, effect-heavy) with fresh frame serials, period P50/P95/P99, percent delivered frames, guest-main exclusive CPU, NVN->GL submission, blocking GL driver/GPU completion, BC page faults/redecode, swaps, audio glitches, memory and cold scene transitions. Use observer-OFF controls; keep the CPU target-HZ correction. Count *real completed game-world frames*, not Loading spinner presents, and do not add overlapping CPU/GPU intervals.
- **F1 acceptance:** three repeatable same-state one-factor A/B pairs; target **P95 <= 33.333 ms** for real world frames for each scenario with functioning audio/input/saves, sustained CMA + MemAvailable margin, no memory leaks or unsafe swap/reclaim, no new shader substitution or image mismatch. If the device is limited by 60 Hz vsync, make frame-pacing/dropped-frame estimates explicit.

**Abandon/defer rule:** after the full host M4-A/B and two evidence-chosen structural memory candidates, if no safe minimum memory envelope emerges, do not keep attempting lower margins. Report that the current Unity/NVN/GLES implementation cannot yet be device-qualified, explain unknowns, and consider a separate higher-RAM target or a strictly optional quality/performance compromise. This is a bounded technical decision, *not* a proof 30 FPS is impossible in all implementations.

### 13.7 Review checklist, hand-off command sequence and release labels

| Ordered PR / report | Must include | Status now |
| --- | --- | --- |
| **M4-A** checked BC stripe sizing | Shared bound, native fixture actually run, overflow/BC pixel parity, manifest and AArch64 result | **DONE host at main@509cc985; build261 not device-qualified, see §14** |
| **M4-B** complete memory-class inventory | Coverage gate, GL buffer/EGL unknowns, generation >512, retained-owner waterfall | TODO host |
| **K1-B** exact allocator backing report | DTB/bootargs, exact-code allocator outcome map, read-only CMA order histogram, unknown classification | TODO host |
| **M4-C** one persistent reduction | Proved duplicate lifetime or separately labeled compressed-format experiment | SELECT ONLY AFTER M4-B/K1-B |
| **GATE-0** device readiness | Fresh safe repeatable independent preflight, operator-approved bounds, revert plan | **NO-GO** |
| **W0 / W1** menu and world/controls/audio/save | Three owned sessions and three functional loops | BLOCKED |
| **F1** world frame budget | True present accounting, P95 and overhead, three controlled A/B pairs | BLOCKED |

Run the host checks *in a provisioned pinned recovered-source environment*. Do not mistake the following generic smoke commands for execution of the native BC fixture:

~~~sh
# Public-repository Python suite; record executed, failures AND skips.
PYTHONPATH=tools python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py'
python3 -m py_compile tools/admission_offline_replay.py tools/cma_readonly_compare.py \
  tools/ledger_bases.py tools/perf_sample.py
git diff --check

# Independently recovered GPL baseline + generated overlay, not stored in this Git repo:
sha256sum -c tools/baseline-manifest.sha256
git apply --check /absolute/path/to/lamentum-portmaster-tsps/runtime/lamentum-adapter.patch
# Then use the pinned build_lamentum.sh recipe in the README, capture ELF hash/GLIBC.
# Supply LAMENTUM_ADAPTER_NATIVE to make tools/test_bc_layout.py run its native C fixture;
# any native fixture SKIP disqualifies M4-A, even if the Python suite passes.
# Do not install, launch or attempt New Game while device GATE-0 is NO-GO.
~~~

For each PR publish: base/head commit, overlay sha, recovered-source manifest receipt, actual test count+skip list, exact compile artifact SHA, content/pixel/reference test provenance, no-device/device-qualification scope, previous evidence linked, disproof attempts, expected benefit class (scratch/requested/declared/retained/physical/FPS), and an explicit **not-measured** field where appropriate. Keep owner game data, firmware blobs, raw kernel logs and screenshots out of the public repository.

**Audit-only verdict at main@1604ed9:** no new performance measurement, no device action, no new executable build, no gameplay and no 30 FPS qualification were produced by this review.

## 14. M4-A host-only execution result (2026-10-23)

**Source base:** the M4-A source/tests were developed against `main@1604ed90bc39f4834bfa23de71401bc9f94661fe`, with recovered adapter base `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`. Before publication, `main` was fast-forwarded through `0f9c17434cd6e7faea264b120d22ffb936136e30` and `815c8c6ff2de4c87faa26b6d68c69a6094d63b03`; the intervening upstream changes were documentation/evidence-index updates and were preserved. The implementation followed §12.2 on `main`; the regenerated runtime patch matches the adapter overlay diff (SHA-256 `23762e1bcd4c5b759c7417647f24e1df4430bcd4fd32e56f0c2a007954db50a8`) and applies to pristine source.

**Host result:** the mandatory native fixture passed with `LAMENTUM_REQUIRE_BC_TEST=1` and zero skips. It exercised 86 full-vs-stripe decode parity cases, 86 unchanged-source checks, 258 buffer guards, 244 contiguous exactly-once stripe-row regions, 28 metadata-only large-chain mip checks, 18 in-place cases and 15 rejected inputs. The reservation fixture passed 14 tests and equated preflight scratch to the upload plan. The full suite passed **359/359**, zero skips/failures/errors; Python compilation, `git diff --check` and the **435/435** baseline manifest passed. ASan/UBSan passed in the pinned GCC10 container (the host itself lacks the sanitizer runtime libraries).

**Cross-build:** pinned image `pmjs-arm64-spruce-local@sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c`, owner image `image-09` with verified ROMFS section digest, AArch64 ELF64 PIE; size 2,206,776 B, Build ID `43aa590ec1209841671e9ad0d8de726d9f5f90a2`, max GLIBC 2.27, SHA-256 `0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332`. It remains a local host artifact, not installed. Full receipt: [cumulative §94](performance-roadmap-30fps.md#94-m4-a-host-only-bc-stripe-sizing-and-native-fixture-2026-10-23) and [M4-A evidence](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md).

**Qualification boundary:** no device install/run, live GL call, physical upload-region observation, KMS pixel capture, alias lifetime, RSS/CMA reclamation, gameplay or FPS was tested. `CmaFree=15,456 KiB` remains the last read-only value and the device gate remains **NO-GO**. Continue with §13.3 M4-B host-only lifetime/coverage work and §13.4 K1-B; do not deploy this candidate without a separately reopened safety gate.

---

## 15. Revised publication, install and runtime-testing gates (2026-10-23; overrides indefinite device NO-GO)

**Correction and precedence.** Earlier instructions conflated (1) committing/publishing host-verified code, (2) transferring files to the handheld without running them, and (3) starting a memory-intensive runtime. The historical idle CmaFree of **15,456 KiB** is a real warning **at the timestamp and boot measured**, not a permanent state and not proof that all occupied CMA is physically pinned. Linux may use CMA for movable pages, but their successful reclaim/migration and a usable contiguous allocation are not guaranteed. Historic allocator warnings and exhausted CMA must still be respected. **This section supersedes any older blanket “device NO-GO / no install / M4-A publication postponed” instructions for future work; historical measurements and their original run verdicts remain unchanged.**

**M4-A is already host-published:** [main@509cc985](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/509cc985893e) and [M4-A evidence](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md). Build261 AArch64 SHA-256 0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332 was compiled locally; there is **no recorded install or device gameplay result**. Native BC parity fixture, ASan/UBSan, 359/359 host tests (zero skipped), 435/435 baseline hashes and cross-build are recorded. Do not redo this PR or report it unpublished because the device is held.

### 15.1 Independent work scopes and go/hold status

| Stage | What it authorizes | CMA condition | Status/acceptance |
| --- | --- | --- | --- |
| **H: host development and publication** | Edit, run host suite, build, commit, push, merge PRs, publish source, public-only receipts and redistributable binaries (never proprietary game assets) | **None**: a historical low CMA must not block a host PR or release | M4-A **DONE**; M4-B / K1-B may proceed now |
| **S: staged transfer / non-executing install** | Inspect device, back up previous ELF, copy candidate/launcher/helper to temporary path, verify hash; optionally activate installed files **without launching** | No CMA minimum for copying files. Require storage, device and busy-process safety checks, valid backup and rollback. | Outcome **STAGED** or **INSTALLED_NOT_RUN**, never device-qualified |
| **D: bounded no-input game diagnostic** | Initial guarded runtime launch, first-present/admission evidence; no New Game | **New fresh stable read-only preflight**, conservative allocation headroom and a working runtime safety guard are mandatory | **ALLOW_BOUNDED** or **HOLD_RUNTIME**, recorded with reasons |
| **W: actual menu/New Game/gameplay/FPS** | Navigation, world loading, interaction, saves, sustained timing | D passes repeatedly, stable memory margin, correct visuals and safe cleanup; W0 then W1 then F1 | **BLOCKED until positive independent qualification** |

**Explicit agent instruction:** M4-A source publication is already done; do not say “publication skipped” because build261 was not installed. Host improvements and PR publication never require a device test. Publishing a binary is optional and subject to ownership/licensing and size limits. If staging is possible but running is unsafe, state exactly **STAGED / RUNTIME HELD**, not “all device work skipped”.

### 15.2 Fresh read-only preflight: do not mistake an old CMA number for a new one

Perform the existing bounded, read-only tools/cma_readonly_snapshot.py + tools/cma_readonly_compare.py process **before considering a D run**. A transfer-only S install may use a limited storage/busy-state preflight instead.

1. Pin target model/firmware/kernel, boot ID, monotonic sample times, MainUI PID+starttime+executable inode, actual installed ELF/launcher/helper SHA and current CPU mask. Check for a live game, pending principal command, immutable/swap state and sufficient SD card space. A busy principal/game or mismatched hash blocks activation.
2. Capture **at least two complete same-boot snapshots** separated by ~20–30 seconds of quiet operation: CmaTotal/CmaFree, nr_free_cma, free CMA buddy blocks *by order*, MemAvailable, MemFree, SwapFree, CMA alloc/fail, page faults, migration/compaction and swap deltas, MainUI DMA-BUF inode/FD inventory and recent fresh kernel OOM/allocation warnings. Do not reboot or run the game to obtain these samples.
3. Reducer must reject partial captures, changed boot, process identity drift, negative/reset counters, nonmonotonic time and missing essential CMA order data; label UNKNOWN rather than guessing a safe value. Distinguish normal background noise from a consistent pressure trend.
4. Compare with prior device phases (roughly 88–103 MiB free CMA in some earlier reads versus ~15 MiB at the last failure). These are **historical comparison points**, not certified safe thresholds. Free CMA alone does not certify contiguous allocation, physical driver backing or reclaimability. Do not equate MemAvailable or CPU scratch with guaranteed usable CMA.
5. Publish a compact preflight receipt: boot, timestamps, same-state/deltas, allocator warnings, run/ELF hashes, projected allocation demand and separate uncertainty reserve, outcome, and rationale. Raw kernel/firmware data remains local-only.

**Preflight decisions:**

- **ALLOW_STAGING:** Device idle, hashes/storage/backup/atomic handoff credible. File staging is allowed even when CMA is too low to run the game. An installer that autostarts the runtime is **not** staging and must satisfy D.
- **ALLOW_BOUNDED:** Two valid stable read-only samples; no fresh allocator/OOM warning or unsafe fragmentation; positive **justified** reserve for the selected bounded allocation path **plus uncertainty** under working strict GL, 96 MiB MemAvailable floor and 300 MiB texture budget; a recorded margin/rollback/watchdog. Base the reserve on the actual per-class requirement and historical device behavior, not an invented universal MiB threshold. Conservative all-requested-bytes-possibly-CMA arithmetic may be retained as a safety upper bound, but it is **not evidence** that CPU malloc always consumes CMA.
- **HOLD_RUNTIME:** The historical danger state around 15 MiB persists without an explanation/proven reclaim and usable block order; samples incomplete or unstable; recent allocation warning; enough margin cannot be demonstrated; or safety tooling is unverified. No runtime launch. Host M4-B/K1-B and read-only diagnosis continue.
- **WORLD_NOT_AUTHORIZED:** A single good preflight or successful game splash cannot authorize New Game, extended runs or a 30 FPS claim. W0/W1 have independent gates.

No blind CMA-margin sweep below the tested 24 MiB; no disabling the admission checks or changing the floor, texture cap, strict-GL behavior, firmware/kernel, CPU governors, CMA knobs, drop_caches, compaction or boot state to force a green decision. Invasive recovery needs a separately justified operator decision.

### 15.3 Safe install without runtime launch

1. Verify the exact build261 architecture/GLIBC and SHA-256 against M4-A evidence, matching launcher and mandatory identity helper, correct target storage, available space, device idle and absence of pending principal command. Preserve prior build259 and its verified backup; no untracked in-place overwrite.
2. Copy the ELF and matching helpers to an **inert temporary staging path** (or perform a verified atomic install only if its orchestration guarantees **no automatic execution**). Read back each SHA-256 and check permissions; document previous file/restore plan. Do not submit a launch command.
3. If file/identity mismatches, restore the prior verified files; preserve MainUI and original CPU mask. Report stage/installed-not-run and no execution. A staged file must not be presented as device-qualified, GPU-safe or playable.
4. If the installer or principal flow implicitly launches the game, leave the ELF staged only until D is authorized.

If the user has already authorized ordinary device development/testing, host publication and safe staging do not require a fresh human approval for each harmless step. Destructive recovery actions or changes to safety limits do.

### 15.4 First guarded runtime diagnostic, ONLY after a positive D preflight

1. Select one exact ELF, same owner image and one behavior change. Keep T2_MEMORY_FLOOR_MIB=96, T2_TEXTURE_BUDGET_MIB=300, strict GL and default-off risky flags; do not silently invent or lower T2_STORAGE_MARGIN_MIB. An unresolved admission model must remain fail-closed, even when that means no run.
2. Run a brief **15–30 s maximum initial no-input** title/admission smoke (or shorter when prudent). Pin boot/run UUID/PID+starttime/build hash. Use existing bounded watchdog, light memory sampling and typed STOP/error recording. Abort on new DMA/CMA allocator warning, exhausted safety margin, T2 refusal/floor, OOM/kill, present-serial identity error, lost MainUI or incomplete critical samples. Do not continue to New Game.
3. Capture fresh preflight, during-run and postflight metrics with timestamps. Do not add declared GL storage + GPU metadata + RSS as if physically distinct, nor equate a CPU scratch request reduction with reclaimed CMA. Spruce cleanup image is not a game frame.
4. Verify cleanup: game exited; original CPU mask/online modes restored; stable MainUI; no pending principal command; no fresh kernel warning; rollback available. If degraded, set HOLD_RUNTIME immediately. Only with repeatable safe startup and later proper owned menu/visual checks can W0 begin.

**No optimistic shortcut:** If enough CMA and allocator backing cannot be established, the answer is **host work published and candidate staged; D held on fresh preflight**. An *old* low reading is reason to remeasure, not reason to ban all future device interaction.

### 15.5 Required report fields and next tasks

Every agent handoff must distinguish:

- Source/PR publication: **DONE** for M4-A at main@509cc985 (or exact newer commit); host-only verified.
- Build261: local AArch64 candidate SHA with host test counts, 0 native skips; binary publication, staging and device qualification each separately marked DONE/NOT DONE.
- Device preflight: **NOT RUN**, **COMPLETE STABLE**, or **INCOMPLETE**; show *timestamp and boot* for the last CMA and order histogram. Never call the 15,456 KiB result current unless newly observed.
- Stage decision: ALLOW_STAGING / HOLD_STAGING and reason.
- Runtime decision: ALLOW_BOUNDED / HOLD_RUNTIME and measured reserve/warning rationale; gameplay W0/W1/F1 separately NOT VERIFIED until tested.
- **Next host work:** M4-B complete GL/EGL/buffer lifetime/generation census and K1-B exact firmware DMA/CMA backing; M4-C persistent atlas optimization only with owner/lifetime proof.

**Historical device result remains NOT PLAYABLE, gameplay FPS unmeasured.** This policy is not a finding that build261 works on device. It corrects agent scheduling: *do the independent safe work and publish it; perform a fresh safety decision before any demanding runtime operation.*

## 16. M4-B host-only source callsite census (2026-10-23)

This is the first M4-B substep, **not** M4-B acceptance. The §13.7 checklist reflects its `main@1604ed9` audit snapshot; §§14–16 record later work, with the revised operation gates in §15.

**Inventory:** [`tools/gl_allocation_inventory.py`](../tools/gl_allocation_inventory.py) scans all C/C++ files in `native/` and `framework/` after the overlay is applied; [`tools/gl_storage_callsite_policy.json`](../tools/gl_storage_callsite_policy.json) binds each candidate site to an explicit status and the exact source-tree digest. `build_lamentum.sh` now runs this gate after patch application and before compilation. The source snapshot has **390 files**, SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`; adapter base `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`, runtime overlay SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.

The scan found **77** storage/copy/attachment/surface candidates: **69 direct and 8 indirect**. The ledger records **12 wrapped+unmeasured**, **65 unknown**, zero wrapped+measured and zero not-reached. The fail-closed fixture adds a new unclassified `glBufferData` path and confirms policy validation rejects it. Focused inventory tests pass **7/7**, generation/lifetime tests **10/10**, and the full tools suite **370/370** with no skips/failures/errors; baseline **435/435**, patch applicability and pinned AArch64 build262 pass. Generation-table behavior and the exact build result are detailed in §17 and the [M4-B evidence](../evidence/m4b-gl-allocation-inventory-2026-10-23/README.md).

**Limits / next:** this scans a source-tree superset, not an exact compiler-unit/include-closure map; indirect NXGL candidates remain unknown. Host tests and the target CPU fixture do not prove game-runtime reach or transactional delete/alias/context-loss/deferred-completion safety. No driver allocation, backing, RSS/CMA refund, gameplay or FPS was measured. Next M4-B work: derive exact build reach, complete the remaining identity/lifetime matrix, then buffer/EGL accounting and the separated memory-class waterfall. Build262 remains uninstalled; the fresh read-only preflight is recorded in §17, but D runtime remains held because the launcher leaves `T2_STORAGE_MARGIN_MIB` unset and no per-run margin was authorized.

## 17. M4-B generation-history capacity and overflow separation (2026-10-23)

**Scope:** Host correctness, pinned AArch64 cross-build, and a standalone target-CPU fixture; no build262 game install or runtime execution. This advances M4-B but does not close its runtime lifetime gate.

**Implementation:** `LC2_LIFE_GENERATION_CAP` is now **2,048** (previously 512). The generation history is separate from the existing 512-entry live-owner/subresource tables. Redundant per-row `seen` storage was removed. When history capacity is exhausted, or a generation would wrap at `UINT64_MAX`, `lc2_life_generation_next()` fails closed and increments `generation_history_overflow`; live-owner table exhaustion increments `live_owner_overflow` instead. Both counters appear in the observation summary. The two exhaustion causes are no longer conflated.

**Host validation:** tests cover 1,200 distinct names and their reuse, 1,024 create/delete pairs, 24 same-name reuses, identical GLuints in separate share groups, full-history and `UINT64_MAX` refusal, independent live-owner exhaustion, and storage/delete event-ring overflow. Focused generation/lifetime tests pass **10/10**; full tools suite **370/370**; baseline source manifest **435/435**; current adapter patch applies cleanly. The scanner still finds 77 sites, with 12 wrapped+unmeasured and 65 unknown.

**Static memory cost:** host `sizeof(lc2_life_events_state)` changed from **155,504 B** to **200,576 B** (**+45,072 B**). The compiled AArch64 ELF `.bss` changed from **12,809,440 B** in build261 to **12,854,512 B** in build262, also **+45,072 B**. This is a static section-size difference; no heap allocation was added, but physical residency, RSS, swap and CMA effects were **not** measured.

**Build:** source base manifest 435/435 and patch applicability passed; the inventory gate matched **390 files / 77 sites**. Built in `pmjs-arm64-spruce-local:20261002-gcc10` (image ID `sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c`). Build262 ELF: **2,206,936 B**, Build ID `9395a24ac719269308b30476f8631349f47242a4`, max GLIBC **2.27**, SHA-256 `dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc`. Candidate remains uninstalled.

**Target-side fixture and preflight:** a standalone AArch64 executable built from the build262 patched header ran on Longan/SpruceOS (firmware 1.0.1, kernel 5.15.147, glibc 2.33): exit 0 in 0.183 s, ELF hash `f4da9806df30504a946ac7af45191451ff4564237be854744781b18b3978a2fa`, max GLIBC 2.17. It passed 1,024 create/delete pairs, 24 reuses, same GLuint across share groups, history/wrap refusal, distinct overflow counters and ring overflow. The temp ELF hash was read back and file removed; MainUI remained, no game was launched, and installed build259 remained unchanged. Two same-boot read-only snapshots 44.009 s apart showed CmaFree **130,412 KiB** both times, MemAvailable **703,500→704,048 KiB**, SwapFree **2,065,884 KiB** unchanged, no CMA failure/major-fault/swap-I/O deltas, no filtered kernel allocation/OOM warnings, and 31 order-10 free CMA blocks. This does not prove physical backing or authorize a game run.

**Remaining gate:** the fixed 2,048 history cap still fails closed and must be monitored; context teardown/recreation epochs and full alias/view lifetime semantics beyond reporting outstanding-view deletes remain open. The host tests and target fixture do not establish exact compiler reach, runtime call coverage, full transactional re-spec/delete/deferred-completion, buffer/EGL ownership, driver backing or physical memory refunds. The build262 game candidate remains uninstalled; D launch is held because `T2_STORAGE_MARGIN_MIB` is unset and no per-run margin was authorized. Continue with the remaining identity/lifetime matrix and exact compiler/include closure before any runtime attempt.

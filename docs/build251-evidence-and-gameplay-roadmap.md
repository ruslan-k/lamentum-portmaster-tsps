# Build251 reassessment and next gameplay/performance roadmap (2026-10-22; historical pre-A/B baseline)

> **POST-DEVICE AUDIT — 2026-10-23 (READ THIS FIRST):** [Current detailed post-build251 plan](post-build251-device-audit-roadmap-2026-10-23.md) and [canonical roadmap §78](performance-roadmap-30fps.md#78-post-build251-device-ab-audit-memory-headroom-and-playability-critical-path-2026-10-23) supersede this page's **pre-device-run task status**. Three same-ELF OFF/ON pairs **were run** (not pending); all six stopped at the 96 MiB floor with zero menu events, candidate KMS pixel parity is missing, and 4/6 live budget-to-texture-pair replays fail on missing IDs 280/288 despite zero event overflow. Medium BC stripes remain default OFF. Prioritize E4 owner-pair coverage, M3-B phase-aligned peak memory, V1 event-triggered live KMS, E3 storage correctness/admission, then one durable M3-C memory saving. No gameplay or gameplay FPS has been verified. [Device receipt](../evidence/m3a-bcstripe-b251-01/README.md).


> **Authority and limit.** This is a source-and-committed-evidence review of `main` at `6797f5f2104fec4e4d3110390ae1fbc04a06285c`. It adds **no new on-device result**. Latest owned, device-executed memory test is **build250**, not build251. The port is **NOT PLAYABLE**; there is no verified first world, controller gameplay, save/load or gameplay FPS. Historical loading-frame durations are **not** FPS evidence. Read [§74](performance-roadmap-30fps.md#74-build250-per-object-budget-and-gl-storage-replay-memory-gate-remains-open-2026-10-22) and [§75](performance-roadmap-30fps.md#75-m3-a-bc3-medium-width-stripe-staging-candidate-build251-device-ab-pending-2026-10-22) for the preceding receipts. This page is the detailed implementation companion to roadmap §76.

## 1. Evidence-based current state: completed versus unproved

| Item | Actually completed | Remaining gate |
| --- | --- | --- |
| Launcher | Spruce principal launch and CPU sysfs value/mode restoration; current launcher avoids unavailable `stat` utility. Owner-verified cleanup reports no game process. | Keep hash/boot/PID/starttime verification on each experiment. |
| Shader/runtime bring-up | ARM64 runtime, strict GL, 45 catalogue entries (7 TEST-only) and historical UI/New Game/Loading paths; ESSL/constant-buffer work; no new shader frontier in latest no-input runs. | Actual world draws, visually correct shaders, test-placeholder audit, control and audio during world. |
| M1/M2A accounting | Build250 has a run-scoped, timestamped per-object T2 charge journal and GL-storage replay with no overflow **for that run**. `tools/ledger_bases.py:replay_texture_budget` matches both budget snapshot and GL summary. E1's prior false STOP/stale frame attribution is corrected. | Multisubresource overwrite, generation reuse beyond current observed sequence, aliases/share group, GPU completion and physical driver residency. |
| M3-A staging | Build251's `LC2_BC_STRIPE_MEDIUM=1` source change, fixture and host compilation; **281 host tests passed**. Default remains OFF. | **Three controlled A/B pairs on TSPS**, source-generation and pixels, actual `MemAvailable`/swap/CMA/RSS effect. |
| Safety | Runtime `T2_MEMORY_FLOOR` stopped build250 at the current 96 MiB floor, no owned kernel OOM evidence; 300 MiB texture cap unchanged. | Pre-allocation admission before transient/permanent GPU/CPU pressure; reliable menu headroom. |
| Gameplay / 30 FPS | Nothing validated on build250/251. Historical `newgame-20` reached 709 presentation events but ended after Mali OOM indications; that is not successful world entry. | Live owned KMS world frame, movement, interactions, save/cold load, then real scene FPS P50/P95/P99. |

The build250 owned run is `40d57167-d5b1-4071-9bdf-a3b2dd028a92`, ELF SHA-256 `fd83556cd52776f4371a1644e9d013cfcb317275d14e907c331f8f2ec7cbd74d`. [Evidence](../evidence/m2a-budget-20261022-01/README.md) and [machine-checkable replay](../evidence/m2a-budget-20261022-01/budget-replay-receipt.json):

- Prelaunch `MemAvailable=673736 KiB`, `CmaFree=102848 KiB`, `SwapFree=2034520 KiB`.
- First-present `MemAvailable=144596 KiB` and `CmaFree=8220 KiB`; texture-budget `112325632 B`. **These are two snapshots, not attribution of the difference to any single allocation class.**
- Floor-stop `MemAvailable=97580 KiB`, `SwapFree=1988100 KiB`, five owned presents, zero `LC2_MENU_EVENT`, one true `STOP status=T2_MEMORY_FLOOR`.
- The end-to-end `SwapFree` delta from the published prelaunch snapshot is **46420 KiB (~45.3 MiB)**. It indicates swap consumption in that window, not necessarily all from a known owner or instantaneous peak.
- Floor-time budget live: `115278848 B` (93 texture IDs). Replayed declared GL: `244815152 B` (88 textures + 2 renderbuffers; 90 storage records). Those quantities have **different accounting bases**. Their difference **does not** demonstrate missing physical VRAM, duplicate residency, a leak or memory that can be reclaimed.
- Three budget-live IDs (46/51/52) correctly have no live GL storage; direct GL snapshot was `EBUSY=16`; the bounded ordered storage journal, not a guessed synchronous snapshot, supplied the 90 records. Physical Mali residency, share-group identity and completion remain unknown.

**Priority consequence:** there is almost no safe menu-memory margin, significant pressure **before the first present**, and a strong swap/CMA problem. Avoid another long loading, shader-catalogue sweep, blind `glFinish` removal or generic FPS tuning until the memory gate is actually passed.

## 2. P0 / PR M3-A1 — Device-qualify build251 medium BC stripes (FIRST)

**Source sites:** `runtime/lamentum-adapter.patch`, `zero_bc_should_stripe`, `lc2_bc_upload_stripes`, both `zero_texture_refresh` and texture initialization branches. `LC2_BC_STRIPE_MEDIUM=1` is default-OFF and does not come from `port/Lamentum.sh`.

**Specific observed target:** build250's BC3 `NVN id=105` at 1920x1080, `format=0x44`, unaliased at observation, touched through the CPU refresh path before first present. IDs are *run-local*: match owner descriptor, source hash/write generation and GL storage identity, not just "105" in another build. The old `width>4096` striped path remains enabled independently of the new flag.

**Expected request-size result (not a RAM result):**

| Path | Decoded RGBA malloc | Linear BC malloc | Sum of overlapping requests |
| --- | ---: | ---: | ---: |
| Full 1920x1080 | 8,294,400 B | 2,073,600 B | 10,368,000 B |
| 128-row stripes | 983,040 B | 245,760 B | 1,228,800 B |
| Difference | | | **9,139,200 B (~8.72 MiB)** |

The output GL texture remains 1920x1080, and `glTexImage2D` + repeated `glTexSubImage2D` may introduce driver staging and calls. Therefore actual host RSS, Mali resources and elapsed upload time can improve, stay equal **or regress**.

### Implementation/testing checklist

1. Confirm intended build251 AArch64 ELF SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78` against **the installed file** before the first arm. Preserve and hash the known-good build250 binary; install/restore through the owner's established atomic deployment and read-back process. Never assume local build artifacts imply deployment.
2. Run existing host suite, source patch application, 435/435 baseline manifest, pinned AArch64/GLIBC compatibility and compiled BC3 equivalence fixture. Confirm all tests actually executed, not merely discovered. The current report says 281 host passes; do not claim device results from them.
3. Inspect prelaunch MainUI and principal ownership, CPU0–3 state/mode, device boot ID, free disk, swap state and game process count. Refuse any concurrent run or unowned process. Back up saves and don't publish private assets.
4. Execute **A/B/A/B/A/B**, six independent owned **no-input** runs of **the same build251 binary**, alternating only `LC2_BC_STRIPE_MEDIUM` (unset or `0` versus `1`). Preserve `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, strict GL, `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300` and the existing safe timeout. Avoid running additional expensive diagnostics in only one arm.
5. Use `tools/device_principal_test.py` only from the trusted, idle Spruce principal workflow. Example **invocation, not an instruction to launch without the preflight**:

   ```sh
   # Run on the host after hash, idle-device and backup preflight.
   python3 tools/device_principal_test.py --budget 90 --wait 240 \
     --env LC2_LIFE_EVENTS=1 --env LC2_MENU_LEDGER=1 \
     --env T2_MEMORY_FLOOR_MIB=96 --env T2_TEXTURE_BUDGET_MIB=300 \
     --env LC2_BC_STRIPE_MEDIUM=0 --evidence evidence/m3a-a1
   # After complete restoration/verification, use a NEW evidence directory:
   python3 tools/device_principal_test.py --budget 90 --wait 240 \
     --env LC2_LIFE_EVENTS=1 --env LC2_MENU_LEDGER=1 \
     --env T2_MEMORY_FLOOR_MIB=96 --env T2_TEXTURE_BUDGET_MIB=300 \
     --env LC2_BC_STRIPE_MEDIUM=1 --evidence evidence/m3a-b1
   ```

   Continue only with fresh evidence directories and verified cleanup for each arm; six runs are an experiment plan, **not** runs performed by this audit.
6. **Behavioral isolation:** A must show a `LC2_BC_FULL_STAGE ... phase=refresh` owner receipt and no medium stripe for the matched texture; B must show `LC2_BC_STRIPED_UPLOAD ... temporary-bytes=983040 ... linear-temporary-bytes=245760` at the equivalent phase, with consistent source data and mip index. Capture the initial camera/UI image while the owned game PID is alive; don't compare the post-exit Spruce screen. A new `GL_ERROR`/STOP, colour/mipmap/sRGB discrepancy or corrupted sprite fails immediately.
7. **Physical effect:** record monotonic timestamps around staging, decode, GL upload, first present and floor stop. Collect `MemAvailable`, `CmaFree`, `VmRSS/VmHWM`, `VmSwap`, `SwapFree` plus actual context-qualified texture ledger; quantify pre-first-present minima/peaks and presentation progress. Compare **matched phases**, not "run A had more frames". If a field is unavailable, label unknown.
8. Classify `PASS_SCOPED` only when decode/pixel equivalence, no regressions and reproducible same-phase memory **or** upload-time improvement is evidenced in multiple pairs. Any improvement smaller than run-to-run noise is **INCONCLUSIVE**. `T2_MEMORY_FLOOR` is still a failed menu gate, even if delayed.
9. Preserve an OFF default until safety, meaningful effect and pixel-quality gates pass. A measured drop in scratch requests alone is **not** a reason to promote this as a gameplay/30 FPS fix.

### M3-A1 code-review edge case to test before promotion

At `lc2_bc_upload_stripes`, `capacity=width*128*bpp` **even when `height<128`**; policy gates only on width. At smaller mip heights the stripe malloc can exceed the full-level RGBA malloc while making more GL calls. Add compiled fixture cases for `1024x64`, `2048x16`, `4096x1`, odd BC block heights, width transitions 1023/1024/4096/4097 and all mip levels of 1920x1080. Follow-up candidate: `rows=min(height,128)` for capacity and/or require a *positive calculated total scratch saving* before striping. Keep source decode output and GL pixels identical; do not change the shipped candidate before its controlled first A/B without repinning the build and restarting the matrix.

**Stop gate:** if build251 still crosses the 96 MiB floor (most likely possibility), classify M3-A1 as a bounded staging experiment; advance to M3-B without entering New Game.

## 3. P0 / PR M3-B — Reconstruct the actual pre-first-present memory peak, not just final live GL totals

### Why this is now more valuable than further final-budget accounting

Build250 already proves same-time budget/GL journal arithmetic **within the observed run**. The dangerous pressure mostly develops before the first completed present; the existing 250 ms watchdog samples may miss a short, larger transient. A `~9 MB` proposed staging reduction is not enough to infer a fix for a menu that already reaches `CmaFree=8220 KiB` at first present.

### Implementation

1. Extend `tools/proc_metrics.py` / `tools/load_metrics.py` with an opt-in **single owner-qualified timeline** `run_uuid, boot_id, pid, starttime, ELF SHA, t_monotonic_ns, phase, sample_status`. Interleave minimal snapshots at: process attach; GL/EGL initialization; each of the largest observed owner's decode **start/peak/end**; GL allocation request/return; first present; texture-ledger changes; T2 floor check; and teardown. Avoid a multi-second/blocking `smaps` scan inside the GL critical section.
2. Record proc signals (`VmRSS`, `VmHWM`, `VmSwap`, per-process `smaps_rollup` at *sparse safe intervals*), system `MemAvailable`/`CmaFree`/`SwapFree`, page-fault count and `/proc/vmstat` swap-in/out deltas if present. Also capture known Mali debug counters with clear units and ownership **only if legitimately readable**. `/proc/pressure/memory` was `null` on build250; handle absence without zero-filling.
3. Add at most N cheap event-bound sample marks in initial seconds (configurable N, dropped-event counter) rather than unconditional high-frequency SSH or printf while allocating. A producer-local bounded ring buffer flushed after the critical call is preferable to blocking `write(STDOUT)` under the budget/GL mutex; retain causal ordering and an explicit `complete` flag.
4. For each large buffer distinguish: compressed guest source, linearized BC intermediate, decoded RGBA staging, GL declared payload, Mali driver allocation descriptor, framebuffer/depth, GPU in-flight, fileback/ZRAM shadow, and unrelated system processes. Do **not** sum virtual guest aliases or two overlapping observations of a reused driver VA as permanent physical bytes. Tie sampling to GL name+generation and NVN owner+generation.
5. For the top 10 contributors emit `t_start/end, owner+generation, compressed_input, staging_requested, staging_live_peak, GL_intent_bytes, snapshot_before/after, GL_error, content_generation, proof_level`. Track requested malloc size separately from observed RSS/cgroup/system deltas; malloc reuse can cause zero RSS growth despite large requests.
6. Compute a **waterfall** from prelaunch to first-present and first-present to stop; annotate sampling non-simultaneity and MainUI exit as a system-memory confounder. Compare an instrumentation-OFF arm on the **same build** to estimate tracing overhead. Stop early on unsafe low CMA/floor; never intentionally replay the old OOM.

**PASS:** for a single safe owned run, all *large* allocation-intent windows and OS snapshots have ordered timestamps and qualified identities, and the run answers whether CPU staging, GL storage/driver, guest backing or another class dominates the **instantaneous** pressure. An unresolved residual must remain explicitly unknown. If the observed event cap overflows, reject "complete" as an outcome.

## 4. P0 / PR M3-C — One meaningful memory saving with correct content/lifetime

Choose **exactly one** based on M3-B data; do not simultaneously increase quotas, switch swap policy and change GL formats.

**C1. Remove redundant overlapping CPU copies (quality-neutral first).** Search in the actual owner code around `zero_texture_bc_pixels`, `zero_texture_refresh`, `lc2_bc_upload_stripes`, `nvn_pointer`, `lc2_fileback_snapshot` and guest-page restoration for a second full decoded/linear staging copy, repeated refresh with unchanged write generation or a host-owned persistent duplicate. A transfer may be elided only after proving guest write/coherency epochs, source pin lifetime and sampler consumption. Prefer direct bounded row/decode-once upload and update-only-on-dirty-owner. Implement counters `refresh_skipped_same_generation`, `bytes_avoided` and `decode_cpu_ns`. Test odd BC coordinates, partial writes, all mip levels, sRGB, GL alignment, context recreation and transient allocation failures. **PASS:** less same-phase peak memory *without* wrong content or slower long-tail stalls.

**C2. Retain genuinely compressed GPU storage (stronger structural upside but quality-sensitive).** Current BC blocks are decoded to RGBA for GLES; `LC2_BC_STRIPE_MEDIUM` does **not** change that. For an immutable high-byte owner, test capability and format triples in the live ES context (ETC2/EAC or actually supported ASTC), exact source/tile conversion, alpha, sRGB, mip selection and sampler/wrap/LOD. Keep the unchanged original compressed source and a source-hash/content-generation-keyed private cache; invalidate on writes. Full image correctness and user approval of lossy representation are needed. This is a *separate* PR, not an automatic default. Measure physical memory if possible and a repeatable KMS ROI, not just GL budget estimates. **Never reinterpret BC3 blocks as ETC2/ASTC without transcoding.**

**C3. Reduce one proven live 1080p render-target family (quality-changing, lower priority).** Existing owner analysis gives **maximum 17.58 MiB nominal** for all four 1920×1080 colour/depth objects changed to 1280×720, not 31.64 MiB saved. First prove framebuffer producer/reader and exact viewport/projection/scissor/UI/UV semantics; gate behind a default-OFF title-specific flag and explicit quality acceptance. Use `tools/frame_diff.py` at tolerance=0 for byte identity; tolerance=2 means approximate visual equivalence, not identical. Reject any GUI hitbox or scene regression. Generic `ZERO_RENDER_SCALE=2` was nearly neutral in historical Loading and must not be sold as a CPU fix.

**C4. Evict/alias only after proof of safe retirement.** A GL delete, reused GLuint or vanished Mali VA alone proves neither last-reader completion nor recovered physical memory. Need texture/view ownership, fence-qualified final consumer, guest write generation, context/share-group generation, re-upload capability and measurable physical refund. The older `LC2_TEXTURE_PAGEOUT` experiment is explicitly OFF and is not a validated release-safe feature.

**C5. Swap/guest-heap or CPU governor changes are diagnostic only.** Do not claim victory from more swap, lower `T2_MEMORY_FLOOR_MIB`, a raised texture cap, `glFlush` replacing `glFinish`, static `MALLOC_ARENA_MAX` tuning or more CPUs. If experiments are warranted later, isolate them and measure page faults, swap IO, CPU cost, cache thrash and thermal stability. Restore all principal/CPU/swap state.

## 5. P0 / PR M2B-E3 — Safety/admission and accounting correctness

This closes **real gaps**, not the already-correct build250 budget replay:

- Implement **pre-allocation** admission before GL storage and relevant large host scratch allocations: checked full mip/layer/face/sample bytes plus conservative *additional driver uncertainty* (unknown until measured). Check current `MemAvailable` and `CmaFree` with an owner-approved margin; log a typed stop such as `T2_STORAGE_ADMISSION` *before* calling GL. A guard prevents OOM but creates **no headroom**; keep 96 MiB floor/300 MiB cap unchanged. Fail closed if sizes/GL formats unavailable. Never take a blocking memory-watch or log mutex under the GL critical section.
- Make journal subresource accounting exact: `(context/share-group, GL object generation, target, face, mip/layer)`. `glTexImage2D` **same subresource redefinition replaces**, a different mip adds, `glTexSubImage2D` mutates content without changing storage; `glBufferData` replaces. Current `lc2_life_events_storage` unconditionally increments `e->bytes` and `e->mips` for an already-live GL name. This is a potential future miscount, **not** a demonstrated build250 mismatch.
- Fix the bounded live observation table: current `LC2_LIFE_EVENT_CAP=512` considers `!entry.name` a free slot, while deleted entries retain the name; a long scene can fill the table despite few live resources. Retain an immutable bounded event history with explicit overflow/`complete=false` and generation-monotonic slot recycling, or separate history from live lookup. Test >512 create/delete cycles and 24 name-reuse cases.
- Build C + Python tests for duplicate face/mip, zero-byte update, name reuse, share-group/context loss, failed GL storage allocation, budget rollback, alias retirement, GL errors, truncated log, reorder, limits and concurrency. The reducer must reject any unreconciled overflow or incomplete journal.
- A physically longer test is gated by headroom; **do not** lengthen runtime or lower the floor solely to exercise the observer.

**PASS:** typed clean preallocation stop, **zero** unaccounted internal counters in fixture and safe owned run, and no invented physical Mali total. If the new observer slows first-present enough to change phase, call that a diagnostic regression.

## 6. P0 / W0 — Menu/headroom gate *before* trying New Game again

**Design acceptance** (keep separate from measured fact):

- Owned **in-game** 1280×720 KMS menu capture, not post-stop Spruce MainUI; expected ELF + boot + PID/starttime and *two newer distinct* presentation serials/consistent page fingerprint.
- 120 s of quiet menu stability, no memory-floor stop, no Mali/kernel OOM, no new GL errors, no low-CMA excursion, no sustained swap growth, and proper game-exit recovery. Target normal **96 MiB minimum** available and plan toward **160 MiB** (~64 MiB extra) for first-world. The 160 MiB target is **not** a measured proof of what world loading needs.
- Three comparable passes, unchanged resource flags, cold/steady state recorded separately. Operator must set a device-specific CMA safe threshold based on measured working margin; do **not** hard-code a guessed threshold.
- Report `menu_reached` independently of `gameplay_verified`. An early safety stop with more present records is still a **FAIL**.

If this fails, loop back to M3-B/C; **do not** navigate to New Game and recreate the historical Mali OOM.

## 7. P0 / W1 — Verified first-world and playable-loop milestone

Only after W0 passes:

1. Use current **owned** navigation helpers (`tools/owned_navigation.py`, `tools/owned_nav_chain.py`, `tools/newgame_navigate.py`). For every action require press/release ACK, distinct newer present serials and independently checked KMS/menu/page fingerprint; never confirm a duplicated frame or stale append-only log.
2. Record transitions title -> New Game config -> controls/loading -> *first-world scene*. Track loader milestones, unique ROMFS reads, texture materialization, actual shader-program **draw** (not merely creation), camera and player updates. Separate `TIME_LIMIT_STALLED`, `WORLD_WRONG_PIXELS`, `GPU_MEMORY_STOP` and `WORLD_ENTERED`.
3. First world must have expected real KMS pixels **while the correct game PID is alive**, correct foreground/UI blend, viewport, colour/sRGB, target/depth/MRT, scene transitions and no TEST-only demanded shaders. A nonblack counter or screenshot of MainUI is insufficient.
4. Demonstrate physical controls: move avatar in two directions, interact, open/close inventory, advance dialogue, pause/menu/back. Capture action-to-frame latency only after input mapping is proved. Check sound is nonzero and actually audible, not solely queued audio frames.
5. Create save in a dedicated backed-up slot, exit cleanly, cold-launch and reload same state, then move/interact again. Do not touch ordinary player saves during development.
6. Three independent correct runs, full runtime/PID/system restoration and no floor/OOM regressions. Record failure classes and owner-qualified logs. Only now mark the project **PLAYABLE (experimental)**.

**Do not** infer that the historical `newgame-20`'s 709 presents are real world frames. Later build250 has no menu events at all; the latest memory gate takes precedence.

## 8. P1 / F1 — Credible 30 FPS work after W1

30 FPS = a **33.33 ms** presentation interval. Apply this to measured **correct gameplay frames**, not overall startup duration, loading, menu, UI animation, or raw `NVN_PRESENT_PIXELS` count. Benchmark at least three >=60 s identical steady-world segments per scenario (idle, movement, visually costly scene; include transitions separately). Capture P50/P95/P99 end-to-end interval, jitter/stall count and actual display cadence; CPU main-thread wall/CPU time, guest-gap, NVN replay, present/swap, GPU waits, ZRAM fault/compress, resource uploads and thermal/governor conditions. For acceptance require P95 <=33.33 ms in target tested scenes, image/control/audio correctness and safe memory; P99 is reported, not hidden.

Order optimizations by new profiler attribution:

1. **Guest main-thread/SVC cost:** use existing `tools/perf_sample.py`, `tools/proc_metrics.py` and C0 cost instrumentation. Find the exact hot owner/PC and its exclusive executing CPU time; avoid "unattributed" as a subsystem. Earlier Loading windows showed `~300 ms` guest gap and `~250 ms` replay; those *historical* numbers cannot forecast world FPS.
2. **Repeated texture uploads/decompression or page faults:** act only on stable content/write generations and measured bottleneck; offload/admit after lifetime correctness, preserve exact pixels and input semantics.
3. **NVN replay/GL driver cost:** optimize redundant state changes, CBUF updates, binding, draw calls only if profiler identifies them; keep GL completion/fence correctness. `LC2_CBUF_SUBIMAGE` was measured neutral in its old comparison; generic scale2 was nearly neutral. Never promote `glFlush` as completion.
4. **Measured GPU fill/bandwidth effects:** quality-off baseline versus one reversible 720p/lighting setting, with identical scene and explicit acceptance of render-quality changes.
5. **Thread scheduling/ZRAM:** one-factor tuning with preserved guest synchronization and verified CPU cores/governor/thermal results; compare performance **and** headroom.

Use `tools/analyze_perf.py` only with single-run raw logs and qualified frame ranges; do not compare stale run-scoped counters. Its current parser and any independent tracing require an audit before being accepted as the *world* FPS oracle.

## 9. Exact next PR order / decision table

| Order | Change / evidence | Acceptance | If failed |
| ---: | --- | --- | --- |
| **1** | M3-A1 build251 six alternating same-ELF OFF/ON arms | Correct pixels/GL + reproducible staging/memory effect; no unsafe cleanup | Keep feature OFF; quantify reason; do not claim RAM saving |
| **2** | M3-B build256b owner windows (BC/non-BC/RB) with ring OFF/ON | Texture/RB windows complete; buffer class incomplete (`nvn_present.glBufferData` uninstrumented); periodic timeline partial; one order-4 DMA-heap page-allocation failure; source-write generation and physical residual unknown | M2B-E3 exact subresources and pre-allocation admission before C1 |
| **3** | M2B-E3 admission + exact subresources/live-table | Typed safe failure; fixture and bounded real-run complete journal | Abort, restore build250 path |
| **4** | M3-C one proven headroom strategy | Real phase-aligned `MemAvailable`/CMA/swap improvement, visual parity | Revert; select next class based on evidence |
| **5** | W0 quiet 120s menu and recovery | Three verified stable in-game runs, floor/CMA headroom | Continue M3-C, never inject New Game |
| **6** | W1 owned first-world and full game loop | Correct scene, movement, interactions, audio, cold save/load | Investigate exact scene/shader/input stop, not FPS |
| **7** | F1 scene-specific P50/P95/P99 profiling | Source-attributed 33.33 ms budget, safe repeated runs | Optimize the largest measured contributor |

### Universal stop/rollback rules

Stop on `T2_MEMORY_FLOOR`, `T2_STORAGE_ADMISSION`, any Mali/kernel OOM notifier tied to the owned PID, unexpected `GL_INVALID_*`, mismatched content/write generation, incomplete storage journal, unsafe GPU fence reuse, pressure below a proven CMA margin, dirty Principal/MainUI/CPU restoration, misidentified game process or corrupted save. Preserve the prior stable ELF, read back hashes, restore system state. Do not call a longer runtime, fewer STOPs, higher swap utilization or host-only pass a physical optimization.

### Immediate host-only regression commands

```sh
python3 -m py_compile tools/ledger_bases.py tools/device_principal_test.py \
  tools/load_metrics.py tools/proc_metrics.py tools/perf_sample.py
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
# Validate patch applicability and 435-file original baseline using the
# existing pinned build instructions in README.md/build_lamentum.sh.
# Never assume these commands test ARM Mali, game frames or physical memory.
```

### Source anchors

- [Runtime overlay](../runtime/lamentum-adapter.patch): `zero_bc_should_stripe`, `lc2_bc_upload_stripes`, `lc2_life_events_storage`, `t2_texture_budget_pre_stop`.
- [Launcher](../port/Lamentum.sh): principal/CPU restoration and default `LC2_TEXTURE_PAGEOUT=0`, floor96.
- [Build250 owned receipt](../evidence/m2a-budget-20261022-01/README.md), [replay JSON](../evidence/m2a-budget-20261022-01/budget-replay-receipt.json), [build248 texture pairs](../evidence/texture-pair-20261022-01/README.md), [launcher smoke](../evidence/launcher-smoke-20261022-01/README.md).
- [Older source-backed priority logic](performance-roadmap-30fps.md#73-build249-evidence-delta-close-the-exact-t2-budget-join-fix-owner-parsing-then-reduce-real-memory-2026-10-22), [New Game bring-up](newgame-bringup.md), [image comparator](../tools/frame_diff.py), [storage source/safety context](g0-storage-layout.md), [historical loading FPS baseline](fps-baseline-2026-10-20.md).

**Current checkpoint (2026-10-23):** build259 is installed (SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`); `.before-259` preserves build256b. Per user authorization, bounded same-ELF arms tested per-run margins 64/48/32/24 MiB with floor96/cap300/strict GL. All stopped before the menu on typed `cmafree-margin` refusals; each refusal preceded any subsequent GL storage event. `SwapFree` stayed constant within each short arm and no new kernel OOM/page-allocation warning appeared. The margin24 arm left `CmaFree=14,244 KiB`, still `15,384 KiB` after 20 s and `15,456 KiB` in the latest read-only preflight; the idle CMA pair stayed at `15,456 KiB` for 30 s with MainUI only; its system-exporter DMA-BUF FDs do not establish CMA residency, and debugfs accounting was unavailable, so the cause remains unknown. Stop lower-margin tests and do not launch again until read-only CMA investigation and recovery. Evidence: [margin sweep](../evidence/m2b-e3-build259-margin-sweep/README.md). No menu, New Game, gameplay, no-swap gameplay, or ≥30 FPS is verified; keep floor96/cap300/strict GL and leave launcher margin unset.

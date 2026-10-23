# Lamentum TSPS — post-build262 evidence-led gameplay recovery and 30 FPS roadmap

> **ACTIVE EXECUTION PLAN — 2026-10-23.** Audited `main@0784e27d3af4d730ee223f77d569af1793532546` against source, the `evidence/` index, the build259 device receipts, build260–262 host receipts, and the earlier detailed roadmaps. This is a **documentation/source-evidence reassessment**, not a new handheld run, benchmark, firmware change, or proof of gameplay. **NOT PLAYABLE; no qualified world FPS.** This file supersedes the *next-action order* in older roadmaps, not their historical measurements. The independent H/S/D/W safety stages in [the existing §15 policy](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go) remain authoritative.

## 0. One-page decision

**Do next on host:** **M4-B2 exact compiled reach → M4-B3 transactional GL/GBM/EGL lifetimes → M4-B4 reconciled memory-class waterfall**, in parallel with **K1-B exact-firmware allocator/backing analysis** and **W-prep offline gameplay-oracle/shader tests**. Do not redo M4-A BC geometry, the 2,048-history fix, K1 kernel identity, or A1's four-denial replay.

**Then choose exactly one measured, lossless retained-memory optimization (M4-C)**, not another speculative BC scratch or render-scale arm. Independently perform a *fresh* read-only same-boot device preflight before any launch. Non-autostart staging of a verified candidate is a separate operation and is not a gameplay test. Proceed D → W0 → W1 → F1 in that order, only when each previous gate passes. A failed or inconclusive gate means HOLD, never a silent margin/floor change.

**Crucial distinction:** `requested scratch`, `declared GL bytes`, `process RSS`, `driver physical backing`, `DMA-BUF exporter size`, and `CmaFree` are different measurement bases. Do not add them or call a logical saving a physical CMA saving. A successful title/menu/Loading present is **not** a world frame.

## 1. Verified progress and still-open evidence

| Work | Verified as of this audit | What this does **not** prove |
| --- | --- | --- |
| Earlier bridge/display | ARM64 Switch/Horizon bridge, NVN→GLES, Spruce/KMS output; historical menu/controls/Loading captures; 46 shader entries (0–45) | Correct first-world rendering, physical controller, audio, save/load |
| M3-A/M3-B | Same-build diagnostics and CPU scratch overlap measurements; 41 BC/non-BC/depth request windows on build256b | Retained physical memory, buffer/EGL coverage, pixel parity; both build256b arms hit floor |
| Build259 A1/E3 | Four `T2_STORAGE_ADMISSION:cmafree-margin` denials with margins 64/48/32/24 MiB, re-created exactly by host replay; no menu in those runs | That CPU malloc is CMA, a safely relaxable margin, or a viable boot |
| K1 firmware/CMA | Target TG5050 firmware 1.0.1 kernel binary matched the observed 5.15.147 symbol layout; order-4 `system_heap_allocate` warning may retry order-0 | Historical ioctl completion, physical CMA owner, allocation success, or safe launch |
| CMA snapshot | In recorded idle *same-boot* reads: `CmaTotal=131,072 KiB`, `CmaFree=15,456 KiB`, `nr_free_cma=3,864`, stable counters 36/0; MainUI `system` exporter FDs total 11,075,584 B | That all unavailable CMA is pinned/leaked or attributable to MainUI; that this is today's device state |
| Build260 E4 | Host owner-event ring + missing-pair classification; 317 test checkpoint; IDs 280/288 unresolved in original build251 logs | On-device owner/pair reconciliation |
| Build261 M4-A | Checked short-mip BC stripe/reservation geometry; 86 native byte-parity cases, ASan/UBSan, 359/359 suite, pinned AArch64 build | Runtime usage, visual parity, RSS/CMA or FPS gain; stripe flag still default-OFF |
| Build262 M4-B (partial) | 390-source/77-callsite census: 38 texture, 6 buffer, 3 renderbuffer, 23 attachment, 3 copy, 4 EGL; 12 statically wrapped/unmeasured, 65 unknown; bounded 2,048-key generation history, independent 512-live-entry cap; 370/370 host tests; AArch64 ELF SHA-256 `dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc` | Exact compile reach, transactional lifetime correctness, a device run, backing or gameplay. Static .bss +45,072 B is **not** measured runtime RSS/CMA |
| FPS | Historical title/Loading timing and CPU attribution, including a no-win 640×360 window render-scale arm | **Any** live playable-world FPS or sustained 30 FPS |

Primary receipts: [M4-B](../evidence/m4b-gl-allocation-inventory-2026-10-23/README.md), [M4-A](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md), [K1](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md), [A1](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md), [build259 sweep](../evidence/m2b-e3-build259-margin-sweep/README.md), [build256b](../evidence/m3b-build256b-pair-20261022-01/README.md), [E4](../evidence/e4-owner-pair-host-2026-10-23/README.md), [historical FPS baseline](fps-baseline-2026-10-20.md).

## 2. Strict priority and dependency matrix

| Order | Work package / suggested branch | Location | Completion gate |
| --- | --- | --- | --- |
| **P0-H1** | `audit/m4b-compiled-reach` | host | Reproducible actual compile/link reach; each of 77 candidate sites explicitly `compiled-reachable`, `compiled-unreachable`, or `unknown` with proof |
| **P0-H2** | `fix/m4b-storage-transaction-lifetimes` | host | Fail-closed per-context/share-group object/storage generation; transactional respec/delete/alias/deferred GPU release tests, buffer and EGL owner model |
| **P0-H3** | `audit/m4b-memory-class-waterfall` | host first, device later | No double counted sums; logical and process/driver/CMA deltas time/identity joined; missing samples propagate UNKNOWN |
| **P0-H4 (parallel)** | `audit/k1b-dma-cma-backing` | host + bounded read-only snapshots | Exact firmware allocator/DT memory map; physical allocation classes proved vs possible vs unknown; justified conservative prospective headroom |
| **P0-H5 (parallel)** | `test/world-oracle-and-shader-receipts` | host | State-transition, input release, owned capture, shader **draw** audit and negative fixtures pass without running game |
| **P1-M** | `perf/m4c-lossless-retained-memory` | host, device gated | One evidence-backed retained-memory candidate, byte/pixel parity and lifetime/fence correctness; measured positive memory margin, not only scratch size |
| **P0-D** | fresh device safety + short title diagnostic | device only after preflight | Positive fresh D decision and bounded no-input run, with full cleanup |
| **P0-W0** | three correct, safe menu sessions | device gated | Current-game-owned menu pixels and event, healthy memory, no swap growth |
| **P0-W1** | first world/input/audio/save/cold-load | device gated | Three complete playable loops with actual world pixels |
| **P1-F1** | actual world frame pacing / 30 FPS | device after W1 | 60 s per route, three matched A/B pairs per promoted change; whole-present P95 ≤33.333 ms in required routes |

### 2.1 P0-H1: prove the *compiled* 77-site set, not just the source-tree superset

**Files:** `build_lamentum.sh`, `tools/gl_allocation_inventory.py`, `tools/gl_storage_callsite_policy.json`, new `tools/test_gl_compiled_reach.py` and a redacted receipt.

1. Keep the existing after-overlay source SHA and callsite-ID policy; **do not replace** a 77-site, 390-file inventory with grep counts. In the *pinned build environment*, collect actual compiler invocations, translation-unit filenames, `-I`, `-D`, response files, and per-unit `-MMD` dependencies or preprocessor inclusion traces. Record compiler path/version and source/overlay hashes. Resolve the effective compiled include closure and linked objects; do not assume the 8 `framework/nxgl` indirect dispatch candidates reach this binary.
2. Key a site by stable `path|API|dispatch|callee|ordinal`, then map it to compilation unit(s) and reachable wrapper/dispatcher. Treat macro aliases, header-inline callsites, `#if` variants and function-pointer dispatch explicitly. `compiled` is not the same as `executed`, and `linked` is not allocation-success proof.
3. Preserve four separate status axes: **source discovered**, **compiled/link reached**, **runtime observed**, and **backing qualified**. `unknown` must be allowed; never mark `not reached` only because a historical log has no event. Update the 12 wrapped paths' evidence only if they are demonstrably behind an effective hook.
4. Add negative tests: changed compiler defines, injected unclassified `glBufferData`, newly included header, conditional dead unit, indirect NXGL dispatch, generated/reordered source lines, missing dependency file. A stale source-tree checksum or missing compile trace must fail CI.
5. Emit `evidence/m4b-compiled-reach-YYYY-MM-DD/{README.md,summary.json}` (or equivalent) with all 77 dispositions, toolchain/build identity and zero device actions.

**Acceptance:** every site has source+compile classification with explicit evidence, no classification silently inferred from silence. This closes H1 **only**, not actual GL lifetime or memory refund. Avoid a second static census PR that duplicates the existing 77-site scan.

### 2.2 P0-H2: transactional ownership, generations, storage and GPU-completion semantics

**Files:** `runtime/lamentum-adapter.patch` (patched `native/nvn_textures.h`, `native/nvn_present.h`, `native/nvn_vertex_stream.h`, `native/nvn_framebuffers.h`, `native/nvn_bridge.h`/window, lifetime/GL admission headers), `tools/test_life_events.py`, `tools/test_gl_storage_layout.py`, new reducer fixtures.

1. Retain the implemented `LC2_LIFE_GENERATION_CAP=2048` and distinct `generation_history_overflow` / `live_owner_overflow`; **do not** repeat the already-passing 1,200-name and 1,024-pair basics. The separate 512-entry live owner/subresource tables and bounded event rings can still exhaust. Refuse uncertain ledger updates on overflow, report lost event capacity, and do **not** silently recycle an observable history generation. Increasing caps alone is not memory optimization.
2. Define an explicit key: `(EGL share-group epoch, context epoch when required, GLuint name, object kind, object generation, storage generation, target, level, face, layer)`. Track context teardown/recreate, share-group boundaries, name reuse, and resource orphaning. Do not conflate an NVN texture ID, GL name, guest pool-write generation and physical driver allocation.
3. Model each `glTexImage2D`/`glRenderbufferStorage`/`glBufferData` re-spec as **begin → GL result checked → commit**; on error leave previous backing charged/unknown, never mark it freed prematurely. Record old logical storage, new request, peak overlap, generation, and failed/unknown replacement. Deletion is a logical name retirement, not proof of physical release: aliases/attachments and GPU in-flight uses can retain backing.
4. Add hooks or explicit unknown classifications for `nvn_present.h` VBO and present texture, three `nvn_vertex_stream.h` `glBufferData` sites, framebuffer attachments, renderbuffers, EGL window/pbuffer/surface recreation. An EGL surface's nominal width×height×4 is a size **estimate**, not a proven allocation or a CMA charge. For copy calls distinguish allocation from mutation of an existing level.
5. For completion, assign monotonic submit/use serials; conservative retire states `requested`, `gl-success`, `logical-deleted`, `gpu-completion-unproven`, `safe-to-reclaim`. Prove same-context fence semantics before freeing staging or aliases; **glFlush is not a fence**. Keep default behavior if reliable sync is unavailable.
6. Host cases: successful and failing respec; reallocation with live attachment; delete while view or FBO reference exists; deferred finish; same GLuint across share groups; context loss; EGL window-surface recreation; storage layers/faces/mips; >512 simultaneous live entries; history 2048 exhaustion; event-ring overflow; 64-bit counter overflow; twice-retired object; truncated tail and mixed-run events. Add native mocks for GL error/success and fence reordering; zero fabricated refunds.
7. Keep hooks lightweight/default-OFF for device telemetry. Compare profiler-OFF vs ON on the *same* ELF only after D is safe; do not infer performance from host fixture time.

**Acceptance:** synthetic histories reconcile all logical live totals, cannot undercount on failed GL/reuse/overlap, retain unknown backing, and fail closed on incomplete evidence. Device data is still needed to change `wrapped+unmeasured` to measured.

### 2.3 P0-H3: memory waterfall on **non-overlapping bases**

**Files:** `tools/proc_metrics.py`, `tools/ledger_bases.py`, `tools/load_metrics.py`, a new `tools/peak_memory_waterfall.py`, `tools/test_peak_memory_waterfall.py`.

Create a per-event/present record with `boot_id, run_uuid, pid, starttime, elf_sha256, monotonic_ns, present_serial, phase, owner_id, GL share/obj/storage-generation, memory_class, requested_bytes, declared_live_bytes, completion_state, confidence`. Join, without interpolation, `LC2_GL_STORAGE_EVENT`, `LC2_TEXTURE_OWNER_EVENT`, `LC2_M3B_WINDOW`, `LC2_MENU_FLOOR_MEMORY`, process `VmRSS/VmHWM/VmSwap`, `MemAvailable`, `CmaFree`, and kernel warning deltas. Propagate missing/late/overflow samples as **incomplete**; the old 100 ms M3-B timeline missed samples and is not a floor oracle.

Produce *side-by-side* ledgers for: (a) guest committed+compressed source; (b) CPU decode scratch/requested overlap; (c) GL nominal mip/layer storage live/re-spec overlap; (d) fileback/alternate CPU mirror; (e) buffer/EGL/display nominal requests; (f) process RSS/swap; (g) driver/DMA physical evidence; (h) CMA free order histogram. Label driver physical bytes as `unattributed` unless backed by actual evidence. Never sum (b)+(c)+(f)+(h), or assume the 10.56 MiB MainUI DMA-BUF exporter listing explains an idle 115+ MiB CMA discrepancy.

For a meaningful next candidate, require a bounded same-run *peak* with two independently linked owners, an observed post-retirement floor, and unchanged visual/semantic output. Render concise ranked **potentially retained** bytes and estimated CPU/GL-request peaks, but **no claimed CMA refund** until observed.

**Acceptance:** fixtures reject mixed PID, reordered monotonic timestamps, missing 64 MiB arm samples, late ID280 pair, ID288 missing owner, GPU-completion unknown, unmatched subresource, and double-counted views. New telemetry must not silently hide the old unresolved cases.

### 2.4 P0-H4: K1-B exact kernel / CMA backing, in parallel

**Files:** `tools/kernel_source_match.py`, `tools/cma_readonly_snapshot.py`, `tools/cma_readonly_compare.py`, new offline decoder/receipt and tests. Use the *already matched* 1.0.1 TG5050 kernel firmware image held host-locally; do not rediscover its hash by another public kernel-analogue search.

1. From effective DTB/bootargs, enumerate reusable CMA/reserved regions, GPU/display memory, IOMMU/DMA aperture, relevant heap and page pool paths; separate static reservation from current allocation.
2. Trace exact `system_heap_allocate` orders `{8,4,0}`, final return and fence/FD lifetime paths; an order-4 warning is an attempted block, not automatically ioctl failure. Distinguish possible migrated CMA pages, DMA-heap system exporter pages, and Mali kernel backing. Where exact attribution is impossible, mark `unknown` and spell out evidence needed to prove it.
3. Correlate only **read-only**, same-boot quiet observations (CMA free and free-by-order, allocation success/fail deltas, migration/compaction, `MemAvailable`, `SwapFree`, MainUI PID/starttime, DMA-BUF FD inode set). `nr_free_cma` versus the buddy histogram may differ because proc reads are non-atomic; do not silently normalize the prior three-page difference.
4. Document an operator-reviewable demand envelope *per physical allocation class*, with uncertainty reserve and fragmentation risk. Do not select a magic `CmaFree` threshold from the failed margin sweep, and do not promote the unqualified `proven_CMA_only` admission model to production.

**Acceptance:** precise evidence/provenance and UNKNOWN outcomes where unavoidable; no target reboot, compaction, drop_caches, CMA knobs, stress allocation, lowering of the 96 MiB floor, 300 MiB texture cap, or `T2_STORAGE_MARGIN_MIB` to force an admission. The K1 binary match closes allocator-**retry semantics**, not physical owner attribution.

## 3. M4-C: one evidence-backed sustained-memory reduction

Choose only *after* the H2/H3 waterfall and H4 backing classifications. Rank proposals by **measured overlap of retained lifetimes**, not total GL-declared bytes.

**Candidate A — duplicate BC/linear/CPU image residency (first choice if proven).** Review owners **92 (3600×3600)** and **81 (3600×2160)**: historical CPU staging peaks 64,800,000 B and 38,880,000 B; their nominal RGBA8 level-0 payloads are 51,840,000 B and 31,104,000 B, combined 82,944,000 B (~79.1 MiB). These are **not** physical CMA bytes. Diagram guest compressed source, CPU decode/linear scratch, fileback mirror, GL copy, re-spec and draw consumers. Eliminate one **provably redundant, no-longer-referenced** backing only after all CPU read/write and GPU use/fence tests, never by guessing from `glDeleteTextures`. A/B single factor, visual equality and actual retained floor measurement.

**Candidate B — transient upload streaming:** M4-A's short-mip geometry is done, but `LC2_BC_STRIPE_MEDIUM` is still OFF. For a qualified, memory-safe device arm only, compare OFF/ON with identical ELF, scene, timing, save state, texture source, GL dimensions/formats/mips and shader output. Confirm scratch-request drop **and** RSS/system/CMA deltas separately, byte-exact mip coverage, no duplicate upload, no pixel regression. If effect is only transient scratch and doesn't improve safety, do not promote as the memory solution.

**Candidate C — verified unneeded full-res menu targets:** four historical 1920×1080 targets total about **31.64 MiB** nominal; reducing all to 1280×720 would at most save **17.58 MiB** nominal, not 31.64 MiB. This is lower priority and **not lossless** absent viewport/UV/projection and image proofs. Test only one candidate at a time; preserve native 1280×720 composition, no resolution scaling of world resources without separate quality acceptance.

**Candidate D — texture/compression retention, shader upload traffic:** only if the exact NVN/GL texture type, supported GLES extension, mutation/format/filtering, mip and readback semantics prove it can be retained compressed or reused without new mirrors. Do not assume Mali-G57's BC GPU support or load native BC blobs as unsupported GLES formats. Avoid repeating the already-negative `ZERO_RENDER_SCALE=2` cold250 experiment as a purported FPS optimization.

For all candidates require **3 controlled repetitions**, a same-ELF same-boot OFF/ON, a nontruncated observer timeline, phase-correct KMS pixel comparisons, owner lifetime and independent memory classes. If the memory state cannot safely reach menu, the candidate remains host-only/unqualified; no device shortcut.

## 4. Device gates — preserve safety without blocking host development

**H:** source edits, tests, PR publication and cross-builds proceed independently of historical CMA.

**S:** optional *non-executing* candidate transfer/activation is allowed only with valid matching launcher/helper/ELF hashes, sufficient disk space, no principal/game in progress, preserved build259 backup, read-back checks, an atomic rollback and guarantee of **no auto-start**. Mark it `STAGED` or `INSTALLED_NOT_RUN` — neither is a performance or compatibility result. The evidence still reports build259 as last installed and build262 as **not installed** at this audit.

**D:** before the first bounded no-input launch, take a fresh minimum two-snapshot, same-boot, 20–30 s read-only CMA/pressure/fragmentation and owner-ID preflight as required by [§15](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go). Decide `ALLOW_BOUNDED` versus `HOLD_RUNTIME` using a **defensible class-specific positive reserve plus uncertainty**, not whether yesterday's 15,456 KiB happened to grow. Incomplete/mismatched/drifting samples or new allocator warnings ⇒ HOLD.

If D is positive, launch **one** exact candidate for **15–30 s maximum, no input**, with default protective 96 MiB floor, 300 MiB texture cap, strict GL and risky performance flags OFF; bounded collector and watchdog; abort on typed refusal, kernel warning, incomplete owned capture, health margin loss or unclean MainUI. Verify kernel log, runtime exit, CPU mask, owner identity, MainUI and rollback after. A pass authorizes only a subsequent bounded gate, **not New Game**.

## 5. W0: prove a real, stable game menu

**Tools:** `tools/load_metrics.py`, `tools/owned_navigation.py`, `tools/page_oracle.py`, `tools/frame_diff.py`, `tools/device_principal_test.py`.

Run three independent **120 s** menu-only sessions *after D and positive safety rechecks*. Require real `LC2_MENU_EVENT`, at least two fresh distinct `NVN_PRESENT_PIXELS` serials, game-owned KMS frames with matching `boot/run/PID/starttime/ELF` before and after capture, and absence of floor/admission stop, kernel warnings, unsafe CMA drop, swap growth, GL errors or incomplete cleanup. Read hardware pixel frame and report correct 1280×720 title, selectors, overlays, and input focus; splash/home/Loading are not menu. A pixel comparison's `tolerance<=2` is a *fuzzy difference*, never byte-identical. Mark phase and tolerance explicitly.

Implement an event-driven fresh-present capture bound to a live game process (not stale `latest.log`) with negative tests for duplicate serial, dead PID, Spruce overlay, mismatched ELF and captures from the wrong stage. Keep observer OFF/ON overhead bounded; never treat a quiet profiler as conclusive unless full-frame samples exist.

## 6. W1: reach and retain a playable world

**Host preparation first:** use the owned semantic state machine `MAIN_MENU → NEWGAME_CONFIG → CONTROLS → LOADING → WORLD_VISIBLE`; add timeout/failure substates. `tools/newgame_navigate.py` and legacy raw-log polling are **diagnostic only**, not an acceptance oracle. Each press must have owner-qualified frame evidence, release acknowledgement and **two newer agreeing observations** before the next confirm. Menu frame rates historically dropped to ~1–2 fps, so blind rapid repeated presses can misnavigate.

**Shader frontier:** the catalogue has **46 indexed entries (0–45)** with **seven TEST-only substitutions**. Do not count a linked shader as a drawn, visually correct shader. For every first-world requested shader collect program identity (code+control digest), stage, UBO bank/layout, first use, draw success, GL compile/link logs, framebuffer attachment, draw count and *pixel effect*. If unknown/unpinned: stop cleanly, preserve private blob, run the existing offline translation/literal-bank pipeline, write one explicit new entry, native semantic fixture and pixel-parity check. Do not generate a guessed shader, silently accept fallback, mutate the verified catalogue 0–45 prefix, or weaken unknown-shader stop.

**First-world proof:** moving character/world at 1280×720 with two independent live presents; two-direction movement on the **physical** pad; one real interaction/dialogue or inventory/back; audible ALSA sample corroborated by listener; clean owned save to a safe isolated save path, quit and **cold load** of the same progress. Repeat three times with correct player location and no memory guard violation. All saved games backed up; agent evdev injection alone is insufficient physical-controller acceptance. Record world ROMFS reads, texture owner/lifetime, foreground pid, shaders actually drawn and KMS images; don't confuse repeat Loading frames with a world.

**If W1 stalls:** classify into mutually exclusive `admission/memory`, `unknown-shader`, `shader-bad-pixels`, `navigation/page`, `input/HID`, `audio`, `asset/ROMFS`, `save/fs`, `GPU synchronization`, `timeout/guest CPU`. Fix the first evidenced blocker, retaining earlier gates. No blanket speculative optimization while first-world state is unqualified.

## 7. F1: actual gameplay performance — only after W1

A **30 FPS** physically presented world needs **33.333 ms** per correct distinct frame; Loading/publisher/menu presentations and `NVN_PROFILE` averages do not count. Collect ≥60 s each after warm-up in three reproducible routes: idle world, navigation/interaction, busy lighting/particles/transitions. Record serial continuity, duplicates, dropped frames, complete P50/P95/P99 present intervals, thermal/CPU governor and frequency, GPU wait, process `VmRSS/HWM/Swap`, swap/page-fault deltas, input responsiveness, audio continuity and correct pixels. Three repeated matched same-ELF A/B pairs per promoted optimization; report confidence/noise and observer overhead (reject if >5%).

Attribute **nonoverlapping wall time** separately to Unity/IL2CPP guest/SVC/host idle gap, NVN command replay/GL submissions, shader build, BC decode and texture refresh, blocked GPU `glFinish`/fence, swap/page faults, present/readback/KMS. Do not reinterpret `CLOCK_MONOTONIC` elapsed time as executing-thread CPU time. `glFlush` cannot replace completion proof, and earlier `ZERO_RENDER_SCALE=2` had no demonstrated whole-frame win.

Rank implementations *only from measured world bottlenecks*: reduce guest calls/resource churn and redundant NVN state if guest-dominated; cache shader compilations with exact program identity if shader-dominated; bound/stream BC uploads if decode-dominated; safe batch/avoid redundant readback if replay-dominated; precision-preserving smaller targets only if GPU-bound and A/B pixels accepted; prefetch carefully if major faults dominate (never hide memory regressions). Pass steps at stable verified 5 → 10 → 15 → 20 → 30 FPS, but do not lower correctness or safety requirements. Final target: full-world **P95 ≤33.333 ms on each required route**, P99 and input/audio published, sustained memory gate intact.

## 8. Minimal reproducibility/PR checklist

Host baseline (using pinned recovered adapter and toolchain for checks that require them):

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m py_compile tools/gl_allocation_inventory.py tools/ledger_bases.py \
  tools/cma_readonly_snapshot.py tools/cma_readonly_compare.py
bash -n build_lamentum.sh
git diff --check
# Apply runtime/lamentum-adapter.patch in the pinned recovered source tree,
# not at the repository root; run the existing manifest + native fixture checks.
# Re-run the 77-callsite policy against the exact patched build tree.
```

For every PR publish: **base/head commit**, scope and one variable changed; source manifest 435/435; inventory classification/changed-site policy; actual test count/skips; exact AArch64 binary SHA/BuildID/GLIBC; `evidence/<phase>/summary.json` with known/unknown flags; rollback; whether **device actions=0**, staged, launched, W0/W1/F1; captured PCM/pixels/serials only if owner-qualified; any unresolved ID or truncated timeline explicitly listed. A host PASS never changes a device stage to PASS.

**Abandon/redirect criteria:** If H2/H3 show no meaningful safely removable retained duplicate, or exact kernel/driver backing remains irreducibly unknown, publish a bounded negative feasibility assessment and stop tuning arbitrary margins. If W1 cannot be reached with stable safe headroom or reliable shader output, make those blockers the primary goal instead of reporting an invented FPS target. If world P95 remains far outside budget with CPU-bound guest execution after correct low-overhead timing, evaluate *documented* performance/quality trade-offs separately rather than endlessly rewriting buffer accounting.

## 9. Exact current handoff and tracked open questions

1. **DONE, do not duplicate:** build261 M4-A checked BC capacities/native fixture; build262 generation capacity/overflow, 77-site source census and 370-test checkpoint; firmware-kernel match; offline admission replay.
2. **NEXT PR:** H1 compiled-unit/include/dispatch reach with pinned compile trace and negative tests; current 65 unknown callsites are **not** 65 proven bugs.
3. **NEXT PR:** H2 GL/EGL/buffer lifetimes, all transactional edge cases and explicit context epochs; avoid a fake physical-memory ledger.
4. **NEXT PR:** H3 joined phase-specific memory waterfall; baseline evidence has missing samples and unresolved ID280/288 owners.
5. **PARALLEL:** H4 exact-firmware DT/CMA/DMA physical-class provenance and fresh read-only device safety if/when evaluating a launch; H5 offline W0/W1 fixtures.
6. **ONLY THEN:** one qualified M4-C retained-memory candidate → fresh D gate → W0 → W1 → real F1.

**Open critical questions:** Why did free CMA remain ~15 MiB at the historical idle boot? Which target GL/EGL/driver allocations actually require migratable/contiguous pages? Can loading retain both original guest/CPU copies and large GL images safely under 1 GiB-class RAM? Which of catalogue's TEST shaders materially affects first-world pixels? Can world initialization complete with enough working set to leave a stable menu and avoid swap? Which actual world-frame stage dominates CPU/GPU time? Current receipts do not answer these; make each a measurable gate, not an assumed fact.

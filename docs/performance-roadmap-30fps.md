# Lamentum (TrimUI Smart Pro S): Roadmap to Stable 30 FPS

> **LATEST EXECUTION ROADMAP (2026-10-23; local main updated after c4a5714 with K1-E/K1-F and candidate-launcher evidence):** [post-build262 evidence-led gameplay recovery and 30 FPS plan](post-build262-gameplay-recovery-roadmap-2026-10-23.md) supersedes older **next-action orders**, not the measurements below. The active plan records H1 compile/link-input completion, partial H2a alias telemetry, K1-B/C/D allocator-class findings, K1-E's expected userspace loader chain (not an executed game path), and the user-prioritized K1-F read-only CMA owner/process audit. Six visible DMA-BUFs are all `system` exporter, mapped to MainUI and platform `display_text.elf`; debugfs/PAGE_OWNER attribution is unavailable, and no safe process lifecycle was identified. The post-build262 candidate is host-built and inertly staged; build259 remains active. After a boot-ID transition of unconfirmed origin (no reboot command was sent by the agent), complete post-boot samples at uptimes `115.96`, `340.99` and `905.30 s` held `CmaFree=130,412 KiB`, with stable MainUI/principal and no game. No allocation/OOM/CMA/Mali warnings appeared; PSI is unavailable. `T2_STORAGE_MARGIN_MIB` remains unset and runtime is **HOLD_RUNTIME** because class-specific demand and reserve are still unqualified. The candidate-specific launcher remains staged/readback-verified and not run. The initial H3 reducer is implemented and exercised by 16 focused fixtures; the full suite passes 429 tests. It preserves M3B phase subintervals, leaves `nvn-object-id` raw until exact run source/ELF binding, and treats the first prelaunch system record separately from runtime-process accounting. A local build256b ON log replay parsed 41 windows/3 marks and validated a separate later live-set snapshot (95 views/owners, 117,441,536 B) without backfilling the earlier budget sample. The replay remains incomplete due to timeline gaps, owner-pair joins, and missing matching CMA snapshots/warning deltas; no physical attribution is available. Next host work is H2 lifetime accounting plus applying H3 to a complete bundle, then selecting a measured M4-C candidate. Loader/API-to-allocator qualification is supporting, not the sole critical path. Device runtime needs a fresh class-specific positive §15 safety preflight; safe staging is separate. First-world and sustained ≥30 FPS **NOT VERIFIED**.

> **CURRENT STAGE-BASED EXECUTION POLICY (2026-10-23):** [detailed roadmap §15](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go) and [§95 below](#95-publication-and-fresh-device-preflight-policy-2026-10-23) override older *indefinite* device NO-GO language. Host PRs/source publication **never** depend on old CMA data; inert staging of the current post-H2a host-built candidate (already staged without activation; build259 remains active) is separate from runtime. A bounded no-input runtime start needs **fresh stable read-only CMA/order/pressure preflight**, a justified allocation safety margin and verified guards; HOLD while class-specific demand or uncertainty remains unqualified (the post-boot sample window is not an independently justified reserve). M4-A host code is already published at main@509cc985. No world gameplay/30 FPS evidence.

> **SOURCE/EVIDENCE REVIEW — `main@c05f879` (historical checkpoint, 2026-10-23):** [§93](#93-post-k1a1-re-audit-and-m4-host-only-critical-path-2026-10-23) and the [detailed roadmap §11](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#11-post-k1a1-re-audit-at-main-c05f879-2026-10-23) are the authoritative next-action order. K1 exact firmware-kernel disassembly and A1 complete-log policy replay are **completed evidence phases**; they do not qualify a device launch. Next: M4-A checked short-mip BC scratch sizing, M4-B owner/GL-generation and buffer provenance, K1.4 exact-binary CMA backing classification—all host-only. Idle free CMA remains ~15 MiB, build260 remains uninstalled, gameplay/FPS unverified.

> **CURRENT EXECUTION ORDER — updated 2026-10-23:** M4-A host acceptance is recorded in [§94](#94-m4-a-host-only-bc-stripe-sizing-and-native-fixture-2026-10-23); operational stages follow [§15](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go). The candidate launcher is staged/readback-verified but not run. A boot transition was observed; post-boot `CmaFree=130,412 KiB` stayed stable for 15 minutes, but physical allocation classes and a positive reserve remain unknown, so D is **HOLD_RUNTIME**. The initial H3 reducer is host-implemented/tested; next apply it to a complete owned bundle, then resolve H2 lifetime owners and use measured overlap to select M4-C. No game launch, world frame or 30 FPS evidence.

> **HISTORICAL REASSESSMENT — 2026-10-21, audited HEAD [a0aa160](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/a0aa16053191e25d86f764ae4451c19923f0361a). Read [§48](#48-post-build232-audit-surviving-the-menu-reliable-new-game-world-pixels-and-a-credible-30-fps-path-2026-10-21) first for the next implementation queue.** §§0–47 contain historical diagnostics and owner receipts. Game remains **NOT PLAYABLE**; no verified real-world FPS exists. The §48 audit adds source-level navigation/observer findings and corrects the theoretical 1080p→720p memory delta (17.58 MiB, not 31.64 MiB). This documentation update does not represent a new device run or a performance gain.

## 0. Audit of the Existing Code and Measurements

**Primary evidence:** [build202 runtime log](../evidence/ui-cbuf-fixed-01/latest.log) and [effective environment](../evidence/ui-cbuf-fixed-01/env.json). The installed executable's SHA-256 is ff4454232247b935748db7a76b05a7af27e62f2a189d199b49d7d6d93f9d1fd2. The run ended with TIME_LIMIT after 520 seconds, with frame 709 being the last presented frame. The distributions below were calculated from **708 T2P_SLOW_FRAME entries**. This was a diagnostic run, **not** a quiet gameplay benchmark.

| Recorded metric | P50 | P95 | Interpretation |
|---|---:|---:|---|
| period-ms, entire run | 620.0 ms | 1242.0 ms | Median interval corresponds to ~1.61 frames/s; not a gameplay result |
| replay-ms | 235.7 ms | 605.7 ms | Replay time only, not complete frame time |
| finish-ms | 0.1 ms | 0.6 ms | Does NOT account for every potential GPU wait |
| present-ms | 3.2 ms | 6.7 ms | Measured present stage |
| swap-ms | 0.2 ms | 0.7 ms | Measured swap stage |
| readback-ms | 2.5 ms | 4.7 ms | Diagnostic GPU readback |
| period-ms, frames 500–709 | 512.5 ms | ~676 ms | Later, relatively warmed-up interval |
| replay-ms, frames 500–709 | 96.9 ms | ~356 ms | Later replay interval |

**Additionally:** the per-frame difference (period - replay - present - swap - readback) for frame >=500 has a median of approximately **403 ms**. This is **unattributed time**, not evidence by itself of sleeping, low clock rates, or memory compression. Only fields actually present in the log have been deducted. **Do not add medians of different columns.** Stable 30 FPS requires complete frame intervals of no more than 33.33 ms, together with correctness. The late diagnostic ~513 ms period and ~97 ms replay illustrate the size of the gap, but their instrumentation overhead has not yet been removed.

**Why these numbers are not final FPS results:** the environment enabled LC2_CBUF_AUDIT=64, COTM_CBUF_GL=32, LC2_PAIR_CENSUS=60, LC2_HID_WATCH=1, LC2_MENU_TRACE=1, MOMO_DIAG_MASK=1, MOMO_FBO_DIAGNOSE=1, and MOMO_FBO_FRAME=300. GL readbacks, shader/UI receipts, tracing, and a very large runtime log may substantially distort frame times.

**Concrete findings tied to code and evidence:**

1. At the end of build202, T2_GZRAM periodic reports compressions=336501, faults=274244, restores=312330, scans=914, compressed=377.7 MiB, stored=82.5 MiB, and reported savings of 295.1 MiB. MemAvailable was approximately 119 MiB; the process reported VmRSS around 644060 KiB and VmSwap around 218912 KiB. These counters **do not quantify compression CPU time**, but they identify a clear candidate for instrumented A/B testing. Disabling compression without proven extra headroom is risky.
2. In runtime/lamentum-adapter.patch, the **native/nvn_render.h** kind=7 constant-buffer branch creates a float staging array, copies guest data, and calls **glTexImage2D(GL_RGBA32F) for every active uniform block on every draw**, even when dimensions and contents are unchanged. This is a concrete candidate for resource reuse, glTexSubImage2D, and exact-content upload skipping, after measuring its actual cost.
3. The NVN_DRAW_PROGRAM_PROFILE sample after frame 660 lists **1620 draw records over 60 frames** (~27 per frame in the profiled subset). Pair 12/14 contributes 540 draws to a 1920×1080 target; pair 17/4 contributes 600 draws to a ten-level bloom/downsample chain from 640×360 down to 1×1. This is a subset of recorded work, **not** a complete cost attribution for GL or Unity. A 1920×1080 target contains 2.25 times as many pixels as the physical 720p output.
4. NVN_COMMANDS_EXECUTED reports completed-with-glFinish=1. A low present finish-ms does not exclude waits elsewhere in the queue. An unsafe earlier implementation triggered NVN_COMMAND_REUSE_BEFORE_COMPLETION; proper SDL/KMSDRM EGL surface lifetime was established in build152.
5. The checked-in port/Lamentum.sh defaults are AW_RELEASE=1, LC2_GLES3=1, COTM_ASYNC_QUEUE=0, T2_GPU_PIPELINE=0, COTM_FB_PRESENT=0, COTM_GL_ERROR_IGNORE=0, LC2_TEXTURE_PAGEOUT=0, and a **96 MiB** memory floor. The successful menu run instead used a diagnostic **32 MiB** floor, lossless file backing, and guest ZRAM. Do not treat this diagnostic environment as validated production defaults.
6. The shader catalogue contains 38 captured/translated real programs and seven TEST substitutes. The build202 correction mapping c4 to NVN UBO1 is specific and essential. Regenerating the entire catalogue without preserving proven compiler/SDK provenance could restore the original bug; use tools/append_program.py for additional shader-tail captures.
7. The currently correct rendering path also depends on sampler-handle mapping, isolated constant-buffer texture units, embedded shader literals, deferred BC uploads, and striped BC decoding. These fixes must not be reverted in the name of performance.

## 1. Mandatory Rules for Every Experiment

- **Two independent acceptance gates:** (A) correct gameplay rendering, input, audio, and saves; (B) complete frame times <=33.33 ms. A frame counter or a fast but visually broken scene cannot pass gate A.
- Change **one variable at a time** and retain the baseline executable SHA-256, Git commit, owner-image hash, and manifest-pinned source identity. Compare the same scene and save state under equivalent warmed-up conditions; repeat three independent A/B pairs if the difference is subtle.
- Profile startup, title/menu, New Game transition, stationary gameplay, moving gameplay, interactions, bloom/effects, and save/load **separately**. Never compare cold loading in run A with a warmed-up menu in run B.
- **Disable expensive diagnostics** in release measurements; debug builds and glReadPixels may distort results. Prefer bounded preallocated ring buffers over printf on every draw or SVC.
- Do not bypass GL errors, shader identity contracts, NVN command-buffer ownership, glFinish, or fences just to produce a better FPS number. Do not disable CPU/memory safety guards or remove the 420 MiB GPU texture-budget cap.
- Original NSO/RomFS/assets/keys/saves/shader binaries remain in the owner's local workspace. Public evidence may contain measurements, configuration, hashes, authored tools, and verified screenshots where distribution is appropriate.
- Verify actual DRM captures **while the port process is alive**, and verify cleanup afterward: MainUI restored, CPU online mask restored, and no orphan game processes. Back up owner saves and the previous known-good executable before each experiment.
- This board has roughly 1 GiB RAM. Guest ZRAM and file backing use different accounting domains; reported compression savings and file-backed bytes must not simply be summed as independent free RAM.

## 2. P0-FUNC — Reach Reproducible Gameplay Before FPS Tuning

**Reason:** optimizing the title menu to 30 FPS is not useful if New Game later fails due to another shader, memory floor, or broken sprites.

**Step-by-step procedure:**

1. Pin build202, executable SHA-256, and owner-image identity. Verify the separate recovered baseline with sha256sum -c tools/baseline-manifest.sha256 (435/435 files).
2. Using the proper Spruce principal launch flow, open the main menu and capture a real KMS framebuffer. Deliberately select **New Game** and confirm. Build202 has already proven that **Options** can be opened; that is **not** proof that New Game works.
3. Run a sufficiently long but bounded New Game test and capture guest shader/service stops, texture loads, memory availability, and screenshots of actual scene transitions. A nonblack pixel counter alone is not a gameplay screenshot.
4. On ZERO_SHADER_NOT_PINN, validate the captured code/control identity and use tools/append_program.py **without regenerating all of** runtime/lamentum-shaders-draft.h. For new pairs record stage, uniforms, sampler slots/offsets, hardware-bank +3 mapping, and correct NVN constant-buffer binding. Run host tests and compare the build202 UI text.
5. During real gameplay, take a short bounded LC2_PAIR_CENSUS and check whether any of the seven TEST substitutes is used. The outstanding features include SSBO skinning and MSAA/per-sample operations, which cannot safely be replaced by ordinary sampler2D sampling without preserving semantics.
6. Verify movement, item interaction, inventory, dialogues, stencil/alpha/lighting, and scene changes. Stop performance experiments on visual regressions until the exact shader, texture, or pipeline-state defect has been identified.
7. Verify **audible** music and sound effects (AUDOUT nonzero counters are insufficient), then save -> quit -> cold start -> load and check character position/inventory. Verify the full return to MainUI and restoration of CPU state.
8. Repeat a short smoke test **without diagnostic draw/GL probes**. Establish whether the default launcher can safely support the required memory environment. Do not promote the 32 MiB diagnostic floor without explicit safety acceptance.

**PASS:** a correct, controllable gameplay scene with reproducible state and save/load. **STOP:** an uncatalogued shader, incorrect pixels, or a save conflict. Do not claim playability before passing the functional gate.

## 3. P0-BENCH — Establish a Quiet Baseline and Measure Diagnostic Overhead

The first controlled run should retain the build202 memory environment that reaches the menu, but remove expensive graphics diagnostics. **Example:** run only after checking that MainUI is idle and owner data has been backed up.

~~~sh
python3 tools/device_principal_test.py --budget 520 --wait 600 \
  --env LC2_GUEST_QUOTA_MIB=3072 \
  --env LC2_BC_LAZY_ALL=1 --env LC2_BC_LAZY_UPLOAD=1 \
  --env LC2_BC_FILE_BACKING=/mnt/SDCARD \
  --env LC2_BC_FILE_BACKING_EXTRA=/mnt/UDISK \
  --env LC2_BC_FILE_CAP_MIB=1280 \
  --env T2_MEMORY_FLOOR_MIB=32 \
  --env T2_GUEST_ZRAM=1 --env T2_GZRAM_BLOCK_KIB=16 \
  --env T2_GZRAM_COLD_MS=10 --env T2_GZRAM_TARGET_MIB=512 \
  --env T2_GZRAM_PERIOD_MS=20 --env T2_GZRAM_BUDGET_MIB=32 \
  --env AW_RELEASE=1 \
  --env LC2_CBUF_AUDIT=0 --env COTM_CBUF_GL=0 \
  --env LC2_PAIR_CENSUS=0 --env LC2_MENU_TRACE=0 \
  --env LC2_HID_WATCH=0 --env MOMO_DIAG_MASK=0 \
  --env MOMO_FBO_DIAGNOSE=0 --env COTM_GL_ERROR_IGNORE=0 \
  --evidence evidence/perf-quiet-b0
~~~

**Important:** this reproduces a **diagnostic memory configuration**, not a safe production preset. Stop immediately if the device approaches the memory floor or exhibits memory pressure; do not free memory by terminating unrelated system processes. Do not enable MOMO_FBO_FRAME or additional dump flags. Audit the source's getenv parsing: for certain experimental flags, an explicit value of "0" may not be equivalent to an unset variable. If in doubt, run from a clean environment using an explicit allowlist.

**Test order:** historical diagnostic A -> quiet B -> repeated quiet-control A/B under the same executable and equivalent menu/game state. Record the actual point when the menu is reached and the start of the subsequent **steady-state** sampling window; compare only like-for-like intervals. Do **not** infer gameplay FPS by dividing 709 frames by 520 seconds, because loading was included.

**Add the following tools in separate PRs (not yet implemented):**

- **tools/lamentum_perf_observer.py:** an external process observer sampling every 1–5 seconds: /proc PID status/stat/io/schedstat, infrequent smaps_rollup, per-thread statistics, MemAvailable, CmaFree, swap counters, temperatures, CPU online mask/governor/frequencies. Avoid high-frequency probing.
- **tools/analyze_perf.py:** a parser for existing T2P_SLOW_FRAME records, extracting frame, period/replay/finish/present/swap/readback, P50/P90/P95/P99/max, missing/unknown spans, early and late phases, and gaps >100/250/1000 ms. Produce JSON and CSV tied to the exact log and executable hash.
- **Gated screenshot acquisition:** capture only while a real game PID is alive, and do not capture every frame. Delayed MainUI restoration is not evidence that a requested screenshot belongs to the game.

**PASS:** three quiet profiles with P50/P95 values and quantified diagnostic overhead. If disabling probes substantially changes results, revise the priority order below.

## 4. P1-TIMELINE — Explain the Unattributed ~400 ms Before Tuning Rendering

**Problem:** frames 500–709 show period P50=512.5 ms and replay P50=96.9 ms; the other measured stages take only a few milliseconds. The underlying cause **may be outside the GPU**.

**Add a narrowly scoped LC2_FRAME_TIMELINE=1 instrument**, preferably using a preallocated ring and one dump every 60–120 frames:

1. Record CLOCK_MONOTONIC_RAW timestamps for previous present end, guest present entry, command-buffer publication/snapshot, replay start/end, **every glFinish and eglMakeCurrent** across threads, SDL swap entry/exit, and the owner frame serial/generation.
2. Record CLOCK_THREAD_CPUTIME_ID and /proc/TID/schedstat for guest main, render, input/audio, and host compression threads. Distinguish CPU running, runnable-but-not-scheduled, blocked waiting, page faults, GPU fence waits, and intentional sleeps.
3. Trace actual guest SVC WaitSynchronization/SleepThread/WaitProcessWideKey/WaitForAddress calls and other waits: occurrence count, requested duration, actual elapsed time, and guest caller PC. Pay special attention to Unity PlayerLoop/frame pacing; do not alter guest deltaTime or bypass sleeps before establishing their purpose.
4. Record CPU page faults/major faults and guest-memory restores with thread IDs and bucketed statistics, not a full printf per trap. Inside NVN replay, report both elapsed wall time and executing thread CPU time.
5. Produce mutually exclusive elapsed categories per frame and verify that the sum accounts for >=95% of each interval. GPU/CPU overlap should be shown separately, not double-counted as inclusive time.
6. Compare an instrumented run with **the same executable, instrumentation off**. Keep profiler overhead below 5%; otherwise sample less frequently.

**Decision branches:** actual guest sleeping -> investigate the timer/SDK contract; guest thread runnable but starved -> CPU affinity/system load; costly decompression -> Section 5; high guest CPU -> profile SDK/IL2CPP hot spots; queue waits -> Section 11; high rendering CPU -> Sections 6–7. Do not rewrite the backend before attributing the time.

**PASS:** >=95% of the frame period is attributed to consistent stages, with a clean comparison. **STOP:** attempts to remove guest sleeps without knowing the caller's timing semantics.

## 5. P1-MEM — Reduce Frequent Guest-Page Compression and Fault Overhead

**Evidence:** 336501 compressions and 274244 faults in build202. Compression also reports substantial saved memory, so simply switching it off may be unsafe.

**Implementation points:** native/t2_guest_memory.h, guest mmap/alias ownership, memory.h, native/nvn_textures.h, LC2_BC_FILE_BACKING, and LC2_BC_LAZY_UPLOAD. Introduce counters for compress_CPU_ns, restore_CPU_ns, faults per guest page, recompression within 10/50/200 ms, pinned/excluded pages, effective saved MiB, and fault-induced stalls. Keep these separate from system swap statistics.

**Controlled A/B matrix** (change one variable at a time; keep the same executable and monitor RAM safety):

| Test | Change from the current diagnostic memory configuration | Hypothesis |
|---|---|---|
| M0 | cold=10ms, period=20ms, budget=32MiB, block=16KiB | Quiet baseline |
| M1 | T2_GZRAM_COLD_MS=50 | Recompression of still-hot pages |
| M2 | T2_GZRAM_COLD_MS=100, then 200 | CPU savings versus resident RAM growth |
| M3 | T2_GZRAM_BUDGET_MIB=16, separately 8 | Lower contention with guest CPU |
| M4 | T2_GZRAM_PERIOD_MS=50, separately 100 | Scan cadence and memory pressure |
| M5 | Selective do-not-compress of verified hot ranges, **only** with exact owner accounting | Eliminate repeat fault/compression churn |
| M6 | T2_GUEST_ZRAM=0, **only with proven headroom** | Upper bound on compression overhead |

Before M1–M4, verify the baseline's parsing and actual semantics of cold/period/budget. For each run, record frame period/replay P50/P95, host compression CPU nanoseconds, faults, VmRSS/VmSwap/PSS, minimum MemAvailable/CmaFree, kernel OOM signals, and whether the requested scene completed. Do not change backing quota or GPU texture budget in the same comparison. A diagnostic floor of 32 MiB and observed MemAvailable ~119 MiB **do not** guarantee safe operation without compression.

For **M5**, first establish a read/write and lifetime map of actual guest ranges: mutable Unity allocations, repeatedly touched pages, NVN GPU pools, and audio/shared IPC. Exclude only ranges proven safe to exclude; do not apply speculative madvise or pageout. **PASS:** repeatable whole-frame P95/guest CPU improvement with correct texture/save results and safe memory. **STOP:** memory floor/OOM, alias invalidation, swap storms, or regressions.

## 6. P1-CBUF — Reduce Per-Draw GL_RGBA32F Constant-Buffer Texture Uploads

**Confirmed in the adapter patch:** native/nvn_render.h, branch u->kind==7, copies a staged guest range and invokes glActiveTexture, glBindTexture, glTexParameteri, glTexImage2D, and glUniform1i. Active buffer data was observed in the 144–368 byte range for relevant draws, but the actual repetition rate and time cost **have not yet been measured**.

**Detailed implementation sequence:**

1. Add counters for kind=7 blocks/frame, bytes copied, distinct active constant-buffer snapshots, identical-data counts, GL texture allocations/redefinitions, and CPU nanoseconds per operation. Separate pair 12/14 UI from pair 17/4 bloom and all newly reached gameplay pairs.
2. **C1:** track GL texture generation, GL unit, allocated format/width/height, and active context/program. Call glTexImage2D on first allocation or resize; use glTexSubImage2D for changed data with the same allocated dimensions. A nonzero GL object name does not prove validity after context loss, resource deletion, or name reuse.
3. **C2:** skip uploads only after comparing the exact bytes and matching resource generation. A cheap 32-/64-bit hash may be a prefilter, **not** proof of identity. Compare actual active and padded data, not the entire 65536-byte maximum buffer on every draw.
4. **C3:** skip redundant glUniform1i/glTexParameteri/glActiveTexture calls only when tracked GL state is provably unchanged. Invalidate shadow state when another shader, texture binding, or EGL context path changes its ownership.
5. **C4:** consider immutable texture storage, GL buffers/PBOs, or a ring for in-flight GPU data only if the simpler changes prove insufficient. Never overwrite a buffer or texture still being read by an earlier GPU queue generation without the appropriate serial, fence, and lifetime guarantees.
6. Preserve build177 texture-unit isolation and build202's c4 -> UBO1 correction. Run tools/test_cbuf_units.c, tools/test_ui_cbuf_binding.py, tools/analyze_ui_cbuf.py, and compare actual KMS screenshots for UI text, selected item, alpha, UVs, and scene textures.
7. Do not introduce a global fallback to an arbitrary nonempty constant-buffer slot. Correct bindings must follow the compiler's instance-name provenance and the SDK contract hardware bank = NVN slot +3, not declaration ordinal or a guessed block type.

**PASS:** lower measured upload/replay times per frame with identical GL output and gameplay state. **STOP:** constant-buffer unit collisions, missing UI, invalid transforms, or undefined resource lifetimes.

## 7. P1-REPLAY — Identify Where the 97–236 ms of Replay Time Goes

**Implementation locations:** baseline native/nvn_replay.h, native/nvn_render.h, native/nvn_samplers.h, native/nvn_shaders.h, native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_commands.h, and native/nvn_queue.h; all changes belong in runtime/lamentum-adapter.patch. The actual costs of these functions in Lamentum **remain unmeasured**. An example of the methodology is the [West of Loathing profiling roundup](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): in that **different** game, replay was split into first texture resolution, state changes, memory transfers, and shader cost. Reuse the **measurement methodology**, not the measured milliseconds or title-specific patches.

### 7.1. Establish a Low-Overhead Replay Profile First

Implement LC2_REPLAY_PHASES=1, aggregating per frame, program, and operation type without writing detailed stdout output for every GL call. For each command list and serial, collect the following **exclusive CPU nanoseconds and occurrence counts**:

- Queue snapshot, command-record parsing, and guest-to-host command copying, together with command count and byte count.
- Pre-GL draw dispatch: sampler-handle decoding, descriptor lookup, texture lifetime verification; distinguish a first resolve from repeated resolves of the same resource key.
- zero_texture_refresh: BC decoding, memory copy, glTexImage/upload, dirty-state checks, bytes transferred, GPU allocations and budget changes.
- Shader catalogue lookup, compilation/linking and shader selection; program binding and uniform-location lookup.
- Constant-buffer GPU upload (Section 6), sampler state, texture bindings, framebuffer attachment/cache/rebind, depth and stencil, blending, scissor and viewport.
- Vertex/index processing: guest-range extraction, format conversions, allocation/reallocation/copy, glBufferData/glBufferSubData, and GL draw-call submission overhead.
- Non-draw commands: TextureWriteTexels, clears, render target changes, barriers, copies, command-buffer reuse, resource creation and deletion.
- **Every** glFinish, GLsync, and eglMakeCurrent, with scheduler waiting and per-thread CPU time separated from GL completion.

At the end of a measurement window, emit frame-range identifiers, replay elapsed wall time, actual host thread CPU time, draw/non-draw exclusive buckets, command counts, transferred bytes, and inclusive/exclusive duration distinctions. A single aggregated log entry every 60 frames and a final exit summary are preferable to per-SVC/per-draw logging. Require that unattributed time inside replay is <=5%. Keep first-use shader compilation separate from steady-state work.

### 7.2. Candidate A: Avoid Expensive Repeated Sampler/Texture Resolution

If repeated resolution of identical handles is expensive, implement a **bounded per-context resource cache** keyed by texture pool ID and generation, descriptor index, sampler ID and generation, view format, mip level, layer, swizzle, target type, and backing modification generation. A cache hit is only valid if the guest descriptor and GL texture lifetime remain valid.

Invalidate on TextureWriteTexels, texture pool unregister/re-register, resource free/recreate, framebuffer aliasing, and context loss. Identical handle bits alone do not prove that the same content remains after a write to the underlying pool.

Measure first and second resolution of the same handle before profiling the entire frame. Report hit/miss counts, invalidations, correctness, CPU P50/P95, and GL allocations. West of Loathing exhibited an expensive first per-frame texture resolve, but **there is no evidence yet that Lamentum shares this bottleneck**. Do not add the cache blindly.

### 7.3. Candidate B: GL State Shadowing

Create an accurate **per-EGL-context shadow state table** covering current shader/program, active texture unit, texture bindings for each unit and target, framebuffer, array/element buffers, blend/scissor/depth/stencil state, and viewport. Before suppressing a redundant GL call, verify matching object identity and generation.

Actual GL state can also be changed by native presentation, diagnostic rendering, and framebuffer helpers between guest draw calls. Any untracked GL entry point must invalidate the affected cached state; otherwise shadowing will introduce subtle graphics regressions.

First instrument **would_skip_calls** without changing any behavior. Next, optimize exactly one GL call or call family at a time. Compare GLenum error records, actual KMS captures, guest pipeline-state parity, and whole-frame latency. glGetIntegerv and glCheckFramebufferStatus may be used for bounded verification, but must not become permanent hot-path checks.

### 7.4. Candidate C: Buffer Churn and Per-Draw Allocations

Collect live counts of malloc/free/realloc and glBufferData vs glBufferSubData, the volume of vertex/index copies, and the number of times an identical guest data range is converted again.

Only if churn is substantial should the runtime consider preallocated scratch memory, a persistent VBO/IBO ring, or a vertex-format conversion cache keyed by source identity, source-write epoch, and format. Protect any in-flight GPU reader with correct fences. For dynamic UI, particle, and stencil geometry, a repeated guest pointer does **not** imply unchanged contents.

Measure resident RAM as well as CPU time: an optimization that doubles residency can cause more guest-ZRAM faults and degrade frame time.

### 7.5. Candidate D: Framebuffer and Render-Pass Transitions

Profile framebuffer cache hit/miss/rebind counts, render-target attachment validity, render-pass boundaries, repeated glCheckFramebufferStatus and glGetError, and attachment load/store patterns. Separate **diagnostic** checks from mandatory validation.

A tile-based Mali GPU may benefit from fewer render-target switches and unnecessary memory stores. However, glInvalidateFramebuffer may be used only after the attachment's **last consumer**, and never for an intermediate bloom image before the final composite reads it. Restore the original framebuffer after any diagnostic readback.

### 7.6. Batching and Its Restrictions

Combining draw commands requires proven equivalence of target, ordering, texture/UBO bindings, blend mode, viewport/scissor, alpha, depth/stencil behavior, fragment side effects, and memory barriers.

Pair 12/14 may render nine separate UI objects per frame; sharing one shader is not enough to combine their draws safely. First count **consecutive** genuinely compatible draws while preserving guest order and capturing per-frame visual diffs. Only then test batching behind an opt-in flag.

**PASS:** complete frame-period P95 improves, not merely replay CPU time shifted into GPU finish; preserve KMS/GL correctness, resource generations, and game state. **STOP:** a new STOP status, broken stencil/UI, incorrect shader mapping, or unknown resource ownership.

## 8. P1-720 — Identify the Owner of the Internal 1920×1080 Targets and Test 720p

**Observed fact:** NVN draws target **1920×1080** resources (including UI pair 12/14 and pair 11/9), even though the physical display is 1280×720. At 1920×1080 the affected render target has ~2.25 times the pixel count of a 720p target. Reducing a target's pixel workload **does not imply 2.25× overall FPS**. If the ~400 ms outside replay persists in quiet runs, render resolution may be a secondary issue.

### 8.1. Find the Owner of the Resolution Instead of Guessing

1. In a low-overhead trace, identify **all** 1920×1080 resource IDs: initial NVN TextureBuilder calls, owning memory pool, format/MSAA/target flags, attachments, reuses, samplers and readbacks, draw counts, and frame frequency. Distinguish those offscreen resources from the final 1280×720 panel surface.
2. In the owner's local image workspace, perform **read-only analysis** of original IL2CPP metadata and main NSO: locate serialized MonoBehaviour/component fields and native call sites potentially involving Unity Screen.SetResolution, RenderTexture.GetTemporary, creation of RenderTextures, CanvasScaler, or graphics preference components. These are **search candidates**, not claims that the game calls those APIs.
3. Correlate runtime creation and values of **1920 and 1080** with reference resolution, internal render scale, dynamic resolution, and UI projection constants. Inspect the actual Options menu exposed by build202 for available graphics/effects controls. Do **not** assume that a Handheld/TV setting controls these render targets without a traced consumer.
4. Build an original-to-candidate dependency matrix for render-target dimensions, viewport/scissor, matrices/UBO, sampled UV coordinates, UI text size, input hitboxes, level of detail, and postprocessing. A mode change must reallocate every affected resource family correctly; do not resize one object while keeping stale descriptor identities and bounds.
5. If an **owner-specific** graphics component is found, implement an optional, identity-guarded override of its value to 1280×720 or a 2/3 scale **only for Lamentum**, pinned to the exact main NSO and metadata SHA-256. Do not commit patched original game files; use a verifiable temporary state override or document an owner-local patching procedure.
6. If no owner component can be established, consider a backend virtual-resolution translator (logical 1920×1080 -> physical 1280×720) **only with complete handling** of FBO dimensions, render/copy rectangles, texel offsets, shader sampling and LOD, viewport/scissor, clipping, UI pixel alignment, pointer coordinates, and downstream render-target consumers. This is a **high-risk, expensive fallback**, not the first experiment.
7. Run a controlled sequence: original 1080 -> 720; later, separate 960×540 and 640×360 experiments only as explicitly labeled quality presets. Prefer native-resolution UI and text, possibly reducing only carefully identified scene/lighting intermediates before upscaling.
8. Compare **real KMS screenshots** of title, main menu, Options, inventory, moving gameplay, bloom/highlights, readable text, clipping and stencil. Collect actual GPU timing, memory residency, CPU replay, frame P95, and startup pressure for the same scene and clocks.
9. Do **not** undo build202's shader mapping correction while rebuilding. The established UI projection values include scales of approximately 2/1920 and 2/1080 in the 160-byte UBO1. Simply resizing an FBO while retaining an old matrix may move or hide UI elements.

**Comparison with West of Loathing:** in that port, an owner-specific Unity UpRender component (whose existence in **Lamentum has not been established**) produced a measured change from about 24 to 33–34 frames/s in one scene. Do not transfer its field offsets, title hashes, or conclusions about docked mode from the [WoL roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md). Determine the source in **Lamentum itself**.

**PASS:** player-visible rendering and interaction remain correct with repeatable whole-frame gains at the same scene, clocks, and memory-safety level. **STOP:** blurred UI, screen/input misalignment, incorrect alpha, or unresolved render-target aliasing.

## 9. P1-POST — Optimize Bloom, Noise, and Other Postprocessing on Mali

**Candidate points:** NVN pair 17/4 and its ten-level downsample chain, pair 11/9 and the near/final composite stages. Exact pass dependencies must be established. An in-game **Noise effect** setting is visible in Options; **do not assume it disables bloom**.

**Methods in increasing order of risk:**

1. Reconstruct a **per-pass dependency graph**: source texture IDs, output target/format/size, draw counts, shader pairs, clear/load/store behavior, subsequent readers, aspect ratio, and resource lifetime.
2. Measure CPU and GPU cost for each pass. Use EXT_disjoint_timer_query only if the actual Mali/EGL stack supports it, with sparse sampling and disjoint checks. Calling glFinish after every pass would distort the workload; otherwise report that GPU query timing is unavailable.
3. Start with supported in-game settings: compare Noise effect On/Off and any actual brightness, shadow, or effects presets independently in the same scene. Confirm which stage the setting affects. Changing noise is **not automatically** equivalent to eliminating blur or lighting.
4. Only if **bloom specifically** is expensive, add a quality tier using proven guest shader uniform/source provenance. Candidates include fewer downsample levels (for example 10 -> 6 **only when no downstream consumer references removed levels**), fewer sampling taps/smaller radius, or lower offscreen resolution while preserving the original mode. Verify alpha blending, color space/sRGB, and temporal behavior.
5. If framebuffer changes dominate, optimize grouping of safely adjacent passes, reuse complete FBO objects, and remove redundant state binds. On Mali, tile discard/invalidate is safe only after the **last attachment reader**; never blindly invalidate inputs to the final composite. Do not disable glBlend/glDepth/glStencil globally.
6. Keep shader code+control identities exact and validate matrices, UV/texelFetch addressing, embedded literal banks, and sampler metadata. Review screenshots in dark scenes, bright scenes, and menus; a nonblack-pixel count alone is not sufficient.
7. Offer an explicit, reversible **Original / Performance** quality setting only if real-game profiling shows a meaningful benefit and its visual cost has been reviewed. Preserve the original renderer as default until accepted.

**PASS:** an accurately described, reversible performance preset with measured GPU/whole-frame savings. **STOP:** invisible/incorrect interface elements, wrong effect colors, broken bloom, or a gain within measurement noise.

## 10. P2-GPU-MEM — BC Atlases, GPU Residency, and Loading

**Existing functionality that must not be reinvented or broken:** an 8192×4096 BC3 atlas, 128-row striped decoding instead of a full 128 MiB RGBA temporary buffer, deferred BC uploads, lossless file backing after complete writes, a bounded **420 MiB** GPU texture budget, and historical memory-floor experiments. See [loading-memory](loading-memory.md) and [builds 170–174](loading-memory-170-174.md). Do not add guest-compressor savings and file-backed byte counts as though they were independent savings.

1. Build a **resource-ID ledger** mapping each texture to its guest pool alias, write epoch, decoded/resident GL texture, format/mips, actual first/last use, creation/destruction timestamps, and in-flight readers. Union overlapping guest backing ranges before computing accounting totals. Do not equate GPU committed bytes with process RSS/PSS.
2. Specifically profile **repeated** zero_texture_refresh, LC2_BC_MATERIALIZED, and TextureWriteTexels operations: allocation, BC3 decompression, GPU upload, driver CPU time, stalls, backing-file reads, and faulted pages. If the same texture repeatedly materializes, investigate an invalidation/dirty-generation loop. Only an exact write-range epoch and resource generation can justify skipping updates.
3. Optimize full-resolution uploads only with strict proof of immutable content. For frequently modified atlases, test partial dirty-region upload using glTexSubImage2D, retaining BC tiled-block alignment, source pitch/stride, swizzle, levels, and the original graphics interpretation.
4. Probe **real device support** for compressed formats: GLES extensions and an independent pbuffer upload/readback test. ASTC support or a narrow working path in **West of Loathing** does not automatically prove that BC3-to-ASTC conversion, quality, or the required library will work correctly for Lamentum.
5. If supported, prototype an **owner-local, content-addressed ASTC side cache** for a small allowlist of immutable atlases. Pin source SHA-256, exact dimensions/mips/format/color space, encoding quality, alpha representation, and free SD storage. Provide a fail-closed fallback to the existing lossless BC path. Never commit proprietary assets or binaries. ASTC conversion may be **lossy** and requires a separate visual-quality acceptance gate.
6. Do not evict/decommit inactive guest bytes based merely on pagemap zeros or inactivity timers. A real owner lifetime, exact reconstruction path, and the absence of GPU framebuffer/sampler readers must be established. Keep valid resource generations and fences; do not disable the 420 MiB cap.
7. Trace SD/UDISK backing latency, disk-capacity reserve, blocking pread, guest page faults, and deferred uploads. Background prefetch is acceptable only with proven dependencies, barriers, and RAM safety.
8. Include menu -> New Game, an interior, and a gameplay/effects scene in A/B testing. The number of successfully initialized textures alone is not FPS evidence, and the **32 MiB diagnostic floor** is not a production default.

**PASS:** lower P95 stalls or measured GPU/CPU residency without image/color regressions and with safe memory headroom. **STOP:** memory floor, corrupted textures, aliasing errors, long storage stalls, or GPU OOM. Do not turn off system swap.

## 11. P2-SYNC — Correct NVN Queue/GPU Pipelining Without Unsafe Early Completion

**Current state:** COTM_ASYNC_QUEUE=0 and T2_GPU_PIPELINE=0 form the measured stable synchronous path. A previous version hit NVN_COMMAND_REUSE_BEFORE_COMPLETION. SDL/KMSDRM can recreate its EGL surface on the first fullscreen swap; handling this is covered in [loading-memory](loading-memory.md). COTM_FB_PRESENT=0 and strict GL errors remain defaults. Do not activate the framebuffer-copy path without separate proof.

1. After Sections 4 and 7, enumerate **all** GPU waits, resource producers/consumers, and command serials. Determine whether the CPU actually sits idle while the GPU is doing significant work, and whether available RAM can support additional in-flight frames.
2. For each command list, track generation, writer publication, replay start/end, touched resources, GPU submission completion, and the **first legal recycling point**. Write a serial-ownership contract and host tests that reject command-arena reuse before fence completion, stale pointers, context loss, and serial wraparound.
3. For GLsync/fences, verify GLES3/extension support, insert the fence **after** producer commands, flush as needed, and perform explicit client wait/completion handling. Never claim completion merely because the host submission function returned. Validate fence-object lifetime and ownership by the EGL context.
4. Only after synthetic ownership tests, separately A/B **COTM_ASYNC_QUEUE=1 versus 0** and **T2_GPU_PIPELINE=1 versus 0**; test 1/1 together only once both isolated configurations are correct. Preserve known-good executables and rollback procedures for each variant. Include idle UI, moving gameplay, and scene transitions.
5. Measure the **whole-frame period and P95**, not just a shorter local replay span. Moving blocked time into glFinish, or introducing dropped/black frames, is not a performance improvement.
6. Explicitly invalidate GL state on each context after surface recreation, render/present context handoff, and shader resource recycling. Do not ignore EGL_BAD_SURFACE or mistake CPU timestamps for GPU completion.
7. If synchronization cost is small, retain the correct synchronous path and close the experiment as **OFF**. Adding concurrency for hypothetical 0–1 ms savings is not justified.

**HARD STOP:** NVN_COMMAND_REUSE_BEFORE_COMPLETION, NVN_QUEUE_CONTEXT, NVN_PRESENT_CONTEXT, EGL_BAD_SURFACE, black/tearing frames, stale uniforms, or premature reuse of command memory.

## 12. P2-CPU — Scheduling/Affinity, Unity Hot Spots, and Compiler Flags

**Observed behavior:** HOST_CPU_AFFINITY logs show guest-main pinned to CPU0. The launcher temporarily brings CPUs 0–3 online and restores their previous online state on exit. Do **not** assume that core 0 is slow without real board measurements. SpruceOS may choose its own CPU layout, governor, and thermal policy.

1. Inspect /sys/devices/system/cpu/{online,cpufreq/*}, available per-core clock frequencies, actual topology, /proc/TID/schedstat, thermal zones, and throttling **while gameplay is active**. Compare actual guest CPU execution, runnable delay, and compression-thread CPU consumption. Collect data externally; do not force clocks.
2. Run one-factor affinity A/B experiments: current CPU0 pin, a specifically identified available/appropriate core, and scheduler-managed placement. **Do not** change guest Horizon core/priority semantics without tracing the relevant thread. Preserve and restore the original online mask on all normal/error exits; verify input/audio threads remain correct.
3. Only when guest CPU time is actually large, sample guest PC/call stacks and map them through read-only owner NSO/IL2CPP metadata, pinned to source hashes. Optimize frequent SVC stubs, TLS, IPC locks, copies, or allocator paths with exact ABI and side-effect equivalence, property tests, and no proprietary title patch.
4. Inspect the actual baseline native/build.sh compiler invocation and tools/cc-lamentum.sh wrapper. The wrapper delegates to GCC with inherited build flags and -DZERO_ZX_GAME=0. Compare -O2 versus -O3, LTO, or PGO **only after** correctness and source parity are established. Train PGO on representative gameplay, not just title/menu or loading. Measure binary size, cold startup, resident memory, thermal impact, and compile/runtime errors.
5. If Section 7 locates significant steady-state work in shader lookup, conversion, or compilation, optimize a narrow proven path: static shader/program specialization, cached uniform locations, fewer temporary allocations, or precomputed metadata. Embedded literal-bank specialization already exists; do not redo it as if it were missing.
6. Avoid permanent governor changes, overclocking, undervolting, min_free_kbytes/swappiness adjustments, or disabling swap. These introduce separate device stability, battery, thermal, and safety questions, and historical memory tuning produced no general solution.

**PASS:** repeatable whole-frame P95 gains in real gameplay without thermal, sound, input, or Spruce CPU-restoration regressions.

## 13. P3 — Other Options That Must Not Be Tried Blindly

| Proposal | Priority / current decision | Evidence needed before revisiting |
|---|---|---|
| Simply lower the physical SDL/KMS display mode to 720p | The panel is **already 720p**; changing it does not imply smaller internal Unity targets | Verified internal resolution owner |
| Force Handheld instead of Docked, or fake a VI resolution | Do not copy the WoL experiment: this game uses a different Unity/SDK contract | An observed API call and verified consumer |
| Bypass glFinish or fake command completion | **Prohibited for release**; resource-reuse stops already occurred | Proven serial/fence/resource-ownership model |
| Enable async unconditionally | Keep disabled by default | Significant measured synchronization waits and passing concurrency correctness tests |
| Disable all ZRAM/file backing | Risks memory-floor stops and OOM | Proven, measured resident memory headroom |
| Set T2_MEMORY_FLOOR_MIB=0 or remove the 420 MiB GPU cap | Not a legitimate FPS toggle | A validated replacement memory-accounting/safety model |
| Global sysctl tuning, swapoff, or forced CPU clocks | Not recommended as a performance fix | A separately reproduced and diagnosed hardware/system cause |
| Remove bloom, UI, or particle draws globally | Incorrect rendering and possibly broken stencil/alpha/depth behavior | An explicit, reversible, quality-reviewed preset |
| Replace a TEST shader with a constant/blank output | Insufficient for correct gameplay | Semantically verified shader implementation or a guarded, proven-unused path |
| Merge every draw that uses the same shader | Unsafe for alpha/depth/UI ordering | Exact draw-dependency and state equivalence |
| Rewrite the runtime around Vulkan or direct DRM zero-copy | Long-term R&D with a very high portability cost | A demonstrated fundamental GLES bottleneck |
| Rebuild Lamentum as a native ARM64 Unity game | Not practical without rebuildable original game sources | Owner has full game source and a viable engine toolchain |
| Increase detailed logging to diagnose FPS | Adds substantial measurement overhead | A bounded diagnostic trace and quiet-run comparison |
| Run the Switch game via Box64 | Not applicable to the native ARM64/Horizon goal | Do not pursue |
| Disable kernel safety mechanisms or patch proprietary game files indiscriminately | Not required or justified | Never use as an unguarded performance workaround |

## 14. Prioritized Execution Plan, Checks, and Deliverables

| Priority | ID | Specific action | Required deliverable | Decision |
|---|---|---|---|---|
| P0 | F0 | New Game -> controllable scene; audible sound; cold save/load | Visual/state screenshots, exact executable, logs | Required before FPS claims |
| P0 | B0 | One-factor diagnostic vs quiet A/B | Frame/replay P50/P95 and external observer data | Reorder work using fresh evidence |
| P0 | T0 | Explain elapsed wall time vs CPU vs wait; >=95% attribution | CPU/GL queue/thread spans | Fix the dominant delay |
| P1 | M0–M5 | Guest-page compression cold/budget/fault A/B | Safe headroom, fault stalls, full-frame P95 | Keep best candidate or close the family |
| P1 | C1–C3 | Replace redundant cbuf TexImage with guarded subimage/reuse | GL call counts, CPU time, pixel parity | Require valid resource generations |
| P1 | R1–R4 | Sampler, GL state, VBO, and FBO hot spots | Replay-stage timing and paired A/B | Only fix measured costs |
| P1 | G1 | Identify 1080p owner and test scoped 720p | Identical-scene screenshots, memory/FPS | Only if a real owner/consumer is proven |
| P1 | G2 | Opt-in postprocessing/bloom preset | Explicit visual quality vs performance report | Only if GPU time is material |
| P2 | M6 | Resource residency, BC decoding, ASTC side cache | Verified lifetime and cache source hashes | Only if memory pressure is substantial |
| P2 | Q1 | Fences/async experimentation when eligible | Serial ownership proof | Keep default OFF until accepted |
| P2 | C4 | CPU affinity/compilation candidates | Clock/thermal data and frame P95 | Reject regressions |
| Final P0 | A0 | Extended gameplay, save/load, release packaging and cleanup | Full release-acceptance evidence | Freeze accepted release flags |

**Frame-time budgeting:** the median values in Section 0 **must not be added**. In the final profile, classify guest CPU, rendering CPU, waits, GPU completion, and present time **for each frame**, then compare distributions of frame P50/P95. If removing diagnostics makes B0 dramatically faster, prioritize the bottleneck observed in the new measurements rather than the historical ones. If a reproducible ~400 ms gap remains, T0/M0 outrank shader tuning. If actual gameplay is substantially more expensive than the menu, prepare a separate gameplay-specific ranking.

## 15. Evidence Format for Every PR: Rationale, Reproducibility, and Rollback

Implement **one small opt-in performance feature per PR**. Each PR description must include precise code locations, a screenshot or log demonstrating the current problem, a falsifiable counterfactual hypothesis (for example, "if cbuf contents are unchanged, bypassing redundant uploads should save X ms"), **a measurement of X before the change**, safety assumptions, regression tests, and a criterion for rejecting the hypothesis. Do not enable a feature by default before passing the complete acceptance gate.

Suggested evidence folder structure, excluding game binaries and user saves:

~~~text
evidence/perf-<ID>-<unique-tag>/
  README.md               Source, version, scene, A/B rationale
  identity.json           Repository commit, baseline manifest hash,
                          ELF SHA-256, owner image/section SHA-256,
                          shader catalogue SHA-256, device/OS identifier
  env-a.json              Flags, clocks/governor, memory settings, phase
  env-b.json              Exactly one changed factor
  frame-a.csv             Present serial, monotonic_ns, phase, duration
  frame-b.csv             Same fields, provenance, missing samples
  observer-a.csv          CPU/TID, faults, RSS, PSS/SwapPSS,
                          MemAvailable, CmaFree, temperature, swap I/O
  observer-b.csv          Equivalent measurements
  summary.json            P50/P90/P95/P99, counts, false/missing frames,
                          A/B deltas and uncertainty/noise classification
  screen-a.png            Actual DRM capture while game PID is alive
  screen-b.png            Equivalent scene, original screenshot retained
  cleanup.json            Game PID=0, MainUI=1, principal restored,
                          original CPU mask, no leaked processes
~~~

**Required experiment workflow:** pin source and image identity -> verify build and tests -> back up current working executable and saves -> verify idle device and disk-space reserve -> run A -> verify cleanup -> run B -> verify cleanup -> repeat matched pairs -> analyze distributions -> manually review screenshots, controls, audio, and saves -> decide on promotion or rollback.

Git evidence must **not** include extracted proprietary NSO code, RomFS assets, keys, user-save data, or unprocessed original shader binary blobs.

**How to report FPS:** calculate real throughput as number_of_presented_frames / measured_steady_elapsed_seconds. The value 1000/median_period_ms may be reported separately as an **inverse median interval**, but must not be interpreted as confirmed physical-display FPS without a verified presentation sequence. Include P95/P99 spikes and missed v-sync intervals. Startup and scene transitions may be excluded **only from an explicitly separate steady-play report**; they must still be reported rather than silently hidden. In a 60 Hz output mode, stable 30 FPS generally requires consistent delivery of one game frame per two scanouts, accounting for queue behavior and jitter. Always disclose sampled frame count, time window, scene/phase, loading fraction, and profiler overhead.

**Prerequisites and host testing:** run sha256sum -c tools/baseline-manifest.sha256, all applicable tools/test_*.py and available C host fixtures, UI cbuf replay tests, launcher CPU-restoration tests, shader append-only tests, and new GL resource-lifetime/invalidation tests. Then perform the full AArch64 cross-build in the pinned container and read back the installed executable's SHA-256. Preserve the previous working binary as a rollback target.

tools/device_principal_test.py is **not a general-purpose test laboratory**: it includes owner-specific SSH/device paths and MainUI handoff assumptions. Adapt it only within the owner's controlled workspace and never run it blindly against another device.

## 16. Definition of Done and Stop Criteria

**Do not claim that 30 FPS has been achieved until all the following are true:**

1. The pinned executable and owner-generated image reach a **reproducible, genuine gameplay scene** controllable via the physical TSPS controller. The real 1280×720 KMS output is correct, with no missing UI text or options and no broken stencil, lighting, bloom, alpha, or constant-buffer binding.
2. Audible music/sound effects, inventory, dialogues/interactions, save -> quit -> cold start -> load, and the restored player/inventory state are verified. The port exits cleanly, returns to MainUI, and restores the original CPU state.
3. At least **three independent warmed-up gameplay runs of 60 seconds each** are available for the same controlled route, with measured clocks and thermals. Test stationary gameplay and movement separately, plus effects/interior scenes and transitions. For gameplay, full-frame **P50 <=33.33 ms and P95 <=33.33 ms** are required; **P99 <=50 ms** is an additional target, with no recurring stalls >100 ms. If strict P95 <=33.33 ms is not met, report that the 30 FPS acceptance criterion **has not been achieved**, even if the average rate is 30.
4. The A/B evidence includes a phase-level latency breakdown, diagnostic overhead, true presented-frame throughput, and verification that frames were neither lost nor rendered incorrectly. Do not artificially accelerate guest clocks or ignore shader/resource errors to pass the benchmark.
5. MemAvailable/CmaFree, SwapPSS, major faults, and temperature remain safe under sustained gameplay, without an OOM, kernel crash, corrupted saves, or orphaned processes. The production memory floor/flags must be qualified independently rather than copied from the diagnostic 32 MiB environment.
6. Full source parity is established: recovered baseline identity, adapter patch, GLSL source catalogue, and installed executable. Evidence and rollback instructions must be available, and rejected experiments must remain explicitly disabled.

**Stop rules for an individual performance feature:** an FPS difference within run-to-run noise after three A/B comparisons; a replay gain completely shifted into GPU wait; any lost texture, UI element, or shader resource; memory floor/OOM; failed CPU restoration; unknown guest-buffer dependencies; or incorrect shader-program identity. In those cases, **do not enable the flag in release**, preserve the evidence, and close the hypothesis or return to prerequisite investigation.

## 17. External References and Recommended Next Steps

- [West of Loathing optimization roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md) and the [measured frame-time breakdown of 2026-10-16](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): a verified methodology for measurement, feature flags, and identifying an owner-level Unity 720p setting; **not** a ready-made Lamentum-specific patch.
- [Arm Mali: framebuffer handling](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/mali-performance-2-how-to-correctly-handle-framebuffers): attachment load/store/invalidate operations require correct tile-rendering dependencies and resource lifetimes.
- [Mali tile-based rendering guide](https://documentation-service.arm.com/static/636dfb934e6cf12278ad8c27): external reference material, **not** a benchmark for this particular handheld.
- Existing [UI cbuf binding](ui-cbuf-binding.md), [constant-buffer isolation](cbuf-unit-isolation.md), [shader literal banks](shader-literal-bank.md), [disabled-fragment probe](probe-disabled-fragment.md), [shader catalogue tail](catalogue-tail.md), and [loading-memory builds 170–174](loading-memory-170-174.md) document exact provenance and previously established failure boundaries.

**Recommended next experiment is not another speculative shader tweak:**

1. Verify New Game and real gameplay correctness (**F0**).
2. Collect a clean performance baseline (**B0**) before interpreting build202's diagnostic frame-time numbers.
3. Instrument an elapsed-wall-time and per-thread-CPU timeline (**T0**) to explain the approximately 400 ms of unattributed time.
4. If guest compression is actually expensive, run controlled **M0–M4** experiments; otherwise, measure and optimize the concrete **constant-buffer/replay** hot path.
5. Then investigate the **Lamentum-specific 720p owner** if the internal 1080p target proves significant. Consider bloom, ASTC, asynchronous GPU submission, and compiler tuning only if profiling identifies a relevant cost and the appropriate safety gates are met.

**Execution note:** this roadmap comes from a GitHub source and evidence audit. **No new handheld runs, verified 30 FPS benchmarks, proprietary game-executable patches, hardware deployments, or on-device tests were performed during the audit.** Build202 measurements establish the existence of a performance problem; the techniques above are engineering hypotheses and a plan for testing them, not completed fixes.


---

## 18. Post-roadmap reassessment (2026-10-20)

**Source revision reviewed:** main 51707cd8b53229ba706d19a92a61e23ec592bd9b, including the three commits since the English roadmap: b3a3c207, 1889e870 and 51707cd8. This is a read-only review of committed code, documents and evidence, **not a new handheld run**. The original 30 FPS target and functional acceptance criteria remain unchanged.

**Evidence limitations:** New performance directories such as evidence/perf-flush, perf-gz-cold250, perf-quiet-b202 and perf-sub-on contain only perf-distribution.json. Their raw latest.log, effective environment files, matching device ELF hashes, live screenshots and cleanup receipts are not committed. The numbers for frames 250–500 in [docs/fps-baseline-2026-10-20.md](fps-baseline-2026-10-20.md) are therefore author-reported; the committed summary JSONs independently contain only whole-run and late (500+) distributions. The README still identifies build202 as its installed reference ELF, while the new baseline mentions build208. Do not assume that the checked-in patch, benchmark build208 and installed executable are identical without their SHA-256 readback.

### 18.1. Completed work and what the new measurements actually show

| Work item | Code/evidence | Verified implementation and measured status | Decision |
|---|---|---|---|
| Frame distribution parser | tools/analyze_perf.py | Added and produces interval P50/P90/P95/P99, but its first sub-1000ms period heuristic is not scene validation | Keep, repair phase identification |
| Quiet diagnostic comparison | docs/fps-baseline-2026-10-20.md and evidence/perf-* | Real runs reported; median diagnostic readback still ~2.3–2.4ms even in quiet variants | Publish complete evidence; test proof-preserving readback reduction |
| Cbuf subimage reuse | runtime/lamentum-adapter.patch, native/nvn_render.h, LC2_CBUF_SUBIMAGE | Implemented and currently defaults ON. Reported period P50 609.2 -> 629.0ms and replay 274.8 -> 297.7ms; no measured gain. But the compared rows name build202 and build208 despite prose claiming same ELF | Same-ELF 0/1 control before causal conclusion; do not spend effort reimplementing C1 |
| Guest compression timing | native/t2_guest_memory.h | Added compress/restore elapsed counters in T2_GZRAM | The code uses CLOCK_MONOTONIC: labels cpu-compress-ms and cpu-restore-ms are **wall elapsed**, not proven CPU time |
| ZRAM cold threshold experiment | evidence/perf-gz-cold250 and baseline doc | Reported cold10 -> cold250: period P50 629.0 -> 579.3ms, replay 297.7 -> 240.8ms; timed paths 138 -> 59ms/frame and compressions 566 -> 248/frame | Promising but memory impact and repeatability still unverified |
| Submit finish to flush | evidence/perf-flush and baseline doc | With cold250, reported period P50 579.3 -> 557.1ms, replay 240.8 -> 185.4ms | Diagnostic only until GPU completion and resource ownership are proven |
| External per-thread sampler | tools/perf_sample.py | Implemented, but top_threads CPU calculation has a missing clock tick conversion | Correct before using for conclusions |
| Input latch | native/lc2_input_latch.h and tools/test_input_latch.c | Implemented behind LC2_INPUT_LATCH=1, default OFF, seven host assertions | On-device button/visual validation pending |
| New Game and tap probes | tools/newgame_probe.py, tap_sweep_probe.py, analyze_newgame.py | Added, but no corresponding verified New Game gameplay evidence published | Fix wrong Confirm event, capture/PID gates |

**Important metric interpretation:** cold250 changes the reported median frame period by about 7.9% in the specific diagnostic window. The subsequent submit flush change improves the reported median by another ~3.8%, but does not demonstrate safe GPU completion or normal gameplay. The latest reported 557ms period is roughly **16.7 times the 33.33ms budget**, with about 338ms of remaining unattributed time. None of these results establishes playable 30 FPS.

### 18.2. P0-A — Correct the New Game test before interpreting any failure

**New source-level defect:** tools/newgame_probe.py currently sends Linux evdev key code **304** while commenting it as BTN_SOUTH/A Confirm. The title-specific measurements in [docs/hid-input-contract.md](hid-input-contract.md) and [the build202 action receipt](../evidence/ui-cbuf-fixed-01/control-actions.json) show **304 / BTN_SOUTH maps to guest Switch B and performed Back**; the successfully tested **Confirm was Linux code 305**. As written, the New Game probe may navigate to New Game and then press Back.

**Implementation sequence:**

1. Change the new-game Confirm event from 304 to **305** and replace the incorrect comment. Make a shared mapping table/constant containing Linux event type/code, guest button mask and previously verified role, with a host regression that checks the action matches the published receipt. Verify the physical evdev provider path/device identity at test start; /dev/input/event4 is a device-specific observation, not a universal constant.
2. Model navigation as BOOT -> LIVE_MENU -> NEW_GAME_SELECTED -> CONFIRM_SENT -> SCENE_LOADING -> LIVE_GAMEPLAY or FAILED. The script currently assumes a default selection of Options and a single Up action reaches New Game. Verify actual highlighted item by a live KMS capture before pressing Confirm; otherwise fail closed and report uncertain selection. Do not label opened Options as New Game.
3. Change shot() so it captures only when the **owned game PID and start_time** are present and the expected active DRM plane belongs to the game. The immediate before-title capture may otherwise be Spruce MainUI. Record PID, frame serial, image hash and capture outcome for every frame; a screenshot filename is not pixel proof.
4. Replace reading only the last 4000 bytes of the log to infer the most recent frame with a low-overhead monotonic frame counter or incremental file cursor. The existing log is large; failure to see a frame in its tail is not proof that rendering stopped.
5. Verify press/release and dwell: use the owner-observed 305 Confirm with an explicit release, then capture after at least one new presentation. Independently A/B short input taps of 120ms and 300ms versus 1000ms holds with LC2_INPUT_LATCH=0/1; ensure one physical tap does not become multiple menu actions or a stuck key.
6. Back up all existing owner saves byte-for-byte, verify SHA, and do not restore over an active runtime. If New Game reaches a new shader tail, preserve the code/control identity and use append-only catalogue tools; do not regenerate the validated build202 UI mapping. Check sound, movement, interaction and scene correctness before claiming gameplay.

**Owner-workspace command only after applying these fixes and validating idle device state:**

~~~sh
LAMENTUM_NEWGAME_BUDGET=600 LAMENTUM_MENU_FRAME=400 \
  python3 tools/newgame_probe.py /owner/local/quiet-env.json newgame-verified-01
python3 tools/analyze_newgame.py evidence/newgame-verified-01
~~~

**PASS:** actual New Game highlight, guest Confirm mapping, visual scene transition and a controllable scene, or an exact named shader/memory/SDK blocker. **STOP:** wrong selection, uncertain owned PID, unverified save backup, incomplete shader, unsafe memory pressure.

### 18.3. P0-B — Repair performance evidence and parser validity

**Problem:** results reported as one-variable comparisons cannot be independently audited if full runtime logs, effective flags, scene classification and ELF identities are absent. Moreover, tools/analyze_perf.py marks the first period below 1000ms as after_warmup; that can be the second frame during loading and is **not** valid phase identification. It clamps unattributed time at zero, masking negative residuals/overlapping instrumentation.

**Tasks, in order:**

1. Produce a complete and reproducible manifest for each run: Git SHA, recovered baseline manifest SHA, adapter patch SHA, owner section hash, shader catalogue hash, installed ELF SHA readback, kernel/Spruce/GLES driver identity, device CPU clocks and temperature, effective non-default env, stop reason and MainUI/CPU restoration.
2. Retain raw compressed logs (or immutable private SHA-pinned log copies when distribution is inappropriate), along with exact frame-250–500 reports computed from those logs. Each evidence/perf-* directory should include identity.json, env.json, summary.json, per-frame metrics, device-state.json, cleanup.json and a game-PID-verified KMS capture. Do not include proprietary NSO/RomFS/shader binaries or user saves.
3. Add explicit phase start/end parameters to tools/analyze_perf.py, tied to visual New Game/menu scene proof. Rename the old first-sub-1000ms criterion heuristic_only or remove it. Do not mark the entire run as warmed up because frame 2 happened to be below 1000ms.
4. Audit the exact T2P_SLOW_FRAME logging predicate in the recovered baseline. If it logs only slow frames, the resulting distribution is selection-biased and becomes useless as performance approaches 30 FPS. Add unconditional cheap timestamp/serial sampling into a fixed-size ring and batch-output once per 60–120 frames or on exit. Track missing/reset serials, dropped samples, and CLOCK_MONOTONIC_RAW.
5. Report signed residual = period - (explicit measured stages), together with negative-residual count. Keep inclusive/exclusive clocks and overlap separate; do not add independent stage medians to infer total frame time.
6. Identify why quiet runs still spend ~2.3–2.4ms on pixel readback. Trace the real present/readback functions and error/proof dependencies before disabling anything. A/B the **diagnostic** readback path with physically identical KMS screenshots; leave GL errors strict.
7. Repeat cbuf, cold threshold and submit arms with one flag changed on the **same ELF** and identical save/scene/clocks. At least A/B/A/B initially, then three matched pairs for any candidate before a release decision. Publish both P50 and P95/P99 and memory headroom.

**PASS:** independent reviewer can reproduce the published 250–500 distribution, classify the real scene and account for sample selection/overhead. No menu-only or arbitrary frame-window results may be promoted as gameplay FPS.

### 18.4. P0-C — Correct perf_sample.py CPU units and attribute the remaining 338ms

**Critical arithmetic defect:** the script computes a top thread's cpu_ms_per_s as 1000 × delta_cpu_ticks / elapsed_seconds. Linux /proc/TID/stat utime+stime is in **clock ticks**, not milliseconds. It must divide by the **device CLK_TCK** too, just as aggregate CPU percentage does.

~~~python
# Example for the analyzer; obtain hz from the device, not the workstation:
hz = device_clk_tck
cpu_ms_per_s = 1000.0 * delta_cpu_ticks / (elapsed_seconds * hz)
cpu_percent = 100.0 * delta_cpu_ticks / (elapsed_seconds * hz)
~~~

**Further fixes and precise instructions:**

1. Collect os.sysconf("SC_CLK_TCK") on the target TSPS through the device-side sampler. The current Python controller calls the workstation's os.sysconf; equality between host and target should **not** be assumed. Add host tests with synthetic 100Hz and 250Hz target clocks.
2. Record the owned PID and process starttime returned by the launcher. The script currently scans for the first matching truncated /proc/comm, which can select a stale/other process; refuse identity changes and handle PID/TID reuse. Parse /proc/PID/stat safely around the parenthesized comm field, not by blindly splitting a command name containing spaces.
3. Return **every** thread's delta for utime/stime, minor/major faults, state, schedstat run/runnable-delay (when accessible), context switches and wchan. Preserve raw thread rows even if the terminal summary shows only the top six.
4. Derive frame numbers from monotonic counters or incremental logs rather than scanning the last 3000 bytes of stdout; reject frame reset/negative delta/missing sample instead of silently deriving guest_frame_ms from unrelated SSH polling.
5. Add true CLOCK_THREAD_CPUTIME_ID CPU instrumentation in the codec, compressor thread and relevant guest/render paths, along with CLOCK_MONOTONIC_RAW elapsed spans. The newly added T2_GZRAM cpu-compress-ms and cpu-restore-ms use CLOCK_MONOTONIC, meaning they include elapsed scheduling and allocation work and cannot be called exact CPU usage.
6. Produce per-frame mutually exclusive categories: guest-main executing, guest-main runnable but not scheduled, guest-main sleeping on Horizon wait/timer, compressor executing, render/replay executing, GPU/context wait, and page-in/IO wait. CPU on different cores can overlap; **never sum thread CPU time as wall time**.
7. Sample externally every 1–5 seconds first; enable a bounded internal ring only after naming the dominant wait/call path. Profile the same scene, ELF and memory envelope, with profiler overhead below 5%.
8. Follow the resulting decision tree: guest-main CPU hotspot -> guest PC/IL2CPP/SDK stack; guest-main blocked -> WaitSynchronization/SleepThread/vblank/event loop; compressor contention -> §18.5; GL wait -> §18.6; major faults -> guest memory residency ledger.

**PASS:** >=95% of complete frame period is attributed through consistent wall-time categories; thread CPU values use correct target units, and the ~338ms residual is no longer an unsupported guess.


### 18.5. P1-ZRAM — Replicate and Safely Extend the Cold-Threshold Result

**Measured, not production-qualified:** according to the new baseline document, cold10 -> cold250 reduced the frame period median from 629.0 to 579.3ms and replay median from 297.7 to 240.8ms, while timed compression+restore work fell from ~138 to ~59ms per presented frame and compressions fell from ~566 to ~248 per frame. Because the source uses CLOCK_MONOTONIC, the latter durations are **elapsed time within selected code paths**, not necessarily executing CPU milliseconds. No independent memory-safety proof for cold250 has been committed.

**Next experiment matrix (all other settings, current shader catalogue, ELF, owner save, device clocks, GPU budget, and memory floor held constant):**

| Arm | Exactly one changed value | Hypothesis / required observation |
|---|---|---|
| Z0 | T2_GZRAM_COLD_MS=10 | Control in the currently documented diagnostic memory envelope |
| Z1 | T2_GZRAM_COLD_MS=100 | Intermediate CPU-vs-memory tradeoff |
| Z2 | T2_GZRAM_COLD_MS=250 | Reproduce the reported best short-window result |
| Z3 | T2_GZRAM_COLD_MS=500 | Check diminishing returns and possible memory pressure |
| Z4 | T2_GZRAM_PERIOD_MS=50, from the safest Z0–Z3 choice | Reduce scan frequency without delaying essential reclamation |
| Z5 | T2_GZRAM_BUDGET_MIB=16, from the chosen baseline | Bound per-period compression contention |
| Z6 | Opt-in adaptive per-block cooldown | Stop repeatedly compressing hot guest pages while retaining cold-page savings |

**Detailed implementation:**

1. Collect cumulative T2_GZRAM counters at both ends of an exact, visually verified phase. Derive delta compressions, restores, faults, scans, compressed bytes, stored bytes and time, and divide by the **actual number of presented frames in the same interval**. Do not interpret cumulative counters at one point as per-frame work.
2. Extend the compressor instrument with separate elapsed wall spans and true thread-CPU spans for scan, compression codec, allocation, memcpy, madvise, mprotect, restore/decompression and signal handling. Reconcile those spans with the external per-TID sampler; distinguish the compressor's own CPU from guest-main runnable delay.
3. Introduce an opt-in bounded hot-block histogram, recording anonymized block index, last compression timestamp, next page fault/restore timestamp, number of compress->restore cycles and current resident/stored size. Do not read or dump guest bytes.
4. Run Z0/Z1/Z2/Z3 in A/B/A/B order with identical 250–500 phase boundaries only when that window has been verified to show the same scene. Include P50/P95/P99, true CPU ms/frame, maximum stall, MemAvailable minimum, CmaFree if supported, process SwapPSS, major faults, kernel pswpin/pswpout and temperature.
5. Confirm whether the existing restore-count-based cooldown is already sufficient: t2_gz_restore_locked increases ready_ms after repeated restores. Change only the condition proven inefficient by the hot-block histogram; guard overflow and exact read/write alias lifetimes.
6. Do not disable guest compression across the whole heap without a separately proven resident headroom. Retain guest buffer IO pins and file-backed exclusions and the 420MiB GPU budget guard.
7. Production qualification requires a separate no-diagnostics launch at a safe floor, long enough to cover menu -> New Game -> scene transition -> save/load and thermal settling, with a complete backup/rollback.
8. If cold250 improves P50 but lowers minimum MemAvailable, increases swap traffic or worsens P95 on scene transitions, **keep the old safe policy**. Do not promote a single-window speedup.

**Pass criterion:** at least three matched same-ELF runs showing lower full-frame P95 or materially lower CPU contention with safe RAM and no graphics/save regressions. **Stop:** memory-floor refusal, swap storm, kernel OOM, unsafe alias/page lifetime or negative movement-scene results.

### 18.6. P1-SYNC — Do Not Mistake Submit glFlush for GPU Completion

**Safety issue:** MOMO_SUBMIT_FINISH=0 is described by the new baseline as using glFlush rather than per-submit glFinish. The [Khronos synchronization reference](https://wikis.khronos.org/opengl/Synchronization) explains that glFlush queues/submits work, while glFinish establishes completion. A quicker submit is **not** proof that the guest command arena, uniform texture or GL FBO is safe to reuse. Previous port work already encountered NVN_COMMAND_REUSE_BEFORE_COMPLETION.

**Instructions:**

1. Locate the precise implementation and defaults of MOMO_SUBMIT_FINISH in the **recovered 435-file runtime baseline**. This flag is not introduced in the Lamentum adapter diff. List all submit and completion call sites and the exact conditions that change command-list state from pending to complete.
2. For each command list and resource, instrument a bounded serial ledger: arena generation, guest writer, host queue submit, EGL/GL context, referenced vertex/index/cbuf/texture/FBO objects, explicit completion evidence, last reader, earliest reuse, and any context recreation. Verify no queue slot or GL resource is recycled before the actual GPU completion.
3. On a verified GLES3 device, test an opt-in fence scheme with glFenceSync after producer commands, glFlush as needed and glClientWaitSync/glWaitSync with correct context, timeout and error semantics. Consult the [Khronos sync-object guide](https://wikis.khronos.org/opengl/Sync_Object); a fence cannot simply be marked complete after issuance.
4. Add host/synthetic tests for delayed GPU completion, command arena wraparound, new texture update while its prior sampler draw is in flight, FBO reuse, multiple context ownership and the first SDL/KMSDRM surface recreation. Treat unsignaled/failed fences as pending or fail-closed, not success.
5. For the physical device compare: (A) previous strictly synchronized submit, (B) fence-based proven completion, (C) flush-only **diagnostic** arm. Require exact owner ELF/env, correct KMS captures, zero GL error/command reuse failures and clean MainUI/CPU restoration. Test New Game, moving scene, effects, audio and save/load before promotion.
6. Track all queue/GPU waits, not only the small finish-ms exposed by T2P_SLOW_FRAME. A local replay improvement can move the wait to a later frame and worsen input or stalls. Report end-to-end frame P95/P99, fence age, maximum in-flight resources and first-use texture correctness.
7. Keep COTM_ASYNC_QUEUE=0 and T2_GPU_PIPELINE=0 as production defaults until independent safety tests pass. Do not turn on COTM_GL_ERROR_IGNORE to conceal driver errors.

**Pass:** proven resource ownership and serial completion plus repeated entire-frame improvement with identical gameplay pixels and saves. **Immediate rollback:** command reuse, stale texture/UBO, misrendered screen, EGL_BAD_SURFACE, wrong GL context, deadlock or timeout.

### 18.7. P1-CBUF — Measure Actual Upload Size; Do Not Reimplement C1

**Code reality:** equal-size constant-buffer upload is **already implemented** using glTexSubImage2D behind LC2_CBUF_SUBIMAGE, default ON; reported results showed no improvement. Current kind-7 texture upload also fixes the RGBA32F texture width at **1024 texels**, with height at least one, even when useful guest cbuf data is just **16–368 bytes**. A complete 1024×1 RGBA32F row is ~16 KiB. Thus the potential issue is not simply glTexImage2D allocation frequency, but oversized padded transfers, GL driver submission and redundant data.

**Detailed next candidates:**

1. **C1 final acceptance / rollback:** on **one build208-equivalent ELF**, run LC2_CBUF_SUBIMAGE=0 vs =1, A/B/A/B, all other flags equal. Capture active allocation, GL uploads and text/UI/alpha KMS correctness. If differences remain within noise, make subimage opt-in/OFF (with a fresh safe default test) and close it instead of claiming optimization.
2. **C2 compact uniform texture footprint:** instrument bytes_actually_read, shader_max_access_index, allocated RGBA texels, uploaded texels and driver call duration. For smaller storage, the translated shaders currently address x=(index>>2)&1023 and y=index>>12. Do **not** shrink a texture without proving maximum read bounds or regenerating validated shader coordinate arithmetic. With all accessed indices inside a compact single row, smaller x dimension can be safe only if exact alignment, zero padding and out-of-bounds guards remain equivalent. For dynamic reads, perform conservative full-size fallback.
3. **C3 skip unchanged uploads:** track actual cbuf byte content, GL context/resource generation, program/slot identity and guest mutation epoch. Use exact memcmp (hash only as an initial filter) and invalidate correctly on writes, program changes and context loss. Verify cbuf texture remains readable by prior GPU draws; if completion unknown, retain independent storage/fences.
4. **C4 less GL state churn:** only after micro-profiling actual CPU cost, shadow glActiveTexture/glBindTexture/glUniform1i/glTexParameteri state by context, with explicit invalidation for other draw and present helpers. Measure total frame time, not just saved call counts.
5. Always retain build177 independent texture units, build202 c4->UBO1 mapping, embedded shader literals, sampler descriptors and six real UI draw checks. Use tools/test_cbuf_units.c, tools/test_ui_cbuf_binding.py and tools/analyze_ui_cbuf.py plus physical gameplay screenshots.
6. Stop if this path costs only a few milliseconds: it cannot explain a ~338ms unattributed gap without a demonstrated implicit GPU stall.

### 18.8. P1-READBACK — Quiet Mode Still Performs Pixel Readbacks

In the new committed distributions, quiet runs report **readback-ms P50 ~2.3–2.4ms**, not zero. The current baseline already advertises AW_RELEASE=1, but AW_RELEASE alone does **not** establish the absence of expensive synchronous glReadPixels or correctness/proof readbacks.

1. Trace where readback-ms starts/ends in the recovered baseline and native/nvn_present.h, along with actual paths through t2_video_needs_readback, NVN_PRESENT_PIXELS, NXGL frame proof and optional FBO diagnostics.
2. Classify each readback as **required to display pixels**, **required to detect a rendering error**, **used for frame proof**, or **pure diagnostic sampling**. Do not delete one until its actual owner and side effects are understood.
3. For pure debug sampling, add sparse/opt-in mode (for example one readback every 300 frames or on first failure), with full readback in a separate diagnostic run. Preserve strict glGetError handling even when the debug readback is skipped; the earlier West of Loathing port exposed coupling between diagnostic reads and GL error state, so verify it on this title instead of assuming.
4. A/B otherwise identical runs with real KMS screenshots and known shader/sampler coverage; record GL errors, GPU busy time, frame latency, stalled submits and stop reasons. Removing a 2.4ms readback can eliminate additional implicit synchronization or do nothing; **measure both**.
5. If the readback is part of essential panel copy, do not disable it. Consider a lawful alternative path only with a verified full-screen output and resource-lifetime contract, not by ignoring missing pixels.

**Pass:** same game image and error-checking behavior, lower full-frame time, no missing diagnostic failures. Keep validation sampling available for release smoke tests.

### 18.9. P2 — Other Optimization Families, Conditional on the New CPU/Frame Attribution

These remain relevant **only if the correct gameplay profile identifies their cost**:

| Family | Candidate and exact prerequisite | Why it is not first |
|---|---|---|
| Guest Unity/IL2CPP loop / SDK waits | Trace high guest-main CPU or long SleepThread/WaitSynchronization calls and precise main.text PC; repair incorrect Horizon timing or frequent SVC/memory copy only with ABI and side-effect parity | Current ~338ms is not attributed yet |
| Unity internal resolution | Trace owner-specific 1920×1080 render-target producer, resource consumers, UI CanvasScaler matrices and New Game scene; guarded 1280×720 experiment | 1080p exists, but its real time cost and owner are unknown |
| Mali postprocess | Per-pass timing of 17/4 downsample pyramid and composite; use supported Mali-G57 counters or GLES disjoint timer query | No evidence bloom dominates hundreds of milliseconds |
| Sampler/texture resolution | Per-draw first-resolve versus subsequent resolve, descriptor generation, zero_texture_refresh and GL allocation timing; exact invalidation cache | High impact measured in WoL cannot be assumed for Lamentum |
| BC3/ASTC and texture residency | Atlas materialization frequency, guest pool alias lifetime, validated compressed upload and owner-local cache | Primarily a correctness/RAM project without scene-cost proof |
| CPU affinity and clocks | Real guest-main runnable delay, current clock/thermal topology and core utilization, then one-factor safe affinity A/B | Core0 pin alone is not evidence of a slow-core bottleneck |
| GL shadow state / batching | Actual repeated calls and equal resource identities, with correct target/blend/stencil order | Can break UI geometry and transparency |
| Multi-frame GPU pipeline | Completed serial/fence/resource ownership, then matched repeated performance tests | Flush-only cannot prove completion |
| Compiler/LTO/PGO | Real CPU compute hot path, manifest-pinned source/build parity, representative gameplay profile and tests | Unlikely to solve missing waits or a huge memory-stall component |
| Alternative GPU backend | Proof that the current GLES backend is intrinsically unable to meet the profiled workload and a viable end-to-end port design | High cost and risk; not a justified near-term rewrite |

For the Mali-G57 specifically, [Arm's GPU performance counter guide](https://support.arm.com/documentation/102659/0109/Content-behavior?lang=en) distinguishes geometry/content volume from GPU-driver bottlenecks. Use measured GPU hardware occupancy and shader/pass costs rather than guessing that every 1080p target or bloom stage is expensive.

### 18.10. Five Focused PRs to Execute Next

| Order | PR / priority | Detailed scope | Concrete acceptance/stop gate |
|---|---|---|---|
| 1 | **Correct New Game and input mapping (P0)** | Fix Linux Confirm 304->305 in newgame_probe.py; visual selection gate, owned-PID KMS shot gate, monotonic frame reader, save backup, input latch taps at 120/300/1000ms | Correct guest Switch A and a real New Game transition, or one reproducible named blocker |
| 2 | **Trustworthy per-thread profile (P0)** | Fix perf_sample target CLK_TCK, PID/TID identity and unit tests; identify actual thread CPU vs wait; fix analyze_perf phase gates and capture full run evidence | At least 95% of frame interval attributed; no fabricated CPU ms/frame; overhead quantified |
| 3 | **Safe compression policy selection (P1)** | 3 matched A/B pairs for cold10/100/250/500, then scan/budget and hot-block histograms; cross-check true CPU and resident memory | Repeatable P95 and memory-safe gain, otherwise close with OFF/default unchanged |
| 4 | **GPU completion / proof overhead (P1)** | Identify exact MOMO_SUBMIT_FINISH baseline semantics; fence/serial ownership; A/B safe sync and remaining readback | Correct GPU lifetime, KMS frames and no command reuse/GL errors before any promotion |
| 5 | **One actual top measured bottleneck (P1/P2)** | Choose exactly one guest wait, 720p owner scaler, sampler resolve, cbuf compact/unchanged data, bloom or BC upload based on PR-2 evidence | Three equivalent gameplay A/B pairs with real frame P95 benefit and no regressions |

**Do not execute PR-5 before PR-2 reveals the biggest owner of elapsed time.** PR-1 is a correctness prerequisite, not an FPS mechanism.

### 18.11. Reproduction Commands and Evidence Checklist

**Existing logs, if present in the owner workspace; JSON summary files alone do not recreate their 250–500 samples:**

~~~sh
python3 tools/analyze_perf.py /owner/local/perf-quiet-b202/latest.log \
  --from-frame 250 --to-frame 500 \
  --json /owner/local/perf-quiet-b202-window.json
python3 tools/analyze_perf.py /owner/local/perf-gz-cold250/latest.log \
  --from-frame 250 --to-frame 500 \
  --json /owner/local/perf-gz-cold250-window.json
~~~

**After fixing the CPU units and process-identity logic in tools/perf_sample.py:**

~~~sh
# Example only: this script is owner-workspace-specific and assumes an idle device.
LAMENTUM_PERF_BUDGET=520 LAMENTUM_PERF_INTERVAL=5 \
  python3 tools/perf_sample.py /owner/local/quiet-env.json perf-thread-01
~~~

**Flag comparison plan:** CBUF0 vs CBUF1 must change **only LC2_CBUF_SUBIMAGE=0/1** on the same ELF. Z0/Z1/Z2/Z3 must change **only T2_GZRAM_COLD_MS=10/100/250/500**. The MOMO_SUBMIT_FINISH=0 arm remains **diagnostic only** pending a valid GPU completion proof; confirm the baseline's actual default before any arm. Use controlled separate runs rather than combining changes for a headline result. Do not simply promote T2_MEMORY_FLOOR_MIB=32 into a production launcher: it was a diagnostic loading envelope, not accepted safe RAM policy.

**For every arm save:** exact runtime and source hashes, whole effective env, clock and thermal data, owner save/section identity, game-PID proof, KMS scene screenshots, frame serial/time ledger, per-thread CPU/scheduler/page-fault data, minimum MemAvailable/CmaFree and swap metrics, STOP status and MainUI/CPU-online restoration. No proprietary NSO/RomFS/keys, unprocessed shader binaries or user save bytes in Git.

**Benchmark rules:** compute reported FPS using actual presented-frame count divided by measured steady elapsed time; show P50/P95/P99 in the same verified gameplay phase, not a title/menu counter. A median period of 557ms corresponds to an inverse median of ~1.8 frames/s in that diagnostic window, **not** proof of gameplay throughput or capability. At a real 30 FPS target, complete per-frame P95 should be at most 33.33ms under the chosen acceptance criterion.

### 18.12. Updated Feasibility / Stop Decision

The current repository demonstrates meaningful **technical progress**, especially a measurable and potentially tunable guest compression overhead and better logging. It also shows that the first cbuf allocation optimization is not a demonstrated win, and that the newer flush timing cannot be accepted as correct GPU completion. The reported best diagnostic frame period remains **~557ms**, with approximately **338ms unexplained outside recorded rendering stages**. Even eliminating all the timed compression work would not make this a 30 FPS frame.

A 30 FPS target is **not disproven**, because the diagnostic setup is not final gameplay and key thread/scene evidence is missing; however it is **not a reasonable current performance claim** on a ~1GiB handheld. Focus on the bounded P0/P1 experiments above. If the large residual is an incorrect guest scheduler/vblank/time contract, that is the highest-value fix. If it is unavoidable RAM and CPU cost for this Unity game, preserve renderer/safety correctness and document an honest lower-FPS experimental state rather than dropping GL fences, memory guards or save integrity.

**Execution note:** this 18.x reassessment documents current source/evidence and proposed experiments. It does not claim any new cross-build, handheld run, code fix, FPS improvement or GPU-synchronization validation performed during this review.


## 19. Current-head reassessment and detailed next steps (2026-10-20)

**Repository head examined:** [964ffe5](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/964ffe5a80f6631692b730dc5e4cdb992ecadb0f) on main, including the work after the §18 audit at 51707cd8. Current code and evidence inspected: README, runtime/lamentum-adapter.patch, port/Lamentum.sh, tools/analyze_perf.py, tools/perf_sample.py, tools/newgame_probe.py, tools/newgame_start.py, tools/tap_sweep_probe.py, tools/test_input_latch.c, docs/fps-baseline-2026-10-20.md, docs/newgame-bringup.md, docs/hid-input-contract.md, and the committed perf distribution files. **This section supersedes older sections when they describe superseded implementations, estimates or TODOs.** No new cross-build or handheld test was performed as part of this reassessment.

**Status remains NOT PLAYABLE.** Build202 demonstrated a correct menu, slots, Options and evdev navigation. Since then the diagnostic infrastructure has improved, but a verifiable New Game gameplay scene, audible output, cold save/reload and real gameplay frame times are still unproven. A TIME_LIMIT, successful device-control injection, or captured image file is not equivalent to playable gameplay.

### 19.1. Delta since the original roadmap: what is complete, partial or a negative result

| Item | Current evidence and implementation | Classification and next action |
|---|---|---|
| UI shader c4 -> UBO1 mapping | Build202 menu, documented real KMS and control-action receipts | **DONE** for current menu only; preserve all verified shader/texture invariants |
| New Game harness and menu-ready event | tools/newgame_start.py and newgame-02/03/04 in docs/newgame-bringup.md | **PARTIAL.** Newgame-03 highlighted Load game, never gameplay. Newgame-04 aborted because MainUI was not yet ready. Newgame-05 is described as in flight without a published completed result |
| Input button latch | native/lc2_input_latch.h, LC2_INPUT_LATCH opt-in, seven host checks | **IMPLEMENTED, NOT DEVICE-QUALIFIED**. A physical press can still be lost/repeated; test actual guest edge semantics |
| Per-frame distribution parser | tools/analyze_perf.py and perf-distribution.json files | **IMPLEMENTED, NEEDS REPAIR**. No phase proof; first sub-1000ms frame is not a valid warm-up boundary |
| Per-thread CPU observer | tools/perf_sample.py, updated by commit 2774d27 | **PARTIAL FIX**. Divides thread CPU ticks by SC_CLK_TCK but obtains the value from the workstation, not directly from the handheld; PID identity and frame tail sampling remain unreliable |
| Native gap instrumentation | current adapter records present_end_ns -> next queue submit and reports gap-ms | **DONE as a wall-time bucket**. Still not attributed to actual IL2CPP CPU versus scheduler, SVC, mutex, paging or I/O |
| Guest-ZRAM compression/restore counters | native/t2_guest_memory.h and reported cold10/cold250 experiment | **PROMISING, NOT ACCEPTED**. Existing cpu-compress-ms/cpu-restore-ms use CLOCK_MONOTONIC: they measure code-path elapsed time, not confirmed executing CPU |
| Cbuf glTexSubImage2D | native/nvn_render.h, LC2_CBUF_SUBIMAGE defaults ON | **DONE, NO DEMONSTRATED WIN**. Do not implement C1 again; compare the same ELF with flag 0/1 only if profiling justifies it |
| MOMO_SUBMIT_FINISH=0 glFlush | perf-flush diagnostic arm | **NOT A SAFE OPTIMIZATION**. A faster submit is not completed GPU work; retain glFinish or implement correct fences with lifetime tracking |
| ZERO_RENDER_SCALE=2 | docs/fps-baseline-2026-10-20.md | **TRIED, NOT USEFUL** in the measured title/menu arm: period 579.3 -> 577.7ms; do not repeat as the next experiment |
| Actual gameplay, RAM safety and 30 FPS | README, current launcher defaults and evidence | **NOT ESTABLISHED**. Default launcher remains synchronous and uses a 96MiB memory floor; 32MiB is a diagnostic memory envelope |

**Important correction:** docs/newgame-bringup.md attributes newgame-03's apparently failed A press to a 600ms tap shorter than a frame. That conclusion is not justified: tools/newgame_start.py still sends Linux EV_KEY **304** while naming it confirm-a, and evidence/ui-cbuf-fixed-01/control-actions.json explicitly proves **304 = Back**, **305 = Confirm** on this controller mapping. Sending Back alone explains the non-transition. The Up overshoot (Options -> Load game with one 600ms hold) may be menu key-repeat, latch timing or navigation state; this test does NOT establish that both symptoms had one sampling root cause.

**Published performance evidence limitation:** the new perf directories contain summary distributions but not the raw 250–500-frame logs, complete effective env, installed ELF hash, temperatures or actual-scene screenshots. Thus the exact window comparisons described below are **author-reported observations**, not independently reconstructable same-build one-variable A/B tests. Do not promote any experimental toggle solely from these results.

### 19.2. New highest-priority finding: guest gap and NVN replay are BOTH large

The averaged 60-frame build209 example now reports:

~~~text
NVN_PROFILE frame=601 count=60
elapsed-ms=572.700 replay-ms=249.626
present-ms=4.725 readback-ms=2.689 gap-ms=316.431
~~~

This means the interval from **the end of a Present until the next NVN QueueSubmit** is now visible. This **gap is wall time**; it may include guest computation, host translation callbacks, page-fault/guest-ZRAM restore, blocking I/O, thread scheduling, synchronization and intentional sleeps. The reported ~78% core utilization of one thread and ~19% of another does not prove that all 316ms were pure game computation. Likewise, replay includes GL driver time and potentially GPU waits, not only host CPU instructions. Averaged phase numbers must not be combined with medians of different data sets.

**Order-of-magnitude problem:** even if the ~250ms replay were completely eliminated, ~316ms remains; eliminating only the ~316ms gap leaves replay above 200ms. Hitting stable 30 FPS requires complete frame time <=33.33ms, plus correctness, not just quicker glFlush calls. At this stage fix the **owner of actual elapsed time**, not isolated low-impact graphics calls.

**Updated priority:** P0-NG (gameplay gate) -> P0-MEASURE (trustworthy identity and phases) -> P0-GAP + P1-REPLAY (two separate profilers) -> one measured high-impact optimization -> P1-ZRAM qualification -> validated GPU completion -> gameplay graphics quality, only if GPU-bound.

### 19.3. P0-NG: fix New Game selection, event identity and input semantics

**Files to change:** tools/newgame_start.py, tools/newgame_probe.py, tools/tap_sweep_probe.py, and a new shared pad-contract module and host tests.

1. **Correct Confirm now:** replace press(1,304,1,...) for the named Confirm action with EV_KEY **305**. Reserve 304 for Back. Document EV_ABS 17 for vertical hat movement. Use named constants in a single shared module; validate the chosen device by its measured TRIMUI Player1 name, GUID and event capabilities instead of assuming /dev/input/event4 always means the same pad.
2. **Host regression test:** read the existing control-actions.json fixture, assert Confirm=305 and Back=304, and check that both new-game scripts use the same constants. Add a deliberately swapped-keys negative fixture to prove the test detects a regression. A passing injection subprocess must not set confirmed=true: confirmation requires an observed guest menu transition.
3. **Stop blind selection:** one 600ms Up moved two entries in newgame-03. Use a short single press/release, enable LC2_INPUT_LATCH=1 in a separate controlled input test, and capture/inspect the selected item after **each** action. Verify the default highlighted item at runtime; do not assume it is always Options. Do not send Confirm until New Game is actually highlighted.
4. **Measure latch edge semantics:** LC2_INPUT_LATCH_CEIL_MS is 900ms, with the adaptive interval derived from presentation counts rather than actual guest Npad read timing. Compare tap lengths 100–150ms and a separately repeat-safe long hold with latch OFF/ON; record real press/release timestamps, guest read sequence and menu selection counts. A long artificial hold can cause key repeat; an adaptive latch may prolong repeats. Demand **exactly one selected item per intended tap**, plus no stuck button or duplicate action.
5. **Reliable readiness gate:** the current newgame_start.py polls the last 4000 log bytes plus repeated grep -c over the entire file. Replace with inode/offset incremental parsing and accept the **specific** ManagerMenuPrincipal menu-ready event, not any LC2_MENU_EVENT line or stale count from an older process. Confirm actual menu rendering with a live KMS screenshot. Distinguish startup/title, slot list and Options.
6. **State machine:** BOOT -> LIVE_MENU -> NEW_GAME_HIGHLIGHTED -> CONFIRM_305_SENT -> GAME_LOADING -> CONTROLLABLE_GAMEPLAY; add explicit FAILED states for bad highlight, title still loading, wrong screen, missing game PID or no new frame after the press. Store per-state monotonic timestamps, input-receipt code, frame serial, screenshot SHA-256 and expected menu event.
7. **Process ownership and screenshots:** obtain the launched PID/starttime from principal flow and check that exact process exists before every kmsgrab; track which DRM plane/window is active. An image of Spruce MainUI, slots or Options is not gameplay proof. Label screenshots by actual phase instead of naming every later sample gameplay-XX.
8. **New shader or load blocker:** if New Game encounters ZERO_SHADER_NOT_PINNED, capture exact code/control identity, shader pair, cbuf/sampler metadata and append only using tools/append_program.py. Preserve the build202 c4->UBO1 correctness contract. Check whether any of seven TEST substitutes is used after scene transition.
9. **Scene and saves acceptance:** verify directional movement, item interaction, inventory, dialogues, correct pixels in dark/highlight scenes and **audible** sound. Back up owner saves before testing; then save -> exit -> cold relaunch -> load and compare game state. Assert MainUI return and original CPU online mask after every failure.

**Short, staged smoke sequence:** first prove 305 opens the already known Options screen; separately prove one navigation step from Options to New Game; then 305 enters New Game; only then run a long scene-capture probe. Repeating entire 10-minute launches without validating earlier stages is low-value.

**Tests to add:** tools/test_lamentum_pad_contract.py for button mapping, tools/test_newgame_fsm.py for failed transition and PID recycling, and a host test for input-latch short-tap, repeated-hold and release behavior. The current tools/test_input_latch.c checks seven logic scenarios, **not** full guest-input behavior.

### 19.4. P0-MEASURE: make frame/CPU evidence reproducible before any further tuning

**Observed source defects:** tools/perf_sample.py reads the controller's os.sysconf(SC_CLK_TCK) rather than the device's value; selects first matching process name without starttime; scans tail -c 3000 for frames. tools/analyze_perf.py identifies warm-up by first period <1000ms, clamps signed unattributed residuals to zero, and does not verify that slow-frame logging covers every presented frame. These defects matter more than a claimed 3% speedup.

1. **PID/starttime identity:** principal harness should save target PID plus /proc/PID/stat starttime and installed ELF SHA-256. Each sampler poll must verify both. Parse /proc/PID/stat by locating the closing parenthesis around comm before parsing fields; do not use blind string splitting where process names may contain whitespace. Reject reused PID and TIDs rather than combining their counters.
2. **Target CPU tick units:** return target os.sysconf(SC_CLK_TCK) from the remote Python sampler; compute CPU ms/s as 1000*delta_ticks/(dt_seconds*target_hz), and CPU percent as 100*delta_ticks/(dt_seconds*target_hz). Test synthetic target HZ=100 and 250 independently of workstation HZ. Keep raw tick values for audit.
3. **All threads:** retain per-TID utime/stime, minflt/majflt, state, wchan, schedstat run/runnable-wait nanoseconds and voluntary/nonvoluntary context switches. Do not discard all except top six. At low frequency also record MemAvailable, CmaFree (if exposed), process RSS/PSS/SwapPSS, vmstat page/swap deltas, CPU frequencies, thermal zones and current CPU online mask. Missing counters are NA, not 0.
4. **Serials and clock alignment:** poll a monotonic frame serial/incremental log cursor rather than the trailing bytes of a high-volume log. Detect logfile replacement, missed serials, SSH polling delay, PID rollover and clock-domain offset. Derive throughput from actual presented frames over a known steady-state interval; do not divide a menu+loading run by the whole probe budget.
5. **Correct parser:** replace first-sub-1000ms after_warmup with an explicit phase from actual title/gameplay/scene checkpoints; report signed residual and count negative/overlapping samples, rather than max(0, residual). Add synthetic tests for duplicate frames, skipped indices, missing stages, out-of-order frames, negative residuals and slow-only sampling bias.
6. **Evidence completeness:** publish exact effective env, adapter patch/source hashes, owner image hash **without proprietary contents**, installed ELF SHA, baseline/shader hash, first/last frame, scene, raw complete log (or private immutable reference with SHA and public per-frame derived CSV), cleanup receipts, P50/P95/P99, stops and lowest RAM headroom. Only claim a same-ELF 0/1 test when both logged executable SHA values really match.
7. **Instrumentation overhead:** prefer bounded fixed-size ring buffers and one summary per 60–120 frames. Alternate profiler OFF/ON with the **same executable** to quantify <=5% timing overhead before trusting new substage results.

**Existing parser command once raw owner logs are available:**

~~~sh
python3 tools/analyze_perf.py /owner/local/perf-quiet-b202/latest.log \
  --from-frame 250 --to-frame 500 --json /owner/local/quiet250-500.json
python3 tools/analyze_perf.py /owner/local/perf-gz-cold250/latest.log \
  --from-frame 250 --to-frame 500 --json /owner/local/cold250-500.json
~~~

These reproduce a frame-index window only; they do **not** by themselves establish same scene, same ELF or same temperature. PASS: a second reviewer can independently regenerate reported quantiles and verify exact device/process/phase identity.

### 19.5. P0-GAP: classify the measured ~316ms Present-to-Submit interval

**Specific implementation locations:** current runtime patch changes native/nvn_present.h (present_end_ns) and native/nvn_replay.h (gap_ns from end-of-present to next NI_nvnQueueSubmitCommands). This is a good initial time boundary, but a shared timestamp is not automatically valid for multiple queues, overlapping submits or present-less command lists. Measure and reject unmatched serials.

1. Add an **opt-in LC2_GAP_TRACE=1** with per-queue/host-TID/guest-TID present and submit serials, CLOCK_MONOTONIC_RAW timestamps, matching status and a bounded 4096-entry ring. Collect start/end for each matched present->next-submit interval and track missing, overlapping and unpaired events. Batch output at phase end, not per SVC.
2. For each matching interval collect CLOCK_THREAD_CPUTIME_ID on the executing thread, runnable delay from /proc/TID/schedstat, context switches, and aggregate wall spans for guest SVC calls. A guest IL2CPP thread running, a thread runnable but unscheduled, and a thread blocked are **different hypotheses**; CPU times on separate cores can overlap and cannot be added to wall time.
3. Bucket the guest events: WaitSynchronization, SleepThread, WaitProcessWideKey/WaitForAddress, mutex acquisition/owner, guest page fault/restore, ZRAM lock, fileback pread, texture creation, IPC, and command-buffer construction. Use call counts, exclusive wall and thread CPU ns, longest stalls and associated guest callsite PC.
4. If guest CPU actually dominates, use **bounded owner-local guest-PC sampling** referenced to SHA-pinned main/subsdk/sdk offsets; rank IL2CPP PlayerLoop, render preparation, asset lifecycle, allocator, SDK synchronization and calls into host services. Check kernel perf_event support first; if unavailable use low-overhead bounded sampling. Do not use repeated stop-the-world GDB breakpoints as a performance measurement.
5. If actual page restoration dominates, correlate page/block ID with compressor cold deadline and repeatedly restored hot pages; hand off to §19.6. If a long Horizon sleep dominates, determine **requested vs actual** duration, refresh/vblank contract, owner thread and time source before altering it. Never bypass guest synchronization speculatively.
6. If runnable starvation dominates, measure CPU0 frequency/topology/thermal state and affinity, then test one identified available core or scheduler-managed placement under strict launcher CPU-state rollback. If an SDK/IPC callback dominates, profile its exact ABI, copy sizes, locks and resource ownership; remove **only provably redundant** work and keep functional equivalence.
7. If the interval is real Unity simulation/animation/physics time, do not silently skip Update/FixedUpdate, time scaling or game logic. A less expensive graphics preset may help the GPU, but cannot be assumed to reduce 300ms of guest CPU.
8. Report P50/P95 of matched gap wall, matching executing-thread CPU, runnable delay, blocked wait, page fault/restore, synchronous I/O, SDK callback and signed leftover; account for >=95% of wall time without double counting. Compare an identical-code profiling-OFF run.

PASS: name the **actual top 3 guest PCs/SVC/locks/fault causes**, with ms/frame and frequency, before proposing a guest-CPU optimization. **High utilization alone is insufficient attribution.**

### 19.6. P1-ZRAM: safely replicate, instrument and potentially improve the cold250 finding

The baseline document reports cold10 -> cold250 at frame indices 250–500: period P50 **629.0 -> 579.3ms**, replay **297.7 -> 240.8ms**, compressions per frame **566 -> 248**, and compression/restore elapsed path durations per frame **138 -> 59ms**. It is a useful hypothesis, not a certified benchmark. CLOCK_MONOTONIC duration is **not** executing-thread CPU time.

**One-variable matrix, with identical executable/scene/BC policy/GPU budget/memory floor:**

| Arm | Exact variable | Purpose |
|---|---|---|
| Z0 | T2_GZRAM_COLD_MS=10 | Verified control |
| Z1 | T2_GZRAM_COLD_MS=100 | Less aggressive reclamation |
| Z2 | T2_GZRAM_COLD_MS=250 | Replicate the promising arm |
| Z3 | T2_GZRAM_COLD_MS=500 | Check tail latency and increased residency |
| Z4 | T2_GZRAM_PERIOD_MS=50, separately 100 | Test scanner scheduling |
| Z5 | T2_GZRAM_BUDGET_MIB=16, separately 8 | Reduce compressor burst/lock contention |
| Z6 | New opt-in adaptive per-block cooldown | Only if hot-block thrash is measured |

1. Read cumulative T2_GZRAM counters **at both phase boundaries** and divide deltas by actually presented frames. Track compress, restores, faults, scans, live/stored bytes, resident growth, MemAvailable minimum, SwapPSS, kernel swap traffic, CmaFree and time spent stalled in page faults.
2. Add actual CLOCK_THREAD_CPUTIME_ID for the dedicated compressor thread and separate CPU/wall spans for synchronous restores in the faulting thread. Split codec, lock wait/hold, scan, memcpy, mprotect, madvise and pread paths. Ensure instrumentation does not introduce races or new lock contention.
3. Maintain a bounded anonymized hot-block histogram: compression->next restore time, restore count per block, repeated cycles within 10/50/250ms, memory saved and recently reused guest allocations. Avoid logging guest bytes. Inspect the existing exponential restore cooldown before changing it.
4. Run Z0/Z2/Z0/Z2 followed by Z1/Z3 and three matched candidate/control pairs; measure **P95/P99** as well as P50 under the same phase. If a more lenient cold threshold raises RSS, swap traffic, scene transition stalls or OOM risk, reject even if the median improves.
5. Only if hot-page churn is verified implement adaptive per-block cooldown with bounded lifetime/generation and memory-pressure hysteresis. Never compress IO-pinned pages, discard alias backing, disable guest ZRAM globally or remove the 420MiB texture cap without a complete correctness and memory proof.
6. The historical 32MiB floor is **diagnostic only**. Production qualification requires a separately safe floor, real New Game transitions, save/reload, thermal settling and no kernel OOM. Preserve known-good launch flags and binary for immediate rollback.

PASS: three matched pairs show safe **full-frame P95** gains or substantial demonstrable reduction in guest-CPU contention without higher resource pressure. Otherwise retain the known safe setting and mark ZRAM tuning rejected.

### 19.7. P1-REPLAY: identify the actual ~250ms NVN/GL cost before refactoring

The observed ~249.6ms replay wall time is not evidence that the UI's 27 profiled draws are intrinsically expensive, nor that all replay wall time is CPU work. Build an **exclusive per-NVN-operation** profile.

1. For each queue submit, aggregate counts, wall ns and CLOCK_THREAD_CPUTIME_ID ns for command parsing, command-memory callback, sampler-handle resolution, shader-program lookup/compile/link, zero_texture_refresh and BC decode/upload, FBO bind/target switch, vertex/index conversion/upload, GL state calls, cbuf staging/memcpy/upload, glDraw submission, eglMakeCurrent, glFinish/fence waits and pixel readback. Mark GPU waits separately from actual CPU execution.
2. Group cost by (program pair, render target, resource generation, command type), not just pair. Print a bounded 60-frame summary rather than tracing every draw. Correlate the highest three exclusive costs with complete period P95; an optimization in a low-cost bucket cannot reach 30 FPS.
3. **Cbuf C1 already exists** and defaults ON. If cbuf is hot, investigate a full **1024x1 RGBA32F row (~16KiB)** being uploaded for 16–368 bytes of useful data: read shader maximum accessed texel index/coordinate transformation before attempting compact dimensions; otherwise keep the original layout. Use exact-byte no-change detection keyed by GL texture generation, program/slot and guest write epoch, never hash-only equality. Respect in-flight readers.
4. If repeated descriptor resolution dominates, test a cache keyed by guest pool generation, handle, sampler, view format and write epoch; invalidate on pool reuse/TextureWriteTexels/aliasing/context recreation. If repeated vertex conversion dominates, test scratch/VBO reuse only with write-generation and fence guarantees.
5. If FBO/GL state thrash dominates, test per-EGL-context state shadowing with explicit invalidation by presentation and debug helpers. Do not merge UI draws unless target, alpha, depth/stencil, textures, UBO and ordering are identical.
6. If the real culprit is fileback/page fault or a GPU completion stall, fix the relevant ownership or memory behavior rather than adding a superficial GL cache. A faster local glTexSubImage2D call that merely defers completion into glFinish is not a frame-time win.
7. For each candidate: unit test generation/invalidation semantics, compare real physical KMS colors/text/stencil, check no zero-shader stop, measure whole-frame P50/P95/P99 with the same ELF, and monitor guest-ZRAM side effects.

**PR gate:** name and measure one dominant exclusive operation; optimize **only that operation** behind a default-OFF flag; promote only after matched full-frame improvements.

### 19.8. P1-SYNC and P1-READBACK: do not confuse fewer waits with correct presentation

MOMO_SUBMIT_FINISH=0 substitutes glFlush for per-submit glFinish. Published frame-250–500 medians changed from **579.3 to 557.1ms**, but glFlush does not establish GPU completion. Existing history contains NVN_COMMAND_REUSE_BEFORE_COMPLETION, so flush-only cannot be accepted as safe shipping behavior.

1. Enumerate command-list generations, actual GPU readers of vertex/cbuf/texture/FBO resources, submit/context ownership, earliest legal reuse and SDL/KMSDRM surface recreation. Use a bounded serial ledger and an invariant that an in-flight generation cannot be mutated or destroyed.
2. After verifying GLES3 support, use glFenceSync/glFlush and glClientWaitSync/glWaitSync under the correct EGL context with failure/timeouts handled fail-closed. Prove that every buffer and command arena is recycled **after** its last consumer, not after the CPU submitted work. Synthetic tests must cover delayed GPU completion and context loss.
3. Only then compare strictly finished submission against a correct fence-backed pipeline, in real game scenes. Keep COTM_ASYNC_QUEUE=0 and T2_GPU_PIPELINE=0 as defaults until proof. A faster diagnostic flush-only output is not an accepted speedup.
4. Quiet distributions still show readback-ms P50 around 2.3–2.4ms. Trace whether this is part of the required presentation, a pixel proof, or optional glReadPixels diagnostic; disable only optional sampling after same-screen physical KMS comparison and strict GL-error testing. Never remove the actual panel-copy path on an assumption.
5. Measure whole-period P95/P99, fence age, in-flight resource count, black frames, GPU stalls, input/audio latency, save/scene transitions and correct cleanup. Any EGL_BAD_SURFACE, stale uniform, deadlock or command reuse is immediate rollback.

### 19.9. P2-QUALITY: deprioritize the failed generic 720p trial

The baseline reports a controlled diagnostic **ZERO_RENDER_SCALE=2** arm, mapping logical 1920x1080 windows to 640x360 storage while keeping 1280x720 output. The period changed only **579.3 -> 577.7ms** and the guest gap remained near 312–330ms. Do not spend the next iteration repeating that generic backend scaling strategy.

1. Once gameplay is reached, separately identify whether CPU driver work, actual GPU shader time or guest simulation dominates. Use supported GLES timer queries (checking disjoint state) or Mali tools where available; report unsupported query counters as unavailable.
2. If GPU-bound, map actual game-side 1920x1080 render-target owners, consumers, viewport/projection and UI CanvasScaler. A title-specific guarded 720p internal setting may help in **a different gameplay scene**, but must be proven rather than copied from West of Loathing.
3. Time the measured 17/4 bloom pyramid and composite before dropping downsample levels/taps; preserve alpha, lighting, shader literal banks, texture data and intermediate render-pass dependencies. Keep original quality as a verified fallback.
4. Investigate BC3 atlas residency, partial dirty-region uploads or content-addressed ASTC side caches **only** when measurements show repeated texture decode/upload or large memory stalls. Check actual Mali GLES compressed format support and never redistribute original assets.
5. If guest CPU dominates, changing raster dimensions is unlikely to remove 300ms of CPU time. Focus on verified hot SDK IPC/guest-PC/allocator/page-restoration paths first. Compiler/affinity experiments require CPU-clock/topology/thermal measurements and full launch-state restoration.

### 19.10. Recommended PR execution order and stop rules

| Order | Proposed PR | Specific deliverable and tests | Gate |
|---|---|---|---|
| **1 P0** | fix/newgame-pad-contract | Use 305 Confirm, 304 Back; shared constants, host mapping regression, one-tap visual selection and state machine; owned screenshots | New Game highlight and accepted transition or precise blocker |
| **2 P0** | feat/precise-gap-profile | Target-HZ CPU ticks, owned PID/starttime, actual per-thread schedstat, per-queue present-submit serials, signed parser, stage/scene proof | >=95% gap wall attribution and profiler overhead <=5% |
| **3 P1** | perf/gzram-cold-matrix | Z0/100/250/500 one-variable repeated A/B plus real CPU/fault/memory headroom | Full-frame P95 improves without memory regression |
| **4 P1** | feat/nvn-exclusive-profiler | Per-command/replay exclusive CPU, wall and sync buckets, top program/resource pairs | >=95% replay stage attribution |
| **5 P1** | perf/one-proven-hotspot | Exactly one costly CPU/GL/cbuf/IPC/memory improvement with correctness tests | Three matched same-scene A/B pairs and meaningful P95 gains |
| **6 Conditional** | feat/serial-fence-ownership | GLES fence ownership, delayed completion and context-recreation tests | Zero command reuse or black/UI failure; no flush-only default |
| **7 Conditional** | perf/verified-quality-preset | Owner-specific resolution/effects option only if real scene is GPU-bound | KMS quality + P95 improvement; reversible |
| **8 Final** | docs/gameplay-acceptance | CPU/GPU frame profile, exact hashes, RAM/thermal/swap and save/audio/cleanup receipts | Three >=60s genuine gameplay runs, frame P95 <=33.33ms |

**Never combine cold250, flush, cbuf and render-scale flags to produce a single headline number.** For every A/B: identical ELF and scene/clock/thermal/memory configuration, one changed flag, measured control and three independent repeats. Stop on visual mismatch, GPU fence/reuse errors, memory-floor refusal, swap storms, save corruption, orphan runtime or MainUI/CPU restore failure.

### 19.11. Feasibility and status reporting

The current median diagnostic frame period is still measured in **hundreds of milliseconds**; no reliable gameplay 30 FPS number exists. The goal is not mathematically disproved, because current runs are mostly menu/loading, and the guest gap and replay still contain unresolved virtualization/driver costs. But a straightforward 720p toggle, the already implemented cbuf subimage or unsafe glFlush **cannot plausibly close the observed gap on their own**.

The most valuable next evidence is a **named CPU/guest call path inside the 316ms gap** and a **named GL/driver operation inside the 250ms replay**, measured against the same scene and build. If those costs can be reduced equivalently, pursue them. If the hot paths prove intrinsic Unity/IL2CPP/SoC compute cost and cannot be reduced without breaking gameplay, keep renderer, memory and synchronization correctness and document an honest lower-FPS target rather than claiming 30 FPS.

**Scope of this revision:** documentation updated based on source and existing evidence. No native runtime patch, ELF deployment, SSH device probe, or new gameplay benchmark is claimed.


---

## 20. Head b1832de audit — historical snapshot (2026-10-20)

> **Historical; superseded by §21 at HEAD 2b6b2a1.** This is a source-and-evidence reassessment of main at commit [b1832de](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b1832dec48a64f9fcadc50a8010f1ce7910875e6), after the earlier §19 review. Keep §§0–19 as the historical audit trail; **use this section to choose the next implementation**. No new handheld run, build, benchmark, shader translation, or source-code fix is claimed in this document-only revision.

### 20.1. Executive decision: work done, unresolved issues and the real critical path

**New since the translated original roadmap:** 15 commits through b1832de. Source additions include tools/analyze_perf.py, tools/perf_sample.py, tools/test_input_latch.c, tools/newgame_start.py, tools/newgame_probe.py, tools/newgame_crash_repro.py, tools/analyze_newgame.py and related probes; native gap and guest-ZRAM timing, cbuf subimage support, input latching, multiple bench evidence summaries, and a first controlled New Game failure. See [fps baseline](fps-baseline-2026-10-20.md) and [New Game bring-up](newgame-bringup.md).

| Area | Proven by currently committed material | Still missing / verdict |
|---|---|---|
| Menu, UBO1/c4, SDL/KMSDRM, input receipt | Physical-screen menu and UI, build202 | **Working as a menu**, not gameplay. Never regress it |
| New Game | A run reached scene-load ROMFS reads, then stopped fail-closed on an exact new shader identity | **BLOCKED** on shader translation; no correctly rendered gameplay |
| Shader dump | Code 1280 B and control 2176 B, full matching hashes, captured owner-locally | **DONE**; do not repeat the dump unless its provenance is lost |
| Existing translator | ES 310, ES 300, and ES 310 --cbuf-ubo each reject the same incompatible buffer layout | **CONFIRMED BLOCKER**; repeating those flags is not a useful next trial |
| CPU/frame profiling | Per-60-frame gap versus replay accounting; basic per-thread observation | **PARTIAL**; no per-guest-PC/per-SVC, CPU-versus-blocked attribution |
| Compression | Cold10 -> cold250 observed period P50 629.0 -> 579.3 ms, compression/restore path time 138 -> 59 ms/frame | **PROMISING**, not a validated production choice; measured time is elapsed-path, not actual CPU |
| Cbuf subimage | Implemented, defaults enabled; no demonstrated improvement and source comparison has identity ambiguity | **NO PROVEN WIN**; stop treating C1 as an unimplemented task |
| Submission flush | Faster diagnostic arm, but no GPU completion guarantee | **DO NOT SHIP** flush-only |
| Generic render scale | ZERO_RENDER_SCALE=2: period P50 579.3 -> 577.7 ms in measured menu window | **NEGATIVE RESULT** for that scene; do not prioritize another blind rescale |
| Memory safety | New Game emits an order-4 kernel allocation-failure message during load | **SECONDARY PRESSURE WARNING**; shader stop is the confirmed immediate exit cause |
| 30 FPS | No verified gameplay scene or reliable game-frame P95 | **NOT ACHIEVED**; estimated improvement needed is an order of magnitude or more |

**Priority change versus §19:** the new **shader blocker is P0 before performance**. Run shader-layout work and reliable benchmark/harness repairs in parallel, then complete gameplay acceptance, instrument the two actual hot phases, and optimize the highest attributable costs. Do not burn the next iteration on cbuf subimage, flush-only, or generic render-scale variants.

**Recorded identity (owner-only blobs):**

~~~text
ZERO_SHADER_NOT_PINNED pc=main.text.seg+0x542b68
code bytes=1280
code SHA-256=7a45f946fe5f9130ad89877e0862164b805734d9b1739093e3099430ec1bbcb7
control bytes=2176
control SHA-256=588a3fad7306d848ce2f3d70e85d5608e7973f1c093d3bb62b940c52aa4419e1
GLSL error: Buffer block cannot be expressed as any of std430, std140,
            scalar, even with enhanced layouts
--cbuf-ubo report: CBUF_AS_UBO decorations-changed=0
~~~

The SPIRV-Cross diagnostic specifically recommends investigating block flattening; that **does not imply** that its flattening feature can handle this shader, an SSBO, writable data, dynamic indexing, or mixed types. Upstream implementation: [SPIRV-Cross GLSL backend](https://github.com/KhronosGroup/SPIRV-Cross/blob/main/spirv_glsl.cpp) and [reflection APIs](https://github.com/KhronosGroup/SPIRV-Cross/blob/main/spirv_cross.hpp). Distinguish diagnosis from a validated fix.

### 20.2. PR-01 (P0): fix input provenance and test ownership BEFORE replaying New Game

**Change:** tools/newgame_crash_repro.py, tools/newgame_start.py, tools/newgame_probe.py, tools/device_principal_test.py; add tools/lamentum_pad_contract.py and tests.

**Source-level inconsistency observed on b1832de:**

- evidence/ui-cbuf-fixed-01/control-actions.json explicitly records **Linux EV_KEY 304 = Back** and **305 = Confirm** on the captured event4 controller. Yet newgame_crash_repro.py still executes press(1,304,1,CONFIRM_MS,'accept-new-game'). newgame_start.py also uses raw evdev codes and assumes a different default menu highlight. The load/shader failure was captured, but this mismatch means **the precise user action and scene transition still require an independent receipt**. Do not overwrite real shader evidence or infer that 304 suddenly changed meaning.
- The fresh crash-repro tool documents the default highlight as **New game**; newgame_start.py assumes **Options** and sends an Up first. Treat both as hypotheses until correlated with an actual same-run screenshot and menu state.
- tools/device_principal_test.py currently returns 0 after printing game/MainUI/CPU state. It does **not** make game exit status, restored MainUI, restored online mask, or an observed stop code a hard test assertion. A green harness return value therefore cannot certify a clean run.

**Implementation checklist:**

1. Read the device input identity/capabilities from the active /dev/input/event* source before injection; store name, event path, EV_KEY/EV_ABS bits and tested SDL mapping. Create named constants CONFIRM=305, BACK=304, DPAD_VERTICAL=(EV_ABS,17). Resolve the actual path by identity, not by silently assuming event4 is stable.
2. Replace duplicated press() implementations with an owner-local helper that sends press + EV_SYN + release + EV_SYN and records monotonic wall timestamps, hold length, write return codes, and final release. **No held button may survive exceptions**. Validate the source device was present throughout the action.
3. At the start of each run, record binary SHA-256, run UUID, process PID/starttime, log inode, initial menu-highlight screenshot and frame serial. Use one confirmed observed default selection, not a remembered previous run.
4. Inject **305** into a known screen such as Options, compare before/after screenshots and a guest menu transition, then prove a one-step movement to New Game; only then inject Confirm on the visibly selected New Game item. Preserve the original, suspicious 304 run as evidence rather than deleting or rewriting it.
5. Compare LC2_INPUT_LATCH=0/1 with short taps and a single longer hold as separate arms. The host unit test's seven checks do not prove one edge per guest Npad sample. Capture actual guest reads, press/release edges, repeat counts and selected-item transitions. Avoid a 600–900ms synthetic hold that can move two menu entries.
6. For the crash tool, explicitly distinguish state **NEW_GAME_CONFIRMED**, **SCENE_LOAD_STARTED**, **FAIL_CLOSED_SHADER**, and **CONTROLLABLE_GAMEPLAY**. ROMFS reads + a new shader can establish a scene-load path; they **cannot alone** establish gameplay. A successful SSH subprocess is not a successful action.
7. Convert principal cleanup into a mandatory exit contract: after stopping the probe assert game PIDs absent, MainUI running with expected identity, principal flow restored, and original CPU online state exactly restored. Compare pre/post snapshots; distinguish a **game failure** from **harness failure**. Ensure early termination, timeout, exceptions, and signal handling cannot bypass cleanup or overwrite collected logs. Never kill arbitrary unrelated device processes as a workaround.
8. Use incremental logfile parsing by inode/offset and a run UUID; do not repeatedly scan multi-MiB log files or mistake stale menu events for current readiness. Annotate all physical captures with **target PID/starttime plus frame serial and live DRM-plane proof**.

**Host tests:** tools/test_lamentum_pad_contract.py (including fixture 304/305, swapped-button negative test, event path changes, release on exception); tools/test_principal_cleanup.py (failed MainUI, wrong CPU mask, process still running, timeout); tools/test_newgame_fsm.py (wrong highlight, stale menu log, PID reuse, new shader stop, post-confirm loading). Do not claim these tests exist until implemented.

**Gate:** identical-input receipts demonstrate a real New Game scene-load transition, or yield a defensible input failure distinct from the shader problem; all device runs leave the frontend and cores in their original state.

### 20.3. PR-02 (P0): solve the one blocked shader, not the entire rendering engine

**Local inputs already captured:** nvn-lc2-shader-code-1792497924-0.bin and nvn-lc2-shader-control-1792497924-0.bin. Both are proprietary owner data; **keep them outside Git**. This PR can be developed on the host before deploying to the handheld.

**Phase A — obtain a reproducible intermediate representation:**

1. Verify the two raw blob SHA-256 values in §20.1. Pin the exact Hades-lineage compiler commit, command-line parameters, SPIRV-Cross commit/build, stage and NVN control metadata. Preserve the existing failing commands as negative fixtures; do not claim a different output based only on changing ES 300 to 310.
2. Add an **owner-workspace-only diagnostic** mode to the translator (or its local fork) to emit *raw SPIR-V before SPIRV-Cross raises*, if that stage exists. Validate the module with spirv-val when applicable, inspect with spirv-dis and, if useful, a reflection tool. Never assume the CLI currently exposes a SPIR-V output flag.
3. Build a **buffer-access report** for the specific SPIR-V variable: Block/BufferBlock, Uniform/StorageBuffer storage class, DescriptorSet/Binding, Offset, ArrayStride, MatrixStride, RowMajor/ColMajor, member scalar/vector/matrix widths, runtime-array bounds, alignment, and whether it is read-only. Walk OpAccessChain/OpLoad/OpStore/atomic instructions and track static versus dynamic indexing and possible aliasing. Compare layout against the original NVN code/control metadata and the actual guest mapped allocation.
4. Emit a human-readable **first layout conflict**: which member/offset/stride fails std430/std140/scalar and whether the failure arose in Hades's SPIR-V IR generation or in SPIRV-Cross's GLES backend. This separates a translator defect from an unsupported GPU feature. Do **not** mechanically remove Offset or ArrayStride decorations: that can silently change memory interpretation.
5. Validate the program stage (SPH bits), varyings, color/depth write masks, cbuf/sampler slots, required precision and interface against the adjacent captured shader that pairs with it. An emitted GLSL file that compiles but links to the wrong vertex/fragment partner is not a fix.

**Phase B — test three options in increasing implementation cost:**

| Option | Only valid when | Work and acceptance |
|---|---|---|
| **B1: faithful layout lowering / SPIR-V normalization** | A semantically equivalent std430/std140/scalar representation can be constructed | Rewrite type/offset/stride and **all address calculations** while preserving bit-for-bit accesses; validate with SPIR-V verifier, reflection snapshots and memory fixtures. Merely changing a decoration is forbidden |
| **B2: flatten a compatible, finite read-only block** | Reflection proves block layout and access patterns can be flattened and SPIRV-Cross supports that resource/type | Try a translator API-level flatten transformation in a pinned experimental fork; confirm allowed scalar types, fixed size, aligned accesses and uniform limits. A generic flattening flag is **not proof** it handles SSBOs or mixed/writable blocks |
| **B3: texture-backed raw-buffer emulation** | All reads/writes and integer/float bitcasts can be faithfully implemented, or proven no writes occur | Lower buffer loads to indexed texelFetch from a carefully typed integer/float texture; handle byte/word addressing, bounds, dynamic indexing, sign extension, half precision, stride and exact bit reinterpretation. Maintain an NVN descriptor-to-GL texture binding with correct update epochs, not one texture allocated/uploaded every draw |

**Texture-backed buffer specifics (for B3):**

- Prefer raw 32-bit lanes and explicit unpack/bitcast operations when the source data requires integer semantics. A float RGBA32F conversion is **not automatically bit-preserving** for all integer, half or packed fields. Select RGBA32UI or another actually supported GLES texture representation only after verifying both device capabilities and shader access requirements.
- Determine exact NVN bound-buffer base/size, guest write generation, alignment, element stride and accessible range. Map NVN binding and hardware-bank +3 provenance from the title's control metadata; do not attach the buffer to an arbitrary free texture unit or collide with the existing cbuf emulation unit reservation.
- Fail closed on atomic operations, shader writes, buffer-to-buffer aliasing, unknown write epochs, out-of-bounds accesses, runtime-dependent buffer size that cannot be safely reflected, or SSBO features not represented by the chosen GLES backend. For writable blocks, texture-fetch **alone is not equivalent** and may require an image/SSBO-capable path with valid ordering and barriers.
- Upload only changed, page-aligned or verified dirty ranges after correct guest writes. Cache by descriptor resource generation + content modification epoch; invalidate on pool replacement, context loss and aliasing. Keep a strict original path and a default-OFF feature flag for the experimental lowering.
- Add a tiny, self-authored buffer fixture exercising relevant offsets/strides, unaligned and dynamic element selection when applicable, negative integers, NaN payloads, and out-of-bounds handling. Compare expected values with actual GLES3 output on the board. Test the shader link/active uniforms and KMS scene pixels separately.

**Phase C — integrate safely:**

1. Use tools/append_program.py **only after** the GLSL, metadata and live bindings are correct. It is append-only by design; never regenerate runtime/lamentum-shaders-draft.h. Ensure the exact **code and control hashes** and stage match the captured pair; do not match by code hash alone if the catalogue's actual identity contract requires both.
2. Cross-build against the 435-file manifest-pinned recovered source tree; confirm c4 -> UBO1 UI screenshots and seven existing TEST entries are byte-for-byte preserved unless deliberately improved.
3. Re-run the proven same-run input -> New Game -> scene-load path. If another shader stops, record its **new** identity, triage layout and repeat. A generic TEST substitution may be used only in an explicitly named **exploratory** branch to enumerate the next blocker, with screenshots labeled non-authoritative; it must never count as correct gameplay, visual parity or release readiness.
4. Verify sprites/geometry, alpha, stencil/depth, animation, camera, menu, input and visible source texture against real screen captures. Add a regression fixture for this shader so later catalogue changes do not reintroduce its layout fault.

**Gate:** an exact-identity valid shader produces demonstrably correct on-device pixels and the title advances past this stop. If the block is writable or requires unsupported GPU functionality, explicitly report that **a larger backend feature** is needed; do not ship a TEST stub as a workaround.

### 20.4. PR-03 (P0): repair measurement validity; the current tools still contain concrete bugs

**Files:** tools/perf_sample.py, tools/analyze_perf.py, tools/device_principal_test.py; new tools/test_perf_sample.py, tools/test_analyze_perf.py and tools/perf_capture_protocol.py as appropriate.

1. **Proc parsing:** tools/perf_sample.py currently does stat.split() for /proc/PID/stat and TID/stat; correctly parse the PID and parenthesized comm first. Collect **PID starttime (field 22)** and TID starttime; permit repeated samples only for the same identities. A process with the same name is not necessarily the same instance, and a vanished thread must not produce a negative CPU delta.
2. **Tick frequency:** the current sampler computes remote CPU counters with the **controller/workstation os.sysconf('SC_CLK_TCK')**. Obtain target HZ **on the device** as part of every sample session, persist it in evidence and use it for all remote tick conversions; tests for HZ=100 and HZ=250 must pass independently of host HZ.
3. **Thread observability:** retain all threads, not just top six. Collect utime/stime, /proc/TID/schedstat running and runnable-wait nanoseconds, /proc/TID/wchan, voluntary/nonvoluntary switches, minflt/majflt, process smaps_rollup at low rate, /proc/vmstat and /proc/meminfo MemAvailable/CmaFree, CPU frequency, temperature and online mask. Missing data must be NA and permissions/errors recorded, never silently replaced by zero.
4. **Frame serial and phase:** do not infer the current game frame from tail -c 3000 or title readiness from first period <1000ms. Emit monotonically increasing serials and explicit menu/loading/gameplay/scene-transition phase markers; check skipped/duplicate frame IDs, log truncation, and clock-domain differences. Distinguish **submitted**, **rendered**, **swap completed**, and **observed scanout** events, and do not use one as an undocumented alias for another.
5. **Parser correctness:** tools/analyze_perf.py currently sorts all slow-frame records and computes max(0,period - stages). Preserve source-order checks, detect duplicates, report **signed residuals**, negative/overlap counts and completeness; log-only slow frames may be a biased sample, so establish the actual number of presented frames before computing distribution or throughput. Eliminate heuristics for automatic warmup from release reports.
6. **Clock and resource attribution:** record CLOCK_MONOTONIC_RAW wall time and CLOCK_THREAD_CPUTIME_ID CPU time separately at the same stage entry/exit. For a measured 250–500 window, publish raw per-frame rows plus cumulative GZRAM deltas, not only percentile JSON; preserve sample sizes, P50/P90/P95/P99 and timestamps.
7. **Correct harness success condition:** do not return success solely because the SSH command ran. Persist main PID, actual stop reason, process exit status, before/after CPU mask, MainUI cleanup, exact ELF SHA, owner image identity and effective environment. Distinguish expected fail-closed shader stop from OOM/kernel fault/timeout/launcher failure and never erase a crash capture on harness termination.
8. **Benchmark protocol:** three separate paired runs with the same ELF/scene and one changed toggle, preferably alternating A/B order. Keep flags affecting timing (AW_RELEASE, LC2_MENU_TRACE, pixel probes, readback) identical across arms. In the pre-gameplay phase call it a **menu or scene-load benchmark**, not game FPS. Run low-overhead profiler ON/OFF to estimate its own cost.

**Host test matrix:** fabricated /proc names containing spaces and close parentheses; TID creation/destruction; PID reuse; missing smaps; target-HZ mismatch; negative counter delta; logfile inode rotation; duplicate/out-of-order frame serial; incomplete slow-frame records; negative wall residual; expected and unexpected STOP status; MainUI not restored. Run against fixtures without device access before relying on numbers.

**Gate:** a third party can reconstruct an A/B result from the committed derived CSV, exact hashes, environment, phase identity and raw private owner log hash. No release performance claim uses unvalidated parser defaults.

### 20.5. PR-04 (P1): split the two dominant elapsed phases into actionable costs

**Measurement anchor:** build209 NVN_PROFILE frame=601 count=60 reports **elapsed 572.700, replay 249.626, present 4.725, readback 2.689, gap 316.431 ms/frame**. These are averages over the same 60-frame window and have minor boundary/overlap differences; **not** a proof that every frame has a 316ms guest computation cost. The new New Game failure reports a frame ~152.8 ms immediately before a shader stop, illustrating that menu, scene-load and gameplay paths can differ radically.

**A. Present -> next QueueSubmit (native/nvn_present.h + native/nvn_replay.h + guest/SVC dispatch):**

1. Replace the single global present_end_ns relationship with **per-queue, serial-correlated** events: present serial, queue submit serial, OS TID, guest thread/context ID, timestamps, overlap/missing/abandoned count. Explicitly handle submits without presents and multiple command lists/queues. Use a bounded nonblocking trace buffer, disabled by default.
2. Instrument inclusive wall, executing-thread CPU, runnable delay and blocked wait for each matched gap. Classify SVC SleepThread, WaitSynchronization, IPC, OS mutex, page faults, ZRAM restore, fileback reads, Unity main/IL2CPP work and NVN command-record construction. Count nested subspans **once** via an exclusive stack; check phase residual (>=95% explained).
3. Extract guest PC samples from a SHA-pinned owner-local main/subsdk/sdk map, associate them with guest CPU hot ranges and call sites. First check low-overhead sampling support on the actual kernel; choose carefully bounded in-process samples only if perf is unavailable. Do not run thousands of synchronous debugger breakpoints on the render thread.
4. **Decision tree:** if faults/restore dominate, optimize §20.6; if page-protection/lock contention dominates, fix ZRAM locking/lifetime; if an IPC/SVC stub dominates, optimize exactly that ABI-preserving path and host tests; if actual IL2CPP CPU dominates, first determine whether it is loading/asset operations, real simulation, or software rendering before considering owner-specific quality settings; if runnable starvation dominates, characterize frequency/affinity and thermal conditions.

**B. QueueSubmit -> replay complete (native/nvn_replay.h, native/nvn_render.h, native/nvn_textures.h, native/nvn_framebuffers.h):**

1. Partition **exclusive** wall and CPU costs into queue parsing, command callback/memory, shader lookup/link, sampler metadata resolve, texture refresh/BC decoding, file-backed guest faults, FBO transitions, draw vertex/index conversion, constant-buffer staging/upload, GL state binds, draw submission, glFinish/fence waits, and required readback. Track command counts, bytes, GL call counts and time by **(program pair, target ID, resource generation)**.
2. Measure driver call **CPU** separately from wall time; a long glDraw or glTexSubImage2D can block for GPU completion even if host CPU is idle. Probe EXT_disjoint_timer_query availability before attempting GPU pass timings; preserve disjoint handling and use sparse queries.
3. Test no-op profiling versus actual probes on the **same executable**, emit a compressed ring-buffer summary once per 60+ frames, and cap probe overhead below 5%. A stdout line on every draw, guest SVC or page fault is not an acceptable optimization baseline.
4. Require the top **three** exclusive operations in each phase, their wall ns/frame, CPU ns/frame and correlation with complete frame P95 before proposing code changes. Do **not** assume cbuf, postprocessing or raster work is hot simply because it is easy to edit.

**Gate:** >=95% exclusive attribution for the sampled phases, no double counting, and a ranked list of measured high-cost call paths on a real scene. This is the evidence needed to choose PR-05, not permission to refactor blindly.

### 20.6. PR-05 (P1): target the evidenced ZRAM cost without causing an OOM

**Measured, but incompletely reproduced:** raising T2_GZRAM_COLD_MS from 10 to 250 corresponds to menu-window period P50 **629.0 -> 579.3 ms** (~7.9%) and reported compression/restore path time **138 -> 59 ms/frame**. Treat this as a useful direction, **not** a certified new default. The source's cpu-compress-ms/cpu-restore-ms fields currently use monotonic elapsed time despite their names.

**Implementation and A/B:**

1. Add dedicated compressor thread CPU accounting (CLOCK_THREAD_CPUTIME_ID around actual compression/scan work) and synchronous fault-handler wall/CPU measures, plus separate lock-wait, codec, memcpy, mprotect, madvise and pread timings. Account for possibly overlapping threads. Retain existing compression correctness/fault test coverage.
2. Measure per-block lifecycle in a **bounded, non-sensitive** histogram: time since compress, time until next restore, repeated compress->fault->restore cycles, actual saved bytes, page residence and faulting thread. Never log source memory contents or user data. Identify whether a small set of hot blocks generates most churn.
3. Control Z0 cold10, Z1 cold100, Z2 cold250, Z3 cold500 in a matched 3-pair A/B matrix, **one variable at a time**. Repeat only if memory constraints permit. As a separate dimension, test scanner PERIOD_MS 20/50/100 and budget 32/16/8 MiB. Hold GPU texture cap, guest quota, lazy BC policy, 32 MiB diagnostic floor, clocks and identical ELF fixed per comparison.
4. For Z2/Z3, check minimum MemAvailable, CmaFree, SwapPSS, kernel pressure, system swap activity, IO stalls, peak RSS, complete frame P95/P99 and whether New Game loading completes. A larger cold interval consumes more uncompressed guest residency, so a latency win with disappearing memory headroom is not a win.
5. Only when **repeat thrash** is quantified, add opt-in per-block cooldown/negative hotness scoring: after a compressed block is restored, progressively postpone the next compression until a quiet window; use bounded metadata and account for data lifecycle and concurrent write epochs. Do not pin entire guest GPU pools on a heuristic.
6. Only if compression remains a major exclusive cost, compare a correctly bounded codec and allocation strategy (e.g. LZ4 versus existing codec) with lossless roundtrips, CPU/wall per MiB, encoded size, max resident bytes, corruption guards, and deterministic fault/restore tests. **First identify the actual compressor implementation in the recovered source**; this is not a claim that a new codec would help.
7. Reject any candidate that introduces extra faults, kernel order-4 pressure, memory-floor failure, stale aliases, unbalanced IO pins, corrupted guest pages, or unstable return to MainUI.

**Gate:** >=3 same-build, same-scene A/B pairs demonstrate a meaningful full-frame P95 gain and memory safety including level transitions. The diagnostic 32 MiB floor is not safe production proof.

### 20.7. PR-06 (P1): choose ONE NVN/GL optimization after replay attribution

Choose from this table only after §20.5 proves its bucket is dominant:

| If profile shows ... | Specific change | Must prove |
|---|---|---|
| Cbuf uploads dominate, with many unchanged 1024×1 RGBA32F rows | Exact touched-texel bound and verified generation/content-equality skip; only then smaller allocation or partial glTexSubImage2D | Shader's maximum coordinate and padded-block contract, GL context generation and UBO1 parity |
| Repeated immutable texture metadata resolution | Cached NVN descriptor -> GL object by pool generation, view, sampler, mip/layer and write epoch | Invalidations for TextureWriteTexels, alias writes, context loss, name reuse |
| Expensive zero_texture_refresh/BC materialization | Dirty-region upload, fewer lossless decompressions, or resource-aware prefetch | BC block stride/format, exact resource identity, safe 420 MiB cap, no added host thrash |
| FBO rebinding/checking and unnecessary target switches | Per-EGL-context FBO/state shadowing; eliminate repeated **verified redundant** checks in release | Last-reader lifetime, correct render pass ordering, alpha/stencil and UI screenshot parity |
| Repeated vertex/index conversion and GL buffer reallocation | Cached converted geometry by guest-write epoch or bounded scratch/ring buffers | In-flight GPU readers fenced, no stale geometry, bounded residency |
| Shader catalogue or program link dominates after cold start | Precompute lookups, defer unnecessary links, cache verified source/metadata | Exact SHA-pinned code/control identity and context recreation behavior |
| A GPU wait dominates replay | Correct fence/serial lifetime experiments, not glFlush-only | Zero NVN_COMMAND_REUSE_BEFORE_COMPLETION, EGL_BAD_SURFACE, stale UBO, black frames |
| A mandatory readback dominates | Examine whether it is presentation copy or a diagnostic pixel proof; remove **only optional probes** | Physically identical scanout and no broken resource synchronization |

**Explicit negative tests already completed:** LC2_CBUF_SUBIMAGE does not have a demonstrated improvement; ZERO_RENDER_SCALE=2 did not materially improve the menu; MOMO_SUBMIT_FINISH=0 has no completion proof. Keep those facts in the decision log so a new agent does not retry them as generic first-line advice.

**Optional R&D only after gameplay and significant GPU-bound evidence:** recover the owner of the 1920×1080 render target (not assumed to be Unity UpRender in this game), benchmark real gameplay bloom pair 17/4, examine native Mali timer extension, or test an owner-local content-hash ASTC side cache with exact source and visual-quality validation. None is the next P0 blocker.

### 20.8. Performance feasibility: use milestone gates, not a single promised FPS

The target is a **verified <=33.33ms complete gameplay frame P95**, with audio/save/input/pixel correctness and sustained thermals. The source/evidence above only measures menu/loading and one short scene-load transition.

| Milestone | Current state | Reasonable evidence gate before continuing |
|---|---|---|
| F0: correct scene load | Fails on the 1280-byte shader | Exact shader translated, correct KMS game scene and owned input state |
| F1: reliable measurement | Basic logs and parsers, outstanding bugs | Stable process/phase identity, raw per-frame evidence and clean device recovery |
| F2: find worst bottlenecks | ~316ms gap and ~250ms replay in a 60-frame diagnostic phase | Exclusive CPU/wall/wait operation profile with matched frame serials |
| F3: eliminate memory churn | One encouraging cold250 arm | Safe P95 improvement in three A/B pairs including New Game |
| F4: optimize renderer hot path | Only hypotheses, cbuf/rescale negative result | One proven expensive operation with visual-equivalent full-frame gain |
| F5: assess target feasibility | Not established | Three real, independent >=60s gameplay runs with P50/P95 <=33.33ms, P99 and slow spikes documented |

Do not extrapolate the New Game load frame reported at **152.8ms** (~6.5 inverse-interval frames/s) into steady gameplay. It is evidence that **one phase is faster than the menu**, not proof of stable 6.5 FPS or the attainability of 30. The frame-time reduction required to move from hundreds of milliseconds to 33.33 is so large that incremental one-digit percentage wins cannot close it alone. If profiling proves the remaining gap is intrinsic Unity/IL2CPP work on this SoC rather than adapter overhead, document a realistic lower-FPS mode and stop hazardous shortcuts. Conversely, if one large duplicated translation or guest-memory stall is identified, prioritize it over graphics presets.

### 20.9. Ready-to-execute change order and exact pass/fail criteria

| Order | Branch / PR suggestion | First code/evidence action | Required tests and stop condition |
|---|---|---|---|
| **1 P0** | fix/pad-and-principal-receipts | Correct 304/305 in test scripts; store PID+starttime and fail the harness on bad cleanup | Fixture-backed input mapping; one visible selection/confirm; CPU mask and MainUI restored |
| **2 P0** | feat/blocked-shader-layout-report | Owner-local SPIR-V/IR dump and precise layout/access inventory for hash 7a45f946… | Verify both blobs; preserve proprietary privacy; stop if transform is not semantics-preserving |
| **3 P0** | feat/blocked-shader-lowering | Implement one B1/B2/B3 method with source data contract; append-only catalogue integration | Shader IR and device GLES tests, UI parity, zero unpinned stop for exact pair |
| **4 P0** | fix/perf-observer-and-parser | Repair target HZ, PID/TID starttime, slow-log sampling, frame serial and signed residuals | Synthetic fixtures plus reconstructable raw/derived evidence and no misreported gameplay FPS |
| **5 P0** | feat/guest-gap-and-replay-ownership | Add bounded exclusive wall/CPU/wait timing in guest gap and NVN replay | >=95% attributed with <5% profiler overhead; identify 3 largest named costs |
| **6 P1** | perf/guest-zram-cold-matrix | Three paired Z0/Z2 runs plus separate 100/500ms, scanner and budget arms | Whole-frame P95 and memory both safe; no OOM, order-4 distress or stale page |
| **7 P1** | perf/one-hotspot-only | Improve the largest exclusive bottleneck and preserve GL/guest identity contracts | Three equivalent-scene A/B pairs, actual KMS comparison, gameplay regression |
| **8 P2** | perf/fences-or-quality-only-if-proven | Fences or owner-specific quality mode only when GPU-bound or waiting | Strict GPU completion and quality gates; unsafe flush/rescale variants OFF |
| **9 Final** | docs/gameplay-30fps-acceptance | Repeat full-game state, audio/save, clock, thermal and memory tests | Three independent 60s gameplay runs meeting strict frame P95 target |

**Minimal host-only checks before deployment:**

~~~sh
# Manifest entries are relative to the recovered GPL runtime tree, not this repo:
(cd /owner/recovered-runtime && sha256sum -c /owner/lamentum-repo/tools/baseline-manifest.sha256)
# Separately, run Python test fixtures from the port repository root:
(cd /owner/lamentum-repo && python3 -m unittest discover -s tools -p 'test_*.py')
# The C input-latch fixture compiles against the recovered GPL native include path.
# Supply the correct include paths for the pinned source tree; do not guess a build command.
sha256sum /owner/private/nvn-lc2-shader-code-1792497924-0.bin \
          /owner/private/nvn-lc2-shader-control-1792497924-0.bin

# Once two complete owner logs, phases and exact process/ELF identity are established:
python3 tools/analyze_perf.py /owner/bench-A/latest.log --from-frame 250 \
  --to-frame 500 --json /owner/bench-A/window.json
python3 tools/analyze_perf.py /owner/bench-B/latest.log --from-frame 250 \
  --to-frame 500 --json /owner/bench-B/window.json
~~~

**Caution:** the existing analyzer still has the validity issues in §20.4; the commands above are convenient smoke parsing, **not** certification of comparable scene, complete frame coverage or trusted FPS until that PR is done.

**Per-PR evidence:** repository HEAD and commit, recovered runtime manifest, compiler commit, catalogue SHA, installed ELF hash, owner image hashes (never bytes), exact device/OS/GLES extensions, stdout log hash, env diff with exactly one variable, frame-window scene identity, raw/derived samples, temperature and memory minima, visual/audio/input comparison, host tests, native stop reason, and cleanup proof. Store failures as well as successful runs.

**Final next-action recommendation:** do **not** start a new 720p/Bloom/FBO refactor. First repair the 304/305 test mismatch and harness semantics, then **translate the known shader with a type/stride-correct lowering** and reach real gameplay. Run the guest-gap/replay and cold250 experiments using a corrected observer, and only then implement the top measured performance optimization.

*No source-code changes or device testing are implied by this roadmap update itself.*


## 21. HEAD 2b6b2a1 reassessment — build210, updated critical path (2026-10-20)

> **HISTORICAL §21 SNAPSHOT; its task status is superseded by §22.** Source state reviewed: [main at 2b6b2a1](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/2b6b2a1d35dead6a9aade1e611700cc9b378c0cb), **19 commits after** the English roadmap commit a4d0a2e. Sections 0–20 preserve the original measurements and successive historical recommendations, but §20's statement that the shader 7a45f946… is still blocked is now **obsolete**. Build210 passed that specific stop. No test was run on the actual handheld for this documentation-only reassessment. Where a device run is described below, its source is a committed owner report, not a new independent reproduction.

### 21.1. Source/evidence delta and updated work status

| Area | What was implemented, fixed or measured since a4d0a2e | Current status / what NOT to conclude |
|---|---|---|
| New Game shader | [2b6b2a1](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/2b6b2a1d35dead6a9aade1e611700cc9b378c0cb) appended program **38** to the shader catalogue (now **39 catalogue entries total, including seven TEST-only substitutes**); the program is vertex, 1280-byte code and 2176-byte control, with the exact preexisting code/control SHA-256 identity | **BLOCKER RESOLVED for that exact pair**, not a general SSBO or translator fix. Controls/tutorial prompt and splash are now reported. Gameplay still NOT established |
| Offline translation | Owner-local Hades/spirv-cross step added a documented §`--fix-strides` conversion for `ArrayStride=4` float arrays that spirv-cross refuses under ESSL std140; source now compiles to ESSL 310 and is sampled through the existing cbuf-to-RGBA32F-texture path | Successful compilation does not independently prove the stride rewrite is safe for other shaders. The translator change is owner-local, not tracked in this Git repository |
| New shader binding | Program 38 required manually correcting generated `c4` metadata from `.binding=0` to `.binding=1` (NVN UBO slot 1; hardware bank 4). This repeats the build202 issue | **GENERATOR BUG STILL OPEN** in `tools/build_lamentum_catalogue.py` / `tools/append_program.py`. Another appended program could silently render incorrectly |
| New Game result | [docs/newgame-bringup.md](newgame-bringup.md) reports build210/newgame-07 showing controls text "Press any button to continue" and a splash; **275 presented frames, no STOP, zero shader-unrecognized errors, 1108 ROMFS reads** | Not yet a physically controlled walking/inventory scene. Screenshots/raw owner logs are not published alongside these particular summary numbers |
| Harness/input | New `tools/newgame_crash_repro.py`, `tools/newgame_start.py`, `tools/newgame_probe.py`, `tools/tap_sweep_probe.py`, `tools/test_input_latch.c` and input-latch integration | Repro code still mixes physical button codes and assumptions. `control-actions.json` identified Linux **305 = Confirm**, **304 = Back**, while `newgame_crash_repro.py` and `newgame_start.py` inject 304 as A. Exact button provenance must be fixed before judging next prompt |
| Frame metrics | `tools/analyze_perf.py`, `tools/perf_sample.py`, `NVN_PROFILE gap-ms` and ZRAM elapsed-path counters landed; `docs/fps-baseline-2026-10-20.md` records new tests | Instrumentation is **partial**, not yet a reproducible, frame-complete CPU/GPU trace. Remote tick/HZ, `/proc/*/stat` parsing, log-window identities and slow-frame sampling need repairs |
| Cbuf upload | `LC2_CBUF_SUBIMAGE` defaults on and uses `glTexSubImage2D` when dimensions match; original `glTexImage2D` available for A/B | No proven gain; don't reimplement it. Compare exact ELF, scene and raw per-frame traces before optimizing another tiny GL call |
| ZRAM cold threshold | Reported cold10 -> cold250 in frames 250–500: period P50 **629.0 -> 579.3 ms**, replay **297.7 -> 240.8 ms**, reported compression/restore elapsed path **138 -> 59 ms/frame** | Promising **single A/B**, not production acceptance; "CPU" fields use `CLOCK_MONOTONIC` elapsed time, not execution CPU |
| Render scaling | `ZERO_RENDER_SCALE=2` with cold250 was tested: full-frame P50 **579.3 -> 577.7 ms**, replay **240.8 -> 226.7 ms** | Not material for the menu workload; leave OFF. Do not repeat without an independently characterized gameplay GPU-bound scene |
| Queue completion | `MOMO_SUBMIT_FINISH=0` / `glFlush` arm shortened some diagnostic timings | **Not a correct completion guarantee**. Keep `glFinish` production path until serial/fence ownership is validated |
| General feasibility | One 60-frame `NVN_PROFILE` report: elapsed **572.700 ms/frame**, replay **249.626**, guest present-to-submit gap **316.431**, present **4.725**, readback **2.689** | Phase averages, **not** gameplay frame P95. Guest gap and replay are both major, though those measurements alone do not distinguish useful CPU work from stalls |

**Very important:** historical documents may say "38 translated real shaders" or "New Game blocked"; those statements described build202–209, not HEAD 2b6b2a1. Do not spend another round re-dumping/re-translating the already accepted exact code/control pair. Instead validate the correct pixels and advance past the tutorial.

### 21.2. P0-NG2 — Advance past the tutorial and establish controllable gameplay

**Reason:** current build210's success is an introduction/tutorial frame, not stable gameplay. This is the first practical blocker, ahead of every speculative 720p/Bloom shader optimization.

**Files:** `tools/newgame_crash_repro.py`, `tools/newgame_start.py`, `tools/device_principal_test.py`, `docs/newgame-bringup.md`; likely a new `tools/newgame_continue.py` plus a pure offline controller fixture. Preserve build210's catalogue identity and c4 binding.

1. **Pin identity.** From the owner device read back the *actual* executable SHA-256, patched runtime manifest and shader catalogue hash, merged game-image hash, SpruceOS build and complete effective environment. The build210 SHA beginning `d4f3d1f6` in the bring-up report is not a substitute for the **full** installed binary hash. Copy the known-good build210 ELF and save directory before testing.
2. **Create a restartable state machine:** WAIT_LIVE_PID -> WAIT_MENU_EVENT -> CONFIRM_VISIBLE_NEW_GAME -> SCENE_LOAD -> WAIT_TUTORIAL_PROMPT -> PRESS_CONTINUE -> WAIT_FIRST_GAMEPLAY -> TEST_MOVEMENT -> INTERACTION -> SAVE_RELOAD -> CLEANUP. Each transition needs a current-run log/guest-state event AND the corresponding real KMS image or other explicit game-state proof. Timeouts should record the last state and reason, never claim success.
3. **Fix pad semantics first.** Load the real active event source by name/GUID/capabilities; compare `evidence/ui-cbuf-fixed-01/control-actions.json` (304=Back, 305=Confirm) with the current injected `304`. Test 305 against one known, visibly interactive screen and record down/EV_SYN/up/EV_SYN with monotonic timestamps. Do not infer an A press merely because the title advanced once after a longer sequence.
4. Do not assume the main menu always opens with one fixed highlighted item. The latest crash script explicitly notes remembered selection; the older start script assumes Options. For a correct run, record the initial highlight, use short one-step navigation with a screenshot after each movement, and confirm **only** when New Game is visibly selected. Four Up taps and one Down are a fallback for a verified menu layout, not a reliable universal strategy.
5. The tutorial may use a different input dispatch than the menu: measure actual guest Npad sampled buttons around the displayed "Press any button to continue" prompt. Start with a bounded 150–300 ms tap; compare `LC2_INPUT_LATCH=0` vs `=1` under an **otherwise identical** ELF and scene state. The current latch has a 120 ms floor and 900 ms ceiling; do not set a forced window so long it creates repeats or multiple menu steps. Verify one guest-visible edge per physical edge and that buttons release on exceptions.
6. Acquire the **before-prompt**, **after-confirm**, **first-scene**, **first-movement** and **inventory** captures while the owner game PID and DRM plane are alive. Count frames between actual state transitions; do not confuse a static loading splash with a valid game scene. Preserve any unexpected `ZERO_SHADER_NOT_PINNED`, GL error, memory floor or STOP with full identity/hash and run stage.
7. Once controls work, verify moving sprite, interaction, camera/UI, transparent sprites, shading, inventory and a reversible menu. Require a first audible music/SFX receipt and cold save/quit/load before classifying the port as playable.
8. Run a separate **minimal-diagnostics** loop after bring-up. Label all New Game transitions/loading phases explicitly; they must not contaminate steady-state gameplay measurements.

**Acceptance:** visually correct, controlled gameplay with current-run input evidence, correct sound/save/load, zero unexpected shader/GL stops and clean frontend/CPU restoration. **Failure classification:** (A) incorrect selection/button, (B) prompt rejects input, (C) new unpinned shader, (D) graphics error, (E) memory floor/kernel stress, (F) guest/service exception, (G) test-harness cleanup failure. Each has a different next owner.

### 21.3. P0-SHADER-META — Eliminate the repeated c4 -> wrong-slot generator regression

**High-confidence source finding:**

- `tools/build_lamentum_catalogue.py::cbuf_blocks_of` extracts `layout(binding=...)` when it exists, **otherwise uses the declaration index**. A shader whose source declares one block instance named `c4` can therefore be emitted with binding=0 even though the captured NVN hardware bank 4 corresponds to **NVN API uniform slot 1** under this SDK's bank=slot+3 convention.
- `tools/append_program.py::append` serializes that guessed `b['binding']` directly; build210 repaired the new program's metadata **by hand**. Another append could undo the same correction.
- Program 38's declared `float data[16384]` becomes a 65,536-byte metadata size, but its currently checked-in GLSL contains constant c4 indices **0 through 79**, with no identified dynamic index within that specific generated program. This is a candidate for **later** touched-range instrumentation, not permission to change the generic 64 KiB layout blindly.

**Implementation, in exact order:**

1. Add a **metadata provenance field/sidecar** for every cbuf: original compiler variable name (e.g. `c4`), declaration ordinal, the raw stage-specific SPIR-V DescriptorSet/Binding, captured hardware constant-buffer bank, derived NVN API slot, guest binding range, and verified mapping method. Distinguish an API slot from a GPU hardware-bank number in names and logs.
2. Use the known SDK rule (hardware-bank = NVN API slot + 3) **only after confirming the source metadata is a hardware-bank ID**. For c4 under the verified build202/build210 contract, emit slot 1. If a source has only ordinal and no validated bank provenance, **fail closed** with `CBUF_BINDING_UNRESOLVED` instead of silently choosing 0 or another occupied slot.
3. Change `cbuf_blocks_of` to return a resolved semantic descriptor rather than silently defaulting `binding=index`. Make `append_program.py` reject an unverified mapping and keep an explicit owner-local resolution manifest keyed by **both code and control hash**. Do not change the actual shader bytes or weaken catalogue hash matching.
4. Add host fixtures for: a single c4 hardware bank 4 -> NVN slot 1; one c3 bank -> slot 0 if its provenance supports that rule; two separate cbufs in one stage; absent layout information; unsupported bank; deliberate declaration-order inversion; mismatched control hash; and an existing corrected build202 UI shader. A bad mapping must fail compilation/integration rather than rendering zero transforms.
5. Snapshot the existing 39 catalogue entries, source/glsl metadata, seven TEST substitutes and program 12/38 bindings. Append a **synthetic self-authored** program in a temporary file, verify existing entries byte-identical and catalogue count increment exactly once; never bulk regenerate the production catalogue.
6. Keep the owner-local offline `--fix-strides` translation step in an independently version-pinned script with a SPIR-V decoration/memory-access equivalence report: for program 38, float array stride 4 in the source is represented via correct indexed RGBA texture lanes; changing stride 16 only permits ESSL emission, it must not change live data address semantics. Test static and dynamic indexing for future programs separately.
7. Device integration: compare original build210 menu/title/tutorial graphics before/after generator fix. Check sampler-unit isolation, gl_Position, varyings, alpha and any relevant skinning/geometry. Shader compilation/link success alone is not a sufficient pass.

**PASS:** exact code/control identities, correct slot mapping, byte-identical existing catalogue and device pixel parity; no manual correction required for the next appended shader. **STOP:** ambiguous source bank provenance, wrong UBO slot or incorrect shader data layout.

### 21.4. P0-HARNESS — Repair input automation, cleanup and benchmark identities

**Source finding:** `tools/device_principal_test.py` currently returns **0** after printing process/MainUI/CPU state, even if it has not established correct restoration. `tools/perf_sample.py` reads remote `/proc/PID/stat` with plain `split()`, identifies processes by name only, converts guest CPU ticks using the **controller host** `os.sysconf('SC_CLK_TCK')`, and tails the last 3000 log bytes for frame identity. These are real correctness flaws that can mislead performance decisions. New Game tools duplicate SSH and input/cleanup logic.

1. Extract a single owner-local test transport with explicit device identity, SSH timeout, qualified active event provider, and a dry-run/read-only preflight. Parameterize repo path, port location, device SSH host and /dev/input node; **do not remove idle-device checks or launch beside another game**.
2. Introduce a **run UUID and monotonic launch generation**: pin PID + `/proc/PID/stat` starttime and log inode plus incremental byte offset. Write identity, exact effective environment and installed ELF hash before any input is issued. Reject events from an old log after rotation/truncation. For each failed SSH call, preserve return code, stderr and partial evidence.
3. Replace direct `press(1,304,...)` calls with the verified named mapping from §21.2 and a balanced press/release helper. Capture UI selection before and after; an injected pad write is not proof that the guest sampled the intended button.
4. Snapshot MainUI's **PID/starttime**, principal process state, game PID identity and CPU online mask before launching. In a `try/finally` and signal-safe outer cleanup path, restore CPU state and frontend only when owned by this run. Verify postconditions and return a **nonzero harness status** for any mismatch, independent of expected guest STOP or TIME_LIMIT. Do not kill unrelated user applications. Preserve abnormal-exit logs before invoking cleanup.
5. Parse `/proc/.../stat` using the numeric PID, the final closing parenthesis and remaining fields; support spaces/parentheses in comm. Collect target device `SC_CLK_TCK` remotely and persist it, not from the Mac/Linux workstation. Track threads by (TID, starttime), report missing samples as null/NA, never report negative CPU deltas across PID reuse.
6. Record running CPU and runnable-delay separately from `/proc/TID/schedstat`, plus TID wchan/switches, min/major faults, and slow external RSS/SwapPSS, MemAvailable/CmaFree/frequency/thermal samples. Include the compressor thread even when it is not in the top six. Do not equate 78% CPU utilization with proof that an entire 316 ms phase executed on CPU.
7. Refactor `tools/analyze_perf.py` to preserve source frame order, flag missing/duplicate/out-of-order serials, report **signed** residuals rather than `max(0,...)`, and report the fraction of all frames represented by `T2P_SLOW_FRAME`. Its automatic "first frame below 1000 ms" warmup inference is not a scene boundary. A frame-P95 or throughput calculation must use a **complete** presented-frame sequence.
8. Add pure host fixtures: wrong BTN 304/305, missing Up release, stale `LC2_MENU_EVENT`, PID reuse, parentheses in /proc names, target HZ 100/250, incomplete frame logs, negative residual/overlap, missed frame, bad CPU restore, missing MainUI and kernel OOM. Introduce structured exit codes distinguishing **GAME_STOP_EXPECTED**, **GAME_STOP_UNEXPECTED**, **HARNESS_FAILURE**, **TIME_LIMIT**, and **CLEANUP_FAILURE**.

**Evidence deliverables:** `identity.json`, `input.jsonl`, `process-threads.csv`, `frames.csv`, `cleanup.json`, two live KMS captures and raw log hash per run. After the fixes, older pre-fix distribution JSON remains historical only; do **not** backfill it with invented phase or CPU fields.

### 21.5. P0-PROFILE — Establish complete-frame CPU/wait/GPU ownership in the NEW playable state

The build209 summary provides a useful **inclusive/phase-level** 572.7 ms report, but not detailed exclusive attribution. Keep it as a control and compare build210's **tutorial** with build202's **menu** only as different phases, never as identical A/B cases.

**Required low-overhead timeline events, keyed by frame serial, guest PC/TID, host TID, guest resource generation and monotonic clock:**

1. **Guest present end -> next QueueSubmit:** subdivide guest SVC calls by service and caller PC, Unity/IL2CPP execution, page faults/restores, memory manager scan/codec/locking, IPC waits, runnable-but-unscheduled time, deliberate frame sleeps and frame callback invocation. Where possible use host CLOCK_THREAD_CPUTIME_ID at entry/exit and monotonic RAW elapsed; mutually exclusive spans must attribute >=95% of the gap. Correctly account for nested SVC and background-worker overlap.
2. **QueueSubmit -> replay end:** aggregate wall and thread-CPU by NVN command record/dispatch, queue lock and command-memory callbacks, descriptor/texture pool lookup, shader cache and GL program use, BC materialization / texture refresh, uniform snapshot/cbuf staging and upload, vertex/index conversion, FBO state and render-pass transitions, GL draw, glFinish/fence waits, and mandatory/optional readback. Attribute to **program pair, GL context generation, render-target ID and resource epoch**.
3. **System delay:** correlate guest CPU running/runnable delay with Linux per-thread schedstat and /proc faults; collect target CPU MHz and temperature. Use asynchronous sampled counters or preallocated rings; no per-draw printf, no per-frame synchronous SSH, no glFinish around every operation.
4. **GPU measurement:** probe support for EXT_disjoint_timer_query and other actual device extensions, and use sampled GPU queries only with correct async retrieval and disjoint handling. A driver GL wall time is **not** automatically GPU time. Distinguish GPU idleness, resource waits and CPU bottlenecks.
5. **Readback:** distinguish mandatory composition from proof-only glReadPixels and `NVN_PRESENT_PIXELS` counters. Under a controlled *debug-only* flag, measure readback ON/OFF while validating physical KMS scanout; do not disable a required copy/ownership fence.
6. **Use signed whole-frame accounting** and prove that sampled frame count and phase labels match the real presentation sequence. Run profiler OFF/ON at identical scene/ELF: profiler overhead target <5%. Publish raw per-frame wall/CPU and the top three exclusive functions within each ~316 ms gap and ~250 ms replay interval.

**Decision gate:** each dominant interval has >=95% attributed time and at least one measured operation whose removal or reduced frequency could plausibly save tens of milliseconds. Without this, another graphics refactor is speculation, not a validated FPS optimization.

### 21.6. P1-ZRAM — Validate cold250 and attack *measured* repeated fault/compression churn

**Don't misread the counters:** the existing `t2_gz_now_ns()` uses CLOCK_MONOTONIC; rename its output as **wall-codec-time** or instrument executing-thread CPU separately. The published **138 -> 59 ms/frame** result is not CPU execution time. Saved MiB and physical free memory cannot be added without accounting for pinned/file-backed/aliased pages.

1. Implement cumulative, thread-safe counters with distinct buckets for **codec CPU**, codec wall, lock wait, scanner cost, mprotect/madvise, fault restore, copy and file-backed pread. Correctly count nested faults and contention; report bytes/sec and effective saved memory.
2. Add a small bounded page-block table/histogram: compress generation, last touch, next fault, hotness, time-to-refault and compress->restore->recompress cycles. Do not record game page contents or proprietary data. Set a memory ceiling for profiling metadata and sample the hottest blocks rather than full tracing.
3. Use **one-change-per-arm** paired experiments: Z0 cold10; Z1 cold100; Z2 cold250; Z3 cold500. For the chosen safe cold value, separately test scan period 20/50/100 ms, budget 32/16/8 MiB and (only if justified) block 16/4 KiB. Alternate control/test order and repeat **three matched pairs**. Keep guest virtual quota, BC backing, memory floor, full ELF, scene state and clocks fixed.
4. Monitor actual minimum MemAvailable and CmaFree, PSS/SwapPSS, compressor task CPU, major faults, swap I/O, kernel `page allocation failure: order:4` messages and runtime memory floor stops. New Game scene loading deserves its own stress arm; a menu win that fails on scene transition is a loss.
5. If Z2 retains headroom and the histogram proves rapid refault, prototype a **bounded adaptive cooldown**: after restoring a hot block, defer only that block's recompression for a capped interval; re-evaluate coldness under free-memory pressure; preserve eviction ability, alias/write generation and fault-handler reentrancy. Explicitly test repeated guest writers, mprotect state, reclaim and decompression failure injection.
6. If codec execution CPU (not just elapsed-path latency) is still substantial, benchmark alternative lossless compression strategies on **synthetic self-authored pages** and representative owner-local runtime pages without publishing them. Require correct round-trips, memory bounds, block metadata versioning, and fault-restore atomicity.
7. **Never promote** cold250 merely from one P50: require whole-frame P95/P99, three matched samples, safe New Game transitions and measured savings relative to comparator. Production 96 MiB floor remains a distinct acceptance gate; 32 MiB is diagnostic, not a safe release recommendation.

**Stop:** degraded P95/P99, OOM/memory floor, stale bytes after alias writes, repeated page faults, kernel distress or broken frontend restoration.

### 21.7. P1-CBUF2 — Optimize the actual padded upload and correct resource lifetimes, ONLY after profiling

The current kind=7 code in `runtime/lamentum-adapter.patch` explicitly sets **`width=1024`**, computes `height=ceil(texels/1024)`, zeroes a static staging buffer and uploads a full **1024×height RGBA32F** texture, even for typical **16–368-byte** live ranges. That means a 1024×1 allocation/update covers **16 KiB** when the useful payload is a few hundred bytes. This is a **potential** CPU copy/driver upload cost, not proof it dominates 250 ms replay. The GLES source itself uses a 1024-texel row addressing contract, so simply changing width to ceil(liveBytes/16) will **break** texelFetch addressing across rows.

**Safe experiment sequence:**

1. Record by (program ID, stage, resolved bank, context generation) every effective `range.size`, `avail`, copied bytes, GL upload width×height, unchanged content bytes, render passes and GPU consumer serial. Split first-use shader 38 from the recurrent UI, rather than blaming its 65,536-byte declaration.
2. Keep the existing **1024-texel logical stride** and allocate/clear full texture storage **on first use or resize**. On subsequent draws, determine the *actual dirty RGBA texels* including the necessary zero-padding when a former range becomes shorter. Upload **only touched subrectangles** via glTexSubImage2D: for a 368-byte current bank in row0 this can be as few as 23 texels, not 1024. For a multi-row range, calculate exact row spans and copy/update all modified rows.
3. Compare the active bytes against a per-texture content snapshot keyed by guest binding/resource **generation**, address, size and write epoch; byte comparison prevents hash collisions. If source writes aren't tracked, make a small exact memcpy+memcmp snapshot **per draw** before skipping GL updates. Never reuse data solely because the pointer value is unchanged.
4. Replace process-static `cbuf_texture[32]` assumptions with clearly documented lifetime and state invalidation on EGL context recreation, texture deletion/name reuse and shader/sampler unit reassignment. Keep the build177 unit allocator/isolation logic. Track `glActiveTexture`/sampler binding ownership per context; use existing GL-error probes only in bounded diagnostics.
5. Make NVN cbuf range selection **exact**: the current fallback from an empty declared stage/bank to `other=u->binding?0:1` can hide generator errors. Retain the legacy fallback behind a debug-only switch until program12/38 and all earlier UI pairs pass the generated metadata fixture; then fail closed for any unverified bank instead of guessing.
6. For **program 38 only**, statically audit GLSL accesses to `c4`: the checked-in generated text contains constant indices 0–79; validate that **all** accesses are fixed and that any legal shader variant uses the same access range before considering a bounded upload or per-program specialization. Preserve defined out-of-range/zero reads, 1024-row addressing and resource write epochs. Declared length 16384 floats is **not** proof that 64 KiB needs to be uploaded each frame.
7. Compare opt-in **C2-full versus C2-partial** with *same* binary and scene, logged uploaded bytes per frame, CPU/driver elapsed, replay P95, whole-frame P95 and exact KMS captures. If measured full-frame improvement is insignificant, keep the simpler existing path and close the hypothesis.

**STOP:** missing UI/sprites, wrong transforms, stale blocks, invalid GL context ownership, increased GPU wait or a gain indistinguishable from measurement noise.

### 21.8. P1-REPLAY2 — Follow measured NVN/GL hot spots, not another blanket optimization list

Once §21.5 names the real hot operations, open **one** separate PR per group:

| Profiled exclusive bottleneck | Exact candidate | Correctness / invalidation |
|---|---|---|
| Sampler/descriptors and texture-view resolution | Cache checked texture+sampler resolution by NVN pool/descriptor generation, underlying backing epoch, layer, mip, target, swizzle and EGL context | Invalidate TextureWriteTexels, alias writes, pool replacement and GL context reset |
| Repeated BC3 atlas materialization, storage reads or glTexImage | Page-aligned/tiled dirty-region refresh, immutable texture residency side cache, owner-local prefetch | Preserve all original 8192×4096 atlas pixels, BC format/sRGB/alpha, 420 MiB GPU cap and safe file-backed lifetime |
| GL state binds / FBO attachment checks | Shadow per-context program, texture, FBO, viewport, scissor, blend/depth/stencil; skip verified redundant calls | Every unmanaged GL entry point invalidates its changed state; sample KMS pixels plus GPU completion |
| Vertex/index conversion or buffer reallocations | Bounded scratch/ring VBO, reusable decoded indices, conversion cache keyed by guest-write epoch | Fence all in-flight readers; never assume static source addresses imply static geometry |
| Command recorder callbacks or queue lock | Reduce allocations and redundant command copies; narrow the expensive lock/callback path | Guest call semantics, command-buffer serial ownership and exact callback ABI |
| Shader lookup or expensive link on warm frames | Precompute exact (code+control) digest maps, lazily link once per program/context, cache verified uniform locations | Context generation, exact stage/interface and no TEST-stub substitution |
| GPU completion wait | Diagnose whether a real frame pipeline can legally overlap CPU/GPU with a correct GLsync scheme | Never replace completion with glFlush alone; zero command-reuse stops or stale buffers |
| Readback/proof-only calls | Restrict optional pixel readback to sampled diagnostic frames | Mandatory presentation and physical scanout remain identical |

**How to choose:** if an operation consumes X exclusive ms/frame, it cannot explain more than X ms/frame of directly eliminated CPU time without secondary effects. Require an operation to be consistently expensive across repeated frames, not just the first shader compile or cold atlas load. Validate new guest gameplay scenes separately from the old static menu.

### 21.9. P2-CPU/GAME — Address the ~316 ms guest gap only after separating actual work and stalls

This part is potentially the hardest remaining obstacle to 30 FPS. **Do not assume every millisecond of the gap is irreducible Unity game logic.** It could contain native Horizon translation, address-space faults, runtime locks, service IPC, guest IL2CPP work or scheduling. The 78%/19% thread snapshots do not supply per-call causality.

1. Instrument guest CPU **PC distribution**, SVC number/caller, guest-memory fault reason, thread context switches and memory copy bandwidth in a *sampled* or ring-buffered manner; correlate each hot PC with hash-pinned owner `main`/`sdk` NSO location without publishing proprietary bytes.
2. For an expensive **Horizon IPC/SVC stub**, perform ABI-exact fast paths only after a host fixture proves return values, flags, object/event lifecycle, error codes and thread wakeups. Keep the original implementation behind a debug/rollback flag.
3. For high **guest memory fault / ZRAM** cost, use §21.6 first. If guest page aliasing or repeated PROT_NONE trapping is the hotspot, profile exact mapping/locking overhead and preserve invalidation and dirty-write semantics; no speculative pageout.
4. For large **IL2CPP CPU** time, identify whether it occurs in cold scene loading/decompression, repetitive UI layout/canvas rebuilds, scripting allocations/GC, per-frame physics/AI, or CPU-side mesh/texture generation. Identify functions only from owner-hash-matched symbols/metadata or sampled PCs, not guesses about Lamentum's Unity components. Require an observed top-three cost and a portable adapter-side mitigation before editing title-specific behavior.
5. Compare CPU placement only with real core topology, per-core clock, throttling and runnable wait data. The adapter/launcher uses CPU0–3 on a handheld with CPU online-state restoration; a single busy core could be a scheduling or SoC limitation, but an arbitrary affinity move is not proof of a speedup. Never leave altered governors/CPU masks behind.
6. Consider owner-specific graphics options or actual Unity internal quality modifiers **only** if the guest profile shows corresponding CPU cost or a later gameplay scene becomes GPU-bound. The original `ZERO_RENDER_SCALE=2` static-menu negative result stands; do not claim "720p fixed it" without a different measured workload.
7. If correct, representative gameplay remains hundreds of milliseconds per frame **after** all identified adapter/memory hot spots are removed, document the hardware feasibility ceiling and a safe lower-FPS goal instead of attempting unsafe shader skips, missing sync or memory-floor bypass.

### 21.10. Revised PR order, exact experiments and acceptance gates

| Sequence | Branch / task | Concrete source to change | Deliverable and go/no-go |
|---|---|---|---|
| **P0-1** | `fix/intro-input-receipts` | `tools/newgame_crash_repro.py`, `tools/newgame_start.py`, shared event helper | Linux 305/304 semantics verified; current-run initial selection and tutorial continue screenshot; correct release on exceptions |
| **P0-2** | `feat/gameplay-state-fsm` | `tools/newgame_continue.py`, `docs/newgame-bringup.md` | First moving scene, inventory, audio and cold save/load, or precisely identified next STOP |
| **P0-3** | `fix/shader-cbuf-bank-provenance` | `tools/build_lamentum_catalogue.py`, `tools/append_program.py` and host tests | c4 -> slot1 auto-generated for the verified pair; full previous catalogue preserved; future uncertain mappings fail closed |
| **P0-4** | `fix/observer-and-harness-integrity` | `tools/perf_sample.py`, `tools/analyze_perf.py`, `tools/device_principal_test.py` plus fixtures | Target HZ + PID/TID starttime, complete frame serial, signed residuals, nonzero bad cleanup exit, reproducible A/B evidence |
| **P0-5** | `feat/guest-gap-replay-exclusives` | `runtime/lamentum-adapter.patch`: native guest/NVN instrumentation | >=95% exclusive attribution for gap and replay with profiler overhead <5% |
| **P1-1** | `perf/gzram-cold-pairs` | Guest memory counters and controlled harness flags | 10/100/250/500 ms A/B repeated 3×; safe P95, RAM and scene-transition results |
| **P1-2** | `perf/one-hotspot` | Exactly one measured replay or guest CPU site | 3 A/B pairs showing improved *whole-frame P95* and identical game behavior |
| **P1-3** | `perf/cbuf-dirty-texels` | kind=7 cbuf branch only if it profiles hot | Compare full 1024-wide uploads vs generation-correct partial data; check UI and GPU fences |
| **P2-1** | `perf/quality-and-residency` | Owner-specific settings, BC cache or Mali pass graph, conditional | Only for proven GPU/memory bottleneck; preserve exact pixels or label a reviewed quality preset |
| **P2-2** | `perf/gpu-overlap` | NVN queue + GLsync when proven waiting | Strict ownership, zero stale resources; `glFlush` is not completion |
| **Final** | `docs/release-benchmark` | Bench docs and packaging | 3 independent correct gameplay runs >=60s, period P50/P95 <=33.33 ms, P99, thermal and no spikes; audio/save/input and cleanup pass |

**Practical owner-workspace commands (examples; do not execute against a busy device):**

~~~sh
# Verify the pinned 435-file source baseline and current Git identity.
(cd /owner/recovered-runtime &&
  sha256sum -c /owner/lamentum-repo/tools/baseline-manifest.sha256)
git -C /owner/lamentum-repo rev-parse HEAD

# Execute the host-only Python regression suite (currently covers only what exists).
(cd /owner/lamentum-repo &&
  python3 -m unittest discover -s tools -p 'test_*.py')

# The actual device test requires an idle Spruce principal flow.
# Record exact ELF/hash/env and capture a prompt->gameplay state transition;
# use the input-contract repair before relying on injected button results.
# Historical parser: smoke-only until P0-4 fixes sampling/completeness.
python3 /owner/lamentum-repo/tools/analyze_perf.py /owner/bench-A/latest.log \
  --from-frame 250 --to-frame 500 --json /owner/bench-A/window.json
python3 /owner/lamentum-repo/tools/analyze_perf.py /owner/bench-B/latest.log \
  --from-frame 250 --to-frame 500 --json /owner/bench-B/window.json
~~~

**Per-PR acceptance contract:** exact Git and installed ELF SHA-256, recovered source manifest and owner-image identity; one changed parameter; same scene/phase and effective environment; correct current-run KMS capture; raw event/frame/thread samples plus derived summary; P50/P95/P99 and confidence from 3 paired A/B runs; no input/visual/audio/save regressions; tested fail-closed behavior; RAM/CmaFree/temperature minima; and verified cleanup restoring MainUI/CPU masks. Never commit private NSO, RomFS, original shader dumps, keys or saves.

**Best next execution path from this HEAD:** §21.2 (press through the tutorial and reach real gameplay), §21.3 (remove the generator's repeated wrong-slot regression) and §21.4 (make tests/evidence trustworthy) can be developed as separate small changes. Then §21.5 identifies whether §21.6 (guest ZRAM), §21.7 (padded cbuf uploads), §21.8 (NVN replay) or §21.9 (guest/IL2CPP) is the next real frame-time win. **Do not adopt glFlush-only submission, 720p rescale, or a different shader TEST stub as an unmeasured shortcut.**

*Scope of this update: repository-source inspection and documentation changes only; no owner device was accessed, no new executable was built, and the 30 FPS target has not been demonstrated.*


## 22. HEAD 2be834a: updated post-shader-tail audit and next performance plan (2026-10-20)

> **CURRENT AUTHORITATIVE DELTA, superseding §21's implementation status.** The concurrent source commit [2be834a](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/2be834adbb0f9f45f5c2bf71fad56c1cf47f4d08) landed after the initial §21 review. Its concrete fixes have been inspected below: **42 total catalogue entries, including 7 TEST-only entries**; program **41** was appended *after* build212/newgame-11 stopped on its hash, so that program still requires its first device replay. The 304/305 control bug, append-only cN bank mapping and basic principal cleanup contract have **now been addressed**. Keep §21 for rationale and unimplemented deeper profiling/optimization ideas, but do not duplicate already committed fixes. No new device run was performed for this documentation update.

### 22.1. Exact state and evidence: what has REALLY been done

| Subsystem / previous task | Committed source and evidence | Status after 2be834a; remaining proof |
|---|---|---|
| Proper New Game selection | New shared `tools/lamentum_pad_contract.py` has **Confirm=(EV_KEY,305)**, Back=(EV_KEY,304), game PID/starttime and live KMS receipts. `newgame-09/10/11` contain per-action receipts, screenshots and cleanup reports; old automated navigation now refuses by default | **INPUT CONTRACT FIXED at harness level**. Still agent evdev injection, not a human-controls acceptance test; no actual walking |
| Harness exit/cleanup | `tools/device_principal_test.py` snapshots MainUI/supervisors/CPU mask, waits for cleanup and returns **3** for cleanup failure, **4** for non-TIME_LIMIT guest STOP, **0** for TIME_LIMIT plus clean state | **BASIC CLEANUP CONTRACT IMPLEMENTED**. Parent scripts must classify an expected shader stop as a **game result**, not an SSH/cleanup failure; deeper run identity/polling improvements remain |
| Shader catalogue | `runtime/lamentum-shaders-draft.h` currently declares **`ZERO_ZX_SHADER_PACKAGES 42`**. Existing seven TEST-only substitutes remain inside those 42 | **42 entries** is the source count; not 42 validated real gameplay programs |
| Program 38 | `7a45f946… / 588a3fad…` vertex, c4/UBO1, fixed layout | **Catalogued**, but a correct live draw/pixel check remains open |
| Program 39 | `e1d6ede5… / 68743131…` fragment; finite read-only float c3 with texture-backed scalar loads, explicit f16 rounding; disabled-probe-volume branch only | **Guarded partial translation**, *not* general sampler3D/volume support. At every draw require UBO0 >=220 B and `c3[8] != 1.0`, otherwise fail closed |
| Program 40 | `84137e66… / 927f1841…` vertex, c3/UBO0; 51 loads with max word index 59, required source size **240 B** | **Catalogued with minimum-range guard**; draw/pixel proof still needed |
| Program 41 | `6b33f390… / a2053408…` fragment (256-byte captured code); output normal mapped to 0..1 with alpha zero, no textures or cbuf | **Appended in HEAD** but **not proven on the device**. In newgame-11 the previous binary stopped on this exact pair at frame 514 |
| Translation reliability | `tools/float_cbuf_contract.py` checks finite, scalar, statically indexed, read-only loads; `append_program.py` now maps source instance cN to NVN slot N−3, fails closed on unknown banks; `tools/append_light_fragment.py` preserves half conversion and guards | **C4 mapping regression fixed for new appends**. Host report: 33 Python tests plus C guard fixture passed. Still require per-stage GLES + actual-pixel verification; do not generalize unsupported dynamic/writable SSBO |
| Measured performance | Historic cold250 and frame gap reports remain. `evidence/newgame-11/progress.json` adds phase averages, not a controlled A/B | Still **NO gameplay FPS**; neither cbuf subimage, render scaling nor flush-only completion was established as a safe useful speedup |

**Explicit correction to §21:** the earlier "studio splash" was a misread **Loading...** text. `docs/newgame-bringup.md` now identifies the earlier full-log truncation and wrong 304-as-A input as sources of false success. Never use the old build210 275-frame no-STOP excerpt as proof of an entire New Game run. Build212/newgame-11 is the last described device frontier.

**Shader stop sequence with proper selection, not an inferred scene state:**

| Evidence | Build | Last presented frame | Exact next uncatalogued program | Minimum sampled MemAvailable |
|---|---:|---:|---|---:|
| `evidence/newgame-09/summary.json` | 210 | 557 | e1d6ede5… fragment (now entry 39) | 70 MiB |
| `evidence/newgame-10/summary.json` | 211 | 495 | 84137e66… vertex (now entry 40) | 50 MiB |
| `evidence/newgame-11/summary.json` | 212 | 514 | 6b33f390… fragment (now entry 41) | 56 MiB |

These are separate loading/frontier runs, **not FPS A/B pairs**. Raw owner logs are pinned by SHA-256 in each evidence summary; the published receipts/screenshots establish stronger traceability than the earlier screenshot-free summaries, but original private log bytes remain owner-local.

### 22.2. P0-FRONTIER — Rebuild program 41 and continue the exact shader-tail chain

**Next concrete experiment:** the first on-device run with all **42** catalogue entries (a build after build212), using an exact SHA-pinned ELF built from HEAD. Do not re-translate entries 38–41 unless their own guard/visual parity fails.

1. Verify `sha256sum -c tools/baseline-manifest.sha256` from the 435-file recovered runtime directory; pin Git source, compiler identity, merged owner image, patch, catalogue SHA and new installed ELF. Preserve build212 as rollback. Never commit original shader code/control binaries.
2. Run host test suites including `tools/test_append_program.py`, `tools/test_float_cbuf_contract.py`, `tools/test_light_fragment.py` and `tools/test_lamentum_pad_contract.py`. Inspect the mandatory runtime guards after applying the patch: index 39 must stop on the enabled probe branch or insufficient UBO0 and index 40 on insufficient UBO0. Check that the intended fallback **does not silently mask those conditions**.
3. Launch exclusively through Spruce principal flow using the updated owner-local harness. Capture menu *before* Confirm, choose New Game visibly, capture its configuration page, confirm *after* checking the live KMS state, and then sample scene loading with bounded screenshots. Save initial/final process+CPU states. Do not let old `newgame_start.py` assumptions override the new shared helper.
4. Before proceeding on an unexpected STOP, inspect **the entire run's final log**, not `latest-end.log` or the last 4KB. Archive exact code/control hashes, stage, return status, frame serial, current KMS capture and memory/thermal state.
5. If the next stop is **another distinct shader**, add it append-only from a verified local dump after checking scalar/dynamic/writable/sampler/image/atomic capabilities. Use the `float_cbuf_contract` path only if its finite read-only/static contract passes. Record required byte extent, bank provenance, varyings, link partner, fragment alpha/depth outputs and GL format. Unknown behavior must fail closed, not become another blank TEST shader.
6. For **program 39**, collect a bounded **per-draw guard receipt**: resolved UBO0 address/size, c3[8] bits, resulting path and count, shader/fragment partner, attachment format and actual pixel change. An enabled probe-volume branch requires a separate real sampler3D path or a clearly identified unsupported-feature STOP. Do not disable probe lighting unconditionally for performance.
7. For **program 40**, verify that the runtime reads **at least 240 B** from its actual UBO0 and does not rely on an accidental fallback from another stage/bank. Check the world-to-clip position and actual scene vertices, not just nonblack pixels. For **program 41**, validate the normal-to-color transfer and intentionally zero alpha against the actual blend/attachment state; a visually empty pass could be correct or could be a masked bug.
8. Stop the frontier loop only at an actual interactive gameplay scene or an explicit unsupported shader capability. Then test movement/inventory/sound/save-load. Record newly reached shader identities separately from per-frame performance work.

**PASS for next build:** program 41 is accepted and physically rendered with correct state, zero new unexpected GL/resource stops, and either a later clearly identified blocker or a correctly controlled game scene. **Important:** clearing a shader stop alone is not evidence of improved FPS.

### 22.3. P0-RECEIPTS — Close the remaining test-infrastructure gaps instead of redoing finished work

Completed in 2be834a: named 305/304 mapping, balanced release, unique live PID and KMS capture receipts, strict basic MainUI/CPU cleanup checks, tests. Remaining **specific** improvements:

1. **tools/perf_sample.py still uses host HZ.** Replace its local `os.sysconf('SC_CLK_TCK')` conversion with the device's HZ recorded by the remote probe. Parse /proc PID/TID stat after the last matching ')' and include PID/TID starttime to handle reused identities. Preserve *all* thread samples, not just top six.
2. In `tools/device_principal_test.py`, maintain the current fail-closed **no-parallel-game** guard and exit-code meanings. Add a stable run UUID, exact owner ELF hash, expected scene/phase, current log inode + byte offset, and explicit capture of kernel pressure. Avoid repeated full multi-MiB log scans while the game runs; archive the completed log once. A guest `ZERO_SHADER_NOT_PINNED` with **cleanup_errors=[]** is not a healthy game run, but is a valid fail-closed shader-frontier receipt.
3. Parent tools must not overwrite the last full crash evidence after harness returns 4. Propagate the game stop and harness cleanup status separately and do not interpret a screenshot captured *after* MainUI takes the DRM plane as a game frame.
4. Improve `tools/analyze_perf.py`: report signed per-frame residuals, duplicate/missing/out-of-order frame IDs, source-order preservation, explicit phase windows, and the number of frames whose `T2P_SLOW_FRAME` records are **not present**. Its current automatic "<1000ms means warmed up" heuristic cannot define gameplay. Do not use incomplete slow-frame samples to certify gameplay P95/FPS.
5. Unit tests must cover inconsistent target HZ, PID reuse, stat names with spaces/parentheses, log truncation, expected shader STOP vs cleanup failure, source capture identity changes, stage coverage and negative frame residual.
6. Respect the new synthetic shader tests but add an actual **GLES driver** fixture for cbuf texture lane addressing, f16 conversion, multiple rows and state invalidation. Passing 33 host tests does not validate a Mali fragment output.

**Gate:** independent analysts can reconstruct *which exact build/phase/input* produced each complete presented-frame distribution, and no test falsely reports playable gameplay on a shader STOP.

### 22.4. P1-PROFILE — The largest cost is STILL unoptimized and still needs attribution

**Additional recent on-device phase averages** from `evidence/newgame-11/progress.json`:

| Ending frame, 60-frame interval | Elapsed ms/frame | Replay ms/frame | Present-to-submit gap ms/frame |
|---|---:|---:|---:|
| 241 | 633.294 | 264.786 | 348.482 |
| 301 | 638.289 | 245.525 | 380.177 |
| 361 | 598.540 | 294.150 | 297.407 |
| 421 | 563.491 | 262.929 | 293.307 |
| 481 | **359.921** | **192.932** | **155.721** |

These are **phase averages, not P50/P95 gameplay**, and their drop near frame 481 might reflect loading-phase changes, not a code optimization. They still show **two large CPU/wait/render buckets**, whereas 30 FPS requires a correct frame every 33.33 ms.

**Next profiling PR**, modifying the runtime only after a representative, reproducible scene exists:

- Sample guest PCs and Horizon SVC caller/latency for the present-to-submit gap. Separate guest IL2CPP compute, memory allocation/GC, loader/decompression work, guest-ZRAM faults/restore, IPC, intentional waits and runnable delays with **exclusive elapsed and actual thread CPU**. Correlate with target core MHz/thermal and thread schedstat; a high Linux CPU percentage alone is insufficient causal attribution.
- Within NVN replay, aggregate counts and exclusive CPU/wall ns for **queue parsing, command callbacks and locks, shader lookup/link, texture resolution/BC materialization, uniform staging/upload, vertex/index conversion, FBO changes, GL state updates, draw and GPU completion waits**. Bucket by shader pair and render-target identity; include the new 39–41 guarded programs only if actually drawn.
- Use bounded ring-buffer snapshots once every 60 frames, not per-draw printf. Measure ON/OFF observer overhead on the *same binary*. Require >=95% accounted time and <5% overhead before deciding that "cbuf is the bottleneck" or "Unity itself is too slow".
- Check whether the <33.33 ms target is even theoretically reachable from the **top three measured exclusive hot spots**. If the largest one is small, batch superficial GL tweaks will not yield the required ~10×–20× improvement.
- Use a complete presentation serial stream to compute throughput and P95; distinguish loading, menu, tutorial, stationary gameplay and moving gameplay.

### 22.5. P1-MEM/REPLAY — Prioritized performance experiments after P0

**Rank 1 — Guest ZRAM thrash.** The cold250 arm still has the strongest *reported* directional improvement. Implement separate wall/CPU timing around compression, restore, locks, scanner, mprotect/madvise and fileback; the current "cpu-...-ms" fields use MONOTONIC elapsed time. Run three matched same-build/scene controls for cold10, cold100, cold250, cold500; then, separately, scanner period/budget changes. Measure frame **P95/P99**, compressor CPU ns, repeated refaults, MemAvailable/CmaFree, swap, order-4 kernel pressure and New Game scene-load correctness. Raise a cold threshold only if RAM headroom survives it; never default to the diagnostic 32 MiB memory floor.

**Rank 2 — Guest gap.** If per-thread profiles identify a large repeatable Horizon/SVC/guest-memory callback, implement a narrow ABI-preserving cache/fast path with exact read/write epochs and negative fixtures. If time is intrinsic Unity simulation or IL2CPP, distinguish repetitive per-frame canvas/mesh/GC work from one-time loading and from paging; test a title-specific quality option only with a verified owner and source identity. Do not edit proprietary game objects indiscriminately.

**Rank 3 — NVN replay.** Select the one **largest measured** class and change only that class. Candidates remain descriptor lookup invalidation, repeat BC atlas refresh, redundant framebuffer/state churn, VBO/index reallocation and glFinish/fence waits. Follow §21.8 for exact invalidation and serial guarantees. The known `LC2_CBUF_SUBIMAGE` arm produced no demonstrated gain: do not redo it. There is a remaining **1024×1 RGBA32F minimum upload (~16 KiB)** for 16–368-byte cbuf contents: if (and only if) real per-frame profiling shows uploads matter, allocate the full logical 1024-wide texture once, update **only dirty RGBA texels**, and explicitly zero stale tail lanes when bound size shrinks; do not blindly change shader row addressing. The static range reports for shaders 39/40 make a finite touched-range experiment feasible, but the runtime must continue honoring the full declared resource and aliasing contract.

**Rank 4 — GPU-bound scenes only.** The earlier generic ZERO_RENDER_SCALE=2 static-menu test was neutral. Do not reattempt it as the first optimization. Once gameplay exists, identify the owner of the 1920×1080 intermediates and profile bloom pairs on Mali; quality reductions require validated GUI and visual outcomes. Changing 720p raster size does not make guest CPU work disappear.

**Rejected shortcuts:** flush-only as a replacement for GPU completion; disabling ZRAM/file backing or system swap under current memory pressure; dropping shader draws/TEST substitution to inflate throughput; bypassing the renderer's GPU budget and minimum-memory admission; copying West of Loathing's Unity field offsets without a Lamentum-specific owner.

### 22.6. Corrected priority table: NEW work, not completed work

| Order | Implementation / experiment | What to produce | Stop/go |
|---|---|---|---|
| **0** | **Build/test all 42 entries including program 41** | New full log hash, installed ELF SHA, live New Game KMS sequence, shader-guard receipts | New shader frontier or verified controllable game scene |
| **1** | **Scene and shader visual parity** for 38–41 | Stage+pair identity, actual bound cbuf lengths, UBO slot, probe guard, blend/alpha, screenshots | Any unknown feature fails closed, no silent TEST rendering |
| **2** | **Close remaining sampler/observer bugs** | Remote HZ, stable PID/TID, signed frame residuals, full-run provenance and cleanup | No false clean-gameplay report |
| **3** | **Complete CPU/replay attribution** | Guest gap + replay top-3 exclusive costs, complete frame distributions, <5% overhead | >=95% attributed before performance modifications |
| **4** | **Re-run ZRAM cold250 safely** | Three A/B pairs; cold100/250/500, New Game load + gameplay, P95 and RAM | Never accept an OOM/memory-floor regression |
| **5** | **One proven hot-path change** | Before/after profiler bucket, actual full-frame P95, exact KMS/game parity | Effect must exceed noise and be repeatable |
| **6** | **Conditional cbuf partial updates** | Bytes uploaded, GL call timing and full-frame changes | Only if cbuf bucket genuinely dominates |
| **7** | **Conditional Mali/720p/GLsync optimization** | Verified owner/gpu-bound cause or correct resource fences | Original visual/sync semantics preserved |
| **Final** | **Gameplay release acceptance** | Three independent 60 s **correct gameplay** runs, complete P50/P95 <=33.33 ms, P99, power/thermal, audio/save/controller/cleanup | Only then label the port 30 FPS |

**Run acceptance and repository hygiene:** keep code/control shader blobs and original game resources owner-local; publish only independently authored tools, hashes, derived IR access contracts, screenshots/evidence suitable to distribute, and stop reasons. For every PR pin HEAD/ELF/owner image and host compiler commit; preserve old working binaries and use the Spruce principal path. When the source changes during a review, **refresh HEAD first** rather than blindly carrying forward the previous "current" audit.

*This section audits committed code and published test receipts. The editor of this roadmap did not run hardware tests or rebuild the title.*

## 23. Current HEAD ffbe7ac: build213 frontier, gameplay and FPS priorities (2026-10-20)

> **This is the current authoritative execution plan, superseding the older status and priorities in §§0–22.** Audited source: [ffbe7ac](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/ffbe7ac14da551b78dcf418717c60489e22e0862). Latest device evidence: [newgame-12](../evidence/newgame-12/README.md), build213. This is a GitHub source/evidence reassessment, **not** a new on-device run or a claim of achieved gameplay/30 FPS.

### 23.1. Source-audited implementation status

| Category | Already done and verified | What remains |
|---|---|---|
| Input/menu | Title, Options, New Game configuration, controls, Loading. Correct agent Confirm **EV_KEY 305** and Back **304**; live KMS and PID/starttime receipts | True first-world scene, physical controller movement, audible audio and save/load |
| Shader catalogue | **42 total entries, including seven TEST substitutes**, indices 0–41; program38 c4/UBO1, guarded 39 c3/UBO0 (min 220B, disabled probe), guarded 40 c3/UBO0 (min 240B), program41 normal→color fragment | New **vertex program42** and an unknown subsequent tail; setup admission does not establish live draw/pixel parity |
| Device lifecycle | tools/device_principal_test.py distinguishes guest stop **exit 4**, cleanup failure **exit 3**; newgame-12 has cleanup_errors=[] and restores MainUI/CPU online mask | Improved process/ELF/log identity and observer tests; do not equate cleaned-up shader STOP to playable game |
| Existing performance probes | NVN_PROFILE splits present-to-next-submit gap and NVN replay. LC2_CBUF_SUBIMAGE is already default-on; one generic 720p ZERO_RENDER_SCALE=2 test was near-neutral | Complete attribution of the two expensive stages and a scene-controlled FPS benchmark |
| Known rejected shortcuts | glFlush-only submit cannot prove GPU completion; unsafe async/recycled command buffers previously failed | Keep synchronous completion, shader correctness, 420MiB GPU cap and diagnostic-vs-production memory boundaries |

**Latest exact stop:** build213, last present **516**, ZERO_SHADER_NOT_PINNED, raw log SHA-256 **a09da06e9b4679ddc203007cdcca8914a03a138de9fcb279024df553ea8520f2**. Installed ELF SHA-256 **7c5c8e85e55d9b95782900af267787a50b885bfe6290d379dc49814b65eebaca**. newgame-12 sampled **47MiB minimum MemAvailable**, with **T2_MEMORY_FLOOR_MIB=32**, **T2_GZRAM_COLD_MS=250**, shader dumps enabled, and experimental **LC2_INPUT_MIN_HOLD_MS=120**. This was an owner-supervised **diagnostic** loading run, not a production-safe memory policy or gameplay performance result. A prior run used different input settings; do not treat it as one-factor FPS A/B.

**Historical corrections that remain binding:** old automatic navigation mislabeled Back code 304 as Accept, an early latest-end.log omitted a later shader stop, and the supposedly new studio splash said **Loading...**. Require a complete final log and game-owned live screenshot, not a frame counter or excerpt.

### 23.2. P0-S42: fix the new vertex shader and GLSL cbuf alias collision

The **exact next missing shader** in evidence/newgame-12 is **vertex**, code **2304B** SHA-256 **301af8ced90e7e506eb4d5ace0dfabd65453557bac79a74dfebacef7396b3098**, control **2176B** SHA-256 **1307789791808c82c0b5c7a141f34ef4780a3ec430630b1588b0803e4ffba4fe**.

The saved evidence/newgame-12/next-shader-names.json identifies original SPIR-V **OpName c1, c3**, but SPIRV-Cross emits GLSL **c1, c3_1** because of a name collision. Original c1 is a literal bank; c3 is an application bank. **c3_1 is a compiler alias, not a hardware bank or binding ordinal.** Current tools/append_program.py accepts cN only, and tools/float_cbuf_contract.py also checks cN, so the compiler alias path requires an actual fix.

1. In the owner-private workspace, locate the exact dumped shader code/control bytes and check full SHA-256, lengths, stage, compiler executable identity and full flags. Do not publish original game shader bytecode, Switch image, keys or saves.
2. Disassemble unchanged SPIR-V and enumerate each resource **result ID, OpName, DescriptorSet, Binding, Block/NonWritable decorations, types, strides and access chains**. Correlate original IDs against SPIRV-Cross reflection and emitted GLSL identifiers. Write a hash-pinned mapping: original resource ID → original c1/c3 name → c1/c3_1 GLSL alias → literal/application kind → NVN stage and slot. **Reject ambiguous or missing provenance.**
3. Extend tools/append_program.py to accept this **verified resource identity map**, never a generic rule that strips every suffix. The expected original c3 maps to NVN **UBO0** under the previously proven hardware bank = NVN slot +3 contract, once original decorations confirm it. Preserve the same alias consistently in shader source and host uniform metadata. Keep build202's c4→UBO1 regression guarded.
4. Extend tools/float_cbuf_contract.py or add a companion validator for **explicitly mapped aliases**, preserving exact finite, read-only, statically indexed accesses, bound sizes and rejection of dynamic/unknown/writable/atomic/SSBO operations. Determine minimum bytes from the maximum actual access, not declaration size alone.
5. Specialize original c1 only after validating its literal values, f16 conversion and usage; do not inadvertently eliminate c3. Preserve bitcast versus numeric-conversion semantics, shader varying outputs and the actual fragment partner. Check RGBA32F packed addressing **x=(word>>2)&1023, y=word>>12, lane=word&3**, including rows and zeros.
6. Add synthetic fixtures: c1 and c3 renamed c1/c3_1; reversed declaration order; wrong SPIR-V ID; ambiguous collision; duplicate resource; unknown bank; incorrect vertex/fragment stage; cbuf one byte too short; unsupported write/dynamic index; literal specialization; unchanged c4→UBO1; code/control SHA mismatch. **Negative fixtures must refuse input.**
7. Compile ESSL310 with the pinned compiler and link with the actual stage partner using a supported GLES path. Host compile does not prove visible pixels; keep that a separate device gate.
8. Append exactly **one** index **42** entry, raising total to **43** including the same seven TEST substitutes. Check the **existing 42-entry prefix byte-for-byte**, shader hashes, link metadata and guards. Do not rebuild the whole catalogue; it can revert hand-validated fixes.
9. Build from the separately recovered **435-file source baseline** with manifest validation, pin owner-image/container/compiler identity, back up build213, verify new ELF SHA on the device, then enter New Game through the Spruce principal flow with visually confirmed EV_KEY305 input and a live KMS sequence.
10. Archive the **entire final log** with code/control hashes, shader stage, live PID, frame serial, KMS and memory. If the old missing identity disappears and another fails during program setup, this proves a **new shader frontier**, not program42 pixel correctness. Only call the new program pixel-validated after observing its draw, correct bound UBO, geometry and resulting actual screen content.

**PASS S42:** matching original resource provenance, correct UBO binding, unchanged old 42 entries, positive/negative host tests and no old 301af8… shader stop. **STOP:** guessed alias, unknown operation, wrong visuals, broken menu or replacing this shader with a blank TEST substitute.

### 23.3. P0-G0: move from New Game/loading to real playable pixels

Build a **state-verified input driver** around tools/lamentum_pad_contract.py instead of enabling the deprecated automatic scripts: **IDLE_SPRUCE → TITLE → NEWGAME_SELECTED → CONFIG → TUTORIAL/CONTROLS → LOADING → FIRST_WORLD → MOVEMENT → INTERACTION → AUDIO/SAVE → CLEAN_EXIT**. Each transition requires exact live game PID/starttime before/after capture, actual highlighted menu choice, frame serial and balanced EV_KEY press/release. A pre-selected frame number is not a reliable UI-state signal.

1. Refuse concurrent game/device access; back up owner saves and original Spruce CPU mask. A screenshot taken after the game exits is a **MainUI cleanup screenshot**, not Lamentum gameplay.
2. Use live KMS captures to choose New Game, confirm the configuration page and follow the controls prompt. The **120ms input hold** used in build213 is experimental, not a general solution: count guest Npad samples to prove one press per action without lost edges or repeats. Later validate physical controller input.
3. For apparent loading hangs, distinguish **new exact shader STOP**, continuing ROMFS/shader/scene initialization, guest IPC/SVC or page-fault stalls, and stale/black GPU presentation. Inspect the full log, thread CPU/schedstat, live frame serial, texture publication and exact last operation. Do not rewrite a shader when the actual cause is blocked IPC or memory.
4. Continue the shader-tail loop only from exact captured code/control identities. A low-overhead **creation-time shader identity census** may expose several next programs in one run before first draw, reducing slow cross-build/device cycles. Do not publish binaries or assume an arbitrary RomFS byte pattern is a shader.
5. The seven TEST-only entries were not drawn in the historical menu frame, but may occur in **gameplay**. Record real pair census and implement demanded capabilities (SSBO skinning, sampler3D/probe, MSAA/sample operation, varyings, alpha/stencil/depth) with exact semantics and fail-closed guards. Do not treat a TEST output as verified game rendering.
6. Once a program links but pixels are wrong, inspect **actual pair, cbuf stage/slot and bounds, sampler handles, textures, framebuffers, viewport/scissor, matrix, color mask, blend/stencil/depth**; compare real gameplay KMS captures with a known-good menu screenshot. A nonblack pixel count alone does not validate a scene.
7. Define first playability by **character position changing after controller movement**, a rendered world, an inventory/dialogue/object interaction and no unsupported shader stop. Then separately verify **audible** audio, save → quit → cold launch → load, and restored player/inventory state. A sound counter alone is not audible music.
8. Every run must restore MainUI, original CPU mask and supervisor identity without orphaned game processes. A shader STOP with cleanup_errors=[] passes **cleanup only**, not the game.

**PASS G0:** ≥30 seconds of actual controllable world rendering, visible movement and one interaction. **PASS G1:** audible music/SFX, cold save/load and safe long-run lifecycle. Do not measure title/menu FPS as gameplay FPS.

### 23.4. P0-I0: fix profiling and harness accuracy before any new FPS conclusions

**Code issues confirmed in the repository**, not proposed features that are missing entirely:

1. **tools/perf_sample.py uses the host CPU tick rate.** Its current lines computing cpu_percent and cpu_ms_per_s call the host os.sysconf('SC_CLK_TCK') despite collecting /proc counters from the remote TSPS. Have the remote Python sampler report its own SC_CLK_TCK, boot ID and monotonic time. Convert interval CPU time as **1000 × delta(utime+stime ticks) / target_HZ** and CPU utilization as **100 × delta_ticks / (target_HZ × delta_elapsed_seconds)**. Do not infer 78% core use from the old readings until corrected and measured again.
2. Parse the remote /proc/PID/stat and /proc/PID/task/TID/stat by splitting at the **last closing parenthesis** of comm, not at arbitrary spaces. Capture starttime (field22), user/system ticks (14/15), process and thread identity and kernel boot ID. Maintain continuity by **boot ID + PID/TID + starttime**, not PID alone. Preserve all threads, not only the most CPU-heavy subset. Add schedstat CPU/runnable delays, page faults, major faults, memory pressure and actual governor/frequencies.
3. **tools/analyze_perf.py sorts samples by frame serial** and thereby hides out-of-order/duplicated events. Preserve log order, line/byte offset, run UUID and complete presentation ID set. Reject repeated IDs, resets and changes of log inode unless a new run is explicitly declared. Its field parser only accepts unsigned numeric text: accept signed residuals and malformed/missing values explicitly.
4. **Do not clamp negative accounting errors to zero.** The current parser applies max(0, period minus measured stages), concealing overlaps or erroneous clocks. Report a **signed residual per frame**; distinguish exclusive versus inclusive stage timers and CPU/GPU overlap. Flag impossible sums and exclude such runs from acceptance instead of silently “fixing” them.
5. The current automatic “first frame whose period is below 1000 ms is warmed up” heuristic is **not a scene detector**. Require an explicitly identified gameplay phase with live on-screen confirmation, exact starting/ending serial, loading markers and independent monotonic timestamps. Slow-frame-only records have **biased sampling** and cannot prove actual P95 or physical presented throughput: report coverage and incomplete samples.
6. Keep tools/device_principal_test.py **no-parallel-game fail-closed guard and exit contracts (0: clean TIME_LIMIT, 3: cleanup failure, 4: guest STOP)**. Add exact installed ELF/catalogue/owner-image SHA, run UUID, log inode + start byte offset and bounded incremental polling. Retrieve/hash the **final entire log once** rather than repeatedly parsing multi-MiB files. Parent scripts must not overwrite a correct shader STOP and cleanup receipt with a later harness timeout.
7. Each real KMS image must be tied to **the unique live game PID/starttime before AND after the capture**, present serial and input receipt. Mark a returned MainUI/Recents capture as cleanup_only. Collect memory/PSI, CmaFree and kernel order-4 allocation pressure in bounded windows; back up saves and verify the original CPU online mask after the run.
8. Add tests for target HZ **100/250/1000**, task comm containing spaces/parentheses, PID reuse, missing TIDs, wrap/reset, negative residual, duplicate/out-of-order serials, 60%-coverage slow-frame logs, STOP with successful cleanup, stale screenshot, log truncation and interrupted SSH. Invalid profiling runs must set **benchmark_valid=false**.

**I0 PASS:** any independent reviewer can reconstruct the exact binary, environment, frame sampling coverage, scene, target CPU units, input sequence and STOP versus cleanup result. A one-off difference of 2–3% in local replay cannot be accepted before this gate.

### 23.5. P1-T1/T2: attribute both large frame phases instead of trying random GL tweaks

From evidence/newgame-11/progress.json, build212 reports **60-frame arithmetic averages during loading**, not gameplay FPS:

| Ending serial | Complete frame interval | NVN replay | Present-to-next-submit gap |
|---|---:|---:|---:|
| 241 | 633.294 ms | 264.786 ms | 348.482 ms |
| 301 | 638.289 ms | 245.525 ms | 380.177 ms |
| 361 | 598.540 ms | 294.150 ms | 297.407 ms |
| 421 | 563.491 ms | 262.929 ms | 293.307 ms |
| 481 | **359.921 ms** | **192.932 ms** | **155.721 ms** |

At the fastest of those listed intervals the total is **~10.8×** the 33.33 ms target. The last interval may simply contain less loading work; it is not proof that a recent change accelerated gameplay. Both **replay** and **guest gap** remain too large, and a small postprocessing/CBUF change alone is insufficient.

**T1: guest/present-to-submit gap**

1. Mark previous present end, next guest frame start, next command-record creation, command publication and replay start using **CLOCK_MONOTONIC_RAW**. Track real host thread **CLOCK_THREAD_CPUTIME_ID** and target per-TID schedstat runnable delay separately from elapsed wall time.
2. Attribute mutually exclusive elapsed categories: Unity/IL2CPP execution, allocations and GC, initial scene deserialization, Horizon SVC/IPC, guest-memory page restoration/ZRAM faults, file-backed storage I/O, intentional sleeps, locks/queue waits and runnable-but-unscheduled periods. Record guest caller PC and sample rates in a bounded preallocated ring; never log full PC for every instruction/fault.
3. Map costly guest PCs to **owner-original NSO plus metadata hashes** to determine whether they are scene-load-only routines or repeated Unity PlayerLoop/Canvas/animation/physics paths. If a large gap occurs while a thread is runnable but off-CPU, inspect scheduler/core online state. If guest main is waiting on memory, investigate M1 first; do not just call the residual “Unity CPU”.
4. Partition >95% of **wall time** using non-overlapping spans. Actual CPU time is a separate measure that may overlap GPU work. Repeat once with instrumentation OFF on the **same executable**, requiring <5% tracing overhead before accepting a causal diagnosis.

**T2: NVN/GL replay**

1. In native/nvn_replay.h, native/nvn_render.h, native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_queue.h and command/descriptor helpers, aggregate **exclusive CPU and wall nanoseconds** for command decoding, guest-to-host copying, shader lookup/link, texture descriptor resolution, BC materialization, cbuf staging/uploads, vertex/index conversion and allocations, FBO transitions, GL state calls, draw submission, eglMakeCurrent, glFinish and other waits.
2. Capture invocation counts, bytes copied/uploaded, unique texture/UBO generation, shader pair, target format and size. Separate cold first-use shader/resource costs from recurring steady-state cost. Do not include program42 as a draw hot spot unless a **real draw receipt** has been recorded.
3. The low present finish-ms historically measured does **not** prove zero GPU wait: GL driver calls may block before the final finish. Use disjoint-checked GPU timer queries only if the real Mali GLES stack supports them; do **not** glFinish after every pass to time the GPU.
4. Ensure exclusive replay buckets account for >=95% of replay wall duration, with CPU running and waiting separated. Dump one summary every 60 frames rather than megabytes of hot-path printfs. Confirm A/B profiler overhead <=5%.
5. Perform scene-controlled tests **after real movement works**: stationary world, moving world, dense sprites, UI/inventory, bloom/effects, load transition. Compare actual complete frame **P50/P95/P99 and real present throughput**, not just replay CPU milliseconds.

**T1/T2 decision:** guest fault/compressor work -> §23.6; guest CPU or SVC work -> §23.8; high replay GL CPU -> §23.7; verified GPU-bound intermediate -> title-specific quality preset; new shader STOP -> §23.2. Never trade correctness for a better profiler number.

### 23.6. P1-M1: controlled ZRAM, resident memory and file-backing optimization

The historical **336501 compressions and 274244 faults** signal possible thrashing, but are **counts, not proof of CPU expense**. An earlier cold=10→250ms run suggested a directional effect, **not** a replicated stable-gameplay gain. The build213 minimum **47MiB MemAvailable with a 32MiB diagnostic floor** does not give comfortable memory headroom.

1. Instrument **compress, restore, scanner, page protection, locks, dirty restart and file-backed read** separately using monotonic **wall** and **thread CPU** nanoseconds. Existing labels such as cpu-...-ms may use MONOTONIC wall time; fix naming before interpreting results. Record per guest-page generation: faults, time since prior access, quick recompression/re-faults, original/compressed bytes and owner memory pool.
2. A/B **cold=10, 100, 250, 500ms** under identical executable, phase, input hold, BC quota/fileback, monitoring, runtime shader and GPU settings. Interleave **at least three** matched pairs and record actual scene/loading status; build211 versus build213 is **not** a valid memory A/B. Only **after** cold is understood vary scanner period/budget in a separate experiment.
3. Require frame P50/P95/P99, actual thread compressor CPU ns, restore count and stall P95, MemAvailable/CmaFree/PSI minima, major faults, VmRSS/SwapPSS, swap I/O, storage latency, kernel order-4 warnings and GPU residency. A lower scan count but worse frame tails or OOM is **failure**.
4. If one guest range is refaulting repeatedly, consider a **generation- and owner-pinned do-not-compress policy** for just that proven range, charging all retained bytes against the same memory budget and preserving guest pool alias/invalidation semantics. Validate allocation/release, writes, fileback, CPU read and in-flight GPU ownership.
5. Retain the existing lossless 8192×4096 BC3 striped upload/deferred loading, file backing, the 420MiB GPU texture cap and system swap. Do not disable global ZRAM or increase a diagnostic floor downward toward zero. A production memory safety policy needs a separate long-run qualification at the default launcher floor of **96MiB**.

**M1 PASS:** repeatable whole-frame or guest CPU savings with healthy memory and no corrupted assets/save, kernel pressure, unexpected page faults or cleanup regression.

### 23.7. P1-R: prioritized NVN/GLES speedups once actual hot spots are measured

**Existing tested approaches to avoid repeating:** glTexSubImage2D replacing repeated full allocation is **already present and default enabled** (LC2_CBUF_SUBIMAGE); it has **no established overall gain**. Generic ZERO_RENDER_SCALE=2 showed period P50 ~579.3→577.7ms with the guest gap unchanged; default remains 0. MOMO_SUBMIT_FINISH=0 or glFlush-only is **not completion**; synchronous ownership remains the correct baseline.

**R1 — CBUF transfer volume:** native/nvn_render.h still uses **1024 RGBA32F texels per row**, so even a one-row 16–368-byte payload can involve a **16KiB GL update**. Instrument active bytes, upload bytes, unique content generations, pair and GL CPU time. Only if the measured bucket dominates, keep the shader's logical texture dimensions while issuing **dirty RGBA texel** glTexSubImage2D rectangles; zero stale tail lanes when a range shrinks. Never change x/y/lane addressing or sample another buffer after source generation changes. Verify 16, 220, 240, 368-byte and multi-row buffers, signed/NaN bit patterns, shrinking ranges, context destruction and GPU in-flight use. Dedupe on **exact bytes+generation**, not hash alone.

**R2 — descriptor/texture resolution cache:** if actual repeated pool lookups dominate, key by pool generation, descriptor index, sampler identity/generation, texture view/mip/format, backing write epoch and EGL context. Invalidate on TextureWriteTexels, backing alias writes, pool re-register, resource destruction, eviction and surface/context recreation. Keep proven reserved-prefix/null-texture semantics; a previously wrong sampler offset generated float-bit-pattern pseudo-handles.

**R3 — redundant GL/FBO state:** first count would-skip for glBindFramebuffer, glUseProgram, glActiveTexture, glTexParameteri, blend/depth/stencil and viewport/scissor. Then suppress **one** call family per PR only with context-specific shadow state and invalidation whenever any native present helper changes GL state. Tile discard or glInvalidateFramebuffer is safe **only after the last consumer** of an intermediate bloom attachment. Do not drop UI/stencil draws for speed.

**R4 — vertex/index and command-copy churn:** measure glBufferData/reallocation frequency, memory copies and conversion CPU by shader pair. Consider preallocated/ring staging only if real cost is significant, with correct guest write epochs, resource generations and NVN/GPU serial fences. Extra resident memory may amplify page faults.

**R5 — texture atlas/materialization:** identify unnecessary BC decompression/refresh and repeated glTexImage by texture ID and write epoch. Reuse lossless native 8192×4096 BC3 decoding and 128-row striped upload. An owner-private ASTC side cache or dirty tile upload is conditional on tested device support, alpha/sRGB parity, immutable content proof, disk capacity and exact resource lifetime. Do not replace proprietary source assets in Git.

**R6 — shader lookup/compile:** profile program-link and uniform location misses separately during **loading** and warmed-up gameplay; precompute metadata and cache validated GL program/context generations only when repeated compilation actually occurs.

**R7 — owner-specific 720p/postprocessing:** the physical screen is **already 1280×720**; the internal **1920×1080** resources belong to a separate guest pipeline. First prove which Lamentum IL2CPP/Unity component creates them and map consumers, UI matrices, FBO, bloom pair and input coordinates. Test a reversible 720p intermediate/effects preset only for a **proven GPU-bound gameplay scene**. The prior generic scaler was neutral and cannot remove guest CPU work. Preserve exact graphics and readable UI.

**R8 — GPU async/fences:** keep OFF until GPU wait is specifically proven material. Previous **NVN_COMMAND_REUSE_BEFORE_COMPLETION** and **EGL_BAD_SURFACE** are hard correctness stops. No fake command completion or reuse of unfenced GPU-read memory. Require correct serial ownership, fence and EGL lifetime fixtures before any opt-in A/B; frame P95 and pixels must remain valid.

**Rank by real exclusive cost, not by the conceptual appeal of a trick.** A 2ms CBUF gain has little relevance when the guest gap is ~156ms and replay ~193ms during a comparable interval.

### 23.8. P2-GUEST: Unity-side performance when the guest actually owns the delay

If corrected target-side CPU profiling attributes major recurring cost to **Unity 2019.4 IL2CPP** rather than the adapter, GL-only optimization cannot close the full frame budget.

1. Hash-pin original owner main NSO/metadata, correlate guest PC samples with actual functions: PlayerLoop, script Update, GC/allocations, scene deserialization, sprite batching, UI Canvas rebuild, physics/animation, and Horizon service calls. A loading-phase hotspot is not necessarily a steady-gameplay hotspot.
2. Try genuine in-game graphics/Noise options first and record which pass or guest component they actually modify. Never invent a Handheld/TV switch or copy West of Loathing title-specific UpRender offsets.
3. Only if a **Lamentum-owned** quality/RenderTexture/resolution component is proven, use a reversible owner-local and SHA-pinned experiment (no proprietary game edits committed). Verify projection, text, alpha, UI hitboxes, input and graphics parity on actual device.
4. For a costly adapter-controlled SVC or memory translation path, create a small ABI- and side-effect-equivalent cache/fast path with write-epoch and alias invalidation, negative tests and explicit rollback. Do not patch guest timing or Unity deltaTime merely to inflate a frame count.
5. Test CPU affinity/governor effects only from target topology/frequency and schedstat evidence with **full CPU online restoration**. No global swapoff, unsafe clock overrides, min_free_kbytes experiments or deletion of the memory cap.
6. Use **5 →10 →15 →20 →30 FPS** as transparent milestones after G0; continue to define success strictly as complete-frame P95<=33.33ms. If persistent correctly measured hundreds-of-ms guest work cannot be reduced, report 30 FPS as **unproven or infeasible under current runtime**, not as guaranteed.

### 23.9. Updated PR execution order, validation and deliverables

| Order | Task / proposed PR | Concrete deliverable | Gate |
|---:|---|---|---|
| **0** | **S42: original shader c1/c3 alias mapping** | Exact stage/resource manifest, host tests, append-only program42, new hashed build and next-stop log | Correct UBO0 binding; original 42 entries unchanged; no silent TEST shader |
| **1** | **G0: first controllable game scene** | Live New Game→world KMS/PID/input sequence, movement and an interaction | Genuine correctly rendered world, no unsupported-stop during play |
| **2** | **I0: target-correct performance analyzer** | Remote HZ, PID/TID starttime, signed residuals, presentation coverage and state-aware harness tests | Two independent runs comparable without guessed units or phases |
| **3** | **T1/T2: guest/replay attribution** | Low-overhead exclusive timed buckets and complete frame ledger | >=95% accounted, <=5% observer overhead |
| **4** | **M1: ZRAM/fault A/B** | Three interleaved repeats cold10/100/250/500 with memory safety | Whole-frame gain without pressure/OOM/regression |
| **5** | **R1–R6: the largest real replay cost** | One subsystem patch, before/after log and KMS parity | P95 full-frame improvement greater than noise |
| **6** | **R7/R8: conditional quality/GPU pipeline** | Exact owner/render target or serial/fence evidence | Correct visuals and GPU completion, measurable frame gain |
| **7** | **G1: full player/audio/save release gate** | Human controller, audible SFX/music, cold save/load and cleanup receipts | Functional port, with honest measured FPS |
| **8** | **F30: real stable 30 FPS** | **Three independent warmed-up 60-second gameplay runs**, complete presented serials and scenes | **P50 and P95 <=33.33ms**, P99 target <=50ms, no recurring >100ms stalls, no lost/incorrect frames |

**Next owner run evidence folder:** evidence/newgame-13/ should include exact source/ELF/compiler/owner image identifiers, separate original code/control SHA only (no bytes), old catalogue prefix equality, input phase and EV_KEY 305 receipts, real PID-bound menu/config/controls/loading/world captures, final raw log SHA + byte size, shader guard/draw counts, pressure samples and cleanup.json. A new STOP with cleanup_errors=[] is **good cleanup but FAILED gameplay**, and must be reported as such.

**Safety and reproducibility:** run the baseline SHA-256 manifest check from the separate **recovered GPL source root**; then host unit/C fixtures, full adapter cross-build, install + independent ELF hash, quiet owner-controlled principal launch and cleanup/CPU mask validation. Keep old known-good executable and save backups. The diagnostic **32MiB floor** and AW_RELEASE=0 shader dump are *not* production defaults; production still requires separate validation at the default **96MiB floor**. Do not run scripts with their owner's hardcoded IP/workstation paths against another handheld.

**Hard acceptance separation:** (a) program appended, (b) linked/accepted, (c) actually drawn/pixel-validated, (d) actual controllable world, (e) audible audio/save/reload, (f) complete-frame stable 30 FPS. Passing one does not imply any later milestone. No 30 FPS result is claimed by this review.


## 24. Current build216 execution priorities and next implementation PRs (2026-10-20)

> **Source of truth for detailed instructions:** [Current Gameplay Bring-up and Performance Plan](current-gameplay-performance-plan.md). This section explicitly supersedes the historical action status in §§0–23 while retaining those sections as technical background. Review covers code through [54e031d](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/54e031d396c559ab90c4de94f54da99a73059b14), without a new on-device test.

### 24.1. Completed and still missing

- **Done:** New Game navigation and Loading verified with the corrected EV_KEY305/304 mapping; shader catalogue entries **42–44** hash-pinned and appended; original c1/c3 bank aliasing guarded; ten narrow real-Mali GLES cbuf fixture checks; build216 ELF and complete newgame-15 log hash pinned; MainUI and CPU state restore cleanly.
- **Not done:** no first playable level/world, physical controller gameplay, audible audio, cold save/reload, or valid gameplay FPS. **Newgame-15 had no shader stop**, but after 900 seconds it was still loading; entry44 **zero draw-guard receipts**. The ROMFS read high-water at EOF is **not** proof that all assets were loaded. Newgame-16 budget 2400 was **rejected** because the historical cap was 900; source cap now 1800; newgame-17 has no committed completed outcome at this review.
- **Already attempted/available, not new work:** glTexSubImage2D constant-buffer optimization default-on, cold250 guest ZRAM setting, original 8192x4096 BC3 striped decoding/lossless backing, generic render scaling tested near-neutral, and synchronous GL completion retained for correct NVN lifetimes.

### 24.2. Strict next sequence

| Priority | Next PR | Minimum concrete acceptance |
|---:|---|---|
| P0-01 | Build an actual New Game **loading progress ledger** | Time/scene-phased ROMFS **interval-union** read coverage, re-read metrics, shader **draw** counts, texture/guest-page activity, CPU/waits and KMS scene state; classify work vs stall vs wrong pixels |
| P0-02 | Finish or inspect the already prepared **1800-second** owner-local probe | One hash-pinned run with full log and independent cleanup; a clean TIME_LIMIT is not a loaded world |
| P0-03 | Correct existing profiling tools | Target SC_CLK_TCK rather than workstation ticks, PID/TID/starttime+boot ID, complete presentation coverage, signed residual and per-run benchmark-validity tests |
| P1-04 | Measure guest present-to-submit and NVN/GLES replay independently | Mutually exclusive wall stages account for >=95%, profiler overhead <=5%, host CPU ns separated from wall waits |
| P1-05 | Fix the **measured** load bottleneck | Repeatable increase in actual completed asset/scene progress per second, safe memory and correct output; not just a bigger timeout |
| P0-06 | Prove first **real-world draw and interaction** | First entry44 draw if reached; any next original program append-only; correct world pixels, player movement, actual interaction |
| P1-07 | Test only validated renderer hot spots | CBUF small dirty-region uploads, sampler/FBO caching, vertex/BC staging, quality controls, or correct fences **only if their measured cost is material** |
| Release | Validate **playable** state and real 30 FPS | Audible sound, controller, cold save/load and 3x60s gameplay P50/P95<=33.33ms, safe memory and clean Spruce exit |

**Immediate interpretation change:** the ~1.63 gross presents/s in newgame-15 includes menu/navigation and startup and cannot be used as gameplay FPS. A new shader should not be appended merely because entry44 was newly admitted; it was **not drawn**. The highest-value investigation is whether the scene load is progressing, waiting on a missing Unity/Horizon event, or running world logic without correct pixels. Guest-ZRAM cold250 and per-draw GL changes must be tested under a phase-matched, target-correct profiler, not inferred from historical loading frame counts.

**Full step-by-step implementation and QA:** [docs/current-gameplay-performance-plan.md](current-gameplay-performance-plan.md), §§3–11. Original game data, NSO shaders, keys and saves remain owner-private, and device principal-flow tests must never be invoked blindly.


## 25. Build218 post-OOM audit and next steps (2026-10-20)

> **Read this section first.** This supersedes §24's build216/current status; keep §§0–24 as traceable historical source and benchmarking discussion. **Full exact procedures, experiments, test fixtures, safety gates and PR design are in [the current implementation plan §§13–20](current-gameplay-performance-plan.md#13-build218--newgame-20-reassessment).** The source for this reassessment was reviewed at [b35f21e](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b35f21e14662e681e27de9c78cc91ea250f0d4be). No new compilation or device run was performed during this documentation review.

### 25.1. Verified progress since the original 30 FPS roadmap

- **Shader tail:** entries 42–44 from the New Game frontier and a new exact code/control-pinned **fragment45** with four MRT outputs and half-accurate arithmetic have been implemented. The catalogue is now **46 entries (indices 0–45), seven TEST substitutions**. newgame-18 verified vertex44 **link**, and [newgame-20](../evidence/newgame-20/summary.json) verified `sources=0/45` and link-on-native-pair-draw. Pixel/raster correctness, framebuffer attachment parity and first world scene remain unverified. [build218 implementation](build218-entry45.md).
- **Navigation:** measured main-menu cursor bands y=425/475/525/575 and New Game row y=475 replaced blind press counting. A previous attempt in newgame-19 opened Options; its failure is preserved in [menu-ground-truth](menu-ground-truth.md). The new navigation primitive should be reused in every test tool, including the load probe, for both menus.
- **Long load:** build216/newgame-15 ran to 900s without a new shader stop. build217/newgame-17 exceeded its **1800s** internal alarm without a guest TIME_LIMIT stop and was host-terminated after reaching 2176 presents; the harness now has an independent exact-game-process bound. The 20.14s loading sample found **23 presents**, **0.836s main CPU/present**, **1.63s total-thread CPU/present**, zero new ROMFS reads/textures/BC deferrals, and one additional NVN command execution. These are **loading phase** measurements and no representative world FPS has been measured. [Measured CPU and watchdog](time-governor-and-load-cost.md).
- **New termination frontier:** [build218/newgame-20](../evidence/newgame-20/summary.json) reached Loading and frame **709**, linked entry45, and was SIGKILLed with **75 Mali OOM-notifier rows** reporting **725,992 kB** GPU allocation/accounting against **986,064 kB** total RAM. No `STOP status` line was emitted. Post-kill memory and the temporarily blanked screen are **not** safe measurements of pre-kill RAM use. The first post-run KMS screenshot was blank; waking the panel revealed correctly restored Spruce MainUI and CPUs.
- **Existing rather than future optimizations:** per-draw CBUF glTexSubImage2D (default-on, historically **no proven whole-frame win**), BC3 striped decoding, lazy BC upload and owner-local lossless file backing, guest ZRAM cold250, nominal 420 MiB texture budget, synchronous NVN/GLES submission and corrected cbuf hardware banks. Do **not** reimplement or disable these blindly.
- **New tools:** `tools/load_probe.py`, `tools/analyze_load_probe.py` and tests exist at HEAD. They still lack an end-to-end, device-executed collector test and no completed new-probe evidence has been committed. The remote regex is nested inside a Python string and **must be tested after decoding**; do not call its backslashes a proven bug without executing the generated payload. The full-log reread every five seconds and fixed Down presses on the New Game configuration screen are real source-level reasons to harden this tool.

### 25.2. What the GPU OOM changes about the priority order

The **420 MiB GPU texture budget** was designed around deferred/materialized texture reservations; it has **not been demonstrated to cover total Mali driver allocation**. A combined set of color/depth/MRT render targets, transient framebuffer resources, driver-private allocations, duplicate generations or retained textures could account for the difference; **none has yet been isolated**. The target GPU can use shared system memory, so do not add guest ZRAM savings, SD backing size and GPU bytes as though they were independent free memory pools. Do not claim a memory leak merely from 75 notifier lines.

**P0 mandatory measurements:**

1. Record one owner- and generation-scoped NVN/GL allocation ledger for all actual textures, color/depth render targets, renderbuffers, buffer objects and EGL surfaces, including dimensions, formats, levels, layers, samples, GL context, guest pool and GPU fence lifetime. Compare **estimated API storage**, 420 MiB **charged budget**, actual driver counters **if exposed**, and system MemAvailable/CmaFree as independent columns. Avoid reading massive logs or querying expensive driver nodes every draw.
2. Collect multiple **pre-OOM** 30–60s memory snapshots at safe earlier loading phases; identify the top growing live owners and last known good headroom. Correlate dmesg Mali victim PID/time with the game's PID/starttime. An unannotated `Killed` line proves SIGKILL, **not by itself OOM**.
3. Extend allocation admission/safety reporting to uncovered classes **without raising** the existing 420 MiB budget, disabling memory checks or accepting the diagnostic 32 MiB floor as release-safe. The first acceptance gate is a controlled clean fail-closed abort **before** kernel OOM.
4. Only after identifying the owner, test one safe fix: lifetime-verified RenderTexture/FBO reuse; **title-owned** 1080p->720p scene attachment and projection changes; reduced duplicate GL resource generations; correct last-consumer eviction/rematerialization; or verified ASTC side cache for immutable BC textures with visual/alpha/sRGB comparison. Preserve original assets, the shader-prefix identity and GPU queue/fence semantics.
5. Re-run *the same verified scene phase* three times per A/B arm; measure a **real decline in driver or attributed resource memory and safe survival beyond the former failure state**, not merely fewer GL calls. No OOM, scene-pixel regression, missing shader/TEST-path semantics, or save corruption is acceptable.

**Example memory sizing to check:** one 1920×1080 RGBA8 offscreen image occupies approximately 7.91 MiB of uncompressed pixels; four live color MRT attachments occupy about 31.64 MiB **before** depth/stencil, extra levels, tiling or MSAA. This is a lower-bound illustration, not proof those resources caused newgame-20's OOM. The physical screen is already 1280×720.

### 25.3. Main-thread CPU: why shaders alone cannot get 30 FPS

At 0.836 **CPU seconds** per displayed Loading frame, build217 is roughly 25 times beyond a 33.33ms frame budget **on that thread alone**. This is neither world FPS nor a definitive hardware limit, but it establishes a strong reason to trace the actual guest CPU call path. No new RomFS, textures or BC deferrals in that 20.14s window means the static Loading sprite may coexist with a hot Unity/IL2CPP loop, unbalanced Horizon event, repeated memory alias/fault handling, or other CPU work. Those are **competing hypotheses**, not established diagnoses.

Use the existing `MOMO_STACK_SAMPLE_MS`, `MOMO_STACK_SAMPLES` and `MOMO_STACK_SAMPLE_AFTER` sampler in a bounded pre-OOM phase and `tools/analyze_guest_samples.py`. Correlate guest `module.seg+offset` PCs against the **owner-private, hash-pinned** main/sdk/subsdk binaries and native adapter symbols; preserve unresolved addresses. Separate actual thread **CPU** from runnable delay, blocked wait, page restoration and replay GPU wait. Then implement one verified, reversible ABI/logic fix and measure the same real scene-progress marker and full frame distribution. Do not patch guest clocks, fake completion, assume an IL2CPP symbol from an offset, or replace glFinish with glFlush without serial/fence ownership.

### 25.4. Prioritized PR checklist with exact acceptance

| Rank | Work item | Required source/test changes | Acceptance |
|---:|---|---|---|
| **P0-1** | **T0 — reliable probes** | `tools/load_probe.py`, `tools/analyze_load_probe.py`, `tools/perf_sample.py`, `tools/device_principal_test.py`: execute/test actual remote regex, incremental run-scoped log processing, New Game state oracle, correct target CPU ticks, correlated OOM/stop taxonomy, mock-remote fixtures | No false frame count/STOP or stale PID; bounded sampling overhead and valid scene transitions |
| **P0-2** | **G0 — GPU allocation ledger** | Adapter patch at `native/nvn_textures.h`, `native/nvn_framebuffers.h`, GL allocation and EGL lifetime paths; per-class generations, bytes, fences; unit tests | Top memory growth classes and charged-vs-unaccounted resource gap measured before unsafe pressure |
| **P0-3** | **G1 — pre-OOM guard** | Resource-aware reservation/abort path, driver/system pressure signals; identity-safe cleanup | Predictable clean runtime stop instead of SIGKILL on the same dangerous allocation |
| **P0-4** | **C0 — bounded guest CPU profile** | Existing MOMO sampler + `tools/analyze_guest_samples.py`; owner-private PC map, target-correct CPU clock and matched sample-off run | Dominant Loading loop code family identified, overhead <5%, no guessed symbols |
| **P1-5** | **G2 — GPU owner fix** | One owner-confirmed render-target/reuse/residency change; correct shader/fence parity | Memory reduction, safer headroom and progress past the previous failure point with identical scene pixels |
| **P1-6** | **C1 — CPU hot path** | One measured compatibility-runtime fix with unit fixture and rollback | Faster **real scene work** and full-frame P95, not just animation rate |
| **P0-7** | **W0 — actual world** | Scene activation state, fragment45 MRT draw/pixel/GL attachment receipts, TEST-pair census, physical controller and gameplay KMS captures | World correctly drawn and player movement/interactions verified |
| **P0-8** | **PLAYABLE gate** | Music/SFX verification, dialogues/inventory, backed-up owner cold save/load, clean MainUI/CPU recovery | May finally say "playable" |
| **P1-9** | **F0/F1 — gameplay FPS** | Complete 60s world-present timeline for each scenario, CPU/replay/driver breakdown, 3 controlled A/B pairs; targeted renderer/CPU fixes | P50/P95 <=33.33ms in three independent 60s runs **plus correctness**, preferably P99 <=50ms |

**Stop signs:** Mali/kernel OOM, `T2_MEMORY_FLOOR`, incorrect GPU ownership/lifetime, `NVN_COMMAND_REUSE_BEFORE_COMPLETION`, `EGL_BAD_SURFACE`, missing shader or wrong constant-buffer bank, partially rendered MRT, unverified TEST substitute, wrong/blank world, failed save recovery, false KMS identity, or MainUI/CPU cleanup regression. Never run a device principal-flow test while another game/application is active.

### 25.5. First implementation bundle and evidence pointers

**Implement first:** a synthetic remote-collector integration test and incremental counters (T0), then a read-only native GL/Mali allocation-class ledger (G0), then a low-overhead guest CPU PC sample (C0). G1/G2 should be chosen using real allocation growth, not a guessed texture cache. A valid full run must capture the source/ELF hash, exact owner image identity, unique game PID/starttime, scene/cursor state, log generation, phase marker, counter coverage, memory minima, kernel victim evidence when present, and physical capture identity.

**Primary references:** [latest GPU wall](gpu-wall-after-entry45.md) · [newgame-20 summary](../evidence/newgame-20/summary.json) · [half-accurate fragment45](build218-entry45.md) · [measured navigation](menu-ground-truth.md) · [guest CPU/watchdog](time-governor-and-load-cost.md) · [live implementation plan, §§13–20](current-gameplay-performance-plan.md#13-build218--newgame-20-reassessment).

**Status after this audit:** detailed roadmap and current plan updated; **no runtime source changes, new binary, on-device measurements, verified gameplay or 30 FPS** were produced by this documentation edit.


---

## 26. Load-probe 03–07 reassessment: GPU atlas residency, first gameplay and CPU performance (2026-10-20)

> **Read this first.** This section supersedes the implementation order in §§0–25 where their historical status disagrees with the newer committed evidence. This review uses evidence/load-probe-03–07, runtime/lamentum-adapter.patch, tools/load_probe.py, tools/perf_sample.py, the independent current gameplay plan, and the newer incremental tools/load_metrics.py and its synthetic execution tests. The inspected repository advanced beyond the earlier build218 audit **during this review**; use the current actual HEAD and installed ELF hash for every future A/B. **No new game binary, device run, gameplay confirmation, or FPS measurement was produced by this documentation-only review.**

### 26.1. Completed since the earlier roadmap; what is *actually* still blocked

| Area | Confirmed completion or measurement | Remaining limitation |
|---|---|---|
| Navigation | Main menu, New Game configuration, controls page, Loading and Options actually reached; main-menu highlight y=475, EV_KEY305 Confirm / 304 Back, live KMS receipts | No confirmed player/world rendering, physical player movement, audible sound, save/reload |
| Shader catalogue | build218 46 programs (indices 0–45), seven TEST substitutes; exact-code/control fragment45 with preserved half-precision arithmetic linked in newgame-20 | Linked does **not** mean four MRT colors, correct world pixels, or game activation are validated |
| Runtime | BC3 striped decode, deferred BC uploads, owner-local fileback, guest ZRAM, default-on CBUF TexSubImage, corrected shader banks, nominal 420 MiB texture budget | These mitigations do not prevent allocation of a large **decoded GPU RGBA** resource. No proven 30 FPS |
| GPU wall | [newgame-20](../evidence/newgame-20/summary.json) and [load-probe-03](../evidence/load-probe-03/summary.json) were terminated by kernel/Mali OOM, with **725,992 kB (~709 MiB)** GPU accounting against **986,064 kB** MemTotal | 75 notifier rows do not mean 75 independent leaks. Ownership of Mali-accounted bytes is not yet measured |
| New live-storage evidence | [load-memory-probe](load-memory-probe.md) found a real T2_TEXTURE_BUDGET live counter: **411 MiB tracked texture storage** against a 420 MiB cap | Rough **298 MiB difference** from Mali ~709 MiB remains **unattributed**, not proof of FBOs/leak |
| Lower budget | [load-probe-04](../evidence/load-probe-04/summary.json): T2_TEXTURE_BUDGET_MIB=300 -> controlled STOP, no OOM, last present 1081 | Still fails to load world. Frame count cannot establish FPS gain |
| Identified first-use trigger | [load-probe-04](../evidence/load-probe-04/summary.json): LC2_BC_DEFERRED **id=295**, **8192×8192**, reservation **268,435,456 bytes = 256 MiB**, budget 155 -> 411 MiB | Need exact BC source metadata, mip count, sampler/resource lifetime, and actual GL bytes |
| SD pressure | [load-probe-05](../evidence/load-probe-05/summary.json) stopped on LC2_FILEBACK_DISK_RESERVE; ~1,404 MiB SD free versus 1,280 MiB requested backing cap plus reserve | Disk capacity is distinct from GPU budget and cannot be solved with GPU flags |
| Repeatable safe boundary | [load-probe-07](../evidence/load-probe-07/summary.json): budget 300 and fileback cap 512 -> controlled T2_TEXTURE_BUDGET, no kernel OOM, last present 806, sampled minimum MemAvailable 60,740 kB | Two independent budget-stop runs are better safety evidence, **not successful gameplay**. Different fileback caps and navigation timing invalidate naive 1081-vs-806 comparison |
| Probe tools | Load probe, analyzer, measured cursor walker, hard-stop harness and tests exist; the newest load_metrics.py adds incremental processing and tests that **execute the payload** on synthetic logs | Need device-level collector integration, complete-line byte framing, run identity, genuine presentation/scene markers and pre-stop vs post-exit separation |
| Guest CPU | Separate build217 20.14s Loading window: **0.836 s main-thread CPU / presented frame** and 1.63 s CPU across threads, zero new ROMFS reads/textures/BC deferrals in that window | This is a Loading measurement, **not gameplay FPS**. Top on-CPU PC and wait/GC/IPC ownership are not proven |

**New critical inference:** the first controlled budget failure is not simply “too many textures.” A single **256 MiB first-use** decoded image increases accounted residency from around 155 to 411 MiB. The checked-in patch invokes t2_texture_budget_add **before** the corresponding glTexImage2D and striped glTexSubImage2D. Thus, a **clean reservation failure** does not itself prove physical GPU allocation took place. Raising the cap back to 420 just bypasses the guard and risks the earlier kernel kill.

### 26.2. P0-T0 — finish reliable load instrumentation rather than starting from scratch

**Files:** tools/load_metrics.py, tools/load_probe.py, tools/test_load_metrics.py, tools/analyze_load_probe.py, tools/perf_sample.py, tools/device_principal_test.py, tools/newgame_navigate.py. Reuse recent incremental-metrics implementation; do not redo completed work.

1. Re-run the existing host suite and the synthetic payload-execution fixture in tools/test_load_metrics.py. Add missing cases for **split event lines**, no complete newline, invalid UTF-8, log truncation/regrowth, new inode with equal-or-greater length, and old PID reuse. The remote payload currently decodes a complete newly read chunk and parses it while advancing offset only to the last newline: parsing a **partial trailing record** may duplicate that record on the next poll. Read binary bytes first, find the last complete newline in bytes, parse *only* its prefix and advance by its raw byte length.
2. Record (boot_id, run UUID, owned PID, /proc starttime, log dev/inode, executable SHA, source commit, image/catalogue hash, memory flags). A replacement log can grow beyond a previous offset before sampling; size check alone cannot detect all rotations. Reject cross-run counter merges.
3. Separate **live game**, **controlled stop**, and **after game exit** periods. In load-probe-03 and 04, post-stop MemAvailable jumps because the game has been freed. Compute minimum/pre-stop/last-safe system memory using *only* samples while the correct game process is alive. Do not use post-kill values as pre-kill headroom.
4. A load-probe-07 series reports frame 806 in successive samples while resource counters continue changing. Verify parser counters and a run-bound frame serial before inferring a rendering hang; a cached last frame number and actual no-present interval are different phenomena. No negative or missing presentation ID may be silently accepted.
5. Correct tools/perf_sample.py: derive SC_CLK_TCK **on the target**, not the workstation; parse /proc/PID/stat after the closing parenthesis; key per-thread deltas by TID **and starttime**, and preserve schedstat/faults rather than only the top six names. CPU ms/s = 1000 * delta_ticks / (target_HZ * elapsed_seconds).
6. Replace fixed New Game-page Down counts with a **page-specific cursor/selection oracle**. The measured main-menu y bands do not establish configuration-screen navigation semantics. Use short controlled press/release pulses and capture a **new** frame after each action; abort if selection is ambiguous.
7. Keep host-side exact-PID hard stop independent of unreliable guest SIGALRM. Preserve genuine exit taxonomy: runtime budget stop, shader stop, kernel-correlated OOM SIGKILL, SIGKILL of unknown cause, host timeout, cleanup failure, and real world reached. A substring Killed with no matching kernel victim is **not proof** of OOM.
8. Unit fixtures must run without a connected device, and the first device verification must take place under the previously demonstrated **safe** 300 MiB cap with the fileback 512 MiB capacity envelope. No automated stress/retry loop on a busy or physically unstable device.

**PASS:** an independent reviewer can reconstruct all counters from one owned process/log generation, distinguish actual scene progress, and verify a **clean safe budget stop** without false pixels or stale log evidence.

### 26.3. P0-G0 — audit the specific 8192×8192 id=295 resource *before* changing its format

**Code owners:** runtime/lamentum-adapter.patch, especially native/nvn_textures.h zero_texture_refresh, lc2_bc_upload_stripes and nvn_texture_dispatch; original baseline native/nvn_framebuffers.h / GL lifetime APIs remain manifest-pinned.

1. Add a **bounded one-shot** log when the id=295 first-use reserve is requested: NVN descriptor/source compression, width/height/depth/layers, format/sRGB flag, mip count/level offsets, output bpp, source pool/address/offset, guest write epoch, alias root, texture ID, GL context+name+generation, sampler and first draw consumer, budget bytes and actual future GL storage. Mask/protect owner-private asset bytes; source hashes, not binaries, belong in Git.
2. Check whether the 256 MiB calculation covers just level zero or all mips; for an ordinary full pyramid total would be approximately **341.3 MiB**, not 256 MiB. If some mips are skipped or shared, document why. Validate every mip base/max level and compressed block alignment, swizzle, alpha and gamma semantics.
3. Confirm **the resource really should be 8192²** in the original NVN descriptor. Check GL_MAX_TEXTURE_SIZE and whether the atlas is immutable and **sampled** rather than a render target, dynamically updated texture, shadow atlas or alias. Never lower dimensions or discard levels based solely on the large allocation size.
4. On the same run, aggregate separate live counts for original NVN texture IDs, actual GL storage (context,name,generation), depth/stencil/renderbuffers, color MRT, vertex/index/PBO buffers, swap surfaces, temporary conversion buffers, and aliased/backed guest ranges. **Do not double count aliases or infer GPU heap from cumulative create sizes**.
5. Use sparse snapshots around scene milestones and one pre-stop snapshot. Account for resource creation, lazy commitment, free/delete, generation replacement and outstanding GPU readers. Compare **411 MiB charged textures**, separately estimated other GL bytes and the Mali notifier **~709 MiB** as independent sources. Their ~298 MiB difference is currently **unknown**, not yet a leak.
6. Preserve T2_TEXTURE_BUDGET_MIB=300 for first validation and never bypass T2_MEMORY_FLOOR, 420 MiB default ceiling, context/fence correctness or the board's physical headroom just to get a screenshot. Stop before unsafe allocation.

**PASS:** the first-use record proves which original resource class needs 256 MiB; the total GPU allocation gap is classified by live owners with safe, bounded measurements.

### 26.4. P1-G1 — primary new optimization: native ETC2/EAC or ASTC GPU storage

**Why it matters:** existing 128-row striped BC3 decoding reduces **temporary CPU decode memory**, but glTexImage2D still reserves an **uncompressed RGBA image in GPU memory**. One 8192² RGBA8 base level is **256 MiB**. An ETC2 RGBA8/EAC or ASTC 4x4 block-compressed base level is about **64 MiB**; ASTC 6x6 is about **28.5 MiB**. Therefore an actually compressed 8bpp allocation could reduce this one base level's storage by **192 MiB**. These are theoretical storage sizes before mips, driver padding and staging, **not measured GPU savings**. Transcoding BC3 may introduce additional visual loss.

**Implement as a gated, owner-local experiment:**

1. Probe actual Mali GLES version, compressed format list, ASTC extension and GL_MAX_TEXTURE_SIZE; run a tiny independently testable upload/sample/readback fixture on the **actual driver**. GLES3 defines ETC2/EAC formats, including GL_COMPRESSED_RGBA8_ETC2_EAC and GL_COMPRESSED_SRGB8_ALPHA8_ETC2_EAC; ASTC 4x4/6x6 requires advertised, successfully tested ASTC support. **Do not treat an advertised format as proof the driver stores it compressed.**
2. Obtain owner-local original BC3 source bytes and pin SHA-256, sampler type, sRGB or linear interpretation, alpha, swizzle, mip count, orientation, and source write generation. Reject a dynamically modified atlas, render target or image-storage resource: immutable sampled images only.
3. Precompute an **offline, bounded, content-addressed** transcode: owner-private BC3 -> RGBA -> ETC2 RGBA8 (first A/B); then ASTC 4x4 and possibly ASTC 6x6 for a separate visual-quality arm. Cache key must include original bytes hash, format, mip geometry, encoder/options/version and runtime format contract. Do not commit copyrighted inputs, raw decoded texels or output game assets.
4. Preserve every mip, correct block padding, alpha and sRGB sampling behavior. Validate transparent sprite edges, dark gradients, pixel-art text, UV orientation, filtering/mip switching, and interpolation against actual KMS captures from the original lossless path. An image hash may change legitimately with lossy transcode; define visual tolerance and a strict correctness review.
5. Add optional exact-descriptor/source-hash logic at the texture's **first materialization** (native/nvn_textures.h). Use glCompressedTexImage2D for all intended levels; do not allocate the full RGBA fallback **in addition to** the compressed texture. If GL rejects the format or cache identity is wrong, fail closed or use a capacity-verified lossless fallback, not a hidden OOM.
6. Charge **actual compressed GPU bytes**, including live mip levels, against a separate verified storage generation. Instrument driver/system live memory. Keep the same safe 300 MiB budget and consistent fileback cap during the experiment. Verify that the former 256 MiB atlas no longer causes a 411 MiB budget jump; this is only a starting check, not sufficient proof of physical savings.
7. Watch real Mali memory and headroom, early scene progress, materialization stalls and guest CPU. Off-device/precomputed encoding is preferable to expensive on-device software compression during already slow loading. Disk space is constrained: load-probe-05 showed only ~1.4 GiB free. Reserve room for saves, logs and rollback and bound the new cache separately from file backing.
8. Run one short guarded validation, then **three matched test runs** comparing GPU/system peak memory, real world progress and visual correctness. If the driver silently expands the compressed data to RGBA, alpha changes visibly, or decode cost becomes the new bottleneck, revert this path.

**Lower-priority alternatives:** a title-controlled texture-quality setting/4096 atlas with known UV/mip consequences; atlas virtual pages only if precise sampling/view remapping is possible; fragment-shader manual BC3 decoding from compressed-byte textures (complex texture filtering and extra fragment cost, **P3 research only**). **Do not** simply halve texture dimensions without correcting dependent coordinate/filtering semantics, and do not declare a BC3 image to be ETC2/ASTC without transcoding it.

**PASS:** substantial physical GPU memory reduction, same meaningful scene output, and progression **past** the previously failed id=295 allocation with no kernel OOM or unsafe pressure.

**Reference:** [Khronos KTX developer guide, ETC2 RGBA 4×4 block sizing and ES3 formats](https://github.com/KhronosGroup/3D-Formats-Guidelines/blob/main/KTXDeveloperGuide.md).

### 26.5. P1-G2 — resolve the other ~298 MiB of Mali-accounted memory

Even an ideal compressed atlas might not be sufficient if non-texture storage remains large. Choose the **actual owner** before trying broad graphics changes.

1. Trace native/nvn_framebuffers.h, NVN target bindings, GL FBO/RBO color/depth/stencil allocations, buffer object reallocations, EGL window/pbuffer surfaces and duplicate texture generations. For each allocate/redefine/delete, record dimensions, format, samples, owner, GL context, generation, backend bytes and last consumer/fence. Distinguish an FBO object itself from its attached texture storage.
2. Verify whether first-use BC upload plus eager texture creation leaves two physical GL storages, or descriptor aliasing charges bytes without duplicating storage. Account for GL delete and resource retirement **after** its final in-flight GPU consumer.
3. As a sizing example, a 1920×1080 RGBA8 target is **7.91 MiB** and four full-size MRT color targets are **31.64 MiB** before depth/stencil and MSAA. The physical 1280×720 display is already 720p, so reducing display mode does **not** remove 1920×1080 internal render targets.
4. If actual internal targets dominate, identify their **Lamentum-specific Unity owner** by original image/metadata hash and trace creation plus projection/UV dependencies. Then A/B an owner-scoped 1280×720 override with correct depth, viewport, scissor, matrix and texture sampling. Do not reuse West of Loathing offsets or blindly change FBO dimensions.
5. If transient render targets accumulate, retain safe resource re-use only while no earlier GPU serial/fence reads the storage. Never globally call glInvalidateFramebuffer while bloom/composite still requires the attachment. Preserve strict GL errors, NVN completion and the synchronous queue by default.
6. Compare **live allocated classes and true Mali/host memory peaks** with equivalent scene phases and same atlas format. A mere reduction in the number of glGen calls without lower physical residency is insufficient.

**PASS:** a quantified, correct source of unbudgeted live GPU memory and a one-factor fix that reduces the actual driver/system peak.

### 26.6. P0-C0 — stop guessing about the 0.836 CPU seconds on the main Loading thread

1. Sample guest PCs using the **already implemented** MOMO_STACK_SAMPLE_MS, MOMO_STACK_SAMPLES, MOMO_STACK_SAMPLE_AFTER and tools/analyze_guest_samples.py in a bounded **pre-budget-stop** period. The isolated load-probe-01 PHYSICAL_MEMORY_CONFLICT has not been causally linked to stack sampling; compare with a no-sampler control and never dismiss a real alias violation.
2. Map PCs only to exact **owner-private, SHA-pinned** main/sdk/subsdk images and available IL2CPP/Unity metadata. Capture module+offset, thread identity, interrupted PC and call chain; keep unresolved addresses explicit. Do not invent symbols from guessed offsets.
3. Separate actual **CPU time** (CLOCK_THREAD_CPUTIME_ID or corrected target thread ticks), elapsed wall time, runnable scheduler delay, Horizon SVC wait, file backing, guest ZRAM compression/restoration and GL/GPU completion. The old T2_GZRAM cpu-compress-ms counters use CLOCK_MONOTONIC elapsed time, not proven executing CPU time.
4. Classify the actual hot path: guest SVC/IPC spin or wrong timeout units, Unity/IL2CPP initialization/GC, repeated metadata/deserialization, guest page restore/recompression, GL submission, or scheduler/thermal limitation. Inspect a guest wait/event mapping against a suitable open-source Horizon implementation **only after finding the offending call**, preserving original return codes and event ownership.
5. Build a synthetic unit fixture for **one identified** ABI/logic bug, implement a reversible adapter change, and benchmark **world-loading progress per CPU-second**, not Loading-spinner presentations. Never universally skip SleepThread, fake GPU completion, or change Unity time scale just to make the FPS counter advance.
6. If CPU time really remains ~0.836 s for each meaningful game frame, stable 30 FPS is not remotely close on the present path; resolve that bottleneck before postprocessing and compiler-flag experiments.

**PASS:** a measured top CPU routine/blocked wait or a rigorous distributed-hotspot profile, with less CPU per unit of *real* scene progress after the eventual fix.

### 26.7. P0-W0 — gameplay bring-up once resource pressure allows it

1. Record an owner-validated Unity scene/async-operation progress marker, camera/player update and newly **drawn** program pair; a rising present counter or static Loading animation does not establish successful scene activation.
2. Confirm fragment45's **four MRT outputs** are actually written: GL_DRAW_BUFFER configuration, attachment 0–3 formats/sizes/samples, FBO completeness, shader location/layout, color mask, depth/stencil state, and producer/consumer order. The already verified link-on-native-pair-draw only proves shader linking, not correct pixels.
3. Trace newly reached vertex44/fragment45 pairs and all seven remaining TEST substitutions with exact captured code/control identities. A substitute unused in menu can still break world lighting, sprites, depth/MSAA or skinning. Append real shaders only if a new exact STOP or verified demanded TEST path occurs.
4. In native/nvn_render.h, a **title-specific fallback** can bind the other constant-buffer slot when the declared slot is empty. This rescued historical data paths but risks silently wiring a wrong bank for a newly reached world shader. Add bounded per-program fallback receipts, prove the actual binding and preserve c4 -> NVN UBO1, c1 literals and c3/c3_1 alias rules; never remove or broaden the fallback without a positive/negative regression test.
5. If KMS appears blank/dark, isolate **render target -> swapchain image -> present quad -> panel** with one-shot, owned-PID readbacks. A blank **post-kill sleeping display** (already observed) is not a black in-game frame. Avoid always-on GPU readback for benchmarks.
6. Require **physical** pad movement with visual player-coordinate changes, item interactions, dialogue/inventory, audible SFX/music and owner-save-backed **save -> quit -> cold launch -> load**. Test Spruce principal and CPU-mask restoration after both normal exit and controlled stop.

**PASS:** a correct controllable world with verified rendering, interactions, sound and persistent saves. Only then change README from NOT PLAYABLE.

### 26.8. P1-F0 — credible 30 FPS optimization *after* gameplay is working

1. Obtain a genuinely quiet, unfiltered **per-present** 60-second world run three times. Record P50/P95/P99, true displayed throughput, missing/duplicate serials and panel refresh cadence. Separate menus, Loading, steady gameplay, movement, combat/effects and scene transition windows.
2. Attribute **exclusive elapsed** frame stages plus concurrent CPU utilization and GPU waits: guest idle/on-CPU, GC/IPC/page restore, NVN queue/replay, GL state/FBO/CBUF/materialization, and present. Do not add independent column medians or call slow-frame-only logs complete FPS distributions.
3. Choose **one measured** hotspot: CPU wait/fault -> guest runtime; memory -> compressed residency/lifetimes; draw submit -> state/cbuf cache; GPU fill -> title-specific render-target resolution or reversible quality preset. Earlier CBUF SubImage was already implemented without a proven whole-frame gain; generic ZERO_RENDER_SCALE=2 had little impact on historical Loading diagnostics.
4. Avoid unsafe async queue, ignored GL errors, pageout without alias proof, forced CPU clocks and global bloom/stencil removal. Compare device temperature, governor, compressed cache storage, driver RAM and audio/input behavior.
5. Declare stable 30 FPS **only** after three independent >=60s correct gameplay runs with complete-frame **P50 and P95 <=33.33 ms**, preferably P99 <=50ms, safe RAM, correct sounds, controls and cold save/load. If not attained, publish the actual verified frame-rate ceiling and its bottleneck.

### 26.9. Updated concrete implementation order

| Rank | Small scoped PR / files | Must produce before the next step |
|---:|---|---|
| **P0-1** | **T0** complete tests and byte-exact incremental collector (tools/load_metrics.py, load_probe.py, perf_sample.py, navigation + harness) | Trusted run/PID/log identity, real phase and pre-stop memory accounting; preserve newer completed test fixtures |
| **P0-2** | **G0** id=295 original descriptor + GL resource ledger (adapter patch, nvn_textures.h / nvn_framebuffers.h) | Prove why a 256 MiB image is required, how mip levels are charged and which classes fill 411->709 MiB |
| **P1-3** | **G1-A** owner-local ETC2/EAC offline cache + actual Mali compressed-upload fixture | Correct 8192² sample at <=64 MiB base allocation **if driver truly stores it compressed**; preserved visual parity |
| **P1-4** | **G1-B** ASTC 4x4/6x6 **only** if device/quality tests justify it | Better measured residency/quality tradeoff, source-SHA-pinned cache, safe fallback |
| **P1-5** | **G2** remove proven duplicate/oversized GL lifetime or source-verified internal 1080p target | Lower total driver peak, safe headroom, actual load progression beyond previous stop |
| **P0-6** | **C0** target-correct guest-PC/CPU profile | Hot guest CPU call family, on-CPU vs blocked classification and low profiler overhead |
| **P1-7** | **C1** narrow Horizon/IL2CPP adapter fix if top CPU site warrants it | Less CPU per unit of real scene progress; behavior/ABI regression tests |
| **P0-8** | **W0** render actual world (MRT 45, texture/cbuf banks, draw census) | Real KMS frame, physical movement, no unjustified TEST substitutes |
| **P0-9** | **PLAYABLE** sound, inventory, dialogue, cold saves and clean device lifecycle | May accurately label the title playable |
| **P1-10** | **F0** world-only profiling and one-factor rendering/CPU optimization | Repeatable 30 FPS acceptance gate, or an accurately reported ceiling |

**First proposed controlled A/B (not performed here):** same build218 owner image, validated 300 MiB texture budget and 512 MiB fileback cap; A is the **known clean id=295 budget stop**, B is an owner-local cache of that proven immutable id=295 source transcoded to ETC2 RGBA8, under **the exact same safe limits**. Check source format/sampler and compressed driver storage first. Success means correct world progression without kernel OOM and a real memory drop; merely turning STOP into SIGKILL is a failure.

**Do not repeat already completed milestones:** cbuf TexSubImage implementation, build218 shader45 generation, measured New Game menu band, simple log-distribution parser, hard host-side timeout, or the newly committed synthetic incremental-metrics payload execution fixture. Extend/correct them based on fresh evidence instead.

**Conclusion:** the next important performance fix is likely not another draw-call micro-optimization; it is **safe GPU residency for a demonstrably expensive 8192² texture**, followed by attribution of the independent **0.836-second main-thread Loading CPU cost**. The port cannot be called playable until a real world scene, controls, audio and saves work, and 30 FPS remains unmeasured.

---

## 27. Build219 reassessment: code-audited action plan for first gameplay and FPS (2026-10-20)

> **T0 subsequent source update:** commits [e6cc966](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/e6cc9668f73217ca2e2fd19e2a61eafd04287bcd) and [e19a9b9](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/e19a9b97f1bd58642e7d3ae6b6cb002b0c30e3e3) have **already fixed** target-side CPU tick units, proc-stat/process-thread generation, unknown-SIGKILL vs kernel-confirmed OOM and probe return status. Read [the action-plan T0 progress note](build219-gameplay-performance-action-plan.md#2-critical-path-priorities-and-non-negotiable-safety) and [exit taxonomy](../evidence/exit-taxonomy/README.md). T1 is **partially implemented**, not a request to redo those completed changes; still needs owned-run integration and a scene oracle. No new gameplay run was performed for these fixes.

> **Current implementation instructions:** [Build219 Gameplay Bring-up and Performance Action Plan](build219-gameplay-performance-action-plan.md), audited against main commit [19dc046](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/19dc04644d6381dd9c4921500116c21333914295). This section supersedes the current-status priorities in §§0–26. Earlier experiments remain as measured history. **No new device run, ELF build, gameplay confirmation or FPS measurement was performed in this documentation audit.**

### 27.1. What was completed and what was corrected

- **build219** adds a texture-charge snapshot beside RSS, VmSwap and MemAvailable; [load-probe-10](../evidence/load-probe-10/summary.json) measured **126 MiB texture live** while VmSwap reached **~870 MiB**, but this was an **earlier Loading phase** terminated by operator TERM. It does **not** prove a guest-heap leak or remove the later id=295 **256 MiB RGBA** first-use threat. The resource/GL owner ledger is still incomplete.
- **load-probe-08** reached a clean texture-budget stop under 300 MiB and recorded **5,506 SVC 0x1A**, **5,389 SVC 0x1B** and **39,516** IPC calls on endpoint0x40 commands 8/7 combined. Those calls suggest a precise **mutex/IPC bridge** investigation. The sampled native PCs and endpoint service owner have not been resolved.
- The 400 MOMO samples were spread approximately evenly across **32 guest threads**. Thus 387 in-kernel samples **cannot be equated to 96.75% of executing CPU time**. Obtain a same-run native mappings receipt and correctly CPU-weighted per-thread samples before claiming a percentage.
- **load_metrics.py byte framing was already fixed.** Since the initial audit snapshot, **proc_metrics.py / perf_sample.py target-HZ and proc identity were also fixed**, with target HZ=100 verified on TSPS, and exit_outcome.py now requires a kernel victim receipt before classifying OOM. Continue with run-wide source/ELF/asset identity, navigation and real-game validation; do not redo completed source fixes.
- The 300 MiB guarded texture budget converted previous Mali OOM runs into clean **T2_TEXTURE_BUDGET** stops, but the game **still has no verified world, physical movement, sound, save/load or gameplay FPS**. A linked fragment45 is not proof of four correct MRT outputs.

### 27.2. Next implementation order

| Priority | Change | Evidence and stop gate |
|---:|---|---|
| **P0-1** | **T1 (partially done):** target CPU tick units and PID/TID starttime identity, exit taxonomy and byte framing **completed**; finish complete run/log identity, scene-specific New Game navigation and real-game acceptance | Executable host tests and one safe owned-PID probe; no false STOP/OOM attribution |
| **P0-2A** | **C1:** profile the real cost and semantics of svcArbitrateLock (0x1A), svcArbitrateUnlock (0x1B), and endpoint0x40 IPC 7/8; symbolize same-run native PCs | CPU/wall timing, request/return/wake and actual service identity; no skipped locks |
| **P0-2B** | **G1:** map original id=295 plus **all live** GL textures, color MRT, depth/stencil, EGL and buffers with generation/alias/fence identity | Reconcile actual owners of texture-charged versus still-unattributed Mali memory under safe 300 MiB cap |
| **P1-3A** | **C2:** narrow, semantics-preserving IPC/SVC fast path or service fix only if profiling proves the cost | Decreased **CPU per actual scene milestone**, not spinner FPS; no lost wakeups |
| **P1-3B** | **G2:** test owner-local offline BC3->ETC2/EAC (then optional supported ASTC) compressed GL storage for **one immutable** atlas | Real Mali memory reduction; safe progress past original 8192x8192 first-use event; image quality reviewed |
| **P0-4** | **W1/W2:** identify Unity scene activation, validate all four fragment45 MRT targets, shader TEST use, proper KMS/world rendering, actual controls, audio and cold saves | Real playable scene and clean Spruce MainUI/CPU restoration |
| **P1-5** | **F1:** profile real gameplay, then target the measured SVC, texture, replay or driver bottleneck | Three independently measured >=60s gameplay runs, complete-frame P50/P95 <=33.33 ms plus visual/audio/memory correctness |

**Implementation-level recipes, source paths, fixtures, rollback and alternatives:** [build219-gameplay-performance-action-plan.md](build219-gameplay-performance-action-plan.md). The two P0 investigation lanes may be developed in parallel off-device; **never run two principal-flow probes on the handheld concurrently**. Do not raise memory caps, remove NVN synchronization, bypass a shader, or call a Loading animation "gameplay".

## 28. HEAD 2968919: Post-C1 Audit and the Critical Path to Gameplay and 30 FPS (2026-10-20)

**Snapshot:** repository HEAD [2968919c0](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/2968919c0bdda35ccca146fe18ebd35e717f6c8c). Audited: adapter patch and shader catalogue; launcher; load, process, profiler, navigation, exit and AudioOut audit tools; docs and committed real-device evidence. The retained deployed **build219 ELF** is SHA-256 b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a. A repo commit does not itself prove a new ELF deployment. **No device test or compilation was conducted for this reassessment.**

### 28.1. Implemented versus unfinished: do not repeat completed work

| Component | Proven so far | Remaining requirement |
|---|---|---|
| New Game | Real menu, Options, New Game config, controls and Loading on physical KMS. Catalogue 46 entries (0–45), seven TEST substitutes. Fragment45 links. | No world scene, world draw, movement, sound, saves or gameplay FPS. A linked four-output fragment is not four valid MRT pixels. |
| Runtime/memory | Manifest-verified 435-file baseline + adapter, BC3 striped decode, deferred uploads, private fileback, guest ZRAM, charged texture cap. | 8192² id295 first-use 256 MiB decoded GL RGBA base level; safe 300 MiB cap stops before allocation. Other live Mali resource classes remain unaccounted. |
| CPU evidence | Historical 0.836 CPU s / Loading present (earlier phase); 5506 ArbitrateLock and 5389 ArbitrateUnlock events in load-probe-08. | No proof these specific calls dominate executing CPU or cause scene load delay. |
| AudioOut identity | Source/ELF-pinned C1 identifies EP_AUDOUT=0x40 from audout:u: child cmd7 appends PCM, cmd8 retrieves released buffer tags. Correct mutex address is **X1 lock / X0 unlock**; 41 unique mutex addresses in load-probe-08. Audit records 105 host tests passing. | Exclusive AudioOut, synchronization and IPC CPU/wall time; audible output. Former 1011 mixed-register values were not mutex addresses. |
| Diagnostic tooling | Incremental complete-byte-line log collector; target HZ=100 proc CPU accounting, boot/PID/starttime and TID identity; kernel-victim-verified OOM classification; FAT filename-alias samefile fix; two verified build219 menu runs with clean CPU/MainUI restoration. | Join run UUID, process, installed ELF, image, shader catalogue and log generation; same-inode log truncate/regrow and semantic New Game oracle; load-phase acceptance. |
| CBUF | SubImage allocation reuse is **already implemented** behind LC2_CBUF_SUBIMAGE, default enabled. Historical A/B showed no trustworthy frame-time win; GL padding remains 1024 RGBA32F texels. | Optimize only verified repeated padded uploads with exact shader texelFetch/stride proof. Do not recommend SubImage as a new feature. |
| Rendering | Generic ZERO_RENDER_SCALE=2 historical Loading A/B had little whole-frame effect; safe synchronous NVN path is default. | Actual Lamentum world GPU profile; real ownership of 1920×1080 targets; strict GL context/serial validity. No glFlush-only completion workaround. |

**Separately measured phases must stay separate:** load-probe-10 build219 saw charged texture plateau ~126 MiB and VmSwap ~870 MiB in earlier Loading, ended operator TERM; load-probe-04/07/08 and newgame-20 reveal later id295 pressure. The former is **not** proof the latter disappeared. No loaded world exists to benchmark.

### 28.2. Updated dependency graph and first three implementation PRs

**GPU lane G:** G0 exact id295 metadata, all GL storage owners and mip-level accounting -> G1 independent real-device ETC2/EAC fixture -> G2 immutable owner-private atlas transcode with true compressed residency -> pass former first-use stop safely -> world validation.

**CPU lane C:** C0 profile actual per-thread executing CPU / scheduler waiting / exclusive SVC and AudioOut handler cost -> C1 implement **one** semantics-preserving fix only if measured -> prove faster **scene milestones**, not a faster Loading animation.

**Evidence lane T:** T1 bind every sample and scene step to an exact boot/process/run/executable/log generation and merge the two conflicting navigation implementations. This must precede comparative claims.

**World lane W:** W0 real Unity scene activation -> W1 actual correct MRT/shaders/final KMS image -> W2 physical controller, interaction, audible audio, cold save/load.

**FPS lane F:** after W2, three independent real gameplay timing runs -> optimize only the top exclusive measured frame cost -> check full frame P50/P95 <=33.33 ms and input/audio/saves/memory safety.

**Best next off-device work:** prepare G0's guarded one-shot id295/GL ledger, C0's all-thread sampled AudioOut/SVC profiler, and a small original ETC2 fixture. The board can only have **one** principal-flow run at a time; do not spend the next cycle on yet another menu-only timeout.

### 28.3. T1: make an unmistakable owned-run and phase oracle

**Inspected code:** port/Lamentum.sh currently uses COTM_RUN_ID=$(date +%s), a second-resolution timestamp. tools/load_metrics.py folds log fragments using opened-file (dev,inode) and consumed-byte offset; an inode truncated then regrown past an old offset can be missed. tools/perf_sample.py pins the observed process identity but log folding is not yet cryptographically bound to that process or the installed ELF. tools/load_probe.py still uses two fixed Down presses on the configuration page and accepts a >=120 changed-cell screen difference. tools/newgame_navigate.py implements a separate four-row procedure. None of these indicates game-world activation.

**Implementation recipe:**

1. Generate one globally unique run UUID at principal launch (e.g. read /proc/sys/kernel/random/uuid) or inject it from the host. Emit complete LAMENTUM_RUN_UUID and LAMENTUM_BUILD_ID headers before runtime events. Create host-controlled identity.json with source commit, launch UUID, boot ID, actual process PID/starttime, installed ELF SHA, launcher hash, private owner-image section hash and shader catalogue hash; keep proprietary source bytes private.
2. Return run UUID, log header identity, opened-file (dev,inode), byte offset and complete-line boundary from every incremental collector call. If same-inode truncation+regrowth reuses the old size, the **run header must still change**, otherwise fail closed with LOG_GENERATION_CHANGED. Do not merge old and new counts; file ctime/mtime alone is not a reliable unique run marker.
3. Associate each sampled process and log chunk with the same boot/PID/starttime/installed ELF/run UUID. Mark LIVE, STOPPED and POST_EXIT explicitly; refuse to count freed post-exit memory as load headroom. Preserve the confirmed os.path.samefile executable identity fix for VFAT path case aliases.
4. Replace divergent navigation scripts with one state machine: MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> WORLD/STOP. For every press, require a new present serial and a **positive page-specific state** (actual highlighted row/prompt/known scene milestone), not generic bright-pixel count or background-animation delta. Keep bounded press/release behavior and known EV_KEY305 Confirm vs 304 Back mapping.
5. Host-only unit tests: identical-time run UUIDs, same-inode truncate/regrow, unrelated process with identical comm, PID reuse, differing VFAT path spellings to same inode, stale log from earlier ELF, old post-kill MainUI screenshot, configuration page animation without page switch, STOP versus host TERM versus SIGKILL without kernel victim evidence, and clean CPU/principal restoration. No SSH is necessary for fixtures.
6. After tests, one bounded **300 MiB texture-budget / 512 MiB fileback** New Game run with original saves/ELF backed up. Keep independent exact-owner PID watchdog and CPU mask restoration. Full run evidence should include identity, complete-byte cursors, states, stop/exit classification and actual live KMS captures.

**PASS:** independent reviewer can reproduce the exact Loading transition and end classification using one coherent run. **STOP:** any ambiguous page, mixed run generations, unknown owner PID, low RAM/storage reserve, or failed cleanup. This is infrastructure, **not** a performance optimization.

### 28.4. G0: check a concrete multilevel GPU-accounting risk, then map the Mali heap

**Fresh source-level finding:** in runtime/lamentum-adapter.patch, the deferred BC materialization branch of native/nvn_textures.h inside zero_texture_refresh reserves width*height*output_bpp as t2_budget_bytes and then loops over t->b.levels allocating/uploading GL storage. Thus a **multi-mip** deferred texture may be charged for only the base mip. This is not yet proof id295 has multiple levels, or that the budget undercount caused Mali OOM. An 8192×8192 RGBA8 base mip is 256 MiB; a complete power-of-two mip pyramid would be approximately 341.33 MiB, before driver padding. ETC2 RGBA8/EAC equivalents are 64 MiB base, ~85.33 MiB complete. Verify actual descriptor first.

1. Add a one-shot gated receipt LC2_RESOURCE_AUDIT_ID=295 **before budget reservation**: exact NVN original dimensions, format, sRGB, mip count, layer/face count, each level geometry, sampler, descriptor pool, guest backing address/alias root, modification epoch, last-known consumer, GL context/storage generation, and calculated per-level decoded/storage byte sum. Do not dump asset bytes or over-read the guest pool.
2. Write a pure host memory-accounting function with **checked 64-bit arithmetic**, summing only actually created levels and layers in RGBA or exact compressed blocks; account for min-width/min-height rounding. Add tests for id295 one mip versus full pyramid, non-square dimensions, non-power-of-two mips, sRGB, BC3/ETC2 block padding, aliases, replacement, delete, and texture budget refunds. Do not confuse logical format bytes with driver committed physical pages.
3. If the multi-mip undercharge is demonstrated, adjust reserve/add/release transactionally; preserve reserve-before-glTexImage, which is how the current 300 MiB guard prevents an unsafe allocation. An accounting correction may cause an *earlier* fail-closed stop; **it is a safety fix, not a way to bypass the guard**.
4. Instrument a sparse live storage ledger with real ownership: GL textures, renderbuffers, depth/stencil, MRT attachment0–3, vertex/index/PBO buffers, EGL surface images and transient decode staging; create/redefine/delete, dimensions/format/sample count, original NVN resource/pool alias, EGL context generation, GL storage generation, and final in-flight GPU reader/fence. An FBO handle is not another image allocation. Deduplicate aliased storages; do not add RSS, SwapPSS, texture charges and Mali accounting as independent physical heaps.
5. Record sparse pre-stop snapshots with actual process MemAvailable/CmaFree, process RSS/PSS/SwapPSS, charged logical storage and separately reported Mali driver numbers. About four RGBA8 1920×1080 MRT targets would cost 31.64 MiB before depth/MSAA/padding, but **this is a sizing example, not an explanation for unaccounted 298 MiB**.
6. Compare only phase-matched build219 and a new safe bounded run; keep the known 300 MiB guard and 512 MiB SD-backed envelope. An id295 budget refusal proves the GL allocation was **avoided**, not that the driver attempted that full allocation.

**PASS:** actual id295 level/format/usage identity and safe charged/resident allocation arithmetic; each significant live GL allocation has an identified class or clearly marked unknown. **STOP:** unexpected alias/lifetime, overcommit, memory floor, kernel OOM or GL errors.

### 28.5. G1: independent ETC2/EAC support and physical-memory fixture

Before integrating into Lamentum, create a small **self-authored** EGL/GLES3 test using the same device driver, but no original game data.

1. Query actual GL version/renderer/extensions and GL_MAX_TEXTURE_SIZE in the **runtime-equivalent** context. Probe GL_COMPRESSED_RGBA8_ETC2_EAC and GL_COMPRESSED_SRGB8_ALPHA8_ETC2_EAC. ASTC only in a separate arm if **advertised and tested**. GLES3 format definitions do not prove this Mali driver keeps the data physically compressed.
2. Create an original test texture with alpha-gradient/sprite border, small text, dark/sRGB gradients, transparent pixels and a complete mip chain. Compress offline to ETC2 RGBA8/EAC; verify dimensions, bytes per 4×4 block, per-level image sizes and alpha/color-space correspondence.
3. Render uncompressed RGBA and ETC2 in **separate** same-environment trials; verify GL errors, mip/filter/sampler completeness, true live KMS screenshots, alpha and edge quality, and approximate physical Mali/host memory peaks. Test small sizes first; attempt 8192² only after verifying driver limit and safe reserve, never both huge variants simultaneously.
4. Confirm physically resident storage is lower. An advertised compressed format whose driver decompresses to RGBA storage is **not** a validated solution to this OOM.
5. Keep fixture source in tools, raw image only self-generated, and log identity plus cleanup. Do not run the fixture at the same time as Lamentum.

**PASS:** reliable real-device ETC2/EAC sampling/alpha/sRGB correctness **and** actual memory reduction. If not, stop this branch before owner-private asset conversion. Sources: [Khronos ES registry](https://registry.khronos.org/OpenGL/index_es.php) and [KTX compressed formats](https://github.com/KhronosGroup/3D-Formats-Guidelines/blob/main/KTXDeveloperGuide.md).

### 28.6. G2: replace **one immutable** BC3 atlas with real compressed GPU storage

**Why:** current lossless stripe decoder saves temporary *CPU* RAM, but the large texture ultimately receives ordinary full RGBA GL storage. For id295 an ETC2 RGBA8/EAC allocation is theoretically 64 MiB for the 8192² base level versus 256 MiB uncompressed, a **192 MiB** payload reduction; full mip-chain sizes may differ. These are format sizes, **not demonstrated Mali savings or acceptable image quality**.

1. In the owner's local private image workspace, identify the **exact** id295 original BC3 bytes by source hash, descriptor, all mip dimensions, swizzle, sRGB/linear behavior, alpha, sampler view, guest memory pool alias and actual write epoch. Explicitly confirm this is an **immutable sampled** texture and not an FBO, writable texture or resource whose BC blocks change during gameplay. If dynamic, exclude it from the first test.
2. Build a **private offline** transcoder and content-addressed cache: original BC3 -> RGBA -> ETC2 RGBA8/EAC, preserving every original mip, alpha, block padding, orientation, color space and filtering expectations. The cache manifest includes source SHA, compressor version/options, target GL format, geometry, mip count, output SHA and owner-image identity. Never commit raw original/decoded/transcoded proprietary image data.
3. At the earliest validated first-use branch in native/nvn_textures.h, inspect this exact manifest identity and select glCompressedTexImage2D for each level; ensure the original 256 MiB RGBA texture is **not also allocated or materialized** in the same or another context. Keep a reversible feature flag and a fail-closed response on wrong cache identity. Fallback to lossless RGBA only if independently proven safe under the memory cap; silent fallback into an unsafe OOM is forbidden.
4. Budget the **actual compressed allocation including mips/layers** transactionally. Track EGL context and GL storage generations and the original guest write epoch. A guest write/alias invalidates the transcoded GL representation; preserve guest BC bytes, ZRAM and fileback coherency rather than treating derived compressed storage as authoritative game data.
5. Measure size and quality on the actual TSPS: transparent sprite edges, dark gradients, alpha blending, mip transitions, UVs, pixel text, noise, and the four-MRT/composite path; compare real live KMS screenshots. ETC2 BC3 transcode is potentially **lossy**. If unacceptable, keep it explicitly experimental/optional instead of quietly changing the default.
6. Respect actual SD storage: the earlier 1280 MiB backing cap exceeded available reserve; the tested 512 MiB guest fileback envelope and space for saves/logs/backups must remain available. Do not encode an 8192² ETC2 atlas on the slow handheld Loading path if an owner-local offline cache is available.
7. Run one guarded trial with the proven 300 MiB charged-texture cap, exact target process, watchdog and pre/post cleanup. Require: genuine compressed GL upload, lower **Mali physical memory peak**, and **a new scene-loading milestone beyond the previously failing id295 first use**, with the same correct image. Repeat three times before considering broader allowlists.

**If ETC2 is insufficient:** compare supported ASTC 4×4 (8 bpp) and 6×6 (~3.56 bpp) in separate visual-quality/driver-memory trials, and inspect **real** GL texture duplicates and MRT lifetime. The last-resort ideas (atlas virtualization with exact derivative/filter/view mapping; shader-side BC3 block decoding; owner-specific texture resolution selection) are P3 research. **Do not** relabel BC3 bytes as ETC2 or simply resize the texture: formats, UVs, mips and alpha must remain semantically correct.

**PASS:** safe loading proceeds past id295 and real physical memory/quality evidence supports the change. **STOP:** compressed storage expanded by driver, incorrect transparency, missing mips, unexpected guest writes, failed budget/GL state or OOM.

### 28.7. C0: profile actual SVC/AudioOut cost instead of guessing a busy loop

**Already established in [the pinned C1 audit](../evidence/C1-audio-owner/README.md):** EP_AUDOUT=0x40 is the audout:u child, cmd7 queues PCM and cmd8 polls/retrieves released buffers. Lock 0x1A's mutex operand is X1; unlock 0x1B's is X0. There were 41 real mutex addresses in load-probe-08, not 1011. Raw counts do **not** tell us CPU consumption, effective wait duration, ownership, or whether audio polling is pathological.

**Existing measurement limitation:** native/guest_profile.h and loader.c already sample CLOCK_THREAD_CPUTIME_ID and CLOCK_MONOTONIC, but the present-end report currently reads only the presenting thread's TLS. It starts SVC timing **after** acquiring kernel_mutex and ends **before** final gate/unlock. IPC buckets duplicate/overlap their enclosing SVC time; their times must never be added together. IPC classification labels AUDREN as AUDIO but leaves AUDOUT under OTHER. Reuse this profiler, do not add a duplicate generic high-volume trace.

1. **Classification-only change first:** in native/ipc.h, group the verified EP_AUDOUT with AUDIO for the existing sampled profiler. Ensure EP_AUDOUT_MANAGER versus child and CMIF command type remain distinct and tested. This changes no IPC behavior.
2. Add bounded **per-thread ring/sharded statistics** and safe merge during a diagnostic window/exit for the presenting thread, main guest, audio worker and dispatcher threads; attach target TID, thread-start identity and caller program counter. No per-op printf. If instrumentation creates meaningful overhead, sample one of every N calls with stable seed and record coverage; preserve uninstrumented A/B control.
3. Separate **exclusive** running CPU nanoseconds using CLOCK_THREAD_CPUTIME_ID and **wall** nanoseconds using CLOCK_MONOTONIC_RAW for trap-entry, kernel_mutex acquisition, SVC emulator, IPC dispatch, AudioOut cmd7 append, cmd8 release, guest-memory copying and resume/return. For nested SVC/IPC spans report parent/child inclusive and exclusive times explicitly; never sum overlapping buckets.
4. Record mutex address and owner, lock result, uncontended vs contended, wait/wake and guest memory-order contract, SVC caller module+offset, and return codes. For AudioOut record only buffer IDs/counts/queue depth, pending and actually released tags, null responses/empty polls, deadlines/timeouts, playback/underrun counters and errors. No PCM bytes in public evidence.
5. Resolve repeated native PCs (e.g. 0x7fa15b0bd4) with **same-run** /proc/PID/maps, exact loaded host ELF/DSO addresses and a symbolized GPL adapter where symbols exist. Map owner guest PCs only against the matching **private SHA-pinned** main/sdk/subsdk images; otherwise retain unresolved module+offset. A round-robin sample count is not on-CPU weighting.
6. Unit tests must exercise arbitration owner/waiter behavior (including thread exit, cancellation, invalid addresses), audio buffer append/release generation, timing brackets and overlapping span detection, AUDOUT/AUDREN categories, lock-X1/unlock-X0 argument decoding, and loss-free ring flush.
7. Run trace OFF versus aggregate ON on the **same installed ELF and same Loading phase**, bounded under the 300 MiB guard with equivalent settings. Correlate CPU seconds and latency to asset/scene progress rather than Loading animation presents. If sampling itself changes behavior, back down the sampling rate.

**Conditional implementation options — only after a measured diagnosis:**

- **Verified AudioOut empty polling dominates:** inspect the actual audout:u contract and event notification. Replace a costly polling path only with equivalent stateful wait/notification preserving queue release, timeouts, cancellation and sound latency. If polling is cheap and valid, **do not change it**.
- **Measured uncontended SVC trap path dominates:** specialize only a *proven* ABI case in the Horizon arbitration bridge, preserving lock owner, acquire/release, wake ordering, invalid input and return semantics. Build a synthetic lock/wait/release fixture and use a reversible identity-guarded fast path, not a global return-success hack.
- **Measured guest ZRAM restore or Unity/IL2CPP CPU dominates:** abandon the AudioOut hypothesis and profile the actual page/guest PC path before making a narrowly proven change. Never hide a deadlock by changing timer units or skipping SleepThread.
- **Measured GPU submission dominates:** switch attention to GL/replay instrumentation, not guest mutex optimizations.

**PASS:** inclusive and exclusive CPU/wall are attributable across all relevant threads and a single correct fix improves actual scene-progress time, without audible/scheduler regressions. **STOP:** lost wakeups, dropped PCM buffers, unaccounted nested timings, bad native PC identity or profiler overhead too large for comparison.

### 28.8. W0: distinguish a truly loading world from a stuck renderer or scene logic

Even after GPU memory is safe, the current Loading screen is **not** world evidence. Use owner-private, read-only main NSO and IL2CPP/Unity metadata pinned to the exact merged image. Do not assume game-specific Unity methods or offsets from West of Loathing.

1. Locate the actual Unity first-world scene load request, async operation progress/activation, scene activation callback, enabled game camera and the real player object's transform/Update. Derive one minimal, exact caller/field identity per milestone and guard any observer with private source hash, module offset and version.
2. Expose run-scoped phase receipts (bounded): NEWGAME_CONFIRMED, LOADING_ENTERED, SCENE_REQUESTED, SCENE_LOADED, SCENE_ACTIVATED, FIRST_CAMERA, FIRST_PLAYER_UPDATE, FIRST_WORLD_DRAW and PLAYER_MOVED. Bind each to run_uuid, owner PID/starttime, guest module/PC, presenter serial and monotonic timestamp. The exact internal names are proposed evidence names, **not claims that existing hook symbols already exist**.
3. If the phase stalls, classify with **mutually exclusive** evidence: ongoing RomFS/deferred BC texture work, main-thread executing IL2CPP/GC, SVC/event wait, guest ZRAM faults, blocked activation, shader STOP, GL resource stop, or scene active with wrong pixels. An unchanging present serial can coexist with a living loader; do not infer deadlock from the spinner alone.
4. If scene activation occurs but no world pixels appear, see W1. If the asset pipeline is progressing but slowly, profile CPU and storage events rather than repeatedly extending guest timeout to unbounded durations.

**PASS:** an independent log and live screenshot can prove one precise first-world scene milestone. **STOP:** world assertions based solely on nonblack pixels, Loading screen text, linked shader or counters.

### 28.9. W1: validate the first world frame, four MRT attachments, all shader bindings

1. At first world draw, capture a **small, bounded** actual program-pair census including vertex44 and fragment45 and any newly demanded program, each with code+control hash, GL program link and **draw receipt**. Fragment45's earlier link alone does not prove it wrote a target.
2. Validate its output layout across all **four** color attachments: GL_COLOR_ATTACHMENT0–3, glDrawBuffers settings, per-target dimensions/format/sample count, GLSL fragment output location 0–3, GL_FRAMEBUFFER_COMPLETE, blend/color mask/depth/stencil state and producer/consumer ordering. Preserve all outputs; do not collapse a four-MRT shader to one RGBA output to make it render.
3. Trace the seven TEST shader substitutes in a **real world draw census**. A TEST shader unused on the menu may be required for world geometry, lighting or MSAA. For an actually demanded placeholder, capture exact shader identity in the **owner-private** workspace, translate with the existing offline pipeline and append with tools/append_program.py without rebuilding away previously corrected shader bindings.
4. Audit the native/nvn_render.h fallback which chooses another nonempty cbuf binding if the declared bank is empty. For each new world shader record declared slot, selected slot, code/control identity, byte extent, instance name, literal access and the correct hardware mapping (NVN bank = SDK slot +3). A plausible-looking but wrong fallback can hide sprites or light. Test known-good menu shader c4 -> UBO1 as a regression.
5. If world offscreen targets have pixels but the final screen is blank/black, isolate **world FBO -> final postprocess/composite -> swapchain -> SDL/EGL surface -> KMS panel** with one-shot live-only readbacks in correct GL context and frame serial, then return original FBO state. A panel blanked by the kernel after an OOM is **not** a blank game render.
6. Confirm that an actual physical D-pad/stick press causes a **player coordinate change plus corresponding live KMS motion**, not only a press receipt or UI animation. Then test room transition and interactions.

**PASS:** actual correct scene, controller-driven player movement and matching KMS pixel output. **STOP:** invalid resource generation, GLSL output mismatch, wrong CBUF bank, corrupted alpha/stencil, TEST placeholders on required draws or new shader STOP.

### 28.10. W2: audio, persistent saves and safe exit are mandatory playability gates

1. On the real handheld, verify audible music and SFX while recording AudioOut queue append->release, nonzero PCM counters and underruns. Nonzero PCM, AudioOut open and consumed-buffer counts **do not prove physical sound**. Keep the ALSA backend and AudioOut return semantics intact.
2. Back up actual owner saves, hash files before launch, change reproducible in-game state, use the in-game save, quit by normal principal flow, then relaunch **cold** and load. Confirm scene, player position, inventory/flags and save-file changes. If broken, narrow-debug Horizon FS paths, permissions, flush/close and atomic writes; never wipe user saves.
3. Prove game PID absent, MainUI/principal/runtime correctly restored, original CPU online mask and sound/video teardown after normal quit, bounded runtime STOP and host TERM. Do not declare kernel OOM solely from a shell Killed token: keep current victim-gated exit taxonomy.
4. Only after world image, physical movement, interactions/dialogue/inventory, audible sound and cold save/load pass may README change from NOT PLAYABLE to a carefully qualified experimental PLAYABLE status.

### 28.11. F0/F1: once gameplay exists, rank FPS work by measured frame-time cost

**Prior measured diagnostics are NOT gameplay benchmarks.** Build209 reported ~249.6ms replay plus ~316.4ms inter-present gap; build217 Loading showed 0.836 main CPU seconds/present. The generic render scale to 640×360 did not significantly improve Loading; the CBUF SubImage change was not a demonstrated frame-rate win. Older ZRAM cpu-compress-ms used CLOCK_MONOTONIC elapsed durations, **not exclusive executing CPU**. glFlush instead of glFinish is not proof of GPU completion and is prohibited as a fake FPS fix.

| Priority after real world | Implementation idea and location | Verification gate |
|---:|---|---|
| 1 | Guest ZRAM cold 10/100/250/500ms one-factor matrix in native/t2_guest_memory.h; record actual compression/restoration **thread CPU**, repeated faults, resident memory, swap and scene progress | Improvement of complete world-frame P95 with safe MemAvailable/CmaFree; 32 MiB floor remains diagnostic-only |
| 2 | Optimize a **measured** costly AudioOut/ArbitrateLock/SVC path in ipc.h/audout.h/threading.h/loader.c | Exact return semantics, wake and PCM ordering, per-thread exclusive on-CPU delta |
| 3 | **Separate new CBUF opportunity:** nvn_render.h currently uses **width=1024 RGBA32F texels** for uniform banks, uploads and clears ~16 KiB per bank even when only ~16–368 bytes are meaningful. Test exact fetch-address requirements; then use smaller correct storage or exact-data/generation-based upload skip behind opt-in flag | Draw/profiler time and pixel parity with original GLSL texelFetch X/Y, row pitch, context-generation invalidation; not a repeat SubImage PR |
| 4 | Resolve/deduplicate live GL texture and FBO generations, properly lifetime-fenced; use measured ETC2/ASTC GPU storage for immutable large atlases | Real driver-memory and physical headroom drop, no wrong alias or stale GL sampler |
| 5 | Profile expensive NVN replay operations: texture/sampler resolution, shader/uniform location, draw state, vertex/index conversion, glBufferData, repeated framebuffer binds | Exclusive CPU/GPU stage improvement; per-context invalidation and unchanged command ordering |
| 6 | Find the true **Lamentum-specific** Unity owner of internal 1920×1080 targets; test 1280×720 **internal** scene rendering with exact camera/CBUF/UV/copy mapping | Correct UI and hitboxes, validated physical KMS, actual GPU cost reduction; physical panel is already 720p |
| 7 | Reversible bloom/noise quality mode after profiling real scene costs | Comparable real screenshots/alpha and whole-frame gains; no blanket removal of depth, blend or stencil |
| 8 | Tune CPU scheduling/affinity/compilation only with real main-thread CPU and thermals; async GPU queue only with complete fences/serial ownership | No NVN_COMMAND_REUSE_BEFORE_COMPLETION, lost audio, owner memory or Spruce cleanup regressions |

**Benchmark protocol:** three independent quiet **>=60-second** runs of stationary world, moving world and interaction/effects separately. Capture presented serials and actual throughput, full-frame P50/P90/P95/P99 (not slow-only frame logs or inverse median alone), scheduler wait and thread CPU, replay/GL/GPU fence time, actual GPU residency, peak RAM, SwapPSS, thermals and input/audio. Report transitions/loading separately, not hidden. Stable 30 FPS requires **complete frame P50 AND P95 <=33.33ms**, preferably P99 <=50ms, without recurring >100ms spikes, and passing W2 correctness. If GPU/CPU remain multiples of this budget, report the achieved world ceiling, not a speculative promise of 30 FPS.

### 28.12. Prioritized PR acceptance queue and experiment rollback

| PR, order | Code/artifact | Host requirements | Safe device pass |
|---|---|---|---|
| T1-run-phase | launcher; tools/load_metrics.py, load_probe.py, newgame_navigate.py, perf_sample.py | Unique run identity; same-inode log reuse; page-specific cursor/controls fixtures; no false PID/STOP | One exact-owner bounded New Game probe, correct phased evidence and cleanup |
| G0-mip-ledger | adapter native/nvn_textures.h, nvn_framebuffers.h; pure storage arithmetic tests | Actual id295 descriptor, base+mip accounting, GL generation/alias dedup, no over/undercharge | Safe early STOP with exact all-class ledger under 300 MiB cap |
| C0-audio-profile | adapter ipc.h/audout.h/guest_profile.h/loader.c | EP_AUDOUT category, all-thread exclusive timings, correct lock X1/unlock X0, nested time guard | Loading trace OFF/ON; measured real CPU/wall hotspot |
| G1-etc-fixture | new self-authored GLES3 test source, no original game | Image byte-size, alpha, sRGB, mip fixture | Correct sampling and actual physical GPU savings on Mali |
| G2-one-atlas | owner-local cache manifest + narrow compressed upload in adapter | Exact source hash/immutability/level/write-epoch, fallback and budget/fence tests | Real safe progression beyond id295 and correct image |
| C1-targeted-fix | one specific measured emulation/service fix | ABI/wake semantics and no lost sound/input | Less CPU per **real scene milestone**, not merely better Loading FPS |
| W0-first-world | scene activation milestones, shader/MRT live receipt | Shader identity/cbuf/attachment tests | First world draw, correct KMS and player Update |
| W2-playable | specific FS/input/audio fixes if found | Private save backup, strict resource lifetime | Physical player movement, SFX/music, interaction, cold save/load and clean exit |
| F1-world-fps | phase-based latency/profiler observer and top one-factor optimization | Same ELF/source/clock/scene, bounded overhead | Three correct world runs; actual frame-time criteria |

**Global safeguards:** retain source baseline 435/435 and only edit runtime through runtime/lamentum-adapter.patch. Never ship proprietary game assets, dumps, keys, saves or transcoded atlas payloads in Git. Preserve strict GL errors, synchronous queue, LC2_TEXTURE_PAGEOUT=0, real GPU command-buffer ownership and all Spruce CPU-state restoration. The 300 MiB charged-texture cap is a **safe diagnostic refusal**, not a validated release optimum; 32 MiB RAM floor is diagnostic only and launcher defaults to 96 MiB. Keep sufficient disk reserve for 512 MiB fileback plus cache/saves/backups. Pin source/ELF/image/catalogue/run_uuid on every experiment. No second principal-game process, no unsafe kill by comm, no unlimited retry loops.

For any future PR, run python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py', git diff --check, the 435-file baseline manifest check in the correct recovered workspace, a pinned ARM64 cross-build, deployed ELF hash verification, and matched rollback-capable A/B. These commands were **not executed in this documentation-only audit**; previous passing host-suite counts above are taken from committed evidence.

**Bottom line:** T1 for reliable evidence, G0/G1/G2 for **safe scene load beyond id295**, C0 for true AudioOut/SVC CPU cost, and W0/W1/W2 for **actual playability** precede any credible 30 FPS claim. §§0–27 remain historical; **§28 is now the implementation order**.

## 29. HEAD 6911da3: Re-audit and Detailed Gameplay/Performance Execution Plan (2026-10-21)

> **LATEST EXECUTION PLAN.** Audited repository [6911da321](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/6911da321e2b3479a575df453a5e4ae427eee38e), including the current adapter patch, 46-entry shader catalogue, launcher, load/navigation tooling, build219 evidence and the [C1 AudioOut source audit](../evidence/C1-audio-owner/README.md). This is a source/evidence reassessment: **no new ELF was compiled or deployed and no new real-device/gameplay benchmark was run for this audit**. Read this section before §§0–28, whose older hypotheses and priorities may be superseded.

**Status: NOT PLAYABLE.** Build219 remains the last evidenced installed ELF (SHA-256 b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a). Actual main menu, New Game configuration, controls prompt, Loading and clean Spruce restoration have been demonstrated. There is still **no verified world scene, physical player movement, audible game audio, cold save/load or gameplay FPS**. The shader catalogue has 46 entries (0–45), including seven TEST substitutes. Entry45 linked, but a shader-link receipt is not proof of a correct draw.

### 29.1. What the previous 92 commits actually delivered

GitHub comparison from the first English-roadmap commit a4d0a2e to this source HEAD reports **92 commits**. The meaningful differences are:

| Workstream | Proven completed | Still unresolved |
|---|---|---|
| Game bring-up | New Game navigation reaches actual Loading. Entries 42–45 were appended. Vertex44 and half-precision four-output fragment45 have byte-pinned compiler/source provenance; fragment45 links. | First world scene, first real draw, all required shader semantics and framebuffer output. TEST placeholders may be required beyond the menu. |
| Memory | Large BC3 atlas is decoded in 128-row stripes, upload can be deferred, guest ZRAM/fileback exist, and 300 MiB texture admission prevents the later unsafe allocation. | The deferred BC path still uploads **decoded GL RGBA** storage. Exact first-use id295 format/mips/immutability and physical driver storage owners remain unknown. |
| Crash handling | Kernel/Mali OOM was observed in a prior unguarded run; a guarded run instead returns T2_TEXTURE_BUDGET before allocating the 8192×8192 resource. OOM classification now requires kernel-victim corroboration. | The guarded refusal still prevents gameplay; raising the cap would recreate risk. |
| Observers | Incremental complete-line byte framing, target HZ=100 CPU ticks, thread starttime, PID/starttime, VFAT executable samefile alias verification, two clean menu-level runs. | Unique run UUID, same-inode truncate/regrow log generation, full phase identity and a semantic New Game oracle. |
| CPU/audio | Loading formerly consumed **0.836 s main-thread CPU per presented Loading frame** in a 20.14s phase with no new asset/texture activity. Audout:u child is now identified: endpoint0x40 cmd7 queues PCM and cmd8 queries released tags. | Per-thread **exclusive CPU/wall time**, actual scheduler waits, audible sound and whether audio/SVC is a real hot spot. The round-robin MOMO samples are not CPU share. |
| Tested FPS ideas | CBUF glTexSubImage2D reuse is **already implemented**, default enabled, without a credible frame-time win. Generic ZERO_RENDER_SCALE=2 was ineffective in Loading. | Shrinking oversized **1024-texel RGBA32F uniform uploads** is a different possible experiment; no world benchmark exists. |
| Correctness | Confirmed SVC lock argument is X1 for 0x1A and **X0** for unlock 0x1B: only 41 real distinct mutex addresses in load-probe-08. | Lock ownership/results, exclusive service costs, GPU allocation accounting, scene rendering and saves. Do not reintroduce the discredited 1011-key or guessed busy-loop claims. |

**Critical evidence distinction:** [load-probe-10](../evidence/load-probe-10/summary.json) ended by operator TERM with charged textures at ~126 MiB and VmSwap near 870 MiB in an **earlier Loading phase**. [load-probe-07](../evidence/load-probe-07/summary.json) instead reached later id295 with a +256 MiB prospective charge, raising the charged total to ~411 MiB against the 300 MiB guard; this run stopped safely. Neither proves the other phase has been fixed. Do not add texture charges, VmSwap, GPU driver accounting and RSS as independent memory totals.

### 29.2. New source finding — the first world may need a renderer feature the menu never used

In runtime/lamentum-adapter.patch, non-ZERO_ZX_GAME native/nvn_commands.h currently handles NI_nvnCommandBufferSetRenderTargets with the following **explicit boundary** in the LC2_RENDER_TARGET_DEPTH path:

~~~c
if (a[0] > 1)
    stop("NVN_RENDER_TARGET_COUNT_REQUIRED", nvn_caller, a[0], 20);
*payload = 16;
~~~

This was documented for the observed **one color target plus depth/stencil** case; it intentionally omits per-target view arrays. Meanwhile [entry45](build218-entry45.md) is a **four-output fragment** translated with fp16-rounding-preserving lowering. Four GLSL outputs **do not necessarily mean** four bound NVN render targets. No current evidence proves a target-count>1 command was reached, or that the four outputs wrote actual world pixels. **This is a concrete compatibility risk, not an established bug.**

**P0-MRT precise next steps:**

1. Before writing a multi-target renderer, add one sparse, strictly bounds-checked receipt for each distinct SetRenderTargets signature after Loading: count; ordered color object IDs; target view mip/layer/face; optional depth/stencil object/view; owner PC; command serial; paired shader ID; and expected lifetime. Redact proprietary pointers/assets from public evidence.
2. Inspect the translated entry45 outputs, location 0–3, actual GL draw buffers, color masks and downstream consumers. Distinguish four declared outputs with one active attachment from actual four-target MRT. Link and compile receipts are **not draw receipts**.
3. If the title keeps count=1, **do not** implement extra targets blindly. Verify actual output0, depth/stencil, producer FBO, postprocessing and KMS output first.
4. If a real count 2–4 occurs, extend native/nvn_commands.h **record size and snapshot ownership** to include the ordered target/view array, optional depth/view, null entries and bounds-checked variable payload. Preserve command serial ordering and replay lifetime.
5. Extend native/nvn_framebuffers.h and native/nvn_render.h to cache attachment **storage generations** and view levels, attach GL_COLOR_ATTACHMENT0..N-1, configure glDrawBuffers, validate framebuffer completeness and preserve blending, color masks, depth/stencil and clear/load/store behavior. Track each actual attachment allocation in the GL ledger. Check the physical GLES3 GL_MAX_COLOR_ATTACHMENTS and GL_MAX_DRAW_BUFFERS first.
6. Host-test count 0/1/2/4, ordered attachment keys, null views, array/mip changes, context loss, command reuse, and four independently read-back synthetic color outputs. Never bypass the STOP by clamping count to 1 or faking successful draws.

**PASS:** actual target-count behavior is known; multi-RT is implemented only if demanded, with correct first-world pixels. **STOP:** invalid views/resource ownership, missing outputs or an unsafe memory increase.

### 29.2a. GL-SRGB — Another concrete GLES3 format-contract defect to test early

**Fresh source-level audit finding:** the LC2 striped BC upload in runtime/lamentum-adapter.patch, native/nvn_textures.h, currently sets a single variable to either 0x8C42 when zero_bc_srgb(t->b.format) is true or GL_RGBA, and passes that same variable as **both the internalformat and the external format**. The other first-use BC materialization path similarly supplies 0x8C42 for both glTexImage2D arguments, and also as the external format for glTexSubImage2D.

0x8C42 denotes legacy GL_SRGB_ALPHA_EXT/GL_SRGB_ALPHA, **not** the valid GLES3 sized storage internal format GL_SRGB8_ALPHA8 (0x8C43). GLES3's standard pixel-data **format** for an sRGB RGBA8 texture is **GL_RGBA**, with GL_UNSIGNED_BYTE data. GLES3 reference: [glTexImage2D / valid internalformat-format-type triples](https://docs.gl/es3/glTexImage2D); [Android Khronos-compatible CTS regression describing exactly the 0x8C42 -> 0x8C43 + GL_RGBA correction](https://android.googlesource.com/platform/cts/+/9a1095c1ed4cf6d1f2fbee4be083ff013dc8b51d).

**This is a source-level GLES3 API mismatch, not yet an on-device demonstrated Loading failure.** It is conditional on an actual sRGB BC path being executed; the latest observed failure is still the earlier 300 MiB texture reservation. Do **not** claim fixing 0x8C42 will bypass id295 or improve FPS. It is nevertheless a cheap, correct compatibility fix worth guarding and testing before accepting new world pixels.

1. Search the entire **effective rebuilt baseline plus adapter overlay** (not only the patch hunk) for 0x8C42, GL_SRGB_ALPHA, zero_bc_srgb, glTexImage2D and glTexSubImage2D. Identify whether the BC path uses GL_UNSIGNED_BYTE versus another upload type, and verify every reachable sRGB variant. Preserve sRGB sampling semantics.
2. For decoded RGBA8 sRGB pixels use **internalformat=GL_SRGB8_ALPHA8**, **format=GL_RGBA**, **type=GL_UNSIGNED_BYTE**. For linear RGBA8 use GL_RGBA8 (sized) with the same GL_RGBA/GL_UNSIGNED_BYTE external pair where supported; do not feed a sized internal enum as the external pixel-data format. On glTexSubImage2D, supply only GL_RGBA/GL_UNSIGNED_BYTE; storage was defined by the earlier glTexImage2D.
3. Create a tiny self-authored GLES3 fixture exercising first allocation, every striped update, first-use lazy materialization, re-upload after a guest write, with both linear and sRGB inputs, a border pixel/alpha gradient and sampled framebuffer readback. Compare with the original game-independent reference fixture; include actual glGetError and a known pixel expectation, not just an empty GL error count.
4. Verify native GL context generation, sampler mip completeness and any framebuffer-versus-texture restrictions. Keep strict COTM_GL_ERROR_IGNORE=0. Do not mask invalid enums by catching and ignoring the GL error.
5. On device, report how frequently the actual Lamentum shader/texture path reaches an sRGB BC image **before** making a performance claim. The patch should reduce compatibility risk and may remove a later GL STOP, but only a traced post-Loading transition proves that.

**PASS:** spec-valid API argument triples and sRGB/linear pixel parity on the actual Mali GLES3 stack; no hidden GL errors. **STOP:** wrong gamma/alpha or any unverified conversion/format. This PR can be implemented and tested **off-device** alongside G0; do not let it displace the proven id295 memory wall as the current priority.

### 29.3. G0 — First fix exact id295/mipmap admission and measure all GL allocations

**Confirmed code risk:** in the adapter's native/nvn_textures.h zero_texture_refresh, deferred BC first-use admission uses base-level width*height*output_bpp, then iterates all texture levels. If an actual deferred texture has multiple mips, its **charged amount can undercount created GL storage**. This is not proof id295 has mips, nor proof it caused the previously reported GPU OOM.

**Implement in one small instrument-first PR:**

1. Derive **id295's exact native descriptor** before first-use reservation: original NVN format, type/target, dimensions 8192², mip count and individual level sizes, sampler/filter and sRGB, guest memory pool alias/root, resource generation, CPU writes and first actual consumer. Confirm independently whether original id295 is **BC3 and immutable**; do not select a BC3-only solution from a size alone.
2. Add a host-pure, checked 64-bit layout calculator for *actual allocated GL internal storage* across levels, layers, faces, samples, block-compressed formats and output conversion. Include BC3 source block rounding versus expanded RGBA GL bytes and correct NPOT mips. Reject overflows and unknown formats rather than silently undercharging.
3. Make texture reserve, GL allocation, storage generation and budget refund **transactional** across all mip levels; admission happens **before** glTexImage2D or glCompressedTexImage2D. On replacement, deletion, alias/resource recreation and context change, accounting must reflect the real object lifetime. A corrected early refusal is a safety improvement, **not** a gameplay regression.
4. Emit a bounded GL ledger covering regular textures, mips and layers, renderbuffers, depth/stencil, up to four MRT images if required, vertex/index/PBO allocations, EGL surface images and transient decoder staging. Count **real storage** and alias relationships; an FBO handle is not another color image. Store context generation, GL storage generation, guest alias/write epoch and last GPU reader.
5. Test one mip versus full chain for 8192² (RGBA8 base **256 MiB**, ideal complete RGBA8 chain ~**341.3 MiB**); 8192×4096 BC3; NPOT, array, cubemap and alias cases; repeated materialization and exact refund. Report bytes separately from unverified driver physical residency.
6. Capture one exact **pre-refusal** memory snapshot: charged classes, safe MemAvailable/CmaFree, process PSS/SwapPSS, GPU driver counters, actual source hash, current scene milestone and exact texture serial. Keep the **300 MiB admission guard**. Avoid OOM reproduction as an information-gathering strategy.

**PASS:** id295 source and GL layout are identified, no undercharge, and formerly unexplained allocations are enumerated or honestly marked unknown. **STOP:** an unresolved alias/in-flight reader, GL error or any memory floor breach.

### 29.4. G1/G2 — Safely pass the 8192² wall (conditional compressed-atlas route)

A single RGBA8 8192² level is **256 MiB**. An ETC2 RGBA8/EAC compressed payload of the same dimensions is **64 MiB** (theoretical 192 MiB reduction); mips, alignment and the **Mali driver's actual physical residency** can change the outcome. The current 128-row BC stripe decoder cuts temporary host storage but **does not keep GL textures compressed**. ZRAM does not reclaim Mali's resident decoded RGBA storage.

**G1: independent driver/quality proof, before original game data:**

1. Create a self-authored EGL/GLES3 test program with the **same context/driver class** as Lamentum. Query GL renderer/version, maximum texture size, supported compressed internal formats and available physical driver memory metrics. Test ETC2 RGBA8/EAC and sRGB8_ALPHA8 ETC2/EAC. Only test ASTC if the actual extension and upload path are supported.
2. Generate a synthetic test image: opaque/transparent sprite borders, thin text, alpha gradient, dark scene and sRGB gradient. Supply a complete mip chain. Use **valid** compressed image data and exact block sizes. First verify smaller sizes and GL sampling/completeness; approach 8192 only if safe device limits and memory reserve permit it.
3. Run separate RGBA and compressed arms; compare real framebuffer captures, alpha, filtering, color-space and **observed Mali physical allocation**. If GL accepts ETC2 but driver expands it to RGBA internally, this is **not** a solution.
4. Publish self-authored source and measurements, never private game textures. Do not run the fixture simultaneously with the game.

**G2: one owner-private immutable atlas after G0+G1 PASS:**

1. Match resource id295 against the exact private merged game image, original descriptor, original BC3 bytes, hash, mip chain, sampler view, sRGB and write epoch. **If it is writable, a render target or not actually BC3, stop this branch**; do not convert arbitrary RGBA textures.
2. Offline private cache: **BC3 -> RGBA -> ETC2/EAC**, preserving all required mip levels, alpha, orientation, color space and filtering. Cache manifest must bind source hash, image identity, encoder/version/options, dimensions, internal format, mip sizes, asset content hash and write generation. Original/transcoded payloads stay private.
3. In native/nvn_textures.h add a narrow identity-guarded compressed upload using glCompressedTexImage2D with checked per-level imageSize and the correct texture generation. Ensure the **original 256 MiB RGBA GL allocation does not also happen**. Reserve correct compressed total before upload; invalidate on actual guest content modification and free on GL generation retirement.
4. Do not permit silent cache fallback to the previously unsafe +256 MiB allocation when the 300 MiB guard forbids it. A mismatch must have a documented fail-closed behavior.
5. Verify peak physical GPU memory falls, no missing mip levels, visually correct alpha/color/sprites in a real world screenshot, and **Loading advances beyond the former id295 refusal**. Keep watchdog and clean teardown. One successful upload counter is insufficient.
6. If ETC2 fails physical-memory/visual tests, separately investigate supported ASTC 4×4 and 6×6, proper duplicate GL storage elimination or resource-lifetime reduction. Splitting a dynamic 8192² image into tiles, shader-side BC3 fetch/decode or owner-specific texture-resolution overrides are **P3 research** requiring exact UV/LOD/wrap/mip and game-asset dependencies. Do not ship them as lossless shortcuts.

**If id295 is not immutable sampled BC3:** investigate exact live GL duplicates, renderable attachment requirements, excessive mip chain or long-lived temporary resources instead. Deleting an apparently unused GL object or dropping mips without the actual last-reader/sampler dependency is unsafe. Neither raising the 300 MiB guard nor lowering the 32 MiB RAM floor is an acceptable workaround.

### 29.5. C0 — Measure actual Loading CPU and AudioOut/ArbitrateLock cost

The 20.14-second static Loading phase with **0.836 main CPU second per presented Loading frame**, 1.63 total thread CPU seconds/frame and no new RomFS/texture activity is **not normal 30 FPS gameplay**. Its cause remains unknown. load-probe-08's **29,140 audout cmd8** queries, **10,376 cmd7** appends and SVC 0x1A/0x1B counts establish frequency, **not CPU duration**. The 400 MOMO samples were distributed across 32 threads, not on-CPU-weighted; their raw fractions cannot diagnose the main hot function.

**The source already has useful instrumentation, so extend it rather than build a second profiler:**

1. In native/ipc.h classify the verified EP_AUDOUT child as **AUDIO**, while preserving manager/child and CMIF command type distinctions. Currently AUDREN gets AUDIO and AUDOUT falls under OTHER. Create an enum/dispatch fixture; classification must not change runtime audio behavior.
2. Extend native/guest_profile.h and loader.c from **presenting-thread-only TLS report** to bounded **all relevant threads** with stable TID/starttime and one report per window. Collect inclusive and **exclusive** CLOCK_THREAD_CPUTIME_ID execution and MONOTONIC_RAW elapsed time for trap entry/return, acquisition of kernel_mutex, wait/contend, SVC emulator, IPC, AudioOut cmd7/8, guest-memory accesses, ZRAM faults and host scheduler wait. Parent IPC+SVC spans **overlap**; never add them.
3. Record return values, mutex owner/waiter/wake for 0x1A/0x1B, correct address register **lock X1 / unlock X0**, AudioOut queue depth, appended versus released tags, empty polls, underruns and result codes. Do **not** publish PCM payloads or identify every cmd8 as broken busy waiting.
4. Resolve native interrupted PCs only with **same-run** /proc/PID/maps and exact ELF/DSO build IDs; resolve private game NSO callers by hash-pinned module+offset. Combine target HZ=100 process/thread CPU ticks, schedstat and actual phase timestamps rather than a round-robin sample fraction.
5. A/B the profiler OFF and sampled aggregate ON on an equivalent **Loading phase** and compute observation overhead. Emit total running CPU, blocked wall time, time per meaningful asset/scene milestone and full exclusive cost distribution; not just Loading-spinner presents. Sample at a lower rate if overhead exceeds about 5%.
6. **Conditional fix, only if verified:** costly repeated **empty AudioOut polls** -> implement contract-correct event/wait semantics retaining PCM lifecycle, timeouts and sound latency; expensive uncontended SVC bridge -> optimize precisely that ABI case with acquire/release/ownership/wake fixtures; repeated ZRAM restores -> try measured cold intervals 10/100/250/500 ms with real thread CPU accounting and RAM headroom; actual Unity/IL2CPP work -> profile game caller and avoid generic SVC hacks.
7. Never globally skip ArbitrateLock, fabricate SVC completion, disable the audio service or unconditionally replace glFinish with glFlush. Measure **time to scene progress** after the change; a smoother spinner with the world still blocked is not success.

**PASS:** reproducible exclusive CPU owner, valid semantic optimization (if warranted), and faster real scene milestones with safe memory/audio. **STOP:** missed wakeups, reordered PCM releases, profiler overhead masking the effect or unverified guest identity.

### 29.6. T1 — Finish evidence identity and unify two New Game navigators

The rechecked port/Lamentum.sh still sets **COTM_RUN_ID=$(date +%s)**: same-second runs may reuse that token. tools/load_metrics.py already processes complete byte-framed lines and opened-log dev/inode identity, but ambiguous **same-inode truncation and regrowth** remains. tools/load_probe.py still blindly sends **two Down presses** on the New Game configuration screen and accepts a generic >=120 changed-cells transition; tools/newgame_navigate.py is a different bottom-anchor walker. These paths remain less reliable than a single explicitly verified page-state contract. Keep the existing process os.path.samefile fix for VFAT aliases; do **not** reimplement it.

**T1 implementation:**

1. Generate a unique run UUID from /proc/sys/kernel/random/uuid at principal launch, propagate it to game and observer, and emit a full run/build header **before** performance records. Bind run UUID, boot ID, PID/starttime, executable dev/inode and SHA-256, launcher SHA, private image SHA and shader catalogue SHA.
2. Have each log poll return dev/inode, cursor byte offset, complete-line boundary and header/run-generation identity. On same-inode truncate/regrow, detect changed generation and fail with LOG_GENERATION_CHANGED; never append counters from different executions solely because an inode/offset still matches.
3. Merge the host navigators into a single bounded state machine: MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> WORLD_OR_STOP. Confirm selected row and page-specific prompt/state **plus a new present serial** after each press. Reject bright-band/background animation as proof of controls or world. Keep explicit press/release and **EV_KEY305 Confirm versus 304 Back** receipts.
4. Host-only tests: same-second restart, different ELF with same basename, VFAT aliases to the **same inode** and distinct copies, PID/TID reuse, partial UTF-8/log rotation/truncate/regrow, animated controls screen, a dropped or duplicated press, old post-OOM MainUI capture and STOP vs host TERM vs unproven SIGKILL.
5. Combine T1 with G0 pre-stop and C0 sparse profiling in **one** bounded safe New Game arm after host fixtures, then classify the first meaningful new frontier. Do not spend additional hardware cycles on menu-only timeout confirmation.

### 29.7. W0/W1 — Define the first playable world as real scene and pixel evidence

**After memory-safe progression past id295:**

1. In the private, SHA-pinned Unity 2019.4.4f1 IL2CPP main and metadata, locate the actual first-world asynchronous scene request, activation, camera, player spawn/Update and room transition. Only emit provenance-backed receipts, e.g. SCENE_REQUESTED, SCENE_LOADED, SCENE_ACTIVATED, FIRST_CAMERA, FIRST_PLAYER_UPDATE, FIRST_WORLD_DRAW, PLAYER_MOVED, with module+offset, monotonic time, owner PID and presenter serial. These are **proposed observers**, not existing verified game symbols.
2. If stuck in Loading, distinguish continued RomFS/texture/BC work, heavy guest IL2CPP CPU, AudioOut/SVC waiting, ZRAM restoring, an incomplete async activation and the first GL/shader STOP. An unchanged spinner does not establish a deadlock. Extend timeouts only if progress is measurable and resources are safe.
3. Obtain the actual world-stage shader program/draw census. Verify entry44/45 **draw execution**, all output locations, and which of the **seven TEST substitute** programs are actually invoked. Append genuinely missing real translations through tools/append_program.py and preserve earlier code/control/UBO bank corrections; don't regenerate the catalogue blindly.
4. Trace the CBUF declared slot versus chosen runtime slot: build202's c4 -> NVN UBO1 is required; a fallback to a different **nonempty** bank may hide incorrect world transforms. Check fragment literals, samplers, alpha/stencil/depth and program-specific texelFetch range.
5. Execute §29.2 render-target-count decision. If correct world offscreen pixels exist but the KMS panel is blank, isolate in order: world producer FBO, postprocess/composite, EGL surface/swap and actual physical KMS scanout. One-shot glReadPixels must use the correct context/serial and restore FBO state. A blank panel after kernel OOM is **not** a rendering result.
6. On real hardware verify **physical** stick/D-pad input changes the player's position and visible world, not just injected menu button receipts. Then validate interactions, inventory, dialogue and one room transition.

**W0 pass:** activated scene and real camera/player draw evidence. **W1 pass:** correct, visible live-world pixels and physical movement. A "Loading..." screen, fragment45 link, or Spruce thumbnail is not a pass.

### 29.8. W2 — Playability gate: sound, persistence and cleanup

Only call the port experimentally playable after real-world rendering and physical controls work **and** these tests pass:

- Audible game music **and** SFX through the handheld's actual speakers/headphone output, with valid AudioOut append/release order; nonzero PCM counters alone are insufficient.
- Owner save backup/hash -> interact to change a real game flag/inventory/position -> in-game save -> clean quit -> **cold restart** -> load -> verify that exact state. Debug FS mapping/flush/rename without deleting or publishing private saves.
- Movement, dialogue, inventory, interaction, room transition, correctly translated necessary shaders, faithful scene colors/alpha/stencil, and game exit to Spruce.
- No orphan game PID, correct principal/MainUI/audio/SDL teardown, and restoration of original CPU online mask under normal exit, runtime STOP and bounded host TERM.

Passing at 1–5 FPS is **playability progress**, not meeting the **30 FPS** performance target.

### 29.9. F1 — Real-world performance experiments in priority order *after* W1/W2

The older figures (build202 menu ~500–600 ms per present; build209 guest gap ~316 ms + replay ~250 ms; build217 0.836 main CPU s/Loading present) are **not world FPS**. A previous generic ZERO_RENDER_SCALE=2 did not improve Loading materially. glFlush-only submission is unsafe as a completion substitute. Re-measure the actual world **before** making any optimization a default.

| Measured dominant world cost | First targeted optimization | Acceptance guard |
|---|---|---|
| ZRAM page fault/recompression thread CPU | native/t2_guest_memory.h cold 10/100/250/500ms and selective verified hot-range residency, changed **one factor per arm** | Real CLOCK_THREAD_CPUTIME_ID CPU, repeated-fault rate, memory floor and full-frame P95 |
| Excessive uniform texture transfer | native/nvn_render.h still uses ~**1024 RGBA32F texels (16 KiB)** per active bank even when actual data may be tens/hundreds of bytes: audit maximum shader texelFetch offset, then test exact smaller storage or byte-exact generation skip | Preserve GL fetch layout and build202 bank provenance. glTexSubImage2D is **already implemented**, not new work |
| NVN replay CPU | Profile sampler/texture descriptor resolution, GL state churn, VBO/IBO conversion, FBO rebinding and glBufferData; optimize only the measured exclusive bucket | Correct resource generations/context invalidation, identical draws and lower **complete frame** P95 |
| GPU shading/RT bandwidth | Verify the actual **Lamentum-specific 1920×1080** owner and internal 1280×720 option, or quality-gated bloom/noise tier | Correct UI, camera UVs, sprite text and input hitboxes. The physical panel is already 720p |
| GPU storage thrashing | Compressed **immutable** atlas cache, lifetime-fenced GL storage dedup/release | Real Mali physical memory reduction, no stale aliases or visual corruption |
| Measured AudioOut/SVC execution CPU | Strictly correct event waiting or uncontended arbitration fast path from §29.5 | No lost wakeups, PCM gaps or bogus guest results |
| Actual Unity/IL2CPP main CPU | Source-pinned guest caller/profile and safe game-level quality/GC/config path if available | Preserved game clock/deltaTime and complete frame improvements |
| GPU queue waits | Only explore correct GLsync/serial-backed overlap after safe synchronous profile | Never NVN_COMMAND_REUSE_BEFORE_COMPLETION or EGL_BAD_SURFACE |

**Benchmark:** three independent quiet, warmed-up **>=60 s** real-world routes per tested mode (stationary, movement, interactions/effects; transitions reported separately). Capture exact presented-frame throughput, **complete frame P50/P90/P95/P99**, host/guest executing CPU and runnable wait, replay and fence time, actual physical GPU memory, MemAvailable/CmaFree/SwapPSS and device temperature/clocks. Confirm screenshots, controls, audio, saves and clean exit for A and B. Consistent 30 FPS requires **P50 and P95 <=33.33 ms** per complete gameplay frame, actual throughput around 30/s and no persistent >100 ms spikes, with correctness. Do not claim a menu or Loading number is gameplay FPS.

### 29.10. Ordered PR backlog, dependencies and evidence gates

| Order | PR | Exact engineering outcome | Device acceptance |
|---:|---|---|---|
| 1 | **G0-storage**: adapter native/nvn_textures.h, native/nvn_framebuffers.h and pure texture layout tests | Exact id295 original format/mips/alias, no budget undercount, GL object/storage lifetime ledger | One **guarded 300 MiB** New Game arm with exact pre-refusal receipt and clean cleanup |
| 2 | **G1-ETC2**: independent self-authored GLES3 compressed texture fixture | Device-valid format/mips/alpha/sRGB and **physical** resident-memory comparison, no original assets | Standalone fixture, not concurrent with Lamentum |
| 3 | **T1-owned-run**: port/Lamentum.sh, tools/load_metrics.py, tools/load_probe.py and tools/newgame_navigate.py | Unique run UUID, log generation integrity, one state machine, host regression tests | Safe source/ELF/scene-identified New Game run |
| 4 | **C0-CPU**: adapter native/guest_profile.h, ipc.h, audout.h, loader.c | Actual all-thread exclusive AudioOut/SVC/scheduler time, correct X1/X0 lock operands | Loading trace OFF vs ON; time to scene milestones |
| 5 | **G2-one-atlas**: owner-private content-addressed cache, adapter native/nvn_textures.h | **Only if G0 proves immutable BC3 and G1 proves ETC2 physical savings**; exact mips/identity/write epoch/transactional admission | Progress **beyond** id295 with lower real Mali memory and correct pixels |
| 6 | **W0/W1-world**: proven Unity milestone observer, shader tail, and **conditional** NVN multi-RT support | Exact scene activated, correct program45 draw, essential shaders, GL attachments/CBUF/composite | Genuine world image + physical movement |
| 7 | **W2-playable**: observed audio/FS/input corrections only | Audible sound, interaction, cold save/load, normal exit | Reproducible functional game session |
| 8 | **F1-world-30fps**: quiet profiler, one measured optimization per PR | Independent complete frame distributions and reversible A/B | True gameplay P95 and stable 30 FPS gate |

**Execution rules:** only one active principal/game process at a time; back up owner ELF/launcher/saves; verify disk reserve and CPU mask; preserve recovered baseline SHA (435/435), exact shader catalogue and source/image pins; use a pinned cross-build and verify installed executable SHA; keep strict GL errors, synchronous queue and disabled pageout; use exact-owner host watchdog; verify after STOP/TERM the game is gone and Spruce/CPU state restored. The **300 MiB charged-texture cap** is a conservative **diagnostic** boundary, not a qualified production preset; the **32 MiB RAM floor** remains diagnostic only and the launcher defaults to 96 MiB. Do not raise admission to the previously OOM-prone configuration or silently disable the guards.

Recommended host-side checks after every change (in the actual correct source workspace, not executed in this audit):

~~~sh
sha256sum -c tools/baseline-manifest.sha256
python3 -W error::ResourceWarning -m unittest discover -s tools -p 'test_*.py'
git diff --check
# Then use README's pinned ARM64 Docker build and independently hash the installed ELF.
~~~

**Immediate best next test:** after implementing G0 sparse descriptor/GL ledger + T1 run identity + C0 bounded exclusive profiler, run **one** safe New Game probe that can answer which **actual** GL object id295 is, whether it has mips, where physical memory is going, what actually burns Loading CPU, and what the **next** scene milestone/STOP is. Those answers decide whether G2 ETC2, audio synchronization, shader/MRT, or another path is the real next fix. Do not spend further device time reconfirming menu-only functionality.

**Conclusion:** compatibility and safe instrumentation have genuinely improved, but playable gameplay and 30 FPS remain undemonstrated. The realistic critical path is **G0 allocation identity -> proven G1 compressed driver support -> conditional G2 atlas residency reduction -> W0/W1 game scene and correct render target/CBUF/shaders -> W2 audio/controls/save -> F1 measured performance**, while **C0** runs in parallel to diagnose CPU pressure. Avoid speculative renderer rewrites, unsafe allocation-budget increases, and FPS claims from Loading.

## 30. Execution follow-up — collector repair, not C0 or gameplay acceptance (2026-10-21)

Reviewed current upstream **46ea9a8** and §29 before implementation. **§29 remains the
execution queue**. This section records actual subsequent work and withdraws unsupported
interpretations; it does not replace the G0/T1/G1 critical path.

Detailed report: [C0 profiler audit](c0-profiler-audit.md). Evidence:
[self-authored TSPS fixture](../evidence/C0-profiler-validation/README.md).

| Item | Observed outcome / acceptance boundary |
|---|---|
| Historical swap-priority-01 | Harness **8**, matched kernel-victim OOM, original priority restored. One negative unmatched-phase arm, not a causal proof of a universal swap policy. |
| Historical C1-svc-cost-01 | Harness **0**, TIME_LIMIT, cleanup clean; TLS threshold/tail loss and TID-dropping reduction invalidate the claimed complete handler totals. **C1/C0 not closed.** |
| Historical C2-bc-decode-01 | Host collection interrupted; retained 319-present snapshot is preliminary, not final. Missing BC rows do not mean zero work. A later boot's log is not a replacement receipt. |
| Collector repair | Bounded 128-thread registry, TID/starttime, explicit stop-time tails, true child-subtracted exclusive time, raw independent clocks, invalid/in-flight/overflow coverage, cumulative snapshot parser preserving thread generations. |
| Host validation | **126 tests PASS**, including short-lived tails, nesting, invalid clocks, raw wall<CPU, valid zero timestamps, TID reuse, overflow/busy snapshots and missing/truncated reports. |
| Rebuild | **435/435** baseline files verified; AArch64 build225 succeeds. Exact built header matches the overlay. Game ELF built **but NOT deployed**. |
| Device component fixture | CPU-only self-authored program through principal; ON/OFF **0/0**, **4 retired thread generations / 12 rows**, synthetic wait/BC/release counts **12/12/4**, clean KMS Spruce restoration, CPU mask **4-7** preserved. No game/display/audio workload was tested. |
| Installed port / policy | Build223 and game launcher hashes unchanged; no texture/swap/quota/admission policy experiment in this follow-up. |

The old **1.98 ms/present / 0.293% core / "mutex calls absent" / "C1 closed"** verdicts
are withdrawn. The older SVC histograms were parsed from **logged calls**, not round-robin
PC sample slots. Anonymous VMAs do not identify texture versus guest/driver ownership, so
the later **"99.66% anonymous proves GPU/textures irrelevant"** verdict is withdrawn too.
Keep id295's later guarded GPU reservation as an independent proven hazard.

**Remaining:** complete G0 id295 descriptor/storage/mips/lifetimes and T1 run UUID/phase
navigation, G1 independent compressed driver fixture, then one guarded combined New Game
arm. C0 still needs trap/IPC/wait/queue outcomes, same-run symbols and a matched Loading
profiler OFF/ON overhead qualification. The independent CPU fixture is not that benchmark.
No new world scene, physical player movement, audible audio, cold save/load or gameplay FPS
is demonstrated. Re-fetch/read roadmap updates every **30–60 minutes of active work** and
before the next experimental phase; record revisions and detailed results in the repo.

## 31. G0 component follow-up — checked payload/admission, not G0 acceptance (2026-10-21)

Reviewed upstream **14d8f80** and **§29.3 / §30**. Detailed source, tests, scope and
remaining gates: [G0 storage layout](g0-storage-layout.md); executed artifacts:
[evidence/G0-storage-layout](../evidence/G0-storage-layout/README.md).

- Added host-pure checked uint64 format-defined layouts across NPOT mips, layers,
  cube faces, 3D depth, realized sample count, BC3 source rounding, expanded RGBA
  and explicitly sized ETC2/ASTC formats. Unknown/unsized formats and overflows
  reject without publishing a partial result. This is **not physical residency**
  and does not certify driver format support.
- Deferred-BC first-use admission now calculates the complete decoded mip payload
  before the existing budget check/first GL bind; repeated identical reservations
  do not double charge. **Eligibility still requires one mip**. The two-mip
  refusal is a synthetic safety regression, not proof id295 actually has mips.
- Compiled C: 8192-square RGBA8 = **268435456 bytes** for one level,
  **335544320** for two, **357913940** for the complete chain. The two-level
  fixture refuses under **300 MiB**, before its simulated GL site.
- **138 host tests PASS**, including 12 G0 tests / 1024 randomized reference
  cases. All 12 also pass compiler trap-on-UB instrumentation. The initial
  ordinary UBSan link failure (missing host runtime library) is retained, not
  reported as execution. **435/435** baseline files and pinned AArch64 build226
  pass; source/header and shader-catalogue identity are recorded.
- **Build226 is not deployed. No device/game/FPS test in this step.** Original
  assets, GL API triples, texture policy/eligibility, floors, swap and shader
  catalogue are not changed. The §29.2 sRGB issue remains unresolved.

**Still open:** exact id295 source/descriptor and T1 run/phase identity, complete
transactional GL generations/refund/alias/context lifetime and all-class ledger,
G1 physical/visual driver proof, real world/render/input/audio/save gates and
stable gameplay **30 FPS**. This narrow arithmetic guard does not close G0 or
justify an unguarded allocation/OOM retry.


## 32. HEAD 0caf515: Current Gameplay Blockers and Next Implementation Queue (2026-10-21)

> **CURRENT EXECUTION PLAN, source/evidence audit at [0caf515](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/0caf5159a9de6e029208fd8959f990181b67113f).** Sections 0–31 retain valuable implementation contracts but their earlier priority labels are superseded. **NOT PLAYABLE: no first-world scene, physical movement, audible audio or cold save/load has been verified. No device game run, new ELF deployment or gameplay benchmark occurred in this documentation audit.**

### 32.1. Reconciliation: what was actually done

| Workstream | Implemented / verified | Still open |
|---|---|---|
| Navigation and shaders | Real menu -> New Game configuration -> controls -> Loading reached with injected input; 46 shader catalogue entries, including seven TEST substitutes; fragment45 **linked** in newgame-20 | First world scene, actual fragment45 draw, necessary other shaders, physical movement |
| GPU memory | Earlier id295 8192x8192 prospective 256 MiB decoded RGBA level was stopped safely by a 300 MiB texture budget rather than repeating the observed correlated Mali/kernel OOM | Original format/mips/immutability of id295, physical Mali residency, all-class GL ownership, safe alternative storage |
| Checked GL payload arithmetic | **Already implemented:** native/lc2_gl_storage.h calculates checked full mip/layer/face/sample format-defined bytes, used before deferred BC first-use admission. 138 host tests, 12 G0 tests, 1024 reference cases, 435/435 baseline, AArch64 build226 successful | Build226 **NOT DEPLOYED**; current deferred BC eligibility still **requires one mip**. Synthetic two-mip rejection is not evidence id295 has mips. No physical-memory saving has been demonstrated |
| CPU profiler | **Already implemented:** lc2_cost V2 registers up to 128 thread generations, keeps retired/short-call tails, nested exclusive clock intervals, bounded explicit final reports. The independent CPU fixture passed ON/OFF on device | Build225 game **NOT DEPLOYED**; real-game V2 coverage, complete AudioOut/SVC cost, observation overhead and CPU bottleneck not proven |
| Earlier CPU claim | The older 1.98 ms per present and 0.293% CPU AudioOut estimate, “C1 closed” claim, and absence of BC work are **withdrawn**, because the earlier TLS reporter omitted tails and TIDs and C2 collection was interrupted | Collect new complete real-game measurements, do not classify missing rows as zero |
| Build identity | C0 audit establishes **installed build223** while synthetic fixture was tested. The last proven New Game frontier remains the older **build218–219** series | Next arm must read back its own installed ELF; no transfer of old phases across builds |
| Memory pressure and Loading | Earlier phase used 0.836 CPU seconds per Loading present on the main thread; a distinct build219 Loading window had ~126 MiB charged textures and ~870 MiB VmSwap | Same-run CPU/wait and actual allocation owners; one early-phase sample does not negate later id295 allocation |
| Renderer correctness | UBO c4 -> NVN UBO1 fix and default cbuf glTexSubImage2D reuse **already exist** | Actual GLES3 sRGB format/type mismatch, first-world MRT/render targets, shader program draw/FB output |
| 30 FPS | A verified gameplay benchmark **does not exist** | World W0/W1/W2 first, then measured whole-frame optimization |

Sources: [G0 implementation](g0-storage-layout.md), [C0 correction](c0-profiler-audit.md), [C1 historical correction](c1-bridge-cost.md), [newgame-20](../evidence/newgame-20/summary.json), [GPU ledger](gpu-ledger.md), [roadmap §29](#29-head-6911da3-re-audit-and-detailed-gameplayperformance-execution-plan-2026-10-21). The G0 calculator models **format-defined bytes**, not driver tiling/padding/resident storage. The one-mip 8192-square RGBA8 layout is 268435456 bytes, but **no evidence yet proves how id295 is stored in Mali**.

### 32.2. Execution order and checkpoints: do not optimize a Loading spinner first

**Immediate independent PRs:** A (sRGB GL correctness), B (G0 id295 descriptor and storage ledger), D (T1 unique run/phase identity), E (C0 V2 real-game scope). A self-authored G1 GLES3 compression/memory fixture can be developed off-device in parallel. Avoid spending another 600 seconds confirming that the menu works.

**First guarded New Game arm:** after tests, install a hash-verified ELF with the necessary diagnostics, retain the 300 MiB charged-texture guard and safe owner-approved RAM floor, follow the single verified New Game navigator, and capture either the exact **pre-refusal id295 owner**, a quantified earlier CPU/wait bottleneck, or a new world/shader/GL frontier. These are different outcomes; label them separately.

**Then choose a specific solution:** if id295 is proven immutable sampled BC3 and real Mali ETC2/ASTC compression saves physical memory, implement an owner-private compressed atlas cache. If it is mutable, renderable, not BC3 or compression is ineffective, fix verified duplicate/retained GL storage or use an explicitly quality-limited title-specific texture strategy. Never raise the 300 MiB budget just to see what happens.

**Next functional stages:** W0 = scene activation and first camera/player/world draw; W1 = correct visible pixels and physical movement; W2 = interactions, audible game sound and cold save/load. Only after W1/W2 should 30 FPS be reported for gameplay. If scene activation is blocked **before** id295, prioritize the measured CPU/guest wait or scene-state owner; do not transcode an atlas that was never requested.

### 32.3. PR A — Correct the GLES3 sRGB upload contract now

**Confirmed source defect to test:** native/nvn_textures.h in runtime/lamentum-adapter.patch still passes 0x8C42 as **both internal and external** pixel format in lc2_bc_upload_stripes and parts of zero_texture_refresh. The G0 admission helper already uses the valid *intended* 0x8C43 sized sRGB storage, but the actual legacy GL upload call is unchanged. This is a concrete API-contract mismatch, **not** proof it caused the current Loading stop.

1. Audit the compiled baseline plus overlay for glTexImage2D, glTexSubImage2D, 0x8C42, zero_bc_srgb, output type, mip allocation and every first-use/re-upload path. Do not fix just the striped branch while leaving the non-striped branch invalid.
2. Add a pure format mapper: decoded 8-bit sRGB RGBA -> **internal GL_SRGB8_ALPHA8 (0x8C43), external GL_RGBA, type GL_UNSIGNED_BYTE**; decoded 8-bit linear RGBA -> **internal GL_RGBA8 (0x8058), external GL_RGBA, type GL_UNSIGNED_BYTE**. In glTexSubImage2D pass **external GL_RGBA/type** only. Handle verified float destinations using their real sized format and supported upload type; never coerce unknown data to RGBA8.
3. Make allocation versus update explicit per actual GL storage generation: full glTexImage2D on newly allocated or resized storage, subimage only for valid allocated matching levels. Preserve sRGB sampling/decode behavior and all original texture swizzles.
4. Build a self-authored EGL/GLES3 texture fixture with linear and sRGB ramps, semi-transparent pixel borders, multiple stripe rows (including the partial final stripe), mip-level update and context recreation. Validate glGetError and **pixel readbacks**, not only successful GL calls; account for sRGB decoding in the expected sample values.
5. Use the actual Mali GLES3 context/device for one fixture validation, then compare a guarded menu/newgame regression. Keep COTM_GL_ERROR_IGNORE=0. **Do not claim FPS or id295 progress merely because the format triple was corrected.**

**PASS:** exact valid triples, no GL errors, correct color/alpha; identical owner image and shader catalogue.

### 32.4. PR B — Finish G0: id295 identity, transactional storage lifetime and true driver evidence

**Reuse the new helper instead of recoding it.** Current lc2_bc_lazy_eligible gates target==1, levels==1, and zero_bc_reserve_first_use calls the pure format calculator before budget admission. The two-mip overflow/admission test is a *synthetic future-proof test*, not a reachable current multi-mip lazy case.

**B1 — first-use id295 record, before refusal:**

1. Emit an opt-in, max-once-per-owner receipt **before** t2_texture_budget_add, without reading/restoring huge guest memory: run UUID, phase, present serial, owner/view ID and generation, GL object/context generation, NVN target/format/swizzle/dimensions/depth/levels, per-level decoded byte count, sampler/wrap/LOD, source pool alias/offset/write generation, caller module+offset and original resource origin where proven.
2. Distinguish source facts from hypotheses. Mark BC3, immutability, render-target usage and content hash as proven/false/unproven. Do not infer immutability from the ID or dimensions. Owner-private hashes can be computed offline, **not** by hashing the entire atlas inside a memory-pressure callback.
3. Record the prospective charge and each existing related allocation. If the run stops in an **earlier Loading phase**, retain that evidence and leave id295 reachability unchanged.

**B2 — GL resource ownership ledger, separate code review:**

1. Key storage by (EGL context generation, GL name/object generation, storage generation); link each storage to NVN pool/view alias, current source write epoch, allocated levels/layers/samples and last GPU reader. Distinguish proposal -> admitted -> GL created -> active -> retired/refunded.
2. Instrument all material GL classes: decoded/ordinary textures and mips, renderbuffer/depth/stencil, transient render targets and bloom, VBO/IBO/PBO, EGL surfaces and staging. **Do not count FBO handles as separately allocated images** or count aliases multiple times.
3. Make allocation, replacement, deletion and failure transitions transactional. Verify no undercharging, double-charge, forgotten charge after context loss or premature deletion while a GPU reader remains in flight. A fatal budget STOP may terminate the process before cleanup; fixtures must test it without claiming a rollback happened.
4. Keep **format-defined bytes**, charged budget bytes and **physically measured Mali resident bytes** in distinct columns. If no trustworthy driver memory counter is available, explicitly label the latter unknown; RSS and VmSwap do not prove a texture owner.
5. Host-test one/full mip 8192² RGBA8, 8192x4096 BC3, NPOT, aliases, repeated refresh, duplicate object IDs across context generations, failed GL allocation and GPU fence retirement. Preserve 300 MiB guard and avoid any unsafe memory-floors experiment.
6. In the first safe device arm, capture MemAvailable/CmaFree/PSS/SwapPSS, accepted+rejected GL allocation events and the id295 pre-refusal receipt. Do **not** reproduce OOM as an information-gathering technique.

**PASS:** actual id295 descriptor plus a coherent live resource graph; no unknown amount represented as zero and no new unsafe physical allocation.

### 32.5. PR C — Prove compression on Mali, then make a conditional private atlas cache

A nominal RGBA8 8192² level is **256 MiB**; an ETC2/EAC RGBA8 compressed level is **64 MiB**. The theoretical **192 MiB delta is not a measured Mali memory saving**. Stripe decoding already reduces temporary CPU memory but leaves the GL image decoded.

**C1 synthetic format/quality/residency proof:**

1. Create an owner-independent, self-authored GLES3 fixture and query real renderer, GL_MAX_TEXTURE_SIZE, supported compressed formats/extensions, texture sampling, sRGB and mip completeness. Check ETC2 RGBA/EAC and ETC2 sRGB; probe ASTC only if supported.
2. Prepare valid **compressed blocks**, not raw RGBA bytes passed to glCompressedTexImage2D. Test 256² then 1024², alpha gradient, dark pixels, sprite borders, wrap/LOD and every needed mip, including source sRGB interpretation. Only try 8192² if size limits, free RAM, watchdog and teardown evidence make it safe.
3. Compare accepted GL storage, readback quality and **real observed driver allocation** with decoded RGBA in separate runs. A driver that accepts compressed input but internally expands it has **not** solved the physical-memory problem. Never run the fixture concurrently with the game.

**C2 only if id295 is proven immutable, sampled BC3:**

1. On the owner's machine, hash-pin original merged image, descriptor, source BC3 bytes, mip chain, encoder/version/quality and guest write epoch. Build a private **BC3 -> RGBA -> ETC2/EAC** cache (ASTC only after real support proof). Preserve swizzle, alpha, sRGB and filtering; no game data in Git.
2. Introduce a narrow, fail-closed runtime branch keyed to exact source identity and storage generation. Check compressed mip sizes, reserve compressed storage before glCompressedTexImage2D and verify that **no old 256 MiB decoded RGBA texture is also allocated**.
3. Invalidate on guest writes, cache/source hash mismatch or context loss; never silently fall back to a forbidden large RGBA allocation. Compare real memory and time-to-scene, plus first-world sprites/text/lighting once available.
4. If compressed physical storage is unsupported, or the original texture is mutable/renderable/not BC3, **close C2** and inspect duplicated storage, render-target lifetimes, unused mip allocations and GPU transient buffers. Source-correct lower-resolution or tiling experiments are opt-in, quality-changing **P3**, requiring UV/wrap/LOD/pixel and input parity.

**PASS:** safe progression beyond the former id295 allocation, verified real memory improvement and correct pixels; a mere accepted upload is not enough.

### 32.6. PR D — Use C0 V2 for real-game CPU ownership; discard the invalid C1 verdict

**Existing correctly tested component:** native/lc2_cost.h V2 with bounded registry and explicit final reporting, plus tools/cost_report.py. The 126 host tests and CPU-only TSPS fixture validate its accounting, **not game runtime cost**.

1. Extend V2 scopes to complete signal/trap/SVC entry/return, mutex acquisition and actual wait, IPC parsing and dispatch, AudioOut cmd7 PCM append / cmd8 released-tag query, BC decode, guest-ZRAM fault/restore and host GL queue/fence waits. Separate enclosing inclusive from child-subtracted exclusive CPU/wall time. Report call counts, errors and queued/released tag state, but not PCM.
2. For SVC 0x1A use **lock address X1**, and for 0x1B use **unlock address X0**, both verified. Record actual wait/owner/release result codes and correctly identify endpoint0x40 as the audout:u **child**. Neither frequent calls nor a round-robin PC occupancy fraction equals executed CPU time.
3. Use CLOCK_THREAD_CPUTIME_ID plus CLOCK_MONOTONIC_RAW and source-pinned (TID,starttime). Preserve raw intervals, incomplete/in-flight coverage, missing tail and reporter overflow; **no_complete_report is not zero work**. Include same-run native /proc/PID/maps and guest module+offset for PCs.
4. Measure an equivalent, semantically verified Loading segment with collector OFF versus ON on the same ELF and memory policy. Accept profiler overhead only if bounded (aim <5%) and all relevant workers are included. Recompute host thread CPU, runnable delay, actual wait time and exclusive cost; do not sum overlapping wall clocks across threads.
5. Only after attribution, fix **one** actual hot path: AudioOut empty-poll behavior with contract-correct event waking and real audio; contended SVC acquisition semantics; repeat guest page-restores via one-factor cold-age experiment; decoded BC work; or owner-pinned Unity/IL2CPP execution. Do not globally skip locks, fabricate IPC completion or speed up the guest clock to show smoother Loading frames.

**PASS:** a qualified same-phase performance result that reduces real scene-loading time, with clean audio, memory and scheduler behavior.

### 32.7. PR E — Make run identity, navigation and first-world detection authoritative

**Current known gaps:** port/Lamentum.sh generates COTM_RUN_ID from seconds, so two starts can collide. tools/load_probe.py still sends **two blind Down presses** on the New Game configuration page and accepts generic changed image cells; tools/newgame_navigate.py has a different cursor-driven policy. A screenshot change is not a game-world oracle.

1. Generate a unique run UUID on device (e.g., /proc/sys/kernel/random/uuid), combine boot ID + PID/starttime + installed ELF SHA, and emit a header before collecting FPS/texture logs. Bind owner-image and shader hashes privately. Preserve the existing successful VFAT samefile executable identity check.
2. On log reads, track generation, dev/inode, byte cursor, complete-line framing and header/run UUID. Detect same-inode truncate/regrow and hard-fail with a distinct LOG_GENERATION_CHANGED, rather than reading two runs as one.
3. Implement **one** verified navigator reused by load_probe/newgame_navigate and the harness: MAIN_MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING -> SCENE_ACTIVATED -> WORLD_VISIBLE or STOP. Check highlight position, page-specific stable features, actual press+release and *new present serial* after every action. One long-press can move two menu rows at ~1–2 frames/s.
4. Add source-pinned **scene** receipts SCENE_REQUESTED, SCENE_LOADED, SCENE_ACTIVATED, CAMERA_UPDATED, PLAYER_UPDATE and FIRST_WORLD_DRAW only after verifying their real Unity/IL2CPP native owner in the private image. They are **proposed** events, not currently established symbols.
5. Test same-second restart, PID/TID reuse, log truncate/regrow, false animated-page transitions, duplicated/dropped evdev events, MainUI restored after OOM, operator TERM and kernel victim-verified SIGKILL. Use an external exact-PID watchdog: guest alarm can fail to terminate a stuck title. Protect saves and restore the original CPU mask/frontend.

**PASS:** a single run can say *exactly which phase and scene milestone was reached*; a dark Loading screenshot is not labeled world.

### 32.8. PR F — After the guarded memory wall, diagnose the **first real world frame**

Use this **fail-closed decision tree**, not simultaneous speculative renderer changes:

1. **No scene activation:** measure meaningful asset/IO progress, actual CPU executing code, thread wait/SVC, ZRAM faults, Unity async scene state and last verified milestone. If there is no progress, return to §32.6; a higher timeout cannot cure a deadlock or excessive repeated CPU work.
2. **Scene active, no draw:** get an exact program-pair census and real draw serial for the first world. Verify shader 44/45 **executed** and whether any seven TEST substitutes are required. If an unknown code+control pair appears, append the exact verified translation via tools/append_program.py; preserve prior 46-entry prefix and build202 application c4 -> NVN UBO1 mapping.
3. **NVN render-target STOP:** native/nvn_commands.h currently intentionally rejects SetRenderTargets count>1. Capture actual count, ordered target/view mip/layer/depth, context and command serial first. Four outputs of fragment45 **do not prove** four attachments. If and only if count 2–4 occurs, extend safe variable command record/snapshot/replay, GL_COLOR_ATTACHMENT0..N, glDrawBuffers, depth/stencil/clear/mask and resource lifetime. Test 0/1/2/4 attachments with synthetic four-color readbacks.
4. **World draws but black panel:** verify producer world FBO pixels -> postprocess/bloom -> final composite -> EGL surface/swap -> real KMS scanout using **sparse, owner-context, one-shot** readbacks that restore GL state. Rule out sRGB GL errors, sampler/cbuf bank mismatch, depth/stencil reject and framebuffer-incomplete conditions. Do not mistake the post-OOM Spruce menu for a world capture.
5. **World visible:** test **physical** left stick/D-pad movement, actual player/camera coordinate changes, collision/interaction, inventory/dialogue and one scene transition. Injected evdev menu Confirm does not prove physical game input.
6. **Playability:** verify game music and effects **audibly**, inspect AudioOut PCM append/release without skipping signals, then save -> quit -> **cold** restart -> load with matching inventory/position. Preserve owner saves and confirm all KMS/SDL/MainUI and CPU cleanup.

W0 = scene activated + camera/player updated + first world draw. W1 = correct visible world pixels + physical controls. W2 = interactions, audio and cold save/load. A 1–5 FPS W1 scene is valuable functional progress, **not a 30 FPS result**.

### 32.9. PR G — Performance work after W1/W2, chosen from complete-frame evidence

**Minimum gameplay benchmark:** three independent quiet **>=60-second warmed-up** identical world routes with complete frame P50/P90/P95/P99, actual presented-frame throughput/serials, lost/duplicate frames, CPU running/runnable/blocked, replay and GPU waits, measured physical GPU bytes if available, MemAvailable/CmaFree/SwapPSS and clocks/temperature. Report menu, Loading and world separately. Stable 30 FPS requires full-gameplay-frame **P50 and P95 <=33.33 ms**, actual ~30 correct frames/s and absence of recurring >100 ms stalls, without rendering, sound or save failures.

| Measured dominant cost | Test next | Guard |
|---|---|---|
| CBUF transfer | Current glTexSubImage2D is **already enabled**; measure executed shader max texelFetch and safely shrink **1024-texel RGBA32F bank** or skip byte-identical updates | Proven bank/projection, identical sprites/UI |
| Guest compression | Try cold age 10/100/250/500 ms **one factor per arm** and only later pinned hot ranges | Correct thread CPU, repeated faults, memory safety |
| NVN replay | Exclusive sampler/descriptor, VBO/IBO, GL state, FBO and allocations; exact-generation caching | Resource lifetime/context/serial parity |
| GPU fill/bandwidth | Identify Lamentum-specific owner of internal 1920x1080 render targets; opt-in 1280x720 or reviewed bloom/noise tier | Panel already 720p; preserve text, UV, camera and input hitboxes |
| GL memory | Fenced release/dedup of actual duplicates; physically validated compressed immutable atlas | No alias corruption or fallback OOM |
| Audio/SVC CPU | Correct wait/notify or uncontended fast path **only after** exclusive profiling | Mutex results, released PCM, audible output |
| Actual Unity main CPU | Same-run module/offset and owner-specific safe quality/GC setting if it exists | Clock/deltaTime, scene logic, saves |
| Queue stalls | Proper EGL/GLsync and command generation after proving wait cost | Never NVN_COMMAND_REUSE_BEFORE_COMPLETION or EGL_BAD_SURFACE |

If three same-scene A/B pairs show no full-frame P95 improvement beyond noise, **close that optimization**, preserve evidence and choose the next measured cause. Avoid repeating negative generic ZERO_RENDER_SCALE=2, unsafe glFlush-only completion or arbitrary swap-priority policy as if they were new ideas.

### 32.10. Practical PR sequence, evidence contracts and stop conditions

| Order | PR | Must prove before moving on |
|---|---|---|
| 1 | A: GLES3 decoded sRGB/linear upload triples | Host and device synthetic color/alpha/mip parity, GL error-free |
| 2 | E: unique run + semantic New Game navigator | Synthetic false-menu/restart/log-truncate tests; real run/phase header |
| 3 | B1: pre-refusal id295 resource/alias receipt | Descriptor and stage tied to installed ELF; no cap increase |
| 4 | B2: all-class GL ledger and transactional lifetimes | Repeated first-use, aliases, delete/reallocate/context loss/refunds tested |
| 5 | C1: independent Mali compressed-format physical proof | Sampled pixels + physical allocation, not just a supported enum |
| 6 | D: game-qualified V2 AudioOut/SVC/BC/guest-wait costs | ON/OFF overhead, complete workers and exclusive CPU phase accounting |
| 7 | C2 *conditional*: private owner-hash-pinned compressed atlas | Safely advance beyond id295 while respecting 300 MiB guard |
| 8 | F: source-pinned scene + world framebuffer + necessary shader/MRT | World visible, real physical movement, audible audio, save/load |
| 9 | G: individual whole-frame performance PRs | Three repeated real-world benchmarks; P50/P95 <=33.33ms |

**Per-run evidence:** a single identity.json (commit, build/ELF, overlay/shader, owner image identity, run UUID, boot ID, PID/starttime), preflight.json (actual CPU mask, memory/CMA/swap, saved ELF/owner backups), semantic phase.jsonl (page/press/release/present serial and scene milestones), GL-owner/memory series (charged versus *verified* physical storage), CPU V2 inclusive/exclusive/coverage report, real live KMS captures and cleanup.json (one MainUI, original CPU mask, no game). Include observer overhead, complete STOP/kernel-victim evidence, human-readable decision/rollback. Never commit owner game files, proprietary shader binaries, secrets, PCM or private saves.

**Build checks:** execute applicable Python tests (notably tools/test_gl_storage_layout.py, tools/test_cost_instrumentation.py, tools/test_newgame_navigate.py and new feature tests) and compiled C fixtures. Verify tools/baseline-manifest.sha256 inside the recovered 435-file source tree; apply the exact overlay in the pinned AArch64 container, record the resulting ELF SHA and **read back the installed device ELF SHA**. The local principal harness has owner-specific SSH/paths: never launch it blindly on another device. A build/test is not marked PASS until its own captured receipt exists.

**Stop and change direction** if the phase never reaches id295 (fix the earlier bottleneck first), compression lacks real physical benefit, the original atlas is mutable/renderable, any test violates RAM/CMA bounds, errors are hidden by lenient GL handling, an MRT patch is made without seeing count>1, C0 coverage/overhead is unqualified, or a visual/audio/save regression appears. If safe 30 FPS proves unattainable at reasonable image quality and memory headroom, record the limiting facts rather than promoting an unstable preset.

**Bottom line:** the next meaningful successful milestone is not another shader link, a smaller payload estimate or a higher FPS counter on Loading. It is a **run-identified, safe first-world draw and physical movement** with a trace explaining why Loading progressed. All subsequent rendering and FPS optimizations should be evaluated from that concrete gameplay baseline.

## 33. T1 partial implementation: owned exec/log safety, not phase acceptance (2026-10-21)

Owner roadmap revision **5ed8462** and its new **§32** were fetched, read and merged before publication. **§32 remains the execution plan**; this section records a component result for **§32.7 / PR E**, not a new priority order.

### Implemented and tested

- Mandatory paired `run_identity.py` obtains a target-kernel UUID and nonce, emits `LAMENTUM_RUN_HEADER`, hashes an opened runtime FD and executes that FD. UUID/nonce + boot/PID/starttime + executable dev/inode/SHA identify the attempt; observers independently verify post-exec ownership. Keep the numeric `COTM_RUN_ID` ABI (<=12 decimal characters); the UUID has its own `LAMENTUM_RUN_UUID` key.
- Strict byte-framed collectors reject changed UUID/header/dev/inode or bounded continuity anchors with `LOG_GENERATION_CHANGED`, rather than silently resetting/merging counters. Pending partial headers cannot downgrade an already accepted generation.
- Principal/control observers check the owned executable generation. Host stop attempts are recorded separately from a delivered pidfd TERM; already-exited, mismatched and unsupported outcomes are not attributed as host termination. No unowned numeric-PID fallback.
- Both divergent legacy navigators now refuse default use. `--allow-unverified-navigation` is explicitly diagnostic; it does not qualify page/scene reachability. No unified semantic navigator or scene event has been invented.
- **159 host tests PASS**, Python 3.10 syntax checks and launcher/build Bash syntax pass. A clean curated export repeats the tests and full pinned non-root AArch64 **build227**: **435/435** baseline, packaged helper exact match, both ELF **PT_LOAD** segments match. Whole unstripped ELF hashes differ; no byte-reproducible claim.
- Read-only TSPS checks: Python **3.10.4**, FD exec supported; Python pidfd convenience APIs absent but kernel syscalls **434/424** accept a self `signal=0` probe. The exact final collector rejects the existing unowned log with zero accepted counters. This is protocol/component validation, **not a game run**.

Details and receipts: [T1 implementation](t1-owned-log.md), [evidence](../evidence/T1-owned-log/README.md). The first clean export caught an omitted launcher-test helper fixture; it was staged and the full export checks rerun, without weakening the missing-helper refusal.

### Deliberately not accepted

- **Build227 is NOT DEPLOYED**; installed runtime/helper policy was not changed and no New Game arm or performance benchmark ran.
- Owner-image/catalogue bindings remain explicit `null` / `content_bindings_complete=false`. Header ownership is not full source-content attestation.
- Unified semantic pages, new-present-per-action receipts, source-pinned scene milestones, physical movement, audible audio and cold save/load are still open. Therefore **T1 is NOT CLOSED**.
- Bounded log anchors implement an append-only continuity contract; they do not attest every earlier byte against adversarial rewriting. Device hard-stop/cleanup acceptance and profiler overhead still need a real owned run.
- G0 id295 descriptor/residency/lifetime, C0 game qualification, first world and **30 FPS remain unproven**. No cap/floor/swap or `alias_physical` policy changed.

Next source-correctness work follows **§32.3 / PR A**: audit all decoded sRGB/linear upload paths, test exact GLES3 format/type triples with self-authored color/alpha/mip readbacks, then qualify on Mali. Do not use this safety-component publication as a gameplay claim.

## 34. PR A contract half: legal GLES upload triples (2026-10-21)

Owner plan reviewed at **5ed8462**; this section records work under **§32.3 / PR A** and does not change §32's priority order.

### Implemented

- `native/lc2_gl_format.h`: pure, checked mapper from (API generation, `GL_EXT_sRGB`, source sRGB, payload type) to `{internal, external, type}`. sRGB 8-bit → 0x8C43 (ES3) or 0x8C42 + `GL_EXT_sRGB` (ES2), always `GL_RGBA`/`GL_UNSIGNED_BYTE` externally. Linear 8-bit → 0x8058 (ES3) or unsized `GL_RGBA` (ES2). Float → 0x8814 (ES3) or unsized `GL_RGBA` (ES2). sRGB with float/half, and sRGB without expressible storage, are refused rather than coerced.
- All five decoded/refresh call sites (striped BC upload, non-striped refresh, deferred first-use materialisation, CPU texel flush, partial-mip completion) now pass the client pair explicitly; `zero_mip_complete_storage` takes a resolved spec instead of one format used twice. The double-use value is gone from the overlay entirely.
- Resolution is cached per **EGLContext** (version and extension strings are context state) and leaves the G0 charge-before-GL ordering intact.

### Verified, and what it does not mean

- **166 host tests PASS** (7 new, compiled mapper + overlay source audit), baseline **435/435**, ARM64 **build228** `9f348c6c…00af`, helper unchanged; **build228 is not deployed** and no game run occurred.
- Device: surfaceless GBM fixture on **Mali-G57**, driven through the principal flow. Stored byte 160 samples as **90** (exact sRGB→linear) against a **160** linear control; partial final stripe, mip level 1 bytes and post-recreation upload are byte-exact. Receipts: [evidence](../evidence/gl-upload-format/README.md), [report](gl-upload-format.md).
- The retired triple raises `GL_INVALID_ENUM` in an explicit ES3 context but is **accepted silently** when client version 2 is requested — this driver reports ES3.2 anyway. Therefore the invalid call was latent, not a demonstrated cause of the Loading stop; `COTM_GL_ERROR_IGNORE=0` during a guarded New Game arm is still the way to learn whether it ever executed.
- Still open in PR A: the same audit for render targets/`t2_page` palette uploads (they already use an unsized `GL_RGBA` pair), and any first-world MRT/composite path once a world frame exists. Still open overall: id295 descriptor/residency (PR B), C0 game qualification (PR D), semantic navigation and scene receipts (PR E), first world and W1/W2 (PR F), and therefore **30 FPS**.

## 35. B1 pre-refusal owner receipt (2026-10-21)

Work under **§32.4 / PR B1**; §32's order is unchanged. Owner plan reviewed at **5ed8462**.

- `native/lc2_bc_owner_receipt.h` emits one bounded, opt-in (`LC2_BC_OWNER_RECEIPT=1`) descriptor per owner **immediately before** `t2_texture_budget_add()`, so the refusal that ends the process no longer destroys the id295 evidence. Max 8 owners per run, then `overflow=1`; at most one record per owner id.
- It reads no guest memory (`nvn_pointer`/`memcmp` absent from the body by test) and keeps hypotheses labelled: `immutable=unproven`, `source-hash=not-read`, `gl-allocation=not-attempted`, `driver-physical=unknown`, with `phase`/`present-serial` reported as `unavailable` in this build instead of a fabricated value.
- Recorded fields: run UUID, owner/view id+object, alias, NVN target/format/swizzle/flags/samples/dims/levels, block bytes, upload type, output bpp, prospective charge, charged owner bytes, budget live/peak/charges, guest storage bytes, pool object/address/size/generation/flags/offset, snapshot generation, GL name, depth buffer, draws, target-seen, references, caller, and per-level decoded bytes.
- **170 host tests PASS** (4 new: opt-in by value, once-per-owner with full field set, 40 owners → 8 records + overflow, no guest reads, receipt-before-charge ordering), **435/435** baseline, ARM64 **build229** `b164cffd…4e82f` **not deployed**.

Honest limits: the receipt cannot fire until a run reaches id295 first use, which needs the guarded New Game arm (§32.2) plus a verified navigator (§32.7); content identity/immutability still require offline owner-private hashing; B2's all-class ledger and transactional lifetimes are untouched. No game run, no id295 resolution, no scene and no FPS result.

## 36. build229 installed and menu regression arm (2026-10-21)

First device arm after §34/§35. Installed **build229** (`b164cffd…4e82f`) with its mandatory `run_identity.py` and the current launcher; previous ELF backed up in `lamentum-switch/.before-229/`. Two bounded principal runs, both owned and cleaned up (no cleanup errors, one MainUI, no game process afterwards):

| arm | env | outcome |
|---|---|---|
| `menu-229-01` | defaults (`floor=96`) | header bound, execution verified, `T2_MEMORY_FLOOR` at frame **2** (`available-MiB=54`) |
| `menu-229-02` | `COTM_GL_ERROR_IGNORE=0`, `LC2_BC_OWNER_RECEIPT=1`, `T2_TEXTURE_BUDGET_MIB=300`, **diagnostic** `floor=32` | **55 presents, 52 with pixels** (`peak nonblack=104461 max=255`), stop `T2_MEMORY_FLOOR` at `available-MiB=29`, `VmSwap=496 MB` |

What the second arm establishes:

- The menu still renders after the §34 upload-triple change, with strict GL error checking: the corrected path ran on the **real 8192x4096 BC atlas** (`LC2_BC_STRIPED_UPLOAD id=291`, 4 MiB stripes) and produced **no** GL-error-family line (`ZERO_TEXTURE_REFRESH_GL`, `ZERO_TEXEL_UPLOAD`, `ZERO_CUBE_UPLOAD`, `LC2_GL_UPLOAD_FORMAT`, `ZERO_SRGB_TEXTURE_BACKEND_REQUIRED` all zero).
- The published ELF is proven to boot and present on the device it was built for, with its own run identity (`elf_sha256` in the header equals the installed file).
- The B1 receipt did **not** fire: the menu performs no deferred-BC first use, so that instrument is still unexercised on hardware.

What it does not establish: no navigation, no New Game, no Loading, no scene, no world draw, no id295 descriptor, no gameplay and no frame-rate figure. The attached kmsgrab was taken **after** the run (Spruce restored) and is cleanup evidence only — the picture claim rests on the runtime's own present readback, not on a panel capture. The 32 MiB floor stays explicitly diagnostic; production keeps the safe floor and the 300 MiB texture guard untouched.

Memory fact worth carrying forward: the **menu alone** drives `MemAvailable` from 90 MiB to 29 MiB (VmSwap 496 MB) in ~55 frames, so any next arm must budget for the menu before it can ever afford Loading. Next step remains a verified navigator (§32.7), which is what makes a New Game arm — and therefore B1 and id295 — measurable at all.

## 37. Navigation core, deliberately not yet wired (2026-10-21)

Work under **§32.7 item 3**. Pure host tooling: no adapter change, no build, no device run.

- `tools/navigator.py` is the single decision core: it takes `(page, cursor_y, present_serial)` observations and returns exactly one action (`press down`, `press confirm`, `wait`, `refuse`, `done`), with `overshoot` events preserved.
- Enforced rules, each already a measured failure mode here: one press per **strictly newer** serial; refusal after more than three observations without a new serial; a row move of more than one row reported as overshoot instead of triggering extra presses; a changed picture never treated as a page change; unbanded cursor waits, unknown page refuses; `WORLD_VISIBLE` never reported as verified.
- Rows come from the measured highlight band (`load 425 / newgame 475 / options 525 / credits 575`, tolerance 12), with pitch derived from those numbers.
- **180 host tests PASS** (10 new) covering stale serial, serial stall, overshoot, animated-picture stillness, page-change non-inference, unknown page, zero serial, world non-claim and the row table.

Deliberately open: there is still **no capture-side oracle** turning a KMS frame into `(page, cursor_y)`, so this core drives nothing yet and both legacy navigators remain disabled by default. The next step is the measured extractor plus one real press→serial→row chain on device; only then can a New Game arm measure B1 and id295. No scene, gameplay or FPS claim.

## 38. Measured page/cursor oracle, and the geometry it refuted (2026-10-21)

Work under **§32.7 items 1+3**. One capture arm (`nav-oracle-01`, build229, `COTM_GL_ERROR_IGNORE=0`, `T2_TEXTURE_BUDGET_MIB=300`, diagnostic floor 32 MiB) presented **30 frames, 27 with pixels**, verified its own run identity, cleaned up with no errors, and stopped at `T2_MEMORY_FLOOR`. Two kmsgrab frames were taken **inside** the run.

- `tools/page_oracle.py` classifies a frame as `MAIN_MENU` or `UNKNOWN` (with a reason), and reports the selected row; `tools/navigator.py` then emits exactly one action.
- The live frame **refuted the recorded geometry**: rows are at y **442/492/542/592** (pitch 50, not 425/475/525/575); the selection is a **cursor glyph left of the row** (ink in x 40..120) that is *dimmer than its own text* (26.6 vs 53.5), so contrast-against-text can never find it; text starts at x 140 and the list lives in y 380..660 (the title at y≈174 otherwise reads as a row). Both modules now carry the measured table, and the superseded navigator verdict is preserved in the receipt.
- Real-frame results: boot capture → `UNKNOWN` ("no bright rows"); menu capture → **`MAIN_MENU`, `load`, cursor_y 442**, bands `[442,492,542,590]`; core action → **`press down`, serial 55**.
- **188 host tests PASS** (8 new oracle tests over self-authored frames; the navigator tests now use the measured rows).

Deliberately open: no press was injected in this arm, so the read side is proven and the **press→serial→row chain is still uncaptured**; `NEWGAME_CONFIG`/`CONTROLS`/`LOADING` have no measured features and return `UNKNOWN`; thresholds are calibrated on one frame of this build only. Therefore no navigation result, no New Game, no scene, no id295 and no FPS claim.

## 39. First press → row chain; hold-length overshoot measured on hardware (2026-10-21)

Arm `nav-chain-02` (build229, `COTM_GL_ERROR_IGNORE=0`, `T2_TEXTURE_BUDGET_MIB=300`, diagnostic floor 32 MiB), frames captured **inside** the run, input injected through the owner-checked pad contract:

| step | oracle |
|---|---|
| before (134,434 B) | `MAIN_MENU`, row **`load`**, cursor_y **442** |
| press `down`, 900 ms | — |
| after, 7 s later (137,614 B) | `MAIN_MENU`, row **`options`**, cursor_y **542** |

- One 900 ms press moved the selection **two rows**. That is the documented hold-length failure reproduced on hardware: at ~1 fps a 900 ms hold spans more than one guest sample and the tap latch extends the bit. The core already reports this as `overshoot` instead of two presses; the fix is a shorter, frame-paced tap, not different row arithmetic.
- The oracle read the live menu correctly at **two different cursor positions**, which is the first evidence the calibrated geometry generalises within this menu.
- The **present serial was not read** in this arm: the helper opened `lamentum-switch/latest.log` while the runtime writes `lamentum-switch/logs/latest.log`. The press is therefore **not serial-qualified**, and `serial: 0` is preserved rather than back-filled. The reader is fixed in `tools/load_metrics.py` (`PORT_LOG`, `present_serial()`, `serial_request()`) with two tests, so the next arm can qualify it.
- **190 host tests PASS**; arm stopped at `T2_MEMORY_FLOOR` with zero cleanup errors and verified execution identity; device afterwards `MainUI=1, runtime.sh=1, principal.sh=1, port=0`.

Limits: one press, one page, two frames. No config page, no Loading, no scene, no id295, no FPS. Next step is the same chain with the corrected serial reader and a frame-paced tap, then the New Game configuration page measurement.
## 40. HEAD 0a8b1b05: New Audit — Navigation Bugs, Menu Memory Survival, First World, Then FPS (2026-10-21)

> **LATEST EXECUTION PLAN. Audited source/evidence against main at [0a8b1b05](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/0a8b1b05f821fbc66c2472f6ad007827abf28aca).** This section supersedes the order of §§32–39 while retaining their technical contracts. This is a **read-only source/evidence audit and roadmap revision**: no new TSPS run, ELF deployment, host regression execution, new game build, or frame-rate measurement was performed. The game remains **NOT PLAYABLE**. The immediate blocker is now twofold: current menu runs exhaust RAM *before* New Game; the navigation loop has independently identifiable correctness defects. Do not spend more 520–1800 second runs on guessed controls or make a 30 FPS claim from menu/Loading frames.

### 40.1. Reconcile the previous 110 commits: completed work versus the actual frontier

The previous English baseline section 0 was written at build202. Comparison of main with [the earlier translation commit](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/a4d0a2e5a07dc3a652149ef6592977e7344a6011) finds **110 subsequent commits**, including many incremental docs/evidence and tool repairs. Commit count is not a performance metric.

| Area | Confirmed checked into current main | Evidence and limitations | Next genuine acceptance step |
|---|---|---|---|
| Shader pipeline | 46 catalogue entries, indices 0–45; seven explicit TEST substitutes; fragment45 links | build218 newgame-20 link receipt, **not** a verified visible world draw | Establish scene draw and exact 4-MRT/attachment semantic output, then census TEST use |
| GL upload format | New native/lc2_gl_format.h; five decoded sRGB/linear upload sites no longer misuse 0x8C42 as both storage and external format | 166 host tests and real Mali-G57 surfaceless ramp/stripe/mip/context fixture; build229 menu hit the corrected 8192x4096 id291 path under strict GL; **not** a demonstrated Loading fix | End-to-end real world rendering, partial update and attachment checks |
| Guest memory layout | native/lc2_gl_storage.h checked payload geometry before deferred BC first-use; eligibility still requires one mip | 138 host tests, randomized and UB fixtures, ARM64 build; **not** a physical GPU memory measurement | Read actual id295 descriptor and all-class allocation ledger |
| BC diagnostic | native/lc2_bc_owner_receipt.h records up to eight bounded owner descriptors before texture-budget refusal, without large guest reads | build229 tested with no owner receipt: **menu did not reach deferred BC first use** | A safe owned New Game run that actually reaches id295 or another definitive frontier |
| Run ownership | Mandatory tools/run_identity.py, fresh kernel UUID/nonce, hash-verified executable, generation-bound byte collector and pidfd cleanup | Host and separate target component tests, build229 installed with helper; no proven scene-phase oracle | Bind actual capture/page/serial and phase receipts to same verified run generation |
| CPU profiler | Native lc2_cost V2 128-generation registry, nested wall/CPU accounting and short-call tails; isolated CPU-only fixture | Older 1.98ms/present / 0.293%-of-core / C1-closed estimate explicitly withdrawn | Scope and overhead-qualified **real-game** CPU/wait/AudioOut observations |
| Page/cursor | tools/page_oracle.py identifies MAIN_MENU from real in-run capture; y=442/492/542/592; tools/navigator.py pure state machine | Two real cursor positions on build229; **one 900ms down moved load -> options, skipping newgame** | Fix below code defects; qualify press against new present serial, one-row response and semantic config/controls/Loading page |
| Memory survival | 300MiB charged-texture stop avoids one historical correlated Mali/kernel OOM | build229 default 96MiB floor stops at **frame 2**; diagnostic 32MiB floor stops at **frame 55**, MemAvailable **29MiB**, VmSwap about **496MiB** | Attribute **early menu** physical/resident memory; obtain safe headroom *before* a full New Game attempt |
| First world | Earlier build218–219 navigated menu -> New Game config -> controls -> Loading | id295 expected 8192x8192, one decoded level would be 256MiB; complete format/mips, usage and actual resident allocation still **unproven** | Reach Loading again safely, distinguish memory/CPU loading from invisible world |
| Measured FPS | Historical menu/Loading frame times, generic resolution and cbuf A/B evidence | CBUF subimage already default, no demonstrated improvement; 720p rendering experiment inconclusive; **no real gameplay FPS** | After correct first world and persistence: controlled presented-frame timing |

**Do not regress solved work:** no wholesale shader catalogue regeneration; preserve source/code/control hashes and c4 -> UBO1 bank mapping. Do not redo the sRGB mapper, the pure memory-layout helper, old CBUF TexSubImage change, T1 UUID collector or V2 registry as if absent. They need integration tests, not replacement.

### 40.2. P0-N1 — Fix a reproducible Python bug in the new present-serial request

**New source finding, verified from current tools/load_metrics.py:** the appended serial_request() builds a remote program equivalent to:

~~~python
marker = "NVN_PRESENT_PIXELS frame="
# Current expression (broken for any positive match):
[int(x) for x in re.findall(marker + r"\d+", text)]
~~~

Python re.findall with that expression returns strings such as **"NVN_PRESENT_PIXELS frame=42"**, **not** the integer substring "42". int(x) therefore raises **ValueError** as soon as a present is logged. The current new tests only assert that the correct **path string** appears in serial_request; they do **not execute its returned script** against a matching log. The direct Python present_serial(text) helper parses correctly, but that does not qualify the separate remote code.

**Required patch and tests:**

1. Add a failing test in tools/test_load_metrics.py which executes the **actual returned serial_request() text** with a temporary current-run log substituted for PORT_LOG. Include zero lines, a valid frame=1, multiple records frame=1/42/9, a malformed frame, a partial trailing line, a stale log and a changed generation.
2. If keeping this helper temporarily, use a **capturing regex** and parse only captured digits, e.g.:

~~~python
matches = re.findall(r"NVN_PRESENT_PIXELS frame=(\d+)(?=\s|$)", text)
serial = max((int(n) for n in matches), default=0)
~~~

3. **Preferred permanent fix:** retire the full-file serial_request() from the control path. Use existing tools/load_metrics.py **owned incremental byte-framed** collector (collector_request/fold) and its verified expected_run header to obtain each new present serial. No full latest.log reread per capture: each poll is otherwise O(entire growing log) and may read stale generations. The current collector's 262144-byte bounded reads, record boundaries and generation checks are already implemented.
4. Couple a frame receipt to one run UUID, boot ID, executable identity, process starttime, collector cursor and actual capture window. A serial extracted independently from latest.log is **not** enough when a process restarts or the log is replaced.
5. Host fixture: run A UUID/frame50; rotate/restart to B UUID/frame1; an old polling cursor must return LOG_GENERATION_CHANGED, never allow a fresh input on B because A reported serial50. Add a partial-line split and 30000-line backlog case.
6. End-to-end acceptance on the owner device: before image -> owned serial S -> injected short press -> **new** owned serial S+ (strictly greater) -> after image, same PID/starttime and context; stop without a press if the serial cannot be qualified.

**PASS:** executable remote-script tests and owned-run integration both pass; log growth does not cause increasing O(log-size) polling cost. **STOP:** ValueError, serial=0 after proven presents, log rotation, unqualified serial or mismatched image owner.

### 40.3. P0-N2 — Fix the navigator's overshoot/direction bug before more device presses

**Second concrete current-source finding, tools/navigator.py lines approximately 102–115:**

- After observing load (442), then options (542), Navigation.observe emits an **overshoot event**, but continues to update last_row and returns **press down** whenever row != target. Target newgame (492) is **above** options. A further Down heads toward credits and increases the risk of a wrong Confirm. The implementation is **not fail-closed on overshoot**, despite the doc claiming that the core refuses.
- confirmed_serial is set when Confirm is emitted, but issued_serial is not updated there; use one uniform action-outstanding/acknowledgment contract rather than separate ad-hoc row and confirm paths.
- Three repeated polls without a new serial use a fixed attempt count, not elapsed time or known render latency. When the title takes ~0.5–1.2s to present, a rapid poll loop can refuse healthy work. Use both bounded wall-time and serial progress, never unlimited retries.

**Required state-machine correction:**

1. Add explicit state **IDLE -> ACTION_ISSUED(serial, button, hold) -> AWAIT_NEW_PRESENT -> OBSERVED_EFFECT -> IDLE/DONE/REFUSED**. A press is not an observation. Never issue a second press while the first action is unacknowledged.
2. Compute direction from ordered row indices. If selected index < target index, Down; if selected index > target index, Up. Do not use the hardcoded unconditional Down branch. A row move >1 in the direction of an action must **refuse/require explicit recovery** by default, not just emit a side-event and continue.
3. If recovery is explicitly enabled for a diagnostic arm, release all held buttons and require two stable, same-generation post-action observations before a *single* opposite-direction microtap; never auto-confirm on an ambiguous row.
4. Confirm only if **two independent, newer present observations** agree on MAIN_MENU/newgame with reliable cursor geometry, after button release. A later page must be observed, and it must match the expected next state. If the config page is still UNKNOWN, stop there instead of treating arbitrary changed pixels as confirmation.
5. Determine the pad's hold-to-frame behavior with bounded **short press sweep** (proposed 80 / 150 / 250 / 400ms; **not pre-proven device-safe values**), released between attempts, one accepted row and serial per attempt. Capture edge/hold/adapter latch flags, client button release, and guest HID sample counts. Do not assume 900ms is safe: hardware demonstrated two-row overshoot.
6. Pure tests in tools/test_navigator.py for load->options overshoot; options->newgame direction=Up; single-row movement; stale serial; repeated same-frame polls; Confirm acknowledgment; wrong config page; genuine unseen/lagged frame; two identical animation frames; first observed row already at newgame; normal step count vs a held latch. Ensure tests assert **no additional press** after overshoot in fail-closed mode.
7. Integrate only one navigation driver in tools/load_probe.py and tools/newgame_navigate.py via the pure core. Both legacy paths currently remain disabled unless an explicitly unsafe diagnostic flag is supplied; do not reactivate their 700–1500ms blind holds/content-change gates.

**PASS:** one short press yields exactly one measured row transition, target entry selected and confirmed only after a serial-qualified screenshot, with no wrong-menu actions. **STOP:** a second row on one press, unknown page, missing release receipt, generation change, or stale serial.

### 40.4. P0-N3 — Add semantic state detection for New Game configuration and controls

Current tools/page_oracle.py recognizes **only MAIN_MENU or UNKNOWN**. Other page-name strings in tools/navigator.py are **not** evidence that those pages can currently be detected. The existing launcher/probe needs a verified transition chain.

1. On verified owner-local captures, record a separate **page fingerprint** for MAIN_MENU, NEWGAME_CONFIG, CONTROLS, LOADING and candidate WORLD using small ROIs, menu landmark arrangement, and background-normalized pixel statistics; do not label content solely by global changed-pixel counts. Record image width, height, RGB/gray channel interpretation, stride, rotation, and sample provenance.
2. For New Game config (historically Limited save / Difficulty / New game / Return), track selected row and actual enabled/disabled state. Do not reuse main-menu y values. For controls use independently measured title-specific graphical landmarks; reject UNKNOWN if contrast or page identity is insufficient.
3. Calibrate on **at least two independent frames per state** of the same executable with different animation times and different cursor positions where possible. Hold out a third frame for a false-positive test. A live observation contradicting historical geometry must update only the identity-pinned profile, never silently fall back to the old 425/475/525/575 table.
4. For LOADING, combine a visible Loading motif **with** same-run New Game confirm, RomFS/scene-progress receipts and a later serial. A persistent spinner does not prove scene activation; a nonblack frame does not prove a world.
5. In tools/lamentum_pad_contract.py and principal harness, require **press-owner + capture-owner + log-owner** invariants for every action. Save one machine-readable transition graph with serials, rows, screenshot hashes, exact input (code, press/release/hold), page confidence and refusal reason.
6. Qualify **physical-pad mapping separately** from an agent's evdev injection. Use already established game-specific Button 305=Confirm and 304=Back evidence; do not silently swap them when moving between pages or assume input injection establishes physical controller success.
7. Provide a smoke test with **early intentional stop at New Game configuration** before attempting long Loading. Only after accurate controls/Loading receipts and adequate safe memory headroom should a full game-load arm be permitted.

### 40.5. P0-M0 — New immediate bottleneck: the MENU itself exhausts available RAM

**Critical recent evidence:** build229 menu-229-01 with the launcher default **T2_MEMORY_FLOOR_MIB=96** stopped at frame **2**, available-MiB=54. menu-229-02 using diagnostic floor **32** rendered 55 presents, then stopped with available-MiB=29, VmSwap=495996 KiB. nav-oracle-01 and nav-chain-02 were also bounded by the 32MiB floor. No one should interpret these clean diagnostic stops as evidence that a 96MiB production memory floor can reach New Game.

The next guarded arm must **first** explain this menu-phase loss of headroom, *not* immediately allocate the id295 world atlas.

**M0 implementation details (measurement without behavioral changes):**

1. Add an opt-in **MENU_MEMORY_LEDGER** with at most 1Hz snapshots, + extra at main-menu first frame / each first-use GL allocation / pre-floor refusal. Include run/phase/serial and CPU clock, **MemAvailable, CmaFree, Cached, AnonPages, Shmem, SwapFree, PSI memory**, game VmRSS/VmSwap/SmapsRollup, other-process RSS where permission permits, GPU driver's exposed memory counters, guest managed allocation/dirty/compression/fault totals, and fileback live reservations. Use a small fixed ring rather than logging every texture upload.
2. Compare absolute changes from **just before the launch**, not from a snapshot after the game had already reserved substantial memory. Explicitly distinguish cold boot versus a second attempt with unreclaimed driver/guest storage. Check MainUI cleanup and original CPU mask between runs.
3. Instrument independently **GL texture image storage**, GL renderbuffers (including depth/stencil), buffer objects, EGL surfaces/images, framebuffer attachment owners and MSAA samples, **live versus deferred**, resource generation and retirement. A framebuffer name alone allocates no attachment storage. Use format-defined bytes as an estimate, not as asserted Mali physical residency. Count CPU/guest allocations separately; do not subtract aliased memory twice.
4. Produce a **waterfall per event**: e.g. boot EGL create, first full-screen UI offscreen FBO, id291 8192x4096 stripe materialization, first shader cache, BC fileback setup, guest heap/ZRAM escalation, driver retained allocations. Identify the top 5 storage lifetimes dominating the first 55 presents.
5. Check for **retained title-logo/menu targets and textures** that can be released when the world loads; **only** release after the last proved sampler/FBO/GPU reader and a completed synchronization epoch. Do not use unverified "no draw in past N frames" heuristics as lifetime proof.
6. Guarded A/B interventions, one at a time after measurement: replace duplicate immutable GL storage by a single generation-safe owner; avoid re-uploading known-unchanged atlas stripes; reclaim a verified dead temporary FBO/CPU staging region; shorten the lifetime of read-only guest decompression intermediates; move an identified immutable GPU asset to a validated compressed representation; change a verified oversized offscreen target via an exact title-specific owner. Each intervention needs before/after peak **MemAvailable and driver usage**, not just a smaller charged-texture tally.
7. **Do not turn off guest ZRAM** or turn the floor below 32 to extend the run. Fileback and guest compression can move cost between memory types; no 300MiB texture-budget counter can enforce a board-wide memory ceiling.
8. If menu memory still cannot maintain a **sustained safe margin above the existing 96MiB release floor**, treat playability as blocked before experimenting with larger New Game allocations. Reassess with the specific owner, not unbounded pressure or a longer timeout.

**PASS M0:** an owned, reproducible menu memory waterfall and a correctly attributed dominant allocation family. **PASS M1:** menu survives its relevant observation window with the intended safe floor, no kernel OOM, no unacceptable swap thrash, and identical actual display output. The latter is not yet demonstrated.

### 40.6. P0-M1 — Complete G0/B2 memory accounting and capture the id295 first-use truth

The helper native/lc2_bc_owner_receipt.h is already merged. Its cap of eight owner records is appropriate for a one-off high-pressure arm; do **not** expand it to hash hundreds of MiB of guest memory during Loading.

1. First obtain **M0 menu headroom** and qualified semantic navigation. Only then arrange one guarded New Game arm with unchanged owner-private image/catalogue, strict GL errors, current 300MiB charged-texture budget, verified executable and the smallest essential opt-in owner receipt.
2. Capture the native receipt **before** t2_texture_budget_add: id/object, NVN target, format, swizzle, sample count, 8192-square logical dimensions, real mip count, pixel type and realized format, pool object/offset/size/generation, aliases, charged owner count, first sampler/program/draw, previous same-pool views and any render-target use. Current fields explicitly marked **unavailable/unproven** must remain so until source data is added.
3. Correlate guest source block identity with the **owner's offline content hash** and write epochs, not an enormous runtime memcpy/hash. Confirm BC3 block validity, transparency, sampling-only status, mip chain and immutability **independently**, not by assuming every id=295 is the same content across runs.
4. Make GL storage charging **transactional**: reserve an owner-generation, attempt allocation, publish charge only once valid GL storage is acquired; refund/retire on failed allocation, deletion, replacement, EGL context loss and alias invalidation; fence-retire in-flight readers. Add an independent ledger for texture, renderbuffer, buffer and EGL classes plus a reconciliation gap with driver measurements. Never report driver physical bytes from nominal GLSizedInternalFormat alone.
5. Add pure host fixtures for view aliases, same GL-name reuse, failed TexImage allocation with glGetError, context recreation, a replaced pool, a not-yet-complete fence, 4 MRT color attachments + depth, MSAA, multiple mips and cross-context shared objects. Verify charge invariants and exact one-time retirement.
6. **Fork the diagnosis** based on the actual run: texture-budget stop with id295 -> evaluate M2 below; memory-floor stop before first-use -> return to M0; world loads but is invisible -> W0; no scene progress and no allocations -> C0/Unity scene barrier; new pinned shader stop -> append verified shader only.

**PASS:** one owned receipt with enough original-source facts to select a real intervention, plus correct all-class accounting. **STOP:** owner unknown, early system floor, unclassified GL object, GPU failure, or incomplete source identity. Do not raise the 300MiB guard to force progress.

### 40.7. P1-M2 — Conditional *real* GPU compression for the first large immutable atlas

**Why test:** a **single one-level** 8192x8192 RGBA8 intent requires 268435456 bytes (256 MiB). If the id295 content is truly a sampled immutable BC3 atlas, transcoding offline and uploading a driver-supported compressed format may avoid the intermediate expanded GPU allocation. Format-defined examples, **not physical device measurements**:

| 8192², one mip | Expected payload | Relative to RGBA8 | Limit |
|---|---:|---:|---|
| RGBA8 / sRGBA8 | 256 MiB | 100% | Current full-decoded intent |
| ETC2 RGBA8/EAC or ASTC 4x4 | ~64 MiB | 25% | Only if alpha/color/quality and device support pass |
| ASTC 6x6 | ~28.4 MiB | ~11% | Lossy and potentially visible at text/edge regions |
| Halve each dimension to 4096² RGBA8 | 64 MiB | 25% | Lossy downscale; changes image detail, not a transparent substitution |

1. First build a **self-authored Mali GLES3 fixture**: allocate representative compressed ETC2/EAC and optionally ASTC data, perform glCompressedTexImage2D and sampling from an owned FBO, check glGetError, verify the returned pattern/colors/alpha, and *measure actual* MemAvailable/CmaFree and any available driver memory signal. Discover GL extensions and explicit format support on this exact Spruce driver. Do not assume ASTC support from a GPU marketing name.
2. Keep alpha semantics exact. ETC2 RGBA8 + EAC stores both color and alpha; ETC2 RGB / punch-through is **not** a drop-in equivalent for arbitrary BC3 alpha. Verify premultiplication, sRGB conversion, mip filtering and border/clamp seams.
3. Read the original BC3 data only in the **owner's private workspace** after mapping the exact source and guest lifetime. Transcode **offline** to content-addressed compressed mips; store source hash, dimensions, per-level offsets, swizzle, color-space flags and encoder settings in an owner-private cache. No proprietary images or compressed byte arrays in Git.
4. Add an opt-in runtime path keyed by **original exact owner hash + texture generation + complete descriptor**, using direct compressed upload and a strictly validated memory charge for the **entire mip tree**. Reject stale/partial cache; fall back to original BC decode path if format unsupported, asset mutable, hash mismatch, or driver storage allocation fails. Do not allocate the 256MiB decoded GPU copy *as well as* the compressed copy and count the latter as a saving.
5. Run a 1024² self-authored integration fixture first, then small allowlisted original atlases, and only then id295 in a bounded, guarded real-game arm. Measure **physical** memory delta, compilation/loading latency, CPU overhead, all-class storage, actual game screenshot and identical sampler/mip result. This is a major quality intervention; keep original graphics as default unless the owner explicitly accepts a reversible performance mode.
6. If id295 turns out **mutable, renderable, an alias of a writeable resource, not BC3, or not requested at all**, **reject this path**. Consider verified RT lifetime reuse, carefully isolated render-resolution reduction, or exact partial-update strategies instead. A direct compressed path cannot preserve arbitrary render-target writes.

**PASS:** measured safe physical-headroom improvement and correct first-world visuals. Size arithmetic alone does not pass.

### 40.8. P0-C0 — Qualify real-game CPU ownership, AudioOut/SVC cost and loading progress

The old main-thread Loading sample of **0.836 CPU seconds per presented frame** is a separate historical phase; older profiler claims that AudioOut is cheap were withdrawn because TLS workers/tails were omitted. V2 is a **tested component**, not a valid current game result.

1. On a safe M0-qualified run, turn on V2 narrow instrumentation for **exactly one Loading/early-world interval**, with matched disabled-control run in the same scene. Persist begin/end reports and all retired thread generations; reject registry overflow, incomplete snapshots and missing final rows. Measure profiler overhead with the same owner image and ELF build variant.
2. Extend narrow scopes to the **complete** SIGTRAP/SVC dispatch, real guest mutex 0x1A/0x1B handlers, IPC parse/dispatch/return and the **audout:u child** (endpoint0x40 commands 7/8). Keep inner/outer inclusive and exclusive CPU/wall timing separate, including waits outside current AudioOut handlers. A count of 5506/5389 arbitration calls does not establish their CPU cost.
3. Correlate TID/starttime and native-PC/guest-PC with the **same-run** ELF maps, plus CLOCK_THREAD_CPUTIME_ID, /proc/TID/schedstat and coarse page fault/guest-ZRAM restore rates. Distinguish CPU executing guest IL2CPP from sleeping, runnable starvation, GPU waits and decompression. Do not attribute round-robin sampled PC counts to CPU percentages.
4. Add bounded Unity progress evidence through verified owner-private image metadata: scene load request, AsyncOperation progress, allowSceneActivation, activation, player/camera Update and first world draw. Do **not** patch game code, forge percent progress or skip Unity thread synchronization based on guesses.
5. If AudioOut is a hot path, inspect buffer-release polling: whether cmd8 retries an unchanged state and whether blocked vs nonblocking semantics match the Switch IPC contract. Optimize only proven redundant host I/O/allocations or incorrect wait scheduling. Never coalesce/drop audio samples or fake buffer-consumed completion for higher FPS. Verify audible quality in the final game.
6. If guest ZRAM is the bottleneck, repeat *controlled* cold-age experiments (10/100/250/500ms only within guarded RAM headroom), calculating true thread CPU via CLOCK_THREAD_CPUTIME_ID; prior cpu-compress-ms field names were wall-clock elapsed time in selected paths. Stop if faults, resident usage, input latency or scene progress regress.
7. Preserve a full-frame clock ledger: guest present-to-next-submit gap, replay CPU vs GPU wait, present/swap, page faults, host compression, scene I/O; aim for **>=95% exclusive accounting**, and avoid adding overlapping thread durations as elapsed wall time.

**PASS:** a measured dominant CPU class and scene-progress delta, with >=95% thread-generation coverage and <=5% profiler overhead. **STOP:** missing reports or mismatched run/scene identities; do not optimize the hottest log counter.

### 40.9. P0-W0/W1 — Detect first-world activation and correct the *rendering*, not just the spinner

Even after all budget stops are resolved, **New Game -> Loading is not gameplay**. A linked fragment45 and changing present serials do not prove any corresponding pixels were drawn.

1. Introduce a per-run **scene transition receipt**: last config Confirm, controls dismiss, first genuine Loading serial, new scene load request/activation, first camera/player update, new world NVN draw, and first **actual pixel-visible** world frame. Emit source confidence for each event; unknown fields stay null.
2. For **first-world draw**, log exact original pair/program identity (0..45), shader stage, count of real draws versus links, vertex/index ranges, UBO bank/size and sampler slots, target/FBO ID and dimensions, blend/depth/stencil state, viewport/scissor, output attachments, and GL error status. Specifically validate fragment45's half arithmetic and **four MRT outputs** (GL_MAX_DRAW_BUFFERS and GL_MAX_COLOR_ATTACHMENTS with actual FBO completeness).
3. Audit all seven TEST substitutes on the **world path**: first real bind/draw, affected geometry/pixels, required MSAA/SSBO/skin functions, and whether the substituted semantics are genuinely sufficient. A game that loads and renders black/incorrect lighting **fails W1**, even if menus were correct.
4. Distinguish four outcomes with evidence: **no scene activation** (Unity/progress/SVC); **scene active but no world draws** (guest camera/pipeline scheduling); **world draws but hidden** (FBO/attachment/MRT, wrong composition, depth/stencil, viewport or shader); **world pixels visible but input ineffective** (HID/player state). Use sparse readbacks of a single intermediate attachment **outside steady-state FPS runs**, compared against in-run KMS capture.
5. Before changing complex MRT logic, create a self-authored **four-attachment ES3 FBO fixture** with half-float and sRGB/linear attachments, independent output colors, clipping/depth/stencil and sampler checks. Verify storage type, glDrawBuffers, glReadBuffer and readback values and test the same exact Mali driver. Do not assume successful program link means its MRT outputs are routed correctly.
6. For layout, inspect the **source-verified** original game screen/reference resolution and per-pass 1920x1080 targets. Generic ZERO_RENDER_SCALE=2 already showed no reliable full-frame improvement; do not reinstate it as a fix for scene correctness. Owner-specific scaling is a subsequent option only after identifying matrices, texture readers and UI layout contracts.
7. Only after a correct world frame, verify camera/player coordinate changes following physical controller input, inventory/dialogue/interaction, audible sound, then save -> quit -> cold boot -> load. Keep scene and save data private, back up owner saves, and verify MainUI/CPU restoration.

**PASS W0:** verified game scene activation and world draw. **PASS W1:** correct visible world pixels + physical player movement. **PASS PLAYABLE:** W1 + interactions, audible audio and cold save/load. **HARD STOP:** missing source-backed shader, black/incorrect scene, undefined MRT output, memory floor or kernel OOM.

### 40.10. P1-F0/F1 — Real 30 FPS program *only after* world correctness

30 FPS gives a **33.33ms complete-frame budget**, not 33.33ms replay alone. An old build209 **Loading/menu** diagnostic interval reported ~572.7ms total, with ~249.6ms replay and ~316.4ms guest gap; its phase, instrumentation and build are not current gameplay performance. CBUF subimage already exists and the historical A/B does not demonstrate a gain. A generic reduction of 1920x1080 targets to smaller storage gave essentially no whole-frame benefit. Any assertion that these features can alone reach 30 FPS would be misleading.

Once W1/W2 pass, run the following **separate ranked experiments**, each with its own reversible flag and 3 matched A/B repetitions:

1. **F0 — genuine FPS capture.** Collect continuous present serial/timestamps (including **all** presented frames, not only T2P_SLOW_FRAME outliers), CPU total and render submit, skipped/repeated serials, p50/p90/p95/p99/max, effective frames/s, frametime variance, thermal/clocks and audio underruns. Separate 60–120s stationary, walking, dark lighting, inventory/dialogue, and transition windows.
2. **F1 — eliminate pathological stalls.** Before shader micro-tuning, find >100ms frame tails and correlate with guest-ZRAM restores, fileback pread, BC materialization, GL first-use shader/program creation, and memory pressure. Prewarm **only verified near-future resources** with strict headroom; avoid unbounded staging or preloading everything.
3. **F2 — GPU memory and texture bandwidth.** If atlas sampling/upload is dominant, use the proven M2 compressed immutable cache, exact dirty-region upload, source-generation-aware GL object reuse, and clamp redundant format conversion. A texture cache without invalidation is a visual correctness bug.
4. **F3 — CPU trap/IPC hot path.** If C0 confirms a hot SVC/Audout/lock/host-copy loop, optimize one source-verified handler; test request/release and lock correctness, measured CPU time and audible audio. Avoid replacing nontrivial Horizon synchronization with a spin or fake signal.
5. **F4 — render targets and bloom.** Measure per-pass GPU times with a real supported timer query or a safely isolated A/B, not glFinish after every draw. If fragments dominate, test **owner-attributed** 1920x1080 -> 1280x720 for *scene targets* while retaining sharp native UI, or an opt-in bloom tier. Validate MRT attachments and UI matrices before claiming savings.
6. **F5 — render replay overhead.** If the native replay bucket is large, revisit cbuf padded 1024x1 float uploads (instead of merely replacing TexImage with TexSubImage), redundant texture resolution, GL state shadows, VBO copies, FBO transitions and shader location caches. Instrument would-skip counts first; invalidate on context/resource-generation changes. Benchmark whole-frame time, not local CPU savings.
7. **F6 — submission/parallelism.** Async NVN queue and glFlush can shift blocking and cause resource-reuse races; require serial/fence/GL-context lifetime proofs before any test. Prior NVN_COMMAND_REUSE_BEFORE_COMPLETION and EGL_BAD_SURFACE are **hard stop** conditions.
8. **F7 — compiler/quality ceilings.** If correct gameplay remains >33.33ms after removing dominant avoidable costs, state its measured sustainable ceiling and consider clearly labeled lower-resolution/effects presets. Do not hide missing world features for a higher FPS counter.

Report intermediate **5 -> 10 -> 15 -> 20 -> 30 real gameplay FPS** milestones; no milestone is achieved yet. Stable 30 FPS acceptance remains three independent >=60s scenes with frame P50 and P95 <=33.33ms, preferably P99<=50ms, plus correct visuals, player input, sound, saves, memory and cleanup. A sustained lower number is an honest outcome on this ~1GiB device.

### 40.11. Strict next PR order, measurable gates and abort conditions

| Order | PR | Exact changes | Minimum acceptance / evidence | Abort or replan if |
|---:|---|---|---|---|
| **1** | **N1** | Fix/retire serial_request regex/full-log scan; add executed-script and owned-generation tests | Valid numeric present series, no mixed generations, no O(log-size) poll | ValueError, fake zero, stale log |
| **2** | **N2** | Correct overshoot state/direction, atomic press+ack, short input sweep | load -> newgame one-row **serial-qualified** move, no duplicate button, exact same run | load -> options/credits, missing release or serial |
| **3** | **M0** | Bounded menu RAM/GPU life ledger, safe-floor preflight | Identify and rank top 5 menu consumers; precise 96MiB-floor disposition | Cannot survive menu without unsafe floor |
| **4** | **N3** | Semantic NEWGAME_CONFIG / CONTROLS / LOADING oracle; retire legacy navigators | One screen-state transition per new owned serial; correct page before every Confirm | Page UNKNOWN / ambiguous input |
| **5** | **B2** | Transactional texture/GL residency ledger and id295 owner receipt | Bounded pre-refusal owner in real Loading, or **explicit earlier stop cause** | Unattributed GL allocation or kernel OOM |
| **6** | **M2 (conditional)** | Independent Mali compression fixture + owner-local atlas cache | Real physical memory improvement, correct alpha, safe new allocation | Mutable/renderable id295, unsupported extension |
| **7** | **C0** | Complete real-game CPU/AudioOut/SVC and Unity wait/scene progress attribution | Thread coverage+matched disabled profile, reproducible hot path | Incomplete TLS/tail/identity, overhead >5% |
| **8** | **W0/W1** | Exact Unity activation, first world draw, 4-MRT fixture, pixel/input parity | Actual world scene and physical controls, no TEST semantic regressions | Loading-only, corrupted world, memory floor |
| **9** | **W2** | Gameplay audio, interaction, persistence and exit | Audibly correct sound and cold save/load, clean MainUI and CPU mask | Missing save or incorrect audio |
| **10** | **F0–F7** | World benchmark; one measured CPU/GPU/memory optimization per PR | Correctly rendered complete-frame P50/P95, A/B and thermal/headroom evidence | Apparent speedup from reduced correctness or shifted GPU wait |

**Dependencies matter more than order numbers:** N1/N2 can be developed and host-tested alongside read-only M0 fixture construction. The next **on-device** run should be M0 memory-safe (no need to press) rather than a blind navigation-to-Loading attempt. If a safe menu window and qualified serial become available, N2/N3 can proceed. B2 cannot obtain its id295 pre-refusal receipt without real Loading. M2 is strictly conditional on B2. C0's narrow isolated fixture does not need a world, but a real-game CPU hot-path claim needs an owned game phase.

**Per-PR evidence contract:** base commit, exact owned ELF SHA-256, owner-private image/catalogue hash (or explicit unavailable), 435-file baseline validation, actual changed source+unit tests, isolated host fixture, target Mali test when relevant, env defaults vs diagnostic overrides, run UUID/PID/starttime, continuous monitor window, before/after frames from *inside* the run, observed physical RAM/GPU resources, exit taxonomy and MainUI/CPU cleanup. Never silently treat the earlier build218–219 Loading runs as build229 evidence. Never publish copyrighted original game data, user saves or private executable images.

### 40.12. Immediate test specification and achievable next checkpoint

**First PR's red/green targets, with no handheld required:**

~~~python
# Actual serial_request() script must be executed, not just inspected as text:
sample = ("NVN_PRESENT_PIXELS frame=1 status=PIXELS\n"
          "NVN_PRESENT_PIXELS frame=42 status=PIXELS\n"
          "NVN_PRESENT_PIXELS frame=9 status=PIXELS\n")
# Remote result: {"present_frames": 42}; no ValueError.
# Rotation or UUID mismatch: REFUSE; never use 42 for another process generation.

# Navigation must be fail-closed:
# observe MAIN_MENU/load at serial 55 -> one Down tap
# observe MAIN_MENU/options at serial 56 -> overshoot, REFUSE/RECOVER_REQUIRED
# absolutely NO automatic Down or Confirm to credits
# separate recovery arm with stable options observation -> one Up microtap
# observe MAIN_MENU/newgame at a new serial twice -> one Confirm
~~~

**Second PR's device checkpoint:** owner-qualified first-boot MAIN_MENU under the **intended safe floor**, one short press with released-button and new-present receipt, resulting in row newgame rather than options/credits; stop there and restore Spruce. Do not add 1800 seconds to the timeout as a substitute for RAM headroom.

**Third PR's target:** a memory waterfall explaining why **the menu** goes from the prelaunch state to floor=96 refusal at frame2 and later floor=32 refusal at frame55, with a ranked physical resource ledger and a *specific* safe intervention. Only after that should the navigation arm proceed through New Game config/controls to capture either the first genuine world draw or the actual id295 descriptor.

**Decision:** The repository's engineering progress in reproducibility and GPU-correctness is real. However, reaching gameplay is currently constrained by **early whole-system memory exhaustion plus incomplete reliable navigation**; 30 FPS is a much larger, unmeasured second problem. The next highest-value change is a tested navigation/serial correction together with menu-phase memory ownership, not another shader-catalogue entry or unconditional GPU async flag.

## 41. Tap-length A/B and the repeatable chain (2026-10-21)

`tools/nav_chain.py` is now the single wiring (oracle + navigator + `logs/latest.log` present counter + owner-checked pad), with 7 tests on its `summarise()` contract and 4 on the serial reader (including an executed payload test).

| arm | tap | before → after | serial | verdict |
|---|---|---|---|---|
| `nav-chain-04` | **350 ms** | `load` → `load` | **19 → 23** | qualified: press did not move the selection |
| `nav-chain-02` | 900 ms | `load` → `options` | not read (wrong path) | two rows: hold-length overshoot |

The one-row window sits between 350 and 900 ms at ~1 presented frame/s; the next arm should test ~500–600 ms with the same qualification.

Recorded failures, not results: `nav-chain-05` ran the chain **before** the arm in a sequential shell (`;` not `&`) and wrote `states: []`, and its arm was then **killed by the kernel OOM reaper** (`Out of memory: Killed process 27722 (terminator2d-ne)`, harness rc 8) with **no** runtime STOP — the 32 MiB floor is a reactive 250 ms check, so an OOM can beat it; that is a memory fact, not a tap result (`evidence/nav-tap-length/correction-oom.json`). `nav-chain-06` overlapped correctly and read the menu, but the fresh run's log had no present line yet, so the serial was 0 and the navigator refused. The tool now calls `wait_serial(0)` so a first-frame race cannot masquerade as a refused chain.

**199 host tests PASS.** Limits unchanged: menu only, one press, two frames — no config page, Loading, scene, id295 or FPS claim.

## 42. P0-N2 implemented: direction, overshoot refusal, double-frame confirm (2026-10-21)

Owner **§40.3** done as pure host work; no device press, no build, no deployment.

- `tools/navigator.py` is now an explicit `IDLE → ACTION_ISSUED → AWAIT_NEW_PRESENT → DONE/REFUSED` machine. A press is an action: while the issued action has no strictly newer frame the core waits, and after three repeats it refuses.
- Direction comes from **ordered row indices**, so `options→newgame` and `credits→newgame` press **up**; the old unconditional `down` branch is gone.
- A move of more than one row is **refused by default** (`overshoot, explicit recovery required`) and no follow-up press is issued. Recovery exists only behind `recovery=True` (diagnostic arms), where the overshoot is recorded and the next action is a single opposite-direction step; nothing auto-confirms.
- Confirm needs **two newer agreeing observations** on the target row, and the page after it must be `NEWGAME_CONFIG`; any other page is refused, and the menu still being shown is `wait`, not a page change. A non-menu page without a preceding confirm is refused.
- `nav_chain.summarise()` now refuses a two-row result instead of calling it qualified; `SWEEP_MS = (80, 150, 250, 400)` declares the owner's bounded short-press sweep.
- **206 host tests PASS**, including every case the owner listed: `load→options` overshoot with an assertion that exactly one press was issued, `options→newgame` direction, single-row movement, stale serial, repeated same-frame polls, confirm acknowledgement, wrong config page, lagged serial, two identical animation frames, first row already at the target, and no auto-confirm after overshoot.

Open: the sweep has not run on device; `NEWGAME_CONFIG` has no measured fingerprint (§40.4); the menu-memory waterfall (§40.5) is untouched. No scene, id295 or FPS claim.

## 43. Short-press sweep: 80/150 ms do not register and the arm cannot finish the sweep (2026-10-21)

Owner **§40.3 item 5** executed once (`nav-sweep-02`, build229, strict GL, 300 MiB texture budget, diagnostic floor 32 MiB), one press per attempt, each requiring a new present serial:

| tap | serial delta | rows | verdict |
|---|---|---|---|
| **80 ms** | 17 → 21 (4) | 0 | qualified, no movement |
| **150 ms** | 21 → 45 (24) | 0 | qualified, no movement |
| 250 ms | — | — | not reached: arm ended (`arm_ended`) |

Together with 350 ms → 0 rows and 900 ms → 2 rows, the one-row window is **between 400 and 900 ms**; values ≤350 ms are lost between guest samples.

The sweep could not complete because the menu run survives only ~30–55 presents (~40 s) and one attempt costs a kmsgrab plus a base64 transfer plus a wait for a newer frame — the 150 ms attempt alone spanned 24 frames. This is **§40.5 in its sharpest form: the menu cannot stay alive long enough to characterise its own input**, so press-only experiments are exhausted until menu memory is explained.

Tooling: `--sweep` / `--sweep-values` with a pure `sweep_decision()` (one row = success, two rows = immediate overshoot stop, no movement = next declared value), and a dead arm is recorded as `arm_ended` instead of raising. **210 host tests PASS.**

Next: the §40.5 menu-memory waterfall (absolute deltas from before launch, 1 Hz plus first-frame and pre-refusal points, GL/RB/buffer/EGL storage with live-vs-deferred and generation, per-event waterfall of the first 55 presents). No scene, id295 or FPS claim.

## 44. Menu-phase memory waterfall (owner §40.5 M0) (2026-10-21)

Opt-in `LC2_MENU_LEDGER=1` (≤1 Hz, first-frame line, host-observable only, no admission/budget/floor/swap change), build230 `8a19df13…0be6` deployed with a `.before-230` backup. Arm `menu-ledger-01`: **41 presents in 20.5 s**, verified identity, zero cleanup errors, stopped at `T2_MEMORY_FLOOR`.

| quantity | start | low / end | delta |
|---|---|---|---|
| `MemAvailable` | 129.3 MiB | **54.7 MiB at frame 16 (4.5 s)** / 71.7 MiB | **−74.6 MiB** |
| `CmaFree` | 24.3 MiB | **1.0 MiB** (end 12.5) | exhausted in the menu |
| game `VmSwap` | 0 | **422.4 MiB** | guest pages to swap |
| charged textures | 107.1 MiB / 91 | 157.3 MiB / 101 | **+52.6 MiB** |
| game `VmRSS` | 714.9 MiB | 719.6 MiB | +4.7 MiB |

Interpretation: the menu halves available RAM in **4.5 s** before any world content; **CMA exhausts first**, and charged texture storage accounts for only about a fifth of the loss while guest pages move to swap. A texture-only ledger would have reported "nothing much happened", which is why the ledger reports classes it cannot measure as `untracked` rather than as zero.

Limits: renderbuffers/buffer objects/EGL surfaces and driver-retained storage are untracked; the first line is `arm-start` (no pre-launch baseline); the pre-floor line did not fire, so the last interval line plus `T2_MEMORY_FLOOR_HIT` bracket the refusal; one arm, one build, diagnostic floor.

Next: attribute the CMA exhaustion to specific GL/EGL classes and decide whether any of it is retainable menu-only storage (owner §40.6 / B2 ledger), not another press experiment.

## 45. Class attribution of the menu loss (owner §40.6 / B2-lite) (2026-10-21)

Build231 `41d6b4f8…c682` adds per-class estimates to `LC2_MENU_LEDGER`. Arm `menu-ledger-02` (same opts, one arm): at the low point (frame 31) `MemAvailable` **51.8 MiB (−78.1)**, `CmaFree` **0.85 MiB** (from 28.0), game `VmSwap` **417 MiB**, charged textures **157.3 MiB (+50.1)**, colour targets **19 (+3, +15.9 MiB estimate)**, depth renderbuffers **2 / 22.9 MiB constant**, and `scaled/half/bc-pending/joined` all **0**.

- The depth/stencil pair is allocated once and does **not** grow while 78 MiB disappears; the visible growth is textures plus three colour targets (~66 MiB estimate), leaving the rest in `buffers`/`egl-surfaces`/`driver-retained`, which the ledger labels untracked rather than zero.
- **CMA is a 28 MiB pool and the menu alone drains it to 0.85 MiB** — reproduced on a second build, so the earlier `CmaFree` collapse is not a one-off.
- Experiment paths that could have explained it (`scaled`, `half`, `bc-pending`, `joined`) are measurably absent in the menu.

Next: the transactional ownership ledger from §40.6 B2 — which of the 19 colour targets is retained after the menu stops needing it, and whether depth renderbuffers are reallocated per target elsewhere. Estimates remain estimates: no scene, id295 or FPS claim.

## 46. Menu colour-target inventory: four 1920×1080 images on a 1280×720 panel (2026-10-21)

Build232 `a9b516e0…8957` adds a bounded per-target receipt (`LC2_MENU_TARGET`, ≤32 lines, once per run, first time `MemAvailable` drops below 64 MiB). Arm `menu-targets-01` (one arm, `T2_MEMORY_FLOOR`, verified identity, zero cleanup errors) listed **19 targets / 43.39 MiB charged**, matching the ledger's independent 43.4 MiB colour-target estimate.

| class | count | charged | ids | draws |
|---|---|---|---|---|
| **1920×1080** (3 colour + 1 depth) | 4 | **31.64 MiB** | 2, 3, 4, 28 | 200 |
| 1280×720 (2 colour + 1 depth) | 3 | 10.55 MiB | 172, 173, 206 | 534 |
| post cascade 640×360 → 1×1 | 12 | 1.21 MiB | 211…225, 260 | 231 |

- **Three 1920×1080 colour targets plus a 1920×1080 depth exist although the panel is 1280×720** — the largest class in the menu and, by construction, not explicable by presentation size. This is the class the §32.9 GPU-fill row names.
- Busiest target is **id 172 (1280×720, 513 draws)**; the 1920 trio carries 200 draws total. The post cascade is twelve images costing 1.21 MiB (4 KiB charge floor each) — real but minor.
- All listed targets report `target-seen=1` and 1–2 references, so no counter proves an orphan; `last-used-serial` does not exist yet.

Next, one factor at a time with identical-output guards: (1) opt-in 1280×720 storage for the 1920 trio and its depth, verifying pixels; (2) only if (1) is not pixel-safe, fenced release of provably unreferenced targets, which is blocked on the B2 last-reader epoch rather than on a guess. Charged bytes are not Mali residency; no scene, id295 or FPS claim.

## 47. Origin of the 1920×1080 menu targets: the game, not the adapter (2026-10-21)

The four 1080p images from §46 are created by the title's own code with **instruction literals**: at `main+0x53bfcc` it executes `mov w21,#0x438` (1080), `orr w1,wzr,#0x780` (1920), then `blr` into `nvnTextureBuilderSetSize2D`; the log shows that call for three colour targets plus a depth target built through a struct-sized site (`main+0x533a40`, which also builds the 1280×720 window target as `0x500×0x2d0`).

Therefore this is **not** an adapter defect: `NVN_WINDOW_REAL framebuffer=1280x720`, the display resolution query answers `{1280,720}`, `ListDisplays` reports maximum-layer capacity (1920×1080) which is a capability field, and the adapter has no `GetOperationMode` handling to report "docked".

Consequence: the panel path is already 720p; reducing the 1080p composition family is a **storage policy** decision, and the adapter already ships the switch for it — `ZERO_RENDER_SCALE=2` maps `1920×1080 → 1280×720` and preserves native 720p composition/UI. It stays off by default because the roadmap records it as a measured performance-negative, and the **four old targets total 31.64 MiB**, but resizing them to 720p would reduce nominal storage by at most **17.58 MiB** (new payload 14.06 MiB), not eliminate that storage; physical savings remain unmeasured.

Next is a single-factor A/B: `ZERO_RENDER_SCALE=2` versus default on the same menu screen, gated by `tools/frame_diff.identical()` and reporting both the charged-byte saving and the pixel difference. That needs the owner's go-ahead because it changes image quality.

## 48. Post-build232 audit: surviving the menu, reliable New Game, world pixels and a credible 30 FPS path (2026-10-21)

**Source snapshot audited:** main at [a0aa16053191e25d86f764ae4451c19923f0361a](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/a0aa16053191e25d86f764ae4451c19923f0361a). The audit read the public adapter overlay, current tools, tests, evidence summaries and §§40–47. **This section is a source/evidence review and an implementation plan.** It does not assert an additional handheld run, successful new build, reproducible FPS improvement, or working gameplay. Treat device measurements in §§44–47 as one or two bounded arms with the named build, not as cross-build FPS data. Earlier sections remain historical; use this section for the **next PR sequence**.

### 48.1. What actually changed since the previous §40 audit

| Component | Implemented/observed by HEAD | Remaining qualification |
|---|---|---|
| Navigation N2 | Ordered-row Up/Down, overshoot fail-closed, explicit action state machine and tests; short-tap sweep showed 80/150/350 ms with no movement and 900 ms with two rows | Confirm still accepts the **same** serial twice; stale-poll budget is count-based; a real one-row press and config-page transition are unproven |
| Tool ownership T1 | Launcher-run UUID, executed ELF identity, generation-aware collector, exact byte-framed logs, owner-checked pad | tools/nav_chain.py still uses unowned full-log serial_request() for navigation serials, independently of the available collector |
| Menu M0 | Build230–232 show rapid available-RAM/CMA loss, rising swap, per-class ledger and 19 menu render targets | Source-level GL object generation/lifetime and driver physical residency are unproven; first menu ledger record is **not** a pre-launch baseline |
| Graphics | GLES3 sRGB/client-format repair with target fixture; fragment45 has linked; TEST substitute census exists | Correct scene MRT/pixels and end-to-end drawable gameplay are not established |
| 1080p origin | Literal 1920×1080 builder calls from game code, not display or docked emulation; actual window 1280×720 | A 720p storage policy may affect UV/viewport/compositing; old generic scale trial did not demonstrate a whole-frame win |
| Large atlas | 300 MiB texture guard can fail closed on the 8192×8192 id295 decoded-reservation intent; checked full mip arithmetic already merged | Exact current-run source format, owner, mutability, aliases, mip selection and physical driver commitment remain unproven |
| CPU/FPS | Nested V2 timing component, historical gap/replay attribution and conservative finish policy | No representative controlled gameplay sample; old 0.836 CPU s/present is a **different Loading arm**, not today's world FPS |

**Hard priorities:** make the navigation contracts true in executable tests; obtain useful 96 MiB-safe menu headroom; prove NEWGAME_CONFIG → CONTROLS → LOADING → WORLD on the *same owned process*; resolve any real id295 wall; then measure and optimise the first correct, controllable scene. Do not use more shader-catalogue churn, unsafe GL queue overlap, frame caps, or a longer timer as substitutes.

### 48.2. Newly verified code findings: fix these before relying on the existing navigator

**N4-A — The two-frame Confirm guarantee is false for duplicate serials.** In tools/navigator.py, the first observation of the target row sets confirm_seen=1, but does not record the serial that established it. If the user polls the same valid present serial again (which is normal at 1–2 fps), the second observation can increment confirm_seen and issue Confirm on **the same frame**. The check against issued_serial only blocks the frame of the *previous button*, not a repeated target observation. The existing test covers consecutive distinct serials, not this case.

Required red/green test (add to tools/test_navigator.py; it must fail on the audited code):

~~~python
nav = Navigation()
first = observe(nav, MAIN_MENU, 492, 10)
again = observe(nav, MAIN_MENU, 492, 10)
assert first["action"] == "wait"
assert again["action"] == "wait"   # currently can emit "press"
assert not any(e.get("button") == "confirm" for e in nav.events)
confirm = observe(nav, MAIN_MENU, 492, 11)
assert confirm["action"] == "press" and confirm["button"] == "confirm"
~~~

Implementation: add target_seen_serial and last_observed_serial to Navigation; increment confirm_seen **only when** a strictly newer, same-generation presented serial independently confirms the target. On repeat, emit wait without changing state. Reset confirmation evidence if the cursor leaves the row, ownership changes or an unknown page appears. A confirm is one issued action and requires a later unique serial + a positively classified NEWGAME_CONFIG before DONE. Unit-test already-on-target, off-target-return, duplicate serial, older/out-of-order image, conflicting cursor, and unexpected page; include release/ack ownership through the integration driver.

**N4-B — Three fast polls can exhaust the stale budget before one frame.** STALE_SERIAL_LIMIT=3 is a count, not a clock. With a ~0.5–1.2s or worse menu period, four immediate calls can refuse a perfectly healthy frame. Move the response deadline to the orchestration layer or accept an injected monotonic now/deadline in the pure state machine. Use an evidence-derived **bounded wall deadline** plus process liveness and an optional max-present-gap, rather than "3 calls". Repeated same-serial reads must not cause another press; timeout refusal must include elapsed ms, last/issued serial and verified owner. Add fake-clock tests (fast 100 polls are still WAIT while under deadline; one post-deadline poll refuses; later fresh serial can only be acted on by a valid non-expired action). Do not introduce unbounded waiting.

**N4-C — nav_chain.py still pays O(log length) and has no owned log generation for its serial.** wait_serial() calls serial_request(), which reads the entire growing logs/latest.log, even though tools/load_metrics.py already implements collector_request()/fold() with expected_run, header SHA, inode, byte offset and continuity anchor. The physical pad owner check does **not** bind the serial to the same UUID. Replace serial_request() in this navigation control path with a persistent owned collector state, checking UUID/boot/PID/starttime/ELF identity **before and after** capture and input. Consume the newest complete-line present, never infer serial from a half-written line. Failure/rotation/missing new serial => do **not** send input. No full-file rescans.

**N4-D — A sweep is not a full stateful navigation test.** nav_chain.py constructs a new Navigation() on each later tap in a sweep, while its summarise() classifies a row delta independently of the state machine. Persist a single Navigation object per attempt chain and advance it only on fresh owned observations; preserve an explicit button-release acknowledgement. Classify a 2-row jump as terminal REFUSED, not an occasion for a second automatic corrective press. A 1-row move is a measurement, **not** evidence that New Game was confirmed or the page changed. Add a host fixture in which the first tap times out, the log rotates, the second capture is foreign, and a fresh Navigator must not silently inherit a previous row/serial. Measure capture/transfer overhead separately, since earlier sweeps consumed most of the short safe menu run.

**N4-E — The legacy full-load driver remains unsafe as a proof path.** tools/load_probe.py still has walk_to() with default 1000ms holds, 1500ms Confirm, and a screen transition triggered by coarse changed-cell counts; it is behind --allow-unverified-navigation. Keep that route disabled. Replace its control path with the common owned collector → page_oracle → navigator → owned pad state machine. Implement distinct NEWGAME_CONFIG and CONTROLS fingerprints before permitting a full load. A changing loading animation cannot substitute for a page oracle or scene receipt.

**N4-F — The frame comparison's “identical” result is tolerance-dependent.** tools/frame_diff.py defaults to tolerance=2, so identical() returns true when **every** channel difference is ≤2 even if every pixel changed. That is useful as a small-noise gate but **not byte-identical RGB output**. Keep separate names/results: exact_pixel_match (tolerance=0), within_channel_tolerance (e.g. ≤2, reports max/mean), and meaningful_visual_parity (phase-aligned ROI comparison with an explicitly excluded animated region). Compare independently decoded same-size/stride/channel captures, never mismatched frames or a screenshot taken after panel blanking. Add bands<=0/channel<=0 argument guards and fixture cases with full-frame +2 differences and animation-only changes. For FBO correctness require independent attachment/readback values, not just the final KMS image.

### 48.3. Correct the 1080p savings arithmetic and set a realistic menu target

**Important correction to §47 and docs/1080p-origin.md:** the **four 1920×1080 RGBA8/depth-equivalent targets cost 31.64 MiB before scaling**. Changing **all four** to 1280×720 does not remove them. At 4 bytes/pixel, the predicted new payload is:

~~~text
old: 4 × 1920 × 1080 × 4 / 2^20 = 31.640625 MiB
new: 4 × 1280 ×  720 × 4 / 2^20 = 14.062500 MiB
delta                              = 17.578125 MiB
~~~

Numbers are *format-defined target storage*, not measured Mali physical savings; actual implementation might scale only a subset, have alignment/tiling/MSAA overhead or retain both generations temporarily. Do not call the original 31.64 MiB a **saving**. The historical 96 MiB floor stopped near 54 MiB at frame 2 (a roughly 42 MiB gap to the floor): even the full theoretical 17.58 MiB reduction cannot be assumed to solve that early floor by itself, much less free the 256 MiB decoded id295 allocation. The depth renderbuffers in §45 are a distinct accounted class from the depth texture in §46: do not blindly sum/alias their bytes. Reconcile names/generations and charging sites.

The 1920x1080 source is game-side literals at main.text.seg+0x53bfcc…+0x53bfdc and related callers; the adapter's output mode is already 1280x720. A generic "switch to handheld mode" or a change to ListDisplays would not address this resource. The already-implemented, **default-off** ZERO_RENDER_SCALE=2 is the first *diagnostic* lever; historical Loading measurements did not show a net performance gain. Do not change its default from source speculation.

### 48.4. Next work packets, in dependency order

| Order | PR / area | Concrete deliverable | Device pass gate |
|---:|---|---|---|
| 1 | **N4: serial/Confirm correctness** | New unique-frame Confirm guard, monotonic timeout, single stateful owned collector/oracle/pad wiring; replace legacy full-log polling | A single **owned, released, serial-qualified** one-row press; no duplicate Confirm or UNKNOWN-page accept |
| 2 | **M1: menu memory truth and safety** | Pre-launch RAM/CMA baseline, GL/EGL/buffer/driver ledger, pre-allocation reserve/admission with bounded safe refusal | No kernel OOM; identify top growth owners and what is actually resident versus estimated |
| 3 | **S1: 720p target A/B (conditional)** | Existing ZERO_RENDER_SCALE=2 experiment, correctly computed 17.58 MiB target upper bound and pixel gate | Safe headroom **increases physically**, output quality accepted, no slower world/menu |
| 4 | **N5: semantic page oracle** | Captures/tests for NEWGAME_CONFIG, CONTROLS and LOADING from this exact build; full run generation and action graph | Verified menu → config → controls transition with expected row/button, no blind Confirm |
| 5 | **B2: complete GL residency and id295 decision** | Transactional per-generation accounting, GL fence retirement, exact pre-refusal descriptor and alias/mip/source owner | A bounded real Loading receipt or a precisely named earlier stop, never a kernel kill |
| 6 | **G2 (conditional): GPU class reduction** | First safe menu resource-lifetime reduction; if id295 is immutable sampled BC3, test owner-private ETC2/ASTC cache | Device-supported upload and correct pixels, physically measured improvement |
| 7 | **W0/W1: first real world** | Unity activation + first true draw + checked 4-MRT/readback + physical movement/inventory | Correct controllable pixels, not just shader link, non-black frame or Loading |
| 8 | **W2 + C0** | Audio/save/cold-load correctness and phase-qualified native/guest CPU + AudioOut attribution | A playable scene with valid audio/save/exit; distinct, trustworthy CPU buckets |
| 9 | **F0–F7** | 60–120s continuous presented-frame ledger, 3 matched A/Bs per source-proven optimisation | First 5/10/15/20 FPS, then 30 with P50/P95 <=33.33ms and safe headroom |

Work on N4 host tests and M1 read-only probes in parallel; **on-device memory safety gates precede another complete menu-to-world attempt**. All changes that alter storage/quality remain opt-in, reversible, and subject to pixel/semantic evaluation.

### 48.5. M1: instructions for a memory-safe menu diagnosis and admission policy

1. **Pre-launch baseline in the principal flow:** before executing the runtime, save run UUID, boot ID, MemAvailable, CmaFree, SwapFree, PSI, /proc/meminfo, game/process identities if any, MainUI/RSS, cgroup if present, page-cache and known GPU debugfs counters *when accessible*. After runtime creation, sample before the first NVN texture or EGL resource. One-second sampling alone misses the startup jump.
2. **Record allocation owners at creation and retirement:** instrument native/nvn_textures.h, native/nvn_framebuffers.h, window/EGL setup, and all reachable glTexImage/glTexStorage, glRenderbufferStorage, glBufferData/glBufferStorage, eglCreateImage/surface, deletions and context recreation. Use object identity=(GL share group, GL name, creation generation); bind guest/NVN object ID, format, WxH, levels, samples, source pool and per-use draw/fence serial. Separate texture allocations from colour-target *roles* — the same object must not be charged twice for being used as both.
3. **Track lifetime, not just peak sizes:** pending reservation, successful GL storage generation, alias views, in-flight last-reader serial, deleted-but-retained-until-fence, actual deletion/refund. Count renderbuffer depth/stencil separately, and track any transient full-frame staging PBO/buffer/readback. On failure glGetError, roll back the admission charge without assuming physical bytes have been freed. In the device report, label driver-resident counter unavailable when kernel/debugfs does not expose one; MemAvailable/CmaFree deltas are not an object-by-object physical GPU attribution.
4. **Move the safety decision closer to storage:** the reactive T2_MEMORY_FLOOR 250ms monitor lost a race to kernel OOM in nav-chain-05. At known high-risk allocations, sample available/CMA and *predict conservative additional storage* before calling GL, then refuse with a typed stop and exact requested bytes/owner if headroom would be unsafe. Keep the 96 MiB policy as the release gate; the 32 MiB floor was a diagnostic and should not be promoted. **Do not** change kernel CMA sizing, disable OOM, lift the 300 MiB texture cap or globally kill Spruce UI processes to force progress.
5. **Publish a reconciliation waterfall:** just-before-boot → first EGL → initial 1080p images → 1280p targets → title → menu frame1/frame16/frame31 → pre-refusal. Show delta by owner/class, actual process RSS/Swap, MemAvailable, CMA, and exact allocations/frees. Explain whether the initial 107 MiB texture charge is already included in a later frame/colour target estimate. Distinguish failure by available-memory floor, failure by GL allocation, and kernel/Mali kill with boot+timestamp corroboration.
6. **Host fixtures:** same GL name reused after delete, two views sharing storage, texture used as FBO, GL context loss, allocation failure, two depth objects, 4 MRT, 2x/4x MSAA, multiple mips/cube faces, lost fence, overflowing sizes, and transient CPU staging. Each object charged exactly once; no release before the last GPU reader; no ghost charge after failure. A Mali fixture can check real driver behavior in isolation without loading the game.
7. **Stop gate:** if the menu is still only ~50–55 MiB available or CMA ~1 MiB under the intended floor, do not attempt id295 or an extended New Game probe. First identify and remove/resize one **measured**, safely reversible class; rerun the exact menu A/B. A longer timeout cannot solve this pressure.

### 48.6. S1: deliberately small A/B on the already-existing scale switch

**Only with explicit approval to trial altered rendering**, retain both output modes and the original as default. No new shader substitutions, no patched game resolution service reply and no private asset publication.

1. Freeze the exact owner image/update, shader catalogue SHA, build ELF hash, Spruce version, thermal state, run harness, memory floor, 300 MiB texture budget and strict GL settings. Confirm ZERO_RENDER_SCALE=0/2 is the **only changed factor**; capture the effective env rather than relying on launcher defaults.
2. For each mode, run a **short menu-only arm** that stays within safe headroom, preferably 3 independent paired alternations A/B/A/B if memory is safe. Capture target inventory **by ID/generation**; verify all expected 1920×1080 targets changed, or recalculate the savings for the actual changed subset. Avoid entering New Game in this phase.
3. Capture two phase-matched, owned and decoded 1280x720 KMS frames per mode (plus intermediate FBO readbacks if staging needs diagnosis). With an animated screen, compare stable ROIs and present serial/phase rather than unrelated timestamps. Report both exact (tolerance=0) and tolerant differences, non-comparable cases, UV/tiling/alpha seams, text/UI readability, post-process output and user-visible quality. A tolerant match is **not byte identity**. Use a control-versus-control pair to estimate animation noise.
4. Report class nominal bytes (expected at most 17.58 MiB for four RGBA8-equivalent buffers), actual MemAvailable/CmaFree/Swap deltas, transient peak at creation, page faults, CPU and presented-frame distributions. A temporary overlap of old+new storage defeats startup savings. Reject unexpected sRGB/linear changes, GL errors, missed compositing, missing depth, non-equivalent text, worse frame P95 or less memory headroom.
5. **Decision:** if safe physical headroom improves and visible differences are acceptable, consider a user-selectable quality preset, still default-off until first-world parity. If the gain is noise, scene pixel parity fails or P95 regresses, revert this path. If only a menu target causes the issue and must stay 1080p for UI, consider owner-verified last-reader **fence retirement**, not blind glDeleteTextures after N frames.
6. **Future high-risk alternative (not next PR):** use a private SHA/offset-pinned owner-image rewrite of verified game literal dimensions and all dependent viewport/UV/matrix contracts, in a separate diagnostic branch, only if adapter storage scaling cannot preserve the intended projection. Verify the original binary checksum and use reversible image reconstruction; never globally patch guessed instructions or publish game code. It is not needed to test ZERO_RENDER_SCALE=2.

### 48.7. N5 / W0: establish an actual gameplay state machine and avoid the next false success

- Add page profiles built from **multiple owner-verified captures**: MAIN_MENU (current y=442/492/542/592), NEWGAME_CONFIG (own measured rows and enabled states), CONTROLS, LOADING and candidate WORLD. A changed pixel count or spinner is not a page. An unrecognised page is UNKNOWN and refuses further presses. Keep scene/world acceptance independent of the image oracle.
- Record an owned sequence: first menu serial → selected New Game row (two *different* confirming serials) → one Confirm and release → recognised config → bounded config choices based on real controls → controls dismissal → first loading receipt → Unity scene activate → first camera/player tick → first native NVN world draw → first KMS-visible world frame. At every transition write hashes/serials, same PID/starttime, action duration and phase classification.
- Interleave one-frame actions with validated releases and **bounded** scene-aware deadlines rather than 1000–1500ms open-loop holds. Find the one-row hold range only after menu headroom is safe; a 900ms press demonstrably skipped New Game, while <=350ms did nothing. It is not appropriate to publish a “550ms fix” before on-device measurement.
- If Unity activation occurs with black output, inspect real bound shader pair, CBUF bank, sampler, FBO ID, texture generation, viewport/scissor, blend/depth/stencil, draw count and GL errors; fragment45 **linked** is not proof it wrote four MRT colours. Test four independently colored half/sRGB MRT attachments on the same Mali context with precise glDrawBuffers/readbacks; audit seven TEST substitutes when truly drawn.
- If loading blocks on id295, take only a **pre-refusal descriptor** under the existing texture budget; distinguish sampled immutable BC3 from mutable/renderable, multi-mip or aliased storage. Only if format, extension, original owner hash and last writer prove a safe sampled atlas, prepare an **offline owner-private** ETC2/EAC or supported ASTC cache; GL compressed uploads must preserve alpha, mips, sampler behavior and fail back to original. Treat 8192² RGBA8=256 MiB versus ETC2 RGBA8≈64 MiB as nominal arithmetic, not a device-memory win until a fixture and full-game run establish it.
- If Unity activation does **not** occur, phase-tag same-run guest main-thread CPU, true thread CPU/wall and wait state, SVC 0x1A/0x1B and AudioOut endpoint cmd7/8, guest memory compression/page faults, and asset I/O. A round-robin sample count is not a CPU percentage. Do not fake Horizon event completion to advance scene logic.
- A correct scene is not yet PLAYABLE: prove physical player motion with changing world/player state, collision/interaction, inventory/dialogue, audible sound, quit/cold-save/reload, then proper Spruce MainUI/CPU-mask cleanup. Scene captures must be from a live in-run process, not the post-kill blank panel.

### 48.8. F0–F7: only measured optimisations, and an explicit feasibility stop

**Frame target:** 30 FPS = **33.333 ms complete displayed frame**. Historical 500–600ms Loading/menu periods are not gameplay FPS, and moving them to 33ms would be roughly an order-of-magnitude-plus improvement. Even after the memory issue is fixed, 30 FPS is a *goal*, not a plausible guarantee from scaling alone. Source timing from a different build/phase cannot be added to the current build's numbers.

Use independently repeated 60–120s **WORLD** samples after stable warmup: idle, walking on a reproducible route, heavy effects, dialogue/inventory, transition/loading. Collect *every unique completed presentation* with monotonic timestamps, p50/p90/p95/p99/max frame intervals, true visible FPS and dropped/duplicated frames. Record temperature, clocks, same-run ELF SHA, input latency/audio XRUNs, resident/CMA/swap and kernel OOM evidence. Use three matched A/B repetitions per change.

Pick **one** optimisation from the evidence, ordered by the largest exclusive stage:
1. **Page-fault / ZRAM / I/O tail:** reduce provably duplicated decompress/restore work, cache only within safe memory headroom, compare same real scene-progress intervals. Do not disable safety/swap or assert the historical clock_monotonic “cpu-compress” columns are true CPU time.
2. **Guest CPU / mutex / IPC / AudioOut:** tighten the hottest *demonstrated* translated trap, buffer-release poll or synchronization path with real contract fixtures and audio tests; no fake ready events.
3. **GL replay CPU:** inspect 1024×1 padded RGBA32F CBUF staging, tracked dirty regions, redundant NVN state translations, texture binds, format conversions, VBO/index uploads, program locations, FBO rebinding. CBUF TexSubImage is already default and showed no convincing whole-frame win; collect would-skip and full-frame before/after, not only per-function microbenchmarks.
4. **GPU fill and post-processing:** after W1, profile the game's true 1080p offscreen passes, bloom and four-MRT writes. Owner-verified 720p targets and opt-in bloom tiers may help **if GPU cost dominates**. Preserve UI native sharpness and every required attachment; compare visuals/temporal stability.
5. **Large immutable GPU atlas residency:** conditional offline ETC2/EAC/ASTC cache, exact generation/owner matching and GL compressed texture support; measure real GPU physical/headroom and rendering. Avoid keeping both decoded and compressed copies.
6. **Sync/pipeline:** only after fence/serial ownership, shared GL context and resource lifetime tests consider decoupling glFinish. glFlush does **not** imply completion and is not by itself an optimisation; previously observed NVN_COMMAND_REUSE_BEFORE_COMPLETION / EGL_BAD_SURFACE remain hard stops.
7. **Scheduler/CPU placement:** record exact effective affinity/frequency/governor/thermal constraints on Spruce; change one policy at a time with restore-on-exit and no interference with MainUI. This may improve a runnable thread but cannot safely invent RAM or bypass a genuine allocation limit.

Publish **5 → 10 → 15 → 20 → 30 measured gameplay FPS** milestones, each with correctness and P95, not optimistic menu counters. The strict stable-30 acceptance is **three >=60s independent real-world runs with P50 and P95 <=33.33ms**, ideally P99<=50ms, no unbounded stalls, safe RAM/CMA, correct pixels, physical controls, audio, saves and clean exit. If representative real-world CPU alone exceeds 33.33ms after identified redundant work is removed, report a measured sustainable ceiling (possibly <30) and reserve quality presets for an explicit trade-off.

### 48.9. Practical next three PRs and evidence checklist

**PR 1 — navigation contract repair, no hardware required.** Modify tools/navigator.py, tools/test_navigator.py, tools/nav_chain.py, tools/test_nav_chain.py, tools/load_metrics.py tests as needed. Commit the duplicate-serial Confirm regression first; then the monotonic timeout and owned incremental serial wiring. Prove identity restart, log truncation, stable serial repeat, 2-row overshoot, valid single-step, target held for two *different* serials, confirm release and expected page. Publish tests as source-level facts only; this PR must not claim a New Game run.

**PR 2 — M1 read-only ledger and admission.** Extend the public overlay around native/lc2_menu_ledger.h, nvn_textures.h, nvn_framebuffers.h and EGL/GL allocation callsites; add a pure host object-generation and charge/retire fixture. Capture a true pre-launch baseline, early GL allocation receipts, and a short safe menu-waterfall. Do not alter texture formats or enable a dangerous low memory floor. Capture exactly which object class is responsible for the most avoidable charged residency, including missing class labels. If the kernel kills the process, record the kernel evidence as failure rather than “safe stop”.

**PR 3 — a *conditional*, reversible single-factor storage experiment.** If M1 confirms an actionable 1080p owner and the user approves altered quality, compare ZERO_RENDER_SCALE=0 versus 2 on the same menu. Correct the savings upper bound to 17.58 MiB; require real RAM/CMA improvement and phase-aligned pixel reports. Otherwise prioritise verified lifetime/GL staging fixes from M1 rather than running the quality experiment speculatively. Only after this PR produces safe headroom should N5 config/controls capture and the first world attempt run.

**Per-PR required artifacts:** base commit and diff, 435/435 source baseline, host test counts, exact runtime ELF+catalogue SHA, private owner-image checksum (do not publish bytes), effective environment and original defaults, run UUID/boot/PID/starttime, image and log owner binding, fresh present serials, phase/timeline, before/after memory/CMA/GL generations, current actual STOP vs SIGKILL, post-run MainUI/runtime/principal and CPU mask. A passed compile or component fixture is not a playable or FPS result.

**Success means**: first stay alive in the menu at a safe policy, then select the correct menu item, then observe a real scene with true world pixels and input, then meet performance milestones. Reevaluate the roadmap on the next actual owned device evidence rather than expanding speculative optimisation branches.

## 49. N1: owned incremental present serial (owner §40.2 / §40.11 item 1) (2026-10-21)

> Owner §48 (post-build232 audit) is the current plan; this section records the N1 work it lists as the first PR, including the correction it made to my earlier arithmetic: the four 1080p targets are 31.64 MiB **before** resizing and still need 14.06 MiB at 720p, so the maximum nominal saving is **17.58 MiB**, not 31.64 MiB, and no physical Mali saving is claimed. `frame_diff` now reports `equivalent()` (inside tolerance) separately from `identical()` (zero difference), so a tolerance match can no longer be called identical.

Roadmap re-read at `a0aa160`; §40 is unchanged and its §40.11 order still starts with N1.

- **Retired**: `serial_request()` and its full-log `re.findall` scan. It would raise `ValueError` on the first present (the match was not a capture group) and every poll cost O(entire growing log) with no generation check, so a rotated log could hand back a previous run's counter.
- **Replacement**: `load_metrics.OwnedSerial` polls the owned byte-framed collector (`collector_request` + `fold`, `include_text=True`). Cost is proportional to new bytes; the generation/anchor checks that were already tested now gate the serial. A rejected generation returns `serial: None` / `fresh: False` and the old value stays history only.
- `present_serial()` counts **complete lines only** — a trailing partial record no longer qualifies a press.
- `tools/nav_chain.py` uses one `OwnedSerial` per chain, so the before-frame and after-press serials share a cursor and a generation.

Tests (**217 host total**): multi-record `frame=1/42/9` → 42 without exception; empty poll keeps the serial with `fresh=False`; **run A at frame 50 → rotation → refuse** (`serial=None`, no reuse); partial trailing line ignored then completed → 7; cursor advances instead of rescanning; 30 000-record backlog parsed from the chunk alone.

Open: the §40.2 item 6 device acceptance (before image → owned serial S → short press → owned serial S+ → after image, same PID/starttime) has not run with the new reader; and `nav_chain` still polls without an `expected_run` UUID, which is the next tightening.

## 50. M1 arithmetic: the 96 MiB floor cannot survive this menu (2026-10-21)

Owner §48 / M1. `tools/floor_analysis.py` (5 tests, 223 host tests total) computes drawdown, rate and floor-crossing projection from a measured ledger series without inventing values.

Measured shape (build230 `menu-ledger-01`, 41 presents / 20.5 s): start **129.3 MiB**, low **54.7 MiB at frame 16 (4.5 s)**, drawdown **74.6 MiB** = **16.46 MiB/s at 3.31 fps**; in the same window CMA 24.3 → 0.0 MiB, game `VmSwap` 0 → 422 MiB, charged textures **+50.2 MiB**.

| floor | margin | projected crossing | measured stop |
|---|---|---|---|
| **96 MiB** | 33.3 MiB | 2.02 s (~6.7 frames) | **frame 2** |
| 32 MiB | 97.3 MiB | 5.91 s (~19.6 frames) | frame 55 |

The projection is a linear upper bound on time, and the data shows a burst → plateau → decline shape: it agrees with the frame-2 stop (the first burst exceeds the 33 MiB margin) and under-predicts the 32 MiB case (19.6 vs 55 frames) because swap/reclaim recovers most of the early loss. Conclusion: the 96 MiB floor is not survivable by this menu beyond the first frames, so a longer timeout or a lower floor is not a fix — the menu's own allocation must shrink before any New Game attempt.

Ranked drawdown: (1) CMA exhaustion 24.3 → 0.0 MiB; (2) guest pages to swap +422 MiB; (3) charged textures +50.2 MiB; (4) three more colour targets ≈ +15.9 MiB with depth renderbuffers constant at 22.9 MiB; (5) buffers/EGL/driver storage untracked.

Recomputed from bytes, the four 1080p images are 31.64 MiB and still need 14.06 MiB at 720p, so the maximum **nominal** saving is **17.58 MiB** — matching the owner's correction, and at most a quarter of the observed drawdown.

Consequences: raising the floor, extending the run, or expecting the 720p scaling to fix the menu are all ruled out by these numbers. The live candidates are the CMA consumer and retained colour targets (B2 ownership/last-reader ledger) plus, with approval, the reversible 720p A/B as one factor gated by `frame_diff.equivalent()` with the exact comparison alongside.

## 51. Allocation receipts: the depth class is half my earlier estimate, and the 1080p family predates the first ledger line (2026-10-21)

Build233 `4c818517…b80c` adds `LC2_ALLOC_LEDGER=1` (bounded 64 lines, opt-in by value, no GL call changed) covering depth renderbuffers, stream/stable VBOs and the EGL window surface. Arm `alloc-ledger-01`: `T2_MEMORY_FLOOR`, verified identity, zero cleanup errors.

- **Correction:** the depth class is **2 renderbuffers / 11.98 MB** (8,294,400 at 1920×1080 and 3,686,400 at 1280×720). `GL_DEPTH24_STENCIL8_OES` (0x88f0) is **4 bytes/pixel**, but `lc2_menu_ledger` counted 8 for format 0x35, so the 22.9 MiB depth figure in §45/#46 was **2× too high**; the true value is 11.4 MiB. Source corrected (effective next build); the alloc receipts are now authoritative.
- **Ordering:** both depth buffers are created at log lines 1013/3686, while the first ledger record is at 4167. The three 1080p colour targets are texture-path objects created in the same window, so ~**33 MB of 1080p GL images** (3×8.29 colour + 8.29 depth) plus 3.69 MB of 720p depth exist *before* `arm-start` — which is exactly why that line already reports CMA at ~20 MiB.
- **CMA churns at the bottom:** 27.0 → 8.2 → 0.01 → 16.0 → 8.9 → 6.9 → 0.2 → 0.05 → 0.78 MiB. Consistent with per-frame allocation/free churn near exhaustion, but a **hypothesis**: no allocation timestamps or free receipts exist yet, and every line says `serial=none physical=unknown`.
- **Unmeasured classes, labelled as such:** EGL window surface (this configuration uses the SDL surface path, so the `eglCreateWindowSurface` branch never ran) and buffers (the menu issues no vertex-stream draws).

Next: emit the first ledger record at GL/texture init so the 1080p step appears inside the series instead of being baked into the baseline; then add retire receipts, which is the minimum before any "release retained targets" claim (owner §48 B2). The 720p storage question keeps its **17.58 MiB** nominal upper bound.

## 52. Early ledger: the pre-first-frame step is the guest heap, and CMA is exhausted before our GL (2026-10-21)

Build234 `571463a494a9` emits the first ledger record at **GL/texture init** (`why=gl-init`) instead of the first present, and adds retire receipts. Arm `menu-early-01`: `T2_MEMORY_FLOOR`, verified identity, zero cleanup errors.

Ordering: `gl-init` shows **available 568.7 MiB / CMA 0.75 MiB / charged 0**; the 1920×1080 depth renderbuffer (8,294,400 B) and the 1280×720 one (3,686,400 B) follow; `first-present` shows **available 134.9 MiB / CMA 23.5 MiB / charged 107.1 MiB**.

Two corrections to my own earlier conclusions:

1. **CMA was already exhausted before the 1080p family existed**, then recovered to 23.5 MiB and churned (0.3 → 13.7 → 19.5 MiB). The earlier "the menu drains CMA" was an artifact of a series that began after the reservation; CMA is contended at process start (MainUI hand-off, DRM/EGL init), not consumed by our GL images.
2. **The dominant step happens before the first frame**: −433.8 MiB between `gl-init` and `first-present`, of which the three 1080p colour targets plus two depth buffers are ~35 MiB of format-defined storage. The remainder is the guest's own reservation — invisible to the old series because its first record came after it. The previously reported 16.46 MiB/s describes only the post-reservation phase.

Consequences: intervention must target that reservation or what the guest keeps resident; 36 MB of GL images cannot explain it, and the 720p experiment keeps its 17.58 MiB nominal ceiling. CMA attribution now needs the pre-GL state (measured here) rather than post-hoc correlation.

Open: retire receipts produced no events in this phase, so allocate/free balance is unproven; the EGL surface (SDL path) and buffers (no vertex streams) remain unaccounted; the guest reservation is a delta without an owner.

## 53. Map receipts: the reservation is alias_physical, not a main heap (2026-10-21)

Build236 `5a1c04148c65` adds `LC2_MAP_LEDGER=1` for three mapping classes (main heap `svc 1`, `alias_physical` `svc 0x2c/0x2d`, blob/file).

Arm `map-ledger-01` is recorded as a **tooling defect**: its 48-line bound was consumed by blob mappings before the first alias line, so it reported `heap=0/0 alias=0/0`. Fixed with a per-class quota (12 blob lines, totals still counted) plus `LC2_MAP_SUMMARY`.

Arm `map-ledger-02` **ended in a kernel OOM kill** (`kernel_oom_sigkill`, `HARNESS_RC=8`, empty STOP taxonomy) — a failed arm, labelled as such. Its data: **blob/file 73,359,360 B = 69.95 MiB over 13 maps** (largest 29.4 MiB, totals complete); **`alias_physical` ≥130,654,208 B = 124.6 MiB over ≥36 maps**, still growing when the window closed, so a floor; **main heap 0 — `svc 1` is never used by this title**. The alias class includes one 64 MiB and one 32 MiB mapping plus a 1 MiB/256 KiB/8 KiB tail.

Established: the −433.8 MiB step is not a main-heap reservation, and two owners are measured (~70 MiB blob, ≥124.6 MiB alias). Not established: the remaining ~240 MiB, because alias totals are truncated by the line window and blob **unmaps** are not receipted, so the balance is one-sided. Not claimed: that `alias_physical` leaks — its `svc 0x2d` unmaps are uninstrumented.

Next: periodic summaries plus unmap receipts for both classes, one clean arm for a full alias total, then compare against the measured 568.7 → 134.9 MiB step. The 720p ceiling (17.58 MiB) remains the smaller lever.

## 54. `alias_physical` is a later phase, and `MemAvailable` is not game memory (2026-10-21)

Build237 `ee28f264afe6` adds `svc 0x2d` unmap receipts (`alias-unmapped`, `alias-live`) and a periodic `LC2_MAP_SUMMARY` every 64 events plus one on line-bound overflow. Arm `map-ledger-03`: clean `T2_MEMORY_FLOOR` stop, verified identity, zero cleanup errors.

| event | frames | available | CMA | charged |
|---|---|---|---|---|
| `gl-init` | 0 | 599.9 MiB | 0.01 MiB | 0 |
| `first-present` | 1 | 128.4 MiB | 20.6 MiB | 107.1 MiB |
| stop | 42 | 31.4 MiB | 5.5 MiB | 157.3 MiB |

Receipts in this arm: 13 blob/file events = 69.95 MiB, then **zero alias events** before the floor stopped the run (`alias-bytes=0/0 events=13`).

Three corrections to §53. (1) `alias_physical` is **not** part of the pre-first-frame step; it appears only in the longer OOM arm, i.e. during decoding/loading, so my §53 wording described an arm that had run past the menu's limit. (2) The `svc 1` main-heap path stays unused in every arm, so neither structured path explains the step. (3) `MemAvailable` is **contaminated by page cache** — the runtime reads a 1.74 GB image in exactly that window and page cache is reclaimable, so the −471.5 MiB step is not guest-owned memory; `VmData` (1,022,876 kB) is virtual, not resident. Claims of the form "the guest reserves N MiB" now require anon+shmem, not `MemAvailable`.

Tooling guarantee: class totals print on line-bound overflow and every 64 events, so a truncated window no longer hides totals, and alias unmaps are two-sided (`alias-unmapped`/`alias-live`), though unexercised here because the alias phase was never reached.

Next: one arm recording anon/shmem beside `MemAvailable`; then reach the alias phase deliberately and label it a loading-phase measurement; the 720p ceiling (17.58 MiB) stays a smaller lever.

## 55. The pre-first-frame step is our own RSS (+520 MiB); page cache falls (2026-10-21)

No rebuild needed: `lc2_menu_ledger` already carries `Cached`, `AnonPages`, `Shmem`, `VmRSS`, `VmSwap`.

| quantity | `map-ledger-03` | `menu-early-01` |
|---|---|---|
| `MemAvailable` | −471.4 MiB | −433.8 MiB |
| `Cached` | **−55.6 MiB** | **−52.6 MiB** |
| `AnonPages` | +240.4 MiB | +241.3 MiB |
| own `VmRSS` | **+521.0 MiB** | **+519.2 MiB** |
| `Shmem` / `VmSwap` | +0.0 / +0.0 | +0.0 / +0.0 |
| charged textures | +107.1 MiB | +107.1 MiB |

Conclusions. (1) **Page cache does not explain the step; it fell ~55 MiB** — §54's caution was right but the direction is opposite: cache was reclaimed into the process. (2) **The owner is our own process: RSS +520 MiB before the first frame**, of which ~241 MiB is anonymous and ~280 MiB file-backed image pages; the adapter's receipts (69.95 MiB of blob mappings) cover only adapter-served mappings, not the runtime's own I/O. (3) At the stop, `VmRSS` 731.7 MiB + `VmSwap` 415.1 MiB ≈ **1.12 GiB footprint on a 963 MiB board** — the floor stop is arithmetic. (4) The +107.1 MiB charge is identical in both arms, so texture accounting is stable if not dominant.

This replaces the "guest reserves N MiB" framing with a measured split: +241 MiB anonymous plus ~280 MiB file-backed inside our RSS. Neither is one declinable allocation; the file-backed half is the cost of reading the game image. Any lever must be judged against 520 MiB, ~30× the 17.58 MiB the 720p experiment could return.

Next: `/proc/self/smaps_rollup` (`RssAnon`, `RssFile`, `RssShmem`) per ledger record, so the file-backed half is a per-frame series rather than a two-point inference.

## 57. M1 same-run smaps reconciliation rejects the image-page attribution (2026-10-21)

Reviewed c2227d1 / owner §48.4–48.5. Fresh owned arm `smaps-owners-02` uses installed build239, original 96 MiB floor and 300 MiB texture budget; execution verified, STOP T2_MEMORY_FLOOR at frame 2, no cleanup errors. No storage-policy change or drop hint.

Four UUID/boot/PID/starttime/executable-inode-bound samples. Last sample (KiB): status VmRSS=710072, RssAnon=371452, RssFile=338348; summed smaps Rss=445536, Anonymous=373172. The 264536 KiB status/smaps gap is not ordinary image-file residency. Anonymous VMAs lead with 361912 KiB RSS, main.text.seg=30132, libmali.so=20320; /dev/mali0 VMAs show smaps Rss=0, which does not prove zero driver storage. Non-atomic samples; overhead not qualified.

**Retraction of §§55–56:** measured status values stand, but their attribution to game-image pages and the proposed reclaim/drop lever do not. System AnonPages cannot be subtracted from process RSS to assign owners. Small RssShmem does not rule out driver/DMA memory. Need same-window driver counters and accounting reconciliation, not page-dropping speculation.

Parser `tools/smaps_owners.py`, four tests (227 total PASS), per-path receipts and method in `docs/smaps-owner-reconciliation.md`. First attempt `smaps-owners-01` failed before owned execution (LOG_GENERATION_CHANGED); pending launch removed by UUID, exact acknowledge child recovery and synthetic shell acknowledgment recorded separately. Final state after retry: MainUI/principal/runtime each one, game zero, CPU mask restored, no pending command; real DRM screenshot shows Spruce. No gameplay or FPS improvement claimed.

## 56. RSS by class: 241 MiB guest heap + 255 MiB image pages before the first frame (2026-10-21)

> RETRACTED attribution: see §57. RssFile is not proof of ordinary game-image residency; small RssShmem does not exclude driver/DMA accounting. Do not implement the proposed drop A/B on this premise.

Build239 `b4edd887274a` prints `RssAnon`/`RssFile`/`RssShmem` from `/proc/self/status` on every ledger record (`-1` when unknown, so "missing" never reads as zero). Arm `rss-split-02`: clean stop at frame 61, verified identity, zero cleanup errors.

| record | frames | anon | file | shmem |
|---|---|---|---|---|
| `gl-init` | 0 | 122.3 MiB | 72.2 MiB | 0.11 MiB |
| `first-present` | 1 | 363.1 MiB | 327.2 MiB | 0.27 MiB |
| interval | 53 | 207.9 MiB | 497.9 MiB | 0.26 MiB |
| stop | 61 | 218.9 MiB | 492.2 MiB | 0.26 MiB |

`gl-init → first-present`: **anon +240.8 MiB, file +255.0 MiB**, reproducing the earlier aggregate `VmRSS` step within a few MiB, now split by class. So the pre-first-frame cost is half guest arenas, half game image pages.

At steady state the halves diverge: anon falls 363 → 219 MiB (`VmSwap` ~415 MiB) while file rises to ~492 MiB. The steady footprint is a small anonymous core plus a large resident image working set; `shmem` is negligible (~0.26 MiB), which rules out shared-memory/dma-buf accounting for the RSS gap.

Consequence: the file half is the larger addressable term at steady state (~492 MiB). Nothing in the adapter advises dropping consumed image pages, and no receipt shows whether the runtime re-reads them — a concrete, testable question. The 720p item stays at 17.58 MiB, one thirtieth of the file half. No FPS claim is made: dropping image pages would change memory pressure, which is what stops the run at frame ~61.

Next: instrument the image read path (touched, re-read, drop hints) and measure one reversible A/B of dropping already-consumed image pages.

## 58. M1: same-window Mali metadata tracks the status/smaps gap (2026-10-21)

Reviewed 7a5b8cb and owner §48.4–48.5. `mali-reconcile-01`: unchanged build239, original floor 96 MiB/cap 300 MiB/strict GL, verified UUID/boot/PID/starttime/executable identity. STOP T2_MEMORY_FLOOR at frame 16, no cleanup errors. No input/world attempt, no storage or admission change.

Debugfs was unmounted, not unsupported: temporarily mounted, read driver allocation metadata, unmounted and verified original state. Five sequential samples (3.83–20.42 ms read windows, overhead unqualified). Status VmRSS minus summed smaps RSS: -284, 45384, 141068, 246112, 299832 KiB. Mali gpu_memory raw counts: 0, 11546, 35368, 60555, 74855. Native commit descriptor sums: 0, 47169536, 144543744, 253177856, 335257600 bytes; last sample additionally Imported UMM=11059200 bytes.

If raw counts are 4 KiB pages, last count corresponds to 299420 KiB, close to the 299832 KiB RSS gap. Exact firmware units/accounting implementation remain unverified; co-growth is evidence for Mali accounting investigation, not exact attribution. Descriptor sums are not alias-deduplicated physical bytes and must not be added blindly to RSS. Largest Native descriptors commit 55984128 and 32821248 bytes, plus several 8990720-byte objects: guest/NVN/GL owners NOT established; do not infer dimensions or release safety from sizes.

Report `docs/mali-rss-reconciliation.md`, raw metadata/reconciliation in `evidence/mali-reconcile-01`, parser with 3 tests, 230 host tests PASS. Final state: supervisors/MainUI each one, game zero, CPU mask restored, no pending command, debugfs unmounted; DRM screenshot shows Spruce charging clock (not gameplay/home icons). Next is owner/generation binding of large Native storage plus firmware counter verification, not image-page dropping. No FPS/playability gain claimed.

## 59. N4-A/B host core: unique-frame Confirm and monotonic response deadline (2026-10-21)

Reviewed 0344ac0, owner §48.2 A/B and §48.4 priority 1. Five assertion regressions reproduced against the original source: duplicate/older serial Confirm, conflicting same-frame cursor action, unknown-cursor streak carryover and off-target-return carryover. Prior-source red output retained under `evidence/n4-unique-confirm/`.

`Navigation` now tracks all observed serials, refuses backwards/conflicting observations, WAITs on duplicates without progressing, clears confirmation evidence when cursor leaves the target or becomes unclassified, and requires two unique agreeing target observations. Replaced the three-poll refusal with an injected monotonic clock and bounded positive finite response timeout. One hundred fast polls WAIT; a post-deadline fresh page cannot resurrect an expired action; MAIN_MENU after Confirm cannot renew its acknowledgment deadline. Timeout carries elapsed/last/issued serial and explicitly owner_verified=false.

Nine new tests, 239 host tests PASS. Five-second default is a HOST diagnostic bound, not device-calibrated. No runtime build/deploy or device state change. Report `docs/n4-unique-confirm.md`. N4 is still open end-to-end: integration must bind ownership/generation and discard navigation state on changes, preserve release ACK, qualify liveness and calibrate timeout; N5 page fingerprints and M1 safe memory headroom still gate a world attempt. No FPS/playability claim.

## 60. N4-C/D host integration: persistent owned reader/navigation and release ACK (2026-10-21)

Reviewed 21e40fd / owner §48.2 C/D, §48.4 priority 1. `nav_chain.py` now delegates to `owned_nav_chain.py`; removed old basename discovery, unpinned reader, unbracketed capture and per-tap Navigation-reset control path. CLI requires expected-run receipt, explicit bounded timeout and diagnostic-input opt-in; no default legacy sweep or Confirm.

`OwnedNavigationDriver` retains one incremental `OwnedSerial(expected_run=...)` and one Navigation. Qualified header generation/process identity pinned once; any ownership/collector rejection is terminal, never a silent reset. Collector/process checks bracket capture/oracle and press/release. Changing serial across capture discards the image. Matching released=True action receipt required, preserved even when a post-release generation check fails. Same navigator makes overshoot terminal without corrective taps; capture/transfer elapsed time recorded. Overall deadline enforced after slow capture and before input. Cross-process check/write races are narrowed, not eliminated atomically.

14 new tests; 253 host tests PASS and Python 3.10 syntax PASS. Real OwnedSerial collector payload executed in a local subprocess on temporary UUID-headed fixture logs: rotation during capture refuses without input/rebinding. Transport fixtures cover foreign capture, capture serial drift, missing release, press rotation, repeated serial, slow capture expiry and terminal overshoot. CLI guard subprocesses require receipt and explicit opt-in before SSH. Fixtures are not device observations.

Report `docs/n4-owned-driver.md`, evidence `evidence/n4-owned-driver/`. No device actions/runtime changes this step. Confirm remains blocked pending M1 safe-memory/N5 semantic-page gates; real one-row movement, tap/timeout calibration and observer overhead remain OPEN. No world/playability/FPS claim.

## 61. M1 GL-call -> Mali metadata brackets identify owner81 upload activity (2026-10-21)

Reviewed 2d4c36f / owner §48.5. Build240 (`474d17adaa12...`) adds default-off `LC2_STORAGE_PROBE=1`: first 12 >=1M-pixel initial glTexImage2D/renderbuffer storage calls, <=512 descriptors and <=4096 lines per read, <=8 changed-descriptor lines/call plus overflow. NVN ID/GL name/kind/size/mip/format bound to before/after driver VA/commit metadata; no storage/content/lifetime/admission/GL synchronization policy changed. Missing metadata is invalid, never fabricated zero; no mem_view/guest-memory reads.

Owned `storage-bracket-01`: original floor96/cap300/strict GL, no input; 12/12 valid brackets. Texture owners3/4 and depth owner28 (1920x1080) each coincide with one 8990720-byte Native descriptor. Owner81 / texture GL39 / 3600x2160 coincides with 31109120-byte and 32821248-byte Native descriptors plus two 262144-byte descriptors. This ties the previously unexplained 31.30 MiB allocation to that upload window, NOT exclusively/permanently to one texture. Background/staging/aliases remain possible; no release safety inferred. The 55984128-byte descriptor remains unbound (outside first 12 observed calls).

Bracket windows 1.28–50.38 ms include GL+metadata, not isolated observer overhead. Pinned build435/435 and host254 tests PASS; clean-export verification retained. Runtime STOP T2_MEMORY_FLOOR at frame7, no cleanup errors; MainUI/principal/runtime each one, game zero, CPU mask restored, no pending command, debugfs unmounted, physical DRM capture shows Spruce home icons. Atomic install/full independent SHA read-back; build239 backup retained, build240 installed probe default-off. Report `docs/storage-mali-brackets.md`, evidence `evidence/storage-bracket-01/`. Next: locate the remaining large descriptor and distinguish owner81 staging from retained storage across completion, before any release/quality/alias change. No gameplay/30 FPS gain.

## 62. M1: same-run owner81 descriptor retention (2026-10-21)

Reviewed 4f5f8dc / owner §48.5. No rebuild or storage/sync/policy change: installed build240, original floor96/cap300/strict GL, no input. `storage-retention-01` collects 13 owned snapshots; eight follow the completed owner81 GL39 upload marker (log byte290101). Process/run/log/context bound; snapshot log size is recorded BEFORE driver metadata to qualify post-bracket ordering.

Owner81 bracket's VA0x5ef6000000 (31109120 B / 29.67 MiB) is present at first post-bracket observation, absent 0.852s later and all seven remaining observations. VA0x5ef7e00000 (32821248 B / 31.30 MiB) is present unchanged across all eight observations over6.192s. Do not count both as permanent owner81 storage. Upload staging vs persistent texture is a hypothesis, not proven: no fence/completion, continuous VA-generation identity or physical refund measured; no deletion/drop authorized by these observations.

The55984128-byte descriptor first appears between snapshots5.017s and5.908s; intervening log window includes a3600x3600 texture GL47 and other allocations. This narrows where to bracket next but establishes no owner from size/proximity.

Runtime STOP T2_MEMORY_FLOOR at frame8, execution verified, cleanup_errors=[]; MainUI/principal/runtime one each, game zero, CPU mask restored, no pending command, debugfs unmounted, DRM shows Spruce home. Four new parser/correlation tests,258 host tests PASS, clean-export verified. Report `docs/storage-descriptor-retention.md`, evidence `evidence/storage-retention-01/`. Next: bracket remaining large allocation and prove retained ownership/lifetime, not heuristic freeing. No physical-headroom/playability/FPS improvement claimed.

## 63. M1: late brackets locate the 55984128-byte descriptor in NVN92 upload (2026-10-21)

Reviewed f3a0c11 / owner §48.5. Build241 b4c8df27e5c9... adds diagnostic-only LC2_STORAGE_PROBE_WINDOW=late (eligible tickets13..24; default still1..12, main probe default-off, unknown windows select none). Boundary/disable C fixture passes. No GL storage, synchronization, content, admission or lifetime policy change.

Owned storage-late-01 uses floor96/cap300/strict GL, no input. Six valid brackets tickets13..18. Ticket13 NVN92 / GL47 /3600x3600 /format0x44 coincides with Native descriptors51847168 B (49.4453125 MiB) and55984128 B (53.390625 MiB), plus two421888 B descriptors. The previously unexplained53.39 MiB descriptor is now tied to this upload WINDOW, not exclusively/permanently to that texture. No duplicate permanent-byte charge or safe-free inference.

Five post-marker snapshots show the first VA absent then reappearing at4263936 B, while the second stays55984128 B. This demonstrates VA is not generation identity; staging, pool retention and reuse remain possible. No GPU fence/completion/physical refund established. Ticket13's168798038 ns includes upload+metadata, not isolated overhead or FPS.

12 owned process samples; verified runtime STOP T2_MEMORY_FLOOR at frame4, cleanup_errors=[]; MainUI/principal/runtime one each, game zero, CPU mask restored, no pending launch, debugfs unmounted, DRM shows Spruce home. Atomic/hash-verified deployment with independent read-back, build240 backup retained; build241 installed default-off probes. Pinned build435 checks and host258 tests PASS; clean-export verification retained. Report docs/storage-late-owner.md and evidence/storage-late-01/. Next: actual storage generation/readers/retirement/physical accounting, not heuristic release or unapproved quality changes. No safe-headroom/gameplay/30 FPS result.

## 64. M1: observed sampler users, not a last-reader ledger (2026-10-21)

Reviewed 0896412 / §48.5. Unchanged build241; existing T2_DRAW_TEXTURE_EVERY=1, LC2_STORAGE_PROBE=0, floor96/cap300/strict GL, no input. Owned sampler-census-01 reports630 generic sampler-preparation events across frames1..13:30 sampler IDs,17 target IDs on those events. NVN81/92 have no matching sampler/target records, although both have source-write receipts. This is a candidate startup-materialization question, NOT proof of unused/immutable/reclaimable storage. Specialized paths, aliases, share groups, storage generations, finalization and GPU completion remain unaccounted. No free/lazy change follows.

New offline sampler_census.py plus6 regression tests retain frame order, reject malformed/regressing events, ignore partial trailing lines and separate roles; explicit absence_proves_unused=false, physical_refund_bytes=null. Clean-export host264 PASS. No runtime change/rebuild or performance comparison claimed. STOP T2_MEMORY_FLOOR at present13, harness4, execution_verified=true, cleanup/identity errors empty, game0 and supervisors/MainUI1; CPU4-7 restored, no pending cmd, debugfs unmounted, DRM Spruce home. Details docs/sampler-census.md, evidence/sampler-census-01/. Next remains generation/alias-resolved use/completion/retirement accounting under §48.5. Menu headroom, gameplay and30 FPS OPEN.

## 65. M1: executable generation/alias/retirement core, not runtime integration (2026-10-21)

Reviewed d8474fa / §48.5. The overlay now carries standalone native/lc2_lifetime.h: bounded64 storage slots and64 timeline identities, unique storage tokens and distinct object generations, explicit share-group/kind/name namespace, reserve/commit failure rollback, alias views, last-reader/completion, retirement/deletion guards and whole-share-group loss. Declared payload is NOT driver residency. No GL calls, allocation, runtime caller, admission change or automatic deletion is introduced; every pre-existing overlay section is byte-identical.

Host fixture extracts the header from the public patch, compiles under C11/-Werror/undefined-sanitizer trap and executes57 assertion sites (capacity loop exercises64 entries). It rejects early delete, live views, wrong/lost fence, stale token/completed serial, completion regression, failed delete, group identity reuse after loss, capacity/overflow. Respecification retains both generations and refuses name-based deletion that would also destroy the newer storage. Actual failed allocation rolls back only pending logical intent. Clean-export host265 PASS; pinned-container ARM64 fixture compile verified. No ARM device execution or GL success/completion evidence is claimed.

Details docs/lifetime-core.md, evidence/lifetime-core/. This closes a HOST-CORE component, not §48.5 or GPU lifetime safety. Next: observation-only integration with real share-group/name generations, all storage success/failure and alias-resolved reader/completion receipts; then real Mali lifecycle fixture. Multi-timeline consumers and old-storage respec retirement remain conservative refusals. No runtime deployment, memory/FPS improvement or new device-cleanup claim. Installed build241 unchanged; safe menu headroom/world/30 FPS remain OPEN.

## 66. M1: first measured GL storage generations — 24/24 names reused (2026-10-21)

Reviewed e93d818 / §48.5. Observation-only integration (native/lc2_life_events.h, default off, 512 entries, write()-only report from the existing stop path) at the two glTexImage2D texture sites, zero_texture_storage join/release and the TextureFinalize storage delete. No admission/budget/floor/format/lifetime/deletion change; renderbuffers, PBO/FBO/EGL surfaces, specialized/CPU-view uploads and GPU completion remain uninstrumented and unclaimed. Every record prints share-group=unverified, so the ledger cannot justify deletion.

Defect caught before measuring: the stop-path decimal formatter added a trailing digit to every non-zero counter (1140→11400), i.e. a 10x inflation. The build243 arm is recorded as a tool defect, not a measurement; a regression now compares all ten fields against snprintf.

Build244 f35b935224ae13df643c14fe2f95df01a2fada5a0bb3c644730b4549e5130574, 435/435 baseline; atomic deployment with hash read-back, build243 in .before-244. Owned arm life-events-02 (PID19297, floor96/cap300/strict GL, no input): storage-calls162, extends50, deletes24, delete-with-views0, name-reuse24, retained/peak232834352 B (222.05 MiB declared payload), live88, alias-views0, overflow0. So 112 images created, 24 deleted, and **every deleted GL name was reused by a later image** — measured proof that name-keyed accounting/deletion is unsound here and that §65's object/storage generation split is required. delete-with-views=0 is a guard receipt at one site, not global safety; alias-views=0 means the ZERO alias path was not exercised. The run's menu ledger (93 live, ~110 MiB charged) counts a different basis and is NOT reconciled with222.05 MiB; neither is physical residency.

Off arm life-events-off-01 (same build/settings, no env) produced zero summaries and the same STOP, so default-off behaviour is observed. Both arms: STOP T2_MEMORY_FLOOR, no OOM receipt, cleanup[]; game0, MainUI/principal/runtime1, CPU4-7, no pending launch, debugfs unmounted, DRM Spruce home. Host266 tests PASS in a clean export; C fixture covers disabled-by-value, mip extension, alias deltas, reuse, delete-with-views and overflow. Details docs/life-events.md, evidence/life-events-02/, life-events-off-01/. No memory, headroom or FPS improvement claimed. Next: renderbuffer/PBO/EGL coverage plus a real completion receipt, and same-run reconciliation against the ledger and gpu_memory.

## 67. M1: per-class declared storage — textures 238.84 MiB, depth 11.43 MiB (2026-10-21)

Reviewed bb81569 / §48.5. The §66 observation ledger now labels classes (1 texture, 2 renderbuffer, 3 buffer), records depth renderbuffers at glRenderbufferStorage/release, and treats glBufferData on an existing name as a REPLACEMENT (new respec path) instead of another mip — a host regression asserts the first store is an allocation and later ones are respecs. Still default off, still no GL/admission/budget/floor/delete change.

Build245 846ef10c3850ec245c702243b3c82b59ca398a863506a78cf1e76d62522ae314, 435/435. Owned arm life-events-03 (PID22012, floor96/cap300/strict GL, no input): storage-calls167 extends50 deletes25 delete-with-views0 name-reuse24 retained262419760 B (250.26 MiB) peak270243120 B (257.72 MiB) live92 alias-views0 overflow0, tex-bytes250438960 (238.84 MiB)/tex-live90, rb-bytes11980800 (11.43 MiB)/rb-live2, buf0/respecs0. Arithmetic closes exactly: 92 live + 25 deleted + 50 extensions = 167 calls. Peak−retained = 7.46 MiB transient. Buffers are zero because the vertex-stream/stable-VBO paths are off here, so respecification is host-only evidence.

Textures and depth are the first per-class split of this ledger. Both figures are DECLARED payload, not Mali residency: the same run's menu ledger shows 93 live textures with a 115278848 B budget charge while this sum is 238.84 MiB of per-level requests, and the two bases are NOT reconciled. delete-with-views=0 is a single-site guard receipt. No class was freed, resized or deferred.

STOP T2_MEMORY_FLOOR, no OOM receipt, cleanup[]; game0, MainUI/principal/runtime1, CPU4-7, no pending launch, debugfs unmounted, DRM Spruce home. Staged atomic deployment with hash read-back, build244 in .before-245. Host266 tests PASS in a clean export. Details docs/life-events-classes.md, evidence/life-events-03/. Next: reconcile declared payload against budget charge and gpu_memory in one run, then a real GPU-completion receipt before any reader-epoch claim. Menu headroom, world and30 FPS remain OPEN.

## 68. M1: three storage bases reconciled; depth matches to the byte, textures 2.09x apart (2026-10-21)

Reviewed 4c91bbe / §48.5. Device-only arm (no build, no runtime change) with a 0.3 s device-side sampler recording pid/starttime/LAMENTUM_RUN_UUID/boot/VmRSS and mali0/gpu_memory during a principal-flow run (floor96/cap300/strict GL, no input); debugfs mounted only for the arm and restored. New host tool tools/ledger_bases.py pairs the bases from one run and refuses foreign/mixed identity, a missing ledger line, or a window without a gpu_memory reading.

Arm ge-ledger-04 (run 70d73d87-bc79-4616-9fbb-4e81f09ead61, game PID26543 in 31 samples): declared payload textures 241485104 B (230.2981 MiB, 90 live) and depth 11980800 B (11.4258 MiB, 2 live); budget charge textures 115278848 B (109.9385 MiB, 93 live) and depth 11980800 B. **Depth agrees to the byte between two independent accounts**; textures differ by 2.0948x with the cause NOT established (declared sums every requested level, the charge is a budget figure) and no waste implied. gpu_memory spans 0..84900 units while total declared payload is 241.72 MiB; the unit is not derived from driver source, so it is quoted as an open question rather than a physical total.

Four earlier attempts are recorded as tool defects, not results: one long SSH sampler call (timeout), a reused evidence directory (harness refused), gpu_memory's first token mis-parsed as the counter, and samples without the run UUID (pairing refused). They stay owner-local under private-backups/ge-invalid/.

STOP T2_MEMORY_FLOOR, no OOM receipt, cleanup[]; game0, MainUI/principal/runtime1, CPU4-7, no pending launch, debugfs unmounted, sampler files/process removed, DRM Spruce home. Host273 tests PASS in a clean export. Details docs/ledger-bases.md, evidence/ge-ledger-04/. Next: per-texture split (level-0 vs full chain vs scaled/half) to explain the 2.0948x without guessing, and a source-derived or fixture-calibrated gpu_memory unit. Menu headroom, world and30 FPS remain OPEN.

## 69. M1: the 2.09x texture gap is decoded-vs-compressed; mips are 0.68 MiB (2026-10-21)

Reviewed 2aba2d3 / §48.5. The opt-in ledger now classifies texture requests (level0 vs extra mips, scaled/half, charged vs uncharged, and the guest/compressed size of charged textures) with a host regression per bucket; still no GL/admission/budget/format/delete change and still default off.

Build247 ecef4ba2075946095e69120137366850c41184d26e3e82c995cdd98995bd6575, 435/435. Arm tex-levels-02 (floor96/cap300/strict GL, no input): tex-bytes241485104 (230.30 MiB, 90 live), tex-l0 247062780, tex-mips713780 (0.68 MiB), scaled/half 0, tex-charged247776560, tex-uncharged0, tex-guest107024384 (102.07 MiB); budget charge at the last interval115278848 (109.94 MiB, 93 live). Declared/charge = 2.095, decoded/guest = 2.256.

Two candidate explanations are measured and refuted for this phase: extra mip levels are 0.29 % of the payload, and no declared request belongs to an uncharged texture. The difference is the BASIS: the budget is denominated in guest/compressed storage while GL holds decoded pixels, so a 300 MiB cap does not bound GL residency (at this ratio ~675 MiB decoded on a 963 MiB board). That is accounting, not a fix; no cap/admission/format policy changed. A residual 7.7 % between tex-guest and the charge is unexplained and recorded as open.

STOP T2_MEMORY_FLOOR, no OOM receipt, cleanup[]; game0, MainUI/principal/runtime1, CPU4-7, no pending launch, debugfs unmounted, DRM Spruce home. Staged atomic deployment with hash read-back, build246 in .before-247. Host273 tests PASS in a clean export. Details docs/tex-levels.md, evidence/tex-levels-02/. Next: per-texture guest/decoded/charge pairing to resolve the 7.7 %, then the same against gpu_memory once its unit is derived. Menu headroom, world and30 FPS remain OPEN.

## 70. TSPS statless launcher smoke; M1 still gates New Game (2026-10-22)

Commit `3bb74d3c2c56e87e5d2741da4208a5864e6a996a` removed the launcher's dependency on the absent target `stat` command by using Python `os.stat`; the launcher/test change is pushed to `main`. On TSPS, the previous launcher was backed up (`63bfac5…`), the new launcher hash `f32204ff…` was installed, and the matching helper/runtime were read back as `abe8e484…` / `ecef4ba…`.

Owned principal-flow run `da207fdd-f695-491a-a35c-3068f69bfb59` (boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda`, PID/starttime `6944/169845`) verified the runtime ELF identity. It recorded 12 `NVN_PRESENT_PIXELS` entries, then stopped itself at `T2_MEMORY_FLOOR_HIT available-MiB=62 floor-MiB=96 swap-free-MiB=1986`; `STOP status=T2_MEMORY_FLOOR`, no kernel-OOM evidence, zero `LC2_MENU_EVENT`, and no input. `HOST_CPU_AFFINITY role=guest-main cpus=0` confirms the required core was online. This does not establish an in-game picture or an FPS sample.

Cleanup errors were empty: no game remained, `MainUI`/`principal.sh`/`runtime.sh` were restored, mask `4-7` returned, and CPU0–3 returned to `online=0, mode=0444`. A local-only post-cleanup 1280×720 KMS capture shows the Spruce PORTS menu; it is not a Lamentum frame and remains excluded by repository policy. Evidence summary: `evidence/launcher-smoke-20261022-01/`. Raw log, kernel dumps, and screenshots remain local. The launcher cleanup compatibility gate is closed; safe menu headroom, New Game/world, input/audio/save, and the 30-FPS target remain open. Follow §69 M1 per-texture pairing; do not lower the 96-MiB floor or enter New Game until the menu can safely retain headroom.


---

## 71. Post-build247 audit: safe first-world bring-up, performance, and REA feasibility (2026-10-22)

**Reviewed source HEAD and same-day device receipt:** [3bb74d3c2c](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/3bb74d3c2c), including the preceding [ed78c1b](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/ed78c1bb2d). Read the recent source/commit diffs, current roadmap §§48–70, runtime and launcher, [October 22 launcher smoke](../evidence/launcher-smoke-20261022-01/README.md), texture/lifetime reports, and upstream [morluto/rea](https://github.com/morluto/rea) documentation. **The original audit was source/evidence review, not a device run or FPS measurement; the later build248 device follow-up is recorded below.** Keep previous numbered sections as a historical record. This section supersedes older NEXT priorities wherever implementation already exists.

**STATUS: NOT PLAYABLE.** Working menu/Options/New Game UI and Loading observations are distinct from a correct controllable world. No verified world movement, audible audio, cold save/load, or gameplay FPS exists. **Goal order: memory-safe menu -> correct owned navigation -> first real world -> playable audio/save -> measured gameplay FPS -> 30 FPS.**

### 71.1. What was actually completed

| Workstream | Verified progress | Still open |
|---|---|---|
| N4 navigation | Commits 21e40fd and 2d4c36f: distinct-present Confirm, monotonic response deadlines, persistent owned navigation, release acknowledgements; host tests | Live device-calibrated page-chain acceptance to Loading and WORLD; no uncontrolled repeated Confirm |
| Build247 M1 | Declared live decoded textures 241485104 bytes / **230.30 MiB**; depth 11980800 bytes / **11.43 MiB**; extra mips only **0.68 MiB**; charged guest/compressed texture bytes 107024384 / **102.07 MiB** | Per-generation same-time join and remaining budget mismatch; physical driver units and residency; no saved memory yet |
| Build248 M1 follow-up | Run `fcb27ba2`; 117 opt-in per-initialize pair events, 114 with live GL records, 3 unknown/no-live, zero pair overflow; safely stopped at floor95/96 | Event-only totals, no timestamped generations or per-ID retirement; no live-set join or headroom gain |
| Build249 M1 follow-up | Run `cc013fc9`; timestamped object/storage generations, 116 texture-pair records, 163 GL storage events, 24 deletes; replay through the floor timestamp reconstructs 89 live GL records and matches the lifecycle summary exactly | Per-object T2 budget retirements and exact charge at the floor remain unclosed; GL-lock trylock was busy, PSI unavailable, no menu/headroom gain |
| Memory budget | Last sampled texture charge 115278848 bytes / **109.94 MiB**, versus decoded 230.30 MiB; decoded/guest ~**2.256x** and decoded/charged ~**2.095x** in this one menu arm | 300 MiB budget is in a different basis than decoded GL storage; it does NOT cap physical GL/Mali residency to 300 MiB |
| Lifetime | Native lc2_lifetime.h C11 test core, object/storage generation tokens, aliases/readers/retirement guards; build244 observed **24/24 deleted GL names reused**; build245 added renderbuffer class | Share-group, all allocation paths, GPU completion, independent live backing and physical deletion unproven; core is not an automatic reclaimer |
| Mali correlation | Native upload brackets for owner81/GL39 and owner92/GL47; one descriptor disappears/reuses a VA; one persists in sampled interval | Allocation VA is not stable resource identity; staged/retained attribution and actual refund unproven |
| Launcher | ed78c1b restores sysfs CPU online mode AND original permissions; 3bb74d gets modes with Python os.stat instead of depending on GNU stat; regression for missing stat | **October 22 device smoke verified**: 12 present records, typed T2_MEMORY_FLOOR at 62 MiB versus floor96, no menu events; CPU0–3 online=0 and mode=0444 restored; forced-exit branch not separately qualified |
| Rendering | Known literal 1920x1080 game-side render targets; physical panel already 1280x720; partial shader-through-45 and menu GLSL fixes | Actual fragment45 four-MRT output, correct world pixels, total scene GPU cost, and first-world shader census |

**Accounting interpretation:** In the same build247 arm, the 230.30 MiB live decoded texture payload is far larger than the 102.07 MiB guest/compressed payload. The additional mip-level total is only 0.68 MiB; scaled/half and uncharged request buckets were zero in this phase. The texture cap of 300 MiB in guest/charged units may correspond to considerably greater decoded GL requests; 300 × 2.256 ≈ 677 MiB is an illustrative pressure warning, **not a measured physical allocation or generally valid conversion factor**. The residual ~7.7% between guest and last charge is also not proven overhead: the sampled counts differ (90 versus 93 objects) and may span different instants. Resolve it by joining the *same live generations at the same timestamp*. Do not infer a leak. Sources: [tex-levels](tex-levels.md), [ledger-bases](ledger-bases.md), [life-events](life-events.md), [lifetime-core](lifetime-core.md), §§65–69.

**Memory gate:** the new [launcher smoke](../evidence/launcher-smoke-20261022-01/README.md) verified build247 on-device, 12 NVN_PRESENT_PIXELS records, zero LC2_MENU_EVENT, and a safe T2_MEMORY_FLOOR refusal at **62 MiB versus floor96**, with clean MainUI/process/CPU value+permission restoration. These are not confirmed Lamentum visible frames or gameplay FPS. Earlier menu arms reached MemAvailable about 54.7 MiB and CmaFree about 1 MiB while normal T2_MEMORY_FLOOR_MIB=96 was active. Historical 96 MiB floor stops are real safe refusals, not successful gameplay. 32 MiB was a diagnostic floor, not a valid release fix. The current accounting additions did not improve headroom.

**Build248 follow-up:** [run report](../evidence/texture-pair-20261022-01/README.md). It verified the new ELF on the same device/boot, emitted 8 presentation records and 117 bounded initialization pairs, then stopped at **95 MiB vs floor96** with no OOM evidence and zero menu events. Prelaunch, GL-init, first-present, interval, and stop samples exist; PSI, guest-mmap/first-GL-allocation landmarks, frame16, and a timestamp-qualified final live set do not. The screen was verified as SpruceOS MainUI after a documented non-physical Back wake. This is partial M2A observation, not a fix or gameplay result.

**Build249 follow-up:** [run report](../evidence/m2a-20261022-01/README.md). Run `cc013fc9` produced 3 presentation records, no menu event, and a safe `T2_MEMORY_FLOOR` stop at **68 MiB vs floor96**; there was no OOM evidence. First-present recorded 119140 KiB `MemAvailable`, 17512 KiB `CmaFree`, and 112325632 bytes budget-live. The timestamped storage journal had 163 events and 24 deletes with zero overflow. The floor callback could not acquire the GL lock (`EBUSY`), but replaying all events through its timestamp reconstructed 87 texture + 2 renderbuffer records totaling 236520752 bytes, exactly matching `LC2_LIFE_SUMMARY`. This is a declared GL-storage set, not proof of physical residency. Per-object T2 budget release and the exact charge at the floor remain open. Cleanup and KMS confirmed SpruceOS MainUI, not Lamentum. The report documents two harness parser defects: an unanchored stop match and a stale global frame count; only the owned run's 3 presents and actual `T2_MEMORY_FLOOR` stop are used.

### 71.2. P0-M2A — Source-accurate generation-joined memory ledger

**Code locations to inspect before each edit:** native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_render.h, native/lc2_lifetime.h, native/lc2_life_events.h within runtime/lamentum-adapter.patch; tools/ledger_bases.py, applicable life-event fixtures, actual guest mmap/alias logic, and the runtime stop handler. Never edit reconstructed baseline files directly; preserve the manifest-pinned 435-file source and include changes in the overlay patch.

**Make this an observation-only/default-off PR first.**

1. Before runtime spawn, capture the run UUID, boot ID, launcher/ELF SHA256, CPU state/mode, MemAvailable, CmaFree, SwapFree, PSI and MainUI process. Capture another sample at guest mmap creation, first EGL context, first GL image allocation, first present, menu frame1/frame16 and immediately before the stop. Sampling only every second misses the startup reservation. Label early guest-heap RSS and later alias_physical events separately; process VmSwap is not physical GPU residency.
2. At every texture creation and extension, record a bounded tuple: (run_id, share_group_generation, GL object_generation, unique storage_token, GLuint, NVN texture_id, guest_pool_id, source_write_generation, format, width, height, mip, layers, samples, decoded_requested_bytes, guest_payload_bytes, budget_charge_bytes, allocation_success, alias_parent, last_reader_serial, retirement_state). **Never key by GLuint**: all 24 deleted names in build244 were recycled. Never key by virtual address: driver VAs were observed reused.
3. Join all three size bases on one storage token and one timestamp, rather than summing an end-of-run declared total against an earlier interval budget line. Emit both event-level and live-set totals; enforce declared=mip0+extra mips only where those quantities share identical counting scope. Separate allocated, retained, evicted, view-alias and pending reservation generations. When joins are missing, mark them unknown rather than treating them as zero.
4. Resolve the remaining guest-versus-budget residual with per-object exact size rules, alignment, creation time and live-object count. Do not add speculative 7.7% safety factors. Test charge-once semantics for a texture used as both sampled image and framebuffer attachment.
5. Complete **all actual storage classes**: color textures, depth/stencil renderbuffers, GL buffer/PBO staging, EGL images/surfaces, shared context groups, temporary readbacks and host staging. FBO objects and sampler views are not automatically extra backing storage. Distinguish driver debugfs totals, declared GL payload, process RSS, guest swap and charged budgets.
6. Extend the owner-tested C11 lifetime state machine with *observed* GL create/failure/delete transitions and actual queue read/completion serials. A command submission return is not GPU fence completion. For name respecification, retain old storage conservatively until a verifiable retirement receipt. For unknown share groups or lost context, refuse an automatic release.
7. Preserve low overhead: a bounded ring and stop-time report, no per-draw printf, no glFinish per storage call. Compare probe-off and probe-on arms with the exact same binary/scene and verified process identities. Store physical driver units as unknown until derived from kernel source or a controlled Mali allocation fixture.

**Host red/green cases:** GLuint reuse after deletion; respecification in same object; two views of one backing; 2D/cube/multi-mip/depth; 4-MRT with shared attachments; failed admission and GL error rollback; lost context; old fence serial; late asynchronous reader; integer overflow/counter wrap; partial final event; missing sampler readings; boot/PID/UUID mismatch. A fixture must refuse deletion if any reader, resource generation, or GPU completion is uncertain.

**PASS:** a timestamp-joined storage/guest/budget ledger with exact counts and explicitly bounded unknowns; source of the observed mismatch either explained or narrowed to per-object evidence. **STOP:** negative balances, phantom frees, source mismatch or instrumentation that changes memory behavior. **This PR does not yet save RAM.**

**Build249 status:** the opt-in records now carry run ID, monotonic timestamp, object/storage generation, owner and subresource; create/extend/delete events are replayable. In the owned build249 run, all 163 GL storage events and 24 deletes preceded the floor timestamp; replay yielded 89 live records (87 textures, 2 renderbuffers; 236520752 bytes) and matched the later lifecycle summary byte-for-byte, with zero event overflow. This closes the *GL-recorded storage-set replay* for that run, despite the direct snapshot's GL mutex trylock returning `EBUSY`. It does not close exact per-NVN budget liveness: budget removals are not yet timestamped per object, and the three `no-live-gl-storage` pairs cannot be retired by GL-name evidence alone. PSI is unavailable on the device, and guest-mmap/first-GL-allocation landmarks plus frame16 remain unobserved. Keep the 96 MiB floor and 300 MiB cap unchanged; do not infer physical Mali residency or proceed to a storage policy change from these declared counters.

### 71.3. P0-M2B — Protect allocations *before* the device is out of memory

After M2A, add a **separate, default-off pre-allocation admission gate**, targeting the earliest actual large GL storage call.

1. For each intended storage object, compute validated decoded byte sizes from real GLES format/width/height/depth/samples/levels, checked with 64-bit overflow guards and correct BC alignment. Separately record CPU staging, temporary upload buffers and known driver-alignment uncertainty; do not simply add every counter if buffers alias.
2. Immediately before a high-risk storage call, read validated host MemAvailable/CmaFree and the in-process committed/pending memory ledger; compare conservative requested peak against the existing normal 96 MiB floor and measured CMA needs. Preserve cap300 and strict GL. If unsafe, return a typed T2_STORAGE_ADMISSION stop with owner/generation/requested_bytes/available/CMA/phase, **before** the driver can OOM.
3. Transactional flow: reserve intent -> GL call -> GL success/failure receipt -> commit logical bytes or rollback **only uncommitted intent** -> later retire only after all readers and GPU completion. A failed GL call does not prove the driver refunded everything. Do not free based on absent sampler records, old GL names, or elapsed seconds.
4. Compare no-input menu arms: original reactive floor, admission-on, and diagnostic-only observer. A safe early refusal is a safety improvement, **not proof of playability or FPS gain**. Confirm actual T2_MEMORY_FLOOR versus T2_STORAGE_ADMISSION versus EGL/GL OOM versus kernel SIGKILL with timestamped identity and cleanup receipts.
5. Test early and late cleanup on the actual Spruce device: restore CPU online values **and sysfs permissions**, preserve MainUI, unmount temporary debugfs and remove sampler processes. Do not bypass the floor by raising guest quotas, swap changes, killing system UI, or changing kernel CMA.

**PASS:** every tested large allocation is either safely admitted with known headroom or rejected before kernel/Mali OOM. Actual additional *available* memory is a later optimization task.

### 71.4. P0-G3 — Reduce a measured storage class; choose one lossless path first

**G3-A: GPU-compressed texture side cache (conditional).**

1. Pick ONE large source texture with exact owner-image and texture-content hash, immutable source generation, verified BC type, actual mip array and sample consumers. Historical id295 8192x8192/256 MiB decoded reservation is a known hazard, but **not proof** it is the best candidate or that its current metadata matches an older arm.
2. Query the actual Mali GLES extension list; run standalone compressed upload/draw/readback validation for device-supported ETC2/EAC or ASTC formats, correct alpha, sRGB/linear, LOD and target. Do not claim compressed-format support from SoC marketing specs alone.
3. Prepare a content-addressed transcode in the owner's **private** workspace, including original SHA, full dimensions/mips, color/alpha mode, encoding parameters and resulting cache SHA. Never publish proprietary input/output textures. Verify deterministic load, failure fallback and strict source hash before applying the substituted upload.
4. Keep lossless BC decode as original default and the experimental side cache opt-in. Evaluate actual Mali resident memory and process/system headroom **alongside** the accounting ledger, cache read latency, visuals in a world/menu ROI and whole-frame stalls. Transcoding BC3→ETC2/ASTC is often **lossy**, therefore it also needs an explicit quality decision. Small compressed file size alone is not sufficient.
5. Stop on incomplete owner identity, unverifiable driver support, wrong alpha/mips/sRGB, memory regression or a cache that causes repeated blocking I/O.

**G3-B: generation- and fence-qualified lifetime retirement (conditional).** Only remove a storage generation after proving every ordinary/special sampler and framebuffer consumer is done, the latest command serial is GPU-complete, and alias views are gone. Submit a correct GL deletion, measure post-delete physical headroom, and keep a rollback guard. The fact owner81/92 have no generic sampler census entry does **not** mean they are unused. Descriptor VA disappearance likewise does not prove a physical refund.

**G3-C: lazy upload/partial staging (conditional).** Use first-actual-reader evidence, immutable source, exact write generations and lossless reconstruction before deferring upload or splitting a large staging request. Compare memory peak *at the first world*, not only during the menu: moving a 256 MiB upload to an already stressed frame can make things worse.

**G3-D: 1920→1280 scoped render target.** The four hard-coded 1920x1080 targets amount to **31.640625 MiB nominal original payload**, **14.0625 MiB** if all become 1280x720, hence **17.578125 MiB maximum nominal saving**; actual affected subset/driver RAM is unknown. Existing ZERO_RENDER_SCALE=2 is a default-off quality experiment, historically no net performance win. It cannot by itself erase a >40 MiB floor deficit. Do NOT invent a Switch docked/handheld setting to explain these literal guest dimensions. Only run an owner-approved A/B with exact/tolerant pixel comparison, UI/stencil/UV equivalence, temporary overlap peak and measured physical savings.

**G3 PASS:** repeatable safe memory headroom for the SAME phase with correct image semantics and no new stall. **STOP:** a smaller budget number without actual RAM benefit, unclear lifecycle or visual regressions.

### 71.5. P0-N5/W0/W1 — Verify New Game and actual gameplay rather than more menu probes

1. **Pin identities:** current installed ELF SHA, exact owner Switch image/segments, metadata, catalogue and adapter hashes, Spruce version, memory floor96, texture cap300, strict GL. Source HEAD 3bb74d alone does NOT prove that launcher or runtime was deployed.
2. **Qualify navigation on device:** use the currently implemented persistent owned reader/N4 action graph, newer distinct presentation serials for observations, monotonic time deadline, mandatory button-release ACK, same PID/starttime/UUID before and after each capture. An identical frame seen twice must never satisfy a two-frame Confirm. A failed page oracle must refuse input instead of sending an automatic corrective press.
3. **Prove exact page transitions** TITLE → MAIN_MENU → NEWGAME_CONFIG → CONTROLS → LOADING → FIRST_WORLD. Acquire actual DRM captures *while the same process is alive* and bind image SHA, serial, phase and action. A changing Loading animation or frame counter is not a world receipt.
4. **First Loading arm** only after menu memory passes M2/G3 safety gate. Collect bounded scene progress: RomFS reads, allocation intent/commit, texture first uses, shader creation/link/**draw**, service calls, guest-scheduler wait, memory faults and actual time spent in Unity scene activation. Stop on unknown state; increasing test budget is not a memory fix.
5. **World graphics:** verify entry44 vertex and entry45 fragment are actually *drawn*; linking them is insufficient. Capture independent four-MRT results, formats/depth/stencil/alpha/UV/sRGB and downstream reads. If no world pixel but scene counters advance, diagnose framebuffer/shader/camera first, not timeout. If a real missing shader blocks, capture exact code/control bytes and append only that program while preserving the existing build202 UBO bank and shader identity corrections.
6. **World interaction:** one documented player movement and camera/scene change, inventory/interaction, dialogue, one transition; physical gamepad receipt and screenshots. Nonblack pixels and a Loading transition alone fail this gate.
7. **W1 correctness:** audible music/effects, save -> quit -> cold relaunch -> load to the same world state, proper full cleanup. Host tests for navigation and shader fixtures do not substitute for this physical acceptance.

**W0 PASS:** reproducible actual first-world pixels plus controlled character motion. **W1 PASS:** interaction, scene transition, audible sound, and cold save/load. **STOP:** missing owner/capture, early memory-floor condition, unverified shader pair, broken framebuffer or GPU error. No gameplay FPS claim before W0.

### 71.6. P1-F0 — The performance plan once W0 succeeds

- F0-A: quiet, phase-qualified 60–120 second presented-frame ledger, CPU scheduling and per-thread CPU, wall vs guest wait, memory compression/fault CPU, NVN replay, GPU fence waits, swap. Use no high-volume GL logging or readback. Three matched runs and exact serial coverage; exclude loading only from an **explicit separate** steady-world metric. Old build202 title/Loading P50/P95 is not gameplay.
- F0-B: if host/guest wait dominates, trace Unity PlayerLoop vs Horizon SleepThread/WaitSynchronization and compressor contention; modify only semantics proven by call-site inspection. If GL replay dominates, start with native/nvn_render.h kind=7 glTexImage2D-per-cbuf cost, buffered glTexSubImage2D and exact-content/generation skip; then sampler state, FBO churn and buffer allocations. If GPU fill dominates, qualify target resolution/bloom and tile-based render passes.
- F0-C: avoid performance shifts: moving CPU replay time into glFinish, accumulating new resident GL caches, or reducing FBO resolution while breaking readable UI all fail. Resource caching keys MUST include share group, object/storage generation, backing write epoch and last-reader/fence semantics.
- F0-D: staged throughput targets 5/10/15/20 and **30 FPS**, with original roadmap's whole-frame P50/P95 ≤33.33 ms, P99 and no recurring >100 ms stutters, under safe RAM/thermal and valid audio/save constraints. Menu-only 30 FPS or an inverse median interval is not acceptance.

### 71.7. REA investigation: could Switch or Windows decompilation yield a native ARM64 launcher?

**Short decision:** [REA](https://github.com/morluto/rea) is useful for *targeted reverse engineering* of the owner game, but **does not automatically turn a Windows x86-64 game or Switch NSO into a native Linux ARM64 game**. The current Switch port already uses **native ARM64 machine code** wrapped by a Linux AArch64 Horizon/NVN/Unity compatibility runtime. The greatest practical benefit of REA is finding the exact owner function/ABI/resource/scene behavior blocking this adapter; not reproducing an entire Unity engine from decompiler output.

#### R0: determine the actual Windows backend, rather than assuming Mono/IL2CPP

Use a legitimately owned Windows installation, kept OUT of this public repository:

    WIN_GAME="/path/to/owned/Lamentum"
    find "$WIN_GAME" -maxdepth 5 -type f \( \
      -iname 'Assembly-CSharp.dll' -o -iname 'GameAssembly.dll' \
      -o -iname 'global-metadata.dat' -o -iname 'UnityPlayer.dll' \
      -o -iname 'mono-2.0-bdwgc.dll' \) -print

    # REA upstream requires Node.js 22.19+/24.11+/26+ and a configured provider.
    npx rea-agents setup
    rea inspect-desktop-application "$WIN_GAME" --json

- **Candidate Windows Mono:** Assembly-CSharp.dll under Game_Data/Managed with UnityEngine references, plus the expected Unity Mono runtime. REA can inspect managed PE/CIL method bodies, types, member references and P/Invoke. High value for behavior reconstruction; not a Linux ARM64 Unity engine.
- **Candidate Windows IL2CPP:** GameAssembly.dll plus Game_Data/il2cpp_data/Metadata/global-metadata.dat (inspect actual layout; do not guess installation filename). REA can decode selected metadata versions and use Ghidra/IDA/Hopper to examine native methods. The PC x86-64 code is not ARM64 executable.
- Both, neither, an old archive or partial installation => **unknown**. Confirm the files, headers and game-build hashes; no verified Windows-backend evidence is in this repository.

**R0 PASS:** manifest with Windows build/version, scripting backend, owner SHA-256 of exact binaries/metadata and a known set of game classes/scene-loading candidates; all kept private.

#### R1: Windows Mono branch — highest source-level recovery potential

    ASSEMBLY="/path/to/owned/Lamentum_Data/Managed/Assembly-CSharp.dll"
    rea inspect-managed-artifact "$ASSEMBLY" --json
    rea inspect-managed-members "$ASSEMBLY" --json

REA's [managed analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) returns metadata, CIL and native boundaries; for readable reconstructed C#, use a separate managed decompiler such as ILSpy, and verify it against the original CIL. Locate real game type/method tokens for scene activation, settings/resolution, save, UI, movement and resource lifetime. Build an owner-private symbol map (method token, type, precise field offsets/serialization, call references, assembly SHA and behavior proof). Contrast with Switch evidence at exact pinned native PCs. Prototype **one** platform-specific contract or isolated function instead of promising a whole-engine rewrite. Recovering C# script logic would not provide Unity's original project/scenes/build pipeline or a native ARM64 Unity Player.

#### R2: Windows IL2CPP branch — native method map, not source recovery

    META="/path/to/owned/Lamentum_Data/il2cpp_data/Metadata/global-metadata.dat"
    ASM="/path/to/owned/GameAssembly.dll"
    rea inspect-il2cpp-metadata "$META" --json
    # If and only if metadata format/layout and matching binary are accepted:
    rea inspect-il2cpp-metadata "$META" --binary "$ASM" --json
    rea inspect "$ASM" --provider ghidra --json
    # First obtain real function address/name from the REA inventory.
    rea search "$ASM" Scene --kind procedures --provider ghidra --json
    rea function "$ASM" VERIFIED_PROCEDURE --provider ghidra --json
    rea decompile "$ASM" VERIFIED_PROCEDURE --provider ghidra --json

**Replace VERIFIED_PROCEDURE with a real name/address** returned by the provider. Supported [metadata versions](https://github.com/morluto/rea/blob/main/docs/il2cpp-metadata.md) are 24, 27, 29, 31, 39, subject to strict per-layout checks: Unity 2019.4 *may* have version24, but older variants can be rejected. REA's documented automatic method-address linker targets GameAssembly.dll, GameAssembly.dylib and Android libil2cpp.so, not Switch NSO. It does **not** regenerate original C++ from IL2CPP or rebuild Unity's runtime. Keep binary/metadata identity verified, treat inferred addresses/generic instance omissions carefully.

#### R3: Switch ARM64 branch — use pinned local NSO/sections with correct address layout

The existing repo records exact owner main.text.seg evidence, for example [hard-coded 1080p call sites](1080p-origin.md) around main.text.seg+0x53bfcc. On the owner's original extracted game, verify decompression, .text/.ro/.data load addresses, offsets, relocations, entry and SHA; **no such private binary was provided in this audit**.

REA [raw-binary Ghidra support](https://github.com/morluto/rea/blob/main/docs/raw-binary.md) accepts arm64 with a caller-supplied mapping base:

    SWITCH_TEXT="/path/to/owned/main.text.seg"
    # REPLACE BOTH placeholders with VERIFIED hex VA and procedure values.
    VERIFIED_TEXT_VA="0xHEX_FROM_OWNER_SEGMENT_MAP"
    rea inspect "$SWITCH_TEXT" --target-format raw-binary \
      --architecture arm64 --entry-point "$VERIFIED_TEXT_VA" \
      --provider ghidra --json
    rea function "$SWITCH_TEXT" VERIFIED_PROCEDURE \
      --target-format raw-binary --architecture arm64 \
      --entry-point "$VERIFIED_TEXT_VA" --provider ghidra --json

Raw mode maps **one file as one region**; it does not reconstruct Switch NSO imports, separate RO/DATA segments, relocations, Horizon dynamic loader or method registration. For cross-segment references, prefer an owner-local NSO-aware Ghidra loader or a carefully reconstructed ELF representation with verified VA/relocation checks. A wrong base can produce plausible but false pseudocode and xrefs. Extracted Switch IL2CPP metadata may be inspected separately if its header is accepted; do not assume REA automatically maps it to Switch NSO methods.

**High-value reverse-engineering questions** (one at a time): where Unity/guest constructs the literal 1920x1080 render target family; whether texture295/owners81/92 are immutable/first-used/scene-retired; the exact scene AsyncOperation and Loading transition; origin of the first world draw and fragment45 four-MRT render pass; guest CPU hot wait site; source of a specific Horizon service/ABI mismatch. For each: known PC and module hash -> REA/Ghidra dossier and xrefs -> independent runtime trace -> one reversible adapter experiment -> source/host/device tests.

#### R4: what kind of "native launcher" is feasible?

| Proposed design | REA usefulness | Feasibility / blocker |
|---|---|---|
| **Keep running Switch AArch64 IL2CPP code in the current native Linux AArch64 Horizon/NVN adapter** | Targeted bug/ABI and performance analysis | **Best practical route**: ARM64 code already runs; fix GPU residency, services and world rendering |
| Rebuild Windows Mono game scripts into new ARM64 game | High if actual Windows Mono CIL exists | Research-level: requires Unity scenes/serialization/asset importer, compatible engine, graphics, scripting, input and audio reimplementation; not a launcher toggle |
| Translate Windows x86-64 IL2CPP pseudocode into compilable ARM64 | Useful for a tiny isolated function | **Not a full-game strategy**: no original IL2CPP generated C++, managed runtime/Unity native APIs or equivalent optimized semantics |
| Wrap raw Switch NSO as a Linux ELF and dlopen | Finds imports and register/memory contracts | **Not a standalone solution**: Horizon ABI, TLS, exceptions, GPU NVN, threads, filesystem, IPC, Unity engine remain |
| Rebuild on available engine from recovered data | Helps identify scene/gameplay contract | Only viable as a long independent porting project with a correctly reconstructed single-room prototype and legal asset handling |

**R4 proof-of-concept gate:** choose **one** known contract blocking safe Loading or world draw, pin Switch/Windows original hashes, derive a testable before/after behavior from verified REA evidence, implement only a small self-authored native adapter or fixture change, run host ABI tests and an owner-qualified handheld A/B with full cleanup. Reject a proposed "REA-native port" without a playable one-room prototype; REA results alone are not a native ARM64 game.

**Licensing/data rule:** use only legally accessible owner binaries, do not commit original game NSO/DLL, metadata, shaders, transformed assets or bulk decompiled pseudocode. Preserve independent hash-pinned evidence rather than publishing proprietary artifacts.

### 71.8. Prioritized PR execution order and hard gates

| Order | PR | Deliverable | PASS / immediate STOP |
|---:|---|---|---|
| CLOSED | **L0** | The [Oct 22 smoke](../evidence/launcher-smoke-20261022-01/README.md) verified statless launcher, owned principal execution, safe memory refusal and CPU online/mode restoration | Normal typed-stop/device cleanup PASS; **forced-exit branch still untested** |
| 2 (PARTIAL) | **M2A-1** | Build249 has prelaunch, GL-init, first-present and exact typed-floor timestamps; see [receipt](../evidence/m2a-20261022-01/README.md) | PSI unavailable; guest-mmap/first-GL-allocation landmarks, frame16, and exact per-object T2 budget at the floor remain open |
| 3 (PARTIAL) | **M2A-2** | Build249 timestamped storage generations and replays 89 live GL records (236520752 B) at floor, matching lifecycle summary | Per-object budget add/sub and no-storage object retirement; aliases/readers/fences/physical residency still open |
| 4 | **M2A-3** | All-class framebuffer/renderbuffer/buffer/EGL staging + fence/reader lifecycle | No early free, completed reader proof or explicit unknown |
| 5 | **M2B** | Tested preallocation admission with normal floor96/cap300/strict GL | Typed refusal before kernel OOM; no storage policy shortcuts |
| 6 | **G3-A/B/C** | ONE selective GPU compression / provably dead storage / JIT upload experiment at a time | Same-scene **actual** memory savings, correct pixels, no FPS regression |
| 7 | **N5** | Unique-owned page chain to verified New Game Loading | Physically captured and released Confirm and all page oracles |
| 8 | **W0** | First actual four-MRT correct world image + character movement | Valid owner scene screenshots and input, not just menu or shader link |
| 9 | **W1** | Audible audio, inventory and save/cold load/scene transition | Playable world acceptance |
| 10 | **R0–R4**, parallel research | Identify owned Windows backend and one REA-aided adapter POC | Confirmed function/callsite or explicit unsupported result; no full-engine diversion |
| 11 | **F0** | Quiet 3×60s minimum gameplay profile and independently tested optimization | Full-frame P50/P95 target, no visual/memory/audio regression |

Every PR must report: SHA256 for source patch, recovered baseline manifest, installed ELF, original owner image and shader catalogue; exact env and feature-off fallback; clean host fixtures; run UUID/boot/PID/starttime; stateful owned screenshot and log coverage; available/CMA, decoded/charged/driver bases with unknown units labeled; typed stop; MainUI/principal restoration; original CPU **online value and mode**, zero stray processes and no lingering debugfs mount. Do NOT describe a new host test count as device proof or the *absence* of an OOM record as positive memory safety without full kernel/run evidence.

**Immediate recommendation:** L0 normal-stop acceptance is closed by the Oct 22 smoke. Finish the per-object T2 budget add/sub timeline and correct the stop/frame snapshot parsers; then retain M2A's generation-joined basis and preallocation safety barrier **before a new New Game run**. In parallel, inspect the owner's **Windows install** with R0 to determine whether a Mono CIL path exists. Use REA primarily to understand the exact Unity scene/resource/SVC blockers in the current ARM64 runtime, not as an automatic native conversion pipeline.


---

## 72. Build248 re-audit: pre-first-present memory, generation-safe evidence and a practical first-world/30-FPS route (2026-10-22)

**Scope and provenance.** Audited `main` at [b72ff869](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b72ff86937c299f4eeddf879b42de07a7461439a), including [the build248 implementation](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/6773743664e4e031ed5b2f68e87d2931bd825f59), `runtime/lamentum-adapter.patch`, `tools/test_life_events.py`, `tools/device_principal_test.py`, the owned [build248 run receipt](../evidence/texture-pair-20261022-01/README.md), build247 texture figures, earlier memory reconciliation, [build229 menu](../evidence/menu-229-02/README.md) and [newgame-20](../evidence/newgame-20/summary.json). This section is a **source/evidence audit and updated implementation plan**, not a new compile, device run or performance benchmark. Retain §71 as the immediately preceding plan; this section refines its execution sequence and introduces implementation-level checks discovered in the newer source.

**Status: NOT PLAYABLE; no measured gameplay FPS.** Do not equate `NVN_PRESENT_PIXELS`, a nonblack counter, a correctly linked program, Loading activity, or a post-cleanup KMS image with first-world evidence. The latest build248 run is a no-input menu-phase diagnostic and ended in `STOP status=T2_MEMORY_FLOOR`, not kernel OOM. The currently installed build248 ELF is SHA256 `1462d92791748650e951cd9256d1fee712213b18bc08e25b8eb22ab0b4aaa73a` per its owned receipt; source HEAD alone never proves a subsequent deployment.

### 72.1. New source-verified findings and re-prioritization

| Finding | Source/evidence | Implication |
|---|---|---|
| **The largest observed pressure occurs before the first present.** | Build248 `gl-init` MemAvailable 592,924 KiB, first present 130,156 KiB after 6,574 ms: **−462,768 KiB / −451.92 MiB**. At frame8/7,603 ms another 52,248 KiB / **51.02 MiB** lower. `CmaFree` at first present was just 3,504 KiB, later 11,764 KiB. | Instrument guest mappings/allocations and first GL storage **before frame1**, not just per-frame or Loading. These are sequential system samples, NOT exclusive ownership/accounting or a synchronized per-object total. |
| **Current memory telemetry is too close to its own bound for the next scene.** | 117 `LC2_TEXTURE_PAIR` initialization records versus `LC2_LIFE_TEXTURE_PAIR_CAP=128` (11-event margin); `LC2_LIFE_EVENT_CAP=512`. | Add bounded streaming/aggregation with overflow-as-incomplete handling before expanding to Loading/world. Merely raising caps risks new resident RAM. |
| **Reused numeric names are not resource identity.** | `lc2_life_event_find(name, kind)` and `lc2_life_events_storage_payload(storage_owner, kind)` lack verified share-group, level-specific generation and GPU completion. Device shows **24 GL-name reuses**. | Generation-qualified live set is mandatory; never infer physical frees from `glDeleteTextures` or from disappearing Mali VA. |
| **Current observation may be wrong on respecification/longer runs.** | In `lc2_life_events_storage()`, a live GL name takes `e->bytes += bytes`; it assumes each call is an **additional mip**. `glTexImage2D` can redefine an existing mip. Slots are allocated by `!entries[i].name`, whereas delete marks `live=0` but leaves `name` set. | **Potential** false live/peak totals on same-level redefinition, plus eventual slot exhaustion despite deletion. Test reachability before claiming build248 counts are incorrect; fix semantics regardless before trust in a world run. |
| **The last event-pair totals are not a simultaneous budget.** | 117 events aggregate 116,851,712 B guest/charge, 239,125,808 B GL texture requests and 11,980,800 B depth requests; 3 records have no live GL match. The final interval separately had 93 live textures / 115,278,848 B charge. | The three absent GL records can include intentionally deferred images, not necessarily leaks. Add a precise `deferred/unmaterialized/unknown` category and join generations at a common epoch. |
| **The old floor-only memory guard is not a headroom fix.** | 96-MiB release floor, 300-MiB *guest/compressed* texture budget; build248 stops at 95 MiB, earlier arms hit kernel Mali OOM. | Pre-allocation admission reduces unsafe failure; **only a real peak-residency reduction can make the game load**. Run a headroom-saving branch in parallel with safety instrumentation, not after endless ledger work. |
| **Before/after snapshot fields have different ownership.** | Build248 `cleanup.json` has `before.frame=12`, `after.frame=8`, while its owned log confirms 8 build248 presents. `device_principal_test.py` snapshots before launching and the collector refuses prior `latest.log` until the new UUID appears. | This can be a valid pre-existing log counter, but **the before-frame count must never be presented as belonging to build248**. Add source/run labels or null for unowned prelaunch log-derived fields. |

**Memory decision:** prioritize a measurable first-frame/high-water saving over shader work or a nominal frame-time micro-optimization. The first 451.92-MiB available-memory drawdown is a **phase difference**, not automatically “GPU textures consumed 451.92 MiB”: guest anon, mapped file pages, shared driver accounting, UMA/CMA and transient staging need independent exact-time reconciliation. Build247's **230.30 MiB decoded texture request vs 102.07 MiB guest-compressed source** and **109.94 MiB interval charge** give a concrete candidate mismatch; they do **not** establish physical GPU residency. The earlier status-vs-smaps gap and Mali descriptor series forbid additive “RSS + GPU” arithmetic without overlap proof. Do not turn a decoded/charge ratio into a new speculative memory cap.

### 72.2. PR M2A-4 — Make the existing per-texture ledger correct across generations (P0; observation only)

**Files:** `runtime/lamentum-adapter.patch` overlay for `native/lc2_life_events.h`, `native/nvn_textures.h`, `native/nvn_framebuffers.h`, `native/nvn_render.h`; `tools/test_life_events.py`; add `tools/test_texture_live_set.py` and `tools/texture_live_set.py` for offline verification. Do **not** directly edit the 435-file recovered baseline.

1. Build a **distinct immutable event stream** and a **current-live storage index**. Event fields: `run_uuid, boot_id, CLOCK_MONOTONIC timestamp_ns, event_seq, share_group_generation or UNKNOWN, context_generation, nvn_id, source_pool/write_epoch, gl_target, gl_name, object_generation, backing_generation, face, mip_level, operation, requested_format, dimensions, declared_bytes, guest_bytes, charge_bytes, result, reader_serial, completion_state`. Unknown is an explicit value, not zero. Keep address/GL-name as *labels*, never global identity. If runtime UUID is only available elsewhere, emit a same-run header mapping; refuse joins without it.
2. Split `glTexImage2D`/storage creation from `glTexSubImage2D`/content writes. Define storage by `(share group, GL object generation, target/face, mip)`; define one backing/storage generation for respecification. `TexImage` of an existing face/mip **replaces** that subresource's current declared size, not `+=`. `TexSubImage` advances content-write generation without counting a second image allocation. `glRenderbufferStorage` and `glBufferData` also replace current logical definitions; renderbuffer/texture attachment aliases reference one backing without double charging.
3. Preserve **old in-flight backings separately** on redefinition/deletion until a proven last reader and GPU completion; distinguish *current logical live*, *pending-retire*, *historical requested bytes*, *temporary staging* and *known physical allocation*. GL delete immediately ends logical naming but is **not a promise of physical refund**. Explicitly say `fence-unverified` until a context-correct fence/wait/proven completion model exists.
4. Replace the “first unused slot where `name==0`” rule with an index keyed by generation that safely reuses **retired** slots while the append-only record sequence (or bounded summary) retains delete history. Keep event counters separate from slot indices, and avoid using a stale reused slot to infer a read or release. Establish a bounded constant memory limit and a `dropped-events` count; if required events overflow, classify the run `INCOMPLETE_LEDGER` and prohibit downstream safety decisions. Do not simply increase the two fixed caps and assume a complete gameplay trace.
5. Change `LC2_TEXTURE_PAIR` into joinable **initialize/materialize/update/delete** events (default off). Include `lc2_bc_pending`, `t2_page.deferred`, `packaged_lazy`, zero-storage aliases and the actual `zero_texture_storage_state(t)` owner token. Explicitly separate `no-current-storage-by-design`, `no-match-unknown`, `GL-error`, `declared` and `actual-driver-byte-unknown`. Record admitted-but-pending charges separately. Do not add heavy per-draw printing.
6. Add `LC2_STORAGE_SNAPSHOT` from the **same critical-section/epoch** for all current live classes, including the charged-texture budget, zero-view alias count, depth/RB, buffers, render-target images and CPU decoder staging, with a joined-count and unjoined-count. A snapshot split across unsynchronized worker threads must carry begin/end monotonic timestamps and be labeled *approximate*. Reconcile per-object, not cumulative last-event versus last-interval totals.
7. Keep observer-off as runtime default and ensure its extra memory/time cost is measured with a same-ELF **probe-off/probe-on** menu comparison; bounded diagnostic logs belong in owner evidence, while proprietary texture buffers, full logs and captures stay private.

**Host red/green fixture matrix:** (a) `TexImage(level0 4 MiB) -> TexImage(level0 1 MiB)` yields current 1 MiB plus old pending until proven retired, not 5 MiB current; (b) level0+level1 sums distinct levels; (c) `TexSubImage` changes write epoch but not size; (d) two GL names/contexts and two NVN views of one storage; (e) delete+same GLuint reuse (including 24 cycles); (f) >512 create/delete cycles with bounded index reclamation; (g) >128 pairs with explicit loss/incomplete, never silent omission; (h) missing/late shader reader and fence; (i) failed/partial allocation and rollback; (j) 2D/cube, MSAA, sRGB, float, BC/ETC block alignment; (k) UINT64 overflow; (l) deferred/no-live expected category. Reuse the existing C11 host extraction pattern in `tools/test_life_events.py`.

**PASS:** exact per-generation live objects and no phantom duplicate accounting in synthetic tests; same-run multi-base snapshot with unresolved counts enumerated; no regression of normal launch or observer-off behavior. **STOP:** an ambiguous storage/share-group generation used to free real memory, unreported dropped records, unexpected GL error, changed render pixels or changed default policy. This PR **does not itself save memory**.

### 72.3. PR M2A-5 — Join the earliest high-water window to resource intents (P0; low-overhead diagnostic)

**Files:** overlay `native/lc2_menu_ledger.h`, `native/nvn_textures.h`, `native/t2_guest_memory.h`, `native/memory.h`, `native/loader.c`; `tools/load_metrics.py`, `tools/ledger_bases.py`, `tools/proc_metrics.py`, `tools/device_principal_test.py` and tests.

1. Emit timestamped landmarks **before guest mmap/alias**, after source-image mapping, first EGL context, first GL allocation, each **large** (> configurable validated threshold) storage intent/commit, first present, frame8, frame16, stop and cleanup. Report both `CLOCK_MONOTONIC` time and process/run identity. The last safe point should be written before a GL OOM-prone call, not only afterwards.
2. Collect `/proc/self/status` memory classes, `/proc/self/smaps_rollup` with read duration and attribution limitations, `/proc/meminfo` `MemAvailable/CmaFree/Cached/SwapFree`, memory PSI `/proc/pressure/memory` if available, guest-heap alias commits, compressed/staged CPU pages and the live texture/renderbuffer ledger **in one short bracketed window**. Avoid large `smaps`/Mali dumps in the hot frame. If `/proc/pressure/memory` is absent, report unsupported; no fabricated zero.
3. Optional read-only Mali driver metadata: capture context ID+generation and the exact same monotonic sample bracket. First derive the `gpu_memory` **units/semantics on this firmware** from kernel source or a *safe small isolated allocation/read/delete* fixture. The observed raw 84900 and VA descriptors must otherwise remain unlabeled units; descriptor sums can overlap and must not be added to VmRSS.
4. Implement an offline phase-window report with `t_start_ns, t_end_ns, run_uuid, first_frame_serial, observed_max_vs_sampled_max`, plus `alloc_intent_bytes, committed_declared_bytes, pending_gpu_retire_bytes, guest_alias_present_bytes, compressed_guest_bytes, private_file_rss_unknown`. Do not subtract counters from unmatched instants, other boots or different ELF hashes.
5. Clarify the `device_principal_test.py` prelaunch snapshots: label any `before.frame/menu_events/stops` parsed from pre-existing `latest.log` as `unowned_prior_log` and exclude them from the new run result. Add a fixture with `before.frame=12`, new run `after.frame=8` proving no accidental inference of 12 frames. Preserve the current run UUID/PID/starttime/ELF matching and explicit cleanup receipts.

**PASS:** can rank the biggest *specific* pre-first-present allocation-intents and memory-state changes without claiming that MemAvailable deltas are exclusive object sizes, including a clear “not attributable yet” bucket. **STOP:** sampler perturbs time/memory substantially, intervals lack identity, real Mali units remain unverified yet are reported as bytes.

### 72.4. PR M2B-1 — Pre-allocation failure containment (P0; safety, NOT speed)

Keep §71.3's admission design but implement it **before** doing dangerous memory-saving experiments. Use already implemented checked `native/lc2_gl_storage.h` format/mip calculation, augmented for actual host upload format, driver alignment uncertainty, peak CPU staging and realized samples. At **every** risky `glTexImage2D`, large BC first-use upload, depth renderbuffer and re-spec path:

```text
validate descriptor/source generation/format -> checked requested peak
  -> read current host floor/CMA + own committed/pending ledger
  -> if admission unsafe: emit T2_STORAGE_ADMISSION; NO GL call
  -> reserve pending intent -> GL call -> glGetError/result receipt
  -> commit new logical generation OR rollback uncommitted intent
  -> old backing retires only after proven readers and GPU completion
```

Make the normal `T2_MEMORY_FLOOR_MIB=96`, budget `T2_TEXTURE_BUDGET_MIB=300`, strict GL, and conservative unknown handling non-negotiable. Do not confuse freeing decoded CPU staging with immediately releasing Mali pages. Test allocation-failure, GL-error, rollback, partial-prefix, unknown physical overhead, command-queue in-flight readers, SIGKILL taxonomy and CPU sysfs value/**mode** restoration, including a separate forced-termination cleanup arm. Typed refusal is a **safer stop**; do not mark it as gameplay progress or memory saved.

### 72.5. PR M3 — Deliver real menu headroom; use one reversible A/B per resource class (P0)

**This is the first PR family capable of changing the PLAYABILITY outcome.** The §71 sequence made complete all-class lifetime instrumentation a dependency of all optimization; refine that: a **specific** owner/storage path can be optimized once its own generations/source writes/readers are proven, while unrelated unknown classes stay instrumented/refused. Do not block a safe targeted A/B on perfect accounting of every hypothetical EGL class, but never speculate about object lifetime.

**M3-A, remove *temporary* duplicate CPU allocations first (lossless candidate).** In overlay `native/nvn_textures.h`, `native/zero_bc.h`, `native/zero_bc_layout.h`, `native/lc2_fileback.h` and the guest alias paths, trace for each large BC upload: immutable guest source -> optional snapshot/mirror -> decode scratch -> packed staging -> `glTexImage2D` -> end-of-call lifetime. Measure peak simultaneous *actual* CPU allocations (not sum of cumulative malloc calls), and note the existing stripe/deferred/direct-copy optimizations already present. For one owner whose source and destination do not overlap and whose read-generation is pinned, try a **bounded tile/stripe buffer** or lifetime shortening without a second whole-RGBA allocation. Keep exact block edge, swizzle, pitch, alpha, sRGB and mip semantics; preserve source COW and pinned I/O/gzram fault safety. Do not call `madvise` on live guest/GL pages. Before/after: peak host RSS, guest VmSwap/major faults, MemAvailable and CMA at matched phase, CRC/pixel equivalence, page-fault/stall time. Save **temporary peak** rather than just “allocator calls” counts.

**M3-B, static sampled GPU textures into device-native ETC2/EAC / optional ASTC (conditional; usually lossy).** Historical BC expansion is a dominant *declared* basis mismatch: examples [build248](../evidence/texture-pair-20261022-01/README.md) include id61 800×1500: 614,400 B guest charge versus 4,800,000 B decoded GL. Use the per-owner *live byte* ranking, not the biggest compression ratio, to choose a texture; ideally group of samples large enough for a measurable headroom improvement. Confirm actual GLES3 context/version and format support; ETC2/EAC are GLES3 core features per [Khronos](https://www.khronos.org/news/press/khronos-releases-opengl-es-3.0-specification), whereas ASTC depends on actual exposed support. Build an **owner-private, content-addressed offline** transcode side cache tied to original source-image hash, NVN format, dimensions/mips, gamma/alpha and write epoch. `GL_COMPRESSED_RGBA8_ETC2_EAC` uses 8 bpp (16 B per 4×4), versus 32 bpp for RGBA8, so nominal payload of an eligible 4-channel texture may fall ~75%; this is **not** an on-device Mali physical-memory saving claim. Upload with `glCompressedTexImage2D`/verified image size, one immutable storage generation and valid sampler completeness. Prove no runtime re-writes/FBO attachments for that source; refuse mutable or unknown inputs. Check alpha gradients, UI fonts, bleeding, normal-map handling and LOD at the *game's actual* ROI, and compare deterministic same-scene KMS captures against the original. ETC2/ASTC transcode can change pixels: default remains original BC→RGBA until explicitly approved. An offline encoder's intermediate RGBA buffer must never be resident in the final runtime. Measure physical memory/peak/stalls as well as image quality; reject if cache I/O/page faults erase the benefit.

**M3-C, release provably dead backing generations (lossless only if truly unused).** From M2A's last-reader evidence, pick a texture that has `destroy` and no alias views, sampler, render-target use or pending GPU work; issue the GL delete at the correct context, then compare *physical* effect after a verified fence and enough controlled observation. The 24 reused numeric names and disappearing/reappearing driver virtual addresses are **not** retirement evidence. Add unit tests for pending draw, shared FBO, texture-view alias, context loss, same-name recycled object, and delayed GPU command completion. If a first-world shader later reads the image, reject.

**M3-D, scoped 1080p internal target reduction (quality-affecting/conditional).** Actual 1280×720 panel is already correct; three 1080p colour targets and one matching depth target are hard-coded by the guest (see [origin](1080p-origin.md)). All four have 31.64 MiB nominal original payload versus 14.06 MiB at 720p, hence **17.58 MiB maximum nominal** difference. Existing `ZERO_RENDER_SCALE=2` has a historical neutral/negative performance result; never present this as a proven FPS win. It **cannot alone** be relied upon to clear the present low-floor shortfall or an unknown larger first-world load. If quality trade-off is approved, test one owner target first with exact/tolerant ROI image comparison, UV/scissor/stencil/depth/viewport/bloom semantics, intermediate dual-storage peak and *driver* memory. Keep off by default and revert on mismatch.

**M3-E, guest memory/page pressure (only if measured).** Earlier Loading arms saw hundreds of MiB of process swap, major faults and expensive cold-compression paths; fresh pre-frame data must establish whether the same owner class is responsible in build248. Use a controlled `cold_ms` matrix with identical ELF/env/scene/thermal state, explicit `CLOCK_THREAD_CPUTIME_ID` for actual thread CPU and wall samples for page waits; verify I/O pins and zero-copy guards. Examine proven-dead guest/source mappings for scoped `madvise`/fileback or lazy mapping **only** after source write/lifetime proof. Do not raise guest quota or disable physical floor, increase swap as a purported GPU-residency fix, kill MainUI, reduce CMA protection, or promote `glFlush` to a completion fence.

**Measurement rule for M3:** baseline and experiment on **the same scene/phase and verified installed binary**, with only one feature toggle difference, repeat at least three times, record prelaunch/first-GL/first-present/max-pressure/stop and true kernel OOM classification, plus capture provenance and visual quality. Proposed provisional **engineering headroom gate**: sustain at least the normal **96 MiB** floor for a no-input 120-second menu run **and target an additional 64 MiB margin** for scene loading; 160 MiB is a planning target, **not an evidenced game requirement**. No number of MB saved in a screenshot-independent counter can replace a safely rendered real menu. If the menu still cannot hold above the release floor, stop before New Game and change a **different measured dominant storage class**.

### 72.6. PR N5/W0/W1 — First-world correctness test after memory passes (P0)

1. With the M3 winner enabled and its rollback ready, require a live KMS menu capture, verified UUID/boot/PID/starttime/ELF, stable floor + CMA, and no kernel/Mali OOM; then run the existing **persistent owned** N4 navigator. Confirm each TITLE → MAIN_MENU → NEWGAME_CONFIG → CONTROLS → LOADING transition only on **two newer distinct owned present serials** and the correct page fingerprint; allow **one explicit** press and a release ACK at a time. Time out/refuse rather than blind auto-retries. Do not misclassify a clean SpruceOS capture as game.
2. During Loading, create a low-overhead **forward-progress state tuple** (last owned present serial, first/last RomFS asset completion, shader instance create/link/**draw**, guest scene-activation markers if independently located, GL memory generation, actual NVN draw/readback, audio service results and last forward-progress timestamp). If frames advance but scene state stalls, symbolize the **same-run** guest ARM64 PC/Unity PlayerLoop; if GPU allocations stop making progress, trace the exact owner-intent; if images render but world remains invisible, inspect FBO/MRT chains. A longer timeout is **not** evidence of progress.
3. Specifically prove entry44's vertex and entry45's **four-MRT fragment** actually execute with their expected bindings, attachment formats and downstream reads. `link=on-native-pair-draw` describes linking only; a correct first-world display needs KMS captures while the game PID is alive, plus GL status and no TEST substitution for any unverified shader. Preserve append-only shader catalogue identity and original rounded-half semantics.
4. **W0 acceptance:** independent in-game KMS evidence of an actual room, a controlled character move, changed world position, consistent input press/release and valid rendering. **W1 acceptance:** interaction/dialogue/inventory, one scene transition, audible sound, save → exit → cold relaunch → load preserving the same state, clean Spruce supervisor/CPU restore.
5. The actor/controller provenance must be labeled accurately: injected evdev input validates the event mapping and scene behavior but does **not** prove physical human gamepad reliability. Physically test controls separately before saying playable. No unowned screenshot/“nonblack” receipt qualifies.

### 72.7. PR F1 — Actual gameplay throughput, CPU and GPU optimization (after W0, not before)

Old menu/Loading records (`docs/fps-baseline-2026-10-20.md`) show ~0.5–0.6 seconds per present and one diagnostic split near **249.6 ms replay + 316.4 ms guest gap**. These are neither steady gameplay nor a bound on the first room. Do not attribute all guest gap to CPU, all replay to Mali, or extrapolate a claimed expected FPS from a single stopped run.

- **Capture a quiet game-state baseline:** pin a reproducible 60–120 s moving/idle scene, identical camera/action path, governor, thermal and memory conditions; 3 runs. Record frame serials, frame wall-period P50/P95/P99, missed/duplicate presents, per-thread CPU via `CLOCK_THREAD_CPUTIME_ID`, CPU wait/off-CPU, signal/SVC dispatch, audio service calls, guest compressor/faults, GL replay, `glFinish`/fence waits, GPU clock/utilization only if truthful driver counters exist. Separate Loading from steady gameplay; capture both.
- **If actual thread CPU dominates**, symbolize owned ARM64 PCs (correct NSO base + build) and separate game IL2CPP PlayerLoop, service/IPC mutex, audio polling, gzip/guest zram, texture decode and draw preparation. Retired C1 cost verdicts are **invalid**, per [C0](c0-profiler-audit.md); use the repaired all-thread/tail collector, not sample frequency as CPU percentage. Optimize only the largest validated call class; confirm function and ordering semantics.
- **If render submit dominates**, profile `native/nvn_render.h` UBO RGBA32F cbuf uploads, source/generation-aware change skipping, `glTexSubImage2D` vs large padded 1024×1 rows, redundant state binds and framebuffer transitions. The earlier `LC2_CBUF_SUBIMAGE` A/B did **not** prove a speed gain. Add one change at a time and validate GL correctness and memory impact.
- **If fill/driver completion dominates**, after image equivalence test targeted RT resolution/FX, shader overdraw, MRT attachment load/store and tile reuse. Never substitute `glFlush` for a real GPU-completion requirement or skip shader work that controls world visuals.
- **If page faults dominate**, solve working-set residency first; doing more GL calls per second while swapping harder will not reach 30 FPS. A true 30-FPS frame budget is **33.33 ms total**; intermediate milestones 5 → 10 → 15 → 20 → 30 measured FPS are iteration gates, not release promises.
- **30-FPS release gate:** full-frame P50 **and P95 ≤33.33 ms** in multiple real scenes, P99/stutter distribution reported, no sustained thermal throttling, correct audio/input/save, no OOM and no unbounded swap growth; do not rebrand 30 FPS for a splash/menu as gameplay.

### 72.8. Exact implementation/review order, commands and stop matrix

| Order | Change set (commit/PR) | Required proof | Abort/revert if |
|---:|---|---|---|
| 0, **done** | Build248 paired event diagnostic and owned launch cleanup | 117 pairs, 8 presents, floor95/96, 0 menu events; [owned report](../evidence/texture-pair-20261022-01/README.md) | Not gameplay; no performance win to claim |
| 1 | **M2A-4A:** live index by GL generation, level-aware storage replacement, bounded event loss | C11 test for name reuse, re-spec, >128 events and >512 cycles; observer OFF baseline unchanged | Missing generations counted as a known free / silent overwrite |
| 2 | **M2A-4B + M2A-5:** same-epoch per-resource joins, early guest mapping/GL landmarks and run-owned snapshots | A reproducible ranked first-present allocation report + explicit unresolved classes | Summing unmatched times or misleading `before.frame` from old log |
| 3 | **M2B-1:** pre-GL admission and transactional rollback, release floor96/cap300 | Typed safe stop before OOM + forced-exit cleanup fixture | A “fix” merely raises quota, swaps more or bypasses floor |
| 4 | **M3-A:** one peak CPU allocation/lifetime shortening A/B | Lower peak actual memory with byte-exact output/owner lifetime | Renderer/guest source altered or lost page pins |
| 5 | **M3-B / M3-C:** ONE confirmed dominant GPU texture/compression or retired resource A/B | Driver/headroom benefit, correct sampled texture semantics and exact owner | Image quality not approved, incomplete fence, new stutters |
| 6 | **M3-D/E** only if bottleneck attribution warrants | Scoped physical memory/quality and actual CPU+fault effect | Loss of UI/scene correctness, extra RSS, worsening swap |
| 7 | **N5 → W0 → W1** after sustained safe menu gate | Owned world capture, control, interactions, audio, cold save/load | Unknown scene, Loading loop, unsafe floor, GL error |
| 8 | **F1**, after first working room | 3× full-frame gameplay baseline and isolated bottleneck gains | Menu FPS mistakenly reported as world, missing P95/P99 or memory regressions |

**Host fast check (in an environment with native dependencies):**

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
# In the separately reconstructed baseline source root, from the port repo:
(cd "<verified-435-file-baseline>" && sha256sum -c "<port-repo>/tools/baseline-manifest.sha256")
# Build via the pinned container command already documented in ../README.md.
# A host fixture is not a driver/TSPS acceptance test.
```

**Device-run contract (each new numbered `evidence/` directory):** exact source commit/overlay SHA, original owner image/metadata identity, ELF/launcher/helper SHA, observer switches and unchanged baseline defaults, UUID/boot/PID/starttime and source of every frame serial, prelaunch CPU online values **and permissions**, one-factor feature change, first-GL/first-present/high-water timestamps with PSI availability status, CmaFree/SwapFree, full stop taxonomy (`TIME_LIMIT`, `T2_MEMORY_FLOOR`, `T2_STORAGE_ADMISSION`, budget stop, GL error, OOM SIGKILL, host kill), postcleanup MainUI/process/CPU/debugfs status, and a live game-pid-bound KMS capture receipt if any in-game picture is claimed. Label prelaunch stale logs and missing join rows as unknown. Committed evidence stays compact; raw logs, game assets and screenshots stay owner-private.

**Decision at this audit:** Continue the native AArch64 Horizon/NVN path; existing shader catalogue and menu progress make it the only demonstrated route. **First deliver a trustworthy bounded generation ledger and safe preallocation barrier, then spend engineering effort on a *measurable* memory-saving change rather than adding indefinite observation layers.** Running New Game repeatedly at <96 MiB or choosing further frame-rate tweaks before a first-world room is not productive. Evaluate REA/Windows-source work only as the separate, targeted §71.7 research branch, not a replacement for the current adapter.


---

## 73. Build249 evidence delta: close the exact T2 budget join, fix owner parsing, then reduce real memory (2026-10-22)

**Newer than §72.** Commit [a9f3e144](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/a9f3e14407b3), published concurrently with the §72 audit, implemented part of §72.2 before this roadmap update. Its owned [build249 report](../evidence/m2a-20261022-01/README.md) and [texture accounting update](tex-levels.md#build249-timestamped-storage-replay-2026-10-22) take precedence over §72's as-of-build248 completion labels. §72's detailed test and optimization design still applies **only to the remaining unimplemented portions**. No new source/device work was performed while drafting §73.

**Current installed build:** build249 ELF SHA256 `0e62238c69c36e9fbd49669d5c062c0449ee56c2624b44acf37461c206cd588b`, owned run `cc013fc9-af26-4e2f-84b6-38e5c7af35dd`. `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL, `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`. The run has **3** owned presentation records, zero menu events, and a typed `T2_MEMORY_FLOOR` stop with **68 MiB available** (pre-stop exact sample `70304 KiB`; no identified kernel OOM). **NOT PLAYABLE**; this is not a menu FPS or world result. Its separate after-run KMS image shows SpruceOS, not the game.

### 73.1. What build249 actually closed and did not close

| Gate | Status | Precise receipt and next decision |
|---|---|---|
| Per-event monotonic journal and generation tags | **PARTIALLY DONE** | 116 `LC2_TEXTURE_PAIR` events, 163 `LC2_GL_STORAGE_EVENT` records (50 extends), 24 `LC2_GL_STORAGE_DELETE`; no reported bounded-event overflow in this short run. The tags are meaningful for the observed GL storage, but share group, last GPU reader/completion, same-mip replacement and exhaustive resource classes are not yet fully implemented. |
| GL live-at-floor reconstruction | **DONE for this observed journal**, not physical bytes | Offline replay to floor timestamp reconstructs 89 records: **87 texture records / 224,539,952 B** and **2 renderbuffers / 11,980,800 B**. Total **236,520,752 B** exactly equals `LC2_LIFE_SUMMARY retained`. This supports the journal's internal arithmetic, **not** unique physical backing or completed GPU reclamation. |
| Direct stop-path live snapshot | **BLOCKED** | `pthread_mutex_trylock(&nvn_gl_completion.mutex)` returned `EBUSY=16`, so `LC2_TEXTURE_LIVE_SET` was **not produced**. Do not block the floor observer on GL or call ordinary non-async-signal-safe functions from a signal context without proving the exact caller. Prefer offline replay with bounded pre-recorded events. |
| Per-object T2 charged-budget accounting | **OPEN; next top telemetry task** | The budget add/sub/retirement events lack a timestamped owner/storage-generation trail. The first-present `budget-live=112,325,632 B` is at another timestamp; no exact at-floor per-NVN reconciliation exists. The GL storage report must not be subtracted from this unrelated sampled budget. |
| Safe memory headroom | **FAIL** | First-present `119140 KiB` available; pre-stop `70304 KiB` available approximately 0.258 seconds later by their reported monotonic clocks: a **48,836 KiB ≈47.69 MiB** drop over the bracket. Two samples do not identify which resource consumed it. Polling can observe the failure late; the earliest high-risk allocations need source-checked admission. |
| Runtime/cleanup classification | **CORRECTION REQUIRED** | A collection parser searched the unanchored substring `STOP status=` and misread `LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable` as a second stop; the **sole** owned runtime stop was `T2_MEMORY_FLOOR`. Prelaunch `before.frame=8` belonged to the previous log generation, **not** build249's 3 presents. `run-outcome-receipt.json` records these differences. |
| Memory PSI | **UNAVAILABLE on target** | `/proc/pressure/memory` was absent; retain `null/unsupported`, not 0. Do not require PSI for subsequent safe tests. |

### 73.2. PR E1 — Fix the false STOP and stale frame parser BEFORE the next evidence arm (P0, small)

**Files:** inspect `tools/device_principal_test.py`, `tools/run_identity.py`, `tools/load_metrics.py`, `tools/exit_outcome.py`, and whatever helper builds `before.json`/`cleanup.json`; then add focused test cases to `tools/test_device_principal_hard_stop.py`, `tools/test_exit_outcome.py`, and `tools/test_load_metrics.py` (or the actual existing test file; do not create duplicates unnecessarily).

1. Parse only **complete owned lines**, not substring matches: `^STOP status=([A-Z0-9_]+)(?:[ \t].*)?$` with `re.MULTILINE`, after validating the current run header and run/inode generation. Text containing `LC2_MENU_LEDGER_PRESTOP status=...` must not match. If a STOP code format differs, add precisely validated alternatives, not permissive fuzzy matching.
2. Qualify every `NVN_PRESENT_PIXELS`, `LC2_MENU_EVENT`, and STOP line by the new UUID/boot/PID/starttime/ELF and **log generation window**. The preflight `before` snapshot may retain an `unowned_prior_log` diagnostic field, but must not imply those frames/stops belong to this launch. Stop taxonomy should be driven by **new run lines only**, including explicitly distinguishable `host_terminated`, `OOM_SIGKILL`, `GL_ERROR`, `T2_STORAGE_ADMISSION` and normal typed runtime stop.
3. Use the build249 regression fixture: prior log eight presents; new owned run three presents and a `LC2_MENU_LEDGER_PRESTOP status=gl-lock-unavailable` line followed by one `STOP status=T2_MEMORY_FLOOR`. Assert **present=3, stops=[T2_MEMORY_FLOOR]** and no phantom second stop, even if log tails/framing are split across reads. Add tests for prior PID reuse, short/partial final line and foreign UUID.
4. Verify the correction against the existing small receipts without mutating or reinterpreting raw owner-private log bytes; publish a *new* fixture/result with distinct provenance. Don't “fix” archived reports by altering their original primary evidence.

**PASS:** exact owned-frame and stop taxonomy; cleanup process/CPU values **and sysfs permission modes** unchanged. **STOP:** any cross-run line is silently attributed to a current process. This repairs evidence, not RAM or FPS.

### 73.3. PR E2 — Timestamped per-object texture-budget lifecycle and nonblocking floor receipt (P0, critical)

**Files:** actual T2 texture budget owner implementation in the separately verified upstream source; overlay `native/nvn_textures.h`, `native/lc2_menu_ledger.h`, `native/lc2_life_events.h`; `tools/ledger_bases.py` and a new narrow reducer/test fixture. In the reconstructed baseline, **locate callers first** rather than assuming `t2_texture_budget_sub()` name exists:

```sh
grep -RnsE 't2_texture_budget_(add|sub|release|live_bytes)|t2_budget_bytes' \
  '<verified-baseline>/native' | head -100
grep -nE 't2_texture_budget_(add|sub|release)|t2_budget_bytes' runtime/lamentum-adapter.patch
```

1. Establish the exact boundary where an NVN texture owner is **charged**, **recharged**, **deferred**, **materialized**, **respecified**, **unlinked** and **released**. Only emit `LC2_BUDGET_EVENT` **after** a successful accounting transition (or a clearly marked attempted transition), with `CLOCK_MONOTONIC` ns, the same run UUID, per-NVN ID, source owner generation, charge delta, live-after **if safely obtained**, phase, outcome and provenance. Track guest/compressed bytes and decoded GL bytes as different fields.
2. Add signed overflow-safe arithmetic for the offline reducer; recompute `budget_live = initial_live + sum(successful_adds) - sum(successful_retires)` through the same floor timestamp as `LC2_GL_STORAGE_EVENT`. Handle object ID reuse and alias owner changes by generation, not name or old pointer. A direct sample obtained earlier must not be substituted for the stop-time value. Unknown/missed events = `INCOMPLETE`, not an exact zero residual.
3. Preserve lock ordering. The build249 floor `trylock` returned EBUSY; **do not block the 250-ms watcher** on GL to force a snapshot. Prefer a separate, immutable, preallocated and bounded budget journal with explicit sequence and overflow counts that can be replayed offline, plus an independently safe counter snapshot if the budget mutex itself is not contended. Distinguish monotonic wall epoch, event publication epoch and completed log writes. No `glFinish` or heavy log I/O added to normal draw path.
4. Implement a matched *same-time* join: for each NVN storage generation, show owner charge and decoded GL subresource live sum; report shared aliases once and deferred `no-live-gl-storage` separately. In the emitted table, label `declared_gl_bytes`, `guest_bytes`, `budget_charge_bytes`, `unknown_driver_physical` explicitly. The exact proof point is the build249 floor timestamp `6558723780460` **only within that archived run**; a new build requires its own newly recorded timestamp.
5. Test: add/remove/reuse same NVN object ID; positive/zero-charge BC deferral; later first materialization; old/new storage generations; multiple views of one GL backing; respec and failed admission; concurrent budget add/decrement near watcher; event-cap overflow; missing T2 release; overflow/underflow arithmetic; reordered line arrival and truncated tail. The test reducer should *refuse to declare reconciliation* until every relevant transition and its run identity has been observed.

**PASS:** same-owned-run replay to the floor timestamp exactly accounts for **per-generation charged bytes** without guessing, then reports why compressed/budget/current GL totals differ. **STOP:** a forced unsafe lock, a fabricated matching-time number, silent dropped events or evidence overwritten by a newer launch. This is still a **measurement/consistency milestone**, not saved device RAM.

### 73.4. PR E3 — Correct remaining generation and capacity traps (P0/P1; scoped follow-up)

Build249 now tags storage generations and timestamps; do **not** rebuild that component. Instead review the actual `lc2_life_events_storage()` behavior: it **still adds** bytes for each storage call on a live GL name, under the assumption that every second `glTexImage2D` means a *new* mip; same-face/mip replacement is not explicitly separated. The recorded `subresource` is a good starting point but no per-subresource current byte array/key currently enforces replacement. The `LC2_LIFE_EVENT_CAP=512` lookup still allocates new entries with `if (!entry.name)` while deletion leaves `name` intact; this can cause diagnostic capacity exhaustion in longer scenes even though the device saw no overflow in this short run.

- Implement `(context/share-group, object-generation, target, face, mip)` current-storage slot and `storage_generation`; make `TexImage` same-subresource update **replace**, `TexSubImage` content-write only, distinct mips **add**, and `glBufferData` replace. Track deleted but potentially GPU-in-flight backing separately; no speculative physical release.
- Reclaim **observation index** entries only with non-conflicting generations and proper event ordering while keeping the historical journal immutable. A bounded ring with `lost-events` + `complete=false` is preferable to silent overwrite; do not grow C buffers without memory-cost measurements.
- Add C11 fixtures for 24 name reuses, >512 create/delete cycles, a 128th/129th pair, same-level redefinition, failed GL call, multiple context groups and mip/cube layers. Match `LC2_LIFE_SUMMARY` with the event-replay live set, as build249 already achieved for its supported event sequence.
- **Do not claim build249's replay is wrong:** it exactly matched its own summary; this PR protects future or unobserved call patterns, not a demonstrated mismatch. Maintain unknown share-group, GPU-completion and physical-driver status rather than inventing safe free semantics.

**PASS:** host generation/subresource cases and a complete owner-qualified bounded device journal. **STOP:** any source assumption about automatic GPU retirement or format semantics.

### 73.5. PR M3-now — Prioritize one actual pre-frame / first-frames memory saving (P0, in parallel with E2)

The build249 first-present-to-stop interval is **extremely short** (~258 ms from the recorded monotonic stamps). A 250-ms periodic watchdog can cross the 96-MiB floor substantially between checks. Implement §72.4/§71.3 **pre-GL admission** at the actual large upload-intent site with correct declared size, peak temporary staging and a conservative physical uncertainty margin; refuse with typed `T2_STORAGE_ADMISSION` **before** driver allocation. This makes failures safer, but *does not create memory capacity*. Do not lower the floor, expand virtual quota, or remove Spruce UI as a “solution.”

In parallel, choose **one currently proven first-present owner** for a reversible, allocation-reducing experiment from §72.5. Selection criteria: timestamp precedes/overlaps the sharp available-memory drop, its current backing is large and provably nonaliased in the relevant accounting basis, original image and source-write generations are known, and a read/consumer semantic can be verified. Rank:

1. **First:** eliminate simultaneous **temporary decoded/staging CPU copies** with bounded BC stripes / direct source reads and verified I/O pins. Note that earlier stripe/direct-copy/fileback work already exists; extend an actual uncovered path, do not reinstall a previous optimization. Compare instantaneous RSS and system available, not historical cumulative malloc bytes.
2. **Next:** for **immutable and sampled-only** texture owners, evaluate original decoded-RGBA versus a private, preencoded ETC2/EAC (or device-verified ASTC) side-cache. Verify alpha/sRGB/mips/LOD, exact source hash and content-write epoch; use a same-scene KMS image ROI plus quantitative memory and stall effects; **lossy transcoding requires explicit image-quality acceptance** and never becomes default blindly. Test driver extensions in the *runtime* context, not by chipset assumption.
3. **Alternatively:** safe texture backing retirement only with last-reader and GPU-completion proof. An observed `glDeleteTextures` and recycled numeric name are insufficient.
4. **Only when justified:** a one-target 1080→720 internal composition experiment (maximum 17.58 MiB **nominal** saving across all four targets; cannot alone fix the earlier >40MiB deficits), or guest page reclamation after proven dead/COW-safe owner lifetime.

**Physical menu memory acceptance gate:** a live in-game (not Spruce cleanup) menu KMS capture with correct run identity, repeatable no-input **120-second** stability at or above the normal 96-MiB floor and sufficient CMA margin, and **planning target** an extra 64 MiB before New Game (160 MiB total is a *design target*, not proven required by the game's first world). Use at least 3 controlled A/B runs at exact scene/ELF, one feature changed at a time, with zero kernel OOM, no GL errors and valid CPU/mode/launcher cleanup. Do **not** run the New Game path when the memory gate fails.

### 73.6. Next execution order and stop/go policy

| Priority | Work | Current state | Gate |
|---:|---|---|---|
| P0.1 | **E1 owned log parser** (false STOP; stale `before.frame`) | **Open**; build249 receipt manually corrects both | Single verified real stop, exactly 3 owned presents in archived build249 fixture |
| P0.2 | **E2 per-owner budget add/sub journal + same-time replay** | **Open**; GL journal now validated | Distinguish each live generation's charged/guest/decoded quantities at **same timestamp** |
| P0.3 | **M2B early GL admission** | **Open** | Typed rejection before unsafe memory call; 96 floor / 300 cap unchanged |
| P0.4 | **M3 targeted CPU or device-native compressed storage** | **Open** | Measurable retained headroom and visual/source correctness; not just a smaller budget charge |
| P1.1 | **E3 subresource overwrite + bounded-index recycling** | **Partially instrumented** | No false live count or silent truncation in long-lived scene |
| P1.2 | **N5/W0** owned navigation, first actual world image and movement | **Blocked by memory gate** | KMS while correct game PID lives + valid player movement |
| P1.3 | **W1** real controller/audio/interact/save/cold load | **Blocked by W0** | Reproducible playable loop |
| P2 | **F1** quiet multi-scene profiling toward 30 FPS | **Blocked by W0** | Whole-frame P50/P95 ≤33.33 ms, P99 documented, safe memory and correct gameplay |

**Do not over-read build249**: 89 GL records matching the final 236,520,752-B summary are a useful **internal accounting consistency check**; they do not prove that many unique device-resident bytes exist, a GPU leak, or any VRAM savings. At 68 MiB available the port still cannot safely approach New Game, and only an observed memory reduction plus a verified first-world run changes playability. §72 remains the detailed how-to for the deeper M3/N5/W0/F1 tests; §73 is the **current status and next implementation queue**.

---

## 74. Build250 per-object budget and GL-storage replay; memory gate remains open (2026-10-22)

**Newer than §73.** Build250 adds timestamped T2 budget add/sub events with NVN texture IDs, a nonblocking budget snapshot at the floor, and run-scoped frame/menu/stop parsing. Those runtime/parser changes and their tests were published in commit `3e71c50`; this follow-up adds `tools/ledger_bases.py:replay_texture_budget` and its synthetic C/Python fixtures. The owned build250 run and compact receipts are in [evidence/m2a-budget-20261022-01](../evidence/m2a-budget-20261022-01/README.md). The prior build249 run and §73 remain historical.

**STATUS: NOT PLAYABLE; no gameplay FPS.** Build250 ELF SHA-256 `fd83556cd52776f4371a1644e9d013cfcb317275d14e907c331f8f2ec7cbd74d`; run `40d57167-d5b1-4071-9bdf-a3b2dd028a92`; floor96, cap300, strict GL, no game input. It produced **5** owned presentation records, **0** menu events, then `STOP status=T2_MEMORY_FLOOR` at **95 MiB vs floor96**. Exact `MemAvailable=97580 KiB`, `SwapFree=1988100 KiB`; prelaunch SwapFree was `2034520 KiB`, so the no-swap target is not met. OOM evidence is empty. First-present recorded `MemAvailable=144596 KiB`, `CmaFree=8220 KiB`, budget-live `112325632 B`.

### 74.1. Per-object budget replay and run-scoped parser result

The opt-in journal emitted 141 T2 budget events: 117 adds (`116851712 B`) and 24 subtracts (`1572864 B`), zero overflow. At `budget-sample-t-ns=8524495216977`, the nonblocking snapshot reports `115278848 B` live across 93 IDs. The sample is 13208 ns after the memory-floor check, with **no** budget or GL-storage event in the bracket. The reducer matches the snapshot, and for every live ID the replayed charge equals its latest pair charge; the aggregate live pair guest and charge payloads both equal `115278848 B`, with zero mismatch/missing pair.

Three live charged IDs (`46`, `51`, `52`) have no current GL-storage record and are explicitly labeled `no-live-gl-storage`; no live GL owner lacks a budget owner. Replaying the timestamped GL storage/deletes to the same sample yields 90 records: 88 textures / `232834352 B` and 2 renderbuffers / `11980800 B`, total `244815152 B`. It matches `LC2_LIFE_SUMMARY` exactly; 164 storage events, 24 deletes, zero event overflow. The direct live-pair snapshot still missed the GL mutex (`EBUSY=16`), so this is bounded journal replay, not a forced lock or physical Mali measurement.

The stop parser now accepts only complete line-start `STOP status=` records, and snapshot counters are scoped to the last owned run UUID. The build250 harness receipt reports only `T2_MEMORY_FLOOR`; prelaunch fields identify the previous log UUID rather than attributing its 3 frames to the new run. `/proc/pressure/memory` remains unavailable (`null`). The host suite passed **280 tests**; the pinned target-compatible build and AArch64/GLIBC checks passed.

### 74.2. What remains open

This closes E1 parsing for the build250 arm and validates the E2 budget/GL-storage arithmetic for this observed **no-alias** run. It does not yet validate ID reuse, shared backing, subresource replacement, all storage classes, share-group identity, last-reader/fence completion, or physical residency; E3 remains open. No measured device RAM reduction was made. The run consumed swap and still stops before the menu, so do not enter New Game.

**Next: §73.5 M3-now.** Source-audit one first-present, quality-neutral CPU staging/decode path and choose a reversible candidate from that evidence. Keep floor96/cap300/strict GL. Lossy texture transcoding or render-resolution changes still require explicit quality acceptance; the no-swap target, menu gate, first world, sound, saves, and >30 gameplay FPS are unmet.

---

## 75. M3-A BC3 medium-width stripe staging candidate; build251 device A/B pending (2026-10-22)

**Candidate from build250 run `40d57167-d5b1-4071-9bdf-a3b2dd028a92`.** The owned log has a pre-first-present BC3 texture `id=105`, `1920x1080`, format `0x44`, unaliased (`storage-owner=105`, `alias-parent=0`). Its refresh path logged `ZERO_TEXTURE_FLUSH_UPLOADED`; no `LC2_BC_STRIPED_UPLOAD` occurred. In the current source, both initialization and refresh stripe only when width exceeds 4096, so this 1920-wide owner takes the full decode path.

For this owner, the full path simultaneously requests an `8294400`-byte RGBA buffer and a `2073600`-byte linear BC buffer (`10368000` B). Existing 128-row stripes request a `983040`-byte RGBA buffer plus a `245760`-byte linear block buffer (`1228800` B): a source-derived requested-scratch reduction of `9139200` B per upload. These are overlapping `malloc` request sizes from source, **not** measured RSS, system-memory savings, or Mali residency.

Build251 adds `zero_bc_should_stripe()` to the existing helper and uses it at both initialization and refresh. Existing `width>4096` behavior is unchanged; `LC2_BC_STRIPE_MEDIUM=1` opts in only for non-scaled BC widths 1024–4096. The launcher does not set the flag. Full and striped logging expose the overlapping scratch requests. A self-authored C fixture checks policy boundaries and byte-for-byte BC3 decode equivalence for `1920x1080` tiled source and the existing partial-stripe case; the Python wrapper compiles it against the pinned adapter checkout. Host suite: **281 passed**. Runtime patch SHA-256 `4daa6db6bdd716520eb69b05b3c9d3325020e9d8ae9865955a633312736cfd74`; build251 is AArch64 ELF64, GLIBC requirements <=2.27, SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`.

**Not yet installed or device-tested.** Build250 remains the device baseline. The next gate is three alternating matched pairs (flag absent, then `LC2_BC_STRIPE_MEDIUM=1`) on the *same build251*, changing no other setting. Keep floor96/cap300/strict GL/no game input; do not enter New Game. Compare owned stage logs, first-present `MemAvailable`/`CmaFree`/`VmRSS`/`VmSwap`, `SwapFree`, presentation progress, GL errors, typed stops and cleanup. The baseline arm must show the full-stage record for id105 and no medium stripe; the candidate must show striped records for that owner. Stop and retain the default-off candidate if any run has a new GL error, image discrepancy, memory regression, or cleanup failure. Even a staging reduction is not a no-swap or >30-FPS result; source-write generation remains `untracked`, and no game pixels/FPS have been verified.


---

## 76. Build251 reassessment: evidence-led headroom, first playable scene, then real 30 FPS (2026-10-22)

**Latest review:** `main` at `6797f5f` (before this documentation-only update). **Authoritative detailed implementation plan:** [Build251 evidence and gameplay roadmap](build251-evidence-and-gameplay-roadmap.md), covering code sites, six-arm device A/B, memory-waterfall instrumentation, generation-safe storage accounting, GL admission, W0/W1 milestones, source-backed optimization options, host commands and fail/rollback rules. This §76 takes precedence over superseded "next" queues in earlier sections; §74 and §75 remain the device/candidate source-of-truth.

**Implemented / measured, not to repeat:**
- Build250 **device result**, owned run `40d57167`: five presentations, **zero menu events**, only `T2_MEMORY_FLOOR` at `97580 KiB` (~95 MiB, floor96), no confirmed OOM, and swap consumption. The 93 live T2 budget owners reconcile to `115278848 B` and the 90 replayed declared GL storage records to `244815152 B`. These are different bases, **not physical GPU memory**. Source: [owned build250 receipt](../evidence/m2a-budget-20261022-01/README.md) and [budget replay](../evidence/m2a-budget-20261022-01/budget-replay-receipt.json). E1 owner-frame/false-STOP parsing is fixed for this run and E2 run-local budget/GL event arithmetic is closed in the observed no-alias case.
- Build251 **host-only candidate**, ELF SHA `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`: `LC2_BC_STRIPE_MEDIUM=1` default OFF, host fixture passes, **281 tests**. 1920x1080 BC3 owner 105 has source-requested overlapping scratch reduction `10368000 -> 1228800 B` (~8.72 MiB), **not** measured resident memory; the full GL texture is unchanged. **No build251 device A/B or gameplay measurement yet.**
- Stop promoting unsupported conclusions from historical `newgame-20`, older `newgame-*`/Loading periods, GL driver VA reuse, TEST-only shader availability, or MainUI cleanup pixels to gameplay/FPS. This port remains **NOT PLAYABLE**.

**New prioritized exact PR queue (full procedures and validations in the linked plan):**

| Priority | PR | Required device/source gate |
| --- | --- | --- |
| P0-1 | **M3-A1**: alternate OFF/ON three times on **identical build251**, `LC2_BC_STRIPE_MEDIUM` only; retained floor96/cap300/strict GL | Owner-qualified stage records + KMS pixel parity, `MemAvailable`/CMA/RSS/swap timing, zero new GL errors; stop on unsafe pressure. Keep OFF if inconclusive. |
| P0-2 | **M3-B**: low-overhead, timestamped waterfall from launch -> GL alloc/decode -> first present -> stop; include process/system and source-generation identities | Find measured **instantaneous** peak owner and residual; do not equate 244.8 MB declared with physical residency. |
| P0-3 | **M2B-E3**: typed preallocation admission; correct same-subresource GL replacement, bounded deleted-slot reuse, aliases and journal completeness | No extra OOM, no silent overflow, correct generation/subresource host fixtures. Build250 accounting is **not** presumed broken. |
| P0-4 | **M3-C**: one data-selected headroom saving: duplicate CPU staging/coherent reuploads first; real ETC2/EAC/ASTC sidecache or one 1080p composition family only with image-quality approval; lifetime eviction only after fence | Measured no-swap/safe headroom and exact source/image semantics, not a lower logical budget number. |
| P0-5 | **W0**: >=120 s true in-game menu stability, normal floor96, safe CMA and stable swap, owned live KMS; **160 MiB is a design headroom target, not proof of necessity** | Three clean device runs and full Spruce/CPU restore **before** New Game. |
| P0-6 | **W1**: owned New Game -> world, rendered pixels, physical movement, interact/inventory/dialogue, audio and cold save/load | Correct playable loop on three independent runs, no test-shader/GL/memory failures. |
| P1 | **F1**: three >=60 s correct *world* scenarios with P50/P95/P99 latency and guest/GL/fault/thermal attribution | Scene-specific P95 <=33.33 ms and no visual, input, audio, save or memory regression. |

**New source audit edge case:** current `lc2_bc_upload_stripes` allocates `width*128*bpp` even for a mip with `height<128`, and `zero_bc_should_stripe` checks width but not total scratch benefit. Add compiled small/odd-mip geometry tests and later cap stripe scratch to actual rows or require a positive estimated saving **without mutating the pinned build251 baseline before its A/B**. The `lc2_life_events_storage` live-name "extend" branch still treats same-level redefinitions as additions, and the 512-entry table does not reuse deleted nonzero-name slots; these are **future/long-scene correctness risks**, not evidenced build250 mismatches. See the linked §2 and §5 for code-level instructions.

**Safety:** retain `T2_MEMORY_FLOOR_MIB=96` and `T2_TEXTURE_BUDGET_MIB=300`. Avoid New Game when W0 fails, lowering safety floors, unvalidated texture pageout, higher quotas, generic `ZERO_RENDER_SCALE=2` or treating `glFlush` as GPU completion. A memory-guarded STOP is not a performance improvement. Newly authored §76 and its detailed companion reflect a **documentation/source audit**, not a new hardware run.

## 77. Build251 M3-A1 device A/B: bounded staging signal, menu gate remains closed (2026-10-22)

**Evidence:** [six-arm report and compact receipts](../evidence/m3a-bcstripe-b251-01/README.md), [machine-readable A/B summary](../evidence/m3a-bcstripe-b251-01/ab-summary.json). This section supersedes §76's “no build251 device A/B yet” statement; §76 accurately described the state before these runs.

The installed AArch64 ELF was the same build251 hash `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78` in all six principal-flow no-input runs. OFF/ON/OFF/ON/OFF/ON changed only `LC2_BC_STRIPE_MEDIUM`; floor96, texture cap300 and strict GL stayed fixed. Every run stopped at `T2_MEMORY_FLOOR`, produced **zero menu events**, had no owned OOM evidence, no counted GL-error markers and `cleanup_errors=[]`.

- The target owner105 (`1920x1080`, BC3 `0x44`) used the full initialize/refresh path OFF (`10368000` requested overlapping scratch bytes/upload) and striped initialize/refresh ON (`1228800` bytes/upload, resolution preserved). Maximum known scratch request across the logs was `64800000` B OFF vs `2304000` B ON. These are requested CPU staging bounds, **not** measured physical memory.
- In all three matched first-present pairs, ON had higher `MemAvailable` and `SwapFree`, lower `VmRSS` and `VmSwap`. Paired deltas in KiB (ON−OFF): `MemAvailable +23520/+25936/+15572`, `SwapFree +8244/+37876/+7680`, `VmRSS -35652/-7240/-15488`, `VmSwap -3348/-31560/-8480`. The first-present T2 budget-live value was `112325632` B in all six runs.
- At the floor, ON retained `35640/42424/1368` KiB more `SwapFree`, but its `MemAvailable` delta was `+700/-5452/-1400` KiB; it was lower in two of three pairs. Median prelaunch-to-floor `SwapFree` loss was still `39880` KiB ON (vs `75524` KiB OFF), so this did **not** achieve no-swap operation or pass the menu safety gate. Different floor live-byte values and presentation counts show the stop phases were not identical; counts are not FPS.
- Budget/pair replay reconciled 2/6 runs. Four fail closed on an active budget owner without a texture-pair row: id288 in `candidate-01` and `baseline-02`; id280 in `baseline-03` and `candidate-03`. All six had 119 pair lines and zero pair/budget-event overflow; the remaining coverage gap is unresolved, not a proven leak or physical-memory discrepancy.
- One supplemental baseline KMS capture, tied to the live owner process before/after, shows the `NEON DOCTRINE` publisher splash, not the Lamentum menu/world. The candidate-side live KMS capture was not obtained; pixel parity is therefore **unverified**. After cleanup the screen was restored from the idle clock overlay to the awake SpruceOS MainUI via an explicitly agent-injected Back; that capture is cleanup evidence only.

**Classification: INCONCLUSIVE; keep the candidate default OFF.** Source-requested scratch and first-present memory counters improved, but the pixel gate is incomplete, all runs still cross the 96 MiB floor and the 120-second menu gate is unmet. Continue with **M3-B**, reconstructing the owner-qualified pre-first-present peak and instrumentation overhead per the detailed plan. Do not enter New Game or lower the safety floor.

---

## 78. Post-build251 device A/B audit: memory headroom and playability critical path (2026-10-23)

**CURRENT / SUPERSEDES §76 IMPLEMENTATION STATUS AND §77 “NEXT GATE”; no new device arm in this documentation audit.** See [the detailed 2026-10-23 implementation roadmap](post-build251-device-audit-roadmap-2026-10-23.md) for function-level edits, experiment design, host fixtures, required receipts, exact pass/fail and rollback conditions. Ground truth: [six-arm build251 A/B report](../evidence/m3a-bcstripe-b251-01/README.md) and [machine-readable run summary](../evidence/m3a-bcstripe-b251-01/ab-summary.json). Reviewed original source at main `00e5388fe71384dec98e98b6a303391b35771f17`; writing this section is not another test.

**What changed since §76/§77:** the earlier plan's “run M3-A1” is **DONE/INCONCLUSIVE**. On build251 the stripe ON arm reduced 1920×1080 owner105 requested overlapping CPU BC scratch per upload `10368000 -> 1228800 B`, and three matched first-present pairs had higher `MemAvailable` (+15572/+23520/+25936 KiB). Yet **all six** OFF/ON arms still reached `STOP status=T2_MEMORY_FLOOR`, had **zero menu events**, swap was still consumed and the floor `MemAvailable` comparison was unfavorable in 2/3 ON arms. One owned baseline live KMS image is **publisher splash**; no owner-qualified ON image, so **pixel parity is unproven**. All six runs had clean cleanup and no owned OOM evidence. Keep `LC2_BC_STRIPE_MEDIUM` OFF; not a 30-FPS result.

**New concrete blocker that §76 did not incorporate:** budget/pair replay rejects 4/6 arms because active budget ID **288** or **280** has no matching texture-pair record, even though 119 pair lines/arm were emitted and overflow counters are zero. Source audit shows `lc2_life_events_texture_pair` is called from initialisation and striped BC materialisation; it does **not** establish why those IDs are missing. Do not weaken `tools/ledger_bases.py:replay_texture_budget` to silently omit them. Resolve event ownership/temporal generation before claiming a complete per-owner memory waterfall.

| Order | New PR/gate | Must produce | Hard stop |
| --- | --- | --- | --- |
| **P0-1 E4** | Trace **280/288** missing `LC2_TEXTURE_PAIR` vs budget charge in raw owner logs; add bounded generation-stamped owner transitions and strict reducer fixtures | Qualified live-ID join at the exact floor sample or explicit incomplete classification | Missing/incomplete identities, overflow, owner ambiguity |
| **P0-2 M3-B** | First-present **peak memory waterfall**: bounded events for BC scratch malloc/free, GL allocations, driver snapshots and safe proc system metrics; observer OFF control | Top current transient + persistent owner, phase-aligned `VmHWM/MemAvailable/CmaFree/SwapFree`, bounded overhead | >5% tracing overhead, unsafe headroom, invented physical attribution |
| **P0-3 V1** | Trigger owned **live** KMS on a fresh present event, not a fixed time delay, for OFF and ON | Same-phase 1280×720 parity + post-capture owner verification; compare mips, alpha/sRGB | Candidate exited/capture missing; no pixel-proof claim |
| **P0-4 E3** | Make GL subresource overwrite vs extension exact, recycle deleted table slots with monotonic generations, and add safe pre-GL storage admission | C/Python fixtures incl. >512 create/delete cycles; typed `T2_STORAGE_ADMISSION` and no new OOM | No clean resource lifetime or missing GL context |
| **P0-5 M3-C** | ONE measured structural memory reduction: duplicate/coherent BC copies, qualified GPU atlas format/lifetime, or scoped 1080p family | Three repeated same-phase pairs with real sustained headroom + pixels; 96 MiB floor unchanged | Scratch-only delta, lower floor, unsafe eviction/GL, content mismatch |
| **P0-6 W0** | Three **120-s owned live menu** runs with KMS, menu event and strict cleanup | No memory floor, safe CMA, stable swap, real menu state and unique present serials | Publisher splash, clock/home image, floor/OOM/GL error |
| **P0-7 W1** | New Game -> first world, physical movement/interaction, inventory/dialogue, audible sound, cold save/reload | Three clean independently playable loops; no TEST-only critical draw | Any real-world or functional gate missing |
| **P1 F1** | Correct *world*-frame P50/P95/P99, CPU/GPU/wait/fault profiling and one-variable performance PR | P95 <=33.33 ms in declared matched world scenes, intact pixels/audio/input/memory | Startup/menu/Loading present count substituted for gameplay FPS |

**Code-level audited risks:** `runtime/lamentum-adapter.patch:lc2_life_events_storage` adds `bytes` on repeated same-name texture storage without distinguishing a redefinition of one mip from a new level; `LC2_LIFE_EVENT_CAP=512` uses `!entry.name` for free slots even though delete leaves an entry name. Neither is proved to be the cause of the build251 floor or four missing pairs. `lc2_bc_upload_stripes` currently requests `width*128*bpp` decoded scratch even for short mips; correct/test `min(height,128)` in a **separate** pinned code change, not retroactively inside the completed build251 A/B.

**Platform feasibility checkpoint:** If two carefully *selected* persistent-memory changes still cannot produce a stable menu with appropriate CMA/swap headroom, explicitly review the minimum guest+Mali working set and alternative rendering/asset-quality/backend cost. The internal 1080p composition family has an **upper-bound nominal** 17.58 MiB saving to 720p, not a proven menu fix. The historic 8192² deferred BC texture hazard is later in Loading, **not** evidence of why today's no-input menu arms stop. Avoid a 32 MiB “success”, larger swap/budget, unsound `glFlush` completion, unvalidated pageout, or generic performance claims while W0/W1 are closed.

**Bottom line:** solve true memory residency and capture correctness first; make New Game playable next; pursue stable 30 FPS **only with measured world frames**.

## 79. Build253 M3-B observer: host green, device waterfall pending (2026-10-22)

**Reviewed source:** `origin/main` at `00e5388`, §77 and [the M3-B implementation plan](build251-evidence-and-gameplay-roadmap.md#3-p0-pr-m3-b--reconstruct-the-actual-pre-first-present-memory-peak-not-just-final-live-gl-totals).

`tools/proc_metrics.py` now builds one target-side, bounded timeline pinned to boot ID, executable device/inode, run UUID, ELF SHA, PID and starttime. It samples process and system memory at 100 ms for at most 256 samples; `smaps_rollup` is read at a sparse 4-second cadence with its read duration. Missing `/proc/pressure/memory`, CMA, vmstat or process fields remain unavailable/`null`. A prelaunch system sample records its device monotonic timestamp and expected runtime identity, with PID/starttime explicitly null and the live MainUI identity retained as a confounder. `device_principal_test.py --memory-timeline` requires a fresh local evidence directory and writes an ignored `memory-timeline.raw.json` plus a compact SHA-256 receipt.

The native overlay adds `LC2_M3B_TIMELINE` (exact value `1`, default off) and a fixed 64-slot ring with an optional lower `LC2_M3B_MAX_EVENTS` limit. It records BC stage windows only when combined requested RGBA and linear scratch reaches 1 MiB: start/end, decode, GL allocation/upload, NVN object ID/generation basis, GL storage generation, content generation, pool identity, compressed bytes, requested staging and GL payload. `egl-context-ready`, first-present and teardown marks share the same bounded ring. It closes at stop without writing inside the allocation path and reports dropped, incomplete, active and format-error counts; an open window or overflow makes `complete=0`.

**Evidence limits:** `staging-live-requested-peak-bytes` is source-level overlapping allocation requests, not measured RSS or physical memory. The current ring does not bracket non-BC GL/EGL/renderbuffer/buffer allocations; stage-local GL error, Mali allocation units/residency, GPU in-flight bytes, fileback/ZRAM shadow and source-write generation remain unmeasured. A device result may therefore conclude “unknown residual”; it cannot claim M3-B PASS until the large allocation classes are covered or independently reconciled.

**Host/build checks:** 292 Python tests passed; the compiled C M3-B ring fixture and BC decode fixture passed; the 435-file recovered baseline manifest passed. Runtime patch SHA-256 `dbb6bb5703ac15774637842edc78f92a49dcd4ff97f6d86f09c7cb78f7c75e7a`. Build253 from the pinned Spruce container is AArch64 ELF64, 2,181,728 bytes, SHA-256 `7acd58704b662184d4f2103d782d911b06c40e18fe7f4505f2753a06242bc6b9`, GLIBC requirements through 2.27. This is an instrumentation build, not a device measurement or optimization result.

**Checkpoint state:** this was the pre-deployment checkpoint. The subsequent same-build device pair and its limits are recorded in §80.

## 80. Build253 M3-B first device OFF/ON pair: BC ring captured, memory attribution incomplete (2026-10-22)

**Evidence:** [paired device report and compact receipt](../evidence/m3b-build253-pair-20261022-01/README.md). The runtime was installed through the TSPS workflow after a read-only idle preflight. Build253 SHA-256 `7acd58704b662184d4f2103d782d911b06c40e18fe7f4505f2753a06242bc6b9` was read back after both arms; build251 backup `.before-253` remains verified at SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`. Launcher/helper hashes were unchanged.

Both no-input principal-flow runs used the same build, process sampler, 96 MiB safety floor, 300 MiB texture cap and strict GL. The sole arm difference was `LC2_M3B_TIMELINE=0` versus `1`; the medium BC stripe candidate remained off. Both timelines completed through process exit with zero dropped samples, but both runs stopped at `T2_MEMORY_FLOOR` before the menu gate. OFF: 104 live/106 total samples, ring emitted no records, floor `MemAvailable=90,960 KiB`, `SwapFree=1,971,432 KiB`, requested live texture bytes `117,441,536`. ON: 89 live/91 total, the bounded ring emitted 30/30 events (27 windows + 3 marks, no incomplete/active/dropped/format-error records), floor `MemAvailable=84,140 KiB`, `SwapFree=2,015,460 KiB`, requested live texture bytes `112,329,728`. Both had zero menu events, no owned OOM evidence and clean process/CPU cleanup. These are not gameplay or FPS runs.

The largest emitted BC window was owner 105, 1920×1080: 2,949,120 B compressed source, 8,294,400 B requested RGBA plus 2,073,600 B linear staging (10,368,000 B requested overlap). Decode wall brackets were 85.9 ms on initialization and 90.3 ms on refresh; GL allocation/upload was 8.77 ms on initialization and refresh upload 12.81 ms. These requests do not establish physical Mali residency or CPU-frame cost. Driver allocation, GPU in-flight/completion, source-write generation, stage-local GL error and Mali residency remain unknown.

**New limitation found:** the ON timeline's nearest live sample was 64.8 ms before the floor and showed `MemAvailable=124,384 KiB`; the floor record was `84,140 KiB`, 40,244 KiB lower. The floor-side menu ledger could not acquire the GL lock, so exact floor CMA/RSS/VmSwap are unavailable. Thus `complete=true` means the bounded sampler ran through process exit, not that it captured the transient peak. The sequential pair also recorded different debug present-probe counts (13 OFF, 2 ON; not FPS), so it cannot establish a causal ring-overhead or memory-improvement result. Swap was consumed in both arms (62,208 KiB OFF and 17,664 KiB ON from prelaunch to floor); neither is a no-swap success.

**Cleanup:** both runs ended with MainUI only, no game process, the principal command absent, online mask `4-7`, and CPU0–3 offline with sysfs mode `0444`. The ON cleanup capture initially showed the idle clock; a released agent-injected 100 ms BACK restored awake MainUI, then KMS verified the home screen. These captures are cleanup evidence only. The lock-independent floor snapshot was implemented and built as build254, but is not yet device-verified; broader non-BC GL/EGL/renderbuffer/buffer owner coverage remains open. See §81. Keep floor96/cap300/strict GL; do not enter New Game. **The port remains NOT PLAYABLE; gameplay 30 FPS and no-swap operation are unverified.**

## 81. Build254 lock-independent floor snapshot: host green, device validation pending (2026-10-22)

`native/lc2_proc_memory_snapshot.h` reads `CmaFree` from `/proc/meminfo` and `VmRSS`/`VmSwap` from `/proc/self/status` once at the T2 pre-stop boundary. The timestamp bracket and existing T2 floor-check timestamp are recorded separately; absent fields print `unknown`, not zero. The call is before `lc2_menu_ledger_floor_preflight`'s GL `trylock`, and runs only when the opt-in `LC2_MENU_LEDGER=1` observer is enabled. It changes neither the floor decision nor the storage ledger. The same `LC2_MENU_LEDGER=1` setting must be used in both ring-OFF/ON arms.

**Host/build:** 294 Python tests passed, including the compiled floor-snapshot fixture for present/missing fields; the life-event and BC-layout fixtures passed; the recovered baseline manifest passed 435/435. Overlay SHA-256 `1a087c052dd1c36354283d92c48817a41a037de85f3c65f617e16cb8c506bdbe`. Build254 is AArch64 ELF64, 2,185,960 bytes, SHA-256 `b6a84e4cd423cbbd88661502c53f1f6de81ab81d1de9c504700d289e96d417e1`, GLIBC requirements through 2.27; the `LC2_MENU_FLOOR_MEMORY` marker is present.

**Checkpoint state:** this was the pre-deployment note; build254 has since been installed and tested. See §82 for the paired device result, which supersedes the pending status above.

## 82. Build254 first floor-snapshot OFF/ON pair: floor telemetry validated, waterfall partial (2026-10-22)

**Evidence:** [paired report and compact receipt](../evidence/m3b-build254-pair-20261022-01/README.md). The exact build254 runtime SHA-256 `b6a84e4cd423cbbd88661502c53f1f6de81ab81d1de9c504700d289e96d417e1` was installed and read back after both arms. Build253 is preserved at `.before-254` (SHA-256 `7acd58704b662184d4f2103d782d911b06c40e18fe7f4505f2753a06242bc6b9`); build251 remains at `.before-253` (SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`).

Both no-input principal-flow arms used floor96, cap300, strict GL, `LC2_MENU_LEDGER=1`, the same 100 ms external sampler, and `LC2_BC_STRIPE_MEDIUM` unset; only the native ring flag changed. The new `LC2_MENU_FLOOR_MEMORY` record worked in both. OFF run `f9868a42-8ccb-4ebc-9df7-72156ab0a151`: floor `MemAvailable=97,356 KiB`, `SwapFree=1,956,736 KiB`, `CmaFree=720 KiB`, `VmRSS=699,520 KiB`, `VmSwap=67,032 KiB`; capture read duration 154,917 ns. The GL live-set lock succeeded. ON run `47ed1738-f227-4668-99f6-374bb43c68d5`: floor `86,388 KiB`, `1,984,232 KiB`, `9,644 KiB`, `728,876 KiB`, `40,436 KiB`; capture read duration 163,958 ns. Its next GL trylock failed with `lock-rc=16`, but the full floor snapshot had already been emitted, proving independence from that lock.

The ON ring completed its bounded BC event set: 30 windows + 3 marks, 33/33 emitted, no incomplete/active/dropped/format-error records. The largest windows were owner92 (3600×3600; requested overlap 64,800,000 B; decode wall 527.8 ms; upload 198.1 ms) and owner81 (3600×2160; 38,880,000 B overlap; decode 317.4 ms; upload 50.3 ms). Neighboring process samples showed large RSS rises during the brackets, but are asynchronous and do not prove allocation attribution or physical residency.

The OFF floor live-set recorded 253,465,904 B of combined declared GL texture/renderbuffer payload versus 117,441,536 B in the T2 budget (a 136,024,368 B numerical gap), with 95 views/owners and no registry overflow. Owners92/81 account for 51,840,000 B and 31,104,000 B of declared GL texture payload. This is declared-payload evidence only: share-group identity, GPU completion, driver allocation and physical Mali residency remain unproven.

**Incomplete:** the periodic timeline ended with `complete=false` in both arms (3 missed intervals OFF, 7 ON; maximum sample durations 212.1/308.8 ms while collector CPU was 4.35/4.13 ms; cause unclassified). The BC ring is complete only for its selected windows; non-BC owners remain uncovered. The arms had 15 vs 17 debug present-probe records, unequal floor readings and unmeasured thermal matching; this single pair cannot establish a causal memory or overhead effect. Both stopped at `T2_MEMORY_FLOOR` before the menu and consumed swap; no gameplay or FPS was measured.

Both cleanups had no game process, zero cleanup errors, MainUI restored, CPU mask `4-7`, and CPU0–3 offline/mode `0444`. KMS captures showed the awake MainUI home, cleanup only. The next step is to reconcile the owner92/81 staging/declared-GL footprint and fill non-BC allocation coverage before any memory-saving patch. Keep floor96/cap300/strict GL; do not enter New Game. **The port remains NOT PLAYABLE; no-swap operation and gameplay 30 FPS remain unverified.**

## 83. Build256b non-BC owner windows prepared; pre-device checkpoint (2026-10-22)

The build254 OFF floor live-set was parsed by owner and GL class: 95 owners, 30 BC textures with 188,899,072 B declared GL texture payload, 63 non-BC textures with 52,586,032 B, and two depth renderbuffers with 11,980,800 B. Combined declared payload 253,465,904 B versus 117,441,536 B T2 charges; this is not physical residency. The largest non-BC owners are 2/3/4 (each 1920×1080, 8,294,400 B), 60 (955×2048, 7,823,360 B), 82 (1032×1122, 4,631,616 B), and 172/206 (each 1280×720, 3,686,400 B). The same run's life summary reported no live buffer storage (`buf-bytes=0`, `buf-live=0`, `respecs=0`), but the buffer class is not proven absent: source audit found `nvn_present.h` creates a VBO with `glBufferData` and does not update the lifecycle ledger. The EGL route was an 8×8 pbuffer. Driver allocation and Mali physical residency remain unknown.

Build256b now records ≥1 MiB non-BC NVN texture initialization/refresh windows and depth-renderbuffer storage windows in the opt-in M3-B ring. The BC in-place decoder candidate remains strictly opt-in (`LC2_BC_INPLACE_DECODE=1`); the launcher does not set it, and no device run has enabled it. Host tests passed: 294 Python tests, life-event/BC-layout/floor-snapshot fixtures, baseline manifest 435/435. Overlay SHA-256 `ea6a4d103f3893ad0420973dcf3077ec84ccd806053b4b017ede1a7fc1ad657c`; build256b is AArch64 ELF64, 2,189,968 B, SHA-256 `27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`, GLIBC ≤2.27.

**Pre-device checkpoint:** at this point build254 remained installed and build256b had not yet been deployed. The subsequent same-build M3-B OFF/ON pair is recorded in §84. This remains instrumentation validation, not a memory win, no-swap result, playable-port result, or FPS measurement.

## 84. Build256b M3-B device OFF/ON: selected allocation windows complete, DMA-heap failure observed (2026-10-22)

**Evidence:** [paired report and compact receipt](../evidence/m3b-build256b-pair-20261022-01/README.md). Build256b (`27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`) was installed and read back on TSPS; build254 remains preserved at `.before-256b` (`b6a84e4cd423cbbd88661502c53f1f6de81ab81d1de9c504700d289e96d417e1`). Build253 `.before-254` and build251 `.before-253` hashes also remained intact.

Both no-input principal-flow arms used floor96, cap300, strict GL, `LC2_LIFE_EVENTS=1`, `LC2_MENU_LEDGER=1`, a 64-event ring cap, and the same 100 ms external memory timeline; `LC2_BC_STRIPE_MEDIUM` and `LC2_BC_INPLACE_DECODE` were unset. Only `LC2_M3B_TIMELINE` changed. Both arms executed the exact owned build256b ELF and stopped at `T2_MEMORY_FLOOR` before the menu; menu events were zero.

OFF `eb0df8ff-d369-4caa-9e5d-abc749a18bb6`: floor `MemAvailable=92,404 KiB`, `SwapFree=1,962,064 KiB`, `CmaFree=7,836 KiB`, `VmRSS=699,000 KiB`, `VmSwap=62,008 KiB`; floor snapshot read 145,792 ns. Ring records were absent as expected. The external timeline was incomplete (109 total/107 live, 3 dropped). The OFF kernel delta added one order-4 page-allocation failure for `terminator2d-ne` PID 30017 via `system_heap_allocate -> dma_heap_ioctl`; its contemporaneous `Mem-Info` reported `free=8399` pages and `free_cma=4122` pages. No OOM-killer or `Killed process` line was added.

ON `df657097-c8f2-4635-b7a9-eb02ada2689b`: floor `MemAvailable=91,616 KiB`, `SwapFree=1,975,176 KiB`, `CmaFree=92 KiB`, `VmRSS=711,928 KiB`, `VmSwap=48,776 KiB`; floor snapshot read 146,875 ns. The bounded ring emitted 44/44 (41 windows + 3 marks), with no incomplete, active, dropped, or format-error records. It covered 25 BC initialize + 4 BC refresh windows, 9 non-BC texture initialize + 1 refresh, and 2 depth-renderbuffer storage windows; all 41 windows had a known storage generation. The periodic timeline remained incomplete (107 total/105 live, 4 dropped). The ON kernel delta had no additional page-allocation-failure entry, but the OFF failure was already in its baseline.

The captured owner-qualified windows extend M3-B coverage to the large non-BC texture and depth paths; storage generations are known, but source-write/content epochs remain untracked, and stage-local GL errors, driver backing, GPU in-flight work, fileback shadows and physical Mali residency remain unknown. The life summary's zero buffer bytes are not an absence proof: `nvn_present.h` creates a VBO through an uninstrumented `glBufferData` call, and M3-B has no buffer window. Owners 92/81 still have requested CPU scratch peaks of 64,800,000 B/38,880,000 B; the declared GL payload remains a separate logical measure. The floor samples and nearest periodic samples are asynchronous; the two sequential runs differ in floor/CMA state, and swap fell by 71,424 KiB OFF and 58,624 KiB ON. Thus the pair does not establish a causal memory or ring-overhead effect. DMA allocation owner correlation and the missing periodic intervals remain unknown. Post-cleanup KMS confirmed awake MainUI after OFF's explicit agent-injected BACK and after ON; the single DMA-heap page-allocation failure is not an OOM-kill but is a real low-memory warning. A fresh preflight then showed `MemAvailable=688,148 KiB`, `CmaFree=102,600 KiB`, `SwapFree=2,032,836 KiB`, MainUI only, and the expected runtime hash.

**Next gate:** §86 records four per-run margin tests; every arm stopped on `cmafree-margin` before the menu. Build259 remains installed. Do not launch below 24 MiB or enter New Game while `CmaFree` remains near 15 MiB; first investigate the CMA drop through read-only evidence and re-establish a safe baseline. Keep floor96/cap300/strict GL.

## 85. M2B-E3 build259 host checkpoint before any device run (2026-10-22)

**Phase start:** remote branch `perf/m3b-memory-waterfall` was fetched and verified at `3590137aa419a3e3092d09d45636e818b13cae39`; this phase follows roadmap-v2 order 3 and the §84 stop conditions. The companion requirements are in [build251 roadmap §5](build251-evidence-and-gameplay-roadmap.md#5-p0--pr-m2b-e3--safetyadmission-and-accounting-correctness).

**Implemented in the candidate:**

- Storage accounting now distinguishes share-group/context epoch, GL name/kind, target, cube face, mip/layer and storage generation; same-key respec replaces bytes, while distinct subresources extend. Python replay uses the same subresource identity. Buffer-store redefinition and buffer storage keys are covered in the source/host fixtures.
- `lc2_gl_storage_admission` checks `MemAvailable >= floor + GL request + overlapping scratch + margin`, and conservatively `CmaFree >= GL request + overlapping scratch + margin`. A RED fixture caught the former CMA formula omitting scratch (12 MiB required instead of 14 MiB for an 8+2+4 MiB request); the corrected host fixture passes.
- `lc2_gl_admission.h` wraps every statically found direct storage call. The scan found 36 `glTexImage2D`, 2 `glRenderbufferStorage`, and 5 `glBufferData` sites; none were before the wrapper include. No direct `glTexStorage*`, `glTexImage3D`, compressed-image or copy-image storage sites were found. Unknown 2D formats fail closed.
- Pre-allocation checks cover the default BC full/striped staging and selected CPU scratch paths. Optional page-substitution/alternate presentation routes remain explicitly disabled or unobserved in the last device logs; their host scratch behavior is not yet device-qualified.

**Host/build evidence:** [compact receipt](../evidence/m2b-e3-build259-predevice-01/README.md). Full host suite 302 passed; storage layout/admission tests 14 passed plus one extracted T2 `/proc`/margin wrapper fixture; pinned source baseline 435/435. Adapter diff check passed and the overlay matches its source diff byte-for-byte (SHA-256 `4a1837eff2b1d3d3619262ee8250e0fc12e504ca9c6357abc561ecb66cdcf5fc`). Build259 succeeded in the pinned AArch64 container: ELF64/AArch64 PIE, 2,198,560 bytes, SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`, max GLIBC 2.27. Nonfatal compiler warnings remain for ignored `write()` results and unused optional functions.

**Not a device result:** build259 is not installed. A fresh read-only preflight confirmed TSPS still has build256b installed (`27a2f9a8...`) and only MainUI running (PID/starttime `31619/2258075`), with `MemAvailable=687,036 KiB`, `CmaFree=102,644 KiB`, and `SwapFree=2,032,836 KiB`; CPUs 0–3 remain offline and `/tmp/cmd_to_run.sh` is absent. No game run has demonstrated the admission decision, complete buffer lifecycle journal, menu, no-swap behavior, gameplay or FPS. The target reports Linux 5.15.147 on `sun55iw3`, with `CONFIG_DMABUF_HEAPS_SYSTEM`, `CONFIG_CMA` and `CONFIG_DMA_CMA` enabled. Public [REG-Linux/linux-t527 commit `9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed`](https://github.com/REG-Linux/linux-t527/tree/9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed) is a matching-version T527 source analogue: its `system_heap.c` retries orders 8, 4, 0 after failed page allocations. That is **not proven to be the exact Dec-2025 device vendor tree**; the build256b order-4 failure may be an intermediate retry, while overall request success and allocation owner remain unknown. The share-group/context token and physical Mali residency are not independently proven.

**Historical stop gate at phase start (2026-10-22):** `T2_STORAGE_MARGIN_MIB` intentionally had no default; the idle preflight did not establish a working threshold. The user later authorized testing different per-run values; see §86. Floor96, cap300 and strict GL remain unchanged.

## 86. M2B-E3 build259 device margin sweep — hard stop (2026-10-23)

**Authorization and procedure:** the user explicitly delegated margin selection (“Тестируй разные значения сам”). Installed build259 after pinning the device state and preserving the previous build256b runtime at `.before-259`. Four no-input principal-flow arms used margins **64, 48, 32, 24 MiB**; all other test settings were held constant: floor96, texture cap300, strict GL, life events/menu ledger on, M3-B ring off, external 100 ms memory timeline, no New Game. `T2_STORAGE_MARGIN_MIB` remains unset in the launcher; these were per-run values only.

| Margin | Run UUID | Admission checks (allowed/refused) | Denied request | Refusal sample: CmaFree / required CMA; MemAvailable | CmaFree after exit |
|---:|---|---:|---|---|---:|
| 64 MiB | `c11ee013-91bf-46c0-80d6-41ebd44b3a89` | 106 (105/1) | owner 61, scratch 5,400,000 B | 70,516 KiB / 72,508,864 B; 540,244 KiB | 97,380 KiB |
| 48 MiB | `8bc3f0cd-e245-4637-bdd5-5a81cc98f1e3` | 192 (191/1) | owner 77, scratch 10,368,000 B | 47,316 KiB / 60,699,648 B; 524,708 KiB | 88,436 KiB |
| 32 MiB | `c4157aca-ffd0-4738-a686-f80cf06b30ca` | 177 (176/1) | owner 0, GL 512,000 B | 30,520 KiB / 34,066,432 B; 509,188 KiB | 87,712 KiB |
| 24 MiB | `143d309a-cf1e-4df3-981c-b475ad69c895` | 193 (192/1) | owner 0, GL 8,294,400 B | 12,664 KiB / 33,460,224 B; 493,096 KiB | 14,244 KiB |

All four refusals were typed `T2_STORAGE_ADMISSION reason=cmafree-margin`; each had zero subsequent `LC2_GL_STORAGE_EVENT` records. Per-arm `SwapFree` did not change, and no new kernel OOM, killed-process, or page-allocation-failure warning appeared. The 64 MiB memory timeline was incomplete (29 live of 31, 0 dropped); the other three were complete (17/19, 16/18, 17/19 live/total). MainUI returned after every arm, no game process remained, CPU mask stayed `4-7`, and CPUs0–3 remained offline/mode `0444`. The 64 MiB cleanup initially showed the idle clock; a released 100 ms BACK restored awake MainUI. Later cleanup captures showed awake MainUI.

**Safety stop:** after margin24, `CmaFree` was 14,244 KiB immediately and 15,384 KiB after a 20 s idle read-only wait. The earlier page-allocation warning reported `free_cma=4,122` pages (16,488 KiB at 4 KiB/page). A later `/proc` sample showed `CmaTotal=131,072 KiB`, `CmaFree=15,416 KiB`, `nr_free_cma=3,854`, and current `cma_alloc_success=36/cma_alloc_fail=0` counters (no paired baseline; not attributable). A separate 30 s idle pair with the same MainUI PID/build kept `CmaFree=15,456 KiB`, `nr_free_cma=3,864`, and CMA success/fail counters unchanged. MainUI had FD 10 to `/dev/dma_heap/system` plus four `system`-exporter DMA-BUF FDs (16,384 B and three 3,686,400 B buffers; 11,075,584 B total); these sizes do not prove CMA residency or explain the drop. The latest read-only preflight still showed `MemAvailable=686,396 KiB`, `SwapFree=2,033,604 KiB`, MainUI only, and build259 installed. No new kernel allocation failure occurred, but free CMA remains below the earlier warning context. Debugfs DMA-buf/DMA-heap/CMA/Mali paths were absent, so physical backing and retention cause remain unknown. Timeline samples fell from 87,604 to 71,712, 47,836, and 17,248 KiB before the refusal snapshot; GL storage journal events overlapped that interval, which is correlation—not proof of physical residency.

**Stop lower-margin tests and do not enter New Game.** Investigate CMA accounting/retention using read-only evidence and wait for a safe baseline before another device launch. Build259 is still installed (SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`); `.before-259` is verified build256b (`27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`). Compact receipts: [margin-sweep README](../evidence/m2b-e3-build259-margin-sweep/README.md) and [machine-readable summary](../evidence/m2b-e3-build259-margin-sweep/ab-summary.json). Raw logs, kernel dumps, timelines and screenshots remain local. No arm reached the menu; gameplay, no-swap behavior, and ≥30 FPS remain unverified.

## 87. E4 owner-pair host checkpoint; device gate remains blocked (2026-10-23)

**Scope:** host/source/replay/build only; no TSPS read, install, or launch in this checkpoint. Full details and compact receipt: [E4 host report](../evidence/e4-owner-pair-host-2026-10-23/README.md) and [summary JSON](../evidence/e4-owner-pair-host-2026-10-23/summary.json).

**Historical build251 replay:** SHA-checked all six logs against the existing A/B summary; all have 119 pair records and no owner-event records or owner summary. `baseline-01` and `candidate-02` reconcile; `baseline-03` has a matching ID280 pair 71.920625 ms after the floor snapshot and is classified `pair_not_yet_emitted`; candidate-01 and baseline-02 retain `288=unresolved`; candidate-03 retains `280=unresolved`. The old logs do not prove why the three IDs have no pair. Replay remains fail-closed.

**Implemented:** the adapter overlay adds a default-off, `LC2_LIFE_EVENTS=1` opt-in owner-event ring (cap 512) and completion/overflow receipt. The reducer now distinguishes late pair, missing owner path, generation conflict, alias-scope mismatch, truncation and over-capacity without suppressing live owners. Schema-capable runs must pass `owner_events_expected=True`; legacy build251 replay keeps the expectation off and remains unresolved rather than being mislabelled truncated. Generation conflicts are evaluated at the floor timestamp, so later NVN ID generations cannot rewrite the earlier live-set join. The object-generation basis is the monotonic NVN object ID; source-write generation remains untracked, and no physical-memory attribution is implied.

**Host/build:** 317 Python tests passed; 45 focused ledger/life-event/GL-storage tests passed; Python compilation passed; baseline 435/435; patch applicability and diff checks passed. The source overlay matches SHA-256 `72b309b02242377d7faf524fe091e9603013d5051098c0c7037ed434d661b6dd`. Pinned build260 is an AArch64 ELF64 PIE, 2,202,664 bytes, SHA-256 `f2930135ecc431ffab92595b6324486cbf5df0b6484138d9dcf33d8cc1c680af`, GLIBC ≤2.27. The owner-image RomFS section was streamed and matched SHA-256 `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`. Build260 is **not installed**.

**Not qualified:** no owner-event capture and no observer-OFF device control were run. The last §86 idle reading was `CmaFree=15,456 KiB`; this host checkpoint did not re-read the device. The immediate next action remains §86 read-only CMA investigation, not installation or gameplay launch. Build259 is the last reported installed ELF. The port remains NOT PLAYABLE; world gameplay, save/load, no-swap behavior, and ≥30 FPS remain unverified.

## 88. Build259 read-only CMA audit: low idle CMA persists, owner unknown (2026-10-23)

**Evidence:** [compact read-only audit](../evidence/m2b-e3-build259-cma-readonly-2026-10-23/README.md) and [machine-readable summary](../evidence/m2b-e3-build259-cma-readonly-2026-10-23/summary.json). Fresh non-multiplexed SSH reads confirmed the installed runtime still matches build259 (`d72e2f69...`), MainUI PID/starttime `28250/4031805`, no Lamentum process, CPU online mask `4-7`, and CPUs0–3 offline/mode `0444`.

Two idle snapshots 20.4 s apart both reported `CmaTotal=131,072 KiB`, `CmaFree=15,456 KiB`, `nr_free_cma=3,864` pages, `cma_alloc_success=36`, `cma_alloc_fail=0`, and `SwapFree=2,033,604 KiB`. A post-probe readback remained at the same CMA/counter values. `MemAvailable` stayed around 683 MiB. This confirms a stable **low** idle CMA state; it does not explain where the unavailable CMA went.

The current boot's dmesg ring contains eight order-4 `terminator2d-ne` allocation failures through `dma_heap_ioctl`; the latest is at kernel uptime `22,380.157231 s`, with `free_cma=4,122` pages. Its stack is `__alloc_pages+0xbe0/0xc20 -> system_heap_allocate+0x120/0x38c -> dma_heap_ioctl+0x14c/0x320`. No new matching warning appeared during the idle snapshot pair and there are no explicit OOM-kill matches in the filtered kernel log. The current MainUI has four `system`-exporter DMA-BUFs (16 KiB and three 3.5 MiB buffers); this is not proof of CMA backing or retention. See §89 for the version-matched but non-vendor source check.

`CONFIG_CMA_DEBUGFS` is not set, `/sys/kernel/mm/cma` is absent, and no debugfs mount was present. Temporary read-only debugfs mount attempts returned busy; post-checks verified that no mount or temporary directory remained. `CONFIG_DEBUG_FS=y`, but no device-side allocator/driver counters were exposed by this attempt.

**Verdict / next gate:** the low-CMA block remains; no install, game launch, New Game, or lower-margin test is permitted. Continue with host-side source identification for the exact vendor DMA-heap/CMA retry path. The public T527 kernel tree remains only an analogue unless exact linkage to this firmware is established. The next device action must remain read-only until a safe CMA baseline is demonstrated.

## 89. Kernel-source cross-check: order-4 warning is not a request verdict (2026-10-23)

The target's latest captured order-4 warning includes the stack `__alloc_pages+0xbe0/0xc20 -> system_heap_allocate+0x120/0x38c -> dma_heap_ioctl+0x14c/0x320`. This proves the failed order-4 `alloc_pages` attempt was in the system-heap path; it does **not** show whether the encompassing DMA-heap allocation later failed or succeeded.

A version-matched public [REG-Linux/linux-t527](https://github.com/REG-Linux/linux-t527) source snapshot at commit [`9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed`](https://github.com/REG-Linux/linux-t527/tree/9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed) declares `VERSION=5`, `PATCHLEVEL=15`, `SUBLEVEL=147`, matching the target release. In its [`system_heap.c`](https://github.com/REG-Linux/linux-t527/blob/9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed/drivers/dma-buf/heaps/system_heap.c), `orders[]` is `{8,4,0}`; `alloc_largest_available()` continues to the next eligible order after `alloc_pages()` returns NULL, and `system_heap_allocate()` aborts only when no eligible page is returned. Therefore, **on that analogue**, an order-4 warning may be an intermediate retry and is not proof of final request failure.

**Limit:** this is not the verified Spruce/vendor kernel tree. Exact target fallback behavior and DMA-heap request completion remain unknown; the eight warnings are valid pressure signals, not eight confirmed failed user allocations. Keep the device launch blocked. Next: locate the exact firmware vendor source or a target-side completion receipt without altering CMA policy; if neither is available, preserve this as an unresolved blocker rather than inferring success.


## 90. Build260 CMA-to-gameplay execution update (2026-10-23)

**Current authoritative next-step roadmap:** [post-build260 CMA-to-gameplay plan](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md). This source/evidence reassessment is documentation only; it made no new device run or benchmark. It follows the full [read-only CMA receipt](../evidence/m2b-e3-build259-cma-readonly-2026-10-23/README.md), the [four margin denials](../evidence/m2b-e3-build259-margin-sweep/README.md), and [E4 host checkpoint](../evidence/e4-owner-pair-host-2026-10-23/README.md).

**Why the order changes:** the installed build259 policy currently checks `CmaFree >= GL nominal bytes + overlapping CPU scratch + operator margin` in `lc2_gl_storage_admission`. This is conservative but not proven to match physical CMA consumption: CPU malloc, guest/GL logical payload and DMA-heap/system pages are distinct accounting bases. Four denials and current idle free CMA ~15 MiB establish the **safety stop**, not the precise retained CMA owner or a verified final failed DMA ioctl. Do not relax the guard by guesswork. Linux CMA pages can also serve movable allocations, so `CmaTotal-CmaFree` is not a measured Mali leak.

**Updated gated PR order:** K1 exact-firmware/read-only CMA work, A1 offline admission replay, and M4-A host stripe-capacity correction are complete as evidence phases; none identifies physical CMA ownership or reclamation. Next is M4b host-only allocation-lifetime coverage. E4/V1 remain behind an independent safe device go/no-go; then W0 true-menu passes, W1 playable-world/input/audio/save reload, and F1 whole-world-frame P95 `<=33.33 ms`. BC stripes, in-place decoding, texture compression and scaling remain default-off pending pixel/working-set proof. See the detailed plan for exact files, fixtures, run identity, stop rules and decision criteria.

**As of this audit:** build259 is the last reported installed binary and build260 is host-built/tested only; no title menu has passed the latest memory gates. **NOT PLAYABLE. No verified gameplay FPS.**

## 91. K1 exact firmware-build match and read-only CMA pair (2026-10-23)

**Evidence:** [K1 report](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md) and [machine-readable receipt](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/summary.json). The user-provided SpruceOS updater/config pins Smart Pro S to firmware `1.0.1` and `trimui_tg5050.awimg`; the release archive SHA-256 matches GitHub's published digest. Its IMAGEWTY payload contains an unstripped AArch64 `vmlinux` with DWARF. The live `/proc/version` banner and firmware version match; four live symbols share one `0x80000` relocation from the extracted ELF, and relevant stack extents match. This is an **exact firmware-build match**, not a hash of the whole live kernel image. The original vendor kernel source tree was not present in the inspected SpruceSource tree.

The matching binary's `system_heap_allocate` order table is `{8,4,0}`. At the logged return site `system_heap_allocate+0x120`, a null `__alloc_pages` result branches back to the candidate loop; order-4 failure can therefore be intermediate. The historical DMA-heap request completion remains unknown. The eight order-4 warnings are still valid pressure signals, not eight confirmed failed user allocations.

The read-only snapshot tools were run on the target via stdin, with no device files written. Two complete snapshots on the same boot, 22.178 s apart, both showed `CmaFree=15,456 KiB`, `nr_free_cma=3,864`, `cma_alloc_success/fail=36/0`, and unchanged `SwapFree=2,033,604 KiB`. MainUI PID/starttime and DMA-BUF FD/inode set were stable. The exact installed-runtime inode scan found no running target instance. `MIGRATE_CMA` order counts sum to 3,861 pages, three pages below `nr_free_cma`; sequential proc reads are not atomic, so this difference remains unresolved. Four `system` exporter DMA-BUF inodes match MainUI FDs, but that does not prove CMA backing or Mali residency. `CONFIG_CMA_DEBUGFS`/`CONFIG_PAGE_OWNER` are unset and tracepoint paths unavailable.

**K1 result / gate:** allocator-warning semantics are resolved from the firmware-matched binary; CMA owner, physical backing, and historical ioctl result are not. The installed runtime still reads back as build259 SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`. Build260 remains uninstalled and unlaunched. **K1.3 NO-GO remains:** A1 replay (§92) and M4-A's host stripe-sizing correction (§94) are complete; physical ownership and a safe headroom baseline remain unresolved. Continue with M4b host-only allocation-lifetime coverage; do not lower the guard or enter New Game. The port remains **NOT PLAYABLE**, with no verified gameplay FPS.

## 92. A1 host-only admission-policy replay (2026-10-23)

**Evidence:** [A1 report](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md) and [machine-readable receipt](../evidence/a1-storage-admission-offline-replay-2026-10-23/summary.json). New host-only tools are `tools/admission_offline_replay.py` and `tools/test_admission_offline_replay.py`; no runtime adapter patch was changed.

The replay strictly validates build259, floor96/cap300/strict GL, the per-run-only margin and unset launcher default, refuses New Game inputs, checks expected run/build identities and complete bounded log reads, then matches each T2 denial against the sanitized summary. All four original denials are exact: margins 64/48/32/24 MiB; requests are owner61 scratch5,400,000 B, owner77 scratch10,368,000 B, owner0 GL512,000 B, owner0 GL8,294,400 B. Each observed reason remains `cmafree-margin`; no post-denial GL-storage event appears. `all_bytes_maybe_CMA` reproduces the deployed arithmetic, while `proven_CMA_only` and `mixed_two_ledger` fail closed with `qualification=unknown` and explicit missing fields.

The `owner77` 10,368,000 B CPU peak is supported by an `LC2_BC_FULL_STAGE` record in the same run/owner log order, but that record has no timestamp; no time join is claimed. Owner61's request kind and both owner0 GL subtypes remain unknown. Physical CMA backing and a driver uncertainty margin are unknown for all requests. The margin64 timeline is incomplete and was not interpolated. Raw logs remain local; the receipt records current-copy hashes and owned-log header/tail checks, which are continuity evidence rather than full historical cryptographic attestation.

A1 used zero device actions, made no build/install/gameplay claim, and changed no production policy or margin default. Host validation passed: 15 focused A1 tests, 359 repository tests, Python compilation and `git diff --check`. Device go/no-go remains NO-GO at the last read-only idle `CmaFree=15,456 KiB`. The next host-only step is M4-A checked BC stripe/small-mip capacity and equivalence tests; no game or build260 launch until independent CMA headroom review. **NOT PLAYABLE; no verified no-swap gameplay or 30-FPS result.**

## 93. Post-K1/A1 re-audit and M4 host-only critical path (2026-10-23)

**Reviewed tree:** `main@c05f879873392787d0157186679e31f973a73ecc`. **Authoritative detailed implementation instructions:** [post-build260 CMA-to-gameplay roadmap §11](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#11-post-k1a1-re-audit-at-main-c05f879-2026-10-23). This section is a **source/evidence review only**: no new device sample, adapter build, game launch, screenshot or FPS result.

**Closed work:** K1 matched firmware 1.0.1's actual AArch64 vmlinux layout to the live kernel and proved that the observed `system_heap_allocate+0x120` order-4 null return may retry an order-0 candidate. Original DMA-heap ioctl outcome and CMA backing remain unknown. Two pairs of owned read-only CMA snapshots show idle `CmaFree=15,456 KiB`, unchanged CMA counters, free `MIGRATE_CMA` order histogram and stable MainUI DMA-BUF inodes, but not the identity of occupied CMA pages. A1 replay validated all four build259 denials with exact log run/clock identities and the current `GL+scratch+margin` admission arithmetic; `proven_CMA_only` and mixed models deliberately refuse without physical backing evidence. A1 reported 15 focused / 359 overall host tests. See [K1](../evidence/m2b-k1-kernel-cma-provenance-2026-10-23/README.md) and [A1](../evidence/a1-storage-admission-offline-replay-2026-10-23/README.md). **Do not repeat those completed workflows.**

**Three new actionable code-review items:**

1. `lc2_bc_upload_stripes` uses `width*128*bpp` scratch even where `height<128`; `lc2_bc_reserve_first_use` repeats the 128-row scratch estimate. Create a single checked, per-mip shared sizing helper and test BC1/BC3, NPOT and all mips with full-vs-stripe byte identity. Check product overflow *before* addition. `tools/test_bc_layout.py` can skip its native fixture when the pinned adapter source is unavailable: make an **unskipped** C/sanitizer receipt mandatory for this PR. This is a potential transient allocation saving, **not** an established persistent memory fix.
2. Build259 admission and A1 owner0 GL records lack binding/physical-provenance semantics. Instrument owner/context/share-group/GL name/generation with typed request kinds and distinct CPU/GL/driver accounting bases, while preserving conservative NO-GO. Additionally `lc2_life_generation_next` keeps at most 512 historically distinct GL name keys without a recycled-history strategy: add 1024-name tests and generation-unique live identity semantics, rather than assuming an observed leak.
3. Reuse the exact K1 firmware ELF/DWARF to classify GFP/heap/page-pool/CMA paths **on host**; the `{8,4,0}` retry table and the 3-order-10 free-block CMA histogram are not a proof of how game allocations are physically backed. Neither a single CMA scalar nor an order-4 warning is a safe margin oracle.

**Execution queue:** `fix/bc-stripe-checked-small-mips` (host) → `audit/owner-generation-and-memory-bases` (host) → `audit/firmware-allocator-backing` (host, may proceed in parallel) → one lossless *persistent* owner reduction (host prepared) → **only after independent device GO**, E4 observer OFF/ON and V1 game-owned live pixel parity → W0 three real 120s menu passes → W1 real world/physical input/audio/save+cold-load → F1 whole-world-frame P95 `<=33.33 ms` at 30 FPS. See detailed §11 for exact source sites, sizing equations, overflow fixtures, 1024-name tests, requested-vs-physical memory ledgers, current feature flags, experiment identities, abort/rollback and acceptance criteria.

**Current hard stop:** last read-only idle `CmaFree=15,456 KiB` and unclassified physical headroom; build259 last installed, build260 only host-built. Do not deploy, reboot automatically, lower the admission margin/floor, intentionally exhaust CMA or enter New Game. **NOT PLAYABLE. No real gameplay FPS.**

## 94. M4-A host-only BC stripe sizing and native fixture (2026-10-23)

**Evidence:** [M4-A report](../evidence/m4a-bc-stripe-capacity-2026-10-23/README.md) and [machine-readable receipt](../evidence/m4a-bc-stripe-capacity-2026-10-23/summary.json). This is a host-correctness phase, not device qualification.

`zero_bc_stripe_geometry()` and `zero_bc_full_geometry()` use checked size arithmetic; `zero_bc_select_stripe()` keeps the wide-atlas path and chooses medium stripes only for a strictly smaller requested peak. `lc2_bc_reserve_first_use()` and `lc2_bc_upload_stripes()` share the plan. The upload passes a checked current-row byte count to the decoder and retains the actual row count in `glTexSubImage2D()`. `LC2_BC_STRIPE_MEDIUM` remains default-OFF; resolution, format and mip semantics are unchanged. BC3/RGBA8 `4097×9` requested scratch is **196,692 B** rather than **2,146,864 B**; `1920×1080` remains **1,228,800 B**.

The native fixture completed **86** full-vs-stripe byte-parity cases, **86** compressed-source preservation checks, **258** buffer-guard checks and **244** exactly-once stripe-region checks; it also validated **28** metadata mip levels for the 8192×8192 BC1/BC3 chains without allocating full decoded images. The required BC profile and pinned-container ASan/UBSan profile each ran once with zero skips. The reservation module passed 14 tests; the full tools suite passed **359/359**, with zero skips, failures or errors. Baseline **435/435**, patch applicability, Python compilation and `git diff --check` all pass.

The pinned AArch64 host build is ELF64 PIE, 2,206,776 B, Build ID `43aa590ec1209841671e9ad0d8de726d9f5f90a2`, max GLIBC 2.27, SHA-256 `0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332`. It remains local-only and uninstalled.

**Limit / next:** no live GL upload, alias-view semantics, KMS pixels, RSS/CMA recovery, gameplay or FPS was measured. The last read-only `CmaFree=15,456 KiB` remains a device **NO-GO**. Continue with host-only M4-B allocation-lifetime coverage and K1-B exact-kernel DMA/CMA backing classification; no device A/B until the independent CMA gate reopens.


## 95. Publication and fresh device preflight policy (2026-10-23)

**This section supersedes all earlier blanket NO-GO / “do not install” wording for future operations.** See the [full, implementation-ready policy](post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go) for evidence requirements, exact staging and bounded smoke steps, and rejection/cleanup conditions.

- **HOST_WORK: ALLOWED:** Develop, validate, build, push and merge changes without fresh CMA evidence. M4-A is already host-complete and published in commit [509cc985](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/509cc985893e); native BC tests 86 parity cases, ASan/UBSan, full 359/359 suite, baseline 435/435 and AArch64 build261 are recorded. Binary publication must exclude game-owned inputs and meet redistribution rules. Next M4-B and K1-B host work is not blocked by CMA.
- **STAGED_ONLY: CONDITIONALLY ALLOWED:** An ELF/launcher/helper transfer or verified non-executing install can proceed with backup, exact SHA and architecture check, writable-storage check, idle process/command identity, atomic rollback, and assurance that staging **cannot autostart the game**. This operation requires no CMA launch margin. Label it STAGED or INSTALLED_NOT_RUN, not device-qualified.
- **BOUNDED_DIAGNOSTIC: FRESH PREFLIGHT REQUIRED:** Before **any** runtime start collect two complete read-only same-boot CMA and free-block-by-order samples, MemAvailable/SwapFree, allocator warnings, kernel/runtime/MainUI identity, background trends, and compare projected per-class allocation demand plus an uncertainty margin to actual available headroom. Reject incomplete measurements, new warnings, unsafe fragmentation, unstable pressure and low unexplained CMA (including a recurrence of the historical ~15 MiB danger state). Preserve strict GL, floor96, cap300 and the fail-closed admission policy. If no defensible safe margin exists, HOLD_RUNTIME and continue host investigation; do not experiment with successively lower margins.
- **WORLD_GAMEPLAY: NOT AUTHORIZED BY STAGING:** An owned stable menu and safe repeated bounded diagnostics are prerequisites for New Game, controls, audio, cold save/reload and real-world frame timing. FPS is unmeasured until that functional gate is met.

**Report distinctly:** M4-A source publication = DONE, build261 host build = DONE, stage/install = unknown/not run until tested, runtime preflight = fresh or historical with timestamp, runtime launch = authorized/held based on **fresh** evidence, and gameplay/30 FPS = NOT VERIFIED. Historical K1 and build259 NO-GO receipts remain factual; they are not a timeless prohibition on harmless host/source and file-copy work.

## 96. M4-B host-only source callsite census (2026-10-23)

**Evidence:** [source-census receipt](../evidence/m4b-gl-allocation-inventory-2026-10-23/README.md), [machine-readable callsite inventory](../evidence/m4b-gl-allocation-inventory-2026-10-23/summary.json), and reviewed [policy file](../tools/gl_storage_callsite_policy.json).

The policy scans all **390** `native/` and `framework/` C/C++ inputs in the patched build262 source tree, bound by source SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb` and overlay SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.

The scan found **77** storage, copy, framebuffer-attachment and EGL-surface callsites: **69 direct + 8 indirect**. The status ledger contains **12 wrapped+unmeasured** and **65 unknown**; no callsite is marked wrapped+measured or not reached. It binds the inventory to the source-tree digest and runs in `build_lamentum.sh` after overlay application but before compilation. A synthetic unclassified `glBufferData` path fails policy validation. The host suite after the generation follow-up passed **370/370**; see §97 for the generation-specific evidence.

**Limit / next:** the scan is a source-tree superset, not an exact compiler-unit/include-closure map; indirect NXGL candidates remain unknown. Host tests and the target CPU fixture do not prove game-runtime reach or transactional re-spec/delete/alias/context-loss/deferred-completion safety. No driver allocation, backing, RSS/CMA refund, gameplay or FPS was measured. This completes only the census substep, **not M4-B acceptance**. Next: prove exact compiler/include reach; complete the remaining identity/lifetime matrix; finish buffer/EGL owner accounting and the separated memory-class waterfall. The older `CmaFree=15,456 KiB` is historical; the fresh stable read-only pair and current D hold are recorded in §97. Build262 remains uninstalled because no per-run margin was authorized.

## 97. M4-B generation-history and capacity follow-up (2026-10-23)

**Implementation:** generation history now holds **2,048** `(share_group, name, kind)` keys (previous cap 512); the separate live-owner/subresource cap remains 512. History exhaustion and `UINT64_MAX` refuse new generation and increment `generation_history_overflow`; live-owner exhaustion increments `live_owner_overflow`. The counters are separately logged. Redundant per-row `seen` state was removed.

**Validation:** host tests cover 1,200 distinct/reused names, 1,024 create/delete pairs, 24 same-name reuses, identical GLuints across share groups, full-table and generation-wrap refusals, separate live-owner overflow, and storage/delete ring overflow. Focused lifecycle tests **10/10**, full tools suite **370/370**, source manifest **435/435**, inventory **77 sites** and pinned AArch64 build262 all pass. Static state and ELF `.bss` both increase **45,072 B** (host ledger state 155,504→200,576 B; ELF `.bss` 12,809,440→12,854,512 B); this is not a device RSS/CMA measurement.

**Target-side fixture:** a pinned-container AArch64 executable built from the build262 patched header passed on Longan (firmware 1.0.1, kernel 5.15.147, glibc 2.33): 22,432 B, max GLIBC 2.17, SHA-256 `f4da9806df30504a946ac7af45191451ff4564237be854744781b18b3978a2fa`, exit 0 in 0.183 s. It verified the 1,024 create/delete churn, 24 reuses, two share groups, capacity/wrap refusal, separate overflow counters and event-ring overflow. The exact device receipt is in the [M4-B evidence](../evidence/m4b-gl-allocation-inventory-2026-10-23/README.md); this was not the game ELF or a game run.

Build262 is a **2,206,936 B** AArch64 PIE, max GLIBC 2.27, SHA-256 `dd13d4ab300fdaa1f51acd78e105a55a02af1de6de05526328d2242b07da1cbc`; it remains **uninstalled**. Two read-only same-boot snapshots showed `CmaFree=130,412 KiB` stable over 44.009 s with no allocation-warning/swap-I/O deltas; the standalone target fixture passed, but no game runtime was launched. D remains held because `T2_STORAGE_MARGIN_MIB` is unset and no per-run margin was authorized. Generation/history overflow remains bounded and fail-closed. M4-B still needs exact compiler/include closure, context teardown/recreation epochs, full alias/view and transactional object lifetime, plus buffer/EGL owner accounting; gameplay and ≥30 FPS remain unverified. Full record: [detailed roadmap §17](../docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md) and [M4-B evidence](../evidence/m4b-gl-allocation-inventory-2026-10-23/README.md).

## 98. M4-B H1 pinned compiler-reach trace checkpoint (2026-10-23)

**Receipt:** [README](../evidence/m4b-compiled-reach-2026-10-23/README.md) and [machine-readable 77-site summary](../evidence/m4b-compiled-reach-2026-10-23/summary.json). Source identity remains the exact patched 390-file tree SHA-256 `1b995ea13bab7aa2afcf865f68006b095a401c3cc71b8321f83c778a052dabfb`; the adapter overlay is SHA-256 `6c549b09797a403390d4ced13e770bc35c65f74d70240a01f2ec77f6e258eba4`.

The pinned container reported compiler path `/usr/bin/aarch64-linux-gnu-gcc-9`, version **9.4.0**, target `aarch64-linux-gnu` (image tag ends in `gcc10`). The tracked wrapper and materializer captured **36** compiler invocations (35 compile, one final link), **45** translation units (43 C + 2 assembly), 45 per-unit dependency/preprocessor records, **275** project dependency paths, exact `-I`/`-D`/wrapper flags, and 32 object plus one archive link inputs. The build265 trace ELF is **2,206,936 B**, max GLIBC 2.27, Build ID `5c60e42b66321320580fb62e1801dd7ffa27b266`, SHA-256 `278612aab77012c09c3287f8e21a7fbb81dec3abea9eb81af60f6cba82e68b54`; it is uninstalled and is not a deployment candidate.

The 77-site compile/preprocessor axis is **58 compiled-reachable**, **11 compiled-unreachable** (eight `nxgl_gles2.c` candidates and three headers absent from all translation-unit dependency closures), and **8 unknown** (included source paths without an exact active line/token match). The final-link input axis is **66 confirmed** (all through direct link source `native/loader.c`) and **11 absent from link inputs**. The tracked wrapper/materializer regenerated build265's actual trace; the analyzer found **zero status delta** against the prior receipt. The 26 focused tests and full tools suite **396/396** pass. H1 is complete at source/compile/link-input scope; the eight unknowns remain explicit. The link uses `--gc-sections`, so per-function retention, runtime execution, allocation and backing remain unproven. No device action or game run occurred; the game goal and ≥30 FPS remain unverified.

## 99. M4-B H2 context-epoch lifetime contract checkpoint (2026-10-23)

The portable `native/lc2_lifetime.h` contract represents object identity as `(share-group epoch, context epoch, GLuint, kind)`, keeps ambiguous storage results pending/charged, and supports storage-only transactions without a fabricated completion timeline. A callback helper now drives the default-off, one-shot `MOMO_STENCIL_SELFTEST` texture/renderbuffer allocations: prior errors skip the call, clean `GL_NO_ERROR` commits logical bytes, and post-call errors remain unknown. Core tests are **7/7**, the mocked caller test **1/1**, and the full tools suite **403/403**. The exact source-census inventory remains 77 sites with 12 wrapped+unmeasured and 65 unknown, pinned to source-tree SHA-256 `76c87011069d987c3d0212a585ef07ca1848282c6e0af9fba46e148a99b8bd57` and patch SHA-256 `4a3599edcb1859f790e58f3354635e349fb1f7046289fc45dc1a6a47b2cc4494`.

The selftest's lifetime state is one-shot and not persistent allocation tracking. The pinned AArch64 mock fixture compiled, but the full game ELF build stopped on `ZERO_ZX_GAME` undefined and unrelated `-Werror` diagnostics; no game/device run or FPS evidence. Next H2 step is persistent owner-generation accounting at one real texture allocation path, with admission and deletion unchanged.

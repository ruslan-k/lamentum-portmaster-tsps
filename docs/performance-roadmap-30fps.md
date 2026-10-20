# Lamentum (TrimUI Smart Pro S): Roadmap to Stable 30 FPS

> **Current authoritative worklist: [§22 — source HEAD 2be834a, 42 shader entries, New Game frontier and FPS work](#22-head-2be834a-updated-post-shader-tail-audit-and-next-performance-plan-2026-10-20).** Sections 0–21 remain a historical audit trail. Recent code fixed several §21 tasks while exposing more shader-tail stops; do not follow older unfinished-task labels without checking §22.

**Latest decision:** [§20 — b1832de audit and execution plan](#20-head-b1832de-audit--actionable-next-iteration-2026-10-20) supersedes the previous priority order where the new shader blocker, test-harness contradictions and runtime measurements change the next action.

**Initial audit:** 2026-10-20; HEAD 4547117fb7b727bd7b8e12c68a2e3899a872c037; build202. **Latest source/evidence review:** main 964ffe5; see [§19](#19-current-head-reassessment-and-detailed-next-steps-2026-10-20). Sections 0–18 are retained as historical/reference guidance.  
**Purpose:** a detailed, actionable engineering roadmap, **not a claim that the target FPS has been achieved**.  
**Game status:** the real main menu, save slots, Options screen, and working UI navigation have been verified. **New Game, gameplay, audible audio, and save/reload have NOT yet been verified.** Functional verification must therefore precede gameplay performance claims.  
**Platform:** Nintendo Switch version of Lamentum, Unity 2019.4.4f1 with ARM64 IL2CPP; guest Horizon + NVN translated to EGL/GLES on the TrimUI Smart Pro S Mali-G57 running SpruceOS; 1280×720 display and approximately 1 GiB of physical RAM. No Box64 and no distribution of modified original game images in the repository. All modifications to the manifest-pinned, 435-file recovered runtime baseline must be applied through runtime/lamentum-adapter.patch.

**Latest reassessment, 2026-10-20 (main 51707cd8):** [Section 18](#18-post-roadmap-reassessment-2026-10-20) supersedes earlier status statements, implementation checklists and optimization priorities. Sections 0–17 preserve the original audit and are historical where they say that profiling/cbuf experiments were not implemented. The latest new results are exploratory, not verified gameplay FPS.

History, architecture, and contracts: [README](../README.md), [architecture](architecture.md), [UI constant-buffer binding](ui-cbuf-binding.md), [shader catalogue tail](catalogue-tail.md), [loading-memory research](loading-memory.md), and [porting log](porting-log.md). Historical entries must not be mistaken for measurements of the current performance baseline.

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

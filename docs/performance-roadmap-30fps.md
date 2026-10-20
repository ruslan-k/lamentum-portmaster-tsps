# Lamentum (TrimUI Smart Pro S): Roadmap to Stable 30 FPS

**Audit date:** 2026-10-20; HEAD 4547117fb7b727bd7b8e12c68a2e3899a872c037; build202.  
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

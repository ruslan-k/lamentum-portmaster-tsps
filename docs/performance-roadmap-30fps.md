# Lamentum (TrimUI Smart Pro S): Roadmap to Stable 30 FPS

**Audit date:** 2026-10-20; HEAD 4547117fb7b727bd7b8e12c68a2e3899a872c037; build202.  
**Purpose:** a detailed, actionable engineering roadmap, **not a claim that the target FPS has been achieved**.  
**Game status:** the real main menu, save slots, Options screen, and working UI navigation have been verified. **New Game, gameplay, audible audio, and save/reload have NOT yet been verified.** Functional verification must therefore precede gameplay performance claims.  
**Platform:** Nintendo Switch version of Lamentum, Unity 2019.4.4f1 with ARM64 IL2CPP; guest Horizon + NVN translated to EGL/GLES on the TrimUI Smart Pro S Mali-G57 running SpruceOS; 1280×720 display and approximately 1 GiB of physical RAM. No Box64 and no distribution of modified original game images in the repository. All modifications to the manifest-pinned, 435-file recovered runtime baseline must be applied through runtime/lamentum-adapter.patch.

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

## 13. P3 — другие варианты, которые нельзя делать вслепую

| Предложение | Приоритет/вердикт | Условие, которое оправдывает тест |
|---|---|---|
| Просто снизить physical SDL/KMS mode до 720 | Уже panel 720; это **не** Unity 1080 target | доказан owner internal scaling |
| Force Handheld вместо Docked / fake VI resolution | Не делать по аналогии с WoL: SDK/Unity разные | наблюдён call и verified consumer |
| glFinish bypass, fake command completion | ЗАПРЕЩЕНО для release, ранее был resource reuse stop | serial+fence ownership доказаны |
| Always enable async | Не default | significant sync waits + stage-level safety |
| Disable all ZRAM/fileback | Риск memory floor/OOM | продемонстрирован точный resident RAM headroom |
| T2_MEMORY_FLOOR_MIB=0 или снять GPU 420MiB cap | Нельзя использовать как FPS toggle | новая безопасная accounting model |
| Global sysctl/swapoff/forced clocks | Не предлагает performance fix | отдельная reproducible hardware cause |
| Remove bloom/UI/particle draws | Некорректный rendering | explicit reversible visual quality mode |
| Подменить shader TEST program нулевым цветом | Не годится для gameplay | shader semantically verified or guarded unused |
| Сгруппировать все draws одинакового shader | Опасно для alpha/depth/UI order | exact dependency and state equivalence |
| Rewrite runtime to Vulkan / direct DRM zero-copy | Долгосрочный R&D: огромный portability cost | доказан принципиальный GLES bottleneck |
| Native Unity ARM64 game build | Не доступен без source/engine-specific port | owner has rebuildable game source |
| Увеличить логирование для поиска FPS | Дополнительный overhead | bounded trace and quiet comparison |
| Играть через Box64 | Не подходит задачам native ARM64/Horizon, исключено | не рассматривать |
| Отключать kernel safeguards или patch proprietary image | Не требуется | никогда как незащищённый performance workaround |

## 14. Приоритетный execution plan с проверками и результатами

| Этап | ID | Чёткое действие | Выходной артефакт | Решение |
|---|---|---|---|---|
| P0 | F0 | New game -> управляемая сцена, звук, cold save/load | visual+state screenshots, exact binary, logs | нужен до FPS claims |
| P0 | B0 | Diagnostic vs quiet one-variable A/B | period/replay p50/p95, observer | пересчитать приоритеты |
| P0 | T0 | Timeline wall vs CPU vs wait, >95% attribution | CPU/gl queue/thread spans | устранить крупную задержку |
| P1 | M0–M5 | Guest compression cold/budget/fault A/B | safe headroom, fault stalls, frame P95 | оставить лучший или закрыть |
| P1 | C1–C3 | cbuf TexImage->guarded subimage/reuse | GL op count, CPU, pixel parity | только с cache generation |
| P1 | R1–R4 | samplers/GL state/VBO/FBO hotspot | replay stage timeline and paired A/B | только по фактической цене |
| P1 | G1 | owner 1080 target -> scoped 720p | same-scene screenshots and memory/FPS | если proven consumer |
| P1 | G2 | postprocess/bloom opt-in preset | explicit image quality vs perf | если GPU hotspot |
| P2 | M6 | residency/BC decode/ASTC side cache | verified object lifetime/cache hash | если significant pressure |
| P2 | Q1 | fences/async only when eligible | serial ownership proof | default OFF until passed |
| P2 | C4 | affinity/CPU/compiler opt-ins | clocks/thermal, P95 | no regressions |
| P0-final | A0 | extended gameplay, save/load, clean package | release acceptance evidence | freeze release flags |

**Распределение time budget — не общая сумма из medians.** На заключительном профиле для **каждого** кадра вычислить guest CPU, render CPU, waits, GPU completion, present, а затем сравнить p50/p95 distribution. Если чистый B0 даёт резкое ускорение из-за отключения диагностики, следовать актуальному bottleneck, а не историческим приоритетам. Если воспроизводимый gap ~400ms сохранился — T0/M0 выше shader tuning. Если gameplay значительно тяжелее меню, составить его отдельный список проблем.

## 15. Формат evidence для каждого PR: обоснование, воспроизводимость, откат

Делать один маленький opt-in feature/PR за раз. PR description содержит exact code lines, скрин текущего симптома, контрфактическую гипотезу («если CBUF повторяется, bypass сэкономит X ms»), **измерение X до изменения**, safety constraints, тесты и критерий исключения гипотезы. Не выставлять feature default=1 до полного acceptance.

Рекомендуемая структура, без game binary и пользовательских saves:

~~~text
evidence/perf-<ID>-<unique-tag>/
  README.md               источник, версия, сцена, намерение A/B
  identity.json           repo commit, baseline manifest hash,
                          ELF SHA256, owner image/section SHA256,
                          shader catalogue SHA256, device/OS identifier
  env-a.json              флаги, clocks/governor, memory envelope, phase
  env-b.json              ровно один изменённый фактор
  frame-a.csv             present serial, monotonic_ns, phase and duration
  frame-b.csv             те же колонки, provenance и missing samples
  observer-a.csv          CPU/TID, faults, RSS, PSS/SwapPSS,
                          MemAvailable, CmaFree, temp, swap IO
  observer-b.csv          те же показатели
  summary.json            p50/p90/p95/p99, counts and false/missing frames,
                          differences, outside confidence/noise limits
  screen-a.png            снято через реальный DRM, при живом game PID
  screen-b.png            эквивалентная сцена, original screenshot preserved
  cleanup.json            Game PID=0, MainUI=1, principal restored,
                          CPU mask original, no leaked subprocesses
~~~

**Строгий процесс**: source+image pin -> verify build/test -> backup working binary & saves -> check idle device/disk reserve -> run A -> cleanup proof -> run B -> cleanup proof -> repeat matched pairs -> analyze distributions -> human review screenshots/input/audio/save -> decide default/rollback. Структура Git evidence не должна включать оцифрованные NSO fragments, RomFS, keys, user save data и необработанные original shader blobs.

**Цифры:** throughput=number_of_presented_frames / measured_steady_elapsed_seconds, median fps=1000/median_period только как отдельная статистика, **не** воспринимать как panel FPS без подтверждённой кадровой последовательности. Считать P95/P99 spikes и missed vsync; отбрасывать startup и scene transition только **в отдельный отчет**, не скрывать плохие лаги gameplay. Презентация в 60Hz может требовать равномерной выдачи одного игрового кадра за два scanouts; внутри 30 FPS кадр <=33.333ms (с учётом очереди и джиттера). Указать sample frame count, time window, phase, loading fraction and instrumentation overhead.

**Пререквизиты и host tests:** sha256sum -c tools/baseline-manifest.sha256, все доступные tools/test_*.py и C host fixtures из репозитория, UI cbuf replay test, launcher CPU restore test, shader append-only test, GL texture lifetime/invalidation tests. Полный AArch64 cross-build в pinned container и read-back SHA256 установленного ELF; при любых отказах использовать сохранённый предыдущий бинарник. Скрипт tools/device_principal_test.py сейчас не является универсальной лабораторией: он использует owner-specific SSH/device path и MainUI handoff; адаптацию нужно делать в контролируемом owner workspace и не запускать вслепую на чужом устройстве.

## 16. Definition of done и stop criteria

**Не объявлять 30 FPS достигнутыми, пока:**

1. Версия ELF и owner-generated image действительно достигает воспроизводимой настоящей игровой сцены, её можно контролировать физическим TSPS controller, правильный KMS 1280×720 вывод без пропадающего текста/пунктов меню, stencil, lighting, bloom, alpha и wrong cbuf.
2. Есть настоящие audible sound/SFX, inventory, диалог/interaction, save -> quit -> cold start -> load и подтверждённое сохранённое состояние, корректное завершение и MainUI/CPU restoration.
3. Имеется **не менее трёх** независимых warm-scene runs по 60 секунд каждое, в одинаковых состояниях и при измеренных clocks/thermal; отдельно stationary и moving routes, effects/interior и transitions. На gameplay **P50 <=33.33ms и P95 <=33.33ms** full frame; P99 <=50ms целевой дополнительный порог, без регулярных >100ms зависаний. Если строго P95 33.33 не достигается — статус «не достигнуто», даже при средних 30.
4. Для A/B зафиксированы latency breakdown, diagnostic overhead, real presented throughput и исключены визуально неверные/потерянные кадры. Нет необходимости искусственно ускорять guest clocks или игнорировать shader/resource errors.
5. MemAvailable/CmaFree, SwapPSS, system major faults, temperatures не демонстрируют опасный тренд; нет OOM, kernel crash, сломанных save files или остаточных процессов. Производственный memory floor/flags отдельно доказаны, а не скопированы из 32MiB diagnostics.
6. Source parity проверена (baseline identity, adapter patch, GLSL source catalogue, конкретный ELF); собранные evidence доступны, проигравшие варианты имеют честный OFF/rollback.

**Stop rules для отдельного performance feature:** FPS различия в пределах run-to-run noise (после 3 A/B), выигрыш replay полностью переехал в GPU wait, потеря ресурса/текста/UI, memory floor/OOM, нарушение CPU restore, неизвестная зависимость guest buffer, неверный shader program identity. Тогда **не** добавлять flag в release, сохранить evidence и закрыть гипотезу.

## 17. Внешние материалы и порядок следующей работы

- [West of Loathing optimisation-roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md) и [2026-10-16 measured frame breakdown](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): проверенная методика измерений, feature flags и доказательства, что owner-level Unity 720p может помочь; *не* готовый port-specific patch Lamentum.
- [Arm Mali: framebuffer handling](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/mali-performance-2-how-to-correctly-handle-framebuffers): использовать load/store/invalidate лишь с просчитанной dependency и tile-based lifetime.
- [Mali tile-based rendering guide](https://documentation-service.arm.com/static/636dfb934e6cf12278ad8c27): внешняя документация, не устройство-специфический benchmark.
- Existing [UI cbuf binding](ui-cbuf-binding.md), [cbuf isolation](cbuf-unit-isolation.md), [shader literal bank](shader-literal-bank.md), [probe-disabled fragment](probe-disabled-fragment.md), [shader tail](catalogue-tail.md) и [loading 170–174](loading-memory-170-174.md) содержат применимые exact provenance и previous failure boundaries.

**Рекомендованный следующий эксперимент — не ещё один shader tweak:**
(1) подтвердить New game и игровую корректность F0; (2) получить clean performance B0, иначе цифры build202 нельзя интерпретировать; (3) измерить wall+CPU timeline T0, установить природу ~400ms; (4) если compression действительно платная — M0–M4, иначе сразу CBUF/replay c конкретным ms профилем; (5) после этого owner-specific 720p (если 1080 target окажется критичным). GPU bloom, ASTC, async и compiler — при фактическом профиле и с жесткими gates.

**Примечание о выполнении:** весь этот roadmap создан по source/evidence аудиту GitHub; новых handheld запусков, 30 FPS замеров, patch игрового ELF, hardware deploy или тестов на устройстве в ходе аудита **не выполнялось**. Данные build202 подтверждают проблему, а шаги выше пока являются инженерными гипотезами и планом их проверки.

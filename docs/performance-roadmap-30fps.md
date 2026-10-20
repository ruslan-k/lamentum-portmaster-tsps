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

## 7. P1-REPLAY — где именно тратятся 97–236 ms replay

**Место внедрения:** базовые native/nvn_replay.h, native/nvn_render.h, native/nvn_samplers.h, native/nvn_shaders.h, native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_commands.h, native/nvn_queue.h; изменения — только в runtime/lamentum-adapter.patch. Реальная измеренная цена каждой функции **не известна**. Пример WoL-методики: [roadmap-roundup](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): в **другой** игре разбили replay на first texture resolve, state changes, memory transfers и shader cost. Переносить можно **метод**, а не ms или конкретный patch.

### 7.1. Сначала low-overhead profile

Добавить LC2_REPLAY_PHASES=1 с per-frame/per-program/per-operation агрегированием, без подробного stdout на каждый GL call. Для каждого command-list и serial зафиксировать следующие exclusive CPU ns и counts:

- queue snapshot/record parsing / guest->host command copy, command count и bytes;
- draw dispatch до GL: sampling handle decoding / descriptor lookup / texture lifetime; отдельно first-resolve и повторный resolve идентичного ключа;
- zero_texture_refresh: время BC decode, memory copy, glTexImage/Upload, dirty flags, bytes, allocation and GPU budget;
- shader lookup (catalogue hash), compile/link и shader switch; program bind, uniform location lookup;
- cbuf GPU upload (см. §6), sampler state, texture bindings, framebuffer attachment/lookup/rebind, depth+stencil, blend, scissor, viewport;
- vertex/index: extract guest range, format conversion, malloc/realloc/copy, glBufferData/glBufferSubData, draw GL API call overhead;
- non-draw records: TextureWriteTexels, clears, render target switches, barriers, buffer copies, command reuse, resource creation/deletion;
- **все** glFinish/GLsync/eglMakeCurrent, время scheduler wait/CPU thread time отдельно от GL completion.
  
В конце окна печатать примерно: frame range, total replay CPU wall, host thread CPU, non-draw / draw, per-op count, bytes and inclusive/exclusive durations; диагностический журнал допускает одну строку каждые 60 кадров плюс on-exit. Подтвердить missing bucket <=5% в пределах replay. Гистограмму не усреднять только по удачным frames: включить P95 и rare >100ms. Фаза shader first-use должна быть отдельной от steady-state.

### 7.2. Кандидат A: быстрый повторный sampler/texture resolve

Если значительны одинаковые handle resolve, внедрить **bounded** per-context cache с ключом: texture pool ID/generation, descriptor index, sampler ID/generation, view format, mip, layer, swizzle, target type, backing modification generation. Cache hit допускается только при сохранённом guest descriptor и GL texture lifetime. На TextureWriteTexels, texture pool unregister/re-register, free, recreate, framebuffer aliasing и context loss — invalidation. В частности нельзя reuse old texture после write в тот же memory pool по одному совпадению handle.

Проверить на первом/втором resolve одного handle, затем на полном кадре. Output: hit/miss, invalidations, correctness, CPU p50/p95, GL allocations. В WoL first per-frame resolve оказался дорогим, но **нет доказательства** такой же причины в Lamentum. Не внедрять cache вслепую.

### 7.3. Кандидат B: GL state shadowing

Добавить точную per-EGL-context shadow state таблицу для текущих shader/program, active texture unit, GL texture bindings на каждом unit/target, GL FBO, GL array/element buffers, blend/scissor/depth/stencil, viewport. Перед вызовом проверять identity+generation, но **действительное состояние** между guest shader passes может меняться в native present, diagnostic draw и FBO helpers. Каждый неучтённый внешний GL entry должен инвалидировать соответствующую часть кэша, иначе будет графическая регрессия.

Сначала только telemetry «would_skip_calls» без изменения поведения; затем оптимизировать **один** вызов/семейство. Сравнивать GLenum errors, real KMS captures, guest state parity и whole-frame latency. glGetIntegerv/glCheckFramebufferStatus нужны для bounded diagnostic, но не должны стать частью нового hot path.

### 7.4. Кандидат C: buffers и per-draw allocations

Собрать live counts realloc/malloc/free, glBufferData vs glBufferSubData, amount of vertex/index copying и сколько раз identical guest byte range преобразуется повторно. Если churn действительно велик — persistent VBO/IBO ring / preallocated scratch и cache conversions с identity, source write epoch и proper GL in-flight fence. Для динамического UI/stencil/particle geometry не считать одинаковый адрес guest memory неизменными данными. Мерить RAM delta: оптимизация CPU не должна удвоить resident memory и спровоцировать ZRAM faults.

### 7.5. Кандидат D: framebuffer/pipeline transitions

Проверить per-frame FBO cache hits/misses/rebinds, RT attachment validity, render-pass boundaries, repeated glCheckFramebufferStatus and glGetError; отделить **diagnostic** проверки от обязательной validation. Tile-based Mali может выигрывать от уменьшения render-target switches и лишних stores, но любой glInvalidateFramebuffer допустим только после последнего чтения attachment; иначе разрушится bloom/UI/final composite. Включить preserve/restore текущего FBO после readback diagnostic.

### 7.6. Batching и ограничения

Объединять draw commands можно лишь при **доказанном** совпадении target, ordering, texture/UBO, blend, viewport/scissor, alpha, depth/stencil, fragment side effects и no memory barrier. Пара 12/14 может рисовать 9 отдельных UI объектов на кадр — нельзя объединять просто по имени program. Сначала census потенциально совместимых consecutive draws с сохранением guest order и per-frame visual diff; далее experimental batch в opt-in branch.

**PASS:** уменьшение **общего** period P95 (а не только replay CPU, который может перейти в GPU finish); KMS/GL parity, no resource-generation races, одинаковые saves. **STOP:** новая строка STOP, wrong stencil/UI, shader remap или неизвестное владение объектами.

## 8. P1-720 — определить владельца внутреннего 1920×1080 и тестировать 720p

**Факт:** на физическом 1280×720 panel встречаются NVN draw targets **1920×1080** (например UI 12/14 и pair 11/9). В 1920×1080 ~2.25 раза больше pixels, чем в 1280×720. Потенциальное сокращение raster/workload ≠ автоматически 2.25× FPS. При диагностических 400 ms вне replay внутреннее разрешение может быть второстепенным.

### 8.1. Найти источник размера, а не угадать

1. В low-overhead trace выделить resource IDs для всех 1920×1080 RT, initial NVN TextureBuilder, memory pool owner, target flags/format/MSAA, attach/reuse/readback, number of draws/frames, framebuffer and sampler consumers; отдельно отметить конечный 1280×720 screen и postprocess.
2. Read-only анализ оригинальных IL2CPP metadata + main NSO в owner workspace: поиск сериализованных component fields/MonoBehaviour и native call-sites (Unity Screen.SetResolution, RenderTexture.GetTemporary, new RenderTexture, CanvasScaler, player graphics settings). Это **список для поиска**, не утверждение, что названные API вызываются этой игрой.
3. Сопоставить события и значения **1920, 1080**, возможные reference resolution / render scale / dynamic resolution, последние изменения UI projection. Изучить Options (в build202 экран виден) на реальные настройки resolution/effects. Не считать handheld/TV request источником внутренних размеров без trace.
4. Сформировать original->candidate матрицу: размер RT, viewport/scissor, matrices/UBO, sample UV, text/UI point size, input hitboxes, LOD and postprocess dependency. При mode change запрашивать полную reallocation resource family, не изменять размер объекта под старой descriptor identity.
5. Если найден **owner-specific** компонент, внедрить *guarded* optional override его значения на 1280×720/scale 2/3 только для Lamentum с точным main NSO/metadata SHA. Изменять owner file в публичном репозитории нельзя; adapter должен либо корректно и проверяемо менять временную копию state, либо описать owner-local patch workflow.
6. Если owner component не найден, рассмотреть backend virtual resolution translator (logical 1920x1080 -> physical 1280x720) только с полным преобразованием FBO sizes, render/copy subrectangles, texel offsets, shader sampling LOD, viewport/scissor, clipping, UI pixel snapping, pointer coordinates и all render-target consumers. **Это дорогой/high-risk вариант**, не первая попытка.
7. А/B: original 1080 -> 720, затем отдельный 960×540/640×360 quality preset только при приемлемом UI. Желательно оставить UI native-res, менять лишь scene/lighting intermediates и применять upscaler после verify.
8. Проверить actual KMS frames из title, main menu, Options, inventory, moving scene, bloom/highlights, text readability, clip/stencil; сравнить actual GPU memory and GPU query time, CPU replay, P95 period, startup memory.
9. При повторной сборке shader catalogue **не** возвращать build201 c4 binding0. Учитывать уже выведенную projection UI ~2/1920,2/1080 в 160-byte UBO1: простое resize RT при неизменённой matrix может скрыть текст.

**Сравнение с WoL:** там конкретный owner Unity UpRender (которого существование в Lamentum НЕ установлено) позволил улучшить measured FPS от ~24 до ~33–34 в одной сцене. Нельзя переносить field offsets, title hashes и выводы о docked mode из [WoL roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md). Измерить источник **самой Lamentum**.

**PASS:** owner-visible pixel/interaction correct, repeatable whole-frame gain при одинаковой scene+clocks и memory safety. **STOP:** смазанный текст, screen/input misalignment, неправильная альфа или unresolved resource alias.

## 9. P1-POST — bloom/noise/post-processing на Mali

**Точки:** NVN pair17/4 -> 10-level downsample targets, 11/9 composite/near-composite и final present; нужны actual pass dependencies. Опциональная UI настройка Noise effect уже доступна; **не утверждать**, что она отключает bloom.

**Методы в порядке цены/риска:**

1. Создать граф per-pass: input texture IDs, output RT/format/size, draw count, shader pair, clear/load/store, following users, aspect ratio; пометить lifetime каждого промежуточного attachment.
2. Измерить cost каждого pass CPU и GPU, если Mali/EGL поддерживает EXT_disjoint_timer_query (иначе report not available). GPU timestamp профилировать редко и проверять disjoint; glFinish после каждого pass исказит результат.
3. Сначала встроенная настройка Noise effect On/Off и, если существует, brightness/shadow/effects presets — одна настройка на run, same scene; оценить actual frame delta и KMS quality. Изменение noise ≠ автоматическое отключение blur/lighting.
4. Если дорог **именно** bloom: quality tier через строго установленные guest shader uniforms/source-provenance, уменьшить число уровней downsample (напр., 10->6 только когда final consumers перестают ссылаться на хвост), sample taps/radius или resolution **без изменения оригинального mode**. Следить за alpha, color space/sRGB, temporal effects.
5. Если дорог FBO change: grouping безопасных последовательных pass, reuse FBO objects, remove redundant state binds. Mali tile discard/invalidate только после последнего reader; no blind glInvalidateFramebuffer. Не вводить искусственное выключение glBlend/glDepth/glStencil.
6. Компонентные тесты shader: exact code+control hash; mat/UV/texelFetch coordinates, shader literal bank и sampler metadata остаются pinned. Снять изображения для темных/светлых сцен и меню, а не только pixel count.
7. Продвинуть quality option Original/Performance **только если** эффект на реальном игровом профиле заметен и качество согласовано; по умолчанию оставить original until accepted.

**PASS:** корректный performance preset с измеренной экономией GPU/frame-time и обратимостью. **STOP:** едва видимый интерфейс или эффект иного цвета/сломан bloom, выигрыш <= noise.

## 10. P2-GPU-MEM — оптимизация BC atlas, GPU residency и загрузки

**Подтверждённые существующие решения, которые не надо заново «изобретать»:** BC3 atlas 8192×4096, 128-row stripes вместо полного 128 MiB RGBA transient, deferred BC upload, lossless file backing после полного write, bounded GPU texture budget **420 MiB**, earlier load floor experiments (см. [loading-memory](loading-memory.md), [loading-memory-170-174](loading-memory-170-174.md)). Компрессор guest pages и file-backed bytes нельзя просто складывать.

1. Новая telemetry таблица resource ID -> guest pool alias and write epoch -> decoded/resident GL texture and format/mips -> actual last use/first use, create/destroy timestamps. Считать unique guest backing ranges по **union**, не по сумме virtual spans; GPU committed bytes не приравнивать к process RSS/PSS.
2. Профилировать именно повторную zero_texture_refresh / LC2_BC_MATERIALIZED и TextureWriteTexels: allocation, BC3 decompression, GPU upload, driver CPU time, stalls, pages read from backing. При повторной materialization искать invalidation loop / dirty range. Exact write-range epochs плюс generation IDs для проверки skip reupload.
3. Оптимизировать полноразмерные uploads только при строгом immutable-content proof. Если атлас часто меняется, partial dirty region upload через glTexSubImage2D вместо полного, с проверкой BC tiled decode, aligned compression blocks, surface pitch/stride, mip and swizzle.
4. Проверить natively supported compressed texture formats **на устройстве**: GLES extensions и независимый pbuffer upload/readback. Возможность ASTC на другом порте West of Loathing не гарантирует BC3->ASTC поддержку/качество и библиотеку на Lamentum.
5. Если supported, owner-local **content-addressed** ASTC side-cache для небольшого allowlist неизменных atlases: source SHA, exact dimensions/mip/format/color space, deterministic encoding quality, correct alpha, room on SD, fallback to existing lossless BC path. Не публиковать proprietary texture/payload; при mismatch never cache hit. ASTC может быть **lossy**, это отдельный quality gate.
6. Для inactive textures: не делать eviction/decommit guest bytes из pagemap zeros или таймера. Требуется реально доказанный owner lifetime + reconstruction path + no in-flight framebuffer/sampler readers, новый generation and fence. 420 MiB GPU cap не отключать.
7. I/O traces: SD/UDISK fileback cap/latency, statvfs disk free reserve, blocked pread, page faults, deferred upload. Стратегия background prefetch допустима только если guest dependency/barrier и RAM safety установлены.
8. Сравнить menu->New game transition, one interior and combat/effects phase, not raw count textures initialized; memory floor=32MiB не становится автоматически default.

**PASS:** меньший P95 stalls/real GPU residency при корректной scene/texture colour и сохранённом headroom. **STOP:** memory floor, corrupted texture, aliases, long disk stalls, GPU OOM. Не заставлять устройство swapoff.

## 11. P2-SYNC — NVN queue / GPU pipeline без небезопасного early completion

**Исходно:** COTM_ASYNC_QUEUE=0 и T2_GPU_PIPELINE=0 — измеренный стабильный синхронный путь. Ранее был NVN_COMMAND_REUSE_BEFORE_COMPLETION; SDL/KMSDRM recreates EGL surface after first fullscreen swap, что уже обрабатывается [loading-memory](loading-memory.md). COTM_FB_PRESENT=0, strict GL errors; без новой работы не переключать на framebuffer-copy путь.

1. После §4/§7 получить **все** GPU waits, resource producer/consumer and command serial; выяснить, есть ли >значимый CPU idle, когда GPU занят, и достаточно ли резерва RAM на async queue.
2. Для каждой command list: generation, writer publication, reader replay start/end, resources touched, GPU submission completion, first allowed recycle. Составить serial ownership contract; тест на повторное использование арен до fence, stale pointer, context loss и wraparound.
3. GLsync/fences: проверка GLES3/extension support, insert fence **после** producer commands, glFlush as needed, explicit client wait/complete event, never mark completed simply because producer thread dispatched. Fence object lifetime and GL context ownership должны быть проверены.
4. Сначала separate opt-in experiments COTM_ASYNC_QUEUE=1 vs 0, затем T2_GPU_PIPELINE=1 vs 0, а потом 1/1 при прошедших independent tests. Для каждого variant backed-up binary and known-good revert, test idle/UI/moving and scene transition.
5. Track output full-frame and P95, not short local replay ns; если stalls переедут в glFinish или возникнут lost/black frames, это не улучшение.
6. GL state per context must be explicitly invalidated on surface recreate, render/present context handoff, shader resource recycle; не игнорировать EGL_BAD_SURFACE, не подменять GPU completion timestamp CPU time.
7. Если стоимость sync мала, оставить верный synchronous path и закрыть пункт OFF: не тратить время на параллелизм ради потенциальных +0–1ms.

**Hard STOP:** NVN_COMMAND_REUSE_BEFORE_COMPLETION, NVN_QUEUE_CONTEXT, NVN_PRESENT_CONTEXT, EGL_BAD_SURFACE, black/tearing, stale uniforms or command memory reuse.

## 12. P2-CPU — scheduling/affinity, Unity и compiler flags

**Реальные наблюдения:** HOST_CPU_AFFINITY guest-main cpus=0; runtime launcher временно включает CPU0–3 и восстанавливает их на EXIT. Нельзя предполагать «core0 медленный» без системных данных. Spruce/OS может иметь свою раскладку CPU, thermals and governor.

1. Снять /sys/devices/system/cpu/{online,cpufreq/*}, доступные per-core freq, topology, /proc/TID schedstat, thermal and throttling while running. Сравнить guest CPU thread time vs runnable delay and zram CPU. Сбор извне, не forced clocks.
2. One-factor A/B affinity: pinned0 vs exact allowed healthy core(s) vs scheduler; **не** менять Horizon guest semantics и приоритеты без trace потока. Сохранять initial online mask и восстанавливать в любых exits/errors; CPU reallocation не должна повреждать input/audio threads.
3. Sampling native guest PC/callgraph с read-only symbol/IL2CPP lookup (hash-pinned owner image) — only if large guest CPU time. Узкие SVC stubs/TLS/IPC locks/memcpy/allocator paths оптимизировать с ABI parity, property tests и no title patch.
4. Compiler: проверить actual native/build.sh команду baseline и wrapper tools/cc-lamentum.sh (сейчас вызывает GCC with inherited flags, -DZERO_ZX_GAME=0). После baseline смотреть -O2 vs -O3, LTO, PGO только при отсутствии correctness issues, full source-parity and owner-local representative profile. Сравнить cold compile, binary size, RSS, compile errors, debug metadata, safety checks.
5. Texture/shader interpretation in guest может быть горячим: hash lookup/format conversions/GLSL compile, только если §7 показывает регулярную нагрузку. При уже pinned static shader literal specialization нет смысла заново делать эту оптимизацию.
6. Не рекомендовать постоянное изменение CPU governor, разгон, undervolting, min_free_kbytes, swappiness и zram swapoff: hardware, battery/heat, safety и результаты предыдущих неудачных memory probes — отдельные факторы.

**PASS:** повторяемые выигрыши full-frame P95 в реальном gameplay, no temperature/sound/input regressions and restored Spruce CPU mask.

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

# Lamentum TSPS — Build219 Gameplay Bring-up and Performance Action Plan

**Audit:** 2026-10-20. **Repository HEAD inspected:** [19dc04644d6381dd9c4921500116c21333914295](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/19dc04644d6381dd9c4921500116c21333914295). **Installed build219 ELF SHA-256:** `b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a`, according to committed [load-probe-10](../evidence/load-probe-10/summary.json). This is a source/evidence audit, **not a new device run, compiled ELF, or claim of playability or 30 FPS**.

**Read alongside:** [main 30 FPS roadmap](performance-roadmap-30fps.md), [previous current gameplay plan](current-gameplay-performance-plan.md), [G0 ledger](gpu-ledger.md), [CPU/SVC attribution](load-cpu-attribution.md), [build218 fragment45](build218-entry45.md), and [New Game bring-up](newgame-bringup.md).

## 1. Updated repository assessment: implemented versus unverified

| Item | Verified current state | Work remaining |
|---|---|---|
| UI | Real title/menu, Options, New Game configuration, controls and Loading reached with PID/KMS-based navigation | No actual controllable world or cold save/load |
| Shader catalogue | 46 entries, indices 0–45; seven TEST substitutes; fragment45 and vertex44 appended with pinned source identities; fragment45 linked | A link receipt does **not** prove four MRT outputs or correct gameplay pixels; TEST substitutes may be reached later |
| Memory optimizations | BC3 128-row streaming decode, deferred first-use uploads, owner-local fileback, guest ZRAM, texture budget, CBUF TexSubImage | Large decoded GPU RGBA storage still causes memory wall; no verified compressed storage path |
| Mali OOM | newgame-20 and load-probe-03 correlated with kernel/Mali OOM around 725,992 KiB GPU accounting | Precise live driver owners not yet established; do not infer a leak |
| Guarded experiments | load-probe-04/07/08/09 stop safely with T2_TEXTURE_BUDGET_MIB=300 | Blocked before gameplay by id=295 first-use 8192x8192 RGBA reservation of **256 MiB**; charged storage ~155 -> 411 MiB |
| Newer G0 samples | build219 load-probe-10: texture-live plateau ~126 MiB, process VmSwap ~870 MiB, MemAvailable ~67–84 MiB in sampled phase | This operator-TERM run did **not** reach/resolve the later id=295 allocation; RSS/VmSwap do not name a memory owner |
| CPU evidence | load-probe-08: 400 MOMO samples; SVC 0x1A=5506, 0x1B=5389; IPC endpoint0x40 cmd8=29140, cmd7=10376 | Actual per-call CPU cost, IPC service identity, handler PC symbolism and synchronization correctness unknown |
| Prior Loading CPU | build217 separate 20.14 s window: 0.836 CPU s main-thread and 1.63 total CPU s per presented Loading frame; zero new RomFS/texture events | Not the build219 gameplay rate; a likely severe issue if representative, but cause not proven |
| Tools | Current load_metrics.py has complete-byte-line framing, opened-file dev/inode cursor, synthetic rotation/UTF-8 tests; load-probe-09 validated live counters | Correct remote CPU ticks in perf_sample.py, run-identity and PID reuse guards, semantic New Game page detection |

**Caution on the hottest-looking sampler statistic:** MOMO sampled **32 threads roughly round-robin** (12–13 samples each). Thus 387/400 `in-kernel` samples are **not** a calibrated 96.75% CPU-time share. The common native PCs `0x7fa15b0bd4` and `0x7fa15b0bd8` must be mapped using a **same-run** `/proc/PID/maps` and the actual ELF. A frequent signal-handler sample is not sufficient to establish the CPU time of that path.

## 2. Critical path, priorities and non-negotiable safety

**Two P0 lanes:** G (GPU/guest memory ownership and safe residency reduction) and C (SVC/IPC handler and actual CPU cost). They can be coded concurrently off-device but only **one** board principal-flow experiment may run at a time. W (world validation) depends on progressing safely through loading. F (steady-world FPS) depends on working world, physical input, audio and saves.

Before any board run: back up owner save data and the last good ELF, pin game image + shader catalogue + adapter source hashes, verify idle Spruce MainUI, capture original CPU mask, confirm fileback reserve, require exact game PID/starttime, start external bounded watchdog, use proven safe **300 MiB diagnostic texture budget** and disk-compatible **512 MiB fileback cap**. The 32 MiB general memory floor is still **diagnostic only**, never a qualified release default. Do not increase to the previously OOM-triggering texture environment for convenience. Validate MainUI restoration and CPU mask after every exit.

**Success has distinct levels:** (1) trustworthy measurement, (2) memory-safe progress beyond the formerly failing resource, (3) correctly rendered scene and actual player state, (4) fully playable (pad, audio, interactions, saves), (5) measured performance. No number of Loading-spinner presents satisfies levels 3–5.

## 3. PR T1 — finish instrumentation identity and correct the CPU observer

**Files:** `tools/perf_sample.py`, `tools/load_probe.py`, `tools/load_metrics.py`, `tools/device_principal_test.py`, `tools/newgame_navigate.py`, `tools/test_load_metrics.py`.

1. **Keep completed work:** load_metrics.PAYLOAD opens `latest.log` in `rb`, fstats the opened descriptor and consumes only bytes through the final newline. The existing test suite covers partial records, split invalid UTF-8, a new inode at equal-or-larger length and truncate/regrow. Re-run tests; do not rewrite this as a TODO or replace with a repeated full-log scan.
2. **Fix real perf_sample.py defects:** return the **device** `os.sysconf('SC_CLK_TCK')` in the remote sample, and compute `cpu_ms_per_s = 1000 * delta_ticks / (device_HZ * elapsed_s)`. Host HZ is not device HZ. Decode `/proc/PID/stat` by finding the final `)` delimiting the parenthesized `comm`, then indexing the subsequent numeric fields. The current `.split()` implementation is not safe for unusual comm strings.
3. **Fix PID and TID reuse:** key owner process by `(boot_id, run_uuid, pid, starttime, installed_ELF_sha)`; key threads by `(tid, thread_starttime)`. If a thread disappears, skip its delta rather than manufacturing negative CPU. Collect `utime/stime`, `schedstat`, `wchan`, minflt/majflt and owner-verified state. Sample `smaps_rollup` much less frequently than `stat`.
4. **Join log and memory windows:** each collector sample needs the same owner PID/starttime and log `(dev, inode, consumed_bytes)` generation. Do not merge different runs after a log rotation even when the new log has already grown past the previous byte offset. A fixed present serial does not prove the loader is stalled when textures or scene milestones still advance.
5. **Correct stop attribution:** T2_TEXTURE_BUDGET and other runtime STOP, explicit host-TERM, SIGKILL without corroborating dmesg, and verified kernel/Mali OOM are separate results. A literal `Killed` proves neither the GPU victim nor the causal allocator. Mark `LIVE`, `STOPPED` and `POST_EXIT` memory samples separately; exclude post-kill MemAvailable rebounds from pre-stop minima.
6. **Make configuration-page navigation semantic:** load_probe.navigate still uses two fixed Down presses after New Game and judges subsequent navigation by a >=120 changed-cells threshold. Use page-specific cursor/selection state and the actual new frame serial for `MENU -> NEWGAME_CONFIG -> CONTROLS -> LOADING`; reject unrelated content changes. Preserve EV_KEY305 confirm, 304 back, release receipts and bounded retries.
7. Test remote HZ=100/250/1000, parenthesized comm, PID and TID reuse, end-of-run STOP, partial UTF-8/new inode, fake `Killed`, stale logfile, unchanged frame serial while loader counters advance, and unexpected config-page transitions. Unit tests must not SSH to the real device.
8. Run one bounded **safe 300 MiB** end-to-end control after host tests. Pin installed ELF and compare incremental counters against the raw log, with a correct STOP classification and clean MainUI/CPU-mask restoration.

**Deliverable:** `evidence/T1-.../identity.json`, `samples.jsonl`, `stop.json`, `cleanup.json`, test output and a per-thread target-correct CPU report. Do not count creating new log formats as a performance fix.

## 4. PR C1 — identify SVC 0x1A/0x1B and actual endpoint0x40 owner

**Reference:** [libnx svc.h](https://github.com/switchbrew/libnx/blob/master/nx/include/switch/kernel/svc.h) documents **0x1A svcArbitrateLock** and **0x1B svcArbitrateUnlock**. Never replace synchronization with unconditional success, global sleep suppression or a guessed guest-thread priority change.

1. In the adapter's SVC/SIGTRAP dispatcher, add **bounded and opt-in** aggregation for caller `(module, text offset)`, guest thread/TID, mutex address, lock owner tag, arguments, return code and path: uncontended, contended/wait, wake, error. Keep counters per distinct exact opcode.
2. Measure **exclusive CLOCK_THREAD_CPUTIME_ID** and wall/monotonic intervals for trap entry, SVC emulation, host mutex, guest-memory access and return; record total ns, mean, P50/P95/max per class. Exclude time blocked waiting from executing CPU. A log line emitted on every SVC would bias this measurement.
3. Resolve native `0x7fa15b0bd4`/`0x7fa15b0bd8` only with a same-run `/proc/PID/maps` capture and ELF/DSO load offsets. Map the GPL adapter with `addr2line` when possible; record unknown module+offset instead of inventing a symbol. Derive aggregate CPU share from **per-thread CPU ticks or calibrated on-CPU sampling**, not round-robin sample percentage.
4. Track service acquisition (`sm`, ConnectToNamedPort/session/handle creation, duplication, IPC close). Resolve **endpoint 0x40** to actual service/session identity in *that run*. Bucket type6 commands **7 and 8** by request parameters, actual result, returned fields, timeout and whether state changes. High counts can reflect legitimate work or polling; the handle number does not identify a service by itself.
5. Correlate a sampled main guest loop with one `0x1A -> 0x1B` sequence and commands 7/8; report mutex owner change, wakeups and useful scene work. Validate whether `0xffffffff` observed in the key distribution is a real sentinel only after its register/ABI role has been established.
6. Create a synthetic arbitration fixture for lock/unlock, contention, wake priority/order, invalid handle/address, cancellation/timeout as supported and thread exit. Preserve all guest-visible results and memory ordering.
7. Run same-ELF A/B **trace OFF vs aggregate ON** to quantify probe overhead. Only if direct measurements show it dominates, prototype a narrow correct uncontended/bridge fast path or **service implementation** fix, guarded by the measured caller and version. Do not speed up a deadlock by faking a result.
8. Measure CPU seconds **per meaningful Loading milestone**, complete elapsed time, scene progress, mutex failures and cleanup—not just spinner FPS.

**Quantitative consistency check:** `load-probe-08` logged **10,895** SVC 0x1A/0x1B across **364** additional presents (~30 per present). An **earlier different build/phase** reported 0.836 main CPU seconds/present. Explaining that entire cost by these ~30 SVCs would require **~28 ms of executing CPU per call**. This is only a hypothesis bound, **not a measured call latency**; the 41,862 IPC events need their own non-double-counted attribution.

**PASS:** per-call CPU cost and service identity are resolved, with a demonstrable costly path and a semantics-preserving fix that improves actual loader progress. **STOP:** missed wakeup, false arbitration result, semantic drift or unexplained resource ownership.

## 5. PR G1 — attribute id295 and all live GL storage; do not diagnose from VmSwap

**Code path:** `runtime/lamentum-adapter.patch`, especially `native/nvn_textures.h::{nvn_texture_dispatch,zero_texture_refresh,lc2_bc_upload_stripes}`, GL resource/framebuffer/EGL lifecycle, and existing `t2_memwatch.h`.

1. Emit **one controlled first-use receipt** for resource **id=295**: native NVN format/target, 8192x8192, levels and mip offsets, sRGB, BC block bytes, guest address/pool/alias root, CPU dirtiness/write epoch, first sampler/draw, GL context/name/generation and expected decoded resident size.
2. The code calls `t2_texture_budget_add()` **before** `glTexImage2D` in the deferred-first-use path. A safe **budget reservation failure** therefore does not prove a physical GL allocation was attempted. Keep this fail-closed ordering.
3. Maintain a **live storage ledger** across textures, four-target MRT color images, renderbuffers/depth/stencil, GPU buffers, EGL surfaces, redefinitions, deletes, attachments and in-flight GPU readers. Key by `(EGL context generation, GL object/storage generation, NVN owner/alias)` and prevent double-counting shared attachment storage. FBO handles do not themselves imply extra image storage.
4. Quantify any 1920x1080 internal attachments: **four RGBA8 targets are ~31.64 MiB before MSAA/depth/padding**. Do not claim that this explains the ~298 MiB Mali-accounting minus charged-texture difference without traced actual allocations.
5. Correlate charged texture live, exact GL live-class estimates, owner guest anonymous PSS/RSS, swap, file-backed BC mirrors, `MemAvailable`, `CmaFree` and driver accounting as **different categories**. Their sizes may overlap in shared RAM. The load-probe-10 ~126 MiB charged plateau and ~870 MiB VmSwap **do not** invalidate the later id295 hazard or prove a guest-heap culprit.
6. Capture sparse 10–30-second live snapshots and a safe pre-stop view, with PID/starttime/boot identity and kernel victim metadata. Avoid glFinish, glGet*, driver debugfs reads or whole-memory scans on every draw.

**PASS:** you can name the live GL resource class and original owner at each major allocation; the 256 MiB first-use cause is exact and the unresolved memory remains explicitly marked unknown if driver accounting cannot expose it.

## 6. PR G2 — replace one immutable decoded RGBA atlas with verified ETC2/EAC GPU storage

**Why:** original BC3 is kept as compressed guest data, but `lc2_bc_upload_stripes` ultimately reserves full **RGBA GL storage**. An 8192x8192 RGBA8 base level uses **256 MiB**. A genuine ETC2 RGBA8/EAC or ASTC 4x4 GPU image uses **64 MiB** of block payload at that size. That is a **theoretical 192 MiB base-level reduction**, not a measured device saving. See [Khronos KTX format guide](https://github.com/KhronosGroup/3D-Formats-Guidelines/blob/main/KTXDeveloperGuide.md) and [GLES compressed texture API](https://docs.gl/es3/glCompressedTexImage2D).

1. First test **small, self-authored** GLES3 sample textures on the actual Mali driver, using `GL_COMPRESSED_RGBA8_ETC2_EAC` and sRGB equivalent, checking `GL_MAX_TEXTURE_SIZE`, supported formats, `glGetError`, draw/readback, transparent-edge behavior and physical memory changes. ASTC only if separately advertised and tested. Support in the API is **not proof of physical compression residency**.
2. Confirm id295 original BC3 image SHA-256, immutable sampler-only ownership, all source levels, BC format/sRGB/alpha, swizzle, filtering, guest write epochs and alias lifetime. **Never** use compressed sampling as a substitute for a dynamic RenderTexture, writable image or FBO.
3. Implement an **owner-local offline** transcode/cache (BC3 -> exact RGBA -> ETC2 RGBA8, optionally ASTC4x4/6x6), content-addressed by original SHA, all mip dimensions, encoded format, compressor version/options and output hash. Preserve per-mip padding, sample coordinates, color space, alpha and orientation. Do not commit proprietary bytes or generated assets.
4. In the first-use native texture materialization path, select the validated compressed cache **before** any fallback RGBA allocation. Upload all appropriate mip levels using `glCompressedTexImage2D`; retain exact GL resource/fence generation and a safe conditional fallback. Do not allocate a 256 MiB RGBA duplicate in parallel.
5. Charge only **actual live compressed storage** under correctly verified budget accounting. Compare true Mali/driver/system memory plus resource-count parity. An apparent budget-counter reduction by itself is not enough.
6. Review real KMS captures, dark gradients, sprite atlas edges, alpha, pixel text, lighting, mip transition and first-world compositing. Recompression **may be lossy**, so label the experiment as a reversible quality/performance tradeoff, not a byte-exact replacement.
7. Bound owner cache disk space and SD reserve; prior fileback cap 1280 MiB did not fit. Avoid on-device encoding during slow Loading. Preserve save/ELF rollback.
8. Test one immutable atlas only, then an explicit allowlist. First succeed under the previously reproducible **300 MiB guard** and **512 MiB fileback cap**, show actual progress **past the old id295 boundary**, no kernel OOM and safe physical memory, then three matched A/B runs.

**Other owner-led alternatives:** free truly dead images after final in-flight fence, remove duplicate GL storage generations, prove transient FBO reuse, or use a verified **Lamentum-specific** Unity internal resolution owner. Blindly reducing atlas dimensions or the panel mode will break texture coordinates or do nothing.

## 7. PR W1 — prove scene activation and all four fragment45 MRT outputs

1. Identify a hash-pinned **real Unity scene request, async operation progress and activation** plus first camera/player Update in the owner-local code/metadata. Loading presentation counters cannot establish scene activation. Distinguish waiting asset work, blocked activation, live world with wrong pixels, and actual world output.
2. Require **draw receipts**, not only link, for new vertex44 and fragment45 programs. Preserve exact shader code/control identities, fragment45's half-rounding product semantics, sampler and CBUF layouts.
3. For fragment45, validate `GL_COLOR_ATTACHMENT0..3`, `glDrawBuffers`, per-attachment format/size/samples, FBO completeness, GLSL output locations, depth/stencil, color masks, blends and ordering of consumers. Do not collapse four MRT writes to one target.
4. Capture a small bounded **live-game** KMS screenshot and one-shot offscreen attachment readbacks tied to PID/starttime/frame. Classify: no scene logic, no world draw, correct offscreen but bad final composite, or drawing with bad sampler/UV/alpha/stencil. A post-kill sleeping/blanked panel is not evidence of blank gameplay.
5. Track **new actual draw pair census** of all seven TEST substitutes. A placeholder unused in menu may be needed for world sprites, skinning, shadow/probe or MSAA. Capture a new demanded exact shader identity and append without regenerating already proved catalogue entries.
6. Audit the current `nvn_render.h` branch `u->kind==7`, which may fall back to the **other nonempty constant-buffer slot**. Prove this is valid for each new world program; do not let an incorrect fallback silently feed plausible-but-wrong data. Preserve build202 c4->UBO1, c1 literals and c3/c3_1 alias provenance.
7. Verify physical pad movement through player coordinate/state and actual KMS change. Then interaction, inventory, dialogue, audible music/SFX and backed-up save -> quit -> cold load. Clean principal/MainUI return and CPU-mask restoration remain mandatory.

**Only after this** can README change from NOT PLAYABLE.

## 8. PR F1 — measured FPS improvements after gameplay exists

Run **three independent >=60-second quiet real-world samples**, separately for idle scene, movement, interactions and effects, with complete presented-frame serials, true displayed throughput, period P50/P95/P99, guest running/waiting CPU, NVN replay, GL/GPU stalls, memory and temperature. Target for verified stable 30 FPS remains complete-frame **P50/P95 <=33.33 ms**; also report P99 and >100ms stalls. Loading spinner throughput is not gameplay FPS.

Only optimize the measured largest stage:

- **SVC/IPC:** a specific proven bridge or service cost, with correct mutex/event semantics and meaningful scene progress.
- **CBUF width:** in `nvn_render.h`, the shader-bank texture uses `width=1024` and clears/uploads a full **1024 * 4 * 4 = 16 KiB** RGBA32F row for an active bank even when only ~16–368 guest bytes are present. Instrument and test exact-size smaller textures **only when the complete GLSL texelFetch X/Y addressing and row pitch are proved**, retaining a safe legacy fallback. Existing glTexSubImage2D has **not** proved faster frames.
- **Context lifetime:** current static `cbuf_texture[32]`, `cbuf_w`, `cbuf_h` caches need an actual test across EGL context/surface recreation. If a stale GL name/storage generation is reproduced, invalidate/recreate by context identity, not every draw.
- **NVN replay and driver:** exclusive profiling of descriptor/sampler resolves, state shadowing, vertex conversions, GL buffer churn, framebuffers and GPU fences before changing them; no unsafe glFlush-only completion.
- **Memory:** matched ZRAM cold=10/100/250/500 comparisons with real **CPU** nanoseconds and safe headroom; previous `cpu-compress-ms` fields were CLOCK_MONOTONIC wall time and cannot be called CPU time.
- **Render resolution/effects:** generic ZERO_RENDER_SCALE=2 barely affected historical Loading; leave OFF until **world GPU fill cost** is proven. Trace the real Lamentum internal 1920x1080 target owner and shader/UI matrices before a safe 720p preset. Only quality-review reversible bloom changes.
- **Compiler/CPU affinity:** test with source/ELF parity and CPU/governor/thermal data, restore all Spruce state and reject any image/sound/save regression.

## 9. Next PR queue and acceptance gate

| Rank | PR | Required output |
|---:|---|---|
| P0-1 | **T1** — observer/run identity | Target-correct CPU ticks; robust `/proc` parser and PID/TID generation; semantic navigator; host tests and one controlled safe run |
| P0-2A | **C1** — SVC and endpoint owner profiling | Native PC symbolic module+offset, exact service behind endpoint0x40, exclusive per-call CPU/wall and mutex/IPC result receipts |
| P0-2B | **G1** — GL live memory and id295 ledger | Actual original resource metadata, GL storage generation, full live resource classes, controlled budget guard |
| P1-3A | **C2** — one measured correct IPC/bridge change | Reduced CPU **per real scene milestone**, no lost wakeup, correct syscall/service semantics |
| P1-3B | **G2** — one owner-local ETC2 atlas experiment | Real physical GPU residency reduction and **progress beyond previous first-use id295**; acceptable image quality |
| P0-4 | **W1** — scene/MRT/world validation | Scene activation evidence, four valid MRT targets, correct KMS picture and physical movement |
| P0-5 | **W2** — playable gate | Interaction, inventory, dialogue, audible audio, cold save/load, clean MainUI/CPU recovery |
| P1-6 | **F1** — genuine world FPS | Three correct independent >=60s runs, complete period P50/P95/P99 and meaningful hotspot-specific A/B gains |

**Stop:** kernel/Mali OOM, T2_MEMORY_FLOOR, unsafe resource alias/last-consumer eviction, command-buffer reuse before completion, EGL errors, incorrect shader/Cbuf bank, broken MRT output, TEST placeholders on a demanded draw, failed cold saves or dirty principal cleanup. A PR merged without a physical test is **implemented but awaiting validation**, not a proven performance improvement.

**Immediate next useful measured results:** actual service owning endpoint0x40 and cost of 0x1A/0x1B plus IPC 7/8; original id295 descriptor and GL live-owner ledger; real Mali ETC2/EAC upload/readback and physical residency test. These findings—not more Loading timeout—should decide the first actual runtime optimization.

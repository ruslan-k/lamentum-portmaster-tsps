# Lamentum TSPS — Current Gameplay Bring-up and Performance Plan

> **Current actionable plan, audited 2026-10-20 through [54e031d](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/54e031d396c559ab90c4de94f54da99a73059b14).** Latest **completed and analyzed** handheld run: [newgame-15](../evidence/newgame-15/README.md), build216. A newgame-16 test requesting 2400 seconds was rejected by the then 900-second ceiling. The newgame-17 folder contains binary identity and environment records for an 1800-second run, **not a committed result** at review time. This is a code/evidence audit, **not** a new device test. Neither gameplay nor 30 FPS has been established.

This document is the **living execution worklist** linked from the [full historical 30 FPS roadmap](performance-roadmap-30fps.md), whose sections 0–23 record earlier investigations. Older references to build213/42 shader entries, a missing vertex42 or a 900-second current ceiling are now superseded; past measurements remain useful as historical, phase-specific evidence.

## 1. What was implemented and what remains unverified

| Area | Confirmed completed | Incomplete |
|---|---|---|
| Inputs | Real title/options/New Game config/control screens/Loading; agent evdev **305 Confirm, 304 Back**; live KMS captures tied to PID/starttime | Physical controller acceptance **in gameplay**, player movement, inventory |
| Shader catalogue | **45 entries, indices 0–44; seven TEST-only**. New original vertex42, fragment43 and vertex44 admitted, without regenerating old entries | No proof vertex44 was **drawn**; no first-world correctness; TEST entries may be used later |
| Constant-buffer provenance | Original SPIR-V **c1** literal and **c3** application banks; SPIRV-Cross name **c3_1** is an alias, **not** slot 1. SHA-pinned vertex42 -> NVN UBO0 minimum384B; vertex44 -> UBO0 minimum368B | Actual draw/scene pixels and complete shader semantic parity |
| Mali driver | Real Mali-G57 GLES3.2 explicit-GBM/surfaceless fixture passed **10** narrow lane/row, update/rebind and scalar-half numerical checks | No production GL context lifetime, in-flight GPU ownership or game-pixel verification |
| build216 / newgame-15 | TIME_LIMIT only, **1469** presents, **1111 ROMFS_READ** calls, highest read end equals RomFS size **1,832,059,520 B**, 14 program IDs bound, **zero** unknown shader stops, clean MainUI/CPU restoration | Still loading / very limited dark content, **zero vertex44 draw-guard receipts**, no player world/audio/saves |
| Probe harness | Invalid requested 2400s run classified as CONFIG REJECTED; source ceiling raised from **900 to 1800 seconds** | 1800s outcome not established; increasing timeout **does not accelerate loading** |
| Performance | CBUF glTexSubImage2D already default-enabled; older NVN_PROFILE splits guest-gap and replay; generic ZERO_RENDER_SCALE=2 was nearly neutral | No clean frame P95 for gameplay; no proven full-frame CBUF speedup |
| Memory | Guest ZRAM, lossless file backing, striped BC atlas, 420MiB GPU texture cap | 32MiB floor remains a **diagnostic risk**; previous minimum MemAvailable ~43–47MiB |
| Profiling | tools/perf_sample.py and tools/analyze_perf.py exist | perf_sample.py still uses workstation rather than **target** CPU ticks; sampled slow frames cannot prove P95 |

**Pinned game binary:** build216 ELF SHA-256 6b1171257de082b0b7dcbc1150c3f815f6fc62f2d0b95228b45fb605099d894a; newgame-15 full raw log SHA-256 a5bdb1786b19252f6cdba16d580bcc9ac85bf582757336560c3d55f6ebdd65d4 (19,343,594 bytes). The newer probe-cap variant has installed hash 9c6ecc47184e12ec4f5a03825132ae43035cf86b49ce2b6d7ae6359255fa1338; do not combine those binary identities in benchmark comparisons.

## 2. Critical decision: diagnose scene loading, not another shader

**New finding:** newgame-15 no longer stops at a shader frontier. Its 900s TIME_LIMIT occurs after 1469 total presents, or **~1.63 presents/second gross over the entire run** including menus and startup. That is not a steady loading rate and emphatically not gameplay FPS. Vertex44 has not produced a draw-guard receipt. More catalogue entries should **not** be appended until an actual new shader stop/identity appears.

Test three mutually different hypotheses:

- **Progress, but much too slowly:** Unity scene deserialization, repeated memory compression/faults, ROMFS/file-backed I/O, shader/texture initialization or NVN replay costs keep work moving at an impractical rate.
- **Deadlock or livelock:** a blocked Horizon event/IPC, Unity AsyncOperation activation, a thread scheduling/wait bug or repeated guest routine prevents scene transition while the loading animation keeps presenting.
- **Scene is loaded but rendered wrong:** world logic/camera has advanced, but missing depth/stencil/viewport/texture/shader or framebuffer wiring renders only a dark overlay.

**Do not overinterpret RomFS high-water:** the maximum read-end offset equalling the container size shows an EOF-boundary read, **not** complete unique interval coverage, successful parsing/decompression of all assets, or scene activation. Derive the **union of read intervals**, repeated-read amplification, I/O rates and explicit loader state instead.

## 3. P0-01 — Build a truthful loading/scene-progress ledger

**Implementation:** add tools/analyze_loading.py with unit fixtures; add bounded, opt-in runtime markers to runtime/lamentum-adapter.patch only where required. Keep the separately verified 435-file baseline unchanged.

1. Parse complete *current-run* logs with run UUID, original game PID/starttime, kernel boot ID, log inode/offset, ELF/adapter/catalogue hashes. Require New Game confirm receipt, first Loading capture, first/last present serial and final STOP. Reject concatenated, truncated or reused-run logs.
2. For ROMFS_READ, capture file/container identity, byte offset, requested and **actual returned count**, errno/result, monotonic timestamp, and owner caller when available. Report aggregate read bytes, interval-union **unique** bytes, sparse/overlapping coverage, rereads, P50/P95 latency and last read time. Current data may not include every field: mark absent fields unknown; add narrow instrumentation rather than fabricating values.
3. Emit 30-second or 60-frame windows: verified screen/scene state, frame count and period P50/P95, guest present-to-submit gap, NVN replay, new program creations/**draws**, texture materialization, compressor/fault counts, ROMFS unique bytes, target CPU time and wait state, memory/PSI/CmaFree. Explicitly preserve no-progress windows.
4. Instrument owner-original hash-pinned **Unity scene-load** sites *only after proving a call-site mapping*: scene request/start, async operation progress, allowSceneActivation, completed activation, Awake/Start/player update. Distinguish scene transition markers from animated loading sprites. Do not assume IL2CPP symbol names or force activation values without proving actual semantics.
5. Define a progress vector: scene/async state; new unique asset ranges/resources; completed jobs; newly **drawn** shader pairs; camera/player/world updates; screenshot classification. Present serial alone is **not** progress.
6. Collect sparse actual KMS screenshots **while the unique game PID is alive** at loading start, changed phase and every ~60–120s if safe. Tie each image to a before/after unique process identity, serial and hash. A post-exit MainUI capture is cleanup evidence, not a game frame.
7. Label outcome: SHADER_STOP, MEMORY_STOP, CONFIG_REJECTED, TIME_LIMIT_STILL_PROGRESSING, TIME_LIMIT_STALLED, WORLD_ENTERED, WORLD_WRONG_PIXELS or CLEANUP_FAILED. These are **postprocessing classes**, not new runtime STOP strings.
8. Write parser tests: ROMFS interval overlaps/gaps, sparse EOF read, missing timestamps/return sizes, duplicate serials, stale PID/log, 60-frame silence, and progressing vs stalled screen animation.

**PASS:** two consecutive windows can tell whether the *actual scene* is progressing, waiting, or already active but visually wrong. Reject "many presents" and "read until EOF" as evidence of successful loading.

## 4. P0-02 — Complete one bounded 1800s diagnostic, if not already done

The code now allows **maximum 1800s**. First check whether the owner already completed the newgame-17 probe outside the repository; do not start concurrent/duplicate tests.

1. Verify idle Spruce MainUI, original CPU mask and supervisor identities, game/saves backup and free disk. Read back and pin actual installed ELF hash **9c6ecc…** if that is the intended variant. The owner-specific tools/device_principal_test.py uses SSH and terminates MainUI in the Spruce principal flow: **never run blindly**.
2. Configure budget 1800 seconds and harness waiting beyond the budget plus cleanup margin. Use actual state-verified EV_KEY305 Confirm/304 Back navigation with press+release receipts and independent KMS screen verification before each step.
3. Initial continuation may preserve newgame-15 diagnostic memory flags (cold250, 16KiB blocks, 20ms scan, 32MiB budget, lossless BC/fileback, 32MiB floor) **only for a behavior comparison**, with continuous safety checks. Monitor min MemAvailable, CmaFree, PSI, swap/fileback read latency, kernel allocation pressure and OOM risk. Abort safely for dangerous pressure; the 32MiB floor is **not release safe**.
4. Use the new scene-progress ledger. Label the result as a new shader STOP, active loading with quantitative progress, fully stalled loader, world with correct pixels and controller, world with wrong pixels, or memory failure. A clean TIME_LIMIT alone says nothing about scene completion.
5. Preserve full final log, run UUID, ELF/input/scene identifiers and cleanup; verify original CPU mask and MainUI afterward. Rebuild back to the prior known-good binary on regression.
6. **Do not just extend the deadline again.** If two or more windows show no loader progress, instrument its wait/PC; if progressing, improve progress *per second* instead of repeating very long waits. Create a separate quiet profile when safe.

**PASS:** one resolved state classification backed by the full run. **STOP:** unsafe memory, unexplained program stop, invalid game identity, or broken cleanup.

## 5. P0-03 — Establish first *correct* interactive gameplay

1. Identify actual scene state/first world update and first **draw** of vertex44. Validate LC2_SCENE_COLOR_VERTEX_GUARD, exact 368-byte UBO0 extent, original shader stage/partner, texture/sampler handles, vertex attributes and varyings. **Bound** program44 is not **drawn** program44.
2. If ZERO_SHADER_NOT_PINNED recurs, capture the **new exact** code/control hashes, stage, lengths and compiler IR/resource details from owner-private data; append just that one verified shader. Do not regenerate old catalogue entries or copy proprietary code to Git. Keep c1 literals distinct from compiler-alias c3_1 -> hardware c3 -> UBO0; retain 384B/368B guards and negative tests.
3. If a real pair is drawn but scene pixels are missing, trace **FBO attachment/size/ownership, viewport/scissor, shader cbuf slot/range, sampler offset, depth/stencil, blending, color mask, UVs and BC residency**. Verify what *actual* KMS images contain, not just whether pixels are nonblack.
4. Record a complete **actual draw-pair census** for the first world. Seven TEST-only entries were not critical to a historical menu but may be used by gameplay for skinning, probes, MSAA or lighting; replace only those **actually demanded**, preserving exact semantics or failing closed.
5. Verify character movement using player-state/position change plus real KMS capture; separately verify object interaction, inventory, dialogue, **audible** music/SFX and save -> quit -> cold launch -> load. Agent evdev simulation is **not** physical-controller acceptance; test the actual buttons too.
6. Continue to require the full device lifecycle: no orphan game, original CPU mask, MainUI restored. Back up original owner saves before manipulating save paths.

**PASS:** correct world, movement, one interaction, audio, and cold save/load. Until then the port must remain labelled **not playable**, regardless of loading progress.

## 6. P0-04 — Repair the existing performance tools before drawing conclusions

**Concrete currently observed defects in tools/perf_sample.py:**

- Remote /proc utime+stime are ticks from the *device*, but CPU percentage and top-thread CPU ms/s use **host** os.sysconf('SC_CLK_TCK'). Return target SC_CLK_TCK in the remote sample and calculate:
  cpu_ms_per_s = 1000 * delta_ticks / (target_HZ * elapsed_seconds);
  cpu_percent = 100 * delta_ticks / (target_HZ * elapsed_seconds).
  Add synthetic HZ100/250/1000 tests.
- Parsing /proc/PID/stat with naive whitespace split is unsafe for parenthesized comm. Parse after the actual closing parenthesis; retain **boot ID + PID/TID + starttime** to reject process/thread reuse. Add schedstat, all threads (not only top six), context switches, minor/major faults and read-only pressure metrics.
- Current process enumeration may select a stale similarly named process; avoid assuming names identify the one running port. Use launcher-owned PID + starttime. The current field total_cpu_ticks is null; fill it from the actual owner thread set with accurate units.
- A 3000-byte tail of latest.log can miss presentations; use an incremental append-only serial/event stream or bounded frame ledger tied to inode, run ID and monotonic clock. SSH polling interval is not a frame duration.
- In tools/analyze_perf.py, preserve original log order, duplicate/missing presentation IDs, incomplete slow-frame coverage and **signed** accounting residuals. Do not silently clamp negative residual or infer "warmed-up" from a single frame below a threshold; require an explicit scene phase.
- device_principal_test.py now distinguishes rejected config (exit **5**) and guest stop (**4**) from cleanup failure (**3**). Yet runtime_ok=true for a clean **TIME_LIMIT** must not be treated as game success. Add separate test_finished_cleanly, world_entered, progress_verified, and benchmark_valid fields.
- The newgame-15 environment was **AW_RELEASE=0 + LC2_SHADER_DUMP=1 + LC2_MENU_TRACE=1**. That is a shader-frontier diagnostic, **not** a quiet benchmark. For quiet runs verify getenv parsing, disable hot-path diagnostics/GL readback where safely supported, preserve strict GL correctness, and change one factor per A/B.

**Test cases:** target HZ mismatch, PID reuse, names containing parentheses/spaces, incomplete sampled frame coverage, duplicate serial, negative signed residual, clean TIME_LIMIT without gameplay, rejected 2400s budget, stale KMS capture, log truncation and SSH interruption.

**PASS:** reconstructable per-run identity, reliable complete-frame P50/P95/P99, target-accurate thread CPU units, phase tags and coverage report. Report benchmark_valid=false when incomplete.

## 7. P1-05 — Attribute both dominant time phases with low overhead

Earlier measured 60-frame loading windows in [historical roadmap §23.5](performance-roadmap-30fps.md#235-p1-t1t2-attribute-both-large-frame-phases-instead-of-trying-random-gl-tweaks) show **both** a large present-to-next-submit guest gap (~156–380ms) **and** NVN/GL replay (~193–295ms). These are **historical, different-run loading** figures, not build216 or gameplay FPS. Measure current phase before tuning.

**Guest gap:** timestamps from previous present end -> Unity/guest frame start -> guest command recording -> submit. Partition **exclusive wall time**, and separately record target thread CPU: guest IL2CPP computation, asset deserialization, GC, Horizon SVC/IPC wait, SleepThread/WaitSynchronization, blocked/runnable delay, ZRAM compression/page restoration and backing I/O. Use CLOCK_MONOTONIC_RAW for elapsed wall time, CLOCK_THREAD_CPUTIME_ID for on-CPU, target schedstat for runnable delay; never call monotonic wall time "CPU ms". Record guest PC for the top proven wait/CPU call sites, hash-pinned to the owner-original NSO and metadata.

**NVN replay:** in the runtime adapter's nvn_replay.h, nvn_render.h, nvn_textures.h, nvn_framebuffers.h and command/queue files, aggregate exclusive command parsing/copy, shader lookup and link, pool/sampler descriptors, BC texture materialization, CBUF staging and upload, glBufferData/vertex conversion, state/FBO changes, GL draw submission and GLsync/glFinish/eglMakeCurrent. Record counts, bytes, program pairs, context and pool generations. Dump every ~60 frames; do not printf on every guest fault/draw.

**Requirements:** buckets account for >=95% of measured phase wall time, no double counting concurrent CPU/GPU time, and instrumentation overhead <5% in same-scene/same-ELF flags-ON/OFF trials. Frame P95 refers to *complete* presented-frame distribution, not slow-frame-only counters.

| Finding | First targeted fix | Unsafe shortcut |
|---|---|---|
| ZRAM repeated restores and CPU | §8 exact page-owner residency | Turn off all ZRAM at ~43MiB available |
| Blocked pread, repeated asset intervals | §9 bounded immutable read cache or staging | Treat RomFS high-water as scene completed |
| Unity scene activation/WaitSynchronization | Hash-pinned event/ABI/signal/wait fix | Force Unity clock or skip sleeps |
| Large GPU replay/driver CPU | §10 one proven descriptor/cbuf/state hot spot | Reimplement already enabled subimage |
| Wrong pixels with live world state | §5 shader/FBO/texture receipts | Count Loading as gameplay |
| GPU fence/context stall | Correct command serial, fences, EGL lifetime | glFlush-only fake completion |

## 8. P1-06 — Memory and guest-ZRAM experiments

Current diagnostic settings already use **T2_GZRAM_COLD_MS=250**, block16KiB, scan period20ms, budget32MiB and guest target512MiB. Previous massive compress/fault counts suggest churn but **do not establish CPU cost**.

1. Add true **per-thread CPU ns** and separate elapsed ns for compressor, fault/restore, page scan/protection, guest alias invalidation and SD/UDISK fileback. Counters: MiB/s, fault/restore P95, hot-page compress->fault->compress intervals, page owner/generation, write epochs, kernel swap/PSI.
2. Compare cold100 vs250 vs500 ms as one-factor A/B, ideally three matched pairs under identical build, loading phase and memory flags; then vary budget/period separately. Keep the diagnostic 32MiB floor only under explicit owner supervision and stop on unsafe MemAvailable/CmaFree/PSI pressure.
3. If a proven hot guest allocation repeatedly faults, test **narrow owner+generation pinned do-not-compress**, fully accounting its RAM cost and alias/in-flight GPU lifetime. Do not pin whole guest memory or turn off kernel swap.
4. Track unique load progress/second, elapsed seconds to world (if attained), full frame P95, CPU and worst stalls, cold-start correctness and resident memory. Reject a faster early loading segment that crashes on first world.
5. Separately qualify **production 96MiB memory floor**, the 420MiB GPU cap, clean thermal behavior and save/load stability.

## 9. P1-07 — New load-specific ideas worth measuring

These are hypotheses, **not** explanations proven by the existing log:

- **Duplicate RomFS and backing reads:** record range union, repeated reads and blocking latency; if a small immutable range is repeatedly reread, try a strictly bounded, hash/owner-pinned read-through cache. Do not cache the entire ~1.83GiB RomFS or confuse file offset with logical asset identifier.
- **Repeated shader/resource initialization:** count actual shader link/relink, texture BC materialization, GL reallocation and FBO recreation **per scene window**. Precompute immutable metadata/lookup once, or prewarm already-admitted shader programs when proven and within memory limits. Program **creation** without later draw validation is not shader correctness.
- **Guest page alias churn:** identify a repeated compression/fault/write epoch for the same mutable Unity asset range. Cache or pin only with correct guest aliases, lifetime and resource generations.
- **Unity async scene-activation hang:** if initial asset work ends but scene activation never progresses, trace exact guest wait/event signaling, NPC/PlayerLoop owner PC and Unity AsyncOperation state. Fix an actual missing Horizon event or translation contract; don't fake completion.
- **Expensive animated loading screen:** if the render loop consumes resources better spent loading assets, test a **reversible loading-only** graphics-work reduction that maintains the required Unity/Horizon present/event ordering. Judge by **load-work units/second and time to world**, not just more/less FPS or a black screen. Do not skip command buffers whose completion is needed for resource lifetime.
- **Logging and sync I/O:** 19.3MB debug log and shader dumps may create device I/O stalls. Compare AW_RELEASE=1, shader dump disabled and minimized readbacks/trace **separately** in a quiet diagnostic with the same binary/scene. Preserve fail-closed shader identities in the frontier debug mode.

## 10. P1-08 — GPU/CPU optimizations, only after phase attribution

1. **CBUF real upload volume:** LC2_CBUF_SUBIMAGE is **already default-on**. A 1024-texel-wide RGBA32F staging row can upload **16KiB** for a logically 16–368B block. Measure source bytes vs GL bytes/calls and CPU/driver time. If material, update *only dirty complete RGBA texels* while retaining logical shader addressing and clearing stale padding on size shrink. Preserve exact code/control bank provenance, NaN bits and GL generation/fences. Extend the existing Mali fixture for row boundary, shrinking data and context rebinding.
2. **Sampler/descriptor caching:** if lookup dominates, cache by pool/view/sampler generations, write epoch, mip/format and actual EGL context. Invalidate on writes, pool recreation, eviction, context loss, and render-target aliasing.
3. **GL state/FBO shadowing:** first count calls that *would* be redundant for current context. Suppress one call family (program/texture/FBO/blend/stencil/viewport) at a time with context invalidation. Mali tile attachment invalidate is allowed **only after the last actual consumer**.
4. **Vertex/index staging:** measure glBufferData allocations and guest conversions by draw pair. Consider bounded reusable VBO/IBO/ring resources only with correct queue serial/fence ownership and RAM accounting.
5. **BC residency/dirty updates:** preserve lossless 8192x4096 BC3 striped decoding, lazy uploads and the 420MiB cap. Optimize repeatedly touched immutable ranges only when write epochs prove freshness. ASTC side caches are conditional on verified hardware support, alpha/sRGB parity and available disk.
6. **Title-owned 720p and postprocessing:** the panel is already 1280x720 but internal resources may be 1920x1080. Generic scaling was nearly neutral; optimize a verified Lamentum Unity/IL2CPP owner only if **real world GPU time is limiting**. Do not copy West of Loathing title offsets or break UI transforms/hitboxes.
7. **Async NVN queue:** keep OFF unless time attribution proves meaningful GPU waits and serial/resource/context fencing is tested. Prior command-buffer reuse/EGL_BAD_SURFACE are correctness failures. glFlush-only is not completion.

## 11. PR order, precise checks and stop conditions

| Order | PR/work item | Deliverable | Acceptance |
|---:|---|---|---|
| **0** | **G1 loading ledger** | ROMFS interval union, live world/scene/progress markers, 60-frame analysis and fixtures | Differentiates work, event wait, wrong pixels |
| **1** | **G2 1800s bounded probe result** | Fully hash-pinned single run, controller/KMS receipts, complete log and cleanup | Explicit WORLD / SHADER / PROGRESS / STALLED / MEMORY classification |
| **2** | **M0 fix existing profiling** | Target HZ, boot/PID/TID/starttime, frame coverage, signed residual, tests | Reproducible valid CPU and frame units |
| **3** | **T1 guest/replay attribution** | Low-overhead independent stage profile, same-phase A/B | >=95% elapsed attribution, <=5% overhead |
| **4** | **L1/M1 major loading bottleneck** | One-factor patch and data vs pinned baseline | Faster *real scene load progress*, no unsafe RAM or wrong assets |
| **5** | **G3 first actual gameplay** | Program44 draw or next exact identity, world screenshot, movement and interaction | Correct world, no unverified TEST path |
| **6** | **R1 one measured rendering hot spot** | Strict visuals and complete-frame P50/P95 before/after | Real improvement, correct fence/context |
| **7** | **PLAYABLE** | Audible audio, physical controller, inventory/dialogue, cold save/load | May finally label playable |
| **8** | **FPS30** | 3 x 60-second controlled world routes, complete presentation log | P50/P95 <=33.33ms, preferably P99 <=50ms, safe RAM/thermals |

**Suggested read-only or host-side validation (not executed in this audit):**

~~~sh
# In the independently recovered 435-file source tree:
sha256sum -c /path/to/repo/tools/baseline-manifest.sha256

# In the port repository with test dependencies available:
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m py_compile tools/perf_sample.py tools/device_principal_test.py

# Before building a new shader, prove catalogue 0..44 prefix is unchanged.
# Do not launch tools/device_principal_test.py on a busy handheld.
~~~

For every PR record **cause, exact current evidence, measured baseline, one changed factor, run/ELF/owner identity, screenshot and shader guard parity, memory headroom, rollback and stop outcome**. Never publish proprietary original game assets or saves.

## 12. Feasibility decision

The evidence **supports continued port development**: real menu and input work, pinned shader translation now advances further into New Game, and the current failure has become a **long, poorly attributed loading phase rather than an immediate missing-shader stop**. The 1800s ceiling change solves a **test limitation only**.

The evidence **does not establish that 30 FPS is feasible**: historical loading is orders of magnitude slower than a 33.33ms whole-frame budget, and no valid interactive-world FPS profile exists. First reach a world with meaningful progress and correct output; then use transparent 5/10/15/20/30 FPS milestones. If large exclusive Unity and NVN costs persist in actual gameplay after safe targeted optimizations, report the physical hardware ceiling rather than promising 30 FPS.

**Next required evidence:** the completed newgame-17 result if it exists; per-window scene/loading progress, corrected target CPU tick units, actual vertex44 **draw** receipt or new captured shader frontier, and a resource-safe quiet run. No device deployment, 30 FPS measurement or source runtime build was performed as part of this written reassessment.

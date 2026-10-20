# Lamentum TSPS — Current Gameplay Bring-up and Performance Plan

> **CURRENT PRIORITIES (2026-10-20; repository HEAD audited: [b35f21e](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b35f21e14662e681e27de9c78cc91ea250f0d4be)): read [§§13–20](#13-build218--newgame-20-reassessment) FIRST.** This updates the build216 analysis retained in §§1–12 for its implementation detail. Source and committed evidence were reviewed; no new device run, binary build, or 30 FPS measurement was performed in this review. The port is **not playable**. build218/newgame-20 linked entry45, then **the game was killed following Mali OOM notifications**, after 709 presented frames. **An earlier independent loading window consumed 0.836 s of main-thread CPU per presented frame while performing zero new RomFS/texture work.** Both issues must be explained before pursuing FPS tweaks.

> **Historical note:** the previous "current" snapshot through 54e031d/build216 and its statement that newgame-17 had no outcome were superseded by [newgame-17](../evidence/newgame-17/summary.json), [newgame-18](../evidence/newgame-18/summary.json), [newgame-19](../evidence/newgame-19/summary.json) and [newgame-20](../evidence/newgame-20/summary.json). §13 onwards is the authoritative execution queue; §§1–12 remain a historical reference and should not be mistaken for current status.

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

## 13. Build218 / newgame-20 reassessment

**Reviewed source:** [b35f21e](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b35f21e14662e681e27de9c78cc91ea250f0d4be), which includes the new tools/load_probe.py and tools/analyze_load_probe.py but **no committed run from these new tools at review time**. It follows 43 commits after the original English-roadmap commit a4d0a2e. All conclusions here are scoped to the files and evidence actually committed.

| Area | Current verified result | Not yet proven |
|---|---|---|
| Frontend and input | Main menu, New Game configuration, controls page and Loading reached with live KMS screenshots and injected EV_KEY305/304. The host now has a measured cursor-row oracle in tools/newgame_navigate.py. | Actual human input during gameplay, movement and combat |
| Shader frontier | **46 catalogue entries, indices 0–45, seven TEST substitutes.** newgame-18 linked vertex44; build218 admitted fragment45 with capture-pinned half-precision MRT lowering; newgame-20 logged **sources=0/45, link=on-native-pair-draw**, with no subsequent unknown-shader stop reported | Successful scene pixels and all draw/attachment semantics; a linked program is not proof of correct output |
| Run/termination | newgame-17 presented 2176 frames and exceeded the guest 1800s alarm; the host test harness now owns an independent stop bound. newgame-20 ended at frame **709** with launcher "Killed" and Mali OOM notifications, **not a runtime STOP**. | A completed and reproducible world load |
| Mali memory | newgame-20 reports **725,992 kB Mali GPU allocation/accounting** in OOM notifiers, on a device with **986,064 kB MemTotal**. The documented 420 MiB texture budget did not prevent the kill. | Exact owner of those driver-accounted bytes, allocation vs retained-resource double counting, time of peak and growth trajectory |
| Guest CPU | A measured *earlier build217* 20.14s Loading window displayed 23 frames (1.14 presents/s), consuming **0.836 s main-thread CPU/frame** and **1.63 s all-thread CPU/frame**, while reporting zero new RomFS reads, textures, texel writes and BC deferrals | Which guest/SDK/runtime call sites burn this CPU; representative world FPS |
| Probe harness | tools/load_probe.py plus an initial analyzer and four synthetic analyzer tests have been added. device_principal_test.py has a SIGKILL-without-STOP return path. | Correctness of the new remote regex/counting collector, bounded sampling overhead, exact OOM correlation and clean scene-progress classification |
| Perf fixes already attempted | CBUF glTexSubImage2D is already default-enabled; historical A/B demonstrated **no reliable frame-time win**; ZRAM cold250 and lossless BC fileback are already used in diagnostic runs; generic render scaling was almost neutral | Independent measured gains in actual gameplay |

**Important measurement boundaries:** a Mali OOM notifier is not a per-GL-object memory ledger; the number 725,992 kB cannot be assigned automatically to decoded BC textures. The historical 0.836s CPU/frame sample is a **Loading** window from build217, not from build218 and not a gameplay FPS value. Frame 709 is a serial, not 709 frames of gameplay. After a SIGKILL, the first KMS screenshot may be black because the panel is asleep; verify the newly awakened MainUI and its original PID/CPU mask. The seven TEST shaders may become relevant only in the world.

**Critical-path decision:** run in this order: (A) repair probe truthfulness -> (B) reproduce and attribute Mali memory peak safely -> (C) eliminate the proven GPU allocation/lifetime hot spot -> (D) use bounded CPU guest-stack samples to identify the expensive Loading loop -> (E) verify first world draw, inputs, audio and saves -> (F) profile and optimize actual gameplay FPS. B and D may use separate safe diagnostic runs. **Do not append shaders just because a load stalls after entry45.**

## 14. P0-TOOLS — Repair the newest load probe before using its counters

**Why this is blocking:** tools/load_probe.py is a new test driver, not yet a validated measurement instrument. The embedded remote Python payload currently includes patterns of the form \`r'NVN_PRESENT_PIXELS frame=(\\d+)'\` and \`r'STOP status=\\S+'\` inside a separate triple-quoted Python string. When interpreted by the remote interpreter, these are **doubly escaped regular expressions** and can return zero counts/missing frames even for matching records. This is a source-level defect, not a hypothesis about the game. It is not exercised by tools/test_analyze_load_probe.py, which injects already parsed rows.

**PR T0 — exact steps:**

1. Extract the remote collector into a pure, host-testable **make_remote_script()** or a separate versioned Python module. Unit-test the **actual string the SSH target executes** against a synthetic log containing \`NVN_PRESENT_PIXELS frame=709\`, \`STOP status=T2_MEMORY_FLOOR\`, one entry45 link, one \`ROMFS_READ\`, and a kernel-kill marker. Require \`frame=709\`, \`presents=1\`, correct stop, and \`entry45=1\`. Keep one quoting layer at most; prefer plain \`re.compile(r'...\\d+')\` in an independently stored script, rather than generating raw regex strings inside another Python string.
2. **Stop rereading the complete latest.log every 5 seconds.** The new collector currently calls \`Path(.../latest.log).read_text()\` on every interval and recounts the entire log. Earlier logs reached ~19 MB; repeated full reads add I/O, allocations and CPU workload to the device being measured. Replace with run-scoped incremental file read (inode + offset + partial-line buffer + generation on truncation), an append-only compact counters file, or counters emitted by a bounded runtime ring. Sample host/driver counters without copying whole logs.
3. Guard against old-data contamination with kernel boot ID, unique game PID **and starttime**, log inode/truncation generation, monotonic sample timestamps, ELF SHA-256 and run UUID. Do not interpret a previous run's trailing \`STOP\` or \`Killed\` as the current outcome. Cross-check the latest completed run's original log SHA.
4. tools/load_probe.py navigates the New Game configuration with a **fixed pair of Down presses** after entering the page; the same repository proved in newgame-19 that press counts and background changes can lie at 1–2 FPS. Reuse \`cursor_row()\` / its state-specific coordinates for **both** menus, or the robust \`goto_row()\` bottom-anchor with explicit page checks. Require a screenshot-validated controls page before continuing to Loading. Abort if any expected row is not found. The main-menu cursor range 88..124 and y=475 is observed; **do not assume** the same coordinates on the New Game configuration screen without a measured capture.
5. tools/analyze_load_probe.py currently sums first-to-last counters regardless of missing samples, log resets or negative deltas. Implement monotonic counter **generation tracking** and return \`unknown/reset\` on wraps, truncation or new run. Report minimum MemAvailable/CmaFree; time-local speed of memory growth, unique ROMFS bytes, texture allocations vs frees, committed GPU/driver bytes, and last valid sample before OOM. Preserve unsampled values as null; do not silently fill zeros.
6. tools/perf_sample.py **still** uses host \`os.sysconf('SC_CLK_TCK')\` for target ticks and whitespace-splits \`/proc/PID/stat\`. Fix both using target \`getconf CLK_TCK\` or target \`os.sysconf\`, parse the final parenthesis of comm, and pin boot ID + PID/TID + starttime. Replace \`tail -c 3000\` frame observation with an incremental run-scoped serial ledger. Test HZ100/250/1000, PID reuse and missing frames.
7. In tools/device_principal_test.py, keep separate outcomes for guest STOP, rejected config, host timeout, dirty cleanup and **SIGKILL without STOP**. \`Killed\` alone proves a killed process, **not why** it was killed; label it confirmed GPU/kernel OOM only when correlated with kernel driver notifier, victim PID/starttime and event time. Store a bounded dmesg/journal delta before and after the run, if available, and verify that the notifier belongs to the same instance. Never terminate any unrelated system process.
8. Add a synthetic **end-to-end** test feeding a mock remote log (not already structured rows), fake samples with a disappearing PID, overlapping log reset, and a controlled OOM message. Verify all generated JSON/CSV output, phase classification and host watchdog result. Run with an artificial large log to catch O(n²) polling overhead.

**Definition of done:** no false zero-frame rate, no falsely attributed STOP, no blind navigation, no cumulative log rescans, no incorrect target CPU units, and all error cases are represented explicitly in the analyzer's JSON. **Do not use the new load probe for optimization A/B until T0 passes.**

Suggested host-only checks (do **not** launch a busy handheld):

~~~sh
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m py_compile tools/load_probe.py tools/analyze_load_probe.py \
  tools/device_principal_test.py tools/perf_sample.py
~~~

## 15. P0-GPU — Find and Fix the Actual Mali GPU Memory Wall

**Evidence:** [GPU wall note](gpu-wall-after-entry45.md), [newgame-20 summary](../evidence/newgame-20/summary.json), [build218 shader note](build218-entry45.md), and the historical [420 MiB budget implementation notes](loading-memory.md#gpu-budget-accounting). Build168 began charging **eligible deferred BC textures upon materialization** rather than at guest-storage creation. This does not prove the counter includes **all** framebuffer/renderbuffer attachments, mip chains, display surfaces, multisampled storage, driver-private allocations or older GL objects whose deletion has not completed.

### 15.1. PR G0 — a GPU allocation and lifetime ledger, without behavior changes

Instrument the owner's baseline native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_render.h, native/nvn_queue.h and the relevant EGL context/surface paths **via runtime/lamentum-adapter.patch only**. Keep the manifest-pinned 435-file original baseline unchanged.

For every event record a bounded tuple of: \`run_uuid, t_mono_ns, game_pid/starttime, frame_serial, NVN_resource_id, guest_pool_id+generation, GL_context_generation, GL_name+creation_generation, resource_class, immutable/content_generation, event, width,height,depth,layers,mip_levels,samples,source_format,actual_GL_internal_format,bytes_expected,budget_reservation,live_consumers\`. Resource classes must distinguish decoded BC textures, non-BC textures, display/EGL images, offscreen color MRTs, depth/stencil, renderbuffers, buffers, temporary shader/CBUF textures, intermediate readback, driver-private unknown, and backing guest pages. Include \`glTexImage2D\`, \`glTexStorage2D\`, \`glRenderbufferStorage\`, \`glBufferData\`, replacements/resizes, eviction, GL resource deletion, and context recreation paths actually present in the runtime. Do **not** assume every API is in use.

- Record **logical guest allocation**, **estimated GL storage**, **reserved texture-budget bytes**, and **driver-reported Mali usage** as separate series. The last is authoritative only to the extent the device exposes a reliable per-process driver counter; discover available \`/sys/kernel/debug/\`, \`/sys/class/misc/\`, Mali driver/sysfs or \`/proc\` nodes read-only first. If inaccessible, label driver bytes **unavailable** instead of deriving them from process RSS.
- Count creation/destruction/redefinition; detect growing numbers of identically-sized render targets or textures with the same guest owner. Use owner and GL generations to avoid false "leak" claims after handle reuse. Track GPU fence completion separately from logical resource deletion.
- For each 30–60 s loading window record top-N allocation owners and deltas, peak MemAvailable, CmaFree, SwapFree, process VmRSS/VmSwap/smaps_rollup (infrequently), \`/proc/pressure/memory\` where available, total GL estimated bytes and Mali driver accounting if exposed.
- **Compute resource lower bounds by format**, including mips, slices, MSAA and depth/stencil. Example: one 1920×1080 RGBA8 2D image is ~7.91 MiB, four simultaneously live MRT attachments ~31.64 MiB before depth/stencil, mip levels, tiling and driver overhead. An MSAA target can be much larger. These estimates are **not** direct Mali heap measurements.
- Add synthetic tests for create -> resize -> delete, guest aliasing, context loss, texture name reuse, missing GL format, failed allocation, delayed GPU completion, and overlapping lifetime. Verify the ledger's accounting identity before relying on it.
- **Avoid an additional OOM run by default.** Collect baseline at earlier, increasing memory checkpoints first; stop before the previously observed dangerous pressure. Only reproduce the full limit if device-owner-approved memory/driver guardrails and rollback are established. A diagnostic **32 MiB** physical-memory floor is **not safe as a release preset**.

**PASS G0:** the ledger explains >=90% of known API-level estimated allocations and isolates the largest increasing resource class, while acknowledging remaining driver-private unknowns; it can show whether Mali-reported bytes exceed the accounted GL subset. Do not claim to have diagnosed a leak merely from 75 repeated OOM notifier lines.

### 15.2. PR G1 — reconcile the 420 MiB policy with total physical memory

Inspect the **actual** 420 MiB reservation code and all allocations it omits. Create separate caps and counters for (1) decoded/uploaded texture storage, (2) offscreen render-target/depth/renderbuffer storage, (3) resource staging/buffers, and (4) global conservative driver-accounted/resident risk. Reserve **before** a new GL allocation, free after valid ownership/fence completion, and fail closed with a distinct \`GPU_ALLOCATION_LIMIT\` classification rather than letting the kernel kill the process. A guessed "VRAM = RAM" subtraction is not acceptable on unified-memory Mali.

Add a **high-water backpressure/abort guard** based on measured safe memory, CMA and driver signals where available, with hysteresis. A safety guard prevents destructive kills but is **not** itself a memory optimization. Keep existing 420 MiB and 96 MiB release defaults until end-to-end qualification; do not simply increase budget or disable the governor to get farther into loading.

**PASS G1:** an identical bad scene stops predictably with documented owner/format/bytes and clean Spruce recovery **before** the kernel OOM, without false stops on already-completed allocations. Keep a known-good fallback if new accounting overestimates aliased storage.

### 15.3. PR G2 — optimize only the actual dominant resource class

Choose one, on the basis of G0 and **one-factor** A/B:

- **Large live offscreen MRT/depth or MSAA images:** find owning Unity/IL2CPP creation site (private game image; hash-pin exact code/metadata identity) and verify actual producer/last-consumer intervals. First try the title's existing resolution/quality settings if any; next test a title-specific **1920×1080 ->1280×720** internal render-target change with matching projections/UI, viewport/scissor, UV, input and all dependent attachments. This could reduce RGBA8 image area by 2.25×, but does **not** promise a 2.25× whole-frame speedup. Generic \`ZERO_RENDER_SCALE=2\` was nearly neutral historically; do not repeat it without a different verified owner.
- **Lifetime/duplicate resource explosion:** reuse framebuffer/RenderTexture objects only when live intervals provably do not overlap. Add a generation-aware bounded pool and observe exact GPU command fences before destruction/reuse. Detect redundant allocation on a context switch or repeated content/format identity. Never alias two render targets with simultaneously live readers.
- **BC3 textures expanded to RGBA:** preserve the lossless 8192×4096 striped decode and texture bytes. Only if source content is immutable and the actual device has supported ASTC path, evaluate a content-addressed owner-local ASTC cache; preserve alpha/sRGB/mips and verify side-by-side images. ASTC transcode may be **lossy**. Lazy upload/file backing primarily save guest-side RAM and I/O, not already resident GL storage; do not assume they solve Mali residency.
- **Excessive stale GL residency:** build a proven resource-last-use plus GL-generation/fence model; evict only safely rematerializable textures while preserving guest backing and 420 MiB cap. Repeated evict/reupload can make load and FPS worse; record refault rate, upload bytes/s and driver memory.
- **MRT width/format or overallocated mip/sample levels:** compare original exact NVN requested dimensions/formats, allocation dimensions, whether all levels/layers are used, and GPU driver semantics. Reconfigure only with a complete render-pass dependency proof; never drop required MRT output, stencil, or MSAA without controlled image parity tests.
- **CBUF staging or GL buffer churn:** CBUF glTexSubImage2D is already enabled; verify actual allocation volume before optimizing dirty subrects or PBOs. A few 16 KiB per-draw rows are not a plausible explanation of hundreds of MiB **without evidence of retained duplicates**.

For each candidate require **original-to-new total Mali memory**, time to the same *verified loading phase*, GL estimated bytes by class, MemAvailable/CmaFree, CPU load, visual parity, and no shader/resource STOP. If the modified run loads further but fails under a new unsafe memory category, the optimization is not release-ready.

## 16. P0-CPU — Attribute the 0.836 s Main-thread Loading Cost

The [newgame-17 CPU measurement](time-governor-and-load-cost.md) is the strongest execution-cost evidence so far. It observed a nearly full core on the main thread **without new ROMFS, texture or BC work**. Do not infer an endless asset-loader operation or GPU fence from a static Loading image. The runtime already contains a bounded guest sampler: \`MOMO_STACK_SAMPLE_MS\`, \`MOMO_STACK_SAMPLES\`, \`MOMO_STACK_SAMPLE_AFTER\`, with tools/analyze_guest_samples.py.

**PR C0:**

1. Record binary SHA-256, original owner image/NSO hashes, build, exact Loading-screen phase, PID/starttime, thread IDs, CPU topology/frequencies, and whether the run used \`AW_RELEASE=0\` and shader dumps. Prefer a safe, short, deterministic pre-OOM window. First verify the sampler is available in the current installed binary; the existing source symbol alone does not prove it is active.
2. Enable a **bounded**, infrequent sampler (for example 128–512 total events with modest spacing; choose exact flags based on verified runtime getenv semantics) only during a steady Loading interval, not during menu startup. Sampling must not materially change rendering or require raw stack dumps to the public repo. Run a matched sampler-off control.
3. Use \`tools/analyze_guest_samples.py\` to report interrupted guest \`pc=module.seg+offset\`, call-chain frequency, thread ID, unresolved frames, in-kernel count, and sample loss. Correlate with actual main-thread \`CLOCK_THREAD_CPUTIME_ID\`, corrected target \`/proc/\` ticks, guest-frame serial and wall time. The sampler's distribution is a **CPU hotspot estimate**, not 836ms divided among call sites.
4. Map the top guest PCs in the **owner-private** main/sdk/subsdk/rtld with hash-pinned ARM64 disassembly and IL2CPP metadata. Build a separate map for adapter/native symbols. Distinguish Unity PlayerLoop/GC/job polling, hot shader/mesh processing, guest memory translation, SVC/IPC WaitSynchronization, audio, clock/time polling, scene activation and asset parsing. Never guess symbol names from unverified offsets.
5. For the top three PCs, capture bounded transition counts and exclusive thread CPU/wait wall time, then reproduce in a synthetic host-side microfixture when possible. Reject a call-site optimization that reduces its own local time but increases wall frame P95 or changes guest event semantics.
6. Compare **sampler-off vs sampler-on** in the same binary/state to establish overhead (<5% target), and repeat at least two intervals in case the loop changes state during load.

**Interpretations / implementation branches:**

| Measured hotspot | First safe experiment | Must not do |
|---|---|---|
| Same PC looping while Unity scene progress does not change | Trace exact state owner, return condition, service/event responses, AsyncOperation activation contract; compare expected state transitions | Patch Unity progress value, force activation or silently skip loop |
| SVC timer, WaitSynchronization, IPC service, audio/input poll | Record requested wait, actual return/result and thread. Fix **one demonstrated** ABI/wakeup/signal mismatch | Ignore a wait or fabricate an event without owner proof |
| Guest page faults/alias translation | Attribute fault CPU to exact owner and modified-page generation; bounded do-not-compress test under memory guard | Turn off ZRAM or pin whole guest allocation |
| Repeated memcpy/format conversion/JIT-like native path | Count calls and bytes; reuse immutable results with exact write generation | Cache mutable memory only by pointer |
| GLES replay command/GL fence wait | Profile replay/glFinish and CPU sleeping separately, then resource-safe fix | Replace GPU completion with glFlush or async without serial/fences |
| Legitimate IL2CPP scene work | Measure load-progress units/sec and consider asset/state-specific reductions or bounded read cache | Present a faster Loading sprite as a loaded world |

**PASS C0:** >=70% of sampled **main-thread CPU** hot-location mass is explained by recognized original or native code families (unresolved samples must remain explicit) and repeated CPU/wall measurements discriminate CPU loops from waits. **STOP:** sample instability, high profiler overhead, guessed PC symbols, or uncontrolled memory pressure.

**PR C1:** only after C0, implement **one owner/ABI-verified CPU-path fix**, with pinned reproduction, tests and rollback. Measure speed to the *same scene progress marker* and full frame P50/P95, not just 1.14 -> 2 presents/s on a Loading spinner.

## 17. P0-WORLD — Correct First-Scene Activation and Pixels

**Three different failure classes still require separate outcomes**: (a) resources are loading but not ready, (b) Unity/Horizon state machine is stalled or wasting CPU, (c) the world is active but its frames are missing/obscured. A successful fragment45 **program link** only proves one stage of the pipeline is admitted.

1. With memory guard G1 enabled, navigate **cursor-grounded** menu -> New Game config -> controls -> Loading. Record an owner-hash-pinned scene progress vector every 30–60s: unique ROMFS interval union, asset/job completion, Unity AsyncOperation/scene activation if traced, vertex and fragment **draw** counts, FBO target identifiers/sizes, live frame hashes, player/camera update counters and controller state. Distinguish no new files from no new *work*; async state can still change without I/O.
2. Determine which program pairs are **bound vs linked vs actually submitted to glDraw** and successfully rasterized into a render target. For the fragment45 four-output MRT, verify original locations/formats, NVN attachment mappings, draw buffers, color write masks, half arithmetic, sampler \`fs_tex0_20\` binding 14 offset 0, source texture residency and actual pixels. Preserve source/code/control byte identity, shader stage and original values.
3. If there are world draws but Loading remains visible: inspect layer/UI ordering, stencil/depth, framebuffer target, viewport/scissor, glDrawBuffers, glReadBuffer, blend, GL errors, EGL present source and saved intermediate images. Use bounded source/attachment readbacks outside hot-path timings; compare game-PID-tied **KMS capture** to intermediate attachments.
4. If the world has not activated and asset progress stopped: use C0 CPU PCs to investigate a specific Unity SceneManager/AsyncOperation or Horizon event/IPC contract. Fix the observed return status or synchronization mechanism; **do not** force the progress percentage or skip resource completion.
5. If a new \`ZERO_SHADER_NOT_PINNED\` appears **after** removing the memory wall, append only the exact original shader and resource mapping to runtime/lamentum-shaders-draft.h via pinned tooling. Do not regenerate entries 0–45, erase shader semantic guards or invent an arbitrary color-producing fragment. Maintain existing original half-product rounding.
6. During first world draws census **all seven TEST substitutes** and fail closed where their actual required semantics have not been implemented (e.g. MSAA, SSBO/skin or lighting); absence in the menu is not evidence of gameplay safety.
7. Validate actual character world-coordinate change and corresponding KMS image over physical controller movement. Test interaction, inventory, dialogue, actual audio and save -> quit -> cold restart -> load using backed-up owner saves. Finish with MainUI/CPU mask restoration.

**PASS W0:** an interactable world with correct scene visuals, no unidentified shader/frontier and validated input. **PASS PLAYABLE:** W0 plus audible audio and cold save/load. **Do not call a persistent Loading sprite gameplay.**

## 18. P1-PERF — Only Once Gameplay Exists: a Measured 30 FPS Strategy

The preceding diagnostic figures are Loading/menu and cannot predict world throughput. When W0 passes:

1. Introduce separate **steady-world** scenarios: idle, walk through a fixed map route, multiple sprites/lighting, inventory/dialogue, effects and scene loading. Each run records 60–120 seconds after a disclosed warm-up, with SHA-pinned executable, settings, PIDs, clocks, temperature and safe memory.
2. Correct the existing \`tools/analyze_perf.py\` presentation coverage to compute actual **unique physically presented serials per monotonic wall interval**, P50/P90/P95/P99 frame times, missing/doubled frames and drop rate; do not infer percentile from only \`T2P_SLOW_FRAME\` events. Keep GPU command submit vs completion, Unity frame duration and SDL/KMS presentation separate.
3. Establish **exclusive** guest CPU-gap, native replay CPU, GPU wait, memory fault/I/O and presentation timing. Cross-check per-thread CPU clocks and Mali driver timing (if exposed) without per-frame glFinish in production.
4. Rank measured bottlenecks; the 30 FPS budget is **33.33ms full-frame**, not a single replay stage. If guest CPU dominates, optimize verified call sites; if GPU memory pressure dominates, revisit G2. If fragment/FBO load dominates, look for Lamentum-owned 1080p render-target scaling or title graphics options; the display itself is already 720p.
5. If texture/sample cost is dominant, test format-conserving BC/ASTC owner cache, texture-unit/cbuf dirty-region uploads, sampler state caching or VBO/index staging separately. Note CBUF glTexSubImage2D is **already default** and did not show a proven gain in a previous historical A/B. If offscreen bloom is dominant, opt-in tier reductions must preserve full-resolution UI and original default graphics.
6. If sync dominates, allow async NVN replay only after correct GL fences, serial/resource lifetime, context recreation and safe additional in-flight memory. Prior NVN_COMMAND_REUSE_BEFORE_COMPLETION and EGL_BAD_SURFACE remain explicit stop signs.
7. First publish intermediate **5 / 10 / 15 / 20 FPS** targets for correctly rendered game scenes without lowering correctness; then evaluate 30 FPS feasibility. Do not declare 30 FPS achieved on aggregate throughput while P95 frame time is high.

**Acceptance:** three independent 60s controlled gameplay routes with **P50 and P95 <=33.33ms**, preferably P99 <=50ms, correct pixels/input/audio/saves, safe memory and clean Spruce recovery. A lower verified steady-gameplay ceiling is an acceptable honest result if the measured Unity/IL2CPP+GLES cost cannot fit the device.

## 19. Revised PR Queue: Implementation Order and Stop Conditions

| Priority | PR | Deliverable / measurable criterion | Abort/reject when |
|---:|---|---|---|
| **P0** | **T0 test harness truth** | Fix load_probe raw-regex + full-log rescans; navigation scene oracle; corrected target CPU ticks; classify SIGKILL only with correlated OOM evidence. Comprehensive mock remote tests. | Fake zero frame counts, stale-run confusion, code runs on busy device |
| **P0** | **G0 live GPU ledger** | Driver memory + every actual GL/NVN allocation family, generation/lifetime and 30–60s growth by class, with safe stop before known OOM | Cannot observe genuine memory class or memory floor unsafe |
| **P0** | **G1 pre-OOM policy** | Account uncapped classes in addition to decoded BC, report reserved/live/deletion vs driver, clean abort for predictable risky case | Unexplained GL/FBO aliasing or false budget charge |
| **P0** | **C0 guest-stack sample** | Low-overhead 128–512 samples, hashed guest PCs; explain actual 0.836 CPU s/present hot paths | Sample overhead >5%, results unresolved |
| **P1** | **G2 one resource-class reduction** | Same-phase driver memory drop plus intact visuals and actual load work, safe headroom | Worse realloc/fault churn, mismatched pixels or loss of GPU completion |
| **P1** | **C1 one proven CPU-path correction** | Lower main-thread CPU per unit of **real scene progress** and frame P95 | Forced/synthetic guest state or unbalanced event signaling |
| **P0** | **W0 first correct world** | Shader45 MRT pixels and full pair census, Unity activation, movement/interaction, no TEST semantic gaps | Loading-only or black/misrouted world |
| **P0** | **PLAYABLE** | Physical pad, audible audio, inventory/dialogue, cold save/load, clean process/device cleanup | Functional regression |
| **P1** | **F0 gameplay profiling** | World P50/P95/P99, frame coverage, exclusive CPU/GPU/wait breakdown, 3 A/B repetitions | Diagnostic spinner throughput masquerading as gameplay |
| **P2** | **F1 targeted optimizations** | Verified higher real-world FPS with stable graphics/audio and memory | Gain within noise or shifted into GPU wait |

**Run invariant:** same owner image, pinned shader catalogue prefix 0–45, no proprietary image/NSO/shader binaries committed, manifest-verified recovered GPL baseline, one-factor diff, on-device executable readback SHA, saved original game data and clean rollback. Retain strict GL checks; async queue and unsafe pageout OFF. Diagnostic 32MiB memory floor is not a release policy.

## 20. Concrete First Three Change Sets to Implement

**Change set 1: instrument reliability.** Modify tools/load_probe.py, tools/analyze_load_probe.py, tools/perf_sample.py, tools/device_principal_test.py and their unit tests. Minimum fixtures: correct regex after remote execution, live-run PID+starttime changes, truncated logs, full-log no-rescan performance, device HZ 100/250/1000, New Game misselection, stalled load with spinner frames, SIGKILL without matching kernel OOM, SIGKILL with matching notifier, and cleanup after panel wake. Output a documented run identity and error taxonomy.

**Change set 2: GPU inventory and guard.** Extend runtime/lamentum-adapter.patch at the native/nvn_textures.h / nvn_framebuffers.h / GL allocation and EGL surface paths to log resource identities/generations and per-class estimated bytes with sparse snapshots. Build host fixtures for identical-name reuse, 4-MRT+depth accounting, MSAA, texture pool alias, deferred vs materialized BC, and a resource whose GPU fence is pending. Introduce **guarded counters before changing allocation strategy**. Collect safe, early pre-OOM device windows and rank the highest live owners.

**Change set 3: guest-CPU hotspot receipts.** After the memory guard is in place, run a phase-tagged MOMO_STACK_SAMPLE_* probe; analyze with tools/analyze_guest_samples.py, map the top 3 owner-private guest PCs, and explicitly report how much time is actually on-CPU versus runnable or blocked. Produce one microfixture and one targeted source patch only if the top hotspot points to a demonstrable compatibility-runtime defect.

These are **implementation instructions, not claims that those changes are already merged or measured**. Publish evidence and tests for each step before moving on to another optimization.

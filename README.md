# Lamentum — experimental Switch-to-Linux-ARM64 port (TSPS / SpruceOS)

**ACTIVE post-build262 roadmap (2026-10-23; latest local result in [CMA reboot observation](evidence/cma-reboot-observation-2026-10-23/README.md)):** [evidence-led recovery and 30 FPS plan](docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md), superseding older *next-action queues*. The roadmap originated with the `main@3cb6b81` source/evidence audit and is locally extended after `main@c4a5714` with K1-E/K1-F and candidate-launcher evidence; see [§10 audit](docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md#10-main3cb6-re-audit-and-next-implementation-slices-2026-10-23). H1 compile/link-input reach is complete locally; H2 alias telemetry is partial, with persistent completion/retained-storage accounting still open. K1-B confirms the active 128 MiB CMA pool and strongly associates `/dev/dma_heap/reserved` with the default CMA heap. K1-C shows the current native Kbase page path uses non-movable `GFP_HIGHUSER|__GFP_ZERO`, whose matched-kernel fallback excludes CMA. K1-D verifies the default `system` DMA heap page requests also lack movable/reclaimable flags and use an Unmovable fallback without CMA; this classifies the generic heap path, not Lamentum's consumers. K1-E narrows only the expected userspace loader chain; K1-F's 12:11Z pair was `608 KiB` and its visible system-exporter buffers mapped to MainUI and platform `display_text.elf`. The later post-stage D pair at 12:52Z measured `CmaFree=792→1,332 KiB`, still with no order-7+ blocks; no safe process lifecycle or owner attribution was found. Game-specific GL allocation ownership remains unknown. The refreshed post-H2a ELF/helper and candidate launcher are staged and read-back verified in the hidden non-autostart path (see [host-build](evidence/current-elf-host-build-2026-10-23/README.md) and [stage/preflight](evidence/current-host-elf-staging-preflight-2026-10-23/README.md)). Build262 remains uninstalled; `build259` remains active and any runtime needs a fresh positive preflight **and reviewed per-run safety margin**. **NOT PLAYABLE; no verified first-world FPS.**

**K1-F owner-audit sample (2026-10-23 12:14Z; superseded by post-stage D):** The latest complete same-boot pair at `12:11:19.541→12:11:55.851Z` remained `CmaFree=608 KiB` both samples; `MemAvailable=662,652→663,192 KiB`, `Cached=579,288 KiB` and `SwapFree=2,065,116 KiB` stayed stable. `CmaTotal-CmaFree=130,464 KiB` is a gauge difference, not pinned-memory attribution. `nr_free_cma=152`; the free CMA histogram counted 149 pages (3-page asynchronous-read discrepancy) and no order-7+ blocks. Across eight earlier same-boot snapshots, the six global DMA-BUF `(inode, exporter, size)` tuples and MainUI FD set were identical, all exporter `system`. Current bounded ownership scan maps inodes 1/3/4/5 to MainUI `2369/1079` and 6/7 to Spruce `display_text.elf` `31142/1800687`; both platform-managed processes hold `system` heap, `/dev/mali0` and `/dev/dri/card0`. The scan was partial by one unreadable proc identity, with no FD errors/truncation; all six visible DMA-BUFs were mapped. No `reserved` exporter was observed. `CONFIG_CMA_DEBUGFS` and `CONFIG_PAGE_OWNER` are unset, debugfs/tracefs are not mounted, `/sys/kernel/mm/cma` is absent; no such owner data is available read-only. CMA alloc counters remained `8/0`, filtered dmesg had zero allocation/OOM matches. No safe user-process lifecycle to restore headroom was identified; do not stop/kill these system processes. Candidate ELF/helper remain inert, candidate launcher host-verified but not yet copied, build259 active, no game. `T2_STORAGE_MARGIN_MIB` is unset; D remains **HOLD_RUNTIME**. [K1-F owner/debugfs receipt](evidence/k1f-cma-owners-debugfs-2026-10-23/README.md).

**Post-stage D/read-only status (2026-10-23 12:51–13:11Z):** Candidate launcher S readback at `12:51:43.063Z` verified SHA-256 and executable mode; root launcher/build259 unchanged, no game/pending command. Complete D pair at `12:52:30.558→12:52:56.247Z` showed `CmaFree=792→1,332 KiB`, no free CMA blocks at orders 7–10, and no `cma_alloc_fail`, swap or major-fault deltas; dmesg filter at `12:53Z` matched zero warning lines. The updated `/proc` census at `13:11:28Z` is complete/non-atomic with MainUI+principal identities stable, one confirmed exit race, no persistent errors/PID reuse/game/pending command. Runtime remains **HOLD_RUNTIME**; no game launch. See [CMA reboot observation](evidence/cma-reboot-observation-2026-10-23/README.md).

**CMA recovery observation (2026-10-23 14:07Z):** boot ID changed from `15b97fe4-5c48-412c-ba39-92efb1823286` to `76212e98-f521-4f2e-8e93-76f58f48991a`; the agent did not issue a reboot command, so the initiating actor is unconfirmed. Complete post-boot samples at uptimes `115.96`, `340.99` and `905.30 s` each showed `CmaFree=130,412 KiB`, stable MainUI/principal, no game/pending command, no CMA/OOM warnings and the same four `system` DMA-BUFs. The preboot `2,008 KiB` sample was about nine minutes before the estimated transition, so this is descriptive cross-boot evidence, not page-owner attribution. No game launched; runtime remains **HOLD_RUNTIME** and `T2_STORAGE_MARGIN_MIB` remains unset. **Do not reboot again for this experiment.** Initial host H3 reducer added; 14 focused and 427 full tests pass. It preserves M3B decode/GL-allocation/upload subintervals, retains the raw `nvn-object-id`, and leaves semantic generation unknown without a source/ELF match for that run. Available local build-262–266 source copies did not match the candidate source-tree digest. Owner-ID/value mismatch fails closed. No complete raw owned bundle is available for a measured waterfall. [H3 receipt](evidence/m4b-h3-waterfall-2026-10-23/README.md). [Observation receipt](evidence/cma-reboot-observation-2026-10-23/README.md); [preflight](evidence/cma-reboot-preflight-2026-10-23/README.md).

**CURRENT OPERATING RULE — [roadmap §15](docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#15-revised-publication-install-and-runtime-testing-gates-2026-10-23-overrides-indefinite-device-no-go):** M4-A is already merged and host-verified at [509cc985](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/509cc985893e). **Never hold a source PR/host build because of an old CmaFree sample.** Safe copy/verification/installation of build262 **without automatically launching it** is a separate staging step requiring disk/identity/backup/rollback checks, not a CMA quota. A short no-input runtime launch requires **fresh complete read-only same-boot CMA/fragmentation/pressure preflight**, positive justified allocation headroom and existing protective guards; if the historical dangerous ~15 MiB state persists unexplained, hold runtime, not development or staging. No game-world or ≥30 FPS result exists. This policy supersedes older blanket "device NO-GO / no install" language, which now describes historical device state only.

**Evidence-led roadmap audit snapshot (2026-10-23, source main@1604ed9):** [post-build260 roadmap §13 — measured facts, exact next host PRs, CMA/device gates, world bring-up and FPS qualification](docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#13-evidence-first-execution-gates-after-the-main1604ed9-re-audit-2026-10-23). That review did **not** prove physical CMA backing; build259 remained the last device-tested runtime and build260 host-only. It identified the checked BC stripe/small-mip planner plus an actually executed native fixture as the first host PR; next were GL/EGL/buffer attribution and exact-kernel allocator analysis. This is an audit snapshot, not a gameplay/FPS result.

**Earlier K1/A1 source review (2026-10-23, reviewed tree `main@c05f879`):** [Detailed implementation queue §11](docs/post-build260-cma-gameplay-performance-roadmap-2026-10-23.md#11-post-k1a1-re-audit-at-main-c05f879-2026-10-23) and [cumulative roadmap §93](docs/performance-roadmap-30fps.md#93-post-k1a1-re-audit-and-m4-host-only-critical-path-2026-10-23) recorded K1/A1 as complete and M4-A as the next host-only step. It did not qualify a device launch.

**Current execution update (2026-10-23; detail in [roadmap §10.9](docs/post-build262-gameplay-recovery-roadmap-2026-10-23.md#109-h2a-alias-generation-diagnostic-and-fresh-d0-preflight-2026-10-23)):** H1 compile/link-input reach is complete on its recorded source snapshot. H2 now has a per-object/per-generation alias-view diagnostic wired to one real zero-storage texture/renderbuffer path; it still does not track physical backing, GPU completion or safe retirement. Full host suite **405/405**, zero skips; required callsite fixture and pinned AArch64 target fixture passed. Fresh D0 pair is complete/stable, but **the game was not launched**: D-policy and reviewed per-run `T2_STORAGE_MARGIN_MIB` remain unresolved. Installed build259 SHA is unchanged; the refreshed current-source ELF is inertly staged but not activated. Title remains **NOT PLAYABLE**; gameplay/FPS unverified.


**Latest device diagnostic (build259 margin sweep, 2026-10-23):** [report](evidence/m2b-e3-build259-margin-sweep/README.md). Per-run margins 64/48/32/24 MiB all stopped at typed `T2_STORAGE_ADMISSION:cmafree-margin` before the menu. The 24 MiB arm left `CmaFree=14,244 KiB`; a later 30 s idle pair stayed at `15,456 KiB`, below the previous order-4 warning context. No gameplay/FPS claim; port remains **NOT PLAYABLE**.

**Installed diagnostic artifact:** build259 SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`; `.before-259` preserves verified build256b. Floor96/cap300/strict GL were unchanged and no margin is set in the launcher. The 302-test host suite and 435/435 source baseline passed; this is an instrumentation/admission candidate, not a performance win.

**Historical roadmap snapshot (2026-10-23; superseded by §94):** [§78 latest source/evidence audit and PR order](docs/performance-roadmap-30fps.md#78-post-build251-device-ab-audit-memory-headroom-and-playability-critical-path-2026-10-23), [detailed post-build251 plan](docs/post-build251-device-audit-roadmap-2026-10-23.md), and [§86 build259 margin-sweep result](docs/performance-roadmap-30fps.md#86-m2b-e3-build259-device-margin-sweep-hard-stop-2026-10-23). M3-A1 remains default-off/inconclusive: all six build251 arms stopped at the memory floor and candidate pixel parity is unverified. The next safe work is host/source diagnosis of missing owner joins 280/288; device work remains stopped until CMA headroom is safely recovered. Do not enter New Game. World/input/audio/save-load, no-swap gameplay and ≥30 FPS remain unverified.

**Historical audit (2026-10-21; audited HEAD a0aa160):** [Performance roadmap §48 — post-build232 next PRs](docs/performance-roadmap-30fps.md#48-post-build232-audit-surviving-the-menu-reliable-new-game-world-pixels-and-a-credible-30-fps-path-2026-10-21). The port is **NOT PLAYABLE**; no real gameplay FPS has been measured. This source/evidence re-audit found that tools/navigator.py can confirm on a duplicate present serial, tools/nav_chain.py still polls the full unowned latest.log, and the existing screenshot comparison calls a tolerance<=2 match "identical". The four 1920x1080 menu targets cost **31.64 MiB** in total, but scaling all four to 1280x720 would save at most **17.58 MiB nominal storage**, not 31.64 MiB, and physical Mali savings remain unverified. The next steps are owned frame-based navigation, proactive safe menu-memory accounting/admission, a reversible single-factor scale A/B only with approval, then correctly verified New Game and first-world pixels. This documentation audit added **no** device result or performance claim.

**Previous 2026-10-21 audit (HEAD 0a8b1b05):** Navigation and serial observations described in roadmap §40 were subsequently refined by §42–§48. Treat that earlier assessment as historical; the latest §48 re-audit is above.


**Historical observer validation:** [two build219 menu-only principal-flow runs](evidence/harness-live-02/README.md) exercised the repaired observers/exit taxonomy. Both ended with TIME_LIMIT and clean menu/CPU restoration; the first exposed a VFAT executable-path alias discovery bug, fixed and verified on the second. This is measurement validation, **not gameplay or an FPS improvement**.

**C0 measurement correction and component validation:** [detailed audit](docs/c0-profiler-audit.md) withdraws the later incomplete TLS timing verdicts (including "C1 closed", 1.98 ms/present and 0.293% core). A rebuilt bounded all-thread collector passed **126 host tests**, **435/435 baseline validation**, and a separate CPU-only TSPS ON/OFF fixture: **4 retired thread generations / 12 rows**, with exact short-call tails and real Spruce cleanup. This is collector validation, **not a game performance result**. Build225 is built but not deployed; installed build223 remains unchanged. Follow [roadmap §32](docs/performance-roadmap-30fps.md#32-head-0caf515-current-gameplay-blockers-and-next-implementation-queue-2026-10-21) and the factual follow-up **§30**; C0, G0/id295, world activation and 30 FPS remain open.

**G0 admission arithmetic (partial):** [checked storage layout report](docs/g0-storage-layout.md) adds overflow-checked per-mip/layer/face/sample payload calculation and uses it before deferred-BC first-use admission. **138 host tests PASS** (12 new G0 tests, including 1024 randomized reference cases), 12 trap-on-UB tests and **435/435** baseline validation; pinned ARM64 **build226 succeeds but is not deployed**. Lazy eligibility remains **single-mip**; id295's actual format/mips, physical GPU residency, all-class ledger and transactional GL lifetime remain unproven. No device or FPS claim; roadmap **§31** records this component step; **§32** defines the current execution queue.

**Navigator P0-N2 fixes (owner §40.3):** [contract](docs/navigator-p0n2.md) implements the owner's required rules in `tools/navigator.py`: explicit `IDLE → ACTION_ISSUED → AWAIT_NEW_PRESENT → DONE/REFUSED` state machine, **direction from ordered row indices** (so `options→newgame` presses **up**), a multi-row move **refused by default** with no follow-up press, recovery only behind an explicit diagnostic flag, and a confirm issued only after **two newer agreeing observations** that must lead to `NEWGAME_CONFIG`. A non-menu page without a preceding confirm is refused. Bounded short-press sweep values `80/150/250/400 ms` are declared. **206 host tests PASS** (16 navigator + 8 chain tests covering every case the owner listed). No device press in this step; the config-page fingerprint (§40.4) and menu-memory waterfall (§40.5) remain open.

**M1 texture basis (§69):** [device report](docs/tex-levels.md) keeps build247's decoded-vs-compressed measurement and the build248/249/250 follow-ups. Build250 joins 93 per-object live T2 charges to 115278848 B and replays 90 GL-storage records / 244815152 declared bytes at the floor sample; physical Mali residency and completion remain unproven. The 96 MiB floor stays unchanged; no memory optimization or gameplay result is claimed.

**M1 three bases (§68):** [reconciliation](docs/ledger-bases.md) pairs declared payload, budget charge and `gpu_memory` from one owned run: **depth matches to the byte** (11980800 B in both accounts), while textures differ **2.0948×** (230.30 vs 109.94 MiB) with no established cause. `gpu_memory` reaches 84900 units with total declared payload 241.72 MiB; its unit is unverified, so no physical total is claimed. New `tools/ledger_bases.py` refuses foreign/mixed run identity. 273 host tests PASS; STOP T2_MEMORY_FLOOR, Spruce restored.

**M1 life events by class (§67):** [device report](docs/life-events-classes.md) splits the opt-in ledger: **238.84 MiB declared across 90 live textures + 11.43 MiB across 2 depth renderbuffers**, 25 deletes, peak 257.72 MiB, and 92+25+50 = 167 calls closing exactly. Buffers read 0 (those paths are off) and `glBufferData` is now counted as a replacement, not an addition. Declared payload is not Mali residency and is not reconciled with the 109.9 MiB budget charge. Build245, STOP T2_MEMORY_FLOOR, Spruce restored; 266 host tests PASS.

**M1 life events (§66):** [device report](docs/life-events.md) instruments an opt-in bounded ledger (512 entries, off by default) at the texture upload/delete sites. Build244 arm: 112 images created, 24 deleted, **24/24 deleted GL names reused**, 88 live images holding 222.05 MiB declared payload; `delete-with-views=0`, `alias-views=0`. Name-keyed accounting/deletion is therefore measurably unsound; renderbuffers/PBO/EGL and GPU completion remain uninstrumented. Off arm produced no summary. STOP T2_MEMORY_FLOOR, Spruce restored; 266 host tests PASS. A trailing-digit formatter defect was fixed before measuring.

**M1 lifetime core (§65):** [host report](docs/lifetime-core.md) adds a bounded generation/alias/retirement contract in the overlay: distinct object and storage generations, shared-view charging, last-reader completion and context-loss refusal. No GL caller, deletion, admission or quality change; installed build241 unchanged. 265 host tests PASS; C fixture (57 assertions) + ARM64 fixture compile; no device run or memory/FPS claim.

**M1 sampler census (§64):** [offline report](docs/sampler-census.md) records 630 generic menu sampler events; NVN81/92 absent there but with source-write receipts, which is not proof of unused/immutable storage. No runtime change.

**M1 late window (§63):** [device report](docs/storage-late-owner.md) locates the 53.39 MiB Native descriptor during NVN92 / GL47 / 3600x3600 upload. A second 49.45 MiB descriptor disappears before the next sample; its VA later reappears with smaller commit. No exclusive lifetime/physical-free proof or quality/storage change. Build241, floor96/cap300, STOP frame4, restored Spruce; host258 tests PASS.

**M1 descriptor retention (§62):** [same-run report](docs/storage-descriptor-retention.md) separates owner81's upload-window descriptors: 29.67 MiB disappears by the next observation, while 31.30 MiB remains at eight observation points over 6.192 s. No physical refund/lifetime proof or safe deletion follows. Same build240/floor96/cap300; STOP frame8, Spruce restored; 258 host tests PASS.

**M1 GL/Mali brackets (§61):** [device report](docs/storage-mali-brackets.md) records 12 valid default-off build240 probes. NVN81 / GL texture39 / 3600x2160 upload coincides with Native descriptors 29.67 and 31.30 MiB; exclusive ownership and lifetime remain unproven. Floor96/cap300 unchanged; STOP at frame7 and Spruce restored. 254 host tests PASS; no FPS gain.

**N4-C/D owned driver (§60):** [integration report](docs/n4-owned-driver.md) replaces the per-tap navigator reset with one UUID/generation-pinned reader/navigation instance, brackets capture/input with process checks, requires explicit release ACK, and refuses rotation/overshoot terminally. Confirm blocked; explicit diagnostic opt-in and timeout required. 253 host tests PASS; no new device/input/FPS qualification.

**N4-A/B host-core correction (§59):** [regression report](docs/n4-unique-confirm.md) fixes duplicate/out-of-order serial Confirm and confirmation evidence carryover. Bounded monotonic deadlines replace the three-poll stale limit; nine new tests, 239 host tests PASS. End-to-end owned navigation/release ACK and device-calibrated timeout remain unqualified. No device/FPS claim.

**M1 attribution correction (§57):** [same-run smaps reconciliation](docs/smaps-owner-reconciliation.md) retracts the claim that RssFile measures reclaimable game-image pages. A fresh 96 MiB-floor run shows status VmRSS=710072 KiB versus summed smaps Rss=445536 KiB; the gap has no proven owner. No drop hint/storage change was made. Four parser tests, 227 host tests PASS; device restored with DRM screenshot.

**RSS by class (owner §48 / M1):** [per-class series](docs/rss-classes.md) adds `LC2_MENU_RSS` (`RssAnon`/`RssFile`/`RssShmem` from `/proc/self/status`, `-1` for unknown) and shows the pre-first-frame step split as **anon +240.8 MiB / file +255.0 MiB**; at steady state anon falls 363→219 MiB into swap while file rises to **492.2 MiB**, so the footprint is a small anonymous core plus a large resident image working set, with `shmem` negligible (~0.26 MiB).

**RSS split: the pre-first-frame step is our own process (owner §48 / M1):** [measurement](docs/rss-split.md) uses existing ledger fields across two arms: `MemAvailable` -471.4/-433.8 MiB while `Cached` **fell** 55.6/52.6 MiB, `AnonPages` grew +240.4/+241.3 MiB and **own `VmRSS` grew +521.0/+519.2 MiB** before the first frame. So page cache is not the contaminant (it was reclaimed into the process); the owner is our own RSS - about half anonymous, about half file-backed image pages. At the stop, RSS 731.7 MiB + swap 415.1 MiB = ~1.12 GiB on a 963 MiB board, which is why the floor stop is arithmetic rather than tuning.

**Map receipts, phase correction (owner §48 / M1):** [phase report](docs/map-ledger-phase.md) adds unmap receipts and periodic summaries (build237 `ee28f264`) and corrects §53 three ways: `alias_physical` first appears only after the menu floor-limited window (clean arm: 13 blob events = 69.95 MiB, then zero alias events before the stop at frame 42); `svc 1` main-heap stays unused; and the -471.5 MiB `MemAvailable` step is contaminated by page cache from the 1.74 GB image, so "the guest reserves N MiB" is not a claim this data supports.

**Map receipts: who reserves the guest memory (owner §48 / M1):** [receipts](docs/map-ledger.md) add `LC2_MAP_LEDGER=1` and find that `svc 1` main-heap reservation is **unused** by this title, while **blob/file mappings are 69.95 MiB (13 maps)** and **`alias_physical` is ≥124.6 MiB (≥36 maps, one 64 MiB and one 32 MiB piece)** — still growing when the bounded window closed, so a floor not a total. The first arm was a recorded tooling defect (blob lines consumed the bound); the second ended in a **kernel OOM kill** and is labelled a failed arm, not a STOP result.

**Early menu ledger: the big drawdown is the guest heap (owner §48 / M1):** [ordering report](docs/menu-early-ledger.md) moves the first ledger record to GL init (build234 `571463a4`) and reorders the story: at `gl-init` available is **568.7 MiB** and CMA is **already 0.75 MiB** — exhausted before any of our textures exist — then CMA recovers to 23.5 MiB at `first-present`, while available falls to **134.9 MiB (−433.8 MiB)** before the first frame. The three 1080p colour targets plus two depth buffers are ~35 MiB of that; the rest is the guest's own reservation, which the old 1 Hz series started too late to see. Retire receipts added; no retire events occurred, so allocate/free balance is unproven.

**Storage-class allocation receipts (owner §48 / M1):** [receipts](docs/alloc-ledger.md) add `LC2_ALLOC_LEDGER=1` (bounded, opt-in, no GL change) and one arm: the depth class is **2 objects / 11.98 MB** (1920×1080 + 1280×720), which **corrects my earlier 22.9 MiB estimate** (0x88f0 is 4 bytes/pixel, not 8). Both depth buffers and the three 1080p colour targets exist **before the first ledger record**, so ~33 MB of 1080p images are created in the pre-observation window — which is why `arm-start` already shows CMA at ~20 MiB, and why CMA then churns at 27→0.01→16→0.05 MiB. EGL surface (SDL-owned path) and buffers (no vertex streams in the menu) stay unmeasured and are labelled so.

**Menu floor analysis (owner §48 / M1):** [arithmetic report](docs/menu-floor-analysis.md) adds `tools/floor_analysis.py` (5 tests) and explains the two observed stops on measured receipts: the menu draws **74.6 MiB in 4.5 s (16.46 MiB/s at 3.31 fps)** from a 129.3 MiB start, so the **96 MiB floor is crossed within the first burst** (projected 2.02 s; measured stop at frame 2), while the 32 MiB floor survives to frame 55 because reclaim/swap recovers most of the early loss. Ranked drawdown: CMA 24.3→0.0 MiB, swap 0→422 MiB, charged textures +50.2 MiB, colour targets +15.9 MiB, untracked driver/EGL. The 720p scaling upper bound recomputes to **17.58 MiB**, matching the owner's correction.

**N1 owned serial (roadmap §40.2, now §49):** [report](docs/n1-owned-serial.md) retires `serial_request()` and its full-log `re.findall` scan — which raised `ValueError` on the first present and cost O(log size) per poll with no generation check — replacing it with `load_metrics.OwnedSerial`, an incremental owned-collector reader. A rejected generation returns `serial: None`, never the previous run's counter, and `present_serial()` now counts complete lines only. **217 host tests PASS** (multi-record 1/42/9 → 42, run A frame 50 → rotation → refuse, partial line, cursor advance, 30 000-record backlog). Device acceptance with the new reader is still open; `nav_chain` now uses it.

**Where 1920×1080 comes from (investigation):** [origin report](docs/1080p-origin.md) — the 1080p images are created by the **game itself** with instruction literals (`mov w21,#0x438` / `orr w1,wzr,#0x780` at `main+0x53bfcc…0x53bfdc`), not by our display answers: the window path is `NVN_WINDOW_REAL framebuffer=1280x720`, the resolution query answers `1280×720`, and the adapter has no docked/operation-mode report at all. The 720p storage change is therefore a policy change with an existing switch (`ZERO_RENDER_SCALE=2` maps exactly this family), already recorded in the roadmap as performance-negative and off by default.

**Menu target inventory (owner §40.6 / B2-lite, step 2):** [inventory](docs/menu-target-inventory.md) adds a bounded per-target receipt and names what the menu holds: **19 targets, 43.39 MiB charged**, of which **31.64 MiB is four 1920×1080 images (three colour + one depth) although the panel is 1280×720**; the busiest target is the 1280×720 colour at 513 draws, and the 12-step post cascade costs only 1.21 MiB. The figure matches the independent 43.4 MiB colour-target estimate from the ledger. Charged ≠ Mali residency, and no last-reader epoch exists, so nothing may be freed yet. No scene, id295 or FPS claim.

**Menu class attribution (owner §40.6 / B2-lite):** [attribution](docs/menu-class-attribution.md) adds per-class estimates to the ledger and runs build231: at the low point `MemAvailable` is **51.8 MiB (−78.1)**, `CmaFree` **0.85 MiB** (exhausted from 28.0), game `VmSwap` **417 MiB**, while the adapter sees **textures +50.1 MiB** and **3 extra colour targets (+15.9 MiB)**; the two depth renderbuffers stay **constant** at 22.9 MiB and `scaled`/`half`/`bc-pending`/`joined` are all **0**. So the menu's loss is texture+colour-target growth plus untracked driver/EGL storage, and CMA is a 28 MiB pool the menu alone drains. No scene, id295 or FPS claim.

**Menu-phase memory waterfall (owner §40.5 M0):** [waterfall](docs/menu-memory-waterfall.md) adds an opt-in `LC2_MENU_LEDGER=1` (≤1 Hz, host-observable only, no behaviour change) and one build230 arm: `MemAvailable` drops **129.3 → 54.7 MiB by frame 16 (4.5 s)**, **CMA is exhausted** (24.3 MiB → 1.0 MiB), game `VmSwap` grows to **422.4 MiB**, while charged texture storage explains only **+52.6 MiB**. The menu, not the world atlas, is the immediate bottleneck — and CMA is the first measured dominant candidate. Renderbuffers/buffers/EGL storage are labelled `untracked`. No scene, id295 or FPS claim.

**Short-press sweep (owner §40.3 item 5):** [sweep report](docs/nav-short-press-sweep.md) tried 80/150/250 ms with one press per attempt and a required new serial: **80 ms and 150 ms both moved 0 rows** (qualified, serials 17→21 and 21→45), while 250 ms was **not reached** because the arm ended mid-sweep. With earlier 350 ms→0 and 900 ms→2 rows, the one-row window lies between 400 and 900 ms — and the sweep cannot finish because the menu run only survives ~30–55 presents. **210 host tests PASS**. That makes the §40.5 menu-memory waterfall the gating next step, not more presses.

**Tap-length A/B on the live menu (roadmap §32.7 item 3):** [measurement](docs/nav-tap-length.md) makes the chain repeatable (`tools/nav_chain.py`: oracle + navigator + the port's own present counter + owner-checked pad). A **350 ms** tap on `load` produced **no move** with a qualified serial (19 → 23); the earlier **900 ms** tap moved **two** rows. The one-row window therefore sits between them, and two 550 ms attempts are recorded as **failed orchestrations**, not results — the first started the chain before the arm and its arm was then **kernel-OOM-killed** (rc 8, no runtime STOP), the second read a zero present counter from a fresh log. The tool now waits for the first present counter instead of refusing a valid frame. **199 host tests PASS**. No config page, Loading, scene, id295 or FPS claim.

**First press→row chain (roadmap §32.7 item 3):** [chain report](docs/nav-press-chain.md) captures a live `MAIN_MENU` at row **`load`/442**, injects one owner-checked `down` press (900 ms), and reads the next frame at row **`options`/542** — one press moved **two rows**, the hold-length overshoot reproduced on hardware (the core already classifies it as overshoot rather than two presses). The oracle read the menu correctly at two different cursor positions. The present serial was **not** read in this arm (helper used `latest.log` instead of `logs/latest.log`), so the press is not yet serial-qualified; the reader is fixed with tests. **190 host tests PASS**. Device clean afterwards. No config page, Loading, scene, id295 or FPS claim.

**Measured page/cursor oracle (roadmap §32.7 items 1+3):** [oracle report](docs/page-oracle.md) adds the capture side the navigation core was missing and, on one in-run frame of build229, **refutes the recorded menu geometry**: rows are at y **442/492/542/592** (pitch 50), the selection is a **cursor glyph left of the row** (x 40..120, dimmer than its own text), and text starts at x 140. On the real capture the oracle returns `MAIN_MENU / load / cursor_y 442` and the core emits `press down` for serial 55; a boot frame is refused as `UNKNOWN`. **188 host tests PASS** (8 new oracle tests). No input was injected in that arm; the first press→row chain is recorded separately in §39. No scene, id295 or FPS claim.

**Navigation core (roadmap §32.7 item 3):** [decision contract](docs/navigator-core.md) adds the single pure navigator that the harness and both probes are meant to share: one press per **new** present serial, refusal when the serial stops advancing, two-row moves reported as **overshoot** rather than extra presses, and no page change inferred from an animated picture. **180 host tests PASS** (10 new), superseded in count by the oracle step below; the capture-side oracle now exists and reports measured rows, but nothing is wired to the device yet and both legacy navigators stay disabled. No scene, id295 or FPS claim.

**build229 menu regression arm (roadmap §32.2 first step):** [evidence](evidence/menu-229-02/README.md) installs the hash-verified build229 with its mandatory helper and runs one bounded principal arm at `COTM_GL_ERROR_IGNORE=0`, `T2_TEXTURE_BUDGET_MIB=300` and a **diagnostic** 32 MiB floor: **55 presented frames, 52 with pixels**, and the corrected upload path executed on the real **8192x4096 BC atlas (id291)** with **zero** GL-error lines. The arm then stopped at its own memory floor (`available-MiB=29`, `VmSwap=496 MB`). The B1 receipt did not fire (no deferred-BC first use in the menu). Menu regression only: **no scene, no navigation, no id295 resolution and no FPS claim**; the default 96 MiB floor stopped the same arm after 2 frames (`menu-229-01`).

**B1 pre-refusal owner receipt (roadmap §32.4, component):** [receipt contract](docs/bc-owner-receipt.md) adds an opt-in, bounded, no-guest-read descriptor emitted **before** the deferred-BC budget charge, so a refusal no longer destroys the id295 evidence. **170 host tests PASS** (4 new, compiled against stubs), **435/435** baseline, ARM64 **build229** `b164cffd…4e82f`, installed and exercised in the §36 menu arm. Unmeasured fields are labelled `unavailable`/`unproven` rather than zero. The receipt cannot fire until a run reaches first use, which still needs the guarded New Game arm and a verified navigator; B2's all-class ledger remains open. No game run, no id295 resolution and no FPS claim.

**GLES upload triples (roadmap §32.3/PR A, contract half):** [format mapper report](docs/gl-upload-format.md) removes the overlay's use of one value as both sized storage and client format in five decoded/refresh paths; `native/lc2_gl_format.h` maps sRGB/linear 8-bit and float payloads per context generation and refuses what it cannot express. **166 host tests PASS** (7 new), **435/435** baseline, ARM64 **build228** `9f348c6c…00af` built but **not deployed**. A self-authored surfaceless GBM fixture on **Mali-G57** decoded a stored byte 160 to 90 (exact sRGB value) against a 160 linear control, with byte-exact partial-stripe, mip and context-recreation checks. The retired double-use triple is rejected as `GL_INVALID_ENUM` in an explicit ES3 context but silently tolerated in the version-2 request — so this is a correctness/portability fix, **not** a proven Loading-stop cause. No game run, no id295, memory or FPS claim.

**T1 owned-log safety (partial, follow-up §33):** [implementation and limits](docs/t1-owned-log.md) add target-kernel UUID/nonce, pinned-FD exec, generation-bound collectors and exact-owner pidfd stop receipts. The paired helper is mandatory; both legacy navigators now refuse default unverified navigation. **159 host tests PASS**, clean-export ARM64 **build227 PASS**, **435/435** baseline and packaged-helper verification; final collector executes on TSPS Python 3.10.4 and rejects the old unowned log. **Not deployed and no game run.** Image/catalogue binding, semantic navigation and scene receipts remain open. The owner's **§32** execution order is unchanged; this is a component result, not T1 completion, id295 progress or 30 FPS.

**C1 owner follow-up:** [source/ELF-pinned AudioOut audit](evidence/C1-audio-owner/README.md) resolves endpoint0x40 as the audout:u child: cmd7 appends PCM and cmd8 retrieves released buffers. Correct SVC-specific mutex operands yield 41 addresses in load-probe-08, not the former 1,011 mixed argument values. Actual complete executing handler/bridge cost is still unmeasured.

**Status: NOT PLAYABLE (world-frontier evidence remains build218–219; later measurement attempts are qualified in the C0 audit).** The device reaches the real main menu, New Game configuration, controls page and Loading; the catalogue contains **46 entries (0–45), including seven TEST substitutes**. Fragment45 linked in [newgame-20](evidence/newgame-20/summary.json), but real world rendering, player movement, audible audio, cold save/load and sustained gameplay FPS remain **unverified**.

**Newest load evidence:** [load-probe-03](evidence/load-probe-03/summary.json) reproduced a kernel/Mali OOM around **709 MiB GPU accounting**; the runtime tracked **411 MiB live textures** against its nominal 420 MiB limit. [load-probe-04](evidence/load-probe-04/summary.json) and [load-probe-07](evidence/load-probe-07/summary.json) show that **T2_TEXTURE_BUDGET_MIB=300** converts the later unsafe allocation into a clean **T2_TEXTURE_BUDGET** stop. The immediate trigger is the first-use **8192×8192 RGBA reservation (256 MiB), resource id=295**. This is safer but **still cannot reach gameplay**; other Mali-accounted resource classes remain unresolved. [load-probe-05](evidence/load-probe-05/summary.json) also demonstrated that a 1280 MiB fileback cap could not fit the SD-card reserve.

**Independent Loading CPU problem:** a prior measured 20.14-second window consumed **0.836 s of main-thread CPU per presented Loading frame**, even without new RomFS/texture/BC events. This is **not gameplay FPS**; sample the guest PCs and thread CPU/wait states before shader or compiler optimization claims.

**Newer load evidence (build218–219):** [load-probe-08](evidence/load-probe-08/summary.json) sampled an intensive SVC/IPC path (0x1A/0x1B mutex arbitration; endpoint0x40 commands 7/8). Its round-robin MOMO samples are **not** an aggregate CPU-time percentage; native caller/service identification and timed handlers remain open. [load-probe-09](evidence/load-probe-09/summary.json) verified incremental collector counters. [load-probe-10](evidence/load-probe-10/summary.json) used the installed **build219** executable and measured a 126 MiB charged-texture plateau while VmSwap grew to approximately 870 MiB in an **earlier Loading interval**. The probe ended with operator TERM, **not** a demonstrated texture-budget stop, and does not disprove the later id=295 memory wall. The file's [GPU ledger analysis](docs/gpu-ledger.md) explicitly avoids attributing the remaining resident memory to an unproven heap owner.

**CURRENT EXECUTION PLAN (source audit through 0caf515 on 2026-10-21):** [roadmap §32 — completed work, the remaining GPU/CPU/rendering blockers, and exact next PRs](docs/performance-roadmap-30fps.md#32-head-0caf515-current-gameplay-blockers-and-next-implementation-queue-2026-10-21) supersedes §29's priority order. **NOT PLAYABLE.** New Game reaches Loading but no actual world scene, physical player movement, audible game sound, cold save/load, or 30 FPS gameplay is established. **Completed:** 46 shader entries including seven TEST substitutes, guarded 300 MiB texture admission, CBUF glTexSubImage2D, source-identified AudioOut child and corrected mutex ABI, run/CPU observation repairs; V2 profiler passed a separate CPU-only TSPS fixture; G0 complete-mip format-defined size guard passed 138 host tests and ARM64 build226. **Not completed:** build226 game deployment, id295 original descriptor and source identity, transactional physical GL residency ledger, a proven Mali ETC2/EAC compressed texture path, real-game complete AudioOut/SVC/BC CPU profile, unambiguous T1 semantic scene/navigation/run identity, and the first world renderer/input/audio/save acceptance. The legacy sRGB decoded-BC upload argument mismatch still needs correction and synthetic GLES3 pixel tests. Do not equate host build/fixture checks with gameplay progress or bypass the 300 MiB guard: earlier id295 8192x8192 expansion caused a safe budget stop instead of the former correlated Mali/kernel OOM. The earlier 126 MiB charged-texture plateau and ~870 MiB VmSwap were from an **earlier Loading interval** and do not disprove that later id295 hazard. The 32 MiB RAM floor is diagnostic only. No new device game run was performed by the roadmap audit.

Earlier engineering milestones (build202 and predecessors; later results supersede their status claims): `docs/ui-cbuf-binding.md` (build202: one-field correction c4 -> NVN
UBO1, SDK/compiler provenance, replay of captured UI draws, actual menu/input
captures, save backup and frontend cleanup). `docs/hid-input-contract.md` (builds 198–199: direct guest-read
receipts, hash-pinned derivation of accessor Attach, retirement of the unrelated
head-table experiment, bounded long-press input probes). `docs/title-screen.md` (build 193:
title screen reached, shader tail closed by appending captured programs).
`docs/catalogue-tail.md` (build 191: the visible frame uses only real
programs, the 64-MiB floor was the load wall, and an append-not-regenerate cycle
closes the remaining shader tail; catalogue 34 → 37 programs).
`docs/probe-disabled-fragment.md` records the guarded real fragment translation
(TEST substitutes 8 → 7). `docs/shader-literal-bank.md`
records build 178's capture-validated literal specialization, and
`docs/cbuf-unit-isolation.md` the preceding same-binary A/B: 37 colliding
audit records versus zero, with physical captures. Memory history remains in
`docs/loading-memory-170-174.md`, `docs/loading-memory.md` and `docs/porting-log.md`.
The historical best loading probe initialized 522 textures before its physical-memory
floor; the new short rendering A/B does not establish an improvement to that limit.
Seven TEST shader substitutes remain; measured, none of them is drawn in the
current frame, so they are not on the critical path to a first menu. Lossless backing/deferred uploads preserve
original texture resolution and the owner image; the 420 MiB GPU ceiling is unchanged.

The installed launcher keeps experimental memory features off unless explicitly requested;
it uses strict GL checks, synchronous submission, SDL/KMSDRM and a 96 MiB memory floor.
The failed pageout experiment remains disabled. The historically verified installed menu binary was build202,
SHA-256 `ff4454232247b935748db7a76b05a7af27e62f2a189d199b49d7d6d93f9d1fd2`,
with its previous runtime backed up and an independent device read-back.
The visible-menu run still uses explicit diagnostic memory/GL settings, not the
strict production defaults. Build200's Start/SetActive tracing and native cache
reads prove the menu objects are active; build202 fixes their invisible UI by
selecting the measured application constant-buffer slot, not by activating game
objects or changing the game image. The temporary watermark experiment was
restored and is not a persistent system change.

This repository tracks the attempt to run the owner's Nintendo Switch copy of *Lamentum*
(Unity 2019.4.4f1, IL2CPP, ARM64) natively on a TrimUI Smart Pro S class handheld through a
recovered Horizon/NVN compatibility runtime — the same class of runtime used by
[west-of-loathing-portmaster-tsps](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps).

Nothing from the game is distributed here: no modules, no RomFS, no textures, no shaders, no
keys, no saves. Only our own tooling, the adapter patch and measured evidence are committed.

## Historical verified facts (2026-10-19; current status is above)

These are source/version facts and prior milestones from that snapshot. Shader catalogue size and current device outcome have changed in build218; use the opening status and the current roadmap for latest results.

- **Title identity**: `0100EC901551C000` (base v0), update `0100EC901551C800` v393216, NCA SDK
  version 10.9.0.0, NPDM stack `0x100000`, main priority 44, core 0, 46 services.
- **Engine**: Unity 2019.4.4f1, IL2CPP. Four NSO modules `rtld`, `main`, `subsdk0`, `sdk`;
  `main` text 30,836,964 B, `sdk` text 5,777,024 B; RomFS 1,829,445,184 B (34 files).
- **NVN bootstrap**: `nvnBootstrapLoaderInternal` at `sdk+0x496720` forwards with `b` at `+8`
  (not `+12` as in the West of Loathing SDK) to the lookup thunk at `sdk+0x45e0b0`
  (`adrp x8,#0x8c6e000` / `ldr x8,[x8,#0xdd0]` / `ldr x2,[x8]` / `br x2`); the resolved NVN
  lookup object lives in the runtime image at `0x0c4379a8` for module base `0x0b7dc000`.
- **Runtime build**: the recovered GPL baseline reconstructs to 435 files with matching
  SHA-256 (`tools/baseline-manifest.sha256`, 435/435 OK) and cross-builds for aarch64 in
  `pmjs-arm64-spruce-local:20261002-gcc10` with `runtime/lamentum-adapter.patch` applied.
  Base-only ELF (superseded): 1,808,328 B,
  SHA-256 `9265c9e3d77d83341a83d5f9ea4bca2fc05c42f67092f3d4205be790bfe61bb9`.
  Merged-content ELF: 1,808,328 B, SHA-256
  `9332846797605be9404ea814b54b06aaf3d64cd470a93550b2051c73b90e1a79`, GLIBC ≤ 2.27.
- **The port uses the merged (base + update v393216) content**, as a console with the update
  installed would: the merged ExeFS replaces `main` (23,861,213 → 23,878,177 B) and
  `main.npdm`, and 11 RomFS files differ (`global-metadata.dat`, `globalgamemanagers*`,
  `level0`, `level2`, `resources.assets*`, `sharedassets0.*`, `sharedassets2.*`). Merged RomFS
  image 1,832,059,520 B; its extraction was compared file-by-file with the merged tree —
  34/34 identical.
- **Adapter scope**: all runtime changes are carried in `runtime/lamentum-adapter.patch`;
  the 435-file recovered source baseline stays read-only and manifest-verified.
- **Shader catalogue**: 42 total source entries, including seven explicit TEST-only
  substitutes; entries 39 (guarded fragment), 40 (vertex), and 41 (fragment) were added for New Game shader-tail progression. Sampler/constant-buffer metadata is exercised on-device, but complete shader
  semantics, scene rendering and gameplay are not yet validated.

## Not done yet

- Handle any further shader tail reached by New game; the bounded menu run no longer stops on it.
- Resolve the incomplete scene rendering and the scene-loading memory wall.
- Replace TEST shader substitutes with validated translations.
- Validate gameplay controls, audible sound, save/reload and sustained performance.
- Resolve scene-load memory pressure and validate the transition beyond the working menus.

## Build your own copy

```sh
# 1. reconstruct the runtime baseline (GPL) from the owner's own release sources, then verify:
sha256sum -c tools/baseline-manifest.sha256      # 435 files

# 2. generate the owner image (segments + contracts + RomFS section) — owner data, never commit:
python3 tools/prepare_lamentum_image.py <exefs-dir> <npdm.json> <romfs.json> <image-dir>

# 3. cross-build (the container ships aarch64-linux-gnu-gcc 9.4):
docker run --rm --security-opt label=disable -e COTM_CC=/work/tools/cc-lamentum.sh \
  -v <baseline>:/reference:ro -v <image-dir>:/image:ro -v "$PWD":/work \
  --entrypoint /bin/sh pmjs-arm64-spruce-local:20261002-gcc10 \
  -c 'cd /work && bash build_lamentum.sh /reference /image /work/build'

# 4. install: port/Lamentum.sh -> /mnt/SDCARD/Roms/PORTS/
#    runtime + build/run_identity.py + section -> lamentum-switch/
#    Keep the launcher and its mandatory run_identity.py helper paired; incomplete installs refuse to start.
```

`tools/cc-lamentum.sh` only downgrades two warning classes (`unused-result`,
`unused-function`) that the pinned container's glibc headers produce in the baseline's own
diagnostic code, and selects `ZERO_ZX_GAME=0`; the baseline source stays untouched apart from
`runtime/lamentum-adapter.patch`.

## Layout

```
build_lamentum.sh              cross-build recipe (baseline + adapter patch + owner image)
runtime/lamentum-adapter.patch our only source change to the GPL baseline
port/Lamentum.sh               PortMaster-style launcher (principal-flow only)
tools/prepare_lamentum_image.py owner image + contract generation (fail-closed derivations)
tools/cc-lamentum.sh           compiler wrapper (warning classes + title profile)
tools/cc_trace_lamentum.py     opt-in compiler/dependency trace wrapper
tools/gl_compiled_reach_trace.py  per-TU preprocessing/dependency materializer
tools/gl_compiled_reach.py     source/compile/link-input site classifier
tools/baseline-manifest.sha256 435-file baseline identity
docs/                          porting log, architecture and measured evidence notes
evidence/                      device runs: logs, stop codes, captures
```

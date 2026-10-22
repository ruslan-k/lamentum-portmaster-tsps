# Lamentum TSPS — post-build251 evidence audit and actionable gameplay/30-FPS roadmap
**Reviewed:** 2026-10-23. **Source:** main at `00e5388fe71384dec98e98b6a303391b35771f17` (documentation-only follow-up). **Evidence:** six build251 paired device arms, published 2026-10-22. **Status:** NOT PLAYABLE. This is a code/evidence audit **without a new device run, new benchmark, or newly executed host tests**.

This supersedes the *action status* in [the original build251 plan](build251-evidence-and-gameplay-roadmap.md) §§1–2 and [the cumulative roadmap](performance-roadmap-30fps.md) §§75–76. Those earlier documents preserve their original historical observations. The build251 device result is [the six-arm evidence report](../evidence/m3a-bcstripe-b251-01/README.md), with [exact per-arm counters](../evidence/m3a-bcstripe-b251-01/ab-summary.json). For the last accepted pre-build251 budget replay, see [build250](../evidence/m2a-budget-20261022-01/README.md). Avoid mistaking the older source review's “device A/B pending” for today's state.

## 0. What is actually completed, and what the evidence rules out

- **Runtime/launcher:** ARM64 guest NSO + Horizon/NVN-to-GLES adapter exists, Spruce principal ownership and cleanup are exercised, sysfs CPU mode/value restoration is implemented, and the launcher works without an unavailable `stat`. An experimental title/menu, configuration/Loading navigation and some shader paths were demonstrated in *historical* runs, not build251. The shader catalogue is indexed 0–45 (**46 entries; 7 TEST-only substitutes**). None proves first-world rendering.
- **Accounting:** build250's T2 per-ID budget events and GL-storage journal replay reconcile *for that one run*: 115,278,848 B budget-live vs 244,815,152 B declared GL live on **different accounting bases**. They are not a physical-VRAM subtraction. Build251's six arms now introduce a **new, observed coverage failure**: four budget/pair joins fail closed despite zero reported event overflow.
- **M3-A1 has been executed** (same pinned build251 ELF SHA-256 `1bcb32a4bac2e1e30e4c64ab8bb5d8ddd58c3cc59363a785919991eac4ab6b78`; OFF/ON/OFF/ON/OFF/ON; floor96, texture cap300, strict GL, no input). All six runs ended at `STOP status=T2_MEMORY_FLOOR` with **zero menu events**, no owned OOM finding, zero counted GL-error markers and clean cleanup. **Keep `LC2_BC_STRIPE_MEDIUM` OFF by default**.
- The 1920×1080 BC3 owner-105 path changed as designed: full-stage overlapping CPU scratch **10,368,000 B/upload** OFF versus striped **1,228,800 B/upload** ON. The maximum *known/requested* scratch from log receipts dropped from **64,800,000 B** to **2,304,000 B**; this is **not** measured freed resident memory or Mali VRAM. GL output size is unchanged.
- For each of the three matched first-present pairs, ON improved `MemAvailable` by **15,572–25,936 KiB**, retained more `SwapFree` and reduced game `VmRSS`/`VmSwap`. But at the **floor** ON `MemAvailable` was lower in **two of three** pairs. Median prelaunch-to-floor `SwapFree` consumption remained **39,880 KiB** ON vs **75,524 KiB** OFF. Early staging helps some moments but has **not solved persistent/headroom pressure**. These snapshots are not simultaneous physical-allocation attribution.
- **Capture gap:** one supplemental owner-verified live 1280×720 KMS frame showed the **NEON DOCTRINE publisher splash**, not the title menu. The ON candidate exited before a scheduled capture; **ON/OFF pixel parity is unverified**. Post-run Spruce home/clock captures are cleanup-only, never game proof.
- **Budget journal gap:** 119 texture-pair lines in every arm, yet live ID **288** is unjoined in candidate-01/baseline-02 and live ID **280** in baseline-03/candidate-03. Only baseline-01 and candidate-02 reconcile. `LC2_LIFE_TEXTURE_PAIR_CAP=128` has **not** been hit in those records; do not blame overflow without reproducing it. This may be emission timing, owner lifecycle, missing branch, or parser join semantics; **root cause is unknown**.
- No build251 first menu, world, controller movement, audible audio, save/cold-load, or valid gameplay FPS measurement exists. Raw number of present records (11–17) is **not FPS**. Existing 30-FPS historical Loading calculations are not a future scene forecast.

**Overall assessment:** the project has unusually good reproducibility and safety instrumentation for an experimental port, and the BC staging experiment exposed a real trade-off. However, a 1 GiB-class system is currently failing its *menu* safety gate, so chasing GPU/CPU micro-optimizations cannot yield playable gameplay yet. Two deliverables must now converge: **qualified, meaningful memory headroom** and **correct owned game pixels**.

## 1. Prioritized work queue and strict gates

| Order | Deliverable | Why now | Pass criterion / stop |
| --- | --- | --- | --- |
| **P0-1 / E4** | Repair *observed* budget ↔ pair join gap (IDs 280/288) | Four of six newest arms currently cannot support complete per-object accounting | Same-run replay joins every live charged owner with no missing event/phase; ambiguous or incomplete remains FAIL |
| **P0-2 / M3-B** | Lightweight **pre-first-present** CPU/GL/Mali/system memory waterfall, with observer OFF control | Scratch improvements fade by floor; permanent peak owner unidentified | Bracket dominant requests, identities, ordering and measured memory; no invented physical owner |
| **P0-3 / V1** | Event-triggered **live** KMS OFF/ON capture proof | Candidate pixel parity absent; timed 8.4-s capture missed the process | Both images tied to living expected PID and distinct current presentation serials; zero unintended GL/pixel difference |
| **P0-4 / E3** | Allocation admission and storage-generation correctness | Prevent historical unguarded GPU pressure; fix observable ledger risks without confusing them with a gain | Typed preallocation stop and fixture-complete subresource/slot accounting |
| **P0-5 / M3-C** | **One measured structural, preferably lossless memory saving** | 96 MiB menu floor fails in every arm despite stripes | Better same-phase **minimum** available/CMA/swap + corrected pixels, meaningful persistent margin; no extra swaps |
| **P0-6 / W0** | Three quiet **120-s true-menu** passes | Only reliable gate to attempting scene load | No floor/OOM/GL error, safe CMA, stable swap and verified owned menu frames |
| **P0-7 / W1** | Correct first world and full playable loop | Separate visual/functionality from speed | Movement, interaction, inventory/dialogue, physical pad, audible sound, backed-up save + cold reload |
| **P1 / F1** | Source-attributed scene-specific 30-FPS work | No present world frames to benchmark today | Three runs/scene; P95 frame interval <=33.33 ms with pixels, audio, input and safe memory |

**Do not execute the old “first run six A/B pairs” step again.** Existing 3 paired results are published; do targeted follow-ups only to close explicit uncertainty. Change one runtime behavior per experiment, keeping `T2_MEMORY_FLOOR_MIB=96`, `T2_TEXTURE_BUDGET_MIB=300`, strict GL and clean principal state. A typed safety stop is a *correct refusal*, not successful loading.

## 2. P0-1 / E4 — find why four build251 arms lack a live `LC2_TEXTURE_PAIR`

**Exact source sites:** `runtime/lamentum-adapter.patch`, `lc2_life_events_texture_pair`, `lc2_life_texture_pair_write`, `lc2_bc_upload_stripes`, texture `initialize` branch, `lc2_bc_reserve_first_use`, `t2_texture_budget_add/sub`. Analysis: `tools/ledger_bases.py:replay_texture_budget`. The constructor currently emits the ordinary `phase=initialize` pair, BC striping may emit `phase=bc-materialize`, and budget charges have their own time sequence. **Do not assume** each active charged texture has an `initialize` event before every floor sample, nor that a missing ID proves an allocation leak.

1. In owner-private **saved raw logs**, for each failed UUID isolate only complete lines with that run-id, then extract all add/sub T2 events for the missing ID, all pair rows, texture initialise/destruction and BC first-use events. Join by **(run UUID, NVN texture ID, object/owner generation, timestamp)**. Compare before/after the nonblocking budget floor sample; record whether the pair is absent from the whole run, emitted after the sample, tied to an alias owner, or replaced by an old phase. Published `ab-summary.json` is not granular enough to determine this alone. Do not make a guessed diagnosis.
2. Add a bounded **`LC2_TEXTURE_OWNER_EVENT`** at each semantic transition: initialize, charge, first-use/materialize, view/alias rebind, update, retire. Include `run-id`, `t-ns`, `nvn-id`, `object-generation`, `storage-owner`, `phase`, `charge-bytes`, `source-write-generation=untracked` where not proven, and `status`. Emit from a fixed-size ring outside the budget/GL mutex if I/O blocking would perturb allocation. Export `lines`, `dropped`, `complete` with a stable receipt schema. No implicit zero for an unseen event.
3. At the budget floor snapshot, report **separately** live charge IDs and the snapshot time. Do not hold the GL mutex while acquiring the budget mutex or scan potentially blocking `/proc` from a locked critical section. Make the replay time-filtered and distinguish `pair_not_yet_emitted`, `missing_owner_path`, `generation_mismatch`, `alias_scope_mismatch`, `log_truncated` and genuine `over_capacity`.
4. Add `tools/test_ledger_bases.py` fixtures for ID 280/288-like missing pairs, pair-after-snapshot, duplicate `bc-materialize`, alias owner, ID reuse with distinct generations, zero charge, independent erase, event truncation, nonmonotonic timestamps and overflow. Tests must **fail closed** on missing data; never loosen `replay_texture_budget` to “ignore unjoined owners”.
5. **Qualification:** host fixture plus one safe owner run with the new observer, and an observer-disabled A/B to check whether tracing affects the first-present window. If the corrected source resolves the four historical artifacts through parser semantics, publish exact proof. If it does not, retain them as rejected; old logs cannot manufacture missing source events.

**Acceptance:** budget replay byte total exactly equals its live snapshot; every active ID has a qualified last pair **before** snapshot or a documented contractually valid no-storage state; storage events reconcile within their declared accounting basis. Unresolved pair coverage must be labeled `incomplete` instead of success.

## 3. P0-2 / M3-B — capture the transient allocation peak and the *persistent* menu deficit

**Implement in:** `runtime/lamentum-adapter.patch` (bounded event stamps near real alloc/decode/GL/storage paths), `tools/proc_metrics.py`, `tools/load_metrics.py`, `tools/device_principal_test.py` and a **new** `tools/peak_memory_waterfall.py` reducer. This is not a repeated broad `smaps` scan.

1. Design `LC2_PEAK_TRACE=1` **default OFF**. An allocation record includes `event_id`, owner NVN/GL identity + generation, thread ID, `t_start_ns/t_end_ns`, `phase`, `kind` (guest/pool, linear BC, decoded RGBA, GL texture, renderbuffer/depth, EGL/present, driver metadata, fileback), `requested_bytes`, `success/retire`, `live_requested_bytes`, `dropped_count`. Capture request/free pairs, not just the latest total. Put cheap monotonic stamps in the allocation hot path; defer text formatting and flush to safe frame/stop boundaries. The ring is capped, with `complete=false` if drops occur. Source hashes are potentially costly: sample owner-local out of band only when safe.
2. Instrument **both full and striped** `zero_texture_refresh` and `lc2_bc_upload_stripes` around linearize, decode and GL upload, including `malloc`/free returns; mark the BC3 owner105, the observed large owner81 (3600×2160, historical bracket), and every actual larger current request. The owner81 historical double Native-descriptor bracket is *not* permission to call it two distinct physical allocations.
3. Bracket `glTexImage2D`, `glTexSubImage2D`, `glRenderbufferStorage` and any large buffer storage with object generation, level/face/layer, layout bytes, return/error semantics, allocated storage vs subimage writes; record whether an allocation is full RGBA despite compressed guest input. Do not call `glFinish` just to make a bracket “atomic” and do not consume GL error state differently in one arm.
4. Within **the exact run/PID/starttime/boot/ELF** collect small, bounded `/proc/<pid>/status` samples (`VmRSS`, `VmHWM`, `VmSwap`, faults) plus `MemAvailable`, `CmaFree`, `SwapFree`, and optional `/proc/vmstat` swap-in/out. Sparse `smaps_rollup` / Mali `mem_allocs` snapshots are separate read-only probes with measured capture latency, known context identity, and their own missing/truncated status. On this device memory PSI has previously been unavailable: record `null`, not 0. Never read `mem_view` (memory contents).
5. Record **phase marks** process attach → GLES init → asset/decode → first draw → first present → publisher splash → menu or floor. First-present deltas are not necessarily the peak; estimate peak using sampled minima **with resolution/uncertainty** and request-lifetime overlap. Account for MainUI exit and other processes as confounders. Do **not** add Mali descriptors to RSS or equate a Mali VA with physically unique pages.
6. First run OFF vs observer-ON **with the same binary and same stripe setting**, with `LC2_PEAK_TRACE` the only variable. Establish instrumentation overhead for first-present time, presentation progress, and resident memory. A tracing overhead over 5%, changed stop class, memory-safety regression, event overflow, or lost ownership makes the profile nonqualifying; reduce scope rather than trusting it.
7. Publish `evidence/m3b-peak-<date>/` with a run-identity manifest, schema, trace event cap/completeness, phase-aligned waterfall, **top 10 overlapping requests**, before/after system snapshots, Mali observation qualifiers and cleanup. Show `unknown/unattributed` residual explicitly.

**Decision rule:** If full-to-stripe eliminates temporary malloc overlap but `VmHWM`/swap/CMA still degrade later, **stop optimizing staging alone**. Select the first *persistent* contributor with a proven lifetime that can be changed safely.

## 4. P0-3 / V1 — rescue live candidate KMS pixel parity without changing the memory policy

The previous ON image was missed because the scheduled capture happened **after PID exit**; don't add another long or fixed-delay trial. Existing helpers: `tools/lamentum_pad_contract.py`, `tools/load_metrics.py` owned byte-framed collector, `tools/frame_diff.py`.

1. Implement an event-triggered, **no-input** `capture_on_owned_present` harness extension: arm capture when a complete **current-run** `NVN_PRESENT_PIXELS frame=N` arrives and the expected PID/starttime is still alive. Attempt one bounded KMS capture as soon as the condition fires, not “at 8.4 s”. Recheck owner identity and a newer/distinct present serial **after** capture. If the process exited or capture tool failed, mark `NOT_CAPTURED`; do not substitute the home overlay.
2. Exercise OFF/ON on the **same hashed build251** with a unique UUID per run, same clean boot conditions, unchanged floor/cap/GL. Pair *the same publisher/Loading stage*, not two different animation times; include exact image dimensions and ROI fingerprints. KMS is **1280×720**; internal 1080p render targets need not imply a 1080p scanout.
3. Compare with `tools/frame_diff.py` using pixel-identity (`tolerance=0`) for fixed deterministic frames, or separately report allowed animation/temporal/quality differences; check alpha, sRGB/colour, mip seam, stripes, GL error and black frames. Explicitly audit **all mip levels** and non-block-aligned BC tiles. A threshold of 2 is approximate, not byte-for-byte proof.
4. Run host fixture cases `1024x64`, `2048x16`, `4096x1`, `1023/1024/4096/4097` width transitions, odd BC block heights and the complete 1920x1080 mip chain. In `lc2_bc_upload_stripes` current `capacity=width*128*bpp` is excessive when `height<128`; test a **separate** follow-up patch using `rows=min(height,128)` and checked `size_t` multiplication. Update `zero_bc_should_stripe` to require positive actual temporary-byte benefit **only after** old candidate parity is classified. Recompile, repin and repeat A/B if the executable changes.

**Pass:** owner-qualified ON and OFF images, no new error, exact/explicit quality evidence, unchanged gameplay-adjacent content. Only then consider opt-in medium stripes as a *limited staging mitigation*. Do not enable by default solely because the first-present memory counters improved.

## 5. P0-4 / E3 — make storage/accounting/admission safe before the next world attempt

**Specific code defects/risks found by inspection (not yet device-proven memory leaks):**

- `lc2_life_events_storage` adds `bytes`/mip count every time it sees an already-live GL name. A second `glTexImage2D` defining the **same subresource** should *replace*, whereas adding a different mip should add. `glTexSubImage2D` changes content, not storage. `glBufferData` redefinition should replace. Introduce per-(share group/context generation, GL name generation, target, face, mip/layer) records, validate checked arithmetic and GL-success before committing budget bytes.
- `LC2_LIFE_EVENT_CAP=512` chooses a free slot only when `!entry.name`, but deleted entries keep their names. Many create/delete cycles can permanently exhaust the table even with a small live set. Keep **live-state slot reuse with independent monotonic generations**, and a separate bounded, honest append-only event ring (overflow >0 ⇒ `complete=false`). Do not erase source-generation provenance when recycling.
- The simple T2 budget cap does not cover all driver/EGL/renderbuffers or temporary CPU allocations. Implement **pre-allocation** admission for one proven large family, using complete checked mip/face/layer/sample sizes and a conservative, *measured* driver uncertainty. Return a typed `T2_STORAGE_ADMISSION` **before** unsafe host malloc/GL, without changing current 96 MiB floor or 300 MiB texture cap. Refuse unknown format/size; never call blocking `smaps` under GL locks. Admission is **safety**, not a headroom saving.

**Host fixture matrix:** 512+ create-delete-recreate cycles, repeated GL name in different share groups, 24 name reuses, overwrite same mip, add another mip, partial update, texture deletion while an alias/view exists, failed GL allocation/rollback, depth/renderbuffer allocation, missing GL context, budget under/overflow, observer log truncation, concurrent emission and context loss. Verify reported retained sum, current live objects and stable generations, including when event capacity is reached. Keep strict negative tests that reject invented physical-memory claims.

**Device gate:** one short owner-qualified, memory-safe diagnostic with `complete=true`, no new GL errors, no OOM, and pristine cleanup. Typed clean stops are acceptable as safety tests but **cannot qualify W0**.

## 6. P0-5 / M3-C — select ONE durable memory-saving mechanism from M3-B

Implementation priority is **ranked by quality/safety and measured bytes**, not a promise that all should be implemented. For every candidate retain an OFF default, an identifiable allocation owner, a one-variable control and a rollback hash.

### C1. Quality-neutral duplicate CPU/upload residency (first if M3-B says it matters)
- Audit `zero_texture_bc_pixels`, `zero_texture_refresh`, `lc2_bc_upload_stripes`, guest pool/snapshot/fileback handling, and `LC2_TEXTURE_PAIR` write metadata. Identify simultaneous retained **compressed guest source, linearized BC copy and RGBA decoded mirror**, and prove which are temporary vs permanently retained.
- Record guest write/dirty generation per owner/view, CPU pool generation and exact source hash at safe points. Only elide a decode/GL upload when write generation, texture generation, mip, sampler, alias and context are unchanged. Current published `source-write-generation=untracked` means naive “same texture ID = same bytes” caching is **unsafe**.
- Prefer a bounded decode-once or row-staging implementation; use GL subimage only with validated storage, stride/alignment and last-reader rules. Prove it lowers **same-phase peaks and sustained swap**, not just malloc requests. Preserve BC3 alpha and full resolution.

### C2. GPU representation/storage pressure (highest potential, highest proof burden)
- Profile actual `glTexImage2D` + Mali `mem_allocs` for live unaliased big atlases. Earlier bracket evidence found owner81's 3600×2160 storage associated with Native descriptors of **31,109,120 + 32,821,248 B** in one read window; this is **not** confirmed unique/final physical memory. The 8192² BC owner295 historically caused an unsafe 256 MiB decoded first-use later in Loading, not in current six menu arms.
- Query the *actual live* Mali-G57 GLES version/extensions; only then evaluate real **ETC2/EAC or ASTC** storage. BC3 blocks are **not** ETC2/ASTC data: transcoding and the resulting alpha/sRGB/mip/filter fidelity must be validated. Reuse cached locally transcoded owner assets only under proven immutable source/write generations; never commit copyrighted textures or guest dumps.
- Quantify GPU driver request/residency (qualified), CPU transcode time, memory headroom and owned KMS pixel quality. Any compression artefact is a **quality change requiring explicit acceptance**. Driver support on other Mali generations is not evidence for this exact firmware/context.

### C3. Scope-limited 1080p composition target storage (not the first “magic 720p” tweak)
- `docs/1080p-origin.md` already locates **hardcoded 1920×1080** guest composition targets distinct from the **1280×720 panel**; `ZERO_RENDER_SCALE=2` was historically performance-neutral/negative. The nominal **maximum** storage reduction for the three colour plus one depth-equivalent target is **17.58 MiB** (31.64 →14.06 MiB), *not* 31.64 MiB physical RAM.
- Revisit only after M3-B identifies a live target's producer/last-reader, GL generation and backbuffer/UV/UI projection correctness. One named family, opt-in; preserve menu hitboxes and shader colour; capture same-scene frames. Reject if added scaling/blits consume the benefit.

### C4. Lifetime retirement/eviction (conditional)
- Use proven NVN owner, GL generation, share group, *last GPU reader fence* and reupload path. A `glDeleteTextures`, recycled GL name, reused Mali VA or decreasing **declared** bytes is **not** proof of a physical refund. The old `LC2_TEXTURE_PAGEOUT` experiment remains OFF and is not a safe universal fix.
- Measure actual refund and reallocation/fault churn. If GPU completion cannot be established, do **not** implement driver-unsafe eviction.

### Ideas to defer or reject for now
- **No:** lowering the 96 MiB floor, inflating swap or texture cap, disabling OOM/GL guards, aggressive `glFlush` replacement for synchronization, speculative 8192² full-RGBA first-use, or running a longer timed menu as “progress.”
- **No blind redo:** `LC2_CBUF_SUBIMAGE` and generic `ZERO_RENDER_SCALE=2` were previously neutral/negative in their tested Loading conditions; re-open only if a new *world* profiler shows an eligible cost.
- **Conditional:** guest CPU/ZRAM cold threshold, governor, thread pinning, SDL present and redundant GL state changes. These might help **after** sustained memory headroom, and do not address current first-menu floor.

**M3-C acceptance:** three paired, identical-phase safety runs show measurable improvement beyond run-to-run variance in **minimum `MemAvailable`, minimum `CmaFree`, `VmHWM`, `VmSwap`, swap consumption and actual menu progress**, with no new errors, equal scene and image content, and no profiler instrumentation penalty. A reduction in source-requested scratch with no durable headroom is *not* enough.

## 7. W0 / W1 — separate playable-game validation from performance claims

**W0 (menu safety):** at least three independent **120-second** idle **game-owned menu** sessions, verified KMS, real `LC2_MENU_EVENT`/page state, advancing distinct presentation serials; floor96 never tripped; no correlated Mali/kernel OOM; safe operator-measured CMA margin and no sustained swap growth; proper launcher/process/CPU restoration. Target **≥160 MiB `MemAvailable`** for headroom design, not as a proven world-load requirement; a device-specific CMA threshold requires measurement. If menu fails, return to M3-C. A publisher splash does **not** pass W0.

**W1 (gameplay):** only after W0, use `tools/owned_navigation.py`, `tools/owned_nav_chain.py` and `tools/newgame_navigate.py` with press **and release** acknowledgment, one action per distinct fresh presented frame and owner-qualified before/after KMS image. Transition title → New Game → config/controls → Loading → live world. For each state report actual ROMFS/texture progress, shader **draws** (not shader-creation count), stop status and frame identity. Reject `TIME_LIMIT_STALLED`, wrong pixels, missing unpinned shader, `TEST` substitute in an essential scene, or memory pressure. Demonstrate physical D-pad/stick 2-direction movement, one interaction, dialogue, inventory/back, audible audio, a development-only saved slot, normal exit and **cold reload of the same progress**. Do three clean independent runs. Never overwrite user saves.

The older `newgame-20` 709 presents and its shader entry45 do **not** satisfy these criteria; older title/menu success is real historical progress but does not override the failed latest safety gate.

## 8. F1 — only then profile gameplay for 30 FPS

30 FPS is **33.333 ms per correctly presented world frame**, not number of presents divided by Loading time. For idle, movement, busy scene (and transitions reported separately), collect three comparable ≥60 s runs each with P50/P95/P99 full-frame interval, dropped/duplicate frames, input-to-photon proxy if qualified, CPU/wall/wait exclusive spans, NVN replay/GL stage cost, driver waits, ZRAM faults/IO, temperature/governor and working set. `tools/perf_sample.py` must use the target `SC_CLK_TCK`; `tools/analyze_perf.py` must reject incomplete identities/stages. Profiler ON/OFF overhead <=5%.

Rank by measured **exclusive** bottleneck: guest Unity/SVC work → texture decode/reuploads/page faults → GL replay/state/CBUF/draw calls → GPU fill/1080p postprocess → scheduling. Historical Loading numbers (~300 ms guest gap / ~250 ms replay) are **not** world benchmarks. Promote one optimization only after ≥3 one-variable paired, image/control/audio-correct gameplay runs show lower **whole-frame P95** without new memory pressure. Accept a scene at 30 FPS only if **P95 <=33.33 ms** while the playable loop stays correct; report P99 separately.

## 9. Minimal test, evidence and rollback contract for every PR

Run host-only verification first (these commands **do not** validate the device or claim 281 new passes):

```sh
python3 -m py_compile tools/ledger_bases.py tools/load_metrics.py tools/proc_metrics.py \
    tools/device_principal_test.py tools/frame_diff.py
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
# In the pinned recovered GPL source: verify 435/435 baseline-manifest hashes,
# apply only runtime/lamentum-adapter.patch and check target AArch64/GLIBC.
# Build and read back deployed ELF hash; compare to prelaunch run identity.
```

For a **qualified** on-device PR: back up owner saves; record current MainUI and game process census; require idle principal and one `boot-id/pid/starttime/run-UUID/ELF-hash`; alternate A/B with **one** flag, resetting cleanly every time; retain exact source and launcher/helper hashes; use bounded 90-s *maximum* owner diagnostics or shorter as safety warrants, not a request to intentionally hit the floor. Collect `MemAvailable/CmaFree/SwapFree/VmRSS/VmHWM/VmSwap` at comparable owner phases, stop code, counted GL errors, KMS while the game process is alive, per-event truncation metadata and complete cleanup. Raw logs, proprietary blobs, memory contents and PNGs remain **local-only**; publish compact hashes, typed summaries and non-sensitive receipts.

**Abort/rollback** on identity mismatch, incomplete event journal, unsafe CMA, `T2_MEMORY_FLOOR` before W0, any kernel/driver OOM, unexpected `GL_INVALID_*`, suspect GPU completion, content mismatch, missing release ACK, lost MainUI, CPU sysfs state/mode drift or affected saves. Restore prior ELF by its readback SHA, launcher/helper pairing, original CPU mask and device principal. A diagnostic arm stopping safely should be reported as **FAIL_W0 / SAFE_STOP**, not “fps optimized.”

### Suggested implementation-sized PR boundaries

| PR | Main modifications | Required artifact |
| --- | --- | --- |
| `fix/owner-pair-coverage` | overlay pair/budget trace + `ledger_bases.py` strict reducer + tests | Missing ID280/288 classification and exact replay |
| `feat/peak-window-waterfall` | opt-in event ring + proc sampler + bounded reducer | Single-run waterfall + OFF control/overhead |
| `test/live-present-capture` | principal owned-present KMS trigger + frame comparator tests | ON/OFF pixel parity or explicit uncapturable reason |
| `fix/storage-subresource-admission` | GL generation/subresource ledger, slot recycling, pre-admission guard | Fixtures, fail-closed behaviour and no new OOM |
| `perf/one-measured-memory-owner` | Exactly one proved memory class | 3 paired qualified on-device runs, same-phase headroom and pixels |
| `feat/w0-menu-and-w1-world-gates` | Frozen flags, owned navigation, transition/scene/save/audio oracles | Real menu/world/playable evidence, never Splash-only |
| `perf/world-frame-p95` | One exclusive measured game hot path | 30 FPS P95 report, full scene quality/thermal/memory |

### Escalation / feasibility checkpoint

After **two evidence-selected structural memory candidates** have each been correctly implemented and qualified (or rejected for clear safety/semantic reasons), reassess whether the Switch ARM64 + GLES adapter can fit the game's **menu + world active set** within the board's physical memory. Publish minimum unavoidable guest+driver+render-target bytes with uncertainty and report alternative backend/asset/quality trade-offs openly. Do not keep extending the menu timeout, silently changing quality or promise stable 30 FPS while W0/W1 remain closed.

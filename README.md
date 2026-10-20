# Lamentum — experimental Switch-to-Linux-ARM64 port (TSPS / SpruceOS)

**Status: NOT PLAYABLE (latest tested build219; review 2026-10-20).** The device reaches the real main menu, New Game configuration, controls page and Loading; the catalogue contains **46 entries (0–45), including seven TEST substitutes**. Fragment45 linked in [newgame-20](evidence/newgame-20/summary.json), but real world rendering, player movement, audible audio, cold save/load and sustained gameplay FPS remain **unverified**.

**Newest load evidence:** [load-probe-03](evidence/load-probe-03/summary.json) reproduced a kernel/Mali OOM around **709 MiB GPU accounting**; the runtime tracked **411 MiB live textures** against its nominal 420 MiB limit. [load-probe-04](evidence/load-probe-04/summary.json) and [load-probe-07](evidence/load-probe-07/summary.json) show that **T2_TEXTURE_BUDGET_MIB=300** converts the later unsafe allocation into a clean **T2_TEXTURE_BUDGET** stop. The immediate trigger is the first-use **8192×8192 RGBA reservation (256 MiB), resource id=295**. This is safer but **still cannot reach gameplay**; other Mali-accounted resource classes remain unresolved. [load-probe-05](evidence/load-probe-05/summary.json) also demonstrated that a 1280 MiB fileback cap could not fit the SD-card reserve.

**Independent Loading CPU problem:** a prior measured 20.14-second window consumed **0.836 s of main-thread CPU per presented Loading frame**, even without new RomFS/texture/BC events. This is **not gameplay FPS**; sample the guest PCs and thread CPU/wait states before shader or compiler optimization claims.

**Newer load evidence (build218–219):** [load-probe-08](evidence/load-probe-08/summary.json) sampled an intensive SVC/IPC path (0x1A/0x1B mutex arbitration; endpoint0x40 commands 7/8). Its round-robin MOMO samples are **not** an aggregate CPU-time percentage; native caller/service identification and timed handlers remain open. [load-probe-09](evidence/load-probe-09/summary.json) verified incremental collector counters. [load-probe-10](evidence/load-probe-10/summary.json) used the installed **build219** executable and measured a 126 MiB charged-texture plateau while VmSwap grew to approximately 870 MiB in an **earlier Loading interval**. The probe ended with operator TERM, **not** a demonstrated texture-budget stop, and does not disprove the later id=295 memory wall. The file's [GPU ledger analysis](docs/gpu-ledger.md) explicitly avoids attributing the remaining resident memory to an unproven heap owner.

**CURRENT NEXT STEPS:** [Performance roadmap §27](docs/performance-roadmap-30fps.md#27-build219-reassessment-code-audited-action-plan-for-first-gameplay-and-fps-2026-10-20) and the **[detailed build219 implementation plan](docs/build219-gameplay-performance-action-plan.md)** supersede earlier current-status priorities. In parallel off-device: fix target CPU accounting and run identity; map real svcArbitrateLock/Unlock cost and endpoint0x40 service identity; measure the live GL memory owners and original id=295 descriptor. Then prototype one owner-local verified immutable ETC2/EAC compressed atlas to avoid the 256 MiB decoded RGBA GPU reservation (real memory savings and image quality must be measured). After safe Loading progression, validate fragment45 four-MRT outputs, world scene activation, physical controls, audible sound and cold save/load, **then** measure gameplay FPS. Keep the proven diagnostic **300 MiB texture-budget** guard and disk reserve; the **32 MiB memory floor is not a release setting**. No runtime patch or on-device validation was performed as part of this documentation audit.

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

# 4. install: port/Lamentum.sh -> /mnt/SDCARD/Roms/PORTS/, runtime + section -> lamentum-switch/
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
tools/baseline-manifest.sha256 435-file baseline identity
docs/                          porting log, architecture and measured evidence notes
evidence/                      device runs: logs, stop codes, captures
```

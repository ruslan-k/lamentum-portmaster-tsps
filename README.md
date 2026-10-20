# Lamentum — experimental Switch-to-Linux-ARM64 port (TSPS / SpruceOS)

**Status: NOT PLAYABLE (build218; updated 2026-10-20).** The physical device reaches the real title/main menu, Options, New Game configuration, controls page and Loading with PID-bound live-KMS receipts and verified agent input (EV_KEY305 Confirm / EV_KEY304 Back). The shader catalogue contains **46 entries, indices 0–45, including seven TEST substitutes**. [newgame-20](evidence/newgame-20/summary.json) confirmed the new capture-pinned half-precision fragment45 **linked** (`sources=0/45`), then the process was killed at presented frame **709** amid Mali GPU OOM notifiers (~725,992 kB driver-reported GPU memory on a device with MemTotal 986,064 kB). This was **not** a `ZERO_SHADER_NOT_PINNED` stop; the scene and first correct gameplay frame remain unverified.

**Two current blockers:** (1) attribute and reduce the Mali GPU memory peak—an existing **420 MiB decoded-texture budget did not prevent this driver OOM**, and the uncovered allocation class is unknown; (2) explain an earlier measured 20.14-second Loading interval with **0.836 seconds of main-thread CPU per presented frame**, despite zero new recorded RomFS reads/textures/BC deferrals. These numbers are **not gameplay FPS**. The port has **no verified player movement, actual audible audio, cold save/reload or 30 FPS**.

**CURRENT IMPLEMENTATION PLAN:** [Gameplay Bring-up and Performance Plan §§13–20](docs/current-gameplay-performance-plan.md#13-build218--newgame-20-reassessment), source reviewed through [b35f21e](https://github.com/ruslan-k/lamentum-portmaster-tsps/commit/b35f21e14662e681e27de9c78cc91ea250f0d4be). Next: harden the new load probe (true run identity, cheap incremental log counters, menu oracle and target-correct CPU metrics); measure native GL/EGL allocation lifetime versus Mali driver accounting; introduce a safe pre-OOM guard; sample the actual guest-CPU hot PCs with the existing bounded sampler; then investigate correct first-world render and controller behavior. [GPU failure analysis](docs/gpu-wall-after-entry45.md) · [CPU and host timeout analysis](docs/time-governor-and-load-cost.md). The **32MiB** diagnostic memory floor is not qualified for release. A new load_probe.py tool exists but has not yet supplied a completed device measurement.

**30 FPS roadmap:** [docs/performance-roadmap-30fps.md §25](docs/performance-roadmap-30fps.md#25-build218-post-oom-audit-and-next-steps-2026-10-20) — latest build218 audit, detailed memory and CPU hypotheses, current PR order, benchmarks and correctness gates; §§0–24 preserve earlier experiments and should not be mistaken for present status. No device run or source runtime build was performed in the current roadmap audit.

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

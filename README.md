# Lamentum — experimental Switch-to-Linux-ARM64 port (TSPS / SpruceOS)

**Status: bring-up. No game frame, no playable launch, not a PortMaster release.**

This repository tracks the attempt to run the owner's Nintendo Switch copy of *Lamentum*
(Unity 2019.4.4f1, IL2CPP, ARM64) natively on a TrimUI Smart Pro S class handheld through a
recovered Horizon/NVN compatibility runtime — the same class of runtime used by
[west-of-loathing-portmaster-tsps](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps).

Nothing from the game is distributed here: no modules, no RomFS, no textures, no shaders, no
keys, no saves. Only our own tooling, the adapter patch and measured evidence are committed.

## Verified facts (2026-10-19)

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
- **Adapter patch scope** (2 files, 8 lines): hoist two texture-lifetime helpers out of the
  `ZERO_ZX_GAME` guard so the generic command recorder can reach them, and declare
  `zero_texture_record_id` for every title profile. Nothing else is changed.
- **Shader translation: absent.** The build uses the baseline's empty catalogue stub, so the
  runtime is expected to stop at its first real `ProgramSetShaders` with a
  `ZERO_SHADER_UNRECOGNIZED`/`ZERO_SHADER_NOT_PINNED` controlled stop. That is a deliberate
  fail-closed answer, not a rendering result.

## Not done yet

- No device run has been performed yet (see `docs/porting-log.md` for the run list as it fills).
- NVN structure layouts for this SDK generation (texture-view width, sampler builder, window
  and command builder offsets) are **not** derived yet; the build currently carries the
  baseline's modern (`MOMO_SHADERS=1`) profile, which is an assumption to verify, not a fact.
- Shader catalogue, audio, input mapping, saves and performance are all unmeasured.

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

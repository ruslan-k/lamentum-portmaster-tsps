# Current post-H2a host ELF build — 2026-10-23

This is the first full native ELF built from the refreshed post-H2a source snapshot. It is a **host build only**: not transferred, installed, or launched on Longan. It supersedes neither the historical build262 artifact nor the installed build259 runtime.

## Inputs pinned and verified

- Recovered baseline: local-only `runtime-src`; `tools/baseline-manifest.sha256` SHA-256 `f8d9ebbb0051faa2a141248031061e20934121ed07953e512b06393cd133300b`; all **435/435** files verified. The baseline checkout has no commit (`No commits yet on master`), so the manifest—not a Git HEAD—pins these files. `git apply --check runtime/lamentum-adapter.patch` passed.
- Owner image: local-only `image-09`, **18 files / 1,898,916,986 bytes**, inventory SHA-256 `a4e734d4f3b90f4c87b676c2247f699c5739786d29a66270cdfb0c87fe09e335` (sorted file name, NUL, size, NUL, file SHA-256, newline). The separate `lamentum-romfs.section` is **1,832,060,032 bytes**, SHA-256 `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`; `module-identities.json` SHA-256 `423833e6a91c9037ec9ddbf40c441377456a42432f34c064c0bee16f7d4c8efa`. No owner data is included in this repository.
- Cross-build container: `pmjs-arm64-spruce-local:20261002-gcc10`, image ID `sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c` (amd64/linux); cross compiler via `tools/cc-lamentum.sh`.
- Patched source inventory: **390 files**, SHA-256 `3fcc9e78155ecdfd71507e860c5120d313a6a2d81967eed2ece572215cf38689`; **77** candidates, **12 wrapped+unmeasured / 65 unknown**. The build-time policy gate passed.

## Output

- ELF64 AArch64 PIE, **2,203,096 bytes**.
- Build ID `5b1b3412da7b43442a0ebf097e904cb8cbef0c8e`.
- SHA-256 `c46714403f22074d92710192d1164cfe0b7a4f62f1a4890ffb7a1e224c542332`.
- Maximum required GLIBC: `2.27` (Longan firmware reports glibc `2.33`).
- Paired `run_identity.py` SHA-256 `abe8e4847b18a750c0796af33d887cf43714126c9751ccdc8236715cb752401a`.
- The build's shader-diagnostic sanitizer reported `count=4`; the final native-build and copied candidate hashes matched. Compiler output contained only the `unused-result` / `unused-function` warning classes explicitly downgraded by the wrapper; the build completed without errors.
- Local scratch artifact; not in Git or on the device.

This differs from the historical build262 ELF (`dd13d4ab…`) because that artifact was built from the earlier source-tree hash `1b995ea…`; this candidate is built from the refreshed `3fcc9e…` tree. Do not report the hashes as the same build.

## Verification and disposition

- Baseline manifest **435/435**; adapter patch apply-check passed; build-time 77-site inventory passed.
- `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'`: **405 tests passed**, suite `OK`.
- `readelf` confirmed ELF64, AArch64, PIE, Build ID and GLIBC requirements; final SHA-256 was recomputed.
- No device files/settings changed; no game launched; build259 remains installed. The candidate is **HOST_BUILT_NOT_INSTALLED**. `T2_STORAGE_MARGIN_MIB` remains unset and D remains **HOLD_RUNTIME** pending actual request-to-allocator routing, peak/uncertainty accounting, safe staging checks and a reviewed one-run reserve.

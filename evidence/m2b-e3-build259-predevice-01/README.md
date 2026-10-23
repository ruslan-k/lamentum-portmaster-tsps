# M2B-E3 build259 host/pre-device checkpoint

**Scope:** next gate after roadmap §83 / companion roadmap order 3. This checkpoint validates implementation and target compilation only; it is not a device run or memory/FPS result.

## Changes in the build259 candidate

- Added generation/subresource-aware storage accounting and buffer-store replacement coverage to the adapter/host replay tests.
- Added checked GL storage-size resolution for known GLES upload triples. Unknown formats fail closed.
- Routed every statically found direct storage call through pre-call admission: 36 `glTexImage2D`, 2 `glRenderbufferStorage`, and 5 `glBufferData` callsites across 15 headers. The wrapper is included before those headers; the pre-wrapper include set has zero direct storage calls. No direct `glTexStorage*`, `glTexImage3D`, compressed-image, or copy-image storage calls were found by the source scan.
- Added scratch checks to the BC reserve/full/striped paths and the CPU-view, cube, packaged-upload, and stable-VBO paths.
- Corrected the CMA requirement to include GL request + overlapping scratch + explicit margin. The RED fixture demonstrated the prior bug: an 8 MiB GL request + 2 MiB scratch + 4 MiB margin incorrectly required only 12 MiB CMA; it now requires 14 MiB. The normal MemAvailable requirement remains floor + GL + scratch + margin.
- No default is supplied for `T2_STORAGE_MARGIN_MIB`; missing/invalid policy refuses storage before the GL call.

## Verified

- Full host suite: **302 tests passed**.
- Focused coverage: **14 storage layout/admission tests** plus **1 extracted T2 `/proc`/margin wrapper test**; the latter exercised unset/invalid margins, missing CMA, available-memory and CMA refusals, and overflow.
- Pinned source baseline: **435/435 hashes OK**.
- Adapter source `git diff --check` passed; generated overlay is byte-for-byte equal to the adapter source diff. Overlay SHA-256: `4a1837eff2b1d3d3619262ee8250e0fc12e504ca9c6357abc561ecb66cdcf5fc`.
- Cross-build in pinned image `sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c` succeeded. `build-259/lamentum-nextos`: ELF64/AArch64 PIE, 2,198,560 bytes, SHA-256 `d72e2f69afa16dd5b846950f3fba80bc9926edcab9b2d45c57ed23faa14b9066`; maximum GLIBC requirement 2.27. The ELF contains `T2_STORAGE_ADMISSION`, `T2_STORAGE_ADMISSION_SUMMARY`, and `T2_STORAGE_MARGIN_MIB` markers.

## Not verified / blocked

- Build259 is not installed or device-tested. A fresh read-only preflight confirmed TSPS boot `66203f22-4ac8-4a2a-a47c-cddc253d3bda`, current build256b SHA `27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`, MainUI PID/starttime `31619/2258075`, no game process and no `/tmp/cmd_to_run.sh`. Snapshot: `MemAvailable=687,036 KiB`, `CmaFree=102,644 KiB`, `SwapFree=2,032,836 KiB`; CPUs 0–3 remain offline/mode 0444.
- `T2_STORAGE_MARGIN_MIB` remains intentionally unset. The build is expected to stop at its first GL-storage admission unless an explicit margin is provided. No device-derived working CMA margin exists yet; do not guess one or enter New Game.
- No menu pass, no-swap result, gameplay, physical input/audio, or ≥30 FPS measurement exists. Physical Mali residency remains unknown.
- Kernel-source triage: the target reports Linux `5.15.147`, build `#42` dated 2025-12-18, model `sun55iw3`; `/proc/config.gz` enables `CONFIG_DMABUF_HEAPS_SYSTEM`, `CONFIG_CMA`, and `CONFIG_DMA_CMA`. Public [REG-Linux/linux-t527 commit `9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed`](https://github.com/REG-Linux/linux-t527/tree/9ed9cb975e8ee303c6b0d4e40a57a81f8110f8ed) has a 5.15.147 `Makefile` and `drivers/dma-buf/heaps/system_heap.c` SHA-256 `d30d4e390dc33549633d0dbc3fda40afb64b03db6995fb3b921107ff13692eca`. Its `alloc_largest_available()` tries orders 8, 4, 0 and continues after a failed `alloc_pages()`; in that source, an order-4 warning alone does not show whether a smaller retry succeeded, and later metadata allocations can also fail. This is a matching-version T527 source analogue, **not verified as the exact Dec-2025 device vendor tree**. Therefore the observed order-4 warning may be an intermediate retry; overall request success and owner remain unknown.
- Compiler emitted nonfatal warnings for ignored `write()` results and unused optional helpers; the build returned success.

**Next gate:** approve or derive an explicit device-specific `T2_STORAGE_MARGIN_MIB` from the fresh preflight (`CmaFree=102,644 KiB`) and the prior order-4 allocation failure. Once that safety value is explicit, install build259 with backup/hash verification and run a bounded principal-flow admission test. Stop on floor/refusal; no New Game.

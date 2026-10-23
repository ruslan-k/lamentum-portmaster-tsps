# M4-A — checked BC stripe sizing and native fixture (host-only)

**Date:** 2026-10-23. **Reviewed main base:** `1604ed90bc39f4834bfa23de71401bc9f94661fe`. This closes M4-A's host-correctness work only; it does not qualify a device or memory saving.

## Change

The adapter now uses checked `zero_bc_stripe_geometry()` and `zero_bc_full_geometry()` plans for scratch sizes. `zero_bc_select_stripe()` keeps the existing wide-atlas path, but selects medium stripes only when their requested peak is strictly smaller than the full-decode peak. `LC2_BC_STRIPE_MEDIUM` remains default-off.

Both `lc2_bc_reserve_first_use()` and `lc2_bc_upload_stripes()` use the same geometry rules. The upload path checks each actual stripe's pixel and linear-block capacities before decoding, passes only the current stripe byte count to `zero_texture_bc_pixels()`, and keeps `glTexSubImage2D()` height equal to the actual rows. Geometry validation rejects invalid dimensions, bpp/block sizes, row limits, and checked `size_t`/`uint64_t` overflow before admission or allocation.

For BC3/RGBA8 `4097×9`, modeled requested scratch is **196,692 B** instead of **2,146,864 B**. For `1920×1080`, it remains **1,228,800 B**. These are requested CPU scratch bytes—not RSS, CMA, or Mali residency measurements.

## Verification

- Recovered source baseline: **435/435** manifest entries pass. The adapter patch applies to pristine source commit `c8d01ca1fed5adab1ae7ad920605f199bb83a72e`; patch and local overlay diff are byte-identical.
- Native BC required profile: **1 run, 0 skipped**. ASan/UBSan profile: **1 run, 0 skipped**, using pinned container `pmjs-arm64-spruce-local@sha256:e437308c01ce7af4a035c3f0652bc886e258889f66803f805bce53d05af75f0c`. Direct host sanitizer linking was unavailable because the host lacks the GCC ASan/UBSan runtime packages; the pinned container run passed.
- Native fixture counts: **86** full-vs-stripe byte-parity cases; **86** compressed-source-preservation checks; **258** guarded buffers; **244** stripe upload regions checked for contiguous, exactly-once row coverage; **28** metadata mip checks for the 8192×8192 BC1/BC3 chains; **18** in-place decode cases; **15** rejected-input cases; **5** stripe-selection cases.
- Coverage includes BC1/BC3 at the required odd, boundary, 1080p and large-atlas sizes; all accepted formats in the `zero_bc_bytes()` range at small/odd sizes; every 1920×1080 BC1/BC3 mip decoded; every 8192×8192 BC1/BC3 mip checked metadata-only to avoid huge allocations. The reservation fixture passes `147,492 B` GL and `196,692 B` scratch for `4097×9`; it also asserts the preflight peak matches the upload planner.
- Full tools suite: **359 passed, 0 skipped, 0 failures, 0 errors**. Focused GL-storage module: **14 passed**. Python compilation and `git diff --check` pass.
- Historical local target receipts recorded `device-limit=16383` (`bc-layout-01/latest.log`, line 8424; current-copy SHA-256 `5555ceba36f419d01b8e2a78bfd8575520881beacb5281e6d8696b5ed4bf05a0`; `sdl-refresh-01/latest.log`, line 8346; SHA-256 `033d688fa276c232f609cb168579a0ebc36d1a7dab68b648d691c78786b6220d`). Thus the host `4097×9` case is below the historically observed limit. Raw logs remain local.
- Pinned AArch64 cross-build passed using the `20261002-gcc10` container (image digest above) and `image-09` owner input. Candidate `build-261/lamentum-nextos`: ELF64 AArch64 PIE, **2,206,776 B**, Build ID `43aa590ec1209841671e9ad0d8de726d9f5f90a2`, max GLIBC **2.27**, SHA-256 `0958651d1e9cb1333023c9a9418be781b6cf2b49d628dc5b9a8c122a80c96332`. Only the known baseline `write()`-result and unused-optional-function warnings appeared. The candidate is local-only and uninstalled.
- `image-09` input identity: RomFS section **1,832,060,032 B**, SHA-256 `80ad4427164a0b7ad61c3a3fcd955bd158635aac1ee42ebb67d01dfae279b893`, matching `image_table.h`; the table and `module-identities.json` hashes are in `summary.json`.

Tool/source hashes are recorded in [`summary.json`](summary.json).

## Not verified / gate

No device actions, install, game launch, New Game, live GL call, KMS capture, gameplay, RSS/CMA reclamation, or FPS measurement occurred. The last read-only target `CmaFree` remains **15,456 KiB**; the device gate is **NO-GO**. M4-A corrects the requested scratch accounting only; it does not prove physical memory recovered. Next host-only step: M4-B allocation-lifetime coverage.
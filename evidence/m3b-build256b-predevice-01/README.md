# Build256b pre-device checkpoint: broaden M3-B coverage

## Source-derived owner census

Parsed the owned build254 OFF floor `LC2_TEXTURE_LIVE_PAIR` records (run `f9868a42-8ccb-4ebc-9df7-72156ab0a151`): 95 owners, with 30 BC owners declaring 188,899,072 B of GL texture payload, 63 non-BC texture owners declaring 52,586,032 B, and 2 depth renderbuffers declaring 11,980,800 B. Combined declared payload is 253,465,904 B versus 117,441,536 B T2 guest/charge accounting. These are logical/declared totals, not physical Mali residency.

Largest non-BC textures include owners 2/3/4 (each 1920×1080, format 0x25, 8,294,400 B), owner60 (955×2048, 7,823,360 B), owner82 (1032×1122, 4,631,616 B), and owners172/206 (1280×720, 3,686,400 B each). The live summary had `buf-bytes=0`, `buf-live=0`, `respecs=0`; the device log identifies an 8×8 EGL pbuffer. Driver allocation and physical residency remain unknown.

## Candidate instrumentation and offline gates

Build256b adds opt-in M3-B windows around ≥1 MiB non-BC NVN texture initialize/refresh staging and depth-renderbuffer storage, in addition to the BC windows. `LC2_M3B_TIMELINE` remains default-off. The quality-neutral in-place BC decoder is included only behind `LC2_BC_INPLACE_DECODE=1`; the launcher does not set it. Host fixtures byte-compare in-place output for all BC formats, partial/odd dimensions, and the 3600×2160 / 3600×3600 owners; the device path has not been enabled or validated.

- Host suite: 294 tests passed; life-event, BC-layout, and floor-snapshot fixtures passed.
- Recovered baseline manifest: 435/435 verified.
- Overlay SHA-256: `ea6a4d103f3893ad0420973dcf3077ec84ccd806053b4b017ede1a7fc1ad657c`.
- Build256b: AArch64 ELF64, 2,189,968 B, SHA-256 `27a2f9a8fcb00761ac6673937145929e675a75c641afde221dc01f96df39d771`, GLIBC ≤2.27.

## Pending physical gate

Build254 remains installed; build256b has not been installed. Next: preserve/read back the current runtime and install build256b, then run a same-build M3-B ring OFF/ON pair, changing only `LC2_M3B_TIMELINE`; keep `LC2_BC_INPLACE_DECODE` unset, `LC2_BC_STRIPE_MEDIUM` unset, floor96/cap300/strict GL unchanged, and stop at the floor. Do not enter New Game. This is instrumentation validation, not a memory win or FPS result.

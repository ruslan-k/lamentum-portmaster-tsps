# Loading investigation, builds 170–174

Status: NOT PLAYABLE. This follows `loading-memory.md`. No game menu, gameplay,
physical input response, audible-audio verification or save/reload acceptance.
Eight TEST shader substitutes remain. No resolution reduction or game-image edit.

## Native fault identified as FMOD software-output code

Resolve disassembly string references using the original NSO segment addresses,
not a guessed rodata displacement. The source reference at module offset
`0x249c3e2` resolves to `C:/buildslave/fmod/build/src/fmod_output_software.cpp`.
`main+0x117fa34` forwards into that component's allocator. At `main+0x117de94`,
a NULL allocation branches into cleanup through a virtual method; that return
address is the observed `main+0x117deb4`. Cleanup eventually dereferences a NULL
parent field at `+0x188`, producing the earlier fault at `main+0x1177010`.
No instruction of the game was patched or skipped.

A strong quota-exhaustion correlation is now measured:

- 1536 MiB declared guest quota: alias-mapped peak 1597132800 bytes, then the fault.
- 2048 MiB declared guest quota: alias-mapped peak 2134003712 bytes, same fault.
- The difference is exactly 536870912 bytes, the quota change.

The two configurations also differ in memory optimizations, so this is not a
fully matched causal proof. It supports allocation failure, rather than a shader
fault, as the trigger. The latest 3072 MiB probes instead stop on physical-memory
pressure. This does NOT mean the full game works with a higher virtual quota.

`LC2_GUEST_QUOTA_MIB` now permits a bounded diagnostic 1536–3072 MiB quota. The
absent-value default is unchanged at 1536 MiB. The host virtual-AS limit remains
8192 MiB; the alias arena remains 4 GiB. The physical MemAvailable floor and
420 MiB GPU budget are independent and unchanged. A pure C test verifies default,
bounds, malformed inputs and unchanged output on rejection.

## Small BC textures also defer GL storage

`LC2_BC_LAZY_ALL=1`, together with `LC2_BC_LAZY_UPLOAD=1`, extends lazy storage
from large atlases to all eligible 2D, single-level BC textures. CPU storage and
original dimensions remain intact. This is opt-in, not a launcher default.

First-use allocation is now positively exercised on-device:

| Texture ID | Original size | GPU reservation bytes |
|---|---|---:|
| 102 | 1000×1000 | 4000000 |
| 107 | 512×512 | 1048576 |
| 97 | 768×768 | 2359296 |
| 61 | 800×1500 | 4800000 |

Each has both `LC2_BC_GPU_RESERVE` and `LC2_BC_MATERIALIZED` receipts. Their
reservations total 12207872 bytes. This closes the previous missing positive
first-use test; it is not proof of shader correctness or a correct scene.

## Snapshot I/O must pin compression-protected padding

Build 171 advanced further but stopped at `LC2_FILEBACK_FAILED`, errno 14
(EFAULT). A kernel `pwrite` cannot raise the guest SIGSEGV restoration path when
its source includes a compression-protected page. Texture padding can remain
protected even after useful texel bytes have been copied.

Build 172 pins/restores the entire snapshot range through its I/O lifetime,
including publication, then unpins it. The lock order does not acquire the
compression mutex while holding the generic snapshot helper's internals.
The original failure errno is preserved across unpinning. The host C test
reproduces EFAULT on PROT_NONE source memory and succeeds after restoration;
subsequent device runs pass the former refusal point.

## Avoid a redundant BC staging allocation

Build 173 reads directly from a disjoint source for native BC block-layout copies.
Overlapping source/destination ranges retain the old full staging copy; non-BC
writes are unchanged. The BC encode function reads, rather than mutates, its
linear input in this direction. The host test compares staged/direct native bytes
and unchanged source bytes in addition to block-address and stripe checks.
Device logs show avoided single transient allocations up to 67108864 bytes.
This is a transient-allocation reduction, not net residency or an FPS claim.

## Two bounded lossless backing files, no deletion of user content

The SD has roughly 1.5 GiB free, and UDISK roughly 734 MiB free. A single SD file
reached its 1280 MiB cap. Build 174 supports optional
`LC2_BC_FILE_BACKING_EXTRA=/mnt/UDISK`, with a separate 384 MiB cap, after the
primary file fills. Each directory retains its independent 128 MiB free-disk
reserve. Both files are immediately unlinked and have independent immutable
published offsets. Unlink failure is now explicitly rejected.

No save, game, backup, other port or partition was removed. Both temporary
payloads disappear after their mappings/process close. The helper's C test
also verifies independent files/cursors and COW independence.

The live smaps sample in `guest-quota-2048-profile-01` contains 54 backing VMAs,
covering 400269312 bytes, with 0 KiB RSS and 0 KiB Anonymous. This proves those
particular CPU mirrors no longer consumed resident pages at the sample time.
It does not equate cumulative file bytes with net system-RAM savings. The same
sample contains 276228 KiB guest-alias anonymous memory and 209032 KiB anonymous
memory outside the alias arena; remaining pressure is not all texture mirrors.
The baseline already periodically calls `malloc_trim(0)` every 2000 ms.

## Run comparison

All counts below are parsed from exact `NVN_TEXTURE_REAL` lines. They are texture
initializations, not distinct shipped assets, percentage complete, frames, or FPS.
The title may initialize internal/duplicate textures, so do not compare the count
as a percentage of the 511 Texture2D entries in the offline asset audit.

| Evidence | Build | Initialized textures | Result |
|---|---:|---:|---|
| `fileback-sd-01` (previous) | 169 | 284 | FMOD NULL-base fault |
| `guest-quota-3072-01` | 170 | — | Physical memory floor |
| `guest-quota-3072-block16-01` | 170 | — | Physical memory floor |
| `reclaim-watermark-01` | 170 | — | Earlier physical-memory-floor refusal; rejected experiment |
| `guest-quota-2048-profile-01` | 170 | — | Physical memory floor; smaps captured |
| `bc-all-deferred-01` | 171 | — | Snapshot EFAULT |
| `bc-fileback-pin-01` | 172 | 419 | Same FMOD fault at larger virtual quota |
| `bc-all-quota3072-01` | 172 | 448 | Physical memory floor |
| `bc-direct-write-01` | 173 | 479 | Physical memory floor, first backing cap reached |
| `bc-two-backings-01` | 174 | 494 | Physical memory floor |
| `bc-two-backings-block4-01` | 174 | 473 | Physical memory floor; worse progression |
| `bc-two-backings-cold50-01` | 174 | 522 | Physical memory floor at 61 MiB |
| `bc-two-backings-cold10-01` | 174 | 486 | Physical memory floor; higher compression savings but worse progression |

Best observed loading progression is the 16 KiB-block, 50 ms cold-time probe.
It wrote 1517314048 cumulative backing bytes, and its last compression receipt
reports 261.6 MiB saved. These are different counters; they must not be added
or presented as net RAM savings. Its presentation counter ceiling is 246,
not a rendered-frame-correctness or performance measurement.

The watermark experiment changed only `vm.watermark_scale_factor` from 10 to
1000, preserving min_free_kbytes=3967 and swappiness=60. It stopped much earlier;
`restore.txt` independently verifies restoration to 10. It is not a proposed
system configuration. No persistent sysctl change was installed.

Physical captures at 90 and 240 seconds in the cold50 probe are white screens,
not a game menu. The 240-second capture in the earlier two-backing probe is
already Spruce's menu after the game exited; its `live-` filename is not evidence
of an in-game capture. Do not claim scene rendering from either.

## Reproduce the best bounded probe

Use the repository's principal-flow harness, not a direct shell launch:

```sh
python3 tools/device_principal_test.py --budget 420 --wait 480 \
  --env LC2_GUEST_QUOTA_MIB=3072 \
  --env LC2_BC_LAZY_UPLOAD=1 --env LC2_BC_LAZY_ALL=1 \
  --env LC2_BC_FILE_BACKING=/mnt/SDCARD \
  --env LC2_BC_FILE_BACKING_EXTRA=/mnt/UDISK \
  --env LC2_BC_FILE_CAP_MIB=1280 \
  --env LC2_ROMFS_BACKPRESSURE_MIB=192 \
  --env T2_MEMORY_FLOOR_MIB=64 --env T2_GUEST_ZRAM=1 \
  --env T2_GZRAM_BLOCK_KIB=16 --env T2_GZRAM_TARGET_MIB=512 \
  --env T2_GZRAM_COLD_MS=50 --env T2_GZRAM_PERIOD_MS=20 \
  --env T2_GZRAM_BUDGET_MIB=32 --evidence evidence/<new-run-name>
```

Build 174 SHA-256:
`a12634e98841fa178eba704f56a0cd31373a6d08d2de1dfc99f070117ae567bd`

The latest diagnostic binary is retained, with its prior binary backed up.
Launcher defaults still do not enable these memory experiments. The eight Python
regressions and the BC, file-backing and virtual-quota C checks pass. Builds
170–174 use the manifest-checked recovered baseline plus the adapter overlay.

Remaining acceptance: get past physical loading pressure, replace the remaining
TEST shaders with validated translations, verify an actual game menu and sustained
scene, then physical input, audible audio, saves/reload and clean exit. Existing
AudioOut logs do contain nonzero PCM samples; that is not an audible-audio test.

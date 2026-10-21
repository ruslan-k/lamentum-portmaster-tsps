# Swap mapping observations — ownership and causality remain unresolved

This note replaces the overconfident original interpretation. Read
[the C0 correction audit](c0-profiler-audit.md) and the current roadmap §29.

## What was actually observed

The historical swap-01 payload summed per-VMA Swap to **784692 kB** while a separately read
smaps_rollup Swap was **784704 kB**, a **12 kB** difference. These reads were not atomic.
The original payload did NOT read status VmSwap; that field was added afterwards. The small
rollup gap supports consistency for that snapshot, not a complete semantic ownership ledger.

The saved top VMA was `366580000-38e216000 rw-p 00000000 00:00 0`, Size 651864 kB,
Swap 432284 kB. Another two reported VMAs had Swap 65644 and 55216 kB. These are VMA ranges,
not texture, allocator or GL object identifiers. Boundary changes may reflect mapping merges
and splits, not one downward-growing arena. Their semantic owners are not established.

A recomputation by *pathname presence* gives 2688 kB in file-named VMAs and the remaining
782004 kB in VMAs without a pathname. That is a mapping classification, not a classification
of game assets, decoded textures, staging allocations or GPU/driver owners. In particular:

- Anonymous host memory can contain texture data/staging and driver allocations.
- Private COW pages in a file-backed mapping can also be anonymous; pathname classification
  is not a full anonymous/file residency classification.
- Process VmSwap/Swap does not measure Mali physical storage and cannot rule out the later
  first-use id295 +256 MiB GPU reservation.

Therefore **"99.66% anonymous proves textures cannot help / Mali is not the bottleneck" is
withdrawn**. The dedicated G0 GL owner/lifetime ledger is still required.

## Swap destinations and the negative priority arm

An observed /proc/swaps snapshot listed the file path `/mnt/sdcard/mmcblk1p1/cachefile` at
priority 40, `/mnt/UDISK/swapfile` at -2, and `/dev/zram0` at -3. These are paths and priorities,
not proof of distinct physical SD/eMMC devices, nor proof that all pages of one process went
to a particular swap device. Per-device usage and actual physical media must be measured.

The priority-100 experiment `swap-priority-01` ended with a kernel-victim-confirmed OOM
(harness **8**, 115 presentation records); the original priority was restored. The result is
negative and must be preserved. It was not an equivalent, semantically matched Loading/world
comparison, so it does NOT prove the proposed mechanism, that file-first is necessary, that
RAM-first is universally unusable, or that zram fallback waits until the entire tier is full.
No such memory-policy experiment was repeated in the correction session.

## Timing and phase limits

The old growth estimates used sampling intervals rather than a fully bound run/phase timeline.
They are not accepted asset-load rates or gameplay benchmarks. swap-01 stopped at
PHYSICAL_MEMORY_CONFLICT with 162 presentation records. Other fault/CPU measurements came
from other runs. Page faults and D-state observations show pressure/waiting, not an exclusive
CPU/GPU owner or a verified explanation of the frame time. No scene/player activation was
proven. Preserve the raw evidence and use the §29 G0/T1/C0 gates before choosing a fix.

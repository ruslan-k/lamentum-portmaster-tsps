# M1: observed GL storage generations in the menu (build244)

Reviewed e93d818 / owner §48.5. This packet integrates the observation-only
ledger from §65 into real storage call sites. It is a measurement, not a policy.

## What is instrumented, and what is not

New native/lc2_life_events.h, default off (`LC2_LIFE_EVENTS=1` enables), bounded
512 entries, report emitted once from the existing runtime stop path with write()
only. Hooks: glTexImage2D for host-half and per-level texture upload in
nvn_textures.h, zero_texture_storage join/release (alias view counts) and the
storage delete in TextureFinalize. Nothing else changes: no admission, budget,
floor, format, size, lifetime or deletion decision, and the off path adds one
getenv() at storage creation only.

Not instrumented, therefore not claimed: renderbuffers/PBO/FBO/EGL surfaces,
specialized or CPU-view upload paths, GL textures created outside these two
call sites, GPU fence completion and driver residency. `share-group=unverified`
is printed in every record: equal GL names in different contexts would be
conflated, so this cannot be used to decide deletion.

## Defect found and fixed before measuring

The stop-path decimal formatter emitted an extra trailing digit for every
non-zero counter (1140 printed as `11400`), which would have inflated every
published number by 10x. The first arm (build243) is therefore discarded as a
tool defect, not reported as a measurement. A regression now compares the
formatter byte-for-byte with snprintf for all ten fields.

## Measured arm life-events-02 (build244)

Owned run: ELF f35b935224ae13df643c14fe2f95df01a2fada5a0bb3c644730b4549e5130574,
PID19297, principal flow, floor96/cap300/strict GL, no input injection.
Summary at the runtime stop:

    storage-calls=162 extends=50 deletes=24 delete-with-views=0
    name-reuse=24 retained=232834352 peak=232834352 live=88
    alias-views=0 overflow=0

- 162 glTexImage2D calls; 50 of them extend an existing image (mip levels), so
  **112 distinct images were created and 24 were deleted**, leaving **88 live**
  images at stop.
- **24 of 24 deleted GL names were reused by a later image** (21 % of created
  images). This is measured evidence that name-keyed storage accounting and any
  name-keyed "delete old storage" are unsound in this title, and it is exactly
  what the object/storage generation split in §65 exists for.
- `delete-with-views=0`: the single instrumented delete site runs only after
  zero_texture_storage_release proved zero views. This is a guard receipt, not
  independent proof of global safety.
- `alias-views=0`: no ZERO 1280x720 alias joins occurred before the stop, so the
  alias path is unexercised on this arm.
- Declared payload of the 88 live images: **232834352 B = 222.05 MiB**. This is
  the sum of requested per-level storage, NOT driver residency and NOT a
  reclaimable figure.

The same run's menu ledger reported `textures-live=93` and
`textures-charged-bytes` about 110 MiB at its last interval. The two numbers
count different things (ledger budget charge vs every glTexImage2D request) and
are **not reconciled**; neither is physical Mali usage. No saving, headroom or
FPS claim follows.

Off arm life-events-off-01, same build, same settings without the env: zero
summary lines, same `T2_MEMORY_FLOOR` stop, cleanup empty. Default-off
behaviour is therefore observed, not only asserted by tests.

## Device result and cleanup

Both arms: runtime STOP `T2_MEMORY_FLOOR` (no OOM receipt), harness cleanup
`[]`. Final independent snapshot: game0, MainUI1, principal1, runtime1, CPU4-7,
no pending launch, debugfs unmounted; DRM capture shows the Spruce home.

Host: 266 tests PASS in a clean index export; C fixture (compiled from the
public patch) covers disabled-by-value, mip extension, alias deltas, name reuse,
delete-with-views and capacity overflow. Build244: 435/435 baseline checks.
Atomic staged deployment with independent hash read-back; build243 kept as
`.before-244`.

## Next

The reuse rate makes generation identity mandatory before any accounting-driven
deletion, and the next arm must instrument renderbuffers/PBO/EGL plus a real GPU
completion receipt, then reconcile declared payload against the ledger and
`gpu_memory` in one run. Menu headroom, world and 30 FPS remain OPEN.

# Loading-memory investigation: builds 156–169

Historical checkpoint; continuation and current frontier: [builds 170–174](loading-memory-170-174.md).

Status: experimental, not playable. No main menu, control response, audible audio,
save/reload or gameplay acceptance has been demonstrated. Eight TEST shader
substitutes remain. Original game image and texture resolution are unchanged.

## Earlier work carried forward

- Launcher: explicit GLES3, synchronous queue, SDL swaps, strict GL checks,
  pageout disabled, 96 MiB memory floor, bounded 120-second default. Avoiding
  `exec` lets the EXIT trap restore the previous CPU-online state.
- Three fragment substitutes were replaced by compiler translations in ESSL 3.10.
  The generator no longer substitutes a fragment merely because it contains `uint`.
- A stride-zero float/UNORM vertex attribute is constant, not a zero-length array.
- Large BC atlases use bounded stripe decoding at their original resolution.
- Optional BC lazy upload retains the guest pool and materializes at first use.
- Optional guest compression saves anonymous pages; the RomFS output pin protects
  a read destination against the compressor between host I/O and the reply.
  The earlier build-162 Obscure Tales splash is not a gameplay claim.

## File backing: measured publication timing error

`LC2_BC_FILE_BACKING=<existing-directory>` uses an immediately unlinked temporary
file. The helper copies complete pages in at most 1 MiB pieces, flushes them,
checks a separate private mapping against the source with `memcmp`, then installs
an equal-byte private mapping. Subsequent writes are COW; the snapshot file is
never modified at an already published offset. Incomplete leading/trailing pages
are untouched. All mappings are inside the guest alias arena, never host malloc.
A capacity limit and 128 MiB free-disk reserve are enforced. The file disappears
when the process closes it; game files and partitions are not replaced.

The first version published at texture initialization. This was too early:
`fileback-profile-01/smaps.txt` has 17 snapshot mappings with 115936 KiB RSS,
all 115936 KiB Anonymous/Private_Dirty and 0 KiB Private_Clean. The game wrote
the texture after initialization, undoing the intended reclaimability by COW.
This is evidence of incorrect publication timing, not proof that file backing
saved that amount of RAM.

Build 167 moves publication to the completed full-image, level-zero,
single-level BC `TextureWriteTexels` path. Partial writes do not publish a new
whole-image snapshot. A mutex serializes snapshot cursor/descriptor updates.
Persistent published-range exclusions protect the anonymous-only guest compressor
even after a texture pool is finalized: `MADV_DONTNEED` on a COW file page restores
file contents, not necessarily zero. Combining file backing with compression of
live NVN pools (`T2_GZRAM_POOLS=1`) remains rejected.

## GPU budget accounting

Build 167 stopped at `T2_TEXTURE_BUDGET`, detail `0x1a8`. The counter was charging
compressed guest storage even for BC textures with no GL storage yet.
Build 168 charges eligible deferred textures zero until first materialization,
then reserves full decoded width × height × output-bytes-per-pixel before GL
allocation. Destruction releases the reserved amount. The 420 MiB limit is NOT
raised or disabled. The separate memory-floor governor remains enabled.

These runs have not yet exercised large-texture first-use materialization:
there are no `LC2_BC_MATERIALIZED` receipts in the latest run. Its new budget
path is cross-built but still needs a positive on-device first-use test.

## Bounded run receipts

See each directory under `evidence/` for its actual log and harness status.
Frame counts below are `NVN_PRESENT_PIXELS` counters, not FPS, visual progress
or correctness of the scene.

| Evidence | Build | Result |
|---|---|---|
| `fileback-01` | 163 | Initialization-time snapshots; still memory floor |
| `backpressure-01` | 164 | Invalid pacing experiment: wrong meminfo success predicate; corrected in 165 |
| `backpressure-02` | 165 | Pacing active; still memory floor |
| `loading-combined-01` | 166 | Compression + early snapshot + pacing; still memory floor |
| `fileback-profile-01` | 166 | smaps proves early snapshot pages became anonymous COW |
| `fileback-postwrite-01` | 167 | 67 snapshot calls, 371761152 bytes; next refusal is texture budget; counter 64 |
| `deferred-budget-01` | 168 | 402653184-byte file cap exhausted; memory floor at detail `0x3f`; counter 104 |
| `fileback-sd-01` | 169 | 141 snapshot calls, 737157120 bytes; CPU fault; counter 136 |
| `fileback-no-gzram-01` | 169 | Compression disabled; memory floor at detail `0x3c`; counter 94 |

The SD-capacity experiment requests 1280 MiB, not the maximum 1536 MiB:
the SD had only 1573600 KiB free at preflight. Runtime reserve checks remain
active. SD disk space returns after the process closes the unlinked file.
The final snapshot byte count is storage written, NOT measured net RAM savings.
`fileback-postwrite-01/fileback-metrics.json` sampled before any relevant mappings
existed (all zero); it cannot establish a post-write RSS gain.

`LC2_ROMFS_BACKPRESSURE_MIB` is an optional pacing experiment: at low available
memory, sleep in 50 ms increments up to 500 ms before a read. It does not change
read bytes, result codes, image data or the memory-floor limit. It is not a fix.

## Current frontier: native NULL-base fault

Build 169 SHA-256:
`ee13ee352f0b3e98f2d98387c7b5445614133d5e3c8c2cc01382597c4bd2bead`

Installed with `.before-169` backup; device SHA-256 independently matched.
The recovered baseline remained manifest-checked through the normal build.

`fileback-sd-01/latest.log`:

```
STOP status=CPU_FAULT pc=main.text.seg+0x1177010 detail=0x9d30
x19 = 0x38944fa98
x8 = 0
x9 = 0x9d30
```

Disassembly of the unchanged owner `main.text.seg`:

```
0x1177008 ldr x8, [x19, #0x188]
0x117700c mov w9, #0x9d30
0x1177010 ldr x21, [x8, x9]
```

The parent structure's `+0x188` pointer is NULL. Why it was not initialized is
unknown. It is NOT yet attributed to the game, compression, file backing or a
missing platform contract. Compression-off is not a matched-phase exoneration:
that run stops earlier under memory pressure.

Physical capture `fileback-sd-01/live-60.png` is uniformly white, not a menu or
rendered scene. `menu-after.png` proves the Spruce menu returned after the test.
Process checks found MainUI alive and no runtime process. No device reboot was
needed in these runs. The latest diagnostic binary remains installed; experimental
memory options were supplied by the test harness, not made launcher defaults.

## Verification

- Seven shader/metadata Python tests pass.
- Launcher default/exit/CPU-restoration test passes.
- BC host test: 2097152 unique in-range blocks for 8192×4096 BC3;
  mip13, guards and full/striped decode equivalence pass.
- File-backing host test: exact bytes, unaligned tails, COW independence,
  exclusion boundaries and capacity guard pass.
- Builds 163–169 cross-built successfully through baseline + adapter overlay.
- Remaining: diagnose the native structure initialization, obtain a correct
  scene with real shader translations, then verify physical input, audio,
  save/reload, clean exit and sustained gameplay.

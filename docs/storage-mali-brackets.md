# M1: bounded GL storage -> Mali metadata brackets (build240)

Reviewed 2d4c36f / owner roadmap §48.5. Adds read-only metadata brackets around
initial large glTexImage2D and glRenderbufferStorage calls. No sizes, formats,
contents, admission, synchronization or lifetime policy changed.

## Diagnostic contract

LC2_STORAGE_PROBE=1 only; first 12 storage calls with >=1048576 pixels. Reads
at most 512 allocation descriptors and 4096 lines per snapshot. Reports up to
8 changed descriptors per call plus an overflow indicator. Missing/ambiguous
context, inaccessible debugfs or truncated table => metadata-valid=0, not a stop
or invented zero delta. Never reads driver mem_view or guest memory.

Printed identity: NVN owner ID, GL name, texture/renderbuffer kind, WxH, mip,
guest format and ticket; context's mem_allocs provides actual VA/commit metadata.
Changes are tagged attribution=bracket-only. No glGetError consumption, added
flush/finish or GL allocation is introduced. TLS snapshots keep simultaneous
probe callers separate; global atomic ticket bound limits total reports.

## Executed owned arm storage-bracket-01

Build240 SHA256 474d17adaa1288e112203195820f883be638850263f450062ce29bb7d0286e6f.
Backup of build239 preserved and verified at .before-240/lamentum-nextos.
Atomic staged install, full SHA read-back and independent target read-back.
Same floor=96 MiB, texture cap=300 MiB, strict GL, principal flow. Temporary
debugfs mount restored to unmounted. No controller injection or New Game.

12/12 brackets had valid complete metadata, no per-call detail overflow.
Selected measured brackets:

| NVN ID | kind / GL name | dimensions | changes inside bracket |
|---|---|---|---|
| 3 | texture / 2 | 1920x1080 | one new Native descriptor, 8990720 B commit |
| 4 | texture / 3 | 1920x1080 | one new Native descriptor, 8990720 B commit |
| 28 | renderbuffer / 1 | 1920x1080 | one new Native descriptor, 8990720 B commit |
| 60 | texture / 25 | 955x2048 | one new Native descriptor, 8523776 B commit |
| 81 | texture / 39 | 3600x2160 | Native descriptors 31109120 + 32821248 B, plus two 262144 B descriptors |

The earlier unexplained 32821248-byte descriptor is now observed during owner
81's upload bracket (29.67 + 31.30 MiB large descriptors). This is stronger than
matching a size alone: explicit GL call + owner + pre/post VA metadata. It is NOT
proof that all changed allocations are solely this texture, permanently live,
or separately physical: driver staging, background allocation, shared pools and
aliases remain possible. Other first-use/draw allocations are outside these
initial-storage hooks. Retired VAs and same-VA same-size replacement are untracked.
The other previously observed 55984128-byte descriptor was NOT identified by
these first 12 brackets; do not assign it from size or proximity.

Elapsed bracket windows (GL call plus both metadata reads, NOT instrumentation
overhead alone): 1.28–50.38 ms. The longest is owner 81. No A/B overhead or FPS gain
is claimed, and no unsafe release/drop is inferred from these windows.

## Build / host verification / cleanup

Pinned ARM64 build succeeded, 435/435 baseline checks. Header parser compiled as
standalone C from the public overlay and exercised hex VA/commit, Native versus
Imported UMM and address lookup; full host suite 254 PASS. Clean-export test and
rebuild verification recorded alongside receipts before publication.

Owned harness: execution_verified=true, runtime STOP T2_MEMORY_FLOOR, frame 7,
cleanup_errors=[]. Final MainUI/principal/runtime each one, game zero, CPU mask
4-7 restored, no pending launch; DRM final-menu.png shows Spruce home icons.
Build240 remains installed; probe default-off on normal launches.

## Next

Extend only the observational frontier needed for the still-unbound 55984128-byte
allocation, and measure whether owner81's extra storage is transient/staging or
retained across completion. Releasing, resizing, reformatting or alias-policy
changes require separate lifetime/content proof (and quality approval where
applicable). M1 safe headroom, gameplay and 30 FPS remain unachieved.

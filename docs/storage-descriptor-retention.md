# M1: owner81 bracket descriptors are transient versus persistently observed

Reviewed 4f5f8dc / owner §48.5, following §61. Same installed build240;
no rebuild, GL synchronization, storage/content/lifetime or memory-policy change.

## Same-run correlation, not cross-run address matching

Arm storage-retention-01 has 13 owned process snapshots. The same run's
LC2_STORAGE_CHANGE lines for owner81 / GL39 identify VAs 0x5ef6000000 and
0x5ef7e00000, with commits 31109120 and 32821248 bytes. A completed/flushed
LC2_STORAGE_PROBE line ends at log byte 290101. Samples record the remote log's
size/dev/inode BEFORE reading allocation metadata, so only observations whose
size already includes that completed marker are used for post-bracket tracking.

Eight observations qualify after that marker, covering 6.192 seconds:

| time from first process snapshot | VA 0x5ef6000000 | VA 0x5ef7e00000 |
|---|---:|---:|
| 4.165 s | 31109120 B | 32821248 B |
| 5.017 s | absent | 32821248 B |
| 5.908 s | absent | 32821248 B |
| 6.757 s | absent | 32821248 B |
| 7.590 s | absent | 32821248 B |
| 8.477 s | absent | 32821248 B |
| 9.444 s | absent | 32821248 B |
| 10.357 s | absent | 32821248 B |

The 29.67 MiB descriptor is gone in the next observation (0.852 s later), while
the 31.30 MiB descriptor remains unchanged at all eight observation points.
They must not be reported as two permanent allocations of owner81.

Hypothesis: the disappearing descriptor is upload staging and the persistent
one is texture storage. This is NOT proven; the driver can recycle VA/storage,
retain a pooled allocation after descriptor removal or allocate in background.
Absence is not a physical refund; persistent presence is not a last-reader fence.
No glFinish was added, and neither GPU completion nor continuous VA-generation
identity is attested. No safe deletion policy follows from this series.

## The remaining 55,984,128-byte descriptor

It first appears between process snapshots at 5.017 and 5.908 s. The corresponding
log-size interval contains a 3600x3600 texture (GL47) and several other allocations.
This narrows the next instrumentation window but does NOT establish its owner:
there is no GL-call bracket for it in the first-12-call instrument. No attribution
by matching dimensions or nearby log lines is promoted to a result.

## Execution / cleanup / tooling

Original 96 MiB floor, 300 MiB cap and strict GL unchanged; no button injection.
Owned identity/execution verified. Runtime STOP T2_MEMORY_FLOOR at frame8; no
cleanup errors. Probe overhead not A/B-qualified; differing frame count from
other arms is not a performance improvement.

Final MainUI/principal/runtime each one, game zero, original CPU mask 4-7, no
pending launch, temporary debugfs mount removed; DRM final-menu.png shows Spruce
home icons. Build240 remains installed with probe default-off on normal launches.

`tools/storage_retention.py` rejects mixed run/process/log/context, backwards
size/time and missing/truncated metadata. Four host tests, full suite 258 PASS.
A clean-export test run is recorded alongside the evidence. Raw smaps remain
owner-local; samples.json contains driver metadata and pathname aggregates.

Next: bracket the narrowed 55 MiB allocation window, and establish retained
storage/lifetime ownership before any resource-policy change. No new physical
headroom, gameplay or 30 FPS result has been obtained.

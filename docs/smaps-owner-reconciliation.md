# M1: RssFile does not establish a game-image working set

Reviewed roadmap revision c2227d1, owner §48.4/48.5. No runtime/storage policy change.

## Retraction of §§55–56

The observed /proc/self/status RssFile values stand. Their attribution to ordinary,
reclaimable game-image pages does NOT. Neither subtracting system AnonPages from
process VmRSS nor the label RssFile proves that owner. Shmem near zero also does
not rule out driver/DMA allocations. Do not run a drop hint based on those claims.

## Fresh owned run: smaps-owners-02

Same installed build239, original 96 MiB memory floor, 300 MiB texture budget,
strict GL. Principal flow; no input, no New Game, no storage change.
Harness: execution_verified=true; runtime STOP T2_MEMORY_FLOOR at frame 2;
cleanup_errors=[]; four read-only samples, all bound to UUID/boot/PID/starttime
and the installed executable inode. UUID 406f39ae-c73d-4fae-92bd-3c7881122cc5,
PID 7073. Sampling is sequential/non-atomic and overhead was not A/B-qualified.

Last sample, raw KiB:

| source | metric | value |
|---|---|---:|
| status | VmRSS | 710072 |
| status | RssAnon | 371452 |
| status | RssFile | 338348 |
| status | RssShmem | 272 |
| sum(smaps) | Rss | 445536 |
| sum(smaps) | Anonymous | 373172 |
| sum(smaps) | Private_Clean | 71028 |

VmRSS minus sum(smaps Rss) is 264536 KiB. This is NOT a measured image-file size.
Top pathname group is anonymous (361912 KiB RSS), main.text.seg is 30132 KiB,
libmali.so is 20320 KiB. /dev/mali0 VMAs occur with smaps Rss=0; zero there is not
proof of zero GPU physical storage. A driver/kernel accounting discrepancy is a
candidate explanation, NOT established causality. Need same-window Mali physical
counters and kernel counter implementation before assigning the gap to a class.

All samples and per-path totals: evidence/smaps-owners-02/samples.json.
Full raw smaps remain owner-local in private-backups/smaps-owners-02/.
Parser tools/smaps_owners.py keeps Anonymous for file VMAs (COW), deleted pathnames
and device pathnames distinct; four host tests. No mapping is declared safe to drop.

## Failed first attempt and recovery

smaps-owners-01 collected zero samples: no owned header appeared; observer rejected
LOG_GENERATION_CHANGED. It is not another game run or an FPS result. Principal was
waiting for acknowledgment with child getevent; removed only our UUID-bound pending
command, stopped that exact child after checking parent/argv, then supplied a
synthetic acknowledgment to the shell's /tmp/ge_out loop (not physical/game input).
No supervisor was restarted. Captured restoration, then retried as a new run UUID.

Final state after run 02: MainUI=1, principal=1, runtime=1, game=0, original CPU
mask 4-7, no pending launch; DRM screenshot final-menu.png visibly shows Spruce.

## Next gate

Reconcile status/smaps against same-window driver counters. Until then retract
'image pages are the largest reclaimable lever', keep original data and all
storage policies unchanged. World/playability/30 FPS remain unachieved.

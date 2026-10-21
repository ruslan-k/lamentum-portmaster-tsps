# swap-priority-01 — negative OOM arm at frame 115; causality unresolved

> **NEGATIVE ARM RETAINED; CAUSAL VERDICT WITHDRAWN.** [Audit](../../docs/c0-profiler-audit.md).
> Harness 8, the matching kernel victim, original-priority restore and clean cleanup are
> confirmed. One unmatched-phase arm does not prove file-first is necessary, that zram
> fallback waits for full capacity, or that this policy universally fails. Physical media
> and per-process swap destinations were not established from path names/priorities.
> Treat mechanism, cross-run FPS/progress and categorical conclusions below as historical
> hypotheses, not accepted results. No new memory-policy arm was run in this correction.

One variable changed on an otherwise identical arm (same ELF `602d05be…3391`, same env as
`evidence/swap-01`): `/dev/zram0` priority **-3 -> 100**, so the RAM-backed tier serves
reclaim before the two file swaps. Both directions were verified by re-reading `/proc/swaps`
(`swap-state.json`, `swap-raise.json`, `swap-restore.json`).

## Why this was worth one arm

`tools/swap_policy.py state` on the idle board:

| device | type | size | priority |
|---|---|---|---|
| `/mnt/sdcard/mmcblk1p1/cachefile` | file | 512 MiB | **40** |
| `/mnt/UDISK/swapfile` | file | 1 GiB | -2 |
| `/dev/zram0` | zram (lzo) | 481 MiB | **-3** |

The guest's "physical" memory is anonymous `alias_physical` mmap (see `loader.c` svc 0x2c), so
the kernel can page it out — and with this ordering it pages it out **to the microSD first**
(766 MiB of VmSwap in `evidence/swap-01`, ~98 major faults/s, `state=D
wait_on_page_bit_common`). Putting the compressed RAM tier first looked like a free win.

## Result: it was killed, not sped up

    07:0x  game start (LAMENTUM_LAUNCH …)
    …      zram0 used 27 648 kB, cachefile unchanged at 32 168 kB
    …      MemAvailable 511 MB -> 131 MB in ~55 s
    argv   /mnt/sdcard/mmcblk1p1/Roms/PORTS/Lamentum.sh: line 56: 3846 Killed  ./lamentum-nextos
    kernel oom_reaper: reaped process 3846 (terminator2d-ne), now anon-rss:0kB,
                       file-rss:132272kB, shmem-rss:0kB
           mali 1800000.gpu: OOM notifier: dev mali0 135416 kB

So this is a **real kernel OOM with a victim receipt**, not a log hint (`tools/exit_outcome.py`
class 8). Frames presented: **115**, against 162 (`PHYSICAL_MEMORY_CONFLICT`) and 944
(`TIME_LIMIT`, 600 s) for the same loading path on the unmodified ordering.

## Mechanism (stated as a hypothesis, not a proof)

With zram first, reclaimed pages stay in RAM as compressed data. zram's memory is
unswappable and competes with the 640-700 MB working set, and the kernel will not fall through
to the file swap until the zram tier is full (493 MB) — it OOM-kills at the floor first. The
file-swap-first ordering instead *removes* those pages from RAM entirely, which is why the
board survives 600 s while being slow. That ordering was not an accident to "fix"; it is what
keeps this 963 MB board alive.

Consequence for the roadmap: "move the swap to RAM" is refuted as a performance lever here.
The remaining option in this family is to stop writing those pages out at all (keep the
resident working set smaller, or avoid touching cold guest memory), which is exactly what the
runtime's own userspace compactor (`t2_guest_memory.h`) already attempts.

## Reversibility

`swap-restore.json`: `swapoff /dev/zram0` drained the 2 092 kB residual, `swapon -p -3` put the
original priority back; verified zram used 0 kB, priority -3, `zram_first=false`.
`tools/swap_policy.py` now takes an explicit `--allow-used-kb` for that residual instead of the
guard being relaxed silently (5 unit tests).

## Limits

- One arm, one configuration, loading stage; no gameplay claim.
- `MemAvailable` was already falling before the OOM (511 -> 131 MB), so the arm also shows the
  pre-existing memory squeeze; the A/B does not isolate how much of the kill is zram policy
  versus the working set. A second arm at the same ordering would be needed to call it
  reproducible.
- The device was left exactly as found: `game=0`, `MainUI=1`, CPU mask `0-7`, swap order
  original.

Artifacts: `swap-state.json`, `swap-raise.json`, `swap-restore.json`, `preflight.json`,
`env.json`, `owner.json`, `samples.jsonl` (7 samples), `harness.log`, `harness-exit.json`,
`before.json`, `cleanup.json`.

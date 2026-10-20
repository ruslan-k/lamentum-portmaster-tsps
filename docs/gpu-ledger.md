# G0 initial ledger: charged textures plateau; remaining memory owners unresolved

Roadmap §25.4 G0 ("top memory growth classes and charged-vs-unaccounted gap measured before unsafe
pressure"). Build219 adds one read-only line to the existing memory sampler; no admission change,
no new allocation, no budget change.

## The instrument

`T2_MEMWATCH_SAMPLE` (every 40 checks ≈ 10 s) now also reports the already-existing charged texture
budget next to the system numbers:

    T2_MEMWATCH_SAMPLE checks=… available-MiB=… swap-free-MiB=… vmrss-MiB=… vmswap-MiB=… level=…
                      texture-live-MiB=… texture-peak-MiB=… texture-charges=… texture-budget-MiB=…

Build219 ELF SHA-256 `b8407822b205b0012401ed327a82f9ae94e31344a0bfc1d77ccdc1f7b798df4a`;
previous executable kept as `lamentum-nextos.before-219` (`034c8f96…`). Host suite: 71 tests.

## The series (arm `load-probe-10`, build219, cap 512 MiB, texture budget 300 MiB)

| checks | MemAvailable MiB | RSS MiB | swap-in-use MiB | texture-live MiB | texture-peak MiB |
|---:|---:|---:|---:|---:|---:|
| 40 | 440 | 416 | 0 | 69 | 69 |
| 200 | 160 | 601 | 19 | 65 | 72 |
| 360 | 68 | 717 | 261 | 102 | 102 |
| 520 | 70 | 701 | 725 | 122 | 122 |
| 680 | 79 | 643 | 874 | 126 | 126 |
| 840 | 77 | 658 | 865 | 126 | 126 |
| 1000 | 81 | 662 | 859 | 126 | 126 |
| 1160 | 67 | 665 | 860 | 126 | 126 |
| 1320 | 84 | 661 | 867 | 126 | 126 |
| 1360 | 75 | 655 | 869 | 126 | 126 |

Raw series: `evidence/load-probe-10/memwatch-series.json`.

## What this corrects

The charged texture budget plateaus at 126 MiB against a 300 MiB cap in this sampled interval,
while `MemAvailable` falls from 440 to around 70 MiB and process `VmSwap` rises to around 870 MiB.
This is evidence of pressure alongside stable **accounted** texture storage, not proof of a specific
unaccounted owner. RSS includes more than the guest heap; `VmSwap` is not physical resident RAM.
Neither value identifies Unity heap, host allocations, driver pages or alias overlap by itself.

The earlier version of this report incorrectly concluded that textures were not the consumer and
that Mali's OOM figure was merely overlapping process memory. Those claims are withdrawn. Shared
physical RAM does not establish whether the particular accounting categories overlap; obtain
mapping/driver ownership evidence before adding or subtracting them. The 8192-square first-use
reservation remains a separate proven hazard (§26.3), even when not reached in this interval.
No priority change or texture-policy change is justified by this series alone.

## What follows

- Follow the latest roadmap §26: finish collector identity/framing, audit the exact large-resource
  descriptor, then classify other GL/driver/guest owners. Do not pick a heap or residency fix yet.
- G0 is not finished: depth/renderbuffer storage, buffers and EGL surfaces remain unclassified;
  FBO object counts must not be confused with attachment storage. Track allocation generations,
  aliases and completion lifetime before deriving a charged-vs-unaccounted gap.
- Arms 04/07/08/09 used build218, **not build219**. They demonstrated controlled budget stops.
  Arm 10 used build219 and was explicitly terminated by the operator with TERM to its game PID;
  it did **not** demonstrate that its 300 MiB texture guard stopped the load. MainUI restoration
  was checked separately. Presentation counts and these memory samples are not gameplay evidence.

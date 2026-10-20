# G0 at first light: textures are NOT the consumer — the guest heap is

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

The charged texture budget **saturates at 126 MiB against a 300 MiB cap** and then stops growing,
while `MemAvailable` collapses from 440 to ~70 MiB and the process's swap-in-use climbs to ~870 MiB.
So in this phase:

- the consumer is the **guest process's own memory** (RSS + swap ≈ 1.5 GiB on a 963 MiB board with
  2 GiB of swap), not textures;
- the earlier "GPU wall" reading (Mali OOM notifier reporting 725 992 kB) was Mali's accounting over
  **shared system memory**, so it must be read next to RSS/swap, not as separate VRAM. The roadmap
  warned about exactly this: ZRAM savings, SD backing and "GPU bytes" are not independent pools;
- the one heavy texture event (an 8192×8192 BC decode charged at 256 MiB) is a **spike**, not the
  steady-state cause: it appears in some arms and not others, and the 126 MiB plateau here shows the
  load does not need it resident to reach this phase.

The earlier request to change texture decode policy is therefore **withdrawn as a priority**: it
addresses a spike that is not what exhausts the device in the measured phase.

## What follows

- The dominant class to investigate is the guest heap (CPU side) — matching §25.3's CPU attribution
  (96.75 % of bounded samples in the adapter's SVC path) and the 0.836 s/present main-thread cost.
- G0 is not finished: this ledger covers the texture class only. Depth/renderbuffer/framebuffer
  classes and EGL surfaces still have no counter, and until they do the charged-vs-unaccounted gap
  stays partially unknown. The next ledger increment must add those classes at allocation and
  release, with generation and fence lifetime, before any residency lever is chosen.
- The first acceptance gate from the roadmap still holds: a **controlled clean fail-closed stop
  before kernel OOM**. Build219 with `T2_TEXTURE_BUDGET_MIB=300` produced exactly that in arms 04,
  07, 08 and 09; this arm is the first one to show *why* the budget alone cannot prevent exhaustion.

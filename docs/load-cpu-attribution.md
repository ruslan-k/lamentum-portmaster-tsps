# Loading samples and SVC/IPC counts: CPU ownership remains unresolved

> Correction following roadmap §27 / the build219 action plan: the 400 MOMO samples were spread
> approximately round-robin over 32 threads. Sample fractions are **not executing CPU-time shares**.
> Earlier claims below identifying the dominant CPU owner from those fractions are withdrawn.
> See [the current profiling requirements](build219-gameplay-performance-action-plan.md#4-pr-c1--identify-svc-0x1a0x1b-and-actual-endpoint0x40-owner).
>
> **C1 source/ELF-pinned follow-up:** [AudioOut owner and mutex operands](../evidence/C1-audio-owner/README.md)
> resolves endpoint0x40 as EP_AUDOUT from audout:u, commands 7/8 as PCM append/released-buffer
> retrieval. Correct opcode-specific mutex operands yield **41 distinct addresses** in load-probe-08;
> the earlier 1,011 mixed X1 values were not a mutex-key census. Executing cost remains unmeasured.

Roadmap §25.3–25.4 (C0, bounded guest CPU profile) — measured on build218, arm `load-probe-08`.
No runtime change; the sampler is the existing `MOMO_STACK_SAMPLE_*` instrument.

## Setup

Same environment as the reproducible budget arm (`T2_TEXTURE_BUDGET_MIB=300`,
`LC2_BC_FILE_CAP_MIB=512`), with `MOMO_STACK_SAMPLE_MS=50`, `MOMO_STACK_SAMPLES=400`,
`MOMO_STACK_SAMPLE_AFTER=200`. Navigation completed through the measured cursor band
(page 391 → controls 1187 sampled bright pixels), then loading ran until the clean
`STOP status=T2_TEXTURE_BUDGET`.

## What the samples say

- **400 samples, 387 flagged `in-kernel=0x1` (96.75% of samples, not CPU time).**
  Thread selection was not CPU-weighted; this cannot distinguish a blocked thread from an on-CPU hot path.
- Native PC `0x7fa15b0bd4` occurred in 299 samples (74.75% of samples), and `0x7fa15b0bd8`
  in 9.5%. Without same-run process maps/ELF load offsets their routine/module attribution remains
  unresolved. The in-kernel flag alone does not symbolize an address.
- 32 probe samples over the run: frames 97 → 461, min `MemAvailable` 57 496 kB, 288 new textures,
  255 new BC deferrals, one entry-45 link, no unknown shader, ends with the clean budget stop.

## Which syscalls and IPC dominate

From the same run's log:

| Rank | SVC | Count | Share of 12 940 |
|---:|---|---:|---:|
| 1 | `0x1a` | 5 506 | 42.5 % |
| 2 | `0x1b` | 5 389 | 41.6 % |
| 3 | `0x2c` | 1 080 | 8.3 % |
| 4 | `0x1c` | 171 | 1.3 % |

`0x1a` + `0x1b` together are **84.1 %** of all syscalls, and both are handled through the
SIGTRAP bridge, so each one is a signal round-trip.

| IPC (endpoint/type/command) | Count | Share of 41 862 |
|---|---:|---:|
| `ep 0x40 type 6 cmd 0x8` | 29 140 | 69.6 % |
| `ep 0x40 type 6 cmd 0x7` | 10 376 | 24.8 % |
| `ep 0x1d type 6 cmd 0x0` | 1 099 | 2.6 % |
| `ep 0x1d type 6 cmd 0x4` | 1 093 | 2.6 % |

Two commands on **one** endpoint are 94.4 % of all IPC traffic.

## Interpretation (kept separate from the numbers)

The earlier 0.836 CPU s/present interval was a different build/phase. These round-robin samples
cannot attribute that cost or exclude Unity/IL2CPP work, compression/restoration, blocking,
scheduler delay or driver work. Endpoint0x40 is now source-bound to AudioOut (see follow-up above),
and SVC 0x1A/0x1B are specific candidates for investigation, not proven CPU bottlenecks. Measure
exclusive CLOCK_THREAD_CPUTIME_ID and wall intervals per handler/class, and resolve PCs using
same-run mappings before choosing a semantics-preserving optimization.

## Historical mixed argument-word distribution (not a mutex-key census)

Every `0x1a`/`0x1b` line already carries its arguments. Over the 10 895 pair calls in this run:

| `arg0x1` (raw logged argument word, not a proven wait key) | Count |
|---|---:|
| `0x34073d08c` | 2 759 |
| `0xffffffff` | 1 493 |
| `0x340000048` | 1 052 |
| `0xb0b40e0` | 1 030 |
| `0x34073d090` | 787 |

There are 1,011 distinct values in this historical mixed-X1 table. It combines the lock address
(X1 for svc0x1a) with a non-address operand (X1 for svc0x1b, whose address is X0). The corrected
source-checked census is 41 mutex addresses; all 1,493 unlock-X1=0xffffffff values are not unlock
mutex operands. Neither distribution alone proves a stalled wait or executing bridge cost.

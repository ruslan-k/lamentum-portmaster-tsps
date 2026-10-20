# Loading CPU attribution: the hot loop is our own SVC/kernel path

Roadmap §25.3–25.4 (C0, bounded guest CPU profile) — measured on build218, arm `load-probe-08`.
No runtime change; the sampler is the existing `MOMO_STACK_SAMPLE_*` instrument.

## Setup

Same environment as the reproducible budget arm (`T2_TEXTURE_BUDGET_MIB=300`,
`LC2_BC_FILE_CAP_MIB=512`), with `MOMO_STACK_SAMPLE_MS=50`, `MOMO_STACK_SAMPLES=400`,
`MOMO_STACK_SAMPLE_AFTER=200`. Navigation completed through the measured cursor band
(page 391 → controls 1187 sampled bright pixels), then loading ran until the clean
`STOP status=T2_TEXTURE_BUDGET`.

## What the samples say

- **400 samples, 387 of them `in-kernel=0x1` (96.75%).** The interrupted thread was inside the
  adapter's SVC/kernel emulation, not inside guest game code.
- Interrupted PCs are native addresses (`0x7fa15b0bd4` = 299 samples, 74.75%; `0x7fa15b0bd8`
  = 9.5%), i.e. the adapter's own trap handler body rather than `main.text.seg`/`sdk.text.seg`.
  Naming them needs a process-map capture in the same run; the raw addresses are preserved here
  instead of being guessed into symbols.
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

The 0.836 s/present main-thread cost measured earlier is not Unity/IL2CPP arithmetic: 96.75 % of
bounded samples land inside the adapter's own kernel emulation, and the syscall mix is a lock/wait
pair plus one IPC service pair. That is consistent with a spin/wait loop whose every iteration pays
our SIGTRAP bridge cost.

Two concrete, competing candidates — to be separated by measurement, not by preference:

1. **Bridge cost per SVC**: the 84 % `0x1a`/`0x1b` pair may be optimizable with a fast path that
   preserves semantics (no fake completion, no changed return values).
2. **A guest-side wait that never satisfies**: the `ep 0x40` command pair at 94 % of IPC may be a
   service answer the title is polling, which would make the loop a stall rather than useful work.

Roadmap §25.4 C1 asks for exactly one of these, chosen by data, with an A/B on the same scene
phase.

## First discriminator already measured: the keys change

Every `0x1a`/`0x1b` line already carries its arguments. Over the 10 895 pair calls in this run:

| `arg0x1` (wait/arbitrate key) | Count |
|---|---:|
| `0x34073d08c` | 2 759 |
| `0xffffffff` | 1 493 |
| `0x340000048` | 1 052 |
| `0xb0b40e0` | 1 030 |
| `0x34073d090` | 787 |

1 011 distinct keys with a small hot set: this is not one stuck key being re-polled forever, it is
fine-grained synchronization traffic across several objects (≈35 SVCs per presented frame).

So the "guest spins on a wait that is never satisfied" hypothesis is weakened for these keys, and
the remaining candidate is the **per-SVC bridge cost**: 35 bridge round-trips per frame at a
33 ms budget allows under ~1 ms per call in total. The next measurement is therefore the cost of
one `0x1a`/`0x1b` bridge round-trip (bounded timing of the existing handler, no semantic change),
followed by — only if it is material — a fast path that preserves return values and wake ordering.

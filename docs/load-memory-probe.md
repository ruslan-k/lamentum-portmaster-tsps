# Load probe: where the memory actually goes (arms 1-3)

Roadmap §22.4/§22.5. Everything below is measured with `tools/load_probe.py`, which drives
New Game from live captures and then samples the device every 5 s. No runtime change was made
for these arms.

## Arms

| Arm | Extra env | Outcome |
|---|---|---|
| `load-probe-01` | `MOMO_STACK_SAMPLE_MS/SAMPLES/AFTER` | fail-closed `STOP status=PHYSICAL_MEMORY_CONFLICT detail=0x3d5004000` at frame 30, before the load |
| `load-probe-02` | none | navigation aborted (the first capture was still the loading splash); run ended on `TIME_LIMIT`, cleanup clean |
| `load-probe-03` | none | reached the load, 98 samples over 548 s, then **OOM SIGKILL** (`Killed`, no STOP line) at frame 572 |

So arm 1's stop is **not** produced by the stack sampler in any established way: the same build
reached the wall without it. The conflict itself (`loader.c:491`, `MapPhysicalMemory` on a region
that is neither free nor an owned alias) remains an open, unexplained fail-closed stop that has
appeared exactly once.

## What the series shows (arm 3)

- `MemAvailable` fell from 112 MiB to a minimum of **48.4 MiB** (`49 536 kB`) while the asset phase
  ran, and the process was killed by the kernel at Mali **725 992 kB** — the same figure the earlier
  build218 run reported, i.e. the wall is the GPU heap, not the CPU heap.
- Textures stopped being created long before the kill: the `NVN_TEXTURE_REAL` counter reached 588
  and the BC-deferral counter 448, then stayed flat for ~280 further frames while memory kept
  falling. Texture **creation** is therefore not what drives the last part of the growth.
- The per-object size fields do **not** sum to residency: allocated `bytes=` fields total 1 801 MiB
  and the deferred `rgba-bytes=` fields total 6 191 MiB, while Mali really held 709 MiB. They are
  per-object sizes (several are 8192x8192 entries), not live storage — quoting them as "GPU memory
  used" would be wrong by an order of magnitude.

## Consequence: the missing instrument

There is no counter of *live* GL/Mali storage (allocated minus released) in the runtime, so the
next step is a bounded accounting instrument, not another guess: a per-frame tally of
`glTexStorage2D`/`glDeleteTextures` bytes plus the BC materialization charge, printed every 60
frames, with its own on/off A/B so its overhead is known. Only then can a residency lever (decode
cap, format choice, mip policy) be chosen and attributed.

## Tool fixes that came out of this

- the probe now waits until the cursor band is actually visible before sending any input
  (arm 2 pressed into a loading splash and lost the run);
- `transitions.json` is written before blocking on the harness, so an aborted probe keeps its reason;
- the harness classifies a SIGKILL without a STOP line as its own outcome (exit 7) and truncates the
  log before the `before` snapshot, so a previous run's stop cannot be re-reported.

Host suite: 65 tests. Device after arm 3: game absent, `MainUI` 1, `principal.sh` 1, CPU mask `0-7`,
and a woken kmsgrab showing a fully lit Spruce menu (57 600/57 600 sampled pixels).

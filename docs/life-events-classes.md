# M1: per-class declared storage in the menu (build245)

Reviewed bb81569 / owner §48.5. Extends the §66 observation ledger to the depth
renderbuffer class and to vertex-buffer stores; still a measurement, still
default off (`LC2_LIFE_EVENTS=1`), still no admission/deletion decision.

## What changed

- kind labels: 1 texture, 2 renderbuffer, 3 buffer; per-class byte and live-count
  totals in the single stop-path summary line.
- depth renderbuffers are recorded at glRenderbufferStorage (w*h*4 for the D24S8
  and D16 host formats used here) and released at the storage delete.
- buffer stores use a NEW respecification path: glBufferData on an existing name
  REPLACES its payload. Adding it as if it were a new mip would double count
  every re-upload; the first store is an allocation, later stores count as
  respecs. A host regression asserts exactly that ordering.
- no GL call, format, size, admission, budget, floor or delete behaviour changed.

## Measured arm life-events-03 (build245)

ELF 846ef10c3850ec245c702243b3c82b59ca398a863506a78cf1e76d62522ae314, PID22012,
principal flow, floor96/cap300/strict GL, no input:

    storage-calls=167 extends=50 deletes=25 delete-with-views=0 name-reuse=24
    retained=262419760 peak=270243120 live=92 alias-views=0 overflow=0
    tex-bytes=250438960 tex-live=90 rb-bytes=11980800 rb-live=2
    buf-bytes=0 buf-live=0 respecs=0

- Internal arithmetic closes exactly: 92 live + 25 deleted + 50 mip extensions
  = 167 storage calls.
- Textures: **238.84 MiB over 90 live images**. Depth renderbuffers: **11.43 MiB
  over 2 live** objects — the first measurement of this class in this ledger.
  The report is a class total, so it does NOT attribute a size to a specific
  render target.
- Peak − retained = **7.46 MiB** of transient declared payload was released
  during the run.
- Buffers read 0/0 with respecs=0 because the vertex-stream and stable-VBO paths
  are off in this configuration; the respecification path is therefore covered
  by the host fixture only, not on device.
- `delete-with-views=0` remains a guard receipt at the single instrumented
  delete site, not a global safety proof.

All of these are **declared payload**, not Mali residency and not reclaimable
memory. The same run's menu ledger reports 93 live textures and a budget charge
of 115278848 B (~109.9 MiB) at its last interval, while this ledger sums 238.84
MiB of texture requests. The two count different things (budget charge/admission
vs every glTexImage2D level request) and are **not reconciled**; that gap is an
open measurement question, not evidence of waste.

## Device result and cleanup

STOP `T2_MEMORY_FLOOR`, no OOM receipt, harness cleanup `[]`. Independent final
snapshot: game0, MainUI1, principal1, runtime1, CPU4-7, no pending launch,
debugfs unmounted; DRM capture shows the Spruce home. Build245 deployed by
staged write + fsync + atomic replace with independent hash read-back; build244
kept as `.before-245`.

Host: 266 tests PASS in a clean index export. The C fixture, compiled from the
public patch, now also covers respecification (replace, not add), per-kind
totals and the formatter/printf equality across all seventeen fields. Build245:
435/435 baseline checks.

## Next

Two open items, in order: (1) reconcile the declared texture payload with the
budget charge and `gpu_memory` in one run, (2) obtain a real GPU-completion
receipt so a reader epoch can be qualified — the ledger still cannot justify any
free, and menu headroom, world and 30 FPS remain OPEN.

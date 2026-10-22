# M1: the 2.09x texture gap is decoded-vs-compressed, not mip chains

Reviewed 2aba2d3 / owner §48.5. Answers the open question from §68 by splitting
the declared texture payload instead of guessing. Observation only: no
admission, budget, format, deletion or quality change.

## What was added (build247, still default off)

The opt-in ledger now classifies each texture request without adding any GL
change:

- `tex-l0` / `tex-mips`: level 0 versus additional mip levels;
- `tex-scaled` / `tex-half`: the host-reduced variants;
- `tex-charged` / `tex-uncharged`: requests whose texture carries a budget
  charge (`t2_budget_bytes != 0`) versus those outside the budget;
- `tex-guest`: for charged textures, the guest-side storage (`t->size`, i.e. the
  compressed BC payload for BC formats).

Host fixture asserts each bucket and keeps the stop-path formatter equal to
snprintf across all fields.

## Measured arm tex-levels-02

ELF ecef4ba2075946095e69120137366850c41184d26e3e82c995cdd98995bd6575, floor96/
cap300/strict GL, principal flow, no input:

    tex-bytes=241485104 tex-live=90      (230.30 MiB live, decoded)
    tex-l0=247062780  tex-mips=713780    (0.68 MiB of extra levels)
    tex-scaled=0      tex-half=0
    tex-charged=247776560  tex-uncharged=0
    tex-guest=107024384                  (102.07 MiB guest/compressed)
    budget charge at the last interval: 115278848 (109.94 MiB), 93 live

Conclusions that follow directly:

1. **Mip chains do not explain the gap.** Extra levels total 0.68 MiB
   (0.29 % of the payload). The earlier hypotheses "budget counts level 0 only"
   and "multi-mip undercharge" are both refuted for this phase.
2. **Scope does not explain the gap.** Every declared texture request belongs to
   a charged texture (`tex-uncharged=0`); nothing bypasses the budget.
3. **The basis explains it.** The budget is denominated in the guest/compressed
   storage (102.07 MiB), while GL holds the decoded pixels (230.30 MiB live,
   241.72 MiB including depth). Decoded/guest = 2.256; declared/charge = 2.095.
   The small residual between `tex-guest` (107.02 MB) and the charge
   (115.28 MB, 7.7 %) is **not** explained by this arm and is recorded as open.

This matters for the memory wall: a 300 MiB texture cap is expressed in
compressed guest bytes, so it does not bound GL residency — at this measured
ratio the cap corresponds to roughly 675 MiB of decoded storage on a 963 MiB
board. That is a statement about accounting, not yet about a fix; no cap,
admission or format policy was changed.

## Device result

STOP `T2_MEMORY_FLOOR`, no OOM receipt, cleanup `[]`; game0, MainUI/principal/
runtime1, CPU4-7, no pending launch, debugfs unmounted; DRM capture shows the
Spruce home. Build247 deployed by staged write + fsync + atomic replace with
independent hash read-back, build246 kept as `.before-247`. Host 273 tests PASS
in a clean index export; build247 435/435.

## Build248 per-initialize pair observation (2026-10-22)

The follow-up [device report](../evidence/texture-pair-20261022-01/README.md)
uses runtime `1462d92791748650e951cd9256d1fee712213b18bc08e25b8eb22ab0b4aaa73a`,
floor96/cap300/strict GL, and no input. It stopped at `T2_MEMORY_FLOOR` (95 MiB
reported against floor96), with no OOM evidence, 8 present records, and no menu
events.

The 1 Hz menu ledger measured first present at 6,574 ms/frame1 with
`budget-live=112325632` B (107.12 MiB), 91 live textures and
`CmaFree=3504` KiB; at 7,603 ms/frame8 it measured `budget-live=115278848` B
(109.94 MiB), 93 live textures and `CmaFree=11764` KiB. Its `MemAvailable`
values were 130156 KiB and 77908 KiB; the separate 250 ms floor-watch event
reported 95 MiB, so these are asynchronous samples, not one timestamp.

The opt-in pair ledger emitted 117 initialization events (114 with a live GL
storage record, 3 `no-live-gl-storage`, zero pair overflow). Cumulative event
payloads were 116851712 B guest/charge, 239125808 B declared GL texture storage,
and 11980800 B declared GL renderbuffers. Across events, GL-declared texture +
renderbuffer bytes exceeded charge in 69/117 pairs; 68 exceeded 2x and 3
exceeded 4x. For example, id61 (800x1500, format `0x42`) recorded 614400 B
charged versus 4800000 B GL-declared (7.812x). These are declared payloads, not
measured Mali residency.

This is **partial M2A evidence**, not a live-set join. There were 24 deletes and
24 GL-name reuses; the records do not yet carry timestamped storage/object
generations, per-ID retirement, aliases, or last-reader completion. The event
sums therefore cannot be reconciled as if they described one simultaneous set.
The budget-versus-guest residual remains unresolved; do not infer a leak or
apply a safety factor from these data. Share-group identity is unverified and
GPU completion unobserved. The raw log and captures are local-only; report and
compact receipts are committed.

## Build249 timestamped storage replay (2026-10-22)

The [build249 device report](../evidence/m2a-20261022-01/README.md) adds monotonic
timestamps and object/storage generations to the opt-in pair and GL storage
journal. Runtime SHA-256 is
`0e62238c69c36e9fbd49669d5c062c0449ee56c2624b44acf37461c206cd588b`; floor96,
cap300, strict GL, no input.

The owned run (`cc013fc9-af26-4e2f-84b6-38e5c7af35dd`) produced 3 presentation
records and no menu events, then stopped at `T2_MEMORY_FLOOR` (68 MiB reported
against floor96). The first-present sample at 6,746 ms/frame1 had
`MemAvailable=119140` KiB, `CmaFree=17512` KiB, and budget-live `112325632` B.
The floor callback found the GL lock busy (`EBUSY`), so it could not emit the
direct live-pair snapshot. It did record the floor timestamp and exact available
sample (`70304` KiB).

The run emitted 116 pair events (113 with GL storage, 3 without), 163
storage events (50 extensions), and 24 delete events; no event ring overflowed.
Replaying each storage generation through the floor timestamp yields 89 live
GL-storage records: 87 textures / `224539952` B and 2 renderbuffers /
`11980800` B. The total `236520752` B matches `LC2_LIFE_SUMMARY` at process stop
exactly. This validates the declared GL-storage event replay for this run; it
does not prove Mali physical residency or GPU completion.

The T2 budget's exact per-object live value at the floor remains unresolved:
budget retirement is not logged per NVN object, and the lock-busy callback did
not sample the independent T2 budget counter. `/proc/pressure/memory` is absent
on this device. The cleanup receipt's unanchored stop parser also mistook the
`LC2_MENU_LEDGER_PRESTOP` diagnostic label for a runtime stop; the actual owned
log contains only `STOP status=T2_MEMORY_FLOOR`. These parser/receipt gaps must
be fixed before the next run.

## Next

Add per-object T2 budget add/sub events and read that independent counter even
when the GL lock is busy; anchor the stop/frame parsers to the owned run. Keep
the 96 MiB floor and 300 MiB cap unchanged. Only after the menu memory gate
passes should the next phase reduce a measured storage class; world, input,
sound, save/load, and gameplay 30 FPS remain OPEN.

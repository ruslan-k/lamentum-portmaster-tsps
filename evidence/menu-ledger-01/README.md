# menu-ledger-01: first menu-phase memory waterfall

One build230 arm with `LC2_MENU_LEDGER=1` (opt-in, at most 1 Hz, host-observable
only, no behaviour change), strict GL, 300 MiB texture budget, diagnostic floor
32 MiB. The arm presented **41 frames in 20.5 s**, verified its own
run identity, cleaned up with no errors, and stopped at `T2_MEMORY_FLOOR`.

- `waterfall.json` — the measured series and its deltas.
- `ledger-lines.txt` — raw `LC2_MENU_LEDGER` records (owner-local copy of the log
  lines; the full runtime log stays owner-local).

Headline numbers: `MemAvailable` 129.3 → **54.7 MiB by frame 16**;
`CmaFree` 24.3 MiB → **1.0 MiB**; game `VmSwap` 0 → **422.4 MiB**;
charged texture storage **+50.2 MiB** across 10 new textures.

Not measured here: renderbuffers, buffer objects, EGL surfaces/images and driver
retained storage are `untracked`; the pre-floor ledger line is missing because the
floor decides inside the memwatch path — the last interval line plus
`T2_MEMORY_FLOOR_HIT` bracket that moment instead.

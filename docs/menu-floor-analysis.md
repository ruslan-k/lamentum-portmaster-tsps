# Why the menu cannot hold the 96 MiB floor (owner §48 / M1)

Reproducible arithmetic on already-measured receipts: `tools/floor_analysis.py`
(5 tests) turns a ledger series + a floor into a drawdown, a drawdown rate and a
floor-crossing projection, and never invents a value it was not given.

## Measured shape (build230, `menu-ledger-01`, 41 presents in 20.5 s)

Start **129.3 MiB** available, low **54.7 MiB at frame 16 (4.5 s)**, so the menu
draws **74.6 MiB in 4.5 s** — **16.46 MiB/s** at **3.31 fps**. In the same window
`CmaFree` goes 24.3 → 0.0 MiB, game `VmSwap` 0 → 422 MiB, and charged texture
storage **+50.2 MiB**.

## Crossing arithmetic

| floor | margin at start | projected crossing | measured stop |
|---|---|---|---|
| **96 MiB** | 33.3 MiB | 2.02 s (~6.7 frames) | **frame 2** (`menu-229-01`) |
| 32 MiB | 97.3 MiB | 5.91 s (~19.6 frames) | frame 55 (`menu-229-02`) |

The projection is deliberately a **linear upper bound on time**, and the data shows
why it cannot be treated as a predictor: the drawdown is a fast burst, then a
plateau around 63–73 MiB, then a further decline. For the 96 MiB floor it *agrees*
with the observed frame-2 stop (the first burst alone exceeds the 33 MiB margin);
for the 32 MiB floor it under-predicts (19.6 frames vs 55) because most of the early
loss is recovered by swap and reclaim before the final slide.

**Conclusion for M1:** the 96 MiB floor is not survivable by this menu for longer
than the first few frames — not a tuning problem, and not fixable by a longer
timeout. Any New Game attempt must first reduce what the menu itself allocates.

## Ranking of the drawdown (as far as the adapter can see)

1. `CmaFree` exhaustion: 24.3 → 0.0 MiB — a ~28 MiB pool drained inside the menu.
2. Guest pages to swap: `VmSwap` 0 → 422 MiB (memory that left the reclaimable pool).
3. Charged texture storage: +50.2 MiB over 10 textures.
4. Colour targets +3 (19 total) ≈ +15.9 MiB; depth renderbuffers constant at 22.9 MiB.
5. Buffers, EGL surfaces and driver-retained storage: **untracked** in the ledger.

## The one number that *is* settled

The four 1080p images (three colour + one depth-equivalent) are **31.64 MiB at
1080p** and would still need **14.06 MiB at 1280×720**: the maximum nominal saving is
**17.58 MiB**, which matches the owner's correction exactly (recomputed here from
bytes, not copied). That is at most a quarter of the observed 74.6 MiB drawdown, and
it is nominal storage, not measured Mali residency.

## What this rules in and out

- **Out:** raising the floor, lengthening the run, or expecting the 720p scaling to
  solve the menu by itself (17.58 MiB of a 74.6 MiB drawdown).
- **In:** finding the CMA consumer and the retained colour targets (needs the B2
  last-reader/ownership ledger), and — with approval — the reversible 720p storage
  A/B as one factor among those, gated by `frame_diff.equivalent()` with the exact
  comparison reported alongside.

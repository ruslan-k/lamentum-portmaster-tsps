# Single navigation core (roadmap 32.7, item 3)

`tools/navigator.py` is the one decision core that `load_probe`, `newgame_navigate`
and the principal harness are meant to share. It is **pure**: it consumes
observations and returns one action. It performs no device I/O, no capture, no
pixel heuristics and no OCR, so it can be tested exhaustively off-device.

## Rules it enforces (each one has already produced a wrong answer here)

| Rule | Why |
|---|---|
| One press per **strictly newer present serial** | At 1–2 fps a tap can start and end between two samples; a stale serial means the press was never observed |
| More than `STALE_SERIAL_LIMIT` observations without a new serial → **refuse** | Otherwise the driver presses forever against a frozen title |
| A row move of >1 per press is reported as **overshoot**, not as a second press | A long hold moves two rows; the fix is hold length, not more presses |
| A changed picture is **not** a page change | Animated menu backgrounds change pixels while the cursor sits still |
| A cursor outside every measured band → `wait`; an unknown page → `refuse` | Guessing a row is how a "New Game" press lands on "Credits" |
| `WORLD_VISIBLE` is never claimed as verified here | A world claim belongs to scene receipts (§32.7 item 4), not to navigation |

Rows come from the measured main-menu highlight band (`load 425 / newgame 475 /
options 525 / credits 575`, tolerance 12 px); the pitch is derived from those
measurements, so a re-measured menu needs a new row table, not new code.

## Actions

`press down`, `press confirm`, `wait` (with a reason), `refuse` (with a reason),
`done` (page reached), plus `overshoot` events retained in `nav.events`.

## Verification

`tools/test_navigator.py` (10 tests): one press per new frame, no re-press on a
stale serial, refusal when the serial stops advancing, two-row overshoot, animated
picture with a static cursor, page change not inferred from cursor movement,
unknown page/unbanded cursor, zero serial, `WORLD_VISIBLE` treated as unverified,
and the measured row table. Full host suite: **180 tests PASS**.

## Not done yet — deliberately

- No capture-side oracle: nothing in this repository yet turns a KMS frame into
  `(page, cursor_y)`. Until that exists and is measured on the current build, this
  core cannot drive the game, and `load_probe`/`newgame_navigate` stay disabled by
  default (`--allow-unverified-navigation` remains diagnostic only).
- No page features for `NEWGAME_CONFIG`, `CONTROLS` or `LOADING` are pinned; the
  core only knows that those pages are terminal for this stage.
- Wiring the harness to this core, and proving one real press→serial→row chain on
  device, is the next step. No scene, id295, memory or FPS claim follows from this
  component.

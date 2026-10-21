# Measured page/cursor oracle (roadmap 32.7, items 1 and 3)

`tools/page_oracle.py` turns one frame into `(page, cursor row)`; `tools/navigator.py`
turns that into one action. Together they are the "capture-side oracle" the previous
step was missing — and the first thing they did was **refute the geometry this
project had been carrying**.

## What the live frame changed

The recorded menu signature was "highlight band at x 88..124, rows at y
425/475/525/575". One in-run capture of build229 (`evidence/nav-oracle-01`) shows a
different picture:

| feature | old assumption | measured on this build |
|---|---|---|
| menu rows | 425 / 475 / 525 / 575 | **442 / 492 / 542 / 592** (pitch 50) |
| selection | bright full-band highlight in x 88..124 | **cursor glyph left of the row**, ink in x 40..120; the selected row reads 26.6 there, the others 0.0 |
| text body | x 200..1000 | **x 140..340** (left-aligned list) |
| region | whole frame | **y 380..660** (the title at y≈174 otherwise reads as a row) |

The glyph is also **dimmer than its own text** (26.6 vs 53.5), so "brightness above
the row's text" can never find it. The oracle therefore selects the row by *has a
glyph* (absolute level plus separation from the second best), not by contrast.

## Result on the real captures

| capture | verdict |
|---|---|
| `nav-oracle-01-00.png` (boot, 2,759 B) | `UNKNOWN` — "no bright rows in the text window" |
| `nav-oracle-01-01.png` (main menu, 138,730 B) | **`MAIN_MENU`, row `load`, cursor_y 442**, bands `[442, 492, 542, 590]` |

Feeding that into the navigation core yields exactly one action:
`press down (row load, serial 55)` — the first press target, derived from a real
frame instead of a blind sequence.

An earlier version of the receipt recorded `wait: cursor not inside a known band`;
that was the navigator still holding the old row table. Corrected rows are now in
both modules and the superseded action is kept in the receipt as
`navigator_action_before_row_correction`.

## Arm context

The capture arm itself (`nav-oracle-01`, build229, `COTM_GL_ERROR_IGNORE=0`,
`T2_TEXTURE_BUDGET_MIB=300`, diagnostic 32 MiB floor) presented **30 frames, 27 with
pixels**, then stopped at `T2_MEMORY_FLOOR` with no cleanup errors and verified run
identity. No input was injected in this arm: the oracle was measured, not driven.

## Verification

**188 host tests PASS** (8 oracle tests over self-authored frames + 10 navigator
tests, now carrying the measured rows). Thresholds are calibrated on one real frame
of this build and are therefore titled as such; a different build or scale needs a
new measurement, not new guesses.

## Still open

- One real press→serial→row chain (press, then a *later* frame showing row
  `newgame`) is not yet captured; this arm only proves the reading side.
- `NEWGAME_CONFIG`, `CONTROLS` and `LOADING` have no measured features yet, so the
  oracle returns `UNKNOWN` for them by design.
- No scene, id295, memory or FPS claim follows from this component.

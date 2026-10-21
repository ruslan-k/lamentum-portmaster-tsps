# P0-N2: navigator direction, overshoot refusal and double-frame confirm

Owner roadmap **§40.3** (P0-N2). Pure host work: no device run, no build.

## Contract now implemented in `tools/navigator.py`

| rule (owner §40.3) | implementation |
|---|---|
| 1. explicit `IDLE → ACTION_ISSUED → AWAIT_NEW_PRESENT → DONE/REFUSED`; a press is not an observation | `state` field on every event; a second press is only issued after a strictly newer frame, otherwise `wait`, then `refuse` after 3 repeats |
| 2. direction from ordered row indices | `direction_to()`: `load→newgame` is **down**, `credits/options→newgame` is **up** |
| 2. a multi-row move must refuse, not just emit a side event | default `recovery=False` → `refuse('one action moved 2 rows … overshoot, explicit recovery required')`, and no further press is issued |
| 3. explicit recovery releases and needs stable observations | `recovery=True` only for diagnostic arms: the overshoot is recorded, the **next** action is a single opposite-direction step, and nothing auto-confirms |
| 4. confirm only on two newer agreeing observations | first target-row frame → `wait`; second newer frame → `confirm`; the page after confirm must be `NEWGAME_CONFIG`, otherwise `refuse` |
| 4. a changed picture is not a page change | a non-menu page seen **without** a preceding confirm is refused; a menu still shown after confirm stays `wait` |
| 5. bounded short-press sweep | `nav_chain.SWEEP_MS = (80, 150, 250, 400)`; `TAP_MS` stays 350 |
| 6. pure tests for every listed case | 16 navigator tests + 8 chain tests, see below |

## Tests (owner §40.3 item 6, all present)

`load→options` overshoot refuses **and asserts exactly one press was issued**;
`options→newgame` uses `up`; single-row movement down; stale serial; repeated
same-frame polls; confirm acknowledgment by a second frame; wrong config page
refused; lagged/backwards serial refused; two identical animation frames never press;
first observed row already at `newgame` still needs two frames; no auto-confirm after
an overshoot.

**206 host tests PASS.** `nav_chain.summarise()` now *refuses* a two-row result
instead of reporting it as a qualified move.

## Not done here

No device press in this step, so the sweep has not run yet; the New Game
configuration page has no measured fingerprint (§40.4) and the menu-memory
waterfall (§40.5) is untouched. No scene, id295 or FPS claim.

# The menu ground truth, and why the first navigator opened Options

Roadmap §22.2/§22.3. Text below is read from live kmsgrab captures of build218's run
(`evidence/newgame-19`), not from a frame counter or a remembered default.

## Measured menu structure

Main menu (lower left, cursor is a diamond to the left of the row):

    Load game
    New game
    Options
    Credits

New game page:

    Limited save:  Yes  - "Classic, saves are limited by the amount of ink in your inventory."
    Difficulty:    Normal
    New game
    Return

Then a controls page: two Joy-Cons with AIM / WALK / SPRINT / MAP / INVENTORY /
ATTACK-USE ITEM / DODGE / X-Y-B SHORTCUT / A ACTION-OK / LOOK, and
"Press any button to continue."

## What went wrong in `newgame-19`

The navigator pressed `stick_down` once and then Confirm, accepting the step because the capture
changed. The screen it reached was the **Options** page (Language / Noise effect / Reading speed /
Rumble / SFX / BGM), where Confirm does not start a game: six Confirm presses produced 1-5 changed
cells each and nothing else. The captured page is in `crop-start.png`; the main menu capture that
proves the highlight was on "Load game" afterwards is `crop-menu-left.png`.

Root cause: "the screen changed" is not "the wanted entry is selected". At 1-2 frames/s a single
stick nudge can also be swallowed, so the tool cannot assume a starting row either.

## What replaced it

`tools/newgame_navigate.py` now anchors on the **bottom** of each list: it presses Down until the
capture stops changing, requires the number of moving steps to equal the pinned list length
(main menu 4, New game page 4), then walks Up a pinned number of rows (2 and 1 respectively) and
only then presses Confirm. Each Confirm still needs a real screen transition (>= 50 changed grid
cells). A list of a different length fails the run instead of confirming an unseen entry.

`rows_to_bottom()` is unit-tested for the moving-count, the repeat-at-bottom case and the
never-reaches-bottom case (56 host tests pass).

## Facts from the rest of that run

- No `ZERO_SHADER_UNRECOGNIZED` and no entry-45 link: the run never reached the load with the new
  fragment because it was parked on the Options page.
- After the harness bound expired, a stray Confirm landed on the Spruce menu and started the port
  once more; that instance stopped immediately with `STOP status=T2_MEMORY_FLOOR detail=0x49`
  at frame 4 (the previous run's memory had not been reclaimed). Recorded rather than hidden.
- Device afterwards: game absent, MainUI back, one `principal.sh`, CPU mask `0-7`, and a fresh
  kmsgrab showing a fully lit Spruce menu.

Entry 45 therefore remains **appended, built, deployed and not yet drawn**.

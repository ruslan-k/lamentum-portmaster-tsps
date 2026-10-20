#!/usr/bin/env python3
"""Drive Lamentum's New Game entry from live captures, never from an assumed highlight.

The measured ground truth (read from live KMS captures in evidence/newgame-19):

  main menu, top to bottom: Load game, New game, Options, Credits       (4 rows)
  New game page, top to bottom: Limited save, Difficulty, New game, Return (4 rows)
  then a controls page: "Press any button to continue."

Rather than trusting whichever row happens to be highlighted when the menu appears, the tool
anchors on the BOTTOM of each list: it presses Down until the capture stops changing, checks
that the number of moving steps matches the pinned list length, then walks Up a pinned number
of rows. A mismatch fails the run instead of confirming an unseen entry.

  python3 tools/newgame_navigate.py --evidence evidence/run-XX
"""
import argparse
import json
import sys
import time
from pathlib import Path

from PIL import Image

from lamentum_pad_contract import capture, press, snapshot

GRID = (64, 36)
DIFF_THRESHOLD = 10
MENU_TRANSITION_CELLS = 50      # a real screen change, not a cursor move
CURSOR_MOVE_CELLS = 2
MAX_ROWS = 8

# (rows in the list, rows to walk up from the bottom to reach the wanted entry)
MAIN_MENU = (4, 2)      # bottom = Credits, up 2 => New game
NEWGAME_PAGE = (4, 1)   # bottom = Return,  up 1 => New game


def grid(path):
    return list(Image.open(path).convert('L').resize(GRID).get_flattened_data())


def changed(a, b):
    return sum(abs(i - j) > DIFF_THRESHOLD for i, j in zip(a, b))


def cursor_row(png, x0=88, x1=124, y0=200, y1=700, threshold=110):
    """Measured highlight row: the bright band left of the menu labels, or None.

    Counting presses is not navigation at 1-2 fps (one press can move two rows and the
    animated background changes the picture), so the cursor band itself is the oracle.
    """
    im = Image.open(png).convert('L')
    px = im.load()
    rows = [y for y in range(y0, y1) if sum(1 for x in range(x0, x1) if px[x, y] > threshold) >= 2]
    if not rows:
        return None
    bands, current = [], [rows[0], rows[0]]
    for y in rows[1:]:
        if y <= current[1] + 3:
            current[1] = y
        else:
            bands.append(tuple(current))
            current = [y, y]
    bands.append(tuple(current))
    return min(bands, key=lambda b: b[0])


def rows_to_bottom(moves):
    """moves = per-press change counts; the last press repeated the previous row."""
    moving = 0
    for value in moves:
        if value < CURSOR_MOVE_CELLS:
            return moving
        moving += 1
    raise ValueError('the cursor never reached the bottom within %d presses' % len(moves))


def wait_for_menu(timeout_s=600):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        s = snapshot()
        if s['game'] and s['menu_events'] >= 4:
            return s
        time.sleep(10)
    raise RuntimeError('the title never announced its menu')


def press_capture(out, name, action, hold_ms, baseline, need):
    receipt = press(action, hold_ms)
    time.sleep(6)
    png = out / ('%s.png' % name)
    rec = capture(png)
    delta = changed(baseline, grid(png))
    record = {'name': name, 'action': action, 'hold_ms': hold_ms, 'changed_cells': delta,
              'need': need, 'capture_sha256': rec['sha256'], 'press': receipt,
              'frame': rec['after']['frame']}
    (out / ('%s.json' % name)).write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ('name', 'action', 'changed_cells', 'need', 'frame')}))
    if delta < need:
        raise RuntimeError('%s did not change the screen (need %d, got %d)' % (name, need, delta))
    return grid(png), record


def goto_row(out, prefix, baseline, rows, ups):
    """Anchor on the bottom of the list, then walk up to the wanted row."""
    moves = []
    current = baseline
    while len(moves) <= MAX_ROWS:
        name = '%s-down-%d' % (prefix, len(moves))
        receipt = press('down', 700)
        time.sleep(5)
        png = out / ('%s.png' % name)
        rec = capture(png)
        delta = changed(current, grid(png))
        moves.append(delta)
        (out / ('%s.json' % name)).write_text(json.dumps(
            {'name': name, 'changed_cells': delta, 'capture_sha256': rec['sha256'],
             'press': receipt, 'frame': rec['after']['frame']}, indent=2) + '\n')
        print(json.dumps({'name': name, 'changed_cells': delta}))
        if delta < CURSOR_MOVE_CELLS:
            break
        current = grid(png)
    found = rows_to_bottom(moves)
    if found + 1 != rows:
        raise RuntimeError('%s list length %d, expected %d' % (prefix, found + 1, rows))
    for i in range(ups):
        current, _ = press_capture(out, '%s-up-%d' % (prefix, i), 'up', 700, current, CURSOR_MOVE_CELLS)
    return current


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--menu-timeout', type=int, default=600)
    a = ap.parse_args()
    a.evidence.mkdir(parents=True, exist_ok=True)
    wait_for_menu(a.menu_timeout)
    capture(a.evidence / 'menu.png')
    base = grid(a.evidence / 'menu.png')
    base = goto_row(a.evidence, 'main', base, *MAIN_MENU)
    base, _ = press_capture(a.evidence, 'newgame-page', 'confirm', 1500, base, MENU_TRANSITION_CELLS)
    base = goto_row(a.evidence, 'page', base, *NEWGAME_PAGE)
    base, _ = press_capture(a.evidence, 'controls', 'confirm', 1500, base, MENU_TRANSITION_CELLS)
    base, _ = press_capture(a.evidence, 'loading', 'confirm', 1200, base, MENU_TRANSITION_CELLS)
    print(json.dumps({'reachable': True, 'phase': 'controls accepted; loading follows'}))


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Drive Lamentum's New Game entry from live captures, never from a frame counter.

Every Confirm is preceded by a fresh KMS capture and followed by one; a transition is
accepted only when the capture actually changed. A cursor step is accepted when the
capture changed at all. If a step does not change the screen the tool retries a bounded
number of times and then fails, so a run never records a "confirmed" state it did not see.

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


def grid(path):
    return list(Image.open(path).convert('L').resize(GRID).get_flattened_data())


def changed(a, b):
    return sum(abs(i - j) > DIFF_THRESHOLD for i, j in zip(a, b))


def wait_for_menu(timeout_s=600):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        s = snapshot()
        if s['game'] and s['menu_events'] >= 4:
            return s
        time.sleep(10)
    raise RuntimeError('the title never announced its menu')


def step(out, name, action, hold_ms, baseline, need, tries=3):
    """Press, capture, and require a minimum change; retry without exceeding the bound."""
    for attempt in range(tries):
        receipt = press(action, hold_ms)
        time.sleep(6)
        png = out / ('%s%s.png' % (name, '' if attempt == 0 else '-r%d' % attempt))
        rec = capture(png)
        delta = changed(baseline, grid(png))
        record = {'name': name, 'action': action, 'hold_ms': hold_ms, 'attempt': attempt,
                  'changed_cells': delta, 'need': need, 'capture_sha256': rec['sha256'],
                  'press': receipt, 'frame': rec['after']['frame']}
        (out / ('%s%s.json' % (name, '' if attempt == 0 else '-r%d' % attempt))).write_text(
            json.dumps(record, indent=2) + '\n')
        print(json.dumps({k: record[k] for k in ('name', 'action', 'attempt', 'changed_cells', 'need', 'frame')}))
        if delta >= need:
            return grid(png), record
        baseline = grid(png)
    raise RuntimeError('%s never changed the screen (last need=%d)' % (name, need))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--menu-timeout', type=int, default=600)
    a = ap.parse_args()
    a.evidence.mkdir(parents=True, exist_ok=True)
    wait_for_menu(a.menu_timeout)
    capture(a.evidence / 'menu.png')
    base = grid(a.evidence / 'menu.png')
    base, _ = step(a.evidence, 'selected', 'stick_down', 900, base, CURSOR_MOVE_CELLS)
    base, _ = step(a.evidence, 'config', 'confirm', 1500, base, MENU_TRANSITION_CELLS)
    for i in range(2):
        base, _ = step(a.evidence, 'cfg-down-%d' % i, 'down', 700, base, CURSOR_MOVE_CELLS)
    base, _ = step(a.evidence, 'start', 'confirm', 1500, base, MENU_TRANSITION_CELLS)
    base, _ = step(a.evidence, 'controls', 'confirm', 1000, base, MENU_TRANSITION_CELLS)
    print(json.dumps({'reachable': True, 'phase': 'controls confirmed; loading follows'}))


if __name__ == '__main__':
    sys.exit(main())

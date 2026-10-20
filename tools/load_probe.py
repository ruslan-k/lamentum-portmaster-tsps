#!/usr/bin/env python3
"""Bounded load probe: reach New Game, then sample memory/frames/shaders every few seconds.

Navigation uses the measured cursor row (x 88..124 band) for the main menu and a bright-pixel
jump for the page -> controls transition, so a wrong screen fails the probe instead of being
reported as progress. Metrics are sampled from the device only (no runtime change):

  MemAvailable / MemFree / SwapFree / CmaFree, presented frames, ROMFS reads,
  NVN_TEXTURE_REAL / LC2_BC_DEFERRED / LC2_BC_FILEBACK counters, Mali-adjacent RSS.

  python3 tools/load_probe.py --evidence evidence/load-probe-01 --budget 900
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from lamentum_pad_contract import capture, press, remote, snapshot
from load_metrics import PAYLOAD as METRICS_RUNNER, fold
from newgame_navigate import changed, cursor_row, grid

NEWGAME_ROW_Y = (475, 503)
CONTROLS_CHANGE_CELLS = 120      # a real content change, not a value toggle or a cursor move
POLL_S = 5

def bright(png):
    """Count lit samples on a 320x180 grid (same sampling as the 4-pixel step used before)."""
    im = Image.open(png).convert('L').resize((320, 180))
    return sum(1 for value in im.get_flattened_data() if value > 110)

def wait_menu(timeout_s):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        s = snapshot()
        if s['game'] and s['menu_events'] >= 4:
            return s
        time.sleep(8)
    raise RuntimeError('menu never appeared')

def pick_action(row, target=NEWGAME_ROW_Y):
    """None means 'the cursor is not visible yet - wait', never a blind nudge."""
    if row is None:
        return None
    if row[0] < target[0]:
        return 'down'
    if row[0] > target[1]:
        return 'up'
    return 'here'

def wait_menu_visible(out, timeout_s=300, name='menu'):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        capture(out / ('%s.png' % name))
        row = cursor_row(out / ('%s.png' % name))
        if row is not None:
            return row
        time.sleep(8)
    raise RuntimeError('no cursor band appeared within %d s' % timeout_s)

def walk_to(out, name, action='down', tries=10, hold_ms=1000):
    """Press until the cursor reaches the New game row, verified by the measured band.

    A press can be swallowed at 1-2 guest frames/s: measured, four 700 ms presses left the
    cursor on "Load game". The loop therefore counts ATTEMPTS, not assumed row steps, keeps a
    hold longer than one measured guest frame interval, and re-reads the cursor after each one.
    """
    png = out / ('%s.png' % name)
    for attempt in range(tries):
        row = cursor_row(png) if png.exists() else None
        if row and NEWGAME_ROW_Y[0] <= row[0] <= NEWGAME_ROW_Y[1]:
            return row
        direction = pick_action(row) or action
        if direction == 'here':
            return row
        press(direction, hold_ms)
        time.sleep(5)
        capture(png)
        (out / ('%s-%d.json' % (name, attempt))).write_text(
            json.dumps({'attempt': attempt, 'action': direction, 'row': cursor_row(png)}, indent=2) + '\n')
    row = cursor_row(png) if png.exists() else None
    if not (row and NEWGAME_ROW_Y[0] <= row[0] <= NEWGAME_ROW_Y[1]):
        raise RuntimeError('could not select New game after %d presses; measured row %r' % (tries, row))
    return row

def navigate(out):
    wait_menu(600)
    row = wait_menu_visible(out)
    walk_to(out, 'selected')
    press('confirm', 1500)
    time.sleep(8)
    capture(out / 'page.png')
    page_bright = bright(out / 'page.png')
    for i in range(2):
        press('down', 700)
        time.sleep(4)
    # Leave the configuration page. Neither brightness nor the cursor band classifies the controls
    # screen reliably (measured: 382, 600 and 1187 lit samples; a bright band is present on both),
    # so gate on a large CONTENT change with bounded retries instead of on a screen heuristic.
    page_grid = grid(out / 'page.png')
    for attempt in range(4):
        press('confirm', 1500)
        time.sleep(9)
        png = out / ('controls%s.png' % ('' if attempt == 0 else '-r%d' % attempt))
        capture(png)
        delta = changed(page_grid, grid(png))
        (out / ('controls%s.json' % ('' if attempt == 0 else '-r%d' % attempt))).write_text(
            json.dumps({'attempt': attempt, 'changed_cells': delta, 'need': CONTROLS_CHANGE_CELLS},
                       indent=2) + '\n')
        print(json.dumps({'step': 'leave-page', 'attempt': attempt, 'changed_cells': delta}))
        if delta >= CONTROLS_CHANGE_CELLS:
            break
    else:
        raise RuntimeError('the configuration page never changed after 4 Confirm presses '
                           '(need %d cells)' % CONTROLS_CHANGE_CELLS)
    controls_bright = bright(png)
    press('confirm', 1200)
    time.sleep(8)
    capture(out / 'loading.png')
    return {'page_bright': page_bright, 'controls_bright': controls_bright}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--budget', type=int, default=900)
    ap.add_argument('--env', action='append', default=[])
    a = ap.parse_args()
    a.evidence.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, '-u', 'tools/device_principal_test.py', '--budget', str(a.budget),
            '--wait', str(a.budget + 80), '--evidence', str(a.evidence)]
    for e in a.env:
        argv += ['--env', e]
    harness = subprocess.Popen(argv, stdout=(a.evidence / 'harness.log').open('w'), stderr=subprocess.STDOUT)
    transitions = {'navigate': 'pending'}
    try:
        transitions = navigate(a.evidence)
        (a.evidence / 'transitions.json').write_text(json.dumps(transitions, indent=2) + '\n')
        rows = []
        running = {}
        while harness.poll() is None:
            try:
                # Incremental: the device sends only the bytes appended since the last poll.
                offset = running.get('offset', 0)
                sample = remote("import sys\nsys.argv=['probe','%d']\n" % offset + METRICS_RUNNER)
                running = fold(running, sample)
                rows.append(dict(running, t=round(time.time(), 1)))
            except Exception as exc:                     # device busy or SSH hiccup: keep the series
                rows.append({'error': str(exc), 't': round(time.time(), 1)})
            (a.evidence / 'samples.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            time.sleep(POLL_S)
    finally:
        # Record the navigation outcome BEFORE blocking on the harness, so an aborted probe
        # still leaves its reason on disk instead of an empty evidence directory.
        (a.evidence / 'transitions.json').write_text(json.dumps(transitions, indent=2) + '\n')
        rc = harness.wait()
        print(json.dumps({'harness_rc': rc, 'transitions': transitions}))

if __name__ == '__main__':
    sys.exit(main())

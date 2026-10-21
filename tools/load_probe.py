#!/usr/bin/env python3
"""Legacy bounded load probe; disabled by default pending a semantic page oracle.

This explicit diagnostic opt-in does NOT qualify T1 or a game phase.
Navigation uses the measured cursor row for the main menu and a bounded content-change gate
for the configuration transition. Content change alone does not prove the controls-screen identity;
page-specific semantic navigation validation remains open. Metrics are sampled from the device
(no runtime change):

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

from lamentum_pad_contract import capture, press, remote, snapshot, set_expected_owner
from load_metrics import collector_request, fold
from proc_metrics import sample_request
from newgame_navigate import changed, cursor_row, grid

NEWGAME_ROW_Y = (475, 503)
CONTROLS_CHANGE_CELLS = 120      # a real content change, not a value toggle or a cursor move
POLL_S = 5

def wait_owned_start(out, harness, timeout_s=90):
    """Attach only to the principal UUID and a live post-exec dev/inode match."""
    deadline = time.monotonic()+timeout_s
    while harness.poll() is None and time.monotonic() < deadline:
        path = out / 'expected-run.json'
        if not path.is_file():
            time.sleep(1)
            continue
        try:
            expected = json.loads(path.read_text())
        except json.JSONDecodeError:
            time.sleep(1)
            continue
        sample = remote(collector_request(expected_run=expected))
        if sample.get('status') != 'ok':
            time.sleep(1)  # stale pre-launch latest.log is never consumed
            continue
        state = fold(None, sample)
        if not state.get('log_identity_qualified'):
            time.sleep(1)
            continue
        header = state['run_header']
        owner = {key: header[key] for key in ('boot_id', 'pid', 'starttime', 'elf_dev', 'elf_ino')}
        process = remote(sample_request(expected=owner))
        if process.get('running'):
            set_expected_owner(owner)
            return state
        time.sleep(1)
    if harness.poll() is not None:
        return None
    raise RuntimeError('owned header/executable attachment timed out')

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
    ap.add_argument('--allow-unverified-navigation', action='store_true',
                    help='diagnostic only: legacy config/controls oracle is not phase-qualified')
    a = ap.parse_args()
    if not a.allow_unverified_navigation:
        ap.error('legacy navigation is disabled until a semantic page-state oracle is verified')
    a.evidence.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, '-u', 'tools/device_principal_test.py', '--budget', str(a.budget),
            '--wait', str(a.budget + 80), '--evidence', str(a.evidence)]
    for e in a.env:
        argv += ['--env', e]
    with (a.evidence / 'harness.log').open('w') as harness_log:
        harness = subprocess.Popen(argv, stdout=harness_log, stderr=subprocess.STDOUT)
    transitions: dict = {'navigate': 'pending'}
    try:
        running = wait_owned_start(a.evidence, harness)
        if running is None:
            transitions = {'navigate': 'not started; harness exited before owned attachment'}
            return harness.wait()
        transitions = navigate(a.evidence)
        (a.evidence / 'transitions.json').write_text(json.dumps(transitions, indent=2) + '\n')
        rows = []
        while harness.poll() is None:
            try:
                # Incremental: the device sends only the bytes appended since the last poll.
                sample = remote(collector_request(running))
                running = fold(running, sample)
                rows.append(dict(running, t=round(time.time(), 1)))
            except RuntimeError as exc:
                transitions['observer_error'] = str(exc)
                raise  # never resume counters after a log-generation failure
            except Exception as exc:                     # transport gap: preserve baseline, not a reset
                rows.append({'error': str(exc), 't': round(time.time(), 1)})
            (a.evidence / 'samples.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            time.sleep(POLL_S)
    finally:
        # Record the navigation outcome BEFORE blocking on the harness, so an aborted probe
        # still leaves its reason on disk instead of an empty evidence directory.
        (a.evidence / 'transitions.json').write_text(json.dumps(transitions, indent=2) + '\n')
        rc = harness.wait()
        set_expected_owner(None)
        print(json.dumps({'harness_rc': rc, 'transitions': transitions}))
    return rc

if __name__ == '__main__':
    sys.exit(main())

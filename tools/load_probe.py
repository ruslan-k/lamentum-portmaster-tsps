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
from newgame_navigate import cursor_row

NEWGAME_ROW_Y = (475, 503)
CONTROLS_BRIGHT_JUMP = 400      # sampled bright pixels: page ~455, controls ~1400
POLL_S = 5

METRICS = '''import json,re
from pathlib import Path
mem={l.split(':')[0]:int(l.split()[1]) for l in Path('/proc/meminfo').read_text().splitlines() if l.split(':')[0] in
     ('MemTotal','MemFree','MemAvailable','SwapFree','CmaFree')}
t=Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log').read_text(errors='replace')
frames=re.findall(r'NVN_PRESENT_PIXELS frame=(\\d+)',t)
print(json.dumps({'mem':mem,'frame':int(frames[-1]) if frames else None,
 'presents':len(frames),'romfs':t.count('ROMFS_READ'),'textures':t.count('NVN_TEXTURE_REAL'),
 'bc_deferred':t.count('LC2_BC_DEFERRED'),'bc_fileback':t.count('LC2_BC_FILEBACK'),
 'stops':re.findall(r'STOP status=\\S+',t)[-3:],'killed':'Killed' in t,
 'entry45':t.count('sources=0/45'),'unknown':len(re.findall(r'ZERO_SHADER_UNRECOGNIZED',t))}))
'''


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


def walk_to(out, name, action, tries=4):
    """Press until the cursor row reaches NEW GAME, verified by the measured band."""
    for i in range(tries):
        row = cursor_row(out / ('%s.png' % name)) if (out / ('%s.png' % name)).exists() else None
        if row and NEWGAME_ROW_Y[0] <= row[0] <= NEWGAME_ROW_Y[1]:
            return row
        press(action, 700)
        time.sleep(5)
        capture(out / ('%s.png' % name))
    row = cursor_row(out / ('%s.png' % name))
    if not (row and NEWGAME_ROW_Y[0] <= row[0] <= NEWGAME_ROW_Y[1]):
        raise RuntimeError('could not select New game; measured row %r' % (row,))
    return row


def navigate(out):
    wait_menu(600)
    row = wait_menu_visible(out)
    action = pick_action(row)
    if action in (None, 'here'):
        action = 'down'
    walk_to(out, 'selected', action)
    press('confirm', 1500)
    time.sleep(8)
    capture(out / 'page.png')
    page_bright = bright(out / 'page.png')
    for i in range(2):
        press('down', 700)
        time.sleep(4)
    press('confirm', 1500)
    time.sleep(9)
    capture(out / 'controls.png')
    controls_bright = bright(out / 'controls.png')
    if controls_bright - page_bright < CONTROLS_BRIGHT_JUMP:
        raise RuntimeError('page -> controls transition not observed (%d -> %d)' % (page_bright, controls_bright))
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
        while harness.poll() is None:
            try:
                rows.append(dict(remote(METRICS), t=round(time.time(), 1)))
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

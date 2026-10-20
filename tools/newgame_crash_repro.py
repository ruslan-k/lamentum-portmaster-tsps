#!/usr/bin/env python3
"""Reproduce the New Game crash and capture its cause.

Measured selection order at menu open: the cursor starts on **New game** (an Up press
moves it to Load game), so a single Accept (A) starts a new game. Earlier probes pressed
Up first and then Accept on Load game, which is why they never left the menu.

The run watches for a guest stop (STOP status=...), a vanished process, or a kernel
segfault, keeps the port log at the moment of failure, and captures the panel every few
seconds so the last visible state is preserved.

  python3 tools/newgame_crash_repro.py <env.json> <evidence-dir>
"""
import json
import os
import pathlib
import re
import subprocess
import sys
from lamentum_pad_contract import ACTIONS, CONFIRM, press as pad_press
import time

REPO = pathlib.Path('/home/ruslan/lamentum-work/repo')
OUT = REPO / 'evidence' / sys.argv[2]
PORT = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'
HOST = 'root@192.168.50.135'
ENV = json.loads(pathlib.Path(sys.argv[1]).read_text())
BUDGET = int(os.environ.get('LAMENTUM_CRASH_BUDGET', '420'))
CONFIRM_MS = int(os.environ.get('LAMENTUM_CONFIRM_MS', '700'))
NAV_MS = int(os.environ.get('LAMENTUM_NAV_MS', '700'))


def ssh(cmd, timeout=60, data=None):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          input=data, capture_output=True, timeout=timeout)


def shot(name):
    remote = f'{PORT}/{name}.png'
    r = ssh(f'/mnt/SDCARD/spruce/bin64/kmsgrab {remote}')
    (OUT / f'{name}.txt').write_bytes(r.stdout + r.stderr)
    if r.returncode == 0:
        (OUT / f'{name}.png').write_bytes(ssh(f'cat {remote}').stdout)


def press(t, code, value, hold_ms, label):
    action = next(k for k, v in ACTIONS.items() if v == (t, code, value))
    receipt = pad_press(action, hold_ms)
    receipt['label'] = label
    with (OUT / 'presses.jsonl').open('a') as f:
        f.write(json.dumps(receipt) + '\n')


def state():
    """Menu count, stop status, last frame and whether the game process still exists."""
    script = r'''import json,re,os
from pathlib import Path
log=Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')
t=log.read_text(errors='replace') if log.exists() else ''
frames=re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)',t)
stops=[l for l in t.splitlines() if 'STOP status=' in l]
menu=t.count('LC2_MENU_EVENT')
alive=0
for p in Path('/proc').iterdir():
    if p.name.isdigit():
        try:
            if (p/'comm').read_text().strip() in ('terminator2d-ne','lamentum-nextos'): alive+=1
        except OSError: pass
print(json.dumps({'menu':menu,'stops':stops[-2:],'frames':frames[-2:],'alive':alive,'bytes':len(t)}))
'''
    r = ssh('python3 -', data=script.encode())
    try:
        return json.loads(r.stdout.decode().strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {'menu': 0, 'stops': [], 'frames': [], 'alive': 0, 'bytes': 0}


def grab_log(tag):
    r = ssh(f'cat {PORT}/logs/latest.log')
    (OUT / f'latest-{tag}.log').write_bytes(r.stdout)
    r = ssh('dmesg | tail -40')
    (OUT / f'dmesg-{tag}.txt').write_bytes(r.stdout + r.stderr)


def main():
    if os.environ.get('LAMENTUM_ALLOW_LEGACY_AUTONAV') != '1':
        raise SystemExit('Legacy automatic selection is unverified. Use device_principal_test.py + lamentum_pad_contract.py with live screenshot review; see roadmap 20.2.')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    (OUT / 'probe.json').write_text(json.dumps({
        'confirm_hold_ms': CONFIRM_MS, 'budget_s': BUDGET,
        'intent': 'press Accept (A) on the measured default selection New game, no navigation',
        'input_source': 'evdev write to the real pad node'}, indent=2) + '\n')
    args = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
            '--budget', str(BUDGET), '--wait', str(BUDGET + 120), '--evidence', str(OUT)]
    for e in ENV:
        args += ['--env', e]
    harness = subprocess.Popen(args, cwd=str(REPO), stdout=(OUT / 'harness.log').open('w'),
                               stderr=subprocess.STDOUT)
    deadline = time.time() + BUDGET + 200
    shot('boot')
    started = crashed = False
    n = 0
    while time.time() < deadline and harness.poll() is None:
        time.sleep(8)
        s = state()
        if not started and s['menu'] > 0:
            shot('menu')
            # The title remembers the last highlighted entry across runs, so the cursor is not
            # reliably on New game. Walk to the top of the list, then one step down:
            # Up saturates on the first entry, so this is deterministic without reading pixels.
            for step in os.environ.get('LAMENTUM_NAV_SEQUENCE', 'up,up,up,up,down').split(','):
                step = step.strip()
                if step == 'up':
                    press(3, 17, -1, NAV_MS, 'nav-up')
                elif step == 'down':
                    press(3, 17, 1, NAV_MS, 'nav-down')
                time.sleep(1.5)
            shot('menu-after-nav')
            press(*CONFIRM, CONFIRM_MS, 'confirm-305')
            started = True
            time.sleep(6)
            shot('after-accept')
            continue
        if started:
            n += 1
            shot(f'post-{n:02d}')
            if s['stops'] or s['alive'] == 0:
                crashed = True
                grab_log('crash')
                shot('crash-state')
                print(json.dumps({'crashed': True, 'state': s}))
                break
            # The intro sequence waits for input between screens ('Press any button to
            # continue'); advance it so the run can reach the first playable scene.
            if os.environ.get('LAMENTUM_ADVANCE') == '1' and n % 2 == 0:
                press(*CONFIRM, 400, f'advance-{n}')
            if n >= 26:
                break
    if not crashed:
        grab_log('end')
    # The harness keeps watching for its own full budget; do not let that wait throw away
    # the crash evidence collected above (it did on newgame-crash-01).
    try:
        harness.wait(timeout=120)
    except subprocess.TimeoutExpired:
        harness.terminate()
        try:
            harness.wait(timeout=60)
        except subprocess.TimeoutExpired:
            harness.kill()
    print(json.dumps({'started': started, 'crashed': crashed, 'state': state(),
                      'harness_rc': harness.returncode}))


if __name__ == '__main__':
    main()

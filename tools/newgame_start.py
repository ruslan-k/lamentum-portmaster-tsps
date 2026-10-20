#!/usr/bin/env python3
"""Start a New Game on the device: wait for the guest's own menu event, move the
selection from the measured default (Options) to New game, confirm, then capture
the transition and the following scene.

The menu-ready signal is the title's own `LC2_MENU_EVENT` from the hash-pinned
ManagerMenuPrincipal trace, not a frame number: the earlier probe fired while the
loading screen was still up, so its 120 ms taps proved nothing.

  python3 tools/newgame_start.py <env.json> <evidence-dir>
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
BUDGET = int(os.environ.get('LAMENTUM_NEWGAME_BUDGET', '620'))
NAV_MS = int(os.environ.get('LAMENTUM_NAV_MS', '600'))
CONFIRM_MS = int(os.environ.get('LAMENTUM_CONFIRM_MS', '600'))
SETTLE_S = int(os.environ.get('LAMENTUM_SETTLE_S', '25'))


def ssh(cmd, timeout=60, data=None):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          input=data, capture_output=True, timeout=timeout)


def shot(name):
    remote = f'{PORT}/{name}.png'
    r = ssh(f'/mnt/SDCARD/spruce/bin64/kmsgrab {remote}')
    (OUT / f'{name}.txt').write_bytes(r.stdout + r.stderr)
    if r.returncode == 0:
        (OUT / f'{name}.png').write_bytes(ssh(f'cat {remote}').stdout)
        return True
    return False


def press(t, code, value, hold_ms, label):
    action = next(k for k, v in ACTIONS.items() if v == (t, code, value))
    receipt = pad_press(action, hold_ms)
    receipt['label'] = label
    with (OUT / 'presses.jsonl').open('a') as f:
        f.write(json.dumps(receipt) + '\n')


def log_tail():
    """Tail plus a persistent menu-event counter: the event scrolls out of a 4 KB tail
    within seconds at this log rate, which is why the previous attempt missed it."""
    tail = ssh(f'tail -c 4000 {PORT}/logs/latest.log').stdout.decode('utf-8', 'replace')
    count = ssh(f'grep -c LC2_MENU_EVENT {PORT}/logs/latest.log').stdout.decode().strip()
    return tail + '\nMENU_EVENT_COUNT=' + (count or '0')


def main():
    if os.environ.get('LAMENTUM_ALLOW_LEGACY_AUTONAV') != '1':
        raise SystemExit('Legacy automatic selection is unverified. Use device_principal_test.py + lamentum_pad_contract.py with live screenshot review; see roadmap 20.2.')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    (OUT / 'probe.json').write_text(json.dumps({
        'nav_hold_ms': NAV_MS, 'confirm_hold_ms': CONFIRM_MS, 'budget_s': BUDGET,
        'menu_signal': 'LC2_MENU_EVENT from the ManagerMenuPrincipal trace',
        'intent': 'Up once from the measured default selection (Options) to New game, then A',
        'input_source': 'evdev write to the real pad node; identical path to a human press'},
        indent=2) + '\n')
    args = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
            '--budget', str(BUDGET), '--wait', str(BUDGET + 120), '--evidence', str(OUT)]
    for e in ENV:
        args += ['--env', e]
    harness = subprocess.Popen(args, cwd=str(REPO), stdout=(OUT / 'harness.log').open('w'),
                               stderr=subprocess.STDOUT)
    deadline = time.time() + BUDGET + 180
    shot('boot')
    menu_seen = confirmed = False
    shots = 0
    while time.time() < deadline and harness.poll() is None:
        time.sleep(8)
        log = log_tail()
        if not menu_seen:
            if 'LC2_MENU_EVENT' in log or not log.rstrip().endswith('MENU_EVENT_COUNT=0'):
                menu_seen = True
                shot('menu-0')
                press(3, 17, -1, NAV_MS, 'up-to-new-game')
                time.sleep(4)
                shot('menu-1')
                press(*CONFIRM, CONFIRM_MS, 'confirm-305')
                time.sleep(6)
                shot('after-confirm')
                confirmed = True
            continue
        if confirmed:
            shots += 1
            shot(f'scene-{shots:02d}')
            time.sleep(SETTLE_S)
        if 'STOP status=' in log:
            break
    harness.wait(timeout=90)
    log = log_tail()
    shot('final')
    frames = [int(x) for x in re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', log)]
    print(json.dumps({'menu_seen': menu_seen, 'confirmed': confirmed, 'scene_shots': shots,
                      'last_frame': frames[-1] if frames else None,
                      'stopped': 'STOP status=' in log,
                      'harness_rc': harness.returncode}))


if __name__ == '__main__':
    main()

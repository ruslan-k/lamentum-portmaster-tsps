#!/usr/bin/env python3
"""Bounded New-game probe: reach the title menu, select New game, confirm with A,
then sample the resulting screen and memory until the run's own time limit.

All key presses are agent evdev injection into the real pad provider; the receipt
file says so explicitly. Screenshots come from kmsgrab on physical scanout.

  python3 tools/newgame_probe.py <env.json> <evidence-dir>
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
BUDGET = int(os.environ.get('LAMENTUM_NEWGAME_BUDGET', '600'))
NAV_HOLD_MS = int(os.environ.get('LAMENTUM_NAV_MS', '1000'))
CONFIRM_HOLD_MS = int(os.environ.get('LAMENTUM_CONFIRM_MS', '1200'))
MENU_FRAME = int(os.environ.get('LAMENTUM_MENU_FRAME', '400'))
SAMPLE_S = int(os.environ.get('LAMENTUM_SAMPLE_S', '30'))


def ssh(cmd, timeout=60, data=None):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          input=data, capture_output=True, timeout=timeout)


def shot(name):
    remote = f'{PORT}/{name}.png'
    r = ssh(f'/mnt/SDCARD/spruce/bin64/kmsgrab {remote}')
    (OUT / f'{name}.txt').write_bytes(r.stdout + r.stderr)
    ok = r.returncode == 0
    if ok:
        (OUT / f'{name}.png').write_bytes(ssh(f'cat {remote}').stdout)
    return ok


def sample(tag):
    """Read-only memory/process sample; one JSON line per sample."""
    script = '''import json,os,re,time
from pathlib import Path
info=dict()
for line in Path('/proc/meminfo').read_text().splitlines():
    k,v=line.split(':',1)
    if k in ('MemTotal','MemAvailable','SwapFree','Cached'): info[k]=int(v.split()[0])
names={}
rss=0
for p in Path('/proc').iterdir():
    if not p.name.isdigit(): continue
    try: comm=(p/'comm').read_text().strip()
    except OSError: continue
    if comm in ('lamentum-nextos','terminator2d-ne'):
        names[comm]=names.get(comm,0)+1
        for line in (p/'status').read_text().splitlines():
            if line.startswith('VmRSS:'): rss+=int(line.split()[1])
info['runtime_rss_kB']=rss; info['runtime_procs']=names
print(json.dumps(info))
'''
    r = ssh('python3 -', data=script.encode())
    line = r.stdout.decode().strip().splitlines()[-1] if r.stdout.strip() else '{}'
    with (OUT / 'memory.jsonl').open('a') as f:
        f.write(json.dumps({'t': time.strftime('%H:%M:%S'), 'tag': tag, 'sample': json.loads(line)}) + '\n')
    return line


def press(t, code, value, hold_ms):
    action = next(k for k, v in ACTIONS.items() if v == (t, code, value))
    receipt = pad_press(action, hold_ms)
    with (OUT / 'presses.jsonl').open('a') as f:
        f.write(json.dumps(receipt) + '\n')
    return receipt


def frames():
    log = ssh(f'tail -c 4000 {PORT}/logs/latest.log').stdout.decode('utf-8', 'replace')
    got = [int(x) for x in re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', log)]
    stopped = 'STOP status=' in log
    return (got[-1] if got else None), stopped, log


def main():
    if os.environ.get('LAMENTUM_ALLOW_LEGACY_AUTONAV') != '1':
        raise SystemExit('Legacy automatic selection is unverified. Use device_principal_test.py + lamentum_pad_contract.py with live screenshot review; see roadmap 20.2.')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    (OUT / 'probe.json').write_text(json.dumps({
        'menu_frame': MENU_FRAME, 'nav_hold_ms': NAV_HOLD_MS,
        'confirm_hold_ms': CONFIRM_HOLD_MS, 'budget_s': BUDGET,
        'intent': 'Up once from the measured default selection (Options) to New game, then A',
        'input_source': 'agent evdev injection, not a physical human press'}, indent=2) + '\n')
    args = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
            '--budget', str(BUDGET), '--wait', str(BUDGET + 120), '--evidence', str(OUT)]
    for e in ENV:
        args += ['--env', e]
    harness = subprocess.Popen(args, cwd=str(REPO), stdout=(OUT / 'harness.log').open('w'),
                               stderr=subprocess.STDOUT)
    deadline = time.time() + BUDGET + 180
    shot('before-title')
    sample('launch')
    navigated = confirmed = False
    last_sample = time.time()
    while time.time() < deadline and harness.poll() is None:
        time.sleep(8)
        frame, stopped, _ = frames()
        if time.time() - last_sample >= SAMPLE_S:
            sample(f'frame={frame}')
            last_sample = time.time()
        if frame is None:
            continue
        if not navigated and frame >= MENU_FRAME:
            shot('menu-before-nav')
            press(3, 17, -1, NAV_HOLD_MS)      # ABS_HAT0Y up: one measured step
            time.sleep(4)
            shot('menu-after-nav')
            navigated = True
        elif navigated and not confirmed:
            press(*CONFIRM, CONFIRM_HOLD_MS)  # measured Switch A / EV_KEY 305
            time.sleep(5)
            shot('after-confirm')
            confirmed = True
        elif confirmed:
            tag = f'gameplay-{int(time.time() % 100000)}'
            shot(tag)
            sample(f'frame={frame}')
            time.sleep(SAMPLE_S)
        if stopped:
            break
    harness.wait(timeout=90)
    frame, stopped, log = frames()
    shot('final')
    sample('end')
    print(json.dumps({'navigated': navigated, 'confirmed': confirmed,
                      'last_frame': frame, 'stopped': stopped,
                      'harness_rc': harness.returncode}))


if __name__ == '__main__':
    main()

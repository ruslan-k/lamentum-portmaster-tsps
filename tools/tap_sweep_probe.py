#!/usr/bin/env python3
"""Short-tap sweep: reach the title menu, then press direction keys for a short,
device-realistic duration and capture the screen after each tap.

Purpose: prove the pad latch. A human tap is ~60-150 ms; before the latch those
taps were shorter than one guest frame (~600 ms at the measured 1-2 fps) and were
never sampled, so the cursor never moved. Each tap is written to the real pad's
evdev node, which the adapter opens as a physical controller.

  python3 tools/tap_sweep_probe.py <env.json> <evidence-dir>
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path('/home/ruslan/lamentum-work/repo')
OUT = REPO / 'evidence' / sys.argv[2]
PORT = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'
HOST = 'root@192.168.50.135'
ENV = json.loads(pathlib.Path(sys.argv[1]).read_text())
BUDGET = int(os.environ.get('LAMENTUM_TAP_BUDGET', '480'))
TAP_MS = int(os.environ.get('LAMENTUM_TAP_MS', '120'))
MENU_FRAME = int(os.environ.get('LAMENTUM_MENU_FRAME', '400'))
# Linux evdev codes on the real pad; directions are the hat, confirm is BTN_SOUTH.
TAPS = [(3, 17, 1, 'down-1'), (3, 17, 1, 'down-2'), (3, 17, -1, 'up-1')]


def ssh(cmd, timeout=60, data=None):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          input=data, capture_output=True, timeout=timeout)


def shot(name):
    remote = f'{PORT}/{name}.png'
    r = ssh(f'/mnt/SDCARD/spruce/bin64/kmsgrab {remote}')
    (OUT / f'{name}.txt').write_bytes(r.stdout + r.stderr)
    if r.returncode == 0:
        (OUT / f'{name}.png').write_bytes(ssh(f'cat {remote}').stdout)


def tap(t, code, value, label, hold_ms):
    script = f'''import os,struct,time
f=os.open("/dev/input/event4",os.O_WRONLY)
e=lambda t,c,v:os.write(f,struct.pack("llHHi",0,0,t,c,v))
e({t},{code},{value});e(0,0,0);time.sleep({hold_ms/1000.0});e({t},{code},0);e(0,0,0);os.close(f)
'''
    r = ssh('python3 -', data=script.encode())
    with (OUT / 'taps.jsonl').open('a') as f:
        f.write(json.dumps({'label': label, 'code': code, 'value': value,
                            'hold_ms': hold_ms, 'rc': r.returncode,
                            'stderr': r.stderr.decode(errors='replace').strip()}) + '\n')
    time.sleep(2.5)  # let the guest present at least one frame


def frames():
    log = ssh(f'tail -c 4000 {PORT}/logs/latest.log').stdout.decode('utf-8', 'replace')
    got = [int(x) for x in re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', log)]
    return (got[-1] if got else None), log


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    (OUT / 'probe.json').write_text(json.dumps({
        'tap_ms': TAP_MS, 'taps': [t[3] for t in TAPS], 'menu_frame': MENU_FRAME,
        'budget_s': BUDGET,
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
    done = False
    while time.time() < deadline and harness.poll() is None:
        time.sleep(8)
        frame, log = frames()
        if done or frame is None or frame < MENU_FRAME:
            continue
        shot('menu-0')
        for t, code, value, label in TAPS:
            tap(t, code, value, label, TAP_MS)
            shot(f'menu-{label}')
            latch = [l for l in frames()[1].splitlines() if 'LC2_INPUT_LATCH' in l]
            if latch:
                (OUT / 'latch.txt').write_text('\n'.join(latch) + '\n')
        done = True
    harness.wait(timeout=90)
    frame, log = frames()
    print(json.dumps({'taps_done': done, 'last_frame': frame,
                      'stopped': 'STOP status=' in log, 'harness_rc': harness.returncode}))


if __name__ == '__main__':
    main()

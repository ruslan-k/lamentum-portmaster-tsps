#!/usr/bin/env python3
"""Bounded run that presses Start once the title screen is up, then captures both states."""
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path('/home/ruslan/lamentum-work/repo')
OUT = REPO / 'evidence' / 'title-input-02'
PORT = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'
HOST = 'root@192.168.50.135'
ENV = json.loads((REPO / 'evidence/lowfloor-32-01/env.json').read_text())
BUDGET = 520
PRESS_AFTER = 330          # measured: title logo present by ~300 s of runtime
KEY_MS = 140


def ssh(cmd, timeout=40):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          capture_output=True, timeout=timeout)


def shot(name):
    remote = f'{PORT}/{name}.png'
    r = ssh(f'/mnt/SDCARD/spruce/bin64/kmsgrab {remote}')
    (OUT / f'{name}.txt').write_bytes(r.stdout + r.stderr)
    if r.returncode == 0:
        (OUT / f'{name}.png').write_bytes(ssh(f'cat {remote}').stdout)
    return r.returncode == 0


PRESS = f'''import os,struct,time
f=os.open("/dev/input/event4",os.O_WRONLY)
e=lambda t,c,v:os.write(f,struct.pack("llHHi",0,0,t,c,v))
e(1,315,1);e(0,0,0);time.sleep({KEY_MS/1000.0});e(1,315,0);e(0,0,0)
os.close(f)
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    ssh(f'truncate -s 0 {PORT}/logs/latest.log')
    cmd = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
           '--budget', str(BUDGET), '--wait', str(BUDGET + 80), '--evidence', str(OUT)]
    for e in ENV:
        cmd += ['--env', e]
    harness = subprocess.Popen(cmd, cwd=str(REPO), stdout=(OUT / 'harness.log').open('w'),
                               stderr=subprocess.STDOUT)
    deadline = time.time() + BUDGET + 120
    shot('before-title')
    pressed = False
    while time.time() < deadline and harness.poll() is None:
        time.sleep(5)
        log = ssh(f'tail -c 2000 {PORT}/logs/latest.log').stdout.decode('utf-8', 'replace')
        frames = [int(x) for x in __import__('re').findall(r'NVN_PRESENT_PIXELS frame=(\d+)', log)]
        if not pressed and frames and frames[-1] >= 400:
            shot('at-title')
            for code,label in ((0x130,'a-south'),(0x13b,'start')):
                script=PRESS.replace('315',str(code))
                r = subprocess.run(['ssh', '-o', 'BatchMode=yes', HOST, 'python3 -'],
                                   input=script.encode(), capture_output=True, timeout=40)
                with (OUT / 'press.txt').open('a') as f:
                    f.write(f'{label} rc={r.returncode} {r.stdout.decode(errors="replace").strip()} {r.stderr.decode(errors="replace").strip()}\n')
                time.sleep(6)
                shot('after-' + label)
            pressed = True
        if 'STOP status=' in log:
            break
    harness.wait(timeout=60)
    print('pressed', pressed, 'harness', harness.returncode)


if __name__ == '__main__':
    main()

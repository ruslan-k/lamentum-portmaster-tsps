#!/usr/bin/env python3
"""Where does a Lamentum frame actually go: guest CPU, I/O wait, or paging?

Launches the port through the principal flow, then samples the runtime process
from /proc while it renders: per-thread CPU deltas, page-fault deltas, RSS/swap,
and the title's own NVN_PROFILE lines. Read-only; nothing is injected.

  python3 tools/perf_sample.py <env.json> <evidence-dir>
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
BUDGET = int(os.environ.get('LAMENTUM_PERF_BUDGET', '420'))
INTERVAL = float(os.environ.get('LAMENTUM_PERF_INTERVAL', '5'))

SAMPLE = r'''import json,os,time
from pathlib import Path
def rd(p):
    try: return Path(p).read_text()
    except OSError: return ''
pid=None
for d in Path('/proc').iterdir():
    if d.name.isdigit():
        try:
            if (d/'comm').read_text().strip() in ('lamentum-nextos','terminator2d-ne'):
                pid=d.name;break
        except OSError: pass
if not pid:
    print(json.dumps({'running':False}));raise SystemExit
base=Path('/proc')/pid
def cpu(stat):
    f=stat.split()
    return int(f[13])+int(f[14])
rows={'running':True,'pid':pid,'total_cpu_ticks':None,'threads':{},'minflt':0,'majflt':0,'rss_kb':0,'swap_kb':0,'state':'','wchan':''}
stat=rd(base/'stat')
if stat:
    f=stat.split()
    rows['state']=f[2];rows['minflt']=int(f[9]);rows['majflt']=int(f[11])
for t in (base/'task').iterdir():
    st=rd(t/'stat')
    if not st: continue
    name=rd(t/'comm').strip() or t.name
    f=st.split()
    rows['threads'][t.name]={'name':name,'cpu':cpu(st),'state':f[2],'minflt':int(f[9]),'majflt':int(f[11])}
for line in rd(base/'status').splitlines():
    if line.startswith('VmRSS:'): rows['rss_kb']=int(line.split()[1])
    elif line.startswith('VmSwap:'): rows['swap_kb']=int(line.split()[1])
rows['wchan']=rd(base/'wchan').strip()
print(json.dumps(rows))
'''


def ssh(cmd, timeout=60, data=None):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, cmd],
                          input=data, capture_output=True, timeout=timeout)


def sample():
    r = ssh('python3 -', data=SAMPLE.encode())
    try:
        return json.loads(r.stdout.decode().strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {'running': False}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'env.json').write_text(json.dumps(ENV, indent=2) + '\n')
    args = [sys.executable, str(REPO / 'tools/device_principal_test.py'),
            '--budget', str(BUDGET), '--wait', str(BUDGET + 120), '--evidence', str(OUT)]
    for e in ENV:
        args += ['--env', e]
    harness = subprocess.Popen(args, cwd=str(REPO), stdout=(OUT / 'harness.log').open('w'),
                               stderr=subprocess.STDOUT)
    deadline = time.time() + BUDGET + 150
    prev = None
    last_frame = None
    out = (OUT / 'perf.jsonl').open('w')
    while time.time() < deadline and harness.poll() is None:
        s = sample()
        log = ssh(f'tail -c 3000 {PORT}/logs/latest.log').stdout.decode('utf-8', 'replace')
        frames = [int(x) for x in re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', log)]
        frame = frames[-1] if frames else None
        rec = {'t': round(time.time(), 3), 'frame': frame, 'sample': s}
        cur = s if s.get('running') and s.get('threads') else None
        prv = prev if prev and prev.get('sample', {}).get('threads') else None
        if cur and prv:
            dt = rec['t'] - prv['t']
            dticks = sum(v['cpu'] for v in cur['threads'].values()) - \
                     sum(v['cpu'] for v in prv['sample']['threads'].values())
            rec['cpu_percent'] = round(100.0 * dticks / (dt * os.sysconf('SC_CLK_TCK')), 1)
            rec['minflt_per_s'] = int((cur['minflt'] - prv['sample']['minflt']) / dt)
            rec['majflt_per_s'] = int((cur['majflt'] - prv['sample']['majflt']) / dt)
            if frame is not None and last_frame is not None and frame > last_frame:
                rec['guest_frame_ms'] = round(1000.0 * dt / (frame - last_frame), 1)
            per = []
            for tid, v in cur['threads'].items():
                old = prv['sample']['threads'].get(tid)
                if old:
                    per.append({'tid': tid, 'name': v['name'],
                                'cpu_ms_per_s': round(1000.0 * (v['cpu'] - old['cpu']) / (dt * os.sysconf('SC_CLK_TCK')), 1),
                                'state': v['state']})
            per.sort(key=lambda r: -r['cpu_ms_per_s'])
            rec['top_threads'] = per[:6]
        if frame is not None:
            last_frame = frame
        out.write(json.dumps(rec) + '\n')
        out.flush()
        prev = rec
        time.sleep(INTERVAL)
    harness.wait(timeout=90)
    out.close()
    print(json.dumps({'harness_rc': harness.returncode, 'samples': sum(1 for _ in (OUT / 'perf.jsonl').open())}))


if __name__ == '__main__':
    main()

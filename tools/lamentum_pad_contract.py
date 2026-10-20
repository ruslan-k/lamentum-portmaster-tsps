#!/usr/bin/env python3
"""Owner-local TSPS control and live capture receipts (not physical human input)."""
import argparse
import json
import pathlib
import subprocess

CONFIRM = (1, 305, 1)
BACK = (1, 304, 1)
UP = (3, 17, -1)
DOWN = (3, 17, 1)
ACTIONS = dict(confirm=CONFIRM, back=BACK, up=UP, down=DOWN,
               stick_down=(3, 1, 32767), stick_up=(3, 1, -32767),
               stick_right=(3, 0, 32767), stick_left=(3, 0, -32767))
HOST = 'root@192.168.50.135'
PORT = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'


def remote(source, timeout=45):
    r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ControlMaster=no',
                        '-o', 'ConnectTimeout=10', HOST, 'python3 -'],
                       input=source, text=True, capture_output=True, timeout=timeout)
    r.check_returncode()
    return json.loads(r.stdout)


# Field 22 follows the last ')' of comm, which may itself contain spaces or ')'.
def parse_stat(text):
    end = text.rindex(')')
    fields = text[end + 2:].split()
    return {'pid': int(text[:text.index('(')].strip()), 'starttime': int(fields[19])}


def validate_cleanup(before, after):
    errors = []
    if after['game']:
        errors.append('game process remains')
    for key in ('MainUI', 'principal.sh', 'runtime.sh'):
        if len(after['processes'].get(key, [])) != 1:
            errors.append(key + ' count is not one')
    if before['online'] != after['online']:
        errors.append('CPU online mask not restored')
    for key in ('principal.sh', 'runtime.sh'):
        if before['processes'].get(key) != after['processes'].get(key):
            errors.append(key + ' identity changed')
    return errors


SNAPSHOT = '''from pathlib import Path
import json,re,hashlib
procs={}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   n=(p/'comm').read_text().strip()
   if n in ('MainUI','principal.sh','runtime.sh','terminator2d-ne','lamentum-nextos'):
    s=(p/'stat').read_text(); f=s[s.rindex(')')+2:].split()
    procs.setdefault(n,[]).append({'pid':int(p.name),'starttime':int(f[19])})
  except OSError:pass
port=Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch')
log=port/'logs/latest.log'
t=log.read_text(errors='replace') if log.exists() else ''
frames=re.findall(r'NVN_PRESENT_PIXELS frame=(\\d+)',t)
print(json.dumps({'processes':procs,'game':procs.get('terminator2d-ne',[])+procs.get('lamentum-nextos',[]),
 'online':Path('/sys/devices/system/cpu/online').read_text().strip(),
 'frame':int(frames[-1]) if frames else None,'menu_events':t.count('LC2_MENU_EVENT'),
 'stops':re.findall(r'STOP status=\\S+',t),'log_inode':log.stat().st_ino if log.exists() else None}))
'''


def snapshot():
    return remote(SNAPSHOT)


def press(action, hold_ms):
    if action not in ACTIONS or not 1 <= hold_ms <= 2000:
        raise ValueError('unknown action or unsafe hold')
    t, code, value = ACTIONS[action]
    return remote('''import os,struct,time,json
from pathlib import Path
nodes=[p for p in Path('/sys/class/input').glob('event*') if (p/'device/name').read_text().strip()=='TRIMUI Player1']
assert len(nodes)==1, 'pad identity is absent or ambiguous'
p=nodes[0]; path='/dev/input/'+p.name
caps={n:(p/'device/capabilities'/n).read_text().strip() for n in ('ev','key','abs')}
f=os.open(path,os.O_WRONLY); writes=[]
def emit(t,c,v):
 b=struct.pack('llHHi',0,0,t,c,v); n=os.write(f,b); writes.append(n); assert n==len(b)
start=time.monotonic_ns(); released=False
try:
 emit(%d,%d,%d);emit(0,0,0);time.sleep(%s)
finally:
 try:
  emit(%d,%d,0);emit(0,0,0);released=True
 finally: os.close(f)
print(json.dumps({'action':%r,'event_type':%d,'code':%d,'value':%d,'hold_ms':%d,
 'provider':path,'name':'TRIMUI Player1','capabilities':caps,'writes':writes,
 'start_ns':start,'end_ns':time.monotonic_ns(),'released':released,
 'source':'agent evdev injection, not a physical human press'}))
''' % (t, code, value, hold_ms / 1000, t, code, action, t, code, value, hold_ms))


def capture(out):
    before = snapshot()
    if len(before['game']) != 1 or before['processes'].get('MainUI'):
        raise RuntimeError('capture refused: no unique game or MainUI owns display')
    receipt = remote('''import subprocess,json,hashlib,base64
p='/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/live-receipt.png'
r=subprocess.run(['/mnt/SDCARD/spruce/bin64/kmsgrab',p],capture_output=True,text=True)
r.check_returncode()
b=open(p,'rb').read()
print(json.dumps({'kmsgrab':r.stdout+r.stderr,'sha256':hashlib.sha256(b).hexdigest(),'png':base64.b64encode(b).decode()}))
''')
    after = snapshot()
    if before['game'] != after['game'] or after['processes'].get('MainUI'):
        raise RuntimeError('capture refused: game identity changed during capture')
    import base64
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(receipt.pop('png')))
    receipt.update(before=before, after=after)
    out.with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['snapshot', 'capture'] + list(ACTIONS))
    ap.add_argument('--hold-ms', type=int, default=700)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    if args.action == 'capture':
        result = capture(args.out)
    else:
        result = snapshot() if args.action == 'snapshot' else press(args.action, args.hold_ms)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

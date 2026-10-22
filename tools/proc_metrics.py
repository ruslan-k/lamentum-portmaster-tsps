#!/usr/bin/env python3
"""Target-side proc snapshots and identity-safe CPU deltas (roadmap §26.2.5)."""
import inspect
from typing import Any


def parse_stat(text):
    """Linux proc_pid_stat: comm may contain spaces and parentheses; fields follow last ')'."""
    end = text.rindex(')')
    begin = text.index('(')
    fields = text[end + 1:].split()
    return {'pid': int(text[:begin].strip()), 'name': text[begin + 1:end],
            'state': fields[0], 'cpu': int(fields[11]) + int(fields[12]),
            'minflt': int(fields[7]), 'majflt': int(fields[9]), 'starttime': int(fields[19])}


def collect_proc(pid=None, expected=None, proc_root='/proc',
                 runtime_path='/mnt/SDCARD/Roms/PORTS/lamentum-switch/lamentum-nextos'):
    """Read one unique runtime or an explicitly pinned PID; never combine process generations."""
    import os
    import time
    from pathlib import Path

    root = Path(proc_root)
    started = time.monotonic()
    cpu_started = time.process_time_ns()
    boot = (root / 'sys/kernel/random/boot_id').read_text().strip()
    hz = os.sysconf('SC_CLK_TCK')

    def optional(path):
        try:
            return path.read_text().strip()
        except OSError:
            return None

    if expected is not None:
        pid = expected['pid']
    if pid is None:
        candidates = []
        runtime = Path(runtime_path).resolve()
        for directory in root.iterdir():
            if directory.name.isdigit() and optional(directory / 'comm') in ('lamentum-nextos', 'terminator2d-ne'):
                try:
                    # Resolve by filesystem identity: VFAT paths can differ in spelling/case
                    # while naming the exact same executable. Do not lowercase or trust comm.
                    if os.path.samefile(directory / 'exe', runtime):
                        candidates.append(int(directory.name))
                except OSError:
                    continue
        if len(candidates) != 1:
            return {'running': False, 'sample_status': 'absent' if not candidates else 'ambiguous',
                    'candidates': candidates, 'boot_id': boot, 'target_hz': hz}
        pid = candidates[0]
    base = root / str(pid)
    try:
        first = parse_stat((base / 'stat').read_text())
        sample_time = time.monotonic()
        identity = {'boot_id': boot, 'pid': int(pid), 'starttime': first['starttime']}
        if expected is not None and any(expected[k] != identity[k] for k in identity):
            return dict(identity, running=False, sample_status='identity_mismatch', target_hz=hz)
        if first['state'] in ('Z', 'X', 'x'):
            return dict(identity, running=False, sample_status='exited', target_hz=hz)
        try:
            executable=os.stat(base/'exe')
        except OSError as exc:
            return dict(identity,running=False,sample_status='unavailable',error=type(exc).__name__,target_hz=hz)
        identity.update(elf_dev=executable.st_dev,elf_ino=executable.st_ino)
        if expected is not None and any(expected.get(key)!=identity[key] for key in ('elf_dev','elf_ino') if key in expected):
            return dict(identity,running=False,sample_status='identity_mismatch',target_hz=hz)
        threads = {}
        for thread in (base / 'task').iterdir():
            try:
                row = parse_stat((thread / 'stat').read_text())
                sched = optional(thread / 'schedstat')
                row['schedstat'] = [int(x) for x in sched.split()[:3]] if sched else None
                if row['schedstat'] is not None and len(row['schedstat']) != 3:
                    row['schedstat'] = None
                row['wchan'] = optional(thread / 'wchan')
                # TID reuse during the individual read invalidates that thread's fields.
                last = parse_stat((thread / 'stat').read_text())
                if row['starttime'] == last['starttime']:
                    threads[thread.name] = row
            except (OSError, ValueError, IndexError):
                continue
        memory = {}
        for line in (base / 'status').read_text().splitlines():
            key = line.split(':')[0]
            if key in ('VmRSS', 'VmSwap'):
                memory[key] = int(line.split()[1])
        wchan = optional(base / 'wchan')
        last = parse_stat((base / 'stat').read_text())
        final_boot = (root / 'sys/kernel/random/boot_id').read_text().strip()
        if 'elf_ino' in identity:
            executable = os.stat(base / 'exe')
            if (executable.st_dev, executable.st_ino) != (identity['elf_dev'], identity['elf_ino']):
                return dict(identity, running=False, sample_status='changed_during_read', target_hz=hz)
        if last['starttime'] != first['starttime'] or final_boot != boot:
            return dict(identity, running=False, sample_status='changed_during_read', target_hz=hz)
        if last['state'] in ('Z', 'X', 'x'):
            return dict(identity, running=False, sample_status='exited', target_hz=hz)
        return dict(identity, running=True, sample_status='ok', target_hz=hz,
                    monotonic_s=sample_time, sample_duration_s=time.monotonic() - started,
                    collector_cpu_ns=time.process_time_ns() - cpu_started,
                    total_cpu_ticks=first['cpu'], minflt=first['minflt'], majflt=first['majflt'],
                    state=first['state'], wchan=wchan, threads=threads,
                    rss_kb=memory.get('VmRSS'), swap_kb=memory.get('VmSwap'))
    except (OSError, ValueError, IndexError) as exc:
        return {'running': False, 'sample_status': 'unavailable', 'error': type(exc).__name__,
                'pid': int(pid), 'boot_id': boot, 'target_hz': hz}


def sample_request(expected=None, pid=None):
    """Serialize the tested functions, not a separate hand-maintained parser mirror."""
    return ('import json\n' + inspect.getsource(parse_stat) + '\n' + inspect.getsource(collect_proc)
            + '\nprint(json.dumps(collect_proc(pid=%r, expected=%r)))\n' % (pid, expected))


def collect_memory_sample(expected, run_uuid, elf_sha256, sample_seq=0, proc_root='/proc'):
    """Lightweight, owner-pinned process/system memory snapshot; missing keys stay None."""
    import os
    import time
    from pathlib import Path

    root=Path(proc_root);pid=expected['pid'];base=root/str(pid)
    stamp=time.monotonic_ns();cpu_start=time.process_time_ns()
    boot=(root/'sys/kernel/random/boot_id').read_text().strip()
    def row(status, **extra):
        return {'run_uuid':run_uuid,'boot_id':boot,'pid':pid,'starttime':expected['starttime'],
                'elf_sha256':elf_sha256,'seq':sample_seq,'phase':'process-attach' if sample_seq==0 else 'sampling',
                't_monotonic_ns':stamp,'sample_status':status,'running':status=='ok',**extra}
    if boot!=expected['boot_id']:
        return row('identity_mismatch',reason='boot_id')
    try:
        first=parse_stat((base/'stat').read_text())
    except FileNotFoundError:
        return row('exited')
    except (OSError,ValueError,IndexError) as exc:
        return row('unavailable',error=type(exc).__name__)
    if first['starttime']!=expected['starttime'] or first['state'] in ('Z','X','x'):
        return row('exited' if first['state'] in ('Z','X','x') else 'identity_mismatch',reason='process_generation')
    try:
        exe=os.stat(base/'exe')
    except OSError as exc:
        return row('unavailable',error=type(exc).__name__)
    if any(expected.get(k)!=v for k,v in (('elf_dev',exe.st_dev),('elf_ino',exe.st_ino))):
        return row('identity_mismatch',reason='executable_inode')
    def read_text(path):
        try:return path.read_text()
        except OSError:return None
    def parse_values(text,keys,unit):
        parsed: dict[str,int|None]={key:None for key in keys}
        if text is None:return parsed
        wanted=set(keys)
        for line in text.splitlines():
            if ':' in line:
                key,tail=line.split(':',1);parts=tail.split()
                if key in wanted and parts and parts[0].isdigit() and (unit is None or len(parts)>1 and parts[1]==unit):
                    parsed[key]=int(parts[0])
            else:
                parts=line.split()
                if len(parts)>1 and parts[0] in wanted and parts[1].isdigit():parsed[parts[0]]=int(parts[1])
        return parsed
    def keyed(path,keys,unit):
        return parse_values(read_text(path),keys,unit)
    process=keyed(base/'status',('VmRSS','VmHWM','VmSwap','RssAnon','RssFile','RssShmem'),'kB')
    system=keyed(root/'meminfo',('MemTotal','MemAvailable','CmaFree','SwapTotal','SwapFree','Cached','AnonPages','Shmem','Slab'),'kB')
    vmstat=keyed(root/'vmstat',('pswpin','pswpout','pgfault','pgmajfault'),None)
    pressure_text=read_text(root/'pressure/memory');pressure_memory=pressure_text.strip() if pressure_text else None
    smaps={'status':'not-scheduled','read_duration_ns':None,'values_kib':{}}
    if sample_seq and sample_seq%40==39:
        smaps_start=time.monotonic_ns();text=read_text(base/'smaps_rollup');smaps_duration=time.monotonic_ns()-smaps_start
        if text is None:smaps={'status':'unavailable','read_duration_ns':smaps_duration,'values_kib':{}}
        else:smaps={'status':'ok','read_duration_ns':smaps_duration,
                    'values_kib':parse_values(text,('Rss','Pss','Pss_Anon','Pss_File','Pss_Shmem','Swap','SwapPss'),'kB')}
    try:
        last=parse_stat((base/'stat').read_text());final_boot=(root/'sys/kernel/random/boot_id').read_text().strip();after=os.stat(base/'exe')
    except (OSError,ValueError,IndexError) as exc:
        return row('changed_during_read',error=type(exc).__name__,process={k+'_kib':v for k,v in process.items()},
                   system={k+'_kib':v for k,v in system.items()},vmstat=vmstat,smaps_rollup=smaps)
    if (last['starttime']!=first['starttime'] or final_boot!=boot or
        (after.st_dev,after.st_ino)!=(exe.st_dev,exe.st_ino)):
        return row('changed_during_read',process={k+'_kib':v for k,v in process.items()},
                   system={k+'_kib':v for k,v in system.items()},vmstat=vmstat,smaps_rollup=smaps)
    return row('ok',sample_duration_ns=time.monotonic_ns()-stamp,
               collector_cpu_ns=time.process_time_ns()-cpu_start,
               process={k+'_kib':v for k,v in process.items()},system={k+'_kib':v for k,v in system.items()},
               vmstat=vmstat,pressure_memory=pressure_memory,smaps_rollup=smaps)


def collect_memory_system_sample(expected,run_uuid,elf_sha256,phase='prelaunch',proc_root='/proc'):
    """One device-timestamped prelaunch system sample; absent metrics remain None."""
    import time
    from pathlib import Path
    root=Path(proc_root);stamp=time.monotonic_ns();cpu_start=time.process_time_ns()
    try:boot=(root/'sys/kernel/random/boot_id').read_text().strip()
    except OSError as exc:
        return {'run_uuid':run_uuid,'boot_id':None,'pid':None,'starttime':None,'elf_sha256':elf_sha256,
                'elf_dev':expected.get('elf_dev'),'elf_ino':expected.get('elf_ino'),
                'phase':phase,'t_monotonic_ns':stamp,'sample_status':'unavailable','running':False,
                'error':type(exc).__name__}
    if boot!=expected['boot_id']:
        return {'run_uuid':run_uuid,'boot_id':boot,'pid':None,'starttime':None,'elf_sha256':elf_sha256,
                'elf_dev':expected.get('elf_dev'),'elf_ino':expected.get('elf_ino'),
                'phase':phase,'t_monotonic_ns':stamp,'sample_status':'identity_mismatch','running':False}
    def values(path,keys,unit):
        result: dict[str,int|None]={key:None for key in keys}
        try:text=path.read_text()
        except OSError:return result
        for line in text.splitlines():
            fields=line.replace(':',' ',1).split()
            if len(fields)<2 or fields[0] not in result or not fields[1].isdigit():continue
            if unit is not None and (len(fields)<3 or fields[2]!=unit):continue
            result[fields[0]]=int(fields[1])
        return result
    system=values(root/'meminfo',('MemTotal','MemAvailable','CmaFree','SwapTotal','SwapFree','Cached','AnonPages','Shmem','Slab'),'kB')
    vmstat=values(root/'vmstat',('pswpin','pswpout','pgfault','pgmajfault'),None)
    try:pressure=(root/'pressure/memory').read_text().strip() or None
    except OSError:pressure=None
    final_boot=(root/'sys/kernel/random/boot_id').read_text().strip()
    if final_boot!=boot:
        status='changed_during_read'
    elif system['MemTotal'] is None or system['MemAvailable'] is None:
        status='unavailable'
    else:status='ok'
    return {'run_uuid':run_uuid,'boot_id':boot,'pid':None,'starttime':None,'elf_sha256':elf_sha256,
            'elf_dev':expected.get('elf_dev'),'elf_ino':expected.get('elf_ino'),
            'phase':phase,'t_monotonic_ns':stamp,'sample_status':status,'running':False,
            'sample_duration_ns':time.monotonic_ns()-stamp,'collector_cpu_ns':time.process_time_ns()-cpu_start,
            'process':{key+'_kib':None for key in ('VmRSS','VmHWM','VmSwap','RssAnon','RssFile','RssShmem')},
            'system':{key+'_kib':value for key,value in system.items()},'vmstat':vmstat,
            'pressure_memory':pressure}


def system_memory_request(expected,run_uuid,elf_sha256,phase='prelaunch'):
    """Serialize the tested one-shot target-side system snapshot."""
    import re
    from run_identity import validate_uuid
    validate_uuid(run_uuid);validate_uuid(expected['boot_id'])
    if not re.fullmatch(r'[0-9a-f]{64}',elf_sha256):raise ValueError('invalid ELF SHA-256')
    source='import json,time\nfrom pathlib import Path\n'+inspect.getsource(collect_memory_system_sample)
    source+='\nprint(json.dumps(collect_memory_system_sample(%r,%r,%r,%r)))\n'%(expected,run_uuid,elf_sha256,phase)
    return source


def discover_memory_owner(expected,proc_root='/proc'):
    """Find the exact pinned executable once, or fail closed on reuse/ambiguity."""
    import os
    from pathlib import Path
    root=Path(proc_root)
    try:boot=(root/'sys/kernel/random/boot_id').read_text().strip()
    except OSError as exc:return {'status':'unavailable','error':type(exc).__name__}
    if boot!=expected['boot_id']:return {'status':'identity_mismatch','reason':'boot_id','boot_id':boot}
    pids=[expected['pid']] if 'pid' in expected else [int(p.name) for p in root.iterdir()
        if p.name.isdigit() and (root/p.name/'comm').exists()]
    matches=[]
    for pid in pids:
        base=root/str(pid)
        try:
            if 'pid' not in expected and (base/'comm').read_text().strip() not in ('lamentum-nextos','terminator2d-ne'):
                continue
            stat=parse_stat((base/'stat').read_text());exe=os.stat(base/'exe')
        except (OSError,ValueError,IndexError):continue
        if stat['state'] in ('Z','X','x'):continue
        if exe.st_dev!=expected['elf_dev'] or exe.st_ino!=expected['elf_ino']:continue
        identity={'status':'ok','boot_id':boot,'pid':int(pid),'starttime':stat['starttime'],
                  'elf_dev':exe.st_dev,'elf_ino':exe.st_ino}
        if 'starttime' in expected and identity['starttime']!=expected['starttime']:
            return dict(identity,status='identity_mismatch',reason='starttime')
        matches.append(identity)
    if len(matches)>1:return {'status':'ambiguous','boot_id':boot,'candidate_pids':[x['pid'] for x in matches]}
    if not matches:return {'status':'waiting','boot_id':boot}
    return matches[0]


def collect_memory_timeline(expected,run_uuid,elf_sha256,max_samples=120,interval_ms=100,proc_root='/proc'):
    """Bounded target-local sampler. It does no thread walk and stops on identity loss."""
    import time
    if type(max_samples) is not int or not 1<=max_samples<=256:raise ValueError('max_samples must be 1..256')
    if type(interval_ms) is not int or not 10<=interval_ms<=1000:raise ValueError('interval_ms must be 10..1000')
    owner=None;attach_deadline=time.monotonic()+5
    while time.monotonic()<attach_deadline:
        found=discover_memory_owner(expected,proc_root)
        if found['status']=='ok':owner={k:found[k] for k in ('boot_id','pid','starttime','elf_dev','elf_ino')};break
        if found['status'] not in ('waiting',):
            return {'schema_version':1,'run_uuid':run_uuid,'elf_sha256':elf_sha256,'identity':None,
                    'interval_ms':interval_ms,'sample_limit':max_samples,'sample_count':0,'dropped_samples':0,
                    'complete':False,'stop_reason':found['status'],'attach_error':found,'samples':[]}
        time.sleep(min(interval_ms/1000,0.1))
    if owner is None:
        return {'schema_version':1,'run_uuid':run_uuid,'elf_sha256':elf_sha256,'identity':None,
                'interval_ms':interval_ms,'sample_limit':max_samples,'sample_count':0,'dropped_samples':0,
                'complete':False,'stop_reason':'attach-timeout','samples':[]}
    start=time.monotonic_ns();period=interval_ms*1000000;samples=[];dropped=0;stop_reason='sample-limit'
    for seq in range(max_samples):
        due=start+seq*period;now=time.monotonic_ns()
        if now<due:time.sleep((due-now)/1000000000)
        sample=collect_memory_sample(owner,run_uuid,elf_sha256,seq,proc_root)
        samples.append(sample)
        if sample['sample_status']!='ok':
            stop_reason=sample['sample_status'];break
        end=time.monotonic_ns();next_due=start+(seq+1)*period
        if end>next_due:dropped+=(end-next_due)//period+1
    complete=stop_reason=='exited' and dropped==0
    return {'schema_version':1,'run_uuid':run_uuid,'elf_sha256':elf_sha256,'identity':owner,
            'interval_ms':interval_ms,'sample_limit':max_samples,'sample_count':len(samples),
            'dropped_samples':int(dropped),'complete':complete,'stop_reason':stop_reason,'samples':samples}


def memory_timeline_request(expected,run_uuid,elf_sha256,max_samples=120,interval_ms=100):
    """Build the exact tested target-side, bounded memory timeline payload."""
    import re
    from run_identity import validate_uuid
    validate_uuid(run_uuid)
    if not re.fullmatch(r'[0-9a-f]{64}',elf_sha256):raise ValueError('invalid ELF SHA-256')
    for key in ('boot_id','elf_dev','elf_ino'):
        if key not in expected:raise ValueError('missing executable identity: '+key)
    if ('pid' in expected)!=('starttime' in expected):raise ValueError('pid and starttime must be supplied together')
    validate_uuid(expected['boot_id'])
    if type(max_samples) is not int or not 1<=max_samples<=256:raise ValueError('max_samples must be 1..256')
    if type(interval_ms) is not int or not 10<=interval_ms<=1000:raise ValueError('interval_ms must be 10..1000')
    source='import json,os,time\nfrom pathlib import Path\n'+inspect.getsource(parse_stat)+'\n'+inspect.getsource(discover_memory_owner)+'\n'+inspect.getsource(collect_memory_sample)+'\n'+inspect.getsource(collect_memory_timeline)
    source+='\nprint(json.dumps(collect_memory_timeline(%r,%r,%r,%r,%r)))\n'%(expected,run_uuid,elf_sha256,max_samples,interval_ms)
    return source


def cpu_delta(previous, current) -> dict[str, Any]:
    """Use process total ticks (including exited threads), target HZ and target monotonic time."""
    if not previous or not previous.get('running') or not current.get('running'):
        return {'delta_status': 'no_live_pair'}
    if any(previous.get(k) != current.get(k) for k in ('boot_id', 'pid', 'starttime', 'target_hz', 'elf_dev', 'elf_ino')):
        return {'delta_status': 'identity_changed'}
    dt = current['monotonic_s'] - previous['monotonic_s']
    hz = current['target_hz']
    ticks = current['total_cpu_ticks'] - previous['total_cpu_ticks']
    if dt <= 0 or hz <= 0 or ticks < 0:
        return {'delta_status': 'invalid_clock_or_counter'}
    threads = []
    for tid, row in current['threads'].items():
        old = previous['threads'].get(tid)
        if not old or old['starttime'] != row['starttime'] or row['cpu'] < old['cpu']:
            continue
        item = {'tid': tid, 'name': row['name'], 'starttime': row['starttime'],
                'state': row['state'], 'wchan': row.get('wchan'),
                'cpu_ms_per_s': round(1000.0 * (row['cpu'] - old['cpu']) / (hz * dt), 3),
                'minflt_delta': row['minflt'] - old['minflt'],
                'majflt_delta': row['majflt'] - old['majflt']}
        if row.get('schedstat') is not None and old.get('schedstat') is not None:
            for index, key in enumerate(('run_ns', 'wait_ns', 'timeslices')):
                item[key] = row['schedstat'][index] - old['schedstat'][index]
        threads.append(item)
    threads.sort(key=lambda item: -item['cpu_ms_per_s'])
    return {'delta_status': 'ok', 'elapsed_s': dt,
            'cpu_percent': round(100.0 * ticks / (hz * dt), 3),
            'minflt_per_s': (current['minflt'] - previous['minflt']) / dt,
            'majflt_per_s': (current['majflt'] - previous['majflt']) / dt,
            'thread_deltas': threads, 'top_threads': threads[:6]}

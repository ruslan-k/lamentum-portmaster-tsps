"""Pair three storage bases from ONE owned run: declared payload, budget charge,
and the driver's gpu_memory counter.

Deliberate limits: declared/charged bytes are accounting figures, not measured
driver residency; gpu_memory's units are not verified against the driver source,
so no physical attribution is produced. A zero-argument reconciliation is not
evidence of memory being free.
"""
import argparse
import json
import re
from pathlib import Path


def _fields(line):
    return dict(re.findall(r'([A-Za-z0-9_-]+)=(\S+)', line))


def _owned(rows, run):
    """Keep only rows of the declared run and refuse a mixed or foreign series.

    An idle row (no pid) asserts nothing about ownership: it is outside the game
    window and must not be counted as either evidence or a mismatch.
    """
    key = ('run_uuid', 'pid', 'starttime', 'boot_id')
    seen = set()
    for row in rows:
        if row.get('pid') is None:
            continue
        if any(str(row.get(k)) != str(run[k]) for k in key):
            raise ValueError('foreign or mixed process identity in samples')
        seen.add(tuple(str(row.get(k)) for k in key))
    if not seen:
        raise ValueError('no samples')
    return rows


def reconcile(ledger_text, life_text, rows, run):
    rows = _owned(rows, run)
    game = [r for r in rows if r.get('game')]
    if not game:
        raise ValueError('no sample observed the game process')
    charge = [_fields(l) for l in ledger_text.splitlines() if l.startswith('LC2_MENU_LEDGER')]
    if not charge:
        raise ValueError('no menu-ledger line in this log')
    charge = charge[-1]
    life = [l for l in life_text.splitlines() if l.startswith('LC2_LIFE_SUMMARY')]
    if not life:
        raise ValueError('no life summary in this log')
    life = _fields(life[-1])
    declared_tex = int(life['tex-bytes'])
    declared_depth = int(life['rb-bytes'])
    charged_tex = int(charge['textures-charged-bytes'])
    charged_depth = int(charge['depth-estimate-bytes'])
    gpu = [r['gpu_memory'] for r in game if r.get('gpu_memory') is not None]
    if not gpu:
        raise ValueError('no gpu_memory reading during the game window')
    return {
        'declared': {'texture_bytes': declared_tex, 'depth_bytes': declared_depth,
                     'texture_mib': round(declared_tex / 2**20, 4),
                     'depth_mib': round(declared_depth / 2**20, 4),
                     'live_textures': int(life['tex-live']), 'live_depth': int(life['rb-live']),
                     'texture_over_charge': round(declared_tex / charged_tex, 4) if charged_tex else None},
        'charged': {'texture_bytes': charged_tex, 'depth_bytes': charged_depth,
                    'texture_mib': round(charged_tex / 2**20, 4),
                    'depth_mib': round(charged_depth / 2**20, 4),
                    'live_textures': int(charge['textures-live'])},
        'depth_agrees_exactly': declared_depth == charged_depth,
        'gpu_memory': {'min': min(gpu), 'max': max(gpu), 'samples': len(gpu),
                       'units_verified': False, 'scope': 'driver counter, unit not derived from source'},
        'physical_attribution': False,
        'notes': ['declared payload counts every requested texture level',
                  'budget charge is an accounting policy figure',
                  'gpu_memory may include alignment, tiling, aliases and non-texture storage'],
    }


def replay_texture_budget(log_text, expected_run):
    """Replay bounded, owned T2 deltas and the declared GL-storage set at its floor sample."""
    max_u64 = (1 << 64) - 1
    if not log_text.endswith('\n'):
        raise ValueError('incomplete final owned log record')
    lines = log_text.splitlines()
    headers = [line[len('LAMENTUM_RUN_HEADER '):] for line in lines
               if line.startswith('LAMENTUM_RUN_HEADER ')]
    if len(headers) != 1:
        raise ValueError('expected exactly one owned run header')
    try:
        header = json.loads(headers[0])
    except (ValueError, TypeError) as exc:
        raise ValueError('invalid owned run header') from exc
    for key in ('run_uuid', 'boot_id', 'pid', 'starttime', 'elf_sha256'):
        if key not in expected_run or str(header.get(key)) != str(expected_run[key]):
            raise ValueError('owned run identity mismatch: ' + key)
    run_uuid = str(expected_run['run_uuid'])

    floors = [_fields(line) for line in lines if line.startswith('LC2_TEXTURE_BUDGET_FLOOR ')]
    if len(floors) != 1 or floors[0].get('run-id') != run_uuid:
        raise ValueError('missing or foreign floor-budget snapshot')
    floor = floors[0]
    if floor.get('status') != 'sampled':
        raise ValueError('floor-budget snapshot unavailable')
    if int(floor.get('event-overflow', '-1')) != 0:
        raise ValueError('budget event overflow')
    sample_ns = int(floor['budget-sample-t-ns'])
    floor_check_ns = int(floor['floor-check-t-ns'])
    if sample_ns < floor_check_ns:
        raise ValueError('budget snapshot precedes floor check')

    budget_rows = []
    events_after_sample = 0
    last_event_ns = -1
    for line in lines:
        if not line.startswith('LC2_TEXTURE_BUDGET_EVENT '):
            continue
        row = _fields(line)
        if row.get('run-id') != run_uuid:
            raise ValueError('foreign budget event')
        t_ns = int(row['t-ns'])
        if t_ns < last_event_ns:
            raise ValueError('budget events are not monotonic')
        last_event_ns = t_ns
        if row.get('action') not in ('add', 'sub'):
            raise ValueError('unknown budget transition')
        delta = int(row['delta-bytes'])
        texture_id = row.get('texture-id')
        if not texture_id or int(texture_id) <= 0 or delta < 0 or delta > max_u64:
            raise ValueError('invalid budget owner or delta')
        if t_ns <= sample_ns:
            budget_rows.append(row)
        else:
            events_after_sample += 1
    if len(budget_rows) != int(floor['event-lines']):
        raise ValueError('budget event count does not match floor snapshot')

    live = peak = add_bytes = sub_bytes = charge_count = 0
    per_id = {}
    for row in budget_rows:
        texture_id = row['texture-id']
        delta = int(row['delta-bytes'])
        if row['action'] == 'add':
            if delta > max_u64-live or delta > max_u64-per_id.get(texture_id, 0):
                raise ValueError('budget arithmetic overflow')
            live += delta
            per_id[texture_id] = per_id.get(texture_id, 0) + delta
            add_bytes += delta
            charge_count += 1
            peak = max(peak, live)
        else:
            if delta > live or delta > per_id.get(texture_id, 0):
                raise ValueError('budget retirement underflow')
            live -= delta
            per_id[texture_id] -= delta
            sub_bytes += delta
        if live != int(row['live-bytes']) or charge_count != int(row['charge-count']):
            raise ValueError('budget event transition does not self-reconcile')
    if live != int(floor['live-bytes']) or peak != int(floor['peak-bytes']) or charge_count != int(floor['charge-count']):
        raise ValueError('budget replay differs from floor snapshot')

    pairs = {}
    for line in lines:
        if not line.startswith('LC2_TEXTURE_PAIR '):
            continue
        row = _fields(line)
        if row.get('run-id') != run_uuid:
            raise ValueError('foreign texture pair')
        if int(row['t-ns']) > sample_ns:
            continue
        texture_id = row['id']
        previous = pairs.get(texture_id)
        if previous and previous.get('object-generation') != row.get('object-generation'):
            raise ValueError('NVN object generation changed under one texture id')
        pairs[texture_id] = row
    active_ids = sorted((key for key, value in per_id.items() if value), key=int)
    pair_missing=[];pair_mismatches=[];guest_charge_mismatches=[]
    guest_bytes=pair_charge_bytes=0;budget_owners=set();no_gl=[]
    live_storage={}
    storage_events=[];delete_events=[];storage_after=delete_after=0
    def storage_identity(row):
        group_id=row.get('share-group-id')
        group_status=row.get('share-group','unverified')
        if group_id is None:
            if group_status!='unverified':raise ValueError('missing share-group identity')
            group_id='unverified'
        elif (group_status=='verified') != (group_id!='0'):
            raise ValueError('inconsistent share-group identity')
        return (group_id,row['owner'],row['gl-name'],row['kind'],row['storage-generation'])
    def subresource_identity(row):
        keys=('target','face','level','layer')
        if all(field in row for field in keys):
            return ('gl',row['target'].lower(),int(row['face']),int(row['level']),int(row['layer']))
        return ('legacy',row.get('subresource','unknown'))
    for line in lines:
        if line.startswith('LC2_GL_STORAGE_EVENT '):
            row=_fields(line)
            if row.get('run-id')!=run_uuid:raise ValueError('foreign GL storage event')
            t_ns=int(row['t-ns'])
            if t_ns>sample_ns:
                storage_after+=1;continue
            if row.get('status')!='recorded':raise ValueError('incomplete GL storage event')
            key=storage_identity(row)
            subresource=subresource_identity(row)
            amount=int(row['bytes']);total=int(row['total-bytes'])
            if amount>max_u64 or total>max_u64:raise ValueError('GL storage value overflow')
            current=live_storage.get(key)
            if row['event']=='allocate':
                if current is not None or amount!=total:raise ValueError('invalid GL storage allocation')
                updated={subresource:amount}
            elif row['event']=='extend':
                if current is None or subresource in current:raise ValueError('invalid GL storage extension')
                updated=dict(current);updated[subresource]=amount
            elif row['event']=='respec':
                if current is None or subresource not in current:raise ValueError('invalid GL storage redefinition')
                updated=dict(current);updated[subresource]=amount
            else:raise ValueError('unknown GL storage transition')
            live_bytes=sum(updated.values())
            if live_bytes>max_u64 or live_bytes!=total:raise ValueError('GL storage subresources do not match total')
            if 'subresource-count' in row and int(row['subresource-count'])!=len(updated):
                raise ValueError('GL storage subresource count mismatch')
            live_storage[key]=updated
            storage_events.append(row)
        elif line.startswith('LC2_GL_STORAGE_DELETE '):
            row=_fields(line)
            if row.get('run-id')!=run_uuid:raise ValueError('foreign GL storage delete')
            t_ns=int(row['t-ns'])
            if t_ns>sample_ns:
                delete_after+=1;continue
            if row.get('matched')!='1':raise ValueError('unmatched GL storage delete')
            key=storage_identity(row)
            current=live_storage.get(key)
            if current is None or sum(current.values())!=int(row['bytes']):
                raise ValueError('GL storage delete does not match current generation')
            if 'subresource-count' in row and int(row['subresource-count'])!=len(current):
                raise ValueError('GL storage delete subresource count mismatch')
            del live_storage[key]
            delete_events.append(row)
    gl_owners={key[1] for key in live_storage}
    for texture_id in active_ids:
        pair=pairs.get(texture_id)
        if pair is None:
            pair_missing.append(texture_id);continue
        net=per_id[texture_id]
        pair_charge=int(pair['charge-bytes'])
        pair_guest=int(pair['guest-bytes'])
        guest_bytes+=pair_guest;pair_charge_bytes+=pair_charge
        if pair_guest!=pair_charge:guest_charge_mismatches.append((texture_id,pair_guest,pair_charge))
        if pair_charge!=net:pair_mismatches.append((texture_id,pair_charge,net))
        owner=pair.get('storage-owner')
        if owner:budget_owners.add(owner)
        if owner not in gl_owners:no_gl.append(texture_id)
    if pair_missing or pair_mismatches:
        raise ValueError('live budget owners do not join to texture pairs')
    by_kind={};count_by_kind={}
    for (_,_,_,kind,_),subresources in live_storage.items():
        by_kind[kind]=by_kind.get(kind,0)+sum(subresources.values())
        count_by_kind[kind]=count_by_kind.get(kind,0)+1
    summaries=[_fields(line) for line in lines if line.startswith('LC2_LIFE_SUMMARY ')]
    if len(summaries)!=1:raise ValueError('expected one lifecycle summary')
    summary=summaries[0]
    summary_matches=None
    if not storage_after and not delete_after:
        summary_matches=(len(live_storage)==int(summary['live']) and
            sum(sum(subresources.values()) for subresources in live_storage.values())==int(summary['retained']) and
            count_by_kind.get('1',0)==int(summary['tex-live']) and
            by_kind.get('1',0)==int(summary['tex-bytes']) and
            count_by_kind.get('2',0)==int(summary['rb-live']) and
            by_kind.get('2',0)==int(summary['rb-bytes']) and
            int(summary['storage-event-overflow'])==0 and int(summary['delete-event-overflow'])==0)
        if not summary_matches:raise ValueError('replayed GL storage differs from stop summary')
    return {
        'status':'reconciled','run_uuid':run_uuid,
        'budget':{'floor_check_t_ns':floor_check_ns,'sample_t_ns':sample_ns,
            'floor_available_kib':int(floor['floor-available-kib']),
            'floor_swap_free_kib':int(floor['floor-swap-free-kib']),
            'live_bytes':int(floor['live-bytes']),'replay_bytes':live,'peak_bytes':peak,
            'charge_count':charge_count,'event_count':len(budget_rows),'event_overflow':int(floor['event-overflow']),
            'events_after_sample':events_after_sample,'add_bytes':add_bytes,'sub_bytes':sub_bytes,
            'live_ids':active_ids,'guest_bytes':guest_bytes,'pair_charge_bytes':pair_charge_bytes,
            'pair_charge_mismatches':pair_mismatches,'pair_guest_charge_mismatches':guest_charge_mismatches,
            'pair_missing_ids':pair_missing,
            'budget_without_gl_storage_ids':no_gl,
            'gl_without_budget_storage_owners':sorted(gl_owners-budget_owners,key=int)},
        'gl_storage':{'events':len(storage_events),'deletes':len(delete_events),
            'events_after_sample':storage_after,'deletes_after_sample':delete_after,
            'live_records':len(live_storage),'bytes_by_kind':by_kind,'records_by_kind':count_by_kind,
            'summary_matches':summary_matches},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--log', type=Path, required=True)
    p.add_argument('--samples', type=Path, required=True)
    p.add_argument('--harness', type=Path, required=True, help='harness.json of the same arm')
    a = p.parse_args()
    harness = json.loads(a.harness.read_text())
    expected = harness['expected_run']
    identity = harness['process_identity']
    run = {'run_uuid': expected['run_uuid'], 'boot_id': expected['boot_id'],
           'pid': identity['pid'], 'starttime': identity['starttime']}
    text = a.log.read_text(errors='replace')
    print(json.dumps(reconcile(text, text, json.loads(a.samples.read_text()), run), indent=2))


if __name__ == '__main__':
    main()

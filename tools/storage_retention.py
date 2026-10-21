"""Track same-context VA descriptors after a flushed log marker, not physical frees."""
from mali_allocs import ROW


def track(samples, *, marker_end, addresses):
    identity = context = log_identity = None
    previous_size = previous_time = -1
    observations = []
    for s in samples:
        owner = tuple(s[k] for k in ('run_uuid', 'boot_id', 'pid', 'starttime'))
        li = (s['log_before']['dev'], s['log_before']['ino'])
        if identity is None:
            identity, log_identity = owner, li
        if owner != identity or li != log_identity:
            raise ValueError('foreign process/run/log identity')
        size, stamp = s['log_before']['size'], s['t']
        if size < previous_size or stamp < previous_time:
            raise ValueError('log size or monotonic time went backwards')
        previous_size, previous_time = size, stamp
        if size < marker_end:
            continue
        contexts = s['driver']
        if len(contexts) != 1:
            raise ValueError('missing or ambiguous context')
        key = next(iter(contexts))
        if context is None:
            context = key
        if key != context or not key.startswith(str(s['pid'])+'_'):
            raise ValueError('context generation changed')
        text = contexts[key]['mem_allocs']
        if (not text.startswith('Zone name:') and not ROW.match(text)) or len(text) >= 1048576:
            raise ValueError('missing/truncated allocation metadata')
        rows = {m[1].lower(): int(m[3],16) for line in text.splitlines() if (m := ROW.fullmatch(line))}
        observations.append({'t':stamp,'log_bytes_before':size,'context':key,
                             'commits':{va:rows.get(va.lower()) for va in addresses}})
    return {'observations':observations,'physical_refund_bytes':None,
            'limitation':'Same VA may be recycled between samples; absence is not a fence/free/physical-refund proof.'}

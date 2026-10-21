#!/usr/bin/env python3
"""Byte-framed log metrics; strict owned-run mode refuses generation changes.

Legacy parsing remains explicitly unqualified for old evidence/tests. Production
probes must supply expected_run. Payload serializes the actual tested functions.
"""
import inspect
import json
import re
from run_identity import validate_uuid

CUMULATIVE = ('presents', 'romfs', 'textures', 'bc_deferred', 'bc_fileback', 'budget_adds')


def parse_chunk(chunk):
    """One complete-line chunk. Counters are neither CPU cost nor gameplay FPS."""
    import re
    counters = {
        'presents': len(re.findall(r'NVN_PRESENT_PIXELS frame=\d+', chunk)),
        'romfs': chunk.count('ROMFS_READ'),
        'textures': chunk.count('NVN_TEXTURE_REAL'),
        'bc_deferred': chunk.count('LC2_BC_DEFERRED'),
        'bc_fileback': chunk.count('LC2_BC_FILEBACK'),
        'budget_adds': len(re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+', chunk)),
    }
    frames = re.findall(r'NVN_PRESENT_PIXELS frame=(\d+)', chunk)
    stops = re.findall(r'STOP status=(\S+)', chunk)
    budget = re.findall(r'T2_TEXTURE_BUDGET add-bytes=\d+ live-MiB=\d+ count=\d+ budget-MiB=\d+', chunk)
    return {'counters': counters, 'frame': int(frames[-1]) if frames else None,
            'stops': stops[-3:], 'budget_last': budget[-1] if budget else None,
            'killed': 'Killed' in chunk}


def collect_log(path, offset=0, expected_identity=None, expected_run=None,
                expected_header=None, previous_anchor=None, max_bytes=262144, include_text=False):
    """Read an opened FD, UUID/header generation, and bounded cursor continuity.

    Header + last-256-byte anchor is an append-only writer contract, NOT a full
    cryptographic attestation of all old bytes against arbitrary in-place edits.
    A new launcher UUID/nonce is mandatory for every execution.
    """
    import hashlib
    import json
    import os
    import re

    if offset < 0 or max_bytes < 8192:
        raise ValueError('invalid log cursor/read bound')
    strict = expected_run is not None
    if strict:
        validate_uuid(expected_run['run_uuid'])
    with path.open('rb') as handle:
        stat = os.fstat(handle.fileno())
        identity, size = [stat.st_dev, stat.st_ino], stat.st_size
        rotated = offset > size or (expected_identity is not None and expected_identity != identity)
        result: dict = dict(parse_chunk(''), offset=offset, size=size, identity=identity, rotated=rotated,
                      strict=strict, status='ok', log_identity_qualified=False, run_header=None,
                      expected_run=expected_run, header_sha256=None, anchor=None)

        def reject(status, reason):
            result.update(status=status, reason=reason)
            return result

        header_blob, header = b'', None
        if strict:
            if rotated:
                return reject('LOG_GENERATION_CHANGED', 'opened-file identity or size changed')
            header_blob = handle.readline(8192)
            if not header_blob.endswith(b'\n'):
                if expected_header is not None:
                    return reject('LOG_GENERATION_CHANGED', 'previously owned header was truncated')
                return reject('LOG_HEADER_PENDING' if len(header_blob) < 8192 else 'LOG_HEADER_INVALID',
                              'complete bounded run header is not available')
            if expected_header is not None and hashlib.sha256(header_blob).hexdigest() != expected_header:
                return reject('LOG_GENERATION_CHANGED', 'previously owned header bytes changed')
            if not header_blob.startswith(b'LAMENTUM_RUN_HEADER '):
                return reject('LOG_HEADER_INVALID', 'owned header must be the first record')
            try:
                header = json.loads(header_blob[len(b'LAMENTUM_RUN_HEADER '):])
                if type(header.get('schema')) is not int or header['schema'] != 1:
                    raise ValueError('unsupported header schema')
                validate_uuid(header['run_uuid'])
                validate_uuid(header['launch_nonce'])
                validate_uuid(header['boot_id'])
                for key in ('pid', 'starttime', 'elf_dev', 'elf_ino'):
                    if type(header[key]) is not int or header[key] < (0 if key == 'elf_dev' else 1):
                        raise ValueError('invalid process/executable identity')
                for key in ('elf_sha256', 'launcher_sha256', 'helper_sha256'):
                    if not re.fullmatch(r'[0-9a-f]{64}', header[key]):
                        raise ValueError('invalid build identity')
            except (KeyError, ValueError, TypeError, AttributeError):
                return reject('LOG_HEADER_INVALID', 'run header fields are malformed')
            digest = hashlib.sha256(header_blob).hexdigest()
            if any(header.get(key) != value for key, value in expected_run.items()):
                return reject('LOG_GENERATION_CHANGED', 'expected owned run/build/process differs')
            if expected_header is not None and digest != expected_header:
                return reject('LOG_GENERATION_CHANGED', 'same-inode header generation changed')
            if offset and not previous_anchor:
                return reject('LOG_GENERATION_CHANGED', 'strict cursor has no continuity anchor')
            if previous_anchor:
                start, length = previous_anchor['offset'], previous_anchor['bytes']
                if length < 0 or length > 256 or start != offset-length or start < 0:
                    return reject('LOG_GENERATION_CHANGED', 'invalid cursor anchor shape')
                handle.seek(start)
                if hashlib.sha256(handle.read(length)).hexdigest() != previous_anchor['sha256']:
                    return reject('LOG_GENERATION_CHANGED', 'consumed cursor bytes were rewritten')
        elif rotated:
            offset = 0
            result['offset'] = 0
        # Preserve the pre-read tail to verify the new boundary after reading.
        tail_length = min(offset, 256)
        handle.seek(offset-tail_length)
        previous_tail = handle.read(tail_length)
        handle.seek(offset)
        raw = handle.read(min(max_bytes, max(0, size-offset)))
        complete = raw.rfind(b'\n') + 1
        if not complete and len(raw) == max_bytes:
            return reject('LOG_RECORD_TOO_LARGE', 'record exceeds bounded chunk')
        consumed = offset + complete
        if strict:
            found = re.findall(rb'(?m)^LAMENTUM_RUN_HEADER ', raw[:complete])
            if len(found) > (1 if offset == 0 else 0):
                return reject('LOG_GENERATION_CHANGED', 'another run header appeared in the body')
            handle.seek(0)
            if handle.readline(8192) != header_blob:
                return reject('LOG_GENERATION_CHANGED', 'header changed during read')
            expected_tail = (previous_tail + raw[:complete])[-min(consumed, 256):] if consumed else b''
            handle.seek(consumed-len(expected_tail))
            actual_tail = handle.read(len(expected_tail))
            if actual_tail != expected_tail:
                return reject('LOG_GENERATION_CHANGED', 'cursor boundary changed during read')
            result.update(log_identity_qualified=True, run_header=header,
                          header_sha256=hashlib.sha256(header_blob).hexdigest(),
                          anchor={'offset': consumed-len(actual_tail), 'bytes': len(actual_tail),
                                  'sha256': hashlib.sha256(actual_tail).hexdigest()})
        # Decode only complete BYTE-framed records; UTF-8 replacement never moves the cursor.
        result.update(parse_chunk(raw[:complete].decode('utf-8', 'replace')))
        result['offset'] = consumed
        result['unconsumed_bytes'] = size-consumed
        result['partial_bytes'] = len(raw)-complete
        if include_text:
            result['chunk_text'] = raw[:complete].decode('utf-8', 'replace')
        return result


PAYLOAD = ('import json, os, sys\nfrom pathlib import Path\n'
           + inspect.getsource(validate_uuid) + '\n' + inspect.getsource(parse_chunk) + '\n'
           + inspect.getsource(collect_log) + r'''
offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
expected_identity = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
path = Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')
sample = collect_log(path, offset, expected_identity, globals().get('_expected_run'),
                     globals().get('_expected_header'), globals().get('_previous_anchor'),
                     include_text=globals().get('_include_text', False))
mem = {}
for line in Path('/proc/meminfo').read_text().splitlines():
    key = line.split(':')[0]
    if key in ('MemTotal', 'MemFree', 'MemAvailable', 'SwapFree', 'CmaFree'):
        mem[key] = int(line.split()[1])
sample['mem'] = mem
print(json.dumps(sample))
''')


def fold(previous, sample) -> dict:
    """Reject cross-generation chunks; never silently reset strict owned totals."""
    if sample.get('strict') and sample.get('status') != 'ok':
        if sample['status'] == 'LOG_HEADER_PENDING':
            return dict(previous or {}, expected_run=sample['expected_run'],
                        log_identity_qualified=False, status='LOG_HEADER_PENDING')
        raise RuntimeError(sample['status'] + ': ' + sample.get('reason', 'invalid log identity'))
    identity_changed = (previous and previous.get('identity') is not None
                        and sample.get('identity') is not None
                        and previous['identity'] != sample['identity'])
    first_owned = sample.get('log_identity_qualified') and not (previous or {}).get('log_identity_qualified')
    base = {} if sample['rotated'] or identity_changed or first_owned else dict(previous or {})
    for key in CUMULATIVE:
        base[key] = base.get(key, 0) + sample['counters'].get(key, 0)
    base['frame'] = sample['frame'] if sample['frame'] is not None else base.get('frame')
    base['stops'] = (base.get('stops', []) + sample['stops'])[-3:]
    if sample.get('budget_last'):
        base['budget_last'] = sample['budget_last']
    base['killed'] = base.get('killed', False) or sample['killed']
    for key in ('mem', 'offset', 'size', 'identity', 'status', 'log_identity_qualified',
                'run_header', 'expected_run', 'header_sha256', 'anchor', 'partial_bytes', 'unconsumed_bytes'):
        base[key] = sample.get(key)
    return base


def collector_request(previous=None, *, expected_run=None, include_text=False):
    """Serialize owned identity + byte cursor into the exact tested remote payload."""
    previous = previous or {}
    if expected_run is None:
        expected_run = previous.get('expected_run')
    args = ['probe', str(previous.get('offset', 0)), json.dumps(previous.get('identity'))]
    context = {'_expected_run': expected_run, '_expected_header': previous.get('header_sha256'),
               '_previous_anchor': previous.get('anchor'), '_include_text': include_text}
    return ('import sys\nsys.argv=%r\n' % args
            + '\n'.join('%s=%r' % (key, value) for key, value in context.items()) + '\n' + PAYLOAD)


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], errors='replace') as handle:
        print(json.dumps(parse_chunk(handle.read()), indent=2))


# The port's own log path, in one place: reading a guessed sibling path yields a
# zero present counter and silently disables press qualification.
PORT_LOG = '/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log'
PRESENT_MARKER = 'NVN_PRESENT_PIXELS frame='


def present_serial(text):
    """Highest presented-frame counter in a runtime log, or 0 when none is present."""
    highest = 0
    for line in text.splitlines():
        if PRESENT_MARKER in line:
            tail = line.split(PRESENT_MARKER, 1)[1].split()
            if tail and tail[0].isdigit():
                highest = max(highest, int(tail[0]))
    return highest


def serial_request():
    """Remote snippet: print {"present_frames": N} read from PORT_LOG."""
    return ("import json,re,pathlib\n"
            "p=pathlib.Path(%r)\n"
            "text=p.read_text(errors='replace') if p.exists() else ''\n"
            "print(json.dumps({'present_frames': max([int(x) for x in re.findall(%r, text)] or [0])}))\n"
            % (PORT_LOG, PRESENT_MARKER + r"\d+"))

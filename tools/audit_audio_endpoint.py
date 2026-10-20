#!/usr/bin/env python3
"""Source/ELF-pinned audit of runtime endpoint tags and captured AudioOut IPC.

Compiles only the trusted adapter's C enum, not game code. Does not execute the ARM64 ELF,
contact a device, or infer CPU time / audibility from event counts.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def summarize_audio_log(text, *, manager, child):
    commands, managers, handles = Counter(), Counter(), set()
    requests = opens = malformed = host_rows = consumed = underrun = nonzero = 0
    # An incomplete trailing event is not a receipt.
    for line in text[:text.rfind('\n') + 1].splitlines():
        if re.fullmatch(r'GET_SERVICE name=audout:u(?:\s.*)?', line):
            requests += 1
        if line.startswith('AUDOUT_OPEN '):
            opens += 1
        fields = dict(re.findall(r'([A-Za-z0-9_-]+)=(\S+)', line))
        try:
            if line.startswith('IPC '):
                endpoint = int(fields['endpoint'], 0)
                command = int(fields['command'], 0)
                handle = int(fields['handle'], 0)
                if endpoint == child:
                    commands[str(command)] += 1
                    handles.add(hex(handle))
                elif endpoint == manager:
                    managers[str(command)] += 1
            elif line.startswith('AUDOUT_HOST_PROFILE ') and fields.get('scope') == 'interval':
                # consumed/underrun are interval deltas, nonzero-total is cumulative.
                a, b, c = (int(fields[k], 0) for k in ('consumed-frames', 'underrun-frames', 'nonzero-total'))
                if min(a, b, c) < 0:
                    raise ValueError('negative audio counter')
                host_rows += 1
                consumed += a
                underrun += b
                nonzero = max(nonzero, c)
        except (KeyError, ValueError):
            if line.startswith(('IPC ', 'AUDOUT_HOST_PROFILE ')):
                malformed += 1
    return {'service_requests': requests, 'successful_opens': opens,
            'manager_commands': dict(sorted(managers.items())),
            'child_commands': dict(sorted(commands.items())), 'child_handles': sorted(handles),
            'malformed_rows': malformed,
            'audio_host': {'interval_rows': host_rows, 'consumed_frames': consumed,
                           'underrun_frames': underrun, 'maximum_nonzero_total': nonzero,
                           'audibility_verified': False}}


def summarize_arbitration_log(text):
    addresses, calls, callers = Counter(), Counter(), Counter()
    ffffffff_count = malformed = 0
    for line in text[:text.rfind('\n') + 1].splitlines():
        if not line.startswith('SVC '):
            continue
        fields = dict(re.findall(r'([A-Za-z0-9_-]+)=(\S+)', line))
        if fields.get('id') not in ('0x1a', '0x1b'):
            continue
        try:
            opcode = fields['id']
            # Exact dispatcher contract: mutex_wait(r[1], r[0], r[2]) vs mutex_release(r[0]).
            address = fields['arg0x1' if opcode == '0x1a' else 'arg0x0']
            int(address, 0)  # Validate numeric shape but preserve the actual logged token.
            pc = fields['pc']
            addresses[address] += 1
            calls[opcode] += 1
            callers[(opcode, pc)] += 1
            ffffffff_count += opcode == '0x1b' and fields.get('arg0x1') == '0xffffffff'
        except (KeyError, ValueError):
            malformed += 1
    return {'calls': dict(calls), 'distinct_mutex_addresses': len(addresses),
            'mutex_addresses': [list(v) for v in addresses.most_common(15)],
            'callers': [{'opcode': op, 'pc': pc, 'calls': count} for (op, pc), count in callers.most_common(20)],
            'unlock_arg1_ffffffff_occurrences': ffffffff_count, 'malformed_rows': malformed,
            'scope': 'logged calls and opcode-specific address registers, not lock outcome or timing'}


def audit(adapter, elf, log, expected_elf_sha256, overlay):
    if not re.fullmatch(r'[0-9a-f]{64}', expected_elf_sha256):
        raise ValueError('expected ELF SHA must be an exact lowercase 64-hex token')
    elf_sha = hashlib.sha256(elf.read_bytes()).hexdigest()
    if elf_sha != expected_elf_sha256:
        raise ValueError('ELF hash mismatch')
    raw = log.read_bytes()
    build_ids = re.findall(rb'^LAMENTUM_BUILD_ID sha256=([0-9a-f]{64})\r?$', raw, re.MULTILINE)
    if build_ids != [elf_sha.encode()]:
        raise ValueError('captured log must have exactly one matching executable build ID')
    diff = subprocess.check_output(['git', '-C', str(adapter), 'diff'])
    if diff != overlay.read_bytes():
        raise ValueError('adapter diff differs from the checked-in runtime overlay')
    ipc = (adapter / 'native/ipc.h').read_text()
    audio = (adapter / 'native/audout.h').read_text()
    relevant = ('ipc.h', 'audout.h', 'guest_profile.h', 'loader.c', 'threading.h')
    # Bind this audit to the retained build input, not just today's source checkout. Build218
    # and build219 have different ELFs but identical service/profiler/dispatch source here.
    for name in relevant:
        built = elf.parent / 'source/native' / name
        if not built.exists() or built.read_bytes() != (adapter / 'native' / name).read_bytes():
            raise ValueError('retained ELF build source missing or different: ' + name)
    compact_ipc, compact_audio = re.sub(r'\s+', '', ipc), re.sub(r'\s+', '', audio)
    compact_loader = re.sub(r'\s+', '', (adapter / 'native/loader.c').read_text())
    required = {
        'svc1a_mutex_address_x1': 'if(svc==0x1a){emit_svc(&b,svc);mutex_wait(r[1],r[0],r[2],pc);' in compact_loader,
        'svc1b_mutex_address_x0': 'if(svc==0x1b){emit_svc(&b,svc);mutex_release(r[0],pc);' in compact_loader,
        'audout_service_manager': 'if(!memcmp(name,"audout:u",8))found=EP_AUDOUT_MANAGER;' in compact_ipc,
        'audio_child_created': 'ipc_child(buffer,s,req,EP_AUDOUT,pc)' in compact_audio,
        'audio_endpoint_gate': 'if(endpoint!=EP_AUDOUT_MANAGER&&endpoint!=EP_AUDOUT)return0;' in compact_audio,
        'command7_append_branch': 'if(req->command==3||req->command==7)' in compact_audio,
        'command8_release_branch': 'if(req->command==5||req->command==8)' in compact_audio,
        'append_queue_operation': 'aout_push(&aout.queue,' in compact_audio,
        'release_queue_operation': 'aout_release(&aout.queue,' in compact_audio,
    }
    if not all(required.values()):
        raise ValueError('source shape changed: re-audit AudioOut dispatch semantics')
    enums = re.findall(r'enum endpoint\s*\{.*?\};', ipc, re.S)
    if len(enums) != 1 or '#' in enums[0]:
        raise ValueError('unconditional endpoint enum not uniquely identified')
    program = '#include <stdio.h>\n' + enums[0] + '\nint main(void){printf("%u %u\\n", (unsigned)EP_AUDOUT_MANAGER, (unsigned)EP_AUDOUT);return 0;}\n'
    with tempfile.TemporaryDirectory() as directory:
        executable = str(Path(directory) / 'endpoint-enum')
        subprocess.run(['cc', '-x', 'c', '-o', executable, '-'], input=program,
                       text=True, capture_output=True, check=True, timeout=30)
        manager, child = map(int, subprocess.check_output([executable], text=True, timeout=10).split())
    result = {'scope': 'static source binding + captured-run event counts; not latency/CPU attribution',
              'log_build_id_verified': True,
              'elf_sha256': elf_sha, 'overlay_sha256': hashlib.sha256(diff).hexdigest(),
              'overlay_matches': True, 'retained_build_source_matches': True,
              'source_sha256': {name: hashlib.sha256((adapter / 'native' / name).read_bytes()).hexdigest()
                                for name in relevant},
              'log_sha256': hashlib.sha256(raw).hexdigest(),
              'compiled_endpoint_enum': {'EP_AUDOUT_MANAGER': manager, 'EP_AUDOUT': child},
              'source_markers_checked': required,
              'interpretation': {'endpoint_field': 'adapter enum tag, NOT guest handle',
                                 'service': 'audout:u -> EP_AUDOUT_MANAGER -> EP_AUDOUT child',
                                 'command7': 'append an AudioOut PCM buffer',
                                 'command8': 'retrieve released AudioOut buffer tags',
                                 'command_timings_measured': False},
              'captured_run': summarize_audio_log(raw.decode('utf-8', 'replace'), manager=manager, child=child),
              'arbitration': summarize_arbitration_log(raw.decode('utf-8', 'replace'))}
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--adapter', type=Path, required=True)
    ap.add_argument('--elf', type=Path, required=True)
    ap.add_argument('--log', type=Path, required=True)
    ap.add_argument('--expected-elf-sha256', required=True)
    ap.add_argument('--overlay', type=Path, default=Path(__file__).resolve().parents[1] / 'runtime/lamentum-adapter.patch')
    args = ap.parse_args()
    print(json.dumps(audit(args.adapter, args.elf, args.log, args.expected_elf_sha256, args.overlay), indent=2))

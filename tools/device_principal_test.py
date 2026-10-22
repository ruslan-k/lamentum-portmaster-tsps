#!/usr/bin/env python3
"""Owned, bounded Spruce-principal run. No direct game launch or unowned PID kill.

Requires the matching Lamentum.sh + run_identity.py installed together. This
observer qualifies run/log/process identity only, NOT scene or content bindings.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import time

from lamentum_pad_contract import remote, snapshot, validate_cleanup
from exit_outcome import KERNEL_PAYLOAD, classify_exit
from load_metrics import collector_request, fold
from proc_metrics import sample_request
from run_identity import preflight_request, terminate_request, uuid_request, validate_uuid

HARD_STOP_GRACE_S = 120
PORT_DIR = '/mnt/SDCARD/Roms/PORTS/lamentum-switch'
LAUNCHER = '/mnt/SDCARD/Roms/PORTS/Lamentum.sh'
STD_LAUNCH = '/mnt/SDCARD/Emu/PORTS/../../spruce/scripts/emu/standard_launch.sh'


def is_killed_without_stop(log, stops):
    return not stops and bool(re.search(r'\bKilled\b|exit status 137', log))


def should_hard_stop(now, hard_deadline, game_pids):
    return bool(hard_deadline) and now > hard_deadline and bool(game_pids)


def confirmed_host_termination(receipt):
    """A refused/racing attempt is not a delivered TERM or an exit cause."""
    return receipt if receipt.get('outcome') == 'pidfd_TERM' else None


def launch_command(run_uuid, budget, extra):
    validate_uuid(run_uuid)
    if budget <= 0:
        raise ValueError('owned probe requires a positive bounded budget')
    assignments = []
    for item in extra:
        if not re.fullmatch(r'[A-Z][A-Z_0-9]*=.*', item):
            raise ValueError('invalid env assignment')
        if item.split('=', 1)[0] in ('LAMENTUM_RUN_UUID', 'LAMENTUM_PROBE_SECONDS'):
            raise ValueError('owned identity and governor are reserved')
        assignments.append('export ' + shlex.quote(item) + ';')
    assignments += ['export LAMENTUM_RUN_UUID=' + shlex.quote(run_uuid) + ';',
                    'export LAMENTUM_PROBE_SECONDS=%d;' % budget,
                    'chmod a+x %s;' % shlex.quote(STD_LAUNCH),
                    shlex.join([STD_LAUNCH, LAUNCHER])]
    return ' '.join(assignments) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget', type=int, default=90)
    parser.add_argument('--wait', type=int, default=180, help='minimum watch window; never shorter than host hard bound')
    parser.add_argument('--env', action='append', default=[])
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    # Validate caller-controlled settings before touching the device.
    launch_command('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', args.budget, args.env)
    if args.evidence:
        args.evidence.mkdir(parents=True, exist_ok=True)
        if (args.evidence / 'expected-run.json').exists():
            raise ValueError('evidence directory already owns a prior run')
    before = snapshot()
    if before['game'] or len(before['processes'].get('MainUI', [])) != 1:
        print('device not idle; refusing launch', file=sys.stderr)
        return 2
    preflight = remote(preflight_request(PORT_DIR + '/lamentum-nextos', LAUNCHER, PORT_DIR + '/run_identity.py'))
    repo = Path(__file__).resolve().parents[1]
    for key, path in (('launcher', repo / 'port/Lamentum.sh'), ('helper', repo / 'tools/run_identity.py')):
        if preflight[key]['sha256'] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise RuntimeError('installed %s differs; deploy launcher/helper together before testing' % key)
    run_uuid = remote(uuid_request())['run_uuid']
    validate_uuid(run_uuid)
    expected = {'run_uuid': run_uuid, 'boot_id': preflight['boot_id'],
                'elf_dev': preflight['runtime']['dev'], 'elf_ino': preflight['runtime']['ino'],
                'elf_sha256': preflight['runtime']['sha256'],
                'launcher_sha256': preflight['launcher']['sha256'],
                'helper_sha256': preflight['helper']['sha256']}
    if args.evidence:
        (args.evidence / 'before.json').write_text(json.dumps(before, indent=2) + '\n')
        (args.evidence / 'expected-run.json').write_text(json.dumps(expected, indent=2) + '\n')
    try:
        kernel_before = remote(KERNEL_PAYLOAD)
    except Exception as error:
        kernel_before = {'available': False, 'error': str(error)}
    command = launch_command(run_uuid, args.budget, args.env)
    # Read-back the exact principal command before asking the menu to exit.
    written = remote('from pathlib import Path\nimport json\np=Path("/tmp/cmd_to_run.sh")\n'
                     'text=%r\np.write_text(text);p.chmod(0o755)\n'
                     'print(json.dumps({"command":p.read_text()}))\n' % command)
    if written['command'] != command:
        raise RuntimeError('principal command read-back differs')
    menu = before['processes']['MainUI'][0]
    menu_owner = remote('from pathlib import Path\nimport os,json\np=Path("/proc")/str(%d)\n'
                        'assert (p/"comm").read_text().strip()=="MainUI"\n'
                        's=(p/"stat").read_text();start=int(s[s.rindex(")")+1:].split()[19])\n'
                        'assert start==%d\ne=os.stat(p/"exe")\n'
                        'print(json.dumps({"pid":%d,"starttime":start,"boot_id":%r,"elf_dev":e.st_dev,"elf_ino":e.st_ino}))\n'
                        % (menu['pid'], menu['starttime'], menu['pid'], expected['boot_id']))
    stopped_menu = remote(terminate_request(menu_owner))
    if stopped_menu['outcome'] != 'pidfd_TERM':
        raise RuntimeError('principal handoff refused: ' + str(stopped_menu))
    started = time.monotonic()
    deadline = started + max(args.wait, args.budget + HARD_STOP_GRACE_S + 30)
    hard_deadline = started + args.budget + HARD_STOP_GRACE_S
    owner, log_state, host_terminated, observer_error = None, {}, None, None
    identity_errors, execution_verified, stop_attempts = [], False, []
    while time.monotonic() < deadline:
        time.sleep(2)
        try:
            sample = remote(collector_request(log_state, expected_run=expected))
            # Prior latest.log can still exist before the new launcher opens it.
            # Never consume it; only the expected kernel UUID may attach.
            if not log_state.get('log_identity_qualified') and sample.get('status') != 'ok':
                if time.monotonic()-started > 60:
                    raise RuntimeError('owned run header did not appear: ' + str(sample.get('status')))
                continue
            log_state = fold(log_state, sample)
            if not log_state.get('log_identity_qualified'):
                continue
            header = log_state['run_header']
            if owner is None:
                owner = {key: header[key] for key in ('boot_id', 'pid', 'starttime', 'elf_dev', 'elf_ino')}
            process = remote(sample_request(expected=owner))
            if process.get('running'):
                execution_verified = True
            if process.get('sample_status') in ('identity_mismatch', 'changed_during_read', 'ambiguous'):
                raise RuntimeError('owned process identity changed')
            if log_state.get('stops') or (execution_verified and process.get('sample_status') in ('exited', 'unavailable')):
                break
            if should_hard_stop(time.monotonic(), hard_deadline, [owner['pid']]):
                attempt = remote(terminate_request(owner))
                attempt['at_elapsed_s'] = time.monotonic()-started
                stop_attempts.append(attempt)
                host_terminated = confirmed_host_termination(attempt)
                if not host_terminated and attempt.get('outcome') != 'already_exited':
                    observer_error = 'owned stop was not delivered: ' + str(attempt.get('outcome'))
                break
        except RuntimeError as error:
            observer_error = str(error)
            if owner:
                attempt = remote(terminate_request(owner))
                stop_attempts.append(attempt)
                host_terminated = confirmed_host_termination(attempt)
            break
        except Exception as error:
            identity_errors.append({'error': str(error), 'elapsed_s': time.monotonic()-started})
            if time.monotonic() > hard_deadline:
                if owner:
                    attempt = remote(terminate_request(owner))
                    stop_attempts.append(attempt)
                    host_terminated = confirmed_host_termination(attempt)
                observer_error = 'observer transport unavailable at hard deadline'
                break
    # principal.sh, not this tool, restores Spruce and the CPU online mask.
    after = snapshot(expected_run_uuid=run_uuid)
    cleanup_deadline = time.monotonic() + 90
    while validate_cleanup(before, after) and time.monotonic() < cleanup_deadline:
        time.sleep(3)
        after = snapshot(expected_run_uuid=run_uuid)
    errors = validate_cleanup(before, after)
    # Final records are read through the SAME owned protocol, never a raw cat/tail.
    log_parts, final_state = [], {}
    final_expected = dict(expected)
    if owner:
        final_expected.update(owner)
    if log_state.get('run_header'):
        final_expected['launch_nonce'] = log_state['run_header']['launch_nonce']
    try:
        for _ in range(256):  # <=64 MiB total, bounded complete-line chunks
            sample = remote(collector_request(final_state, expected_run=final_expected, include_text=True))
            final_state = fold(final_state, sample)
            if sample['status'] != 'ok':
                raise RuntimeError('final owned header is incomplete')
            log_parts.append(sample['chunk_text'])
            if sample['offset'] == sample['size']:
                break
            if not sample['chunk_text']:
                raise RuntimeError('final log has an incomplete record')
        else:
            raise RuntimeError('final owned log exceeds bounded read')
    except Exception as error:
        observer_error = observer_error or str(error)
    log = ''.join(log_parts)
    stops = [line[len('STOP status='):].split(' ',1)[0] for line in log.splitlines()
             if line.startswith('STOP status=') and line[len('STOP status='):]]
    try:
        kernel_after = remote(KERNEL_PAYLOAD)
    except Exception as error:
        kernel_after = {'available': False, 'error': str(error)}
    termination = classify_exit(log, host_terminated=host_terminated, kernel_before=kernel_before,
                                kernel_after=kernel_after, owner=owner)
    result = {'cleanup_errors': errors, 'before': before, 'after': after,
              'expected_run': expected, 'process_identity': owner, 'execution_verified': execution_verified,
              'host_terminated': host_terminated, 'termination': termination,
              'stop_attempts': stop_attempts,
              'observer_error': observer_error, 'identity_errors': identity_errors,
              'stops': stops, 'killed_without_stop': is_killed_without_stop(log, stops),
              'runtime_ok': termination['kind'] == 'runtime_timeout' and not observer_error and execution_verified,
              'config_rejected': any(value.startswith('INVALID_') for value in stops),
              'content_bindings_complete': False, 'scene_verified': False}
    if args.evidence:
        for name, value in (('kernel-before.json', kernel_before), ('kernel-after.json', kernel_after),
                            ('cleanup.json', result), ('owned-log-final.json', final_state)):
            (args.evidence / name).write_text(json.dumps(value, indent=2) + '\n')
        (args.evidence / 'latest.log').write_text(log)
    print(json.dumps(result))
    if errors:
        return 3
    if observer_error or not execution_verified:
        return 9
    if result['config_rejected']:
        return 5
    if host_terminated:
        return 6
    if termination['kind'] == 'kernel_oom_sigkill':
        return 8
    if termination['kind'] == 'sigkill_unknown':
        return 7
    return 0 if result['runtime_ok'] else 4


if __name__ == '__main__':
    sys.exit(main())

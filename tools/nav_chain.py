"""Frame-paced press → row chain, qualified by a new presented frame.

This is the wiring roadmap 32.7 asks for: one navigator (`navigator.Navigation`),
one oracle (`page_oracle.analyse`), the port's own present counter
(`load_metrics.present_serial`) and the owner-checked pad contract.

Two lessons from the first ad-hoc chain are baked in:
  * the serial is read from `.../logs/latest.log` (a guessed sibling path returns 0
    and silently removes the qualification);
  * a press is SHORT (default 350 ms) because 900 ms at ~1 fps moved two rows.
"""
import argparse
import base64
import json
from pathlib import Path
import struct
import sys
import time
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lamentum_pad_contract as pad          # noqa: E402
import page_oracle                            # noqa: E402
from load_metrics import present_serial, serial_request  # noqa: E402
from navigator import Navigation, observe     # noqa: E402

TAP_MS = 350
SERIAL_WAIT_S = 25
# Owner P0-N2 asks for a bounded short-press sweep on hardware: 80/150/250/400 ms.
SWEEP_MS = (80, 150, 250, 400)
EVIDENCE = Path('evidence')


def summarise(serial_before, row_before, serial_after, row_after, tap_ms=TAP_MS):
    """Decide what one press+frame pair proves. No device, no guessing."""
    if not serial_before or not serial_after:
        return {'qualified': False, 'reason': 'present serial unavailable; the press is not '
                'qualified by a new frame', 'step': None}
    if serial_after <= serial_before:
        return {'qualified': False, 'reason': 'no newer presented frame after the press',
                'step': None, 'serial_delta': serial_after - serial_before}
    if row_before is None or row_after is None:
        return {'qualified': False, 'reason': 'a row was not measurable', 'step': None,
                'serial_delta': serial_after - serial_before}
    if row_before == row_after:
        return {'qualified': True, 'reason': 'press did not move the selection',
                'step': 0, 'serial_delta': serial_after - serial_before,
                'hint': 'longer tap or the wrong button' if tap_ms >= 600 else 'check the button role'}
    position = {name: y for y, name in page_oracle.EXPECTED_ROWS.items()}
    ordered = sorted(position.values())
    pitch = max(1, ordered[1] - ordered[0])
    step = round(abs(position[row_after] - position[row_before]) / pitch)
    verdict = {'qualified': True, 'step': step, 'serial_delta': serial_after - serial_before,
               'row_before': row_before, 'row_after': row_after}
    if step > 1:
        return {'qualified': False, 'step': step,
                'serial_delta': serial_after - serial_before,
                'row_before': row_before, 'row_after': row_after,
                'reason': ('one %d ms press moved %d rows - overshoot refused; shorten the tap'
                           % (tap_ms, step))}
    else:
        verdict['reason'] = 'one press moved exactly one row on a newer frame'
    return verdict


def sweep_decision(attempts, values=SWEEP_MS):
    """Next hold length to try, or why the sweep stops. Pure.

    Stop rules from roadmap 40.3: one row on a newer frame ends the sweep as
    SUCCESS; a two-row move ends it immediately as OVERSHOOT (never continue past
    it); no movement at all keeps trying shorter/longer values until exhausted.
    """
    for attempt in attempts:
        verdict = attempt.get('verdict') or {}
        if verdict.get('qualified') and verdict.get('step') == 1:
            return {'done': True, 'outcome': 'one_row', 'tap_ms': attempt['tap_ms'],
                    'row_before': verdict.get('row_before'), 'row_after': verdict.get('row_after')}
        if verdict.get('step') is not None and verdict['step'] > 1:
            return {'done': True, 'outcome': 'overshoot', 'tap_ms': attempt['tap_ms'],
                    'step': verdict['step'], 'reason': verdict.get('reason')}
    tried = [attempt['tap_ms'] for attempt in attempts]
    remaining = [value for value in values if value not in tried]
    if not remaining:
        return {'done': True, 'outcome': 'no_movement_across_sweep', 'tried': tried}
    return {'done': False, 'next_tap_ms': remaining[0], 'tried': tried}


def decode_png(data):
    pos, idat = 8, b''
    width = height = depth = colour = interlace = None
    while pos < len(data):
        length, = struct.unpack('>I', data[pos:pos + 4])
        kind, chunk = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b'IHDR':
            width, height, depth, colour, _, _, interlace = struct.unpack('>IIBBBBB', chunk)
        elif kind == b'IDAT':
            idat += chunk
        elif kind == b'IEND':
            break
    assert depth == 8 and interlace == 0, (depth, interlace)
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
    raw, stride, rows, previous, i = zlib.decompress(idat), width * channels, [], bytearray(width * channels), 0
    for _ in range(height):
        kind, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if kind == 1:
            for x in range(channels, stride):
                line[x] = (line[x] + line[x - channels]) & 0xFF
        elif kind == 2:
            for x in range(stride):
                line[x] = (line[x] + previous[x]) & 0xFF
        elif kind == 3:
            for x in range(stride):
                left = line[x - channels] if x >= channels else 0
                line[x] = (line[x] + ((left + previous[x]) >> 1)) & 0xFF
        elif kind == 4:
            for x in range(stride):
                a = line[x - channels] if x >= channels else 0
                b, c = previous[x], previous[x - channels] if x >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        rows.append(bytes(line))
        previous = line
    return width, height, channels, b''.join(rows)


def grab(tag, owner_dir):
    remote_dir = '/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs'
    capture = pad.remote('''import subprocess,pathlib,json
d=pathlib.Path(%r);d.mkdir(parents=True,exist_ok=True)
out=d/%r
r=subprocess.run(["/mnt/SDCARD/spruce/bin64/kmsgrab",str(out)],capture_output=True,text=True)
print(json.dumps({"rc":r.returncode,"bytes":out.stat().st_size if out.exists() else 0}))'''
                       % (remote_dir, tag + '.png'))
    if not capture.get('bytes'):
        return None, capture
    data = base64.b64decode(pad.remote('''import base64,pathlib,json
print(json.dumps({"png":base64.b64encode(pathlib.Path(%r).read_bytes()).decode()}))'''
                                    % (remote_dir + '/' + tag + '.png'))['png'])
    owner_dir.mkdir(parents=True, exist_ok=True)
    (owner_dir / (tag + '.png')).write_bytes(data)
    width, height, channels, pixels = decode_png(data)
    grey = bytes(pixels[i] for i in range(0, len(pixels), channels))
    return page_oracle.analyse(grey, width, height), capture


def game_pid():
    return pad.remote('''import pathlib,os,json
pid=None
for d in pathlib.Path("/proc").glob("[0-9]*"):
 try:
  if os.path.basename(os.readlink(d/"exe"))=="lamentum-nextos": pid=int(d.name)
 except OSError: continue
print(json.dumps({"pid":pid}))''')['pid']


def owner_of(pid):
    return pad.remote('''import pathlib,os,json
pid=%d
s=(pathlib.Path("/proc")/str(pid)/"stat").read_text();start=int(s[s.rindex(")")+2:].split()[19])
e=os.stat(pathlib.Path("/proc")/str(pid)/"exe")
print(json.dumps({"pid":pid,"starttime":start,"elf_dev":e.st_dev,"elf_ino":e.st_ino,
 "boot_id":pathlib.Path("/proc/sys/kernel/random/boot_id").read_text().strip()}))''' % pid)


def wait_serial(after, deadline_s=SERIAL_WAIT_S):
    deadline = time.monotonic() + deadline_s
    while time.monotonic() < deadline:
        value = pad.remote(serial_request())['present_frames']
        if value > after:
            return value
        time.sleep(0.7)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tap-ms', type=int, default=TAP_MS)
    parser.add_argument('--sweep', action='store_true',
                        help='try SWEEP_MS one press at a time, stopping on one row or overshoot')
    parser.add_argument('--sweep-values', default=None,
                        help='comma-separated subset of the sweep, e.g. 80,150,250')
    parser.add_argument('--target', default='newgame')
    parser.add_argument('--evidence', type=Path, default=EVIDENCE / 'nav-chain-03')
    parser.add_argument('--wait-game', type=int, default=240)
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    deadline, owner = time.monotonic() + args.wait_game, None
    record = {'tap_ms': args.tap_ms, 'target': args.target, 'states': []}
    while time.monotonic() < deadline:
        time.sleep(1.5)
        pid = game_pid()
        if not pid:
            continue
        if owner is None:
            owner = owner_of(pid)
            pad.set_expected_owner(owner)
            record['owner'] = owner
        # A brand-new run can still have an empty/rotated log: wait for the
        # first present line instead of reading 0 and refusing a valid frame.
        before_serial = wait_serial(0)
        before, capture = grab('nav-chain-a', args.evidence)
        record['states'].append({'phase': 'before', 'serial': before_serial,
                                 'capture': capture, 'oracle': before})
        if not before or before['page'] != page_oracle.MAIN_MENU or not before.get('row'):
            continue
        navigator = Navigation(target=args.target)
        action = observe(navigator, before['page'], before['cursor_y'], before_serial)
        record['navigator_action'] = action
        if action['action'] != 'press':
            record['stopped'] = 'navigator did not ask for a press: ' + str(action)
            break
        if args.sweep and args.sweep_values:
            taps = [int(value) for value in args.sweep_values.split(',')]
        else:
            taps = list(SWEEP_MS) if args.sweep else [args.tap_ms]
        attempts, serial = [], before_serial
        for tap_ms in taps:
            try:
                pad.press(action['button'], tap_ms)
            except RuntimeError as error:
                attempts.append({'tap_ms': tap_ms, 'verdict': {
                    'qualified': False, 'reason': 'owned process unavailable before the press: %s' % error}})
                record['sweep'] = {'attempts': attempts,
                                   'decision': {'done': True, 'outcome': 'arm_ended'}}
                break
            after_serial = wait_serial(serial)
            after, capture = grab('nav-chain-b-' + str(tap_ms), args.evidence)
            verdict = summarise(serial, before['row'], after_serial,
                                (after or {}).get('row'), tap_ms)
            attempt = {'tap_ms': tap_ms, 'serial_before': serial, 'serial_after': after_serial,
                       'verdict': verdict, 'capture': capture}
            attempts.append(attempt)
            record['states'].append({'phase': 'after', 'tap_ms': tap_ms, 'serial': after_serial,
                                     'capture': capture, 'oracle': after, 'verdict': verdict})
            if after_serial:
                serial = after_serial
            decision = sweep_decision(attempts) if args.sweep else {
                'done': True, 'outcome': 'single_tap', 'tap_ms': tap_ms}
            if decision['done']:
                record['sweep'] = {'attempts': attempts, 'decision': decision}
                break
            before = after or before
            navigator = Navigation(target=args.target)
            next_action = observe(navigator, before['page'], before['cursor_y'], serial)
            if next_action['action'] != 'press':
                record['sweep'] = {'attempts': attempts,
                                   'decision': {'done': True, 'outcome': 'navigator_stopped',
                                                'reason': str(next_action)}}
                break
            action = next_action
        else:
            record['sweep'] = {'attempts': attempts, 'decision': sweep_decision(attempts)}
        record['verdict'] = (record['sweep']['attempts'][-1]['verdict']
                             if record.get('sweep') else None)
        break
    (args.evidence / 'chain.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    return 0 if record.get('verdict', {}).get('qualified') else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""PNG/single-step analysis helpers and the owned row-driver entry point.

CLI now delegates to owned_nav_chain: mandatory expected-run receipt, one reader
and one Navigation per attempt, explicit release receipts, no blind sweep reset.
The pure summarise/sweep helpers remain for historical receipt tests only.
"""
import struct
import sys
from pathlib import Path
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import page_oracle  # noqa: E402

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


def main():
    # Retired the per-tap reset and unpinned-reader sweep path.
    from owned_nav_chain import main as owned_main
    return owned_main()

if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Replay a private captured log through the actual incremental remote collector, on the host.

Only counters and a source digest are emitted; never copy private log content to public evidence.
This validates framing/counters, not device identity, sampling overhead or scene progress.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile

from load_metrics import collector_request, fold, parse_chunk


def replay(path):
    data = path.read_bytes()
    # Uneven boundaries plus splits inside real event names/numbers near either end.
    cuts = {0, len(data)}
    cuts.update(range(0, len(data), max(1, len(data) // 32)))
    for marker in (b'NVN_PRESENT_PIXELS frame=', b'STOP status=', b'ROMFS_READ'):
        for pos in (data.find(marker), data.rfind(marker)):
            if pos >= 0:
                cuts.update(min(len(data), pos + j) for j in (1, len(marker), len(marker) + 1))
    state = {}
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / 'latest.log'
        log.write_bytes(b'')
        cursor = 0
        for end in sorted(cuts):
            with log.open('ab') as handle:
                handle.write(data[cursor:end])
            cursor = end
            source = collector_request(state).replace(
                "Path('/mnt/SDCARD/Roms/PORTS/lamentum-switch/logs/latest.log')",
                'Path(%r)' % str(log))
            source = source.replace("Path('/proc/meminfo').read_text().splitlines()", "[]")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(compile(source, '<real-collector-replay>', 'exec'), {})
            state = fold(state, json.loads(out.getvalue()))
    complete = data.rfind(b'\n') + 1
    expected = parse_chunk(data[:complete].decode('utf-8', 'replace'))
    for key, value in expected['counters'].items():
        if state[key] != value:
            raise AssertionError((key, state[key], value))
    for key in ('frame', 'stops', 'budget_last', 'killed'):
        if state.get(key) != expected[key]:
            raise AssertionError((key, state.get(key), expected[key]))
    if state['offset'] != complete:
        raise AssertionError(('offset', state['offset'], complete))
    return {'pass': True, 'source_sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data), 'complete_bytes': complete, 'polls': len(cuts),
            'counters': {key: state[key] for key in expected['counters']},
            'frame': state['frame'], 'stops': state['stops'],
            'scope': 'host replay of captured log; not a new device run or FPS result'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('log', type=Path)
    args = ap.parse_args()
    print(json.dumps(replay(args.log), indent=2))

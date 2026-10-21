"""Bounded diagnostic row-navigation driver; Confirm intentionally disabled.

Does not launch a game. Consume the expected-run.json produced by the separately
bounded principal harness. Requires explicit diagnostic-input opt-in and timeout.
"""
import argparse
import json
import math
from pathlib import Path
import time

import lamentum_pad_contract as pad
from load_metrics import OwnedSerial
from owned_navigation import OwnedNavigationDriver
from proc_metrics import sample_request
from run_identity import validate_uuid


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-run', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--response-timeout-s', type=float, required=True,
                        help='explicit bounded diagnostic timeout, not a calibrated device preset')
    parser.add_argument('--tap-ms', type=int, default=350)
    parser.add_argument('--target', default='newgame', choices=('load', 'newgame', 'options', 'credits'))
    parser.add_argument('--diagnostic-input', action='store_true',
                        help='opt in to row-only evdev input; not safe-memory/gameplay qualification')
    args = parser.parse_args(argv)
    if not args.diagnostic_input:
        parser.error('diagnostic input opt-in required; memory/page gates are not qualified')
    if not math.isfinite(args.response_timeout_s) or not 0 < args.response_timeout_s <= 60:
        parser.error('response timeout must be finite, positive, and at most 60 seconds')
    if not 1 <= args.tap_ms <= 400:
        parser.error('tap must be 1..400 ms')
    expected = json.loads(args.expected_run.read_text())
    for key in ('run_uuid', 'boot_id'):
        validate_uuid(expected[key])
    for key in ('elf_dev', 'elf_ino', 'elf_sha256', 'launcher_sha256', 'helper_sha256'):
        if key not in expected:
            parser.error('expected-run receipt missing ' + key)
    args.evidence.mkdir(parents=True, exist_ok=True)
    result_path = args.evidence / 'owned-chain.json'
    if result_path.exists():
        parser.error('refusing to overwrite an existing attempt')
    reader = OwnedSerial(expected_run=expected)
    capture_index = 0

    def verify(owner):
        sample = pad.remote(sample_request(expected=owner))
        valid = sample.get('running') is True
        if valid:
            pad.set_expected_owner(owner)
        return valid

    def capture():
        nonlocal capture_index
        # Use the common owner-bracketed capture, never an unowned guessed file.
        from nav_chain import decode_png
        import page_oracle
        path = args.evidence / ('capture-%04d.png' % capture_index)
        capture_index += 1
        pad.capture(path)
        w, h, channels, pixels = decode_png(path.read_bytes())
        grey = bytes(pixels[i] for i in range(0, len(pixels), channels))
        return page_oracle.analyse(grey, w, h)

    driver = OwnedNavigationDriver(reader=reader, remote=pad.remote,
                                   capture=capture, press=pad.press, verify_owner=verify,
                                   response_timeout_s=args.response_timeout_s,
                                   target=args.target, tap_ms=args.tap_ms)
    deadline = time.monotonic() + args.response_timeout_s
    try:
        while time.monotonic() < deadline:
            event = driver.tick()
            if event['action'] in ('refuse', 'done'):
                break
            time.sleep(0.1)
        else:
            driver._refuse('overall diagnostic attempt deadline expired')
    finally:
        result_path.write_text(json.dumps({'scope': 'row-only diagnostic; not gameplay qualification',
                                          'expected_run': expected, 'events': driver.events,
                                          'refused': driver.refused, 'owner': driver.owner,
                                          'generation': driver.generation}, indent=2) + '\n')
        pad.set_expected_owner(None)
    print(json.dumps({'receipt': str(result_path), 'refused': driver.refused}))
    return 1 if driver.refused else 0


if __name__ == '__main__':
    raise SystemExit(main())

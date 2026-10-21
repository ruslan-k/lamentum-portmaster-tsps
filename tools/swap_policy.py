#!/usr/bin/env python3
"""Move RAM-backed swap ahead of the file swaps for one measured arm (reversible).

Why: `/proc/swaps` on the device lists a 512 MiB file swap on the microSD at priority 40,
a 1 GiB swapfile on UDISK at -2, and zram0 (493 MiB, lzo) at -3. The kernel therefore pages
the guest's anonymous "physical" memory out to the SD card first, which is what
`docs/swap-attribution.md` measured as 766 MiB of VmSwap on a 963 MiB board.

This tool only re-orders priorities: the file swaps stay enabled as a fallback, so a full
zram cannot turn into an OOM the way `swapoff` would. Both directions are verified by
re-reading /proc/swaps, and the original priority is recorded so restore() is exact.

  python3 tools/swap_policy.py state
  python3 tools/swap_policy.py raise --device /dev/zram0 --priority 100 --evidence evidence/x
  python3 tools/swap_policy.py restore --device /dev/zram0 --priority -3 --evidence evidence/x
"""
import argparse
import json
import os
import pathlib
import shlex
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HOST = os.environ.get('LAMENTUM_DEVICE')


def parse_swaps(text):
    """Rows of /proc/swaps as dicts; the header line is skipped."""
    rows = []
    for line in text.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        filename, kind, size, used = parts[0], parts[1], parts[2], parts[3]
        priority = parts[4] if len(parts) > 4 else '0'
        rows.append({'filename': filename, 'type': kind, 'size_kb': int(size),
                     'used_kb': int(used), 'priority': int(priority)})
    return rows


def zram_first(rows, device):
    """True when `device` outranks every file swap, i.e. RAM is used before the SD card."""
    target = [r for r in rows if r['filename'] == device]
    others = [r for r in rows if r['filename'] != device]
    if len(target) != 1:
        return False
    return all(target[0]['priority'] > r['priority'] for r in others)


def apply_plan(device, priority, rows, allow_used_kb=0):
    """swapoff/on sequence for re-ordering a zram device. Refuses a device above the allowance.

    A residual allowance is not a RAM-headroom or idle-state check. The caller must
    separately authorize the experiment and establish safe headroom before draining.
    """
    target = [r for r in rows if r['filename'] == device]
    if len(target) != 1:
        raise ValueError('device %r appears %d times in /proc/swaps' % (device, len(target)))
    if allow_used_kb < 0:
        raise ValueError('negative residual allowance')
    if target[0]['type'] != 'partition':
        raise ValueError('%r is not a block-device swap' % device)
    if target[0]['used_kb'] > allow_used_kb:
        raise ValueError('%r holds %d kB (allowance %d kB); refusing to cycle a live swap'
                         % (device, target[0]['used_kb'], allow_used_kb))
    return [['swapoff', device], ['swapon', '-p', str(priority), device]]


def ssh(command, timeout=90):
    if not HOST:
        raise RuntimeError('Set LAMENTUM_DEVICE to the SSH target before remote access')
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST, command],
                            capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError('%s -> %d: %s' % (command, result.returncode, (result.stderr or result.stdout).strip()))
    return result.stdout


def state():
    return parse_swaps(ssh('cat /proc/swaps'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=['state', 'raise', 'restore'])
    parser.add_argument('--device', default='/dev/zram0')
    parser.add_argument('--priority', type=int)
    parser.add_argument('--evidence', type=pathlib.Path)
    parser.add_argument('--allow-used-kb', type=int, default=0,
                        help='permit draining this much residual swap (restore on an idle board)')
    args = parser.parse_args(argv)

    before = state()
    receipt = {'action': args.action, 'device': args.device, 'before': before}
    if args.action != 'state':
        if args.priority is None:
            parser.error('%s needs --priority' % args.action)
        plan = apply_plan(args.device, args.priority, before, args.allow_used_kb)
        receipt['plan'] = plan
        for command in plan:
            receipt.setdefault('outputs', []).append(ssh(shlex.join(command)).strip())
        after = state()
        receipt['after'] = after
        receipt['zram_first'] = zram_first(after, args.device)
        target = [r for r in after if r['filename'] == args.device]
        if len(target) != 1 or target[0]['priority'] != args.priority:
            raise RuntimeError('requested swap priority was not verified: %r' % after)
        if args.action == 'raise' and not receipt['zram_first']:
            raise SystemExit('priority change did not take effect: %r' % (after,))
    else:
        receipt['after'] = before
        receipt['zram_first'] = zram_first(before, args.device)
    receipt['summary'] = {r['filename']: r['priority'] for r in receipt['after']}
    if args.evidence:
        out = args.evidence if args.evidence.is_absolute() else REPO / 'evidence' / args.evidence
        out.mkdir(parents=True, exist_ok=True)
        name = {'state': 'swap-state.json', 'raise': 'swap-raise.json', 'restore': 'swap-restore.json'}[args.action]
        (out / name).write_text(json.dumps(receipt, indent=2) + '\n')
        receipt['written'] = str(out / name)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

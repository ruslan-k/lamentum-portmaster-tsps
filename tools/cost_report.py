#!/usr/bin/env python3
"""Parse complete LC2_COST_V2 snapshots without losing thread IDs or summing cumulative windows.

These are measured-handler intervals, NOT a whole-process/frame profile. Missing snapshots,
unfinished calls and dropped clock/identity samples are reported, never filled with zeros.
"""
import argparse
import json
from pathlib import Path


def fields(line):
    return dict(word.split('=', 1) for word in line.split()[1:] if '=' in word)


def summarize(text):
    complete = []
    active = None
    used_reports = set()
    for line in text.splitlines():
        if line.startswith('LC2_COST_V2_BEGIN '):
            header = fields(line)
            report = int(header['report'])
            if report in used_reports:
                raise ValueError('RUN_GENERATION_AMBIGUOUS: repeated cumulative report id')
            used_reports.add(report)
            active = {'header': header, 'rows': [], 'keys': set()}
        elif line.startswith('LC2_COST_V2 '):
            if active is None:
                raise ValueError('row without a snapshot header')
            row = fields(line)
            if row['report'] != active['header']['report']:
                raise ValueError('row/header report mismatch')
            key = (int(row['tid']), int(row['tid_starttime']), row['class'])
            if key in active['keys']:
                raise ValueError('duplicate thread-generation/class row')
            active['keys'].add(key)
            numeric = ('entered', 'completed', 'valid', 'invalid', 'nesting_errors',
                       'cpu_inclusive_ns', 'cpu_exclusive_ns', 'wall_inclusive_ns',
                       'wall_exclusive_ns', 'max_cpu_ns', 'max_wall_ns', 'wall_lt_cpu')
            parsed = {name: int(row[name]) for name in numeric}
            if any(value < 0 for value in parsed.values()):
                raise ValueError('negative counter')
            if parsed['completed'] > parsed['entered'] or parsed['valid'] + parsed['invalid'] != parsed['completed']:
                raise ValueError('unbalanced call counters')
            if (parsed['cpu_exclusive_ns'] > parsed['cpu_inclusive_ns'] or
                    parsed['wall_exclusive_ns'] > parsed['wall_inclusive_ns']):
                raise ValueError('exclusive interval exceeds inclusive interval')
            active['rows'].append(dict(parsed, tid=key[0], tid_starttime=key[1], class_name=key[2]))
        elif line.startswith('LC2_COST_V2_END '):
            if active is None:
                raise ValueError('snapshot footer without header')
            footer = fields(line)
            if footer['report'] != active['header']['report'] or int(footer['rows']) != len(active['rows']):
                raise ValueError('snapshot footer/count mismatch')
            active['footer'] = footer
            complete.append(active)
            active = None
    if not complete:
        return {'status': 'no_complete_report', 'coverage_complete': False,
                'note': 'No evidence of zero calls or zero CPU; legacy V1 has unreported TLS tails.'}
    current = complete[-1]
    rows = current['rows']
    covered = (not active and not int(current['header']['overflow']) and
               not int(current['header']['identity_failures']) and
               not int(current['footer']['incomplete_snapshots']) and
               all(r['entered'] == r['completed'] and not r['invalid'] and not r['nesting_errors'] for r in rows))
    classes = {}
    for row in rows:
        target = classes.setdefault(row['class_name'], {'entered': 0, 'completed': 0,
            'valid': 0, 'invalid': 0, 'cpu_inclusive_ns': 0, 'cpu_exclusive_ns': 0})
        for key in target:
            target[key] += row[key]
    return {'status': 'ok', 'report': int(current['header']['report']),
            'complete_snapshots': len(complete), 'trailing_incomplete_snapshot': active is not None,
            'coverage_complete': covered, 'registered_threads': int(current['header']['slots']),
            'snapshot_header': current['header'], 'snapshot_footer': current['footer'],
            'aggregate_is_lower_bound': not covered,
            'reporting_threads': len({(r['tid'], r['tid_starttime']) for r in rows}),
            'classes': classes, 'rows': rows,
            'total_measured_exclusive_cpu_ns': sum(r['cpu_exclusive_ns'] for r in rows),
            'scope': 'measured handlers only, not a complete frame/bridge/process profile',
            'profiler_overhead_qualified': False,
            'wall_policy': 'raw per-thread intervals; not added as elapsed time; no CPU flooring'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('log', type=Path)
    args = ap.parse_args()
    print(json.dumps(summarize(args.log.read_text(errors='replace')), indent=2))


if __name__ == '__main__':
    main()

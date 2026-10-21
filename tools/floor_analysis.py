"""Reproducible menu-floor analysis (owner roadmap 48 / M1).

Answers one question with arithmetic instead of opinion: given a measured menu
memory series and the configured floor, when does the run cross the floor, and
which resource classes produced the drawdown. Inputs are ledger records already
captured on device; this module never invents a value it was not given.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Series:
    frames: list
    seconds: list
    available_mib: list
    swap_used_mib: list
    cma_free_mib: list
    charged_mib: list


def series_from_records(records):
    """Build a Series from ledger records; missing fields stay None, never 0."""
    def pick(record, key):
        value = record.get(key)
        return None if value is None else float(value)

    return Series(frames=[int(r['frames']) for r in records],
                  seconds=[float(r['t_ms']) / 1000.0 for r in records],
                  available_mib=[float(r['available_kib']) / 1024.0 for r in records],
                  swap_used_mib=[float(r['vmswap_kib']) / 1024.0 for r in records],
                  cma_free_mib=[float(r['cmafree_kib']) / 1024.0 for r in records],
                  charged_mib=[float(r['charged']) / 1048576.0 for r in records])


def analyse(series, floor_mib, measured_stop_frame=None):
    """Drawdown, floor-crossing projection and class deltas for one arm."""
    if len(series.frames) < 2:
        return {'analysable': False, 'reason': 'need at least two ledger records'}
    start_available = series.available_mib[0]
    lowest_index = min(range(len(series.available_mib)), key=lambda i: series.available_mib[i])
    low_available = series.available_mib[lowest_index]
    elapsed = series.seconds[lowest_index] - series.seconds[0]
    drawn = start_available - low_available
    rate = drawn / elapsed if elapsed > 0 else None
    margin = start_available - floor_mib
    projection = None
    if rate and rate > 0:
        seconds_to_floor = margin / rate
        # frames per second over the same window, so the crossing can be expressed
        # in frames as well as seconds
        frame_span = series.frames[lowest_index] - series.frames[0]
        fps = frame_span / elapsed if elapsed > 0 else None
        projection = {'seconds': round(seconds_to_floor, 2),
                      'frames': round(frame_span * seconds_to_floor / elapsed, 1) if fps else None,
                      'rate_mib_per_s': round(rate, 2), 'fps': round(fps, 2) if fps else None}
    return {'analysable': True,
            'start_available_mib': round(start_available, 1),
            'low_available_mib': round(low_available, 1),
            'low_at_frame': series.frames[lowest_index],
            'low_at_s': round(series.seconds[lowest_index], 1),
            'drawn_mib': round(drawn, 1),
            'floor_mib': floor_mib,
            'margin_mib': round(margin, 1),
            'projection': projection,
            'measured_stop_frame': measured_stop_frame,
            'floor_reached_in_window': low_available <= floor_mib,
            'cma_start_mib': round(series.cma_free_mib[0], 2),
            'cma_low_mib': round(min(series.cma_free_mib), 2),
            'swap_start_mib': round(series.swap_used_mib[0], 1),
            'swap_end_mib': round(series.swap_used_mib[-1], 1),
            'charged_delta_mib': round(series.charged_mib[-1] - series.charged_mib[0], 1)}


def explain(result):
    """One sentence a report can quote, with the numbers it used."""
    if not result.get('analysable'):
        return 'not analysable: ' + result.get('reason', 'unknown')
    projection = result.get('projection') or {}
    parts = ['start %.1f MiB, low %.1f MiB at frame %d (%.1f s), drawdown %.1f MiB'
             % (result['start_available_mib'], result['low_available_mib'],
                result['low_at_frame'], result['low_at_s'], result['drawn_mib'])]
    if projection:
        parts.append('rate %.2f MiB/s at %.2f fps projects the %.0f MiB floor in %.2f s (~%s frames)'
                     % (projection['rate_mib_per_s'], projection['fps'] or 0, result['floor_mib'],
                        projection['seconds'], projection['frames']))
    if result.get('measured_stop_frame') is not None:
        parts.append('measured stop at frame %d' % result['measured_stop_frame'])
    parts.append('CMA %.2f -> %.2f MiB, swap %.1f -> %.1f MiB, charged textures %+.1f MiB'
                 % (result['cma_start_mib'], result['cma_low_mib'], result['swap_start_mib'],
                    result['swap_end_mib'], result['charged_delta_mib']))
    return '; '.join(parts)

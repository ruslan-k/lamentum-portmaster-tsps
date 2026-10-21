"""Floor-crossing analysis: arithmetic on measured series, no invented values."""
import unittest

import floor_analysis as fa


def records(points):
    """points: (t_ms, frames, available_kib, cma_kib, vmswap_kib, charged_bytes)"""
    return [{'t_ms': t, 'frames': f, 'available_kib': a, 'cmafree_kib': c,
             'vmswap_kib': s, 'charged': b} for t, f, a, c, s, b in points]


class FloorAnalysisTests(unittest.TestCase):
    def test_projection_reproduces_the_measured_early_stop(self):
        # shape of the real menu arm: 129 MiB start, ~17 MiB/s, ~2 fps, floor 96
        rows = records([(0, 1, 132368, 24916, 0, 112325632),
                        (147, 2, 119928, 53864, 0, 112329728),
                        (1312, 7, 111032, 43428, 22264, 115278848),
                        (4500, 16, 56000, 1000, 300000, 160000000)])
        result = fa.analyse(fa.series_from_records(rows), floor_mib=96, measured_stop_frame=2)
        self.assertTrue(result['analysable'])
        self.assertLess(result['projection']['seconds'], 5.0,
                        'the 96 MiB floor must be crossed within seconds, explaining the frame-2 stop')
        self.assertLess(result['projection']['frames'], 10.0)
        text = fa.explain(result)
        self.assertIn('frame 2', text)
        self.assertIn('CMA', text)

    def test_a_flat_series_projects_no_crossing(self):
        rows = records([(0, 1, 200000, 20000, 0, 0), (1000, 30, 200000, 20000, 0, 0)])
        result = fa.analyse(fa.series_from_records(rows), floor_mib=96)
        self.assertIsNone(result['projection'])
        self.assertFalse(result['floor_reached_in_window'])

    def test_one_record_is_refused(self):
        self.assertFalse(fa.analyse(fa.series_from_records(records([(0, 1, 1, 1, 1, 1)])), 96)['analysable'])

    def test_floor_already_breached_is_reported_not_projected(self):
        rows = records([(0, 1, 90000, 1000, 0, 0), (1000, 5, 50000, 0, 100, 0)])
        result = fa.analyse(fa.series_from_records(rows), floor_mib=96)
        self.assertTrue(result['floor_reached_in_window'])
        self.assertEqual(result['low_at_frame'], 5)

    def test_missing_values_are_not_zeroed(self):
        rows = [{'frames': 1, 't_ms': 0, 'available_kib': 100000, 'vmswap_kib': 0, 'cmafree_kib': 0, 'charged': 0},
                {'frames': 2, 't_ms': 1000, 'available_kib': 50000, 'vmswap_kib': 0, 'cmafree_kib': 0, 'charged': 0}]
        result = fa.analyse(fa.series_from_records(rows), floor_mib=40)
        self.assertTrue(result['analysable'])
        self.assertEqual(result['drawn_mib'], 48.8)


if __name__ == '__main__':
    unittest.main()

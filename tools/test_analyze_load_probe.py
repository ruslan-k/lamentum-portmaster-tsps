import unittest
from analyze_load_probe import summarize
from load_probe import pick_action


def row(t, avail, frame, textures, presents, **extra):
    r = {'t': t, 'mem': {'MemTotal': 986064, 'MemAvailable': avail, 'SwapFree': 2000000, 'CmaFree': 1300},
         'frame': frame, 'textures': textures, 'presents': presents, 'romfs': 10, 'bc_deferred': 0,
         'bc_fileback': 0, 'stops': [], 'killed': False, 'entry45': 0, 'unknown': 0}
    r.update(extra)
    return r


class LoadProbeSummaryTests(unittest.TestCase):
    def test_trend_and_minimum(self):
        rows = [row(0, 600000, 10, 5, 10), row(30, 300000, 20, 40, 20), row(60, 420000, 30, 60, 30)]
        s = summarize(rows)
        self.assertEqual(s['samples'], 3)
        self.assertEqual(s['min_available_kb'], 300000)
        self.assertEqual(s['counter_delta']['textures'], 55)
        self.assertEqual(s['frames'], {'first': 10, 'last': 30})
        self.assertEqual(s['span_s'], 60.0)

    def test_failed_polls_are_counted_not_used(self):
        rows = [row(0, 500000, 1, 0, 1), {'error': 'ssh', 't': 5}, row(10, 400000, 2, 1, 2)]
        s = summarize(rows)
        self.assertEqual((s['samples'], s['usable'], s['errors']), (3, 2, 1))
        self.assertEqual(s['min_available_kb'], 400000)

    def test_kill_and_stops_are_reported_separately(self):
        rows = [row(0, 100000, 1, 0, 1, killed=True, stops=['STOP status=ZERO_SHADER_NOT_PINNED'])]
        s = summarize(rows)
        self.assertTrue(s['killed'])
        self.assertEqual(s['stops'], ['STOP status=ZERO_SHADER_NOT_PINNED'])

    def test_no_samples_is_zero_not_crash(self):
        self.assertEqual(summarize([]), {'samples': 0, 'usable': 0, 'errors': 0})


class PickActionTests(unittest.TestCase):
    def test_invisible_cursor_never_nudges(self):
        self.assertIsNone(pick_action(None))

    def test_direction_from_the_measured_row(self):
        self.assertEqual(pick_action((425, 453)), 'down')
        self.assertEqual(pick_action((475, 503)), 'here')
        self.assertEqual(pick_action((575, 603)), 'up')


if __name__ == '__main__':
    unittest.main()

import unittest
from device_principal_test import should_hard_stop, is_killed_without_stop


class HardStopTests(unittest.TestCase):
    def test_stops_only_past_deadline_with_a_live_game(self):
        self.assertTrue(should_hard_stop(100, 90, [4321]))
        self.assertFalse(should_hard_stop(100, 120, [4321]))
        self.assertFalse(should_hard_stop(100, 90, []))

    def test_disabled_bound_never_kills(self):
        self.assertFalse(should_hard_stop(10 ** 9, None, [4321]))
        self.assertFalse(should_hard_stop(10 ** 9, 0, [4321]))


class KillClassificationTests(unittest.TestCase):
    def test_sigkill_without_stop_is_the_oom_path(self):
        log = 'AUDOUT_HOST_PROFILE ...\n... Lamentum.sh: line 56: 26250 Killed                  ./lamentum-nextos\n'
        self.assertTrue(is_killed_without_stop(log, []))

    def test_a_real_stop_is_not_reclassified(self):
        self.assertFalse(is_killed_without_stop('Killed\nSTOP status=TIME_LIMIT', ['TIME_LIMIT']))

    def test_normal_exit_is_not_a_kill(self):
        self.assertFalse(is_killed_without_stop('NATIVE_PROBE_TIME_BUDGET seconds=900\n', []))


if __name__ == '__main__':
    unittest.main()

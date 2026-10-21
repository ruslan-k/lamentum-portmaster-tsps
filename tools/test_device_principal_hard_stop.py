import unittest
from device_principal_test import should_hard_stop, is_killed_without_stop


import device_principal_test as principal


class OwnedLaunchTests(unittest.TestCase):
    def test_uuid_is_explicit_and_reserved_env_cannot_replace_it(self):
        self.assertTrue(hasattr(principal, 'launch_command'), 'owned principal launch contract is missing')
        uuid = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        command = principal.launch_command(uuid, 90, ['T2_TEXTURE_BUDGET_MIB=300'])
        self.assertIn('LAMENTUM_RUN_UUID=' + uuid, command)
        self.assertIn('LAMENTUM_PROBE_SECONDS=90', command)
        self.assertIn('/mnt/SDCARD/Emu/PORTS/../../', command)
        for value in ('LAMENTUM_RUN_UUID=wrong', 'LAMENTUM_PROBE_SECONDS=0', 'bad=value'):
            with self.assertRaises(ValueError):
                principal.launch_command(uuid, 90, [value])
        with self.assertRaises(ValueError):
            principal.launch_command('123', 90, [])
        with self.assertRaises(ValueError):
            principal.launch_command(uuid, 0, [])


class HardStopTests(unittest.TestCase):
    def test_rejected_or_racing_stop_is_not_claimed_as_a_delivered_host_term(self):
        self.assertTrue(hasattr(principal, 'confirmed_host_termination'), 'pidfd receipt qualification is missing')
        for result in ({'outcome': 'already_exited'}, {'outcome': 'identity_mismatch'},
                       {'outcome': 'pidfd_unavailable'}, {'outcome': 'pidfd_error'}):
            self.assertIsNone(principal.confirmed_host_termination(result))
        delivered = {'outcome': 'pidfd_TERM'}
        self.assertIs(principal.confirmed_host_termination(delivered), delivered)

    def test_stops_only_past_deadline_with_a_live_game(self):
        self.assertTrue(should_hard_stop(100, 90, [4321]))
        self.assertFalse(should_hard_stop(100, 120, [4321]))
        self.assertFalse(should_hard_stop(100, 90, []))

    def test_disabled_bound_never_kills(self):
        self.assertFalse(should_hard_stop(10 ** 9, None, [4321]))
        self.assertFalse(should_hard_stop(10 ** 9, 0, [4321]))


class KillClassificationTests(unittest.TestCase):
    def test_sigkill_without_stop_is_only_a_cause_unknown_hint(self):
        log = 'AUDOUT_HOST_PROFILE ...\n... Lamentum.sh: line 56: 26250 Killed                  ./lamentum-nextos\n'
        self.assertTrue(is_killed_without_stop(log, []))

    def test_a_real_stop_is_not_reclassified(self):
        self.assertFalse(is_killed_without_stop('Killed\nSTOP status=TIME_LIMIT', ['TIME_LIMIT']))

    def test_normal_exit_is_not_a_kill(self):
        self.assertFalse(is_killed_without_stop('NATIVE_PROBE_TIME_BUDGET seconds=900\n', []))


if __name__ == '__main__':
    unittest.main()

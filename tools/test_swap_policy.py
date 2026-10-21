import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from swap_policy import apply_plan, parse_swaps, zram_first

# The real ordering measured on the TSPS: the SD-card file swap outranks RAM.
DEVICE = '''Filename\t\t\t\tType\t\tSize\t\tUsed\t\tPriority
/mnt/UDISK/swapfile                     file\t\t1048572\t\t1756\t\t-2
/mnt/sdcard/mmcblk1p1/cachefile         file\t\t524284\t\t33472\t\t40
/dev/zram0                              partition\t493028\t\t0\t\t-3
'''


class SwapPolicyTests(unittest.TestCase):
    def test_parses_the_device_ordering_and_sees_the_file_swap_first(self):
        rows = parse_swaps(DEVICE)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[2], {'filename': '/dev/zram0', 'type': 'partition', 'size_kb': 493028,
                                   'used_kb': 0, 'priority': -3})
        self.assertFalse(zram_first(rows, '/dev/zram0'))       # the defect under test

    def test_raise_plan_refuses_a_live_device(self):
        rows = parse_swaps(DEVICE.replace('493028\t\t0\t\t-3', '493028\t\t4096\t\t-3'))
        with self.assertRaises(ValueError):
            apply_plan('/dev/zram0', 100, rows)

    def test_raise_plan_refuses_a_missing_or_file_device(self):
        rows = parse_swaps(DEVICE)
        with self.assertRaises(ValueError):
            apply_plan('/dev/zram9', 100, rows)
        with self.assertRaises(ValueError):
            apply_plan('/mnt/UDISK/swapfile', 100, rows)

    def test_raise_plan_is_exactly_two_verified_commands(self):
        plan = apply_plan('/dev/zram0', 100, parse_swaps(DEVICE))
        self.assertEqual(plan, [['swapoff', '/dev/zram0'], ['swapon', '-p', '100', '/dev/zram0']])

    def test_zram_first_after_the_change_and_restore_returns_to_the_file_first_state(self):
        raised = parse_swaps(DEVICE.replace('0\t\t-3', '0\t\t100'))
        self.assertTrue(zram_first(raised, '/dev/zram0'))
        self.assertFalse(zram_first(parse_swaps(DEVICE), '/dev/zram0'))


if __name__ == '__main__':
    unittest.main()

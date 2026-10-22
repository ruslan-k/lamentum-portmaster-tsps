import copy
import json
from pathlib import Path
import unittest
from lamentum_pad_contract import ACTIONS, parse_stat, validate_cleanup


class PadContractTests(unittest.TestCase):
    def test_mapping_matches_published_receipt(self):
        actions = json.loads((Path(__file__).resolve().parents[1] / 'evidence/ui-cbuf-fixed-01/control-actions.json').read_text())['actions']
        confirm = next(a for a in actions if a.get('result') == 'Options page opens')
        back = next(a for a in actions if a.get('result') == 'Back returns to main menu')
        self.assertEqual(ACTIONS['confirm'], (1, confirm['code'], 1))
        self.assertEqual(ACTIONS['back'], (1, back['code'], 1))
        self.assertNotEqual(ACTIONS['confirm'], ACTIONS['back'])

    def test_owned_input_and_capture_reject_a_changed_process_before_action(self):
        import lamentum_pad_contract as pad
        from unittest.mock import patch
        self.assertTrue(hasattr(pad, 'set_expected_owner'), 'owned control boundary is missing')
        owner = {'boot_id': 'fixture-boot', 'pid': 77, 'starttime': 42, 'elf_dev': 1, 'elf_ino': 2}
        pad.set_expected_owner(owner)
        try:
            for action in (lambda: pad.press('confirm', 700), lambda: pad.capture('/unused/no-image.png')):
                with patch.object(pad, 'remote', return_value={'running': False, 'sample_status': 'identity_mismatch'}) as rpc:
                    with self.assertRaisesRegex(RuntimeError, 'owned process'):
                        action()
                    self.assertEqual(rpc.call_count, 1)
                    self.assertIn('collect_proc', rpc.call_args.args[0])
        finally:
            pad.set_expected_owner(None)

    def test_stat_name_with_spaces_and_parentheses(self):
        s = '123 (a (b) c) ' + ' '.join(['S'] + ['0'] * 18 + ['456'] + ['0'] * 5)
        self.assertEqual(parse_stat(s), {'pid': 123, 'starttime': 456})

    def test_cleanup_contract(self):
        b = {'processes': {n: [{'pid': i, 'starttime': i * 5}] for i, n in enumerate(['MainUI', 'principal.sh', 'runtime.sh'], 1)}, 'game': [], 'online': '4-7', 'boot_id': 'fixture-boot', 'cpu_sysfs': {str(i): {'online': '0', 'mode': '444'} for i in range(4)}}
        a = copy.deepcopy(b)
        a['processes']['MainUI'][0]['pid'] = 999
        self.assertEqual(validate_cleanup(b, a), [])
        for key in ('MainUI', 'principal.sh', 'runtime.sh'):
            bad = copy.deepcopy(a); bad['processes'][key] = []
            self.assertTrue(validate_cleanup(b, bad))
        bad = copy.deepcopy(a); bad['game'] = [{'pid': 10, 'starttime': 50}]
        self.assertIn('game process remains', validate_cleanup(b, bad))
        bad = copy.deepcopy(a); bad['online'] = '0-7'
        self.assertIn('CPU online mask not restored', validate_cleanup(b, bad))
        bad = copy.deepcopy(a); bad['cpu_sysfs']['0']['mode'] = '644'
        self.assertIn('CPU online values or sysfs modes not restored', validate_cleanup(b, bad))
        bad = copy.deepcopy(a); bad['boot_id'] = 'different-boot'
        self.assertIn('device boot changed during run', validate_cleanup(b, bad))


if __name__ == '__main__':
    unittest.main()

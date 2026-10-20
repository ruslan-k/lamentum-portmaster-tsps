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

    def test_stat_name_with_spaces_and_parentheses(self):
        s = '123 (a (b) c) ' + ' '.join(['S'] + ['0'] * 18 + ['456'] + ['0'] * 5)
        self.assertEqual(parse_stat(s), {'pid': 123, 'starttime': 456})

    def test_cleanup_contract(self):
        b = {'processes': {n: [{'pid': i, 'starttime': i * 5}] for i, n in enumerate(['MainUI', 'principal.sh', 'runtime.sh'], 1)}, 'game': [], 'online': '4-7'}
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


if __name__ == '__main__':
    unittest.main()

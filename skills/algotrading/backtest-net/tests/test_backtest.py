import copy
from decimal import Decimal as D
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('backtest', ROOT/'scripts/backtest.py')
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)


class BacktestTests(unittest.TestCase):
    def setUp(self):
        self.bars = bt.read_bars(ROOT/'fixtures/bars.csv')
        self.fees = json.loads((ROOT/'fixtures/fees-demo.json').read_text())

    def test_next_open_and_cash_identity(self):
        result = bt.run(self.bars, slippage_bps=0)
        self.assertEqual([x['price'] for x in result['fills']], ['105', '109'])
        self.assertEqual(result['final_equity'], '10040')
        for row in result['equity']:
            self.assertEqual(D(row['cash'])+D(row['mark_price'])*row['position_units'], D(row['equity']))

    def test_adverse_slippage_changes_both_sides(self):
        result = bt.run(self.bars, slippage_bps=10)
        self.assertEqual([D(x['price']) for x in result['fills']], [D('105.105'),D('108.891')])
        self.assertEqual(D(result['final_equity']), D('10037.860'))

    def test_future_targets_do_not_change_earlier_fills(self):
        changed = copy.deepcopy(self.bars)
        changed[-1]['target'] = 1
        self.assertEqual(bt.run(changed)['fills'], bt.run(self.bars)['fills'])

    def test_open_position_is_marked_not_liquidated(self):
        result = bt.run(self.bars[:3], slippage_bps=0)
        self.assertEqual(len(result['fills']), 1)
        self.assertEqual(result['equity'][-1]['position_units'], 10)
        self.assertEqual(D(result['final_equity']), D('10060'))

    def test_insufficient_cash_does_not_invent_leverage(self):
        result = bt.run(self.bars, initial_cash=100)
        self.assertEqual(result['fills'], [])
        self.assertTrue(result['rejections'])

    def test_zero_fees_equal_gross(self):
        zero = copy.deepcopy(self.fees)
        for rule in zero['rules']:
            for component in rule['components']:
                component['rate'] = '0'
        net = bt.run(self.bars, mode='net', schedule=zero, allow_demo=True)
        gross = bt.run(self.bars)
        self.assertEqual(D(net['final_equity']), D(gross['final_equity']))

    def test_effective_date_and_side_rules(self):
        old_id, old = bt.charge(self.fees, '2025-01-05','SELL',D('1000'),allow_demo=True)
        new_id, new = bt.charge(self.fees, '2025-01-06','SELL',D('1000'),allow_demo=True)
        _, buy = bt.charge(self.fees, '2025-01-06','BUY',D('1000'),allow_demo=True)
        self.assertNotEqual(old_id, new_id)
        self.assertEqual(old['sell_tax'],D('2'))
        self.assertEqual(new['sell_tax'],D('3'))
        self.assertEqual(buy['sell_tax'],D('0'))
        self.assertEqual(buy['buy_stamp'],D('0.10'))

    def test_cap_and_dependent_tax(self):
        _, costs = bt.charge(self.fees,'2025-01-06','BUY',D('100000'),allow_demo=True)
        self.assertEqual(costs['brokerage'],D('2'))
        self.assertEqual(costs['fee_tax'],D('0.20'))

    def test_net_cash_reconciles_with_charges(self):
        gross = bt.run(self.bars,slippage_bps=0)
        net = bt.run(self.bars,mode='net',schedule=self.fees,allow_demo=True,slippage_bps=0)
        # Per-component half-up rounding: buy 1.05 + .11 + .11; sell 1.09 + 3.27 + .11.
        self.assertEqual(D(net['total_charges']),D('5.74'))
        self.assertEqual(D(gross['final_equity'])-D(net['final_equity']),D(net['total_charges']))

    def test_demo_requires_explicit_flag(self):
        with self.assertRaises(ValueError):
            bt.run(self.bars,mode='net',schedule=self.fees)

    def test_uncovered_dates_and_overlapping_rules_fail(self):
        with self.assertRaises(ValueError):
            bt.charge(self.fees,'2026-01-01','BUY',D('100'),allow_demo=True)
        self.fees['rules'].append(copy.deepcopy(self.fees['rules'][0]))
        with self.assertRaises(ValueError):
            bt.charge(self.fees,'2025-01-03','BUY',D('100'),allow_demo=True)

    def test_nan_and_unsupported_target_are_rejected(self):
        with self.assertRaises(ValueError):
            bt.decimal('NaN')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'bad.csv'
            text = (ROOT/'fixtures/bars.csv').read_text()
            path.write_text(text.replace(',102,1', ',102,2'))
            with self.assertRaises(ValueError):
                bt.read_bars(path)

    def test_naive_timestamps_are_rejected(self):
        with self.assertRaises(ValueError):
            bt.timestamp('2025-01-02T09:15:00')


if __name__ == '__main__':
    unittest.main()

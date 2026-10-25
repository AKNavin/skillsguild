"""Independent synthetic accounting and causal-data checks (no broker credentials)."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import engine
import panel
import runner
import signals


def dates(n, start='2023-01-02'):
    current = date.fromisoformat(start)
    result = []
    while len(result) < n:
        if current.weekday() < 5:
            result.append(current.isoformat())
        current += timedelta(days=1)
    return result


def synthetic(n=560, stocks=12, start='2023-01-02'):
    t = np.arange(n)[:, None]
    j = np.arange(stocks)[None, :]
    close = 100 + .025 * (j + 1) * t + 3 * np.sin(t * .17 + j)
    market = 1000 + np.arange(n) * .4 + 12 * np.sin(np.arange(n) * .13)
    return dict(dates=dates(n, start), symbols=[f'S{j:03}' for j in range(stocks)],
                open=close * .998, high=close * 1.015, low=close * .985, close=close,
                volume=np.full(close.shape, 1000), mark=close.copy(),
                market_close=market, market_open=market * .999, n50_close=market * 2,
                n50_open=market * 1.998, industries=['Industry' + str(j // 6) for j in range(stocks)])


def write_dataset(root, n=65):
    p = synthetic(n=n, stocks=100)
    (root / 'data').mkdir(parents=True)
    universe = {'current_only': True, 'items': {s: {'kind': 'stock', 'industry': p['industries'][j]} for j, s in enumerate(p['symbols'])}}
    (root / 'Universe.json').write_text(json.dumps(universe))
    (root / 'Data-quality-quarantine.json').write_text(json.dumps({'symbols': []}))
    for j, symbol in enumerate(p['symbols']):
        rows = [dict(date=d, **{k: float(p[k][i, j]) for k in panel.FIELDS}) for i, d in enumerate(p['dates'])]
        (root / 'data' / (symbol + '.json')).write_text(json.dumps(rows))
    for symbol in ['NIFTY_500', 'NIFTY_50']:
        rows = [dict(date=d, open=float(p['market_open'][i]), close=float(p['market_close'][i]),
                     high=float(p['market_close'][i] * 1.02), low=float(p['market_close'][i] * .98), volume=0)
                for i, d in enumerate(p['dates'])]
        (root / 'data' / (symbol + '.json')).write_text(json.dumps(rows))
    return p


class SignalTests(unittest.TestCase):
    def test_all_twelve_signals_ignore_future_candles(self):
        p = synthetic()
        changed = {k: v.copy() if hasattr(v, 'copy') else v for k, v in p.items()}
        t = 520
        for key in ['open', 'high', 'low', 'close', 'volume', 'mark', 'market_close', 'market_open', 'n50_close', 'n50_open']:
            changed[key][t + 1:] *= 50
        for strategy in runner.frozen_strategies().values():
            c = strategy['configuration']
            with self.subTest(family=c['family']):
                a = signals.score_at(p, t, c['family'], c['lookback'])
                b = signals.score_at(changed, t, c['family'], c['lookback'])
                np.testing.assert_array_equal(a, b)

    def test_high52_uses_highs_including_signal_session(self):
        p = synthetic(n=260, stocks=2)
        p['high'][:] = 100
        p['close'][:] = 90
        p['high'][251, 1] = 200
        np.testing.assert_allclose(signals.score_at(p, 251, 'high52', 252), [.9, .45])

    def test_mad_and_smad_hand_formula(self):
        p = synthetic(n=210, stocks=2)
        p['close'][:, 0] = np.arange(1, 211)
        score = signals.score_at(p, 199, 'mad', 50)
        self.assertAlmostEqual(score[0], np.mean(np.arange(151, 201)) / np.mean(np.arange(1, 201)))
        score = signals.score_at(p, 199, 'smad', 10)
        self.assertAlmostEqual(score[0], -200 / np.mean(np.arange(191, 201)))

    def test_unknown_family_is_rejected(self):
        with self.assertRaises(ValueError):
            signals.score_at(synthetic(), 520, 'invented', 1)


class AccountingTests(unittest.TestCase):
    def fixture(self):
        p = synthetic(n=12, stocks=1)
        for key in ['open', 'high', 'low', 'close', 'mark']:
            p[key][:] = 100
        c = dict(id='fixture', family='absolute', lookback=1, n=1, months=6)
        cache = {(1, 'absolute', 1): np.array([1.])}
        return p, c, cache

    def test_delayed_buy_and_terminal_costs_equal_hand_calculation(self):
        p, c, cache = self.fixture()
        result = engine.run(p, cache, c, p['dates'][2], p['dates'][10], detail=True)
        expected_qty = 100 / (100 * 1.0005 * (1 + engine.BUY_RATE))
        expected_equity = expected_qty * 100 * .9995 * (1 - engine.SELL_RATE)
        self.assertEqual(result['orders'][0]['date'], p['dates'][4])
        self.assertEqual(result['orders'][0]['signal_date'], p['dates'][1])
        self.assertAlmostEqual(result['orders'][0]['qty'], expected_qty)
        self.assertEqual(result['orders'][-1]['reason'], 'terminal_estimate')
        self.assertAlmostEqual(result['ending_equity'], expected_equity)
        self.assertAlmostEqual(result['accounting_residual'], 0)

    def test_zero_cost_zero_slippage_flat_market_conserves_equity(self):
        p, c, cache = self.fixture()
        result = engine.run(p, cache, c, p['dates'][2], p['dates'][10], detail=True, costs=False, slip=0)
        np.testing.assert_array_equal(result['equity'], [100.] * 9)
        self.assertEqual(result['fees_equity_points'], 0)
        self.assertEqual(result['slippage_equity_points'], 0)

    def test_zero_volume_buy_is_skipped(self):
        p, c, cache = self.fixture()
        p['volume'][4, 0] = 0
        result = engine.run(p, cache, c, p['dates'][2], p['dates'][10], detail=True)
        self.assertEqual(result['orders'], [])
        self.assertEqual(len(result['skipped_events']), 1)
        self.assertEqual(result['ending_equity'], 100)

    def test_two_session_sale_settlement_funds_replacement(self):
        p = synthetic(n=40, stocks=2)
        c = dict(id='fixture', family='absolute', lookback=1, n=1, months=1)
        boundary = next(i for i in range(3, len(p['dates'])) if p['dates'][i][:7] != p['dates'][i - 1][:7])
        cache = {(1, 'absolute', 1): np.array([1., 0.]), (boundary - 1, 'absolute', 1): np.array([0., 1.])}
        result = engine.run(p, cache, c, p['dates'][2], p['dates'][-1], detail=True)
        sales = [o for o in result['orders'] if o['reason'] == 'rebalance' and o['side'] == 'SELL']
        buys = [o for o in result['orders'] if o['side'] == 'BUY']
        self.assertEqual(sales[0]['date'], p['dates'][boundary])
        self.assertEqual(buys[1]['date'], p['dates'][boundary + 2])
        ledger = {r['date']: r for r in result['ledger']}
        self.assertGreater(ledger[p['dates'][boundary]]['unsettled_cash'], 0)
        self.assertGreater(ledger[p['dates'][boundary + 1]]['unsettled_cash'], 0)
        self.assertEqual(ledger[p['dates'][boundary + 2]]['unsettled_cash'], 0)
        for row in result['ledger']:
            self.assertAlmostEqual(row['equity'], row['free_cash'] + row['unsettled_cash'] + row['position_value'])
            self.assertGreaterEqual(row['free_cash'], -1e-8)

    def test_replay_does_not_read_beyond_end(self):
        p = synthetic()
        c = runner.frozen_strategies()['smad']['configuration']
        a = engine.run(p, {}, c, p['dates'][300], p['dates'][500], detail=True)
        for key in ['open', 'high', 'low', 'close', 'mark', 'volume']:
            p[key][501:] *= 100
        b = engine.run(p, {}, c, p['dates'][300], p['dates'][500], detail=True)
        self.assertEqual(a, b)


class PanelAndCliTests(unittest.TestCase):
    def test_dates_and_warmup_errors(self):
        for invalid in ['2026-02-30', '2026-1-01', None]:
            with self.assertRaises(ValueError):
                panel.iso_date(invalid)
        p = synthetic()
        c = runner.frozen_strategies()['residual']['configuration']
        with self.assertRaisesRegex(ValueError, 'warm-up'):
            panel.validate_window(p, c, p['dates'][400], p['dates'][-1])
        with self.assertRaisesRegex(ValueError, 'after end'):
            panel.validate_window(p, c, '2029-01-01', '2028-01-01')
        with self.assertRaisesRegex(ValueError, 'cutoff'):
            panel.validate_window(p, c, p['dates'][510], '2029-01-01')

    def test_invalid_ohlc_and_duplicate_dates_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'bad.json'
            row = dict(date='2026-01-01', open=100, high=101, low=99, close=100, volume=100)
            for content in [[row, row], [dict(row, high=90)], [dict(row, volume=-1)], [dict(row, close=float('nan'))]]:
                file.write_text(json.dumps(content))
                with self.assertRaises(ValueError):
                    panel.read_rows(file)

    def test_cli_and_api_match_without_input_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            root = temp / 'cache'
            source = write_dataset(root)
            _, _, before = panel.load_panel(root)
            start, end = source['dates'][15], source['dates'][-1]
            api = runner.execute('smad', root, start, end, temp / 'api')
            command = [sys.executable, '-B', str(HERE / 'runner.py'), '--strategy', 'smad', '--data-dir', str(root), '--start', start, '--end', end, '--output', str(temp / 'cli')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            cli = json.loads((temp / 'cli' / 'results.json').read_text())
            self.assertEqual(api, cli)
            _, _, after = panel.load_panel(root)
            self.assertEqual(before, after)
            manifest = json.loads((temp / 'cli' / 'run-manifest.json').read_text())
            self.assertEqual(manifest['data']['sha256'], before['sha256'])
            self.assertEqual(len(manifest['data']['files']), 104)
            self.assertNotIn(str(temp), json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'outside'):
                runner.execute('smad', root, start, end, root / 'outputs')

    def test_incomplete_shared_session_is_omitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = write_dataset(root)
            file = root / 'data' / 'S000.json'
            rows = json.loads(file.read_text())
            removed = rows.pop(20)['date']
            file.write_text(json.dumps(rows))
            p, audit, _ = panel.load_panel(root)
            self.assertNotIn(removed, p['dates'])
            self.assertEqual(audit['omitted_incomplete_sessions'], [{'date': removed, 'stock_bars': 99}])
            self.assertEqual(len(p['dates']), len(original['dates']) - 1)


if __name__ == '__main__':
    unittest.main()

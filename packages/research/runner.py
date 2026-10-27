"""Reproduce the fifteen frozen study configurations against a private daily panel."""
import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import engine
from panel import load_panel, validate_window

HERE = Path(__file__).resolve().parent
LIMITATIONS = [
    'Current constituent universe and industry classifications introduce survivorship and classification look-ahead; these are not point-in-time universes.',
    '2026 was inspected in prior research and is not an untouched out-of-sample holdout.',
    'Equity starts at 100 and uses fractional stock quantities; this is normalized research, not an executable Indian cash-equity account.',
    'Current percentage charges are applied to all history. Historical tariffs, DP fees, order-level rounding and taxes outside the model are not reconstructed.',
    'Terminal positions are liquidated at an estimated final close with slippage and charges; a terminal estimate is not an observed executable fill.',
    'A current whole-symbol data-quality quarantine is applied across history; corporate-action adjustments, delistings, symbol changes and dividends are not fully reconstructed.',
    'Execution eligibility uses the execution day daily volume; locked-bar stress also uses that day high/low. Those are ex-post daily-bar feasibility assumptions, not facts known at the open.',
    'Missing held closes are carried forward only for valuation. Missing lookback candles are not imputed. Shared sessions with fewer than 100 stock candles are omitted.',
    'Nifty comparisons are uninvestable price-index reference series, without dividends, fees or an execution-delay match.',
]


def frozen_strategies():
    return json.loads((HERE / 'strategies.json').read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def execute(strategy, data_dir, start, end, output, *, quarantine=None, slippage_bps=5.0, costs=True, avoid_locked=False):
    strategies = frozen_strategies()
    if strategy not in strategies:
        raise ValueError('Unknown strategy; choose one of: ' + ', '.join(strategies))
    if not np.isfinite(slippage_bps) or not 0 <= slippage_bps <= 100:
        raise ValueError('Slippage must be between 0 and 100 basis points per side')
    root, output = Path(data_dir).resolve(), Path(output).resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError('Use a separate output directory, outside the input data directory')
    panel, audit, fingerprint = load_panel(root, quarantine)
    config = strategies[strategy]['configuration']
    validate_window(panel, config, start, end)
    report = engine.run(panel, {}, config, start, end, slip=slippage_bps / 10000,
                        costs=costs, detail=True, avoid_locked=avoid_locked)
    report['strategy_id'] = strategy
    report['name'] = strategies[strategy]['name']
    report['schema_version'] = 1
    report['limitations'] = LIMITATIONS
    report['assumptions'] = {
        'initial_equity': 100, 'fractional_quantities': True, 'slippage_bps_per_side': slippage_bps,
        'costs_enabled': costs, 'buy_rate': engine.BUY_RATE if costs else 0,
        'sell_rate': engine.SELL_RATE if costs else 0, 'avoid_locked_bars': avoid_locked,
        'buy_session_offset_from_signal': 3, 'sale_settlement_session_offset': 2,
        'terminal_estimate': True, 'cash_interest_rate': 0,
        'requested_start': start, 'requested_end': end,
    }
    report['data_sha256'] = fingerprint['sha256']
    report['benchmarks'] = {name: engine.benchmark(panel, start, end, name) for name in ['Nifty 500', 'Nifty 50']}
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / 'results.json', report)
    write_json(output / 'panel-audit.json', audit)
    write_csv(output / 'equity.csv', report['ledger'], ['date', 'equity', 'free_cash', 'unsettled_cash', 'position_value', 'positions'])
    write_csv(output / 'orders.csv', report['orders'], ['date', 'symbol', 'side', 'qty', 'reference', 'fill', 'notional', 'fee', 'reason', 'signal_date'])
    write_csv(output / 'trades.csv', report['trades'], ['symbol', 'entry_date', 'exit_date', 'entry', 'exit', 'qty', 'entry_cost', 'net_proceeds', 'net_pnl', 'exit_reason'])
    code = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ['engine.py', 'signals.py', 'panel.py', 'runner.py', 'strategies.json', 'requirements.txt']}
    manifest = {
        'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(), 'strategy_id': strategy,
        'configuration': config, 'requested_start': start, 'requested_end': end,
        'actual_start': report['start'], 'actual_end': report['end'], 'assumptions': report['assumptions'],
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'code_sha256': code, 'data': fingerprint,
        'result_sha256': hashlib.sha256((output / 'results.json').read_bytes()).hexdigest(),
        'source_provenance': json.loads((HERE / 'source-provenance.json').read_text(encoding='utf-8')),
        'privacy': 'No credentials or absolute input paths are recorded. Result trade prices and private data audit must not be published without appropriate rights.',
    }
    write_json(output / 'run-manifest.json', manifest)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog='Uses your local broker-data panel only; this command cannot log in or place orders. Read README.md for the dataset contract and study limitations.')
    parser.add_argument('--strategy', required=True, choices=tuple(frozen_strategies()))
    parser.add_argument('--data-dir', required=True, type=Path, help='Folder containing Universe.json, Data-quality-quarantine.json and data/*.json')
    parser.add_argument('--start', required=True, help='First requested session, YYYY-MM-DD; earlier history must be present for warm-up')
    parser.add_argument('--end', required=True, help='Last requested session, YYYY-MM-DD')
    parser.add_argument('--output', required=True, type=Path, help='Private output folder outside the data folder')
    parser.add_argument('--quarantine', type=Path, help='Optional explicit quarantine metadata path when replaying the original source folder')
    parser.add_argument('--slippage-bps', type=float, default=5.0, help='One-way slippage in basis points; original baseline 5, stress 10')
    parser.add_argument('--no-costs', action='store_true', help='Turn off percentage charges. Slippage remains unless separately set to zero.')
    parser.add_argument('--avoid-locked', action='store_true', help='Stress variant: skip fills when the daily high equals the daily low')
    args = parser.parse_args(argv)
    try:
        report = execute(args.strategy, args.data_dir, args.start, args.end, args.output,
                         quarantine=args.quarantine, slippage_bps=args.slippage_bps,
                         costs=not args.no_costs, avoid_locked=args.avoid_locked)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(2, 'Backtest could not run: ' + str(error) + '\n')
    print(json.dumps({k: report[k] for k in ['strategy_id', 'start', 'end', 'return_pct', 'max_drawdown_pct', 'turnover_orders', 'accounting_residual']}, allow_nan=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

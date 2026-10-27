"""Read the original study's daily panel without modifying its inputs."""
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path

import numpy as np

FIELDS = ('open', 'high', 'low', 'close', 'volume')
SYMBOL = re.compile(r'^[A-Za-z0-9_&.\-]+$')


def iso_date(value):
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('Dates must be YYYY-MM-DD strings')
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('Dates must be YYYY-MM-DD strings')
    return value


def read_rows(path):
    raw = path.read_bytes()
    rows = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(rows, list):
        raise ValueError(f'{path.name}: expected an array of daily candles')
    previous = ''
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f'{path.name}: candle {i} must be an object')
        current = iso_date(row.get('date'))
        if current <= previous:
            raise ValueError(f'{path.name}: dates must be unique and strictly ascending')
        previous = current
        for field in FIELDS:
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{path.name}: {current} has invalid {field}')
            if value < 0 or (field != 'volume' and value == 0):
                raise ValueError(f'{path.name}: {current} has invalid {field}')
        if row['high'] < max(row['open'], row['close'], row['low']) or row['low'] > min(row['open'], row['close']):
            raise ValueError(f'{path.name}: {current} has inconsistent OHLC')
    return rows, hashlib.sha256(raw).hexdigest()


def load_panel(data_dir, quarantine=None):
    """Keep the study's >=100-stock shared calendar and forward-marking rules."""
    root = Path(data_dir).resolve()
    universe_path = root / 'Universe.json'
    quarantine_path = Path(quarantine).resolve() if quarantine else root / 'Data-quality-quarantine.json'
    universe_raw = universe_path.read_bytes()
    quarantine_raw = quarantine_path.read_bytes()
    universe = json.loads(universe_raw.decode('utf-8-sig'))['items']
    excluded_list = json.loads(quarantine_raw.decode('utf-8-sig'))['symbols']
    if not isinstance(universe, dict) or not isinstance(excluded_list, list) or not all(isinstance(x, str) for x in excluded_list):
        raise ValueError('Invalid universe or quarantine metadata')
    excluded = set(excluded_list)
    symbols = sorted(n for n, v in universe.items() if v['kind'] == 'stock' and n not in excluded)
    if len(symbols) < 100:
        raise ValueError('The original study requires at least 100 eligible stocks; a single-symbol CSV is not a compatible panel')
    if any(not SYMBOL.fullmatch(n) or n in ('.', '..') for n in symbols):
        raise ValueError('Universe contains an unsafe symbol filename')
    hashes = {
        'Universe.json': hashlib.sha256(universe_raw).hexdigest(),
        'Data-quality-quarantine.json': hashlib.sha256(quarantine_raw).hexdigest(),
    }
    market, hashes['data/NIFTY_500.json'] = read_rows(root / 'data' / 'NIFTY_500.json')
    if not market:
        raise ValueError('NIFTY_500 calendar is empty')
    dates = [r['date'] for r in market]
    date_index = {d: i for i, d in enumerate(dates)}
    arrays = {k: np.full((len(dates), len(symbols)), np.nan) for k in FIELDS}
    coverage = {}
    anomalies = []
    for j, symbol in enumerate(symbols):
        rows, digest = read_rows(root / 'data' / (symbol + '.json'))
        hashes['data/' + symbol + '.json'] = digest
        for row in rows:
            i = date_index.get(row['date'])
            if i is not None:
                for field, values in arrays.items():
                    values[i, j] = row[field]
        coverage[symbol] = {'first': rows[0]['date'] if rows else None, 'last': rows[-1]['date'] if rows else None, 'candles': len(rows)}
        for a, b in zip(rows, rows[1:]):
            ratio = b['close'] / a['close']
            if (ratio > 1.4 or ratio < .6) and b['date'] >= '2017-01-01':
                anomalies.append({'symbol': symbol, 'date': b['date'], 'ratio': ratio})
    counts = np.isfinite(arrays['close']).sum(axis=1)
    omitted = [{'date': d, 'stock_bars': int(counts[i])} for i, d in enumerate(dates) if counts[i] < 100]
    keep = counts >= 100
    if not keep.any():
        raise ValueError('No shared sessions have at least 100 stock candles')
    arrays = {k: a[keep] for k, a in arrays.items()}
    dates = [d for i, d in enumerate(dates) if keep[i]]
    market = [r for i, r in enumerate(market) if keep[i]]
    mark = arrays['close'].copy()
    for i in range(1, len(dates)):
        mark[i] = np.where(np.isfinite(mark[i]), mark[i], mark[i - 1])
    n50, hashes['data/NIFTY_50.json'] = read_rows(root / 'data' / 'NIFTY_50.json')
    n50map = {r['date']: r for r in n50}
    if any(d not in n50map for d in dates):
        raise ValueError('NIFTY_50 must contain every retained NIFTY_500 calendar session')
    industries = [universe[n].get('industry') for n in symbols]
    if any(not isinstance(x, str) or not x.strip() for x in industries):
        raise ValueError('Every stock needs an industry string in Universe.json')
    panel = dict(**arrays, mark=mark, dates=dates, symbols=symbols, industries=industries,
                 market_close=np.array([r['close'] for r in market]), market_open=np.array([r['open'] for r in market]),
                 n50_close=np.array([n50map[d]['close'] for d in dates]), n50_open=np.array([n50map[d]['open'] for d in dates]))
    audit = {'stocks': len(symbols), 'excluded': sorted(excluded), 'coverage': coverage,
             'extreme_daily_moves': anomalies, 'omitted_incomplete_sessions': omitted,
             'calendar_first': dates[0], 'calendar_last': dates[-1],
             'missing_stock_session_bars': int(np.isnan(arrays['close']).sum()),
             'current_universe_only': True, 'calendar_minimum_stock_bars': 100}
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return panel, audit, {'sha256': fingerprint, 'files': hashes}


def validate_window(panel, config, start, end):
    iso_date(start)
    iso_date(end)
    if start > end:
        raise ValueError('Start date must not be after end date')
    dates = panel['dates']
    indices = [i for i, d in enumerate(dates) if start <= d <= end]
    if not indices:
        raise ValueError('The selected interval has no retained sessions')
    if end > dates[-1]:
        raise ValueError(f'End date exceeds the available data cutoff ({dates[-1]})')
    family, look = config['family'], config['lookback']
    if family in ('intermediate', 'seasonal'):
        # Calendar-month signals need complete prior month endpoints, not a
        # session count inferred from the configuration's months/years unit.
        month = lambda d: int(d[:4])*12+int(d[5:7])-1
        ends = {month(d):i for i,d in enumerate(dates)}
        signal = indices[0]-1
        m = month(dates[signal]) if signal >= 0 else None
        enough = signal >= 0 and (m-12 in ends and m-6 in ends if family == 'intermediate'
                 else sum(m+1-12*y in ends and m-12*y in ends for y in range(1, look+1)) >= 2)
        if not enough:
            raise ValueError(f'Insufficient warm-up: {family} requires prior calendar-month history; seasonality needs at least two complete same-month returns')
        if len(indices) < 2:
            raise ValueError('Select at least two retained sessions')
        return indices
    minimum = (252 if family == 'high52' else 505 if family == 'residual' else
               200 if family == 'mad' else look if family == 'smad' else
               look + 22 if family == 'fip' or family.startswith(('riskmom_', 'industry_')) else look + 1)
    if indices[0] < minimum:
        raise ValueError(f'Insufficient warm-up: {family} requires at least {minimum} retained sessions before the first run session')
    if len(indices) < 2:
        raise ValueError('Select at least two retained sessions')
    return indices

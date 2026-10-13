"""Offline long-only daily cash-equity reference backtester. No network or orders.

Targets use the current completed bar; fills occur at the next bar's opening time.
Fee fixtures are synthetic. Production costs require a verified effective-dated schedule.
"""
import argparse
import csv
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path

D = Decimal
CENT = D('0.01')
IST_OFFSET = timedelta(hours=5, minutes=30)


def decimal(value):
    value = D(str(value))
    if not value.is_finite():
        raise ValueError('Non-finite numeric value')
    return value


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def timestamp(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() != IST_OFFSET:
        raise ValueError('Use explicit Asia/Kolkata offset +05:30')
    return result


def read_bars(path):
    with open(path, newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 2:
        raise ValueError('At least two bars are required')
    bars = []
    for row in rows:
        start, end = timestamp(row['timestamp']), timestamp(row['bar_end'])
        if not start < end or start.date() != end.date():
            raise ValueError('Daily bars need same-date opening and closing times')
        if bars and (start.date() <= bars[-1]['start'].date() or start <= bars[-1]['end']):
            raise ValueError('Daily bars must be strictly chronological without overlap')
        prices = {k: decimal(row[k]) for k in ('open','high','low','close')}
        if min(prices.values()) <= 0:
            raise ValueError('Prices must be positive')
        if not prices['low'] <= min(prices['open'], prices['close']) <= max(prices['open'], prices['close']) <= prices['high']:
            raise ValueError('Invalid OHLC envelope')
        if str(row['target']) not in ('0','1'):
            raise ValueError('Target must be 0 (flat) or 1 (long)')
        bars.append(dict(start=start, end=end, target=int(row['target']), **prices))
    return bars


def charge(schedule, trade_date, side, turnover, exchange='NSE', product='CNC', allow_demo=False):
    if schedule.get('demo') and not allow_demo:
        raise ValueError('Synthetic fee fixture requires --allow-demo')
    matches = [r for r in schedule['rules'] if r['exchange'] == exchange and r['product'] == product
               and r['effective_from'] <= trade_date < r['effective_to']]
    if len(matches) != 1:
        raise ValueError('Exactly one fee schedule must cover each trade date/product/exchange')
    rule = matches[0]
    amounts = {}
    for component in rule['components']:
        name = component['name']
        if name in amounts:
            raise ValueError('Duplicate fee component')
        if side not in component['sides']:
            amounts[name] = D(0)
            continue
        rate = decimal(component['rate'])
        if rate < 0:
            raise ValueError('Negative fee rate is unsupported')
        basis = component['basis']
        if basis == 'turnover':
            base = turnover
        elif basis == 'fixed':
            base = D(1)
        elif basis == 'components':
            try:
                base = sum((amounts[n] for n in component['components']), D(0))
            except KeyError as exc:
                raise ValueError('Tax refers to a missing or later component') from exc
        else:
            raise ValueError('Unsupported fee basis')
        amount = base * rate
        if 'cap' in component:
            cap = decimal(component['cap'])
            if cap < 0:
                raise ValueError('Negative fee cap')
            amount = min(amount, cap)
        amounts[name] = money(amount)
    return rule['id'], amounts


def run(bars, mode='gross', initial_cash='10000', units=10, slippage_bps='5', schedule=None, allow_demo=False):
    if mode not in ('gross','net'):
        raise ValueError('Mode must be gross or net')
    cash, friction = decimal(initial_cash), decimal(slippage_bps) / D(10000)
    if cash <= 0 or not isinstance(units, int) or units <= 0 or not D(0) <= friction < D(1):
        raise ValueError('Positive capital/units and nonnegative slippage below 10000 bps required')
    if mode == 'net' and schedule is None:
        raise ValueError('Net mode requires an effective-dated fee configuration')
    position, total_fees = 0, D(0)
    fills, equity, rejections = [], [], []
    for index, bar in enumerate(bars):
        if index:
            previous = bars[index - 1]
            difference = previous['target'] * units - position
            if difference:
                side = 'BUY' if difference > 0 else 'SELL'
                # A single synthetic market fill; slippage includes spread if requested.
                price = bar['open'] * (1 + friction if side == 'BUY' else 1 - friction)
                turnover = price * abs(difference)
                rule, components = (None, {}) if mode == 'gross' else charge(
                    schedule, bar['start'].date().isoformat(), side, turnover, allow_demo=allow_demo)
                fee = sum(components.values(), D(0))
                if difference > 0 and turnover + fee > cash:
                    rejections.append({'time': bar['start'].isoformat(), 'reason': 'insufficient_cash',
                                       'requested_units': difference})
                else:
                    cash += -turnover - fee if side == 'BUY' else turnover - fee
                    position += difference
                    total_fees += fee
                    fills.append({'order_id': f'offline-{index}', 'signal_time': previous['end'].isoformat(),
                                  'fill_time': bar['start'].isoformat(), 'side': side,
                                  'quantity': abs(difference), 'price': str(price), 'fee_rule': rule,
                                  'charges': {k: str(v) for k,v in components.items()}, 'total_charges': str(fee)})
        marked = bar['close'] * position
        equity.append({'time': bar['end'].isoformat(), 'cash': str(cash), 'position_units': position,
                       'mark_price': str(bar['close']), 'equity': str(cash + marked)})
    return {'manifest': {'mode': mode, 'initial_cash': str(initial_cash), 'fixed_units': units,
                         'slippage_bps': str(slippage_bps), 'fill_rule': 'prior_completed_target_at_next_open',
                         'product': 'CNC', 'exchange': 'NSE', 'fee_demo': bool(schedule and schedule.get('demo')),
                         'terminal_policy': 'mark_open_positions_no_forced_liquidation',
                         'limitations': ['daily_one_equity', 'single_fill_per_order', 'no_partial_fills',
                                         'no_stops_or_targets', 'no_derivatives', 'no_corporate_actions']},
            'fills': fills, 'equity': equity, 'rejections': rejections,
            'total_charges': str(total_fees), 'final_equity': equity[-1]['equity']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bars', type=Path)
    parser.add_argument('--mode', choices=['gross','net'], default='gross')
    parser.add_argument('--fees', type=Path)
    parser.add_argument('--allow-demo', action='store_true')
    parser.add_argument('--initial-cash', default='10000')
    parser.add_argument('--units', type=int, default=10)
    parser.add_argument('--slippage-bps', default='5')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    schedule = json.loads(args.fees.read_text(encoding='utf-8')) if args.fees else None
    result = run(read_bars(args.bars), args.mode, args.initial_cash, args.units,
                 args.slippage_bps, schedule, args.allow_demo)
    result['manifest']['bars_sha256'] = hashlib.sha256(args.bars.read_bytes()).hexdigest()
    result['manifest']['fees_sha256'] = hashlib.sha256(args.fees.read_bytes()).hexdigest() if args.fees else None
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f"{len(result['fills'])} fills; final equity {result['final_equity']}; charges {result['total_charges']}")


if __name__ == '__main__':
    main()

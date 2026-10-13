"""Rank same-expiry OI walls from an offline option-chain CSV. No network or orders.

OI is raw Kite units; convert with each contract's dated lot_size. A wall is a
concentration heuristic, not identified dealer inventory or guaranteed support.
"""
import argparse
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path

D = Decimal
IST = timedelta(hours=5, minutes=30)


def number(value):
    result = D(str(value))
    if not result.is_finite():
        raise ValueError('Non-finite numeric value')
    return result


def instant(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError('Timestamp must have a timezone offset')
    return result


def load_rows(path):
    with open(path, newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def screen(rows, expiry, asof, max_age_seconds=30, band_pct='10', min_oi_lots='100',
           max_spread_pct='5', min_volume_lots='0', expiry_at=None):
    day = date.fromisoformat(expiry)
    now = instant(asof)
    band, minimum, spread_limit, min_volume = map(number, (band_pct,min_oi_lots,max_spread_pct,min_volume_lots))
    if now.utcoffset() != IST:
        raise ValueError('As-of timestamp must use Asia/Kolkata offset +05:30')
    if day < now.date():
        raise ValueError('Selected expiry is already past as-of date')
    if expiry_at:
        end=instant(expiry_at)
        if end.utcoffset()!=IST or end.date()!=day or now>=end:
            raise ValueError('Expiry timestamp must match the selected expiry and be later than as-of')
    elif day==now.date():
        raise ValueError('Supply the verified --expiry-at timestamp on expiry day')
    if max_age_seconds < 0 or min(band, minimum, spread_limit, min_volume) < 0:
        raise ValueError('Thresholds must be nonnegative')
    grouped, seen = {}, set()
    for row in rows:
        if row['expiry'] != expiry:
            continue
        key = (row['underlying'], row['type'], number(row['strike']))
        if row['type'] not in ('CE','PE') or key in seen:
            raise ValueError('Invalid option type or duplicate same-expiry contract key')
        seen.add(key)
        grouped.setdefault(row['underlying'], []).append(row)
    output = []
    for underlying, contracts in sorted(grouped.items()):
        result = {'underlying': underlying, 'expiry': expiry, 'asof': asof,
                  'spot': None, 'call_wall': None, 'put_wall': None,
                  'eligible_counts': {'CE':0,'PE':0}, 'exclusions': [],
                  'input_contract_count':len(contracts)}
        try:
            spots = {number(row['spot']) for row in contracts}
            spot_ages = [(now-instant(row['spot_timestamp'])).total_seconds() for row in contracts]
            if len(spots) != 1 or min(spots) <= 0 or any(age < 0 or age > max_age_seconds for age in spot_ages):
                raise ValueError('Invalid, inconsistent or stale spot')
            spot = spots.pop()
        except (ValueError, KeyError, ArithmeticError):
            result['status'] = 'invalid_spot'
            output.append(result)
            continue
        result['spot'] = float(spot)
        eligible = {'CE':[], 'PE':[]}
        times = []
        for row in contracts:
            kind, strike = row['type'], number(row['strike'])
            reason = None
            distance = (strike-spot)/spot*100 if kind == 'CE' else (spot-strike)/spot*100
            if strike <= 0 or distance < 0 or distance > band:
                reason = 'outside_side_or_band'
            elif any(row.get(k) in (None,'') for k in ('quote_time','bid','ask','oi_units','lot_size','volume_units')):
                reason = 'missing_quote_fields'
            else:
                try:
                    quote_time = instant(row['quote_time'])
                    age = (now-quote_time).total_seconds()
                    bid, ask, oi, lot, volume = map(number, (row['bid'],row['ask'],row['oi_units'],row['lot_size'],row['volume_units']))
                    if age < 0:
                        reason = 'future_quote'
                    elif age > max_age_seconds:
                        reason = 'stale_quote'
                    elif lot <= 0 or lot != lot.to_integral_value() or min(oi,volume) < 0:
                        reason = 'invalid_quantity'
                    elif bid <= 0 or ask <= 0 or ask < bid:
                        reason = 'invalid_spread'
                    else:
                        spread = 100*(ask-bid)/((ask+bid)/2)
                        oi_lots, volume_lots = oi/lot, volume/lot
                        if spread > spread_limit:
                            reason = 'wide_spread'
                        elif volume_lots < min_volume:
                            reason = 'low_volume'
                        elif oi_lots <= 0 or oi_lots < minimum:
                            reason = 'low_oi'
                        else:
                            eligible[kind].append({'strike':strike,'oi_units':oi,'oi_lots':oi_lots,
                                'distance_pct':distance,'spread_pct':spread,'quote_age_seconds':age,
                                'lot_size':lot,'volume_lots':volume_lots})
                            times.append(quote_time)
                except (ValueError, KeyError, ArithmeticError):
                    reason = 'invalid_quote_fields'
            if reason:
                result['exclusions'].append({'type':kind,'strike':float(strike),'reason':reason})
        for kind, field in (('CE','call_wall'),('PE','put_wall')):
            candidates = eligible[kind]
            result['eligible_counts'][kind] = len(candidates)
            if candidates:
                wall = dict(sorted(candidates, key=lambda x:(-x['oi_lots'],x['distance_pct'],x['strike']))[0])
                total = sum((x['oi_lots'] for x in candidates),D(0))
                wall['eligible_side_oi_lots'] = total
                wall['concentration_share'] = wall['oi_lots']/total if total else None
                result[field] = {k:float(v) if isinstance(v,D) else v for k,v in wall.items()}
        result['snapshot_skew_seconds'] = (max(times)-min(times)).total_seconds() if times else None
        result['status'] = 'ok' if result['call_wall'] and result['put_wall'] else 'missing_call' if result['put_wall'] else 'missing_put' if result['call_wall'] else 'no_eligible_walls'
        output.append(result)
    ranks = {}
    for field in ('call_wall','put_wall'):
        ranks[field] = sorted([{'underlying':row['underlying'], **row[field]} for row in output if row[field]],
                             key=lambda row:(row['distance_pct'],row['underlying']))
    return {'manifest':{'expiry':expiry,'asof':asof,'max_age_seconds':max_age_seconds,
                        'band_pct':str(band),'min_oi_lots':str(minimum),'max_spread_pct':str(spread_limit),
                        'min_volume_lots':str(min_volume),'oi_input_unit':'underlying_units',
                        'wall_rule':'max_eligible_oi_lots_then_min_distance_then_strike',
                        'expiry_at':expiry_at,'coverage':'supplied_contracts_only; provide a complete selected-expiry chain'},
            'status':'ok' if output else 'no_selected_expiry_data','stocks':output,'rankings':ranks}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chain',type=Path)
    parser.add_argument('--expiry',required=True)
    parser.add_argument('--asof',required=True)
    parser.add_argument('--max-age-seconds',type=int,default=30)
    parser.add_argument('--band-pct',default='10')
    parser.add_argument('--min-oi-lots',default='100')
    parser.add_argument('--max-spread-pct',default='5')
    parser.add_argument('--min-volume-lots',default='0')
    parser.add_argument('--expiry-at',help='Verified offset-aware contract expiry time; required on expiry day')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=screen(load_rows(args.chain),args.expiry,args.asof,args.max_age_seconds,args.band_pct,
                  args.min_oi_lots,args.max_spread_pct,args.min_volume_lots,args.expiry_at)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(f"Screened {len(result['stocks'])} underlyings; result {args.out}")


if __name__=='__main__':
    main()

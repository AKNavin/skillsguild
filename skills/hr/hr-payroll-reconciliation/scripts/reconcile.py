"""Strict, local payroll line reconciliation. No network or payroll mutations."""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

FIELDS = ('entity', 'period', 'employee_id', 'currency', 'component', 'amount')
KEY_FIELDS = FIELDS[:-1]
TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,79}\Z')
PERIOD = re.compile(r'\d{4}-(?:0[1-9]|1[0-2])\Z', re.ASCII)
MONEY = re.compile(r'-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?\Z')


def amount(value):
    """Accept bounded fixed-point decimals, never floats or exponents."""
    if not isinstance(value, str) or not MONEY.fullmatch(value):
        raise ValueError('amount must be a plain decimal with at most 12 integer and 2 fractional digits')
    return Decimal(value)


def money(value):
    return format(value if value else Decimal('0'), '.2f')


def read_csv(filename):
    raw = Path(filename).read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
    if reader.fieldnames != list(FIELDS):
        raise ValueError('CSV header must be exactly: ' + ','.join(FIELDS))
    rows = {}
    for row in reader:
        line = reader.line_num
        if set(row) != set(FIELDS) or any(v is None for v in row.values()):
            raise ValueError(f'CSV line {line}: unexpected or missing columns')
        for field in KEY_FIELDS:
            value = row[field]
            if value != value.strip() or not value:
                raise ValueError(f'CSV line {line}: {field} must be nonempty without outer whitespace')
            if field == 'period':
                valid = PERIOD.fullmatch(value) and value[:4] != '0000'
            elif field == 'currency':
                valid = re.fullmatch('[A-Z]{3}', value)
            else:
                valid = TOKEN.fullmatch(value)
            if not valid:
                raise ValueError(f'CSV line {line}: invalid {field}')
        key = tuple(row[field] for field in KEY_FIELDS)
        if key in rows:
            raise ValueError(f'CSV line {line}: duplicate line key; use distinct approved component codes')
        try:
            rows[key] = amount(row['amount'])
        except ValueError as error:
            raise ValueError(f'CSV line {line}: {error}') from error
    return rows, hashlib.sha256(raw).hexdigest()


def compare(expected, actual, tolerance=Decimal('0')):
    if not isinstance(tolerance, Decimal) or not tolerance.is_finite() or tolerance < 0:
        raise ValueError('tolerance must be a nonnegative finite Decimal')
    lines = []
    totals = defaultdict(lambda: [Decimal('0'), Decimal('0')])
    for key in sorted(expected.keys() | actual.keys()):
        wanted = expected.get(key)
        received = actual.get(key)
        delta = (received or Decimal('0')) - (wanted or Decimal('0'))
        if wanted is None:
            status = 'unexpected'
        elif received is None:
            status = 'missing'
        elif delta == 0:
            status = 'matched'
        elif abs(delta) <= tolerance:
            status = 'within_tolerance'
        else:
            status = 'changed'
        line = dict(zip(KEY_FIELDS, key))
        line.update(status=status, expected=None if wanted is None else money(wanted),
                    actual=None if received is None else money(received), delta=money(delta))
        lines.append(line)
        bucket = (key[0], key[1], key[3])
        totals[bucket][0] += wanted or Decimal('0')
        totals[bucket][1] += received or Decimal('0')
    counts = Counter(line['status'] for line in lines)
    return {
        'tolerance': money(tolerance),
        'expected_line_count': len(expected),
        'actual_line_count': len(actual),
        'has_records': bool(lines),
        'counts': {s: counts[s] for s in ('matched', 'within_tolerance', 'changed', 'missing', 'unexpected')},
        'unresolved_count': sum(counts[s] for s in ('changed', 'missing', 'unexpected')),
        'control_totals': [dict(entity=k[0], period=k[1], currency=k[2], expected=money(v[0]),
                               actual=money(v[1]), delta=money(v[1]-v[0]))
                           for k, v in sorted(totals.items())],
        'lines': lines,
        'scope': 'Arithmetic comparison only. No entitlement, statutory calculation or payment approval.',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('expected')
    parser.add_argument('actual')
    parser.add_argument('--tolerance', default='0.00', help='Nonnegative fixed decimal; default exact comparison')
    args = parser.parse_args(argv)
    try:
        tolerance = amount(args.tolerance)
        if tolerance < 0:
            raise ValueError('tolerance must be nonnegative')
        expected, expected_hash = read_csv(args.expected)
        actual, actual_hash = read_csv(args.actual)
        result = compare(expected, actual, tolerance)
        result['source_sha256'] = {'expected': expected_hash, 'actual': actual_hash}
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f'Input rejected: {error}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

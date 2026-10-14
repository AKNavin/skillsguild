"""Observable arithmetic, malformed-input and local CLI regression checks."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('reconcile', ROOT / 'scripts/reconcile.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
HEADER = 'entity,period,employee_id,currency,component,amount\n'
KEY = ('DEMO', '2026-10', 'EMP001', 'INR', 'BASIC')


class ReconciliationTests(unittest.TestCase):
    def read_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'input.csv'
            filename.write_text(text, encoding='utf-8')
            return MOD.read_csv(filename)

    def test_fixture_offsetting_errors_do_not_clear_line_exceptions(self):
        expected, _ = MOD.read_csv(ROOT / 'fixtures/expected.csv')
        actual, _ = MOD.read_csv(ROOT / 'fixtures/actual.csv')
        result = MOD.compare(expected, actual)
        self.assertEqual(result['control_totals'][0]['delta'], '0.00')
        self.assertEqual(result['counts'], {'matched': 1, 'within_tolerance': 0, 'changed': 2, 'missing': 1, 'unexpected': 1})
        self.assertEqual(result['unresolved_count'], 4)

    def test_missing_zero_is_not_matched_and_tolerance_cannot_hide_it(self):
        result = MOD.compare({KEY: Decimal('0')}, {}, Decimal('100'))
        self.assertEqual(result['lines'][0]['status'], 'missing')
        self.assertIsNone(result['lines'][0]['actual'])
        self.assertEqual(result['unresolved_count'], 1)

    def test_decimal_tolerance_boundary_is_visible(self):
        result = MOD.compare({KEY: Decimal('0.10')}, {KEY: Decimal('0.11')}, Decimal('0.01'))
        self.assertEqual(result['lines'][0]['status'], 'within_tolerance')
        self.assertEqual(result['lines'][0]['delta'], '0.01')
        self.assertEqual(MOD.compare({KEY: Decimal('0.10')}, {KEY: Decimal('0.12')}, Decimal('0.01'))['unresolved_count'], 1)

    def test_currency_and_entity_totals_stay_separate(self):
        other = ('SECOND', '2026-10', 'EMP001', 'USD', 'BASIC')
        result = MOD.compare({KEY: Decimal('100'), other: Decimal('2')}, {KEY: Decimal('100'), other: Decimal('3')})
        self.assertEqual(len(result['control_totals']), 2)
        self.assertEqual([x['delta'] for x in result['control_totals']], ['0.00', '1.00'])

    def test_duplicate_key_rejected_even_if_amount_equal(self):
        row = 'DEMO,2026-10,EMP001,INR,BASIC,1.00\n'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.read_text(HEADER + row + row)

    def test_invalid_money_rejected(self):
        for value in ('NaN', 'Infinity', '1e2', '1.001', ' 1.00', '+1', '01.00', '', '1000000000000'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.read_text(HEADER + f'DEMO,2026-10,EMP001,INR,BASIC,{value}\n')

    def test_invalid_schema_period_currency_and_missing_field_rejected(self):
        cases = [
            HEADER.replace('entity,period', 'period,entity'),
            HEADER + 'DEMO,2026-13,EMP001,INR,BASIC,1\n',
            HEADER + 'DEMO,0000-01,EMP001,INR,BASIC,1\n',
            HEADER + 'DEMO,2026-10,EMP001,inr,BASIC,1\n',
            HEADER + 'DEMO,2026-10,,INR,BASIC,1\n',
            HEADER + 'DEMO,2026-10,EMP001,INR,BASIC\n',
            HEADER + 'DEMO,2026-10,EMP001,INR,BASIC,1,extra\n',
            HEADER + 'DEMO,2026-10,=formula,INR,BASIC,1\n',
        ]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.read_text(text)

    def test_empty_input_is_explicit(self):
        rows, _ = self.read_text(HEADER)
        result = MOD.compare(rows, rows)
        self.assertFalse(result['has_records'])
        self.assertEqual(result['expected_line_count'], 0)

    def test_negative_deductions_and_zero_normalization(self):
        result = MOD.compare({KEY: Decimal('-10')}, {KEY: Decimal('-11')})
        self.assertEqual(result['lines'][0]['delta'], '-1.00')
        self.assertEqual(MOD.money(Decimal('-0.00')), '0.00')

    def test_cli_is_deterministic_and_emits_hashes(self):
        args = [str(ROOT / 'fixtures/expected.csv'), str(ROOT / 'fixtures/actual.csv')]
        outputs = []
        for _ in range(2):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(MOD.main(args), 0)
            outputs.append(out.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        result = json.loads(outputs[0])
        self.assertEqual(len(result['source_sha256']['expected']), 64)

    def test_cli_invalid_input_has_no_partial_json(self):
        out, err = io.StringIO(), io.StringIO()
        args = [str(ROOT / 'fixtures/expected.csv'), str(ROOT / 'fixtures/actual.csv'), '--tolerance=-1']
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(MOD.main(args), 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('nonnegative', err.getvalue())


if __name__ == '__main__':
    unittest.main()

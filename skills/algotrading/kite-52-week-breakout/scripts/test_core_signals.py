"""Observable calculation checks; run python -m unittest discover -s scripts."""
import copy
import unittest
from datetime import datetime
from pathlib import Path

from core_signals import calculate, read_calendar, read_prices


class CoreSignalsTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.rows = read_prices(root / "fixtures/core.csv")
        self.calendar = read_calendar(root / "fixtures/sessions.csv")
        self.as_of = datetime.fromisoformat("2026-10-09T16:00:00+05:30")

    def run_scan(self, rows=None, as_of=None):
        return calculate(self.rows if rows is None else rows, self.calendar,
                         self.as_of if as_of is None else as_of, 3, 3)

    def test_current_high_and_volume_excluded(self):
        item = self.run_scan()[3]
        self.assertEqual(item["reference_high"], 100)
        self.assertTrue(item["breakout"])
        self.assertFalse(item["near_high"])
        self.assertEqual(item["baseline_volume"], 200)
        self.assertEqual(item["rvol"], 2)

    def test_future_rows_cannot_change_past(self):
        edited = copy.deepcopy(self.rows)
        edited[-1].update(high=1000, low=1, close=999, volume=1000000)
        self.assertEqual(self.run_scan()[:4], self.run_scan(edited)[:4])

    def test_unfinished_session_excluded(self):
        before_close = datetime.fromisoformat("2026-10-08T15:00:00+05:30")
        self.assertEqual(len(self.run_scan(as_of=before_close)), 3)

    def test_missing_session_not_compressed(self):
        edited = [row for i, row in enumerate(self.rows) if i != 1]
        self.assertEqual(self.run_scan(edited)[3]["data_quality"], "missing_reference_session")
        self.assertIsNone(self.run_scan(edited)[3]["breakout"])

    def test_equal_high_and_near_boundaries(self):
        for close, expected_near in [(100, True), (97, True), (96, False), (101, False)]:
            edited = copy.deepcopy(self.rows)
            edited[3].update(high=106, low=90, open=100, close=close)
            result = self.run_scan(edited)[3]
            self.assertEqual(result["near_high"], expected_near)
            self.assertEqual(result["breakout"], close > 100)

    def test_zero_volume_baseline_is_unavailable(self):
        edited = copy.deepcopy(self.rows)
        for row in edited[:3]:
            row["volume"] = 0
        result = self.run_scan(edited)[3]
        self.assertEqual(result["data_quality"], "zero_volume_baseline")
        self.assertIsNone(result["rvol"])
        self.assertIsNone(result["volume_breakout"])

    def test_duplicate_price_rows_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_scan(self.rows + [self.rows[0]])

    def test_audit_fields_and_configurable_buffer(self):
        result=calculate(self.rows,self.calendar,self.as_of,3,3,buffer_pct=10)[3]
        self.assertFalse(result['breakout'])
        self.assertEqual(result['history_count'],3)
        self.assertEqual(result['reference_start'],self.rows[0]['session'])
        self.assertEqual(result['reference_end'],self.rows[2]['session'])
        self.assertEqual(result['lookback_mode'],'sessions')
        self.assertEqual(result['distance_above_pct'],-result['distance_pct'])

    def test_near_rank_uses_distance_then_identity(self):
        one=copy.deepcopy(self.rows);two=copy.deepcopy(self.rows)
        for r in two:r['symbol']='SECOND'
        one[3]['close']=98;two[3]['close']=99
        results=calculate(one+two,self.calendar,self.as_of,3,3)
        latest=[r for r in results if r['session']==self.rows[3]['session']]
        self.assertEqual(next(r for r in latest if r['symbol']=='SECOND')['rank'],1)


if __name__ == "__main__":
    unittest.main()

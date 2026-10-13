import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('oi_walls',ROOT/'scripts/oi_walls.py')
walls=importlib.util.module_from_spec(spec)
spec.loader.exec_module(walls)


class WallTests(unittest.TestCase):
    def setUp(self):
        self.rows=walls.load_rows(ROOT/'fixtures/chain.csv')

    def run_screen(self,rows=None,**kwargs):
        return walls.screen(self.rows if rows is None else rows,'2026-10-27','2026-10-13T11:00:10+05:30',**kwargs)

    def test_wall_is_max_oi_not_closest_strike_and_tie_is_nearest(self):
        stock=self.run_screen()['stocks'][0]
        self.assertEqual(stock['call_wall']['strike'],105)
        self.assertEqual(stock['call_wall']['oi_lots'],300)
        self.assertEqual(stock['call_wall']['distance_pct'],5)
        self.assertEqual(stock['put_wall']['strike'],98)
        self.assertEqual(stock['put_wall']['distance_pct'],2)
        self.assertEqual(stock['status'],'ok')

    def test_other_expiry_has_no_effect(self):
        rows=copy.deepcopy(self.rows)
        rows[-1]['oi_units']='1'
        self.assertEqual(self.run_screen(rows),self.run_screen())

    def test_stale_puts_are_null_not_zero(self):
        rows=copy.deepcopy(self.rows)
        for row in rows:
            if row['type']=='PE': row['quote_time']='2026-10-13T10:00:00+05:30'
        stock=self.run_screen(rows)['stocks'][0]
        self.assertIsNone(stock['put_wall'])
        self.assertEqual(stock['status'],'missing_put')
        self.assertEqual(len([r for r in stock['exclusions'] if r['reason']=='stale_quote']),2)

    def test_lot_threshold_uses_units_conversion(self):
        stock=self.run_screen(min_oi_lots='301')['stocks'][0]
        self.assertIsNone(stock['call_wall'])
        self.assertEqual(stock['put_wall']['oi_lots'],400)

    def test_distance_band_and_missing_side(self):
        stock=self.run_screen(band_pct='1.5')['stocks'][0]
        self.assertEqual(stock['call_wall']['strike'],101)
        self.assertIsNone(stock['put_wall'])

    def test_missing_and_crossed_quotes_are_excluded(self):
        rows=copy.deepcopy(self.rows)
        rows[1]['ask']=''
        rows[2]['ask']='0.5'
        stock=self.run_screen(rows)['stocks'][0]
        self.assertEqual(stock['call_wall']['strike'],101)

    def test_stale_spot_blocks_whole_underlying(self):
        rows=copy.deepcopy(self.rows)
        rows[0]['spot_timestamp']='2026-10-13T10:00:00+05:30'
        stock=self.run_screen(rows)['stocks'][0]
        self.assertEqual(stock['status'],'invalid_spot')
        self.assertIsNone(stock['call_wall'])

    def test_duplicate_contract_and_no_expiry_fail_honestly(self):
        with self.assertRaises(ValueError): self.run_screen(self.rows+[self.rows[0]])
        self.assertEqual(self.run_screen([self.rows[-1]])['status'],'no_selected_expiry_data')

    def test_expiry_day_needs_time_and_rejects_post_expiry(self):
        with self.assertRaises(ValueError):
            walls.screen([], '2026-10-13','2026-10-13T11:00:00+05:30')
        with self.assertRaises(ValueError):
            walls.screen([], '2026-10-13','2026-10-13T16:00:00+05:30',expiry_at='2026-10-13T15:30:00+05:30')
        result=walls.screen([], '2026-10-13','2026-10-13T11:00:00+05:30',expiry_at='2026-10-13T15:30:00+05:30')
        self.assertEqual(result['status'],'no_selected_expiry_data')


if __name__=='__main__': unittest.main()

import random
import unittest
from veil.births import draw_country, snapshot


class BirthTests(unittest.TestCase):
    def test_snapshot_covers_historical_years_without_aggregates(self):
        data = snapshot()['years']
        self.assertEqual(set(map(int, data)), set(range(1950, 2024)))
        for entry in data.values():
            codes = [c['code'] for c in entry['countries']]
            self.assertEqual(len(codes), len(set(codes)))
            self.assertNotIn('OWID_WRL', codes)
            self.assertGreater(len(codes), 200)
            self.assertTrue(all(c['births'] >= 0 for c in entry['countries']))
            coverage = sum(c['births'] for c in entry['countries']) / entry['world_births']
            self.assertTrue(0.999 < coverage < 1.001)

    def test_weights_are_births_not_population(self):
        class Inspect:
            def choices(self, rows, weights, k):
                assert weights == [row['births'] for row in rows]
                assert k == 1
                return [next(row for row in rows if row['code'] == 'IND')]
        result = draw_country(1985, Inspect())
        self.assertEqual(result['code'], 'IND')
        self.assertAlmostEqual(result['probability'], result['births'] / result['covered_births'])

    def test_repeatable_and_rejects_projection(self):
        self.assertEqual(draw_country(1985, random.Random(8)), draw_country(1985, random.Random(8)))
        for year in (1949, 2024, 2090):
            with self.assertRaises(ValueError):
                draw_country(year, random.Random())

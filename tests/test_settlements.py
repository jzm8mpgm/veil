import unittest
from unittest.mock import patch

from veil.settlements import _load_urban, draw_settlement


class Fixed:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


class SettlementTests(unittest.TestCase):
    def test_city_other_urban_and_rural_partition(self):
        with patch('veil.settlements._load', return_value=(
            {('ABC', 1985): 1000}, {'ABC': {'Example': {1985: 100}}}
        )), patch('veil.settlements._load_urban', return_value={('ABC', 1985): 0.4}):
            results = [draw_settlement('ABC', 1988, Fixed(v)) for v in (0.05, 0.2, 0.7)]
        self.assertEqual([r['kind'] for r in results], ['city', 'urban', 'rural'])
        self.assertAlmostEqual(sum(r['probability'] for r in results), 1)
        self.assertEqual(results[2]['probability'], 0.6)
        self.assertEqual(results[2]['year'], 1985)
        self.assertIn('village', results[2]['name'])

    def test_country_without_named_cities_still_has_rural_detail(self):
        with patch('veil.settlements._load', return_value=({}, {})), patch(
            'veil.settlements._load_urban', return_value={('ABC', 1950): 0.2}
        ):
            result = draw_settlement('ABC', 1952, Fixed(0.5))
        self.assertEqual(result['kind'], 'rural')
        self.assertEqual(result['probability'], 0.8)

    def test_inconsistent_city_population_does_not_erase_rural_share(self):
        with patch('veil.settlements._load', return_value=(
            {('ABC', 1985): 1000}, {'ABC': {'Example': {1985: 500}}}
        )), patch('veil.settlements._load_urban', return_value={('ABC', 1985): 0.4}):
            result = draw_settlement('ABC', 1985, Fixed(0.7))
        self.assertEqual(result['kind'], 'rural')
        self.assertEqual(result['probability'], 0.6)
        self.assertIn('withheld', result['caveat'])

    def test_snapshot_is_historical_and_valid(self):
        values = _load_urban()
        self.assertGreater(len(values), 15000)
        self.assertTrue(all(1950 <= year <= 2023 and 0 <= value <= 1
                            for (_, year), value in values.items()))
        self.assertIn(('IND', 1950), values)
        self.assertIn(('OWID_KOS', 1950), values)

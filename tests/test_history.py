import random
import unittest
from unittest.mock import patch
from veil.history import draw_early_life, _snapshot


class Fixed:
    def __init__(self, value): self.value = value
    def random(self): return self.value


class HistoryTests(unittest.TestCase):
    def test_mutually_exclusive_childhood_draws(self):
        data = {'source': 'fixture', 'sources': {}, 'countries': {'ABC': {'1960': {
            'life_expectancy': 45, 'infant_mortality_percent': 20,
            'under_five_mortality_percent': 35}}}}
        with patch('veil.history._snapshot', return_value=data):
            for roll, expected, probability in [(0, 'died_in_infancy', .2),
                (.2, 'died_in_early_childhood', .15), (.3499, 'died_in_early_childhood', .15),
                (.35, 'survived_to_five', .65), (.9999, 'survived_to_five', .65)]:
                result = draw_early_life('ABC', 1960, Fixed(roll))
                self.assertEqual(result['outcome'], expected)
                self.assertAlmostEqual(result['probability'], probability)
                self.assertEqual(result['life_expectancy_at_birth'], 45)
                self.assertAlmostEqual(sum(result['outcome_probabilities'].values()), 1)

    def test_exact_birth_year_not_current_life_expectancy(self):
        past = draw_early_life('IND', 1950, random.Random(1))
        later = draw_early_life('IND', 2023, random.Random(1))
        self.assertLess(past['life_expectancy_at_birth'], later['life_expectancy_at_birth'])
        self.assertGreater(past['infant_death_probability'], later['infant_death_probability'])
        self.assertEqual(past['year'], 1950)

    def test_no_neighbouring_year_or_country_substitution(self):
        for code, year in [('XXX', 1985), ('IND', 1949)]:
            result = draw_early_life(code, year, random.Random(1))
            self.assertEqual(result['outcome'], 'unavailable')
            self.assertIsNone(result['life_expectancy_at_birth'])

    def test_snapshot_validates_all_probability_pairs(self):
        for years in _snapshot()['countries'].values():
            for row in years.values():
                self.assertTrue(0 <= row['infant_mortality_percent'] <= row['under_five_mortality_percent'] <= 100)

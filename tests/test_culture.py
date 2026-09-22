import unittest
from veil.culture import describe_culture


class CultureTests(unittest.TestCase):
    def test_real_country_has_all_context_layers(self):
        result = describe_culture('IND', 1985)
        for key in ('language', 'religion', 'food', 'music'):
            self.assertTrue(result[key]['text'])
            self.assertIsNotNone(result[key]['source_url'])
        self.assertEqual(result['food']['reference_year'], 1985)
        self.assertIn('not the most-eaten dish', result['food']['method'])

    def test_language_is_a_random_named_choice_with_comparison(self):
        result = describe_culture('GHA', 1985)
        self.assertIn('You speak ', result['language']['text'])
        self.assertIn('% of people here', result['language']['text'])
        self.assertNotIn('other is the most', result['language']['text'])
        self.assertIn('choice', result['language'])

    def test_birth_year_selects_historical_food_observation(self):
        old = describe_culture('IND', 1961)
        recent = describe_culture('IND', 2023)
        self.assertEqual(old['food']['reference_year'], 1961)
        self.assertEqual(recent['food']['reference_year'], 2023)

    def test_unknown_country_is_explicitly_unavailable(self):
        result = describe_culture('XXX', 1985)
        self.assertIn('unavailable', result['language']['text'])
        self.assertIn('unavailable', result['food']['text'])

import unittest

from veil.outcomes import get_outcomes


class OutcomesTests(unittest.TestCase):
    def test_real_country_has_sourced_context(self):
        result = get_outcomes('GBR')
        for key in ('income', 'life_expectancy', 'leading_death_category'):
            self.assertIsNotNone(result[key])
            self.assertLessEqual(result[key]['year'], 2026)
            self.assertTrue(result[key]['source_url'].startswith('https://'))
        self.assertIn('not salary', result['income']['caveat'])
        self.assertIn('not remaining', result['life_expectancy']['caveat'])

    def test_as_of_filters_observations(self):
        result = get_outcomes('IND', 2018)
        for key in ('income', 'life_expectancy', 'leading_death_category'):
            if result[key]:
                self.assertLessEqual(result[key]['year'], 2018)

    def test_unavailable_does_not_fabricate(self):
        for result in (get_outcomes('XXX'), get_outcomes('GBR', 1900)):
            for key in ('income', 'life_expectancy', 'leading_death_category'):
                self.assertIsNone(result[key])

    def test_broad_category_is_largest_comparable_group(self):
        row = get_outcomes('NGA')['leading_death_category']
        self.assertEqual(row['value'], max(row['groups_compared'].values()))
        self.assertIn('not a specific disease', row['caveat'])

    def test_who_cause_available_and_historical_filter_applies(self):
        row = get_outcomes('GBR')['leading_death_cause']
        self.assertIsNotNone(row)
        self.assertEqual(row['year'], 2021)
        self.assertEqual(row['unit'], 'deaths per 100,000 population')
        self.assertIn('not your personal', row['caveat'])
        self.assertIsNone(get_outcomes('GBR', 2020)['leading_death_cause'])
        self.assertIsNone(get_outcomes('XXX')['leading_death_cause'])

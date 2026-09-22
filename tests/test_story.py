import json
import random
import unittest
from unittest.mock import patch
from veil.__main__ import create_story, render, likelihood_label
from veil.settlements import draw_settlement


class StoryTests(unittest.TestCase):
    def test_likelihood_labels_are_plain_language(self):
        self.assertEqual(likelihood_label(0.2), 'fair')
        self.assertEqual(likelihood_label(0.02), 'rare')
        self.assertEqual(likelihood_label(0.002), 'very rare')
        self.assertEqual(likelihood_label(None), 'unknown')

    def test_repeatable_serializable_story_and_honest_labels(self):
        story = create_story(1985, 'first-light', 2026)
        self.assertEqual(story, create_story(1985, 'first-light', 2026))
        self.assertEqual(json.loads(json.dumps(story)), story)
        self.assertEqual(story['age_this_year'], 41)
        text = render(story)
        self.assertIn('Fifth of the national income distribution', text)
        self.assertIn('population estimate', text)

    def test_city_probability_leaves_residual(self):
        population = {('ABC', 1985): 1000}
        cities = {'ABC': {'Example': {1985: 100}}}
        with patch('veil.settlements._load', return_value=(population, cities)):
            class Fixed:
                def __init__(self, value): self.value = value
                def random(self): return self.value
            city = draw_settlement('ABC', 1988, Fixed(0.05))
            other = draw_settlement('ABC', 1988, Fixed(0.5))
            self.assertEqual(city['kind'], 'city')
            self.assertEqual(city['probability'], 0.1)
            self.assertEqual(city['year'], 1985)
            self.assertEqual(other['kind'], 'residual')
            self.assertEqual(other['probability'], 0.9)

    def test_uncovered_country_is_not_assigned_a_capital(self):
        result = draw_settlement('XXX', 1985, random.Random(1))
        self.assertEqual(result['kind'], 'unresolved')
        self.assertIsNone(result['probability'])

    def test_early_death_does_not_receive_adult_outcomes(self):
        story = create_story(1950, '3', 2026)
        self.assertEqual(story['early_life']['outcome'], 'died_in_infancy')
        text = render(story)
        self.assertIn('this life ends before its first birthday', text)
        self.assertNotIn('Income context', text)
        self.assertNotIn('Income context', text)
        self.assertNotIn('You would turn', text)

    def test_early_life_draw_changes_with_seed(self):
        outcomes = {create_story(1950, str(seed), 2026)['early_life']['outcome'] for seed in range(40)}
        self.assertGreater(len(outcomes), 1)

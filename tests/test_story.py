import json
import random
import unittest
from unittest.mock import patch
from veil.__main__ import create_story, render
from veil.settlements import draw_settlement


class StoryTests(unittest.TestCase):
    def test_repeatable_serializable_story_and_honest_labels(self):
        story = create_story(1985, 'first-light', 2026)
        self.assertEqual(story, create_story(1985, 'first-light', 2026))
        self.assertEqual(json.loads(json.dumps(story)), story)
        self.assertEqual(story['age_this_year'], 41)
        text = render(story)
        self.assertIn('Illustrative', text)
        self.assertIn('population proxy', text)

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

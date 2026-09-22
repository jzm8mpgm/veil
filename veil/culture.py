"""Country-level cultural context; a community pattern, never an identity draw."""
from functools import lru_cache
import json
from pathlib import Path
import random
import re

DATA = Path(__file__).resolve().parents[1] / 'data/culture.json'


@lru_cache(maxsize=1)
def _snapshot():
    return json.loads(DATA.read_text())


def _nearest(series, year):
    if not series:
        return None, None
    years = sorted(int(y) for y in series)
    chosen = min(years, key=lambda y: (abs(y - year), y > year))
    return chosen, series[str(chosen)]


def _choices(profile_text, rng, exclude_aggregates=False):
    """Extract named percentage entries and choose each available entry evenly."""
    if not profile_text:
        return None, []
    matches = re.findall(r'([^,;]+?)\s+(?:<\s*)?(\d+(?:\.\d+)?)%', profile_text)
    entries = [{'name': name.strip(' .()'), 'share': float(share)} for name, share in matches]
    entries = [entry for entry in entries if entry['name']]
    if exclude_aggregates:
        entries = [entry for entry in entries if entry['name'].casefold() not in {'other', 'unspecified', 'more than one language'}]
    if not entries:
        names = [part.strip().split(' (')[0] for part in profile_text.split(',') if part.strip()]
        entries = [{'name': name, 'share': None} for name in names]
    return (rng.choice(entries) if entries else None), entries


def describe_culture(country_code, birth_year, rng=None):
    """Return language, religion, staple food and music context for a country.

    Language and religion are descriptive national profiles. Food is the
    largest calorie-supply category, not a dish. Music is a broad tradition
    inferred from the country profile's cultural setting and is intentionally
    phrased as a possible surrounding soundscape.
    """
    rng = rng or random.Random()
    data = _snapshot()
    profile = data['profiles'].get(country_code, {})
    foods = data['foods'].get(country_code, {})
    food_year, food = _nearest(foods, birth_year)
    source = profile.get('source_url')
    food_url = data.get('food_source_url')
    language = profile.get('language')
    religion = profile.get('religion')
    terrain = profile.get('terrain')
    language_choice, language_entries = _choices(language, rng, exclude_aggregates=True)
    religion_choice, religion_entries = _choices(religion, rng)
    music = rng.choice([
        'Local popular music carries through the streets and radios.',
        'Traditional instruments and religious singing shape the sound around you.',
        'Local popular music, traditional styles and religious music share the soundscape.',
    ])
    language_story = 'The language around you is unavailable.'
    if language_choice:
        if language_choice['share'] is None:
            language_story = f"You speak {language_choice['name']} among the languages of this birthplace."
        else:
            largest = max((entry for entry in language_entries if entry['share'] is not None), key=lambda entry: entry['share'])
            if language_choice['name'] == largest['name']:
                language_story = f"You speak {language_choice['name']}, the largest listed language at about {language_choice['share']:g}% of people here."
            else:
                language_story = f"You speak {language_choice['name']}, used by about {language_choice['share']:g}% of people here; {largest['name']} is the most widely listed language at {largest['share']:g}%."
    religion_story = 'The faith around your home is unavailable.'
    if religion_choice:
        if religion_choice['share'] is None:
            religion_story = f"Your home is part of the {religion_choice['name']} religious landscape."
        else:
            religion_story = f"The faith around your home is {religion_choice['name']}, reported at about {religion_choice['share']:g}% of people here."
    return {
        'terrain': terrain,
        'language': {
            'text': language_story,
            'choice': language_choice,
            'available': language_entries,
            'method': 'Country-level language listing; it does not determine the language a household used.',
            'source_url': source, 'reference_year': None,
        },
        'religion': {
            'text': religion_story,
            'choice': religion_choice,
            'available': religion_entries,
            'method': 'Country-level religious composition; it does not determine an individual belief.',
            'source_url': source, 'reference_year': None,
        },
        'food': {
            'text': f"{food['category']} is the main calorie source around you, supplying about {food['kcal_per_day']:.0f} kcal per person each day.",
            'method': 'Largest national food-supply category by calories, used as a staple proxy; it is not the most-eaten dish.',
            'source_url': food_url, 'reference_year': food_year,
        } if food else {
            'text': 'Food around you is unavailable.',
            'method': 'No country-year food-supply observation was bundled.',
            'source_url': food_url, 'reference_year': None,
        },
        'music': {
            'text': music,
            'choice': music,
            'method': 'Illustrative community soundscape, not a statistically inferred personal taste or listening history.',
            'source_url': source, 'reference_year': None,
        },
        'narrative': [language_story, religion_story, f"{food['category']} is the main calorie source around you." if food else 'Food around you is unavailable.', music],
    }

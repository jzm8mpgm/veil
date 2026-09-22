"""Country-level cultural context; a community pattern, never an identity draw."""
from functools import lru_cache
import json
from pathlib import Path

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


def describe_culture(country_code, birth_year, rng=None):
    """Return language, religion, staple food and music context for a country.

    Language and religion are descriptive national profiles. Food is the
    largest calorie-supply category, not a dish. Music is a broad tradition
    inferred from the country profile's cultural setting and is intentionally
    phrased as a possible surrounding soundscape.
    """
    data = _snapshot()
    profile = data['profiles'].get(country_code, {})
    foods = data['foods'].get(country_code, {})
    food_year, food = _nearest(foods, birth_year)
    source = profile.get('source_url')
    food_url = data.get('food_source_url')
    language = profile.get('language')
    religion = profile.get('religion')
    terrain = profile.get('terrain')
    # A soundscape cannot be inferred from a demographic table. Keep it broad,
    # sourced to the country profile, and avoid claiming a personal preference.
    music = 'local popular music alongside regional traditional and religious music'
    return {
        'terrain': terrain,
        'language': {
            'text': f"Languages around you: {language}." if language else 'Languages around you: unavailable.',
            'method': 'Country-level language listing; it does not determine the language a household used.',
            'source_url': source, 'reference_year': None,
        },
        'religion': {
            'text': f"Religions around you: {religion}." if religion else 'Religions around you: unavailable.',
            'method': 'Country-level religious composition; it does not determine an individual belief.',
            'source_url': source, 'reference_year': None,
        },
        'food': {
            'text': f"The largest calorie-supply category was {food['category']} ({food['kcal_per_day']:.0f} kcal/person/day).",
            'method': 'Largest national food-supply category by calories, used as a staple proxy; it is not the most-eaten dish.',
            'source_url': food_url, 'reference_year': food_year,
        } if food else {
            'text': 'Food around you: unavailable.',
            'method': 'No country-year food-supply observation was bundled.',
            'source_url': food_url, 'reference_year': None,
        },
        'music': {
            'text': 'Music around you: ' + music + (f" Terrain and place context: {terrain}." if terrain else '.'),
            'method': 'Illustrative community soundscape, not a statistically inferred personal taste or listening history.',
            'source_url': source, 'reference_year': None,
        },
        'caveat': 'These are country-level surroundings. They are not conditional on city, income rank, ethnicity, household or survival to any age.',
    }

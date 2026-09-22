"""Historical country draws, weighted by annual live births."""
import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'


@lru_cache(maxsize=1)
def snapshot():
    return json.loads((DATA / 'births.json').read_text())


def draw_country(year, rng):
    data = snapshot()
    if str(year) not in data['years']:
        raise ValueError('Choose a birth year from 1950 to 2023 (historical estimates only).')
    entry = data['years'][str(year)]
    countries = entry['countries']
    total = sum(c['births'] for c in countries)
    country = rng.choices(countries, weights=[c['births'] for c in countries], k=1)[0]
    return {**country, 'year': year, 'probability': country['births'] / total,
            'covered_births': total, 'world_births': entry['world_births'],
            'coverage': total / entry['world_births'],
            'source': data['source'], 'url': data['url']}

"""Birth-year period mortality, with mutually exclusive childhood outcomes."""
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def _snapshot():
    return json.loads((Path(__file__).resolve().parents[1] / 'data/history.json').read_text())


def draw_early_life(country_code, year, rng):
    data = _snapshot()
    row = data['countries'].get(country_code, {}).get(str(year), {})
    result = {
        'year': year, 'life_expectancy_at_birth': row.get('life_expectancy'),
        'infant_death_probability': None, 'under_five_death_probability': None,
        'outcome': 'unavailable', 'probability': None, 'adult_life_conditional': True,
        'source': data['source'],
        'source_urls': {key: value['url'] for key, value in data['sources'].items()},
        'method': 'One draw from birth-year period risks: death before 1, death from 1 to under 5, or survival to 5. Under-five risk already includes infant deaths.',
        'caveat': 'Holds birth-year mortality rates fixed: a period scenario, not the observed fate of that birth cohort. Life expectancy already includes early deaths; do not subtract them again. Survival to five does not establish survival to today. No adult death age or specific childhood cause is inferred.',
    }
    infant = row.get('infant_mortality_percent')
    child = row.get('under_five_mortality_percent')
    if infant is None or child is None:
        return result
    q1, q5 = infant / 100, child / 100
    if not 0 <= q1 <= q5 <= 1:
        raise ValueError('Historical mortality risks must satisfy 0 <= infant <= under-five <= 1')
    result.update(infant_death_probability=q1, under_five_death_probability=q5)
    outcomes = {'died_in_infancy': q1, 'died_in_early_childhood': q5 - q1, 'survived_to_five': 1 - q5}
    draw = rng.random()
    outcome = 'died_in_infancy' if draw < q1 else 'died_in_early_childhood' if draw < q5 else 'survived_to_five'
    result.update(outcome=outcome, probability=outcomes[outcome], outcome_probabilities=outcomes,
                  most_likely_early_outcome=max(outcomes, key=outcomes.get))
    return result

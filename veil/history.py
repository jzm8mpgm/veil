"""Birth-year period mortality and a seeded life-course draw."""
from functools import lru_cache
import json
import math
from pathlib import Path


@lru_cache(maxsize=1)
def _snapshot():
    return json.loads((Path(__file__).resolve().parents[1] / 'data/history.json').read_text())


def draw_early_life(country_code, year, rng, as_of_year=None):
    """Draw an age outcome from the birth-year mortality profile.

    Infant and under-five risks are taken directly from the historical row.
    For lives reaching five, an exponential adult-age tail is calibrated to
    the same row's period life expectancy, then compared with the current age.
    """
    if as_of_year is None:
        from datetime import date
        as_of_year = date.today().year
    data = _snapshot()
    row = data['countries'].get(country_code, {}).get(str(year), {})
    result = {
        'year': year, 'life_expectancy_at_birth': row.get('life_expectancy'),
        'infant_death_probability': None, 'under_five_death_probability': None,
        'outcome': 'unavailable', 'probability': None, 'adult_life_conditional': True,
        'life_status': 'unavailable', 'alive_today': None, 'age_now': max(0, as_of_year - year),
        'age_at_death': None,
        'source': data['source'],
        'source_urls': {key: value['url'] for key, value in data['sources'].items()},
        'method': 'One draw from birth-year period risks, followed by a life-span draw calibrated to birth-year life expectancy for those reaching age five.',
        'caveat': 'Holds birth-year mortality rates fixed: a period scenario, not the observed fate of that birth cohort. Life expectancy already includes early deaths; do not subtract them again. The later-life age draw is calibrated to the birth-year life expectancy, and cause is sampled from country-level cause shares.',
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
    age_at_death = None
    if outcome == 'died_in_infancy':
        age_at_death = rng.random()
    elif outcome == 'died_in_early_childhood':
        age_at_death = 1 + 3 * rng.random()
    else:
        life_expectancy = row.get('life_expectancy')
        if life_expectancy is not None:
            early_death_years = q1 * 0.5 + (q5 - q1) * 2.5
            survivor_mean = max(5.0, (life_expectancy - early_death_years) / max(1 - q5, 1e-9))
            tail_mean = max(0.1, survivor_mean - 5)
            age_at_death = 5 - tail_mean * math.log1p(-rng.random())
    age_now = max(0, as_of_year - year)
    sampled_age_at_death = age_at_death
    alive_today = sampled_age_at_death is None or sampled_age_at_death > age_now
    life_status = 'alive_today' if alive_today else outcome if outcome != 'survived_to_five' else 'died_later'
    result.update(outcome=outcome, probability=outcomes[outcome], outcome_probabilities=outcomes,
                  most_likely_early_outcome=max(outcomes, key=outcomes.get),
                  age_at_death=None if alive_today else sampled_age_at_death,
                  age_now=age_now, alive_today=alive_today, life_status=life_status)
    return result

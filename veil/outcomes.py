"""Country context from real observations; never an individual forecast."""
from functools import lru_cache
import json
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / 'data/outcomes.json'
DEATH_GROUPS = {
    'SH.DTH.NCOM.ZS': 'non-communicable diseases',
    'SH.DTH.COMM.ZS': 'communicable, maternal, prenatal and nutritional conditions',
    'SH.DTH.INJR.ZS': 'injuries',
}


@lru_cache(maxsize=1)
def _snapshot():
    return json.loads(SNAPSHOT.read_text())


@lru_cache(maxsize=1)
def _causes():
    return json.loads(SNAPSHOT.with_name('outcomes_causes.json').read_text())


def get_outcomes(country_code: str, as_of_year: int = 2026) -> dict:
    """Latest observations <= as_of_year, using ISO3 codes; missing stays None.

    This is a current data vintage, not what was known in the historical year.
    The bundled snapshot retains 2015 onward. No age, city or class adjustment
    is inferred. The death result ranks three broad groups at a common year.
    """
    if isinstance(as_of_year, bool) or not isinstance(as_of_year, int):
        raise ValueError('as_of_year must be an integer')
    country_code = country_code.upper()
    snapshot = _snapshot()
    country = snapshot['countries'].get(country_code, {})
    indicators = country.get('indicators', {})

    def measure(code, label, unit, caveat):
        row = next((r for r in indicators.get(code, []) if r['year'] <= as_of_year), None)
        if row is None:
            return None
        return {**row, 'label': label, 'unit': unit, 'indicator': code,
                'source': 'World Bank World Development Indicators',
                'source_url': f'https://data.worldbank.org/indicator/{code}',
                'caveat': caveat}

    income = measure('NY.GNP.PCAP.PP.CD', 'GNI per capita, PPP',
                     'current international dollars per person per year',
                     'National income divided by all residents, adjusted for purchasing power; not salary, household income or expected personal earnings.')
    life = measure('SP.DYN.LE00.IN', 'Period life expectancy at birth', 'years',
                   'A newborn under the observation year mortality rates; not remaining years or predicted lifespan for someone your age.')
    shared_years = None
    for code in DEATH_GROUPS:
        years = {r['year'] for r in indicators.get(code, []) if r['year'] <= as_of_year}
        shared_years = years if shared_years is None else shared_years & years
    death = None
    if shared_years:
        year = max(shared_years)
        values = {code: next(r['value'] for r in indicators[code] if r['year'] == year)
                  for code in DEATH_GROUPS}
        code = max(values, key=values.get)
        death = {
            'label': DEATH_GROUPS[code], 'value': values[code], 'year': year,
            'unit': 'percent of all deaths', 'indicator': code,
            'source': 'WHO Global Health Estimates via World Bank WDI',
            'source_url': f'https://data.worldbank.org/indicator/{code}',
            'groups_compared': {DEATH_GROUPS[k]: v for k, v in values.items()},
            'caveat': 'Largest of three broad cause groups, across all ages and sexes; not a specific disease or your most likely future cause. Pandemic categories may be reported separately.',
        }
    cause_snapshot = _causes()
    cause_row = cause_snapshot['countries'].get(country_code)
    cause = None
    if cause_row and cause_row['year'] <= as_of_year:
        cause = {
            **cause_row, 'unit': 'deaths per 100,000 population',
            'source': cause_snapshot['source'], 'source_url': cause_snapshot['source_url'],
            'caveat': 'Leading WHO-ranked cause in the whole population, all ages and both sexes, in 2021; not your personal future cause of death. Pandemic-year rankings may differ from later years.',
        }
    return {
        'country_code': country_code, 'country_name': country.get('name'),
        'as_of_year': as_of_year, 'snapshot_retrieved_at': snapshot['retrieved_at'],
        'income': income, 'life_expectancy': life, 'leading_death_category': death,
        'leading_death_cause': cause,
        'caveats': [
            'Country-level context only; no unsupported adjustment for city, birth year or socioeconomic group.',
            'Latest available observations are not necessarily measurements from today.',
            'Missing observations remain unavailable; no other country is substituted.',
        ],
    }

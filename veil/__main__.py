"""Run with python3 -m veil [birth-year] [--seed any-text] [--json]."""
import argparse
from datetime import date
import json
import random
import secrets
import shlex

from .births import draw_country
from .outcomes import get_outcomes
from .settlements import draw_settlement, draw_socioeconomic
from .history import draw_early_life
from .culture import describe_culture


def likelihood_label(probability):
    """Turn a probability into a plain-language rarity label."""
    if probability is None:
        return 'unknown'
    if probability >= 0.05:
        return 'fair'
    if probability >= 0.01:
        return 'rare'
    return 'very rare'


def draw_death_cause(outcomes, rng):
    """Choose a broad cause using the country's observed cause shares."""
    row = outcomes.get('leading_death_category')
    if not row or not row.get('groups_compared'):
        return None
    groups = {label: value for label, value in row['groups_compared'].items() if value is not None and value >= 0}
    total = sum(groups.values())
    if not groups or total <= 0:
        return None
    draw = rng.random() * total
    cumulative = 0
    selected = next(iter(groups))
    for label, value in groups.items():
        cumulative += value
        if draw <= cumulative:
            selected = label
            break
    return {
        'label': selected,
        'share': groups[selected],
        'probability': groups[selected] / total,
        'year': row['year'],
        'source_url': row['source_url'],
    }


def _clean_story(value):
    """Keep the structured result focused on the drawn story."""
    if isinstance(value, dict):
        return {key: _clean_story(item) for key, item in value.items()
                if key not in {'caveat', 'caveats', 'method', 'adult_life_conditional'}}
    if isinstance(value, list):
        return [_clean_story(item) for item in value]
    return value


def create_story(year, seed, today_year=None):
    today_year = today_year if today_year is not None else date.today().year
    rng = random.Random(str(seed))
    country = draw_country(year, rng)
    story = {
        'title': 'VEIL — behind the veil of ignorance', 'birth_year': year,
        'age_this_year': today_year - year, 'as_of_year': today_year,
        'seed': str(seed), 'country': country,
        'settlement': draw_settlement(country['code'], year, rng),
        'socioeconomic': draw_socioeconomic(rng),
        'outcomes': get_outcomes(country['code'], today_year),
    }
    # Separate streams keep new narrative layers from reshuffling the birthplace.
    story['early_life'] = draw_early_life(country['code'], year, random.Random(f'{seed}:early-life'), today_year)
    if story['early_life'].get('alive_today') is False:
        story['early_life']['cause_of_death'] = draw_death_cause(story['outcomes'], random.Random(f'{seed}:death-cause'))
    story['culture'] = describe_culture(country['code'], year, random.Random(f'{seed}:culture'))
    return _clean_story(story)


def render(story):
    c, city, group, o = (story[k] for k in ('country', 'settlement', 'socioeconomic', 'outcomes'))
    early = story['early_life']
    alive_today = early.get('alive_today', early['outcome'] == 'survived_to_five')
    lines = [
        '', 'V E I L', 'behind the veil of ignorance',
        'A birthplace drawn before you know your place in the world.', '',
        f"The year is {story['birth_year']}. The place could have been different.", '',
        f"You draw {c['name']}.",
        f"{c['births']:,} estimated births that year. {c['probability']:.2%} · {likelihood_label(c['probability'])}.",
        '', f"Place  ·  {city['name']}",
        f"          {city['year']} population estimate.",
        f"          {city.get('detail') or 'Settlement detail unavailable for this year.'}",
        '', f"Circumstances  ·  {group['name']}",
        f"                 Fifth of the national income distribution · {likelihood_label(group.get('probability'))}.",
    ]
    lines += ['', f"At birth in {story['birth_year']}"]
    if early['life_expectancy_at_birth'] is not None:
        lines += [f"Life expectancy  ·  {early['life_expectancy_at_birth']:.0f} years",
                  '                   Birth-year period average, already including infant deaths.']
    else:
        lines += ['Life expectancy  ·  No birth-year observation.']
    if early['infant_death_probability'] is not None:
        lines += [f"Before age one   ·  {early['infant_death_probability']:.1%} risk of death",
                  f"Before age five  ·  {early['under_five_death_probability']:.1%} risk of death (includes infancy)"]
    if early['life_status'] == 'died_in_infancy':
        lines += ['', 'In this draw, this life ends before its first birthday.']
    elif early['life_status'] == 'died_in_early_childhood':
        lines += ['', f"In this draw, this life ends at age {early['age_at_death']:.0f}."]
    elif early['life_status'] == 'died_later':
        lines += ['', f"In this draw, this life ends at age {early['age_at_death']:.0f}."]
    elif alive_today:
        lines += ['', f"In this draw, this life is still alive at age {early['age_now']}."]
    if not alive_today and early.get('cause_of_death'):
        cause = early['cause_of_death']
        lines += [f"Cause of death  ·  {cause['label']} ({cause['year']})",
                  f"                 {cause['share']:.0f}% of recorded deaths in this country."]
    elif early['life_status'] == 'unavailable':
        lines += ['', 'Childhood survival  ·  No observation.']
    lines += ['', 'The household and culture around this life']
    for key, label in [('language', 'The language you speak'), ('religion', 'The faith around your home'), ('food', 'The food around you'), ('music', 'The music around you')]:
        value = story['culture'].get(key)
        if value:
            lines += [value['text']]
    lines += ['Culture  ·  Language, faith, food and music around this birthplace.']
    if city['kind'] in ('rural', 'urban') and story['culture'].get('terrain'):
        lines += [f"The landscape around you  ·  {story['culture']['terrain']}"]
    if not alive_today:
        lines += ['']
    else:
        lines += ['', f"You would turn {story['age_this_year']} in {story['as_of_year']}.",
                  'Current country comparisons:']
    income, life, death = (o[k] for k in ('income', 'life_expectancy', 'leading_death_category'))
    if alive_today and income:
        lines += [f"Income context  ·  {income['value']:,.0f} international dollars / person / year ({income['year']})",
                  '                   Purchasing-power-adjusted GNI per capita.']
    elif alive_today:
        lines += ['Income context  ·  No observation available.']
    if alive_today and life:
        lines += [f"For comparison  ·  Today's newborn life expectancy: {life['value']:.0f} years ({life['year']})",
                  '                   Period measure for a newborn in that year.']
    elif alive_today:
        lines += ['Life expectancy  ·  No observation available.']
    specific = o.get('leading_death_cause')
    if alive_today and specific:
        lines += [f"Most likely cause of death  ·  {specific['label']} ({specific['year']})",
                  f"                 WHO estimate for all ages and both sexes ({specific['year']})."]
    elif alive_today and death:
        lines += [f"Most likely cause of death  ·  {death['label']} ({death['year']})",
                  f"                 {death['value']:.1f}% of deaths; largest of three broad groups.",
                  '                 Largest broad category across all ages and sexes.']
    elif alive_today:
        lines += ['Death context  ·  No comparable observation available.']
    lines += ['', 'The life drawn from the veil.', '',
              f"Birth data: UN WPP 2024 / Our World in Data; {c['coverage']:.3%} of world births covered.",
              f"City data: {city['source']}",
              f"City denominator: {city['population_source']}",
              f"Birth source: {c['url']}"]
    if city.get('urban_source'):
        lines += [f"Urban/rural source: {city['urban_source']}"]
    for key, url in early['source_urls'].items():
        lines += [f"Birth-year {key.replace('_', ' ')}: {url}"]
    for key in ('language', 'religion', 'food', 'music'):
        row = story['culture'].get(key)
        if row and row.get('source_url'):
            lines += [f"{key.title()} source: {row['source_url']}"]
    for row in (() if not alive_today else (income, life, specific or death)):
        if row:
            lines += [f"{row['label']}: {row['source_url']}"]
    lines += [f"Repeat this draw: python3 -m veil {story['birth_year']} --seed {shlex.quote(story['seed'])}", '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='VEIL: a sourced birthplace lottery. Historical years: 1950–2023.')
    parser.add_argument('year', nargs='?', type=int, help='Your year of birth, 1950–2023')
    parser.add_argument('--seed', help='Repeatable draw; any text. Omit for a fresh draw.')
    parser.add_argument('--json', action='store_true', help='Structured result with sources and limitations')
    args = parser.parse_args(argv)
    try:
        year = args.year
        if year is None:
            year = int(input('Your year of birth (1950–2023): '))
        story = create_story(year, args.seed if args.seed is not None else secrets.token_hex(6))
    except (ValueError, EOFError) as error:
        parser.error(str(error) or 'A year is required.')
    print(json.dumps(story, indent=2, ensure_ascii=False) if args.json else render(story))


if __name__ == '__main__':
    main()

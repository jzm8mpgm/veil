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


def create_story(year, seed, today_year=None):
    today_year = today_year if today_year is not None else date.today().year
    rng = random.Random(str(seed))
    country = draw_country(year, rng)
    return {
        'title': 'VEIL — another beginning', 'birth_year': year,
        'age_this_year': today_year - year, 'as_of_year': today_year,
        'seed': str(seed), 'country': country,
        'settlement': draw_settlement(country['code'], year, rng),
        'socioeconomic': draw_socioeconomic(rng),
        'outcomes': get_outcomes(country['code'], today_year),
    }


def render(story):
    c, city, group, o = (story[k] for k in ('country', 'settlement', 'socioeconomic', 'outcomes'))
    lines = [
        '', 'V E I L', 'another beginning', '',
        f"The year is {story['birth_year']}. The place could have been different.", '',
        f"You draw {c['name']}.",
        f"{c['births']:,} estimated births that year. A {c['probability']:.2%} chance in this draw.",
        '', f"Place  ·  {city['name']}",
        f"          {city['year']} population proxy; city birth counts are unavailable.",
        f"          {city['covered_cities']} cities covered in this country; other places remain in the draw.",
        '', f"Circumstances  ·  {group['name']}",
        '                 Illustrative 20% draw, not measured birth odds.',
        '', f"You would turn {story['age_this_year']} in {story['as_of_year']}.",
        'If you still lived there, the latest country-level comparisons are:', '',
    ]
    income, life, death = (o[k] for k in ('income', 'life_expectancy', 'leading_death_category'))
    if income:
        lines += [f"Income context  ·  {income['value']:,.0f} international dollars / person / year ({income['year']})",
                  '                   Purchasing-power-adjusted GNI per capita, not expected earnings.']
    else:
        lines += ['Income context  ·  No observation available.']
    if life:
        lines += [f"Life expectancy  ·  {life['value']:.1f} years at birth ({life['year']})",
                  '                   A newborn measure, not your remaining life or predicted age at death.']
    else:
        lines += ['Life expectancy  ·  No observation available.']
    specific = o.get('leading_death_cause')
    if specific:
        lines += [f"Leading cause  ·  {specific['label']} ({specific['year']})",
                  f"                 {specific['caveat']}"]
    elif death:
        lines += [f"Death context  ·  {death['label']} ({death['year']})",
                  f"                 {death['value']:.1f}% of deaths; largest of three broad groups.",
                  '                 Not a specific disease or a prediction of your death.']
    else:
        lines += ['Death context  ·  No comparable observation available.']
    lines += ['', 'These are population comparisons. Your story remains unwritten.', '',
              f"Birth data: UN WPP 2024 / Our World in Data; {c['coverage']:.3%} of world births covered.",
              'Country draw uses source country/area boundaries, not historical political borders.',
              f"City data: {city['source']}",
              f"City denominator: {city['population_source']}",
              f"City method: {city['method']}",
              f"City limits: {city['caveat']}",
              f"Birth source: {c['url']}"]
    for row in (income, life, specific or death):
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

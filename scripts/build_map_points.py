#!/usr/bin/env python3
"""Build the compact map lookup from downloaded capital/city CSVs.

Usage: python scripts/build_map_points.py /tmp/countries.csv /tmp/world_cities_geo.csv
Only cities present in the bundled settlement sample are retained.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(value):
    return re.sub(r'[^a-z0-9]', '', value.casefold())


def build(capital_path, cities_path):
    capitals, iso2_to_iso3 = {}, {}
    with open(capital_path, encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            if row.get('ISO3') and row.get('LATITUDE') and row.get('LONGITUDE'):
                code = row['ISO3']
                capitals[code] = {'name': row['CAPITAL'], 'lat': float(row['LATITUDE']), 'lng': float(row['LONGITUDE'])}
                iso2_to_iso3[row['ISO2']] = code

    country_codes = {}
    with (ROOT / 'data/settlements_population.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['Code']:
                country_codes[row['Entity']] = row['Code']
    city_names = {}
    with (ROOT / 'data/settlements_cities.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            country_field = next(field for field in row if 'Annotations' in field and 'Projected' not in field)
            code = country_codes.get(row[country_field])
            if code:
                city_names.setdefault(row['Entity'], set()).add(code)
    city_points = {}
    with open(cities_path, encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            code = iso2_to_iso3.get(row['country'])
            if not code or not row.get('name'):
                continue
            key = norm(row['name'])
            for target, countries in city_names.items():
                if code in countries and norm(target) == key:
                    city_points.setdefault(code, {})[target] = {'lat': float(row['lat']), 'lng': float(row['lng'])}
    output = {
        'source': 'Country capital coordinates from budhash country reference; city coordinates from joelacus/world-cities.',
        'source_urls': [
            'https://gist.github.com/budhash/9c9ab486119de0796d2de33973b63da1',
            'https://github.com/joelacus/world-cities',
        ],
        'capitals': capitals,
        'cities': city_points,
    }
    (ROOT / 'data/map_points.json').write_text(json.dumps(output, separators=(',', ':')) + '\n')
    print(f"Wrote {len(capitals)} capital points and {sum(map(len, city_points.values()))} city points")


if __name__ == '__main__':
    build(*sys.argv[1:])

"""Rebuild offline cultural context: CIA Factbook mirror and FAO/OWID food supply.

No dependencies. The Factbook commit is pinned; food source bytes are fingerprinted.
"""
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import re
import tarfile
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '144d6977b2b01ac1cbd220de754c0a005616760b'
ARCHIVE = f'https://codeload.github.com/factbook/factbook.json/tar.gz/{COMMIT}'
FOOD = 'https://ourworldindata.org/grapher/dietary-composition-by-country'


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()


def fetch(url):
    return subprocess.run(['curl', '-L', '--fail', '--max-time', '120', '-sS', url],
                          check=True, capture_output=True).stdout


def main():
    births = json.loads((ROOT / 'data/births.json').read_text())
    names = {c['name'].casefold(): c['code'] for year in births['years'].values()
             for c in year['countries']}
    names.update({'burma': 'MMR', 'congo, democratic republic of the': 'COD',
                  'congo, republic of the': 'COG', 'korea, north': 'PRK',
                  'korea, south': 'KOR', 'cote d’ivoire': 'CIV',
                  "cote d'ivoire": 'CIV', 'gambia, the': 'GMB',
                  'bahamas, the': 'BHS', 'czechia': 'CZE', 'turkey (turkiye)': 'TUR',
                  'timor-leste': 'TLS', 'eswatini': 'SWZ', 'cabo verde': 'CPV',
                  'micronesia, federated states of': 'FSM', 'czech republic': 'CZE',
                  'drc': 'COD', 'congo (brazzaville)': 'COG', 'the gambia': 'GMB',
                  "côte d'ivoire": 'CIV', 'federated states of micronesia': 'FSM',
                  'the bahamas': 'BHS', 'the dominican': 'DOM', 'macau': 'MAC',
                  'sint maarten': 'SXM', 'saint martin': 'MAF', 'virgin islands': 'VIR',
                  'holy see (vatican city)': 'VAT',
                  'falkland islands (islas malvinas)': 'FLK'})
    raw = fetch(ARCHIVE)
    profiles = {}
    unmatched = []
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.endswith('.json'):
                continue
            doc = json.load(archive.extractfile(member))
            government = doc.get('Government', {})
            country = government.get('Country name', {}).get('conventional short form', {}).get('text', '')
            if country == 'none':
                country = government.get('Country name', {}).get('conventional long form', {}).get('text', '')
            country = clean(country)
            code = names.get(country.casefold())
            society = doc.get('People and Society', {})
            if not code:
                if society:
                    unmatched.append(country)
                continue
            path = '/'.join(member.name.split('/')[1:])
            profiles[code] = {
                'name': country,
                'source_url': f'https://github.com/factbook/factbook.json/blob/{COMMIT}/{path}',
                'language': clean(society.get('Languages', {}).get('text', '') or
                                  society.get('Languages', {}).get('Languages', {}).get('text', '')),
                'religion': clean(society.get('Religions', {}).get('text', '')),
                'terrain': clean(doc.get('Geography', {}).get('Terrain', {}).get('text', '')),
            }
    food_raw = fetch(FOOD + '.csv')
    foods = {}
    for row in csv.DictReader(io.StringIO(food_raw.decode())):
        code = row['Code']
        if code not in names.values():
            continue
        values = {k: float(v) for k, v in row.items()
                  if k not in ('Entity', 'Code', 'Year') and v}
        if values:
            key = max(values, key=values.get)
            foods.setdefault(code, {})[row['Year']] = {'category': key, 'kcal_per_day': values[key]}
    output = {'factbook_commit': COMMIT, 'factbook_archive_sha256': hashlib.sha256(raw).hexdigest(),
              'factbook_source': 'CIA World Factbook, public-domain text via factbook/factbook.json mirror',
              'food_source': 'FAO Food Balances (2025), processed by Our World in Data',
              'food_source_url': FOOD, 'food_csv_sha256': hashlib.sha256(food_raw).hexdigest(),
              'profiles': profiles, 'foods': foods}
    (ROOT / 'data/culture.json').write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'{len(profiles)} country profiles; {len(foods)} countries with food supply')
    print('Unmatched Factbook names:', unmatched)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build matched WPP historical mortality data from downloaded OWID CSVs.

Download each SLUG.csv and SLUG.metadata.json to --cache-dir with a veil-
prefix, then run this script. All three series are percentages/years, not
deaths per thousand. Metadata and raw checksums are retained.
"""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = {
    'life_expectancy': ('life-expectancy', 'Life expectancy'),
    'infant_mortality_percent': ('infant-mortality-rates', 'UNWPP'),
    'under_five_mortality_percent': ('child-mortality-around-the-world', 'Child mortality rate'),
}


def build(cache_dir):
    countries, sources = {}, {}
    for key, (slug, column) in SERIES.items():
        path = cache_dir / f'veil-{slug}.csv'
        raw = path.read_bytes()
        metadata = json.loads((cache_dir / f'veil-{slug}.metadata.json').read_text())
        for row in csv.DictReader(raw.decode().splitlines()):
            code, year = row['Code'], int(row['Year'])
            if not (len(code) == 3 or code == 'OWID_KOS') or not 1950 <= year <= 2023:
                continue
            if row[column]:
                countries.setdefault(code, {}).setdefault(str(year), {})[key] = float(row[column])
        sources[key] = {
            'url': f'https://ourworldindata.org/grapher/{slug}',
            'raw_sha256': hashlib.sha256(raw).hexdigest(), 'metadata': metadata,
        }
    for years in countries.values():
        for row in years.values():
            infant, child = (row.get(k) for k in ('infant_mortality_percent', 'under_five_mortality_percent'))
            if infant is not None and child is not None and not 0 <= infant <= child <= 100:
                raise ValueError('Inconsistent childhood mortality probabilities')
    result = {'retrieved_at': date.today().isoformat(),
              'source': 'UN World Population Prospects (2024), processed by Our World in Data',
              'sources': sources, 'countries': countries}
    (ROOT / 'data/history.json').write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print(f'Historical mortality: {len(countries)} countries/areas')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=Path('/tmp'))
    build(parser.parse_args().cache_dir)

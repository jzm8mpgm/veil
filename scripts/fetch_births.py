#!/usr/bin/env python3
"""Build the compact historical snapshot from an OWID Grapher CSV download.

Download with curl, then run this script with CSV and metadata paths.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def build(csv_path, metadata_path):
    raw = Path(csv_path).read_bytes()
    rows = list(csv.DictReader(raw.decode().splitlines()))
    years = {}
    for row in rows:
        year, code = int(row['Year']), row['Code']
        if not 1950 <= year <= 2023 or not row['Number of births']:
            continue
        entry = years.setdefault(str(year), {'countries': [], 'world_births': None})
        value = int(float(row['Number of births']))
        if code == 'OWID_WRL':
            entry['world_births'] = value
        elif len(code) == 3 or code == 'OWID_KOS':
            entry['countries'].append({'code': code, 'name': row['Entity'], 'births': value})
    for entry in years.values():
        entry['countries'].sort(key=lambda r: r['code'])
        assert entry['world_births'] and len(entry['countries']) > 200
    result = {
        'source': 'UN World Population Prospects (2024), processed by Our World in Data',
        'url': 'https://ourworldindata.org/grapher/number-of-births-per-year',
        'csv_url': 'https://ourworldindata.org/grapher/number-of-births-per-year.csv',
        'downloaded': '2026-09-21',
        'raw_sha256': hashlib.sha256(raw).hexdigest(),
        'metadata': json.loads(Path(metadata_path).read_text()),
        'method': 'Historical estimates only; ISO3 country/area codes plus OWID_KOS. Regional aggregates excluded. Probabilities normalized over covered countries/areas; world coverage reported separately. Current source geography, not historical political borders.',
        'years': years,
    }
    (ROOT / 'data' / 'births.json').write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print(f"Wrote {len(years)} years to data/births.json")


if __name__ == '__main__':
    build(*sys.argv[1:])

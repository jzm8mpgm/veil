#!/usr/bin/env python3
"""Rebuild the compact World Bank outcomes snapshot (network required).

Use --cache-dir /tmp to reuse lore-{countries,income,health}.json downloads.
All source records from 2015 onward are retained for as-of-year selection.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://api.worldbank.org/v2/'
URLS = {
    'countries': BASE + 'country?format=json&per_page=400',
    'income': BASE + 'country/all/indicator/NY.GNP.PCAP.PP.CD?format=json&per_page=30000&date=2015:2026',
    'health': BASE + 'country/all/indicator/SP.DYN.LE00.IN;SH.DTH.NCOM.ZS;SH.DTH.COMM.ZS;SH.DTH.INJR.ZS?source=2&format=json&per_page=30000&date=2015:2026',
}
WHO_URL = 'https://xmart-api-public.who.int/DEX_CMS/GHE_FULL?$filter=FLAG_RANKABLE%20eq%201%20and%20DIM_SEX_CODE%20eq%20%27TOTAL%27%20and%20DIM_AGEGROUP_CODE%20eq%20%27TOTAL%27%20and%20DIM_YEAR_CODE%20eq%202021&$select=DIM_COUNTRY_CODE,DIM_GHECAUSE_CODE,DIM_GHECAUSE_TITLE,VAL_DTHS_RATE100K_NUMERIC,DIM_YEAR_CODE&$top=30000'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path)
    args = parser.parse_args()
    responses = {}
    for key, url in URLS.items():
        cached = args.cache_dir / f'lore-{key}.json' if args.cache_dir else None
        if cached and cached.exists():
            response = json.loads(cached.read_text())
        else:
            with urllib.request.urlopen(url, timeout=90) as handle:
                response = json.load(handle)
        if not isinstance(response, list) or len(response) != 2 or response[0]['pages'] != 1:
            raise ValueError(f'Incomplete API response for {key}')
        responses[key] = response
    countries = {
        row['id']: {'name': row['name'], 'indicators': {}}
        for row in responses['countries'][1]
        if row['region']['id'] != 'NA'
    }
    for key in ('income', 'health'):
        for row in responses[key][1]:
            code, value = row['countryiso3code'], row['value']
            if code not in countries or value is None:
                continue
            series = countries[code]['indicators'].setdefault(row['indicator']['id'], [])
            series.append({'year': int(row['date']), 'value': value})
    for country in countries.values():
        for series in country['indicators'].values():
            series.sort(key=lambda row: row['year'], reverse=True)
    output = {
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'source': 'World Bank World Development Indicators',
        'license': 'CC BY 4.0',
        'license_url': 'https://datacatalog.worldbank.org/int/public-licenses#cc-by',
        'api_urls': URLS,
        'source_updated': {key: responses[key][0].get('lastupdated') for key in ('income', 'health')},
        'countries': countries,
    }
    target = ROOT / 'data/outcomes.json'
    target.write_text(json.dumps(output, separators=(',', ':'), ensure_ascii=False) + '\n')
    print(f'Wrote {len(countries)} country/economy records to {target}')
    cached = args.cache_dir / 'lore-who-causes.json' if args.cache_dir else None
    if cached and cached.exists():
        causes = json.loads(cached.read_text())
    else:
        with urllib.request.urlopen(WHO_URL, timeout=90) as handle:
            causes = json.load(handle)
    if '@odata.nextLink' in causes:
        raise ValueError('WHO result is paginated; refusing incomplete snapshot')
    leaders = {}
    for row in causes['value']:
        code = row['DIM_COUNTRY_CODE']
        value = row['VAL_DTHS_RATE100K_NUMERIC']
        if code not in countries or value is None:
            continue
        if code not in leaders or value > leaders[code]['value']:
            leaders[code] = {
                'label': row['DIM_GHECAUSE_TITLE'], 'value': value,
                'year': row['DIM_YEAR_CODE'], 'cause_code': row['DIM_GHECAUSE_CODE'],
            }
    who_output = {
        'retrieved_at': datetime.now(timezone.utc).isoformat(), 'api_url': WHO_URL,
        'source': 'WHO Global Health Estimates 2021 (published 2024)',
        'source_url': 'https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates/ghe-leading-causes-of-death',
        'method': 'Maximum crude death rate among WHO FLAG_RANKABLE=1 causes, both sexes, all ages, 2021. Ties retain first source row.',
        'countries': leaders,
    }
    target = ROOT / 'data/outcomes_causes.json'
    target.write_text(json.dumps(who_output, separators=(',', ':'), ensure_ascii=False) + '\n')
    print(f'Wrote {len(leaders)} WHO leading-cause records to {target}')


if __name__ == '__main__':
    main()

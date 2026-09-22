"""Transparent settlement proxies; these are not measured birth probabilities."""

import csv
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CITY_SOURCE = "https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities"
POPULATION_SOURCE = "https://ourworldindata.org/grapher/population"
URBAN_SOURCE = "https://ourworldindata.org/grapher/share-of-population-urban"


@lru_cache(maxsize=1)
def _load_urban():
    with (DATA / "settlements_urban.csv").open(encoding="utf-8", newline="") as handle:
        return {(row["Code"], int(row["Year"])): float(row["UrbanPercent"]) / 100
                for row in csv.DictReader(handle)}


@lru_cache(maxsize=1)
def _load():
    population = {}
    codes = {}
    with (DATA / "settlements_population.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            year = int(row["Year"])
            code = row["Code"]
            if len(code) == 3 and 1950 <= year <= 2023:
                codes[row["Entity"]] = code
                population[(code, year)] = float(row["Population"])
    codes["Côte d'Ivoire"] = "CIV"
    cities = {}
    with (DATA / "settlements_cities.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        value_column = reader.fieldnames[3]
        country_column = next(name for name in reader.fieldnames if "Annotations" in name)
        for row in reader:
            year = int(row["Year"])
            if year > 2020 or not row[value_column]:
                continue
            code = codes.get(row[country_column])
            if code:
                cities.setdefault(code, {}).setdefault(row["Entity"], {})[year] = float(row[value_column])
    return population, cities


def draw_settlement(country_code, year, rng):
    """Draw a covered city or residual, using nearest prior five-year data.

    A city with no observation at the selected epoch remains in the residual.
    National population is matched to that epoch, never the requested year.
    """
    population, cities = _load()
    data_year = min(2020, year - year % 5)
    national_total = population.get((country_code, data_year))
    candidates = [
        (name, values[data_year])
        for name, values in sorted(cities.get(country_code, {}).items())
        if data_year in values
    ]
    covered_total = sum(value for _, value in candidates)
    urban_share = _load_urban().get((country_code, data_year))
    result = {
        "name": "Elsewhere in this country (other cities, towns or rural areas)",
        "kind": "unresolved",
        "year": data_year,
        "requested_year": year,
        "source": CITY_SOURCE,
        "population_source": POPULATION_SOURCE,
        "method": "Population-weighted proxy, not birth-weighted; top 100 cities ranked in 2020, fixed 2025 boundaries. Prior five-year observation, capped at 2020.",
        "caveat": "City and national estimates come from different population vintages; city values use UN WPP 2022 totals. Residual includes all places not represented in this city dataset.",
        "covered_cities": len(candidates),
        "covered_population_share": None,
        "probability": None,
        "detail": None,
        "urban_population_share": urban_share,
        "urban_source": URBAN_SOURCE if urban_share is not None else None,
    }
    if urban_share is not None:
        # National definitions and GHSL boundaries differ. Do not subtract city
        # mass from an urban total smaller than the represented cities.
        compatible = bool(national_total and covered_total <= national_total * urban_share)
        city_share = covered_total / national_total if compatible else 0
        result["covered_population_share"] = city_share if compatible else None
        result["method"] += " Urban/rural split uses UN national-definition population shares at the same epoch."
        result["caveat"] = (
            "Population-weighted, not birth-weighted. Urban definitions vary by country and over time; "
            "GHSL city boundaries and national urban classifications are not identical. "
            "Treat their combination as a settlement proxy, not a census allocation."
        )
        if not compatible:
            result["caveat"] += " Named-city allocation withheld because its denominator is missing or city totals exceed national urban population."
        value = rng.random()
        if compatible:
            for name, weight in candidates:
                probability = weight / national_total
                if value < probability:
                    result.update(name=name, kind="city", probability=probability,
                                  detail="A named major city in the historical population sample; its neighbourhood, household and occupation are not modelled.")
                    return result
                value -= probability
        if value < urban_share - city_share:
            result.update(
                name="Other urban area — an unlisted city or town" if compatible else "Urban area — city or town",
                kind="urban", probability=urban_share - city_share,
                detail="Classified as urban under this country's definition. This category includes unlisted large cities as well as smaller towns; its size and exact location are not modelled.",
            )
        else:
            result.update(
                name="Rural area — village or dispersed countryside settlement",
                kind="rural", probability=1 - urban_share,
                detail="Outside areas classified as urban under this country's definition. Village versus dispersed home is descriptive context, not a separately sampled outcome; an exact village and household occupation are not modelled.",
            )
        return result
    if not national_total or not candidates:
        result["name"] = "City or settlement unavailable in this dataset"
        result["caveat"] += " No covered city observation or national denominator for this country and epoch."
        return result
    if covered_total > national_total:
        result["name"] = "City or settlement unavailable: inconsistent source totals"
        result["caveat"] += " Covered-city population exceeds national population; draw withheld."
        return result
    result["covered_population_share"] = covered_total / national_total
    value = rng.random() * national_total
    for name, weight in candidates:
        if value < weight:
            result.update(name=name, kind="city", probability=weight / national_total,
                          detail="A named major city in the historical population sample; its neighbourhood, household and occupation are not modelled.")
            return result
        value -= weight
    result.update(kind="residual", probability=1 - covered_total / national_total)
    return result


def draw_socioeconomic(rng):
    """An explicitly illustrative rank, never a historical birth distribution."""
    quintile = rng.randrange(1, 6)
    labels = ["lowest fifth", "second fifth", "middle fifth", "fourth fifth", "highest fifth"]
    return {
        "name": labels[quintile - 1] + " of the country's income distribution",
        "quintile": quintile,
        "probability": 0.2,
        "source": None,
        "year": None,
        "method": "Illustrative: equal 20% draw across population income quintiles.",
        "caveat": "Not measured socioeconomic status at birth. Fertility differs by income group; no historical birth-by-quintile data is included. Rank does not determine individual earnings or health.",
    }

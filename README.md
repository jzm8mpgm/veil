# Veil

*The year is the same. The beginning is different.*

Veil takes its name from John Rawls's **veil of ignorance**: the thought
experiment of choosing the rules of society before knowing who or where you
will be within it. Here, the veil becomes a birthplace lottery. You enter only
your year; the demographic record chooses a beginning.

A text-first experiment: enter a birth year and draw another birthplace, weighted by the estimated number of live births in each country or area that year. Python 3.10+, standard library only. Runs offline with bundled data; no accounts, tracking, API keys or installations.

## Try it

```bash
cd /home/jzm8mpgm/Projects/veil
python3 -m veil
python3 -m veil 1985 --seed first-light
python3 -m veil 1985 --seed 1
python3 -m veil 1985 --json
python3 -m unittest discover -s tests -v
```

## Streamlit interface

The graphical prototype lives at [`app.py`](app.py). It keeps the draw engine
offline and presents one quiet input, one reveal and an expandable source
panel. The visual system uses an ink background, parchment text, amber light
and restrained typography inspired by the atmosphere of Hollow Knight.

Run it locally after installing the single app dependency:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run streamlit_app.py
```

For Streamlit Community Cloud, connect the GitHub repository, choose `main` as
the branch and `streamlit_app.py` as the entrypoint. (`app.py` also works
locally.) Community Cloud reads the root
`requirements.txt` and `.streamlit/config.toml`; subsequent GitHub commits
become app updates through the connected deployment.

Omit `--seed` for a new draw. A printed seed lets you repeat it against this data/code version. A year without a birthday gives the age you turn this year, not necessarily your age today. JSON exposes the same results for a future web interface.

The seed `1` example was selected to demonstrate a named city (India / Kolkata); it is not representative of how often named cities appear. [Read the full example](EXAMPLE.txt).

## What this prototype can say

| Layer | Method | Limitation |
| --- | --- | --- |
| Country/area | UN WPP 2024 estimated live births in the requested year, 1950–2023 | Source geography rather than historical borders; sampled over covered countries/areas, with global coverage reported |
| City/settlement | Historical population of 100 major cities, weighted against national population | Population is a birth-share proxy; most places are outside this city sample |
| Socioeconomic group | Uniform draw across five income ranks | Illustrative only: equal population fifths are not equal shares of births |
| Income context | Latest available GNI per capita at purchasing power parity | National income per resident, **not expected salary** |
| Birth-year survival | UN WPP period life expectancy plus infant and under-five mortality in the birth year | A period scenario: one draw can end before age one, between one and five, or survive to five |
| Longevity context | Latest available period life expectancy at birth | **Not remaining life expectancy at your current age** |
| Mortality context | Latest comparable observed causes/groups | Population pattern, **not a forecast of your death** |

Country probability is `births(country, year) / sum(births(covered countries, year))`. Regional and income-group aggregates never enter the lottery. Kosovo is retained separately, as in the source. Historical estimates are modelled demographic estimates, not a complete register of individual births. 2024 onwards is excluded because this edition labels those years projections.

Settlement draws use the previous five-year observation, capped at 2020. “Elsewhere” includes unlisted cities, towns and rural areas; it does not mean rural. Countries outside the city sample say unavailable. See [settlement methods](data/settlements_sources.md). City and national population datasets have different vintages, explicitly reported. No invented adjustment links city or socioeconomic rank to income or health.

When the city sample is compatible with a country's historical urban share, the settlement draw splits the remainder into an unlisted urban area or a rural area described as a village/dispersed countryside setting. It does not invent an exact village, household or occupation. The rural label is a population-class context, not a claim that every non-city birth happened on a farm.

The birth-year life section uses the requested year's period life expectancy, infant mortality and under-five mortality. The infant and under-five outcomes are mutually exclusive: an infant death is not counted again in the under-five band. A child who dies in the simulated early-life draw does not receive adult earnings, present-day age or adult music/food experiences. The rates hold the birth-year mortality schedule fixed; they are not a reconstruction of one observed birth cohort.

The cultural section describes country-level surroundings: listed languages, religious composition, the largest calorie-supply category as a staple proxy, and an explicitly illustrative local soundscape. It does not assign a personal language, faith, favourite food or listening history. The Factbook source is a pinned public-domain mirror; food categories come from FAO supply data processed by OWID. See the source URLs in each result.

The counterfactual assumes continued residence in the drawn country. Migration, survival to today, occupation, sex, family circumstances and social mobility are not modelled. Today's comparison means the latest available observation in the bundled snapshot, not a measurement made today. Missing values remain missing.

## Data and refresh

Snapshot retrieved 21 September 2026. Sources and observation years accompany every real measure in the JSON output. Source datasets remain under their respective terms; no blanket software license is applied to third-party data.

See [outcome attribution and reuse terms](data/outcomes_sources.md), including WHO's separate data terms. Permission for redistributing the extracted WHO snapshot in a public creative app needs resolving before that release.

- Births: [UN WPP 2024, processed by Our World in Data](https://ourworldindata.org/grapher/number-of-births-per-year). Original chart metadata and raw CSV checksum are embedded in `data/births.json`.
- Cities: [European Commission JRC / GHSL, processed by OWID](https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities), with [national population](https://ourworldindata.org/grapher/population).
- Income: [World Bank GNI per capita, PPP](https://data.worldbank.org/indicator/NY.GNP.PCAP.PP.CD).
- Longevity: [World Bank life expectancy at birth](https://data.worldbank.org/indicator/SP.DYN.LE00.IN).
- Mortality groups: [WHO Global Health Estimates via World Bank](https://data.worldbank.org/indicator/SH.DTH.NCOM.ZS).
- Leading specific causes: [WHO Global Health Estimates 2021, published 2024](https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates/ghe-leading-causes-of-death), 183 countries. The largest crude death rate among WHO's rankable causes, both sexes and all ages. This pandemic-year observation can rank COVID-19 first; it is not a forecast. Broad groups provide the fallback where available.
- Birth-year survival: [UN WPP 2024 life expectancy](https://ourworldindata.org/grapher/life-expectancy), [infant mortality](https://ourworldindata.org/grapher/infant-mortality-rates), and [under-five mortality](https://ourworldindata.org/grapher/child-mortality-around-the-world), all processed by OWID. The bundled `data/history.json` records source metadata and checksums.

To rebuild births, download the chart `.csv` and `.metadata.json`, then run `python3 scripts/fetch_births.py /path/to/births.csv /path/to/metadata.json`. To rebuild historical survival, place the three `veil-*.csv` and metadata files in `/tmp` and run `python3 scripts/fetch_history.py`. `python3 scripts/fetch_outcomes.py` refreshes the outcome snapshot and requires network access. The runtime never makes network requests.

## Next version

The statistical work still needed for the complete concept is substantial: broader historical settlement coverage and local fertility estimates; birth distributions by socioeconomic group (for example, harmonised household surveys); comparable earnings distributions and mobility; remaining-life tables conditional on age and sex; and age-specific competing mortality risks. A plausible narrative must not imply these have already been estimated.

The web version can reuse the pure Python result model behind a small endpoint, or export the compact snapshots to a static JavaScript app. Keep the experience to one input, one reveal, and an expandable source panel. No frontend framework is needed for the first visual experiment.

Visual direction: midnight blue and charcoal, chalk-white serif typography, a single softly lit point becoming a birthplace, restrained motion and ample empty space. Aim for the quiet, cavernous atmosphere that makes Hollow Knight memorable, with original artwork and composition. Respect reduced-motion preferences and keyboard navigation. No graphics or web app are implemented yet.

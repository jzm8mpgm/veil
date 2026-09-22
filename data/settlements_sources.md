# Settlement data

Downloaded 2026-09-21 from:

- https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities.csv
- https://ourworldindata.org/grapher/population.csv

City source: European Commission, Joint Research Centre (2025), GHS-WUP-MTUC R2025A; Schiavina, Alessandrini, Melchiorri and Dijkstra. DOI: 10.2905/1ea967e5-bedc-4cf3-a0b0-3851742ee7e2. Minor processing by Our World in Data. City source and methodology: https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities

Only historical observations through 2020 are used. The CSV also contains projections which the module ignores. Coverage is the 100 largest cities ranked in 2020, using fixed 2025 city boundaries. Missing low-plausibility observations are omitted by OWID. Years between observations use the preceding five-year point, explicitly reported. Years after 2020 use 2020.

National population: Our World in Data population series, with UN World Population Prospects historical estimates in the years used. See https://ourworldindata.org/grapher/population for current full attribution and source license. Different source vintages are explicitly identified: the GHSL city source uses WPP 2022 national totals. A covered-city total exceeding the country total withholds the draw instead of renormalising.

The draw weights each covered city against the national population in the same observation year. The residual means *all other places*, including unlisted large cities, smaller cities, towns and rural areas. It is not a rural probability. Countries without covered cities remain unresolved. Population shares are a proxy for birth shares; there is no claim to measured births by city.

OWID processing is CC BY 4.0; original third-party source terms also apply. Cite the original providers when redistributing these data.

Socioeconomic quintiles are an illustrative uniform draw only. No socioeconomic source dataset is bundled, and no association between quintile and earnings or mortality is inferred.

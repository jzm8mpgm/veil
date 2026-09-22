# Settlement data

Downloaded 2026-09-21 from:

- https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities.csv
- https://ourworldindata.org/grapher/population.csv

City source: European Commission, Joint Research Centre (2025), GHS-WUP-MTUC R2025A; Schiavina, Alessandrini, Melchiorri and Dijkstra. DOI: 10.2905/1ea967e5-bedc-4cf3-a0b0-3851742ee7e2. Minor processing by Our World in Data. City source and methodology: https://ourworldindata.org/grapher/population-of-the-worlds-largest-cities

Only historical observations through 2020 are used. The CSV also contains projections which the module ignores. Coverage is the 100 largest cities ranked in 2020, using fixed 2025 city boundaries. Missing low-plausibility observations are omitted by OWID. Years between observations use the preceding five-year point, explicitly reported. Years after 2020 use 2020.

National population: Our World in Data population series, with UN World Population Prospects historical estimates in the years used. See https://ourworldindata.org/grapher/population for current full attribution and source license. Different source vintages are explicitly identified: the GHSL city source uses WPP 2022 national totals. A covered-city total exceeding the country total withholds the draw instead of renormalising.

The draw weights each covered city against the national population in the same observation year. Historical urban shares now divide the remainder into other urban areas and rural areas. Other urban areas include unlisted large cities as well as smaller towns; no particular town size or exact rural village is inferred. Population shares are a proxy for birth shares; fertility differences between urban and rural areas are not modelled.

## Historical urban and rural split

Downloaded 2026-09-22: https://ourworldindata.org/grapher/share-of-population-urban.csv

Original provider: United Nations, Department of Economic and Social Affairs, Population Division (2025), World Urbanization Prospects: The 2025 Revision, Online Edition, POP/DB/WUP/Rev.2025/F15. Minor processing by Our World in Data. Methodology: https://ourworldindata.org/grapher/share-of-population-urban and https://population.un.org/wup/ . Snapshot `settlements_urban.csv` retains country-code rows in 1950–2023, with no projected values. Refresh using `python3 scripts/fetch_settlements_urban.py`.

Urban and rural mean the country's own statistical definitions. Those definitions vary between countries and may change over time. The sampled probabilities at the city observation epoch are: each covered city population divided by national population; other urban = national urban share minus covered-city share; rural = 1 minus national urban share. Their sum is one. This explicitly combines non-identical GHSL and national definitions as a proxy, not an exact census decomposition. Where city totals exceed national urban population or the national denominator is missing, named cities are withheld and the national urban/rural split alone is used. Countries with no named cities can therefore still yield meaningful rural/urban detail. When urban data is absent the original unresolved residual remains, never labelled rural.

The displayed rural name describes a class of settlement, not a draw between villages and dispersed homes. It makes no inference about farming, household occupation or an exact locality. Any country terrain shown separately describes the country's geographic context, not a sampled village's terrain.

OWID processing is CC BY 4.0; original third-party source terms also apply. Cite the original providers when redistributing these data.

Socioeconomic quintiles are an illustrative uniform draw only. No socioeconomic source dataset is bundled, and no association between quintile and earnings or mortality is inferred.

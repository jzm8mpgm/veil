# Birth-year survival data

`history.json` bundles three country-year series for 1950–2023 from the UN
World Population Prospects 2024 revision, processed by Our World in Data:

- period life expectancy at birth;
- infant mortality: probability of dying before age one;
- under-five mortality: probability of dying before age five.

The probabilities are period measures: if the year's age-specific death rates
stayed unchanged. They are not the observed fate of a named cohort. The runtime
uses infant risk first, then the increment from infancy to age five, then
survival to five. This prevents double counting. See the per-series metadata
inside `data/history.json` for citations, checksums and definitions.

The model intentionally stops its personal narrative at age five. It does not
invent a childhood cause of death, adult survival, earnings or adult tastes for
a simulated child who dies early.

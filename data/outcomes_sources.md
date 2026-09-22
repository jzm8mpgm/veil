# Country outcome snapshots

`outcomes.json` contains World Bank World Development Indicators observations
from 2015 onward, retrieved 21 September 2026. Aggregate regions are excluded
using the country API's region classification. It covers 217 economies: income
is available for 198, life expectancy for 217 and broad death groups for 185.
Missing values are retained as unavailable by the application.

- Income: [NY.GNP.PCAP.PP.CD](https://data.worldbank.org/indicator/NY.GNP.PCAP.PP.CD),
  GNI per capita at purchasing power parity, current international dollars.
  Most latest values are 2025. This is national income per resident, not wages.
- Life expectancy: [SP.DYN.LE00.IN](https://data.worldbank.org/indicator/SP.DYN.LE00.IN),
  latest 2024. Period life expectancy at birth does not estimate remaining years
  of life for an adult and is not a cohort lifespan prediction.
- Broad causes: SH.DTH.NCOM.ZS, SH.DTH.COMM.ZS, SH.DTH.INJR.ZS; latest 2021,
  WHO Global Health Estimates via WDI. These compare three broad groups at a
  shared year and do not identify a disease.
- WDI data: [CC BY 4.0 and dataset terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by).

`outcomes_causes.json` contains the leading cause among the WHO rankable causes
for 183 countries, for 2021, both sexes and all ages. The crude death rate is
per 100,000 residents. It is not the proportion of all deaths or an individual's
probability of dying. A cause can rank first without causing most deaths.

Source: Global Health Estimates 2021: Deaths by Cause, Age, Sex, by Country and
by Region, 2000–2021. Geneva, World Health Organization; 2024.
[WHO source and methods](https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates/ghe-leading-causes-of-death).
The download uses the same GHE_FULL API and FLAG_RANKABLE filter as WHO's top-ten
interactive chart. The complete query is recorded in the snapshot. 24,522 rows
were compared to select a maximum rate per country; the refresh refuses a
paginated response to avoid silently using an incomplete dataset.

WHO data are separately governed by [WHO data terms](https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions),
not the code's license. These terms grant use for public health purposes,
require attribution, prohibit commercial promotion and restrict dataset
modifications beyond minimal figure/table styling. Do not describe this
snapshot as unrestricted open data. Resolve the applicable permission for
redistribution of the extracted snapshot in a public creative or commercial
app before publishing it.

Attribution: WHO, Global Health Estimates 2021: Deaths by Cause, Age, Sex, by
Country and by Region, 2000–2021, published 2024, accessed 21 September 2026.
Acknowledgement is made to the countries that supplied the underlying data.
WHO does not endorse this project or its interpretation of the estimates.

2021 is a pandemic year: COVID-19 is the leading cause in some countries.
These are population observations, not forecasts for a newborn or current
adult. Income, lifespan and mortality are not adjusted for city or wealth rank.
The as-of filter selects observation years from today's data vintage; it does
not reconstruct what was known at that historical time.

Refresh from the project directory: `python scripts/fetch_outcomes.py`.

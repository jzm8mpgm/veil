# Interactive map data

`map_points.json` contains a compact coordinate lookup for the Streamlit
visualisation. Country points use the latitude and longitude fields in the
country reference; named settlement points use matching entries from the
world-cities reference. The app uses a named city point when one is available
and the country point for an urban, rural or unmatched settlement draw.

- Country coordinates: [budhash country reference](https://gist.github.com/budhash/9c9ab486119de0796d2de33973b63da1)
- City coordinates: [joelacus/world-cities](https://github.com/joelacus/world-cities)

Regenerate with `python3 scripts/build_map_points.py /path/to/countries.csv
/path/to/world_cities.csv`. Coordinates support visual orientation; the
demographic draw remains weighted by the population data described elsewhere.

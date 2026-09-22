"""Refresh the historical UN national-definition urban share snapshot."""

import argparse
import csv
import io
from pathlib import Path
from urllib.request import urlopen

SOURCE = "https://ourworldindata.org/grapher/share-of-population-urban.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Use an already downloaded source CSV")
    args = parser.parse_args()
    text = args.input.read_text() if args.input else urlopen(SOURCE, timeout=90).read().decode()
    reader = csv.DictReader(io.StringIO(text))
    value_column = reader.fieldnames[3]
    rows = []
    for row in reader:
        if (len(row["Code"]) == 3 or row["Code"] == "OWID_KOS") and 1950 <= int(row["Year"]) <= 2023:
            value = float(row[value_column])
            if not 0 <= value <= 100:
                raise ValueError("Urban share outside 0–100")
            rows.append((row["Entity"], row["Code"], row["Year"], value))
    if not rows:
        raise ValueError("No historical urban shares")
    output = Path(__file__).resolve().parents[1] / "data/settlements_urban.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Entity", "Code", "Year", "UrbanPercent"])
        writer.writerows(rows)
    print(f"Saved {len(rows)} historical urban shares to {output}")


if __name__ == "__main__":
    main()

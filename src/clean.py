r"""
Step 5: Turn DGCA's airline Excel files into one tidy table.

Reads the files saved by download.py, keeps only scheduled domestic flights for the
months we want, and saves one row per airline per month to data/clean/airline_monthly.csv.

How to run (from the project folder):
    .venv\Scripts\python.exe src\clean.py
"""

from pathlib import Path

import openpyxl
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw" / "excel"
CLEAN_FOLDER = PROJECT_FOLDER / "data" / "clean"
OUTPUT_FILE = CLEAN_FOLDER / "airline_monthly.csv"

# The months we want, as year-month
FIRST_MONTH = "2025-09"
LAST_MONTH = "2026-08"

# Start of each file name (from download.py) -> (display name, airline group)
AIRLINES = {
    "indigo": ("IndiGo", "IndiGo"),
    "air_india": ("Air India", "Air India Group"),
    "air_india_express": ("Air India Express", "Air India Group"),
    "akasa_air": ("Akasa Air", "Akasa Air"),
    "spicejet": ("SpiceJet", "SpiceJet"),
    "alliance_air": ("Alliance Air", "Alliance Air"),
    "star_air": ("Star Air", "Star Air"),
    "fly91": ("Fly91", "Fly91"),
    "flybig": ("Flybig", "Flybig"),
    "indiaone_air": ("IndiaOne Air", "IndiaOne Air"),
}

# DGCA writes month names in different ways ("JUN", "JUNE")
MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUNE": 6,
    "JUL": 7, "JULY": 7, "AUG": 8, "SEP": 9, "SEPT": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

# Column position in DGCA's table -> our column name
COLUMNS = {
    1: "departures",
    2: "hours",
    4: "passengers",
    5: "passenger_km_thousand",
    6: "seat_km_thousand",
    7: "load_factor_pct",
}


def to_number(value):
    """Turn a DGCA cell into a number. Blanks and dashes count as 0."""
    if value is None or str(value).strip() in ("", "-"):
        return 0
    return float(str(value).replace(",", ""))


def read_scheduled_domestic(path):
    """Read the 'Scheduled Domestic Services' table from one DGCA file.

    Each file stacks up to four tables (scheduled/non-scheduled, domestic/international),
    each starting with a title row. We only keep rows from the scheduled domestic one.
    """
    year = int(path.stem[-4:])  # file names end in the year, e.g. indigo_2026
    sheet = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]

    rows = []
    in_wanted_table = False
    for row in sheet.iter_rows(values_only=True):
        text = " ".join(" ".join(str(c) for c in row if isinstance(c, str)).split())
        if "Traffic And Operating Statistics" in text:
            in_wanted_table = "Scheduled Domestic" in text and "Non-" not in text
            continue

        label = str(row[0]).strip().upper() if row[0] is not None else ""
        if not in_wanted_table or label not in MONTHS:
            continue
        # Months DGCA hasn't filled in yet have a name but no numbers
        if all(c in (None, "", "-") for c in row[1:8]):
            continue

        record = {"month": f"{year}-{MONTHS[label]:02d}"}
        for position, name in COLUMNS.items():
            record[name] = to_number(row[position])
        rows.append(record)
    return rows


def main():
    # 1. Read every airline's files into one table
    records = []
    for path in sorted(RAW_FOLDER.glob("*.xlsx")):
        file_start = path.stem[:-5]  # "indigo_2026" -> "indigo"
        if file_start == "total":
            continue
        airline, group = AIRLINES[file_start]
        for record in read_scheduled_domestic(path):
            records.append({"airline": airline, "airline_group": group, **record})

    table = pd.DataFrame(records)

    # 2. Keep only the months we want
    table = table[(table["month"] >= FIRST_MONTH) & (table["month"] <= LAST_MONTH)]

    # 3. Whole numbers where it makes sense; round the rest
    table["departures"] = table["departures"].astype(int)
    table["passengers"] = table["passengers"].astype(int)
    table["hours"] = table["hours"].round(1)

    # 4. Market share: each airline's passengers as a % of all passengers that month
    month_total = table.groupby("month")["passengers"].transform("sum")
    table["market_share_pct"] = (100 * table["passengers"] / month_total).round(2)

    table = table.sort_values(["month", "passengers"], ascending=[True, False])
    table = table[["month", "airline", "airline_group", "departures", "hours", "passengers",
                   "passenger_km_thousand", "seat_km_thousand", "load_factor_pct",
                   "market_share_pct"]]

    # 5. Check our work before saving
    check(table)

    CLEAN_FOLDER.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(table)} rows to {OUTPUT_FILE.relative_to(PROJECT_FOLDER)}")


def check(table):
    """Stop with a clear message if anything looks wrong."""
    problems = []

    months = sorted(table["month"].unique())
    print(f"Months: {months[0]} to {months[-1]} ({len(months)} months)")
    if len(months) != 12:
        problems.append(f"expected 12 months, found {len(months)}")

    duplicates = table[table.duplicated(["month", "airline"], keep=False)]
    if not duplicates.empty:
        problems.append(f"some airlines appear twice in a month:\n{duplicates}")

    numbers = table.select_dtypes("number")
    if (numbers < 0).any().any():
        problems.append("some numbers are negative")

    # Each month, the airlines should add up to DGCA's own total
    totals = {}
    for path in RAW_FOLDER.glob("total_*.xlsx"):
        for record in read_scheduled_domestic(path):
            totals[record["month"]] = int(record["passengers"])
    print("\nPassengers per month (our airlines vs DGCA total):")
    for month, ours in table.groupby("month")["passengers"].sum().items():
        dgca = totals.get(month, 0)  # 0 if DGCA's total for this month is missing
        ok = "OK" if ours == dgca else "MISMATCH"
        print(f"  {month}: {ours:>12,} vs {dgca:>12,}  {ok}")
        if ours != dgca:
            problems.append(f"{month}: airlines add up to {ours:,}, DGCA total is {dgca:,}")

    if problems:
        raise SystemExit("Problems found, nothing saved:\n- " + "\n- ".join(problems))
    print("All checks passed.")


if __name__ == "__main__":
    main()

r"""
Step 7: Put the tidy tables into the SQLite database (data/aviation.db).

Reads the table made by clean.py and the hand-typed on-time/cancellations file, and saves
each as a database table. Old tables are replaced, so the database always matches the files.

How to run (from the project folder):
    .venv\Scripts\python.exe src\load.py
"""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_FOLDER / "data" / "aviation.db"

# Database table name -> the file it comes from
TABLES = {
    "airline_monthly": PROJECT_FOLDER / "data" / "clean" / "airline_monthly.csv",
    "otp_cancellations": PROJECT_FOLDER / "data" / "manual" / "otp_cancellations.csv",
}


def main():
    for path in TABLES.values():
        if not path.exists():
            raise SystemExit(f"Missing {path.relative_to(PROJECT_FOLDER)}. Run src\\clean.py first.")

    # closing() closes the database file at the end; the inner "database" saves the changes
    with closing(sqlite3.connect(DATABASE_FILE)) as database, database:
        for table_name, path in TABLES.items():
            # Keep month as text ("2025-09") rather than letting pandas guess
            table = pd.read_csv(path, dtype={"month": str})
            table.to_sql(table_name, database, if_exists="replace", index=False)
            print(f"{table_name}: {len(table)} rows loaded")

        # A sample question, to check the tables work together
        print("\nSample: September 2025, airlines with on-time data")
        sample = pd.read_sql(
            """
            SELECT o.airline,
                   SUM(a.passengers)       AS passengers,
                   SUM(a.market_share_pct) AS market_share_pct,
                   o.otp_pct,
                   o.cancellation_rate_pct
            FROM otp_cancellations AS o
            JOIN airline_monthly AS a
              ON a.month = o.month AND a.airline_group = o.airline
            WHERE o.month = '2025-09' AND o.otp_pct IS NOT NULL
            GROUP BY o.airline
            ORDER BY passengers DESC
            """,
            database,
        )
        print(sample.to_string(index=False))

    print(f"\nSaved to {DATABASE_FILE.relative_to(PROJECT_FOLDER)}")


if __name__ == "__main__":
    main()

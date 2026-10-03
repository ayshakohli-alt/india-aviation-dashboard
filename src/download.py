r"""
Step 3: Download DGCA's Excel files of monthly domestic airline traffic.

DGCA publishes one file per airline per year, plus one file with the totals for all
airlines combined. Each file has one row per month. DGCA adds new months to the
current year's files, so run this again to get fresh data.

Files are saved unchanged, with tidy names (e.g. indigo_2026.xlsx). The original
web address of each file is recorded in download_log.csv.

How to run (from the project folder):
    .venv\Scripts\python.exe src\download.py
"""

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

# Where DGCA keeps its domestic traffic files
BASE_URL = (
    "https://public-prd-dgca.s3.ap-south-1.amazonaws.com/InventoryList/dataReports/"
    "aviationDataStatistics/airTransport/domestic/monthly/"
)

# The years we need for September 2025 to August 2026
YEARS = ["25", "26"]

# Our tidy name -> the start of DGCA's file name (DGCA's spacing and capitals are inconsistent)
FILES = {
    "total": "totaldom",
    "indigo": "indigo",
    "air_india": "Air India",
    "air_india_express": "air india express",
    "akasa_air": "akasa air ",
    "spicejet": "spicejet",
    "alliance_air": "alliance air",
    "star_air": "star air",
    "fly91": "fly91 ",
    "flybig": "Flybig",
    "indiaone_air": "india one air",
}

# Where to save them: the project's data/raw/excel folder
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
SAVE_FOLDER = PROJECT_FOLDER / "data" / "raw" / "excel"
LOG_FILE = SAVE_FOLDER / "download_log.csv"


def download(tidy_name, dgca_name, year):
    url = BASE_URL + quote(f"{dgca_name}{year}.xlsx")  # quote() handles spaces in names
    save_as = f"{tidy_name}_20{year}.xlsx"

    response = requests.get(url, timeout=60)

    # DGCA's storage answers 403 or 404 when a file hasn't been published
    if response.status_code in (403, 404):
        print(f"  {save_as}: not published by DGCA, skipped")
        return
    # Stop with a clear error for any other problem
    response.raise_for_status()

    # Excel files always begin with the letters "PK". If not, we got something else,
    # such as an error page, and shouldn't save it.
    if not response.content.startswith(b"PK"):
        raise ValueError(f"{save_as} doesn't look like an Excel file. Not saved.")

    (SAVE_FOLDER / save_as).write_bytes(response.content)

    # Note when and where the file came from
    if not LOG_FILE.exists():
        LOG_FILE.write_text("downloaded_at,file,size_kb,url\n")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    size_kb = len(response.content) // 1024
    with LOG_FILE.open("a") as log:
        log.write(f"{now},{save_as},{size_kb},{url}\n")

    print(f"  {save_as}: saved ({size_kb} KB)")


if __name__ == "__main__":
    SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        print(f"Year 20{year}:")
        for tidy_name, dgca_name in FILES.items():
            download(tidy_name, dgca_name, year)
    print("Done.")

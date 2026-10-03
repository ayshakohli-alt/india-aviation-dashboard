# Plan: Get and clean 12 months of DGCA airline data

This plan explains how we'll collect and tidy up the data for the dashboard.
We'll do **one step at a time**. Before each step, Claude explains what it will do and why,
then pauses afterwards so you can ask questions.

**Status:** Not started yet.

---

## What we found out about the data

DGCA (India's aviation regulator) posts its data on its website, **dgca.gov.in**, under
*Data & Reports → Aviation Statistics → Domestic Air Transport → Monthly Statistics*.

Each month it publishes **two kinds of files**. We need both.

### 1. Excel spreadsheets: the "how many" numbers
- **What's in them:** for each airline, each month: flights flown, **passengers carried**,
  seats available, and **load factor** (how full the planes were, as a percentage).
- **Market share** isn't listed, but it's easy to work out: one airline's passengers ÷ all passengers.
- **Format:** Excel files, one per year (for example `totaldom26.xlsx` for 2026). They sit at fixed
  web addresses, so a small program can download them automatically.
- **Quirks to fix:** extra heading rows, a dash ("-") used to mean zero, and airline names that
  change over time (for example, Vistara merged into Air India in November 2024).

### 2. Monthly "Traffic Data" report: the "how well" numbers
- **What's in it:**
  - **On-time performance (OTP):** the share of flights that ran on time. It's measured only at the
    four big metro airports: Bengaluru, Delhi, Hyderabad and Mumbai.
  - **Cancellation rate** for each airline, plus the reasons (weather, technical faults, etc.)
  - Reasons for delays, passenger complaints, and passengers affected by long delays or denied boarding
  - A repeat of the market share and load factor numbers
- **Format:** a PDF of about 17 pages, made **mostly of bar charts**. When a computer reads it, the
  chart numbers come out scrambled, so OTP and cancellations can't be pulled out reliably by a program.
- **Note:** in these reports, "Air India" includes Air India Express.

### Which 12 months
DGCA publishes each month's data about 3–4 weeks after the month ends. As of early October 2026,
the latest month is **August 2026**. The last 12 months are **September 2025 to August 2026**.

---

## The golden rule
The files we download are **never edited**. All tidying happens in code, or in one clearly
labelled hand-typed file. That way we can always redo everything from scratch.

---

## The 8 steps

### Step 1: Set up Python for the project
- Create a **virtual environment**: a private toolbox just for this project, so its add-ons
  don't mix with anything else on the computer.
- Install the add-ons we need:
  - **pandas** for cleaning tables
  - **DuckDB** for the database
  - **Streamlit** for the dashboard
  - **openpyxl** for reading Excel files
  - **requests** for downloading files
- Create `requirements.txt`, a "shopping list" of those add-ons so they can be reinstalled easily.
- Create `.gitignore`, a list of files Git should *not* include in snapshots (like the toolbox folder).

### Step 2: Create folders
```
data/raw/excel/       ← original Excel files, never edited
data/raw/pdf/         ← original monthly PDF reports, never edited
data/manual/          ← the one hand-typed file (on-time performance & cancellations)
data/aviation.duckdb  ← the cleaned database (made by code)
src/                  ← our Python scripts (small programs)
```

### Step 3: Download the Excel files (automatic)
- A script, `src/download.py`, fetches the 2025 and 2026 Excel files into `data/raw/excel/`.
- It writes down when and where each file came from.

### Step 4: Download the 12 monthly PDF reports (by hand, about 10 minutes)
- The DGCA website doesn't give these files predictable web addresses, so it's simplest to
  download them from the website by hand.
- Save them with clear names, like `data/raw/pdf/2025-09.pdf`, `2025-10.pdf`, and so on.
- Claude will give you the exact clicks.

### Step 5: Clean the Excel data (automatic)
A script, `src/clean.py`, will:
- keep only the 12 months we want
- make one tidy table with **one row per airline per month**, with columns such as
  month, airline, flights, passengers, seats and load factor
- use the same name for each airline every time (for example, "Indigo" and "IndiGo" both become `IndiGo`)
- group Air India and Air India Express together as "Air India Group", the same way DGCA does
- turn dashes into zeros, and make sure numbers are stored as numbers, not text
- work out **market share** for each airline each month

### Step 6: Record on-time performance and cancellations (with Claude's help, checked)
- For each of the 12 PDF reports, Claude reads the report and types the on-time performance and
  cancellation numbers into `data/manual/otp_cancellations.csv`. A `.csv` file is a simple
  spreadsheet saved as plain text.
- That's about 70 rows: one per airline per month.
- Each row notes which PDF and page the number came from, so anyone can check it.
- We'll spot-check some numbers against news reports, and you can open any PDF to compare.
- This is slower than a fully automatic method, but much more reliable for chart-based PDFs.

### Step 7: Put everything into the database
- A script, `src/load.py`, puts both tidy tables into `data/aviation.duckdb`, our single-file
  database, ready for the dashboard.

### Step 8: Save a Git snapshot
- Save the scripts and the hand-typed file in Git.
- Leave out the big downloaded files and the database, because they can be recreated by
  running the scripts again.

---

## How we'll know it worked
- Each script finishes without errors.
- Total domestic passengers for **August 2026** are about **1.21 crore** (12.1 million), matching news reports.
- IndiGo's market share in **July 2026** is about **67%**, matching news reports.
- Every airline appears exactly once for each month, with no blank or negative numbers.
- A few rows of the hand-typed file match the PDF reports when checked side by side.

---

## Sources
- DGCA website: https://www.dgca.gov.in/digigov-portal/
- Example of the DGCA Excel file addresses (from a public GitHub project):
  https://github.com/Vonter/india-aviation-traffic
- Sample monthly report (December 2024):
  https://livefromalounge.com/wp-content/uploads/2025/01/Traffic-Data-Report-December-24.pdf
- August 2026 traffic news (Business Standard):
  https://www.business-standard.com/industry/aviation/domestic-air-passenger-traffic-falls-6-34-to-12-12-million-in-august-dgca-126092300401_1.html

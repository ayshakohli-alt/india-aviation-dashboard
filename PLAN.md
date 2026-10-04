# Plan: Get and clean 12 months of DGCA airline data

This plan explains how we'll collect and tidy up the data for the dashboard.
We'll do **one step at a time**. Before each step, Claude explains what it will do and why,
then pauses afterwards so you can ask questions.

**Status:** Steps 1–3 and 5 done. Steps 4 and 6 partly done: only September 2025 of the 12 monthly reports is downloaded and recorded so far. Next: Step 7.

---

## What we found out about the data

DGCA (India's aviation regulator) posts its data on its website, **dgca.gov.in**, under
*Data & Reports → Aviation Statistics → Domestic Air Transport → Monthly Statistics*.

Each month it publishes **two kinds of files**. We need both.

### 1. Excel spreadsheets: the "how many" numbers
- **What's in them:** for each airline, each month: flights flown, **passengers carried**,
  seats available, and **load factor** (how full the planes were, as a percentage).
- **Market share** isn't listed, but it's easy to work out: one airline's passengers ÷ all passengers.
- **Format:** Excel files, **one per airline per year** (for example `indigo26.xlsx`), plus one file
  per year with the totals for all airlines (`totaldom26.xlsx`). Each has one row per month. They sit at
  fixed web addresses, so a small program can download them automatically.
- **Quirks to fix:** extra heading rows, a dash ("-") used to mean zero, and airline names that
  change over time (for example, Vistara merged into Air India in November 2024).

### 2. Monthly "Traffic Data" report: the "how well" numbers
- **What's in it:**
  - **On-time performance (OTP):** the share of flights that ran on time. It's measured only at the
    six big metro airports: Bengaluru, Delhi, Hyderabad, Mumbai, Chennai and Kolkata (older
    reports, such as December 2024, used only the first four). It's given only for the five
    larger airlines: IndiGo, Air India Group, Akasa Air, SpiceJet and Alliance Air.
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
  - (the database, **SQLite**, is already built into Python, so it doesn't need installing)
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
data/aviation.db      ← the cleaned SQLite database (made by code)
src/                  ← our Python scripts (small programs)
```

### Step 3: Download the Excel files (automatic)
- A script, `src/download.py`, fetches each airline's 2025 and 2026 Excel files, plus the
  all-airline totals, into `data/raw/excel/`, with tidy names like `indigo_2026.xlsx`.
- It writes down when and where each file came from in `download_log.csv`.
- Files DGCA hasn't published are skipped with a note (for example, Flybig has no 2026 file).
- **Checked:** for July and August 2026, the airlines add up exactly to DGCA's total, and
  IndiGo's July share (67.4%) matches the news.

### Step 4: Download the 12 monthly PDF reports (by hand, about 10 minutes)
- The DGCA website doesn't give these files predictable web addresses, so it's simplest to
  download them from the website by hand.
- Save them with clear names, like `data/raw/pdf/2025-09.pdf`, `2025-10.pdf`, and so on.
- Claude will give you the exact clicks.

**Progress (3 October 2026): partly done, continuing with what we have for now.**

| Report | Status |
|---|---|
| September 2025 | ✅ Have it (`2025-09.pdf`) |
| October 2025 – December 2025 | ❌ Missing |
| January 2026 – August 2026 | ❌ Missing |

- So we have **1 of the 12** target months. **11 are still missing**: October, November and
  December 2025, and January to August 2026.
- **Bonus reports:** we also have January, February and April to August **2025**
  (`2025-01.pdf` to `2025-08.pdf`; March 2025 is missing). They're outside our 12-month window,
  but useful for comparing with last year.
- Some later downloads didn't save to the computer. Next time, check the browser's download
  list (Ctrl + J) to see where files went.
- Every report saved so far has been checked: it's a genuine DGCA report for the month in its
  file name, 17 pages long.

### Step 5: Clean the Excel data (automatic)
A script, `src/clean.py`, will:
- keep only the 12 months we want
- make one tidy table with **one row per airline per month**, with columns such as
  month, airline, flights, passengers, seat-kilometres (seats × distance flown) and load factor
- use the same name for each airline every time (for example, "Indigo" and "IndiGo" both become `IndiGo`)
- group Air India and Air India Express together as "Air India Group", the same way DGCA does
- turn dashes into zeros, and make sure numbers are stored as numbers, not text
- work out **market share** for each airline each month

**Done (3 October 2026):** `src/clean.py` saves 110 rows to `data/clean/airline_monthly.csv`
(a plain-text table that also opens in Excel). Checks passed: all 12 months present, each airline
once per month, no negative numbers, and every month adds up exactly to DGCA's total.
Air India and Air India Express are kept as separate rows with an `airline_group` column,
so the dashboard can show them together or apart.

### Step 6: Record on-time performance and cancellations (with Claude's help, checked)
- For each of the 12 PDF reports, Claude reads the report and types the on-time performance and
  cancellation numbers into `data/manual/otp_cancellations.csv`. A `.csv` file is a simple
  spreadsheet saved as plain text.
- That's about 70 rows: one per airline per month.
- Each row notes which PDF and page the number came from, so anyone can check it.
- We'll spot-check some numbers against news reports, and you can open any PDF to compare.
- This is slower than a fully automatic method, but much more reliable for chart-based PDFs.

**Progress (3 October 2026): started with the one report we have.**
- September 2025 is recorded: 10 rows (9 airlines plus "All airlines"). On-time performance is
  on page 6 of the report and cancellations on page 2.
- Airline names match the `airline_group` column of the clean table (for example "Air India Group").
- **How the numbers were checked:** the cancellation chart's text comes out jumbled, so it was
  read in two other modes ("raw" and "table"), which agreed. All 15 numbers were then compared
  automatically against the PDF text, and all matched. The airline rates, weighted by flights,
  come to about 1.07%, close to the report's overall 1.04%.
- **Still to do:** October 2025 to August 2026, once those reports are downloaded (see Step 4).

### Step 7: Put everything into the database
- A script, `src/load.py`, puts both tidy tables into `data/aviation.db`, our single-file
  SQLite database, ready for the dashboard.

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

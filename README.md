# India Aviation Operations Dashboard

An interactive dashboard of how India's domestic airlines are performing: passengers,
market share, load factor, on-time performance and cancellations for IndiGo, Air India
Group, Akasa Air, SpiceJet and smaller carriers. It uses public monthly data from the
**DGCA** (Directorate General of Civil Aviation), India's aviation regulator.

Built with Python, pandas, SQLite and Streamlit.

## What the dashboard shows

- **Headline numbers** for the latest month (passengers, IndiGo's market share, overall
  load factor, airlines flying), each with its change from the previous month
- **Market share over time**, one line per airline group
- **Passengers per month** on scheduled domestic flights
- **On-time performance and cancellation rates** by airline
- **Data tables** behind every chart

A month slider at the top filters the whole page. Each airline keeps one fixed colour on every
chart, and the colours were checked for colour-blind safety in light and dark mode.

## Data

| Data | DGCA source | How it's collected |
|---|---|---|
| Passengers, flights, hours, seat-km, load factor (per airline, per month) | Monthly Statistics: Excel files, one per airline per year | Downloaded automatically by `src/download.py` |
| On-time performance, cancellation rates | Monthly *Traffic Data* reports (PDF, mostly charts) | Read from each report and recorded by hand, with page references, in `data/manual/otp_cancellations.csv` |

**Coverage:** September 2025 to August 2026, scheduled domestic services only.

**Checks built in:**
- For every month, the per-airline passenger numbers add up exactly to DGCA's published total.
- Market shares match published news figures (for example, IndiGo at 67.4% in July 2026).
- Each hand-recorded PDF value was checked against the report text.

**Current limitations:**
- On-time performance and cancellations are recorded for **September 2025 only** so far. More
  months will be added as the monthly reports are processed, and the dashboard picks them up
  automatically.
- On-time performance is published by DGCA for five airlines, measured at six metro airports
  (Bengaluru, Chennai, Delhi, Hyderabad, Kolkata, Mumbai).
- DGCA figures are provisional. Air India and Air India Express appear separately in the Excel
  data and are grouped as "Air India Group", matching DGCA's reports.
- Flybig stopped scheduled flights after October 2025, so it appears only in the first two months.

## How it works

```
DGCA Excel files ──► src/download.py ──► src/clean.py ──► src/load.py ──► data/aviation.db ──► src/dashboard.py
DGCA PDF reports ──► data/manual/otp_cancellations.csv ─────┘
```

| File | What it does |
|---|---|
| `src/download.py` | Downloads each airline's monthly Excel files from DGCA, logging each source address |
| `src/clean.py` | Reads the *scheduled domestic* table from each file, standardises names and numbers, calculates market share, and checks totals |
| `src/load.py` | Loads the clean table and the on-time/cancellations file into a SQLite database |
| `src/dashboard.py` | The Streamlit dashboard |

Downloaded files, the clean table and the database aren't stored in this repository. The
scripts recreate them.

## Run it yourself

Requires Python 3.11 or newer.

```bash
# 1. Create a virtual environment and install the packages
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt     # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # macOS / Linux

# 2. Get and prepare the data
.venv\Scripts\python.exe src\download.py
.venv\Scripts\python.exe src\clean.py
.venv\Scripts\python.exe src\load.py

# 3. Open the dashboard (then go to http://localhost:8501)
.venv\Scripts\streamlit.exe run src\dashboard.py
```

## Project notes

- `PLAN.md` describes the step-by-step plan and what was learned along the way.
- `CLAUDE.md` holds working notes for [Claude Code](https://claude.com/claude-code), which was
  used to build this project.

## Possible next steps

- Add on-time and cancellation data for the remaining months
- Year-on-year comparisons using 2025 reports
- A live flight map of aircraft over India

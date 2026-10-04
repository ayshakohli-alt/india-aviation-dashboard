# India Aviation Operations Dashboard

## About this project

An interactive dashboard about how Indian airlines operate, using public monthly
data from DGCA (Directorate General of Civil Aviation, India's aviation regulator).

The dashboard will show:
- **On-time performance (OTP)**: the share of flights that depart or arrive on schedule
- **Cancellations**: how many flights were cancelled, and why when the data says
- **Passenger numbers**: how many people each airline carried
- **Market share**: each airline's share of all domestic passengers

Airlines covered: IndiGo, Air India (including merged brands such as Air India
Express), Akasa Air, SpiceJet, and any others that appear in the DGCA data.

**Possible later addition:** a live flight map showing aircraft over India. This is
not in scope yet. Don't build it unless the user asks.

## Purpose

1. **Learning:** the user is learning Claude Code hands-on through this project.
2. **Portfolio:** the finished project should show skills that matter for airline
   operations analytics, so it should look clean, have clear charts, and be easy to explain.

## Tech choices

| Tool | What it is | What it does here |
|------|------------|-------------------|
| **Python** | A popular, beginner-friendly programming language | The language for all project code |
| **pandas** | A Python library (a ready-made toolkit) for working with tables of data | Cleans and reshapes the raw DGCA data |
| **SQLite** | A small database stored as a single file, built into Python | Stores the cleaned data and answers questions about it |
| **Streamlit** | A Python library that turns scripts into interactive web pages | Builds the dashboard the user will see and click through |

**Why SQLite, not DuckDB:** DuckDB was the original choice, but Windows Smart App Control
(a security feature that's switched on on the user's computer) blocks DuckDB from running. SQLite is
built into Python and works. Don't suggest DuckDB again, or turning off Smart App Control,
unless the user brings it up. Other packages that include their own compiled files may be blocked
in the same way, so test any new package straight after installing it.

Don't add other major tools or libraries without explaining why and getting the user's agreement first.

## About the data

- DGCA publishes monthly domestic traffic reports, usually as PDF or Excel files.
- These files often need cleaning: their layouts change from month to month, airline
  names vary, and they can contain merged cells and footnotes.
- Keep the original downloaded files unchanged. Do all cleaning in code so it can be repeated.
- Note the source and month of every file used.

## How to work with the user

The user is **non-technical** and is learning. Follow these rules:

1. **Use plain language.** Avoid jargon. When a technical term is unavoidable,
   explain it in simple words the first time it comes up.
2. **Work in small steps.** Do one thing at a time instead of many changes at once.
3. **Explain before acting.** Before each step, say what you're about to do and
   why, then do it. Afterwards, briefly say what happened.
4. **Check understanding.** At natural stopping points, offer to explain more or
   answer questions before moving on.
5. **Tell the user about any problem.** If something fails or doesn't work as
   expected, say so clearly and explain what it means in plain words.
6. **Teach as you go.** When it helps, mention a Claude Code feature or habit
   the user could use (for example, how to ask for a change or undo one).

## Current status

- The step-by-step plan is in `PLAN.md`. Do one step at a time, and only when the user says to.
- Step 1 (Python setup) is done: the virtual environment is in `.venv`, and the packages are listed in `requirements.txt`.
- Run Python through the toolbox: `.\.venv\Scripts\python.exe` (Windows).
- Step 2 (folders) is done: `data/raw/excel/`, `data/raw/pdf/`, `data/manual/`, `src/`.
- Step 3 (download Excel files) is done: `src/download.py` saves one file per airline per year,
  plus totals, to `data/raw/excel/`. Run it with `.\.venv\Scripts\python.exe src\download.py`.
- Each airline's Excel file stacks four tables (scheduled domestic, scheduled international,
  non-scheduled domestic, non-scheduled international), each with a title row. Use only
  "Scheduled Domestic Services". `src/clean.py` finds it by its title.
- Step 4 (monthly PDF reports) is partly done: only September 2025 of the 12 target months is
  downloaded so far (see PLAN.md). Some bonus 2025 reports are also saved.
- Step 5 (cleaning) is done: `src/clean.py` writes `data/clean/airline_monthly.csv`, with one row per
  airline per month (Sep 2025 – Aug 2026), plus market share. It checks that the airlines add up to DGCA's totals.
- Flybig stopped scheduled flights after October 2025, so it has only two months of data.
- Step 6 (on-time performance & cancellations) is partly done: `data/manual/otp_cancellations.csv`
  has September 2025 only. Airline names there match `airline_group` in the clean table.
  OTP is measured at six metro airports and given only for five airlines; cancellations cover all airlines.
- Reading chart numbers from the PDFs: the normal text layout jumbles them. Use
  `pdftotext -raw` and `pdftotext -table` (in the Bash terminal) and only accept numbers when both
  modes agree. Record the page number for every value.
- Step 7 (database) is done: `src/load.py` rebuilds `data/aviation.db` with tables `airline_monthly`
  and `otp_cancellations`. Join them on `month` and `airline_monthly.airline_group = otp_cancellations.airline`.
- To refresh everything, run in order: `src\download.py`, `src\clean.py`, `src\load.py`.
- On Windows PowerShell, inline `python -c "..."` commands with quotes inside break easily.
  Put check code in a temporary .py file instead.
- Step 8 (Git snapshot) is done. The data plan in PLAN.md is complete apart from the missing PDF months.
- The dashboard (first version) is done: `src/dashboard.py`. Open it with
  `.\.venv\Scripts\streamlit.exe run src\dashboard.py`, then go to http://localhost:8501.
- Dashboard design rules:
  - Each airline group has a fixed colour (`COLOURS` in `src/dashboard.py`; checked for colour blindness in light and dark mode).
  - Keep the same colour for the same airline on every chart.
  - Never use two y-axes on one chart.
  - Every chart's numbers also appear in the "See the data" tables.
- Test the dashboard without a browser using `streamlit.testing.v1.AppTest`. Charts sit inside
  columns, so search nested elements; chart elements have type `vega_lite_chart`.
- Next: add the missing PDF months (Steps 4 and 6 in PLAN.md) when the user downloads them. Add more PDF months to Step 6 whenever they're downloaded.

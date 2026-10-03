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
| **DuckDB** | A small, fast database stored as a single file on the computer | Stores the cleaned data and answers questions about it |
| **Streamlit** | A Python library that turns scripts into interactive web pages | Builds the dashboard the user will see and click through |

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

- Project just started. Only this CLAUDE.md file exists so far.
- No code has been written yet. Wait for the user to say when to start coding.

r"""
The India Aviation Operations Dashboard (Streamlit).

Reads the tables made by load.py from data/aviation.db and shows them as an interactive page.

How to open it (from the project folder):
    .venv\Scripts\streamlit.exe run src\dashboard.py
"""

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_FOLDER / "data" / "aviation.db"

# The airline groups shown as separate lines; the rest are grouped as "Others"
MAIN_AIRLINES = ["IndiGo", "Air India Group", "Akasa Air", "SpiceJet"]
SERIES = MAIN_AIRLINES + ["Others"]

# Fixed colours, so each airline looks the same on every chart. The four airline colours
# were checked for colour-blind safety in both modes; "Others" is a neutral grey.
COLOURS = {
    "light": {
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#898781"],
        "total": "#4a3aa7",  # purple: not used for any airline
        "text": "#52514e",
        "muted": "#898781",
    },
    "dark": {
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#898781"],
        "total": "#9085e9",
        "text": "#c3c2b7",
        "muted": "#898781",
    },
}


@st.cache_data
def load_data():
    """Read both tables from the database (kept in memory so the page stays fast)."""
    # closing() makes sure the database file is closed afterwards
    with closing(sqlite3.connect(DATABASE_FILE)) as database:
        airlines = pd.read_sql("SELECT * FROM airline_monthly", database)
        operations = pd.read_sql("SELECT * FROM otp_cancellations", database)
    return airlines, operations


def month_label(month):
    """'2026-08' -> 'Aug 2026'"""
    return datetime.strptime(month, "%Y-%m").strftime("%b %Y")


def short_month(month):
    """'2026-08' -> "Aug '26" (short enough for chart axes)"""
    return datetime.strptime(month, "%Y-%m").strftime("%b '%y")


def colours():
    """The colour set for the page's current light/dark mode."""
    return COLOURS["dark" if st.context.theme.type == "dark" else "light"]


def spread_labels(values, min_gap):
    """Nudge end-of-line label positions apart so they don't overlap (keeps their order)."""
    order = sorted(values, key=values.get)
    positions, previous = {}, None
    for name in order:
        y = values[name] if previous is None else max(values[name], previous + min_gap)
        positions[name] = previous = y
    return positions


def market_share_chart(shown, month_order):
    c = colours()
    share = shown.assign(
        series=shown["airline_group"].where(shown["airline_group"].isin(MAIN_AIRLINES), "Others")
    )
    share = share.groupby(["month", "series"], as_index=False)["market_share_pct"].sum()
    share["label"] = share["month"].map(short_month)

    # One row per month with every airline's share, for the hover tooltip
    wide = share.pivot(index="label", columns="series", values="market_share_pct").reset_index()

    # Line-end labels for the last month, nudged apart where lines end close together
    last = share[share["month"] == share["month"].max()].copy()
    positions = spread_labels(dict(zip(last["series"], last["market_share_pct"])), min_gap=3.5)
    last["label_y"] = last["series"].map(positions)
    last["end_text"] = last["series"] + " " + last["market_share_pct"].map("{:.1f}%".format)

    x = alt.X("label:O", sort=month_order, title=None, axis=alt.Axis(labelAngle=0))
    y = alt.Y("market_share_pct:Q", title="Market share (%)", scale=alt.Scale(domain=[0, 75]))
    colour = alt.Color(
        "series:N",
        scale=alt.Scale(domain=SERIES, range=c["series"]),
        legend=alt.Legend(title=None, orient="top"),
    )
    hover = alt.selection_point(fields=["label"], on="pointerover", nearest=True, empty=False)

    lines = alt.Chart(share).mark_line(strokeWidth=2).encode(x=x, y=y, color=colour)
    points = (
        alt.Chart(share)
        .mark_point(filled=True, size=70)
        .encode(x=x, y=y, color=colour, opacity=alt.condition(hover, alt.value(1), alt.value(0)))
    )
    end_labels = (
        alt.Chart(last)
        .mark_text(align="left", dx=8, fontSize=12)
        .encode(x=x, y=alt.Y("label_y:Q"), text="end_text:N", color=alt.value(c["text"]))
    )
    # An invisible full-height strip per month: hovering anywhere in it shows the tooltip
    hover_strips = (
        alt.Chart(wide)
        .mark_rect(opacity=0)
        .encode(
            x=x,
            tooltip=[alt.Tooltip("label:O", title="Month")]
            + [alt.Tooltip(field=s, type="quantitative", title=s, format=".1f")
               for s in SERIES if s in wide],
        )
        .add_params(hover)
    )
    crosshair = (
        alt.Chart(wide)
        .mark_rule(color=c["muted"], strokeWidth=1)
        .encode(x=x)
        .transform_filter(hover)
    )
    return (
        alt.layer(lines, crosshair, points, end_labels, hover_strips)
        .properties(height=380, padding={"left": 5, "top": 5, "bottom": 5, "right": 150})
    )


def passengers_chart(shown, month_order):
    c = colours()
    totals = shown.groupby("month", as_index=False)["passengers"].sum()
    totals["label"] = totals["month"].map(short_month)
    totals["millions"] = totals["passengers"] / 1e6

    return (
        alt.Chart(totals)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=c["total"])
        .encode(
            x=alt.X("label:O", sort=month_order, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("millions:Q", title="Passengers (millions)"),
            tooltip=[
                alt.Tooltip("label:O", title="Month"),
                alt.Tooltip("passengers:Q", title="Passengers", format=","),
            ],
        )
        .properties(height=380)
    )


def airline_bar_chart(rows, value_column, title, number_format):
    """Horizontal bars, one per airline, largest at the top, with the value at each bar's end."""
    c = colours()
    airline_colour = dict(zip(SERIES, c["series"]))
    rows = rows.assign(colour=rows["airline"].map(airline_colour).fillna(c["muted"]))
    y = alt.Y("airline:N", sort="-x", title=None)
    # Extra room past the longest bar so its number isn't cut off
    x = alt.X(f"{value_column}:Q", title=title,
              scale=alt.Scale(domain=[0, rows[value_column].max() * 1.18], nice=False))

    bars = (
        alt.Chart(rows)
        .mark_bar(cornerRadiusEnd=4, height={"band": 0.7})
        .encode(
            x=x,
            y=y,
            color=alt.Color("colour:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("airline:N", title="Airline"),
                alt.Tooltip(f"{value_column}:Q", title=title, format=number_format),
            ],
        )
    )
    values = (
        alt.Chart(rows)
        .mark_text(align="left", dx=4, fontSize=12)
        .encode(x=x, y=y, text=alt.Text(f"{value_column}:Q", format=number_format),
                color=alt.value(c["text"]))
    )
    return (bars + values).properties(height=32 * len(rows) + 20)


def month_summary(airlines, month):
    """The four headline numbers for one month."""
    rows = airlines[airlines["month"] == month]
    indigo = rows[rows["airline"] == "IndiGo"]
    return {
        "passengers": rows["passengers"].sum(),
        "indigo_share": indigo["market_share_pct"].sum(),
        # Load factor for all airlines together: passenger-km flown / seat-km available
        "load_factor": 100 * rows["passenger_km_thousand"].sum() / rows["seat_km_thousand"].sum(),
        "airlines_flying": int((rows["passengers"] > 0).sum()),
    }


st.set_page_config(page_title="India Aviation Dashboard", page_icon="✈️", layout="wide")

if not DATABASE_FILE.exists():
    st.error("The database is missing. Run src\\download.py, src\\clean.py and src\\load.py first.")
    st.stop()

airlines, operations = load_data()
all_months = sorted(airlines["month"].unique())

# --- Title and month filter ---
st.title("India Aviation Operations Dashboard")
st.caption(
    "Scheduled domestic flights by Indian airlines. "
    "Source: DGCA (Directorate General of Civil Aviation) monthly traffic data."
)

first_month, last_month = st.select_slider(
    "Months to show",
    options=all_months,
    value=(all_months[0], all_months[-1]),
    format_func=month_label,
)
months = [m for m in all_months if first_month <= m <= last_month]
shown = airlines[airlines["month"].isin(months)]

# --- Headline numbers for the last month in the range ---
latest = months[-1]
earlier = all_months[all_months.index(latest) - 1] if latest != all_months[0] else None
now = month_summary(airlines, latest)
before = month_summary(airlines, earlier) if earlier else None

st.subheader(f"{month_label(latest)} at a glance")
if before:
    st.caption(f"Changes are compared with {month_label(earlier)}.")

tile1, tile2, tile3, tile4 = st.columns(4)
tile1.metric(
    "Passengers",
    f"{now['passengers'] / 1e6:.2f} M",
    f"{100 * (now['passengers'] / before['passengers'] - 1):+.1f}%" if before else None,
    border=True,
)
tile2.metric(
    "IndiGo market share",
    f"{now['indigo_share']:.1f}%",
    f"{now['indigo_share'] - before['indigo_share']:+.1f} pts" if before else None,
    delta_color="off",
    border=True,
)
tile3.metric(
    "Load factor (how full planes were)",
    f"{now['load_factor']:.1f}%",
    f"{now['load_factor'] - before['load_factor']:+.1f} pts" if before else None,
    border=True,
)
tile4.metric(
    "Airlines flying",
    now["airlines_flying"],
    (now["airlines_flying"] - before["airlines_flying"]) or None if before else None,
    delta_color="off",
    border=True,
)

# --- Market share and passengers ---
month_order = [short_month(m) for m in months]
left, right = st.columns([3, 2])
with left:
    st.subheader("Market share over time")
    st.caption("Share of all domestic passengers. Smaller airlines are grouped as \"Others\".")
    st.altair_chart(market_share_chart(shown, month_order), width="stretch")
with right:
    st.subheader("Passengers per month")
    st.caption("Total passengers on scheduled domestic flights.")
    st.altair_chart(passengers_chart(shown, month_order), width="stretch")

# --- On-time performance and cancellations ---
st.subheader("On-time performance & cancellations")
ops_months = sorted(m for m in operations["month"].unique() if m in months)
if not ops_months:
    st.info(
        "On-time and cancellation figures aren't available for the months selected yet. "
        f"Months available so far: {', '.join(month_label(m) for m in sorted(operations['month'].unique()))}."
    )
else:
    ops_month = ops_months[-1]
    ops = operations[operations["month"] == ops_month]
    overall = ops.loc[ops["airline"] == "All airlines", "cancellation_rate_pct"]
    ops = ops[ops["airline"] != "All airlines"]

    available = sorted(operations["month"].unique())
    note = f"Showing **{month_label(ops_month)}**, the latest month in your selection with these figures."
    if len(available) < len(all_months):
        note += (
            f" So far, figures from DGCA's monthly reports cover {len(available)} of "
            f"{len(all_months)} months; more are coming."
        )
    st.info(note)

    left, right = st.columns(2)
    with left:
        st.markdown("**On-time performance (%)**")
        st.caption("Flights on time at the six big metro airports. DGCA reports this for five airlines.")
        st.altair_chart(
            airline_bar_chart(ops.dropna(subset=["otp_pct"]), "otp_pct", "On time (%)", ".1f"),
            width="stretch",
        )
    with right:
        st.markdown("**Cancellation rate (%)**")
        overall_text = f" Overall for all airlines: **{overall.iloc[0]:.2f}%**." if not overall.empty else ""
        st.caption(f"Share of planned flights that were cancelled.{overall_text}")
        st.altair_chart(
            airline_bar_chart(ops.dropna(subset=["cancellation_rate_pct"]), "cancellation_rate_pct",
                              "Cancelled (%)", ".2f"),
            width="stretch",
        )

# --- The numbers behind the charts ---
with st.expander("See the data"):
    tab1, tab2 = st.tabs(["Airlines by month", "On-time & cancellations"])
    with tab1:
        st.dataframe(
            shown,
            hide_index=True,
            column_config={
                "month": "Month",
                "airline": "Airline",
                "airline_group": "Airline group",
                "departures": st.column_config.NumberColumn("Flights", format="localized"),
                "hours": st.column_config.NumberColumn("Hours flown", format="localized"),
                "passengers": st.column_config.NumberColumn("Passengers", format="localized"),
                "passenger_km_thousand": st.column_config.NumberColumn(
                    "Passenger-km (thousand)", format="localized"),
                "seat_km_thousand": st.column_config.NumberColumn("Seat-km (thousand)", format="localized"),
                "load_factor_pct": st.column_config.NumberColumn("Load factor (%)", format="%.2f"),
                "market_share_pct": st.column_config.NumberColumn("Market share (%)", format="%.2f"),
            },
        )
    with tab2:
        st.dataframe(
            operations[operations["month"].isin(months)],
            hide_index=True,
            column_config={
                "month": "Month",
                "airline": "Airline",
                "otp_pct": st.column_config.NumberColumn("On time (%)", format="%.1f"),
                "cancellation_rate_pct": st.column_config.NumberColumn("Cancelled (%)", format="%.2f"),
                "source_file": "Source report",
                "otp_page": st.column_config.NumberColumn("On-time page", format="%d"),
                "cancellation_page": st.column_config.NumberColumn("Cancellation page", format="%d"),
            },
        )

st.caption(
    "Data: DGCA monthly domestic traffic statistics (Excel) and monthly Traffic Data reports (PDF). "
    "Figures are provisional, as published by DGCA."
)

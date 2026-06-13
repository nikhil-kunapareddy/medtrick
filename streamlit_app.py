"""
Aayu — Personal Health Dashboard (Streamlit)

Entry point: run with `streamlit run streamlit_app.py`.

Renders the banner KPIs, a global month filter (sidebar), and the sleep /
activity sections. All figure-building lives in core.charts; this file is the
thin Streamlit view layer.
"""

import pandas as pd
import streamlit as st

from core import charts
from core import data as d
from ui import components as ui
from ui import styles

st.set_page_config(page_title="Aayu · Health Dashboard", layout="wide")
styles.inject()


@st.cache_data
def _months() -> list:
    return charts.all_months()


# ── Sidebar: global month filter (replaces the Dash callback) ──────────────────
months = _months()
with st.sidebar:
    st.markdown("### Filter")
    month = st.selectbox(
        "Month",
        options=months,
        index=len(months) - 1 if months else 0,
        format_func=lambda m: pd.Period(m, freq="M").strftime("%b %Y"),
    ) if months else None


# ── Banner ─────────────────────────────────────────────────────────────────────
score = charts.sleep_score()
weight_lbs = round(d.latest_weight * 2.20462, 1) if d.latest_weight else None
ui.banner(
    "Aayu",
    [
        ("Sleep Score", score if score is not None else "—", "/100"),
        ("Avg Daily Steps", f"{d.avg_steps:,}", ""),
        ("Avg Sleep", d.avg_sleep_h, "hrs"),
        ("Resting HR", d.avg_resting_hr, "bpm"),
        ("Weight", weight_lbs if weight_lbs is not None else "—", "lbs"),
    ],
)


# ── Sleep section ────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    ui.chart_card("Sleep Breakdown", charts.sleep_breakdown(month))
with c2:
    ui.chart_card("Workout Sessions", charts.workouts())


# ── Activity section ───────────────────────────────────────────────────────────
if not d.body.empty:
    c3, c4 = st.columns(2)
    with c3:
        ui.chart_card("Calories Burned", charts.calories(month))
    with c4:
        ui.chart_card("Weight Trend", charts.weight(month))
else:
    ui.chart_card("Calories Burned", charts.calories(month))


ui.footer("Aayu · Personal Health Analytics · Zepp Data")

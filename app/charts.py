"""
Plotly figure builders.

Each function returns a go.Figure ready to be dropped into a dcc.Graph.
"""

import pandas as pd
import plotly.graph_objects as go

from app import data as d
from app.theme import C, AXIS, fade, plot_base


# Local timezone the UTC sleep timestamps are displayed in.
TZ = "America/New_York"


def sleep_months() -> list:
    """Year-months present in the sleep data, oldest → newest, as 'YYYY-MM' strings."""
    return [str(p) for p in sorted(d.sleep["date"].dt.to_period("M").unique())]


def all_months() -> list:
    """Union of year-months across sleep, activity and body data, oldest → newest."""
    return sorted(set(sleep_months()) | set(activity_months()) | set(body_months()))


def _clock(ts: pd.Series) -> pd.Series:
    """Fractional clock-hour on a night-centred axis: evenings go negative, mornings positive."""
    h = ts.dt.hour + ts.dt.minute / 60
    return h.where(h < 14, h - 24)


def _clock_label(v: float) -> str:
    hh = int(round(v)) % 24
    ampm = "AM" if hh < 12 else "PM"
    return f"{hh % 12 or 12} {ampm}"


# ── Sleep score ──────────────────────────────────────────────────────────────────
# Targets on the night-centred clock: 11:30 PM (-0.5) bed, 6:30 AM (6.5) wake.
_IDEAL_BED, _IDEAL_WAKE = -0.5, 6.5
_IDEAL_RATIOS = {"deep": 0.20, "rem": 0.22, "light": 0.53, "awake": 0.05}
_TARGET_SLEEP_H = 7.5


def _closeness(dev: float, full: float, zero: float) -> float:
    """1.0 when deviation ≤ `full` hours, fading linearly to 0.0 at `zero`."""
    if dev <= full:
        return 1.0
    if dev >= zero:
        return 0.0
    return 1 - (dev - full) / (zero - full)


def sleep_score(asof=None) -> int | None:
    """
    0–100 sleep score for the latest day, over the trailing 14 nights.

    Timing 30% · Stage ratios 35% · Duration 20% · Consistency 15%.
    """
    df = d.sleep.sort_values("date")
    if df.empty:
        return None
    last = asof if asof is not None else df["date"].max()
    win = df[(df["date"] > last - pd.Timedelta(days=14)) & (df["date"] <= last)]
    if win.empty:
        return None

    start = pd.to_datetime(win["start"], utc=True).dt.tz_convert(TZ)
    stop  = pd.to_datetime(win["stop"],  utc=True).dt.tz_convert(TZ)
    bed, wake = _clock(start), _clock(stop)

    # Timing (30%) — average bed/wake vs ideal
    timing = (_closeness(abs(bed.mean()  - _IDEAL_BED),  1 / 3, 2.0)
              + _closeness(abs(wake.mean() - _IDEAL_WAKE), 1 / 3, 2.0)) / 2

    # Consistency (15%) — tightness of the schedule
    consistency = (_closeness(bed.std(ddof=0),  1 / 3, 1.5)
                   + _closeness(wake.std(ddof=0), 1 / 3, 1.5)) / 2

    # Stage ratios (35%) — closeness to the magic ratio (awake only penalised when high)
    deep, rem, light, awake = (win["deepSleepTime"].sum(), win["REMTime"].sum(),
                               win["shallowSleepTime"].sum(), win["wakeTime"].sum())
    total = deep + rem + light + awake
    ratios = {"deep": deep / total, "rem": rem / total, "light": light / total, "awake": awake / total}

    def stage_pts(k: str) -> float:
        dev = ratios[k] - _IDEAL_RATIOS[k]
        if k == "awake":
            dev = max(0.0, dev)
        return max(0.0, 1 - abs(dev) / 0.15)

    stages = sum(stage_pts(k) for k in _IDEAL_RATIOS) / len(_IDEAL_RATIOS)

    # Duration (20%) — average time asleep vs target
    avg_asleep_h = (deep + rem + light) / 60 / len(win)
    duration = _closeness(abs(avg_asleep_h - _TARGET_SLEEP_H), 0.5, 3.0)

    score = 100 * (0.30 * timing + 0.15 * consistency + 0.35 * stages + 0.20 * duration)
    return round(score)


# Colour per sleep stage, shared by the breakdown bars and the composition donut.
STAGE_COLORS = {
    "Deep":  C["purple"],   # purple
    "REM":   C["cyan"],     # cyan
    "Light": C["amber"],    # yellow
    "Awake": C["pink"],     # coral
}


def sleep_breakdown(month: str | None = None) -> go.Figure:
    """One bar per night spanning sleep → wake time, split into stage-coloured segments."""
    df = d.sleep.sort_values("date").copy()
    months = sleep_months()
    month = month or (months[-1] if months else None)
    if month:
        df = df[df["date"].dt.to_period("M") == pd.Period(month, freq="M")]

    start = pd.to_datetime(df["start"], utc=True).dt.tz_convert(TZ)
    stop  = pd.to_datetime(df["stop"],  utc=True).dt.tz_convert(TZ)
    bed, wake = _clock(start), _clock(stop)

    stages = [
        ("Deep",  df["deepSleepTime"]),
        ("REM",   df["REMTime"]),
        ("Light", df["shallowSleepTime"]),
        ("Awake", df["wakeTime"]),
    ]
    fig = go.Figure()
    base = bed.copy()
    for name, mins in stages:
        hrs = mins / 60
        fig.add_trace(go.Bar(
            x=df["date"], base=base, y=hrs, name=name,
            marker_color=STAGE_COLORS[name],
            customdata=mins,
            hovertemplate=f"{name}: " + "%{customdata:.0f} min<extra></extra>",
        ))
        base = base + hrs

    if not bed.empty:
        lo, hi = float(bed.min()), float(wake.max())
        ticks = list(range(int(lo // 2 * 2), int(hi // 2 * 2) + 3, 2))
        fig.update_yaxes(tickvals=ticks, ticktext=[_clock_label(t) for t in ticks])

    fig.update_layout(
        **plot_base(
            title=dict(text="Sleep stages by night (local time)", font=dict(size=12, color=C["sub"])),
            barmode="overlay",
        ),
        bargap=0.72,
        xaxis={**AXIS, "showgrid": False},
        yaxis={**AXIS, "side": "right"},
    )
    return fig


def sleep_donut() -> go.Figure:
    """Donut showing average nightly sleep stage composition."""
    avg_deep  = d.sleep["deepSleepTime"].mean()
    avg_rem   = d.sleep["REMTime"].mean()
    avg_light = d.sleep["shallowSleepTime"].mean()
    avg_wake  = d.sleep["wakeTime"].mean()
    total_h   = round((avg_deep + avg_rem + avg_light) / 60, 1)

    fig = go.Figure(go.Pie(
        labels=["Deep", "REM", "Light", "Awake"],
        values=[avg_deep, avg_rem, avg_light, avg_wake],
        hole=0.68,
        marker=dict(colors=[STAGE_COLORS["Deep"], STAGE_COLORS["REM"], STAGE_COLORS["Light"], STAGE_COLORS["Awake"]], line=dict(color=C["bg"], width=3)),
        textfont=dict(color=C["bg"], size=11),
        hovertemplate="%{label}: %{value:.0f} min (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        **plot_base(
            title=dict(text="Avg Sleep Composition", font=dict(size=12, color=C["sub"])),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["sub"], size=10),
                        orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            margin=dict(l=10, r=90, t=36, b=10),
            annotations=[dict(
                text=f"<b>{total_h}h</b><br><span style='font-size:10px'>avg</span>",
                x=0.5, y=0.5,
                font=dict(size=22, color=C["text"], family="Inter"),
                showarrow=False, align="center",
            )],
        )
    )
    return fig


def sleep_stage_hr() -> go.Figure:
    """Average heart rate recorded during each sleep stage."""
    df = d.sleep_min[d.sleep_min["hr"].notna() & (d.sleep_min["hr"] > 0)]
    stage_hr = df.groupby("stage")["hr"].mean().reset_index().round(1)
    color_map = {"LIGHT": C["surface2"], "DEEP": C["violet"], "REM": C["lime"], "WAKE": C["orange"]}
    colors = [color_map.get(s, C["sub"]) for s in stage_hr["stage"]]
    fig = go.Figure(go.Bar(
        x=stage_hr["stage"], y=stage_hr["hr"],
        marker_color=colors,
        text=stage_hr["hr"].apply(lambda v: f"{v:.0f} bpm"),
        textposition="outside",
        textfont=dict(color=C["text"], size=12),
        hovertemplate="%{x}: %{y:.0f} bpm<extra></extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Avg HR per Sleep Stage", font=dict(size=12, color=C["sub"])), showlegend=False),
        bargap=0.45,
        xaxis=dict(tickfont=dict(color=C["sub"], size=12), linecolor="rgba(0,0,0,0)", zeroline=False, showgrid=False),
        yaxis=AXIS,
    )
    return fig


def steps() -> go.Figure:
    """Daily step count bars with 7-day rolling average and 10K goal line."""
    df = d.activity.sort_values("date").copy()
    df["roll7"] = df["steps"].rolling(7, min_periods=1).mean().round(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"], y=df["steps"], name="Steps",
        marker_color=C["lime"], marker_opacity=0.85,
        hovertemplate="%{x|%b %d}: %{y:,}<extra>Steps</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        line=dict(color=C["amber"], width=2.5, shape="spline"),
        hovertemplate="%{y:,.0f}<extra>7d avg</extra>",
    ))
    fig.add_hline(y=10000, line_dash="dot", line_color=C["muted"],
                  annotation_text="10K goal", annotation_font_color=C["sub"],
                  annotation_position="top right")
    fig.update_layout(
        **plot_base(title=dict(text="Daily Steps", font=dict(size=12, color=C["sub"]))),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig


def distance() -> go.Figure:
    """Daily distance (km) with 7-day rolling average."""
    df = d.activity.sort_values("date").copy()
    df["roll7"] = df["distanceKm"].rolling(7, min_periods=1).mean().round(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["distanceKm"], name="Distance",
        fill="tozeroy", fillgradient=fade(C["lime"]),
        line=dict(color=C["lime"], width=2, shape="spline"),
        hovertemplate="%{x|%b %d}: %{y:.2f} km<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        line=dict(color=C["violet"], width=2, dash="dash"),
        hovertemplate="%{y:.2f} km<extra>7d avg</extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Daily Distance (km)", font=dict(size=12, color=C["sub"]))),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig


def hr_trend() -> go.Figure:
    """Daily average and resting heart rate over time."""
    df = d.daily_hr.sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["avg"].round(0), name="Avg HR",
        fill="tozeroy", fillgradient=fade(C["cyan"], top=0.30),
        line=dict(color=C["cyan"], width=2, shape="spline"),
        hovertemplate="%{x|%b %d}: %{y:.0f} bpm<extra>Avg HR</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["resting"].round(0), name="Resting HR",
        line=dict(color=C["pink"], width=2, dash="dash"),
        hovertemplate="%{x|%b %d}: %{y:.0f} bpm<extra>Resting HR</extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Heart Rate Trend", font=dict(size=12, color=C["sub"]))),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig


def hr_24h() -> go.Figure:
    """Average heart rate by hour of day across all recorded days."""
    df = d.hourly_hr
    fig = go.Figure(go.Scatter(
        x=df["hour"], y=df["heartRate"], mode="lines",
        fill="tozeroy", fillgradient=fade(C["violet"]),
        line=dict(color=C["violet"], width=2.5, shape="spline"),
        hovertemplate="%{x}:00 — %{y:.0f} bpm<extra></extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Avg HR by Hour of Day", font=dict(size=12, color=C["sub"])), showlegend=False),
        xaxis=dict(
            gridcolor=C["grid"], showgrid=True, zeroline=False,
            tickvals=list(range(0, 24, 3)),
            ticktext=["12am", "3am", "6am", "9am", "12pm", "3pm", "6pm", "9pm"],
            tickfont=dict(color=C["sub"], size=10), linecolor="rgba(0,0,0,0)",
        ),
        yaxis=AXIS,
    )
    return fig


def workouts() -> go.Figure:
    """Grouped weekly session counts for the last 8 weeks: two-tone Strength + solid Running."""
    sp = d.sport.copy()
    sp["week"] = sp["date"].dt.to_period("W")
    weeks = []
    if sp["week"].notna().any():
        last = sp["week"].max()
        weeks = [last - i for i in range(7, -1, -1)]          # last 8 weeks, oldest → current
    labels = [w.start_time.strftime("%b %d") for w in weeks]

    def counts_for(name):
        return [int(((sp["week"] == w) & (sp["sportName"] == name)).sum()) for w in weeks]

    LIFT = 0.05   # float bars just off the axis so all four corners round
    series = [("Strength", C["purple"]), ("Running", C["amber"])]
    fig = go.Figure()
    for name, color in series:
        counts = counts_for(name)
        fig.add_trace(go.Bar(
            x=labels,
            base=[LIFT if c else 0 for c in counts],
            y=[c - LIFT if c else 0 for c in counts],
            name=name, customdata=counts,
            marker=dict(color=color, cornerradius="40%"),
            hovertemplate="Wk of %{x} · " + name + ": %{customdata}<extra></extra>",
        ))

    fig.update_layout(
        **plot_base(title=dict(text="Sessions per week — last 8 weeks", font=dict(size=12, color=C["sub"])), barmode="group"),
        bargap=0.45, bargroupgap=0.18,
        xaxis=dict(tickfont=dict(color=C["sub"], size=11), linecolor="rgba(0,0,0,0)", zeroline=False, showgrid=False),
        yaxis={**AXIS, "dtick": 1},
    )
    return fig


def activity_months() -> list:
    """Year-months present in the activity data, oldest → newest, as 'YYYY-MM' strings."""
    return [str(p) for p in sorted(d.activity["date"].dt.to_period("M").unique())]


def calories(month: str | None = None) -> go.Figure:
    """Daily activity calories with a 7-day average drawn as a marker-dotted line, one month at a time."""
    df = d.activity.sort_values("date").copy()
    df["roll7"] = df["calories"].rolling(7, min_periods=1).mean().round(0)   # rolled on full series for context
    months = activity_months()
    month = month or (months[-1] if months else None)
    if month:
        df = df[df["date"].dt.to_period("M") == pd.Period(month, freq="M")]
    pts = df.iloc[:: max(1, len(df) // 14)]   # spaced points for the glow markers

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["calories"], name="Calories",
        line=dict(color=C["green"], width=1), opacity=0.3,
        hovertemplate="%{x|%b %d}: %{y} kcal<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        line=dict(color=C["green"], width=3, shape="linear"),
        hovertemplate="%{y:.0f} kcal<extra>7d avg</extra>",
    ))
    # Soft halo behind each marker, then the marker itself.
    fig.add_trace(go.Scatter(
        x=pts["date"], y=pts["roll7"], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(size=22, color=C["green"], opacity=0.16),
    ))
    fig.add_trace(go.Scatter(
        x=pts["date"], y=pts["roll7"], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(size=8, color=C["green"], line=dict(color=C["bg"], width=1.5)),
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Daily Calories Burned", font=dict(size=12, color=C["sub"]))),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig


def body_months() -> list:
    """Year-months present in the body/weight data, oldest → newest, as 'YYYY-MM' strings."""
    return [str(p) for p in sorted(d.body["date"].dt.to_period("M").unique())]


def weight(month: str | None = None) -> go.Figure:
    """Weight trend (lbs) as a marker-dotted line, one month at a time."""
    df = d.body.sort_values("date").copy()
    df["lbs"] = (df["weight"] * 2.20462).round(1)
    months = body_months()
    month = month or (months[-1] if months else None)
    if month:
        df = df[df["date"].dt.to_period("M") == pd.Period(month, freq="M")]
    pts = df.iloc[:: max(1, len(df) // 14)]   # spaced points for the glow markers

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lbs"], name="Weight",
        line=dict(color=C["amber"], width=3, shape="linear"),
        hovertemplate="%{x|%b %d}: %{y} lbs<extra>Weight</extra>",
    ))
    # Soft halo behind each marker, then the marker itself.
    fig.add_trace(go.Scatter(
        x=pts["date"], y=pts["lbs"], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(size=22, color=C["amber"], opacity=0.16),
    ))
    fig.add_trace(go.Scatter(
        x=pts["date"], y=pts["lbs"], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(size=8, color=C["amber"], line=dict(color=C["bg"], width=1.5)),
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Weight (lbs)", font=dict(size=12, color=C["sub"])), showlegend=False),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig

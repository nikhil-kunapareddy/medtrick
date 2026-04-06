"""
Plotly figure builders.

Each function returns a go.Figure ready to be dropped into a dcc.Graph.
"""

import plotly.graph_objects as go

from app import data as d
from app.theme import C, AXIS, plot_base


def sleep_trend() -> go.Figure:
    """Stacked bar: nightly Deep / REM / Light sleep with 8hr target line."""
    df = d.sleep.sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["date"], y=df["deepSleepTime"],    name="Deep",  marker_color=C["purple"], hovertemplate="%{y}m<extra>Deep</extra>"))
    fig.add_trace(go.Bar(x=df["date"], y=df["REMTime"],          name="REM",   marker_color=C["cyan"],   hovertemplate="%{y}m<extra>REM</extra>"))
    fig.add_trace(go.Bar(x=df["date"], y=df["shallowSleepTime"], name="Light", marker_color=C["muted"],  hovertemplate="%{y}m<extra>Light</extra>"))
    fig.add_hline(
        y=480, line_dash="dot", line_color=C["sub"],
        annotation_text="8hr target", annotation_font_color=C["sub"],
        annotation_position="top right",
    )
    fig.update_layout(
        **plot_base(barmode="stack", title=dict(text="Sleep Breakdown (min)", font=dict(size=12, color=C["sub"]))),
        bargap=0.25,
        xaxis=AXIS, yaxis=AXIS,
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
        marker=dict(colors=[C["purple"], C["cyan"], C["muted"], C["border"]], line=dict(color=C["bg"], width=3)),
        textfont=dict(color=C["text"], size=11),
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
    color_map = {"LIGHT": C["muted"], "DEEP": C["purple"], "REM": C["cyan"]}
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
        xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["sub"], size=12),
                   linecolor=C["border"], zeroline=False, showgrid=False),
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
        marker_color=C["green"], marker_opacity=0.65,
        hovertemplate="%{x|%b %d}: %{y:,}<extra>Steps</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        line=dict(color=C["amber"], width=2.5),
        hovertemplate="%{y:,.0f}<extra>7d avg</extra>",
    ))
    fig.add_hline(y=10000, line_dash="dot", line_color=C["sub"],
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
        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
        line=dict(color=C["green"], width=1.5), opacity=0.7,
        hovertemplate="%{x|%b %d}: %{y:.2f} km<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        line=dict(color=C["amber"], width=2, dash="dash"),
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
        fill="tozeroy", fillcolor="rgba(34,211,238,0.08)",
        line=dict(color=C["cyan"], width=2),
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
        fill="tozeroy", fillcolor="rgba(129,140,248,0.12)",
        line=dict(color=C["purple"], width=2.5),
        hovertemplate="%{x}:00 — %{y:.0f} bpm<extra></extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Avg HR by Hour of Day", font=dict(size=12, color=C["sub"])), showlegend=False),
        xaxis=dict(
            gridcolor=C["grid"], showgrid=True, zeroline=False,
            tickvals=list(range(0, 24, 3)),
            ticktext=["12am", "3am", "6am", "9am", "12pm", "3pm", "6pm", "9pm"],
            tickfont=dict(color=C["sub"], size=10), linecolor=C["border"],
        ),
        yaxis=AXIS,
    )
    return fig


def workouts() -> go.Figure:
    """Session count per workout type."""
    summary = (
        d.sport.groupby("sportName")
        .agg(sessions=("durationMin", "count"), total_min=("durationMin", "sum"))
        .reset_index()
        .sort_values("sessions", ascending=False)
    )
    color_map = {
        "Running": C["green"], "Strength": C["purple"],
        "Outdoor Walk": C["cyan"], "Indoor Walk": C["amber"], "Other": C["muted"],
    }
    colors = [color_map.get(s, C["muted"]) for s in summary["sportName"]]
    fig = go.Figure(go.Bar(
        x=summary["sportName"], y=summary["sessions"],
        marker_color=colors,
        text=summary["sessions"],
        textposition="outside",
        textfont=dict(color=C["text"], size=12),
        customdata=summary[["total_min"]].values,
        hovertemplate="%{x}<br>%{y} sessions · %{customdata[0]:.0f} min total<extra></extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Workout Sessions by Type", font=dict(size=12, color=C["sub"])), showlegend=False),
        xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["sub"], size=11),
                   linecolor=C["border"], zeroline=False, showgrid=False),
        yaxis=AXIS,
    )
    return fig


def calories() -> go.Figure:
    """Daily activity calories with 7-day rolling average."""
    df = d.activity.sort_values("date").copy()
    df["roll7"] = df["calories"].rolling(7, min_periods=1).mean().round(0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["calories"], name="Calories",
        line=dict(color=C["pink"], width=1), opacity=0.4,
        hovertemplate="%{x|%b %d}: %{y} kcal<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["roll7"], name="7-day avg",
        fill="tozeroy", fillcolor="rgba(244,114,182,0.10)",
        line=dict(color=C["pink"], width=2.5),
        hovertemplate="%{y:.0f} kcal<extra>7d avg</extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Daily Calories Burned", font=dict(size=12, color=C["sub"]))),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig


def weight() -> go.Figure:
    """Weight trend over recorded measurements."""
    df = d.body.sort_values("date")
    fig = go.Figure(go.Scatter(
        x=df["date"], y=df["weight"],
        mode="lines+markers",
        line=dict(color=C["amber"], width=2),
        marker=dict(size=7, color=C["amber"], line=dict(color=C["bg"], width=2)),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
        hovertemplate="%{x|%b %d}: %{y} kg<extra>Weight</extra>",
    ))
    fig.update_layout(
        **plot_base(title=dict(text="Weight (kg)", font=dict(size=12, color=C["sub"])), showlegend=False),
        xaxis=AXIS, yaxis=AXIS,
    )
    return fig

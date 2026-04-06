"""
Dash layout and UI component helpers.

Assembles the full page from reusable card/KPI primitives and chart figures.
"""

from dash import dcc, html

from app import charts
from app import data as d
from app.theme import C


# ── UI Primitives ──────────────────────────────────────────────────────────────

def kpi(label: str, value, unit: str = "", color: str = C["purple"], sub: str = "") -> html.Div:
    return html.Div([
        html.Div(label, className="section-label", style={"marginBottom": "10px"}),
        html.Div([
            html.Span(str(value), className="kpi-value", style={"--kpi-color": color}),
            html.Span(f" {unit}", style={"fontSize": "13px", "color": C["sub"], "marginLeft": "3px"}) if unit else None,
        ], style={"display": "flex", "alignItems": "baseline"}),
        html.Div(sub, style={"fontSize": "10px", "color": C["muted"], "marginTop": "6px"}) if sub else None,
    ], className="kpi-card dash-card", style={
        "background": C["surface"],
        "borderRadius": "16px",
        "padding": "22px 24px",
        "flex": "1",
        "minWidth": "150px",
    })


def card(children, flex: int = 1, min_width: str = "0") -> html.Div:
    return html.Div(children, className="dash-card", style={
        "background": C["surface"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "16px",
        "padding": "20px",
        "flex": str(flex),
        "minWidth": min_width,
        "overflow": "hidden",
    })


def section_title(text: str) -> html.Div:
    return html.Div(text, style={
        "fontSize": "14px", "fontWeight": "600", "color": C["text"],
        "marginBottom": "4px", "letterSpacing": "-0.01em",
    })


def graph(fig, height: int = 280) -> dcc.Graph:
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": f"{height}px"})


def row(children, mb: str = "20px") -> html.Div:
    return html.Div(children, style={"display": "flex", "gap": "16px", "marginBottom": mb, "flexWrap": "wrap"})


# ── Sections ───────────────────────────────────────────────────────────────────

def _header() -> html.Div:
    return html.Div([
        html.Div([
            html.Div([
                html.Span("Med", style={
                    "fontSize": "22px", "fontWeight": "800",
                    "background": f"linear-gradient(135deg, {C['purple']}, {C['cyan']})",
                    "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
                    "backgroundClip": "text",
                }),
                html.Span("Trick", style={"fontSize": "22px", "fontWeight": "800", "color": C["text"]}),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(
                f"Personal Health · {d.date_start} – {d.date_end}",
                style={"fontSize": "12px", "color": C["sub"], "marginTop": "3px"},
            ),
        ]),
        html.Div([
            html.Span(className="pulse-dot", style={"marginRight": "8px"}),
            html.Span(f"Hey, {d.user_name}", style={"fontSize": "13px", "color": C["sub"]}),
        ], style={
            "background": C["surface2"], "border": f"1px solid {C['border']}",
            "padding": "8px 18px", "borderRadius": "24px",
            "display": "flex", "alignItems": "center",
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "marginBottom": "24px", "padding": "18px 24px",
        "background": C["surface"], "border": f"1px solid {C['border']}",
        "borderRadius": "16px",
    })


def _kpi_row() -> html.Div:
    cards = [
        kpi("Avg Daily Steps", f"{d.avg_steps:,}",     color=C["green"],  sub=f"Best: {d.best_steps:,} · {d.active_days} days ≥8K"),
        kpi("Avg Sleep",       d.avg_sleep_h, "hrs",   color=C["purple"], sub=f"Deep {d.avg_deep_min}m · REM {d.avg_rem_min}m"),
        kpi("Resting HR",      d.avg_resting_hr, "bpm",color=C["cyan"],   sub=f"Peak avg: {d.avg_peak_hr} bpm"),
        kpi("Workouts",        d.total_workouts, "sessions", color=C["pink"],  sub=f"Running: {d.total_run_km} km total"),
        kpi("Avg Calories",    d.avg_calories, "kcal", color=C["amber"],  sub="Daily activity burn"),
    ]
    if d.latest_weight:
        cards.append(kpi("Weight", d.latest_weight, "kg", C["purple"], sub=f"BMI {d.latest_bmi}"))
    return row(cards)


def _sleep_section() -> list:
    return [
        row([
            card([section_title("Sleep Breakdown"),   graph(charts.sleep_trend(), 290)], flex=2),
            card([section_title("Sleep Composition"), graph(charts.sleep_donut(), 290)], flex=1, min_width="260px"),
        ]),
        row([
            card([section_title("HR During Sleep Stages"), graph(charts.sleep_stage_hr(), 260)], flex=1),
            card([section_title("Daily Steps"),            graph(charts.steps(),          260)], flex=2),
        ]),
    ]


def _hr_section() -> list:
    return [
        row([
            card([section_title("Heart Rate Trend"),   graph(charts.hr_trend(), 260)], flex=2),
            card([section_title("HR Pattern — 24hr"), graph(charts.hr_24h(),   260)], flex=1, min_width="280px"),
        ]),
    ]


def _activity_section() -> list:
    return [
        row([
            card([section_title("Distance Covered"),  graph(charts.distance(), 250)], flex=1),
            card([section_title("Calories Burned"),   graph(charts.calories(), 250)], flex=1),
        ]),
    ]


def _sports_section() -> list:
    body_card = [card([section_title("Weight Trend"), graph(charts.weight(), 260)], flex=1)] if not d.body.empty else []
    return [
        row([card([section_title("Workout Sessions"), graph(charts.workouts(), 260)], flex=1)] + body_card),
    ]


# ── Full Page Layout ───────────────────────────────────────────────────────────

def build() -> html.Div:
    return html.Div(
        [
            _header(),
            _kpi_row(),
            *_sleep_section(),
            *_hr_section(),
            *_activity_section(),
            *_sports_section(),
            html.Div(
                "MedTrick · Personal Health Analytics · Zepp Data",
                style={"textAlign": "center", "color": C["muted"], "fontSize": "11px", "padding": "16px 0 8px"},
            ),
        ],
        style={
            "background": C["bg"],
            "minHeight": "100vh",
            "padding": "24px 28px",
            "fontFamily": "Inter, ui-sans-serif, system-ui, sans-serif",
            "color": C["text"],
            "maxWidth": "1400px",
            "margin": "0 auto",
        },
    )

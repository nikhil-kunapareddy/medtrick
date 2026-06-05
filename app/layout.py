"""
Dash layout and UI component helpers.

Assembles the full page from reusable card/KPI primitives and chart figures.
"""

import pandas as pd
from dash import Input, Output, callback, dcc, html

from app import charts
from app import data as d
from app.theme import C


# ── UI Primitives ──────────────────────────────────────────────────────────────

def banner_stat(label: str, value, unit: str = "") -> html.Div:
    return html.Div([
        html.Div(label, style={"fontSize": "14px", "color": C["sub"], "fontWeight": "500", "marginBottom": "8px"}),
        html.Div([
            html.Span(str(value), style={"fontSize": "32px", "fontWeight": "600", "color": C["text"], "letterSpacing": "-0.02em"}),
            html.Span(f" {unit}", style={"fontSize": "15px", "color": C["sub"], "marginLeft": "2px"}) if unit else None,
        ], style={"display": "flex", "alignItems": "baseline"}),
    ])


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

def _banner() -> html.Div:
    weight_lbs = round(d.latest_weight * 2.20462, 1) if d.latest_weight else None
    score = charts.sleep_score()
    stats = html.Div([
        banner_stat("Sleep Score",     score if score is not None else "—", "/100"),
        banner_stat("Avg Daily Steps", f"{d.avg_steps:,}"),
        banner_stat("Avg Sleep",       d.avg_sleep_h, "hrs"),
        banner_stat("Resting HR",      d.avg_resting_hr, "bpm"),
        banner_stat("Weight",          weight_lbs if weight_lbs is not None else "—", "lbs"),
    ], style={"display": "flex", "gap": "44px", "alignItems": "flex-start", "flexWrap": "wrap"})
    months = charts.all_months()
    left = html.Div([
        html.Div("Aayu", style={
            "fontSize": "40px", "fontWeight": "800", "color": C["text"], "letterSpacing": "-0.02em",
        }),
        html.Div(
            dcc.Dropdown(
                id="global-month",
                options=[{"label": pd.Period(m, freq="M").strftime("%b %Y"), "value": m} for m in months],
                value=months[-1] if months else None,
                clearable=False,
                searchable=False,
                className="month-dropdown",
            ),
            style={"width": "150px"},
        ),
    ], style={"display": "flex", "alignItems": "center", "gap": "20px", "flexWrap": "wrap"})
    return html.Div([
        left,
        stats,
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "gap": "32px", "flexWrap": "wrap",
        "marginBottom": "24px", "padding": "26px 36px",
        "background": C["surface"], "border": f"1px solid {C['border']}",
        "borderRadius": "18px",
    })


def _graph_card(title: str, graph_id: str, height: int, flex: int, min_width: str = "0") -> html.Div:
    g = dcc.Graph(id=graph_id, config={"displayModeBar": False}, style={"height": f"{height}px"})
    return card([section_title(title), g], flex=flex, min_width=min_width)


@callback(
    Output("sleep-breakdown", "figure"),
    Output("calories-graph", "figure"),
    Output("weight-graph", "figure"),
    Input("global-month", "value"),
)
def _update_monthly_charts(month):
    return charts.sleep_breakdown(month), charts.calories(month), charts.weight(month)


def _sleep_section() -> list:
    return [
        row([
            _graph_card("Sleep Breakdown", "sleep-breakdown", 280, flex=1),
            card([section_title("Workout Sessions"), graph(charts.workouts(), 280)], flex=1),
        ]),
    ]


def _activity_section() -> list:
    cards = [_graph_card("Calories Burned", "calories-graph", 280, flex=1)]
    if not d.body.empty:
        cards.append(_graph_card("Weight Trend", "weight-graph", 280, flex=1))
    return [row(cards)]


# ── Full Page Layout ───────────────────────────────────────────────────────────

def build() -> html.Div:
    return html.Div(
        [
            _banner(),
            *_sleep_section(),
            *_activity_section(),
            html.Div(
                "Aayu · Personal Health Analytics · Zepp Data",
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

"""
Design tokens — colors, typography, and Plotly layout defaults.
"""

# Palette
C = dict(
    bg       = "#080C18",
    surface  = "#0F1525",
    surface2 = "#141E30",
    border   = "#1E2A3A",
    purple   = "#818CF8",
    cyan     = "#22D3EE",
    green    = "#10B981",
    pink     = "#F472B6",
    amber    = "#F59E0B",
    red      = "#EF4444",
    text     = "#F1F5F9",
    sub      = "#94A3B8",
    muted    = "#475569",
    grid     = "#1A2438",
)

# Shared axis style
AXIS = dict(
    gridcolor=C["grid"],
    showgrid=True,
    zeroline=False,
    tickfont=dict(color=C["sub"], size=10),
    linecolor=C["border"],
)


def plot_base(**overrides) -> dict:
    """Return a base Plotly layout dict, optionally merged with overrides."""
    cfg = dict(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font          = dict(color=C["text"], family="Inter, sans-serif", size=11),
        margin        = dict(l=16, r=16, t=36, b=16),
        hovermode     = "x unified",
        hoverlabel    = dict(
            bgcolor     = C["surface2"],
            font_color  = C["text"],
            bordercolor = C["border"],
        ),
        legend = dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=C["sub"], size=10),
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="right",  x=1,
        ),
    )
    cfg.update(overrides)
    return cfg

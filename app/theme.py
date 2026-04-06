"""
Design tokens — colors, typography, and Plotly layout defaults.
"""

# Palette — inspired by iOS Health widget dark theme
C = dict(
    bg       = "#0C0C0E",   # near-black (warmer than navy)
    surface  = "#1C1C1E",   # iOS dark card
    surface2 = "#2C2C2E",   # elevated surface
    border   = "#3A3A3C",   # subtle separator
    purple   = "#BF5AF2",   # iOS violet
    cyan     = "#0A84FF",   # iOS blue
    green    = "#30D158",   # iOS green (dominant accent)
    pink     = "#FF375F",   # iOS pink-red
    amber    = "#FFD60A",   # iOS yellow
    red      = "#FF453A",   # iOS red
    text     = "#FFFFFF",   # primary text
    sub      = "#AEAEB2",   # secondary text
    muted    = "#636366",   # muted / disabled
    grid     = "#2C2C2E",   # chart gridlines
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

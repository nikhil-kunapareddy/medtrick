"""
Aayu — Personal Health Dashboard
Entry point: initialises the Dash app, wires up the layout, and starts the server.
"""

import dash

from app.layout import build

app = dash.Dash(
    __name__,
    title="Aayu · Health Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = build()

if __name__ == "__main__":
    app.run(debug=False, port=8050)

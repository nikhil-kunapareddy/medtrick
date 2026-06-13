# Aayu — Personal Health Dashboard

An interactive dark-themed dashboard for visualising wearable health data exported from the **Zepp** app (Amazfit devices).

Built with [Streamlit](https://streamlit.io/) + [Plotly](https://plotly.com/python/).

---

## Dashboard Sections

| Section | Charts |
|---|---|
| **KPIs** | Steps, Sleep, Resting HR, Workouts, Calories, Weight |
| **Sleep** | Nightly breakdown (Deep/REM/Light), avg composition donut, HR per sleep stage |
| **Heart Rate** | Daily avg + resting HR trend, avg HR by hour of day |
| **Activity** | Daily distance, calories burned trend |
| **Sports** | Workout sessions by type, weight trend |

---

## Setup

**1. Clone the repo**
```bash
git clone <repo-url>
cd aayu
```

**2. Create a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your data**

Export your health data from the Zepp app and place the folders under `data/`:

```
data/
├── ACTIVITY/
├── ACTIVITY_MINUTE/
├── ACTIVITY_STAGE/
├── BODY/
├── HEARTRATE_AUTO/
├── SLEEP/
├── SLEEP_MINUTE/
├── SPORT/
└── USER/
```

Each folder should contain a single `.csv` file as exported by Zepp.

**5. Run**
```bash
streamlit run streamlit_app.py
```

Streamlit opens [http://localhost:8501](http://localhost:8501) in your browser automatically.

---

## Project Structure

```
aayu/
├── streamlit_app.py    # Entry point — the Streamlit view (run this)
├── core/               # Framework-agnostic logic
│   ├── theme.py        # Design tokens: colours, Plotly layout defaults
│   ├── data.py         # CSV loading, data processing, KPI computations
│   └── charts.py       # Plotly figure builders (one function per chart)
├── ui/                 # Streamlit view primitives
│   ├── styles.py       # Injected CSS for the custom dark theme
│   └── components.py   # Banner / card / footer helpers
├── .streamlit/
│   └── config.toml     # Base dark theme config
├── requirements.txt
└── .gitignore
```

---

## Data Privacy

The `data/` folder is listed in `.gitignore` and will never be committed. Your personal health data stays local.

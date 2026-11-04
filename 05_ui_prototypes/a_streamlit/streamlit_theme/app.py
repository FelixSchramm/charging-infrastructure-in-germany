"""Overview page prototype: Streamlit with a custom theme (issue #33).

Run from this folder:
``uv run --no-project --with-requirements requirements.txt streamlit run app.py``
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[2] / "_shared" / "data"
ALL_STATES = "Alle Bundesländer"
DARK_BLUE = "#003247"
# Stacking order bottom to top follows the dict order.
CATEGORIES = {
    "hpc": ("HPC-Laden (>= 150 kW)", "#00B092"),
    "schnell": ("Schnellladen (> 22 kW)", DARK_BLUE),
    "normal": ("Normalladen (<= 22 kW)", "#D3D3D3"),
}

pio.templates["now"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, sans-serif", color=DARK_BLUE, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, linecolor="#C5D0D5", automargin=True),
        yaxis=dict(gridcolor="#E1E7EA", zeroline=False, tickformat=",d", automargin=True),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title=None),
        separators=",.",
        hoverlabel=dict(bgcolor="white", font_family="Inter, sans-serif"),
        bargap=0.25,
    )
)

# Theme options cannot style the metric cards, so a few targeted CSS rules do.
CSS = """
<style>
[data-testid="stMetric"] {
    background: #FFFFFF;
    box-shadow: 0 1px 3px rgba(0, 50, 71, 0.08);
}
[data-testid="stMetricLabel"] p {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #5B7785;
}
[data-testid="stMetricValue"] { font-weight: 700; }
.data-status { color: #5B7785; font-size: 0.85rem; margin-top: -0.75rem; }
@media (max-width: 640px) {
    h1 { font-size: 1.75rem !important; }
}
</style>
"""


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Read the shared CSV files built by ``_shared/prepare_data.py``.

    :return: overview table and the single meta row
    """
    overview = pd.read_csv(DATA_DIR / "overview.csv")
    meta = pd.read_csv(DATA_DIR / "meta.csv", dtype=str).iloc[0]
    return overview, meta


def german_int(value: float) -> str:
    """Format a number with a dot as thousands separator.

    :param value: number to format
    :return: e.g. ``113.385``
    """
    return f"{value:,.0f}".replace(",", ".")


def bar_chart(yearly: pd.DataFrame, types: list[str], stacked: bool) -> go.Figure:
    """Build the annual additions bar chart.

    :param yearly: charging points per year (index) and ``lp_*`` column
    :param types: selected power types
    :param stacked: one bar segment per type if True, else one total bar
    :return: plotly figure
    """
    fig = go.Figure(layout=dict(template="now", barmode="stack", height=360))
    if stacked:
        for t in types:
            label, color = CATEGORIES[t]
            fig.add_bar(x=yearly.index, y=yearly[f"lp_{t}"], name=label, marker_color=color)
    else:
        fig.add_bar(x=yearly.index, y=yearly.sum(axis=1), name="Ladepunkte", marker_color=DARK_BLUE)
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f}", marker_cornerradius=4)
    return fig


st.set_page_config(page_title="Ladeinfrastruktur in Deutschland", layout="wide")
st.html(CSS)
overview, meta = load_data()

with st.sidebar:
    st.subheader("Filter")
    state = st.selectbox("Bundesland", [ALL_STATES, *sorted(overview["bundesland"].unique())])
    types = st.pills(
        "Leistungstyp",
        list(CATEGORIES),
        selection_mode="multi",
        default=list(CATEGORIES),
        format_func=lambda t: CATEGORIES[t][0],
    )

st.title("Ladeinfrastruktur in Deutschland")
st.html(
    f'<p class="data-status">Datenstand: BNetzA: {meta.bnetza_stand} | '
    f"KBA: {meta.kba_stand} (Update: {meta['update']})</p>"
)

if not types:
    st.info("Bitte wähle mindestens einen Leistungstyp aus.")
    st.stop()

rows = overview if state == ALL_STATES else overview[overview["bundesland"] == state]
point_cols = [f"lp_{t}" for t in types]
# A station counts once if any of its charging points matches a selected type.
matching = rows[[f"has_{t}" for t in types]].any(axis=1)
hpc_points = rows["lp_hpc"].sum() if "hpc" in types else 0
gigawatt = f"{rows.loc[matching, 'kw'].sum() / 1_000_000:.2f}".replace(".", ",")

kpis = {
    "Ladestationen": german_int(rows.loc[matching, "stationen"].sum()),
    "Ladepunkte": german_int(rows[point_cols].to_numpy().sum()),
    "HPC-Ladepunkte": german_int(hpc_points),
    "Gesamtleistung": f"{gigawatt} GW",
}
for column, (label, value) in zip(st.columns(4), kpis.items()):
    column.metric(label, value, border=True)

yearly = rows[rows["jahr"] >= 2010].groupby("jahr")[point_cols].sum()
left, right = st.columns(2)
with left.container(border=True):
    st.subheader("Jährlicher Zubau von Ladepunkten (Gesamt)")
    st.plotly_chart(bar_chart(yearly, types, stacked=False), theme=None)
with right.container(border=True):
    st.subheader("Jährlicher Zubau nach Leistungstyp")
    st.plotly_chart(bar_chart(yearly, types, stacked=True), theme=None)

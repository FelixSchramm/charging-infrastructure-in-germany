"""Overview page prototype: Solara with AppLayout and Vuetify theme (issue #39).

Run from this folder:
uv run --no-project --with-requirements requirements.txt solara run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import solara
import solara.lab

DATA_DIR = Path(__file__).resolve().parents[2] / "_shared" / "data"
ALL_STATES = "Alle Bundesländer"
GREEN = "#00B092"
DARK_BLUE = "#003247"
# Stacking order bottom to top follows the dict order.
CATEGORIES = {
    "hpc": ("HPC-Laden (>= 150 kW)", GREEN),
    "schnell": ("Schnellladen (> 22 kW)", DARK_BLUE),
    "normal": ("Normalladen (<= 22 kW)", "#D3D3D3"),
}
LABEL_TO_KEY = {label: key for key, (label, _) in CATEGORIES.items()}
# FigurePlotly draws a chart once, before the layout has settled, and never resizes it.
# This invisible Vue template refits every chart whenever its container changes size.
RESIZE_CHARTS = """
<template><span></span></template>
<script>
module.exports = {
  mounted() {
    const resizer = new ResizeObserver((entries) =>
      entries.forEach((entry) => Plotly.Plots.resize(entry.target.firstElementChild))
    );
    new MutationObserver(() =>
      document.querySelectorAll(".js-plotly-plot").forEach((plot) => resizer.observe(plot.parentElement))
    ).observe(document.body, { childList: true, subtree: true });
  },
};
</script>
"""

overview = pd.read_csv(DATA_DIR / "overview.csv")
meta = pd.read_csv(DATA_DIR / "meta.csv", dtype=str).iloc[0]

selected_state = solara.reactive(ALL_STATES)
selected_labels = solara.reactive(list(LABEL_TO_KEY))


def german_int(value: float) -> str:
    """Format a number with a dot as thousands separator.

    :param value: number to format
    :return: e.g. ``113.385``
    """
    return f"{value:,.0f}".replace(",", ".")


def bar_chart(yearly: pd.DataFrame, keys: list[str], stacked: bool) -> go.Figure:
    """Build an annual additions bar chart.

    :param yearly: charging points per year (index) and ``lp_*`` column
    :param keys: selected power types
    :param stacked: one bar segment per type if True, else one total bar
    :return: plotly figure
    """
    fig = go.Figure(
        layout=dict(
            barmode="stack",
            height=360,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=DARK_BLUE),
            separators=",.",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#E1E7EA", tickformat=",d"),
            legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, traceorder="normal"),
        )
    )
    if stacked:
        for key in keys:
            label, color = CATEGORIES[key]
            fig.add_bar(x=yearly.index, y=yearly[f"lp_{key}"], name=label, marker_color=color)
    else:
        fig.add_bar(x=yearly.index, y=yearly.sum(axis=1), marker_color=DARK_BLUE)
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f}<extra></extra>")
    return fig


@solara.component
def Kpi(label: str, text: str):
    """Show one KPI card.

    :param label: KPI title
    :param text: German formatted value
    """
    with solara.Card(style={"border-radius": "12px", "height": "100%"}):
        solara.Text(label, style={"font-size": "0.9rem", "opacity": "0.7"})
        solara.Text(
            text,
            style={
                "display": "block",
                "font-size": "2rem",
                "font-weight": "600",
                "color": DARK_BLUE,
            },
        )


@solara.component
def Content():
    """Show KPIs and charts for the current filters, or a hint if no type is selected."""
    keys = [LABEL_TO_KEY[label] for label in selected_labels.value]
    if not keys:
        solara.Info("Bitte wähle mindestens einen Leistungstyp aus.")
        return
    rows = (
        overview
        if selected_state.value == ALL_STATES
        else overview[overview["bundesland"] == selected_state.value]
    )
    matching = rows[rows[[f"has_{k}" for k in keys]].any(axis=1)]
    lp_columns = [f"lp_{k}" for k in keys]
    gigawatt = matching["kw"].sum() / 1_000_000
    kpis = {
        "Ladestationen": german_int(matching["stationen"].sum()),
        "Ladepunkte": german_int(rows[lp_columns].to_numpy().sum()),
        "HPC-Ladepunkte": german_int(rows["lp_hpc"].sum() if "hpc" in keys else 0),
        "Gesamtleistung": f"{gigawatt:.2f} GW".replace(".", ","),
    }
    yearly = rows[rows["jahr"] >= 2010].groupby("jahr")[lp_columns].sum()
    # Four KPIs per row on desktop, two on tablets, one on phones.
    with solara.ColumnsResponsive(default=12, small=6, large=3):
        for label, text in kpis.items():
            Kpi(label, text)
    with solara.ColumnsResponsive(default=12, large=6):
        with solara.Card("Jährlicher Zubau von Ladepunkten (Gesamt)"):
            solara.FigurePlotly(bar_chart(yearly, keys, stacked=False))
        with solara.Card("Jährlicher Zubau nach Leistungstyp"):
            solara.FigurePlotly(bar_chart(yearly, keys, stacked=True))


@solara.component
def Layout(children: list):
    """Wrap every page in the app layout; ``solara run`` picks this up by its name.

    :param children: page content
    """
    # AppLayout turns the sidebar into a drawer behind a menu button on phones.
    solara.AppLayout(children=children, color=DARK_BLUE, sidebar_open=None)


@solara.component
def Page():
    """Overview page: sidebar filters, data date, KPIs and charts."""
    # The title also fills the app bar of the layout.
    solara.Title("Ladeinfrastruktur in Deutschland")
    # Solara creates the theme widget per browser session, so set the colors here.
    solara.lab.theme.themes.light.primary = GREEN
    solara.lab.theme.themes.light.secondary = DARK_BLUE
    solara.Style(".v-application, .v-main { background: #F4F7F8 !important; }")
    solara.v.VuetifyTemplate(template=RESIZE_CHARTS)
    with solara.Sidebar():
        solara.Select(
            "Bundesland",
            value=selected_state,
            values=[ALL_STATES, *sorted(overview["bundesland"].unique())],
        )
        solara.SelectMultiple("Leistungstyp", selected_labels, list(LABEL_TO_KEY))
    solara.Text(
        f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
        f"(Update: {meta['update']})",
        style={"font-size": "0.85rem", "opacity": "0.75"},
    )
    Content()

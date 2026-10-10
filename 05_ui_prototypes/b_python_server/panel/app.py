"""Overview page prototype: Panel (HoloViz) with FastListTemplate (issue #36).

Run from this folder:
uv run --no-project --with-requirements requirements.txt panel serve app.py
"""

from pathlib import Path

import pandas as pd
import panel as pn
import plotly.graph_objects as go

# The template has no responsive title size; the long title would overflow on phones.
pn.extension(
    "plotly", raw_css=["@media (max-width: 600px) { .app-header .title { font-size: 1.1rem; } }"]
)

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

overview = pd.read_csv(DATA_DIR / "overview.csv")
meta = pd.read_csv(DATA_DIR / "meta.csv", dtype=str).iloc[0]

state = pn.widgets.Select(
    name="Bundesland", options=[ALL_STATES, *sorted(overview["bundesland"].unique())]
)
types = pn.widgets.CheckBoxGroup(
    name="Leistungstyp",
    options={label: key for key, (label, _) in CATEGORIES.items()},
    value=list(CATEGORIES),
)


def german_int(value: float) -> str:
    """Format a number with a dot as thousands separator.

    :param value: number to format
    :return: e.g. ``113.385``
    """
    return f"{value:,.0f}".replace(",", ".")


def kpi(label: str, value: float, text: str) -> pn.indicators.Number:
    """Build one KPI card.

    :param label: KPI title
    :param value: numeric value
    :param text: German formatted value; ``Number.format`` only knows Python's
        format spec, which has no dot as thousands separator
    :return: number indicator
    """
    return pn.indicators.Number(
        name=label,
        value=value,
        format=text,
        default_color=DARK_BLUE,
        font_size="28pt",
        title_size="12pt",
        # flex lets the four cards share a row on desktop and wrap on phones.
        styles={
            "background": "white",
            "border-radius": "12px",
            "padding": "4px 20px",
            "flex": "1 1 220px",
        },
    )


def bar_chart(title: str, yearly: pd.DataFrame, keys: list[str], stacked: bool) -> pn.Card:
    """Build an annual additions bar chart in a card.

    :param title: card title
    :param yearly: charging points per year (index) and ``lp_*`` column
    :param keys: selected power types
    :param stacked: one bar segment per type if True, else one total bar
    :return: card with a plotly pane
    """
    fig = go.Figure(
        layout=dict(
            barmode="stack",
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
    plot = pn.pane.Plotly(fig, height=360, sizing_mode="stretch_width", config={"responsive": True})
    return pn.Card(
        plot,
        title=title,
        collapsible=False,
        header_background="white",
        styles={"flex": "1 1 480px", "background": "white", "border-radius": "12px"},
    )


def content(selected_state: str, keys: list[str]) -> pn.viewable.Viewable:
    """Build KPIs and charts for the current filters.

    :param selected_state: federal state or ``ALL_STATES``
    :param keys: selected power types
    :return: hint if no type is selected, else KPI row and charts
    """
    if not keys:
        return pn.pane.Alert("Bitte wähle mindestens einen Leistungstyp aus.", alert_type="info")
    rows = (
        overview
        if selected_state == ALL_STATES
        else overview[overview["bundesland"] == selected_state]
    )
    matching = rows[rows[[f"has_{k}" for k in keys]].any(axis=1)]
    lp_columns = [f"lp_{k}" for k in keys]
    stations = matching["stationen"].sum()
    points = rows[lp_columns].to_numpy().sum()
    hpc_points = rows["lp_hpc"].sum() if "hpc" in keys else 0
    gigawatt = matching["kw"].sum() / 1_000_000
    yearly = rows[rows["jahr"] >= 2010].groupby("jahr")[lp_columns].sum()
    kpis = pn.FlexBox(
        kpi("Ladestationen", stations, german_int(stations)),
        kpi("Ladepunkte", points, german_int(points)),
        kpi("HPC-Ladepunkte", hpc_points, german_int(hpc_points)),
        kpi("Gesamtleistung", gigawatt, f"{gigawatt:.2f} GW".replace(".", ",")),
        gap="16px",
    )
    charts = pn.FlexBox(
        bar_chart("Jährlicher Zubau von Ladepunkten (Gesamt)", yearly, keys, stacked=False),
        bar_chart("Jährlicher Zubau nach Leistungstyp", yearly, keys, stacked=True),
        gap="16px",
        flex_wrap="wrap",
    )
    return pn.Column(kpis, charts, sizing_mode="stretch_width")


pn.template.FastListTemplate(
    title="Ladeinfrastruktur in Deutschland",
    main=[
        pn.pane.Markdown(
            f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
            f"(Update: {meta['update']})",
            styles={"font-size": "0.85em", "opacity": "0.75"},
        ),
        # Filters sit in the main area: the template sidebar does not collapse on phones.
        pn.FlexBox(
            state,
            pn.Column(pn.widgets.StaticText(value="Leistungstyp"), types),
            gap="8px 32px",
            styles={"background": "white", "border-radius": "12px", "padding": "8px 12px"},
        ),
        pn.bind(content, state, types),
    ],
    accent_base_color=GREEN,
    header_background=DARK_BLUE,
    background_color="#F4F7F8",
    main_layout=None,
    theme_toggle=False,
).servable()

# Overview page prototype: Shiny for Python, Express syntax (issue #35).
# No module docstring: Shiny Express renders top-level strings into the page.
# Run from this folder:
# uv run --no-project --with-requirements requirements.txt shiny run app.py

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from shiny import reactive, render, req
from shiny.express import input, ui
from shinywidgets import render_plotly

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

# Bootstrap Sass variables, compiled by libsass at startup.
theme = ui.Theme("shiny").add_defaults(
    primary=GREEN,
    secondary=DARK_BLUE,
    body_bg="#F4F7F8",
    body_color=DARK_BLUE,
    headings_color=DARK_BLUE,
    border_radius="0.75rem",
    navbar_bg=DARK_BLUE,
)


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
        for t in types:
            label, color = CATEGORIES[t]
            fig.add_bar(x=yearly.index, y=yearly[f"lp_{t}"], name=label, marker_color=color)
    else:
        fig.add_bar(x=yearly.index, y=yearly.sum(axis=1), marker_color=DARK_BLUE)
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f}<extra></extra>")
    return fig


ui.page_opts(
    title=ui.div(
        # headings_color would make the title dark on the dark navbar.
        ui.h4("Ladeinfrastruktur in Deutschland", class_="mb-0 text-white"),
        ui.span(
            f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
            f"(Update: {meta['update']})",
            class_="small opacity-75",
        ),
    ),
    window_title="Ladeinfrastruktur in Deutschland",
    theme=theme,
    fillable=False,
)

with ui.sidebar(title="Filter"):
    ui.input_select("state", "Bundesland", [ALL_STATES, *sorted(overview["bundesland"].unique())])
    ui.input_checkbox_group(
        "types",
        "Leistungstyp",
        {k: v[0] for k, v in CATEGORIES.items()},
        selected=list(CATEGORIES),
    )


@reactive.calc
def rows() -> pd.DataFrame:
    """Rows of the selected federal state.

    :return: filtered ``overview`` rows
    """
    if input.state() == ALL_STATES:
        return overview
    return overview[overview["bundesland"] == input.state()]


@reactive.calc
def types() -> list[str]:
    """Selected power types; stops all outputs while none is selected.

    :return: selected type keys
    """
    return list(req(input.types()))


@reactive.calc
def matching() -> pd.DataFrame:
    """Rows whose stations have at least one charging point of a selected type.

    :return: filtered rows
    """
    return rows()[rows()[[f"has_{t}" for t in types()]].any(axis=1)]


@reactive.calc
def yearly() -> pd.DataFrame:
    """Charging points per year from 2010 for the selected types.

    :return: one ``lp_*`` column per selected type, indexed by year
    """
    recent = rows()[rows()["jahr"] >= 2010]
    return recent.groupby("jahr")[[f"lp_{t}" for t in types()]].sum()


# The hint and the dashboard are toggled in the browser, so no output errors.
with ui.panel_conditional("!input.types || input.types.length === 0"):
    ui.div("Bitte wähle mindestens einen Leistungstyp aus.", class_="alert alert-info")

with ui.panel_conditional("input.types && input.types.length > 0"):
    with ui.layout_column_wrap(width="220px"):
        with ui.value_box(theme="primary"):
            "Ladestationen"

            @render.text
            def stations():
                """:return: number of matching stations"""
                return german_int(matching()["stationen"].sum())

        with ui.value_box(theme="secondary"):
            "Ladepunkte"

            @render.text
            def points():
                """:return: number of charging points of the selected types"""
                return german_int(rows()[[f"lp_{t}" for t in types()]].to_numpy().sum())

        with ui.value_box(theme="primary"):
            "HPC-Ladepunkte"

            @render.text
            def hpc_points():
                """:return: number of HPC charging points, 0 if HPC is not selected"""
                return german_int(rows()["lp_hpc"].sum() if "hpc" in types() else 0)

        with ui.value_box(theme="secondary"):
            "Gesamtleistung"

            @render.text
            def capacity():
                """:return: installed capacity of the matching stations in GW"""
                gigawatt = matching()["kw"].sum() / 1_000_000
                return f"{gigawatt:.2f} GW".replace(".", ",")

    with ui.layout_columns(col_widths={"sm": 12, "lg": 6}):
        with ui.card(full_screen=True):
            ui.card_header("Jährlicher Zubau von Ladepunkten (Gesamt)")

            @render_plotly
            def total_chart():
                """:return: bar chart of all selected charging points per year"""
                return bar_chart(yearly(), types(), stacked=False)

        with ui.card(full_screen=True):
            ui.card_header("Jährlicher Zubau nach Leistungstyp")

            @render_plotly
            def type_chart():
                """:return: stacked bar chart per power type and year"""
                return bar_chart(yearly(), types(), stacked=True)

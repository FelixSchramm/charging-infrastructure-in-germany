"""Overview page prototype: Dash + Dash Mantine Components (issue #34).

Run from this folder:
``uv run --no-project --with-requirements requirements.txt python app.py``
"""

from pathlib import Path

import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc

DATA_DIR = Path(__file__).resolve().parents[2] / "_shared" / "data"
ALL_STATES = "Alle Bundesländer"
DARK_BLUE = "#003247"
# Stacking order bottom to top follows the dict order.
CATEGORIES = {
    "hpc": ("HPC-Laden (>= 150 kW)", "#00B092"),
    "schnell": ("Schnellladen (> 22 kW)", DARK_BLUE),
    "normal": ("Normalladen (<= 22 kW)", "#D3D3D3"),
}

# Mantine needs ten shades per color; index 6 is the main shade (#00B092, #003247).
THEME = {
    "fontFamily": "Inter, sans-serif",
    "headings": {"fontFamily": "Inter, sans-serif"},
    "primaryColor": "now",
    "primaryShade": 6,
    "defaultRadius": "md",
    "colors": {
        "now": [
            "#E0FBF5",
            "#B8F2E5",
            "#8AE8D4",
            "#5CDEC3",
            "#2ED4B2",
            "#00C4A0",
            "#00B092",
            "#009A80",
            "#00836D",
            "#006B59",
        ],
        "navy": [
            "#E6EEF2",
            "#C2D4DD",
            "#9AB7C6",
            "#6F98AD",
            "#46798F",
            "#1E5670",
            "#003247",
            "#002B3D",
            "#002333",
            "#001B28",
        ],
    },
}

overview = pd.read_csv(DATA_DIR / "overview.csv")
meta = pd.read_csv(DATA_DIR / "meta.csv", dtype=str).iloc[0]


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
            height=340,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color=DARK_BLUE),
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
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f}<extra></extra>", marker_cornerradius=4)
    return fig


def kpi_card(label: str, value: str) -> dmc.Card:
    """Build one KPI card.

    :param label: KPI name
    :param value: formatted KPI value
    :return: Mantine card
    """
    return dmc.Card(
        [
            dmc.Text(label, size="xs", c="dimmed", tt="uppercase", fw=600),
            dmc.Text(value, fz=28, fw=700, c="navy"),
        ],
        withBorder=True,
        shadow="xs",
    )


def chart_card(title: str, figure: go.Figure) -> dmc.Card:
    """Build one card holding a chart.

    :param title: chart title
    :param figure: plotly figure
    :return: Mantine card
    """
    return dmc.Card(
        [
            dmc.Title(title, order=4, c="navy", mb="sm"),
            dcc.Graph(figure=figure, config={"displayModeBar": False}),
        ],
        withBorder=True,
        shadow="xs",
    )


filters = dmc.Card(
    dmc.Grid(
        [
            dmc.GridCol(
                dmc.Select(
                    id="state",
                    label="Bundesland",
                    data=[ALL_STATES, *sorted(overview["bundesland"].unique())],
                    value=ALL_STATES,
                    allowDeselect=False,
                ),
                span={"base": 12, "md": 4},
            ),
            dmc.GridCol(
                dmc.Stack(
                    [
                        dmc.Text("Leistungstyp", size="sm", fw=500),
                        dmc.ChipGroup(
                            dmc.Group([dmc.Chip(v[0], value=k) for k, v in CATEGORIES.items()]),
                            id="types",
                            multiple=True,
                            value=list(CATEGORIES),
                        ),
                    ],
                    gap=6,
                ),
                span={"base": 12, "md": 8},
            ),
        ],
        align="flex-end",
    ),
    withBorder=True,
    shadow="xs",
)

app = Dash(
    __name__,
    title="Ladeinfrastruktur in Deutschland",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
)
app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Stack(
                    [
                        dmc.Title("Ladeinfrastruktur in Deutschland", order=3, c="white"),
                        dmc.Text(
                            f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
                            f"(Update: {meta['update']})",
                            size="sm",
                            c="navy.1",
                        ),
                    ],
                    gap=0,
                    px="lg",
                    py="sm",
                ),
                bg="navy",
            ),
            dmc.AppShellMain(
                dmc.Container(
                    dmc.Stack([filters, dmc.Box(id="content")], gap="lg"),
                    size="xl",
                    py="lg",
                ),
                bg="#F4F7F8",
            ),
        ],
        header={"height": {"base": 124, "sm": 88}},
    ),
    theme=THEME,
)


@callback(Output("content", "children"), Input("state", "value"), Input("types", "value"))
def update_content(state: str, types: list[str]):
    """Recompute KPIs and charts for the selected filters.

    :param state: selected federal state or ``ALL_STATES``
    :param types: selected power types
    :return: KPI cards and charts, or a hint if no type is selected
    """
    if not types:
        return dmc.Alert("Bitte wähle mindestens einen Leistungstyp aus.", color="navy")

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
    yearly = rows[rows["jahr"] >= 2010].groupby("jahr")[point_cols].sum()

    return dmc.Stack(
        [
            dmc.SimpleGrid(
                [kpi_card(label, value) for label, value in kpis.items()],
                cols={"base": 2, "lg": 4},
            ),
            dmc.SimpleGrid(
                [
                    chart_card(
                        "Jährlicher Zubau von Ladepunkten (Gesamt)",
                        bar_chart(yearly, types, stacked=False),
                    ),
                    chart_card(
                        "Jährlicher Zubau nach Leistungstyp",
                        bar_chart(yearly, types, stacked=True),
                    ),
                ],
                cols={"base": 1, "lg": 2},
            ),
        ],
        gap="lg",
    )


if __name__ == "__main__":
    app.run(port=8050)

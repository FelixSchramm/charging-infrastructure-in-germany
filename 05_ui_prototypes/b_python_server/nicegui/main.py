"""Overview page prototype: NiceGUI with Quasar layout and ECharts (issue #38).

Run from this folder:
uv run --no-project --with-requirements requirements.txt python main.py
"""

from pathlib import Path

import pandas as pd
from nicegui import ui

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
# ECharts formats numbers in the browser; a leading colon makes NiceGUI pass JavaScript.
GERMAN_NUMBER_JS = "value => value.toLocaleString('de-DE')"

overview = pd.read_csv(DATA_DIR / "overview.csv")
meta = pd.read_csv(DATA_DIR / "meta.csv", dtype=str).iloc[0]


def german_int(value: float) -> str:
    """Format a number with a dot as thousands separator.

    :param value: number to format
    :return: e.g. ``113.385``
    """
    return f"{value:,.0f}".replace(",", ".")


def bar_chart(yearly: pd.DataFrame, keys: list[str], stacked: bool) -> dict:
    """Build the ECharts options of an annual additions bar chart.

    :param yearly: charging points per year (index) and ``lp_*`` column
    :param keys: selected power types
    :param stacked: one bar segment per type if True, else one total bar
    :return: ECharts options
    """
    if stacked:
        series = [
            {
                "type": "bar",
                "stack": "total",
                "name": CATEGORIES[key][0],
                "color": CATEGORIES[key][1],
                "data": yearly[f"lp_{key}"].tolist(),
            }
            for key in keys
        ]
    else:
        series = [{"type": "bar", "color": DARK_BLUE, "data": yearly.sum(axis=1).tolist()}]
    return {
        # containLabel keeps the axis labels inside the card; the legend scrolls on phones.
        "grid": {
            "left": 0,
            "right": 0,
            "bottom": 0,
            "top": 40 if stacked else 10,
            "containLabel": True,
        },
        "legend": {"show": stacked, "type": "scroll", "top": 0, "left": 0},
        "tooltip": {"trigger": "axis", ":valueFormatter": GERMAN_NUMBER_JS},
        "xAxis": {"type": "category", "data": yearly.index.astype(str).tolist()},
        "yAxis": {"type": "value", "axisLabel": {":formatter": GERMAN_NUMBER_JS}},
        "series": series,
    }


@ui.page("/")
def page() -> None:
    """Overview page: header, filter drawer, data date, KPIs and charts."""
    ui.colors(primary=GREEN, secondary=DARK_BLUE)
    ui.query("body").classes("bg-[#F4F7F8]")
    labels = {key: label for key, (label, _) in CATEGORIES.items()}

    @ui.refreshable
    def content() -> None:
        """Show KPIs and charts for the current filters, or a hint if no type is selected."""
        keys = type_select.value
        if not keys:
            ui.label("Bitte wähle mindestens einen Leistungstyp aus.").classes(
                "w-full p-4 rounded-lg bg-blue-50 text-[#003247]"
            )
            return
        rows = (
            overview
            if state_select.value == ALL_STATES
            else overview[overview["bundesland"] == state_select.value]
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
        with ui.grid().classes("w-full gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"):
            for label, text in kpis.items():
                with ui.card().classes("rounded-xl shadow-sm"):
                    ui.label(label).classes("text-sm text-gray-500")
                    ui.label(text).classes("text-3xl font-semibold text-[#003247]")
        with ui.grid().classes("w-full gap-4 grid-cols-1 lg:grid-cols-2"):
            for title, stacked in [
                ("Jährlicher Zubau von Ladepunkten (Gesamt)", False),
                ("Jährlicher Zubau nach Leistungstyp", True),
            ]:
                with ui.card().classes("rounded-xl shadow-sm"):
                    ui.label(title).classes("text-lg font-medium text-[#003247]")
                    ui.echart(bar_chart(yearly, keys, stacked)).classes("w-full h-80")

    # Quasar hides the drawer on narrow screens; the menu button opens it as an overlay.
    with ui.header().classes("bg-[#003247] items-center no-wrap"):
        ui.button(icon="menu", on_click=lambda: drawer.toggle()).props("flat color=white")
        ui.label("Ladeinfrastruktur in Deutschland").classes("text-lg sm:text-xl font-semibold")
    with ui.left_drawer().classes("bg-white p-4 gap-4") as drawer:
        state_select = ui.select(
            [ALL_STATES, *sorted(overview["bundesland"].unique())],
            label="Bundesland",
            value=ALL_STATES,
            on_change=content.refresh,
        ).classes("w-full")
        type_select = (
            ui.select(
                labels,
                label="Leistungstyp",
                value=list(labels),
                multiple=True,
                on_change=content.refresh,
            )
            .classes("w-full")
            .props("use-chips")
        )
    ui.label(
        f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
        f"(Update: {meta['update']})"
    ).classes("text-sm text-gray-500")
    content()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Ladeinfrastruktur in Deutschland", reload=False, show=False)

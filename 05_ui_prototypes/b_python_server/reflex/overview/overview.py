"""Overview page prototype: Reflex with Radix Themes and Recharts (issue #37).

Run from the prototype folder:
uv run --no-project --with-requirements requirements.txt reflex run
"""

from pathlib import Path

import pandas as pd
import reflex as rx

DATA_DIR = Path(__file__).resolve().parents[3] / "_shared" / "data"
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
STATES = [ALL_STATES, *sorted(overview["bundesland"].unique())]


def german_int(value: float) -> str:
    """Format a number with a dot as thousands separator.

    :param value: number to format
    :return: e.g. ``113.385``
    """
    return f"{value:,.0f}".replace(",", ".")


class OverviewState(rx.State):
    """Filter selection and the KPIs and chart data derived from it."""

    state: str = ALL_STATES
    types: list[str] = list(CATEGORIES)

    @rx.event
    def set_state(self, value: str) -> None:
        """Select a federal state.

        :param value: federal state or ``ALL_STATES``
        """
        self.state = value

    @rx.event
    def toggle_type(self, key: str, checked: bool) -> None:
        """Add a power type to the selection or remove it.

        :param key: key of ``CATEGORIES``
        :param checked: new checkbox state
        """
        self.types = [
            k for k in CATEGORIES if (k == key and checked) or (k != key and k in self.types)
        ]

    def _rows(self) -> pd.DataFrame:
        """Return the rows of the selected federal state.

        :return: filtered ``overview`` rows
        """
        if self.state == ALL_STATES:
            return overview
        return overview[overview["bundesland"] == self.state]

    @rx.var
    def kpis(self) -> list[list[str]]:
        """Compute the four KPIs as label/value pairs.

        :return: ``[[label, formatted value], ...]``
        """
        rows = self._rows()
        matching = rows[rows[[f"has_{k}" for k in self.types]].any(axis=1)]
        gigawatt = matching["kw"].sum() / 1_000_000
        return [
            ["Ladestationen", german_int(matching["stationen"].sum())],
            ["Ladepunkte", german_int(rows[[f"lp_{k}" for k in self.types]].to_numpy().sum())],
            ["HPC-Ladepunkte", german_int(rows["lp_hpc"].sum() if "hpc" in self.types else 0)],
            ["Gesamtleistung", f"{gigawatt:.2f} GW".replace(".", ",")],
        ]

    @rx.var
    def yearly(self) -> list[dict[str, int]]:
        """Sum the charging points per year from 2010 on, per type and in total.

        :return: one dict per year with ``jahr``, the selected ``lp_*`` keys and ``total``
        """
        rows = self._rows()
        yearly = rows[rows["jahr"] >= 2010].groupby("jahr")[[f"lp_{k}" for k in self.types]].sum()
        yearly["total"] = yearly.sum(axis=1)
        return yearly.reset_index().to_dict("records")


def kpi_card(kpi: rx.Var) -> rx.Component:
    """Render one KPI as a card.

    :param kpi: label/value pair from ``OverviewState.kpis``
    :return: card component
    """
    return rx.card(
        rx.text(kpi[0], size="2", color_scheme="gray"),
        rx.heading(kpi[1], size="7", color=DARK_BLUE),
        size="3",
    )


def chart_card(title: str, *bars: rx.Component, legend: bool = False) -> rx.Component:
    """Render an annual additions bar chart in a card.

    :param title: chart title
    :param bars: ``rx.recharts.bar`` series
    :param legend: show the series legend
    :return: card component
    """
    return rx.card(
        rx.heading(title, size="4", color=DARK_BLUE),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.x_axis(data_key="jahr"),
            # German thousands separator on the axis and in the tooltip.
            rx.recharts.y_axis(
                tick_formatter=rx.vars.FunctionStringVar("v => v.toLocaleString('de-DE')")
            ),
            rx.recharts.graphing_tooltip(
                formatter=rx.vars.FunctionStringVar("v => v.toLocaleString('de-DE')")
            ),
            *bars,
            # Recharts 3 sorts legend entries by name; a constant sorter keeps the stacking order.
            rx.cond(
                legend,
                rx.recharts.legend(
                    custom_attrs={"itemSorter": rx.vars.FunctionStringVar("() => 0")}
                ),
            ),
            data=OverviewState.yearly,
            height=320,
        ),
        size="3",
    )


def stacked_bar(key: str) -> rx.Component:
    """Render the bar segment of one power type, only if it is selected.

    :param key: key of ``CATEGORIES``
    :return: conditional bar component
    """
    label, color = CATEGORIES[key]
    return rx.cond(
        OverviewState.types.contains(key),
        rx.recharts.bar(data_key=f"lp_{key}", name=label, fill=color, stack_id="total"),
    )


def filters() -> rx.Component:
    """Render the federal state select and the power type checkboxes.

    :return: card with both filters
    """
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.text("Bundesland", size="2", weight="medium"),
                rx.select(STATES, value=OverviewState.state, on_change=OverviewState.set_state),
            ),
            rx.vstack(
                rx.text("Leistungstyp", size="2", weight="medium"),
                rx.flex(
                    *[
                        rx.checkbox(
                            label,
                            checked=OverviewState.types.contains(key),
                            on_change=OverviewState.toggle_type(key),
                        )
                        for key, (label, _) in CATEGORIES.items()
                    ],
                    direction=rx.breakpoints(initial="column", sm="row"),
                    spacing="3",
                    wrap="wrap",
                ),
            ),
            direction=rx.breakpoints(initial="column", md="row"),
            spacing="5",
        ),
        size="3",
        width="100%",
    )


def content() -> rx.Component:
    """Render KPIs and charts, or a hint if no power type is selected.

    :return: content component
    """
    return rx.cond(
        OverviewState.types,
        rx.fragment(
            # Four KPIs per row on desktop, two on tablets, one on phones.
            rx.grid(
                rx.foreach(OverviewState.kpis, kpi_card),
                columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card(
                    "Jährlicher Zubau von Ladepunkten (Gesamt)",
                    rx.recharts.bar(data_key="total", name="Ladepunkte", fill=DARK_BLUE),
                ),
                chart_card(
                    "Jährlicher Zubau nach Leistungstyp",
                    *[stacked_bar(key) for key in CATEGORIES],
                    legend=True,
                ),
                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),
        ),
        rx.callout("Bitte wähle mindestens einen Leistungstyp aus.", icon="info", width="100%"),
    )


def index() -> rx.Component:
    """Overview page: header bar, data date, filters, KPIs and charts.

    :return: page component
    """
    return rx.box(
        rx.box(
            rx.heading(
                "Ladeinfrastruktur in Deutschland",
                size=rx.breakpoints(initial="5", sm="7"),
                color="white",
            ),
            rx.text(
                f"Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} "
                f"(Update: {meta['update']})",
                size="2",
                color="rgba(255, 255, 255, 0.75)",
            ),
            background=DARK_BLUE,
            border_bottom=f"4px solid {GREEN}",
            padding=rx.breakpoints(initial="16px", sm="24px 40px"),
        ),
        rx.vstack(
            filters(),
            content(),
            spacing="4",
            max_width="1440px",
            margin="0 auto",
            padding=rx.breakpoints(initial="12px", sm="24px 40px"),
        ),
        background="#F4F7F8",
        min_height="100vh",
    )


# Radix only offers named color scales (theme in rxconfig.py); its solid accent step
# is set to NOW-Grün.
# Recharts colors legend labels like their series, which leaves the grey label unreadable.
app = rx.App(
    style={
        ".radix-themes": {"--accent-9": GREEN},
        ".recharts-legend-item-text": {"color": f"{DARK_BLUE} !important"},
    }
)
app.add_page(index, title="Ladeinfrastruktur in Deutschland")

"""KPI-Kacheln: Ladestationen, Ladepunkte, HPC-Ladepunkte, Gesamtleistung,
Betreiber, Ø Leistung je Ladepunkt, Ø Ladepunkte je Station, Orte mit Ladeinfrastruktur."""

import pandas as pd
import streamlit as st

from config import HPC_THRESHOLD_KW

_METRIC_LABEL_STYLE = """
    <style>
    [data-testid="stMetricLabel"] p { font-size: 1.2rem !important; }
    </style>
"""


def _de(value: int) -> str:
    """Formatiert eine Ganzzahl mit Punkt als Tausendertrennzeichen."""
    return f"{value:,}".replace(",", ".")


def _de_dec(value: float, decimals: int = 1) -> str:
    """Formatiert eine Kommazahl mit Komma als Dezimaltrennzeichen."""
    return f"{value:.{decimals}f}".replace(".", ",")


def render_kpis(df_filtered: pd.DataFrame):
    """Zeichnet die acht KPI-Kacheln aus den gefilterten Daten."""
    df_stationen = df_filtered.drop_duplicates(subset="ladestation_id")
    n_ladepunkte = len(df_filtered)
    n_stationen = df_stationen["ladestation_id"].nunique()

    st.markdown(_METRIC_LABEL_STYLE, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ladestationen", _de(n_stationen))
    col2.metric("Ladepunkte", _de(n_ladepunkte))
    col3.metric(
        "HPC-Ladepunkte",
        _de(len(df_filtered[df_filtered["LadeleistungInKW"] >= HPC_THRESHOLD_KW])),
    )
    gesamtleistung_gw = df_stationen["InstallierteLadeleistungNLL"].sum() / 1_000_000
    col4.metric("Gesamtleistung", f"{_de_dec(gesamtleistung_gw, 2)} GW")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Betreiber", _de(df_filtered["BetreiberBereinigt"].nunique()))

    if n_ladepunkte > 0:
        col6.metric(
            "Ø Leistung je Ladepunkt",
            f"{_de_dec(df_filtered['LadeleistungInKW'].mean())} kW",
        )
    else:
        col6.metric("Ø Leistung je Ladepunkt", "–")

    if n_stationen > 0:
        col7.metric("Ø Ladepunkte je Station", _de_dec(n_ladepunkte / n_stationen))
    else:
        col7.metric("Ø Ladepunkte je Station", "–")

    col8.metric("Orte mit Ladeinfrastruktur", _de(df_filtered["Ort"].nunique()))

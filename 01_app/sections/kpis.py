"""KPI-Kacheln: Ladestationen, Ladepunkte, HPC-Ladepunkte, Gesamtleistung."""

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


def render_kpis(df_filtered: pd.DataFrame):
    """Zeichnet die vier KPI-Kacheln aus den gefilterten Daten."""
    df_stationen = df_filtered.drop_duplicates(subset="ladestation_id")

    st.markdown(_METRIC_LABEL_STYLE, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ladestationen", _de(df_stationen["ladestation_id"].nunique()))
    col2.metric("Ladepunkte", _de(len(df_filtered)))
    col3.metric(
        "HPC-Ladepunkte",
        _de(len(df_filtered[df_filtered["LadeleistungInKW"] >= HPC_THRESHOLD_KW])),
    )
    gesamtleistung_gw = df_stationen["InstallierteLadeleistungNLL"].sum() / 1_000_000
    col4.metric("Gesamtleistung", f"{gesamtleistung_gw:.2f} GW".replace(".", ","))

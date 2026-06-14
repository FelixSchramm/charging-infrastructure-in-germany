"""Kopfbereich: Titel und Datenstand-Zeile."""

import pandas as pd
import streamlit as st

# Wird vom monatlichen GitHub-Action-Update überschrieben. Der Import zwingt
# Streamlit Cloud bei jedem Daten-Commit zu einem Redeploy (sonst bleibt der
# laufende Prozess auf den alten, im Container zwischengespeicherten Daten).
try:
    from _data_version import LAST_UPDATED
except ImportError:
    LAST_UPDATED = "lokal"


def render_header(df: pd.DataFrame, df_kba: pd.DataFrame | None):
    """Zeichnet Titel und Datenstand-Hinweis (BNetzA / KBA / Update)."""
    st.title("Ladeinfrastruktur in Deutschland")

    bnetza_stand = df["Inbetriebnahmedatum"].max().strftime("%d.%m.%Y")
    if df_kba is not None:
        raw = df_kba["Berichtszeitpunkt"].iloc[0]  # z.B. "2024.04"
        year, month = raw.split(".")
        kba_stand = pd.Timestamp(year=int(year), month=int(month), day=1).strftime("%m/%Y")
    else:
        kba_stand = "–"

    st.markdown(
        f'<p style="text-align:left; color:#999; font-size:0.85rem; margin-top:-1rem;">'
        f"Datenstand: BNetzA: {bnetza_stand} | KBA: {kba_stand} "
        f"(Update: {LAST_UPDATED})</p>",
        unsafe_allow_html=True,
    )

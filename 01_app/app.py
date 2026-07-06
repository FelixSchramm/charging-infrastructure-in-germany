"""Streamlit-Dashboard: Ladeinfrastruktur in Deutschland.

Schlanker Entry-Point. Die eigentliche Logik liegt in:
- ``config.py``        – Seiteneinstellung, Farben, Konstanten
- ``data_loading.py``  – Laden/Vorbereiten der Daten (mit Caching)
- ``filters.py``       – Seitenleisten-Filter und ihre Anwendung
- ``sections/``        – je ein Modul pro Dashboard-Abschnitt

Start:  uv run streamlit run 01_app/app.py
"""

from config import configure_page

# Muss vor jedem anderen Streamlit-Aufruf stehen.
configure_page()

import streamlit as st

from data_loading import load_all
from filters import apply_filters, render_sidebar
from sections import (
    render_analyses,
    render_header,
    render_info,
    render_kpis,
    render_map,
    render_timeseries,
)

df, gdf_districts, df_kba = load_all()

if df is not None:
    filters = render_sidebar(df)
    df_filtered = apply_filters(df, filters)

    # Titel und Datenstand bleiben ueber den Tabs immer sichtbar.
    render_header(df, df_kba)

    tab_ueberblick, tab_zeit, tab_betreiber, tab_regional, tab_info = st.tabs(
        [
            "Überblick",
            "Zeitverlauf",
            "Betreiber & Typen",
            "Regional",
            "Info & Quellen",
        ]
    )

    with tab_ueberblick:
        render_kpis(df_filtered)
    with tab_zeit:
        render_timeseries(df_filtered)
    with tab_betreiber:
        render_analyses(df_filtered)
    with tab_regional:
        render_map(df, gdf_districts, df_kba, filters)
    with tab_info:
        render_info(df, df_kba)

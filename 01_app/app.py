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

    render_header(df, df_kba)
    render_kpis(df_filtered)
    render_timeseries(df_filtered)
    render_analyses(df_filtered)
    render_map(df, gdf_districts, df_kba, filters)
    render_info(df, df_kba)

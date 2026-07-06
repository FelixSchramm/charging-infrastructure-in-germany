"""Render-Funktionen der einzelnen Dashboard-Abschnitte."""

from sections.analyses import render_analyses
from sections.data_table import render_data_table
from sections.header import render_header
from sections.info import render_info
from sections.kpis import render_kpis
from sections.map_view import render_map
from sections.timeseries import render_kumulativ_charts, render_zubau_charts

__all__ = [
    "render_header",
    "render_kpis",
    "render_zubau_charts",
    "render_kumulativ_charts",
    "render_analyses",
    "render_map",
    "render_data_table",
    "render_info",
]

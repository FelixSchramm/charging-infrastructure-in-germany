"""Render-Funktionen der einzelnen Dashboard-Abschnitte."""

from sections.analyses import render_analyses
from sections.header import render_header
from sections.info import render_info
from sections.kpis import render_kpis
from sections.map_view import render_map
from sections.timeseries import render_timeseries

__all__ = [
    "render_header",
    "render_kpis",
    "render_timeseries",
    "render_analyses",
    "render_map",
    "render_info",
]

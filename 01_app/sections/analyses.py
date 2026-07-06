"""Detailanalysen: Anteil der Ladepunkttypen (Pie) und Top-10-Betreiber."""

import pandas as pd
import plotly.express as px
import streamlit as st

from config import LEISTUNGS_COLORS, NOW_GRUEN


def render_analyses(df_filtered: pd.DataFrame):
    """Zeichnet die beiden Detail-Charts nebeneinander."""
    st.header("Detaillierte Analysen")

    col1, col2 = st.columns(2)
    with col1:
        kategorie_counts = df_filtered["Leistungskategorie"].value_counts().reset_index()
        fig = px.pie(
            kategorie_counts, names="Leistungskategorie", values="count",
            title="<b>Anteil der Ladepunkttypen</b>",
            color="Leistungskategorie", color_discrete_map=LEISTUNGS_COLORS,
        )
        st.plotly_chart(fig, use_container_width=True, key="fig_kategorien")

    with col2:
        top_10 = df_filtered["BetreiberBereinigt"].value_counts().nlargest(10).reset_index()
        fig = px.bar(
            top_10, x="count", y="BetreiberBereinigt", orientation="h",
            title="<b>Top 10 Betreiber</b>",
            labels={"count": "Anzahl Ladepunkte", "BetreiberBereinigt": "Betreiber"},
            color_discrete_sequence=[NOW_GRUEN],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True, key="fig_betreiber")

"""Zeitreihen: jährlicher Zubau und kumulativer Bestand (gesamt + nach Typ)."""

import pandas as pd
import plotly.express as px
import streamlit as st

from config import CHART_START_YEAR, LEISTUNGS_COLORS, NOW_DUNKELBLAU


def render_zubau_charts(df_filtered: pd.DataFrame):
    """Zeichnet die beiden Überblick-Charts zum jährlichen Zubau."""
    zubau_gesamt, kat_basis = _build_basis(df_filtered)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            zubau_gesamt, x="Jahr", y="Anzahl",
            title="<b>Jährlicher Zubau von Ladepunkten (Gesamt)</b>",
            color_discrete_sequence=[NOW_DUNKELBLAU],
        )
        fig.update_layout(bargap=0.2)
        st.plotly_chart(fig, use_container_width=True, key="fig_zubau_gesamt")

    with col2:
        fig = px.bar(
            kat_basis, x="Jahr", y="Anzahl", color="Leistungskategorie",
            title="<b>Jährlicher Zubau nach Leistungstyp</b>",
            color_discrete_map=LEISTUNGS_COLORS,
        )
        fig.update_layout(bargap=0.2, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig, use_container_width=True, key="fig_zubau_kat")


def render_kumulativ_charts(df_filtered: pd.DataFrame):
    """Zeichnet die beiden Analyse-Charts zum kumulativen Bestand."""
    zubau_gesamt, kat_basis = _build_basis(df_filtered)

    col1, col2 = st.columns(2)
    with col1:
        cumulative_gesamt = _cumulative_gesamt(df_filtered, zubau_gesamt)
        fig = px.bar(
            cumulative_gesamt, x="Jahr", y="Anzahl",
            title="<b>Kumulativer Bestand an Ladepunkten (Gesamt)</b>",
            color_discrete_sequence=[NOW_DUNKELBLAU],
        )
        fig.update_layout(bargap=0.2)
        st.plotly_chart(fig, use_container_width=True, key="fig_cum_gesamt")

    with col2:
        kat_kumulativ = _cumulative_kat(df_filtered, kat_basis)
        fig = px.bar(
            kat_kumulativ, x="Jahr", y="Anzahl", color="Leistungskategorie",
            title="<b>Kumulativer Bestand nach Leistungstyp</b>",
            color_discrete_map=LEISTUNGS_COLORS,
        )
        fig.update_layout(bargap=0.2, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig, use_container_width=True, key="fig_cum_kat")


def _build_basis(df_filtered: pd.DataFrame):
    """Gemeinsame Basis für alle vier Charts (ab ``CHART_START_YEAR``)."""
    zubau_gesamt = df_filtered.groupby("Jahr").size().reset_index(name="Anzahl")
    zubau_gesamt = zubau_gesamt[zubau_gesamt["Jahr"] >= CHART_START_YEAR]

    kat_basis = (
        df_filtered.groupby(["Jahr", "Leistungskategorie"]).size().reset_index(name="Anzahl")
    )
    jahre_range = pd.RangeIndex(
        start=max(CHART_START_YEAR, kat_basis["Jahr"].min()),
        stop=kat_basis["Jahr"].max() + 1,
    )
    full_index = pd.MultiIndex.from_product(
        [jahre_range, list(LEISTUNGS_COLORS)], names=["Jahr", "Leistungskategorie"]
    )
    kat_basis = (
        kat_basis.set_index(["Jahr", "Leistungskategorie"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )
    return zubau_gesamt, kat_basis


def _cumulative_gesamt(df_filtered: pd.DataFrame, zubau_gesamt: pd.DataFrame) -> pd.DataFrame:
    """Kumulativer Gesamtbestand inkl. Offset für Jahre vor ``CHART_START_YEAR``."""
    zubau_alle_jahre = df_filtered.groupby("Jahr").size().reset_index(name="Anzahl")
    cumulative = zubau_gesamt.copy()
    offset = zubau_alle_jahre[zubau_alle_jahre["Jahr"] < CHART_START_YEAR]["Anzahl"].sum()
    cumulative["Anzahl"] = cumulative["Anzahl"].cumsum() + offset
    return cumulative


def _cumulative_kat(df_filtered: pd.DataFrame, kat_basis: pd.DataFrame) -> pd.DataFrame:
    """Kumulativer Bestand je Leistungskategorie inkl. Offset für frühe Jahre."""
    kat_alle_jahre = (
        df_filtered.groupby(["Jahr", "Leistungskategorie"]).size().reset_index(name="Anzahl")
    )
    kat_offsets = (
        kat_alle_jahre[kat_alle_jahre["Jahr"] < CHART_START_YEAR]
        .groupby("Leistungskategorie")["Anzahl"]
        .sum()
    )
    kat_kumulativ = kat_basis.copy()
    kat_kumulativ["Anzahl"] = kat_kumulativ.groupby("Leistungskategorie")["Anzahl"].cumsum()
    kat_kumulativ["Anzahl"] += (
        kat_kumulativ["Leistungskategorie"].map(kat_offsets).fillna(0).astype(int)
    )
    return kat_kumulativ

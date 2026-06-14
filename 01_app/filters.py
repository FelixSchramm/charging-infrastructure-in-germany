"""Seitenleisten-Filter: Rendern der Bedienelemente und Anwenden auf die Daten."""

from dataclasses import dataclass

import pandas as pd
import streamlit as st


@dataclass
class Filters:
    """Vom Nutzer in der Seitenleiste gewählte Filterwerte."""

    jahre: tuple[int, int]
    bundeslaender: list[str]
    leistungstypen: list[str]
    search_kreis: str
    search_betreiber: str


def render_sidebar(df: pd.DataFrame) -> Filters:
    """Zeichnet die Filter-Seitenleiste und gibt die gewählten Werte zurück."""
    st.sidebar.header("Filteroptionen")

    min_jahr, max_jahr = int(df["Jahr"].min()), int(df["Jahr"].max())
    selected_jahre = st.sidebar.slider(
        "Zeitraum (Jahr):", min_value=min_jahr, max_value=max_jahr, value=(min_jahr, max_jahr)
    )

    bundeslaender = sorted(df["Bundesland"].unique())
    selected_bundeslaender = st.sidebar.multiselect(
        "Bundesland:", options=bundeslaender, default=bundeslaender
    )

    leistungstypen = sorted(df["Leistungskategorie"].unique())
    selected_leistungstypen = st.sidebar.multiselect(
        "Leistungstyp:", options=leistungstypen, default=leistungstypen
    )

    search_kreis = st.sidebar.text_input("Landkreis/Stadt (Suche):", "").lower()
    search_betreiber = st.sidebar.text_input("Betreiber (Suche):", "").lower()

    return Filters(
        jahre=selected_jahre,
        bundeslaender=selected_bundeslaender,
        leistungstypen=selected_leistungstypen,
        search_kreis=search_kreis,
        search_betreiber=search_betreiber,
    )


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wendet alle Filter (inkl. Bundesland) auf den DataFrame an."""
    df_filtered = df[
        (df["Bundesland"].isin(f.bundeslaender))
        & (df["Jahr"] >= f.jahre[0])
        & (df["Jahr"] <= f.jahre[1])
        & (df["Leistungskategorie"].isin(f.leistungstypen))
    ]
    return _apply_search(df_filtered, f)


def apply_filters_for_map(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wie ``apply_filters``, aber ohne Bundesland-Filter (Karte ist gesamtdeutsch)."""
    df_filtered = df[
        (df["Jahr"] >= f.jahre[0])
        & (df["Jahr"] <= f.jahre[1])
        & (df["Leistungskategorie"].isin(f.leistungstypen))
    ]
    return _apply_search(df_filtered, f)


def _apply_search(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wendet die Text-Suchfelder (Kreis, Betreiber) an."""
    if f.search_kreis:
        df = df[df["KreisKreisfreieStadt"].str.lower().str.contains(f.search_kreis, na=False)]
    if f.search_betreiber:
        df = df[df["BetreiberBereinigt"].str.lower().str.contains(f.search_betreiber, na=False)]
    return df

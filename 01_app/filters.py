"""Seitenleisten-Filter: Rendern der Bedienelemente und Anwenden auf die Daten."""

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from config import LEISTUNGS_KATEGORIEN

# Auswahlwert der Kreis-Auswahl, der "kein Filter" bedeutet.
KREIS_ALLE = "(alle)"

# session_state-Keys der Filter-Widgets; der Reset-Button entfernt genau diese.
_FILTER_KEYS = (
    "flt_jahre",
    "flt_bundesland",
    "flt_leistung",
    "flt_kreis",
    "flt_betreiber",
)


@dataclass
class Filters:
    """Vom Nutzer in der Seitenleiste gewählte Filterwerte."""

    jahre: tuple[int, int]
    bundeslaender: list[str]
    leistungstypen: list[str]
    kreis: str | None
    betreiber: list[str]


def render_sidebar(df: pd.DataFrame) -> Filters:
    """Zeichnet die Filter-Seitenleiste und gibt die gewählten Werte zurück."""
    st.sidebar.header("Filteroptionen")

    # Setzt alle Filter auf ihre Startwerte zurueck, indem die Widget-Keys aus
    # dem session_state entfernt werden; der rerun zeichnet sie mit Defaults neu.
    if st.sidebar.button("Filter zurücksetzen", use_container_width=True):
        for key in _FILTER_KEYS:
            st.session_state.pop(key, None)
        st.rerun()

    min_jahr, max_jahr = int(df["Jahr"].min()), int(df["Jahr"].max())
    selected_jahre = st.sidebar.slider(
        "Zeitraum (Jahr):",
        min_value=min_jahr,
        max_value=max_jahr,
        value=(min_jahr, max_jahr),
        key="flt_jahre",
    )

    # Leere Auswahl bedeutet bewusst "alle": so startet das Widget aufgeräumt
    # (statt mit 16 Chips) und ein einzelnes Land ist ein Klick statt 15 Abwahlen.
    bundeslaender = sorted(df["Bundesland"].unique())
    selected_bundeslaender = st.sidebar.multiselect(
        "Bundesland:",
        options=bundeslaender,
        default=[],
        placeholder="Alle Bundesländer",
        help="Leer lassen = alle Bundesländer. Tippe zum Suchen, um einzelne auszuwählen.",
        key="flt_bundesland",
    )
    effektive_bundeslaender = selected_bundeslaender or bundeslaender

    # Feste Reihenfolge (nach Leistung, absteigend) statt alphabetisch; pills sind
    # bei nur drei Kategorien scanbarer als ein Multiselect.
    vorhandene_leistungstypen = set(df["Leistungskategorie"].unique())
    leistungstypen = [k for k in LEISTUNGS_KATEGORIEN if k in vorhandene_leistungstypen]
    selected_leistungstypen = st.sidebar.pills(
        "Leistungstyp:",
        options=leistungstypen,
        selection_mode="multi",
        default=leistungstypen,
        key="flt_leistung",
    )

    # selectbox/multiselect sind durchsuchbare Comboboxen: Tippen filtert die
    # echten Werte als Vorschläge, ohne die Seitenleiste mit langen Listen zu füllen.
    kreise = sorted(df["KreisKreisfreieStadt"].dropna().unique())
    selected_kreis = st.sidebar.selectbox(
        "Landkreis/Stadt:",
        options=[KREIS_ALLE, *kreise],
        index=0,
        help="Tippe zum Suchen (z. B. 'Mün' für München/Münster).",
        key="flt_kreis",
    )

    betreiber = sorted(
        {b.strip() for b in df["BetreiberBereinigt"].dropna() if b.strip()}
    )
    selected_betreiber = st.sidebar.multiselect(
        "Betreiber:",
        options=betreiber,
        default=[],
        placeholder="Betreiber suchen…",
        help="Leer lassen = alle Betreiber. Tippe die ersten Buchstaben für Vorschläge.",
        key="flt_betreiber",
    )

    return Filters(
        jahre=selected_jahre,
        bundeslaender=effektive_bundeslaender,
        leistungstypen=selected_leistungstypen,
        kreis=None if selected_kreis == KREIS_ALLE else selected_kreis,
        betreiber=selected_betreiber,
    )


def _format_de(n: int) -> str:
    """Formatiert eine ganze Zahl mit Punkt als Tausendertrennzeichen (de-DE)."""
    return f"{n:,}".replace(",", ".")


def render_result_count(df: pd.DataFrame, df_filtered: pd.DataFrame) -> None:
    """Zeigt in der Seitenleiste, wie viele Ladepunkte die Filter aktuell treffen."""
    st.sidebar.divider()
    st.sidebar.caption(
        f"**{_format_de(len(df_filtered))}** von {_format_de(len(df))} Ladepunkten"
    )


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wendet alle Filter (inkl. Bundesland) auf den DataFrame an."""
    df_filtered = df[
        (df["Bundesland"].isin(f.bundeslaender))
        & (df["Jahr"] >= f.jahre[0])
        & (df["Jahr"] <= f.jahre[1])
        & (df["Leistungskategorie"].isin(f.leistungstypen))
    ]
    return _apply_selection(df_filtered, f)


def apply_filters_for_map(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wie ``apply_filters``, aber ohne Bundesland-Filter (Karte ist gesamtdeutsch)."""
    df_filtered = df[
        (df["Jahr"] >= f.jahre[0])
        & (df["Jahr"] <= f.jahre[1])
        & (df["Leistungskategorie"].isin(f.leistungstypen))
    ]
    return _apply_selection(df_filtered, f)


def _apply_selection(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Wendet die Auswahl aus Kreis- und Betreiber-Combobox an."""
    if f.kreis:
        df = df[df["KreisKreisfreieStadt"] == f.kreis]
    if f.betreiber:
        df = df[df["BetreiberBereinigt"].str.strip().isin(f.betreiber)]
    return df

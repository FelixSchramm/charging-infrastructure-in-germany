"""Datentabelle der gefilterten Ladepunkte mit CSV-Download."""

import pandas as pd
import streamlit as st

_PREVIEW_ROWS = 1000


def _build_export_df(df_filtered: pd.DataFrame) -> pd.DataFrame:
    """Baut die kuratierte, umbenannte Spaltenauswahl fuer Anzeige und Export."""
    return pd.DataFrame(
        {
            "Betreiber": df_filtered["BetreiberBereinigt"],
            "Bundesland": df_filtered["Bundesland"],
            "Landkreis/Stadt": df_filtered["KreisKreisfreieStadt"],
            "Ort": df_filtered["Ort"],
            "PLZ": df_filtered["PLZ"],
            "Adresse": (
                df_filtered["Strasse"].fillna("") + " " + df_filtered["Hausnummer"].fillna("")
            ).str.strip(),
            "Inbetriebnahme": df_filtered["Inbetriebnahmedatum"].dt.strftime("%d.%m.%Y"),
            "Ladeleistung (kW)": df_filtered["LadeleistungInKW"],
            "Typ": df_filtered["Leistungskategorie"],
            "Steckertyp": df_filtered["Steckertyp"],
            "Art der Ladeeinrichtung": df_filtered["ArtLadeeinrichtung"],
            "Breitengrad": df_filtered["Breitengrad"],
            "Laengengrad": df_filtered["Laengengrad"],
        }
    )


@st.cache_data
def _to_csv_bytes(export_df: pd.DataFrame) -> bytes:
    """CSV mit deutschen Excel-Konventionen (Semikolon, Dezimalkomma, BOM)."""
    return export_df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def render_data_table(df_filtered: pd.DataFrame):
    """Zeigt eine Vorschau der gefilterten Ladepunkte und bietet den CSV-Download an."""
    st.header("Datentabelle")

    export_df = _build_export_df(df_filtered)
    n_total = len(export_df)

    if n_total > _PREVIEW_ROWS:
        st.caption(
            f"Zeigt die ersten {_PREVIEW_ROWS:,} von {n_total:,} gefilterten Zeilen "
            f"(Punkt als Tausendertrennzeichen). Der Download enthält alle gefilterten "
            f"Zeilen.".replace(",", ".")
        )
    else:
        st.caption(f"{n_total:,} gefilterte Zeilen.".replace(",", "."))

    st.dataframe(export_df.head(_PREVIEW_ROWS), use_container_width=True, hide_index=True)

    st.download_button(
        label="Als CSV herunterladen",
        data=_to_csv_bytes(export_df),
        file_name=f"ladeinfrastruktur_gefiltert_{pd.Timestamp.now():%Y-%m-%d}.csv",
        mime="text/csv",
    )

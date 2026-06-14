"""Laden und Vorbereiten der Daten (Ladesäulenregister, Geodaten, KBA-Bestand).

Alle Loader sind mit ``@st.cache_data(ttl=3600)`` versehen und werden somit
stündlich aufgefrischt.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import streamlit as st

from config import (
    HPC_THRESHOLD_KW,
    KAT_HPC,
    KAT_NORMAL,
    KAT_SCHNELL,
    SCHNELL_THRESHOLD_KW,
    SIMPLIFY_TOLERANCE,
    TARGET_CRS,
)

PROJECT_ROOT = Path(__file__).parent.parent

CHARGING_PARQUET = "02_data/03_computed_data/combined_ladestation_ladepunkt.parquet"
KBA_PARQUET = PROJECT_ROOT / "02_data/03_computed_data/kba_ev_bestand.parquet"
SHAPEFILE = (
    PROJECT_ROOT
    / "02_data/02_meta_data/vg250_01-01.gk3.shape.ebenen/vg250_ebenen_0101/VG250_KRS.shp"
)


def _leistungskategorie(leistung):
    """Ordnet eine Ladeleistung (kW) einer der drei Kategorien zu."""
    if leistung >= HPC_THRESHOLD_KW:
        return KAT_HPC
    elif leistung > SCHNELL_THRESHOLD_KW:
        return KAT_SCHNELL
    else:
        return KAT_NORMAL


@st.cache_data(ttl=3600)
def load_data():
    """Lädt das Ladesäulenregister und ergänzt Jahr + Leistungskategorie."""
    try:
        df = pd.read_parquet(CHARGING_PARQUET)
        df["Inbetriebnahmedatum"] = pd.to_datetime(df["Inbetriebnahmedatum"], errors="coerce")
        df["Jahr"] = df["Inbetriebnahmedatum"].dt.year
        df.dropna(subset=["Inbetriebnahmedatum", "Bundesland", "KreisKreisfreieStadt"], inplace=True)
        df["Leistungskategorie"] = df["LadeleistungInKW"].apply(_leistungskategorie)
        return df
    except FileNotFoundError:
        st.error(
            "FEHLER: Die Datei 'combined_ladestation_ladepunkt.parquet' wurde nicht "
            "gefunden. Bitte überprüfe den Pfad."
        )
        return None


@st.cache_data(ttl=3600)
def load_geodata():
    """Lädt das Kreis-Shapefile, vereinfacht die Geometrien und projiziert nach WGS84."""
    try:
        gdf = gpd.read_file(SHAPEFILE)
        gdf["geometry"] = gdf["geometry"].simplify(
            tolerance=SIMPLIFY_TOLERANCE, preserve_topology=True
        )
        gdf = gdf.to_crs(epsg=TARGET_CRS)
        for col in gdf.columns:
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)
        return gdf
    except Exception:
        return None


@st.cache_data(ttl=3600)
def load_kba_data():
    """Lädt den KBA-EV-Bestand (BEV/PHEV je Zulassungsbezirk)."""
    try:
        return pd.read_parquet(KBA_PARQUET)
    except Exception:
        return None


def load_all():
    """Lädt alle drei Datenquellen und gibt sie als Tupel zurück."""
    return load_data(), load_geodata(), load_kba_data()

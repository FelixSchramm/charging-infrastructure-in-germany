import requests
import pandas as pd
from pathlib import Path

KBA_API_URL = (
    "https://services-eu1.arcgis.com/U09msXRZoxesNntH/arcgis/rest/services/"
    "FZ%20Pkw%20mit%20Elektroantrieb%20Zulassungsbezirk/FeatureServer/0/query"
)
OUT_PATH = Path("02_data/03_computed_data/kba_ev_bestand.parquet")


def _get_latest_berichtszeitpunkt() -> str:
    r = requests.get(KBA_API_URL, params={
        "where": "1=1",
        "outFields": "Berichtszeitpunkt",
        "returnDistinctValues": "true",
        "f": "json",
    }, timeout=60)
    r.raise_for_status()
    vals = [f["attributes"]["Berichtszeitpunkt"] for f in r.json()["features"]]
    return max(vals)


def download_kba() -> pd.DataFrame:
    latest = _get_latest_berichtszeitpunkt()
    print(f"Lade KBA-Daten, Berichtszeitpunkt: {latest} ...")
    # Absolute Zählwerte werden vom KBA aus Datenschutzgründen unterdrückt (ZS = ".").
    # Stattdessen werden Prozentanteile + Pkw_insgesamt veröffentlicht, aus denen
    # wir die absoluten Bestände näherungsweise berechnen.
    r = requests.get(KBA_API_URL, params={
        "where": f"Berichtszeitpunkt='{latest}'",
        "outFields": (
            "Schluessel_Zulbz,Zulassungsbezirk,Pkw_insgesamt,"
            "Pkw_BEV_Anteil,Pkw_Plug_In_Hybrid_Anteil,Berichtszeitpunkt"
        ),
        "f": "json",
    }, timeout=60)
    r.raise_for_status()
    features = r.json()["features"]
    df = pd.DataFrame([f["attributes"] for f in features])
    print(f"  → {len(df)} Zulassungsbezirke")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "Schluessel_Zulbz": "AGS",
        "Zulassungsbezirk": "zulassungsbezirk",
        "Pkw_insgesamt": "pkw_gesamt",
        "Pkw_BEV_Anteil": "bev_anteil",
        "Pkw_Plug_In_Hybrid_Anteil": "phev_anteil",
    })
    df["AGS"] = df["AGS"].astype(str).str.zfill(5)
    df["pkw_gesamt"] = pd.to_numeric(df["pkw_gesamt"], errors="coerce").fillna(0)
    df["bev_anteil"] = pd.to_numeric(df["bev_anteil"], errors="coerce").fillna(0)
    df["phev_anteil"] = pd.to_numeric(df["phev_anteil"], errors="coerce").fillna(0)
    df["bev_bestand"] = (df["pkw_gesamt"] * df["bev_anteil"] / 100).round().astype(int)
    df["phev_bestand"] = (df["pkw_gesamt"] * df["phev_anteil"] / 100).round().astype(int)
    return df[["AGS", "zulassungsbezirk", "bev_bestand", "phev_bestand", "Berichtszeitpunkt"]].copy()


def main():
    df_raw = download_kba()
    df = transform(df_raw)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    print(f"Gespeichert: {OUT_PATH}")


if __name__ == "__main__":
    main()

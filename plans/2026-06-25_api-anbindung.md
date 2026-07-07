# Ausführplan: Ladesäulenregister-API an Repo & Dashboard anbinden

> **Hinweis (überarbeitet).** Die ursprüngliche Spezifikation beschrieb einen
> eigenständigen Agenten (`bnetza-ladestationen-agent/`) mit eigenem
> Output-File und Roh-Esri-Schema. Das ließe sich **nicht** an dieses Repo /
> Dashboard anbinden. Dieser Plan ersetzt sie durch eine Variante, die das
> bestehende Schema, die Pfade und die uv/CI-Konventionen dieses Repos
> respektiert. Verifizierte Fakten zur API siehe Abschnitt 1.

## Role & Goal
Du bist ein Expert Python Data Engineer. Schreibe ein ETL-Skript, das die
BNetzA-Ladesäulen-Daten über die **öffentliche ArcGIS-REST-API** abruft,
in das **bestehende Ladepunkt-Schema** dieses Repos transformiert und die
vorhandene Parquet-Datei überschreibt, die das Streamlit-Dashboard liest.
Das Skript läuft per GitHub-Actions-Cronjob, committet das Ergebnis und pusht.

Sauberer, robuster Code (PEP 8), sicheres Error-Handling, gleiche Sprache/
Tonalität wie die bestehenden `scripts/` (deutsche Print-/Kommentar-Texte).

---

## 1. Verifizierte API-Fakten (WICHTIG — vor Implementierung lesen)

- **Falscher Endpoint:** `https://ladestationen.api.bund.dev/query` ist **nur die
  OpenAPI-Dokumentationsseite** (GitHub Pages, liefert 404 auf `/query`).
- **Echter Endpoint (kein Token nötig, getestet):**
  ```
  https://services2.arcgis.com/jUpNdisbWqRpMo35/arcgis/rest/services/Ladesaeulen_in_Deutschland/FeatureServer/0/query
  ```
- **Standard-Esri-Parameter:** `where=1=1`, `outFields=*`, `f=json`.
- **Pagination ist Pflicht.** Der Server deckelt pro Antwort (~2.000 Features,
  `exceededTransferLimit: true`). Gesamtbestand aktuell **≈ 109.457** Datensätze.
  → Über `resultOffset` + `resultRecordCount` blättern, bis weniger als
  `resultRecordCount` Features zurückkommen bzw. `exceededTransferLimit=false`.
- **Eine Zeile = eine Ladeeinrichtung** (Station), mit bis zu 6 Steckern als
  Spalten `Steckertypen1..6` / `Nennleistung_Stecker1..6`.
- **Feldnamen (API)** nutzen Unterstriche statt Leerzeichen/Klammern, z. B.:
  | API-Feld | Bedeutung |
  |---|---|
  | `Ladeeinrichtungs_ID` | Stations-ID |
  | `Betreiber`, `Straße`, `Hausnummer`, `Adresszusatz`, `Postleitzahl`, `Ort` | Adresse |
  | `Bundesland`, `Kreis_kreisfreie_Stadt` | Gebiet |
  | `Breitengrad`, `Längengrad` | WGS84-Koordinaten (als float) |
  | `Inbetriebnahmedatum` | **Epoch-Millisekunden** (z. B. `1578700800000`) |
  | `Nennleistung_Ladeeinrichtung__kW_` | Nennleistung gesamt |
  | `Art_der_Ladeeinrichtung` | Normal-/Schnellladeeinrichtung |
  | `Anzahl_Ladepunkte` | Anzahl Ladepunkte |
  | `Steckertypen1..6`, `Nennleistung_Stecker1..6` | je Stecker-Slot |
- **Geometrie** kommt in Web-Mercator (EPSG:3857) → **ignorieren**, stattdessen
  die WGS84-Attribute `Breitengrad`/`Längengrad` verwenden (so erwartet es
  `add_ags`).

---

## 2. Ziel-Schema (das Dashboard liest dieses und NICHTS anderes)

Output **muss** das vorhandene Format reproduzieren:
- **Pfad:** `02_data/03_computed_data/combined_ladestation_ladepunkt.parquet`
  (NICHT `data/ladesaeulen_aktuell.parquet`).
- **Granularität:** ge-meltet auf **Ladepunkt-Ebene** (eine Zeile pro Stecker).
- **Spalten:** `ladestation_id, Betreiber, BetreiberBereinigt, Strasse,
  Hausnummer, Adresszusatz, PLZ, Ort, Bundesland, KreisKreisfreieStadt,
  Breitengrad, Laengengrad, Inbetriebnahmedatum, InstallierteLadeleistungNLL,
  NennleistungBNetzA, ArtLadeeinrichtung, AnzahlLadepunkteBNetzA, Steckertyp,
  LadeleistungInKW, LadeUseCase, ladepunkt_id, ARS`.

`data_loading.load_data()` filtert anschließend auf vorhandenes
`Inbetriebnahmedatum`, `Bundesland`, `KreisKreisfreieStadt` und leitet `Jahr`
und `Leistungskategorie` aus `LadeleistungInKW` ab.

---

## 3. Strategie: bestehende Transformations-Logik wiederverwenden

`scripts/update_data.py` enthält bereits erprobte Funktionen `transform()` und
`add_ags()`, die genau das Ziel-Schema erzeugen. **Nicht neu erfinden** — nur
die Datenquelle tauschen:

1. **Fetch** (API, paginiert) → DataFrame mit API-Feldnamen.
2. **Normalisieren:** API-Felder auf die XLSX-Spaltennamen umbenennen, die
   `transform()` erwartet, und `Inbetriebnahmedatum` aus Epoch-ms in datetime
   wandeln (`pd.to_datetime(col, unit="ms")`).
3. `transform()` und `add_ags()` **unverändert** aufrufen.
4. Parquet + `_data_version.py` schreiben (wie `update_data.py:main`).

Rename-Mapping API → erwartete Spaltennamen:
```python
RENAME = {
    "Ladeeinrichtungs_ID": "Ladeeinrichtungs-ID",
    "Kreis_kreisfreie_Stadt": "Kreis/kreisfreie Stadt",
    "Nennleistung_Ladeeinrichtung__kW_": "Nennleistung Ladeeinrichtung [kW]",
    "Art_der_Ladeeinrichtung": "Art der Ladeeinrichtung",
    "Anzahl_Ladepunkte": "Anzahl Ladepunkte",
    **{f"Nennleistung_Stecker{i}": f"Nennleistung Stecker{i}" for i in range(1, 7)},
    # Steckertypen1..6, Betreiber, Straße, Hausnummer, Adresszusatz,
    # Postleitzahl, Ort, Bundesland, Breitengrad, Längengrad heißen identisch.
}
```

---

## 4. Datei-Struktur (in DIESES Repo integriert)

Kein separates Sub-Repo. Neue/angepasste Dateien:
```text
scripts/update_data_api.py        # neuer API-Loader (ersetzt XLSX-Quelle)
.github/workflows/update_data_api.yml   # täglicher Cron, oder bestehendes update_data.yml umstellen
```
`transform()`, `add_ags()`, `_to_float()` werden aus `update_data.py`
importiert oder dorthin als gemeinsames Modul ausgelagert (`scripts/_common.py`),
um Duplizierung zu vermeiden.

---

## 5. `scripts/update_data_api.py` — Anforderungen

- **Konstanten:**
  ```python
  API_URL = "https://services2.arcgis.com/jUpNdisbWqRpMo35/arcgis/rest/services/Ladesaeulen_in_Deutschland/FeatureServer/0/query"
  PAGE_SIZE = 2000
  OUT_PATH = Path("02_data/03_computed_data/combined_ladestation_ladepunkt.parquet")
  VERSION_PATH = Path("01_app/_data_version.py")
  ```
- **`fetch_all() -> pd.DataFrame`:** `requests.get` mit `timeout=60` und Retry
  (z. B. 3 Versuche mit Backoff). Schleife über `resultOffset += PAGE_SIZE`,
  Params `where=1=1, outFields=*, f=json, returnGeometry=false,
  resultOffset, resultRecordCount=PAGE_SIZE`. Abbruch, wenn `features` leer
  oder `exceededTransferLimit` fehlt/false. Attribute jedes Features einsammeln,
  in DataFrame wandeln. `requests.exceptions.RequestException` sauber loggen.
- **`normalize(df) -> df`:** `RENAME` anwenden;
  `Inbetriebnahmedatum = pd.to_datetime(df["Inbetriebnahmedatum"], unit="ms")`;
  Stecker-/Nennleistungs-Spalten als `str` belassen (`_to_float`/`transform`
  übernehmen den Rest).
- **`main()`:** `fetch_all` → `normalize` → `transform` → `add_ags` →
  `to_parquet(OUT_PATH, index=False)`; danach
  `VERSION_PATH.write_text(f'LAST_UPDATED = "{date.today():%Y-%m-%d}"\n')`
  (die API hat kein Datum im Dateinamen → heutiges Datum als Datenstand).
- **Robustheit:** Pflicht-Spalten nach `fetch_all` prüfen; bei < ~50.000
  Datensätzen Fehler werfen (Schutz vor Teil-/Leer-Antworten, die sonst gute
  Daten überschreiben).
- Globales `try/except` mit Logging; `sys.exit(1)` bei Fehler, damit der
  CI-Step rot wird und KEIN kaputtes Parquet committet wird.

## 6. Logging
Standard-`logging`: `StreamHandler` → `sys.stdout` (sichtbar im Action-Log)
+ optional `FileHandler` (`logs/agent.log`). Format
`%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
(Die bestehenden Skripte nutzen `print`; `logging` ist hier ein Upgrade — bei
Wunsch nach Konsistenz stattdessen `print` beibehalten.)

## 7. GitHub Actions (`.github/workflows/update_data_api.yml`)
An die **vorhandene** `update_data.yml` angelehnt (uv, nicht pip):
- Trigger: `cron: '0 4 * * *'` (täglich 04:00 UTC) + `workflow_dispatch`.
- `runs-on: ubuntu-latest`, `permissions: contents: write`.
- Steps: `actions/checkout@v4` → `astral-sh/setup-uv@v5` (python 3.12) →
  `uv sync` → `uv run python scripts/update_data_api.py`.
- Commit-Step wie in `update_data.yml`: `combined_ladestation_ladepunkt.parquet`
  **und** `01_app/_data_version.py` adden, `git diff --staged --quiet ||
  git commit`, `git pull --rebase origin main`, `git push`.
- **Entscheidung treffen:** Daily-API-Workflow *zusätzlich* zur monatlichen
  XLSX-Pipeline ist Konflikt-anfällig (beide schreiben dieselbe Datei). Empfohlen:
  die monatliche `update_data.yml` **deaktivieren/ersetzen**, sobald die
  API-Pipeline verifiziert ist. (Commit-Messages ohne AI-Attribution, s. CLAUDE.md.)

## 8. Dependencies
Bereits in `pyproject.toml` vorhanden (`requests`, `pandas`, `geopandas`,
`pyarrow`). Kein neues `requirements.txt` — `uv sync` nutzen.

---

## 9. Akzeptanzkriterien
- [ ] `uv run python scripts/update_data_api.py` zieht alle ~109k Stationen
      (Pagination greift), nicht nur 2.000.
- [ ] Output-Parquet hat exakt die Spalten aus Abschnitt 2.
- [ ] `uv run streamlit run 01_app/app.py` lädt ohne Fehler; KPIs, Zeitreihe,
      Karte zeigen plausible Werte.
- [ ] `01_app/_data_version.py` enthält das heutige Datum.
- [ ] Bei API-Fehler/Teil-Antwort bricht das Skript ab, ohne die alte Datei zu
      überschreiben.

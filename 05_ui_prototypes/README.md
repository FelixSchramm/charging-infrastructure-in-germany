# UI-Prototypen

Für die Frontend-Entscheidung in #31 entsteht hier je Framework ein Entwurf der
ersten Dashboard-Seite ("Überblick"). Alle Entwürfe lesen dieselben zwei
CSV-Dateien aus `_shared/`, damit sie dieselben Zahlen zeigen.

## Struktur

```
05_ui_prototypes/
  _shared/                         Datenaufbereitung (DuckDB-SQL)
  a_streamlit/streamlit_theme/
  b_python_server/dash/  shiny/  panel/  reflex/  nicegui/  solara/
  c_static/observable/  evidence/  quarto/
  d_custom_frontend/react/
```

## Daten erzeugen

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
```

Funktioniert aus jedem Arbeitsverzeichnis. Das Skript führt `overview.sql` und
`meta.sql` auf den committeten Parquet-Dateien aus und schreibt
`_shared/data/overview.csv` und `_shared/data/meta.csv`. Die CSV-Dateien sind
gitignored und werden in jeder Sitzung neu erzeugt (sonst veralten sie nach dem
täglichen Daten-Update). Am Ende gibt das Skript die Soll-KPIs für zwei
Referenzfälle aus: ohne Filter sowie Bayern mit nur HPC.

### `overview.csv`

Eine Zeile je (`bundesland`, `jahr`, `has_hpc`, `has_schnell`, `has_normal`).

| Spalte | Typ | Bedeutung |
|---|---|---|
| `bundesland` | Text | Bundesland |
| `jahr` | Ganzzahl | Inbetriebnahmejahr der Stationen |
| `has_hpc`, `has_schnell`, `has_normal` | Boolean | Station hat mindestens einen Ladepunkt dieser Kategorie |
| `stationen` | Ganzzahl | Anzahl Stationen |
| `kw` | Dezimalzahl | Summe `InstallierteLadeleistungNLL` dieser Stationen |
| `lp_hpc`, `lp_schnell`, `lp_normal` | Ganzzahl | Anzahl Ladepunkte je Kategorie |

Kategorien nach `LadeleistungInKW`: `>= 150` HPC, `> 22` Schnellladen, sonst
Normalladen (auch bei fehlender Leistung).

### `meta.csv`

Eine Zeile: `bnetza_stand` (`TT.MM.JJJJ`), `kba_stand` (`MM/JJJJ`), `update`
(`LAST_UPDATED` aus `01_app/_data_version.py`).

## Rechenlogik

Mit B = gewähltes Bundesland und S = gewählte Leistungstypen (Teilmenge von
`hpc`, `schnell`, `normal`):

- Zeilen auf `bundesland = B` filtern (bei "Alle Bundesländer" nicht filtern).
- **Ladestationen** = Summe `stationen` über die Zeilen, in denen mindestens ein
  `has_k` mit k in S wahr ist.
- **Gesamtleistung** = Summe `kw` über dieselben Zeilen, geteilt durch 1.000.000
  (GW).
- **Ladepunkte** = Summe von `lp_k` über alle Zeilen und alle k in S.
- **HPC-Ladepunkte** = Summe `lp_hpc`, wenn `hpc` in S ist, sonst 0.
- **Zubau gesamt** = je `jahr` ab 2010 die Summe von `lp_k` für k in S.
- **Zubau nach Leistungstyp** = je `jahr` ab 2010 und je k in S die Summe `lp_k`.

Die `has_*`-Kombination ist nötig, weil eine Station Ladepunkte mehrerer
Kategorien haben kann; Stationen und Leistung lassen sich nicht über Kategorien
addieren. So bleibt jede Filterauswahl exakt und entspricht der App
(`01_app/sections/kpis.py`, `timeseries.py`).

## Regeln für alle Prototypen

- Keine Änderungen an `01_app/`, `02_data/`, `scripts/`, der Root-`pyproject.toml`
  oder `uv.lock`. Streamlit Cloud installiert aus diesen Dateien.
- Abhängigkeiten nur im Prototyp-Ordner. Python: `requirements.txt`, Start mit
  `uv run --no-project --with-requirements requirements.txt …`. JavaScript:
  eigene `package.json`.
- Erzeugte Dateien (Builds, `node_modules/`, kopierte Daten) gitignoren.
- SQL im DuckDB-Dialekt, formatiert mit `uvx sqlfluff format --dialect duckdb <datei>`.

## Warum nicht jede Option aus #31 einen Prototyp bekommt

- Gradio und Mesop sind für ML-Demos gebaut.
- Superset und Metabase brauchen Server und Datenbank.
- Looker Studio, Datawrapper und Flourish sind Web-Tools ohne Code im Repo.

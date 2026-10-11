# Überblick-Entwurf: Reflex

Entwurf der Seite "Überblick" für #31, umgesetzt mit Reflex 0.10 (Radix Themes,
Komponenten `rx.card`, `rx.select`, `rx.checkbox`, `rx.grid`), Diagramme mit
`rx.recharts` (Recharts 3).

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/reflex
uv run --no-project --with-requirements requirements.txt reflex run
```

Der erste Start baut das Frontend und lädt dafür Bun- und Node-Pakete (dauert
etwas). Die Seite läuft unter http://localhost:3000, das Backend auf Port 8000.

## Aufbau

`rxconfig.py` setzt App-Name und Theme (`RadixThemesPlugin`). `overview/overview.py`
liest `overview.csv` und `meta.csv` aus `../../_shared/data/`; die Klasse
`OverviewState` hält die Filter und rechnet in den berechneten Variablen `kpis`
und `yearly` nach der Rechenlogik in `05_ui_prototypes/README.md`. Die Funktionen
darunter bauen Kopfzeile, Filterkarte, KPI-Karten und die zwei Diagramme.
`screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

## Eindruck

Stärken:

- Klare Trennung von Zustand (`rx.State` mit berechneten Variablen) und
  Oberfläche; Filterlogik ist normales Python mit pandas.
- Radix Themes sieht ohne eigenes CSS modern aus (Karten, Select, Checkboxen,
  Callout); Responsivität über `rx.breakpoints` direkt an den Props.
- Echtes React/Next.js-Frontend: schnelle Interaktion im Browser, Recharts-Diagramme
  mit Tooltip und Legende.

Schwächen:

- Schwerster Start aller Python-Entwürfe: der erste `reflex run` lädt Bun und
  Node-Pakete und kompiliert ein Frontend; Hosting braucht Frontend und
  Python-Backend mit Websocket. Streamlit Cloud entfällt.
- Schnelle API-Wechsel: `App(theme=...)` ist seit 0.9 veraltet (Theme jetzt als
  Plugin in `rxconfig.py`), das Sitemap-Plugin warnt, bis es abgeschaltet ist.
- Fallen bei Props: `gap="4"` landet als ungültiges CSS im Style, richtig ist
  `spacing="4"`; `rx.checkbox_group` hat kein Change-Event, daher einzelne
  Checkboxen.
- Radix kennt nur benannte Farbskalen; NOW-Grün geht nur über die CSS-Variable
  `--accent-9`. Recharts 3 sortiert die Legende alphabetisch und färbt die
  Beschriftung in Serienfarbe; beides braucht kleine JavaScript-/CSS-Eingriffe.

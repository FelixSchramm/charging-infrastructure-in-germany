# Überblick-Entwurf: Evidence

Entwurf der Seite "Überblick" für #31, umgesetzt mit Evidence (Open-Source-Version
40, `@evidence-dev/evidence`). Das Ergebnis ist eine statische Seite ohne Server:
Die SQL-Abfragen laufen im Browser in DuckDB-Wasm.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/c_static/evidence
npm install && npm run sources && npm run dev
```

Die Seite läuft unter http://localhost:3000. Statischer Build nach `build/`:

```bash
npm run build
```

`npm run sources` muss nach jedem `prepare_data.py` erneut laufen, sonst zeigt
die Seite alte Zahlen.

## Aufbau

`pages/index.md` ist die ganze Seite: Markdown mit SQL-Blöcken (DuckDB), die die
Rechenlogik aus `05_ui_prototypes/README.md` umsetzen, dazu `<Dropdown>`,
`<BigValue>` und `<BarChart>`. `copy_data.js` kopiert vor `npm run sources` die
beiden CSV-Dateien aus `../../_shared/data/` (Pfad relativ zum Skript) nach
`sources/shared/`, wo die CSV-Quelle (`connection.yaml`) sie einliest.
`pages/+layout.svelte` blendet Seitenleiste, Breadcrumbs und Abfrage-Ansichten
aus, `evidence.config.yaml` setzt Farben und helles Theme. `screenshots/` zeigt
den Stand bei 1440 px und 390 px Breite (statischer Build).

## Eindruck

Stärken:

- Sehr wenig Code (rund 130 Zeilen Seite), die Rechenlogik ist reines SQL.
  Für ein SQL-affines Team die kürzeste Variante.
- Statische Seite ohne Server, Hosting auf GitHub Pages oder jedem Webspace.
- Filter, KPIs und Diagramme sind fertige Komponenten mit einheitlicher,
  moderner Optik; auf Handybreite brechen `Grid` und Filter sauber um.
- Abfragen bauen aufeinander auf (`${filtered}`) und rechnen bei Filteränderung
  automatisch neu, ohne Callbacks.

Schwächen:

- Die offizielle Vorlage (`npx degit evidence-dev/template`) zeigt inzwischen
  auf "Evidence Studio" (gehostet, eigenes CLI mit Login, ClickHouse-SQL). Die
  Open-Source-Version kommt nur noch über den Zweig `legacy`
  (`npx degit evidence-dev/template#legacy`); ihre Zukunft ist unklar.
- Zahlenformate sind nur englisch (`1,234.5`). Die deutschen KPI-Werte werden
  deshalb in SQL als Text erzeugt; die Diagrammachsen bleiben englisch
  formatiert (`40.00k`, `40,000`).
- Eine leere Mehrfachauswahl liefert eine leere Unterabfrage statt `()`; die
  Abfragen mussten darauf umgebaut werden.
- Wenig Kontrolle über Details: Mit `xType="category"` werden die Jahreszahlen
  gekürzt, mit numerischer Achse reicht das Gesamt-Diagramm von 2007 bis 2028.
- Großer Node-Stack (rund 840 npm-Pakete, ein Peer-Konflikt mit TypeScript 7
  musste per `overrides` gelöst werden), der Build dauert rund 40 Sekunden.

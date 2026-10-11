# Überblick-Entwurf: React + Vite (eigenes Frontend)

Entwurf der Seite "Überblick" für #31, umgesetzt als eigenes Frontend mit React
und Vite. Diagramme mit Apache ECharts, CSV-Parsing mit `d3-dsv`, Styling mit
eigenem CSS. Das Ergebnis ist eine statische Seite ohne Server: Die Rechenlogik
läuft als reines JavaScript im Browser.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/d_custom_frontend/react
npm install && npm run dev
```

Die Seite läuft unter http://localhost:5173. Statischer Build nach `dist/`
(ansehen mit `npm run preview`):

```bash
npm run build
```

## Aufbau

`src/overview.js` setzt die Rechenlogik aus `05_ui_prototypes/README.md` um,
`src/App.jsx` ist die Seite (Kopf, Filter, KPI-Karten, Diagramme) und
`src/BarChart.jsx` ein kleiner Wrapper um ECharts. `copy_data.js` kopiert vor
`npm run dev` und `npm run build` (`predev`/`prebuild`) die beiden CSV-Dateien
aus `../../_shared/data/` (Pfad relativ zum Skript) nach `public/data/`, das
Design steckt in `src/styles.css`. `screenshots/` zeigt den Stand bei 1440 px
und 390 px Breite (statischer Build).

## Eindruck

Stärken:

- Volle Kontrolle über Layout, Bedienung und Optik: Filter als Chips, KPI-Karten
  und das Umbrechen auf Handybreite sind genau so, wie man sie haben will.
- Deutsche Zahlenformate ohne Umwege über `Intl.NumberFormat("de-DE")`, auch in
  Achsen und Tooltips der Diagramme.
- Statische Seite ohne Server, Hosting auf GitHub Pages oder jedem Webspace.
  Kleiner Stack (rund 75 npm-Pakete), der Build dauert wenige Sekunden.
- Die Rechenlogik ist eine kleine, testbare JavaScript-Funktion.

Schwächen:

- Am meisten selbst geschriebener Code (rund 250 Zeilen JavaScript plus rund 190 Zeilen CSS):
  Laden der Daten, Formatierung, Diagramm-Wrapper und Responsive-Design muss man
  selbst bauen. Es gibt keine fertigen Dashboard-Komponenten.
- Das Team braucht JavaScript/React-Kenntnisse; die Datenaufbereitung bleibt in
  Python, die Logik der Seite liegt dann in einer zweiten Sprache.
- Das ECharts-Bundle ist groß (rund 1,2 MB, gzip rund 390 kB, Vite warnt beim
  Build). Mit gezielten Importen aus `echarts/core` ließe sich das verkleinern,
  kostet aber zusätzlichen Code.
- Für jede weitere Seite (Karte, Analysen) fällt wieder eigener Code an; eine
  Karte bräuchte z. B. zusätzlich Leaflet oder MapLibre.

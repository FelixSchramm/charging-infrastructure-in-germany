# Überblick-Entwurf: Observable Framework

Entwurf der Seite "Überblick" für #31, umgesetzt mit Observable Framework 1.13
und Observable Plot. Das Ergebnis ist eine statische Seite ohne Server: Die
Filter laufen im Browser.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/c_static/observable
npm install && npm run dev
```

Die Seite läuft unter http://127.0.0.1:3000. Statischer Build nach `dist/`:

```bash
npm run build
```

## Aufbau

`src/index.md` ist die ganze Seite: Markdown mit JavaScript-Blöcken, die die
Rechenlogik aus `05_ui_prototypes/README.md` umsetzen und Filter (`Inputs`),
KPI-Karten (`grid`/`card`) und zwei Plot-Diagramme ausgeben. Die Data Loader
`src/data/overview.csv.js` und `src/data/meta.csv.js` geben die CSV-Dateien aus
`../../_shared/data/` aus (Pfad relativ zur Loader-Datei); Framework speichert
das Ergebnis im Cache und kopiert es beim Build in `dist/`.
`observablehq.config.js` setzt Theme (`air`, `wide`) und blendet Seitenleiste,
Pager und Footer aus. `screenshots/` zeigt den Stand bei 1440 px und 390 px
Breite.

## Eindruck

Stärken:

- Statische Seite ohne Server, Hosting auf GitHub Pages oder jedem Webspace.
- Wenig Code (rund 100 Zeilen Seite plus zwei Loader mit je 5 Zeilen), nur eine
  Sprache (JavaScript in Markdown).
- Reaktiv wie eine Tabellenkalkulation: Jeder Block rechnet neu, wenn sich ein
  Filter ändert, ohne Callbacks. Ein leerer Filter ist ein einfaches `? :`.
- `grid`/`card` und die Themes sehen ohne eigenes CSS modern aus und brechen auf
  Handybreite sauber auf eine Spalte um. `resize()` passt die Diagramme an die
  Kartenbreite an.
- Data Loader in beliebiger Sprache, Ergebnis wird gecacht; der Build ist in
  wenigen Sekunden fertig, `npm run dev` lädt bei Änderungen sofort neu.

Schwächen:

- Node.js-Werkzeugkette nötig (`npm install`), für ein Python-Team ein
  zusätzlicher Stack.
- Daten liegen vollständig im Browser; für große Rohdaten bräuchte es eine
  Voraggregation (hier durch `prepare_data.py` gegeben) oder DuckDB-Wasm.
- Der Loader-Cache wird nur neu gebaut, wenn sich die Loader-Datei ändert, nicht
  wenn sich die CSV ändert: Nach `prepare_data.py` muss
  `src/.observablehq/cache/` gelöscht werden, sonst zeigt die Seite alte Zahlen.
- Filter in Karten zu legen braucht `Generators.input` statt des einfachen
  `view()`, weil `view()` das Eingabefeld an Ort und Stelle ausgibt.
- Mehrseitige Apps mit gemeinsamem Zustand zwischen Seiten sind nicht
  vorgesehen; jede Seite ist für sich.

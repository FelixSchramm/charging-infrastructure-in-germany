# Überblick-Entwurf: Quarto Dashboard

Entwurf der Seite "Überblick" für #31, umgesetzt als Quarto Dashboard
(Quarto 1.10) mit Observable JS und Observable Plot. Das Ergebnis ist eine
statische Seite ohne Server: Die Filter laufen im Browser.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/c_static/quarto
uv run --no-project --with-requirements requirements.txt quarto preview index.qmd --no-browser --port 4200
```

Die Seite läuft unter http://localhost:4200. Statischer Build (erzeugt
`index.html` und `index_files/`):

```bash
uv run --no-project --with-requirements requirements.txt quarto render index.qmd
```

## Aufbau

`index.qmd` ist die ganze Seite: Eine Python-Zelle liest `overview.csv` und
`meta.csv` aus `../../_shared/data/` und reicht sie per `ojs_define` an Observable
JS weiter. Eine OJS-Zelle setzt die Rechenlogik aus `05_ui_prototypes/README.md`
um; Filter (`Inputs`), Value Boxes (Markdown mit `${…}`) und zwei Plot-Diagramme
reagieren darauf. `theme.scss` setzt die Farben über Bootstrap-Variablen auf dem
Bootswatch-Theme `cosmo`. `screenshots/` zeigt den Stand bei 1440 px und 390 px
Breite.

## Eindruck

Stärken:

- Statische Seite ohne Server: Hosting auf GitHub Pages oder jedem Webspace,
  die Daten stecken im HTML.
- Wenig Code (rund 130 Zeilen inklusive Layout); Seitenleiste, Value Boxes,
  Karten mit Vollbild-Knopf und das Umbrechen auf Handybreite kommen von Quarto.
- Layout in Markdown über Überschriften (`## Column`, `### Row`) und
  Höhenangaben, Theme über SCSS-Variablen.
- Observable JS ist reaktiv wie eine Tabellenkalkulation: Jede Zelle rechnet
  neu, wenn sich ein Filter ändert, ohne Callbacks.

Schwächen:

- Zwei Sprachen in einer Datei: Python nur zum Laden, die eigentliche Logik in
  JavaScript (OJS), dazu Quarto-eigene Syntax.
- Fehlersuche ist mühsam: Eine Zelle mit `kpis = ({a: 1, b: 2})` wurde in
  Quarto 1.10 ohne Fehlermeldung verworfen, sichtbar nur als "kpis is not
  defined" an anderer Stelle. Lösung: Blockform `kpis = { return {...} }`.
- Value Boxes sind für statische Werte gedacht. Dynamische Werte gehen nur über
  `${…}` im Markdown, und dort scheiterten Ausdrücke mit Anführungszeichen; die
  Texte werden deshalb in der OJS-Zelle fertig formatiert.
- Kein eingebautes Ein- und Ausblenden von Bereichen: Der Hinweis bei leerer
  Auswahl braucht eine CSS-Klasse am `body`, die eine OJS-Zelle setzt.
- `scrolling: true` ließ die Diagramme endlos wachsen (Plot übernimmt die
  Kartenhöhe); die Diagramme haben deshalb eine feste Höhe von 420 px.
- Auf dem Handy ist die Seitenleiste eingeklappt, die Filter öffnen sich über
  den Pfeil oben links.
- Jeder Build startet einen Jupyter-Kernel und dauert rund 15 Sekunden.

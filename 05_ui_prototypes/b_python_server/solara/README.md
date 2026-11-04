# Überblick-Entwurf: Solara

Entwurf der Seite "Überblick" für #31, umgesetzt mit Solara 1.64 (`AppLayout`,
`Sidebar`, `Card`, Vuetify-Theme), Diagramme über `solara.FigurePlotly`.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/solara
uv run --no-project --with-requirements requirements.txt solara run app.py
```

Die Seite läuft unter http://localhost:8765.

## Aufbau

`app.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/`. Die Filter
sind zwei `solara.reactive`-Werte in der Seitenleiste; die Komponente `Content`
rechnet daraus nach der Rechenlogik in `05_ui_prototypes/README.md` die vier KPIs
und zwei Diagramme und rendert sie bei jeder Änderung neu. Die Komponente `Layout`
setzt das `AppLayout` (Kopfzeile in Dunkelblau), `Page` setzt die Theme-Farben.
`screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

## Eindruck

Stärken:

- Kurzer, gut lesbarer Code (rund 170 Zeilen) im React-Stil: Komponenten sind
  Python-Funktionen, `solara.reactive` ersetzt Callbacks. Der Hinweis bei leerer
  Auswahl ist ein einfaches `if` mit frühem `return`.
- `AppLayout` liefert Kopfzeile, Seitenleiste und Menü-Button; auf dem Handy wird
  die Seitenleiste ohne eigenes CSS zur einklappbaren Schublade.
- Material-Design über Vuetify: Karten, Auswahlfelder und Hinweis wirken modern,
  `ColumnsResponsive` bricht KPIs und Karten je Breakpoint um.
- Theme-Farben (`primary`, `secondary`) über `solara.lab.theme` in zwei Zeilen.

Schwächen:

- Versionsfallen: Solara 1.64 zieht ipyvuetify 3 (Vuetify 3); damit überdeckt die
  Seitenleiste den Inhalt und die Kopfzeile verschwindet. `requirements.txt` pinnt
  deshalb `ipyvuetify<2` (Vuetify 2). `FigurePlotly` braucht zusätzlich
  `anywidget`, das nicht als Abhängigkeit mitkommt.
- `FigurePlotly` zeichnet ein Diagramm einmal mit 700 px Breite und passt es nie
  an den Container an. Ein kleines eingebettetes Vue-Skript (`RESIZE_CHARTS`)
  ruft deshalb `Plotly.Plots.resize` auf, sobald sich ein Container ändert.
- Theme-Farben greifen nur, wenn sie innerhalb der Seite gesetzt werden, nicht auf
  Modulebene. Ein `AppLayout` direkt in `Page` wird als "eingebettet" dargestellt;
  richtig ist die spezielle Komponente `Layout`. Beides steht nicht prominent in
  der Doku.
- Feinschliff (Hintergrund, Schriftgrößen) geht über Inline-Styles oder
  `solara.Style` mit `!important` gegen Vuetify.
- Hosting braucht einen Python-Server mit Websocket; Streamlit Cloud entfällt.
  Unten rechts steht fest "This website runs on Solara".

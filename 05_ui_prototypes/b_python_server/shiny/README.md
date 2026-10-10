# Überblick-Entwurf: Shiny for Python

Entwurf der Seite "Überblick" für #31, umgesetzt mit Shiny for Python 1.8
(Express-Syntax), Plotly über `shinywidgets` und einem `ui.Theme`.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/shiny
uv run --no-project --with-requirements requirements.txt shiny run app.py
```

Die Seite läuft unter http://localhost:8000.

## Aufbau

`app.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/`. Das Layout
ist ein `page_sidebar` mit den Filtern links, vier `value_box`-KPIs und zwei
Diagrammkarten; `reactive.calc`-Funktionen filtern die Daten nach der Rechenlogik
in `05_ui_prototypes/README.md`. Die Farben kommen aus einem `ui.Theme`
(Bootstrap-Sass-Variablen, von `libsass` beim Start kompiliert), kein eigenes
CSS. `screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

Express statt Core: Für eine einzelne Seite ist Express kürzer, weil Layout und
Ausgaben an einer Stelle stehen und keine getrennten `ui`- und `server`-Teile
nötig sind.

## Eindruck

Stärken:

- Wenig Code (rund 200 Zeilen) für ein fertig wirkendes Dashboard:
  Seitenleiste, Value Boxes und Karten mit Vollbild-Knopf kommen aus `bslib`.
- Theme über Bootstrap-Variablen (`primary`, `secondary`, `navbar_bg`, …):
  Value Boxes, Checkboxen und Kopfzeile übernehmen die Farben ohne CSS.
- Reaktives Modell: `reactive.calc` rechnet nur neu, was von einem geänderten
  Filter abhängt, ähnlich wie Dash-Callbacks, aber ohne IDs zu verdrahten.
- Responsives Verhalten ohne Zutun: `layout_column_wrap` und `layout_columns`
  brechen auf Handybreite um.

Schwächen:

- Express rendert jeden Text auf oberster Ebene in die Seite, auch einen
  Modul-Docstring; Doku muss dort als Kommentar stehen.
- Den Hinweis bei leerer Auswahl löst ein `panel_conditional` mit
  JavaScript-Bedingung, Python-seitig hält `req()` die Ausgaben an.
- Auf dem Handy steht die Seitenleiste unter dem Inhalt, die Filter sind also
  erst nach dem Scrollen erreichbar (bslib-Standard, ohne CSS nicht änderbar).
- `headings_color` färbt auch den Titel in der dunklen Kopfzeile; er braucht
  eine eigene Klasse (`text-white`).
- Plotly übernimmt das Theme nicht, Farben und Schrift stehen doppelt im Code.
  Im Headless-Browser der Cloud-Sitzung brauchten die zwei Plotly-Widgets
  mehrere Sekunden zum Neuzeichnen; lokal prüfen.
- `ui.Theme` braucht `libsass` als zusätzliche Abhängigkeit. Hosting braucht
  einen Python-Server (z. B. Posit Connect, shinyapps.io); Streamlit Cloud
  entfällt.

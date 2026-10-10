# Überblick-Entwurf: Dash + Dash Mantine Components

Entwurf der Seite "Überblick" für #31, umgesetzt mit Dash 4.4 und Dash Mantine
Components (DMC) 2.8.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/dash
uv run --no-project --with-requirements requirements.txt python app.py
```

Die Seite läuft unter http://localhost:8050.

## Aufbau

`app.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/` und baut
das Layout aus DMC-Komponenten: `AppShell` mit dunkelblauem Kopf, eine Filterkarte
(`Select`, `ChipGroup`), KPI-Karten und zwei Diagrammkarten in `SimpleGrid`s, die
auf Handybreite untereinander umbrechen. Ein Callback berechnet KPIs und
Plotly-Diagramme nach der Rechenlogik in `05_ui_prototypes/README.md`. Die Farben
kommen aus dem Mantine-Theme (`now` = Grün, `navy` = Dunkelblau, je zehn
Abstufungen), kein eigenes CSS. `screenshots/` zeigt den Stand bei 1440 px und
390 px Breite.

## Eindruck

Stärken:

- Moderne, ruhige Optik ohne CSS: Karten, Schatten, Chips und Abstände kommen
  aus Mantine, das Theme setzt Schrift, Radius und Farben an einer Stelle.
- Responsives Verhalten über Props (`cols={"base": 2, "lg": 4}`, `span`),
  ohne Media Queries.
- Callbacks berechnen nur das, was sich ändert; der Rest der Seite bleibt
  stehen (anders als der Skript-Neulauf bei Streamlit).
- Volle Plotly-Kontrolle und ein großes Komponentenangebot (DMC hat über 100
  Komponenten).

Schwächen:

- Mehr Code als Streamlit (rund 260 Zeilen), viel davon verschachtelte
  Layout-Aufrufe.
- Mantine-Farben brauchen zehn Abstufungen je Farbe; die Paletten für NOW-Grün
  und Dunkelblau sind von Hand erstellt.
- Feste Kopfhöhe der `AppShell`: Auf dem Handy bricht der Titel um, die Höhe
  muss je Breakpoint von Hand gesetzt werden.
- Plotly-Diagramme übernehmen das Mantine-Theme nicht; Schrift und Farben
  stehen doppelt im Code.
- Hosting braucht einen Python-Server (z. B. gunicorn), Streamlit Cloud entfällt.

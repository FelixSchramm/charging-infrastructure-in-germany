# Überblick-Entwurf: Streamlit (eigenes Theme)

Entwurf der Seite "Überblick" für #31, umgesetzt mit Streamlit 1.54 ohne
Frameworkwechsel. Er ist die Vergleichsbasis für alle anderen Prototypen.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten
(Streamlit liest `.streamlit/config.toml` aus dem Arbeitsverzeichnis):

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/a_streamlit/streamlit_theme
uv run --no-project --with-requirements requirements.txt streamlit run app.py
```

Die Seite läuft unter http://localhost:8501.

## Aufbau

`app.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/`, setzt die
Filter in der Seitenleiste, berechnet die KPIs nach der Rechenlogik in
`05_ui_prototypes/README.md` und zeichnet die zwei Plotly-Diagramme mit einem
eigenen Template. `.streamlit/config.toml` enthält das Theme (Schrift Inter,
Eckenradien, Rahmen, Diagrammfarben, dunkelblaue Seitenleiste über
`[theme.sidebar]`). Wenige CSS-Regeln über `st.html` gestalten die KPI-Karten.
`screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

## Eindruck

Stärken:

- Sehr wenig Code (rund 140 Zeilen). Filter, KPI-Karten, Layout und das
  responsive Umbrechen auf Handybreite gibt es ohne eigene Arbeit.
- Das Theme in Streamlit 1.54 reicht weit: Google-Font per URL, Eckenradien,
  Rahmen, Überschriftengrößen und eine eigene Farbgebung für die Seitenleiste
  sind reine Konfiguration.
- Gleiches Framework wie die heutige App: kein Umzug, kein Hosting-Wechsel,
  Streamlit Cloud bleibt nutzbar.

Schwächen:

- Feinheiten (KPI-Karten, Titelgröße auf dem Handy) brauchen CSS auf interne
  `data-testid`-Selektoren. Die können sich mit jedem Streamlit-Update ändern.
- Jede Filteränderung führt das ganze Skript erneut aus; bei der kleinen
  `overview.csv` ist das schnell, bei größeren Daten spürbar.
- Auf dem Handy liegen die Filter in der eingeklappten Seitenleiste und sind
  damit weniger sichtbar.
- Das Layout bleibt erkennbar "Streamlit" (Seitenleiste, Abstände); ein
  eigenes Seitenraster ist kaum möglich.

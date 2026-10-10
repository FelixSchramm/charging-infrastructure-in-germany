# Überblick-Entwurf: Panel (HoloViz)

Entwurf der Seite "Überblick" für #31, umgesetzt mit Panel 1.9 und dem
eingebauten `FastListTemplate`, Diagramme über das Plotly-Pane.

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/panel
uv run --no-project --with-requirements requirements.txt panel serve app.py
```

Die Seite läuft unter http://localhost:5006/app.

## Aufbau

`app.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/`. Die Filter
sind Panel-Widgets; `pn.bind(content, state, types)` baut bei jeder Änderung die
vier `pn.indicators.Number`-KPIs und zwei Diagrammkarten nach der Rechenlogik in
`05_ui_prototypes/README.md` neu. Farben kommen aus den Template-Parametern
(`accent_base_color`, `header_background`, `background_color`), dazu Inline-Styles
für die weißen Karten. `screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

Plotly statt hvPlot: Plotly ist schon in der heutigen App und in den anderen
Entwürfen im Einsatz, die Diagrammfunktion bleibt damit vergleichbar.
Deutsche Tausendertrennzeichen und gestapelte Balken mit eigener Farbe je
Kategorie gehen dort direkt (`separators`, `marker_color`); hvPlot bräuchte dafür
Bokeh-Formatter und eine Umformung ins Long-Format.

## Eindruck

Stärken:

- Kurzer Code (rund 170 Zeilen); Template, Kopfzeile und Akzentfarbe kommen aus
  `FastListTemplate` ohne eigenes CSS-Gerüst.
- `pn.bind` ist sehr direkt: eine normale Python-Funktion bekommt die
  Widget-Werte und gibt das Layout zurück, auch den Hinweis bei leerer Auswahl.
  Kein Callback-ID-Verdrahten wie bei Dash.
- Große Auswahl an Panes (Plotly, Bokeh, hvPlot, Matplotlib, …) im selben Layout.
- `FlexBox` bricht KPIs und Karten ohne Media Queries um.

Schwächen:

- Die Seitenleiste des Templates klappt auf dem Handy nicht ein und drückt den
  Inhalt aus dem Bild; die Filter stehen deshalb im Hauptbereich.
  Der Titel braucht eine CSS-Regel (`raw_css`), sonst läuft er auf 390 px über.
- `pn.indicators.Number` formatiert nur mit Pythons Format-Spezifikation, die
  keinen Punkt als Tausendertrennzeichen kennt; der Text wird vorab formatiert
  und als `format` übergeben.
- Inhalte liegen im Shadow DOM; Tests mit Playwright brauchen Locator statt
  `inner_text`, Styling geht nur über `styles`/`stylesheets` je Komponente.
- Optik wirkt eher wie ein Werkzeug als wie eine moderne Web-App; Feinschliff
  (Abstände, Kartenkopf) kostet Inline-Styles. Neuere Panel-Versionen setzen
  dafür auf `panel-material-ui` statt der eingebauten Templates.
- Hosting braucht einen Python-Server mit Websocket (Bokeh-Server);
  Streamlit Cloud entfällt.

# Überblick-Entwurf: NiceGUI

Entwurf der Seite "Überblick" für #31, umgesetzt mit NiceGUI 3.18 (Quasar-Layout
mit `ui.header`, `ui.left_drawer`, `ui.card`, `ui.select`, Tailwind-Klassen),
Diagramme nativ mit `ui.echart` (Apache ECharts).

## Start

Einmal aus dem Repo-Root die Daten erzeugen, dann aus diesem Ordner starten:

```bash
uv run python 05_ui_prototypes/_shared/prepare_data.py
cd 05_ui_prototypes/b_python_server/nicegui
uv run --no-project --with-requirements requirements.txt python main.py
```

Die Seite läuft unter http://localhost:8080.

## Aufbau

`main.py` liest `overview.csv` und `meta.csv` aus `../../_shared/data/` und
definiert die Seite als Funktion `page`. Die beiden Filter in der Seitenleiste
rufen bei jeder Änderung `content.refresh()` auf; die `@ui.refreshable`-Funktion
`content` rechnet nach der Rechenlogik in `05_ui_prototypes/README.md` die vier
KPIs und baut die ECharts-Optionen der zwei Diagramme (`bar_chart`).
`screenshots/` zeigt den Stand bei 1440 px und 390 px Breite.

## Eindruck

Stärken:

- Kurzer, direkter Code (rund 150 Zeilen) ohne Callback-Verdrahtung: Elemente
  entstehen in `with`-Blöcken, `@ui.refreshable` baut den Inhalt bei Filteränderung
  neu.
- Quasar liefert Kopfzeile, Seitenleiste und Menü-Button; auf dem Handy wird die
  Seitenleiste ohne eigenes CSS ausgeblendet und per Button eingeblendet.
- Tailwind-Klassen (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`, `rounded-xl`)
  machen Layout und Responsivität knapp und gut lesbar.
- `ui.echart` braucht keine Zusatzbibliothek; ECharts wirkt modern und schnell.
  Mehrfachauswahl mit Chips (`use-chips`) ist eine Quasar-Prop.
- Installation leicht und problemlos (keine Versionsfallen wie bei Solara).

Schwächen:

- ECharts-Optionen sind rohe Dicts ohne Typprüfung. Deutsche Zahlenformate auf
  den Achsen und im Tooltip gehen nur über JavaScript-Strings (Schlüssel mit
  führendem `:`, z. B. `":formatter"`).
- Die ECharts-Legende überlappt ohne Feineinstellung (`grid.containLabel`,
  `legend.type = "scroll"`) Achse und Balken; auf dem Handy wird sie zu einer
  blätterbaren Zeile.
- Drei Styling-Ebenen nebeneinander (Tailwind-Klassen, Quasar-Props,
  `ui.colors`), man muss wissen, welche wofür zuständig ist.
- Hosting braucht einen Python-Server mit Websocket; Streamlit Cloud entfällt.

# Umsetzungsplan: Tests für `01_app/filters.py`

**Ziel:** Die reinen DataFrame-Filterfunktionen absichern, entkoppelt von der Streamlit-Seitenleiste. `render_sidebar()` (UI) wird **nicht** getestet, wohl aber `apply_filters`, `apply_filters_for_map` und `_apply_search`.

**Datei:** `tests/test_filters.py`
**Priorität:** mittel
**Aufwand:** ~40 min, ~9–11 Tests, läuft <1 s.

---

## Voraussetzungen (einmalig, geteilt mit Plänen 2/4/5)
Siehe Plan 2: pytest als Dev-Dependency, `[tool.pytest.ini_options]` mit
`pythonpath = ["01_app", "scripts"]`, `tests/__init__.py`.

> `filters.py` importiert beim Laden `streamlit as st`, ruft aber auf Modulebene
> keine `st.*`-Funktion auf. Import in Tests ist daher unkritisch (streamlit ist installiert).

---

## Test-Fixtures

Import: `from filters import Filters, apply_filters, apply_filters_for_map, _apply_search`

**Sample-DataFrame** (Fixture `sample_df`), 1 Zeile pro Kombination, mit genau den
Spalten, die die Filter lesen:

| Bundesland | Jahr | Leistungskategorie | KreisKreisfreieStadt | BetreiberBereinigt |
|------------|------|--------------------|----------------------|--------------------|
| Bayern     | 2018 | HPC                | München              | EnBW               |
| Bayern     | 2022 | Normal             | Nürnberg             | Tesla              |
| Hessen     | 2020 | Schnell            | Frankfurt am Main    | EnBW               |
| Hessen     | 2024 | HPC                | Kassel               | Stadtwerke         |
| Berlin     | 2024 | Normal             | Berlin               | None *(Test na)*   |

**Filter-Factory** (Fixture/Helper `make_filters(**overrides)`): liefert einen
„alles durchlassend"-`Filters` als Default (volle Jahr-Range, alle Bundesländer,
alle Kategorien, leere Suchstrings) und erlaubt punktuelle Overrides pro Test.

---

## Testfälle

### `apply_filters`
| # | Test | Erwartung |
|---|------|-----------|
| 1 | **Default lässt alles durch** | `len == len(sample_df)`. |
| 2 | **Jahr-Range inklusiv (untere Grenze)** | `jahre=(2020, 2024)` → Zeile 2018 raus, 2020 bleibt drin. |
| 3 | **Jahr-Range inklusiv (obere Grenze)** | `jahre=(2018, 2022)` → 2024-Zeilen raus, 2022 bleibt. |
| 4 | **Bundesland-Filter** | `bundeslaender=["Hessen"]` → nur Hessen-Zeilen. |
| 5 | **Leistungskategorie-Filter** | `leistungstypen=["HPC"]` → nur HPC-Zeilen. |
| 6 | **UND-Verknüpfung** | `bundeslaender=["Bayern"]` + `jahre=(2020,2024)` → nur die Nürnberg/2022-Zeile. |
| 7 | **Leere Ergebnismenge** | `bundeslaender=["Saarland"]` → 0 Zeilen, kein Crash, DataFrame zurück. |

### `apply_filters_for_map` (Invariante!)
| # | Test | Erwartung |
|---|------|-----------|
| 8 | **Ignoriert Bundesland** | `bundeslaender=["Bayern"]` → Hessen/Berlin-Zeilen bleiben **trotzdem** drin (Karte ist gesamtdeutsch). Jahr/Kategorie/Suche greifen aber. |
| 9 | **Jahr/Kategorie greifen weiter** | `leistungstypen=["HPC"]` → nur HPC, unabhängig vom Bundesland. |

### `_apply_search`
| # | Test | Erwartung |
|---|------|-----------|
| 10 | **Kreis-Suche case-insensitive Teilstring** | `search_kreis="münchen"` (lower) → nur München. `search_kreis="frankfurt"` matcht „Frankfurt am Main". |
| 11 | **Betreiber-Suche** | `search_betreiber="enbw"` → die zwei EnBW-Zeilen. |
| 12 | **`na=False`-Robustheit** | `search_betreiber="x"` crasht nicht trotz `None` in `BetreiberBereinigt` (Berlin-Zeile). |
| 13 | **Leerer Suchstring = kein Filter** | `search_kreis=""` → alle Zeilen (Branch wird übersprungen). |

> Hinweis zu #10: Die Suchstrings kommen aus `render_sidebar` bereits `.lower()`-normalisiert; in Tests die Filter entsprechend mit Kleinbuchstaben befüllen, um das reale Verhalten zu spiegeln.

## Bewusst NICHT testen
- `render_sidebar()` — reine `st.sidebar.*`-Aufrufe. Wird indirekt über den Smoke-Test (Plan 5) abgedeckt.

## Definition of Done
- `uv run pytest tests/test_filters.py` grün.
- Map-Invariante (#8) explizit abgedeckt — das ist der subtilste Unterschied der beiden Filter-Funktionen.

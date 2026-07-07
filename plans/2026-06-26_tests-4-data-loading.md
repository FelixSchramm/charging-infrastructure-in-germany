# Umsetzungsplan: Tests für `01_app/data_loading.py`

**Ziel:** Die reine Klassifizierungsfunktion `_leistungskategorie()` absichern — die kW→Kategorie-Schwellen (HPC ≥ 150, Schnell > 22, sonst Normal). Klein, aber fachlich zentral (steuert Farben, Pie-Chart, Karte) und mit Grenzwerten, die leicht „off-by-one" werden.

**Datei:** `tests/test_data_loading.py`
**Priorität:** niedrig–mittel (schnell verdient)
**Aufwand:** ~15 min, ~6 Tests, läuft <1 s.

---

## Voraussetzungen (einmalig, geteilt mit Plänen 2/3/5)
Siehe Plan 2: pytest als Dev-Dependency, `[tool.pytest.ini_options]` mit
`pythonpath = ["01_app", "scripts"]`, `tests/__init__.py`.

> `data_loading.py` importiert `streamlit` + `config`. Beim Import werden nur die
> `@st.cache_data`-Dekoratoren angewandt (kein `st.set_page_config`, das steckt in
> `config.configure_page()` und wird *nicht* beim Import gerufen). Import in Tests
> ist daher unkritisch.

---

## Testfälle

Import: `from data_loading import _leistungskategorie`
Wichtig: In den Assertions die **Konstanten aus `config`** verwenden
(`KAT_HPC`, `KAT_SCHNELL`, `KAT_NORMAL`, `HPC_THRESHOLD_KW`, `SCHNELL_THRESHOLD_KW`),
nicht die String-Literale hartkodieren — sonst brechen Tests bei Label-Änderungen,
ohne dass sich die Logik geändert hat.

`from config import KAT_HPC, KAT_SCHNELL, KAT_NORMAL`

| # | Test | Eingabe → Erwartung |
|---|------|---------------------|
| 1 | **HPC-Grenze (inklusiv)** | `150` → `KAT_HPC` (`>= 150`). |
| 2 | **knapp unter HPC** | `149.9` → `KAT_SCHNELL`. |
| 3 | **Schnell-Bereich** | `23`, `50`, `99` → `KAT_SCHNELL`. |
| 4 | **Schnell-Grenze (exklusiv)** | `22` → `KAT_NORMAL` (Schwelle ist `> 22`, also ist 22 noch Normal). `22.0001` → `KAT_SCHNELL`. |
| 5 | **Normal-Bereich** | `0`, `11`, `22` → `KAT_NORMAL`. |
| 6 | **NaN-Verhalten dokumentieren** | `float("nan")` → `KAT_NORMAL` (beide Vergleiche `>=`/`>` sind mit NaN `False`, fällt in den `else`-Zweig). Fixiert das aktuelle Verhalten, damit eine spätere Änderung sichtbar wird. |

Empfehlung: Tests 1–5 als **parametrisierte** Tests (`@pytest.mark.parametrize`)
mit Tupeln `(leistung, erwartete_kategorie)` schreiben — kompakt und gut lesbar.

## Bewusst NICHT testen (in dieser Datei)
- `load_data`, `load_geodata`, `load_kba_data`, `load_all` — dünne
  `pd.read_parquet`/`gpd.read_file`-Wrapper mit `@st.cache_data` und
  Try/Except. Geringer Logik-Anteil, hoher Mock-/Fixture-Aufwand. Der reale
  Lade-Pfad wird über den Smoke-Test (Plan 5) end-to-end abgedeckt.
- Optional (später): Ein Test, dass `load_data()` bei fehlender Datei `None`
  zurückgibt — bräuchte aber Streamlit-Cache-Umgehung; nur falls nötig.

## Definition of Done
- `uv run pytest tests/test_data_loading.py` grün.
- Beide Grenzwerte (150 inklusiv, 22 exklusiv) explizit abgedeckt.

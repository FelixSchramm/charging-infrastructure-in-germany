# Umsetzungsplan: Tests für `scripts/update_data.py` (inkl. Hypothesis)

**Ziel:** Den fragilsten, unbeaufsichtigt laufenden Teil der Pipeline absichern — den
BNetzA-XLSX-Parser. Er läuft monatlich per Cron; bricht das Format, scheitert er
**still** und committet kaputte Daten. Kern ist `_to_float` (Parser) + `transform`
(Melt von 6 Steckertyp-Spalten zu Ladepunkt-Zeilen). Hier wird zusätzlich
**property-based testing mit Hypothesis** eingesetzt, weil Parser genau dessen
Paradedisziplin sind.

**Datei:** `tests/test_update_data.py`
**Priorität:** **hoch** (höchster fachlicher ROI der gesamten Test-Suite)
**Aufwand:** ~60 min, ~10–14 Tests (Beispiel + Property), läuft <2 s, kein Netzwerk.

---

## Voraussetzungen
- Geteiltes Setup aus `tests-0-setup.md` (pytest-Dev-Dep, `pythonpath = ["01_app", "scripts"]`,
  `tests/__init__.py`).
- **Zusätzliche Dev-Dependency für die Property-Tests:**
  ```bash
  uv add --dev hypothesis
  ```
- **`.gitignore`** um `.hypothesis/` ergänzen (Hypothesis legt dort seine Beispiel-DB
  / gefundene Gegenbeispiele ab — nicht einchecken).

> `scripts/update_data.py` hat beim Import keine Seiteneffekte (nur Konstanten +
> Funktionsdefinitionen). `_to_float`, `transform`, `get_xlsx_url`, `add_ags` sind
> direkt importierbar. Netzwerk-/IO-Funktionen (`download_and_parse`, `main`) werden
> nicht getestet.

Import: `from update_data import _to_float, transform, get_xlsx_url`

---

## Teil A — `_to_float` (Beispiel-Tests)

Die konkreten, dokumentierenden Fälle zuerst — sie sind beim Lesen wertvoller als
jede Property:

| # | Eingabe → Erwartung |
|---|---------------------|
| 1 | `"50.0"` → `50.0` |
| 2 | **Dezimalkomma:** `"22,5"` → `22.5` |
| 3 | **`;`-Mehrfachwert, max:** `"11; 22; 50"` → `50.0` |
| 4 | **`;` mit Komma gemischt:** `"3,7; 11,0"` → `11.0` |
| 5 | **`NaN`/None:** `pd.isna`-Input (`None`, `float("nan")`) → `math.isnan(result)` |
| 6 | **Leerer/Whitespace-`;`-Teil wird ignoriert:** `"50; "` → `50.0` (Split filtert leere Teile) |
| 7 | **Einzelwert mit Whitespace:** `" 7,4 "` → `7.4` |

## Teil B — `_to_float` (Hypothesis-Properties)

```python
from hypothesis import given, strategies as st
```

**P1 — Komma-Roundtrip (Einzelwert):**
```python
@given(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
def test_comma_roundtrip(x):
    s = f"{x}".replace(".", ",")          # Dezimalkomma wie im BNetzA-Sheet
    assert _to_float(s) == pytest.approx(x)
```

**P2 — `max`-Invariante (Mehrfachwert):** generiere eine nicht-leere Liste von
Floats, formatiere jeden mit Komma, verbinde mit `"; "` → Ergebnis ist `approx(max(werte))`
und `>= ` jedem Einzelwert.
```python
@given(st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False,
                          allow_infinity=False), min_size=1, max_size=6))
def test_semicolon_returns_max(werte):
    s = "; ".join(f"{w}".replace(".", ",") for w in werte)
    assert _to_float(s) == pytest.approx(max(werte))
```

**P3 — Totalität / kein Crash:** für „plausibel verrauschte" Eingaben (Ziffern,
Komma, Semikolon, Whitespace) wirft `_to_float` entweder ein sauberes `float`/`nan`
oder einen *erwarteten* `ValueError` — nie etwas anderes. Bewusst eng halten:
Hypothesis soll realistische Sheet-Zellen modellieren, nicht beliebigen Unicode.
```python
zelle = st.from_regex(r"[0-9]{1,4}(,[0-9]{1,2})?(; ?[0-9]{1,4}(,[0-9]{1,2})?)*",
                      fullmatch=True)
@given(zelle)
def test_parses_without_unexpected_error(s):
    result = _to_float(s)
    assert isinstance(result, float)
```

> **Designhinweis:** Strategien eng an reale BNetzA-Zellinhalte halten. Ziel ist,
> Format-Kombinationen zu finden, die man in einer Beispieltabelle vergisst —
> **nicht**, den Parser mit Müll-Unicode zu „fuzzen" (das testet keine reale
> Anforderung und produziert nur Rauschen).

## Teil C — `transform` (Beispiel-Tests, struktur-orientiert)

Kleiner synthetischer Roh-DataFrame mit den BNetzA-Spaltennamen (siehe `station_cols`
in `update_data.py`) + mind. `Steckertypen1/2` und `Nennleistung Stecker1/2`.

| # | Test | Erwartung |
|---|------|-----------|
| 8 | **Melt-Zeilenzahl** | 2 Stationen × je 2 befüllte Steckerslots → 4 Ladepunkt-Zeilen. |
| 9 | **Dropna leerer Slots** | Slot mit leerem `Steckertyp`/`LadeleistungInKW` fällt raus (kein Phantom-Ladepunkt). |
| 10 | **Spalten-Renames** | Ziel-Spalten existieren: `ladestation_id`, `Strasse`, `PLZ`, `KreisKreisfreieStadt`, `Laengengrad`, `LadeleistungInKW`, … |
| 11 | **Abgeleitete Spalten** | `ladepunkt_id` ist fortlaufend `1..n`; `BetreiberBereinigt == Betreiber`; `LadeUseCase == "Unbekannt"`. |
| 12 | **Datums-Parsing** | `Inbetriebnahmedatum` ist `datetime64`; unparsebares Datum → `NaT` (via `errors="coerce"`). |
| 13 | **`_to_float` greift in Lat/Lon** | `"48,1"` in `Breitengrad` → `48.1` (float). |

## Teil D — `get_xlsx_url` (gemockt, ohne Netzwerk)

| # | Test | Erwartung |
|---|------|-----------|
| 14 | **Link gefunden** | `monkeypatch` auf `update_data.requests.get` → Response mit HTML, das eine `…Ladesaeulenregister….xlsx`-URL enthält → Funktion liefert exakt diese URL. |
| 15 | **Link fehlt → RuntimeError** | HTML ohne passende URL → `pytest.raises(RuntimeError)`. |

> `add_ags` (räumlicher Join via Shapefile) bewusst auslassen — IO-/Geo-lastig,
> wird indirekt vom Smoke-Test (Plan 5) und der realen Pipeline abgedeckt.

## Bewusst NICHT testen
- `download_and_parse`, `main` — reines Netzwerk/IO.
- `add_ags` — Shapefile-Abhängigkeit, geringer Logik-Anteil.

## Definition of Done
- `uv add --dev hypothesis` ausgeführt, `.hypothesis/` in `.gitignore`.
- `uv run pytest tests/test_update_data.py` grün (Beispiel- **und** Property-Tests).
- `max`-Invariante und Komma-Roundtrip von `_to_float` per Hypothesis abgedeckt.
- Property-Strategien eng an realen BNetzA-Zellinhalten gehalten (kein Müll-Fuzzing).

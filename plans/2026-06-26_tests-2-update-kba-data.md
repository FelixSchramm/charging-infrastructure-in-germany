# Umsetzungsplan: Tests für `scripts/update_kba_data.py`

**Ziel:** Die reine Transformations-Funktion `transform()` absichern, ohne das ArcGIS-Netzwerk anzufassen. Das ist die fachlich heikelste Stelle des KBA-Loaders: Aus Prozentanteilen + `Pkw_insgesamt` werden absolute BEV/PHEV-Bestände *näherungsweise* berechnet (das KBA unterdrückt Absolutwerte aus Datenschutzgründen).

**Datei:** `tests/test_update_kba_data.py`
**Priorität:** mittel
**Aufwand:** ~30 min, ~6–8 Tests, läuft <1 s, kein Netzwerk.

---

## Voraussetzungen (einmalig, geteilt mit Plänen 3–5)

1. **pytest als Dev-Dependency:**
   ```bash
   uv add --dev pytest
   ```
2. **`pyproject.toml`** um pytest-Konfiguration ergänzen:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["01_app", "scripts"]
   ```
   `pythonpath` macht sowohl die App-Module (`config`, `filters`, …) als auch
   die `scripts/`-Module direkt importierbar — ohne Paket-Umbau.
3. **`tests/__init__.py`** anlegen (leer), damit der Ordner als Paket erkannt wird.

> Hinweis: `scripts/update_kba_data.py` hat beim Import keine Seiteneffekte
> (nur Konstanten + Funktionsdefinitionen). `transform()` ist daher direkt importierbar.

---

## Testfälle

Import: `from update_kba_data import transform`

Hilfs-Fixture für einen rohen Eingabe-DataFrame mit den **API-Spaltennamen**
(vor dem Rename), d. h. `Schluessel_Zulbz`, `Zulassungsbezirk`, `Pkw_insgesamt`,
`Pkw_BEV_Anteil`, `Pkw_Plug_In_Hybrid_Anteil`, `Berichtszeitpunkt`.

| # | Test | Eingabe → Erwartung |
|---|------|---------------------|
| 1 | **Spalten-Rename + Output-Schema** | Ergebnis hat exakt die Spalten `["AGS", "zulassungsbezirk", "bev_bestand", "phev_bestand", "Berichtszeitpunkt"]` in dieser Reihenfolge. |
| 2 | **BEV-Berechnung** | `Pkw_insgesamt=100000`, `Pkw_BEV_Anteil=10.0` → `bev_bestand == 10000`. |
| 3 | **PHEV-Berechnung** | `Pkw_insgesamt=100000`, `Pkw_Plug_In_Hybrid_Anteil=5.0` → `phev_bestand == 5000`. |
| 4 | **Rundung** | `Pkw_insgesamt=12345`, `Pkw_BEV_Anteil=1.0` → `round(123.45) == 123` (kaufmännisch via pandas `.round()`). Grenzfall `…=10001, anteil=1.0` → `round(100.01)=100`. |
| 5 | **AGS-zfill** | `Schluessel_Zulbz="8111"` → `AGS == "08111"` (5-stellig, führende Null). Auch numerischer Input `8111` (int) → `"08111"`. |
| 6 | **dtype** | `bev_bestand` und `phev_bestand` sind `int` (nicht float). `assert df["bev_bestand"].dtype == "int64"`. |
| 7 | **NaN-/Fehlwert-Robustheit** | `Pkw_BEV_Anteil=None`/`"."` → `fillna(0)`/`coerce` greift → `bev_bestand == 0`. `Pkw_insgesamt="."` (KBA-Suppression) → `pd.to_numeric(errors="coerce").fillna(0)` → `0`. |

## Edge Cases bewusst dokumentieren
- KBA liefert unterdrückte Werte als String `"."` — Test #7 fixiert, dass das zu `0` wird statt zu einem Crash.
- `transform()` mutiert den Eingabe-DataFrame teilweise in-place (`df.rename` gibt zwar neu zurück, die `astype`/`to_numeric`-Zuweisungen schreiben auf das umbenannte df). Im Test mit frischem Fixture pro Testfall arbeiten (kein geteilter State).

## Bewusst NICHT testen
- `_get_latest_berichtszeitpunkt()` und `download_kba()` — reine Netzwerk-/IO-Funktionen. Optional ein Test mit gemocktem `requests.get` (via `monkeypatch`), der prüft, dass `max(vals)` den jüngsten Berichtszeitpunkt zieht — aber niedrige Priorität.
- `main()` — schreibt Parquet auf Platte; kein Testwert.

## Definition of Done
- `uv run pytest tests/test_update_kba_data.py` grün.
- Tests laufen offline und deterministisch.

# Umsetzungsplan: Smoke-Test der App via Streamlit `AppTest`

**Ziel:** Ein einziger End-to-End-Test, der die komplette App (`01_app/app.py`) gegen die echten Parquet-Dateien einmal durchlaufen lässt und prüft, dass **keine Exception** fliegt. Deckt Verdrahtung ab, die Unit-Tests nicht sehen: Imports, `render_sidebar`, alle `sections/*`, die echten Datenpfade.

**Datei:** `tests/test_smoke.py`
**Priorität:** niedrig (hoher Abdeckungswert pro Zeile, aber abhängig von vorhandenen Datendateien)
**Aufwand:** ~30 min, 1–3 Tests, läuft ~2–5 s.

---

## Voraussetzungen (einmalig, geteilt mit Plänen 2/3/4)
Siehe Plan 2: pytest als Dev-Dependency, `[tool.pytest.ini_options]` mit
`pythonpath = ["01_app", "scripts"]`, `tests/__init__.py`.

**Zusätzlich für AppTest kritisch:**

1. **`pythonpath` muss `01_app` enthalten** (ist durch Plan 2 erfüllt). `app.py`
   nutzt flache Imports (`from config import …`, `from filters import …`), die nur
   mit `01_app` auf dem Pfad auflösen. Vgl. Memory: AppTest braucht `PYTHONPATH=01_app`.
2. **Arbeitsverzeichnis = Repo-Root.** Die App liest Parquet über Pfade relativ
   zum cwd (`02_data/03_computed_data/…`). pytest läuft per Konvention aus dem
   Repo-Root → passt. Zur Absicherung im Test einen `chdir`-Guard oder eine
   Pfadprüfung (siehe unten) ergänzen.
3. **Datendateien müssen existieren** (`combined_ladestation_ladepunkt.parquet`,
   `kba_ev_bestand.parquet`, `VG250_KRS.shp`). Sind im Repo eingecheckt → i. d. R.
   vorhanden. Test bei Fehlen sauber **skippen**, nicht failen.

---

## Test-Skizze

```python
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parent.parent
APP = REPO_ROOT / "01_app" / "app.py"
DATA = REPO_ROOT / "02_data/03_computed_data/combined_ladestation_ladepunkt.parquet"

requires_data = pytest.mark.skipif(
    not DATA.exists(), reason="Parquet-Daten nicht vorhanden (CI ohne Datenstand)"
)

@requires_data
def test_app_runs_without_exception():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
```

## Testfälle
| # | Test | Erwartung |
|---|------|-----------|
| 1 | **App läuft fehlerfrei** | `at.run()` → `at.exception` ist falsy. Kernabsicherung. |
| 2 | **Inhalt gerendert** (optional) | Mind. ein Header/KPI vorhanden, z. B. `len(at.header) > 0` oder ein erwarteter Titel-Teilstring taucht in `at.markdown`/`at.title` auf. |
| 3 | **Filter-Interaktion** (optional) | Einen Sidebar-Slider/Multiselect via AppTest setzen und erneut `run()`; weiterhin `not at.exception`. Sichert den Re-Run-Pfad mit verändertem Filterzustand ab. |

## Stolpersteine
- **`configure_page()` / `st.set_page_config`** läuft als erster App-Befehl —
  unter AppTest unproblematisch, solange `app.py` unverändert als Skript läuft.
- **Datetime-Spalten in GeoDataFrame** werden in `load_geodata` zu String gecastet;
  falls der Shapefile fehlt, gibt der Loader `None` zurück → App rendert die Karte
  ggf. eingeschränkt, sollte aber nicht crashen. Test #1 deckt das ab.
- **Laufzeit/Caching:** `@st.cache_data` greift; der erste Run lädt ~7 MB Parquet.
  `default_timeout` großzügig (30 s) setzen.
- **CI:** Wenn der Workflow ohne eingecheckte Daten läuft, greift `skipif` →
  Test wird übersprungen statt rot. In `update_data.yml` (nach dem Daten-Build)
  läuft er dagegen scharf — ideale Vorstufe vor dem Commit kaputter Daten.

## Bewusst NICHT testen
- Einzelne Plotly-/Folium-Figuren auf konkreten Inhalt — zu spröde, geringer Wert.
  Der Smoke-Test sichert „läuft durch", nicht „sieht korrekt aus".

## Definition of Done
- `uv run pytest tests/test_smoke.py` grün (oder sauber geskippt, wenn keine Daten).
- Bei vorhandenen Daten: App läuft ohne Exception durch alle Sections.

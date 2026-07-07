# Umsetzungsplan: Test-Setup & Orchestrierung (Fundament für Pläne 2–5)

**Für den nächsten Agenten.** Dieser Plan legt die einmalige pytest-Infrastruktur
an und sequenziert die vier Test-Pläne. Erst diesen Plan abarbeiten, dann die
Einzelpläne in der angegebenen Reihenfolge.

**Ziel:** Lauffähiges pytest-Setup (offline, deterministisch, <2 s ohne Smoke-Test),
sodass `uv run pytest` aus dem Repo-Root grün läuft.

**Aufwand:** ~15 min Setup + die Einzelpläne.

---

## Kontext (Repo-Stand 2026-06-26)
- Kein einziger Test existiert bisher. Kein `tests/`-Ordner, pytest ist **nicht** installiert.
- Package-Manager ist **uv** (`uv sync`, `uv run …`), Venv unter `.venv/`.
- App-Module unter `01_app/` nutzen **flache Imports** (`from config import …`),
  Pipeline-Skripte unter `scripts/`. Beide Ordner müssen auf den Importpfad.
- Die zu testenden reinen Funktionen sind bereits sauber von Streamlit entkoppelt
  (gute Architektur dafür) — Details je Einzelplan.

## Verwandte Pläne (Einzeldateien in `plans/`)
- `2026-06-26_tests-1-update-data.md` — `scripts/update_data.py::_to_float`/`transform` **(inkl. Hypothesis)**
- `2026-06-26_tests-2-update-kba-data.md` — `scripts/update_kba_data.py::transform`
- `2026-06-26_tests-3-filters.md` — `01_app/filters.py` (Filterfunktionen)
- `2026-06-26_tests-4-data-loading.md` — `01_app/data_loading.py::_leistungskategorie`
- `2026-06-26_tests-5-smoke.md` — `AppTest` end-to-end

> **Datei 1 (`test_update_data.py`)** ist fachlich die **höchste** Priorität
> (fragilster, monatlich unbeaufsichtigt laufender Cron-Pfad) und nutzt als einziger
> Plan zusätzlich **Hypothesis** (property-based testing) für den Parser `_to_float`.
> Details in `tests-1-update-data.md`.

---

## Schritt-für-Schritt

### Schritt 1 — pytest als Dev-Dependency
```bash
uv add --dev pytest
```
Legt pytest in der `[dependency-groups]`/`dev`-Gruppe der `pyproject.toml` an und
aktualisiert `uv.lock`. (Keine Laufzeit-Dependency — gehört nicht in `[project].dependencies`.)

### Schritt 2 — pytest-Konfiguration in `pyproject.toml`
Folgenden Block ergänzen:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["01_app", "scripts"]
```
- `pythonpath` (Feature von pytest ≥7) macht `config`, `filters`, `data_loading`
  **und** die `scripts/`-Module direkt importierbar — **ohne** Paket-Umbau und
  ohne `conftest.py`-Pfad-Hacks.
- Damit ist die in der Memory notierte Anforderung „AppTest braucht `PYTHONPATH=01_app`"
  für alle Tests zentral erfüllt.

### Schritt 3 — Test-Ordner anlegen
```bash
mkdir tests
```
Leere `tests/__init__.py` erstellen (markiert das Paket; verhindert
Modulnamens-Kollisionen zwischen Testdateien).

### Schritt 4 — Smoke-Verifikation der Infrastruktur
Vor den echten Tests einen Trivialtest `tests/test_setup_sanity.py` mit einem
`assert True` **und** je einem Import-Check pro Zielmodul anlegen:
```python
def test_imports_resolve():
    import config, filters, data_loading        # 01_app via pythonpath
    import update_kba_data, update_data          # scripts via pythonpath
```
```bash
uv run pytest -q
```
Erwartung: grün. Damit ist bewiesen, dass `pythonpath` korrekt greift, **bevor**
echte Tests geschrieben werden. Danach `test_setup_sanity.py` löschen oder
behalten (optional).

### Schritt 5 — Einzelpläne abarbeiten (empfohlene Reihenfolge)
Mischung aus „schneller Gewinn zuerst" und „höchster fachlicher ROI früh":
1. **Plan 4** (`test_data_loading.py`) — kleinster, schnellster Gewinn (~15 min);
   etabliert den parametrisierten Beispiel-Stil.
2. **Plan 1** (`test_update_data.py`) — höchste Priorität (fragilster Cron-Pfad);
   führt **Hypothesis** ein → vorher `uv add --dev hypothesis` und `.hypothesis/`
   in `.gitignore` (siehe Plan 1).
3. **Plan 2** (`test_update_kba_data.py`) — reine Arithmetik, kein Netzwerk.
4. **Plan 3** (`test_filters.py`) — DataFrame-Filter inkl. Map-Invariante.
5. **Plan 5** (`test_smoke.py`) — zuletzt, da abhängig von eingecheckten Parquet-Daten
   und am langsamsten.

Nach jeder Datei `uv run pytest tests/<datei>` laufen lassen, bevor zur nächsten
gegangen wird.

> **Hypothesis ist optional und nur für Plan 1 nötig.** Wer ohne property-based
> testing starten will, kann Plan 1 auf die Beispiel-Tests reduzieren und Hypothesis
> später ergänzen — die übrigen Pläne brauchen es nicht.

---

## Optionaler Folgeschritt: CI-Anbindung (separat, nach Nutzer-Freigabe)
Hoher Hebel, aber bewusst getrennt halten:
- Neuer Workflow `.github/workflows/tests.yml`, der bei Push/PR `uv sync` +
  `uv run pytest` ausführt.
- Zusätzlich den pytest-Lauf als **Vorstufe** in `.github/workflows/update_data.yml`
  einklinken (nach dem Daten-Build, vor dem Commit) — so scheitert der monatliche
  Cron-Job sichtbar, statt kaputte Daten zu committen. Das ist der eigentliche
  Schutzwert der Tests.
- **Nicht** ungefragt anlegen — erst mit dem Nutzer klären.

## Konventionen beachten
- Commit-Messages / PRs: **keine** AI-Attribution-Zeilen (siehe CLAUDE.md).
- Tests müssen offline & deterministisch sein (kein echtes Netzwerk in 2–4;
  Smoke-Test nutzt lokale Parquet und skippt sauber, wenn diese fehlen).

## Definition of Done (dieses Plans)
- `uv add --dev pytest` ausgeführt, `uv.lock` aktualisiert.
- `[tool.pytest.ini_options]` mit `pythonpath` in `pyproject.toml`.
- `tests/__init__.py` vorhanden.
- `uv run pytest` läuft grün (mind. der Sanity-Import-Test).
- Reihenfolge & offener Punkt (Datei 1) an den nächsten Schritt übergeben.

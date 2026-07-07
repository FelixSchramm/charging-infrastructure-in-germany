# CLAUDE.md

Compact project context for Claude Code. Keep this short and current.

## What this is
Streamlit dashboard visualizing Germany's public charging infrastructure
(BNetzA Ladesäulenregister + KBA EV stock). Live: https://ladeinfrastruktur-in-deutschland.streamlit.app/

## Stack & tooling
- Python >=3.12, package manager: **uv** (`uv sync`, `uv run …`). Venv: `.venv/`.
- Key deps: streamlit==1.54.0, pandas, geopandas, plotly, folium, pyarrow.

## Run
```bash
uv run streamlit run 01_app/app.py
```

## Layout
- `01_app/app.py` — schlanker Entry-Point, orchestriert nur die Abschnitte.
- `01_app/config.py` — Seiteneinstellung, Farben, Konstanten.
- `01_app/data_loading.py` — Loader (mit `@st.cache_data`).
- `01_app/filters.py` — Seitenleisten-Filter + Anwendung auf die Daten.
- `01_app/sections/` — je ein Modul pro Abschnitt (header, kpis, timeseries,
  analyses, map_view, info).
- `01_app/_data_version.py` — `LAST_UPDATED` stamp; imported by the app so a
  data commit forces a Streamlit Cloud redeploy. Overwritten by the CI workflows.
- `scripts/update_data.py` — downloads BNetzA xlsx, writes the parquet.
- `scripts/update_kba_data.py` — updates the KBA EV-stock parquet.
- `02_data/03_computed_data/combined_ladestation_ladepunkt.parquet` — main data (~7 MB).
- `02_data/03_computed_data/kba_ev_bestand.parquet` — KBA EV stock.
- `02_data/02_meta_data/…/VG250_KRS.shp` — district shapefile for spatial join.

## Data pipeline (GitHub Actions)
- `.github/workflows/update_data.yml` — monthly (1st, 06:00 UTC), commits the
  charging parquet + `_data_version.py`.
- `.github/workflows/update_kba_data.yml` — yearly (May 1), commits the KBA parquet.
- Data is committed **into the repo** (read directly by Streamlit Cloud). See the
  README note for the trade-off and possible bucket/DuckDB future steps.

## Conventions
- App reads parquet via paths relative to repo root (cwd), e.g.
  `pd.read_parquet('02_data/03_computed_data/…')`.
- `@st.cache_data(ttl=3600)` on the loaders — refreshes hourly.
- Commit messages / PRs: no AI-attribution lines.
# AI Coding Instructions

## General Coding Standards
- Write code in English, as easy as possible and do not use emojis.
- Follow PEP 8 coding style for Python
- Variable and function names: use snake_case
- Use reStructuredText (reST) format for all Python docstrings.
- Format: Use `:param name: description` and `:return: description`.
- Python code needs to be formatted with `black`
- sql files needs to be formatted with `sqlfluff` using the "standard" style.
- sql is used with AWS Athena and Redshift, so ensure compatibility with these systems.


## Commit & Branching Conventions
- Use conventional commits (https://www.conventionalcommits.org/)
- Branch names must include Jira ticket numbers: Format "NLL-XXX-description"
- Always work with feature branches
- Pull requests must include:
  * Description with data source, background, request/results links
  * Complexity level
  * Priority/Urgency

## Documentation Requirements
- Every code needs a Markdown file
- Every function needs a docstring
- Inline comments: Focus on WHY, not WHAT

## Plans
- Implementierungs-/Ausführpläne werden **immer** im Ordner `plans/` abgelegt.
- `plans/` ist in `.gitignore` und wird **nicht** ins Repo committet (nur lokal).
- Dateiname-Format: `YYYY-MM-DD_name.md` (aktuelles Datum + kurzer Slug),
  z. B. `2026-06-25_api-anbindung.md`.

# Project Structure & Organization
- Repositories are structured by: Acquisition, ETL, Data Service, or Analysis
- Data process follows CRISP-DM methodology

## SQL Views:
- On DWH-Redshift: automatic deployment via CI/CD on dwh-application repository
- On Athena: manual execution

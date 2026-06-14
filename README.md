# Public Charging Infrastructure in Germany: Data Analysis & Dashboard

This project is an interactive dashboard application that visualizes the current state of public charging infrastructure in Germany. It was developed as a take-home task for a data analyst position at NOW GmbH.

🔗 **Link to the live application:** [https://ladeinfrastruktur-in-deutschland.streamlit.app/](https://ladeinfrastruktur-in-deutschland.streamlit.app/)

## Data Used

This project utilizes three main datasets:

1.  **Charging Infrastructure Data:** The Federal Network Agency's (BNetzA) public charging station register (*Ladesäulenregister*). The automated pipeline downloads the current XLSX directly from the [BNetzA download page](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html) and transforms it into one row per charging point (coordinates, operator, address, charging power, connector types). The original take-home version used the `ladestationFactTable.csv` / `ladepunktFactTable.csv` exports from the Mobilithek platform ([offer 842113170303512576](https://mobilithek.info/offers/842113170303512576)), which are still kept in `02_data/01_original_data/`.

2.  **EV Stock Data (KBA):** Electric-vehicle stock figures from the Federal Motor Transport Authority (Kraftfahrt-Bundesamt, KBA), used to relate charging infrastructure to the number of registered EVs.

3.  **Geospatial Data:** A Shapefile (`VG250_KRS.shp`) from the Federal Agency for Cartography and Geodesy (BKG). This data was used to visualize the German district boundaries and spatially join the charging infrastructure data for a map-based analysis.

## What Was Done

1.  **Data Integration:** The provided CSV files were processed and merged using Python and Pandas, joining them on a common `ladestation_id`.
2.  **Geospatial Join:** The aggregated charging infrastructure data was joined with the district boundary data to enable a visual representation of charging station density on a map.
3.  **Dashboard Development:** An interactive dashboard was built using Streamlit and Plotly. It allows users to visualize the charging infrastructure at the district level and apply filters (e.g., by state or charging type).

## Project Structure

The project follows a clear and professional folder structure for organization and reproducibility:
```
├── 01_app/
│   ├── app.py                     # Entry point (orchestrates the sections)
│   ├── config.py                  # Page config, colours, constants
│   ├── data_loading.py            # Cached data loaders
│   ├── filters.py                 # Sidebar filters + application
│   ├── sections/                  # One module per dashboard section
│   └── _data_version.py           # LAST_UPDATED stamp, bumped by the CI workflows
├── 02_data/
│   ├── 01_original_data/          # Original take-home CSVs from the charging register
│   │   ├── ladestationFactTable.csv
│   │   └── ladepunktFactTable.csv
│   ├── 02_meta_data/              # Geospatial data and other metadata (VG250_KRS Shapefile)
│   └── 03_computed_data/          # Processed parquet files read by the app
│       ├── combined_ladestation_ladepunkt.parquet
│       └── kba_ev_bestand.parquet
├── scripts/
│   ├── update_data.py             # Downloads BNetzA XLSX, writes the charging parquet
│   └── update_kba_data.py         # Updates the KBA EV-stock parquet
├── 03_notebooks/                  # Optional: For initial data analysis and prototyping
├── 04_documents/                  # Optional: For documentation or reports
├── .github/workflows/             # GitHub Actions data-update pipelines
├── .gitignore                     # Git configuration to ignore unwanted files
├── README.md                      # This file
├── pyproject.toml                 # Project metadata and dependencies (managed by uv)
├── uv.lock                        # Locked dependency versions
└── .streamlit/
    └── config.toml                # Streamlit configuration for app layout
```

## Automated Data Pipeline

The data is automatically updated on the **1st of every month** via a GitHub Actions workflow.

The pipeline ([`.github/workflows/update_data.yml`](.github/workflows/update_data.yml)) runs [`scripts/update_data.py`](scripts/update_data.py) and performs the following steps:

1. Scrapes the [BNetzA download page](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html) to find the current XLSX link
2. Downloads the latest charging station register (~26 MB)
3. Transforms the wide format (up to 6 connectors per row) into one row per charging point
4. Assigns district codes (AGS) via a spatial join with the shapefile
5. Saves the result as `combined_ladestation_ladepunkt.parquet` and commits it to the repository

The workflow can also be triggered manually via **GitHub Actions → Run workflow**.

> **Note — data is committed into the repo (tech-debt to revisit).**
> The pipeline commits the resulting `.parquet` files (~7 MB charging data, ~14 KB KBA data) directly into Git and pushes them. This is intentional and pragmatic for now: the files are small, updates are infrequent (monthly/yearly), and Streamlit Community Cloud reads them straight from the repo checkout — no external storage, secrets, or cost.
>
> The trade-off is that every monthly version stays in the Git history forever, so the repo (and every clone/CI run) grows over time. It's not a problem at the current size, but if the data grows larger or the history gets heavy, move the data out of Git. Best effort/value for this setup: **GitHub Releases** (app loads the `.parquet` via URL) or **Git LFS**; for larger/more frequent data, an external bucket (S3/R2/Supabase Storage) loaded at runtime.
>
> **Possible future step — DuckDB on a bucket.** Once the data lives in a bucket, [DuckDB](https://duckdb.org/) (free, open-source, runs in-process — no server or account) can query the remote `.parquet` directly via SQL without downloading the whole file, e.g. `SELECT Bundesland, COUNT(*) FROM 'https://bucket/…​.parquet' GROUP BY Bundesland`. It can also `JOIN` the BNetzA and KBA files in one query. Overkill at the current ~7 MB (pandas is fine), but a clean, serverless, zero-cost upgrade if the data is moved out of Git. The hosted variant **MotherDuck** has a free tier but adds an account/token — not needed for this project's size.

## How to Run the Project

This project uses [**uv**](https://docs.astral.sh/uv/) for dependency management (Python >= 3.12). To run the dashboard locally:

1.  **Clone the repository:**
    `git clone https://github.com/YourUsername/Charging_Infrastructure_in_Germany.git`
    `cd Charging_Infrastructure_in_Germany`

2.  **Install dependencies** (uv creates the `.venv/` automatically from `pyproject.toml` / `uv.lock`):
    `uv sync`

3.  **Start the dashboard:**
    `uv run streamlit run 01_app/app.py`

# Public Charging Infrastructure in Germany: Data Analysis & Dashboard

This project is an interactive dashboard application that visualizes the current state of public charging infrastructure in Germany. It was developed as a take-home task for a data analyst position at NOW GmbH.

🔗 **Link to the live application:** [https://ladeinfrastruktur-in-deutschland.streamlit.app/](https://ladeinfrastruktur-in-deutschland.streamlit.app/)

## Data Used

This project utilizes three main datasets:

1.  **Charging Infrastructure Data:** Cleaned data from the Federal Network Agency's charging station register, provided by the National Control Centre for Charging Infrastructure at NOW GmbH. The raw data can be downloaded from the public data platform Mobilithek:
    * **Data Source Link:** https://mobilithek.info/offers/842113170303512576
    * **`ladestationFactTable.csv`**: Contains metadata on charging stations, such as geographical coordinates, operator information, and addresses.
    * **`ladepunktFactTable.csv`**: Contains technical details for individual charging points, including charging power and connector types.

2.  **Geospatial Data:** A Shapefile (`VG250_KRS.shp`) from the Federal Agency for Cartography and Geodesy (BKG). This data was used to visualize the German district boundaries and spatially join the charging infrastructure data for a map-based analysis.

## What Was Done

1.  **Data Integration:** The provided CSV files were processed and merged using Python and Pandas, joining them on a common `ladestation_id`.
2.  **Geospatial Join:** The aggregated charging infrastructure data was joined with the district boundary data to enable a visual representation of charging station density on a map.
3.  **Dashboard Development:** An interactive dashboard was built using Streamlit and Plotly. It allows users to visualize the charging infrastructure at the district level and apply filters (e.g., by state or charging type).

## Project Structure

The project follows a clear and professional folder structure for organization and reproducibility:
```
├── 01_app/
│   └── dashboard.py               # The main Streamlit script
├── 02_data/
│   ├── 01_original_data/          # CSV files from the charging station register
│   │   ├── ladestationFactTable.csv
│   │   └── ladepunktFactTable.csv
│   └── 02_meta_data/              # Folder for geospatial data and other metadata
│       └── ...                    # Contains the VG250_KRS Shapefile
├── 03_notebooks/                  # Optional: For initial data analysis and prototyping
├── 04_documents/                  # Optional: For documentation or reports
├── .gitignore                     # Git configuration to ignore unwanted files
├── README.md                      # This file
├── requirements.txt               # List of all Python dependencies
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

To run the dashboard locally, follow these steps:

1.  **Clone the repository:**
    `git clone https://github.com/YourUsername/Charging_Infrastructure_in_Germany.git`
    `cd Charging_Infrastructure_in_Germany`

2.  **Create and activate a virtual environment:**
    `python3 -m venv venv`
    * **macOS / Linux:** `source venv/bin/activate`
    * **Windows:** `venv\Scripts\activate`

3.  **Install dependencies:**
    `pip install -r requirements.txt`

4.  **Start the dashboard:**
    `streamlit run 01_app/dashboard.py`

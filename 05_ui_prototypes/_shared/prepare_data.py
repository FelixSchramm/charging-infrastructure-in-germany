"""Build the shared CSV files for the UI prototypes with DuckDB.

Run: ``uv run python 05_ui_prototypes/_shared/prepare_data.py``
"""

from pathlib import Path

import duckdb

SHARED_DIR = Path(__file__).resolve().parent
REPO_ROOT = SHARED_DIR.parents[1]
DATA_DIR = SHARED_DIR / "data"


def read_last_updated() -> str:
    """Read ``LAST_UPDATED`` from ``01_app/_data_version.py`` without importing it.

    :return: the update stamp, e.g. ``2026-10-10``
    """
    namespace = {}
    exec((REPO_ROOT / "01_app/_data_version.py").read_text(), namespace)
    return namespace["LAST_UPDATED"]


def kpis(overview, bundesland=None, types=("hpc", "schnell", "normal")):
    """Compute the reference KPIs from ``overview.csv`` (see README calculation logic).

    :param overview: DuckDB relation of ``overview.csv``
    :param bundesland: federal state to filter on, ``None`` for all
    :param types: selected power types, subset of hpc, schnell, normal
    :return: dict with stations, gigawatt, charging points, HPC charging points
    """
    state = "TRUE" if bundesland is None else f"bundesland = '{bundesland}'"
    match = " OR ".join(f"has_{t}" for t in types)
    points = " + ".join(f"SUM(lp_{t})" for t in types)
    hpc = "SUM(lp_hpc)" if "hpc" in types else "0"
    row = overview.filter(state).aggregate(f"""
        SUM(stationen) FILTER (WHERE {match}) AS stationen,
        SUM(kw) FILTER (WHERE {match}) / 1000000 AS gesamtleistung_gw,
        {points} AS ladepunkte,
        {hpc} AS hpc_ladepunkte
        """).fetchone()
    return dict(zip(("stationen", "gesamtleistung_gw", "ladepunkte", "hpc_ladepunkte"), row))


def main() -> None:
    """Write ``overview.csv`` and ``meta.csv`` and print the reference KPIs."""
    DATA_DIR.mkdir(exist_ok=True)
    # SQL paths are relative to the repo root, so the script works from any cwd.
    con = duckdb.connect(config={"file_search_path": str(REPO_ROOT)})

    for name in ("overview", "meta"):
        sql = (SHARED_DIR / f"{name}.sql").read_text()
        out = DATA_DIR / f"{name}.csv"
        con.execute(f"COPY ({sql}) TO '{out}' (HEADER, DELIMITER ',')")

    meta = DATA_DIR / "meta.csv"
    con.execute(
        f"COPY (SELECT *, '{read_last_updated()}' AS update FROM read_csv('{meta}', all_varchar=true)) "
        f"TO '{meta}.tmp' (HEADER, DELIMITER ',')"
    )
    Path(f"{meta}.tmp").replace(meta)

    overview = con.read_csv(str(DATA_DIR / "overview.csv"))
    print("Reference KPIs (no filter):", kpis(overview))
    print("Reference KPIs (Bayern, HPC only):", kpis(overview, "Bayern", ("hpc",)))


if __name__ == "__main__":
    main()

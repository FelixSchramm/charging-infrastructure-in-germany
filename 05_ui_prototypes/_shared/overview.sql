-- One row per (bundesland, jahr, has_hpc, has_schnell, has_normal).
-- Cleaning and power categories mirror 01_app/data_loading.py and config.py.
WITH points AS (
    SELECT
        ladestation_id,
        bundesland,
        installierteladeleistungnll AS kw,
        YEAR(inbetriebnahmedatum) AS jahr,
        COALESCE(ladeleistunginkw >= 150, FALSE) AS is_hpc,
        COALESCE(ladeleistunginkw > 22 AND ladeleistunginkw < 150, FALSE) AS is_schnell
    FROM
        READ_PARQUET('02_data/03_computed_data/combined_ladestation_ladepunkt.parquet')
    WHERE
        inbetriebnahmedatum IS NOT NULL
        AND bundesland IS NOT NULL
        AND kreiskreisfreiestadt IS NOT NULL
),

stations AS (
    -- bundesland, jahr and kw are constant per station
    SELECT
        ladestation_id,
        ANY_VALUE(bundesland) AS bundesland,
        ANY_VALUE(jahr) AS jahr,
        ANY_VALUE(kw) AS kw,
        COUNT(*) FILTER (WHERE is_hpc) AS lp_hpc,
        COUNT(*) FILTER (WHERE is_schnell) AS lp_schnell,
        COUNT(*) FILTER (WHERE NOT is_hpc AND NOT is_schnell) AS lp_normal
    FROM points
    GROUP BY ladestation_id
)

SELECT
    bundesland,
    jahr,
    lp_hpc > 0 AS has_hpc,
    lp_schnell > 0 AS has_schnell,
    lp_normal > 0 AS has_normal,
    COUNT(*) AS stationen,
    SUM(kw) AS kw,
    SUM(lp_hpc) AS lp_hpc,
    SUM(lp_schnell) AS lp_schnell,
    SUM(lp_normal) AS lp_normal
FROM stations
GROUP BY ALL
ORDER BY bundesland, jahr, has_hpc, has_schnell, has_normal

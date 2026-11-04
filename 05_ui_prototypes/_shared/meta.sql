-- One row with the data status shown in the header (01_app/sections/header.py).
SELECT
    (
        SELECT STRFTIME(MAX(inbetriebnahmedatum), '%d.%m.%Y')
        FROM
            READ_PARQUET('02_data/03_computed_data/combined_ladestation_ladepunkt.parquet')
        WHERE bundesland IS NOT NULL AND kreiskreisfreiestadt IS NOT NULL
    ) AS bnetza_stand,
    (
        SELECT SUBSTR(berichtszeitpunkt, 6, 2) || '/' || SUBSTR(berichtszeitpunkt, 1, 4)
        FROM READ_PARQUET('02_data/03_computed_data/kba_ev_bestand.parquet')
        ORDER BY berichtszeitpunkt DESC
        LIMIT 1
    ) AS kba_stand

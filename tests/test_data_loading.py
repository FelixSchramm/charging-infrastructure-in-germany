"""Tests for the connector-to-charging-point aggregation."""

import numpy as np
import pandas as pd

from data_loading import _aggregate_to_ladepunkte


def _connector_rows():
    """Build a small connector-level frame incl. a missing station id."""
    return pd.DataFrame(
        {
            "ladestation_id": ["s1", "s1", "s1", np.nan, np.nan],
            "ladepunkt_id": [
                "e1#CCS",
                "e1#Type2",
                "e2#CCS",
                "e3#CCS",
                "e3#CHAdeMO",
            ],
            "LadeleistungInKW": [150.0, 22.0, 50.0, 11.0, 22.0],
            "Steckertyp": ["CCS", "Type2", "CCS", "CCS", "CHAdeMO"],
        }
    )


def test_one_row_per_evse():
    """:return: None; connectors of one EVSE collapse into one row."""
    assert len(_aggregate_to_ladepunkte(_connector_rows())) == 3


def test_max_power_and_combined_plugs():
    """:return: None; power is the maximum, plug types are joined."""
    result = _aggregate_to_ladepunkte(_connector_rows())
    first = result.iloc[0]
    assert first["LadeleistungInKW"] == 150.0
    assert first["Steckertyp"] == "CCS, Type2"


def test_missing_station_id_is_kept():
    """:return: None; rows without station id are aggregated, not dropped."""
    result = _aggregate_to_ladepunkte(_connector_rows())
    assert result["LadeleistungInKW"].iloc[2] == 22.0

"""The patient grid: spatial units × ISO weeks (Monday-anchored).

`make_grid(inst)` returns the unit assigner declared in `atlantis.yaml → grid` — `kind: rules | polygons | cells`.
`week_start(dates)` is the one place the time step is defined.
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.grid.rules import RuleGrid, RuleError
from atlantis_core.grid.polygons import PolygonGrid
from atlantis_core.grid.cells import CellGrid

__all__ = ["RuleGrid", "RuleError", "PolygonGrid", "CellGrid", "make_grid", "week_start", "patient_weeks"]


def make_grid(inst):
    g = inst.cfg["grid"]
    kind = g["kind"]
    if kind == "rules":
        return RuleGrid(g["rules"])
    if kind == "polygons":
        return PolygonGrid.from_file(inst.path(g["path"]), g["id_property"], g.get("name_property"))
    if kind == "cells":
        return CellGrid(g["res"], *g["bbox"])
    raise ValueError(f"grid.kind {kind!r} — expected rules | polygons | cells")


def week_start(dates) -> pd.Series:
    """Monday of the ISO week containing each date."""
    d = pd.to_datetime(pd.Series(dates))
    return (d - pd.to_timedelta(d.dt.weekday, unit="D")).dt.normalize()


def patient_weeks(first: pd.Timestamp, last: pd.Timestamp) -> pd.DatetimeIndex:
    return pd.date_range(first, last, freq="7D")

"""Registries + config + raw stream frames → the patient × week vitals table.

    frames = load_frames(inst)                  # raw artifacts named in atlantis.yaml → normalised long frames
    table, info = build(inst, frames)           # grid (unit, week) + one column per vital, registry order + label

`build` never reads beyond the frames it is given, so the self-test can hand it synthetic frames.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from atlantis_core.config import Instance, feature_name
from atlantis_core.grid import make_grid, week_start, patient_weeks
from atlantis_core.vitals import grammar
from atlantis_core.vitals.ops import Evaluator


def normalise(inst: Instance, stream_id: str, raw: pd.DataFrame, grid=None) -> pd.DataFrame:
    """Rename a raw artifact to the shape's standard columns; point streams get their unit assigned by the grid."""
    spec = inst.stream_spec(stream_id)
    shape, cols = spec["shape"], spec["columns"]
    df = pd.DataFrame({"date": pd.to_datetime(raw[cols["date"]]).values,
                       "value": pd.to_numeric(raw[cols["value"]], errors="coerce").values})
    if shape == "point":
        grid = grid or make_grid(inst)
        df["unit"] = grid.assign(raw[cols["lat"]].values, raw[cols["lon"]].values)
        df = df[pd.notna(df["unit"])]
        if inst.cfg["grid"].get("unit_dtype") == "int":
            df["unit"] = df["unit"].astype("int64")
    elif shape == "unit_daily":
        df["unit"] = raw[cols["unit"]].values
        if inst.cfg["grid"].get("unit_dtype") == "int":
            df["unit"] = df["unit"].astype("int64")
    elif shape == "station_daily":
        df["station"] = raw[cols["station"]].astype(str).values
    else:
        raise ValueError(f"{stream_id}: shape {shape!r} — expected point | unit_daily | station_daily")
    return df.reset_index(drop=True)


def load_frames(inst: Instance) -> dict:
    grid = make_grid(inst)
    out = {}
    for sid in inst.streams:
        spec = inst.stream_spec(sid)
        out[sid] = normalise(inst, sid, pd.read_parquet(inst.path(spec["artifact"])), grid)
    return out


def patient_grid(inst: Instance, frames: dict) -> tuple[list, pd.DatetimeIndex]:
    """Units × weeks. `grid.units_from` / `grid.weeks_from` name the stream that defines them (the exemplar: the
    event stream, as `hab.build_features` did), or `grid.units` / `grid.weeks` give them explicitly."""
    g = inst.cfg["grid"]
    if "units" in g:
        units = list(g["units"])
    else:
        units = sorted(pd.unique(frames[g["units_from"]]["unit"]))
    if "weeks" in g:
        w0, w1 = (pd.Timestamp(x) for x in g["weeks"])
        weeks = patient_weeks(week_start([w0]).iloc[0], week_start([w1]).iloc[0])
    else:
        wk = week_start(frames[g["weeks_from"]]["date"])
        weeks = patient_weeks(wk.min(), wk.max())
    return units, weeks


def _weekly_index(weeks: pd.DatetimeIndex, frame: pd.DataFrame) -> pd.DatetimeIndex:
    """Complete weekly index spanning the grid AND the stream's own data, so rolling windows and climatologies see
    the stream's full record, then everything is cut back to the grid."""
    wk = week_start(frame["date"])
    lo, hi = min(weeks.min(), wk.min()), max(weeks.max(), wk.max())
    return patient_weeks(lo, hi)


def evaluator(inst: Instance, sid: str, frames: dict, units, weeks) -> Evaluator:
    spec = inst.stream_spec(sid)
    consts = dict(inst.cfg.get("constants", {}))
    consts[grammar.EVENT_CONSTANT] = float(inst.event["threshold"])
    return Evaluator(sid, frames[sid], spec["shape"], _weekly_index(weeks, frames[sid]), units, consts,
                     climatology=inst.climatology(sid), stations=spec.get("stations"),
                     weeks_since_cap=inst.cfg.get("vitals", {}).get("weeks_since_cap", 104))


def build(inst: Instance, frames: dict, with_label: bool = True) -> tuple[pd.DataFrame, dict]:
    units, weeks = patient_grid(inst, frames)
    evs = {sid: evaluator(inst, sid, frames, units, weeks) for sid in inst.streams}
    ucol, wcol = inst.cfg["grid"].get("unit_column", "unit"), "week"
    table = pd.MultiIndex.from_product([units, weeks], names=[ucol, wcol]).to_frame(index=False)
    consts = list(inst.cfg.get("constants", {}))
    for v in inst.vitals:
        node = grammar.parse(v["transform"], consts, v["vital_id"])
        w = evs[v["stream_ref"]].weekly(node, v.get("window"), v.get("lag", 0)).reindex(weeks)
        table[feature_name(v)] = w[units].to_numpy().T.reshape(-1)   # unit-major, matching the product order
    info = {"units": units, "weeks": [str(weeks.min().date()), str(weeks.max().date())], "n_patient_weeks": len(table)}
    if with_label:
        from atlantis_core import label
        table = label.make(inst, table, evs, units, weeks)
    return table, info

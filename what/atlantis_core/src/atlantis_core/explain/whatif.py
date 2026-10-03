"""Counterfactual re-scoring, declared in config (`atlantis.yaml → whatif.scenarios`). Correlational, not causal.

A scenario scales a RAW stream for the units it names over a period, re-derives the vitals through `vitals.build`
(so every vital reading that stream moves exactly as its transform says — no hand-edited feature columns), and
re-scores the modelling rows of those units in that period with the trained model.

    {name, units, period: [d0, d1], stream, op: scale, factor, lookback_days?}

The raw stream is scaled from d0 − lookback_days to the end of d1's week. The default lookback covers every vital that
reads the stream: 7 × (max lag + max window + 1) days, plus the largest `*_days` constant. A scenario is refused if the
stream has no vital tagged `lever` (nothing a steward can change), or if the scaled span touches a climatology era
(the normal itself would move). Scaling a station the stream does not list in `lever_stations` is reported, not hidden.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from atlantis_core.grid import week_start
from atlantis_core.vitals.build import build


def lookback_days(inst, sid: str) -> int:
    vs = [v for v in inst.vitals if v["stream_ref"] == sid]
    weeks = max((int(v.get("lag", 0) or 0) + int(v.get("window", 0) or 0) for v in vs), default=0) + 1
    days = max((int(x) for k, x in (inst.cfg.get("constants") or {}).items() if k.endswith("_days")), default=0)
    return 7 * weeks + days


def _mask(inst, sid, frame, units, lo, hi):
    spec = inst.stream_spec(sid)
    inside = (frame["date"] >= lo) & (frame["date"] <= hi)
    if spec["shape"] == "station_daily":
        st = [s for s, us in spec["stations"].items() if set(us) & set(units)]
        return inside & frame["station"].isin(st), st
    return inside & frame["unit"].isin(units), []


def scenario(inst, frames: dict, L, model, model_df: pd.DataFrame, sc: dict) -> dict:
    sid, units = sc["stream"], list(sc["units"])
    if not any(v["stream_ref"] == sid and v["tag"] == "lever" for v in inst.vitals):
        raise ValueError(f"whatif {sc['name']}: {sid} feeds no vital tagged lever — nothing a steward can change")
    if sc.get("op", "scale") != "scale":
        raise ValueError(f"whatif {sc['name']}: op {sc['op']!r} — only scale is implemented")
    d0, d1 = (pd.Timestamp(x) for x in sc["period"])
    lb = int(sc.get("lookback_days", lookback_days(inst, sid)))
    lo, hi = d0 - pd.Timedelta(days=lb), week_start([d1]).iloc[0] + pd.Timedelta(days=6)
    era = inst.climatology(sid)
    if era and lo.year <= era[1] and hi.year >= era[0]:
        raise ValueError(f"whatif {sc['name']}: scaled span {lo.date()}..{hi.date()} touches the {sid} climatology era {era}")
    f = frames[sid].copy()
    m, stations = _mask(inst, sid, f, units, lo, hi)
    f.loc[m, "value"] = f.loc[m, "value"] * float(sc["factor"])
    table_cf, _ = build(inst, {**frames, sid: f}, with_label=False)
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    rows = model_df[model_df[ucol].isin(units) & (model_df.week >= d0) & (model_df.week <= d1)].sort_values([ucol, "week"])
    cf = rows[[ucol, "week"]].merge(table_cf, on=[ucol, "week"], how="left")
    p0, p1 = L.predict(model, rows), L.predict(model, cf)
    levers = set(inst.stream_spec(sid).get("lever_stations") or [])
    out = {"name": sc["name"], "units": units, "stream": sid, "op": "scale", "factor": float(sc["factor"]),
           "scaled_span": [str(lo.date()), str(hi.date())], "lookback_days": lb, "rows_scaled": int(m.sum()),
           "weeks": rows.week.dt.strftime("%Y-%m-%d").tolist(), "p_actual": np.round(p0, 4).tolist(),
           "p_scenario": np.round(p1, 4).tolist(), "y": rows.y.astype(int).tolist(),
           "mean_delta": float(np.mean(p1 - p0)), "mean_abs_delta": float(np.mean(np.abs(p1 - p0))),
           "max_abs_delta": float(np.max(np.abs(p1 - p0))) if len(rows) else None}
    if stations:
        out["stations_scaled"] = stations
        out["non_lever_stations_scaled"] = [s for s in stations if s not in levers]
    return out


def run(inst, frames, L, model, model_df, log=print) -> dict:
    out = {"caveat": "Counterfactual re-scoring of a correlational model: what the score would have been, not what the sea would have done."}
    for sc in (inst.cfg.get("whatif") or {}).get("scenarios", []) or []:
        r = scenario(inst, frames, L, model, model_df, sc)
        out[sc["name"]] = r
        log(f"whatif {sc['name']}: mean Δp = {r['mean_delta']:+.4f}, mean |Δp| = {r['mean_abs_delta']:.4f}"
            + (f"  ⚠ non-lever stations scaled: {r['non_lever_stations_scaled']}" if r.get("non_lever_stations_scaled") else ""))
    return out

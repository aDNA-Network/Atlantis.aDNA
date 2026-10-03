"""The all-stream leakage self-test — SO-7, the method's one hard invariant. Synthetic data, no network.

    python -m atlantis_core.selftest --instance <dir>

It builds a synthetic patient at `atlantis.yaml → selftest` (a unit, a coordinate inside it, a week t after every
climatology era), runs the instance's OWN registries over it, and for EVERY registered stream asserts:

  C0  positive control — perturbing week t itself moves ≥ 1 vital fed by that stream (the instrument can fail)
  C1  perturbing week t+1 moves NO vital at ANY patient-week ≤ t (the whole past, not just t); the label at t moves
      iff the stream is the event stream
  C2  perturbing week t+H+1 moves no vital at any week ≤ t, and not the label at t (the horizon is respected)
  C3  (point streams) deleting every observation in t+1..t+H flags the outcome unknown and moves no vital at t
and once:
  C4  every vital at t is non-NaN on the clean build (no assertion above is vacuous)
  C5  a `below` event on the same streams: label flips on a t+1 drop, not on a t+H+1 drop
  C6  REPORTED, not hidden: inside a climatology era, a t+1 perturbation moves anomaly() vitals at earlier weeks — the
      era normal is one statistic over the whole era, so the same calendar week in EVERY earlier era year depends on it.
      Asserted: only anomaly() vitals move. Reported: cells and max |Δ| (float residue of pandas' running-sum rolling
      mean is ~1e-15 and is separated from real dependence at 1e-9). Registry R7 keeps every era before validation.

Equality is exact (NaN == NaN): a leak of any size fails.
"""
from __future__ import annotations

import argparse, copy, sys

import numpy as np
import pandas as pd

from atlantis_core.config import Instance, load_instance, feature_name
from atlantis_core.grid import week_start
from atlantis_core.vitals import grammar
from atlantis_core.vitals.build import build


class LeakError(AssertionError):
    pass


# -- synthetic data -------------------------------------------------------------------------------------------------
def _span(inst: Instance, t: pd.Timestamp):
    eras = [e for e in (inst.cfg.get("climatology") or {}).values()]
    first = min([pd.Timestamp(f"{e[0]}-01-01") for e in eras] + [t - pd.Timedelta(weeks=120)])
    in_era = pd.Timestamp(inst.cfg["selftest"].get("in_era_week", t))
    first = min(first, in_era - pd.Timedelta(weeks=120))
    return first, t + pd.Timedelta(weeks=30)


def synth(inst: Instance, t: pd.Timestamp, seed: int = 0) -> dict:
    st, rng = inst.cfg["selftest"], np.random.default_rng(seed)
    first, last = _span(inst, t)
    ev = inst.event
    out = {}
    for sid in inst.streams:
        spec = inst.stream_spec(sid)
        shape = spec["shape"]
        if shape == "point":
            weeks = pd.date_range(week_start([first]).iloc[0], last, freq="7D")
            n = len(weeks) * 3
            dates = np.repeat(weeks.values, 3) + pd.to_timedelta(rng.integers(0, 7, n), unit="D").values
            if sid == ev["event_variable_stream"]:
                thr = float(ev["threshold"])
                lo, hi = (0.0, 0.05 * thr) if ev["direction"] == "above" else (2.0 * thr, 3.0 * thr)
            else:
                lo, hi = 0.0, 5000.0
            out[sid] = pd.DataFrame({"date": pd.to_datetime(dates), "value": rng.uniform(lo, hi, n), "unit": st["unit"]})
        else:
            days = pd.date_range(first, last, freq="D")
            doy = days.dayofyear.values
            if shape == "unit_daily":
                base = 25 + 3 * np.sin(2 * np.pi * doy / 365.25)
                out[sid] = pd.DataFrame({"date": days, "unit": st["unit"], "value": base + rng.normal(0, 1, len(days))})
            else:
                sites = [s for s, us in spec["stations"].items() if st["unit"] in us]
                if not sites:
                    raise ValueError(f"selftest unit {st['unit']} has no station on {sid}; pick a unit every stream feeds")
                out[sid] = pd.concat([pd.DataFrame({"date": days, "station": s,
                                                    "value": 1000 + 300 * np.sin(2 * np.pi * doy / 365.25) + rng.normal(0, 50, len(days))})
                                      for s in sites], ignore_index=True)
    return out


def perturb(frames: dict, inst: Instance, sid: str, week: pd.Timestamp, how: str = "spike") -> dict:
    f = {k: v.copy() for k, v in frames.items()}
    d = f[sid]
    in_week = d["date"].between(week, week + pd.Timedelta(days=6))
    if how == "delete":
        f[sid] = d[~in_week].reset_index(drop=True); return f
    ev = inst.event
    if inst.stream_spec(sid)["shape"] == "point":
        if sid == ev["event_variable_stream"]:
            big = 50.0 * float(ev["threshold"]) if ev["direction"] == "above" else 0.0
        else:
            big = 1e7
        d.loc[in_week, "value"] = big
        extra = d[in_week].copy()                        # and look harder that week: presence moves too
        f[sid] = pd.concat([d, extra], ignore_index=True)
    else:
        scale = 100.0 * (float(d["value"].abs().mean()) + 1.0)
        d.loc[in_week, "value"] = d.loc[in_week, "value"] + scale
        f[sid] = d
    return f


# -- comparison -----------------------------------------------------------------------------------------------------
def row_at(table: pd.DataFrame, inst: Instance, week: pd.Timestamp) -> pd.Series:
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    r = table[(table["week"] == week) & (table[ucol] == inst.cfg["selftest"]["unit"])]
    if len(r) != 1:
        raise LeakError(f"selftest patient ({inst.cfg['selftest']['unit']}, {week.date()}) not on the grid")
    return r.iloc[0]


def moved(a: pd.Series, b: pd.Series, cols) -> list[str]:
    out = []
    for c in cols:
        va, vb = a[c], b[c]
        if pd.isna(va) and pd.isna(vb):
            continue
        if pd.isna(va) != pd.isna(vb) or va != vb:
            out.append(f"{c}: {va} → {vb}")
    return out


def moved_table(a: pd.DataFrame, b: pd.DataFrame, cols, upto: pd.Timestamp) -> dict:
    """Per column: cells that differ at weeks ≤ `upto` → (n, max |Δ|, first week, last week, n with |Δ| > 1e-9).
    Exact, NaN-aware."""
    m = a["week"] <= upto
    out = {}
    for c in cols:
        x, y = a.loc[m, c].to_numpy(float), b.loc[m, c].to_numpy(float)
        d = ~((np.isnan(x) & np.isnan(y)) | (x == y))
        if d.any():
            w = a.loc[m, "week"][d]
            delta = np.abs(np.nan_to_num(x[d] - y[d], nan=np.inf))
            out[c] = (int(d.sum()), float(delta.max()), str(w.min().date()), str(w.max().date()), int((delta > 1e-9).sum()))
    return out


def _streams_of(inst):
    return {sid: [feature_name(v) for v in inst.vitals if v["stream_ref"] == sid] for sid in inst.streams}


# -- the test -------------------------------------------------------------------------------------------------------
def run(inst: Instance, verbose: bool = True) -> dict:
    say = print if verbose else (lambda *a, **k: None)
    st = inst.cfg["selftest"]
    t = pd.Timestamp(st["week"]); H = int(inst.event["horizon"])
    if t != week_start([t]).iloc[0]:
        raise ValueError(f"selftest.week {t.date()} is not a Monday")
    feats, ev_sid, by_stream = inst.feature_names, inst.event["event_variable_stream"], _streams_of(inst)
    t1, tH1 = t + pd.Timedelta(weeks=1), t + pd.Timedelta(weeks=H + 1)
    frames = synth(inst, t)
    base_tab, _ = build(inst, frames)
    base = row_at(base_tab, inst, t)
    res = {"streams": {}, "vitals": len(feats)}

    nan_at_t = [f for f in feats if pd.isna(base[f])]
    if nan_at_t:
        raise LeakError(f"C4 vacuous: vitals NaN at t on the clean synthetic build: {nan_at_t}")
    if base["y"] != 0 or base["already_in_event"] or base["outcome_unknown"]:
        raise LeakError(f"C4 baseline patient is not a clean negative: y={base['y']} in_event={base['already_in_event']} unknown={base['outcome_unknown']}")
    say(f"C4 ✅ clean build: {len(feats)} vitals non-NaN at t={t.date()}, y=0, patient kept")

    for sid in inst.streams:
        r = {}
        # C0
        b0 = row_at(build(inst, perturb(frames, inst, sid, t))[0], inst, t)
        hit = moved(base, b0, by_stream[sid])
        if not hit:
            raise LeakError(f"C0 {sid}: perturbing week t moved none of its vitals — the instrument cannot fail")
        r["C0_moved_at_t"] = len(hit)
        # C1
        tab1 = build(inst, perturb(frames, inst, sid, t1))[0]
        b1 = row_at(tab1, inst, t)
        leak = moved_table(base_tab, tab1, feats, t)
        if leak:
            raise LeakError(f"C1 LEAK {sid}: perturbing t+1 moved vitals at weeks ≤ t: {leak}")
        if sid == ev_sid and not (base["y"] == 0 and b1["y"] == 1):
            raise LeakError(f"C1 {sid}: label did not respond to a t+1 event ({base['y']} → {b1['y']})")
        if sid != ev_sid and b1["y"] != base["y"]:
            raise LeakError(f"C1 {sid}: label moved on a non-event stream ({base['y']} → {b1['y']})")
        # C2
        tab2 = build(inst, perturb(frames, inst, sid, tH1))[0]
        b2 = row_at(tab2, inst, t)
        late = moved(base, b2, ["y", "already_in_event", "outcome_unknown"]) or moved_table(base_tab, tab2, feats, t)
        if late:
            raise LeakError(f"C2 {sid}: perturbing t+H+1 moved something at/before t: {late}")
        # C3
        if inst.stream_spec(sid)["shape"] == "point":
            f3 = frames
            for k in range(1, H + 1):
                f3 = perturb(f3, inst, sid, t + pd.Timedelta(weeks=k), how="delete")
            b3 = row_at(build(inst, f3)[0], inst, t)
            leak = moved(base, b3, feats)
            if leak:
                raise LeakError(f"C3 LEAK {sid}: deleting t+1..t+H observations moved vitals at t: {leak}")
            if sid == ev_sid and not b3["outcome_unknown"]:
                raise LeakError(f"C3 {sid}: no observations in t+1..t+H but outcome not flagged unknown")
            r["C3"] = "ok"
        res["streams"][sid] = r
        say(f"   ✅ {sid}: C0 bites ({r['C0_moved_at_t']} vitals at t) · C1 no leak · C2 horizon"
            + (" · C3 presence" if "C3" in r else "") + (" · label responds" if sid == ev_sid else " · label still"))

    # C5 — a below event on the same streams
    below = copy.deepcopy(inst)
    ev = below.event
    ev["direction"] = "below"
    fb = synth(below, t, seed=1)
    tb = row_at(build(below, fb)[0], below, t)
    t1b = row_at(build(below, perturb(fb, below, ev_sid, t1))[0], below, t)
    tHb = row_at(build(below, perturb(fb, below, ev_sid, tH1))[0], below, t)
    if not (tb["y"] == 0 and t1b["y"] == 1 and tHb["y"] == 0) or tb["already_in_event"]:
        raise LeakError(f"C5 below: y {tb['y']} → t+1 {t1b['y']} / t+H+1 {tHb['y']}; in_event {tb['already_in_event']}")
    if moved(tb, t1b, feats):
        raise LeakError(f"C5 below: t+1 drop moved vitals at t: {moved(tb, t1b, feats)}")
    say("C5 ✅ below-direction event: label flips on a t+1 drop, not on t+H+1; no vital moves")
    res["C5"] = "ok"

    # C6 — declared climatology dependence, reported
    te = pd.Timestamp(st["in_era_week"]); res["C6"] = {}
    consts = list(inst.cfg.get("constants", {}))
    anomaly_vitals = {feature_name(v) for v in inst.vitals
                      if "anomaly" in grammar.functions_used(grammar.parse(v["transform"], consts))}
    for sid in (inst.cfg.get("climatology") or {}):
        tab_e = build(inst, perturb(frames, inst, sid, te + pd.Timedelta(weeks=1)))[0]
        mv = moved_table(base_tab, tab_e, feats, te)
        stray = sorted(set(mv) - anomaly_vitals)
        if stray:
            raise LeakError(f"C6 {sid}: inside the era, non-anomaly vitals moved before t+1: { {k: mv[k] for k in stray} }")
        real = {k: v for k, v in mv.items() if v[1] > 1e-9}
        res["C6"][sid] = mv
        say(f"C6 ⚠ REPORTED {sid}: a t+1 perturbation inside its era ({te.date()}) moves, at weeks ≤ t:")
        for k, (n, dmax, w0, w1, nreal) in sorted(mv.items()):
            say(f"       {k}: {n} cells ({nreal} real dependence · {n - nreal} float residue ≤ 1e-9), max |Δ| {dmax:.2e}, {w0} → {w1}")
        if not mv:
            say("       nothing")
        say(f"     → {len(real)} vital(s) with real dependence; all anomaly(). Declared: the era normal includes those weeks; "
            f"eras end before split.val_start (R7), so validation and test weeks are clean (C1).")
    say(f"✅ atlantis_core self-test passed — {len(inst.streams)} streams perturbed, {len(feats)} vitals, horizon {H}")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instance", required=True)
    a = ap.parse_args(argv)
    try:
        run(load_instance(a.instance))
    except LeakError as e:
        print(f"❌ {e}", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()

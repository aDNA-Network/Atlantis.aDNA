"""The all-stream leakage self-test — SO-7, the method's one hard invariant. Synthetic data, no network.

    python -m atlantis_core.selftest --instance <dir>

It synthesises RAW frames (the instance's own column names, run through `normalise`, so unit assignment and dtypes are
exercised) for ≥ 2 patients declared at `atlantis.yaml → selftest.patients` — the first is the PRIMARY, the rest are
NEIGHBOURS — with deliberate gaps (primary event stream unobserved at t−4 and t+2, neighbour at t−1 and t; daily
streams miss week t−1 and scattered days), and runs the instance's OWN registries over them. t is a Monday after every
climatology era. For EVERY registered stream:

  C0  per-vital positive control — for every vital that reads `value`, perturbing (spike, else delete) week t−lag moves
      that vital at (primary, t). The instrument can fail, vital by vital; a lag counted in rows, not weeks, fails here.
  C1  perturbing week t+1 (all patients; spike, and delete for point streams) moves NO vital and NO `already_in_event`
      flag at ANY patient-week ≤ t; the label at (primary, t) moves iff the stream is the event stream (spike).
  C2  perturbing week t+H+1 moves no vital / `already_in_event` at weeks ≤ t, and not y / outcome_unknown at (primary, t).
  C3  (point streams, and the event stream whatever its shape) deleting every observation in t+1..t+H moves no vital /
      `already_in_event` at weeks ≤ t; for the event stream the outcome at (primary, t) becomes unknown.
  C7  perturbing the PRIMARY only at week t, through entities that feed no neighbour, moves nothing at any neighbour, any
      week (no cross-unit mixing). Skipped — and reported — for a stream whose every entity is shared.
  C8  calendar-lag invariance: for every vital with lag L ≥ 1, deleting the primary's weeks (t−L, t] does not move it at t
      (a lag counted in observed rows does). Needs no gap in the synthetic world (M-1d-i III F-2).
and once:
  C2b the horizon from inside: a spike at t+H flips y at (primary, t); deleting t+1..t+H−1 but keeping t+H does not make
      the outcome unknown.
  C4  the clean build has every vital non-NaN at (primary, t), y = 0, patient kept (nothing above is vacuous).
  C5  the event re-declared in the MIRROR direction (an `above` event → `below` with weekly_min; a `below` event → `above`
      with weekly_max): a single observation past the threshold at t+1 or t+H flips y, at t+H+1 does not; no vital /
      `already_in_event` at weeks ≤ t moves. Both tails are exercised on every instance.
  C6  REPORTED, not hidden: inside a climatology era a t+1 perturbation moves anomaly() vitals at earlier weeks — the era
      normal is one statistic over the whole era, so the same calendar week in EVERY earlier era year depends on it.
      Asserted: only anomaly() vitals move. Reported: cells, max |Δ|, real vs float residue (pandas' running-sum rolling
      mean leaves ~1e-15). Registry R7 keeps eras before validation.

The event stream may have any shape (M-1d-i: a station-keyed `below` event — hypoxia — was the dry run's first finding;
until then the synthetic world placed event values against the threshold, and spiked them, for point streams only). Its
synthetic values sit on the safe side of a POSITIVE threshold; a spike is ONE observation per entity past it (for a daily
stream, one date set across every selected entity, so a mean over stations crosses too). A threshold ≤ 0 is refused here.

Equality is exact (NaN == NaN). KNOWN LIMITS — what this test does not prove:
  * coverage is what the synthetic world exercises: two units, the gap pattern above, one t; a transform whose leak only
    appears with data shapes not synthesised here (e.g. multi-year gaps, a unit with no data at all) can pass;
  * the label is checked through y / already_in_event / outcome_unknown at the primary; `future_signal` is not asserted;
  * a WRONG-but-causal vital (e.g. the wrong lag that still looks backward) passes C1–C7; C0 catches only a vital that
    no longer responds to its own week t−lag — correctness against a reference is `tests/test_equivalence.py`'s job,
    and a new instance with no reference has only this test.
"""
from __future__ import annotations

import argparse, copy, sys
from pathlib import Path

import numpy as np
import pandas as pd

from atlantis_core.config import Instance, load_instance, feature_name
from atlantis_core.grid import week_start, make_grid
from atlantis_core.vitals import grammar
from atlantis_core.vitals.build import build, normalise

FLAGS = ["already_in_event"]


class LeakError(AssertionError):
    pass


W = lambda n: pd.Timedelta(weeks=n)


# -- synthetic world ------------------------------------------------------------------------------------------------
def patients(inst: Instance) -> list[dict]:
    ps = inst.cfg["selftest"]["patients"]
    if len(ps) < 2:
        raise ValueError("selftest.patients needs ≥ 2 (a primary and a neighbour) — cross-unit checks need a neighbour")
    return ps


def _span(inst: Instance, t: pd.Timestamp):
    eras = list((inst.cfg.get("climatology") or {}).values())
    te = pd.Timestamp(inst.cfg["selftest"].get("in_era_week", t))
    first = min([pd.Timestamp(f"{e[0]}-01-01") for e in eras] + [t - W(120), te - W(120)])
    return first, t + W(30)


def _event_band(ev) -> tuple[float, float]:
    thr = float(ev["threshold"])
    if not thr > 0:
        raise ValueError(f"selftest synthesises event values against a POSITIVE threshold; {ev['event_id']} has {thr} "
                         f"(a known limit — shift the variable, or extend the synthetic world in atlantis_core)")
    return (0.0, 0.05 * thr) if ev["direction"] == "above" else (2.0 * thr, 3.0 * thr)


def _event_big(ev) -> float:
    return 50.0 * float(ev["threshold"]) if ev["direction"] == "above" else 0.0


GAP_DEFAULT = {"point": 4, "unit_daily": 1, "station_daily": 1}


def _eq(x, v) -> bool:
    """NA-safe equality for label fields: an unknown y is not 0 and not 1 (a horizon defect that blanks y is a named
    failure, not a TypeError — M-1d-i III, short_horizon at H = 2)."""
    return bool(pd.notna(x) and x == v)


def future_gap(H: int) -> int | None:
    """The primary event stream's unobserved week inside the horizon: t+2 (the exemplar's world), t+1 when H = 2 (t+H
    must stay observed for C2b), none when H = 1 (no room inside the horizon; reported by C2b's own check)."""
    return 2 if H >= 3 else (1 if H == 2 else None)


def gap_week(inst: Instance, sid: str) -> int:
    """How many weeks before t the PRIMARY's stream is wholly unobserved. A missing week between t−lag and t is what
    exposes a lag counted in rows (C0); a missing week AT t−lag only blanks that vital (its honest value is NaN) and
    makes C4 call it vacuous. So: the shape's default (point 4, daily 1 — the exemplar's world, unchanged), unless a
    vital of this stream lags exactly there; then the smallest free week inside the stream's lag span (still crossed
    by a longer lag), else one past it (M-1d-i: a lag-1 weekly mean of a daily stream was the first fork's C4)."""
    lags = {int(v.get("lag") or 0) for v in inst.vitals if v["stream_ref"] == sid}
    k = GAP_DEFAULT[inst.stream_spec(sid)["shape"]]
    if k not in lags:
        return k
    free = [j for j in range(1, max(lags)) if j not in lags]
    return free[0] if free else max(lags) + 1


def synth(inst: Instance, t: pd.Timestamp, seed: int = 0) -> dict:
    """Raw frames in the instance's own columns, normalised through the real path."""
    rng = np.random.default_rng(seed)
    ps, ev, H = patients(inst), inst.event, int(inst.event["horizon"])
    first, last = _span(inst, t)
    grid = make_grid(inst)
    out = {}
    for sid in inst.streams:
        spec, cols = inst.stream_spec(sid), inst.stream_spec(sid)["columns"]
        shape = spec["shape"]
        k = gap_week(inst, sid)                                          # the primary's unobserved past week
        f = future_gap(H)                                                # the primary's unobserved week inside the horizon
        gaps_point = {0: {t - W(k)} | ({t + W(f)} if f else set()), 1: {t - W(1), t}}   # primary · neighbour (unobserved)
        gaps_daily = {0: {t - W(k)}, 1: {t - W(1), t}}   # III F-1: neighbour unobserved at t−1 AND t, so a back-fill from t+1 shows
        if sid == ev["event_variable_stream"]:
            # M-1d-i III F-1: the event stream carries the gaps that expose label defects WHATEVER its shape — a back-filled
            # last-known state needs the neighbour unobserved at t; a horizon counted in observed weeks needs a hole
            # inside (t, t+H]. Daily event streams had only the point-free pattern and both defects passed.
            gaps_daily = gaps_point
        if shape == "point":
            weeks = pd.date_range(week_start([first]).iloc[0], last, freq="7D")
            if sid == ev["event_variable_stream"]:
                lo, hi = _event_band(ev)
            else:
                lo, hi = 0.0, 5000.0
            parts = []
            for i, p in enumerate(ps):
                wk = weeks[~weeks.isin(list(gaps_point.get(i, set())))]
                n = len(wk) * 3
                dates = np.repeat(wk.values, 3) + pd.to_timedelta(rng.integers(0, 7, n), unit="D").values
                parts.append(pd.DataFrame({cols["date"]: pd.to_datetime(dates), cols["value"]: rng.uniform(lo, hi, n),
                                           cols["lat"]: float(p["lat"]), cols["lon"]: float(p["lon"])}))
            raw = pd.concat(parts, ignore_index=True)
        else:
            days = pd.date_range(first, last, freq="D")
            doy = days.dayofyear.values
            keep_random = rng.random(len(days)) > 0.05
            entities = ([(i, p["unit"]) for i, p in enumerate(ps)] if shape == "unit_daily" else
                        [(min(i for i, p in enumerate(ps) if p["unit"] in us), s)
                         for s, us in spec["stations"].items() if any(p["unit"] in us for p in ps)])
            parts = []
            for i, ent in entities:
                gap = np.zeros(len(days), dtype=bool)
                for g in gaps_daily.get(i, set()):
                    gap |= (days >= g) & (days <= g + pd.Timedelta(days=6))
                m = keep_random & ~gap
                if sid == ev["event_variable_stream"]:
                    v = rng.uniform(*_event_band(ev), len(days))       # the safe side of the threshold, every day
                    key = cols["unit"] if shape == "unit_daily" else cols["station"]
                    parts.append(pd.DataFrame({cols["date"]: days[m], key: ent, cols["value"]: v[m]}))
                elif shape == "unit_daily":
                    v = 25 + 3 * np.sin(2 * np.pi * doy / 365.25) + rng.normal(0, 1, len(days))
                    parts.append(pd.DataFrame({cols["date"]: days[m], cols["unit"]: ent, cols["value"]: v[m]}))
                else:
                    v = 1000 + 300 * np.sin(2 * np.pi * doy / 365.25) + rng.normal(0, 50, len(days))
                    parts.append(pd.DataFrame({cols["date"]: days[m], cols["station"]: ent, cols["value"]: v[m]}))
            if not parts:
                raise ValueError(f"no selftest patient is fed by {sid}; choose patients every stream reaches")
            raw = pd.concat(parts, ignore_index=True)
        out[sid] = normalise(inst, sid, raw, grid)
    return out


def _entity_mask(inst, sid, d, units, exclusive=False):
    shape = inst.stream_spec(sid)["shape"]
    if shape != "station_daily":
        return d["unit"].isin(units)
    pu = {p["unit"] for p in patients(inst)}
    st = inst.stream_spec(sid)["stations"]
    ok = [s for s, us in st.items() if set(us) & set(units) and (not exclusive or not (set(us) & pu) - set(units))]
    return d["station"].isin(ok)


def _entities(inst, sid, units, exclusive=False) -> list:
    if inst.stream_spec(sid)["shape"] != "station_daily":
        return list(units)
    pu = {p["unit"] for p in patients(inst)}
    return [s for s, us in inst.stream_spec(sid)["stations"].items()
            if set(us) & set(units) and (not exclusive or not (set(us) & pu) - set(units))]


def perturb(frames, inst, sid, week, how="spike", units=None, exclusive=False):
    units = units if units is not None else [p["unit"] for p in patients(inst)]
    f = {k: v.copy() for k, v in frames.items()}
    d = f[sid]
    sel = d["date"].between(week, week + pd.Timedelta(days=6)) & _entity_mask(inst, sid, d, units, exclusive)
    if how == "delete":
        f[sid] = d[~sel].reset_index(drop=True); return f
    ev = inst.event
    if inst.stream_spec(sid)["shape"] == "point":
        big = _event_big(ev) if sid == ev["event_variable_stream"] else 1e7
        first = d[sel].groupby("unit").head(1).index        # ONE observation per unit: an aggregate must pick it up
        d.loc[first, "value"] = big
        f[sid] = pd.concat([d, d.loc[first]], ignore_index=True)   # and one more sample: presence moves too
    elif sid == ev["event_variable_stream"]:
        # ONE date (the week's Monday) past the threshold, across every selected entity — a unit's value is a mean over its
        # stations, so all must cross. An entity unobserved that day (a declared gap) gets the observation inserted:
        # the event happens whether or not last week's sampling did.
        key = "station" if inst.stream_spec(sid)["shape"] == "station_daily" else "unit"
        big = _event_big(ev)
        at_day = d["date"].eq(week) & _entity_mask(inst, sid, d, units, exclusive)
        d.loc[at_day, "value"] = big
        missing = [e for e in _entities(inst, sid, units, exclusive) if e not in set(d.loc[at_day, key])]
        if missing:
            d = pd.concat([d, pd.DataFrame({"date": week, key: missing, "value": big})], ignore_index=True)
        f[sid] = d
    else:
        scale = 100.0 * (float(d["value"].abs().mean()) + 1.0)
        d.loc[sel, "value"] = d.loc[sel, "value"] + scale
        f[sid] = d
    return f


def can_isolate(inst, frames, sid, primary) -> bool:
    return bool(_entity_mask(inst, sid, frames[sid], [primary], exclusive=True).any())


# -- comparison -----------------------------------------------------------------------------------------------------
def at(table, inst, unit, week) -> pd.Series:
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    r = table[(table["week"] == week) & (table[ucol] == unit)]
    if len(r) != 1:
        raise LeakError(f"selftest patient ({unit}, {week.date()}) not on the grid")
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


def moved_table(a: pd.DataFrame, b: pd.DataFrame, cols, upto=None, mask=None) -> dict:
    """Per column: cells that differ (weeks ≤ `upto`, and/or a row mask) → (n, max |Δ|, first week, last week,
    n with |Δ| > 1e-9). Exact, NaN-aware."""
    m = np.ones(len(a), dtype=bool)
    if upto is not None: m &= (a["week"] <= upto).to_numpy()
    if mask is not None: m &= np.asarray(mask)
    out = {}
    for c in cols:
        x, y = a.loc[m, c].to_numpy(float), b.loc[m, c].to_numpy(float)
        d = ~((np.isnan(x) & np.isnan(y)) | (x == y))
        if d.any():
            w = a.loc[m, "week"][d]
            delta = np.abs(np.nan_to_num(x[d] - y[d], nan=np.inf))
            out[c] = (int(d.sum()), float(delta.max()), str(w.min().date()), str(w.max().date()), int((delta > 1e-9).sum()))
    return out


def _past_clean(inst, base_tab, tab, t, feats, tag):
    leak = moved_table(base_tab, tab, feats + FLAGS, upto=t)
    if leak:
        raise LeakError(f"{tag}: moved vitals/filters at weeks ≤ t: {leak}")


# -- the test -------------------------------------------------------------------------------------------------------
def run(inst: Instance, verbose: bool = True) -> dict:
    say = print if verbose else (lambda *a, **k: None)
    st = inst.cfg["selftest"]
    t = pd.Timestamp(st["week"]); H = int(inst.event["horizon"])
    if t != week_start([t]).iloc[0]:
        raise ValueError(f"selftest.week {t.date()} is not a Monday")
    ps = patients(inst); P = ps[0]["unit"]; neighbours = [p["unit"] for p in ps[1:]]
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    feats, ev_sid = inst.feature_names, inst.event["event_variable_stream"]
    consts = list(inst.cfg.get("constants", {}))
    vit = {feature_name(v): v for v in inst.vitals}
    frames = synth(inst, t)
    base_tab, _ = build(inst, frames)
    B = lambda f: build(inst, f)[0]
    base = at(base_tab, inst, P, t)
    res = {"streams": {}, "vitals": len(feats), "patients": [p["unit"] for p in ps]}

    nan_at_t = [f for f in feats if pd.isna(base[f])]
    if nan_at_t:
        raise LeakError(f"C4 vacuous: vitals NaN at (primary, t) on the clean synthetic build: {nan_at_t}")
    if not _eq(base["y"], 0) or _eq(base["already_in_event"], True) or _eq(base["outcome_unknown"], True):
        raise LeakError(f"C4 baseline primary is not a clean negative: y={base['y']} in_event={base['already_in_event']} "
                        f"unknown={base['outcome_unknown']}")
    say(f"C4 ✅ clean build: {len(feats)} vitals non-NaN at (unit {P}, {t.date()}), y=0, kept · patients {res['patients']} · gaps in")

    for sid in inst.streams:
        r = {}
        point = inst.stream_spec(sid)["shape"] == "point"
        hows = ("spike", "delete") if point or sid == ev_sid else ("spike",)   # the event stream: presence matters, any shape
        # C0 — per vital, at t − lag
        mine = [f for f, v in vit.items() if v["stream_ref"] == sid
                and grammar.uses_value(grammar.parse(v["transform"], consts, f))]
        dead, cache = [], {}
        for f in mine:
            wk = t - W(int(vit[f].get("lag") or 0))
            ok = False
            for how in hows:
                key = (wk, how)
                if key not in cache:
                    cache[key] = at(B(perturb(frames, inst, sid, wk, how, units=[P])), inst, P, t)
                if moved(base, cache[key], [f]):
                    ok = True; break
            if not ok:
                dead.append(f)
        if dead:
            raise LeakError(f"C0 {sid}: perturbing week t−lag does not move {dead} at (primary, t) — the instrument "
                            f"cannot fail for them (or their lag is not calendar weeks)")
        r["C0_vitals"] = len(mine)
        # C8 — calendar-lag invariance (M-1d-i III F-2): a lag-L vital at t reads week t−L only, so deleting the primary's
        # weeks (t−L, t] must not move it. A lag counted in observed ROWS moves. Unlike C0 this needs no gap between t−L and
        # t, so it holds whatever weeks the synthetic world leaves out.
        by_lag = {}
        for fn in mine:
            L = int(vit[fn].get("lag") or 0)
            if L >= 1:
                by_lag.setdefault(L, []).append(fn)
        for L, fns in sorted(by_lag.items()):
            f8 = frames
            for j in range(L):
                f8 = perturb(f8, inst, sid, t - W(j), "delete", units=[P])
            mv8 = moved(base, at(B(f8), inst, P, t), fns)
            if mv8:
                raise LeakError(f"C8 {sid}: deleting the primary's weeks (t−{L}, t] moved lag-{L} vitals at t: {mv8} — "
                                f"the lag is not counted in calendar weeks")
        r["C8_vitals"] = sum(len(v) for v in by_lag.values())
        k = gap_week(inst, sid)
        r["gap_week"] = k
        r["C0_crosses_gap"] = any(int(vit[fn].get("lag") or 0) > k for fn in mine)
        # C1 — t+1, whole past, every patient
        for how in hows:
            tab1 = B(perturb(frames, inst, sid, t + W(1), how))
            _past_clean(inst, base_tab, tab1, t, feats, f"C1 LEAK {sid} ({how} at t+1)")
            b1 = at(tab1, inst, P, t)
            if how == "spike" and sid == ev_sid and not (_eq(base["y"], 0) and _eq(b1["y"], 1)):
                raise LeakError(f"C1 {sid}: label did not respond to a t+1 event ({base['y']} → {b1['y']})")
            if sid != ev_sid and moved(base, b1, ["y"]):
                raise LeakError(f"C1 {sid}: label moved on a non-event stream ({base['y']} → {b1['y']})")
        # C2 — t+H+1
        tab2 = B(perturb(frames, inst, sid, t + W(H + 1)))
        _past_clean(inst, base_tab, tab2, t, feats, f"C2 {sid} (t+H+1)")
        late = moved(base, at(tab2, inst, P, t), ["y", "outcome_unknown"])
        if late:
            raise LeakError(f"C2 {sid}: perturbing t+H+1 moved the label at (primary, t): {late}")
        # C3 — delete t+1..t+H
        if point or sid == ev_sid:
            f3 = frames
            for k in range(1, H + 1):
                f3 = perturb(f3, inst, sid, t + W(k), "delete")
            tab3 = B(f3)
            _past_clean(inst, base_tab, tab3, t, feats, f"C3 LEAK {sid} (t+1..t+H deleted)")
            if sid == ev_sid and not at(tab3, inst, P, t)["outcome_unknown"]:
                raise LeakError(f"C3 {sid}: no observations in t+1..t+H but outcome not flagged unknown")
            r["C3"] = "ok"
        # C7 — cross-unit
        if can_isolate(inst, frames, sid, P):
            tab7 = B(perturb(frames, inst, sid, t, "spike", units=[P], exclusive=True))
            nb = base_tab[ucol].isin(neighbours).to_numpy()
            cross = moved_table(base_tab, tab7, feats + FLAGS + ["y", "outcome_unknown"], mask=nb)
            if cross:
                raise LeakError(f"C7 {sid}: perturbing the primary moved neighbours: {cross}")
            r["C7"] = "ok"
        else:
            r["C7"] = "skipped: every entity of this stream also feeds a neighbour"
        res["streams"][sid] = r
        say(f"   ✅ {sid}: C0 {r['C0_vitals']} vitals bite at t−lag · C8 {r['C8_vitals']} lags calendar"
            + ("" if r["C0_crosses_gap"] or not r["C8_vitals"] else f" (gap t−{r['gap_week']} crossed by no lag: C8 alone guards it)")
            + " · C1 no leak (whole past, filters) · C2 horizon"
            + (" · C3 presence" if "C3" in r else "") + (" · C7 units isolated" if r["C7"] == "ok" else f" · C7 {r['C7']}")
            + (" · label responds" if sid == ev_sid else " · label still"))

    # C2b — the horizon from inside
    bH = at(B(perturb(frames, inst, ev_sid, t + W(H))), inst, P, t)
    if not _eq(bH["y"], 1):
        raise LeakError(f"C2b: a t+H event did not flip y at (primary, t) — the label looks short of its horizon")
    fk = frames
    for k in range(1, H):
        fk = perturb(fk, inst, ev_sid, t + W(k), "delete")
    if at(B(fk), inst, P, t)["outcome_unknown"]:
        raise LeakError("C2b: t+H observed but outcome flagged unknown — presence looks short of its horizon")
    say(f"C2b ✅ horizon from inside: t+{H} flips y; t+{H} alone keeps the outcome known")

    # C5 — the event in the MIRROR direction on the same streams (an above instance tests below, and vice versa)
    mirror = "below" if inst.event["direction"] == "above" else "above"
    mi = copy.deepcopy(inst)
    mi.event["direction"] = mirror
    mi.cfg["label"]["signal"] = "weekly_min(value)" if mirror == "below" else "weekly_max(value)"
    fb = synth(mi, t, seed=1)
    tb_tab = build(mi, fb)[0]; tb = at(tb_tab, mi, P, t)
    t1_tab = build(mi, perturb(fb, mi, ev_sid, t + W(1)))[0]
    tH = at(build(mi, perturb(fb, mi, ev_sid, t + W(H)))[0], mi, P, t)
    tH1 = at(build(mi, perturb(fb, mi, ev_sid, t + W(H + 1)))[0], mi, P, t)
    t1 = at(t1_tab, mi, P, t)
    if not (_eq(tb["y"], 0) and _eq(t1["y"], 1) and _eq(tH["y"], 1) and _eq(tH1["y"], 0)) or _eq(tb["already_in_event"], True):
        raise LeakError(f"C5 {mirror}: y {tb['y']} → t+1 {t1['y']} / t+H {tH['y']} / t+H+1 {tH1['y']}; in_event {tb['already_in_event']}")
    _past_clean(mi, tb_tab, t1_tab, t, feats, f"C5 {mirror} (t+1 crossing)")
    say(f"C5 ✅ mirror-direction event ({mirror}, {mi.cfg['label']['signal']}): one observation past the threshold at "
        f"t+1 / t+H flips y, at t+H+1 not; past clean")
    res["C5"] = "ok"
    res["C5_direction"] = mirror

    # C6 — declared climatology dependence, reported
    te = pd.Timestamp(st["in_era_week"]); res["C6"] = {}
    anomaly_vitals = {f for f, v in vit.items() if "anomaly" in grammar.functions_used(grammar.parse(v["transform"], consts))}
    for sid in (inst.cfg.get("climatology") or {}):
        tab_e = B(perturb(frames, inst, sid, te + W(1)))
        mv = moved_table(base_tab, tab_e, feats, upto=te)
        stray = sorted(set(mv) - anomaly_vitals)
        if stray:
            raise LeakError(f"C6 {sid}: inside the era, non-anomaly vitals moved before t+1: { {k: mv[k] for k in stray} }")
        res["C6"][sid] = mv
        say(f"C6 ⚠ REPORTED {sid}: a t+1 perturbation inside its era ({te.date()}) moves, at weeks ≤ t:")
        for k, (n, dmax, w0, w1, nreal) in sorted(mv.items()):
            say(f"       {k}: {n} cells ({nreal} real dependence · {n - nreal} float residue ≤ 1e-9), max |Δ| {dmax:.2e}, {w0} → {w1}")
        if not mv:
            say("       nothing")
        say("     → only anomaly() vitals; declared: the era normal includes those weeks; eras end before validation (R7).")
    say(f"✅ atlantis_core self-test passed — {len(inst.streams)} streams, {len(feats)} vitals, {len(ps)} patients, horizon {H}")
    return res


# -- the receipt (M-1d-i) ---------------------------------------------------------------------------------------------
# Contract item 6: the self-test is green BEFORE any real data is fetched. A green CLI run writes this receipt; the fetch
# CLI refuses without one whose semantic_hash equals the current config's (a vitals/label/grid change invalidates it).
# It is a local gate, not an artifact (gitignored); anyone can re-earn it, because the self-test needs no data.
RECEIPT = "outputs/atlantis_core/selftest_receipt.json"


def write_receipt(inst: Instance, res: dict) -> Path:
    import json
    from datetime import datetime, timezone
    from atlantis_core import __version__
    from atlantis_core.config import semantic_hash
    out = inst.root / RECEIPT
    out.parent.mkdir(parents=True, exist_ok=True)
    rec = {"receipt": "atlantis_core.selftest", "passed": True, "semantic_hash": semantic_hash(inst),
           "core_version": __version__, "selftest_code": selftest_code_hash(), "streams": sorted(inst.streams), "n_vitals": res["vitals"],
           "patients": res["patients"], "horizon": int(inst.event["horizon"]),
           "passed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    tmp = out.with_suffix(".tmp"); tmp.write_text(json.dumps(rec, indent=1) + "\n"); tmp.rename(out)
    return out


def selftest_code_hash() -> str:
    """sha256 (12 hex) over the code a receipt vouches for: this file, the label and the vitals evaluator. A receipt
    earned under a weaker self-test is not a receipt for the current one (M-1d-i III F-1)."""
    import hashlib
    here = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for f in ("selftest.py", "label/__init__.py", "vitals/ops.py", "vitals/build.py", "vitals/grammar.py"):
        h.update((here / f).read_bytes())
    return h.hexdigest()[:12]


def receipt_problem(inst: Instance) -> str | None:
    """None if a green receipt for THIS config exists; else why not (the fetch gate's refusal)."""
    import json
    from atlantis_core.config import semantic_hash
    f = inst.root / RECEIPT
    if not f.exists():
        return f"no self-test receipt at {RECEIPT} — run `python -m atlantis_core.selftest --instance {inst.root}` first"
    try:
        rec = json.loads(f.read_text())
    except ValueError:
        return f"{RECEIPT} is not JSON"
    if rec.get("passed") is not True:
        return f"{RECEIPT} does not record a pass"
    h = semantic_hash(inst)
    if rec.get("semantic_hash") != h:
        return (f"{RECEIPT} is for config {rec.get('semantic_hash')!r}, the instance is now {h!r} — "
                f"vitals, label or grid changed since the self-test; re-run it (SO-7)")
    if rec.get("selftest_code") != selftest_code_hash():
        return (f"{RECEIPT} was earned under different self-test code ({rec.get('selftest_code')!r}, now "
                f"{selftest_code_hash()!r}) — re-run it")
    if sorted(rec.get("streams") or []) != sorted(inst.streams):
        return f"{RECEIPT} covers streams {rec.get('streams')}, the instance declares {sorted(inst.streams)}"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instance", required=True)
    ap.add_argument("--no-receipt", action="store_true", help="run without writing the fetch gate's receipt")
    a = ap.parse_args(argv)
    try:
        inst = load_instance(a.instance)
        res = run(inst)
    except LeakError as e:
        print(f"❌ {e}", file=sys.stderr); sys.exit(1)
    if not a.no_receipt:
        print(f"   receipt → {write_receipt(inst, res).relative_to(inst.root)} (the fetch CLI's gate, contract item 6)")


if __name__ == "__main__":
    main()

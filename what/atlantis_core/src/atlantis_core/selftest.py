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
  C9  (an event with `refractory_weeks` R > 0 — M-2a-i) the onset refractory bites and is the declared length: a crossing
      at the primary's week t−R sets already_in_event at t, one at t−R−1 does not (any unobserved week it could be carried
      through is filled first, and the result says so — never skipped, III F-3), and neither moves y. That it reads nothing AFTER t is C1's and C2's job — they
      already diff every already_in_event flag at weeks ≤ t. In the accumulating world (below) it also checks the past
      episode: at every primary week of it, the drop equals "the carried weekly signal crossed in w−R … w", recomputed from
      the synthetic frame, not from the label; the episode has a dip between two crossings (the flicker) and a gap of
      last_known_weeks + 1 weeks right after a crossing, so a raw-signal or row-counted refractory disagrees (III F-7).
  C6  REPORTED, not hidden: inside a climatology era a t+1 perturbation moves anomaly() vitals at earlier weeks — the era
      normal is one statistic over the whole era, so the same calendar week in EVERY earlier era year depends on it.
      Asserted: only anomaly() vitals move. Reported: cells, max |Δ|, real vs float residue (pandas' running-sum rolling
      mean leaves ~1e-15). Registry R7 keeps eras before validation.

The event stream may have any shape (M-1d-i: a station-keyed `below` event — hypoxia — was the dry run's first finding;
until then the synthetic world placed event values against the threshold, and spiked them, for point streams only). Its
synthetic values sit on the safe side of a POSITIVE threshold; a spike is ONE observation per entity past it (for a daily
stream, one date set across every selected entity, so a mean over stations crosses too). A threshold ≤ 0 is refused here.

Event series (M-2a-i): `selftest.event_series` is `iid` (values drawn independently each day on the safe side of the
threshold — every world before M-2a-i) or `accumulating` (a DHW-like trailing 12-week sum of a non-negative daily
"hotspot": persistent, and carrying one past episode that crosses, dips below and re-crosses well before t). The default
is `accumulating` for an `above` event with R > 0 on a `unit_daily` event stream, `iid` otherwise; the world used is recorded in
the result and the receipt (computed, C-023). The mirror-direction world (C5) is always `iid`.

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
SERIES = ("iid", "accumulating")
EPISODE_START_WEEKS = 60   # the accumulating world's past episode starts this many weeks before t …
EPISODE_A, EPISODE_B = (0, 6, 0.22), (16, 18, 0.6)
EPISODE_GAP_AFTER = 27     # III F-7: the primary's event stream is unobserved for last_known_weeks + 1 weeks after episode
                           # week 27 (a crossing week: 1.20·thr all week) — carried and raw refractories then disagree   # … hotspot blocks (first week, end week, level × threshold). Weekly
# maxima (× thr, simulated at M-2a-i): crossing from episode week 4 to 13 (peak 1.32), a three-week dip 14–16 (0.85 · 0.63 ·
# 0.82), re-crossing 17–28 (the flicker: 1.20), below from 29, baseline from 30 — all ≥ 30 weeks before t.


def event_series(inst: Instance) -> str:
    """Which synthetic event series the world uses (module docstring). Refuses a combination it cannot honour."""
    from atlantis_core.label import refractory
    ev = inst.event
    shape = inst.stream_spec(ev["event_variable_stream"])["shape"]
    want = (inst.cfg.get("selftest") or {}).get("event_series")
    if want is None:
        return "accumulating" if refractory(ev) and ev["direction"] == "above" and shape == "unit_daily" else "iid"
    if want not in SERIES:
        raise ValueError(f"selftest.event_series {want!r} — expected one of {SERIES}")
    if want == "accumulating" and (ev["direction"] != "above" or shape != "unit_daily"):   # III F-6: station frames have no unit
        raise ValueError("selftest.event_series accumulating synthesises an ABOVE event on a unit_daily event stream "
                         f"(this event: {ev['direction']}, shape {shape})")
    return want


def _accumulating(days: pd.DatetimeIndex, t: pd.Timestamp, thr: float, rng) -> np.ndarray:
    """A DHW-like series: the trailing 84-day sum of a daily hotspot, / 7 (°C-weeks from °C). Baseline hotspot keeps the
    sum ≤ 0.05·thr (the safe side, as in the iid world); the episode blocks are EPISODE_A / EPISODE_B."""
    hot = rng.uniform(0, 0.05 * thr / 12, len(days))
    e0 = week_start([t - W(EPISODE_START_WEEKS)]).iloc[0]
    for w0, w1, lvl in (EPISODE_A, EPISODE_B):
        hot[(days >= e0 + W(w0)) & (days < e0 + W(w1))] = lvl * thr
    return pd.Series(hot).rolling(84, min_periods=1).sum().to_numpy() / 7.0


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


def synth(inst: Instance, t: pd.Timestamp, seed: int = 0, series: str | None = None) -> dict:
    """Raw frames in the instance's own columns, normalised through the real path."""
    rng = np.random.default_rng(seed)
    series = series or event_series(inst)
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
            gaps_daily = {k: set(v) for k, v in gaps_point.items()}
            if series == "accumulating":
                e0 = week_start([t - W(EPISODE_START_WEEKS)]).iloc[0]
                lk = int(inst.cfg["label"]["last_known_weeks"])
                gaps_daily[0] |= {e0 + W(EPISODE_GAP_AFTER + 1 + j) for j in range(lk + 1)}
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
                    v = (_accumulating(days, t, float(ev["threshold"]), rng) if series == "accumulating" else
                         rng.uniform(*_event_band(ev), len(days)))       # the safe side of the threshold, every day
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


def _fill(frames, inst, sid, week, units):
    """Insert one SAFE-side observation (the week's Monday) for each entity of `units` that has none in that week — a
    probe-local edit that removes a declared gap, so a carried value cannot ride through it (M-2a-i III F-3)."""
    f = {k: v.copy() for k, v in frames.items()}
    d = f[sid]
    key = "station" if inst.stream_spec(sid)["shape"] == "station_daily" else "unit"
    lo, hi = _event_band(inst.event)
    seen = set(d.loc[d["date"].between(week, week + pd.Timedelta(days=6)) & _entity_mask(inst, sid, d, units), key])
    add = [e for e in _entities(inst, sid, units) if e not in seen]
    if add:
        f[sid] = pd.concat([d, pd.DataFrame({"date": week, key: add, "value": (lo + hi) / 2})], ignore_index=True)
    return f, len(add)


def _c9(inst, frames, base, B, P, t, R, series, ev_sid, say) -> dict:
    out = {}
    bR = at(B(perturb(frames, inst, ev_sid, t - W(R), units=[P])), inst, P, t)
    if not _eq(bR["already_in_event"], True):
        raise LeakError(f"C9 refractory: a crossing at t−{R} (R = refractory_weeks) did not set already_in_event at "
                        f"(primary, t) — the refractory is ignored or shorter than declared")
    if moved(base, bR, ["y", "outcome_unknown"]):
        raise LeakError(f"C9 refractory: a crossing at t−{R} moved the label at (primary, t): {moved(base, bR, ['y', 'outcome_unknown'])}")
    # III F-3: never skipped. A crossing at t−R−1 may legitimately be CARRIED into t−R … only through unobserved weeks; the
    # probe fills any of the primary's unobserved weeks in t−R … t−R+lk−1 first (and says how many), then asserts.
    lk = int(inst.cfg["label"]["last_known_weeks"])
    fb, filled = frames, 0
    for j in range(lk):
        fb, n = _fill(fb, inst, ev_sid, t - W(R - j), [P]); filled += n
    bR1 = at(B(perturb(fb, inst, ev_sid, t - W(R + 1), units=[P])), inst, P, t)
    if not _eq(bR1["already_in_event"], False):
        raise LeakError(f"C9 refractory: a crossing at t−{R + 1} set already_in_event at (primary, t) — the refractory "
                        f"is longer than the declared {R} weeks")
    out["boundary"] = "ok" if not filled else f"ok ({filled} unobserved week(s) in t−{R}…t−{R - lk + 1} filled first)"
    out["bites"] = "ok"
    if series == "accumulating":
        out["episode"] = _c9_episode(inst, frames, B(frames), P, t, R)
    e = out.get("episode")
    say(f"C9 ✅ refractory R = {R}: a crossing at t−{R} drops (primary, t), at t−{R + 1} not ({out['boundary']}); y unmoved"
        + (f" · episode: {e['crossing_runs']} crossing runs, a {e['gap_weeks']}-week gap after a crossing, "
           f"{e['dropped_by_refractory']} weeks dropped by the refractory alone, {e['dip_weeks_dropped']}/{e['dip_weeks']} "
           f"dip weeks dropped" if e else " · episode: n/a (iid world)"))
    return out


EPISODE_AGG = {"weekly_max": "max", "weekly_min": "min", "weekly_mean": "mean", "weekly_median": "median"}


def _c9_episode(inst, frames, tab, P, t, R) -> dict:
    """The accumulating world's past episode, checked against the RAW frame, not the label's code. At every primary week
    from the episode's start to lk + R + 2 weeks past its last crossing, already_in_event must equal 'the CARRIED weekly
    signal (ffill, limit lk) crossed at some week in w−R … w' — the documented rule. The world puts a gap of lk + 1 weeks
    right after a crossing (EPISODE_GAP), so a refractory on the raw signal, or counted in observed rows, disagrees
    (III F-7). The signal must be weekly_{max,min,mean,median}(value); anything else is refused, not skipped (III F-3)."""
    sig = inst.cfg["label"]["signal"].replace(" ", "")
    agg = next((v for k, v in EPISODE_AGG.items() if sig == f"{k}(value)"), None)
    if agg is None:
        raise LeakError(f"C9 episode: cannot recompute label.signal {inst.cfg['label']['signal']!r} from the raw frame — "
                        f"declare selftest.event_series: iid to run without the episode check (it is then recorded as iid)")
    thr = float(inst.event["threshold"]); lk = int(inst.cfg["label"]["last_known_weeks"])
    d = frames[inst.event["event_variable_stream"]]
    d = d[d["unit"] == P]
    e0 = week_start([t - W(EPISODE_START_WEEKS)]).iloc[0]
    weekly = d.groupby(week_start(d["date"]).values)["value"].agg(agg)
    full = weekly.reindex(pd.date_range(e0 - W(R + lk + 2), t, freq="7D"))
    cross = full.ffill(limit=lk).ge(thr)                         # NaN (beyond the carry) is not a crossing
    raw_cross = full.ge(thr)
    if not raw_cross.any():
        raise LeakError("C9 episode: the accumulating world never crossed — the episode is vacuous")
    cw = set(raw_cross[raw_cross].index)
    carried = set(cross[cross].index)
    runs = sum(1 for w in sorted(cw) if (w - W(1)) not in cw)
    if runs < 2:
        raise LeakError(f"C9 episode: {runs} crossing run — the world has no flicker for the refractory to act on")
    weeks = pd.date_range(e0, max(cw) + W(lk + R + 2), freq="7D")
    gap = [w for w in weeks if pd.isna(full.get(w))]
    if len(gap) <= lk:
        raise LeakError(f"C9 episode: the episode's gap is {len(gap)} weeks, not > last_known_weeks ({lk}) — carried and raw "
                        f"refractories would agree (III F-7)")
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    rows = tab[(tab[ucol] == P) & tab["week"].isin(weeks)].set_index("week")["already_in_event"]
    bad, by_r = [], 0
    for w in weeks:
        exp = any((w - W(j)) in carried for j in range(R + 1))
        got = bool(rows.get(w, False))
        if got != exp:
            bad.append(f"{w.date()}: expected {exp}, label {got}")
        by_r += exp and w not in carried
    if bad:
        raise LeakError(f"C9 episode: already_in_event disagrees with 'carried signal crossed in w−{R}…w' on the raw frame: {bad[:4]}")
    first, last = min(cw), max(cw)
    dips = [w for w in weeks if first < w < last and w not in cw and w not in gap]
    return {"checked": True, "signal": sig, "crossing_runs": runs, "weeks": len(weeks), "gap_weeks": len(gap),
            "dropped_by_refractory": int(by_r), "dip_weeks": len(dips),
            "dip_weeks_dropped": int(sum(bool(rows.get(w, False)) for w in dips))}


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
    series = event_series(inst)
    from atlantis_core.label import refractory
    R = refractory(inst.event)
    frames = synth(inst, t, series=series)
    base_tab, _ = build(inst, frames)
    B = lambda f: build(inst, f)[0]
    base = at(base_tab, inst, P, t)
    res = {"streams": {}, "vitals": len(feats), "patients": [p["unit"] for p in ps], "event_series": series,
           "refractory_weeks": R}

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

    # C9 — the onset refractory bites, at its declared length, and never moves y (M-2a-i)
    res["C9"] = _c9(inst, frames, base, B, P, t, R, series, ev_sid, say) if R else "n/a: no refractory_weeks declared"

    # C5 — the event in the MIRROR direction on the same streams (an above instance tests below, and vice versa)
    mirror = "below" if inst.event["direction"] == "above" else "above"
    mi = copy.deepcopy(inst)
    mi.event["direction"] = mirror
    mi.cfg["label"]["signal"] = "weekly_min(value)" if mirror == "below" else "weekly_max(value)"
    fb = synth(mi, t, seed=1, series="iid")
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
           **{k: res[k] for k in ("event_series", "refractory_weeks", "C9") if k in res},   # what run() computed (M-2a-i, III F-3)
           "passed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    tmp = out.with_suffix(".tmp"); tmp.write_text(json.dumps(rec, indent=1) + "\n"); tmp.rename(out)
    return out


def selftest_code_hash() -> str:
    """sha256 (12 hex) over the code a receipt vouches for: this file, the label, the vitals evaluator and the grid. A receipt
    earned under a weaker self-test is not a receipt for the current one (M-1d-i III F-1)."""
    import hashlib
    here = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for f in ("selftest.py", "label/__init__.py", "vitals/ops.py", "vitals/build.py", "vitals/grammar.py",
              "grid/__init__.py", "grid/polygons.py"):   # III F-8: receipts vouch for the pin check and unit assignment too
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
    try:
        h = semantic_hash(inst)
    except ValueError as e:   # III M-1f F-6: a malformed config (e.g. a partial embargo) is a refusal, not a traceback
        return f"the instance's config cannot be hashed ({e}) — fix it, then re-run the self-test"
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

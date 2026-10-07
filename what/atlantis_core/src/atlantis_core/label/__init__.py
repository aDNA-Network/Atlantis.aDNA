"""The direction-aware onset label — the only code in atlantis_core that looks past week t.

From `events.yaml` (threshold · direction · horizon) and `atlantis.yaml → label`:
    signal        transform (grammar) of the event stream read for the event, e.g. weekly_max(value)
    presence      transform counting observations, e.g. weekly_count(value) — 0 means "nobody looked"
    last_known_weeks   how far the last observed signal is carried forward for the already-in-event drop

    above: y = max(signal[t+1..t+H]) >= threshold ; already_in_event = carried signal[t] >= threshold
    below: y = min(signal[t+1..t+H]) <= threshold ; already_in_event = carried signal[t] <= threshold
    y is NA where no week in t+1..t+H has a signal; outcome_unknown = presence summed over t+1..t+H == 0.

Onset refractory (`events.yaml → refractory_weeks`, R, atl_v0 0.5.0, M-2a-i; absent = 0): already_in_event becomes "the
carried signal crossed at ANY of t−R … t". R = 0 is the rule above, computed by the same expression, so a config without R
labels byte-identically. For a persistent event (DHW accumulates for weeks, decays, can re-cross) R stops a flicker from
counting as a fresh onset; R = H makes the label's onset the one `eval/lead.py` counts (no crossing in the previous H
weeks). It reads only the past — the self-test's C9 proves it.

`finalize` applies the modelling filters (split years; drop already-in-event; drop unknown outcome) and reports BOTH
drop counts (SO-9's honesty applies to denominators too).
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.vitals import grammar

DIRECTIONS = ("above", "below")


def _cut(df: pd.DataFrame, units, weeks) -> pd.Series:
    return pd.Series(df.reindex(weeks)[units].to_numpy().T.reshape(-1))


def refractory(ev: dict) -> int:
    """`refractory_weeks` of an event definition: absent / null → 0; anything not a whole number ≥ 0 is refused."""
    r = ev.get("refractory_weeks")
    if r is None:
        return 0
    if isinstance(r, bool) or not isinstance(r, int) or r < 0:
        raise ValueError(f"refractory_weeks {r!r} — a whole number of weeks ≥ 0 (atl_v0 0.5.0)")
    return r


def make(inst, table: pd.DataFrame, evs: dict, units, weeks, event: dict | None = None, lcfg: dict | None = None):
    ev = event or inst.event
    lcfg = lcfg or inst.cfg["label"]
    direction, thr, H = ev["direction"], float(ev["threshold"]), int(ev["horizon"])
    R = refractory(ev)
    if direction not in DIRECTIONS:
        raise ValueError(f"direction {direction!r} — expected above | below")
    e = evs[ev["event_variable_stream"]]
    consts = list(inst.cfg.get("constants", {}))
    sig = e.weekly(grammar.parse(lcfg["signal"], consts, "label.signal"))
    pres = e.weekly(grammar.parse(lcfg["presence"], consts, "label.presence"))

    fut = pd.concat([sig.shift(-k) for k in range(1, H + 1)], keys=range(1, H + 1))
    fut_sig = fut.groupby(level=1).max() if direction == "above" else fut.groupby(level=1).min()
    fut_sig = fut_sig.reindex(sig.index)
    n_future = sum(pres.shift(-k).fillna(0) for k in range(1, H + 1))
    last_known = sig.ffill(limit=int(lcfg["last_known_weeks"]))

    hit = fut_sig.ge(thr) if direction == "above" else fut_sig.le(thr)
    in_event = last_known.ge(thr) if direction == "above" else last_known.le(thr)
    if R:
        in_event = in_event | sum(in_event.shift(k, fill_value=False).astype(int) for k in range(1, R + 1)).gt(0)

    t = table.copy()
    t["future_signal"] = _cut(fut_sig, units, weeks).values
    t["last_known_signal"] = _cut(last_known, units, weeks).values
    t["y"] = _cut(hit, units, weeks).astype(float).astype("Int64").values
    t.loc[t["future_signal"].isna(), "y"] = pd.NA
    t["already_in_event"] = _cut(in_event, units, weeks).fillna(False).astype(bool).values
    t["outcome_unknown"] = _cut(n_future, units, weeks).eq(0).values
    return t


def finalize(inst, table: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    s = inst.cfg["split"]
    y = table["week"].dt.year
    base = table[(y >= s["min_train_year"]) & (y <= s["test_end"])]
    report = {"patient_weeks_in_window": int(len(base))}
    m = base[~base["already_in_event"]]
    report["dropped_already_in_event"] = int(len(base) - len(m))
    m2 = m[~m["outcome_unknown"]]
    report["dropped_outcome_unknown"] = int(len(m) - len(m2))
    unlabelled = int(m2["y"].isna().sum())
    if unlabelled:   # presence said "observed" but the signal is NaN: positives and prevalence would use different denominators
        raise ValueError(f"finalize: {unlabelled} kept rows have no label — label.presence and label.signal disagree")
    report["modelling_rows"] = int(len(m2))
    report["positives"] = int(m2["y"].sum())
    report["prevalence"] = float(m2["y"].mean())
    return m2.reset_index(drop=True), report

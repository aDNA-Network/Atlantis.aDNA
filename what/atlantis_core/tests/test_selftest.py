"""SO-7: the all-stream self-test passes on the exemplar — and FAILS when a leak is planted (M-1c lesson: an instrument
is only trusted once it has been seen to fail). Each sabotage plants one defect and must be caught by the named check
— the FIRST check that fails, so a leak that also breaks the synthetic world's non-vacuity (C4) or a vital's response
(C0) is named there."""
import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance, label
from atlantis_core import selftest as st
from atlantis_core.vitals import ops


@pytest.fixture(scope="module")
def inst(exemplar_dir):
    return load_instance(exemplar_dir)


def test_selftest_passes(inst):
    r = st.run(inst, verbose=False)
    assert set(r["streams"]) == set(inst.streams)                       # every registered stream perturbed
    assert sum(v["C0_vitals"] for v in r["streams"].values()) == 23          # every vital that reads `value` (25 − 2 harmonics)
    assert r["C5"] == "ok"
    assert all(v["C7"] == "ok" for v in r["streams"].values())                # every stream isolable across units
    real = {sid: {k for k, v in mv.items() if v[4] > 0} for sid, mv in r["C6"].items()}
    assert real == {"atl_stream_oisst_region_daily": {"sst_anom_t0", "sst_anom_t2", "sst_anom_t4"},
                    "atl_stream_usgs_discharge_daily": {"discharge_anom_t0"}}


def _sabotage(monkeypatch, cls_or_mod, name, fn):
    monkeypatch.setattr(cls_or_mod, name, fn)


@pytest.mark.parametrize("name,fn,check", [
    # a rolling window that peeks one week ahead (centre=True-style leak)
    ("f_rolling_max", lambda self, x, window=None: ops.Weekly(self._weekly(x, "r").shift(-1).rolling(int(window), min_periods=1).max()), "C1"),
    # diff against the FUTURE instead of the past
    ("f_diff", lambda self, x, window=None: ops.Weekly(self._weekly(x, "d") - self._weekly(x, "d").shift(-int(window))), "C4"),   # reads t+2, unobserved → NaN at t
    # sampling the week's daily stream one day late (Monday of t+1 instead of Sunday of t)
    ("f_at_week_end", lambda self, x, window=None: ops.Weekly(pd.DataFrame(self._to_units(x).reindex(self.weekly_index + pd.Timedelta(days=7)).values, index=self.weekly_index, columns=self.units)), "C1|C8"),   # M-1d-i: C8 now sees it first (the late sample reads a deleted week)
    # a weekly mean that includes next week
    ("f_weekly_mean", lambda self, x, window=None: ops.Weekly((lambda w: (w + w.shift(-1)) / 2)(self._aggregate(x, "mean").df)), "C4"),   # t−2 mean reads t−1, a daily gap
    # a count that sees the whole future
    ("f_weekly_count", lambda self, x, window=None: ops.Weekly(self._aggregate(x, "count", fill=0).df.iloc[::-1].cumsum().iloc[::-1]), "C0"),   # weeks_since_sample goes inert
])
def test_selftest_catches_planted_vital_leak(inst, monkeypatch, name, fn, check):
    monkeypatch.setattr(ops.Evaluator, name, fn)
    with pytest.raises(st.LeakError, match=check):
        st.run(inst, verbose=False)


def test_selftest_catches_horizon_overreach(inst, monkeypatch):
    """Label looks one step past the horizon → C2 must fail."""
    orig = label.make
    def overreach(inst_, table, evs, units, weeks, event=None, lcfg=None):
        ev = dict(event or inst_.event); ev["horizon"] = int(ev["horizon"]) + 1
        return orig(inst_, table, evs, units, weeks, event=ev, lcfg=lcfg)
    monkeypatch.setattr(label, "make", overreach)
    with pytest.raises(st.LeakError, match="C2"):
        st.run(inst, verbose=False)


def test_selftest_catches_deaf_label(inst, monkeypatch):
    """A label that never fires → C1 (label must respond to a t+1 event)."""
    orig = label.make
    def deaf(*a, **k):
        t = orig(*a, **k); t["y"] = t["y"] * 0; return t
    monkeypatch.setattr(label, "make", deaf)
    with pytest.raises(st.LeakError, match="C1"):
        st.run(inst, verbose=False)


def test_selftest_catches_vacuous_build(inst, monkeypatch):
    """If a stream's vitals come out NaN the test would pass trivially → C4 must refuse."""
    monkeypatch.setattr(ops.Evaluator, "f_weekly_mean",
                        lambda self, x, window=None: ops.Weekly(self._aggregate(x, "mean").df * np.nan))
    with pytest.raises(st.LeakError, match="C4"):
        st.run(inst, verbose=False)


def test_selftest_catches_non_anomaly_era_dependence(inst, monkeypatch):
    """A vital that is not anomaly() but uses a whole-era statistic → C6 must refuse (only anomaly() is declared)."""
    def era_mean(self, x, window=None):
        w = self._aggregate(x, "mean").df
        return ops.Weekly(w - w[(w.index.year >= 1982) & (w.index.year <= 2011)].mean())
    monkeypatch.setattr(ops.Evaluator, "f_weekly_mean", era_mean)
    with pytest.raises(st.LeakError, match="C6"):
        st.run(inst, verbose=False)


# --- the six defects the M-1b-i III review demonstrated passing the first self-test (F-1 … F-4); each must now be caught
from atlantis_core.config import feature_name
from atlantis_core.vitals import build as B, grammar


def _label_variant(mode):
    orig = label.make
    def make(inst_, table, evs, units, weeks, event=None, lcfg=None):
        ev = dict(event or inst_.event); lc = lcfg or inst_.cfg["label"]
        if mode == "short_horizon":
            ev["horizon"] = int(ev["horizon"]) - 1
            return orig(inst_, table, evs, units, weeks, event=ev, lcfg=lcfg)
        t = orig(inst_, table, evs, units, weeks, event=event, lcfg=lcfg)
        sig = evs[ev["event_variable_stream"]].weekly(grammar.parse(lc["signal"], list(inst_.cfg.get("constants", {}))))
        thr = float(ev["threshold"])
        if mode == "label_rowshift":           # horizon counted in OBSERVED weeks
            fs = {}
            for u in sig.columns:
                x = sig[u].dropna()
                fut = pd.concat([x.shift(-k) for k in range(1, int(ev["horizon"]) + 1)], axis=1)
                fs[u] = (fut.max(axis=1) if ev["direction"] == "above" else fut.min(axis=1)).reindex(sig.index)
            fsig = pd.DataFrame(fs)
            hit = fsig.ge(thr) if ev["direction"] == "above" else fsig.le(thr)
            t["y"] = label._cut(hit, units, weeks).astype(float).astype("Int64").values
            t.loc[label._cut(fsig, units, weeks).isna().values, "y"] = pd.NA
            return t
        lk = sig.shift(-1).ffill(limit=4) if mode == "in_event_next_week" else sig.bfill(limit=4)
        ie = lk.ge(thr) if ev["direction"] == "above" else lk.le(thr)
        t["already_in_event"] = label._cut(ie, units, weeks).fillna(False).astype(bool).values
        return t
    return make


def _build_weekmajor(inst_, frames, with_label=True):
    units, weeks = B.patient_grid(inst_, frames)
    evs = {sid: B.evaluator(inst_, sid, frames, units, weeks) for sid in inst_.streams}
    table = pd.MultiIndex.from_product([units, weeks], names=[inst_.cfg["grid"].get("unit_column", "unit"), "week"]).to_frame(index=False)
    for v in inst_.vitals:
        w = evs[v["stream_ref"]].weekly(grammar.parse(v["transform"], list(inst_.cfg.get("constants", {}))), v.get("window"), v.get("lag", 0)).reindex(weeks)
        table[feature_name(v)] = w[units].to_numpy().reshape(-1)        # week-major into a unit-major table
    return (label.make(inst_, table, evs, units, weeks) if with_label else table), {}


def _wsgt_forward(self, x, thr, window=None):        # weeks UNTIL the next sample
    df = self._weekly(x, "w"); flag = df.gt(thr)
    return ops.Weekly(pd.DataFrame({c: ops.weeks_since(flag[c].to_numpy(dtype=bool)[::-1], self.cap)[::-1] for c in df.columns},
                                   index=df.index).astype(float))


@pytest.mark.parametrize("mode,check", [
    ("in_event_next_week", "C1"),      # F-1: the row filter reads next week
    ("in_event_bfill", "C1"),          # F-3: back-filled last-known state (neighbour unobserved at t)
    ("label_rowshift", "C2"),          # F-3: horizon in observed weeks (primary unobserved at t+2)
    ("short_horizon", "C2b"),          # F-4: label looks H−1 ahead
])
def test_review_label_sabotages_caught(inst, monkeypatch, mode, check):
    monkeypatch.setattr(label, "make", _label_variant(mode))
    with pytest.raises(st.LeakError, match=check):
        st.run(inst, verbose=False)


def test_review_weekmajor_caught(inst, monkeypatch):            # F-2: cross-unit / cross-time scramble
    monkeypatch.setattr(st, "build", _build_weekmajor)
    with pytest.raises(st.LeakError):
        st.run(inst, verbose=False)


def test_review_weeks_until_next_sample_caught(inst, monkeypatch):   # F-3
    monkeypatch.setattr(ops.Evaluator, "f_weeks_since_gt", _wsgt_forward)
    with pytest.raises(st.LeakError, match="C1|C3"):
        st.run(inst, verbose=False)


def test_row_lag_instead_of_calendar_caught(inst, monkeypatch):
    """The hab SST defect class: lag counted in OBSERVED rows. Since M-1d-i, C8 (calendar-lag invariance) catches it on the
    first stream with a lag ≥ 1, before C0 reaches the daily gap; either name is a catch."""
    orig = ops.Evaluator.weekly
    def rowlag(self, node, window=None, lag=0):
        df = orig(self, node, window, 0)
        return df.apply(lambda c: c.dropna().shift(int(lag or 0)).reindex(c.index))
    monkeypatch.setattr(ops.Evaluator, "weekly", rowlag)
    with pytest.raises(st.LeakError, match="C8|C0"):
        st.run(inst, verbose=False)


def test_finalize_refuses_unlabelled_rows(inst):
    t = pd.DataFrame({"week": pd.to_datetime(["2000-01-03"] * 2), "already_in_event": [False, False],
                      "outcome_unknown": [False, False], "y": pd.array([1, pd.NA], dtype="Int64")})
    with pytest.raises(ValueError, match="no label"):
        label.finalize(inst, t)


def test_backfilled_weekly_mean_caught(inst, monkeypatch):
    """M-1d-i III F-1 (pre-existing): a weekly mean back-filled from next week passed while no daily stream left the
    neighbour unobserved at t. The neighbour's daily gaps are now t−1 and t."""
    monkeypatch.setattr(ops.Evaluator, "f_weekly_mean",
                        lambda self, x, window=None: ops.Weekly(self._aggregate(x, "mean").df.bfill(limit=2)))
    with pytest.raises(st.LeakError, match="C1 LEAK"):
        st.run(inst, verbose=False)

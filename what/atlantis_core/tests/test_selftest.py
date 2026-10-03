"""SO-7: the all-stream self-test passes on the exemplar — and FAILS when a leak is planted (M-1c lesson: an instrument
is only trusted once it has been seen to fail). Each sabotage plants one defect and must be caught by the named check."""
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
    assert all(v["C0_moved_at_t"] > 0 for v in r["streams"].values())
    assert r["C5"] == "ok"
    real = {sid: {k for k, v in mv.items() if v[4] > 0} for sid, mv in r["C6"].items()}
    assert real == {"atl_stream_oisst_region_daily": {"sst_anom_t0", "sst_anom_t2", "sst_anom_t4"},
                    "atl_stream_usgs_discharge_daily": {"discharge_anom_t0"}}


def _sabotage(monkeypatch, cls_or_mod, name, fn):
    monkeypatch.setattr(cls_or_mod, name, fn)


@pytest.mark.parametrize("name,fn,check", [
    # a rolling window that peeks one week ahead (centre=True-style leak)
    ("f_rolling_max", lambda self, x, window=None: ops.Weekly(self._weekly(x, "r").shift(-1).rolling(int(window), min_periods=1).max()), "C1"),
    # diff against the FUTURE instead of the past
    ("f_diff", lambda self, x, window=None: ops.Weekly(self._weekly(x, "d") - self._weekly(x, "d").shift(-int(window))), "C1"),
    # sampling the week's daily stream one day late (Monday of t+1 instead of Sunday of t)
    ("f_at_week_end", lambda self, x, window=None: ops.Weekly(pd.DataFrame(self._to_units(x).reindex(self.weekly_index + pd.Timedelta(days=7)).values, index=self.weekly_index, columns=self.units)), "C1"),
    # a weekly mean that includes next week
    ("f_weekly_mean", lambda self, x, window=None: ops.Weekly((lambda w: (w + w.shift(-1)) / 2)(self._aggregate(x, "mean").df)), "C1"),
    # a count that sees the whole future
    ("f_weekly_count", lambda self, x, window=None: ops.Weekly(self._aggregate(x, "count", fill=0).df.iloc[::-1].cumsum().iloc[::-1]), "C1"),
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

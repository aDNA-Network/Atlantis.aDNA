"""M-3b-ii-b-1: a stream's QC mask, station windows and era-fitted station offsets (core 0.11.0).

The FKNMS wind stream carries flag columns and a reporting set that changes by era (M-3b-ii-a III F-1, F-2, F-8). These
tests hold the three keys to what they claim: a flagged day is masked (NaN), never zero; a window drops rows; an offset
is the mean paired difference over the era, subtracted before the station → unit mean; the era obeys R7; the self-test
reports the era's dependence and refuses a week too close to it.
"""
from __future__ import annotations

import copy, shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from atlantis_core import registry
from atlantis_core.config import load_instance, semantic_hash
from atlantis_core.vitals import grammar
from atlantis_core.vitals.build import normalise
from atlantis_core.vitals.ops import Daily, Evaluator
from atlantis_core.grid import patient_weeks, week_start

WIND = "atl_stream_example_wind_daily"
WIND_STATIONS = {"W1": [1, 2], "W2": [1, 2], "W3": [1, 2]}      # Keys-wide: every station feeds every unit


# ── a forked instance with a reef-light-like wind stream ───────────────────────────────────────────────────────────────
def add_wind(d: Path, *, mask=True, offsets=True, windows=True, vitals=True) -> Path:
    cfg = yaml.safe_load((d / "atlantis.yaml").read_text())
    spec = {"shape": "station_daily", "artifact": "data/raw/example_wind_daily.parquet",
            "columns": {"date": "date", "value": "wspd", "station": "station"}, "stations": copy.deepcopy(WIND_STATIONS)}
    if mask:
        spec["mask_columns"] = ["qc_low_ratio_causal"]
    if offsets:
        spec["station_offsets"] = {"reference": "W1", "era": [2006, 2012], "min_days": 30}
    if windows:
        spec["station_windows"] = {"W3": [None, "2019-06-30"]}
    cfg["streams"][WIND] = spec
    cfg["constants"] = {**(cfg.get("constants") or {}), "calm": 4.0}
    (d / "atlantis.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    st = yaml.safe_load((d / "streams.yaml").read_text())
    st["observation_streams"].append({
        "stream_id": WIND, "fetcher": "NDBCStdmet", "modality": "buoy_series", "source_system": "illustrative",
        "source_id": "W1 · W2 · W3 (illustrative)", "authority": "CF:wind_speed", "variable": "wind_speed", "unit": "m/s",
        "license": "public (illustrative)", "surveillance_channel": False})
    (d / "streams.yaml").write_text(yaml.safe_dump(st, sort_keys=False))
    if vitals:
        fe = yaml.safe_load((d / "features.yaml").read_text())
        for vid, tr, lag in (("wind_mean_t0", "weekly_mean(value)", 0), ("wind_mean_t1", "weekly_mean(value)", 1),
                             ("wind_calm_t0", "weekly_count_lt(value, calm)", 0)):
            fe["vitals"].append({"vital_id": f"atl_vital_example_{vid}", "name": vid, "description": "test",
                                 "stream_ref": WIND, "transform": tr, "lag": lag, "group": "wind", "tag": "proxy"})
        (d / "features.yaml").write_text(yaml.safe_dump(fe, sort_keys=False))
    return d


@pytest.fixture
def windy(variant_master, tmp_path):
    d = tmp_path / "inst"
    shutil.copytree(variant_master, d)
    return add_wind(d)


# ── evaluator, by hand ─────────────────────────────────────────────────────────────────────────────────────────────────
def _ev(df, **kw):
    weeks = patient_weeks(week_start([df["date"].min()]).iloc[0], week_start([df["date"].max()]).iloc[0])
    return Evaluator("s", df, "station_daily", weeks, [1], {"calm": 4.0}, stations={"A": [1], "B": [1], "C": [1]}, **kw)


def _frame(days, values: dict, flags: dict | None = None):
    parts = []
    for st, v in values.items():
        part = pd.DataFrame({"date": days, "station": st, "value": v})
        part["qc_low_ratio"] = (flags or {}).get(st, np.zeros(len(days), bool))
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def test_mask_blanks_flagged_days_and_never_zero_fills():
    days = pd.date_range("2020-01-06", periods=14, freq="D")            # two ISO weeks
    flag = np.zeros(14, bool); flag[:7] = True                           # station A: its whole first week flagged
    df = _frame(days, {"A": np.full(14, 1.0)}, {"A": flag})
    e = _ev(df, mask_columns=["qc_low_ratio"])
    calm = e.weekly(grammar.parse("weekly_count_lt(value, calm)", ["calm"]))
    mean = e.weekly(grammar.parse("weekly_mean(value)", []))
    assert np.isnan(calm.loc["2020-01-06", 1]) and np.isnan(mean.loc["2020-01-06", 1])   # masked → no week, not 0 calm days
    assert calm.loc["2020-01-13", 1] == 7 and mean.loc["2020-01-13", 1] == 1.0
    unmasked = _ev(df).weekly(grammar.parse("weekly_count_lt(value, calm)", ["calm"]))
    assert unmasked.loc["2020-01-06", 1] == 7                                               # the flag is what blanked it


def test_mask_reads_the_flag_not_the_value():
    days = pd.date_range("2020-01-06", periods=7, freq="D")
    flag = np.zeros(7, bool); flag[3] = True
    df = _frame(days, {"A": np.arange(7.0) + 10, "B": np.full(7, 10.0)}, {"A": flag})
    d = _ev(df, mask_columns=["qc_low_ratio"])._value()
    assert np.isnan(d.df.loc["2020-01-09", "A"]) and d.df.loc["2020-01-09", "B"] == 10.0
    assert d.df["A"].notna().sum() == 6


def test_window_drops_rows_outside_it():
    days = pd.date_range("2020-01-01", periods=10, freq="D")
    df = _frame(days, {"A": np.full(10, 2.0), "B": np.full(10, 3.0)})
    d = _ev(df, station_windows={"B": [None, "2020-01-05"], "A": ["2020-01-03", None]})._value().df
    assert d["B"].notna().sum() == 5 and d["B"].last_valid_index() == pd.Timestamp("2020-01-05")
    assert d["A"].first_valid_index() == pd.Timestamp("2020-01-03")


def test_offsets_are_the_era_mean_paired_difference_and_restore_the_level():
    rng = np.random.default_rng(0)
    days = pd.date_range("2010-01-01", "2013-12-31", freq="D")
    a = 5 + rng.normal(0, 1, len(days))
    era = days.year <= 2011
    vals = {"A": np.where(era, a, np.nan),          # the reference reports only in the era
            "B": a + 1.0 + rng.normal(0, 0.1, len(days)),
            "C": a - 2.0 + rng.normal(0, 0.1, len(days))}
    df = _frame(days, vals).dropna(subset=["value"])
    e = _ev(df, station_offsets={"reference": "A", "era": [2010, 2011], "min_days": 30})
    d = e._value()
    off = e.offsets
    assert off["A"] == {"offset": 0.0, "n_days": int(era.sum())}
    assert off["B"]["offset"] == pytest.approx(1.0, abs=0.02) and off["C"]["offset"] == pytest.approx(-2.0, abs=0.02)
    assert off["B"]["n_days"] == int(era.sum())
    exact_b = float(np.mean((vals["B"] - a)[era]))
    assert off["B"]["offset"] == pytest.approx(exact_b, abs=1e-12)
    unit = e._to_units(d)[1]
    after = days.year >= 2012                       # only B and C report: the corrected mean is A's level, not +1 − 2
    assert np.abs(unit[after].to_numpy() - a[after]).max() < 0.4
    raw = _ev(df)._to_units(_ev(df)._value())[1]
    assert np.abs(raw[after].to_numpy() - a[after]).mean() > 0.4     # without offsets the level is off by the mix


def test_offset_reads_only_the_era():
    """B drifts after the era (+1 → +1.5): the offset is the era's +1, not the whole record's mean."""
    days = pd.date_range("2010-01-01", "2013-12-31", freq="D")
    a = np.full(len(days), 5.0)
    b = np.where(days.year <= 2011, 6.0, 6.5)
    e = _ev(_frame(days, {"A": a, "B": b}), station_offsets={"reference": "A", "era": [2010, 2011]}); e._value()
    assert e.offsets["B"] == {"offset": pytest.approx(1.0), "n_days": int((days.year <= 2011).sum())}


def test_offset_fitted_after_the_mask():
    days = pd.date_range("2010-01-01", "2010-12-31", freq="D")
    flag = np.zeros(len(days), bool); flag[:100] = True                  # B's first 100 days read 0.2 × (a failed sensor)
    a = np.full(len(days), 5.0)
    b = np.where(flag, 1.0, 6.0)
    df = _frame(days, {"A": a, "B": b}, {"B": flag})
    sp = {"reference": "A", "era": [2010, 2010]}
    e = _ev(df, mask_columns=["qc_low_ratio"], station_offsets=sp); e._value()
    assert e.offsets["B"] == {"offset": pytest.approx(1.0), "n_days": len(days) - 100}
    e = _ev(df, station_offsets=sp); e._value()
    assert e.offsets["B"]["offset"] < 0.0                                   # unmasked, the failed sensor drags it below


def test_offset_refused_without_enough_paired_era_days():
    days = pd.date_range("2010-01-01", "2013-12-31", freq="D")
    v = np.full(len(days), 5.0)
    df = _frame(days, {"A": v, "B": np.where(days.year >= 2012, 6.0, np.nan)}).dropna(subset=["value"])
    e = _ev(df, station_offsets={"reference": "A", "era": [2010, 2011], "min_days": 30})
    with pytest.raises(ValueError, match="station B has 0 days paired with A"):
        e._value()


def test_offset_refused_when_the_reference_has_no_data():
    days = pd.date_range("2010-01-01", periods=40, freq="D")
    df = _frame(days, {"B": np.full(40, 6.0)})
    with pytest.raises(ValueError, match="reference A has no data"):
        _ev(df, station_offsets={"reference": "A", "era": [2010, 2010]})._value()


# ── normalise ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_normalise_carries_flags_and_refuses_a_missing_or_gappy_one(windy):
    inst = load_instance(windy)
    raw = pd.DataFrame({"date": pd.date_range("2010-01-01", periods=3), "station": "W1", "wspd": [1.0, 2.0, 3.0],
                        "qc_low_ratio_causal": [False, True, False]})
    n = normalise(inst, WIND, raw)
    assert n["qc_low_ratio_causal"].tolist() == [False, True, False]
    with pytest.raises(ValueError, match="mask column 'qc_low_ratio_causal' is declared but absent"):
        normalise(inst, WIND, raw.drop(columns="qc_low_ratio_causal"))
    with pytest.raises(ValueError, match="must be boolean with no gaps"):
        normalise(inst, WIND, raw.assign(qc_low_ratio_causal=[False, None, True]))


# ── registry R5 · R7 ───────────────────────────────────────────────────────────────────────────────────────────────────
def _errs(d, edit):
    inst = load_instance(d, check=False)
    edit(inst)
    with pytest.raises(registry.RegistryError) as ex:
        registry.check(inst)
    return str(ex.value)


def test_registry_accepts_the_declared_wind(windy):
    load_instance(windy)


@pytest.mark.parametrize("edit, msg", [
    (lambda i: i.cfg["streams"][WIND].__setitem__("mask_columns", ["qc_bogus"]), "not flags NDBCStdmet writes"),
    (lambda i: i.cfg["streams"][WIND].__setitem__("mask_columns", []), "non-empty list"),
    # III M-3b-ii-b-1 F-5: a flag that reads ahead of its day may not mask
    (lambda i: i.cfg["streams"][WIND].__setitem__("mask_columns", ["qc_low_ratio"]), "'qc_low_ratio', which reads ahead"),
    (lambda i: i.cfg["streams"][WIND].__setitem__("mask_columns", ["qc_stuck"]), "'qc_stuck', which reads ahead"),
    # III F-7: the spec is a closed key set
    (lambda i: i.cfg["streams"][WIND].__setitem__("mask_column", ["qc_low_ratio_causal"]),
     "unknown stream key 'mask_column' — did you mean 'mask_columns'"),
    (lambda i: i.cfg["streams"][WIND].__setitem__("station_offset", {}), "unknown stream key 'station_offset' — did you mean"),
    (lambda i: i.cfg["streams"][WIND].__setitem__("frobnicate", 1), "unknown stream key 'frobnicate' .*under `fetch`"),
    # III F-6: under per-fold selection the first fold early-stops on min(ro), which no offset era may reach
    (lambda i: i.cfg["split"].__setitem__("rolling_origin_years", [2012, 2013]), "R7 .* per_fold .* early-stops on 2012"),
    (lambda i: i.cfg["streams"][WIND]["station_offsets"].__setitem__("reference", "W9"), "reference 'W9' is not in the stations"),
    (lambda i: i.cfg["streams"][WIND]["station_offsets"].__setitem__("era", [2012, 2006]), "era must be"),
    (lambda i: i.cfg["streams"][WIND]["station_offsets"].__setitem__("min_days", 0), "min_days must be"),
    (lambda i: i.cfg["streams"][WIND]["station_offsets"].__setitem__("extra", 1), "must be {reference, era, min_days}"),
    (lambda i: i.cfg["streams"][WIND]["station_windows"].__setitem__("W9", [None, "2019-01-01"]), "names 'W9'"),
    (lambda i: i.cfg["streams"][WIND]["station_windows"].__setitem__("W3", ["2019-01-01", "2018-01-01"]), "runs backwards"),
    (lambda i: i.cfg["streams"][WIND]["station_windows"].__setitem__("W3", [None, None]), "at least one date"),
    (lambda i: i.cfg["streams"][WIND]["station_offsets"].__setitem__("era", [2006, 2017]), "R7 .* era ends 2017 ≥ val_start"),
    (lambda i: i.cfg["split"].__setitem__("rolling_origin_years", [2010, 2011]), "R7 .* rolling-origin folds test"),
    (lambda i: i.cfg["streams"]["atl_stream_example_do_daily"].__setitem__("station_offsets",
               {"reference": "EXS01", "era": [2006, 2012]}), "on the event stream"),
    (lambda i: i.cfg["streams"]["atl_stream_example_sst_daily"].__setitem__("station_windows", {"x": [None, "2019-01-01"]}),
     "station-keyed streams only"),
])
def test_registry_refuses(windy, edit, msg):
    import re
    assert re.search(msg, _errs(windy, edit)), _errs(windy, edit)


def test_offset_era_may_reach_the_first_stop_year_only_without_per_fold_selection(windy):
    """III F-6: full_model selection does not early-stop on the inner year, so the looser bound (the first TEST year)
    holds; the default per_fold needs the era to end before min(rolling_origin_years)."""
    inst = load_instance(windy, check=False)
    inst.cfg["split"]["rolling_origin_years"] = [2012, 2013]
    inst.cfg.setdefault("eval", {})["rolling_selection"] = "full_model"
    registry.check(inst)


def test_hash_unchanged_without_the_new_keys(variant_master, tmp_path):
    """The keys move the hash only when present: every instance written before 0.11.0 keeps its hash."""
    d = tmp_path / "a"; shutil.copytree(variant_master, d)
    add_wind(d, mask=False, offsets=False, windows=False)
    h0 = semantic_hash(load_instance(d))
    e = tmp_path / "b"; shutil.copytree(variant_master, e)
    add_wind(e)
    assert semantic_hash(load_instance(e)) != h0
    for key in ("mask", "offsets", "windows"):
        f = tmp_path / key; shutil.copytree(variant_master, f)
        add_wind(f, **{k: k == key for k in ("mask", "offsets", "windows")})
        assert semantic_hash(load_instance(f)) != h0, key


# ── the self-test ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_selftest_green_and_reports_the_offset_era(windy):
    from atlantis_core import selftest
    res = selftest.run(load_instance(windy), verbose=False)
    c6 = res["C6_offsets"][WIND]
    assert isinstance(c6, dict) and c6, "an in-era perturbation of the non-reference stations must move a wind vital"
    assert set(c6) <= {"example_wind_mean_t0", "example_wind_mean_t1", "example_wind_calm_t0"}
    assert "example_wind_mean_t0" in c6
    assert c6["example_wind_mean_t0"][4] > 0, "real dependence (|Δ| > 1e-9), not float residue"
    assert res["streams"][WIND]["C0_vitals"] == 3


def test_selftest_without_wind_vitals_says_na(variant_master, tmp_path):
    from atlantis_core import selftest
    d = tmp_path / "inst"; shutil.copytree(variant_master, d)
    add_wind(d, vitals=False)
    res = selftest.run(load_instance(d), verbose=False)
    assert res["C6_offsets"][WIND].startswith("n/a")


def test_selftest_refuses_a_week_inside_the_lag_reach_of_the_era(windy):
    from atlantis_core import selftest
    cfg = yaml.safe_load((windy / "atlantis.yaml").read_text())
    cfg["selftest"]["week"] = "2013-01-14"           # t − (longest lag 1 + 1) weeks = 2012-12-31, the era's last day
    cfg["streams"][WIND]["station_offsets"]["era"] = [2006, 2012]
    (windy / "atlantis.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    with pytest.raises(ValueError, match="not clear of the station_offsets era"):
        selftest.run(load_instance(windy), verbose=False)


def test_selftest_synthesises_an_offset_era_older_than_every_other(windy):
    """The synthetic world must reach back to the offset era, or the offsets cannot be fitted (_span)."""
    from atlantis_core import selftest
    cfg = yaml.safe_load((windy / "atlantis.yaml").read_text())
    cfg["streams"][WIND]["station_offsets"]["era"] = [1985, 1988]          # before the climatology era (1991–2010)
    (windy / "atlantis.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    res = selftest.run(load_instance(windy), verbose=False)
    assert isinstance(res["C6_offsets"][WIND], dict) and res["C6_offsets"][WIND]


# ── III M-3b-ii-b-1 F-1: calm days in every season; a world without them is the world's fault ─────────────────────────
def _calm_vitals(d: Path, thresholds=(2.0, 6.0)):
    fe = yaml.safe_load((d / "features.yaml").read_text())
    for c in thresholds:
        fe["vitals"].append({"vital_id": f"atl_vital_example_wind_calm_{int(c)}", "name": f"calm_{int(c)}",
                             "description": "test", "stream_ref": WIND, "transform": f"weekly_count_lt(value, {c})",
                             "lag": 0, "group": "wind", "tag": "proxy"})
    (d / "features.yaml").write_text(yaml.safe_dump(fe, sort_keys=False))


@pytest.mark.parametrize("week", ["2014-03-03", "2014-07-07", "2014-10-06", "2015-01-05"])
def test_selftest_calm_vitals_bite_in_every_season(windy, week):
    """The 0.11.0 world centred a sine on the median threshold; a March week (FKNMS) left C0 nothing to remove."""
    from atlantis_core import selftest
    _calm_vitals(windy)
    cfg = yaml.safe_load((windy / "atlantis.yaml").read_text())
    cfg["selftest"]["week"] = week
    (windy / "atlantis.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    res = selftest.run(load_instance(windy), verbose=False)
    assert res["streams"][WIND]["C0_vitals"] == 5


def test_selftest_refuses_a_world_without_calm_days_by_name(windy, monkeypatch):
    from atlantis_core import selftest
    monkeypatch.setattr(selftest, "calm_values", lambda thr, n, rng: np.full(n, max(thr) + 5.0))   # plant: never calm
    with pytest.raises(selftest.LeakError, match="world fault"):
        selftest.run(load_instance(windy), verbose=False)


def test_selftest_catches_a_mask_that_reads_the_next_week(windy, monkeypatch):
    """III F-5: C1 raises every declared flag over t+1; a mask that reaches back a week must be caught."""
    from atlantis_core import selftest
    real = Evaluator._prepared

    def ahead(self):
        d = self.data
        if self.mask_columns:
            d = d.copy()
            for c in self.mask_columns:
                nxt = d.assign(date=d["date"] - pd.Timedelta(days=7))[["date", "station", c]]
                d = d.drop(columns=c).merge(nxt, on=["date", "station"], how="left")
                d[c] = d[c].fillna(False).astype(bool)
        self.data, keep = d, self.data
        try:
            return real(self)
        finally:
            self.data = keep

    monkeypatch.setattr(Evaluator, "_prepared", ahead)
    with pytest.raises(selftest.LeakError, match=r"C1 LEAK .*mask flags"):
        selftest.run(load_instance(windy), verbose=False)

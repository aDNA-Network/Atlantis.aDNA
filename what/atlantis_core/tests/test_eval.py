"""eval/ — the port reproduces hab.train on hab's own vitals; the R7 obligation is executed, not waived; lead time is
direction-aware; the logistic learner fits its statistics on training rows only."""
import copy, json

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.eval import ObligationError, run
from atlantis_core.eval.lead import lead_time
from atlantis_core.eval.learners import learner
from atlantis_core.eval.rolling import FoldTables, clipped_eras
from atlantis_core.vitals.build import build, load_frames
from atlantis_core.label import finalize


def _cmp(a, b, path=""):
    """Every key of b present in a and equal (floats to 1e-12, NaN == NaN)."""
    bad = []
    if isinstance(b, dict):
        for k in b:
            bad += [f"{path}/{k} missing"] if k not in a else _cmp(a[k], b[k], f"{path}/{k}")
    elif isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} len {len(a)} != {len(b)}"]
        for i, (x, y) in enumerate(zip(a, b)):
            bad += _cmp(x, y, f"{path}[{i}]")
    elif isinstance(b, float):
        if not (abs(a - b) <= 1e-12 or (np.isnan(a) and np.isnan(b))):
            bad.append(f"{path} {a} != {b}")
    elif a != b:
        bad.append(f"{path} {a} != {b}")
    return bad


@pytest.fixture(scope="module")
def hab_port(exemplar_dir):
    """Core eval on hab's features.parquet, in hab's log10(1+x) signal space, reference mode (hab did not refit)."""
    proc = exemplar_dir / "data" / "processed"
    if not (proc / "features.parquet").exists():
        pytest.skip("exemplar data/processed missing — run hab.build_features + hab.train first")
    inst = load_instance(exemplar_dir)
    i2 = copy.copy(inst)
    # hab's after-the-fact readings (F-8), kept as modes so the port still reproduces metrics.json exactly
    i2.cfg = {**inst.cfg, "eval": {**inst.cfg["eval"], "threshold_from": "test", "rolling_selection": "full_model"}}
    eid = inst.cfg["label"]["event"]
    i2.events = {**inst.events, eid: {**inst.event, "threshold": float(np.log10(1 + inst.event["threshold"]))}}
    df = pd.read_parquet(proc / "features.parquet")
    rw = pd.read_parquet(proc / "region_week_all.parquet")[["region", "week", "log_max"]].rename(columns={"log_max": "signal"})
    thr2 = np.log10(1 + inst.cfg["eval"]["sensitivity_threshold"])
    d2 = df.copy(); d2["y"] = (d2["future_log_max"] >= thr2).astype(int); d2 = d2[~d2["last_obs_log_max"].ge(thr2).fillna(False)]
    res, _ = run(i2, df, rw, sensitivity_df=d2, reference=True, log=lambda *_: None)
    return res, json.loads((exemplar_dir / "outputs" / "metrics.json").read_text())


@pytest.mark.parametrize("key", ["splits", "full", "no_surveillance", "surveillance_only_test_auroc", "climatology_baseline_test"])
def test_port_reproduces_metrics_json(hab_port, key):
    res, m = hab_port
    assert _cmp(res[key], m[key]) == []


def test_port_headline(hab_port):
    res, _ = hab_port
    assert res["full"]["n_trees"] == 141
    assert round(res["full"]["test"]["auroc"], 4) == 0.8941 and round(res["full"]["test"]["auprc"], 4) == 0.5473


def test_port_rolling_and_sensitivity(hab_port):
    res, m = hab_port
    assert _cmp([{k: r[k] for k in m["rolling_origin"][0]} for r in res["rolling_origin"]], m["rolling_origin"]) == []
    assert _cmp(res["sensitivity"], m["sensitivity_50k"]) == []


def test_reference_mode_is_marked_unhonoured(hab_port):
    res, _ = hab_port
    assert res["mode"] == "reference" and res["obligations"] and not any(o["honoured"] for o in res["obligations"])


# ── R7: the obligation is executed ──────────────────────────────────────────────────────────────────────────────────

def test_eval_refuses_unhonoured_obligation(exemplar_dir):
    inst = load_instance(exemplar_dir)
    assert inst.obligations, "the exemplar's discharge era overlaps the 2016 fold — R7 must record an obligation"
    with pytest.raises(ObligationError, match="R7"):
        run(inst, pd.DataFrame(), pd.DataFrame())


def test_clipped_eras(exemplar_dir):
    inst = load_instance(exemplar_dir)
    D, S = "atl_stream_usgs_discharge_daily", "atl_stream_oisst_region_daily"
    assert clipped_eras(inst, 2015) == {S: (1982, 2011), D: (1990, 2015)}
    assert clipped_eras(inst, 2016) == {S: (1982, 2011), D: (1990, 2016)}
    with pytest.raises(ValueError, match="precedes"):
        clipped_eras(inst, 1985)


@pytest.fixture(scope="module")
def exemplar_built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    return inst, frames, m


def test_fold_refit_moves_only_the_clipped_anomaly(exemplar_built):
    inst, frames, m = exemplar_built
    folds = FoldTables(inst, frames, m)
    same, eras, rebuilt = folds(2016)
    assert not rebuilt and same is m
    f15, eras, rebuilt = folds(2015)
    assert rebuilt and eras["atl_stream_usgs_discharge_daily"] == (1990, 2015)
    assert len(f15) == len(m) and (f15["y"].values == m["y"].values).all()   # the label reads no normal
    moved = [c for c in inst.feature_names if not np.allclose(f15[c].values, m[c].values, equal_nan=True)]
    assert moved == ["discharge_anom_t0"]


# ── lead time is direction-aware ────────────────────────────────────────────────────────────────────────────────────

def _lead_panel(signal, p):
    weeks = pd.date_range("2020-01-06", periods=len(signal), freq="7D")
    return pd.DataFrame({"u": 1, "week": weeks, "signal": signal, "p": p})


def test_lead_time_below_event():
    sig = [5, 5, 5, 5, 5, 5, 1, 5]        # onset (≤ 2) at index 6, after ≥ 4 weeks not in event
    p = [0, 0, 0, 0.9, 0, 0, np.nan, np.nan]   # first alert 3 weeks before
    r = lead_time(_lead_panel(sig, p), unit_col="u", threshold=2, direction="below", horizon=4, alert_threshold=0.5, test_start=2020)
    assert r["n_onsets"] == 1 and r["median_lead_weeks"] == 3.0
    r = lead_time(_lead_panel(sig, p), unit_col="u", threshold=2, direction="above", horizon=4, alert_threshold=0.5, test_start=2020)
    assert r["n_onsets"] == 0   # read with the wrong tail, every week is "in event" — no onset after a quiet run


# ── logistic: statistics from training rows only ───────────────────────────────────────────────────────────────────

def test_logistic_fits_on_train_only():
    """The selection model's imputer/scaler statistics are a function of TRAIN rows alone: wild val rows change
    nothing it learned (III F-6: the first version of this test could not fail)."""
    rng = np.random.default_rng(0)
    def frame(n):
        x = rng.normal(size=n); x[::7] = np.nan
        return pd.DataFrame({"a": x, "b": rng.normal(size=n), "y": (rng.random(n) < 0.3).astype(int)})
    train, val = frame(400), frame(200)
    L = learner({"kind": "logistic", "C_grid": [1.0], "max_iter": 1000}, ["a", "b"])
    vm, final, info = L.fit(train, val)
    wild = val.assign(a=1e6, b=-1e6)
    vm_w, final_w, _ = L.fit(train, wild)
    for step in ("impute", "scale"):
        a, b = vm.named_steps[step], vm_w.named_steps[step]
        sa, sb = (a.statistics_, b.statistics_) if step == "impute" else (a.mean_, b.mean_)
        assert np.allclose(sa, sb)
    assert vm.named_steps["impute"].statistics_[0] == pytest.approx(np.nanmedian(train["a"]))
    assert not np.allclose(final.named_steps["scale"].mean_, final_w.named_steps["scale"].mean_)   # the final model does see val


# ── R7: the obligation is VERIFIED per fold, not presumed from an argument (III F-3) ───────────────────────────────

def test_noop_fold_callable_is_refused(exemplar_built):
    inst, frames, m = exemplar_built
    panel = m[["region", "week"]].assign(signal=np.nan)
    base = {sid: inst.climatology(sid) for sid in inst.cfg["climatology"]}
    with pytest.raises(ObligationError, match="2015"):
        run(inst, m, panel, fold_tables=lambda Y: (m, base, False), log=lambda *_: None)
    with pytest.raises(ObligationError, match="2015"):   # claims a rebuild, with the wrong eras
        run(inst, m, panel, fold_tables=lambda Y: (m, base, True), log=lambda *_: None)


# ── the core's own label paths against hab (III F-6: these were outside the port test) ──────────────────────────

def test_relabel_and_signal_panel_match_hab(exemplar_dir, exemplar_built):
    proc = exemplar_dir / "data" / "processed"
    if not (proc / "features.parquet").exists():
        pytest.skip("exemplar data/processed missing")
    from atlantis_core.run import relabel, signal_panel
    from atlantis_core.vitals.build import patient_grid
    inst, frames, _ = exemplar_built
    units, weeks = patient_grid(inst, frames)
    table, _ = build(inst, frames)
    d2, rep = relabel(inst, frames, table, units, weeks, float(inst.cfg["eval"]["sensitivity_threshold"]))
    df = pd.read_parquet(proc / "features.parquet")
    thr2 = np.log10(1 + inst.cfg["eval"]["sensitivity_threshold"])
    h2 = df.assign(y=(df["future_log_max"] >= thr2).astype(int))
    h2 = h2[~h2["last_obs_log_max"].ge(thr2).fillna(False)]
    j = d2[["region", "week", "y"]].merge(h2[["region", "week", "y"]], on=["region", "week"], how="outer", indicator=True)
    assert (j["_merge"] == "both").all() and len(j) == len(h2) == 10556
    assert (j["y_x"].astype(int) == j["y_y"].astype(int)).all() and int(d2["y"].sum()) == 1202
    pan = signal_panel(inst, frames, units, weeks)
    rw = pd.read_parquet(proc / "region_week_all.parquet")[["region", "week", "log_max"]]
    k = pan.merge(rw, on=["region", "week"], how="outer", indicator=True)
    assert (k["_merge"] == "both").all() and len(k) == 25011
    thr = float(inst.event["threshold"])
    assert (k["signal"].ge(thr).fillna(False) == k["log_max"].ge(np.log10(1 + thr)).fillna(False)).all()

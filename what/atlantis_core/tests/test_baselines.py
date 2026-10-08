"""M-2b (steward rulings 16 and 19): the event signal's own comparators — persistence (s(t), no model) and trend (logistic
on s(t) and its last step) — and the base rate and calibration-in-the-large per segment. Each defect is planted into the
real source and caught by name, and each control is shown able to fail (C-009)."""
import copy, types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core import eval as ev_mod
from atlantis_core.board import BoardError, assert_comparators, project
from atlantis_core.eval import ObligationError
from atlantis_core.eval import metrics as met_mod
from atlantis_core.eval.metrics import evaluate, persistence_baseline, signal_history, trend_baseline
from atlantis_core.label import finalize
from atlantis_core.run import signal_panel
from atlantis_core.vitals.build import build, load_frames, patient_grid

METRICS_PLANTS = {
    # s(t) read one week ahead — the leak a persistence baseline exists to rule out
    "S1_signal_reads_next_week": ('s_t = g.groupby(unit_col)["signal"].ffill(limit=L) if L else g["signal"].copy()',
                                  's_t = g.groupby(unit_col)["signal"].shift(-1)'),
    # carried without the label's limit: no longer the signal the label reads
    "S2_carry_unlimited": ('s_t = g.groupby(unit_col)["signal"].ffill(limit=L) if L else g["signal"].copy()',
                           's_t = g.groupby(unit_col)["signal"].ffill()'),
}
EVAL_PLANTS = {
    "B1_trend_fit_on_test": ('res["trend_baseline_test"] = trend_baseline(base_fit, test, hist, unit_col=unit_col)',
                             'res["trend_baseline_test"] = trend_baseline(test, test, hist, unit_col=unit_col)'),
    "B2_baseline_fit_unembargoed": ('base_fit = pd.concat([train, embargo(val, s["test_start"], E)])',
                                    'base_fit = pd.concat([train, val])'),
}


def planted(mod, plants: dict, name: str):
    """A fresh copy of `mod` with one plant written into its source."""
    src = Path(mod.__file__).read_text()
    old, new = plants[name]
    assert src.count(old) == 1, f"plant {name}: the line it replaces moved — update the plant, do not drop it"
    m = types.ModuleType(f"planted_{name}")
    m.__dict__["__file__"] = mod.__file__
    exec(compile(src.replace(old, new), f"<planted {name}>", "exec"), m.__dict__)
    if hasattr(mod, "ObligationError"):
        m.ObligationError = mod.ObligationError
    return m


# ── a synthetic world: the next week's signal decides the label (H = 1), so a leak is perfect and visible ───────────

def _world(direction="above", seed=0, n_units=6, n_weeks=260):
    rng = np.random.default_rng(seed)
    weeks = pd.date_range("2000-01-03", periods=n_weeks, freq="7D")
    rows = []
    for u in range(n_units):
        e, s = rng.normal(0, 1, n_weeks), np.zeros(n_weeks)
        for i in range(1, n_weeks):   # AR(1): s(t) informs s(t+1) without deciding it
            s[i] = 0.7 * s[i - 1] + e[i]
        rows += [{"unit": u, "week": w, "signal": v} for w, v in zip(weeks, s)]
    panel = pd.DataFrame(rows)
    nxt = panel.groupby("unit")["signal"].shift(-1)
    thr = panel["signal"].median()
    panel["y"] = (nxt >= thr if direction == "above" else nxt <= thr).astype(int)
    panel = panel[nxt.notna()].reset_index(drop=True)
    yr = panel["week"].dt.year
    return panel, panel[yr <= 2002], panel[yr >= 2003]


def test_persistence_ranks_by_the_signal_and_cannot_see_ahead():
    panel, fit, test = _world()
    hist = signal_history(panel, "unit", 4)
    clean = persistence_baseline(fit, test, hist, unit_col="unit", direction="above")
    assert 0.6 < clean["auroc"] < 0.99 and clean["n_imputed"] == 0 and clean["n_test"] == len(test)
    leak = planted(met_mod, METRICS_PLANTS, "S1_signal_reads_next_week")
    bad = leak.persistence_baseline(fit, test, leak.signal_history(panel, "unit", 4), unit_col="unit", direction="above")
    assert bad["auroc"] > 0.999, "a next-week read went unnoticed — this world cannot tell a leak from a forecast"


def test_persistence_is_direction_aware():
    panel, fit, test = _world(direction="below")
    hist = signal_history(panel, "unit", 4)
    below = persistence_baseline(fit, test, hist, unit_col="unit", direction="below")
    above = persistence_baseline(fit, test, hist, unit_col="unit", direction="above")
    assert below["auroc"] > 0.6 and abs(below["auroc"] + above["auroc"] - 1) < 1e-12
    with pytest.raises(ValueError, match="direction"):
        persistence_baseline(fit, test, hist, unit_col="unit", direction="sideways")


def test_imputation_is_counted_not_hidden():
    panel, fit, test = _world()
    gap = panel.copy()
    drop = gap.index[(gap["week"].dt.year == 2004) & (gap["unit"] == 0)][::3]
    gap.loc[drop, "signal"] = np.nan          # every third week of one unit's 2004: carried forward, not missing
    assert persistence_baseline(fit, test, signal_history(gap, "unit", 4), unit_col="unit", direction="above")["n_imputed"] == 0
    hist0 = signal_history(gap, "unit", 0)    # no carry: each blanked week is missing at t (and at t−1 for the next week)
    p = persistence_baseline(fit, test, hist0, unit_col="unit", direction="above")
    t = trend_baseline(fit, test, hist0, unit_col="unit")
    assert p["n_imputed"] == len(drop)
    h = test[["unit", "week"]].merge(hist0, on=["unit", "week"], how="left")
    assert t["n_imputed"] == int((h["s_t"].isna() | h["s_prev"].isna()).sum()) > len(drop)   # t−1 missing counts too


def test_trend_reports_what_it_was_fitted_on():
    panel, fit, test = _world()
    t = trend_baseline(fit, test, signal_history(panel, "unit", 4), unit_col="unit")
    assert t["fit_years"] == [2000, 2002] and t["n_fit"] == len(fit) and t["n_test"] == len(test) and 0.6 < t["auroc"] < 1


def test_calibration_in_the_large_is_mean_p_minus_prevalence():
    y = np.array([0, 0, 0, 1] * 25)
    p = np.linspace(0.05, 0.6, 100)
    r = evaluate(y, p, "test")
    assert abs(r["calibration_in_the_large"] - (p.mean() - y.mean())) < 1e-15


# ── on the exemplar: the persistence signal IS the label's carried signal; the run's plants are refused by name ────────

@pytest.fixture(scope="module")
def built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    m = m.copy(); m["y"] = m["y"].astype(int)
    units, weeks = patient_grid(inst, frames)
    return inst, frames, m, signal_panel(inst, frames, units, weeks)


def _carried(mod, inst, m, panel):
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    h = mod.signal_history(panel, ucol, int(inst.cfg["label"]["last_known_weeks"]))
    return m[[ucol, "week"]].merge(h, on=[ucol, "week"], how="left")["s_t"]


def test_persistence_signal_is_the_labels_last_known_signal(built):
    inst, _, m, panel = built
    got, want = _carried(met_mod, inst, m, panel), m["last_known_signal"].astype(float)
    assert got.notna().sum() > 0 and np.allclose(got, want, equal_nan=True, rtol=0, atol=0)
    for name in METRICS_PLANTS:   # each plant must break the identity (C-009: the control can fail)
        bad = _carried(planted(met_mod, METRICS_PLANTS, name), inst, m, panel)
        assert not np.allclose(bad, want, equal_nan=True, rtol=0, atol=0), f"{name} went unnoticed"


LOGISTIC = {"kind": "logistic", "C_grid": [1.0], "max_iter": 2000}


def _noabl(inst):
    i2 = copy.copy(inst); i2.cfg = {**inst.cfg, "eval": {**inst.cfg["eval"], "ablations": []}}
    return i2


def _run(mod, inst, frames, m, panel):
    from atlantis_core.eval.rolling import FoldTables
    return mod.run(_noabl(inst), m, panel, fold_tables=FoldTables(inst, frames, m), learner_spec=LOGISTIC, log=lambda *_: None)


@pytest.fixture(scope="module")
def clean_res(built):
    inst, frames, m, panel = built
    res, _ = _run(ev_mod, inst, frames, m, panel)
    return res


def test_clean_run_carries_comparators_and_segments(clean_res, built):
    inst, _, m, _ = built
    res = clean_res
    for seg in ("train", "val", "test"):
        v = res["splits"][seg]
        assert v["base_rate"] == v["positives"] / v["n"]
    assert res["persistence_baseline_test"]["n_test"] == res["trend_baseline_test"]["n_test"] == res["full"]["test"]["n"]
    assert res["trend_baseline_test"]["fit_years"][1] < inst.cfg["split"]["test_start"]
    for blk in ("val", "test"):
        assert "calibration_in_the_large" in res["full"][blk]
    ev = project(res, _noabl(inst), version=99, recorded_at="2026-10-08T00:00:00Z", config_hash="0" * 10)
    for slot in ("persistence_auroc", "persistence_auprc", "trend_auroc", "trend_auprc", "base_rate_train",
                 "base_rate_validation", "calibration_in_the_large_validation", "calibration_in_the_large_test"):
        assert slot in ev
    assert_comparators(ev, res)


@pytest.mark.parametrize("plant,match", [("B1_trend_fit_on_test", "baselines: the trend was fitted on rows through"),
                                         ("B2_baseline_fit_unembargoed", "embargo baselines fit→test")])
def test_eval_plants_are_refused_by_name(built, plant, match):
    inst, frames, m, panel = built
    with pytest.raises(ObligationError, match=match):
        _run(planted(ev_mod, EVAL_PLANTS, plant), inst, frames, m, panel)


RESULT_PLANTS = [
    (lambda r: r["splits"]["train"].__setitem__("base_rate", r["splits"]["train"]["base_rate"] + 0.01), "splits.train: base rate"),
    (lambda r: r["splits"]["val"].pop("base_rate"), "splits.val: no base rate"),
    (lambda r: r.pop("persistence_baseline_test"), "persistence_baseline_test missing"),
    (lambda r: r["trend_baseline_test"].__setitem__("n_test", 1), "trend_baseline_test: scored 1 rows"),
    (lambda r: r["trend_baseline_test"].__setitem__("fit_years", [1990, 2030]), "fitted on rows through 2030"),
]


@pytest.mark.parametrize("mutate,match", RESULT_PLANTS)
def test_board_refuses_a_result_without_honest_comparators(clean_res, built, mutate, match):
    inst = built[0]
    r = copy.deepcopy(clean_res); mutate(r)
    ev = project(r, _noabl(inst), version=99, recorded_at="2026-10-08T00:00:00Z", config_hash="0" * 10)
    with pytest.raises(BoardError, match=match):
        assert_comparators(ev, r)


def test_a_result_before_0_7_0_projects_without_the_new_slots(clean_res, built):
    inst = built[0]
    r = copy.deepcopy(clean_res)
    for k in ("persistence_baseline_test", "trend_baseline_test"):
        r.pop(k)
    for v in r["splits"].values():
        v.pop("base_rate")
    for blk in ("val", "test"):
        r["full"][blk].pop("calibration_in_the_large")
    ev = project(r, _noabl(inst), version=99, recorded_at="2026-10-08T00:00:00Z", config_hash="0" * 10)
    assert not {k for k in ev if k.startswith(("persistence_", "trend_", "base_rate_", "calibration_in_the_large"))}


def test_exemplar_v4_differs_from_v3_by_the_comparators_alone(exemplar_dir):
    """M-2b moved no number: every v3 field is equal in v4 but the core version and the run time; the model, SHAP and
    what-if bytes are identical; v4 adds the comparators, the segment rates and calibration-in-the-large."""
    import json
    o = exemplar_dir / "outputs"
    a, b = (json.loads((o / d / "metrics.json").read_text()) for d in ("atlantis_core_v3", "atlantis_core_v4"))

    def diff(x, y, p=""):
        if isinstance(x, dict):
            return [d for k in x for d in ([f"{p}/{k} missing"] if k not in y else diff(x[k], y[k], f"{p}/{k}"))]
        if isinstance(x, list):
            return [f"{p} len"] if len(x) != len(y) else [d for i, (u, v) in enumerate(zip(x, y)) for d in diff(u, v, f"{p}[{i}]")]
        return [] if x == y else [p]
    assert diff(a, b) == ["/atlantis_core", "/run_at"]
    assert {"persistence_baseline_test", "trend_baseline_test"} <= set(b) and "base_rate" in b["splits"]["train"]
    assert "calibration_in_the_large" in b["full"]["test"]
    for f in ("model.json", "shap_summary.json", "whatif.json"):
        assert (o / "atlantis_core_v3" / f).read_bytes() == (o / "atlantis_core_v4" / f).read_bytes(), f

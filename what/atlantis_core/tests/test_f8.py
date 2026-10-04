"""F-8 (M-1e): nothing is chosen on the years it scores. Each defect the fix exists for is planted and caught by name, and
the control itself is shown to fail when the old reading is planted back (C-009). v2 differs from v1 by F-8 alone."""
import copy, hashlib, json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance, semantic_hash
from atlantis_core import eval as ev_mod
from atlantis_core.board import BoardError, assert_thresholds_fixed, delta, emit, project
from atlantis_core.eval import ObligationError, check_fold_selection, check_thresholds_fixed, fixed_thresholds, split
from atlantis_core.eval.metrics import at_alert_rates, quantile_thresholds
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames

WHAT = Path(__file__).resolve().parents[2]
ENTRIES = WHAT / "board" / "entries"
V1 = ENTRIES / "2026-10-02_gulf_karenia_brevis_v1.json"
RATES = (0.05, 0.10, 0.20)


# ── (a) a threshold computed from test ─────────────────────────────────────────────────────────────────────────────

def _scores(seed=0):
    rng = np.random.default_rng(seed)
    return rng.beta(1, 8, 600), rng.beta(1, 6, 400)


def test_fixed_rule_is_invariant_to_test_scores():
    p_val, p_test = _scores()
    check_thresholds_fixed(lambda pv, pt: fixed_thresholds(pv, RATES, "val"), p_val, p_test)


def test_planted_threshold_from_test_is_caught():
    p_val, p_test = _scores()
    with pytest.raises(ObligationError, match="F-8: threshold moved with test scores"):
        check_thresholds_fixed(lambda pv, pt: quantile_thresholds(pt, RATES), p_val, p_test)


def test_val_mode_refuses_to_quantile_the_scored_set():
    """`val` without thresholds fixed beforehand would silently quantile the test scores — refused, not defaulted."""
    y, p = np.array([0, 1] * 50), np.linspace(0, 1, 100)
    with pytest.raises(ValueError, match="fixed beforehand"):
        at_alert_rates(y, p, RATES, threshold_from="val")


# ── (a, by effect) + (d, C-009): the real eval path, and the old reading planted back into it ─────────────────────

@pytest.fixture(scope="module")
def built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    table, _ = build(inst, load_frames(inst))
    m, _ = finalize(inst, table)
    m = m.copy(); m["y"] = m["y"].astype(int)
    return inst, m


def _thresholds(inst, m, test_override=None):
    """The test thresholds `_variant` reports, on the exemplar (logistic C=1: fast, and the rule is learner-agnostic)."""
    tr, va, te = split(m, inst.cfg["split"])
    if test_override is not None:
        te = test_override(tr, te)
    ucol = inst.cfg["grid"]["unit_column"]
    panel = te[[ucol, "week"]].assign(signal=np.nan)
    spec = {"kind": "logistic", "C_grid": [1.0], "max_iter": 2000}
    r, *_ = ev_mod._variant(inst, spec, inst.feature_names, tr, va, te, panel, inst.cfg["eval"], ucol)
    return {k: v["threshold"] for k, v in r["test"]["alert_rates"].items()}, r


def _shifted(tr, te):
    """Test rows replaced by train rows (a different score distribution), keys kept."""
    f = [c for c in te.columns if c not in ("week", "y") and not c.startswith("region")]
    sample = tr.sample(len(te), replace=True, random_state=0)[f].to_numpy()
    out = te.copy(); out[f] = sample
    return out


def test_eval_thresholds_do_not_move_with_test(built):
    inst, m = built
    a, r = _thresholds(inst, m)
    b, _ = _thresholds(inst, m, _shifted)
    assert a == b
    assert all(v["threshold_from"] == "val" for v in r["test"]["alert_rates"].values())
    assert {k: round(v["nominal_rate"], 2) for k, v in r["test"]["alert_rates"].items()} == {"5pct": 0.05, "10pct": 0.1, "20pct": 0.2}
    assert all(abs(v["realised_rate"] - v["n_alerts"] / r["test"]["n"]) < 1e-12 for v in r["test"]["alert_rates"].values())


def test_c009_planting_the_test_quantile_back_fails_the_control(built, monkeypatch):
    """C-009: the invariance test above must be able to fail. Plant hab's reading (each scored set quantiles itself)
    into the real path and watch it fail."""
    inst, m = built
    real = ev_mod.evaluate
    monkeypatch.setattr(ev_mod, "evaluate", lambda y, p, label, rates, bins, **kw: real(y, p, label, rates, bins))
    a, _ = _thresholds(inst, m)
    b, _ = _thresholds(inst, m, _shifted)
    assert a != b, "the planted test-quantile threshold went unnoticed — the control passes by construction"


# ── (b) a fold stopped on its test year ────────────────────────────────────────────────────────────────────────────

def _years(*ys):
    return pd.DataFrame({"week": pd.to_datetime([f"{y}-06-01" for y in ys])})


def test_fold_selection_rule():
    check_fold_selection(2018, _years(2015, 2016, 2017), _years(2018))


@pytest.mark.parametrize("s_tr, s_va", [
    (_years(2016, 2017), _years(2019)),          # stopped on its test year
    (_years(2016, 2017, 2018), _years(2018)),    # selection trained through the year it stops on
    (_years(2016, 2017), _years(2018, 2019)),    # the stop set reaches the test year
])
def test_planted_fold_selected_on_its_test_year_is_caught(s_tr, s_va):
    with pytest.raises(ObligationError, match="F-8 fold 2018"):
        check_fold_selection(2018, s_tr, s_va)


def test_v2_folds_each_selected_on_their_own_inner_year(exemplar_dir):
    m = json.loads((exemplar_dir / "outputs" / "atlantis_core_v2" / "metrics.json").read_text())
    assert m["rolling_selection"] == "per_fold" and len(m["rolling_origin"]) == 8
    for r in m["rolling_origin"]:
        assert r["selection"]["selected_on"] == r["train_through"] != r["test_year"]
    eras = {r["train_through"]: r["selection"]["selection_eras"]["atl_stream_usgs_discharge_daily"] for r in m["rolling_origin"]}
    assert eras[2015] == [1990, 2014] and eras[2016] == [1990, 2015] and eras[2017] == [1990, 2016]   # R7 on the inner split


# ── (c) a realised rate missing beside a nominal one — and the board refuses F-8 ──────────────────────────────────

@pytest.fixture(scope="module")
def v2(exemplar_dir):
    o = exemplar_dir / "outputs" / "atlantis_core_v2"
    res = json.loads((o / "metrics.json").read_text())
    shap = json.loads((o / "shap_summary.json").read_text())
    swaps = {"learner_swap_logistic": json.loads((o / "learner_swap_logistic.json").read_text())}
    return load_instance(exemplar_dir), res, shap, swaps


def _emit(inst, res, shap, swaps):
    return emit(res, inst, version=2, run_date="2026-10-03", recorded_at="2026-10-03T00:00:00Z", shap=shap, swaps=swaps)


def test_v2_emits(v2):
    e = _emit(*v2)
    assert all(b["threshold_from"] == "validation" and 0 <= b["realised_rate"] <= 1 for b in e["evaluation"]["alert_budgets"])
    assert e["evaluation"]["lead_time"]["threshold_from"] == "validation"


@pytest.mark.parametrize("plant, match", [
    (lambda r: r["full"]["test"]["alert_rates"]["10pct"].pop("realised_rate"), "budget 0.1: no realised rate"),
    (lambda r: r["full"]["test"]["alert_rates"]["5pct"].update(threshold_from="test"), "budget 0.05: threshold_from 'test'"),
    (lambda r: r["full"]["lead_time_test_10pct"].update(threshold_from="test"), "lead_time: threshold_from 'test'"),
    (lambda r: r.update(rolling_selection="full_model"), "rolling folds selected 'full_model'"),
])
def test_planted_f8_defects_refused_at_emit(v2, plant, match):
    inst, res, shap, swaps = v2
    r = copy.deepcopy(res); plant(r)
    with pytest.raises(BoardError, match=match):
        _emit(inst, r, shap, swaps)


def test_a_swap_selected_after_the_fact_is_refused(v2):
    inst, res, shap, swaps = v2
    s = copy.deepcopy(swaps); s["learner_swap_logistic"]["full"]["threshold_from"] = "test"
    with pytest.raises(BoardError, match="learner swap learner_swap_logistic: eval.threshold_from 'test'"):
        _emit(inst, res, shap, s)


def test_v1_outputs_are_refused(exemplar_dir, v2):
    """v1's run predates the fix: its budgets carry no threshold_from and cannot become a new entry."""
    inst, _, shap, swaps = v2
    o = exemplar_dir / "outputs" / "atlantis_core"
    res1 = json.loads((o / "metrics.json").read_text())
    with pytest.raises(BoardError, match="F-8"):
        _emit(inst, res1, shap, {"learner_swap_logistic": json.loads((o / "learner_swap_logistic.json").read_text())})


# ── single cause: v2 differs from v1 by F-8 alone ──────────────────────────────────────────────────────────────────

UNMOVED = ("n_test", "n_positives", "base_rate", "auroc", "auprc", "brier", "calibration_slope", "climatology_auroc",
           "climatology_auprc", "ablations", "config_hash", "data_pins", "event_ref", "unit_ref", "split", "claim")


def test_v2_differs_from_v1_by_f8_alone(v2, exemplar_dir):
    inst, res, shap, swaps = v2
    old = json.loads(V1.read_text())
    ev = project(res, inst, version=2, recorded_at="2026-10-03T00:00:00Z")
    assert {k: ev[k] for k in UNMOVED} == {k: old["evaluation"][k] for k in UNMOVED}
    assert "141 trees" in ev["learner"] and ev["learner"] == old["evaluation"]["learner"]
    x = old["evaluation_extras"]
    assert res["semantic_hash"] == x["semantic_hash"] == semantic_hash(inst) == "acfa22c6e4"
    assert {k: shap[k] for k in x["shap_summary"]} == x["shap_summary"]
    sens = res["sensitivity"]
    assert [round(sens[k], 4) for k in ("test_auroc", "test_auprc")] == [x["sensitivity"][0][k] for k in ("test_auroc", "test_auprc")]
    for f in ("model.json", "shap_summary.json", "whatif.json"):   # the trained model and everything read from it: identical bytes
        a, b = (exemplar_dir / "outputs" / d / f for d in ("atlantis_core", "atlantis_core_v2"))
        assert a.read_bytes() == b.read_bytes(), f
    d = delta(ev, old)["fields"]
    assert all(d[k]["change"] == 0 for k in ("auroc", "auprc", "brier", "calibration_slope", "base_rate"))
    # what F-8 does move: every budget's threshold source, and the lead time read at the fixed threshold
    assert all(v["threshold_from"] == {"was": None, "now": "validation"} for v in d["alert_budgets"].values())


# ── byte-stable: what M-1e must not touch ──────────────────────────────────────────────────────────────────────────

PINNED = {
    "board/entries/2026-09-23_gulf_karenia_brevis_v0.json": "4a0b1fe6fcdd2cf5a972a1f3ab907b535edd0a173ce3ee5fe782afcd9dede9ef",
    "board/entries/2026-10-02_gulf_karenia_brevis_v1.json": "91be699e4faf744af425720f46f9e78df46c138d18a51073211b6d07eb7cf7fe",
    "exemplars/gulf_karenia_brevis/site/hab_crash_risk.html": "c7fae2039e8aaf2568e1a28bf7bb72e6103c4f28a18aae15fca8b114e45eb07e",
    "exemplars/gulf_karenia_brevis/site/gulf_karenia_brevis_v1.html": "c9e2e0adecf71d7c0899d479557ad79819766a6042f24bd7188186c7568faa69",
    "exemplars/gulf_karenia_brevis/outputs/atlantis_core/metrics.json": "1fb52eaa74d62284be897067dc258f21cbc20ecd3b7a54db16f1dbae271cf368",
}


@pytest.mark.parametrize("rel", sorted(PINNED))
def test_v0_v1_byte_stable(rel):
    assert hashlib.sha256((WHAT / rel).read_bytes()).hexdigest() == PINNED[rel]

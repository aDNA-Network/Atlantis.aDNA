"""F-8 (M-1e): nothing is chosen on the years it scores. Each defect the fix exists for is planted and caught by name, and
the control itself is shown to fail when the old reading is planted back (C-009). v2 differs from v1 by F-8 alone."""
import copy, hashlib, json, types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance, semantic_hash
from atlantis_core import eval as ev_mod
from atlantis_core.board import BoardError, assert_thresholds_fixed, delta, emit, project
from atlantis_core.eval import ObligationError, check_fold_selection, split
from atlantis_core.eval.metrics import at_alert_rates
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames

WHAT = Path(__file__).resolve().parents[2]
ENTRIES = WHAT / "board" / "entries"
V1 = ENTRIES / "2026-10-02_gulf_karenia_brevis_v1.json"
RATES = (0.05, 0.10, 0.20)


# ── planted back into the REAL code (III M-1e F-1/F-2/F-3, C-009): each defect is written into eval's own source ───
# A guard that reads a label the same code wrote cannot fail. These plants change what the code DOES, as the reviewer did,
# and every one must be refused by name — or, for P4, caught by the real-path invariance test.

EVAL_SRC = Path(ev_mod.__file__).read_text()
PLANTS = {
    "P1_stop_on_test_year": ("_, _, finfo = L.fit(s_tr, s_va)", "_, _, finfo = L.fit(s_tr, te)"),
    "P2_selection_eras_through_Y": ("sdf, s_eras, _ = fold(Y - 1)", "sdf, s_eras, _ = fold(Y)"),
    "P3_lead_threshold_from_test": ('alert_threshold=r["test"]["alert_rates"][rate_key(budget)]["threshold"]',
                                    "alert_threshold=float(np.quantile(p_test, 1 - budget))"),
    "P4_fixed_from_test_scores": ("fixed = fixed_thresholds(p_val, rates, tf)",
                                  "fixed = fixed_thresholds(L.predict(final, test), rates, tf)"),
}


def planted(name=None):
    """A fresh copy of atlantis_core.eval, with one plant written into its source (None: a clean copy)."""
    src = EVAL_SRC
    if name:
        old, new = PLANTS[name]
        assert src.count(old) == 1, f"plant {name}: the line it replaces moved — update the plant, do not drop it"
        src = src.replace(old, new)
    mod = types.ModuleType(f"atlantis_core_eval_planted_{name}")
    mod.__dict__["__file__"] = ev_mod.__file__
    exec(compile(src, f"<planted {name}>", "exec"), mod.__dict__)
    mod.ObligationError = ev_mod.ObligationError   # raises resolve the global at call time: one class to catch
    return mod


@pytest.fixture(scope="module")
def built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    m = m.copy(); m["y"] = m["y"].astype(int)
    return inst, frames, m


LOGISTIC = {"kind": "logistic", "C_grid": [1.0], "max_iter": 2000}   # fast, and the F-8 rules are learner-agnostic


def _run(mod, inst, frames, m):
    from atlantis_core.eval.rolling import FoldTables
    i2 = copy.copy(inst); i2.cfg = {**inst.cfg, "eval": {**inst.cfg["eval"], "ablations": []}}
    panel = m[["region", "week"]].assign(signal=np.nan)
    return mod.run(i2, m, panel, fold_tables=FoldTables(inst, frames, m), learner_spec=LOGISTIC, log=lambda *_: None)


def _thresholds(mod, inst, m, test_override=None):
    """The test thresholds `_variant` reports, and its result."""
    tr, va, te = split(m, inst.cfg["split"])
    if test_override is not None:
        te = test_override(tr, te)
    panel = te[["region", "week"]].assign(signal=np.nan)
    r, *_ = mod._variant(inst, LOGISTIC, inst.feature_names, tr, va, te, panel, inst.cfg["eval"], "region")
    return {k: v["threshold"] for k, v in r["test"]["alert_rates"].items()}, r


def _shifted(tr, te):
    """Test rows replaced by train rows (a different score distribution), keys kept."""
    f = [c for c in te.columns if c not in ("week", "y") and not c.startswith("region")]
    out = te.copy(); out[f] = tr.sample(len(te), replace=True, random_state=0)[f].to_numpy()
    return out


def test_eval_thresholds_do_not_move_with_test(built):
    inst, _, m = built
    a, r = _thresholds(ev_mod, inst, m)
    b, _ = _thresholds(ev_mod, inst, m, _shifted)
    assert a == b
    lt = r["lead_time_test_10pct"]
    assert lt["alert_threshold"] == a["10pct"] and lt["threshold_from"] == "val"
    assert {k: round(v["nominal_rate"], 2) for k, v in r["test"]["alert_rates"].items()} == {"5pct": 0.05, "10pct": 0.1, "20pct": 0.2}
    assert all(abs(v["realised_rate"] - v["n_alerts"] / r["test"]["n"]) < 1e-12 for v in r["test"]["alert_rates"].values())


def test_p4_invariance_control_can_fail(built):
    """C-009: thresholds fixed on the final model's TEST scores pass every runtime identity check (fixed == applied ==
    lead) — only the real-path invariance test sees them, and it must."""
    inst, _, m = built
    mod = planted("P4_fixed_from_test_scores")
    a, _ = _thresholds(mod, inst, m)
    b, _ = _thresholds(mod, inst, m, _shifted)
    assert a != b, "a test-derived threshold went unnoticed — the invariance control passes by construction"


def test_hab_reading_moves_with_test(built):
    """The same control, fed hab's own reading (threshold_from: test), also fails — as it must."""
    inst, _, m = built
    i2 = copy.copy(inst); i2.cfg = {**inst.cfg, "eval": {**inst.cfg["eval"], "threshold_from": "test"}}
    assert _thresholds(ev_mod, i2, m)[0] != _thresholds(ev_mod, i2, m, _shifted)[0]


def test_p3_lead_threshold_from_test_is_refused(built):
    inst, _, m = built
    with pytest.raises(ObligationError, match="F-8: lead time read threshold"):
        _thresholds(planted("P3_lead_threshold_from_test"), inst, m)


def test_evaluate_ignoring_fixed_thresholds_is_refused(built):
    """hab's after-the-fact quantile planted beneath the threshold (evaluate drops `thresholds`): read back, refused."""
    inst, _, m = built
    mod = planted()
    real = mod.evaluate
    mod.evaluate = lambda y, p, label, rates, bins, **kw: real(y, p, label, rates, bins)
    with pytest.raises(ObligationError, match="F-8: applied thresholds"):
        _thresholds(mod, inst, m)


def test_val_mode_refuses_to_quantile_the_scored_set():
    """`val` without thresholds fixed beforehand would silently quantile the test scores — refused, not defaulted."""
    y, p = np.array([0, 1] * 50), np.linspace(0, 1, 100)
    with pytest.raises(ValueError, match="fixed beforehand"):
        at_alert_rates(y, p, RATES, threshold_from="val")


# ── (b) a fold stopped on its test year — and its eras ─────────────────────────────────────────────────────────────

def _years(*ys):
    return pd.DataFrame({"week": pd.to_datetime([f"{y}-06-01" for y in ys])})


def test_fold_selection_rule():
    check_fold_selection(2018, _years(2015, 2016, 2017), _years(2018))


@pytest.mark.parametrize("s_tr, s_va", [
    (_years(2016, 2017), _years(2019)),          # stopped on its test year
    (_years(2016, 2017, 2018), _years(2018)),    # selection trained through the year it stops on
    (_years(2016, 2017), _years(2018, 2019)),    # the stop set reaches the test year
])
def test_fold_selection_rule_refuses(s_tr, s_va):
    with pytest.raises(ObligationError, match="F-8 fold 2018"):
        check_fold_selection(2018, s_tr, s_va)


@pytest.mark.parametrize("plant, match", [
    ("P1_stop_on_test_year", r"F-8 fold 2015→2016: selection must train ≤ 2014 and stop on 2015"),
    ("P2_selection_eras_through_Y", r"F-8 fold 2015→2016: selection read eras"),
])
def test_planted_fold_defects_refused_in_the_real_loop(built, plant, match):
    inst, frames, m = built
    with pytest.raises(ObligationError, match=match):
        _run(planted(plant), inst, frames, m)


def test_clean_loop_selects_on_the_frames_it_fitted(built):
    inst, frames, m = built
    res, _ = _run(ev_mod, inst, frames, m)
    assert res["rolling_selection"] == "per_fold" and res["rolling_skipped"] == []
    for r in res["rolling_origin"]:
        assert r["selection"]["selected_on"] == [r["train_through"]]   # derived from the frame fit() received
    eras = {r["train_through"]: r["selection"]["selection_eras"]["atl_stream_usgs_discharge_daily"] for r in res["rolling_origin"]}
    assert eras[2015] == [1990, 2014] and eras[2016] == [1990, 2015] and eras[2017] == [1990, 2016]   # R7 on the inner split


def test_inner_year_with_too_few_positives_is_skipped_and_said(built):
    inst, frames, m = built
    thin = m[~((m.week.dt.year == 2018) & (m.y == 1))].copy()   # the 2018 stop set loses its onsets
    res, _ = _run(ev_mod, inst, frames, thin)
    assert {"test_year": 2019, "reason": "inner stop year 2018 has 0 positives (< 5)"} in res["rolling_skipped"]
    assert 2019 not in [r["test_year"] for r in res["rolling_origin"]]


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


SW = "learner_swap_logistic"


@pytest.mark.parametrize("plant, match", [   # III M-1e F-4: the swap is checked as the headline is; arithmetic, not labels
    (lambda r, s: s[SW]["full"]["test"]["alert_rates"]["10pct"].update(threshold_from="test"),
     f"learner swap {SW} budget 0.1: threshold_from 'test'"),
    (lambda r, s: s[SW]["full"]["lead_time_test_10pct"].update(threshold_from="test"), f"learner swap {SW} lead_time: threshold_from 'test'"),
    (lambda r, s: s[SW]["full"]["test"]["alert_rates"]["5pct"].pop("realised_rate"), f"learner swap {SW} budget 0.05: no realised rate"),
    (lambda r, s: r["full"]["test"]["alert_rates"]["10pct"].update(realised_rate=0.10), r"budget 0.1: realised rate 0.1 is not n_alerts / n_test"),
    (lambda r, s: r["full"]["test"]["alert_rates"]["20pct"].update(threshold_from="validation"), r"budget 0.2: threshold_from 'validation'"),
    (lambda r, s: r["full"]["lead_time_test_10pct"].update(alert_threshold=0.2295), r"headline lead_time: read threshold 0.2295, not the 10pct"),
    (lambda r, s: r["rolling_origin"][3]["selection"].update(selected_on=[2019]), r"rolling folds testing \[2019\] did not select on their own inner year"),
])
def test_planted_board_defects_refused_by_name(v2, plant, match):
    inst, res, shap, swaps = v2
    r, sw = copy.deepcopy(res), copy.deepcopy(swaps); plant(r, sw)
    with pytest.raises(BoardError, match=match):
        _emit(inst, r, shap, sw)


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

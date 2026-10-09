"""M-2c (P2 gate III G-3, C-034): T11 at its terms. Climatology is scored at the model's budgets under the model's M-1e rule,
and a season-block paired interval is drawn for model − climatology. Each defect is planted into the real source and caught
by name, and each control is shown able to fail (C-009)."""
import json, types
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core import eval as ev_mod
from atlantis_core.eval import ObligationError, embargo, split
from atlantis_core.eval import interval as iv_mod
from atlantis_core.eval.interval import IntervalError, assert_whole_blocks, season_block_interval
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames

EVAL_PLANTS = {
    # thresholds quantiled from the scores they then judge: passes the read-back (fixed == applied), so only the
    # real-path invariance test can see it (P4's shape, C-009)
    "C1_climatology_thresholds_from_test": (
        "fixed = fixed_thresholds(p_val, rates, tf)                 # set BEFORE test is scored",
        "fixed = fixed_thresholds(climatology_scores(base_fit, test)[0], rates, tf)"),   # (C-1 is unchanged by F-4)
    # the selection fit not embargoed against val: its last H weeks are labelled by validation. Since III M-2c-i F-4 (plant
    # B, C-037) the label windows are checked on the frame the fit RECEIVES, so this is the same defect as the reviewer's B
    "C2_climatology_selection_unembargoed": ('p_val, sel_years, sel_rows = fit_scored(embargo(train, s["val_start"], E), val,',
                                             "p_val, sel_years, sel_rows = fit_scored(train, val,"),
    # the selection fit reads validation itself
    "C2b_climatology_selection_reads_val": ('p_val, sel_years, sel_rows = fit_scored(embargo(train, s["val_start"], E), val,',
                                            'p_val, sel_years, sel_rows = fit_scored(pd.concat([embargo(train, s["val_start"], E), val]), val,'),
    # III M-2c-i plant B as the reviewer wrote it: the fit bypasses the checking helper with the unembargoed frame
    "B_fit_bypasses_the_check": ('p_val, sel_years, sel_rows = fit_scored(embargo(train, s["val_start"], E), val, "climatology selection→val", s["val_start"])',
                                 'p_val, sel_years, sel_rows = climatology_scores(train, val)'),
}
INTERVAL_PLANTS = {
    # rows resampled, not seasons: 21 zones in one week become 21 independent draws
    "C3_rows_not_seasons": ("idx = _draw(chosen, blocks)", "idx = rng.choice(len(y), size=len(y), replace=True)"),
    # III M-2c-i plant A (C-037): rows resampled INSIDE the drawn seasons, after the draw — the guard must read what is scored
    "A_rows_resampled_after_the_draw": ("idx = _draw(chosen, blocks)",
                                        "idx = _draw(chosen, blocks); idx = rng.choice(idx, size=len(idx), replace=True)"),
    # model and comparator each get their own draw: no longer paired
    "C4_unpaired": ("yc = yy                                               # the comparator is scored on the model's draw: paired",
                    "c_idx = _draw(rng.choice(labels, size=B, replace=True), blocks); yc, cc = y[c_idx], p_comp[c_idx]"),
}


def planted(mod, plants: dict, *names: str):
    """A fresh copy of `mod` with the named plants written into its source."""
    src = Path(mod.__file__).read_text()
    for name in names:
        old, new = plants[name]
        assert src.count(old) == 1, f"plant {name}: the line it replaces moved — update the plant, do not drop it"
        src = src.replace(old, new)
    m = types.ModuleType(f"planted_{'_'.join(names)}")
    m.__dict__["__file__"] = mod.__file__
    exec(compile(src, f"<planted {names}>", "exec"), m.__dict__)
    for k in ("ObligationError", "IntervalError"):
        if hasattr(mod, k):
            setattr(m, k, getattr(mod, k))
    return m


@pytest.fixture(scope="module")
def built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    m = m.copy(); m["y"] = m["y"].astype(int)
    return inst, m


def _clim(mod, inst, m, test_override=None):
    s = inst.cfg["split"]
    tr, va, te = split(m, s)
    if test_override is not None:
        te = test_override(te)
    E, _ = ev_mod._embargo_of(inst)
    base_fit = pd.concat([tr, embargo(va, s["test_start"], E)])
    return mod.climatology_at_budget(inst, tr, va, te, base_fit, inst.cfg["eval"]), te


def _winter_dropped(te):
    """A different test season mix (no Dec–Feb weeks), keys kept: thresholds fixed on validation cannot move."""
    return te[~te["week"].dt.month.isin([12, 1, 2])]


# ── climatology at budget ─────────────────────────────────────────────────────────────────────────────────────────────

def test_climatology_at_budget_on_the_exemplar(built):
    inst, m = built
    (blk, p), te = _clim(ev_mod, inst, m)
    s = inst.cfg["split"]
    assert blk["threshold_from"] == "val" and blk["n_test"] == len(te) == len(p)
    assert blk["selection_fit_years"][1] < s["val_start"] and blk["fit_years"][1] < s["test_start"]
    for k, r in blk["alert_rates"].items():
        assert r["threshold_from"] == "val"
        assert abs(r["realised_rate"] - r["n_alerts"] / len(te)) < 1e-12
    # tied week-of-year scores: the realised rate is not the nominal one, and that is the point of reporting it
    assert any(abs(r["realised_rate"] - r["nominal_rate"]) > 0.01 for r in blk["alert_rates"].values())


def test_climatology_auroc_auprc_did_not_move(built, exemplar_dir):
    """The score/metric split leaves the pinned numbers alone, to the bit (hab port · v2 reproduction)."""
    inst, m = built
    s = inst.cfg["split"]
    tr, va, te = split(m, s)
    E, _ = ev_mod._embargo_of(inst)
    got = ev_mod.climatology_baseline(pd.concat([tr, embargo(va, s["test_start"], E)]), te)
    v4 = json.loads((exemplar_dir / "outputs/atlantis_core_v4/metrics.json").read_text())["climatology_baseline_test"]
    assert got["auroc"] == v4["auroc"] and got["auprc"] == v4["auprc"]


def test_climatology_thresholds_do_not_move_with_test(built):
    inst, m = built
    (a, _), _ = _clim(ev_mod, inst, m)
    (b, _), _ = _clim(ev_mod, inst, m, _winter_dropped)
    thr = lambda blk: {k: v["threshold"] for k, v in blk["alert_rates"].items()}
    assert thr(a) == thr(b)


def test_c1_invariance_control_can_fail(built):
    """C-009: thresholds quantiled from test pass the read-back; only the invariance test sees them, and it must."""
    inst, m = built
    mod = planted(ev_mod, EVAL_PLANTS, "C1_climatology_thresholds_from_test")
    (a, _), _ = _clim(mod, inst, m)
    (b, _), _ = _clim(mod, inst, m, _winter_dropped)
    thr = lambda blk: {k: v["threshold"] for k, v in blk["alert_rates"].items()}
    assert thr(a) != thr(b), "a test-derived climatology threshold went unnoticed — the control passes by construction"


@pytest.mark.parametrize("name,match", [("C2_climatology_selection_unembargoed", "embargo climatology selection→val"),
                                        ("B_fit_bypasses_the_check", r"climatology selection fit received \d+ rows"),
                                        ("C2b_climatology_selection_reads_val", r"embargo climatology selection→val|thresholds fixed by a fit through")])
def test_c2_selection_fit_defects_are_refused(built, name, match):
    inst, m = built
    with pytest.raises(ObligationError, match=match):
        _clim(planted(ev_mod, EVAL_PLANTS, name), inst, m)


def test_evaluate_ignoring_fixed_climatology_thresholds_is_refused(built):
    """at_alert_rates planted to quantile the scored set: read back, refused."""
    inst, m = built
    mod = planted(ev_mod, EVAL_PLANTS)   # a clean copy
    real = mod.at_alert_rates
    mod.at_alert_rates = lambda y, p, rates, **kw: real(y, p, rates, thresholds=None, threshold_from="test")
    with pytest.raises(ObligationError, match=r"F-8 \(climatology\): applied thresholds"):
        _clim(mod, inst, m)


# ── the season-block paired interval ──────────────────────────────────────────────────────────────────────────────────

def _seasons(n_years=5, n=120, seed=0, signal=1.0):
    rng = np.random.default_rng(seed)
    years = np.repeat(np.arange(2019, 2019 + n_years), n)
    y = (rng.random(len(years)) < 0.15).astype(int)
    p_model = y * signal + rng.normal(0, 1, len(y))
    p_comp = rng.normal(0, 1, len(y))
    return y, p_model, p_comp, years


def test_interval_shape_and_honesty():
    y, pm, pc, years = _seasons()
    out = season_block_interval(y, pm, pc, years, n_draws=300, seed=1)
    assert out["resample_unit"] == "season_year" and out["paired"] and out["n_blocks"] == 5
    assert out["n_distinct_multisets"] == comb(9, 5) == 126
    for m in ("auroc", "auprc"):
        r = out[m]
        assert r["lower"] <= r["upper"] and r["spans_zero"] == (r["lower"] <= 0 <= r["upper"])
    assert out["auroc"]["lower"] > 0   # a real signal against noise is distinguished even at 5 blocks
    assert season_block_interval(y, pm, pc, years, n_draws=300, seed=1) == out   # seeded


def test_identical_scores_give_exactly_zero():
    """Paired: the same draw scores both, so a comparator equal to the model differs by exactly 0 on every draw."""
    y, pm, _, years = _seasons()
    out = season_block_interval(y, pm, pm.copy(), years, n_draws=200, seed=2)
    assert all(out[m]["lower"] == out[m]["upper"] == out[m]["estimate"] == 0.0 for m in ("auroc", "auprc"))


def test_no_signal_spans_zero():
    y, _, pc, years = _seasons(signal=0.0)
    rng = np.random.default_rng(9)
    out = season_block_interval(y, rng.normal(0, 1, len(y)), pc, years, n_draws=300, seed=3)
    assert out["auroc"]["spans_zero"]


def test_whole_blocks_accepts_repeats_and_refuses_rows():
    blocks = {2020: np.array([0, 1, 2]), 2021: np.array([3, 4])}
    assert_whole_blocks(np.array([0, 1, 2, 0, 1, 2]), blocks, [2020, 2020]) is None
    with pytest.raises(IntervalError, match="rows were drawn, not seasons"):
        assert_whole_blocks(np.array([0, 1, 3, 4, 2]), blocks, [2020, 2021, 2020])


def test_c3_row_resampler_is_caught():
    y, pm, pc, years = _seasons()
    mod = planted(iv_mod, INTERVAL_PLANTS, "C3_rows_not_seasons")
    with pytest.raises(IntervalError, match="rows were drawn, not seasons"):
        mod.season_block_interval(y, pm, pc, years, n_draws=20, seed=0)


def test_a_rows_resampled_after_the_draw_are_caught():
    """III M-2c-i plant A (C-037): the guard reads the very indices that are scored, in the same call."""
    y, pm, pc, years = _seasons()
    mod = planted(iv_mod, INTERVAL_PLANTS, "A_rows_resampled_after_the_draw")
    with pytest.raises(IntervalError, match="rows were drawn, not seasons"):
        mod.season_block_interval(y, pm, pc, years, n_draws=20, seed=0)


def test_c4_unpaired_fails_the_identity_control():
    """C-009 / III F-8: what proves the pairing is the identical-scores control — under an unpaired draw it must fail."""
    y, pm, _, years = _seasons()
    mod = planted(iv_mod, INTERVAL_PLANTS, "C4_unpaired")
    out = mod.season_block_interval(y, pm, pm.copy(), years, n_draws=200, seed=2)
    assert not (out["auroc"]["lower"] == out["auroc"]["upper"] == 0.0)


def test_season_labels_start_month():
    w = pd.to_datetime(["2020-01-06", "2020-07-27", "2020-08-03", "2020-12-28", "2021-02-01"]).values
    assert iv_mod.season_labels(w, 8).tolist() == [2019, 2019, 2020, 2020, 2020]
    assert iv_mod.season_labels(w, 1).tolist() == [2020, 2020, 2020, 2020, 2021]
    with pytest.raises(IntervalError, match="expected 1…12"):
        iv_mod.season_labels(w, 13)


def test_sign_test_and_per_season():
    y, pm, pc, years = _seasons(n_years=4)
    out = season_block_interval(y, pm, pc, years, n_draws=100, seed=1)
    r = out["auroc"]
    assert r["seasons_scored"] == 4 and set(r["per_season"]) == {"2019", "2020", "2021", "2022"}
    assert r["seasons_favouring_model"] == sum(v > 0 for v in r["per_season"].values())
    assert iv_mod._sign_p(4, 4) == 1 / 16 and iv_mod._sign_p(0, 4) == 1.0
    assert out["level_is_nominal"] is True


def test_precision_at_count_breaks_ties_in_expectation():
    y = np.array([1, 0, 1, 0, 0, 1])
    s = np.array([0.9, 0.5, 0.5, 0.5, 0.5, 0.1])        # a four-way tie at the cut
    assert iv_mod.precision_at_count(y, s, 1) == 1.0
    assert iv_mod.precision_at_count(y, s, 3) == pytest.approx((1 + 2 * 0.25) / 3)
    assert iv_mod.precision_at_count(y, s, 0) == 0.0


def test_budget_deltas_point_estimate_is_the_two_budgets():
    from atlantis_core.eval.metrics import at_alert_rates
    y, pm, pc, years = _seasons()
    tm = {"10pct": float(np.quantile(pm, 0.9))}; tc = {"10pct": float(np.quantile(pc, 0.9))}
    out = season_block_interval(y, pm, pc, years, n_draws=100, seed=1, thresholds={"10pct": (tm["10pct"], tc["10pct"])})
    a = at_alert_rates(y, pm, (0.10,), thresholds=tm, threshold_from="val")["10pct"]
    b = at_alert_rates(y, pc, (0.10,), thresholds=tc, threshold_from="val")["10pct"]
    got = out["budgets"]["10pct"]
    assert got["precision"]["estimate"] == pytest.approx(a["precision"] - b["precision"], abs=1e-12)
    assert got["recall"]["estimate"] == pytest.approx(a["recall"] - b["recall"], abs=1e-12)
    mv = a["precision"] - iv_mod.precision_at_count(y, pc, a["n_alerts"])
    assert got["matched_volume_precision"]["estimate"] == pytest.approx(mv, abs=1e-12)


def test_one_season_and_one_class_are_refused():
    y, pm, pc, years = _seasons(n_years=1)
    with pytest.raises(IntervalError, match="no resample is possible"):
        season_block_interval(y, pm, pc, years, n_draws=10)
    _, pm2, pc2, years2 = _seasons()
    with pytest.raises(IntervalError, match="single class"):
        season_block_interval(np.zeros(len(years2), int), pm2, pc2, years2, n_draws=10)


# ── the board: T11 at its terms is required, and read against the result (exemplar v4 at core 0.7.0) ────────────────

import copy
from atlantis_core.board import (INTERVAL_KEY, BoardError, assert_climatology_at_budget, assert_green, assert_interval,
                                 emit, project)

RATES = (0.05, 0.10, 0.20)


@pytest.fixture(scope="module")
def v4(exemplar_dir):
    o = exemplar_dir / "outputs" / "atlantis_core_v4"
    res = json.loads((o / "metrics.json").read_text())
    shap = json.loads((o / "shap_summary.json").read_text())
    swaps = {"learner_swap_logistic": json.loads((o / "learner_swap_logistic.json").read_text())}
    return load_instance(exemplar_dir), res, shap, swaps


def _emit(inst, res, shap, swaps):
    return emit(res, inst, version=4, run_date="2026-10-08", recorded_at="2026-10-08T00:00:00Z", shap=shap, swaps=swaps)


def test_v4_carries_climatology_at_budget_and_the_interval(v4):
    inst, res, shap, swaps = v4
    e = _emit(inst, res, shap, swaps)
    ev, ex = e["evaluation"], e["evaluation_extras"]
    assert [b["rate"] for b in ev["climatology_alert_budgets"]] == list(RATES)
    assert all(b["threshold_from"] == "validation" and b["realised_rate"] is not None for b in ev["climatology_alert_budgets"])
    assert [iv["metric"] for iv in ev["paired_intervals"]] == ["auroc", "auprc"]
    # ruling 5: bloom seasons start in August, so the 2020–2023 test window holds 5 seasons, two of them partial
    assert all(iv["n_blocks"] == 5 and iv["resample_unit"] == "season_year" and iv["season_start_month"] == 8
               for iv in ev["paired_intervals"])
    px = ex["paired_interval"]
    assert px["blocks"] == [2019, 2020, 2021, 2022, 2023] and px["n_distinct_multisets"] == 126 and px["level_is_nominal"]
    assert set(px["budgets"]) == {"5pct", "10pct", "20pct"}
    assert all(set(b) >= {"precision", "recall", "matched_volume_precision"} for b in px["budgets"].values())
    assert ex["baselines"]["climatology"]["selection_fit_years"][1] < 2017
    # the projection is the result, never retyped
    cb = res["climatology_baseline_test"]["alert_rates"]
    assert [b["precision"] for b in ev["climatology_alert_budgets"]] == [round(cb[k]["precision"], 4) for k in ("5pct", "10pct", "20pct")]
    assert_green(e)


K = INTERVAL_KEY
RESULT_PLANTS = [
    (lambda r: r["climatology_baseline_test"].pop("alert_rates"), r"climatology at budget \(M-2c\): no climatology alert budgets"),
    (lambda r: r["climatology_baseline_test"].update(threshold_from="test"), r"climatology thresholds fixed on 'test'"),
    (lambda r: r["climatology_baseline_test"]["alert_rates"]["10pct"].update(threshold_from="test"), r"climatology budget 0.1: threshold_from 'test'"),
    (lambda r: r["climatology_baseline_test"]["alert_rates"]["5pct"].update(realised_rate=0.05), r"climatology budget 0.05: realised rate 0.05 is not n_alerts / n_test"),
    (lambda r: r["climatology_baseline_test"]["alert_rates"]["20pct"].pop("realised_rate"), r"climatology budget 0.2: no realised rate"),
    (lambda r: r["climatology_baseline_test"].update(selection_fit_years=[1994, 2019]), r"thresholds were fixed by a fit through 2019"),
    (lambda r: r["climatology_baseline_test"].update(fit_years=[1994, 2020]), r"climatology refit read rows through 2020"),
    (lambda r: r["climatology_baseline_test"].update(n_test=999), r"climatology scored 999 rows"),
    (lambda r: r.pop(K), r"paired interval \(M-2c\): paired_interval_model_vs_climatology missing"),
    (lambda r: r[K].update(resample_unit="zone_week"), r"resampled by 'zone_week'"),
    (lambda r: r[K].update(paired=False), r"paired interval \(M-2c\): not paired"),
    (lambda r: r[K].update(n_blocks=6), r"\(n_blocks 6\) are not the test seasons"),
    (lambda r: r[K].update(blocks=[2020, 2021, 2022, 2023]), r"are not the test seasons \[2019, 2020, 2021, 2022, 2023\]"),
    (lambda r: r[K].update(season_start_month=1), r"season_start_month 1 is not the instance's"),
    (lambda r: r[K].update(n_distinct_multisets=35), r"n_distinct_multisets 35 is not C\(2B−1, B\)"),
    (lambda r: r[K].update(n_draws=50, n_degenerate=0), r"50 draws — fewer than 200"),
    (lambda r: r[K].update(level_is_nominal=False), r"the level is not marked nominal"),
    (lambda r: r[K]["budgets"]["10pct"]["precision"].update(estimate=0.9), r"budget 10pct precision: Δ 0.9 is not model − climatology"),
    (lambda r: r[K]["budgets"].pop("20pct"), r"interval budgets \['10pct', '5pct'\] are not the model's"),
    (lambda r: r[K]["auroc"].update(spans_zero=True), r"auroc: spans_zero True but the interval is"),
    (lambda r: r[K]["auprc"].update(lower=0.9, upper=0.1), r"auprc: lower 0.9 > upper 0.1"),
    (lambda r: r[K].update(n_degenerate=2000), r"2000 of 2000 draws degenerate"),
]


@pytest.mark.parametrize("plant,match", RESULT_PLANTS)
def test_result_defects_refused_at_emit(v4, plant, match):
    inst, res, shap, swaps = v4
    r = copy.deepcopy(res); plant(r)
    with pytest.raises(BoardError, match=match):
        _emit(inst, r, shap, swaps)


@pytest.mark.parametrize("tamper,check,match", [
    (lambda ev: ev["climatology_alert_budgets"][1].update(precision=0.9), "clim", "climatology_alert_budgets is not the projection"),
    (lambda ev: ev["climatology_alert_budgets"].pop(), "clim", "climatology_alert_budgets is not the projection"),
    (lambda ev: ev["paired_intervals"][0].update(delta_lower=-0.2), "iv", "paired_intervals is not the projection"),
    (lambda ev: ev.pop("paired_intervals"), "iv", "paired_intervals is not the projection"),
])
def test_slots_must_equal_the_result(v4, tamper, check, match):
    inst, res, _, _ = v4
    ev = project(res, inst, version=4, recorded_at="2026-10-08T00:00:00Z")
    tamper(ev)
    with pytest.raises(BoardError, match=match):
        assert_climatology_at_budget(ev, res, RATES) if check == "clim" else assert_interval(ev, res, inst.cfg["eval"])


# ── BOARD.md (G-7): the lead cell names its budget nominal AND realised ──────────────────────────────────────────────

def test_lead_cell_prints_the_realised_rate():
    from atlantis_core.board.index import render
    entries = Path(__file__).resolve().parents[2] / "board" / "entries"
    md = render(entries)
    row = lambda eid: next(l for l in md.splitlines() if l.startswith(f"| [`{eid}`]"))
    assert "(@ 0.1 nominal · 0.2034 realised)" in row("2026-10-08_florida_keys_coral_v2")   # the G-7 case
    assert "realised —, threshold set on test after the fact (F-8)" in row("2026-10-02_gulf_karenia_brevis_v1")
    assert "(@ 0.1)" not in md
    assert "## Climatology at the same nominal budgets" in md and "not distinguished at this sample" in md
    assert "is not \\\"distinguished at that level\\\"" in md or "distinguished at that level" in md

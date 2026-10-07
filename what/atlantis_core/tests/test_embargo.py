"""M-1f: the label-horizon embargo (III M-1e F-6, C-022). A week's label reads t+1…t+H, so a fit or stop set's last H
weeks are labelled by the period after it. The embargo drops them; the check reads label windows on the frames the learner
received (never row years, C-018); `none` reproduces board v2 (C-025: both run, not asserted). The plants that break the
embargo in eval's own source are in test_f8.py, beside the F-8 plants they share a harness with."""
import copy, json

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core import eval as ev_mod
from atlantis_core.eval import ObligationError, check_label_windows, embargo, embargo_weeks, horizon_spill, split
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames

EV = {"horizon": 4, "threshold": 1.0, "direction": "above"}


# ── the setting ─────────────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("given, want", [({}, 4), ({"embargo_weeks": 4}, 4), ({"embargo_weeks": 6}, 6),
                                         ({"embargo_weeks": "none"}, 0), ({"embargo_weeks": 0}, 0)])
def test_embargo_weeks_resolves(given, want):
    assert embargo_weeks(given, 4) == want


@pytest.mark.parametrize("bad", [2, 3, -1, 4.0, True, False, None, "four", "None"])
def test_embargo_weeks_refuses(bad):
    with pytest.raises(ValueError, match="embargo_weeks"):
        embargo_weeks({"embargo_weeks": bad}, 4)


# ── the rule and the check, on a frame whose windows are known ──────────────────────────────────────────────────────

def _weeks(start, n, unit=1, y=0):
    return pd.DataFrame({"unit": unit, "week": pd.date_range(start, periods=n, freq="W-MON"), "y": y})


def test_embargo_drops_exactly_the_rows_whose_window_reads_the_next_year():
    f = _weeks("2016-11-07", 10)
    kept = embargo(f, 2017, 4)
    last, first_dropped = kept.week.max(), f.week[~f.week.isin(kept.week)].min()
    assert (last + pd.Timedelta(weeks=4)).year == 2016 and (first_dropped + pd.Timedelta(weeks=4)).year == 2017


def test_none_returns_the_same_frame():
    f = _weeks("2016-11-07", 10)
    assert embargo(f, 2017, 0) is f


def test_a_planted_crossing_row_fails_by_name():
    f = embargo(_weeks("2016-01-04", 52), 2017, 4)
    check_label_windows("val→test", f, 2017, 4)                                   # clean
    planted = pd.concat([f, _weeks("2016-12-26", 1)])                              # its window is 2017-01-02 … 01-23
    with pytest.raises(ObligationError, match=r"embargo val→test: 1 rows' label windows cross into 2017 \(latest ends 2017-01-23\)"):
        check_label_windows("val→test", planted, 2017, 4)


def test_the_check_reads_the_horizon_not_the_embargo():
    """An embargo shorter than H cannot pass a check that reads H (the setting itself refuses it, too)."""
    short = embargo(_weeks("2016-01-04", 52), 2017, 2)
    with pytest.raises(ObligationError, match="embargo x"):
        check_label_windows("x", short, 2017, 4)


def test_horizon_spill_counts_on_known_signal():
    f = _weeks("2016-11-28", 4).assign(y=1)                                         # Mondays 11-28 · 12-05 · 12-12 · 12-19
    wk = pd.date_range("2016-11-28", periods=12, freq="W-MON")
    sig = pd.Series(0.0, index=wk); sig[pd.Timestamp("2016-12-26")] = 2.0; sig[pd.Timestamp("2017-01-09")] = 2.0
    panel = pd.DataFrame({"unit": 1, "week": wk, "signal": sig.values})
    s = horizon_spill(f, panel, "unit", 2017, EV)
    # 11-28 window ends 12-26 (no crossing). 12-05 → 01-02: crosses, hit 12-26 inside. 12-12 → 01-09: crosses, hit inside.
    # 12-19 → 01-16: crosses, hit 12-26 inside. All positives that cross also hold inside the year.
    assert s == {"next_start": 2017, "rows": 4, "crossing_rows": 3, "positives": 4, "crossing_positives": 3,
                 "labelled_by_next": 0}
    sig[pd.Timestamp("2016-12-26")] = 0.0                                           # no 2016 crossing left: every crossing
    panel["signal"] = sig.values                                                    # positive holds only by 2017's signal
    s = horizon_spill(f, panel, "unit", 2017, EV)
    assert s["crossing_positives"] == 3 and s["labelled_by_next"] == 3


# ── on the exemplar ─────────────────────────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def built(exemplar_dir):
    from atlantis_core.run import signal_panel
    from atlantis_core.vitals.build import patient_grid
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    units, weeks = patient_grid(inst, frames)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    m = m.copy(); m["y"] = m["y"].astype(int)
    return inst, frames, m, signal_panel(inst, frames, units, weeks)


def test_exemplar_defaults_to_the_horizon(built):
    inst, *_ = built
    assert "embargo_weeks" not in inst.cfg["split"] and inst.event["horizon"] == 4
    assert embargo_weeks(inst.cfg["split"], inst.event["horizon"]) == 4


def test_spill_reproduces_the_m1e_review(built):
    """III M-1e F-6 counted, per inner stop year, the positives whose window reads the next year. Same method, same
    numbers; and the main split, measured here for the first time (M-1f)."""
    inst, _, m, panel = built
    s, ev = inst.cfg["split"], inst.event
    got = {Y: horizon_spill(m[m.week.dt.year == Y], panel, "region", Y + 1, ev) for Y in s["rolling_origin_years"]}
    assert {Y: (g["crossing_positives"], g["positives"]) for Y, g in got.items()} == {
        2015: (6, 28), 2016: (3, 41), 2017: (6, 27), 2018: (9, 67), 2019: (1, 27), 2020: (4, 11), 2021: (0, 67), 2022: (10, 31)}
    tr, va, _ = split(m, s)
    main = horizon_spill(tr, panel, "region", s["val_start"], ev), horizon_spill(va, panel, "region", s["test_start"], ev)
    assert [(x["crossing_rows"], x["crossing_positives"], x["labelled_by_next"]) for x in main] == [(25, 3, 3), (34, 1, 0)]


LOGISTIC = {"kind": "logistic", "C_grid": [1.0], "max_iter": 2000}


def _run(inst, m, panel, frames, E=None):
    from atlantis_core.eval.rolling import FoldTables
    i2 = copy.copy(inst)
    sp = inst.cfg["split"] if E is None else {**inst.cfg["split"], "embargo_weeks": E}
    i2.cfg = {**inst.cfg, "eval": {**inst.cfg["eval"], "ablations": []}, "split": sp}
    return ev_mod.run(i2, m, panel, fold_tables=FoldTables(inst, frames, m), learner_spec=LOGISTIC, log=lambda *_: None)[0]


def test_clean_run_embargoes_and_checks_every_boundary(built):
    inst, frames, m, panel = built
    res = _run(inst, m, panel, frames)
    e = res["embargo"]
    assert e["weeks"] == 4 and e["horizon"] == 4 and e["checked"]
    for name, nxt in [("train→val", 2017), ("val→test", 2020), ("refit→test", 2020)]:
        b = e["boundaries"][name]
        assert b["checked"] and b["next_start"] == nxt and pd.Timestamp(b["latest_window_end"]).year < nxt
    assert e["boundaries"]["train→val"]["rows_dropped"] == 25 and e["boundaries"]["val→test"]["rows_dropped"] == 34
    assert e["boundaries"]["refit→test"]["rows_dropped"] == 34          # the train tail is back in the refit
    assert e["spill"]["val→test"]["crossing_rows"] == 34
    assert res["full"]["val"]["n"] == res["splits"]["val"]["n"] - 34     # val metrics read the stop set's labels only
    for row in res["rolling_origin"]:
        Y = row["train_through"]
        bs = {**row["selection"]["embargo"], "refit→test": row["embargo"]["refit→test"]}
        assert set(bs) == {"train→stop", "stop→test", "refit→test"}
        for name, b in bs.items():
            assert b["checked"] and pd.Timestamp(b["latest_window_end"]).year < b["next_start"], (Y, name)
        assert bs["train→stop"]["next_start"] == Y and bs["stop→test"]["next_start"] == Y + 1


def test_none_is_recorded_as_unchecked_and_drops_nothing(built):
    inst, frames, m, panel = built
    res = _run(inst, m, panel, frames, E="none")
    e = res["embargo"]
    assert e["weeks"] == 0 and not e["checked"]
    assert all(not b["checked"] and b["rows_dropped"] == 0 for b in e["boundaries"].values())
    assert pd.Timestamp(e["boundaries"]["val→test"]["latest_window_end"]).year == 2020    # the spill v2 carried
    assert res["full"]["val"]["n"] == res["splits"]["val"]["n"]


# ── `none` reproduces board v2 (C-025: run both, compare every number) ───────────────────────────────────────────────

V2_METRICS = "outputs/atlantis_core_v2/metrics.json"


def _cmp(a, b, path=""):
    """Every key of b present in a and equal (floats to 1e-12, NaN == NaN) — as test_eval's port check."""
    if isinstance(b, dict):
        return sum(([f"{path}/{k} missing"] if k not in a else _cmp(a[k], b[k], f"{path}/{k}") for k in b), [])
    if isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} len {len(a)} != {len(b)}"]
        return sum((_cmp(x, y, f"{path}[{i}]") for i, (x, y) in enumerate(zip(a, b))), [])
    if isinstance(b, float):
        return [] if abs(a - b) <= 1e-12 or (np.isnan(a) and np.isnan(b)) else [f"{path} {a} != {b}"]
    return [] if a == b else [f"{path} {a} != {b}"]
PROVENANCE = {"atlantis_core", "semantic_hash", "config_bytes_md5", "features_report", "run_at"}


def test_none_reproduces_board_v2(built):
    """The full per-fold xgboost run (~1 min): every number board v2 was emitted from, to 1e-12."""
    from atlantis_core.eval.rolling import FoldTables
    from atlantis_core.run import relabel
    from atlantis_core.vitals.build import patient_grid
    inst, frames, m, panel = built
    units, weeks = patient_grid(inst, frames)
    table, _ = build(inst, frames)
    sens, _ = relabel(inst, frames, table, units, weeks, float(inst.cfg["eval"]["sensitivity_threshold"]))
    i2 = copy.copy(inst); i2.cfg = {**inst.cfg, "split": {**inst.cfg["split"], "embargo_weeks": "none"}}
    res, _ = ev_mod.run(i2, m, panel, fold_tables=FoldTables(inst, frames, m), sensitivity_df=sens, log=lambda *_: None)
    v2 = json.loads((inst.root / V2_METRICS).read_text())
    assert set(v2) - set(res) == PROVENANCE
    assert _cmp(res, {k: v for k, v in v2.items() if k not in PROVENANCE}) == []

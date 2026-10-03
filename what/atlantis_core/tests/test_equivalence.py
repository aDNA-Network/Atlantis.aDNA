"""The exemplar through atlantis_core == the exemplar through hab.build_features — except where hab was wrong.

Needs the exemplar's gitignored `data/processed/` (regenerate: `cd what/exemplars/gulf_karenia_brevis &&
.venv/bin/python -m hab.build_features`). Compares on the three committed raw parquets:

  * same patient grid (region × week rows, in order) and same modelling rows
  * 22 of 25 vitals exactly equal (NaN-aware)
  * sst_anom_t2 / sst_anom_t4 / sst_delta_4w equal EXCEPT on rows whose lag window contains a week with no OISST data:
    hab shifted the weekly SST table by ROW, so across one of OISST's 20 missing weeks a "2-week lag" was 3–4 weeks.
    atlantis_core shifts by calendar. Every differing row must be predicted by that rule (and they are all 1994–1998,
    train-only among MODELLING rows; in the full table they also fall in 1993 and 2023 — the 2023 rows are a test year,
    excluded today only because every one of them is dropped by the label filters). Operator ruling 2026-10-02: calendar-correct; M-1b-ii lands the corrected run as a new board version.
  * label, both drop flags, and the finalize report identical.
"""
import json
import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.grid import week_start
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames

GAP_SENSITIVE = {"sst_anom_t2": 2, "sst_anom_t4": 4, "sst_delta_4w": 4}
SST = "atl_stream_oisst_region_daily"


@pytest.fixture(scope="module")
def both(exemplar_dir):
    proc = exemplar_dir / "data" / "processed"
    if not (proc / "region_week_all.parquet").exists():
        pytest.skip("exemplar data/processed missing — run hab.build_features first")
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    model, report = finalize(inst, table)
    return dict(inst=inst, frames=frames, table=table, model=model, report=report,
                old=pd.read_parquet(proc / "region_week_all.parquet"), old_model=pd.read_parquet(proc / "features.parquet"),
                old_report=json.loads((proc / "features_report.json").read_text()))


def _differ(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return ~((np.isnan(a) & np.isnan(b)) | (a == b))


def test_same_grid(both):
    assert len(both["old"]) == len(both["table"]) == 25011
    assert (both["old"][["region", "week"]].values == both["table"][["region", "week"]].values).all()


def test_vitals_exact_except_gap_rows(both):
    """22 vitals exact. The 3 gap-sensitive vitals: (a) every differing row has a missing SST week in its lag window,
    and (b) — the tight rule (III F-9) — atlantis_core's value IS hab's lag-0 series shifted by CALENDAR weeks, on every
    row: so the only change is the lag definition, and nothing else hides in the excused rows."""
    inst, old, new = both["inst"], both["old"], both["table"]
    s = both["frames"][SST]
    wk = pd.DatetimeIndex(week_start(s["date"]).unique())
    missing = set(pd.date_range(wk.min(), wk.max(), freq="7D").difference(wk))
    assert len(missing) == 20
    exact = [f for f in inst.feature_names if f not in GAP_SENSITIVE]
    assert len(exact) == 22
    for f in exact:
        assert not _differ(old[f], new[f]).any(), f
    cal = lambda col, k: old.groupby("region")[col].shift(k)        # old table is a complete weekly grid per region
    expect = {"sst_anom_t2": cal("sst_anom_t0", 2), "sst_anom_t4": cal("sst_anom_t0", 4),
              "sst_delta_4w": old["sst_t0"] - cal("sst_t0", 4)}
    for f, k in GAP_SENSITIVE.items():
        bad = _differ(old[f], new[f])
        predicted = np.array([any(w - pd.Timedelta(weeks=j) in missing for j in range(k + 1)) for w in new["week"]])
        assert bad.any() and not (bad & ~predicted).any(), f
        assert not _differ(expect[f], new[f]).any(), f"{f}: not the calendar-shifted hab series"


def test_gap_rows_are_train_only(both):
    m = both["model"].merge(both["old_model"], on=["region", "week"], suffixes=("", "_old"))
    years = set()
    for f in GAP_SENSITIVE:
        years |= set(m.loc[_differ(m[f + "_old"], m[f]), "week"].dt.year)
    assert years and max(years) <= both["inst"].cfg["split"]["train_end"]


def test_label_and_drops_identical(both):
    old, new = both["old"], both["table"]
    assert old["y"].astype(float).fillna(-1).equals(new["y"].astype(float).fillna(-1))
    assert (old["already_in_bloom"].values == new["already_in_event"].values).all()
    assert (old["outcome_unknown"].values == new["outcome_unknown"].values).all()


def test_modelling_rows_and_report_identical(both):
    o, n = both["old_report"], both["report"]
    assert (o["region_weeks_in_window"], o["dropped_already_in_bloom"], o["dropped_outcome_unknown"], o["modelling_rows"],
            o["positives"], o["prevalence"]) == (n["patient_weeks_in_window"], n["dropped_already_in_event"],
                                                 n["dropped_outcome_unknown"], n["modelling_rows"], n["positives"], n["prevalence"])
    assert (both["old_model"][["region", "week"]].values == both["model"][["region", "week"]].values).all()

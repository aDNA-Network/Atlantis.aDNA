"""M-3b-ii-b-1: `atlantis_core.scan` picks a constant on validation and never reads test.

A synthetic world on the forked variant + a Keys-wide wind stream (test_vitals_mask_offsets.add_wind), 2005–2023: calm
weeks lower the oxygen, so the calm-day count carries signal and the scan has something real to choose on.
"""
from __future__ import annotations

import json, shutil

import numpy as np
import pandas as pd
import pytest

from atlantis_core import scan as S
from atlantis_core.config import load_instance
from atlantis_core.eval import ObligationError
from atlantis_core.grid import week_start
from atlantis_core.vitals.build import normalise

from test_vitals_mask_offsets import WIND, add_wind

DO, SST = "atl_stream_example_do_daily", "atl_stream_example_sst_daily"


def world(inst, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    days = pd.date_range("2005-01-01", "2023-12-31", freq="D")
    doy = days.dayofyear.to_numpy()
    w = np.empty(len(days)); w[0] = 5.0
    for i in range(1, len(days)):                                      # persistent wind, m/s
        w[i] = 5.0 + 0.8 * (w[i - 1] - 5.0) + rng.normal(0, 0.9)
    w = np.clip(w, 0.1, None)
    calm7 = pd.Series((w < 4.0).astype(float)).rolling(7, min_periods=1).sum().to_numpy()
    raw = {}
    parts = []
    for st, bias in (("W1", 0.0), ("W2", 1.0), ("W3", -0.5)):
        keep = rng.random(len(days)) > 0.05
        parts.append(pd.DataFrame({"date": days[keep], "station": st, "wspd": (w + bias)[keep],
                                   "qc_low_ratio_causal": False}))
    raw[WIND] = pd.concat(parts, ignore_index=True)
    parts = []
    for st in ("EXS01", "EXS02", "EXS03"):
        do = 5.2 + 1.2 * np.cos(2 * np.pi * doy / 365.25) - 0.45 * calm7 + rng.normal(0, 0.5, len(days))
        parts.append(pd.DataFrame({"date": days, "station": st, "do_mg_l": do}))
    raw[DO] = pd.concat(parts, ignore_index=True)
    raw[SST] = pd.concat([pd.DataFrame({"date": days, "seg": u, "sst": 25 + 3 * np.sin(2 * np.pi * doy / 365.25)
                                        + rng.normal(0, 1, len(days))}) for u in (1, 2)], ignore_index=True)
    return {sid: normalise(inst, sid, r) for sid, r in raw.items()}


@pytest.fixture
def windy(variant_master, tmp_path):
    d = tmp_path / "inst"
    shutil.copytree(variant_master, d)
    return load_instance(add_wind(d))


def _strip(r):
    return json.dumps(S._json(r), sort_keys=True)


def test_scan_chooses_on_val_and_reports_a_green_table(windy):
    frames = world(windy)
    r = S.scan(windy, "calm", [2.0, 4.0], frames=frames, log=lambda *a: None)
    assert r["test_scored"] is False and r["read_by"] == ["atl_vital_example_wind_calm_t0"]
    assert [row["value"] for row in r["rows"]] == [2.0, 4.0]
    assert r["chosen"] == min(r["rows"], key=lambda x: x["val"]["log_loss"])["value"]
    assert len({row["semantic_hash"] for row in r["rows"]}) == 2               # each value its own config
    for row in r["rows"]:
        assert row["val"]["positives"] > 0 and 0 < row["val"]["base_rate"] < 1
        assert set(row["val"]) == {"n", "positives", "base_rate", "log_loss", "auroc", "auprc"}
    off = r["station_offsets"][WIND]
    assert off["W1"]["offset"] == 0.0 and off["W2"]["offset"] == pytest.approx(1.0, abs=1e-9)
    assert off["W3"]["offset"] == pytest.approx(-0.5, abs=1e-9)


def test_scan_never_reads_test_years(windy):
    """Poison every test-WEEK row of every stream (values and mask flags): the scan's output must not move by a byte. A test week
    is one whose ISO week starts in a test year — eval.split's definition. (1–5 Jan of the first test year belong to the
    last val week; poisoning them moves that week's vitals, and the embargo is what keeps its label out of the stop set.)"""
    frames = world(windy)
    r0 = S.scan(windy, "calm", [3.0, 4.0], frames=frames, log=lambda *a: None)
    ts = int(windy.cfg["split"]["test_start"])
    bad = {k: v.copy() for k, v in frames.items()}
    for sid in bad:                                     # III F-10: every stream, and every flag column
        d = bad[sid]
        late = week_start(d["date"]).dt.year >= ts
        d.loc[late, "value"] = np.where(np.arange(late.sum()) % 2, np.inf, -np.inf)
        for c in windy.stream_spec(sid).get("mask_columns") or []:
            d.loc[late, c] = True
        assert late.any()
    r1 = S.scan(windy, "calm", [3.0, 4.0], frames=bad, log=lambda *a: None)
    assert _strip(r0) == _strip(r1)


def test_scan_refuses_test_rows_that_survive_the_cut(windy, monkeypatch):
    frames = world(windy)
    real = S.split
    def leaky(df, s):
        tr, va, _ = real(df, s)
        return tr, va, va.iloc[:1]
    monkeypatch.setattr(S, "split", leaky)
    with pytest.raises(ObligationError, match="test rows survived the cut"):
        S.scan(windy, "calm", [4.0], frames=frames, log=lambda *a: None)


def test_scan_refuses_a_fit_that_received_test_years(windy, monkeypatch):
    frames = world(windy)
    real = S.select
    def sneaky(L, train, val, s, E):
        """The embargo would drop a future row before the learner; this plant records one as RECEIVED, which is what
        the guard reads (C-023)."""
        R, vm, info, stop = real(L, train, val, s, E)
        late = val.iloc[:3].assign(week=pd.Timestamp(f"{s['test_start']}-03-02"))
        R.fits.append(("fit", pd.concat([train, late]), stop))
        return R, vm, info, stop
    monkeypatch.setattr(S, "select", sneaky)
    with pytest.raises(ObligationError, match="received rows from"):
        S.scan(windy, "calm", [4.0], frames=frames, log=lambda *a: None)


def test_scan_refuses_an_undeclared_or_unread_constant(windy):
    with pytest.raises(ValueError, match="not declared"):
        S.scan(windy, "nope", [1.0], frames={}, log=lambda *a: None)
    windy.cfg["constants"]["unused"] = 1.0
    with pytest.raises(ValueError, match="no vital reads constant 'unused'"):
        S.scan(windy, "unused", [1.0], frames={}, log=lambda *a: None)


def test_scan_refuses_values_scored_on_different_stop_rows(windy, monkeypatch):
    """III F-11: a value that changed the stop set would win or lose on different rows."""
    frames = world(windy)
    real, calls = S.select, []
    def shrinking(L, train, val, s, E):
        R, vm, info, stop = real(L, train, val, s, E)
        calls.append(1)
        return R, vm, info, (stop if len(calls) == 1 else stop.iloc[:-1])
    monkeypatch.setattr(S, "select", shrinking)
    with pytest.raises(ObligationError, match="different stop rows"):
        S.scan(windy, "calm", [3.0, 4.0], frames=frames, log=lambda *a: None)

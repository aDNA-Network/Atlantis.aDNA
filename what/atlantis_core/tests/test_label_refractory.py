"""label: the onset refractory (M-2a-i, atl_v0 0.5.0). A hand-built persistent, flickering series, one unit:

    week   0  1  2  3  4  5  6  7  8  9 10 11
    DHW    0  0  5  5  3  5  0  0  0  0  0  0      threshold 4 · above · H = 2

R = 0 drops only weeks at or past threshold (2, 3, 5), so week 4 — a dip between two crossings of ONE episode — is kept
as a fresh positive (its future holds week 5). R = 2 drops weeks whose signal crossed in t−2 … t: 4, 6 and 7 go too, so
the episode yields its pre-onset ramp (weeks 0, 1) and nothing else."""
import pandas as pd
import pytest

from atlantis_core import label

WEEKS = pd.date_range("2020-01-06", periods=12, freq="7D")
SIG = pd.DataFrame({"u1": [0, 0, 5, 5, 3, 5, 0, 0, 0, 0, 0, 0]}, index=WEEKS, dtype=float)
PRES = pd.DataFrame({"u1": [7.0] * 12}, index=WEEKS)


class _Stream:
    def weekly(self, node):
        return SIG.copy() if node.startswith("weekly_max") else PRES.copy()


class _Inst:
    def __init__(self, ev):
        self.event, self.cfg = ev, {"label": {"signal": "weekly_max(value)", "presence": "weekly_count(value)",
                                              "last_known_weeks": 1}}


def _make(monkeypatch, **extra):
    monkeypatch.setattr(label.grammar, "parse", lambda s, consts, where: s)
    ev = {"event_variable_stream": "s", "threshold": 4.0, "direction": "above", "horizon": 2, **extra}
    table = pd.DataFrame({"week": WEEKS, "unit": "u1"})
    return label.make(_Inst(ev), table, {"s": _Stream()}, ["u1"], WEEKS)


def test_r0_is_the_old_rule_and_keeps_the_flicker(monkeypatch):
    t0 = _make(monkeypatch)
    pd.testing.assert_frame_equal(t0, _make(monkeypatch, refractory_weeks=0))   # absent ≡ 0, same frame
    assert list(t0.index[t0["already_in_event"]]) == [2, 3, 5]
    assert t0.loc[4, "y"] == 1 and not t0.loc[4, "already_in_event"]           # the flicker: a second "onset"


def test_r2_drops_the_episode_tail(monkeypatch):
    t2 = _make(monkeypatch, refractory_weeks=2)
    assert list(t2.index[t2["already_in_event"]]) == [2, 3, 4, 5, 6, 7]
    kept = t2[~t2["already_in_event"]]
    assert list(kept.index[kept["y"] == 1]) == [0, 1]                           # one episode, one ramp
    pd.testing.assert_series_equal(t2["y"], _make(monkeypatch)["y"])          # R moves the drop, never the label


@pytest.mark.parametrize("bad", [-1, 2.5, True, "8"])
def test_bad_refractory_refused(monkeypatch, bad):
    with pytest.raises(ValueError, match="refractory_weeks"):
        _make(monkeypatch, refractory_weeks=bad)


# ── M-2a-i III F-4: the label's refractory paired with eval/lead.py's onset, through both modules ────────────────────
from atlantis_core.eval.lead import lead_time

W2 = pd.date_range("2020-01-06", periods=14, freq="7D")
SIG2 = pd.DataFrame({"u1": [0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0]}, index=W2, dtype=float)   # crossings at 3 and 7, H = 3


class _Stream2:
    def weekly(self, node):
        return SIG2.copy() if node.startswith("weekly_max") else pd.DataFrame({"u1": [7.0] * 14}, index=W2)


def _kept_positive_coverage(monkeypatch, R) -> float:
    """lead.py's detected fraction when the 'score' is 1 exactly on the label's KEPT positive rows: the share of the onsets
    lead.py counts that the label gives at least one kept positive row to."""
    monkeypatch.setattr(label.grammar, "parse", lambda s, consts, where: s)
    ev = {"event_variable_stream": "s", "threshold": 4.0, "direction": "above", "horizon": 3, "refractory_weeks": R}
    t = label.make(_Inst(ev), pd.DataFrame({"week": W2, "unit": "u1"}), {"s": _Stream2()}, ["u1"], W2)
    kept_pos = (~t["already_in_event"]) & t["y"].eq(1).fillna(False)
    panel = pd.DataFrame({"unit": "u1", "week": W2, "signal": SIG2["u1"].values, "p": kept_pos.astype(float).where(kept_pos)})
    r = lead_time(panel, unit_col="unit", threshold=4.0, direction="above", horizon=3, alert_threshold=0.5, test_start=2020)
    assert r["n_onsets"] == 2
    return r["detected_fraction"]


def test_refractory_h_minus_1_matches_lead_onsets(monkeypatch):
    assert _kept_positive_coverage(monkeypatch, 2) == 1.0      # R = H − 1: every lead.py onset keeps a positive row


def test_refractory_h_is_one_week_stricter(monkeypatch):
    assert _kept_positive_coverage(monkeypatch, 3) == 0.5      # R = H: the onset 4 weeks after the last crossing has none

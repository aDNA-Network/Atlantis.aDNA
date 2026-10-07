"""III M-1f F-4 / C-027: the embargo's cut and its check share one formula (`_window_end`); this test ties them to the
labeller itself. Every raw observation of the event stream in or after the next period is inflated (binned by the grid's
ISO-Monday week, as the label is), the labels are rebuilt through `label.make`, and no kept row may move — while a cut one
week short must leave a row that does. The boundary is exact in week-years: a year's last week can hold the first days of
January (README §Known limits 2b)."""
import pytest

from atlantis_core import load_instance
from atlantis_core.eval import embargo
from atlantis_core.grid import week_start
from atlantis_core.vitals.build import build, load_frames

COLS = ["y", "future_signal", "outcome_unknown", "already_in_event"]
KEYS = ["region", "week"]


@pytest.fixture(scope="module")
def world(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    base, _ = build(inst, frames)
    return inst, frames, base


def _moved(a, b, idx):
    x, y = a.loc[idx, COLS], b.loc[idx, COLS]
    return int((~((x == y) | (x.isna() & y.isna()))).any(axis=1).sum())


@pytest.mark.parametrize("which", ["train→val", "val→test"])
def test_kept_labels_do_not_read_the_next_period(world, which):
    inst, frames, base = world
    s, H, sid = inst.cfg["split"], int(inst.event["horizon"]), inst.event["event_variable_stream"]
    lo, nxt = (s["min_train_year"], s["val_start"]) if which == "train→val" else (s["val_start"], s["test_start"])
    rows = base[(base.week.dt.year >= lo) & (base.week.dt.year < nxt)]
    f = frames[sid].copy(); f.loc[week_start(f["date"]).dt.year.values >= nxt, "value"] = 1e12
    after, _ = build(inst, {**frames, sid: f})
    a, b = base.set_index(KEYS), after.set_index(KEYS)
    kept = embargo(rows, nxt, H).set_index(KEYS).index
    assert _moved(a, b, kept) == 0
    dropped = rows.set_index(KEYS).index.difference(kept)
    assert _moved(a, b, dropped) == len(dropped) > 0                       # every dropped row did read the next period
    short = embargo(rows, nxt, H - 1).set_index(KEYS).index
    assert _moved(a, b, short) > 0                                          # one week short: a kept label reads it

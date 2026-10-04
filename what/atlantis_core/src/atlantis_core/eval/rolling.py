"""Rolling origin with the R7 obligation honoured: every fold sees only normals it could have known.

A climatology normal is one statistic over its whole era (M-1b-i AAR Finding 3). A fold that trains through year Y
and tests Y+1 must not read a normal whose era reaches past Y, so each era is clipped to end at ≤ Y and the vitals of
every stream whose era moved are rebuilt through `vitals.build`. The label does not read a normal, so the fold's
modelling rows are unchanged; only the anomaly vitals move.
"""
from __future__ import annotations

import copy

import pandas as pd

from atlantis_core.label import finalize
from atlantis_core.vitals.build import build


def clipped_eras(inst, Y: int) -> dict:
    eras = {sid: inst.climatology(sid) for sid in (inst.cfg.get("climatology") or {})}
    out = {}
    for sid, (a, b) in eras.items():
        if b > Y:
            if a > Y:
                raise ValueError(f"R7 refit: fold training through {Y} precedes the whole {sid} era {a}–{b}; no normal is knowable")
            out[sid] = (a, Y)
        else:
            out[sid] = (a, b)
    return out


def with_eras(inst, eras: dict):
    """A shallow copy of `inst` whose climatology eras are `eras`; registries and obligations are shared, not re-checked."""
    i2 = copy.copy(inst)
    i2.cfg = {**inst.cfg, "climatology": {sid: list(e) for sid, e in eras.items()}}
    return i2


class FoldTables:
    """`fold(Y) → (modelling rows for that fold, eras used, rebuilt?)`. Rebuilds only when an era had to move.

    Memoised by the eras: per-fold selection (F-8, M-1e) reads the table for Y−1 as well as Y, so a rebuilt table is
    shared between the fold that tests Y and the selection of the fold that tests Y+1 (and between learner swaps)."""

    def __init__(self, inst, frames: dict, model_df: pd.DataFrame):
        self.inst, self.frames, self.model_df = inst, frames, model_df
        self.base = {sid: inst.climatology(sid) for sid in (inst.cfg.get("climatology") or {})}
        self._built: dict = {}

    def __call__(self, Y: int):
        eras = clipped_eras(self.inst, Y)
        if eras == self.base:
            return self.model_df, eras, False
        key = tuple(sorted(eras.items()))
        if key not in self._built:
            i2 = with_eras(self.inst, eras)
            table, _ = build(i2, self.frames)
            self._built[key], _ = finalize(i2, table)
        return self._built[key], eras, True

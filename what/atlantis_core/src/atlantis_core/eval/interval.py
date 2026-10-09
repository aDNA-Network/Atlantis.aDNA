"""A season-block paired interval for model − comparator (M-2c; P2 gate III G-3, C-034).

Zone-weeks are not independent: 21 zones in one hot week are one event seen 21 times. The unit that can be resampled is
the **season** (a test year). Each draw takes the test years with replacement, and the rows of a chosen year enter once
for each time it was chosen. **The same rows score both the model and the comparator**, which is what makes the interval
paired. The difference is then read on that shared draw.

With B season blocks there are only C(2B − 1, B) distinct draws. That is 35 at B = 4 and 1,716 at B = 7. The interval is
crude, and it says so: `n_blocks` and `n_distinct_multisets` travel with it. An interval that spans 0 is reported as
exactly that, which means "not distinguished at this sample". It never means "no difference".

Only summaries leave this module. The draws themselves never reach the board (green caps).
"""
from __future__ import annotations

from math import comb

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

__all__ = ["season_block_interval", "assert_whole_blocks", "IntervalError", "METRICS"]

METRICS = {"auroc": roc_auc_score, "auprc": average_precision_score}


class IntervalError(RuntimeError):
    pass


def _blocks(years) -> dict:
    years = np.asarray(years)
    return {int(y): np.flatnonzero(years == y) for y in np.unique(years)}


def assert_whole_blocks(idx, blocks: dict, chosen) -> None:
    """Check that a draw is a union of whole seasons. Every row of a season appears exactly as many times as that season
    was drawn, and every row belongs to some season. A row-level resample fails here, by name."""
    counts = np.bincount(np.asarray(idx), minlength=sum(len(b) for b in blocks.values()))
    times = {y: int(np.sum(np.asarray(chosen) == y)) for y in blocks}
    for y, rows in blocks.items():
        c = counts[rows]
        if not (c == times[y]).all():
            raise IntervalError(f"season-block resample: year {y} drawn {times[y]}× but its rows appear "
                                f"{sorted(set(c.tolist()))}× — rows were drawn, not seasons")


def _draw(chosen, blocks: dict):
    return np.concatenate([blocks[int(c)] for c in chosen])


def season_block_interval(y, p_model, p_comp, years, *, comparator: str = "climatology", n_draws: int = 2000,
                          seed: int = 0, level: float = 0.95) -> dict:
    """model − comparator, on AUROC and AUPRC, by percentile over `n_draws` season-block draws (seeded).

    A draw with only one class can score neither metric. It is counted in `n_degenerate` and left out, never imputed."""
    y, p_model, p_comp, years = (np.asarray(a) for a in (y, p_model, p_comp, years))
    if not (len(y) == len(p_model) == len(p_comp) == len(years)):
        raise IntervalError(f"season-block interval: lengths differ — y {len(y)}, model {len(p_model)}, "
                            f"{comparator} {len(p_comp)}, years {len(years)}")
    blocks = _blocks(years)
    seasons = np.array(sorted(blocks))
    B = len(seasons)
    if B < 2:
        raise IntervalError(f"season-block interval: {B} season(s) in test — no resample is possible")
    rng = np.random.default_rng(seed)
    deltas = {m: [] for m in METRICS}
    n_degenerate = 0
    for _ in range(n_draws):
        chosen = rng.choice(seasons, size=B, replace=True)
        idx = _draw(chosen, blocks)
        assert_whole_blocks(idx, blocks, chosen)
        idx_model, idx_comp = idx, idx                       # one draw scores both: paired
        if not np.array_equal(idx_model, idx_comp):
            raise IntervalError("season-block interval: the model and the comparator were scored on different draws "
                                "— the interval is not paired")
        yy = y[idx_model]
        if yy.min() == yy.max():
            n_degenerate += 1
            continue
        for m, f in METRICS.items():
            deltas[m].append(f(yy, p_model[idx_model]) - f(y[idx_comp], p_comp[idx_comp]))
    if n_degenerate == n_draws:
        raise IntervalError("season-block interval: every draw held a single class")
    lo_q, hi_q = (1 - level) / 2, 1 - (1 - level) / 2
    out = {"comparator": comparator, "resample_unit": "season_year", "blocks": [int(s) for s in seasons],
           "n_blocks": B, "n_distinct_multisets": comb(2 * B - 1, B), "n_draws": int(n_draws),
           "n_degenerate": n_degenerate, "seed": int(seed), "level": float(level), "paired": True,
           "scope": "this run's full model on the main test split — not its ablations, sensitivity run or rolling folds"}
    for m, f in METRICS.items():
        d = np.asarray(deltas[m])
        lo, hi = float(np.quantile(d, lo_q)), float(np.quantile(d, hi_q))
        out[m] = {"estimate": float(f(y, p_model) - f(y, p_comp)), "lower": lo, "upper": hi,
                  "spans_zero": bool(lo <= 0.0 <= hi)}
    return out

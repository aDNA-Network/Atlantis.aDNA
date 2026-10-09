"""A season-block paired interval for model − comparator (M-2c; P2 gate III G-3, C-034).

Zone-weeks are not independent: 21 zones in one hot week are one event seen 21 times. The unit that can be resampled is
the **season**, a season-year that starts at the instance's declared month (`eval.interval_season_start_month`; 1 is a
calendar year; III M-2c-i F-5, ruling 5). With a start month other than January, the test window's edges are partial
seasons, and they are blocks like any other. Each draw takes the seasons with replacement, and the rows of a chosen
season enter once for each time it was chosen. **The same rows score both the model and the comparator**, which makes it
paired.

**What it reports, and how to read it (III M-2c-i F-2, C-036).**
- **The bounds are percentiles at a NOMINAL level.** With B blocks there are only C(2B − 1, B) distinct draws (35 at
  B = 4). The percentile interval under-covers at small B. The reviewer's simulation gave about 0.80 at B = 4 and about
  0.87 at B = 7 for a nominal 0.95, under ideal independence. "Spans 0: no" at small B is therefore NOT "distinguished at
  95%".
- **Read beside it, per season:** the season's own delta, how many of the B seasons favour the model, and the exact
  one-sided sign test.
- **At each budget (ruling 4, F-3):** model − comparator precision and recall at the thresholds each fixed on
  validation, in the same draws. Also the **matched-volume** precision: the model's precision minus the comparator's
  expected precision at the same number of alerts the model raised in that draw. Ties are broken at random in
  expectation, because climatology ties in whole week groups.

Only summaries leave this module. The draws themselves never reach the board (green caps).
"""
from __future__ import annotations

from math import comb

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

__all__ = ["season_block_interval", "season_labels", "assert_whole_blocks", "precision_at_count", "IntervalError",
           "METRICS"]

METRICS = {"auroc": roc_auc_score, "auprc": average_precision_score}


class IntervalError(RuntimeError):
    pass


def season_labels(weeks, start_month: int = 1) -> np.ndarray:
    """The season-year of each week: its year if month ≥ start_month, else the year before (a season is named by the
    year it starts in). start_month = 1 → calendar years."""
    if not 1 <= int(start_month) <= 12:
        raise IntervalError(f"interval_season_start_month {start_month!r} — expected 1…12")
    weeks = np.asarray(weeks, dtype="datetime64[ns]")
    yrs = weeks.astype("datetime64[Y]").astype(int) + 1970
    mon = weeks.astype("datetime64[M]").astype(int) % 12 + 1
    return np.where(mon >= int(start_month), yrs, yrs - 1)


def _blocks(seasons) -> dict:
    seasons = np.asarray(seasons)
    return {int(y): np.flatnonzero(seasons == y) for y in np.unique(seasons)}


def assert_whole_blocks(idx, blocks: dict, chosen) -> None:
    """Check that a draw is a union of whole seasons. Every row of a season appears exactly as many times as that
    season was drawn, and every row belongs to some season. A row-level resample fails here, by name."""
    idx = np.asarray(idx)
    n = sum(len(b) for b in blocks.values())
    if len(idx) and (idx.min() < 0 or idx.max() >= n):
        raise IntervalError("season-block resample: an index outside the test rows")
    counts = np.bincount(idx, minlength=n)
    times = {y: int(np.sum(np.asarray(chosen) == y)) for y in blocks}
    for y, rows in blocks.items():
        c = counts[rows]
        if not (c == times[y]).all():
            raise IntervalError(f"season-block resample: season {y} drawn {times[y]}× but its rows appear "
                                f"{sorted(set(c.tolist()))}× — rows were drawn, not seasons")


def _draw(chosen, blocks: dict):
    return np.concatenate([blocks[int(c)] for c in chosen])


def _take(idx, blocks: dict, chosen, *arrays):
    """The rows a draw scores, checked as they are taken (III F-4, C-037): the guard reads the very indices that are
    consumed, in the same call, so a resample between check and use cannot pass."""
    assert_whole_blocks(idx, blocks, chosen)
    return tuple(a[idx] for a in arrays)


def precision_at_count(y, s, n: int) -> float:
    """Expected precision of the top `n` scores, ties at the cut broken at random (climatology ties in whole week-of-year
    groups, so 'the top n' is otherwise undefined)."""
    if n <= 0:
        return 0.0
    order = np.sort(s)[::-1]
    t = order[min(n, len(s)) - 1]
    above, tie = s > t, s == t
    take = min(n, len(s)) - int(above.sum())
    exp_tp = y[above].sum() + take * (y[tie].mean() if tie.any() else 0.0)
    return float(exp_tp / n)


def _at(y, s, thr):
    a = s >= thr
    tp = (a & (y == 1)).sum()
    return float(tp / max(a.sum(), 1)), float(tp / max((y == 1).sum(), 1)), int(a.sum())


def _budget_deltas(y, pm, pc, thresholds: dict) -> dict:
    out = {}
    for k, (tm, tc) in thresholds.items():
        prm, rcm, nm = _at(y, pm, tm)
        prc, rcc, _ = _at(y, pc, tc)
        out[k] = {"precision": prm - prc, "recall": rcm - rcc, "matched_volume_precision": prm - precision_at_count(y, pc, nm)}
    return out


def _summ(d, est, lo_q, hi_q) -> dict:
    d = np.asarray(d)
    lo, hi = float(np.quantile(d, lo_q)), float(np.quantile(d, hi_q))
    return {"estimate": float(est), "lower": lo, "upper": hi, "spans_zero": bool(lo <= 0.0 <= hi)}


def _sign_p(k: int, n: int) -> float:
    """One-sided exact sign test: P(at least k of n seasons favour the model | each side equally likely)."""
    return float(sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n) if n else 1.0


def season_block_interval(y, p_model, p_comp, seasons, *, comparator: str = "climatology", thresholds: dict | None = None,
                          season_start_month: int = 1, n_draws: int = 2000, seed: int = 0, level: float = 0.95) -> dict:
    """model − comparator by percentile over `n_draws` season-block draws (seeded), on AUROC and AUPRC and, given
    `thresholds` ({budget key: (model threshold, comparator threshold)}, each fixed beforehand), at each budget.

    A draw with only one class can score neither metric. It is counted in `n_degenerate` and left out, never imputed."""
    y, p_model, p_comp, seasons = (np.asarray(a) for a in (y, p_model, p_comp, seasons))
    if not (len(y) == len(p_model) == len(p_comp) == len(seasons)):
        raise IntervalError(f"season-block interval: lengths differ — y {len(y)}, model {len(p_model)}, "
                            f"{comparator} {len(p_comp)}, seasons {len(seasons)}")
    blocks = _blocks(seasons)
    labels = np.array(sorted(blocks))
    B = len(labels)
    if B < 2:
        raise IntervalError(f"season-block interval: {B} season(s) in test — no resample is possible")
    thresholds = thresholds or {}
    rng = np.random.default_rng(seed)
    deltas = {m: [] for m in METRICS}
    bdel = {k: {q: [] for q in ("precision", "recall", "matched_volume_precision")} for k in thresholds}
    n_degenerate = 0
    for _ in range(n_draws):
        chosen = rng.choice(labels, size=B, replace=True)
        idx = _draw(chosen, blocks)
        yy, mm, cc = _take(idx, blocks, chosen, y, p_model, p_comp)
        yc = yy                                               # the comparator is scored on the model's draw: paired
        if yy.min() == yy.max():
            n_degenerate += 1
            continue
        for m, f in METRICS.items():
            deltas[m].append(f(yy, mm) - f(yc, cc))
        for k, v in _budget_deltas(yy, mm, cc, thresholds).items():
            for q, x in v.items():
                bdel[k][q].append(x)
    if n_degenerate == n_draws:
        raise IntervalError("season-block interval: every draw held a single class")
    lo_q, hi_q = (1 - level) / 2, 1 - (1 - level) / 2
    out = {"comparator": comparator, "resample_unit": "season_year", "season_start_month": int(season_start_month),
           "blocks": [int(s) for s in labels], "block_rows": {str(s): int(len(blocks[s])) for s in labels},
           "n_blocks": B, "n_distinct_multisets": comb(2 * B - 1, B), "n_draws": int(n_draws),
           "n_degenerate": n_degenerate, "seed": int(seed), "level": float(level), "level_is_nominal": True,
           "paired": True,
           "scope": "this run's full model on the main test split — not its ablations, sensitivity run or rolling folds"}
    for m, f in METRICS.items():
        r = _summ(deltas[m], f(y, p_model) - f(y, p_comp), lo_q, hi_q)
        per = {}
        for s in labels:
            ys = y[blocks[s]]
            if ys.min() != ys.max():
                per[str(s)] = float(f(ys, p_model[blocks[s]]) - f(ys, p_comp[blocks[s]]))
        k = sum(1 for v in per.values() if v > 0)
        r.update({"per_season": per, "seasons_scored": len(per), "seasons_favouring_model": k,
                  "sign_test_p_one_sided": _sign_p(k, len(per))})
        out[m] = r
    if thresholds:
        full = _budget_deltas(y, p_model, p_comp, thresholds)
        out["budgets"] = {k: {**{q: _summ(bdel[k][q], full[k][q], lo_q, hi_q) for q in bdel[k]},
                              "model_threshold": float(thresholds[k][0]), f"{comparator}_threshold": float(thresholds[k][1])}
                          for k in thresholds}
    return out

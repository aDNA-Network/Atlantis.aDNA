"""Scores read against their base rate (SO-9). Ported from `hab.train` unchanged: the port-equivalence test
(`tests/test_eval.py`) holds these to `metrics.json` on hab's own vitals."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, brier_score_loss, precision_recall_curve, roc_auc_score,
                             roc_curve)


def calibration(y, p, bins: int = 10):
    q = pd.qcut(p, bins, labels=False, duplicates="drop")
    g = pd.DataFrame({"y": y, "p": p, "bin": q}).groupby("bin").agg(pred=("p", "mean"), obs=("y", "mean"), n=("y", "size"))
    slope = np.polyfit(g["pred"], g["obs"], 1)[0] if len(g) > 2 else np.nan
    return g.reset_index().to_dict("records"), float(slope)


def rate_key(r: float) -> str:
    return f"{int(r * 100)}pct"


THRESHOLD_FROM = ("val", "test")


def quantile_thresholds(p, rates) -> dict:
    """The alert threshold for each budget: the (1 − r) quantile of the scores `p`."""
    return {rate_key(r): float(np.quantile(p, 1 - r)) for r in rates}


def at_alert_rates(y, p, rates=(0.05, 0.10, 0.20), *, thresholds: dict | None = None, threshold_from: str = "test"):
    """The alert budget: alert on the top `r` of scores. Precision at a budget a steward can staff is the number
    that matters; a bare AUROC is not a result here.

    `thresholds` (rate_key → threshold), when given, is APPLIED rather than taken from `p`: it was fixed beforehand on
    other scores (`threshold_from: val`, M-1e / F-8). The rate a steward then actually gets is `realised_rate` — reported
    beside the nominal one, never instead of it (SO-9). Without `thresholds` the quantile is of `p` itself
    (`threshold_from: test` — hab's after-the-fact reading, kept so the port reproduces)."""
    if threshold_from not in THRESHOLD_FROM:
        raise ValueError(f"threshold_from {threshold_from!r} — expected one of {THRESHOLD_FROM}")
    if (thresholds is None) != (threshold_from == "test"):
        raise ValueError("threshold_from: test quantiles the scored set itself; val needs thresholds fixed beforehand")
    thr_by = thresholds if thresholds is not None else quantile_thresholds(p, rates)
    out = {}
    for r in rates:
        thr = thr_by[rate_key(r)]
        alert = p >= thr
        tp = (alert & (y == 1)).sum()
        out[rate_key(r)] = {"threshold": float(thr), "precision": float(tp / max(alert.sum(), 1)),
                            "recall": float(tp / max((y == 1).sum(), 1)), "n_alerts": int(alert.sum()),
                            "nominal_rate": float(r), "realised_rate": float(alert.sum() / max(len(p), 1)),
                            "threshold_from": threshold_from}
    return out


def evaluate(y, p, label: str, rates=(0.05, 0.10, 0.20), bins: int = 10, *, thresholds: dict | None = None,
             threshold_from: str = "test") -> dict:
    fpr, tpr, _ = roc_curve(y, p)
    prec, rec, _ = precision_recall_curve(y, p)
    cal, slope = calibration(y, p, bins)
    keep = np.linspace(0, len(fpr) - 1, min(len(fpr), 200)).astype(int)
    keep2 = np.linspace(0, len(rec) - 1, min(len(rec), 200)).astype(int)
    return {"split": label, "n": int(len(y)), "positives": int(y.sum()), "prevalence": float(y.mean()),
            "auroc": float(roc_auc_score(y, p)), "auprc": float(average_precision_score(y, p)),
            "brier": float(brier_score_loss(y, p)), "calibration": cal, "calibration_slope": slope,
            "alert_rates": at_alert_rates(y, p, rates, thresholds=thresholds, threshold_from=threshold_from),
            "roc": {"fpr": fpr[keep].round(4).tolist(), "tpr": tpr[keep].round(4).tolist()},
            "pr": {"recall": rec[keep2].round(4).tolist(), "precision": prec[keep2].round(4).tolist()}}


def climatology_baseline(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Week-of-year onset rate from the training years: the 'no model' comparator (T11)."""
    woy = lambda d: d["week"].dt.isocalendar().week.astype(int)
    rate = train.assign(woy=woy(train)).groupby("woy")["y"].mean()
    p = woy(test).map(rate).fillna(train["y"].mean()).astype(float).values
    return {"auroc": float(roc_auc_score(test["y"].astype(int), p)),
            "auprc": float(average_precision_score(test["y"].astype(int), p))}

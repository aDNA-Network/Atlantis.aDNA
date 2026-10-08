"""Scores read against their base rate (SO-9). Ported from `hab.train` unchanged: the port-equivalence test
(`tests/test_eval.py`) holds these to `metrics.json` on hab's own vitals."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, precision_recall_curve, roc_auc_score,
                             roc_curve)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


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
            # ruling 16 (M-2b): mean(p) − prevalence — > 0 over-predicts. Under a base-rate shift a model fitted on low-rate
            # years under-predicts the high-rate years even when its ranking holds; the slope alone does not show that
            "calibration_in_the_large": float(np.mean(p) - np.mean(y)),
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


# ── the no-model comparators where the event variable is also a vital (M-2b; steward ruling 19) ─────────────────────────
# DHW accumulates: DHW(t) nearly decides DHW(t+k), so a model that reads DHW(t) can score high without adding anything.
# These say what the event signal alone, read at t, already knows. Both read ONLY the signal as the label carries it
# (`label.last_known_weeks`), so persistence's s(t) IS the label's `last_known_signal` (tests/test_baselines.py proves it
# on the exemplar). They score test once; the trend is fitted on the refit's rows, as climatology is.

def signal_history(panel: pd.DataFrame, unit_col: str, last_known_weeks: int) -> pd.DataFrame:
    """Per unit-week: `s_t`, the event signal carried forward at most `last_known_weeks` (the label's rule), and `s_prev`,
    the same at t−1. Reads the past only."""
    g = panel[[unit_col, "week", "signal"]].sort_values([unit_col, "week"]).reset_index(drop=True)
    L = int(last_known_weeks)
    s_t = g.groupby(unit_col)["signal"].ffill(limit=L) if L else g["signal"].copy()   # pandas refuses limit=0
    s_prev = s_t.groupby(g[unit_col]).shift(1)
    return pd.DataFrame({unit_col: g[unit_col], "week": g["week"], "s_t": s_t, "s_prev": s_prev})


def _signal_on(rows: pd.DataFrame, hist: pd.DataFrame, unit_col: str) -> pd.DataFrame:
    out = rows[[unit_col, "week"]].merge(hist, on=[unit_col, "week"], how="left", validate="m:1")
    if len(out) != len(rows):
        raise ValueError(f"signal history: {len(rows)} rows became {len(out)} on the merge")
    return out


def _years(frame: pd.DataFrame) -> list:
    return [int(frame["week"].dt.year.min()), int(frame["week"].dt.year.max())]


def persistence_baseline(fit: pd.DataFrame, test: pd.DataFrame, hist: pd.DataFrame, *, unit_col: str,
                         direction: str) -> dict:
    """Test rows ranked by s(t) itself — no fit (`below` events rank by −s). A missing s(t) takes the fit rows' median,
    and the count of those rows is reported, never hidden. AUROC/AUPRC are rank-based, so no calibration is claimed."""
    if direction not in ("above", "below"):
        raise ValueError(f"direction {direction!r} — expected above | below")
    x = _signal_on(test, hist, unit_col)["s_t"]
    med = _signal_on(fit, hist, unit_col)["s_t"].median()
    n_imp = int(x.isna().sum())
    x = x.fillna(med if pd.notna(med) else 0.0).astype(float).values
    p = x if direction == "above" else -x
    y = test["y"].astype(int).values
    return {"auroc": float(roc_auc_score(y, p)), "auprc": float(average_precision_score(y, p)),
            "score": "s(t), carried as the label carries it", "n_test": int(len(test)), "n_imputed": n_imp}


def trend_baseline(fit: pd.DataFrame, test: pd.DataFrame, hist: pd.DataFrame, *, unit_col: str) -> dict:
    """A logistic fit on [s(t), s(t) − s(t−1)] — the signal and its last step — on `fit`, scored once on `test`. Missing
    values take the fit rows' medians; the test rows that needed one are counted. `fit_years` is read from the frame the
    fit received (C-023), so a caller that fitted on the wrong rows is seen by what it did, not by what it meant."""
    def X(rows):
        h = _signal_on(rows, hist, unit_col)
        return pd.DataFrame({"s_t": h["s_t"].values, "step": (h["s_t"] - h["s_prev"]).values})
    Xf, Xt = X(fit), X(test)
    med = Xf.median().fillna(0.0)
    n_imp = int(Xt.isna().any(axis=1).sum())
    Xf, Xt = Xf.fillna(med), Xt.fillna(med)
    yf, yt = fit["y"].astype(int).values, test["y"].astype(int).values
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(Xf.values, yf)
    p = m.predict_proba(Xt.values)[:, 1]
    return {"auroc": float(roc_auc_score(yt, p)), "auprc": float(average_precision_score(yt, p)),
            "score": "logistic on [s(t), s(t) − s(t−1)]", "fit_years": _years(fit), "n_fit": int(len(fit)),
            "n_test": int(len(test)), "n_imputed": n_imp}

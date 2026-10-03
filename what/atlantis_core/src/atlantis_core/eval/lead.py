"""Lead time: how much warning the alert budget buys (T6). Ported from `hab.train.lead_time`, made direction-aware.

An onset is a week whose event signal crosses the threshold (`above`: ≥ · `below`: ≤) after `horizon` weeks in which
it did not (unobserved counts as not). For each onset in the test years, the lead is how many weeks before it the
score first reached the alert threshold inside the horizon; −1 = not flagged. `panel` is the FULL unit-week grid (every
week, scored or not) with the event signal and the test scores merged in as `p` (NaN where not scored).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def crossed(signal: pd.Series, threshold: float, direction: str) -> np.ndarray:
    hit = signal.ge(threshold) if direction == "above" else signal.le(threshold)
    return hit.fillna(False).astype(bool).values


def lead_time(panel: pd.DataFrame, *, unit_col: str, threshold: float, direction: str, horizon: int,
              alert_threshold: float, test_start: int, signal_col: str = "signal") -> dict:
    if direction not in ("above", "below"):
        raise ValueError(f"direction {direction!r} — expected above | below")
    H, leads = int(horizon), []
    for _, g in panel.groupby(unit_col):
        g = g.sort_values("week").reset_index(drop=True)
        obs = crossed(g[signal_col], threshold, direction)
        for i in np.where(obs)[0]:
            if g.loc[i, "week"].year < test_start or i < H or obs[i - H:i].any():
                continue
            window = g.iloc[i - H:i]
            fired = window[window["p"].ge(alert_threshold).fillna(False)]
            leads.append(int((g.loc[i, "week"] - fired.iloc[0]["week"]).days // 7) if len(fired) else -1)
    hist = {str(k): int(v) for k, v in pd.Series(leads, dtype=int).value_counts().sort_index().items()}
    det = [l for l in leads if l >= 0]
    return {"n_onsets": len(leads), "histogram_weeks_before_onset": hist,
            "detected_fraction": float(len(det) / len(leads)) if leads else None,
            "median_lead_weeks": float(np.median(det)) if det else None}

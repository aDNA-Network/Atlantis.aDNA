"""Train the onset classifier with a leakage-safe temporal split; write metrics + models.
Run: .venv/bin/python -m hab.train                      # the reference run → outputs/metrics.json + models
     .venv/bin/python -m hab.train --negative-control   # T4 control: AUPRC early-stopping → outputs/negative_control_auprc_stop.json
"""
import json, hashlib, sys
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve, precision_recall_curve
from hab import load_config, DATA_PROC, OUT, ROOT
from hab.build_features import FEATURES, FEATURE_GROUPS


def split(df, cfg):
    y = df["week"].dt.year
    s = cfg["split"]
    return (df[(y >= s["min_train_year"]) & (y <= s["train_end"])],
            df[(y >= s["val_start"]) & (y <= s["val_end"])],
            df[(y >= s["test_start"]) & (y <= s["test_end"])])


def params(cfg, features):
    p = dict(cfg["xgb"])
    mono = p.pop("monotone_increasing")
    p.pop("n_estimators"); p.pop("early_stopping_rounds")
    p["monotone_constraints"] = "(" + ",".join("1" if f in mono else "0" for f in features) + ")"
    return p


def fit(train, val, cfg, features):
    p = params(cfg, features)
    clf = xgb.XGBClassifier(n_estimators=cfg["xgb"]["n_estimators"],
                            early_stopping_rounds=cfg["xgb"]["early_stopping_rounds"], **p)
    clf.fit(train[features], train["y"].astype(int), eval_set=[(val[features], val["y"].astype(int))], verbose=False)
    best = int(clf.best_iteration) + 1
    # final: refit on train+val at the early-stopped size, then score test exactly once
    final = xgb.XGBClassifier(n_estimators=best, **p)
    both = pd.concat([train, val])
    final.fit(both[features], both["y"].astype(int), verbose=False)
    return clf, final, best


def calibration(y, p, bins=10):
    q = pd.qcut(p, bins, labels=False, duplicates="drop")
    g = pd.DataFrame({"y": y, "p": p, "bin": q}).groupby("bin").agg(pred=("p", "mean"), obs=("y", "mean"), n=("y", "size"))
    slope = np.polyfit(g["pred"], g["obs"], 1)[0] if len(g) > 2 else np.nan
    return g.reset_index().to_dict("records"), float(slope)


def at_alert_rates(y, p, rates=(0.05, 0.10, 0.20)):
    out = {}
    for r in rates:
        thr = np.quantile(p, 1 - r)
        alert = p >= thr
        tp = (alert & (y == 1)).sum()
        out[f"{int(r*100)}pct"] = {"threshold": float(thr), "precision": float(tp / max(alert.sum(), 1)),
                                    "recall": float(tp / max((y == 1).sum(), 1)), "n_alerts": int(alert.sum())}
    return out


def lead_time(panel, cfg, alert_threshold, test_start):
    """Onset = a week whose observed max >= threshold after >= 4 weeks below it (or unobserved). For each onset in the
    test years, the lead time is how many weeks before it the score first crossed the alert threshold, within the horizon.
    `panel` is the FULL region-week table (all weeks) with the test scores merged in as `p` (NaN where not scored)."""
    thr = np.log10(1 + cfg["target"]["bloom_threshold_cells_per_l"])
    H = cfg["target"]["horizon_weeks"]
    leads = []
    for _, g in panel.groupby("region"):
        g = g.sort_values("week").reset_index(drop=True)
        obs = g["log_max"].ge(thr).fillna(False).values
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


def evaluate(y, p, label):
    fpr, tpr, _ = roc_curve(y, p)
    prec, rec, _ = precision_recall_curve(y, p)
    cal, slope = calibration(y, p)
    keep = np.linspace(0, len(fpr) - 1, min(len(fpr), 200)).astype(int)
    keep2 = np.linspace(0, len(rec) - 1, min(len(rec), 200)).astype(int)
    return {"split": label, "n": int(len(y)), "positives": int(y.sum()), "prevalence": float(y.mean()),
            "auroc": float(roc_auc_score(y, p)), "auprc": float(average_precision_score(y, p)),
            "brier": float(brier_score_loss(y, p)), "calibration": cal, "calibration_slope": slope,
            "alert_rates": at_alert_rates(y, p),
            "roc": {"fpr": fpr[keep].round(4).tolist(), "tpr": tpr[keep].round(4).tolist()},
            "pr": {"recall": rec[keep2].round(4).tolist(), "precision": prec[keep2].round(4).tolist()}}


def climatology_baseline(train, test, cfg):
    """Week-of-year onset rate from the training years, as the 'no model' comparator."""
    woy = lambda d: d["week"].dt.isocalendar().week.astype(int)
    rate = train.assign(woy=woy(train)).groupby("woy")["y"].mean()
    p = woy(test).map(rate).fillna(train["y"].mean()).astype(float).values
    return {"auroc": float(roc_auc_score(test["y"].astype(int), p)),
            "auprc": float(average_precision_score(test["y"].astype(int), p))}


def config_hash():
    """md5 of config.yaml's bytes, first 10 hex — the join key metrics.json / the board carry. NOTE (M-1a): a comment
    or a SHAP-only edit changes it; the committed metrics.json hash e9dea88254 is the S329 training-time config
    (shap.background_n: 2000), the live file hashes differently. atlantis_core (M-1b) hashes the parsed training-relevant
    sections instead."""
    return hashlib.md5(open(ROOT / "config.yaml", "rb").read()).hexdigest()[:10]


def negative_control():
    """Thesis T4 negative control: early-stop on validation AUPRC instead of log-loss — the S329 first attempt, which
    gave a 2-tree model. In-memory override only: config.yaml, metrics.json and the saved models are untouched."""
    cfg = load_config(); cfg["xgb"]["eval_metric"] = "aucpr"
    df = pd.read_parquet(DATA_PROC / "features.parquet"); df["y"] = df["y"].astype(int)
    train, val, test = split(df, cfg)
    clf, final, best = fit(train, val, cfg, FEATURES)
    keep = ("auroc", "auprc", "brier", "calibration_slope", "prevalence", "n", "positives")
    sub = lambda r: {**{k: r[k] for k in keep}, "alert_rate_10pct": r["alert_rates"]["10pct"]}
    metrics = json.load(open(OUT / "metrics.json")); ref = metrics["full"]
    out = {"control": "early_stopping_on_val_auprc", "thesis_claim": "T4 — calibration is the work: stop on log-loss, not AUPRC",
           "eval_metric_override": "aucpr", "live_config_hash": config_hash(), "reference_run_config_hash": metrics["config_hash"],
           "n_trees": best,
           "val": sub(evaluate(val["y"].values, clf.predict_proba(val[FEATURES])[:, 1], "val")),
           "test": sub(evaluate(test["y"].values, final.predict_proba(test[FEATURES])[:, 1], "test")),
           "reference_full_model": {"n_trees": ref["n_trees"], "test": sub(ref["test"])},
           "run_at": pd.Timestamp.now("UTC").isoformat(),
           "note": "Reproduces the S329 observation (2026-09-23): validation AUPRC is flat from the first split while log-loss keeps "
                   "improving, so AUPRC early-stopping halts almost immediately and the model is badly calibrated. Ranking is easy; "
                   "calibration is the work. Nothing here is a forecast (SO-4)."}
    (OUT / "negative_control_auprc_stop.json").write_text(json.dumps(out, indent=1))
    print(f"negative control: trees={best} test AUROC={out['test']['auroc']:.3f} AUPRC={out['test']['auprc']:.3f} "
          f"Brier={out['test']['brier']:.4f} cal-slope={out['test']['calibration_slope']:.2f} | reference trees={ref['n_trees']} "
          f"cal-slope={ref['test']['calibration_slope']:.2f} → outputs/negative_control_auprc_stop.json")


def main():
    if "--negative-control" in sys.argv:
        negative_control(); return
    cfg = load_config()
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(DATA_PROC / "features.parquet")
    df["y"] = df["y"].astype(int)
    train, val, test = split(df, cfg)
    rw_all = pd.read_parquet(DATA_PROC / "region_week_all.parquet")[["region", "week", "log_max"]]
    results = {"config_hash": config_hash(),
               "features": FEATURES, "feature_groups": FEATURE_GROUPS,
               "splits": {k: {"years": [int(v["week"].dt.year.min()), int(v["week"].dt.year.max())], "n": int(len(v)),
                              "positives": int(v["y"].sum())} for k, v in [("train", train), ("val", val), ("test", test)]}}

    variants = {"full": FEATURES, "no_surveillance": [f for f in FEATURES if f not in FEATURE_GROUPS["surveillance"]]}
    for name, feats in variants.items():
        clf, final, best = fit(train, val, cfg, feats)
        p_val = clf.predict_proba(val[feats])[:, 1]
        p_test = final.predict_proba(test[feats])[:, 1]
        r = {"n_trees": best, "val": evaluate(val["y"].values, p_val, "val"), "test": evaluate(test["y"].values, p_test, "test")}
        scored = test.assign(p=p_test)
        panel = rw_all.merge(scored[["region", "week", "p"]], on=["region", "week"], how="left")
        r["lead_time_test_10pct"] = lead_time(panel, cfg, r["test"]["alert_rates"]["10pct"]["threshold"], cfg["split"]["test_start"])
        r["gain_importance"] = {k: float(v) for k, v in sorted(final.get_booster().get_score(importance_type="gain").items(), key=lambda kv: -kv[1])}
        results[name] = r
        final.save_model(OUT / (f"model.json" if name == "full" else f"model_{name}.json"))
        if name == "full":
            scored.to_parquet(DATA_PROC / "test_scored.parquet", index=False)
            # also score EVERY modelling row (for the risk strip), using the final model — train rows are in-sample, flagged as such
            allp = df.assign(p=final.predict_proba(df[feats])[:, 1],
                             split=np.where(df.week.dt.year <= cfg["split"]["train_end"], "train",
                                            np.where(df.week.dt.year <= cfg["split"]["val_end"], "val", "test")))
            allp.to_parquet(DATA_PROC / "all_scored.parquet", index=False)
        print(f"{name}: trees={best} val AUROC={r['val']['auroc']:.3f} AUPRC={r['val']['auprc']:.3f} (prev {r['val']['prevalence']:.3f}) | "
              f"test AUROC={r['test']['auroc']:.3f} AUPRC={r['test']['auprc']:.3f} (prev {r['test']['prevalence']:.3f}) "
              f"cal-slope={r['test']['calibration_slope']:.2f} lead={r['lead_time_test_10pct']}")

    # single-feature surveillance baseline: how much does 'how hard we looked' alone predict?
    results["surveillance_only_test_auroc"] = float(roc_auc_score(test["y"], test["n_samples_4w"].fillna(0)))
    results["climatology_baseline_test"] = climatology_baseline(pd.concat([train, val]), test, cfg)

    # rolling-origin panel (full feature set)
    p = params(cfg, FEATURES)
    panel = []
    for Y in cfg["split"]["rolling_origin_years"]:
        tr = df[df.week.dt.year <= Y]; te = df[df.week.dt.year == Y + 1]
        if te["y"].sum() < 5: continue
        m = xgb.XGBClassifier(n_estimators=results["full"]["n_trees"], **p).fit(tr[FEATURES], tr["y"], verbose=False)
        pp = m.predict_proba(te[FEATURES])[:, 1]
        panel.append({"train_through": Y, "test_year": Y + 1, "n": int(len(te)), "positives": int(te["y"].sum()),
                      "prevalence": float(te["y"].mean()), "auroc": float(roc_auc_score(te["y"], pp)),
                      "auprc": float(average_precision_score(te["y"], pp))})
        print(f"  rolling {Y}→{Y+1}: AUROC {panel[-1]['auroc']:.3f} AUPRC {panel[-1]['auprc']:.3f} prev {panel[-1]['prevalence']:.3f}")
    results["rolling_origin"] = panel

    # sensitivity: 5e4 threshold label (same features), reported as a headline pair only
    thr2 = np.log10(1 + cfg["target"]["sensitivity_threshold"])
    df2 = df.copy(); df2["y"] = (df2["future_log_max"] >= thr2).astype(int)
    df2 = df2[~df2["last_obs_log_max"].ge(thr2).fillna(False)]
    tr2, va2, te2 = split(df2, cfg)
    _, f2, b2 = fit(tr2, va2, cfg, FEATURES)
    p2 = f2.predict_proba(te2[FEATURES])[:, 1]
    results["sensitivity_50k"] = {"test_auroc": float(roc_auc_score(te2["y"], p2)), "test_auprc": float(average_precision_score(te2["y"], p2)),
                                  "test_prevalence": float(te2["y"].mean()), "n_trees": b2}
    (OUT / "metrics.json").write_text(json.dumps(results, indent=1))
    print("→ outputs/metrics.json")


if __name__ == "__main__":
    main()

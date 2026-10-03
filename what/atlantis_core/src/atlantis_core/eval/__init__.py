"""Training and evaluation: the temporal split, the learner, and every number the board carries (SO-9).

    res, art = run(inst, model_df, panel, fold_tables=FoldTables(...), sensitivity_df=...)

`model_df` is `label.finalize`'s modelling table; `panel` is the full unit-week grid with the event `signal` (for lead
time). `res` mirrors the exemplar's `metrics.json` keys; `art` holds models and scored frames (never on the board).

**R7 obligations.** If `inst.obligations` is non-empty, `run` refuses to start without `fold_tables` (the per-fold
refit). `reference=True` is the one exception — the port-equivalence check against hab, which did not refit — and the
result then says so in `obligations` and cannot be emitted to the board.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from atlantis_core.config import feature_name
from atlantis_core.eval.lead import lead_time
from atlantis_core.eval.learners import learner
from atlantis_core.eval.metrics import climatology_baseline, evaluate, rate_key
from atlantis_core.eval.rolling import clipped_eras

__all__ = ["run", "split", "groups", "ObligationError"]


class ObligationError(RuntimeError):
    pass


def split(df: pd.DataFrame, s: dict):
    y = df["week"].dt.year
    return (df[(y >= s["min_train_year"]) & (y <= s["train_end"])],
            df[(y >= s["val_start"]) & (y <= s["val_end"])],
            df[(y >= s["test_start"]) & (y <= s["test_end"])])


def groups(inst) -> dict:
    out: dict = {}
    for v in inst.vitals:
        out.setdefault(v["group"], []).append(feature_name(v))
    return out


def _variant(inst, spec, feats, train, val, test, panel, ecfg, unit_col):
    L = learner(spec, feats, inst)
    vm, final, info = L.fit(train, val)
    rates, bins = tuple(ecfg["alert_rates"]), int(ecfg.get("calibration_bins", 10))
    p_test = L.predict(final, test)
    r = {**info, "learner": L.describe(info),
         "val": evaluate(val["y"].values, L.predict(vm, val), "val", rates, bins),
         "test": evaluate(test["y"].values, p_test, "test", rates, bins)}
    budget = float(ecfg["lead_budget"])
    ev = inst.event
    scored = test.assign(p=p_test)
    pan = panel.merge(scored[[unit_col, "week", "p"]], on=[unit_col, "week"], how="left")
    r[f"lead_time_test_{rate_key(budget)}"] = lead_time(
        pan, unit_col=unit_col, threshold=float(ev["threshold"]), direction=ev["direction"], horizon=int(ev["horizon"]),
        alert_threshold=r["test"]["alert_rates"][rate_key(budget)]["threshold"], test_start=inst.cfg["split"]["test_start"])
    r["gain_importance" if L.kind == "xgboost" else "importance"] = L.importance(final)
    return r, L, final, scored


def run(inst, model_df: pd.DataFrame, panel: pd.DataFrame, *, fold_tables=None, sensitivity_df=None,
        learner_spec: dict | None = None, reference: bool = False, log=print):
    if inst.obligations and fold_tables is None and not reference:
        raise ObligationError("eval refuses to run: unhonoured obligations (registry R7) —\n  " + "\n  ".join(inst.obligations))
    s, ecfg = inst.cfg["split"], inst.cfg["eval"]
    spec = learner_spec or inst.cfg["learner"]
    unit_col = inst.cfg["grid"].get("unit_column", "unit")
    df = model_df.copy(); df["y"] = df["y"].astype(int)
    feats = inst.feature_names
    grp = groups(inst)
    train, val, test = split(df, s)
    res = {"learner_kind": spec["kind"], "features": feats, "feature_groups": grp,
           "splits": {k: {"years": [int(v["week"].dt.year.min()), int(v["week"].dt.year.max())], "n": int(len(v)),
                          "positives": int(v["y"].sum())} for k, v in [("train", train), ("val", val), ("test", test)]}}
    art = {}
    variants = {"full": feats}
    for ab in ecfg.get("ablations", []) or []:
        g = ab["drop_group"]
        if g not in grp:
            raise ValueError(f"eval.ablations: no vital group {g!r} (groups: {sorted(grp)})")
        variants[f"no_{g}"] = [f for f in feats if f not in grp[g]]
    for name, fs in variants.items():
        r, L, final, scored = _variant(inst, spec, fs, train, val, test, panel, ecfg, unit_col)
        res[name] = r
        art[name] = {"learner": L, "model": final, "features": fs}
        if name == "full":
            art["test_scored"] = scored
            art["all_scored"] = df.assign(p=L.predict(final, df), split=np.where(
                df.week.dt.year <= s["train_end"], "train", np.where(df.week.dt.year <= s["val_end"], "val", "test")))
        lt = r[f"lead_time_test_{rate_key(float(ecfg['lead_budget']))}"]
        n_sel = r.get("n_trees", r.get("C"))
        log(f"{name}: {spec['kind']} [{n_sel}] val AUROC={r['val']['auroc']:.3f} AUPRC={r['val']['auprc']:.3f} | test AUROC="
            f"{r['test']['auroc']:.4f} AUPRC={r['test']['auprc']:.4f} (prev {r['test']['prevalence']:.3f}) "
            f"cal-slope={r['test']['calibration_slope']:.2f} lead={lt['detected_fraction']}/{lt['median_lead_weeks']}")

    so = ecfg.get("surveillance_only")
    if so:
        res["surveillance_only_test_auroc"] = float(roc_auc_score(test["y"], test[so].fillna(0)))
        res["surveillance_only_vital"] = so
    res["climatology_baseline_test"] = climatology_baseline(pd.concat([train, val]), test)

    # rolling origin: the full feature set, the selection from the full model held fixed (as hab.train)
    L, info = art["full"]["learner"], {k: res["full"][k] for k in ("n_trees", "C") if k in res["full"]}
    panel_ro, refit_years = [], []
    base = {sid: inst.climatology(sid) for sid in (inst.cfg.get("climatology") or {})}
    for Y in s["rolling_origin_years"]:
        if fold_tables is not None:
            fdf, eras, rebuilt = fold_tables(Y); fdf = fdf.copy(); fdf["y"] = fdf["y"].astype(int)
        else:
            fdf, eras, rebuilt = df, base, False
        need = clipped_eras(inst, Y)
        if inst.obligations and not reference and need != base and not (rebuilt and dict(eras) == need):
            # verified, not presumed: the fold callable must have rebuilt with exactly the clipped eras (III F-3)
            raise ObligationError(f"R7 fold {Y}→{Y + 1}: needs eras {need}, got {eras} (rebuilt={rebuilt}) — obligation not executed")
        tr, te = fdf[fdf.week.dt.year <= Y], fdf[fdf.week.dt.year == Y + 1]
        if te["y"].sum() < 5:
            continue
        pp = L.predict(L.refit_fixed(tr, info), te)
        row = {"train_through": Y, "test_year": Y + 1, "n": int(len(te)), "positives": int(te["y"].sum()),
               "prevalence": float(te["y"].mean()), "auroc": float(roc_auc_score(te["y"], pp)),
               "auprc": float(average_precision_score(te["y"], pp)),
               "climatology_eras": {k: list(v) for k, v in eras.items()}, "climatology_refit": bool(rebuilt)}
        panel_ro.append(row)
        if rebuilt:
            refit_years.append(Y + 1)
        log(f"  rolling {Y}→{Y+1}: AUROC {row['auroc']:.3f} AUPRC {row['auprc']:.3f} prev {row['prevalence']:.3f}"
            + ("  [climatology refit]" if rebuilt else ""))
    res["rolling_origin"] = panel_ro
    honoured = fold_tables is not None and not reference   # every fold needing a refit was checked above, or we raised
    res["obligations"] = [{"obligation": o, "honoured": honoured,
                           "how": (f"eras clipped to ≤ train_through; vitals rebuilt for folds testing {refit_years} (verified per fold)"
                                   if honoured else
                                   "NOT honoured — reference mode (port check against hab, which did not refit)")}
                          for o in inst.obligations]
    res["mode"] = "reference" if reference else "core"

    thr = ecfg.get("sensitivity_threshold")
    if thr is not None and sensitivity_df is not None:
        d2 = sensitivity_df.copy(); d2["y"] = d2["y"].astype(int)
        tr2, va2, te2 = split(d2, s)
        L2 = learner(spec, feats, inst)
        _, f2, i2 = L2.fit(tr2, va2)
        p2 = L2.predict(f2, te2)
        res["sensitivity"] = {"threshold": thr, "test_auroc": float(roc_auc_score(te2["y"], p2)),
                              "test_auprc": float(average_precision_score(te2["y"], p2)),
                              "test_prevalence": float(te2["y"].mean()), "n_test": int(len(te2)),
                              "positives_test": int(te2["y"].sum()), **i2}
    return res, art

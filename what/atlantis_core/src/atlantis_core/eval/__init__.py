"""Training and evaluation: the temporal split, the learner, and every number the board carries (SO-9).

    res, art = run(inst, model_df, panel, fold_tables=FoldTables(...), sensitivity_df=...)

`model_df` is `label.finalize`'s modelling table; `panel` is the full unit-week grid with the event `signal` (for lead
time). `res` mirrors the exemplar's `metrics.json` keys; `art` holds models and scored frames (never on the board).

**R7 obligations.** If `inst.obligations` is non-empty, `run` refuses to start without `fold_tables` (the per-fold
refit). `reference=True` is the one exception — the port-equivalence check against hab, which did not refit — and the
result then says so in `obligations` and cannot be emitted to the board.

**F-8 (M-1e): nothing is chosen on the years it scores.** `eval.threshold_from: val` (default) fixes every alert-budget
threshold — and so the lead-time threshold — on the selection model's out-of-sample validation scores BEFORE test is
scored, and reports the realised test alert rate beside the nominal one. `eval.rolling_selection: per_fold` (default)
early-stops each rolling fold on its own inner validation year (train ≤ Y−1, stop on Y, refit ≤ Y), with the R7 eras
clipped to ≤ Y−1 for that selection; no fold reuses a count stopped on its test year. `test` / `full_model` are hab's
after-the-fact readings, kept so the port reproduces; the board refuses them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from atlantis_core.config import feature_name
from atlantis_core.eval.lead import lead_time
from atlantis_core.eval.learners import learner
from atlantis_core.eval.metrics import THRESHOLD_FROM, climatology_baseline, evaluate, quantile_thresholds, rate_key
from atlantis_core.eval.rolling import clipped_eras

__all__ = ["run", "split", "groups", "ObligationError", "check_thresholds_fixed", "eval_modes"]

ROLLING_SELECTION = ("per_fold", "full_model")


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


def check_fold_selection(Y: int, s_tr: pd.DataFrame, s_va: pd.DataFrame) -> None:
    """F-8, checked per fold: a fold testing Y+1 selects on rows strictly before it, on its inner year Y."""
    yrs_tr, yrs_va = set(s_tr.week.dt.year), set(s_va.week.dt.year)
    if not yrs_va or yrs_va != {Y} or (yrs_tr and max(yrs_tr) >= Y):
        raise ObligationError(f"F-8 fold {Y}→{Y + 1}: selection must train ≤ {Y - 1} and stop on {Y} "
                              f"(got train ≤ {max(yrs_tr) if yrs_tr else None}, stop on {sorted(yrs_va)})")
    if (yrs_tr | yrs_va) & {Y + 1}:
        raise ObligationError(f"F-8 fold {Y}→{Y + 1}: selected on its test year")


def eval_modes(ecfg: dict) -> tuple[str, str]:
    tf, rs = ecfg.get("threshold_from", "val"), ecfg.get("rolling_selection", "per_fold")
    if tf not in THRESHOLD_FROM:
        raise ValueError(f"eval.threshold_from {tf!r} — expected one of {THRESHOLD_FROM}")
    if rs not in ROLLING_SELECTION:
        raise ValueError(f"eval.rolling_selection {rs!r} — expected one of {ROLLING_SELECTION}")
    return tf, rs


def fixed_thresholds(p_val, rates, threshold_from: str):
    """The thresholds a steward could have set beforehand: quantiles of the selection model's validation scores (the
    model trained on train only, so these scores are out of sample). None in `test` mode (quantiled after the fact)."""
    return quantile_thresholds(p_val, rates) if threshold_from == "val" else None


def check_thresholds_fixed(thresholds_of, p_val, p_test, *, seed: int = 0) -> None:
    """F-8, checked by effect: a threshold fixed beforehand cannot move when the test scores do. `thresholds_of(p_val,
    p_test)` is the threshold rule under test; the test scores are replaced by a permutation-and-shift of themselves and
    every threshold must stay put. Raises ObligationError naming the budget that moved."""
    rng = np.random.default_rng(seed)
    a = thresholds_of(p_val, p_test)
    b = thresholds_of(p_val, np.clip(rng.permutation(p_test) * 0.5 + 0.25, 0, 1))
    moved = [k for k in a if not np.isclose(a[k], b[k], rtol=0, atol=1e-15)]
    if moved:
        raise ObligationError(f"F-8: threshold moved with test scores at {moved} — chosen on the years it scores")


def _variant(inst, spec, feats, train, val, test, panel, ecfg, unit_col):
    tf, _ = eval_modes(ecfg)
    L = learner(spec, feats, inst)
    vm, final, info = L.fit(train, val)
    rates, bins = tuple(ecfg["alert_rates"]), int(ecfg.get("calibration_bins", 10))
    p_val = L.predict(vm, val)
    fixed = fixed_thresholds(p_val, rates, tf)    # set BEFORE test is scored
    p_test = L.predict(final, test)
    r = {**info, "learner": L.describe(info), "threshold_from": tf,
         "val": evaluate(val["y"].values, p_val, "val", rates, bins, thresholds=fixed, threshold_from=tf),
         "test": evaluate(test["y"].values, p_test, "test", rates, bins, thresholds=fixed, threshold_from=tf)}
    budget = float(ecfg["lead_budget"])
    ev = inst.event
    scored = test.assign(p=p_test)
    pan = panel.merge(scored[[unit_col, "week", "p"]], on=[unit_col, "week"], how="left")
    lt = lead_time(
        pan, unit_col=unit_col, threshold=float(ev["threshold"]), direction=ev["direction"], horizon=int(ev["horizon"]),
        alert_threshold=r["test"]["alert_rates"][rate_key(budget)]["threshold"], test_start=inst.cfg["split"]["test_start"])
    r[f"lead_time_test_{rate_key(budget)}"] = {**lt, "threshold_from": tf}
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

    # rolling origin. per_fold (F-8): each fold selects on its own inner validation year with eras it could have known;
    # full_model: hab's reading — the full model's selection (stopped on val) held fixed for every fold.
    _, rsel = eval_modes(ecfg)
    L, info = art["full"]["learner"], {k: res["full"][k] for k in ("n_trees", "C") if k in res["full"]}
    panel_ro, refit_years = [], []
    base = {sid: inst.climatology(sid) for sid in (inst.cfg.get("climatology") or {})}

    def fold(Y):
        if fold_tables is not None:
            fdf, eras, rebuilt = fold_tables(Y); fdf = fdf.copy(); fdf["y"] = fdf["y"].astype(int)
        else:
            fdf, eras, rebuilt = df, base, False
        need = clipped_eras(inst, Y)
        if inst.obligations and not reference and need != base and not (rebuilt and dict(eras) == need):
            # verified, not presumed: the fold callable must have rebuilt with exactly the clipped eras (III F-3)
            raise ObligationError(f"R7 fold {Y}→{Y + 1}: needs eras {need}, got {eras} (rebuilt={rebuilt}) — obligation not executed")
        return fdf, eras, rebuilt

    for Y in s["rolling_origin_years"]:
        fdf, eras, rebuilt = fold(Y)
        tr, te = fdf[fdf.week.dt.year <= Y], fdf[fdf.week.dt.year == Y + 1]
        if te["y"].sum() < 5:
            continue
        sel = {}
        if rsel == "per_fold":
            sdf, s_eras, _ = fold(Y - 1)   # the selection reads only normals knowable through Y−1 (R7 on the inner split)
            s_tr, s_va = sdf[sdf.week.dt.year <= Y - 1], sdf[sdf.week.dt.year == Y]
            check_fold_selection(Y, s_tr, s_va)
            _, _, finfo = L.fit(s_tr, s_va)
            finfo = {k: finfo[k] for k in ("n_trees", "C") if k in finfo}
            sel = {"selected_on": Y, **finfo, "selection_eras": {k: list(v) for k, v in s_eras.items()}}
        else:
            finfo = info
            sel = {"selected_on": [s["val_start"], s["val_end"]], **info}
        pp = L.predict(L.refit_fixed(tr, finfo), te)
        row = {"train_through": Y, "test_year": Y + 1, "n": int(len(te)), "positives": int(te["y"].sum()),
               "prevalence": float(te["y"].mean()), "auroc": float(roc_auc_score(te["y"], pp)),
               "auprc": float(average_precision_score(te["y"], pp)),
               "climatology_eras": {k: list(v) for k, v in eras.items()}, "climatology_refit": bool(rebuilt),
               "selection": sel}
        panel_ro.append(row)
        if rebuilt:
            refit_years.append(Y + 1)
        log(f"  rolling {Y}→{Y+1}: AUROC {row['auroc']:.3f} AUPRC {row['auprc']:.3f} prev {row['prevalence']:.3f}"
            + ("  [climatology refit]" if rebuilt else "") + f"  [selected on {sel['selected_on']}: {finfo}]")
    res["rolling_selection"] = rsel
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

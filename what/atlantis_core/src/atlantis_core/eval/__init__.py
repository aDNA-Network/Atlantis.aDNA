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

**The label-horizon embargo (M-1f; III M-1e F-6, C-022).** A week's label reads t+1…t+H, so the last H weeks of a fit or
stop set are labelled by the period after it. `split.embargo_weeks` (absent → the event horizon H; `none` → off, v2's
reading) drops, from each set, the rows whose label window ends in or after the period that set must not see:
selection-train → its stop set, the stop set → test, the refit → test (main split and every rolling fold). The train
tail comes back for the refit, because its labels read only the stop set, which the refit trains on anyway. Each
boundary is then checked on the frames the learner actually received, with H read from the event and never from the
embargo setting (`check_label_windows`), and the result carries what was dropped and the measured spill (`embargo`).
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

__all__ = ["run", "split", "groups", "ObligationError", "check_fold_selection", "eval_modes", "embargo_weeks", "embargo",
           "check_label_windows", "horizon_spill"]

ROLLING_SELECTION = ("per_fold", "full_model")


class ObligationError(RuntimeError):
    pass


def split(df: pd.DataFrame, s: dict):
    y = df["week"].dt.year
    return (df[(y >= s["min_train_year"]) & (y <= s["train_end"])],
            df[(y >= s["val_start"]) & (y <= s["val_end"])],
            df[(y >= s["test_start"]) & (y <= s["test_end"])])


def embargo_weeks(s: dict, horizon: int) -> int:
    """`split.embargo_weeks`, resolved: absent → the event horizon; `none` (or 0) → 0, off; else a whole number of weeks
    ≥ the horizon. A partial embargo (0 < E < H) still lets labels read the next period, and is refused."""
    H = int(horizon)
    if "embargo_weeks" not in s:
        return H
    E = s["embargo_weeks"]
    if isinstance(E, bool) or not (E == "none" or isinstance(E, int)) or (isinstance(E, int) and E < 0):
        raise ValueError(f"split.embargo_weeks {E!r} — a whole number of weeks ≥ the horizon ({H}), or none")
    if E == "none" or E == 0:
        return 0
    if E < H:
        raise ValueError(f"split.embargo_weeks {E} < horizon {H} — a partial embargo still spills; use ≥ {H}, or none")
    return E


def _window_end(frame: pd.DataFrame, weeks: int) -> pd.Series:
    return frame["week"] + pd.Timedelta(weeks=weeks)


def embargo(frame: pd.DataFrame, next_start: int, weeks: int) -> pd.DataFrame:
    """`frame` without the rows whose label window (t+1…t+weeks) ends in or after year `next_start`."""
    if not weeks:
        return frame
    return frame[_window_end(frame, weeks).dt.year < next_start]


def check_label_windows(boundary: str, frame: pd.DataFrame, next_start: int, horizon: int) -> dict:
    """C-022, checked on a frame the learner actually received: every row's label window t+1…t+H ends before
    `next_start`. H is the EVENT's horizon — never the embargo setting, so the check cannot hold by construction."""
    end = _window_end(frame, int(horizon))
    bad = end.dt.year >= next_start
    if bad.any():
        raise ObligationError(f"embargo {boundary}: {int(bad.sum())} rows' label windows cross into {next_start} "
                              f"(latest ends {end.max().date()})")
    return _windows(frame, next_start, horizon)


def _windows(frame: pd.DataFrame, next_start: int, horizon: int) -> dict:
    end = _window_end(frame, int(horizon))
    return {"next_start": int(next_start), "n": int(len(frame)), "positives": int(frame["y"].sum()),
            "latest_window_end": None if frame.empty else str(end.max().date())}


def _boundaries(where: str, got: list, E: int, H: int) -> dict:
    """Each (name, frame received, next period, frame before the embargo): checked when the embargo is on (`none` is
    v2's reading, recorded as unchecked), with what the embargo dropped — counted from the frames, not from E."""
    out = {}
    for name, frame, nxt, before in got:
        b = check_label_windows(f"{where}{name}", frame, nxt, H) if E else _windows(frame, nxt, H)
        out[name] = {**b, "checked": bool(E), "rows_dropped": int(len(before) - len(frame)),
                     "positives_dropped": int(before["y"].sum() - frame["y"].sum())}
    return out


def horizon_spill(frame: pd.DataFrame, panel: pd.DataFrame, unit_col: str, next_start: int, ev: dict) -> dict:
    """The measured spill at one boundary (M-1f). `crossing_rows`: rows whose label window reads `next_start` or later
    (a negative's "no crossing" reads it too). `crossing_positives`: III M-1e F-6's count, the positives among them.
    `labelled_by_next`: positives that hold ONLY by signal in or after `next_start` — cut at the boundary, the window
    would not have crossed the threshold."""
    H, thr, above = int(ev["horizon"]), float(ev["threshold"]), ev["direction"] == "above"
    crossing_rows = int((_window_end(frame, H).dt.year >= next_start).sum())
    pos = frame[frame["y"].astype(int) == 1]
    cross = pos[_window_end(pos, H).dt.year >= next_start]
    sig = panel.set_index([unit_col, "week"])["signal"]
    inside = pd.Series(False, index=cross.index)
    for k in range(1, H + 1):
        wk = cross["week"] + pd.Timedelta(weeks=k)
        v = pd.Series(sig.reindex(pd.MultiIndex.from_arrays([cross[unit_col], wk])).to_numpy(), index=cross.index)
        hit = (v >= thr) if above else (v <= thr)
        inside |= hit & (wk.dt.year < next_start)
    return {"next_start": int(next_start), "rows": int(len(frame)), "crossing_rows": crossing_rows,
            "positives": int(len(pos)), "crossing_positives": int(len(cross)),
            "labelled_by_next": int((~inside).sum())}


def groups(inst) -> dict:
    out: dict = {}
    for v in inst.vitals:
        out.setdefault(v["group"], []).append(feature_name(v))
    return out


MIN_INNER_POSITIVES = 5   # as a test year: a stop set with fewer onsets than this selects on noise; the fold is skipped, and says so


class FitRecorder:
    """The rolling learner, recording the frames it is ACTUALLY fitted on (III M-1e F-1, C-023): the fold checks read what
    `fit` / `refit_fixed` received, never the intent of the code that called them."""

    def __init__(self, L):
        self._L, self.fits = L, []

    def fit(self, train, val):
        self.fits.append(("fit", train, val))
        return self._L.fit(train, val)

    def refit_fixed(self, train, info):
        self.fits.append(("refit", train, None))
        return self._L.refit_fixed(train, info)

    def __getattr__(self, k):
        return getattr(self._L, k)


def check_fold_selection(Y: int, s_tr: pd.DataFrame, s_va: pd.DataFrame) -> None:
    """F-8, checked per fold on the frames the learner actually received: a fold testing Y+1 selects on rows strictly
    before it, stopping on its inner year Y. Calendar years only — the label horizon spill across a boundary is a
    disclosed limit (III M-1e F-6), not checked here."""
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


def _embargo_of(inst) -> tuple[int, int]:
    H = int(inst.event["horizon"])
    return embargo_weeks(inst.cfg["split"], H), H


def _fit_main(L, train, val, s: dict, E: int, H: int, where: str = ""):
    """Select on train ⊣ the stop set (val), refit on train ∪ stop set ⊣ test; each set embargoed against the period it must
    not see, each boundary checked on what the learner received. The refit is composed here (the learner's own `final`
    is discarded): `refit_fixed` is the same construction, and with the embargo off it receives concat([train, val])."""
    R = FitRecorder(L)
    stop = embargo(val, s["test_start"], E)
    vm, _, info = R.fit(embargo(train, s["val_start"], E), stop)
    full = pd.concat([train, val])
    final = R.refit_fixed(pd.concat([train, stop]), info)
    (_, f_tr, f_va), = [f for f in R.fits if f[0] == "fit"]     # what was ACTUALLY fitted on (C-023)
    (_, r_tr, _), = [f for f in R.fits if f[0] == "refit"]
    b = _boundaries(where, [("train→val", f_tr, s["val_start"], train), ("val→test", f_va, s["test_start"], val),
                            ("refit→test", r_tr, s["test_start"], full)], E, H)
    return vm, final, info, f_va, b


def _variant(inst, spec, feats, train, val, test, panel, ecfg, unit_col):
    tf, _ = eval_modes(ecfg)
    E, H = _embargo_of(inst)
    L = learner(spec, feats, inst)
    vm, final, info, stop, emb = _fit_main(L, train, val, inst.cfg["split"], E, H)
    rates, bins = tuple(ecfg["alert_rates"]), int(ecfg.get("calibration_bins", 10))
    # thresholds are quantiles of scores, which read no label: fixed on every validation week (a budget is per year).
    # The val metrics read labels, so they are scored on the stop set — the embargoed rows that early stopping read.
    fixed = fixed_thresholds(L.predict(vm, val), rates, tf)    # set BEFORE test is scored
    p_stop = L.predict(vm, stop)
    p_test = L.predict(final, test)
    r = {**info, "learner": L.describe(info), "threshold_from": tf, "embargo": emb,
         "val": evaluate(stop["y"].values, p_stop, "val", rates, bins, thresholds=fixed, threshold_from=tf),
         "test": evaluate(test["y"].values, p_test, "test", rates, bins, thresholds=fixed, threshold_from=tf)}
    if fixed is not None:   # III M-1e: the RESULT must carry the thresholds fixed above — read back, not presumed (C-023)
        applied = {k: v["threshold"] for k, v in r["test"]["alert_rates"].items()}
        if applied != fixed:
            raise ObligationError(f"F-8: applied thresholds {applied} are not the ones fixed on validation {fixed}")
    budget = float(ecfg["lead_budget"])
    ev = inst.event
    scored = test.assign(p=p_test)
    pan = panel.merge(scored[[unit_col, "week", "p"]], on=[unit_col, "week"], how="left")
    lt = lead_time(
        pan, unit_col=unit_col, threshold=float(ev["threshold"]), direction=ev["direction"], horizon=int(ev["horizon"]),
        alert_threshold=r["test"]["alert_rates"][rate_key(budget)]["threshold"], test_start=inst.cfg["split"]["test_start"])
    lead_thr = r["test"]["alert_rates"][rate_key(budget)]["threshold"]
    if tf == "val" and (lead_thr != fixed[rate_key(budget)] or lt.get("alert_threshold") != lead_thr):
        raise ObligationError(f"F-8: lead time read threshold {lt.get('alert_threshold')} — not the {rate_key(budget)} budget's "
                              f"threshold fixed on validation ({fixed[rate_key(budget)]})")
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
    E, H = _embargo_of(inst)
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
    # the baseline is fitted on the refit's rows: the embargo is the model's, so the comparison stays like for like
    res["climatology_baseline_test"] = climatology_baseline(pd.concat([train, embargo(val, s["test_start"], E)]), test)
    ev = inst.event
    res["embargo"] = {"weeks": E, "horizon": H, "checked": bool(E), "boundaries": res["full"]["embargo"],
                      "spill": {"train→val": horizon_spill(train, panel, unit_col, s["val_start"], ev),
                                "val→test": horizon_spill(val, panel, unit_col, s["test_start"], ev)}}

    # rolling origin. per_fold (F-8): each fold selects on its own inner validation year with eras it could have known;
    # full_model: hab's reading — the full model's selection (stopped on val) held fixed for every fold.
    _, rsel = eval_modes(ecfg)
    L, info = FitRecorder(art["full"]["learner"]), {k: res["full"][k] for k in ("n_trees", "C") if k in res["full"]}
    panel_ro, refit_years, skipped = [], [], []
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
        L.fits.clear()
        if rsel == "per_fold":
            sdf, s_eras, _ = fold(Y - 1)   # the selection reads only normals knowable through Y−1 (R7 on the inner split)
            if inst.obligations and not reference and dict(s_eras) != clipped_eras(inst, Y - 1):
                raise ObligationError(f"F-8 fold {Y}→{Y + 1}: selection read eras {s_eras}, not those knowable through {Y - 1} "
                                      f"({clipped_eras(inst, Y - 1)})")
            s_tr0, s_va0 = sdf[sdf.week.dt.year <= Y - 1], sdf[sdf.week.dt.year == Y]
            s_tr, s_va = embargo(s_tr0, Y, E), embargo(s_va0, Y + 1, E)
            if s_va["y"].sum() < MIN_INNER_POSITIVES:
                skipped.append({"test_year": Y + 1, "reason": f"inner stop year {Y} has {int(s_va['y'].sum())} positives "
                                                              f"(< {MIN_INNER_POSITIVES})"})
                continue
            _, _, finfo = L.fit(s_tr, s_va)
            (_, f_tr, f_va), = [f for f in L.fits if f[0] == "fit"]   # what was ACTUALLY fitted on (C-023)
            check_fold_selection(Y, f_tr, f_va)
            emb = _boundaries(f"fold {Y}→{Y + 1} ", [("train→stop", f_tr, Y, s_tr0), ("stop→test", f_va, Y + 1, s_va0)], E, H)
            finfo = {k: finfo[k] for k in ("n_trees", "C") if k in finfo}
            sel = {"selected_on": sorted(int(y) for y in set(f_va.week.dt.year)), **finfo, "embargo": emb,
                   "selection_eras": {k: list(v) for k, v in s_eras.items()}}
        else:
            finfo = info
            sel = {"selected_on": [s["val_start"], s["val_end"]], **info}
        pp = L.predict(L.refit_fixed(embargo(tr, Y + 1, E), finfo), te)
        (_, r_tr, _), = [f for f in L.fits if f[0] == "refit"]
        if max(r_tr.week.dt.year) > Y or (Y + 1) in set(r_tr.week.dt.year):
            raise ObligationError(f"F-8 fold {Y}→{Y + 1}: refit on rows through {max(r_tr.week.dt.year)}")
        r_emb = _boundaries(f"fold {Y}→{Y + 1} ", [("refit→test", r_tr, Y + 1, tr)], E, H)
        row = {"train_through": Y, "test_year": Y + 1, "n": int(len(te)), "positives": int(te["y"].sum()),
               "prevalence": float(te["y"].mean()), "auroc": float(roc_auc_score(te["y"], pp)),
               "auprc": float(average_precision_score(te["y"], pp)),
               "climatology_eras": {k: list(v) for k, v in eras.items()}, "climatology_refit": bool(rebuilt),
               "selection": sel, "embargo": {**r_emb,
                                             "spill": horizon_spill(fdf[fdf.week.dt.year == Y], panel, unit_col, Y + 1, ev)}}
        panel_ro.append(row)
        if rebuilt:
            refit_years.append(Y + 1)
        log(f"  rolling {Y}→{Y+1}: AUROC {row['auroc']:.3f} AUPRC {row['auprc']:.3f} prev {row['prevalence']:.3f}"
            + ("  [climatology refit]" if rebuilt else "") + f"  [selected on {sel['selected_on']}: {finfo}]")
    res["rolling_selection"] = rsel
    res["rolling_skipped"] = skipped
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
        _, f2, i2, _, _ = _fit_main(L2, tr2, va2, s, E, H, where="sensitivity ")
        p2 = L2.predict(f2, te2)
        res["sensitivity"] = {"threshold": thr, "test_auroc": float(roc_auc_score(te2["y"], p2)),
                              "test_auprc": float(average_precision_score(te2["y"], p2)),
                              "test_prevalence": float(te2["y"].mean()), "n_test": int(len(te2)),
                              "positives_test": int(te2["y"].sum()), **i2}
    return res, art

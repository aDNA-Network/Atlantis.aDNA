"""Site data: everything the explainer page renders, assembled from the instance's core outputs, registries and
`site.yaml` — never from `hab`. Per-patient rows (strips, cases, beeswarm, trace, map) are embedded in the page; the
page is an INSTANCE artifact under the instance's own data ruling (the public-data exemplar commits it, as v0's), and
nothing assembled here goes to the board (SO-3). Ported from hab.export_site_data (M-1b-ii-b)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from atlantis_core.config import Instance, feature_name, load_yaml
from atlantis_core.grid import make_grid

OUT_DIR = "outputs/atlantis_core"   # default; site.yaml `outputs:` names another run (M-1e: v2's page reads outputs/atlantis_core_v2)


def run_dirs(root: Path, site: dict) -> tuple[Path, Path]:
    """The run a page reads: `<outputs>` and its processed tables `data/processed/<basename>` (as atlantis_core.run writes)."""
    o = site.get("outputs", OUT_DIR)
    return root / o, root / "data" / "processed" / Path(o).name


class SiteError(ValueError):
    pass


def R(a, d=3):
    a = np.round(np.asarray(a, dtype=float), d)
    return [None if not np.isfinite(v) else float(v) for v in a.tolist()]


def clean(o):
    """Recursively make the payload strict JSON: NaN/inf → None, numpy scalars → Python."""
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (float, np.floating)): return None if not np.isfinite(o) else float(o)
    return o


def load_site(inst: Instance, name: str = "site.yaml") -> dict:
    p = inst.root / name
    if not p.exists():
        raise SiteError(f"{inst.root.name}: no site.yaml — the site is optional; declare it to build one")
    return load_yaml(p)


def _ge(values: pd.Series, thr: float, direction: str) -> pd.Series:
    return values.ge(thr) if direction == "above" else values.le(thr)


def unit_names(inst: Instance) -> dict:
    """Display names per unit: a rule grid's `name`s; a polygon grid's `name_property` (M-2b — the FKNMS page labelled its
    zones 1…21 because only rules were read). Ids are cast to the grid's unit dtype, as the patient grid's are."""
    g = inst.cfg["grid"]
    if g.get("kind") == "polygons" and g.get("name_property"):
        from atlantis_core.grid import make_grid
        cast = int if g.get("unit_dtype") == "int" else (lambda v: v)
        return {cast(u): n for u, n in make_grid(inst).names().items()}
    return {r["id"]: r["name"] for r in g.get("rules", []) or []}


BOARD_META = {"recorded_at", "recorded_by", "learner", "limitations_ref", "split", "shap_summary_ref", "evaluation_id",
              "event_ref", "unit_ref", "claim", "owner_ruling_ref", "name", "description", "tier", "version"}


def board_check(metrics: dict, entry: dict, inst) -> dict:
    """The page must say what its board entry says. The run's metrics are re-projected through the board's own projector
    and EVERY evaluated field (metrics, budgets, lead time, ablations, hash, data pins) must equal the entry's; only
    record metadata may differ (III F-3c — a five-field check passed a doctored Brier)."""
    from atlantis_core.board import project
    ev = entry["evaluation"]
    mine = project(metrics, inst, version=0, recorded_at=ev.get("recorded_at") or "1970-01-01T00:00:00Z", config_hash=metrics["semantic_hash"])
    keys = (set(ev) | set(mine)) - BOARD_META
    bad = {k: (mine.get(k), ev.get(k)) for k in sorted(keys) if mine.get(k) != ev.get(k)}
    if bad:
        raise SiteError(f"outputs disagree with board entry {entry['entry_id']}: {bad} — rerun atlantis_core.run, or point site.yaml at the right entry")
    return {"entry_id": entry["entry_id"], "auroc": ev["auroc"], "auprc": ev["auprc"], "base_rate": ev["base_rate"],
            "n_test": ev["n_test"], "config_hash": ev["config_hash"], "run_date": entry.get("run_date"),
            "fields_checked": len(keys), "delta_vs": (entry.get("evaluation_extras") or {}).get("delta_vs")}


def shap_check(z, ss: dict, test: pd.DataFrame, allr: pd.DataFrame) -> None:
    """The gitignored per-patient arrays must belong to the run whose summary is committed (III F-3c): row counts match the
    scored tables, the base matches, and each column's mean |SHAP| on the test rows reproduces shap_summary.json."""
    sv, sv_all = z["shap"], z["shap_all"]
    errs = []
    if sv.shape[0] != len(test): errs.append(f"shap rows {sv.shape[0]} != test_scored rows {len(test)}")
    if sv_all.shape[0] != len(allr): errs.append(f"shap_all rows {sv_all.shape[0]} != all_scored rows {len(allr)}")
    if abs(float(z["base"]) - float(ss["base_logit"])) > 1e-6: errs.append(f"base {float(z['base'])} != summary {ss['base_logit']}")
    cols = [str(c) for c in z["columns"]]
    ma = np.abs(sv).mean(0)
    off = [c for k, c in enumerate(cols) if c in ss["mean_abs_shap"] and abs(ma[k] - ss["mean_abs_shap"][c]) > 1e-4]
    if off: errs.append(f"mean |SHAP| disagrees with shap_summary.json for {off[:4]}")
    if errs:
        raise SiteError("data/processed/atlantis_core is not the run outputs/atlantis_core records: " + "; ".join(errs) +
                        " — rerun atlantis_core.run")


def _lead_key(full: dict) -> str:
    ks = [k for k in full if k.startswith("lead_time_test")]
    if len(ks) != 1:
        raise SiteError(f"expected one lead_time_test_* block in metrics.full, found {ks}")
    return ks[0]


def _metrics(inst, m: dict) -> dict:
    full = dict(m["full"]); lk = _lead_key(full)
    from atlantis_core.eval.metrics import rate_key
    budget = float(inst.cfg["eval"]["lead_budget"])
    full["lead"] = {**full.pop(lk), "budget": budget, "budget_key": rate_key(budget)}
    full.pop("gain_importance", None)
    abl = [{"group": a["drop_group"], **{k: m[f"no_{a['drop_group']}"][k] for k in ("n_trees", "test")}}
           for a in inst.cfg["eval"].get("ablations", []) or []]
    keep = ("splits", "climatology_baseline_test", "persistence_baseline_test", "trend_baseline_test",
            "surveillance_only_test_auroc", "surveillance_only_vital",
            "rolling_origin", "obligations", "mode", "sensitivity", "semantic_hash", "features_report", "atlantis_core")
    out = {k: m[k] for k in keep if k in m}
    if "calibration_in_the_large" in full.get("test", {}):   # ruling 16: val beside test, so the shift is on the page
        v = full.get("val") or {}   # III M-2b F-7: val's CITL is on the embargoed stop set — its own n and prevalence travel with it
        out["calibration_in_the_large"] = {"val": v.get("calibration_in_the_large"), "test": full["test"]["calibration_in_the_large"],
                                           "val_n": v.get("n"), "val_prevalence": v.get("prevalence")}
    for blk in ("val",):
        full.pop(blk, None)
    out.update(full=full, ablations=abl)
    return out


def _swaps(out_dir: Path, inst) -> list:
    out = []
    for spec in inst.cfg.get("learner_swaps", []) or []:
        p = out_dir / f"learner_swap_{spec['kind']}.json"
        if not p.exists():
            raise SiteError(f"{p.name} missing — rerun atlantis_core.run without --no-swaps")
        s = json.loads(p.read_text()); ss = s["shap_summary"]; t = s["full"]["test"]
        avail = {c: v for c, v in ss["mean_abs_shap"].items() if c.startswith("availability:")}
        out.append({"kind": s["learner_kind"], "learner": s["full"]["learner"], "semantic_hash": s["semantic_hash"],
                    "test": {k: t[k] for k in ("auroc", "auprc", "brier", "calibration_slope", "prevalence", "alert_rates")},
                    "group_mean_abs": ss["group_mean_abs_shap"], "group_net_mean_abs": ss["group_net_mean_abs_shap"],
                    "availability_top": dict(sorted(avail.items(), key=lambda kv: -kv[1])[:6]),
                    "n_availability": len(avail)})
    return out


def _event_raw(inst, frames):
    """The event stream's observations, with unit, and lat/lon when it is point-shaped (for the sample map)."""
    sid = inst.event["event_variable_stream"]; spec = inst.stream_spec(sid)
    df = frames[sid].copy()
    latlon = None
    if spec["shape"] == "point":
        raw = pd.read_parquet(inst.root / spec["artifact"])
        cols = spec["columns"]
        raw = raw.dropna(subset=[cols["date"], cols["value"], cols["lat"], cols["lon"]])
        u = make_grid(inst).assign(raw[cols["lat"]].values, raw[cols["lon"]].values)
        latlon = pd.DataFrame({"lat": raw[cols["lat"]].values, "lon": raw[cols["lon"]].values, "unit": u}).dropna()
    return df, latlon


def eda(inst, site, frames, names) -> dict:
    """Descriptive pass over the event stream's raw observations (was hab.eda)."""
    df, latlon = _event_raw(inst, frames)
    thr, direction = float(inst.event["threshold"]), inst.event["direction"]
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["ge"] = _ge(df["value"], thr, direction)
    per_year = df.groupby("year").agg(n=("value", "size"), ge=("ge", "sum"))
    py0 = int(site.get("per_year_from", per_year.index.min()))
    per_unit = df.groupby("unit").agg(n=("value", "size"), ge_share=("ge", "mean"))
    sp = inst.cfg["split"]; years = list(range(int(sp["min_train_year"]), int(sp["test_end"]) + 1))
    order = sorted(names) if names else sorted(per_unit.index)
    cov = df.groupby(["year", "unit"]).size().unstack(fill_value=0).reindex(index=years, columns=order, fill_value=0)
    out = {"n_obs": int(len(df)),
           "per_year": {int(y): {"n": int(r["n"]), "ge": int(r["ge"])} for y, r in per_year.iterrows() if y >= py0},
           "per_unit": {int(u): {"n": int(r["n"]), "ge_share": float(r["ge_share"])} for u, r in per_unit.iterrows()},
           "coverage": {"years": years, "units": [int(u) for u in order], "counts": cov.values.astype(int).tolist()},
           "map": None}
    mcfg = site.get("map") or {}
    if latlon is not None and mcfg:
        g = float(mcfg.get("round_deg", 0.05))
        loc = latlon.assign(la=(latlon.lat / g).round() * g, lo=(latlon.lon / g).round() * g) \
                    .groupby(["la", "lo", "unit"]).size().reset_index(name="n")
        loc = loc[loc.n >= int(mcfg.get("min_n", 1))]
        out["map"] = {"lat": R(loc.la, 2), "lon": R(loc.lo, 2), "unit": loc.unit.astype(int).tolist(),
                      "n": loc.n.astype(int).tolist(), "round_deg": g, "bounds": mcfg.get("bounds"),
                      "accent_units": mcfg.get("accent_units", [])}
    return out


def _window(df, ucol, unit, d0, d1):
    w = pd.to_datetime(df["week"])
    return df[(df[ucol] == unit) & (w >= pd.Timestamp(d0)) & (w <= pd.Timestamp(d1))].sort_values("week")


def _wk(s):
    return pd.to_datetime(s).dt.strftime("%Y-%m-%d").tolist()


def trace(inst, site, table, panel, names) -> dict | None:
    t = site.get("trace")
    if not t:
        return None
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    g = _window(table, ucol, t["unit"], *t["window"]).merge(panel.rename(columns={"unit": ucol}), on=[ucol, "week"], how="left")
    out = {"unit": t["unit"], "unit_name": names.get(t["unit"], str(t["unit"])), "weeks": _wk(g.week), "panels": []}
    for p in t["panels"]:
        col = "signal" if p == "signal" else p
        if col not in g:
            raise SiteError(f"site.yaml trace panel {p!r}: not 'signal' and not a vital")
        out["panels"].append({"key": p, "values": [None if pd.isna(v) else float(v) for v in g[col]]})
    return out


def strips(inst, site, table, panel, all_scored, shap_all, groups, names) -> dict:
    """Risk decomposed over time: the unit's full weekly grid in the window; weeks outside the modelling rows keep
    their observed signal and carry no score (grey bands). Group sums are per-row NET sums of SHAP."""
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    a = all_scored.reset_index(drop=True).assign(_i=np.arange(len(all_scored)))
    out = {}
    for s in site.get("strips", []) or []:
        g = _window(table[[ucol, "week"]], ucol, s["unit"], *s["window"])
        g = g.merge(panel.rename(columns={"unit": ucol}), on=[ucol, "week"], how="left") \
             .merge(a[[ucol, "week", "p", "y", "split", "_i"]], on=[ucol, "week"], how="left")
        idx = g["_i"]
        S = {gid: [None if pd.isna(i) else float(shap_all[int(i), ix].sum()) for i in idx] for gid, ix in groups.items()}
        out[s["key"]] = {"unit": s["unit"], "unit_name": names.get(s["unit"], str(s["unit"])), "weeks": _wk(g.week),
                         "p": R(g.p, 4), "y": [None if pd.isna(v) else int(v) for v in g.y],
                         "split": [None if pd.isna(v) else str(v) for v in g.split],
                         "signal": [None if pd.isna(v) else float(v) for v in g.signal],
                         "groups": {k: R(v) for k, v in S.items()},
                         "bands": bands(g.week, g.split)}
    return out


def bands(weeks, split) -> list:
    """Weeks outside the modelling rows (already in event, unknown outcome) as half-open intervals one week wide, centred on
    the ISO week's Monday ± 3.5 days (III F-1: a zero-width rect on a date axis draws nothing)."""
    out = []
    for w, sp in zip(pd.to_datetime(weeks), split):
        if pd.isna(sp):
            out.append([(w - pd.Timedelta(hours=84)).isoformat(), (w + pd.Timedelta(hours=84)).isoformat()])
    return out


def cases(inst, site, test, sv, panel, feats, names) -> list:
    """Three out-of-sample patients by rule (was hab.export_site_data): the most confident true positive whose onset came
    ≥ `lead_min` weeks out (among the top `p_quantile` of scores, if any are), the most confident false alarm, and the
    quietest week of a configured month. NOT "the longest lead" — the v0 page said so and the rule never did (III F-2)."""
    c = site.get("cases") or {}
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    thr, H, direction = float(inst.event["threshold"]), int(inst.event["horizon"]), inst.event["direction"]
    test = test.reset_index(drop=True).assign(idx=np.arange(len(test)))
    pan = panel.rename(columns={"unit": ucol}).set_index([ucol, "week"])["signal"]
    test["signal_t0"] = [pan.get((u, w), np.nan) for u, w in zip(test[ucol], test["week"])]

    def lead_of(row):
        for k in range(1, H + 1):
            v = pan.get((row[ucol], row["week"] + pd.Timedelta(weeks=k)), np.nan)
            if pd.notna(v) and (v >= thr if direction == "above" else v <= thr):
                return k
        return 0
    tp = test[test.y == 1].copy(); tp["lead"] = tp.apply(lead_of, axis=1)
    lead_min, q = int(c.get("lead_min", 2)), float(c.get("p_quantile", 0.9))
    cand = tp[(tp.lead >= lead_min) & (tp.p >= test.p.quantile(q))]
    if cand.empty: cand = tp[tp.lead >= lead_min]
    if cand.empty: cand = tp
    picks = [("true_positive", cand.sort_values("p", ascending=False).iloc[0]),
             ("false_positive", test[test.y == 0].sort_values("p", ascending=False).iloc[0]),
             ("quiet", test[(pd.to_datetime(test.week).dt.month == int(c.get("quiet_month", 7))) & (test.y == 0)].sort_values("p").iloc[0])]
    X = test[feats].values
    out = []
    for tag, row in picks:
        i = int(row.idx)
        out.append({"tag": tag, "unit": int(row[ucol]), "unit_name": names.get(int(row[ucol]), str(row[ucol])),
                    "week": pd.Timestamp(row.week).strftime("%Y-%m-%d"), "p": float(row.p), "y": int(row.y),
                    "lead_weeks": int(row.lead) if tag == "true_positive" else None,
                    "signal_this_week": None if pd.isna(row.signal_t0) else float(row.signal_t0),
                    "future_signal": None if pd.isna(row.future_signal) else float(row.future_signal),
                    "shap": {f: float(sv[i, k]) for k, f in enumerate(feats)},
                    "x": {f: (None if pd.isna(X[i, k]) else float(X[i, k])) for k, f in enumerate(feats)}})
    return out


def whatif(inst, wi: dict, names, labels: dict) -> dict:
    sp = inst.cfg["split"]
    group_of = {}
    for v in inst.vitals:
        group_of.setdefault(v["stream_ref"], v["group"])
    out = {}
    for k, w in wi.items():
        if not isinstance(w, dict):
            continue
        yrs = [int(x[:4]) for x in w["weeks"]]
        split = ["test" if y >= int(sp["test_start"]) else "val" if y >= int(sp["val_start"]) else "train" for y in yrs]
        out[k] = {**{f: w[f] for f in ("weeks", "p_actual", "p_scenario", "y", "mean_delta", "mean_abs_delta", "max_abs_delta",
                                        "factor", "stream", "stations_scaled", "non_lever_stations_scaled")},
                  "units": w["units"], "unit_name": ", ".join(names.get(u, str(u)) for u in w["units"]), "split": split,
                  "group": group_of.get(w["stream"]),
                  "stations_scaled_labels": [labels.get(s, s) for s in w["stations_scaled"]],
                  "non_lever_labels": [labels.get(s, s) for s in w["non_lever_stations_scaled"]],
                  "only_non_lever": bool(w["stations_scaled"]) and set(w["stations_scaled"]) <= set(w["non_lever_stations_scaled"])}
    return out


def assemble(inst: Instance, site: dict | None = None) -> dict:
    from atlantis_core.run import signal_panel
    from atlantis_core.vitals.build import build, load_frames, patient_grid
    site = site or load_site(inst)
    root = inst.root; out_dir, proc = run_dirs(root, site)
    need = [out_dir / "metrics.json", out_dir / "shap_summary.json", out_dir / "whatif.json",
            proc / "all_scored.parquet", proc / "test_scored.parquet", proc / "shap.npz"]
    missing = [str(p.relative_to(root)) for p in need if not p.exists()]
    if missing:
        raise SiteError(f"missing {missing} — run `python -m atlantis_core.run --instance {root}` first")
    m = json.loads((out_dir / "metrics.json").read_text())
    ss = json.loads((out_dir / "shap_summary.json").read_text())
    wi = json.loads((out_dir / "whatif.json").read_text())
    entry = json.loads((root / site["board_entry"]).read_text())
    board = board_check(m, entry, inst)

    names = unit_names(inst)
    feats = [feature_name(v) for v in inst.vitals]
    z = np.load(proc / "shap.npz"); cols = [str(c) for c in z["columns"]]
    if cols != feats:
        raise SiteError(f"shap.npz columns are not the registry's vitals in order — the headline learner must be the "
                        f"tree learner (got {cols[:3]}…)")
    sv, base, sv_all = z["shap"], float(z["base"]), z["shap_all"]
    test = pd.read_parquet(proc / "test_scored.parquet").reset_index(drop=True)
    allr = pd.read_parquet(proc / "all_scored.parquet")
    shap_check(z, ss, test, allr)
    gorder = list(site["groups"])
    reg_groups = {v["group"] for v in inst.vitals}
    if set(gorder) != reg_groups:
        raise SiteError(f"site.yaml groups {sorted(gorder)} != features.yaml groups {sorted(reg_groups)}")
    gidx = {g: [feats.index(feature_name(v)) for v in inst.vitals if v["group"] == g] for g in gorder}

    frames = load_frames(inst)
    units, weeks = patient_grid(inst, frames)
    table, _ = build(inst, frames, with_label=False)
    panel = signal_panel(inst, frames, units, weeks)

    rng = np.random.default_rng(int(site.get("seed", 42)))
    n = len(test); keep = np.sort(rng.choice(n, size=min(int(site.get("beeswarm_rows", 3000)), n), replace=False))
    X = test[feats].values
    dep = {}
    for f in ss["top6"]:
        k = feats.index(f); pk = feats.index(ss["dependence_partners"][f])
        dep[f] = {"x": R(X[keep, k]), "shap": R(sv[keep, k]), "partner": ss["dependence_partners"][f], "partner_x": R(X[keep, pk])}

    stations = {}
    for sid, spec in inst.cfg["streams"].items():
        lever = set(spec.get("lever_stations", []) or [])
        for st, us in (spec.get("stations") or {}).items():
            for u in us:
                stations.setdefault(int(u), []).append({"id": st, "label": (site.get("station_labels") or {}).get(st, st), "lever": st in lever})

    ev = inst.event
    site_data = {
        "generated": pd.Timestamp.now("UTC").strftime("%Y-%m-%d"),
        "instance": inst.root.name, "board": board,
        "event": {k: ev.get(k) for k in ("event_id", "name", "threshold", "unit", "direction", "horizon")},
        "signal_display": site.get("signal_display", {}),
        "units": [{"id": int(u), "name": names.get(u, str(u))} for u in (sorted(names) or units)],
        "stations": stations,
        "groups": [{"id": g, "label": site["groups"][g]["label"]} for g in gorder],
        "vital_display": site.get("vital_display", []),
        "features": [{"name": feature_name(v), "label": v["name"], "desc": v["description"], "group": v["group"], "tag": v["tag"]}
                     for v in inst.vitals],
        "split": {k: inst.cfg["split"][k] for k in ("min_train_year", "train_end", "val_start", "val_end", "test_start", "test_end")},
        "climatology": inst.cfg.get("climatology", {}),
        "data": {**eda(inst, site, frames, names), "trace": trace(inst, site, table, panel, names)},
        "metrics": _metrics(inst, m),
        "shap": {"learner_kind": ss["learner_kind"], "base_logit": base, "base_p": ss["base_p"],
                 "additivity_max_gap": ss["additivity_max_gap"], "perturbation": ss["perturbation"],
                 "background_n": ss["background_n"], "n_test_rows": ss["n_test_rows"], "mean_abs": ss["mean_abs_shap"],
                 "group_mean_abs": ss["group_mean_abs_shap"], "group_net_mean_abs": ss["group_net_mean_abs_shap"],
                 "tag_mean_abs": ss["tag_mean_abs_shap"], "top6": ss["top6"], "top_interaction": ss["top_interaction_pair"],
                 "caveat": ss["caveat"],
                 "beeswarm": {"features": feats, "shap": [R(sv[keep, k]) for k in range(len(feats))],
                              "x": [R(X[keep, k]) for k in range(len(feats))], "y": test.y.values[keep].astype(int).tolist()},
                 "dependence": dep, "cases": cases(inst, site, test, sv, panel, feats, names),
                 "strips": strips(inst, site, table, panel, allr, sv_all, gidx, names)},
        "swaps": _swaps(out_dir, inst),
        "whatif": whatif(inst, wi, names, site.get("station_labels") or {}), "whatif_caveat": wi.get("caveat"),
    }
    site_data["shap"]["beeswarm_n"] = len(keep)
    return clean(site_data)


TOKEN = re.compile(r"\{\{([^}|]+)(?:\|([^}]+))?\}\}")


def resolve(data: dict, path: str):
    cur = data
    for k in path.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and k.isdigit() and int(k) < len(cur):
            cur = cur[int(k)]
        else:
            raise KeyError(path)
    return cur

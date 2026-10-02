"""Assemble outputs/site_data.json — everything the explainer page renders, downsampled to fit."""
import json
import numpy as np, pandas as pd
from hab import load_config, DATA_RAW, DATA_PROC, OUT
from hab.build_features import FEATURES, FEATURE_GROUPS
from hab.regions import assign_regions, region_names

def R(a, d=3):
    a = np.round(np.asarray(a, dtype=float), d)
    return [None if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else float(v) for v in a.tolist()]


def clean(o):
    """Recursively replace NaN/inf floats with None so the JSON is strict."""
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    if isinstance(o, float) and (np.isnan(o) or np.isinf(o)): return None
    if isinstance(o, (np.floating,)): return None if np.isnan(o) else float(o)
    if isinstance(o, (np.integer,)): return int(o)
    return o
def discharge_tag(cfg):
    """Tag for the discharge features: `lever` if any configured gauge carries `lever: true` (a managed release a
    steward can actually change — S-79 here), else `proxy`. Read from config.yaml → gauges.*.lever; before M-1a that
    flag was declared in config but never read."""
    return "lever" if any(g.get("lever") for g in cfg["gauges"].values()) else "proxy"


def lever_gauges(cfg):
    return [f"{site} ({g['name']})" for site, g in cfg["gauges"].items() if g.get("lever")]


FEATURE_DOC = {  # short label · what it is · tag (lever / proxy / artifact / state); discharge tags set from config below
    "log_max_t0": ["max count, this week", "log10(1+cells/L) of the highest sample in the region this week", "state"],
    "log_max_t1": ["max count, 1 wk ago", "same, one week earlier", "state"],
    "log_max_t2": ["max count, 2 wk ago", "same, two weeks earlier", "state"],
    "log_max_t3": ["max count, 3 wk ago", "same, three weeks earlier", "state"],
    "log_med_t0": ["median count, this week", "median sample this week — is the region broadly seeded or one hot spot?", "state"],
    "log_p90_t0": ["90th-pct count, this week", "upper tail of this week's samples", "state"],
    "roll_max_4w": ["4-week peak", "highest weekly max over the last 4 weeks", "state"],
    "roll_max_8w": ["8-week peak", "highest weekly max over the last 8 weeks", "state"],
    "growth_1w": ["1-week growth", "change in log max vs last week (the 'trend in the vitals')", "state"],
    "growth_2w": ["2-week growth", "change in log max vs two weeks ago", "state"],
    "weeks_since_bloom": ["weeks since last bloom", "weeks since the region last exceeded 100k cells/L (cap 104)", "state"],
    "weeks_since_detect": ["weeks since last detection", "weeks since the region last exceeded 1,000 cells/L (cap 104)", "state"],
    "weeks_since_sample": ["weeks since last sample", "how stale the vitals are", "artifact"],
    "n_samples_t0": ["samples this week", "surveillance intensity — how hard we looked", "artifact"],
    "n_samples_4w": ["samples, last 4 wk", "surveillance intensity over a month", "artifact"],
    "woy_sin": ["season (sin)", "week-of-year, sine component", "proxy"],
    "woy_cos": ["season (cos)", "week-of-year, cosine component", "proxy"],
    "sst_t0": ["sea-surface temp", "OISST weekly mean over the region's nearshore box, °C", "proxy"],
    "sst_anom_t0": ["SST anomaly", "this week's SST minus the 1982–2011 week-of-year normal", "proxy"],
    "sst_anom_t2": ["SST anomaly, 2 wk ago", "same, two weeks earlier", "proxy"],
    "sst_anom_t4": ["SST anomaly, 4 wk ago", "same, four weeks earlier", "proxy"],
    "sst_delta_4w": ["4-week SST change", "warming or cooling over the last month, °C", "proxy"],
    "discharge_30d_t0": ["river discharge, 30 d", "log10 mean daily discharge of the region's river gauge(s), last 30 days", "discharge"],  # tag set from config
    "discharge_30d_t3": ["river discharge, 30 d (3 wk ago)", "same window ending three weeks earlier", "discharge"],  # tag set from config
    "discharge_anom_t0": ["discharge anomaly", "30-day discharge minus the 1990–2016 day-of-year normal", "discharge"],  # tag set from config
}
_DISCHARGE_TAG = discharge_tag(load_config())
for _k in ("discharge_30d_t0", "discharge_30d_t3", "discharge_anom_t0"):
    FEATURE_DOC[_k][2] = _DISCHARGE_TAG


def main():
    cfg = load_config(); names = region_names()
    metrics = json.load(open(OUT / "metrics.json")); shap_s = json.load(open(OUT / "shap_summary.json"))
    eda = json.load(open(OUT / "eda.json")); freport = json.load(open(DATA_PROC / "features_report.json"))
    whatif = json.load(open(OUT / "whatif.json"))
    test = pd.read_parquet(DATA_PROC / "test_scored.parquet").reset_index(drop=True)
    allr = pd.read_parquet(DATA_PROC / "all_scored.parquet")
    z = np.load(OUT / "shap_test.npz"); sv, base, sv_all = z["shap"], float(z["base"]), z["shap_all"]
    group_of = {f: g for g, fs in FEATURE_GROUPS.items() for f in fs}
    gidx = {g: [FEATURES.index(f) for f in fs] for g, fs in FEATURE_GROUPS.items()}
    rng = np.random.default_rng(42)

    # --- sample map: unique locations rounded to 0.05°, with region + n
    s = pd.read_parquet(DATA_RAW / "fwc_hab_karenia_1970_2023.parquet"); s["region"] = assign_regions(s)
    loc = s.assign(la=(s.lat * 20).round() / 20, lo=(s.lon * 20).round() / 20).groupby(["la", "lo", "region"]).size().reset_index(name="n")
    loc = loc[loc.n >= 3]

    # --- beeswarm / dependence rows (test split, downsampled)
    n = len(test); keep = np.sort(rng.choice(n, size=min(cfg["shap"]["site_rows_max"], n), replace=False))
    X = test[FEATURES].values

    # --- case studies (test split only → genuinely out-of-sample)
    test["idx"] = np.arange(n)
    thr = np.log10(1 + cfg["target"]["bloom_threshold_cells_per_l"])
    # (i) true positive with the longest lead: y=1, high p, and the first bloom week is >= 2 weeks out
    rw_all = pd.read_parquet(DATA_PROC / "region_week_all.parquet")
    def lead_of(row):
        g = rw_all[(rw_all.region == row.region) & (rw_all.week > row.week) & (rw_all.week <= row.week + pd.Timedelta(weeks=4))].sort_values("week")
        hit = g[g.log_max >= thr]
        return int((hit.iloc[0].week - row.week).days // 7) if len(hit) else 0
    tp = test[test.y == 1].copy()
    tp["lead"] = tp.apply(lead_of, axis=1)
    cand = tp[(tp.lead >= 2) & (tp.p >= test.p.quantile(0.9))]
    if cand.empty: cand = tp[tp.lead >= 2]
    if cand.empty: cand = tp
    tp = cand.sort_values("p", ascending=False)
    fp = test[test.y == 0].sort_values("p", ascending=False)
    quiet = test[(test.week.dt.month == 7) & (test.y == 0)].sort_values("p")
    cases = []
    for tag, row in [("true_positive", tp.iloc[0]), ("false_positive", fp.iloc[0]), ("quiet", quiet.iloc[0])]:
        i = int(row.idx)
        cases.append({"tag": tag, "region": names[int(row.region)], "week": row.week.strftime("%Y-%m-%d"), "p": float(row.p), "y": int(row.y),
                      "lead_weeks": int(row.get("lead", 0)) if tag == "true_positive" else None,
                      "max_cells_this_week": None if pd.isna(row.log_max_t0) else float(10 ** row.log_max_t0 - 1),
                      "future_max_cells": None if pd.isna(row.future_log_max) else float(10 ** row.future_log_max - 1),
                      "shap": {f: float(sv[i, k]) for k, f in enumerate(FEATURES)},
                      "x": {f: (None if pd.isna(X[i, k]) else float(X[i, k])) for k, f in enumerate(FEATURES)}})

    # --- risk strips (grouped SHAP over time): out-of-sample 2022-23 Lee-Collier; in-sample 2017-19 for the famous bloom
    def strip(region, d0, d1):
        m = (allr.region == region) & (allr.week >= d0) & (allr.week <= d1)
        g = allr[m].sort_values("week"); idx = g.index.values
        S = sv_all[idx]
        return {"region": names[region], "weeks": g.week.dt.strftime("%Y-%m-%d").tolist(), "p": R(g.p, 4), "y": g.y.astype(int).tolist(),
                "split": g.split.tolist(), "max_cells": [None if pd.isna(v) else float(10 ** v - 1) for v in g.log_max_t0],
                "n_samples": g.n_samples_t0.astype(int).tolist(), "base_logit": base,
                "groups": {gname: R(S[:, ix].sum(1)) for gname, ix in gidx.items()}}
    strips = {"oos_2022_23": strip(7, "2022-06-01", "2023-04-30"), "insample_2017_19": strip(7, "2017-06-01", "2019-03-31"),
              "oos_2021_tampa": strip(4, "2021-01-01", "2021-12-31")}

    # --- raw count trace for the 'vitals' section: Lee-Collier weekly max 2017-06 → 2019-03 (the famous bloom), samples/week
    rw = pd.read_parquet(DATA_PROC / "region_week_all.parquet")
    tr = rw[(rw.region == 7) & (rw.week >= "2017-06-01") & (rw.week <= "2019-03-31")].sort_values("week")
    trace = {"region": names[7], "weeks": tr.week.dt.strftime("%Y-%m-%d").tolist(),
             "max_cells": [None if pd.isna(v) else float(v) for v in tr.max_cells], "n_samples": tr.n_samples.astype(int).tolist(),
             "sst": [None if pd.isna(v) else round(float(v), 2) for v in tr.sst_t0],
             "discharge_cfs": [None if pd.isna(v) else round(float(10 ** v - 1)) for v in tr.discharge_30d_t0]}

    # coverage heatmap: modelling-window years × regions (sample counts)
    years = sorted(int(y) for y in eda["coverage_year_region"] if cfg["split"]["min_train_year"] <= int(y) <= cfg["split"]["test_end"])
    cov = {"years": years, "regions": [names[r] for r in sorted(names)],
           "counts": [[eda["coverage_year_region"][str(y)].get(names[r], 0) for r in sorted(names)] for y in years]}

    # dependence plots: top6 with partner colouring
    dep = {}
    for f in shap_s["top6"]:
        k = FEATURES.index(f); pk = FEATURES.index(shap_s["dependence_partners"][f])
        dep[f] = {"x": R(X[keep, k]), "shap": R(sv[keep, k]), "partner": shap_s["dependence_partners"][f], "partner_x": R(X[keep, pk])}

    site = {
        "generated": pd.Timestamp.utcnow().strftime("%Y-%m-%d"), "config": {"target": cfg["target"], "split": cfg["split"], "xgb": cfg["xgb"], "shap": cfg["shap"]},
        "regions": [{"id": r, "name": names[r]} for r in sorted(names)],
        "gauges": cfg["gauges"], "region_boxes": cfg["region_boxes"],
        "data": {"n_samples": eda["n_samples"], "per_year": {y: v for y, v in eda["per_year"].items()}, "per_region": eda["per_region"],
                 "zero_fraction": eda["zero_fraction"], "coverage": cov,
                 "map": {"lat": R(loc.la, 2), "lon": R(loc.lo, 2), "region": loc.region.astype(int).tolist(), "n": loc.n.astype(int).tolist()},
                 "features_report": freport, "trace": trace},
        "features": [{"name": f, "label": FEATURE_DOC[f][0], "desc": FEATURE_DOC[f][1], "tag": FEATURE_DOC[f][2], "group": group_of[f]} for f in FEATURES],
        "metrics": {k: metrics[k] for k in ("splits", "full", "no_surveillance", "surveillance_only_test_auroc", "climatology_baseline_test", "rolling_origin", "sensitivity_50k", "config_hash")},
        "shap": {"base_logit": base, "base_p": shap_s["base_p"], "additivity_max_gap": shap_s["additivity_max_gap"], "perturbation": shap_s["perturbation"],
                 "background_n": shap_s["background_n"], "n_test_rows": shap_s["n_test_rows"], "mean_abs": shap_s["mean_abs_shap"],
                 "group_mean_abs": shap_s["group_mean_abs_shap"], "top6": shap_s["top6"], "top_interaction": shap_s["top_interaction_pair"],
                 "beeswarm": {"features": FEATURES, "shap": [R(sv[keep, k]) for k in range(len(FEATURES))],
                              "x": [[None if np.isnan(v) else round(float(v), 3) for v in X[keep, k]] for k in range(len(FEATURES))],
                              "y": test.y.values[keep].astype(int).tolist(), "p": R(test.p.values[keep], 4)},
                 "dependence": dep, "cases": cases, "strips": strips},
        "whatif": whatif,
    }
    out = OUT / "site_data.json"
    out.write_text(json.dumps(clean(site), separators=(",", ":"), allow_nan=False))
    print(f"→ {out} ({out.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()

"""Counterfactual re-scoring: the discharge lever (the gauge(s) flagged `lever: true` in config.yaml — S-79) reduced by
30% over one region's strip. Correlational, not causal — the site carries the caveat. Writes outputs/whatif.json."""
import json
import numpy as np, pandas as pd, xgboost as xgb
from hab import load_config, DATA_PROC, OUT
from hab.build_features import FEATURES
from hab.export_site_data import lever_gauges

def main():
    cfg = load_config()
    df = pd.read_parquet(DATA_PROC / "all_scored.parquet")
    m = xgb.XGBClassifier(); m.load_model(OUT / "model.json")
    out = {"lever_gauges": lever_gauges(cfg)}   # read from config (M-1a); an instance with no lever gets [] and should not run this
    assert out["lever_gauges"], "no gauge carries lever: true — nothing to counterfactual"
    for region, d0, d1 in [(7, "2022-06-01", "2023-04-30"), (7, "2017-06-01", "2019-03-31"), (4, "2021-01-01", "2021-12-31")]:
        g = df[(df.region == region) & (df.week >= d0) & (df.week <= d1)].sort_values("week").copy()
        y0, y1 = d0[:4], d1[:4]
        cf = g.copy()
        for c in ("discharge_30d_t0", "discharge_30d_t3"):
            cf[c] = np.log10(1 + 0.7 * (10 ** cf[c] - 1))      # 30% less flow, in log space
        cf["discharge_anom_t0"] = cf["discharge_anom_t0"] + (cf["discharge_30d_t0"] - g["discharge_30d_t0"])
        p0 = m.predict_proba(g[FEATURES])[:, 1]; p1 = m.predict_proba(cf[FEATURES])[:, 1]
        out[f"r{region}_{y0}_{y1}"] = {"region": int(region), "weeks": g.week.dt.strftime("%Y-%m-%d").tolist(),
                                       "p_actual": p0.round(4).tolist(), "p_discharge_minus30": p1.round(4).tolist(),
                                       "y": g.y.astype(int).tolist(), "split": g.split.tolist(),
                                       "mean_abs_delta": float(np.mean(np.abs(p1 - p0))), "mean_delta": float(np.mean(p1 - p0)),
                                       "discharge_30d_t0": g.discharge_30d_t0.round(3).tolist()}
        print(f"region {region} {y0}-{y1}: mean Δp = {np.mean(p1-p0):+.4f}, mean |Δp| = {np.mean(np.abs(p1-p0)):.4f}, max |Δp| = {np.max(np.abs(p1-p0)):.4f}")
    (OUT / "whatif.json").write_text(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()

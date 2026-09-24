"""Build the region × ISO-week 'patient' table, the vitals (features) and the onset label.

Everything in a feature row for week t is computed from data dated <= the end of week t.
Run: .venv/bin/python -m hab.build_features [--self-test]
"""
import sys, json
import numpy as np
import pandas as pd
from hab import load_config, DATA_RAW, DATA_PROC
from hab.regions import assign_regions

FEATURE_GROUPS = {
    "counts": ["log_max_t0", "log_max_t1", "log_max_t2", "log_max_t3", "log_med_t0", "log_p90_t0",
               "roll_max_4w", "roll_max_8w", "growth_1w", "growth_2w",
               "weeks_since_bloom", "weeks_since_detect", "weeks_since_sample"],
    "surveillance": ["n_samples_t0", "n_samples_4w"],
    "season": ["woy_sin", "woy_cos"],
    "sst": ["sst_t0", "sst_anom_t0", "sst_anom_t2", "sst_anom_t4", "sst_delta_4w"],
    "discharge": ["discharge_30d_t0", "discharge_30d_t3", "discharge_anom_t0"],
}
FEATURES = [f for g in FEATURE_GROUPS.values() for f in g]


def week_start(dates):
    """Monday of the ISO week containing each date."""
    d = pd.to_datetime(dates)
    return (d - pd.to_timedelta(d.dt.weekday, unit="D")).dt.normalize()


def weeks_since(flag, cap=104):
    """For a boolean series ordered in time: weeks since the last True at or before t (cap if never)."""
    idx = np.arange(len(flag))
    last = pd.Series(np.where(flag.values, idx, np.nan)).ffill().values
    out = idx - last
    out = np.where(np.isnan(last), cap, out)
    return np.minimum(out, cap)


def aggregate_region_week(samples, cfg):
    s = samples.copy()
    s["region"] = assign_regions(s)
    s["week"] = week_start(s["sample_date"])
    s["logc"] = np.log10(1.0 + s["cells_per_l"].clip(lower=0))
    g = s.groupby(["region", "week"])
    rw = g.agg(max_cells=("cells_per_l", "max"), log_max=("logc", "max"), log_med=("logc", "median"),
               log_p90=("logc", lambda x: np.percentile(x, 90)), n_samples=("logc", "size")).reset_index()
    regions = sorted(s["region"].unique())
    weeks = pd.date_range(rw["week"].min(), rw["week"].max(), freq="7D")
    grid = pd.MultiIndex.from_product([regions, weeks], names=["region", "week"]).to_frame(index=False)
    rw = grid.merge(rw, on=["region", "week"], how="left")
    rw["n_samples"] = rw["n_samples"].fillna(0).astype(int)
    return rw.sort_values(["region", "week"]).reset_index(drop=True)


def count_features(rw, cfg):
    thr = np.log10(1 + cfg["target"]["bloom_threshold_cells_per_l"])
    det = np.log10(1 + cfg["target"]["detect_threshold"])
    out = []
    for _, g in rw.groupby("region", sort=False):
        g = g.sort_values("week").copy()
        lm = g["log_max"]
        g["log_max_t0"] = lm
        for k in (1, 2, 3):
            g[f"log_max_t{k}"] = lm.shift(k)
        g["log_med_t0"] = g["log_med"]
        g["log_p90_t0"] = g["log_p90"]
        g["roll_max_4w"] = lm.rolling(4, min_periods=1).max()
        g["roll_max_8w"] = lm.rolling(8, min_periods=1).max()
        g["growth_1w"] = lm - lm.shift(1)
        g["growth_2w"] = lm - lm.shift(2)
        g["weeks_since_bloom"] = weeks_since(lm.ge(thr).fillna(False))
        g["weeks_since_detect"] = weeks_since(lm.ge(det).fillna(False))
        g["weeks_since_sample"] = weeks_since(g["n_samples"].gt(0))
        g["n_samples_t0"] = g["n_samples"]
        g["n_samples_4w"] = g["n_samples"].rolling(4, min_periods=1).sum()
        # last-known state: forward-fill the observed max for up to 4 weeks (used for the 'already in bloom' drop)
        g["last_obs_log_max"] = lm.ffill(limit=4)
        # outcome window: t+1..t+4 (future-looking, used ONLY for the label)
        fut = pd.concat([lm.shift(-k) for k in range(1, cfg["target"]["horizon_weeks"] + 1)], axis=1)
        g["future_log_max"] = fut.max(axis=1)
        g["n_future_samples"] = pd.concat([g["n_samples"].shift(-k) for k in range(1, cfg["target"]["horizon_weeks"] + 1)], axis=1).sum(axis=1)
        out.append(g)
    df = pd.concat(out, ignore_index=True)
    woy = df["week"].dt.isocalendar().week.astype(float)
    df["woy_sin"] = np.sin(2 * np.pi * woy / 52.18)
    df["woy_cos"] = np.cos(2 * np.pi * woy / 52.18)
    return df


def sst_features(df, sst):
    sst = sst.copy()
    sst["week"] = week_start(sst["date"])
    w = sst.groupby(["region", "week"])["sst"].mean().reset_index()
    w["woy"] = w["week"].dt.isocalendar().week.astype(int)
    clim = (w[(w.week.dt.year >= 1982) & (w.week.dt.year <= 2011)]
            .groupby(["region", "woy"])["sst"].mean().rename("sst_clim").reset_index())
    w = w.merge(clim, on=["region", "woy"], how="left")
    w["sst_anom"] = w["sst"] - w["sst_clim"]
    w = w.sort_values(["region", "week"])
    feats = []
    for _, g in w.groupby("region", sort=False):
        g = g.copy()
        g["sst_t0"] = g["sst"]
        g["sst_anom_t0"] = g["sst_anom"]
        g["sst_anom_t2"] = g["sst_anom"].shift(2)
        g["sst_anom_t4"] = g["sst_anom"].shift(4)
        g["sst_delta_4w"] = g["sst"] - g["sst"].shift(4)
        feats.append(g[["region", "week", "sst_t0", "sst_anom_t0", "sst_anom_t2", "sst_anom_t4", "sst_delta_4w"]])
    return df.merge(pd.concat(feats), on=["region", "week"], how="left")


def discharge_features(df, q, cfg):
    q = q.copy()
    q["logq"] = np.log10(1.0 + q["discharge_cfs"])
    daily = q.pivot_table(index="date", columns="site", values="logq")
    daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max(), freq="D"))
    roll30 = daily.rolling(30, min_periods=20).mean()      # 30-day mean ending each day
    # anomaly vs day-of-year climatology (1990-2016, training era only)
    sub = roll30[(roll30.index.year >= 1990) & (roll30.index.year <= 2016)]
    clim = sub.groupby(sub.index.dayofyear).mean()
    anom = roll30 - clim.reindex(roll30.index.dayofyear).set_axis(roll30.index)
    site_to_regions = {s: m["regions"] for s, m in cfg["gauges"].items()}
    rows = []
    for region in sorted(df["region"].unique()):
        sites = [s for s, rs in site_to_regions.items() if region in rs and s in roll30.columns]
        wk = df.loc[df.region == region, "week"].drop_duplicates().sort_values()
        end = wk + pd.Timedelta(days=6)        # window ends on the Sunday closing week t
        end3 = end - pd.Timedelta(weeks=3)
        if not sites:
            rows.append(pd.DataFrame({"region": region, "week": wk.values, "discharge_30d_t0": np.nan,
                                      "discharge_30d_t3": np.nan, "discharge_anom_t0": np.nan}))
            continue
        r30 = roll30[sites].mean(axis=1)
        a30 = anom[sites].mean(axis=1)
        rows.append(pd.DataFrame({"region": region, "week": wk.values,
                                  "discharge_30d_t0": r30.reindex(end).values,
                                  "discharge_30d_t3": r30.reindex(end3).values,
                                  "discharge_anom_t0": a30.reindex(end).values}))
    return df.merge(pd.concat(rows), on=["region", "week"], how="left")


def make_label(df, cfg):
    thr = np.log10(1 + cfg["target"]["bloom_threshold_cells_per_l"])
    df = df.copy()
    df["y"] = (df["future_log_max"] >= thr).astype("Int64")
    df.loc[df["future_log_max"].isna(), "y"] = pd.NA
    df["already_in_bloom"] = df["last_obs_log_max"].ge(thr).fillna(False)
    df["outcome_unknown"] = df["n_future_samples"].eq(0)
    return df


def build(samples, sst, q, cfg):
    rw = aggregate_region_week(samples, cfg)
    df = count_features(rw, cfg)
    df = sst_features(df, sst)
    df = discharge_features(df, q, cfg)
    df = make_label(df, cfg)
    return df


def finalize(df, cfg):
    """Apply the modelling-set filters and report what they removed."""
    y0 = df["week"].dt.year >= cfg["split"]["min_train_year"]
    y1 = df["week"].dt.year <= cfg["split"]["test_end"]
    base = df[y0 & y1]
    report = {"region_weeks_in_window": int(len(base))}
    m = base[~base["already_in_bloom"]]
    report["dropped_already_in_bloom"] = int(len(base) - len(m))
    m2 = m[~m["outcome_unknown"]]
    report["dropped_outcome_unknown"] = int(len(m) - len(m2))
    report["modelling_rows"] = int(len(m2))
    report["positives"] = int(m2["y"].sum())
    report["prevalence"] = float(m2["y"].mean())
    return m2.reset_index(drop=True), report


def self_test():
    """Leakage test: perturbing week t+1 must not change any feature at week t; the label must change."""
    cfg = load_config()
    rng = np.random.default_rng(0)
    weeks = pd.date_range("2000-01-03", periods=60, freq="7D")
    rows = []
    for w in weeks:
        for _ in range(3):
            rows.append({"sample_date": w + pd.Timedelta(days=int(rng.integers(0, 7))),
                         "lat": 26.2, "lon": -82.0, "cells_per_l": float(rng.integers(0, 5000))})
    s = pd.DataFrame(rows)
    sst = pd.DataFrame({"date": pd.date_range("1999-01-01", "2001-12-31"), "region": 7, "sst": 25.0})
    sst["sst"] += rng.normal(0, 1, len(sst))
    q = pd.DataFrame({"date": pd.date_range("1999-01-01", "2001-12-31"), "site": "02292900",
                      "discharge_cfs": 1000.0 + rng.normal(0, 50, len(sst))})
    a = build(s, sst, q, cfg)
    t = weeks[30]
    s2 = s.copy()
    s2.loc[s2.sample_date.between(weeks[31], weeks[31] + pd.Timedelta(days=6)), "cells_per_l"] = 5e6
    b = build(s2, sst, q, cfg)
    ra, rb = a[a.week == t].iloc[0], b[b.week == t].iloc[0]
    for f in FEATURES:
        va, vb = ra[f], rb[f]
        assert (pd.isna(va) and pd.isna(vb)) or np.isclose(va, vb), f"LEAK: {f} at week t changed when t+1 changed ({va} → {vb})"
    assert ra["y"] == 0 and rb["y"] == 1, f"label did not respond to t+1 change: {ra['y']} → {rb['y']}"
    # and a t+5 change must NOT change the label (outside the horizon)
    s3 = s.copy()
    s3.loc[s3.sample_date.between(weeks[35], weeks[35] + pd.Timedelta(days=6)), "cells_per_l"] = 5e6
    c = build(s3, sst, q, cfg)
    assert c[c.week == t].iloc[0]["y"] == 0, "label saw beyond the horizon"
    print("✅ build_features self-test passed (no feature at t depends on t+1; label does; horizon respected)")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    cfg = load_config()
    DATA_PROC.mkdir(parents=True, exist_ok=True)
    samples = pd.read_parquet(DATA_RAW / "fwc_hab_karenia_1970_2023.parquet")
    sst = pd.read_parquet(DATA_RAW / "oisst_region_daily.parquet")
    q = pd.read_parquet(DATA_RAW / "usgs_discharge_daily.parquet")
    df = build(samples, sst, q, cfg)
    df.to_parquet(DATA_PROC / "region_week_all.parquet", index=False)
    m, report = finalize(df, cfg)
    m.to_parquet(DATA_PROC / "features.parquet", index=False)
    (DATA_PROC / "features_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print("missingness (modelling rows):")
    print(m[FEATURES].isna().mean().round(3).to_string())


if __name__ == "__main__":
    main()

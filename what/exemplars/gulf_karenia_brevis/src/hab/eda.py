"""Descriptive pass over the raw samples: coverage by year × region, threshold rates. Writes outputs/eda.json."""
import json
import numpy as np, pandas as pd
from hab import load_config, DATA_RAW, OUT
from hab.regions import assign_regions, region_names

def main():
    cfg = load_config(); OUT.mkdir(exist_ok=True)
    s = pd.read_parquet(DATA_RAW / "fwc_hab_karenia_1970_2023.parquet")
    s["region"] = assign_regions(s); s["year"] = s.sample_date.dt.year
    names = region_names()
    cov = s.groupby(["year", "region"]).size().unstack(fill_value=0)
    per_year = s.groupby("year").agg(n=("cells_per_l", "size"), ge1e5=("cells_per_l", lambda x: (x >= 1e5).sum()),
                                     ge1e6=("cells_per_l", lambda x: (x >= 1e6).sum()))
    per_region = s.groupby("region").agg(n=("cells_per_l", "size"), ge1e5=("cells_per_l", lambda x: (x >= 1e5).mean()),
                                         lat_mean=("lat", "mean"), lon_mean=("lon", "mean"))
    per_region.index = [names[i] for i in per_region.index]
    out = {"n_samples": int(len(s)), "coverage_year_region": {str(y): {names[r]: int(v) for r, v in row.items()} for y, row in cov.iterrows()},
           "per_year": per_year.to_dict("index"), "per_region": per_region.round(4).to_dict("index"),
           "count_distribution_log10_quantiles": {str(q): float(np.quantile(np.log10(1 + s.cells_per_l), q)) for q in (0.5, 0.75, 0.9, 0.95, 0.99)},
           "zero_fraction": float((s.cells_per_l == 0).mean()),
           "layer_location_examples": {l: s[s.layer == l]["location"].dropna().head(3).tolist() for l in s.layer.unique()}}
    (OUT / "eda.json").write_text(json.dumps(out, indent=1, default=int))
    print(per_year.loc[[1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]])
    print(per_region.round(3))
    print("zero fraction", out["zero_fraction"], "| log10 quantiles", out["count_distribution_log10_quantiles"])

if __name__ == "__main__":
    main()

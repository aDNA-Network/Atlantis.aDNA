"""Fetch FWC Historic Harmful Algal Bloom Events (Karenia brevis cell counts) from the
FWC ArcGIS Open Data MapServer layers, paginated, cached to parquet.

Run: .venv/bin/python -m hab.fetch_fwc   (from src/)
"""
import sys, time, json
import requests
import pandas as pd
from hab import load_config, DATA_RAW

BASE = ("https://gis.myfwc.com/mapping/rest/services/Open_Data/"
        "Historic_Harmful_Algal_Bloom_Events_{name}/MapServer/{layer}/query")
PAGE = 2000
FIELDS = "OBJECTID,SAMPLE_DATE,TIME,TIMEZONE,DEPTH,LOCATION,LATITUDE,LONGITUDE,NAME,COUNT_,HAB_ID"


def get(url, params, retries=5):
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=120)
            r.raise_for_status()
            j = r.json()
            if "error" in j:
                raise RuntimeError(j["error"])
            return j
        except Exception as e:  # noqa
            wait = 2 ** i
            print(f"  retry {i+1}/{retries} after {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up: {url} {params}")


def fetch_layer(name, layer, expected):
    out = DATA_RAW / f"fwc_{name}.parquet"
    if out.exists():
        df = pd.read_parquet(out)
        print(f"{name}: cached {len(df)} rows")
        return df
    url = BASE.format(name=name, layer=layer)
    n = get(url, {"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
    print(f"{name}: server count {n} (expected {expected})")
    rows, offset = [], 0
    while offset < n:
        j = get(url, {"where": "1=1", "outFields": FIELDS, "returnGeometry": "false",
                      "orderByFields": "OBJECTID", "resultOffset": offset,
                      "resultRecordCount": PAGE, "f": "json"})
        feats = j.get("features", [])
        if not feats:
            break
        rows.extend(f["attributes"] for f in feats)
        offset += len(feats)
        print(f"  {offset}/{n}", end="\r", flush=True)
    df = pd.DataFrame(rows)
    df["layer"] = name
    assert len(df) == n, f"{name}: fetched {len(df)} != server count {n}"
    if n != expected:
        print(f"  ⚠ {name}: server count {n} differs from probe-day expected {expected}")
    df.to_parquet(out, index=False)
    print(f"{name}: fetched {len(df)} rows → {out.name}")
    return df


def main():
    cfg = load_config()
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    parts = [fetch_layer(l["name"], l["layer"], l["expected"]) for l in cfg["fwc_layers"]]
    df = pd.concat(parts, ignore_index=True)
    df["sample_date"] = pd.to_datetime(df["SAMPLE_DATE"], unit="ms", utc=True).dt.tz_convert(None).dt.normalize()
    df = df.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon", "COUNT_": "cells_per_l",
                            "DEPTH": "depth_m", "LOCATION": "location", "NAME": "species",
                            "HAB_ID": "hab_id", "OBJECTID": "objectid"})
    df = df[["objectid", "hab_id", "sample_date", "lat", "lon", "depth_m", "location", "species",
             "cells_per_l", "layer"]]
    n0 = len(df)
    df = df[df["species"] == "Karenia brevis"]
    print(f"species filter: {n0} → {len(df)} rows")
    df = df.dropna(subset=["sample_date", "lat", "lon", "cells_per_l"])
    print(f"after dropna: {len(df)} rows; date range {df.sample_date.min().date()} → {df.sample_date.max().date()}")
    out = DATA_RAW / "fwc_hab_karenia_1970_2023.parquet"
    df.to_parquet(out, index=False)
    print(f"→ {out} ({out.stat().st_size/1e6:.1f} MB)")
    summary = {"rows": int(len(df)), "min_date": str(df.sample_date.min().date()),
               "max_date": str(df.sample_date.max().date()),
               "per_layer": df.groupby("layer").size().to_dict(),
               "fetched_at": pd.Timestamp.utcnow().isoformat()}
    (DATA_RAW / "fwc_fetch_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

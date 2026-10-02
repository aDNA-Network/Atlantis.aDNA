"""Fetch environmental covariates, cached to parquet:
  * NOAA OISST v2.1 daily SST per region box (CoastWatch ERDDAP griddap ncdcOisst21Agg_LonPM180)
  * USGS NWIS daily discharge (00060) for the configured gauges
Run: .venv/bin/python -m hab.fetch_env [--offline]
"""
import sys, io, time, json
import requests
import pandas as pd
from hab import load_config, DATA_RAW
from hab.provenance import summarise, now_utc

ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv"
NWIS = "https://waterservices.usgs.gov/nwis/dv/"
OFFLINE = "--offline" in sys.argv
REGIONS = [int(x) for a in sys.argv if a.startswith("--regions=") for x in a.split("=")[1].split(",")]
MERGE = "--no-merge" not in sys.argv


def get_text(url, params=None, retries=5):
    if OFFLINE:
        raise RuntimeError(f"offline: would fetch {url}")
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=300)
            if r.status_code == 404 and "No data" in r.text:  # ERDDAP: empty subset
                return ""
            r.raise_for_status()
            return r.text
        except Exception as e:  # noqa
            wait = 3 * 2 ** i
            print(f"  retry {i+1}/{retries} after {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up: {url}")


def fetch_sst(cfg):
    out = DATA_RAW / "oisst_region_daily.parquet"
    if out.exists():
        print(f"sst: cached {out.name}")
        if not (DATA_RAW / "oisst_fetch_summary.json").exists(): summarise("oisst")
        return pd.read_parquet(out)
    chunks = [(y, min(y + 4, 2023)) for y in range(1982, 2024, 5)]
    frames = []
    for rid, (la0, la1, lo0, lo1) in cfg["region_boxes"].items():
        if REGIONS and int(rid) not in REGIONS:
            continue
        for y0, y1 in chunks:
            cache = DATA_RAW / "oisst" / f"r{rid}_{y0}_{y1}.csv"
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not cache.exists():
                q = (f"sst[({y0}-01-01T12:00:00Z):1:({y1}-12-31T12:00:00Z)][(0.0):1:(0.0)]"
                     f"[({la0}):1:({la1})][({lo0}):1:({lo1})]")
                txt = get_text(ERDDAP + "?" + q)
                tmp = cache.with_suffix(".tmp"); tmp.write_text(txt); tmp.rename(cache)
                print(f"  sst r{rid} {y0}-{y1}: {len(txt)/1e6:.1f} MB")
            df = pd.read_csv(cache, skiprows=[1])
            if df.empty:
                continue
            df = df.dropna(subset=["sst"])
            df["date"] = pd.to_datetime(df["time"]).dt.tz_convert(None).dt.normalize()
            d = df.groupby("date")["sst"].mean().rename("sst").reset_index()
            d["region"] = int(rid)
            frames.append(d)
    if not MERGE:
        print("chunks fetched; no merge"); return None
    sst = pd.concat(frames, ignore_index=True)
    sst.to_parquet(out, index=False)
    summarise("oisst", fetched_at=now_utc())
    print(f"sst: {len(sst)} region-days → {out.name}")
    return sst


def fetch_discharge(cfg):
    out = DATA_RAW / "usgs_discharge_daily.parquet"
    if out.exists():
        print(f"discharge: cached {out.name}")
        if not (DATA_RAW / "usgs_fetch_summary.json").exists(): summarise("usgs")
        return pd.read_parquet(out)
    frames = []
    for site, meta in cfg["gauges"].items():
        txt = get_text(NWIS, {"format": "json", "sites": site, "parameterCd": "00060",
                              "startDT": "1990-01-01", "endDT": "2023-12-31", "siteStatus": "all"})
        j = json.loads(txt)
        ts = j["value"]["timeSeries"]
        if not ts:
            print(f"  ⚠ {site}: no series"); continue
        vals = ts[0]["values"][0]["value"]
        d = pd.DataFrame(vals)
        d["date"] = pd.to_datetime(d["dateTime"].str[:10])
        d["discharge_cfs"] = pd.to_numeric(d["value"], errors="coerce")
        d = d[["date", "discharge_cfs"]].dropna()
        d.loc[d.discharge_cfs < 0, "discharge_cfs"] = 0.0   # S-79 reports reverse flow as negative
        d["site"] = site
        frames.append(d)
        print(f"  {site} {meta['name']}: {len(d)} days {d.date.min().date()}→{d.date.max().date()}")
    q = pd.concat(frames, ignore_index=True)
    q.to_parquet(out, index=False)
    summarise("usgs", fetched_at=now_utc())
    print(f"discharge: {len(q)} site-days → {out.name}")
    return q


def main():
    cfg = load_config()
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    fetch_discharge(cfg)
    fetch_sst(cfg)
    print("env fetch done")


if __name__ == "__main__":
    main()

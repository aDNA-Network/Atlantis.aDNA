"""Fetch summaries — one JSON per cached raw artifact: rows · date range · sha256 · fetched_at.

`data/raw/<source>_fetch_summary.json` is the provenance record the dataset notes, the board entry's `data_pins`
and an instance's stream registry point at. Run `python -m hab.provenance` to (re)summarise the cached parquets;
`fetched_at` is preserved when the bytes are unchanged, otherwise it falls back to the file's mtime and says so.
The fetchers call `summarise(source, fetched_at=<now>)` right after a real download. (M-1a, 2026-10-02.)
"""
import hashlib, json, sys
from datetime import datetime, timezone
import pandas as pd
from hab import DATA_RAW

SOURCES = {  # summary stem → (artifact, date column, source-specific extras)
    "fwc":   ("fwc_hab_karenia_1970_2023.parquet", "sample_date",
              lambda df: {"per_layer": {str(k): int(v) for k, v in df.groupby("layer").size().items()}}),
    "oisst": ("oisst_region_daily.parquet", "date",
              lambda df: {"regions": sorted(int(r) for r in df["region"].unique()), "region_days": int(len(df))}),
    "usgs":  ("usgs_discharge_daily.parquet", "date",
              lambda df: {"sites": sorted(str(s) for s in df["site"].unique()), "site_days": int(len(df))}),
}


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def summarise(source, fetched_at=None):
    artifact, date_col, extras = SOURCES[source]
    path = DATA_RAW / artifact
    out = DATA_RAW / f"{source}_fetch_summary.json"
    df = pd.read_parquet(path)
    digest = sha256(path)
    prev = json.loads(out.read_text()) if out.exists() else {}
    if fetched_at is not None:
        src = "fetch"
    elif prev.get("sha256") == digest and prev.get("fetched_at"):
        fetched_at, src = prev["fetched_at"], prev.get("fetched_at_source", "fetch")
    elif prev.get("fetched_at") and "sha256" not in prev:
        fetched_at, src = prev["fetched_at"], "legacy summary (pre-sha256, S329); kept at M-1a"
    else:
        fetched_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
        src = "file mtime (retro-summarised at M-1a; no fetch-time record)"
    summary = {"artifact": artifact, "rows": int(len(df)),
               "min_date": str(pd.Timestamp(df[date_col].min()).date()),
               "max_date": str(pd.Timestamp(df[date_col].max()).date()),
               "sha256": digest, "fetched_at": fetched_at, "fetched_at_source": src,
               "summarised_at": now_utc(), **extras(df)}
    out.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main():
    wanted = [a for a in sys.argv[1:] if a in SOURCES] or list(SOURCES)
    for s in wanted:
        if not (DATA_RAW / SOURCES[s][0]).exists():
            print(f"{s}: artifact missing, skipped"); continue
        r = summarise(s)
        print(f"{s}: {r['rows']} rows {r['min_date']}→{r['max_date']} sha256 {r['sha256'][:12]}… fetched_at {r['fetched_at']} ({r['fetched_at_source']})")


if __name__ == "__main__":
    main()

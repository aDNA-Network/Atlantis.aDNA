"""Ingest Rule-5 provenance for a cached artifact — rows · date range · sha256 · ingested_at · pipeline_version.

Generalised from the exemplar's `hab.provenance` (M-1a). The summary JSON sits beside the artifact as
`<stem>_fetch_summary.json` (the exemplar's naming) and is what a stream registry's `sha256` / `ingested_at` and a
board entry's `data_pins` point at. `fetched_at` is kept when the bytes are unchanged; otherwise it falls back to the
file's mtime and says so — a summary never invents a fetch time.
"""
from __future__ import annotations

import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256(path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarise(artifact: Path, summary_path: Path, date_col: str, extras=None, fetched_at: str | None = None,
              pipeline_version: str | None = None) -> dict:
    artifact, summary_path = Path(artifact), Path(summary_path)
    df = pd.read_parquet(artifact)
    digest = sha256(artifact)
    prev = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    if fetched_at is not None:
        src = "fetch"
    elif prev.get("sha256") == digest and prev.get("fetched_at"):
        fetched_at, src = prev["fetched_at"], prev.get("fetched_at_source", "fetch")
    else:
        fetched_at = datetime.fromtimestamp(artifact.stat().st_mtime, tz=timezone.utc).isoformat()
        src = "file mtime (no fetch-time record)"
    summary = {"artifact": artifact.name, "rows": int(len(df)),
               "min_date": str(pd.Timestamp(df[date_col].min()).date()),
               "max_date": str(pd.Timestamp(df[date_col].max()).date()),
               "sha256": digest, "fetched_at": fetched_at, "fetched_at_source": src,
               "summarised_at": now_utc(), **({"pipeline_version": pipeline_version} if pipeline_version else {}),
               **(extras(df) if extras else {})}
    tmp = summary_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(summary, indent=2) + "\n"); tmp.rename(summary_path)
    return summary


def daily_completeness(df, date_col: str, unit_col: str | None = None, listed: int = 20) -> dict:
    """Distinct days present against the calendar span of a daily artifact (M-2a-ii III F-2). A day the source never sent is
    not a null, so a null count cannot see it (FKNMS DHW has no 1999-05-01: CRW's own axis skips it). `dates_per_unit`
    says whether every unit has every day the artifact has. At most `listed` missing days are named; `n_missing` counts all."""
    d = pd.to_datetime(df[date_col]).dt.normalize()
    if d.empty:
        return {"calendar_days": 0, "n_dates": 0, "n_missing": 0, "missing_dates": []}
    cal, have = pd.date_range(d.min(), d.max(), freq="D"), pd.DatetimeIndex(d.unique())
    miss = cal.difference(have)
    out = {"calendar_days": int(len(cal)), "n_dates": int(len(have)), "n_missing": int(len(miss)),
           "missing_dates": [str(x.date()) for x in miss[:listed]]}
    if unit_col and unit_col in df.columns:
        per = d.groupby(df[unit_col].to_numpy()).nunique()
        out["dates_per_unit"] = {"min": int(per.min()), "max": int(per.max())}
    return out


def verify(artifact: Path, summary_path: Path) -> tuple[bool, str, str]:
    """Re-hash the cached bytes against the recorded pin. A well-formed pin of the wrong bytes is only caught here."""
    recorded = json.loads(Path(summary_path).read_text())["sha256"]
    actual = sha256(artifact)
    return actual == recorded, actual, recorded

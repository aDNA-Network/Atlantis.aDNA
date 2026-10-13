"""NOAA NDBC standard meteorological data (historical yearly files): one daily series per station.

BUILT at M-3b-ii-a (WI-19), for `FloridaKeysCoral.aDNA`'s reef-light wind (the C-MAN lights MLRF1 · SMKF1 · LONF1 ·
SANF1). Until then it was declared only (M-1b-i ruling). One file per station-year:

    https://www.ndbc.noaa.gov/data/historical/stdmet/<station>h<year>.txt.gz

The files come in three header forms, all read here by the header line's own column names:
  - before 1999: `YY MM DD hh WD WSPD …` (a two-digit year, no minute column, hourly);
  - 1999–2004: `YYYY MM DD hh …` (a four-digit year; some years carry `mm`);
  - from 2005: `#YY MM DD hh mm WDIR WSPD …` followed by a `#yr mo dy hr mn degT m/s …` units line (10-minute rows from
    the late 2000s on some stations).
Missing values are written as 99 · 999 · 9999 (per column width). Every such value becomes NaN before any reduction.
Times are UTC, so the day boundary is UTC midnight (`day_boundary` in the summary).

spec: {stations: [ids], years: [y0, y1], variable (a header column, e.g. WSPD), min_hours (default 18),
       value_name (default: the stream's `columns.value`, else the variable lower-cased)}

Reduction, per station and UTC day:
  1. Rows with the same timestamp across adjacent year files are counted once (the first file's row; `duplicates`).
  2. A day keeps its value only if at least `min_hours` distinct clock hours carry a valid observation. A shorter day is
     dropped and counted (`days_short`), never filled. The value is the mean of every valid observation that day, so a
     10-minute day and an hourly day are both means over the day, not over a fixed count.
  3. `n_hours` (distinct hours with data) is written beside the value, so a reader can see how full each day was.

**An absent year is a record, not a failure.** NDBC answers 404 for a station-year it does not hold (MLRF1 after 2019;
SMKF1 2016–17), and that is written into the summary under `per_station.<id>.years_absent`. Any other failure fails closed (the base
class retries, then raises), and a station with **no** year present in the span is refused: that is an id typo or a
retired station, and a silent empty column would read as calm. A cached 404 is a zero-byte file, so a re-run does not
re-ask. A fetch is pinned by its artifact, never by the raw cache.

**The stations come from the instance as well as the spec.** `bind(inst, sid)` takes the stream's `stations` map
(atlantis.yaml); a mapped station the spec does not fetch is refused before any request. The summary's `reduction`
block is computed by the download (C-023); a cached artifact whose recorded basis (stations · years · variable ·
min_hours) differs from the spec is refused by `fetch`, `fetch --verify` and conform item 3 (as `CoralReefWatch`).
"""
from __future__ import annotations

import gzip, io, json

import numpy as np
import pandas as pd

from atlantis_core.fetch import provenance
from atlantis_core.fetch.base import Fetcher

SENTINELS = (99.0, 999.0, 9999.0)
YEAR_COLS = ("YY", "YYYY")


def _absent(r) -> bool:
    return getattr(r, "status_code", 200) == 404


def parse_stdmet(raw: bytes, variable: str, where: str = "?") -> pd.DataFrame:
    """One yearly file's bytes (gzipped or plain) → columns `time` (UTC, naive) and `v` (the variable; sentinels NaN)."""
    try:
        text = gzip.decompress(raw).decode("ascii", "replace") if raw[:2] == b"\x1f\x8b" else raw.decode("ascii", "replace")
    except (OSError, EOFError) as e:
        raise ValueError(f"{where}: not a readable stdmet file ({e})") from None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError(f"{where}: empty stdmet file")
    cols = lines[0].lstrip("#").split()
    body = lines[1:]
    if body and body[0].lstrip().startswith("#"):          # the units line (2005 on)
        body = body[1:]
    ycol = next((c for c in YEAR_COLS if c in cols), None)
    missing = [c for c in (ycol, "MM", "DD", "hh", variable) if c is None or c not in cols]
    if missing:
        raise ValueError(f"{where}: header {cols[:8]}… lacks {missing}")
    df = pd.read_csv(io.StringIO("\n".join(body)), sep=r"\s+", header=None, names=cols, usecols=range(len(cols)),
                     dtype=str, engine="python")
    num = {c: pd.to_numeric(df[c], errors="coerce") for c in (ycol, "MM", "DD", "hh", variable)}
    yr = num[ycol]
    yr = yr.where(yr >= 100, yr + 1900)                     # two-digit years are the 19xx files (before 1999)
    mi = pd.to_numeric(df["mm"], errors="coerce") if "mm" in cols else pd.Series(0, index=df.index)
    t = pd.to_datetime({"year": yr, "month": num["MM"], "day": num["DD"], "hour": num["hh"], "minute": mi.fillna(0)},
                       errors="coerce")
    v = num[variable].astype(float)
    v = v.mask(v.isin(SENTINELS))
    out = pd.DataFrame({"time": t, "v": v}).dropna(subset=["time"])
    return out


class NDBCStdmet(Fetcher):
    protocol = "ndbc_stdmet"
    endpoint = "https://www.ndbc.noaa.gov/data/historical/stdmet/"
    spec_required = ("stations", "years", "variable")
    daily = True        # `fetch --verify` and the summary report the calendar days a station lacks (III F-2)
    columns: dict | None = None
    mapped: list | None = None

    def bind(self, inst, sid: str) -> None:
        s = inst.stream_spec(sid)
        self.columns = dict(s.get("columns") or {})
        self.mapped = sorted(map(str, (s.get("stations") or {})))
        self.date_col = self.columns.get("date", "date")
        self.reduction: dict = {}

    def unit_column(self, spec) -> str:
        return (self.columns or {}).get("station", "station")

    def value_name(self, spec) -> str:
        return spec.get("value_name") or (self.columns or {}).get("value") or str(spec["variable"]).lower()

    def basis(self, spec) -> dict:
        """What a reduction is computed over. A cached artifact is valid only for the same basis."""
        y0, y1 = (int(y) for y in spec["years"])
        return {"stations": sorted(map(str, spec["stations"])), "years": [y0, y1], "variable": str(spec["variable"]),
                "min_hours": int(spec.get("min_hours", 18))}

    def provenance_problem(self, spec) -> str | None:
        if not spec or not self.summary.exists() or not self.artifact.exists():
            return None
        red = json.loads(self.summary.read_text()).get("reduction")
        if not red:
            return (f"{self.artifact.name} has no recorded reduction (a cache hit without a summary) — "
                    f"delete it and re-fetch so the stations it was reduced over are on record")
        want = self.basis(spec)
        diff = {k: (red.get(k), v) for k, v in want.items() if red.get(k) != v}
        if diff:
            return (f"{self.artifact.name} was reduced over a different basis than the spec now names: "
                    + "; ".join(f"{k} {a!r} → {b!r}" for k, (a, b) in diff.items())
                    + " — delete the artifact (and its summary) and re-fetch")
        return None

    def fetch(self, spec: dict | None = None):
        p = self.provenance_problem(spec or {})
        if p:
            raise ValueError(p)
        return super().fetch(spec)

    def _year(self, station: str, year: int) -> bytes | None:
        """The station-year's raw bytes from the cache or the network; None if NDBC does not hold it (404)."""
        name = f"{station.lower()}h{year}.txt.gz"
        cache = self.cache_dir / self.artifact.stem / station.upper() / name
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not cache.exists():
            r = self.get(self.endpoint + name, empty_ok=_absent)
            data = b"" if _absent(r) else r.content
            tmp = cache.with_suffix(".tmp"); tmp.write_bytes(data); tmp.rename(cache)
        data = cache.read_bytes()
        return data or None

    def _download(self, spec):
        b = self.basis(spec)
        if self.mapped is not None:
            unfetched = sorted(set(self.mapped) - set(b["stations"]))
            if unfetched:
                raise ValueError(f"stations {unfetched} are mapped to units in atlantis.yaml but not in the fetch spec — "
                                 f"a mapped station with no data would read as an empty column")
        var, (y0, y1), min_h = b["variable"], b["years"], b["min_hours"]
        if y0 > y1:
            raise ValueError(f"fetch spec years {[y0, y1]}: first year after last")
        st_col, val = self.unit_column(spec), self.value_name(spec)
        frames, stations = [], {}
        for st in b["stations"]:
            present, absent, parts = [], [], []
            for y in range(y0, y1 + 1):
                raw = self._year(st, y)
                if raw is None:
                    absent.append(y); continue
                present.append(y)
                parts.append(parse_stdmet(raw, var, where=f"{st} {y}"))
            if not present:
                raise ValueError(f"station {st}: no stdmet year file in {y0}–{y1} (every year 404) — check the id; "
                                 f"a station with no data would read as an empty column")
            obs = pd.concat(parts, ignore_index=True)
            n_rows = len(obs)
            obs = obs.drop_duplicates(subset=["time"], keep="first")
            dup = n_rows - len(obs)
            obs = obs[(obs["time"].dt.year >= y0) & (obs["time"].dt.year <= y1)]
            ok = obs.dropna(subset=["v"])
            day = ok["time"].dt.normalize()
            g = ok.assign(day=day, hour=ok["time"].dt.floor("h")).groupby("day")
            daily = pd.DataFrame({"v": g["v"].mean(), "n_hours": g["hour"].nunique()})
            short = daily["n_hours"] < min_h
            kept = daily[~short]
            frames.append(pd.DataFrame({self.date_col: kept.index, st_col: st, val: kept["v"].to_numpy(),
                                        "n_hours": kept["n_hours"].to_numpy(dtype=int)}))
            stations[st] = {"years_present": present, "years_absent": absent, "n_obs_valid": int(len(ok)),
                            "n_obs_missing": int(obs["v"].isna().sum()), "duplicates": int(dup),
                            "days_kept": int(len(kept)), "days_short": int(short.sum()),
                            "first_day": str(kept.index.min().date()) if len(kept) else None,
                            "last_day": str(kept.index.max().date()) if len(kept) else None}
        self.reduction = {**b, "day_boundary": "UTC", "sentinels": list(SENTINELS), "per_station": stations}
        out = pd.concat(frames, ignore_index=True)
        out[self.date_col] = pd.to_datetime(out[self.date_col])
        return out.sort_values([st_col, self.date_col]).reset_index(drop=True)

    def extras(self, df) -> dict:
        done = {"completeness": provenance.daily_completeness(df, self.date_col, self.unit_column({}))}
        red = getattr(self, "reduction", None)
        if not red:
            return {"reduction": None, "reduction_note": "cache hit without a summary: the per-station reduction was not "
                                                         "recomputed here (re-fetch to record it)", **done}
        return {**done, "reduction": red,
                "reduction_rule": "per station and UTC day: the mean of valid observations, kept if ≥ min_hours distinct "
                                  "hours carry one; sentinels → NaN; duplicate timestamps across year files counted once"}

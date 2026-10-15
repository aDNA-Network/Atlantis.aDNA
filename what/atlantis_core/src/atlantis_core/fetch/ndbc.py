"""NOAA NDBC standard meteorological data (historical yearly files): one daily series per station, with QC flags.

BUILT at M-3b-ii-a (WI-19), for `FloridaKeysCoral.aDNA`'s reef-light wind (the C-MAN lights MLRF1 · SMKF1 · LONF1 ·
SANF1). Until then it was declared only (M-1b-i ruling). One file per station-year:

    https://www.ndbc.noaa.gov/data/historical/stdmet/<station>h<year>.txt.gz

**Four header forms** are in the record (III M-3b-ii-a F-7), all read by the header line's own column names:
  - before 1999: `YY MM DD hh WD WSPD …` (a two-digit year → 19xx, no minute column, hourly);
  - 1999–2004: `YYYY MM DD hh …` (2000–04 add `TIDE`; rows may carry fewer trailing fields than the header names);
  - 2005–2006: `YYYY MM DD hh mm …` (a minute column, no `#`, no units line);
  - from 2007: `#YY MM DD hh mm WDIR WSPD …` followed by a `#yr mo dy hr mn …` units line.
Hourly rows may be stamped at :49 · :50 · :55; from 2019 three of the Keys lights report 10-minute rows (`cadence`,
below, records it per station-year). Missing values are 99 · 999 · 9999 and become NaN. Times are UTC (checked at the
M-3b-ii-a review: the air-temperature maximum falls at 21–22 UTC in every era), so the day boundary is UTC midnight
(19:00 EST).

spec: {stations: [ids], years: [y0, y1], variable (a header column, e.g. WSPD), min_hours (default 18),
       value_name (default: the stream's `columns.value`, else the variable lower-cased),
       qc: {low_ratio (0.4), ratio_window_days (15), stuck_hours (6)}}

Reduction, per station and UTC day:
  0. Only the leading columns the read needs are parsed. A row too short to hold them, or whose timestamp (minute
     included) does not parse, is dropped and counted (`rows_malformed`); a repeated header or units line mid-file is
     counted apart (`header_lines`). Rows outside the requested years (a stray prior-year row) are dropped and counted.
  1. **Duplicate timestamps** (within a file or across adjacent year files): if every copy carries the same value, one is
     kept (`duplicates_identical`, rows removed). If the copies disagree, **none is kept** and the timestamps are counted
     (`duplicates_conflicting`, with their first and last) — no rule says which copy is the station's (SMKF1 2020 holds
     a second block that is LONF1's record; III F-2).
  2. A day keeps its value only if at least `min_hours` distinct clock hours carry a valid observation. A shorter day is
     dropped and counted (`days_short`), never filled. The value is the mean of every valid observation that day.
  3. `n_hours` (distinct hours with data) is written beside the value.

**QC flags (III F-1; operator ruling 8, M-3b-ii-a): no value is deleted, a flag is a column.**
  - `qc_low_ratio`: the station's daily value divided by the median of the OTHER stations reporting that day; the
    centred rolling median of that ratio over `ratio_window_days` is below `low_ratio`. A failed anemometer reads as calm
    (LONF1 2020-02-27…06-04 read 0.14–0.20 × the others). The window is CENTRED, so the flag is a retrospective cleaning
    rule that reads up to half a window ahead: a mask built from it is a ruling, not a vital, and the self-test does
    not see it.
  - `qc_stuck`: the day is touched by a run of identical consecutive valid observations spanning ≥ `stuck_hours`
    distinct hours (a stuck sensor; most runs are at 0.0).
  The summary counts flagged days per station and year. Which flags mask an index is the instance's ruling.

**An absent year is confirmed, recorded, and never inferred from an empty reply (III F-3).** NDBC answers 404 for a
station-year it does not hold (MLRF1 after 2019; SMKF1 2016–17). A 404 is asked once more after a backoff; two 404s are
written as `<file>.absent.json` (status, URL, time) and the year as absent. An empty 200 is a failure, not an absence. A
span that reaches the current UTC year is refused: NDBC publishes a yearly file only after the year ends, so this year's
404 would be recorded as permanent absence. A station with **no** year present is refused (an id typo or a retired
station would read as an empty column). Any other failure fails closed (the base class retries, then raises).

**The raw cache is pinned.** Each downloaded file gets a `<file>.json` sidecar (sha256 · bytes · fetched_at), and the
summary's `reduction.raw_files` records them. `fetch --verify` (through `provenance_problem`) re-hashes the raw cache
against that record when the cache is present. A summary written without any request says so: `fetched_at_source` is
"offline re-reduction of the raw cache" and the downloads' own times are in `raw_files`.

**The stations come from the instance as well as the spec.** `bind(inst, sid)` takes the stream's `stations` map
(atlantis.yaml); a mapped station the spec does not fetch is refused before any request, and so is a station listed
twice. The `reduction` block is computed by the download (C-023); a cached artifact whose recorded basis (stations ·
years · variable · min_hours · qc) differs from the spec is refused by `fetch`, `fetch --verify` and conform item 3.
"""
from __future__ import annotations

import gzip, json, time
from datetime import datetime, timezone

import pandas as pd

from atlantis_core.fetch import provenance
from atlantis_core.fetch.base import Fetcher

SENTINELS = (99.0, 999.0, 9999.0)
YEAR_COLS = ("YY", "YYYY")
QC_DEFAULTS = {"low_ratio": 0.4, "ratio_window_days": 15, "stuck_hours": 6}
REREDUCED = "offline re-reduction of the raw cache (downloads: reduction.raw_files)"


def _absent(r) -> bool:
    return getattr(r, "status_code", 200) == 404


def _is_header(line: str) -> bool:
    tok = line.lstrip("#").split()[:1]
    return line.lstrip().startswith("#") or (bool(tok) and tok[0] in YEAR_COLS)


def parse_stdmet(raw: bytes, variable: str, where: str = "?") -> pd.DataFrame:
    """One yearly file's bytes (gzipped or plain) → columns `time` (UTC, naive) and `v` (the variable; sentinels NaN).
    `attrs`: `malformed` (rows dropped: too short, or a timestamp that does not parse) · `header_lines` (repeated
    headers mid-file; the 2007-on units line is expected and not counted)."""
    try:
        text = gzip.decompress(raw).decode("ascii", "replace") if raw[:2] == b"\x1f\x8b" else raw.decode("ascii", "replace")
    except (OSError, EOFError) as e:
        raise ValueError(f"{where}: not a readable stdmet file ({e})") from None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError(f"{where}: empty stdmet file")
    cols = lines[0].lstrip("#").split()
    ycol = next((c for c in YEAR_COLS if c in cols), None)
    missing = [c for c in (ycol, "MM", "DD", "hh", variable) if c is None or c not in cols]
    if missing:
        raise ValueError(f"{where}: header {cols[:8]}… lacks {missing}")
    units_line = len(lines) > 1 and lines[1].lstrip().startswith("#")
    body = [ln for ln in lines[1:] if not _is_header(ln)]
    headers = len(lines) - 1 - len(body) - (1 if units_line else 0)
    # Only the leading columns this read needs are taken: NDBC rows can carry fewer trailing fields than the header names
    # (LONF1 2000: a 17-column header with `TIDE`, rows of 16 and 17). A row too short to hold them is dropped and counted.
    want = [c for c in (ycol, "MM", "DD", "hh", "mm", variable) if c in cols]
    need = max(cols.index(c) for c in want) + 1
    split = [ln.split() for ln in body]
    keep = [r[:need] for r in split if len(r) >= need]
    df = pd.DataFrame(keep, columns=cols[:need], dtype=str)
    num = {c: pd.to_numeric(df[c], errors="coerce") for c in (ycol, "MM", "DD", "hh", variable)}
    yr = num[ycol]
    yr = yr.where(yr >= 100, yr + 1900)                     # two-digit years are the 19xx files (before 1999)
    mi = pd.to_numeric(df["mm"], errors="coerce") if "mm" in cols else pd.Series(0, index=df.index)   # garbled → NaT
    t = pd.to_datetime({"year": yr, "month": num["MM"], "day": num["DD"], "hour": num["hh"], "minute": mi},
                       errors="coerce")
    v = num[variable].astype(float)
    v = v.mask(v.isin(SENTINELS))
    out = pd.DataFrame({"time": t, "v": v})
    bad_time = int(out["time"].isna().sum())
    out = out.dropna(subset=["time"])
    out.attrs["malformed"] = (len(split) - len(keep)) + bad_time   # short rows + rows whose timestamp does not parse
    out.attrs["header_lines"] = max(headers, 0)
    return out


def _dedup(obs: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Identical copies of a timestamp → one kept; disagreeing copies → none kept (III F-2)."""
    dmask = obs.duplicated("time", keep=False)
    if not dmask.any():
        return obs, {"duplicates_identical": 0, "duplicates_conflicting": 0}
    d = obs[dmask]
    nun = d.assign(k=d["v"].fillna(-1e9)).groupby("time")["k"].nunique()
    conflicting = nun.index[nun > 1]
    drop_conf = obs["time"].isin(conflicting)
    out = obs[~drop_conf].drop_duplicates(subset=["time"], keep="first")
    info = {"duplicates_identical": int(len(obs) - int(drop_conf.sum()) - len(out)),
            "duplicates_conflicting": int(len(conflicting))}
    if len(conflicting):
        info["conflicting_span"] = [str(conflicting.min()), str(conflicting.max())]
    return out, info


def _stuck_days(ok: pd.DataFrame, hours: int) -> pd.DatetimeIndex:
    """Days touched by a run of identical consecutive valid observations over ≥ `hours` distinct clock hours."""
    if ok.empty:
        return pd.DatetimeIndex([])
    s = ok.sort_values("time")
    run = (s["v"] != s["v"].shift()).cumsum()
    span = s.assign(h=s["time"].dt.floor("h")).groupby(run)["h"].nunique()
    long_runs = span.index[span >= hours]
    return pd.DatetimeIndex(s.loc[run.isin(long_runs), "time"].dt.normalize().unique())


class NDBCStdmet(Fetcher):
    FLAG_COLUMNS = ("qc_low_ratio", "qc_stuck")   # what a stream may name in `mask_columns` (registry R5)
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
        st = [str(x) for x in spec["stations"]]
        if len(set(st)) != len(st):
            raise ValueError(f"fetch spec stations {st}: a station is listed twice (its station-days would be duplicated)")
        y0, y1 = (int(y) for y in spec["years"])
        return {"stations": sorted(st), "years": [y0, y1], "variable": str(spec["variable"]),
                "min_hours": int(spec.get("min_hours", 18)), "qc": {**QC_DEFAULTS, **(spec.get("qc") or {})}}

    def _raw_problem(self, red: dict) -> str | None:
        """Re-hash the raw cache, where present, against the record the reduction was computed from (III F-3c)."""
        bad = []
        for st, years in (red.get("raw_files") or {}).items():
            for y, rec in years.items():
                f = self.cache_dir / self.artifact.stem / st / f"{st.lower()}h{y}.txt.gz"
                if f.exists() and provenance.sha256(f) != rec.get("sha256"):
                    bad.append(f"{st} {y}")
        return (f"the raw cache under {self.artifact.stem}/ changed since the reduction: {bad[:5]}"
                + (" …" if len(bad) > 5 else "") + " — delete the artifact and re-fetch") if bad else None

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
        return self._raw_problem(red)

    def fetch(self, spec: dict | None = None):
        p = self.provenance_problem(spec or {})
        if p:
            raise ValueError(p)
        return super().fetch(spec)

    def _year(self, station: str, year: int):
        """(raw bytes, file record) for a station-year from the cache or the network; (None, absence record) if NDBC
        confirms it does not hold it (two 404s)."""
        name = f"{station.lower()}h{year}.txt.gz"
        cache = self.cache_dir / self.artifact.stem / station.upper() / name
        side, absent = cache.with_name(name + ".json"), cache.with_name(name + ".absent.json")
        cache.parent.mkdir(parents=True, exist_ok=True)
        if absent.exists():
            return None, json.loads(absent.read_text())
        if cache.exists() and cache.stat().st_size == 0:
            cache.unlink()                                   # a 0.10.0 zero-byte "absent": re-confirmed, never trusted
        if cache.exists():
            data = cache.read_bytes()
            if not side.exists():                            # cached before 0.10.1: the download time was not recorded
                rec = {"sha256": provenance.sha256(cache), "bytes": len(data),
                       "fetched_at": datetime.fromtimestamp(cache.stat().st_mtime, tz=timezone.utc).isoformat(),
                       "fetched_at_source": "file mtime (cached before atlantis_core 0.10.1)"}
                side.write_text(json.dumps(rec, indent=1) + "\n")
            return data, json.loads(side.read_text())
        url = self.endpoint + name
        self.requests += 1
        r = self.get(url, empty_ok=_absent)
        if _absent(r):
            time.sleep(self.backoff)
            self.requests += 1
            r = self.get(url, empty_ok=_absent)
            if _absent(r):
                rec = {"status": 404, "url": url, "at": provenance.now_utc(), "confirmed_by": 2}
                tmp = absent.with_suffix(".tmp"); tmp.write_text(json.dumps(rec, indent=1) + "\n"); tmp.rename(absent)
                return None, rec
        data = getattr(r, "content", b"") or b""
        if not data:
            raise ValueError(f"{url}: HTTP {getattr(r, 'status_code', '?')} with an empty body — not taken as absent")
        tmp = cache.with_suffix(".tmp"); tmp.write_bytes(data); tmp.rename(cache)
        rec = {"sha256": provenance.sha256(cache), "bytes": len(data), "fetched_at": provenance.now_utc(),
               "fetched_at_source": "fetch"}
        side.write_text(json.dumps(rec, indent=1) + "\n")
        return data, rec

    def _download(self, spec):
        b = self.basis(spec)
        if self.mapped is not None:
            unfetched = sorted(set(self.mapped) - set(b["stations"]))
            if unfetched:
                raise ValueError(f"stations {unfetched} are mapped to units in atlantis.yaml but not in the fetch spec — "
                                 f"a mapped station with no data would read as an empty column")
        var, (y0, y1), min_h, qc = b["variable"], b["years"], b["min_hours"], b["qc"]
        if y0 > y1:
            raise ValueError(f"fetch spec years {[y0, y1]}: first year after last")
        this_year = datetime.now(timezone.utc).year
        if y1 >= this_year:
            raise ValueError(f"fetch spec years {[y0, y1]} reach {this_year}: NDBC publishes a yearly file only after the "
                             f"year ends, so this year's 404 would be recorded as permanent absence — end at {this_year - 1}")
        st_col, val = self.unit_column(spec), self.value_name(spec)
        self.requests = 0
        daily, stations, raw_files, ok_obs = {}, {}, {}, {}
        for st in b["stations"]:
            present, absent, parts, malformed, headers, cadence = [], {}, [], 0, 0, {}
            raw_files[st] = {}
            for y in range(y0, y1 + 1):
                raw, rec = self._year(st, y)
                if raw is None:
                    absent[str(y)] = rec.get("at"); continue
                present.append(y); raw_files[st][str(y)] = rec
                part = parse_stdmet(raw, var, where=f"{st} {y}")
                malformed += part.attrs.get("malformed", 0); headers += part.attrs.get("header_lines", 0)
                if len(part):
                    per_day = part.groupby(part["time"].dt.normalize()).size()
                    mins = sorted(int(m) for m in part["time"].dt.minute.unique())
                    cadence[str(y)] = {"rows_per_day_median": float(per_day.median()),
                                       "minutes": mins if len(mins) <= 12 else mins[:12] + ["…"]}
                parts.append(part)
            if not present:
                raise ValueError(f"station {st}: no stdmet year file in {y0}–{y1} (every year a confirmed 404) — check "
                                 f"the id; a station with no data would read as an empty column")
            obs = pd.concat(parts, ignore_index=True)
            in_span = obs["time"].dt.year.between(y0, y1)
            stray, obs = int((~in_span).sum()), obs[in_span]
            obs, dup = _dedup(obs)
            ok = obs.dropna(subset=["v"])
            ok_obs[st] = ok
            g = ok.assign(day=ok["time"].dt.normalize(), hour=ok["time"].dt.floor("h")).groupby("day")
            d = pd.DataFrame({"v": g["v"].mean(), "n_hours": g["hour"].nunique()})
            short = d["n_hours"] < min_h
            daily[st] = d[~short]
            stations[st] = {"years_present": present, "years_absent": sorted(int(y) for y in absent),
                            "absent_confirmed_at": absent, "n_obs_valid": int(len(ok)),
                            "n_obs_missing": int(obs["v"].isna().sum()), **dup, "rows_stray_year": stray,
                            "rows_malformed": int(malformed), "header_lines": int(headers),
                            "days_kept": int((~short).sum()), "days_short": int(short.sum()), "cadence": cadence}
        # QC flags (III F-1): computed across stations, once every station's days are known
        wide = pd.DataFrame({st: d["v"] for st, d in daily.items()})
        w = int(qc["ratio_window_days"])
        frames = []
        for st, d in daily.items():
            others = wide.drop(columns=[st]).median(axis=1)
            ratio = (wide[st] / others.where(others > 0)).rolling(w, center=True, min_periods=max(1, w // 2)).median()
            low = (ratio < float(qc["low_ratio"])).reindex(d.index, fill_value=False)
            stuck = pd.Series(d.index.isin(_stuck_days(ok_obs[st], int(qc["stuck_hours"]))), index=d.index)
            frames.append(pd.DataFrame({self.date_col: d.index, st_col: st, val: d["v"].to_numpy(),
                                        "n_hours": d["n_hours"].to_numpy(dtype=int),
                                        "qc_low_ratio": low.to_numpy(dtype=bool), "qc_stuck": stuck.to_numpy(dtype=bool)}))
            by_year = pd.DataFrame({"low": low, "stuck": stuck}).groupby(d.index.year).sum()
            stations[st]["days_flagged"] = {"qc_low_ratio": int(low.sum()), "qc_stuck": int(stuck.sum()),
                                            "either": int((low | stuck).sum())}
            stations[st]["days_flagged_by_year"] = {str(y): [int(r["low"]), int(r["stuck"])]
                                                    for y, r in by_year.iterrows() if r["low"] or r["stuck"]}
            stations[st]["first_day"] = str(d.index.min().date()) if len(d) else None
            stations[st]["last_day"] = str(d.index.max().date()) if len(d) else None
        self.fetched_at_source = "fetch" if self.requests else REREDUCED
        self.reduction = {**b, "day_boundary": "UTC", "sentinels": list(SENTINELS),
                          "qc_rule": "flags only, no value deleted: low_ratio = centred rolling median over "
                                     "ratio_window_days of (station / median of the other stations that day) < low_ratio; "
                                     "stuck = a run of identical valid observations over ≥ stuck_hours distinct hours",
                          "requests": int(self.requests), "per_station": stations, "raw_files": raw_files}
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
                                  "hours carry one; sentinels → NaN; identical duplicate timestamps kept once, "
                                  "conflicting ones dropped; QC flags as columns, no value deleted"}

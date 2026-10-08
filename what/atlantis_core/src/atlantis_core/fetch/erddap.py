"""ERDDAP griddap — box-mean daily series per unit (ported from the exemplar's `hab.fetch_env.fetch_sst`).

spec: {base (…/griddap/<dataset>.csv), variable, boxes: {unit: [lat0, lat1, lon0, lon1]}, years: [y0, y1],
       chunk_years (default 5) | chunk_months | chunk_days (M-2a-ii; name one), zlev (optional, e.g. 0.0), unit_column (default "unit"),
       start (optional ISO date in the first year: a dataset that begins mid-year; M-2a-ii)}
Each unit × chunk CSV is cached under `<cache>/<stem>/b<basis>/` before the merged artifact (date · unit · value). `<basis>` hashes
the base, variable, zlev and the unit's box (M-2a-ii III F-1): before it, a cache fetched from one dataset or box was read
back for another once the artifact was deleted. The summary's `completeness` block counts distinct days against the calendar
span (III F-2): a day the server never sent is not a null, and a null count cannot see it.

**Chunk size is bounded by the server, not by taste (M-2a-ii).** CRW's ERDDAP sits behind a proxy that answers 502 to any
request still running at ~10.3 s. A month of one zone took ~1 s there, a year > 10 s, and the 5-year default ~40 s, so a
probe-gated retry loop could never succeed: index.html answering 200 says nothing about a data request fitting. `chunk_months`
cuts the request to calendar months (aligned to January of the first year; the first is clamped by `start`). `chunk_days`
cuts it to consecutive N-day spans from the first day, across year ends, so extending `years` renames no cached span but the
last (the one the old end truncated).
A union-box month over the FKNMS zones took 4.3–11.5 s live, so the instance runs 15-day spans (steward ruling 15).
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.fetch import provenance
from atlantis_core.fetch.base import Fetcher


def basis_tag(*parts) -> str:
    """A short, stable hash of what a cached chunk was requested over: a different source never reads it back (III F-1)."""
    import hashlib, json
    return hashlib.sha256(json.dumps(parts, default=str).encode()).hexdigest()[:10]


def first_day(spec: dict, y0: int) -> str:
    """The first day a chunk asks for: 1 January, or `spec.start` in the spec's first year (M-2a-ii). ERDDAP refuses a time
    range that begins before the dataset's axis minimum with a 404 that is NOT "No data" (CRW's DHW begins 1985-03-25), so
    a dataset that starts mid-year names its first day rather than losing that year's chunk. Refused outside the first year."""
    start = spec.get("start")
    if start is None:
        return f"{y0}-01-01"
    import datetime as _dt
    try:
        d = _dt.date.fromisoformat(str(start))
    except ValueError:
        raise ValueError(f"fetch spec start {start!r}: an ISO date (YYYY-MM-DD)") from None
    if d.year != int(spec["years"][0]):
        raise ValueError(f"fetch spec start {start!r} must fall in the first year of years {spec['years']}")
    return str(d) if y0 == d.year else f"{y0}-01-01"


CHUNK_KEYS = ("chunk_years", "chunk_months", "chunk_days")


def chunks(spec: dict) -> list[tuple[str, str]]:
    """The (first_day, last_day) ISO pairs a fetch requests, in order. `chunk_years` (default 5): the pre-M-2a-ii behaviour,
    query strings and cache names unchanged. `chunk_months`: calendar months. `chunk_days`: N-day spans. More than one key,
    a bool, or a value < 1 is refused."""
    import datetime as _dt
    y_first, y_last = (int(y) for y in spec["years"])
    named = [k for k in CHUNK_KEYS if k in spec]
    if len(named) > 1:
        raise ValueError(f"fetch spec: {' and '.join(named)} are exclusive — name one")
    key = named[0] if named else "chunk_years"
    step = spec.get(key, 5)
    if isinstance(step, bool) or not isinstance(step, int) or step < 1:
        raise ValueError(f"fetch spec {key} {step!r}: an integer ≥ 1")
    if key == "chunk_years":
        return [(first_day(spec, y), f"{min(y + step - 1, y_last)}-12-31") for y in range(y_first, y_last + 1, step)]
    start, last, out = _dt.date.fromisoformat(first_day(spec, y_first)), _dt.date(y_last, 12, 31), []
    if key == "chunk_days":
        d = start
        while d <= last:
            e = min(d + _dt.timedelta(days=step - 1), last)
            out.append((str(d), str(e))); d = e + _dt.timedelta(days=1)
        return out
    y, m = y_first, 1
    while y <= y_last:
        ny, nm = y + (m - 1 + step) // 12, (m - 1 + step) % 12 + 1
        end = min(_dt.date(ny, nm, 1) - _dt.timedelta(days=1), last)
        if end >= start:
            out.append((str(max(_dt.date(y, m, 1), start)), str(end)))
        y, m = ny, nm
    return out


def chunk_label(spec: dict, d0: str, d1: str) -> str:
    """A chunk's cache-file stem: `<y0>_<y1>` for year chunks (unchanged names), else the dates. A year chunk that `start`
    moved names its first day (III F-6), so adding or changing `start` never reads a chunk fetched from another day."""
    if any(k in spec for k in CHUNK_KEYS[1:]):
        return f"{d0}_{d1}"
    return f"{d0[:4]}_{d1[:4]}" if d0.endswith("-01-01") else f"{d0}_{d1[:4]}"


def _empty(r) -> bool:   # ERDDAP answers an empty subset with 404 "No data"
    return r.status_code == 404 and "No data" in r.text


class ERDDAPGriddap(Fetcher):
    protocol = "erddap_griddap"
    spec_required = ("base", "variable", "boxes", "years")   # fork refuses a fetch spec without these (M-1d-i III F-8)
    endpoint = "https://<erddap>/erddap/griddap/<dataset>.csv"
    daily = True        # a daily product: `fetch --verify` and the summary report missing calendar days (III F-2)
    _unit_col = "unit"

    def unit_column(self, spec) -> str:
        return spec.get("unit_column", "unit")

    def extras(self, df) -> dict:
        col = self.unit_column({"unit_column": self._unit_col})
        return {"completeness": provenance.daily_completeness(df, self.date_col, col)}

    def query(self, spec, d0: str, d1: str, box) -> str:
        """One request: ISO first and last day (a pair from `chunks`), then the box."""
        la0, la1, lo0, lo1 = box
        z = f"[({spec['zlev']}):1:({spec['zlev']})]" if spec.get("zlev") is not None else ""
        return (f"{spec['variable']}[({d0}T12:00:00Z):1:({d1}T12:00:00Z)]{z}"
                f"[({la0}):1:({la1})][({lo0}):1:({lo1})]")

    def _download(self, spec):
        var, frames = spec["variable"], []
        self._unit_col = self.unit_column(spec)
        for unit, box in spec["boxes"].items():
            tag = basis_tag(spec["base"], var, spec.get("zlev"), [float(x) for x in box])
            for d0, d1 in chunks(spec):
                cache = self.cache_dir / self.artifact.stem / f"b{tag}" / f"u{unit}_{chunk_label(spec, d0, d1)}.csv"
                cache.parent.mkdir(parents=True, exist_ok=True)
                if not cache.exists():
                    r = self.get(spec["base"] + "?" + self.query(spec, d0, d1, box), empty_ok=_empty)
                    txt = "" if _empty(r) else r.text
                    tmp = cache.with_suffix(".tmp"); tmp.write_text(txt); tmp.rename(cache)
                if cache.stat().st_size == 0:
                    continue
                df = pd.read_csv(cache, skiprows=[1])
                if df.empty:
                    continue
                df = df.dropna(subset=[var])
                df["date"] = pd.to_datetime(df["time"]).dt.tz_convert(None).dt.normalize()
                d = df.groupby("date")[var].mean().rename(var).reset_index()
                d[spec.get("unit_column", "unit")] = unit
                frames.append(d)
        return pd.concat(frames, ignore_index=True)

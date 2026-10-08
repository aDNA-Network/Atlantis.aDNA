"""NOAA Coral Reef Watch, daily 5 km v3.1 (DHW · HotSpot · SST · SST anomaly): one zone-mean series per polygon unit.

BUILT at M-2a-i, for `FloridaKeysCoral.aDNA` (P2). Until then it was declared only, at the PFEG mirror `NOAA_DHW`, which
timed out when it was probed on 2026-10-06. CRW's own ERDDAP serves one dataset per product:

    https://coastwatch.noaa.gov/erddap/griddap/<dataset>.csv
    noaacrwdhwDaily        degree_heating_week               (degree_Celsius_weeks)
    noaacrwhotspotDaily    hotspot                           (degree_Celsius)
    noaacrwsstDaily        analysed_sst                      (degree_Celsius)
    noaacrwsstanomalyDaily sea_surface_temperature_anomaly   (degree_Celsius)

Latitude is stored descending. The ascending `[(lat0):1:(lat1)]` query that `ERDDAPGriddap` writes is answered, which was
checked live at planning. The licence reads "available for use without restriction; credit NOAA CRW and the dataset DOI".
The instance's posture ADR rules on it, including any upstream era caveat (CoralTemp's 1985–2002 OSTIA input).

spec: {base (…/griddap/<dataset>.csv), variable, years: [y0, y1], chunk_years (default 5) | chunk_months | chunk_days (erddap.chunks),
       pad_deg (default 0.05), start (optional; noaacrwdhwDaily begins 1985-03-25 — see erddap.first_day),
       envelope: zone (default) | union (M-2a-ii)}

**`envelope: union` (M-2a-ii, steward ruling 14).** CRW's proxy cuts every request at ~10.3 s (erddap module note), so a
long record is fetched in short chunks (15-day spans for FKNMS, ruling 15), and per zone that is one request per zone per span. `union` asks once per chunk for the
union of every zone's padded envelope, then gives each zone the cells ERDDAP would have returned for its own envelope:
each bound snapped to the NEAREST grid centre on its axis (`snap`, ERDDAP griddap's rule for an off-grid bound). Everything
after that (step 2 onward) is the same code. So `union` changes the request count, never the reduction. The summary's
`request` block says which was used. A union box takes in land and open water between zones, which is cheap at 5 km.

**The patients come from the instance, not from the spec.** `bind(inst, sid)` takes the instance's polygon grid through
`make_grid`, so the zone file's sha256 pin is checked before any request. It also takes the stream's own column names.

Reduction, per zone (per feature: a cell may count for two overlapping zones, and that is recorded, not hidden):
  1. Download the zone's envelope, padded by `pad_deg` (one cell), per chunk (or the union of them; below); cached.
  2. Keep the cells whose **centre** lies inside the zone's polygon (even-odd, holes honoured), among cells with any data.
  3. If none qualifies (a zone smaller than a 5 km cell, or all land-masked), **fall back** to the one data cell nearest
     the zone's vertex mean, with longitude scaled by cos(latitude).
  4. Take the daily mean over the kept cells. NaN, CRW's land, ice and missing fill, is dropped before the mean.

The fetch summary's `reduction` block records what the reduction was computed over: the zone file's `grid_sha256`,
`pad_deg`, `variable` and `base`. Under `zones` it records, per zone, `n_cells`, `fallback`, `cells_in_envelope` and
`shared_cells` (cells also kept by another zone). These values are **computed by this download** (C-023). A cache hit
whose summary is missing says that the reduction was not recomputed, instead of inventing one.

**Stale data is refused (M-2a-i III F-1).** The CSV cache is keyed by the grid pin, pad, variable and base (the base, with
any zlev, since M-2a-ii III F-1: it had been left out, so a new base after a deleted artifact read the old source's cells
and stamped the new base on them), so a re-pinned zone file or a new source never reads old cells. A cached artifact whose recorded reduction was computed over a different
zone file, pad, variable or base is refused by `fetch`, by `fetch --verify` and so by conform item 3 at the fetched stage.
The message names the mismatch, and the remedy is to delete the artifact and re-fetch. Zone ids must be unique (III F-2):
`PolygonGrid` refuses a duplicate, so dissolve a multi-part zone into one MultiPolygon feature first.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from atlantis_core.fetch.erddap import CHUNK_KEYS, ERDDAPGriddap, _empty, basis_tag, chunk_label, chunks
from atlantis_core.grid.polygons import PolygonGrid, geometry_contains


def _rings(geom: dict) -> list:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    raise ValueError(f"unsupported geometry type {geom['type']!r}")


def envelope(geom: dict, pad: float) -> list[float]:
    """[lat0, lat1, lon0, lon1] of every exterior ring, padded."""
    pts = np.concatenate([np.asarray(r, dtype=float) for r in _rings(geom)])
    return [float(pts[:, 1].min() - pad), float(pts[:, 1].max() + pad), float(pts[:, 0].min() - pad), float(pts[:, 0].max() + pad)]


def vertex_mean(geom: dict) -> tuple[float, float]:
    pts = np.concatenate([np.asarray(r, dtype=float) for r in _rings(geom)])
    return float(pts[:, 1].mean()), float(pts[:, 0].mean())


def snap(axis, lo: float, hi: float) -> np.ndarray:
    """Boolean mask over a sorted `axis` of grid centres: the run between the centres NEAREST `lo` and `hi`, inclusive.
    For bounds inside the axis this is what ERDDAP's griddap returns for an off-grid `[(lo):1:(hi)]`; a bound outside it is
    clamped here, where ERDDAP refuses it with a 404 (III F-8), which is harmless because every zone box lies inside the
    union box. On an exact tie the lower centre is taken. A bound on a cell EDGE is such a tie, and FKNMS zones 20 and 21
    sit within ~4e-6° of one (their vertices lie on the 0.05° lattice), so ERDDAP's side is reprojection noise. Either side
    keeps the same cells: an edge cell's centre lies at least half a cell outside the polygon. Only `cells_in_envelope`
    can move (III F-5; tested). The live parity check at M-2a-ii compared `snap` with a real per-zone request."""
    a = np.asarray(axis, dtype=float)
    i0, i1 = int(np.abs(a - lo).argmin()), int(np.abs(a - hi).argmin())
    i0, i1 = min(i0, i1), max(i0, i1)
    m = np.zeros(len(a), dtype=bool); m[i0:i1 + 1] = True
    return m


def union_box(boxes) -> list[float]:
    boxes = list(boxes)
    return [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes)]


def in_box(raw: pd.DataFrame, box) -> pd.DataFrame:
    """The rows of a union download that a request for `box` alone would have returned (nearest-centre snap per axis)."""
    lats, lons = np.sort(raw["latitude"].unique()), np.sort(raw["longitude"].unique())
    keep_la, keep_lo = lats[snap(lats, box[0], box[1])], lons[snap(lons, box[2], box[3])]
    return raw[raw["latitude"].isin(keep_la) & raw["longitude"].isin(keep_lo)]


def select_cells(geom: dict, cells: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """The cells (lat, lon) that represent a zone: centres inside it; else the single nearest one (fallback=True)."""
    if cells.empty:
        raise ValueError("no CRW cell with data in the zone's padded envelope — widen pad_deg, or the zone is all land")
    inside = geometry_contains(geom, cells["latitude"].to_numpy(), cells["longitude"].to_numpy())
    if inside.any():
        return cells[inside], False
    clat, clon = vertex_mean(geom)
    d2 = (cells["latitude"] - clat) ** 2 + ((cells["longitude"] - clon) * np.cos(np.radians(clat))) ** 2
    return cells.loc[[d2.idxmin()]], True


class CoralReefWatch(ERDDAPGriddap):
    protocol = "noaa_crw"
    spec_required = ("base", "variable", "years")   # the polygons come from the instance's pinned grid, not the spec
    endpoint = "https://coastwatch.noaa.gov/erddap/griddap/noaacrwdhwDaily.csv"

    grid: PolygonGrid | None = None
    columns: dict | None = None

    def bind(self, inst, sid: str) -> None:
        from atlantis_core.grid import make_grid
        g = make_grid(inst)                                    # checks grid.sha256: no request for an unpinned zone file
        if not isinstance(g, PolygonGrid):
            raise ValueError(f"{sid}: CoralReefWatch reduces over polygon zones; atlantis.yaml → grid.kind is "
                             f"{inst.cfg['grid']['kind']!r}")
        self.grid, self.columns = g, dict(inst.stream_spec(sid)["columns"])
        self.grid_sha256 = str(inst.cfg["grid"]["sha256"])           # make_grid has just checked the bytes against it
        self.date_col, self._unit_col = self.columns["date"], self.columns["unit"]
        self.reduction: dict = {}

    def unit_column(self, spec) -> str:
        return self.columns["unit"] if self.columns else super().unit_column(spec)

    def basis(self, spec) -> dict:
        """What a reduction is computed over. A cached artifact is valid only for the same basis."""
        return {"grid_sha256": self.grid_sha256, "pad_deg": float(spec.get("pad_deg", 0.05)),
                "variable": spec["variable"], "base": spec["base"]}

    def provenance_problem(self, spec) -> str | None:
        import json
        if not (self.artifact.exists() and self.summary.exists()):
            return None
        red = json.loads(self.summary.read_text()).get("reduction")
        if not red:
            return (f"{self.artifact.name}: its summary records no reduction (a cache hit summarised without a download) — "
                    f"delete it and re-fetch so the zones it was reduced over are on record")
        want = self.basis(spec)
        diff = {k: (red.get(k), v) for k, v in want.items() if red.get(k) != v}
        if diff:
            return (f"{self.artifact.name} was reduced over a different basis than the instance now pins: "
                    + "; ".join(f"{k} {str(a)[:16]!r} → {str(b)[:16]!r}" for k, (a, b) in diff.items())
                    + " — delete the artifact (and its summary) and re-fetch")
        return None

    def fetch(self, spec: dict | None = None):
        p = self.provenance_problem(spec or {}) if self.grid is not None else None
        if p:
            raise ValueError(p)
        return super().fetch(spec)

    def _chunk(self, spec, key, name, d0, d1, box) -> pd.DataFrame | None:
        cache = self.cache_dir / self.artifact.stem / key / f"{name}_{chunk_label(spec, d0, d1)}.csv"
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not cache.exists():
            r = self.get(spec["base"] + "?" + self.query(spec, d0, d1, box), empty_ok=_empty)
            txt = "" if _empty(r) else r.text
            tmp = cache.with_suffix(".tmp"); tmp.write_text(txt); tmp.rename(cache)
        return pd.read_csv(cache, skiprows=[1]) if cache.stat().st_size else None

    def _download(self, spec):
        if self.grid is None:
            raise ValueError("CoralReefWatch needs the instance's polygon grid: build it with fetch.fetcher_for (bind)")
        mode = spec.get("envelope", "zone")
        if mode not in ("zone", "union"):
            raise ValueError(f"fetch spec envelope {mode!r}: zone | union")
        pad, spans = float(spec.get("pad_deg", 0.05)), chunks(spec)
        var, frames, kept = spec["variable"], [], {}
        b = self.basis(spec)
        key = (f"g{b['grid_sha256'][:12]}_p{b['pad_deg']}_{var}"        # III F-1: a re-pin, a new pad, variable or base
               f"_b{basis_tag(b['base'], spec.get('zlev'))}")             # never reads old cells (base: M-2a-ii III F-1)
        empty = pd.DataFrame(columns=["time", "latitude", "longitude", var])
        boxes = {uid: envelope(geom, pad) for uid, _name, geom in self.grid.units}
        if mode == "union":
            ub = union_box(boxes.values())
            parts = [p for d0, d1 in spans if (p := self._chunk(spec, key, "union", d0, d1, ub)) is not None]
            union_raw = pd.concat(parts, ignore_index=True) if parts else empty
        zones = {}
        for uid, _name, geom in self.grid.units:
            if mode == "union":
                raw = in_box(union_raw, boxes[uid]) if len(union_raw) else empty
            else:
                parts = [p for d0, d1 in spans if (p := self._chunk(spec, key, f"u{uid}", d0, d1, boxes[uid])) is not None]
                raw = pd.concat(parts, ignore_index=True) if parts else empty
            data = raw.dropna(subset=[var])
            cells = data[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
            sel, fb = select_cells(geom, cells)
            kept[uid] = set(map(tuple, sel[["latitude", "longitude"]].to_numpy()))
            d = data.merge(sel, on=["latitude", "longitude"])
            d = d.assign(date=pd.to_datetime(d["time"]).dt.tz_convert(None).dt.normalize())
            out = d.groupby("date")[var].mean().rename(self.columns["value"]).reset_index()
            out = out.rename(columns={"date": self.columns["date"]})
            out[self.columns["unit"]] = uid
            frames.append(out)
            zones[str(uid)] = {"n_cells": len(sel), "fallback": fb,
                               "cells_in_envelope": int(len(raw[["latitude", "longitude"]].drop_duplicates()))}
        for uid, cells_kept in kept.items():
            others = set().union(*(k for u, k in kept.items() if u != uid)) if len(kept) > 1 else set()
            zones[str(uid)]["shared_cells"] = len(cells_kept & others)
        self.reduction = {**b, "zones": zones}
        self.request = {"envelope": mode, "chunk": {k: spec[k] for k in CHUNK_KEYS if k in spec}
                        or {"chunk_years": 5}, "n_chunks": len(spans)}
        return pd.concat(frames, ignore_index=True)

    def extras(self, df) -> dict:
        red, done = getattr(self, "reduction", None), super().extras(df)
        if not red:
            return {"reduction": None, "reduction_note": "cache hit without a summary: the per-zone reduction was not "
                                                         "recomputed here (re-fetch to record it)", **done}
        return {**done, "reduction": red, "reduction_rule": "cell centre in polygon, per feature; else the nearest data cell to "
                                                    "the zone's vertex mean (cos-lat scaled)",
                "request": getattr(self, "request", None)}

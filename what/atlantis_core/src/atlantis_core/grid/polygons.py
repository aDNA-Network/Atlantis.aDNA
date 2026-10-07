"""Patient units from polygon files — GeoJSON (incl. a WDPA export) that the *instance* points at.

Atlantis never holds a polygon (ADR-002 §4): `grid.path` is resolved inside the instance, and its bytes are pinned by
`grid.sha256` in `atlantis.yaml`. `fork` writes the pin, `make_grid` and `conform` item 1 refuse a missing or mismatched
pin, and because the pin sits in the `grid` section it is inside `semantic_hash`, so a new zone file invalidates the
self-test receipt. (M-2a-i: until then this docstring claimed a pin no code made, the C-023 class.) Point-in-polygon is even-odd ray casting in numpy, holes honoured, MultiPolygon supported;
no shapely. First feature that contains a point wins (declare overlapping zones in priority order). Points exactly on
an edge are not guaranteed either way — snap or buffer upstream if that matters for an instance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np


class GridPinError(ValueError):
    """The polygon file is not the one `grid.sha256` pins (or there is no pin)."""


def file_sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_pin(path, sha256) -> None:
    """Refuse a polygon file whose bytes are not the pinned ones. A missing pin is a refusal too, not a pass."""
    if not sha256:
        raise GridPinError(f"grid.sha256 missing: the polygon file {Path(path).name} is unpinned (re-fork, or pin it "
                           f"with its sha256 in atlantis.yaml → grid)")
    got = file_sha256(path)
    if got != str(sha256):
        raise GridPinError(f"grid.sha256 mismatch: {Path(path).name} is {got[:12]}…, atlantis.yaml pins {str(sha256)[:12]}… "
                           f"— the zone file changed; re-pin deliberately and re-run the self-test")


def _ring_contains(ring: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Even-odd rule for one closed or open ring of (lon, lat) vertices."""
    inside = np.zeros(len(x), dtype=bool)
    xs, ys = ring[:, 0], ring[:, 1]
    xj, yj = np.roll(xs, 1), np.roll(ys, 1)
    for xi_, yi_, xj_, yj_ in zip(xs, ys, xj, yj):
        crosses = (yi_ > y) != (yj_ > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (xj_ - xi_) * (y - yi_) / (yj_ - yi_) + xi_
        inside ^= crosses & (x < xint)
    return inside


def _polygon_contains(rings: list, x, y) -> np.ndarray:
    shell = _ring_contains(np.asarray(rings[0], dtype=float), x, y)
    for hole in rings[1:]:
        shell &= ~_ring_contains(np.asarray(hole, dtype=float), x, y)
    return shell


def geometry_contains(geom: dict, lat, lon) -> np.ndarray:
    x, y = np.asarray(lon, dtype=float), np.asarray(lat, dtype=float)
    if geom["type"] == "Polygon":
        return _polygon_contains(geom["coordinates"], x, y)
    if geom["type"] == "MultiPolygon":
        out = np.zeros(len(x), dtype=bool)
        for poly in geom["coordinates"]:
            out |= _polygon_contains(poly, x, y)
        return out
    raise ValueError(f"unsupported geometry type {geom['type']!r} (Polygon / MultiPolygon only)")


class PolygonGrid:
    """`features`: GeoJSON features; `id_property`: the property holding the unit id (e.g. WDPAID)."""

    def __init__(self, features: list[dict], id_property: str, name_property: str | None = None):
        ids = [f["properties"][id_property] for f in features]
        dups = sorted({str(i) for i in ids if ids.count(i) > 1})
        if dups:   # M-2a-i III F-2: a per-zone cache, record or row keyed by a repeated id collides silently
            raise ValueError(f"duplicate {id_property} {dups} in the zone file — one feature per unit: dissolve a "
                             f"multi-part zone into one MultiPolygon first")
        self.units = []
        for f in features:
            uid = f["properties"][id_property]
            name = f["properties"].get(name_property, str(uid)) if name_property else str(uid)
            self.units.append((uid, name, f["geometry"]))

    @classmethod
    def from_file(cls, path: Path, id_property: str, name_property: str | None = None, sha256: str | None = None,
                  pinned: bool = True):
        if pinned:
            check_pin(path, sha256)
        gj = json.loads(Path(path).read_bytes())
        feats = gj["features"] if gj.get("type") == "FeatureCollection" else [gj]
        return cls(feats, id_property, name_property)

    def names(self) -> dict:
        return {uid: name for uid, name, _ in self.units}

    def assign(self, lat, lon) -> np.ndarray:
        lat = np.asarray(lat, dtype=float)
        out = np.full(len(lat), np.nan, dtype=object)
        unassigned = np.ones(len(lat), dtype=bool)
        for uid, _name, geom in self.units:
            hit = geometry_contains(geom, lat, lon) & unassigned
            out[hit] = uid
            unassigned &= ~hit
            if not unassigned.any(): break
        return out

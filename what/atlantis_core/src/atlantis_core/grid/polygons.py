"""Patient units from polygon files — GeoJSON (incl. a WDPA export) that the *instance* points at.

Atlantis never holds a polygon (ADR-002 §4): `grid.polygons.path` is resolved inside the instance, and the file is
pinned there by sha256. Point-in-polygon is even-odd ray casting in numpy, holes honoured, MultiPolygon supported;
no shapely. First feature that contains a point wins (declare overlapping zones in priority order). Points exactly on
an edge are not guaranteed either way — snap or buffer upstream if that matters for an instance.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np


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
        self.units = []
        for f in features:
            uid = f["properties"][id_property]
            name = f["properties"].get(name_property, str(uid)) if name_property else str(uid)
            self.units.append((uid, name, f["geometry"]))

    @classmethod
    def from_file(cls, path: Path, id_property: str, name_property: str | None = None):
        gj = json.loads(Path(path).read_text())
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

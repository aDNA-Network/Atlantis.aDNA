"""fetch.CoralReefWatch (M-2a-i): polygon-zone means over CRW's ERDDAP. Offline: a fake ERDDAP answers every query from a
synthetic 0.05° grid of cell CENTRES (x.x25 / x.x75, as CRW's are) whose value is a known function of position, so every
zone mean has an expected value computed here, independently of the fetcher's mask. No network, ever."""
import json, re, shutil
from urllib.parse import unquote

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.fetch import CoralReefWatch, OfflineError
from atlantis_core.fetch import crw as crw_mod
from atlantis_core.fetch.__main__ import fetcher_for
from atlantis_core.grid import GridPinError
from atlantis_core.grid.polygons import PolygonGrid

LAND = (35.025, -76.475)          # one land-masked cell: NaN every day
DAYS = ["2020-07-01T12:00:00Z", "2020-07-02T12:00:00Z"]


def value(lat, lon, day):
    """Non-linear on purpose: with a linear field a symmetric padding has the polygon's own mean, and a mask that keeps the
    whole envelope would pass the check unseen (found writing this test)."""
    return round(100 * (lat - 34) ** 2 + (lon + 77) ** 3 + day, 6)


class FakeERDDAP:
    """Answers `<base>?var[(t0):1:(t1)][(lat0):1:(lat1)][(lon0):1:(lon1)]` with the cell centres inside the box."""
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        var, la0, la1, lo0, lo1 = re.match(r".*\?(\w+)\[.*?\]\[\((.*?)\):1:\((.*?)\)\]\[\((.*?)\):1:\((.*?)\)\]", unquote(url)).groups()
        la0, la1, lo0, lo1 = map(float, (la0, la1, lo0, lo1))
        lats = [c for c in np.round(np.arange(34.025, 36.0, 0.05), 3) if la0 <= c <= la1]
        lons = [c for c in np.round(np.arange(-77.975, -75.0, 0.05), 3) if lo0 <= c <= lo1]
        rows = ["time,latitude,longitude," + var, "UTC,degrees_north,degrees_east,x"]
        for di, day in enumerate(DAYS):
            for la in lats:
                for lo in lons:
                    v = "NaN" if (la, lo) == LAND else value(la, lo, di)
                    rows.append(f"{day},{la},{lo},{v}")
        r = type("R", (), {})()
        r.status_code, r.text = 200, "\n".join(rows) + "\n"
        r.raise_for_status = lambda: None
        return r


def square(uid, lat0, lat1, lon0, lon1):
    return {"type": "Feature", "properties": {"seg": uid},
            "geometry": {"type": "Polygon", "coordinates": [[[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]]}}


SPEC = {"base": "https://coastwatch.noaa.gov/erddap/griddap/noaacrwdhwDaily.csv", "variable": "degree_heating_week", "years": [2020, 2020]}
COLS = {"date": "date", "value": "dhw", "unit": "seg"}


def crw(tmp_path, features, session=None, offline=False):
    f = CoralReefWatch(tmp_path, "dhw.parquet", "dhw_fetch_summary.json", offline=offline, session=session or FakeERDDAP())
    f.grid, f.columns, f.date_col, f.reduction = PolygonGrid(features, "seg"), dict(COLS), "date", {}
    return f


def expected(feature, day: int) -> tuple[float, int]:
    """Independent of the fetcher: the mean over grid centres strictly inside an axis-aligned square, land excluded."""
    (lon0, lat0), _, (lon1, lat1) = feature["geometry"]["coordinates"][0][:3]
    cells = [(la, lo) for la in np.round(np.arange(34.025, 36.0, 0.05), 3) for lo in np.round(np.arange(-77.975, -75.0, 0.05), 3)
             if lat0 < la < lat1 and lon0 < lo < lon1 and (la, lo) != LAND]
    return float(np.mean([value(la, lo, day) for la, lo in cells])), len(cells)


def zone_problems(df, features) -> list[str]:
    out = []
    for feat in features:
        uid = feat["properties"]["seg"]
        got = df[df["seg"] == uid].sort_values("date")["dhw"].to_numpy()
        want = [expected(feat, d)[0] for d in range(len(DAYS))]
        if len(got) != len(want) or not np.allclose(got, want, atol=1e-9):
            out.append(f"zone {uid}: {got} ≠ {want}")
    return out


SEG1 = square(1, 35.2, 35.5, -76.6, -76.2)     # the forked worlds' zones (conftest GEOJSON)
SEG2 = square(2, 34.9, 35.2, -76.6, -76.2)     # holds the land cell


def test_zone_means_are_the_cells_inside_each_polygon(tmp_path):
    f = crw(tmp_path, [SEG1, SEG2])
    df = f.fetch(SPEC)
    assert list(df.columns) == ["date", "dhw", "seg"]
    assert zone_problems(df, [SEG1, SEG2]) == []
    assert f.reduction["1"] == {"n_cells": expected(SEG1, 0)[1], "fallback": False, "cells_in_envelope": 8 * 10, "shared_cells": 0}
    # envelope 35.15–35.55 × −76.65–−76.15 → 8 latitude × 10 longitude centres
    assert f.reduction["2"]["n_cells"] == expected(SEG2, 0)[1]          # the land cell is not counted
    s = json.loads((tmp_path / "dhw_fetch_summary.json").read_text())
    assert s["reduction"] == f.reduction and s["rows"] == 4 and "cell centre in polygon" in s["reduction_rule"]


def test_plant_an_envelope_mask_is_caught(tmp_path, monkeypatch):
    """C-009: the check above must fail if the mask keeps out-of-polygon cells (here: the whole padded envelope)."""
    monkeypatch.setattr(crw_mod, "geometry_contains", lambda geom, lat, lon: np.ones(len(lat), dtype=bool))
    df = crw(tmp_path, [SEG1, SEG2]).fetch(SPEC)
    assert zone_problems(df, [SEG1, SEG2])


def test_sub_cell_zone_falls_back_to_the_nearest_cell_and_says_so(tmp_path):
    tiny = square(9, 35.31, 35.32, -76.42, -76.41)   # between centres: no centre inside
    f = crw(tmp_path, [tiny])
    df = f.fetch(SPEC)
    assert f.reduction["9"]["fallback"] is True and f.reduction["9"]["n_cells"] == 1
    assert df["dhw"].tolist() == [value(35.325, -76.425, 0), value(35.325, -76.425, 1)]   # the nearest centre


def test_overlapping_zones_share_cells_and_say_so(tmp_path):
    a, b = square(1, 35.2, 35.5, -76.6, -76.2), square(2, 35.3, 35.6, -76.4, -76.0)
    f = crw(tmp_path, [a, b])
    f.fetch(SPEC)
    assert f.reduction["1"]["shared_cells"] == f.reduction["2"]["shared_cells"] > 0


def test_cache_hit_without_summary_does_not_invent_a_reduction(tmp_path):
    crw(tmp_path, [SEG1]).fetch(SPEC)
    (tmp_path / "dhw_fetch_summary.json").unlink()
    f2 = crw(tmp_path, [SEG1], offline=True)
    f2.fetch(SPEC)
    s = json.loads((tmp_path / "dhw_fetch_summary.json").read_text())
    assert s["reduction"] is None and "not recomputed" in s["reduction_note"]


def test_offline_never_touches_network(tmp_path):
    class Boom:
        def get(self, *a, **k): raise AssertionError("network touched")
    with pytest.raises(OfflineError):
        crw(tmp_path, [SEG1], session=Boom(), offline=True).fetch(SPEC)


def test_unbound_refuses(tmp_path):
    f = CoralReefWatch(tmp_path, "dhw.parquet", "s.json", session=FakeERDDAP())
    with pytest.raises(ValueError, match="needs the instance's polygon grid"):
        f.fetch(SPEC)


def test_fetcher_for_binds_the_pinned_grid_and_the_streams_columns(persistent_master, tmp_path):
    d = tmp_path / "inst"; shutil.copytree(persistent_master, d)
    inst = load_instance(d)
    sess = FakeERDDAP()
    f = fetcher_for(inst, "atl_stream_example_dhw_daily", session=sess)
    df = f.fetch(inst.stream_spec("atl_stream_example_dhw_daily")["fetch"] | {"years": [2020, 2020]})
    assert list(df.columns) == ["date", "dhw", "seg"] and sorted(df["seg"].unique()) == [1, 2]
    assert sess.calls and all(c.startswith("https://coastwatch.noaa.gov/erddap/griddap/noaacrwdhwDaily.csv?degree_heating_week[")
                              for c in sess.calls)
    g = d / inst.cfg["grid"]["path"]                                 # one moved vertex: refused before any request
    g.write_text(g.read_text().replace("-76.2, 35.5", "-76.2, 35.51", 1))
    silent = FakeERDDAP()
    with pytest.raises(GridPinError, match="grid.sha256 mismatch"):
        fetcher_for(load_instance(d), "atl_stream_example_dhw_daily", session=silent)
    assert silent.calls == []

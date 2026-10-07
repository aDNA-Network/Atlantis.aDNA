"""grid: rules (ported whitelist + the 9 frozen exemplar counts), polygons, cells."""
import json
import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.grid import RuleGrid, RuleError, PolygonGrid, CellGrid, GridPinError, file_sha256, make_grid, week_start
from atlantis_core.grid.rules import parse_rule

# frozen at M-1a from hab.regions on the committed FWC parquet (exemplar tests/test_regions.py)
FROZEN = {1: 15992, 2: 6341, 3: 2686, 4: 32893, 5: 56108, 6: 20190, 7: 30563, 8: 12833, 9: 18418}


@pytest.mark.parametrize("bad", ["__import__('os')", "lat.real > 1", "lat >= 'x'", "depth > 3", "lat + 1 > 2",
                                 "(lambda: 1)()", "lat in [1, 2]", "lat >= 1j", "not lat"])
def test_rule_whitelist_rejects(bad):
    with pytest.raises(RuleError):
        parse_rule(bad)


def test_rule_first_match_wins():
    g = RuleGrid([{"id": 1, "rule": "lat >= 10"}, {"id": 2, "rule": "lat >= 0"}, {"id": 3, "rule": "True"}])
    assert g.assign([11, 5, -1], [0, 0, 0]).tolist() == [1, 2, 3]


def test_rule_no_match_is_nan():
    assert np.isnan(RuleGrid([{"id": 1, "rule": "lat > 100"}]).assign([0], [0])[0])


def test_exemplar_frozen_counts(exemplar_dir):
    inst = load_instance(exemplar_dir)
    s = pd.read_parquet(exemplar_dir / "data/raw/fwc_hab_karenia_1970_2023.parquet")
    u = make_grid(inst).assign(s["lat"].values, s["lon"].values)
    assert not np.isnan(u).any()
    assert {int(k): int(v) for k, v in pd.Series(u).value_counts().sort_index().items()} == FROZEN


SQUARE = {"type": "Feature", "properties": {"WDPAID": 555, "NAME": "square"},
          "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
                                                          [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]}}
MULTI = {"type": "Feature", "properties": {"WDPAID": 777},
         "geometry": {"type": "MultiPolygon", "coordinates": [[[[20, 20], [22, 20], [22, 22], [20, 22]]],
                                                               [[[30, 30], [32, 30], [32, 32], [30, 32]]]]}}


def test_polygon_holes_and_multipolygon(tmp_path):
    p = tmp_path / "zones.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": [SQUARE, MULTI]}))
    g = PolygonGrid.from_file(p, "WDPAID", "NAME", sha256=file_sha256(p))
    lat = [2, 5, 21, 31, 25, -1]; lon = [2, 5, 21, 31, 25, -1]   # inside · in hole · multi-a · multi-b · between · outside
    out = g.assign(lat, lon)
    assert out[0] == 555 and out[2] == 777 and out[3] == 777
    assert all(pd.isna(out[i]) for i in (1, 4, 5))
    assert g.names() == {555: "square", 777: "777"}



def test_polygon_pin_refuses_missing_and_changed_bytes(tmp_path):
    """M-2a-i: the pin the docstring claimed now exists. Missing → refused; one moved vertex → refused, by name."""
    p = tmp_path / "zones.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": [SQUARE, MULTI]}))
    pin = file_sha256(p)
    with pytest.raises(GridPinError, match="grid.sha256 missing"):
        PolygonGrid.from_file(p, "WDPAID")
    moved = json.loads(p.read_text()); moved["features"][0]["geometry"]["coordinates"][0][1] = [10, 0.001]
    p.write_text(json.dumps(moved))
    with pytest.raises(GridPinError, match="grid.sha256 mismatch"):
        PolygonGrid.from_file(p, "WDPAID", sha256=pin)
    assert PolygonGrid.from_file(p, "WDPAID", pinned=False).names() == {555: "555", 777: "777"}   # explicit opt-out only


def test_cells():
    g = CellGrid(0.5, 24.0, 26.0, -83.0, -81.0)
    out = g.assign([24.1, 25.9, 26.0, 23.9], [-82.9, -81.1, -82.0, -82.0])
    assert out[0] == "r0_c0" and out[1] == "r3_c3" and pd.isna(out[2]) and pd.isna(out[3])
    assert len(g.names()) == 16


def test_week_start_is_monday():
    w = week_start(["2026-10-02", "2026-09-28", "2026-10-04"])   # Fri · Mon · Sun
    assert (w == pd.Timestamp("2026-09-28")).all()

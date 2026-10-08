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


LATS, LONS = np.round(np.arange(34.025, 36.0, 0.05), 3), np.round(np.arange(-77.975, -75.0, 0.05), 3)


class FakeERDDAP:
    """Answers `<base>?var[(t0):1:(t1)][(lat0):1:(lat1)][(lon0):1:(lon1)]` as ERDDAP griddap does: the days in [t0, t1], and
    the centres between the ones NEAREST each bound (M-2a-ii; it was `lo ≤ c ≤ hi` before). It uses the fetcher's own `snap`,
    so these tests prove the union plumbing against one rule; the live parity check proves the rule against CRW."""
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        var, t0, t1, la0, la1, lo0, lo1 = re.match(
            r".*\?(\w+)\[\((.*?)\):1:\((.*?)\)\]\[\((.*?)\):1:\((.*?)\)\]\[\((.*?)\):1:\((.*?)\)\]", unquote(url)).groups()
        la0, la1, lo0, lo1 = map(float, (la0, la1, lo0, lo1))
        lats, lons = LATS[crw_mod.snap(LATS, la0, la1)], LONS[crw_mod.snap(LONS, lo0, lo1)]
        rows = ["time,latitude,longitude," + var, "UTC,degrees_north,degrees_east,x"]
        for di, day in enumerate(DAYS):
            if not (t0 <= day <= t1):
                continue
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
    f.grid_sha256 = "0" * 64
    return f


def _in_square(feature):
    (lon0, lat0), _, (lon1, lat1) = feature["geometry"]["coordinates"][0][:3]
    return lambda la, lo: lat0 < la < lat1 and lon0 < lo < lon1


INSIDE = {}   # uid → an analytic membership test, written by hand per shape (never the fetcher's geometry code)


def expected(feature, day: int) -> tuple[float, int]:
    """Independent of the fetcher: the mean over grid centres inside the zone (INSIDE, else an axis-aligned square), land excluded."""
    inside = INSIDE.get(feature["properties"]["seg"]) or _in_square(feature)
    cells = [(la, lo) for la in np.round(np.arange(34.025, 36.0, 0.05), 3) for lo in np.round(np.arange(-77.975, -75.0, 0.05), 3)
             if inside(la, lo) and (la, lo) != LAND]
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
    z = f.reduction["zones"]
    assert z["1"] == {"n_cells": expected(SEG1, 0)[1], "fallback": False, "cells_in_envelope": 8 * 10, "shared_cells": 0}
    # envelope 35.15–35.55 × −76.65–−76.15 → 8 latitude × 10 longitude centres
    assert z["2"]["n_cells"] == expected(SEG2, 0)[1]                   # the land cell is not counted
    s = json.loads((tmp_path / "dhw_fetch_summary.json").read_text())
    assert s["reduction"] == f.reduction and s["rows"] == 4 and "cell centre in polygon" in s["reduction_rule"]
    assert {k: s["reduction"][k] for k in ("grid_sha256", "pad_deg", "variable", "base")} == \
        {"grid_sha256": "0" * 64, "pad_deg": 0.05, "variable": SPEC["variable"], "base": SPEC["base"]}   # III F-1: the basis


def test_plant_an_envelope_mask_is_caught(tmp_path, monkeypatch):
    """C-009: the check above must fail if the mask keeps out-of-polygon cells (here: the whole padded envelope)."""
    monkeypatch.setattr(crw_mod, "geometry_contains", lambda geom, lat, lon: np.ones(len(lat), dtype=bool))
    df = crw(tmp_path, [SEG1, SEG2]).fetch(SPEC)
    assert zone_problems(df, [SEG1, SEG2])


def test_sub_cell_zone_falls_back_to_the_nearest_cell_and_says_so(tmp_path):
    tiny = square(9, 35.31, 35.32, -76.42, -76.41)   # between centres: no centre inside
    f = crw(tmp_path, [tiny])
    df = f.fetch(SPEC)
    assert f.reduction["zones"]["9"]["fallback"] is True and f.reduction["zones"]["9"]["n_cells"] == 1
    assert df["dhw"].tolist() == [value(35.325, -76.425, 0), value(35.325, -76.425, 1)]   # the nearest centre


def test_overlapping_zones_share_cells_and_say_so(tmp_path):
    a, b = square(1, 35.2, 35.5, -76.6, -76.2), square(2, 35.3, 35.6, -76.4, -76.0)
    f = crw(tmp_path, [a, b])
    f.fetch(SPEC)
    assert f.reduction["zones"]["1"]["shared_cells"] == f.reduction["zones"]["2"]["shared_cells"] > 0


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



# ── M-2a-i III F-5: zones that are not their bounding box ───────────────────────────────────────────────────────────
TRI = {"type": "Feature", "properties": {"seg": 21}, "geometry": {"type": "Polygon", "coordinates": [
    [[-76.6, 35.2], [-76.19, 35.2], [-76.6, 35.61], [-76.6, 35.2]]]}}   # no centre ON the hypotenuse (edges are undefined)
HOLED = {"type": "Feature", "properties": {"seg": 22}, "geometry": {"type": "Polygon", "coordinates": [
    [[-76.6, 35.2], [-76.2, 35.2], [-76.2, 35.6], [-76.6, 35.6], [-76.6, 35.2]],
    [[-76.5, 35.3], [-76.3, 35.3], [-76.3, 35.5], [-76.5, 35.5], [-76.5, 35.3]]]}}
MULTI = {"type": "Feature", "properties": {"seg": 23}, "geometry": {"type": "MultiPolygon", "coordinates": [
    [[[-76.6, 35.2], [-76.4, 35.2], [-76.4, 35.4], [-76.6, 35.4], [-76.6, 35.2]]],
    [[[-76.0, 35.6], [-75.8, 35.6], [-75.8, 35.8], [-76.0, 35.8], [-76.0, 35.6]]]]}}
INSIDE[21] = lambda la, lo: lo > -76.6 and la > 35.2 and (lo + 76.6) / 0.41 + (la - 35.2) / 0.41 < 1
INSIDE[22] = lambda la, lo: (35.2 < la < 35.6 and -76.6 < lo < -76.2) and not (35.3 < la < 35.5 and -76.5 < lo < -76.3)
INSIDE[23] = lambda la, lo: (35.2 < la < 35.4 and -76.6 < lo < -76.4) or (35.6 < la < 35.8 and -76.0 < lo < -75.8)
SHAPES = [TRI, HOLED, MULTI]


def test_non_rectangular_zones(tmp_path):
    f = crw(tmp_path, SHAPES)
    df = f.fetch(SPEC)
    assert zone_problems(df, SHAPES) == []
    assert all(not z["fallback"] and z["n_cells"] == expected(ft, 0)[1] for ft, z in zip(SHAPES, f.reduction["zones"].values()))


def test_plant_a_bounding_box_mask_is_caught(tmp_path, monkeypatch):
    """III F-5: a mask that is the zone's own bounding box (not its padded envelope) passed the rectangle-only tests."""
    def bbox(geom, lat, lon):
        lat0, lat1, lon0, lon1 = crw_mod.envelope(geom, 0.0)
        return (np.asarray(lat) > lat0) & (np.asarray(lat) < lat1) & (np.asarray(lon) > lon0) & (np.asarray(lon) < lon1)
    monkeypatch.setattr(crw_mod, "geometry_contains", bbox)
    df = crw(tmp_path, SHAPES).fetch(SPEC)
    assert len(zone_problems(df, SHAPES)) == 3       # triangle, hole and MultiPolygon each caught


# ── M-2a-i III F-1: a re-pinned zone file never reuses the old zones' data ──────────────────────────────────────────
def test_repin_with_artifact_kept_is_refused(tmp_path):
    crw(tmp_path, [SEG1]).fetch(SPEC)
    moved = square(1, 35.6, 35.9, -76.6, -76.2)
    f2 = crw(tmp_path, [moved], session=FakeERDDAP()); f2.grid_sha256 = "1" * 64
    with pytest.raises(ValueError, match="grid_sha256"):
        f2.fetch(SPEC)


def test_repin_with_artifact_deleted_refetches_the_new_zone(tmp_path):
    crw(tmp_path, [SEG1]).fetch(SPEC)
    (tmp_path / "dhw.parquet").unlink(); (tmp_path / "dhw_fetch_summary.json").unlink()
    moved = square(1, 35.6, 35.9, -76.6, -76.2)
    sess = FakeERDDAP()
    f2 = crw(tmp_path, [moved], session=sess); f2.grid_sha256 = "1" * 64
    df = f2.fetch(SPEC)
    assert sess.calls, "the old zone's cached cells were reused"
    assert zone_problems(df, [moved]) == [] and not f2.reduction["zones"]["1"]["fallback"]


def test_summary_without_reduction_is_refused_at_the_next_fetch(tmp_path):
    crw(tmp_path, [SEG1]).fetch(SPEC)
    (tmp_path / "dhw_fetch_summary.json").unlink()
    crw(tmp_path, [SEG1], offline=True).fetch(SPEC)              # cache hit: summary rewritten, reduction None
    with pytest.raises(ValueError, match="records no reduction"):
        crw(tmp_path, [SEG1], offline=True).fetch(SPEC)


def test_verify_and_conform_refuse_a_stale_basis(persistent_master, tmp_path):
    """The CLI's --verify (and so conform item 3, fetched) reads the basis, not only the bytes."""
    from atlantis_core.fetch.__main__ import verify
    d = tmp_path / "inst"; shutil.copytree(persistent_master, d)
    inst = load_instance(d); sid = "atl_stream_example_dhw_daily"
    spec = inst.stream_spec(sid)["fetch"] | {"years": [2020, 2020]}
    f = fetcher_for(inst, sid, session=FakeERDDAP()); f.fetch(spec)
    summ = json.loads(f.summary.read_text()); summ["reduction"]["pad_deg"] = 0.1
    f.summary.write_text(json.dumps(summ))
    probs = verify(inst, sid)
    assert any("pad_deg" in p for p in probs), probs


# ── M-2a-i III F-2: one feature per unit ────────────────────────────────────────────────────────────────────────────
def test_duplicate_zone_ids_are_refused(tmp_path):
    twin = square(1, 34.9, 35.2, -76.6, -76.2)
    with pytest.raises(ValueError, match="duplicate seg"):
        PolygonGrid([SEG1, twin], "seg")


def test_start_clamps_the_first_chunk_only(tmp_path):
    """M-2a-ii: CRW's DHW begins 1985-03-25, and ERDDAP answers a range that starts before it with a 404 that is not
    "No data", so a 1985 fetch gave up. `start` moves the first chunk's first day; later chunks still begin 1 January."""
    from atlantis_core.fetch.erddap import first_day
    f = crw(tmp_path, [SEG1])
    spec = {**SPEC, "years": [1985, 1994], "start": "1985-03-25"}
    from atlantis_core.fetch.erddap import chunks
    (a0, a1), (b0, b1) = chunks(spec)
    q1, q2 = f.query(spec, a0, a1, [24.5, 24.6, -81.4, -81.3]), f.query(spec, b0, b1, [24.5, 24.6, -81.4, -81.3])
    assert "[(1985-03-25T12:00:00Z):1:(1989-12-31T12:00:00Z)]" in q1 and "[(1990-01-01T12:00:00Z):1:(1994-12-31T12:00:00Z)]" in q2
    assert first_day(SPEC, 2020) == "2020-01-01"                                   # absent: unchanged
    for bad, why in (("1986-03-25", "first year"), ("25/03/1985", "ISO date")):
        with pytest.raises(ValueError, match=why):
            first_day({**spec, "start": bad}, 1985)
    df = crw(tmp_path / "s", [SEG1]).fetch({**SPEC, "start": "2020-07-02"})        # through the real download path
    assert len(df) == 1                                                            # the fake honours the range (M-2a-ii)


# ── M-2a-ii: month chunks and one union request per chunk (steward ruling 14: CRW's proxy cuts a request at ~10 s) ─────
MONTHS = {**SPEC, "years": [2020, 2020], "chunk_months": 1}


def test_snap_is_nearest_centre_inclusive():
    a = np.array([25.125, 25.175, 25.225, 25.275])
    assert a[crw_mod.snap(a, 25.16, 25.24)].tolist() == [25.175, 25.225]     # 25.16 → 25.175 (not the 25.125 below it)
    assert a[crw_mod.snap(a, 25.14, 25.26)].tolist() == [25.125, 25.175, 25.225, 25.275]   # each bound to its nearest
    assert a[crw_mod.snap(a, 25.0, 30.0)].tolist() == a.tolist()             # outside the axis: clamped to its ends


@pytest.mark.parametrize("features", [[SEG1, SEG2], SHAPES, [square(9, 35.31, 35.32, -76.42, -76.41), SEG1],
                                      [square(1, 35.2, 35.5, -76.6, -76.2), square(2, 35.3, 35.6, -76.4, -76.0)]],
                         ids=["land", "shapes", "fallback", "shared"])
def test_union_equals_per_zone(tmp_path, features):
    """The union request changes the request count, never the reduction: identical frames and an identical zones block,
    across the land cell, non-rectangular zones, a fallback zone and two zones sharing cells."""
    zs, us = FakeERDDAP(), FakeERDDAP()
    fz, fu = crw(tmp_path / "z", features, session=zs), crw(tmp_path / "u", features, session=us)
    dz, du = fz.fetch(MONTHS), fu.fetch({**MONTHS, "envelope": "union"})
    pd.testing.assert_frame_equal(dz.sort_values(["seg", "date"]).reset_index(drop=True),
                                  du.sort_values(["seg", "date"]).reset_index(drop=True))
    assert fz.reduction == fu.reduction
    inside = [ft for ft in features if not fu.reduction["zones"][str(ft["properties"]["seg"])]["fallback"]]
    assert zone_problems(du, inside) == []                     # the fallback zone's value is checked by its own test above
    assert len(zs.calls) == 12 * len(features) and len(us.calls) == 12              # one request per month, not per zone
    s = json.loads((tmp_path / "u" / "dhw_fetch_summary.json").read_text())
    assert s["request"] == {"envelope": "union", "chunk": {"chunk_months": 1}, "n_chunks": 12}


def test_union_box_covers_every_zone_and_is_cached_per_month(tmp_path):
    sess = FakeERDDAP()
    f = crw(tmp_path, [SEG1, MULTI], session=sess)
    f.fetch({**MONTHS, "envelope": "union"})
    la0, la1, lo0, lo1 = map(float, re.search(r"\]\[\((.*?)\):1:\((.*?)\)\]\[\((.*?)\):1:\((.*?)\)\]$", unquote(sess.calls[0])).groups())
    assert (la0, la1, lo0, lo1) == pytest.approx((35.15, 35.85, -76.65, -75.75))  # SEG1 ∪ MULTI, each padded 0.05
    cached = sorted(p.name for p in (tmp_path / "dhw").rglob("*.csv"))
    assert len(cached) == 12 and cached[6] == "union_2020-07-01_2020-07-31.csv"
    (tmp_path / "dhw.parquet").unlink(); (tmp_path / "dhw_fetch_summary.json").unlink()
    again = FakeERDDAP()
    crw(tmp_path, [SEG1, MULTI], session=again).fetch({**MONTHS, "envelope": "union"})
    assert again.calls == []                                                      # resumes from the month cache


def test_unknown_envelope_is_refused(tmp_path):
    with pytest.raises(ValueError, match="zone \\| union"):
        crw(tmp_path, [SEG1]).fetch({**MONTHS, "envelope": "box"})


def test_union_offline_never_touches_network(tmp_path):
    class Boom:
        def get(self, *a, **k): raise AssertionError("network touched")
    with pytest.raises(OfflineError):
        crw(tmp_path, [SEG1], session=Boom(), offline=True).fetch({**MONTHS, "envelope": "union"})


def test_plant_a_union_without_the_per_zone_subset_is_caught(tmp_path, monkeypatch):
    """C-009: the equivalence check must fail if each zone reads the whole union box (no snap-to-its-own-envelope)."""
    features = [SEG1, MULTI, square(9, 35.31, 35.32, -76.42, -76.41)]
    fz = crw(tmp_path / "z", features); fz.fetch(MONTHS)
    monkeypatch.setattr(crw_mod, "in_box", lambda raw, box: raw)
    fu = crw(tmp_path / "u", features); fu.fetch({**MONTHS, "envelope": "union"})
    assert fz.reduction["zones"] != fu.reduction["zones"]



def test_union_in_day_spans_equals_per_zone(tmp_path):
    """Ruling 15: the instance runs `chunk_days: 15`; the union ≡ per-zone property holds for day spans too."""
    spec = {**SPEC, "years": [2020, 2020], "chunk_days": 15}
    zs, us = FakeERDDAP(), FakeERDDAP()
    fz, fu = crw(tmp_path / "z", [SEG1, SEG2], session=zs), crw(tmp_path / "u", [SEG1, SEG2], session=us)
    dz, du = fz.fetch(spec), fu.fetch({**spec, "envelope": "union"})
    pd.testing.assert_frame_equal(dz.sort_values(["seg", "date"]).reset_index(drop=True), du.sort_values(["seg", "date"]).reset_index(drop=True))
    assert fz.reduction == fu.reduction and len(du) == 4 and len(us.calls) == 25 and len(zs.calls) == 50   # 366 days / 15
    assert fu.request == {"envelope": "union", "chunk": {"chunk_days": 15}, "n_chunks": 25}


# ── M-2a-ii III review: a new base is a new cache (F-1) · missing days are said (F-2) · edge ties keep the cells (F-5) ─────
def test_a_new_base_never_reads_the_old_sources_cells(tmp_path):
    """F-1: the cache key held grid, pad and variable but not the base, so deleting the artifact and changing the base
    re-read the old source's cells under the new base's stamp. Both envelopes, and the generic ERDDAP fetcher too."""
    from atlantis_core.fetch import ERDDAPGriddap
    other = SPEC["base"].replace("coastwatch.noaa.gov", "mirror.example.org")
    for env in ("zone", "union"):
        d = tmp_path / env
        crw(d, [SEG1]).fetch({**SPEC, "envelope": env})
        (d / "dhw.parquet").unlink(); (d / "dhw_fetch_summary.json").unlink()
        sess = FakeERDDAP()
        f2 = crw(d, [SEG1], session=sess); f2.fetch({**SPEC, "base": other, "envelope": env})
        assert sess.calls and all(c.startswith(other) for c in sess.calls), env
        assert f2.reduction["base"] == other
    g = {"base": SPEC["base"], "variable": SPEC["variable"], "years": [2020, 2020], "boxes": {1: [35.2, 35.5, -76.6, -76.2]}}
    ERDDAPGriddap(tmp_path / "g", "s.parquet", "s.json", session=FakeERDDAP()).fetch(g)
    for p in ("s.parquet", "s.json"):
        (tmp_path / "g" / p).unlink()
    for change in ({"base": other}, {"boxes": {1: [35.6, 35.9, -76.6, -76.2]}}, {"variable": "hotspot"}):
        sess = FakeERDDAP()
        ERDDAPGriddap(tmp_path / "g", "s.parquet", "s.json", session=sess).fetch({**g, **change})
        assert sess.calls, change
        for p in ("s.parquet", "s.json"):
            (tmp_path / "g" / p).unlink()


def test_plant_a_key_without_the_base_is_caught(tmp_path, monkeypatch):
    """C-009: the test above must fail if the key ignores the base again."""
    monkeypatch.setattr(crw_mod, "basis_tag", lambda *parts: "same")
    crw(tmp_path, [SEG1]).fetch(SPEC)
    (tmp_path / "dhw.parquet").unlink(); (tmp_path / "dhw_fetch_summary.json").unlink()
    sess = FakeERDDAP()
    crw(tmp_path, [SEG1], session=sess).fetch({**SPEC, "base": SPEC["base"].replace("coastwatch.noaa.gov", "m.example.org")})
    assert sess.calls == []                                                       # the defect, reproduced under the plant


def test_summary_counts_calendar_days_and_names_a_missing_one(tmp_path, monkeypatch):
    """F-2: FKNMS DHW lacks 1999-05-01 (CRW's own axis); a null count saw nothing. The summary now says it."""
    f = crw(tmp_path / "full", [SEG1, SEG2]); f.fetch(SPEC)
    c = json.loads((tmp_path / "full" / "dhw_fetch_summary.json").read_text())["completeness"]
    assert c == {"calendar_days": 2, "n_dates": 2, "n_missing": 0, "missing_dates": [], "dates_per_unit": {"min": 2, "max": 2}}
    monkeypatch.setitem(globals(), "DAYS", ["2020-07-01T12:00:00Z", "2020-07-03T12:00:00Z"])     # the source skips 07-02
    crw(tmp_path / "gap", [SEG1, SEG2]).fetch(SPEC)
    s = json.loads((tmp_path / "gap" / "dhw_fetch_summary.json").read_text())
    assert s["completeness"]["n_missing"] == 1 and s["completeness"]["missing_dates"] == ["2020-07-02"]
    assert s["reduction"]["zones"]["1"]["n_cells"] > 0                            # the reduction block is still there


def test_daily_completeness_sees_a_unit_short_of_a_day():
    from atlantis_core.fetch.provenance import daily_completeness
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-01"]), "seg": [1, 1, 2]})
    c = daily_completeness(df, "date", "seg")
    assert c["n_missing"] == 0 and c["dates_per_unit"] == {"min": 1, "max": 2}
    assert daily_completeness(df.iloc[:0], "date", "seg")["calendar_days"] == 0


def test_verify_says_which_days_a_daily_artifact_lacks(persistent_master, tmp_path, capsys, monkeypatch):
    from atlantis_core.fetch.__main__ import main
    d = tmp_path / "inst"; shutil.copytree(persistent_master, d)
    inst = load_instance(d); sid = "atl_stream_example_dhw_daily"
    monkeypatch.setitem(globals(), "DAYS", ["2020-07-01T12:00:00Z", "2020-07-03T12:00:00Z"])
    f = fetcher_for(inst, sid, session=FakeERDDAP()); f.fetch(inst.stream_spec(sid)["fetch"] | {"years": [2020, 2020]})
    main(["--instance", str(d), "--stream", sid, "--verify"])
    assert f"ⓘ {sid}: 2 of 3 calendar days present; missing 1: 2020-07-02" in capsys.readouterr().out


def test_an_edge_tie_flips_cells_in_envelope_never_the_kept_cells():
    """F-5: FKNMS zones 20 and 21 have vertices on the 0.05° lattice, so a padded bound lands on a cell EDGE, and which side
    ERDDAP takes is float noise. Either side keeps the same cells (an edge cell's centre is half a cell outside the
    polygon); only cells_in_envelope moves. Every one of the 16 tie resolutions is tried, and at least one must move it."""
    import itertools
    raw = pd.DataFrame([(DAYS[0], la, lo, value(la, lo, 0)) for la in LATS for lo in LONS],
                       columns=["time", "latitude", "longitude", "dhw"])
    for zone in (SEG1, MULTI, HOLED):
        box, kept, sizes = crw_mod.envelope(zone["geometry"], 0.05), set(), set()
        for signs in itertools.product((-1e-6, 1e-6), repeat=4):
            sub = crw_mod.in_box(raw, [b + s for b, s in zip(box, signs)])
            cells = sub[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
            sel, fb = crw_mod.select_cells(zone["geometry"], cells)
            kept.add(frozenset(map(tuple, sel[["latitude", "longitude"]].to_numpy()))); sizes.add(len(cells))
            assert not fb
        assert len(kept) == 1, zone["properties"]["seg"]
        assert len(sizes) > 1, "no tie flipped: the test is not exercising an edge"

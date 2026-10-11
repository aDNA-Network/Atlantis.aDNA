"""discover (M-3a): playbook §B as checks. Every trap is shown to fire on a planted case and to stay quiet on a clean one.
No network, ever: probes run against fake sessions, and a socket opened anywhere fails the test."""
import json, shutil, socket

import pandas as pd
import pytest
import yaml

from atlantis_core import load_instance
from atlantis_core.discover import probe as P
from atlantis_core.discover import traps as T
from atlantis_core.discover.__main__ import main as discover_main
from atlantis_core.discover.rows import (DECL_FIELDS, DiscoveryError, check_request, check_searched, compare,
                                         pointer_rows, validate_rows)
from atlantis_core.fetch import ArcGISMapServer, NWISDailyValues

FWC, OISST, USGS = "atl_stream_fwc_hab_karenia", "atl_stream_oisst_region_daily", "atl_stream_usgs_discharge_daily"


@pytest.fixture(autouse=True)
def no_sockets(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a socket was opened")
    monkeypatch.setattr(socket.socket, "connect", boom)


class R:
    def __init__(self, body=None, code=200, text=""):
        self.body, self.status_code, self.text = body, code, text

    def json(self):
        if self.body is None:
            raise ValueError("no json")
        return self.body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class Fake:
    """Routes a GET by the first matching (substring, params-predicate) → response. Records every URL asked."""
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, dict(params or {})))
        for sub, pred, resp in self.routes:
            if sub in url and pred(params or {}):
                return resp(url, params or {}) if callable(resp) else resp
        return R(code=404)


@pytest.fixture
def inst_dir(exemplar_dir, tmp_path):
    """The exemplar's declarations + tiny planted artifacts (clean unless a test plants otherwise)."""
    for f in ("atlantis.yaml", "streams.yaml", "features.yaml", "events.yaml"):
        shutil.copy(exemplar_dir / f, tmp_path / f)
    raw = tmp_path / "data" / "raw"; raw.mkdir(parents=True)
    days = pd.date_range("1994-01-01", "2023-12-31", freq="30D")
    # FWC: points inside box 4 (Tampa Bay, [27.6, 28.4, -83.2, -82.4]) — unit 4 by the rules, inside its box
    pd.DataFrame({"sample_date": days, "cells_per_l": 1000.0, "lat": 28.0, "lon": -82.7}).to_parquet(raw / "fwc_hab_karenia_1970_2023.parquet")
    (raw / "fwc_fetch_summary.json").write_text(json.dumps({"rows": len(days), "min_date": "1994-01-01", "max_date": "2023-12-01",
                                                            "per_layer": {"1990___1999": 7}}))
    pd.DataFrame({"date": days, "sst": 25.0, "region": 4}).to_parquet(raw / "oisst_region_daily.parquet")
    (raw / "oisst_fetch_summary.json").write_text(json.dumps({"rows": len(days), "min_date": "1994-01-01", "max_date": "2023-12-01"}))
    pd.DataFrame({"date": days[:3], "discharge_cfs": [10.0, 0.0, 5.0], "site": "02292900"}).to_parquet(raw / "usgs_discharge_daily.parquet")
    (raw / "usgs_fetch_summary.json").write_text(json.dumps({"rows": 3}))
    return tmp_path


def _edit(d, fname, fn):
    p = d / fname; doc = yaml.safe_load(p.read_text()); fn(doc); p.write_text(yaml.safe_dump(doc, sort_keys=False))


def _status(results, trap):
    return next(r for r in results if r["trap"] == trap)


# ── rows: pointer rows only, validated, compared ───────────────────────────────────────────────────────────────────
def _candidates(exemplar_dir):
    s = yaml.safe_load((exemplar_dir / "streams.yaml").read_text())["observation_streams"]
    c = [{**{k: r[k] for k in DECL_FIELDS if k in r}, "step": st} for r, st in zip(s, ("A1", "A2", "A3"))]
    return {"request": {"grid_kind": "rules", "event_stream": FWC, "event_variable": "Karenia brevis", "ecosystem": "estuary"},
            "searched": [{"step": f"A{i}", "found": [c[i - 1]["stream_id"]] if i <= 3 else []} for i in range(1, 7)],
            "candidates": c}


def test_rows_reproduce_the_exemplar_registry(exemplar_dir):
    rows = pointer_rows(_candidates(exemplar_dir))
    assert validate_rows(rows) == []
    assert compare(rows, exemplar_dir / "streams.yaml") == []
    assert all(k not in r for r in rows for k in ("sha256", "ingested_at", "row_count", "step"))


def test_a_candidate_carrying_fetch_provenance_is_refused(exemplar_dir):
    doc = _candidates(exemplar_dir); doc["candidates"][0]["sha256"] = "0" * 64
    with pytest.raises(DiscoveryError, match="pointer"):
        pointer_rows(doc)


def test_a_candidate_without_its_step_is_refused(exemplar_dir):
    doc = _candidates(exemplar_dir); doc["candidates"][1]["step"] = "B2"
    with pytest.raises(DiscoveryError, match="§A step"):
        pointer_rows(doc)


@pytest.mark.parametrize("edit,why", [
    (lambda r: r.__setitem__("modality", "satellite"), "atl_v0"),
    (lambda r: r.__setitem__("fetcher", "MyScraper"), "not an atlantis_core fetcher"),
    (lambda r: r.pop("surveillance_channel"), "surveillance_channel not stated"),
    (lambda r: r.pop("license"), "atl_v0"),
])
def test_validate_rows_catches(exemplar_dir, edit, why):
    rows = pointer_rows(_candidates(exemplar_dir)); edit(rows[0])
    assert any(why in e for e in validate_rows(rows))


def test_compare_catches_a_changed_licence(exemplar_dir):
    rows = pointer_rows(_candidates(exemplar_dir)); rows[2]["license"] = "CC-BY-4.0"
    assert compare(rows, exemplar_dir / "streams.yaml") == [
        f"{USGS}.license: streams.yaml 'public (NOAA / USGS)' ≠ discovered 'CC-BY-4.0'"]


def test_every_step_is_accounted_for_and_the_request_is_this_instances(exemplar_dir):
    doc = _candidates(exemplar_dir)
    inst = load_instance(exemplar_dir)
    assert check_request(doc, inst) == [] and check_searched(doc) == []
    doc["searched"] = doc["searched"][:4]; doc["request"]["event_stream"] = OISST; doc["request"]["ecosystem"] = " "
    errs = check_request(doc, inst) + check_searched(doc)
    assert any("A5 not accounted" in e for e in errs) and any("request.event_stream" in e for e in errs)
    assert any("request.ecosystem" in e for e in errs)


# ── trap 2: longitude per unit ─────────────────────────────────────────────────────────────────────────────────────
def test_longitude_quiet_when_points_sit_in_their_unit(inst_dir):
    r = T.longitude_by_unit(load_instance(inst_dir), T.DEFAULTS)
    assert r["status"] == "pass", r
    assert r["evidence"][FWC]["units"]["4"]["out_gross"] == 0


def test_longitude_fires_on_open_gulf_points_in_a_coastal_unit(inst_dir):
    """S329's trap in miniature: a latitude-band rule takes every point at Tampa's latitude, wherever it lies."""
    p = inst_dir / "data/raw/fwc_hab_karenia_1970_2023.parquet"
    df = pd.read_parquet(p); df.loc[df.index[:20], "lon"] = -88.5      # 20 of 366 points, 5° west of box 4
    df.to_parquet(p)
    r = T.longitude_by_unit(load_instance(inst_dir), T.DEFAULTS)
    assert r["status"] == "fail" and r["evidence"][FWC]["failing_units"] == ["4"]
    assert r["evidence"][FWC]["units"]["4"]["out_gross"] == 20


def test_longitude_counts_what_vitals_build_drops(inst_dir, monkeypatch):
    from atlantis_core.grid import RuleGrid
    monkeypatch.setattr(RuleGrid, "assign", lambda self, la, lo: pd.Series([4.0] * (len(la) - 3) + [float("nan")] * 3).to_numpy())
    r = T.longitude_by_unit(load_instance(inst_dir), T.DEFAULTS)
    assert r["evidence"][FWC]["unassigned"] == 3 and r["status"] == "warn"


# ── trap 4: samples per year ───────────────────────────────────────────────────────────────────────────────────────
def test_samples_per_year_fires_on_a_sparse_early_year(inst_dir):
    p = inst_dir / "data/raw/fwc_hab_karenia_1970_2023.parquet"
    df = pd.read_parquet(p)
    df = df[~((df.sample_date.dt.year == 1994) & (df.index % 12 != 0))]   # 1994 keeps one sample of ~12
    df.to_parquet(p)
    r = T.samples_per_year(load_instance(inst_dir), T.DEFAULTS)
    assert r["status"] == "warn" and r["evidence"][FWC]["sparse_years"] == [1994]
    assert r["evidence"][FWC]["earliest_min_train_year_with_no_sparse_year"] == 1995


def test_samples_per_year_quiet_on_an_even_record(inst_dir):
    assert T.samples_per_year(load_instance(inst_dir), T.DEFAULTS)["status"] == "pass"


# ── trap 5: negative flow ──────────────────────────────────────────────────────────────────────────────────────────
def _nwis(values, nodata=-999999.0):
    body = {"value": {"timeSeries": [{"variable": {"noDataValue": nodata},
                                      "values": [{"value": [{"dateTime": f"2020-01-0{i+1}T00:00:00.000", "value": str(v)}
                                                            for i, v in enumerate(values)]}]}]}}
    return Fake([("waterservices", lambda p: "parameterCd" in p, R(body))])


def test_negative_flow_clipped_by_declaration_is_counted_by_the_probe(inst_dir):
    inst = load_instance(inst_dir)
    probes = {USGS: P.probe_stream(inst, USGS, P.Probe(session=_nwis([12.5, -3, 4])))}
    r = T.negative_flow(inst, probes)
    assert r["status"] == "pass"
    assert set(r["evidence"][USGS]["server_negatives"].values()) == {1}


def test_negative_flow_fails_without_the_declaration(inst_dir):
    _edit(inst_dir, "atlantis.yaml", lambda d: d["streams"][USGS]["fetch"].pop("clip_negative"))
    inst = load_instance(inst_dir)
    probes = {USGS: P.probe_stream(inst, USGS, P.Probe(session=_nwis([12.5, -3])))}
    assert T.negative_flow(inst, probes)["status"] == "fail"


def test_a_nodata_sentinel_is_not_flow(inst_dir):
    inst = load_instance(inst_dir)
    probes = {USGS: P.probe_stream(inst, USGS, P.Probe(session=_nwis([12.5, -999999])))}
    r = T.negative_flow(inst, probes)
    assert r["status"] == "fail" and "sentinel" in r["evidence"][USGS]["why"]


def test_negative_flow_offline(inst_dir):
    inst = load_instance(inst_dir)
    assert T.negative_flow(inst, None)["status"] == "na"            # clipped: the count is not knowable offline
    _edit(inst_dir, "atlantis.yaml", lambda d: d["streams"][USGS]["fetch"].pop("clip_negative"))
    p = inst_dir / "data/raw/usgs_discharge_daily.parquet"
    df = pd.read_parquet(p); df.loc[0, "discharge_cfs"] = -2.0; df.to_parquet(p)
    assert T.negative_flow(load_instance(inst_dir), None)["status"] == "fail"


def test_the_nwis_fetcher_clips_what_it_declares(tmp_path):
    """The clip the trap relies on, asserted (FakeNWIS in test_fetch_cli serves −3 and never checked it became 0)."""
    f = NWISDailyValues(tmp_path, "q.parquet", "q.json", session=_nwis([12.5, -3]))
    df = f._download({"sites": ["1"], "parameter": "00060", "start": "2020", "end": "2020", "value_name": "q", "clip_negative": True})
    assert df["q"].tolist() == [12.5, 0.0]


# ── traps 1 + 3: the server's count, and a zero probed ─────────────────────────────────────────────────────────────
def _one_layer(inst_dir):
    _edit(inst_dir, "atlantis.yaml", lambda d: d["streams"][FWC]["fetch"].__setitem__("layers", [{"name": "1990___1999", "layer": 4, "expected": 7}]))


def _arcgis(count_body, meta=R({"name": "Historic"})):
    return Fake([("/query", lambda p: p.get("returnCountOnly") == "true", count_body), ("MapServer/4", lambda p: True, meta)])


def test_server_count_matches(inst_dir):
    _one_layer(inst_dir); inst = load_instance(inst_dir)
    probes = {FWC: P.probe_stream(inst, FWC, P.Probe(session=_arcgis(R({"count": 7}))))}
    assert T.server_count(inst, probes)["status"] == "pass"
    assert T.probe_zero(inst, probes)["status"] == "na"     # III F-4: no zero met is nothing tested, not a pass


def test_server_count_drift_fails(inst_dir):
    _one_layer(inst_dir); inst = load_instance(inst_dir)
    probes = {FWC: P.probe_stream(inst, FWC, P.Probe(session=_arcgis(R({"count": 9}))))}
    r = T.server_count(inst, probes)
    assert r["status"] == "fail" and r["evidence"][FWC][0]["fetched"] == 7


def test_a_reply_without_the_count_key_is_a_broken_question_not_a_zero(inst_dir):
    """S329: a returnDistinctValues reply had no `features` key and read as empty."""
    _one_layer(inst_dir); inst = load_instance(inst_dir)
    probes = {FWC: P.probe_stream(inst, FWC, P.Probe(session=_arcgis(R({"features": []}))))}
    z = T.probe_zero(inst, probes)
    assert z["status"] == "fail" and z["evidence"][FWC][0]["kind"] == "broken question"
    assert "no `count` key" in z["evidence"][FWC][0]["error"]


def test_a_zero_is_true_only_when_the_control_answers(inst_dir):
    _one_layer(inst_dir); inst = load_instance(inst_dir)
    real = {FWC: P.probe_stream(inst, FWC, P.Probe(session=_arcgis(R({"count": 0}))))}
    assert T.probe_zero(inst, real)["status"] == "warn"
    dead = {FWC: P.probe_stream(inst, FWC, P.Probe(session=_arcgis(R({"count": 0}), meta=R(code=503))))}
    z = T.probe_zero(inst, dead)
    assert z["status"] == "fail" and z["evidence"][FWC][0]["reading"] == "a broken question"


def _erddap_info(n, lo, hi):
    rows = [["dimension", "time", "", "double", f"nValues={n}, evenlySpaced=true"],
            ["attribute", "time", "actual_range", "double", f"{lo}, {hi}"]]
    return R({"table": {"columnNames": ["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"], "rows": rows}})


def test_erddap_time_axis_must_cover_what_was_fetched(inst_dir):
    inst = load_instance(inst_dir)
    lo, hi = pd.Timestamp("1981-09-01").timestamp(), pd.Timestamp("2026-10-01").timestamp()
    ok = {OISST: P.probe_stream(inst, OISST, P.Probe(session=Fake([("/info/ncdcOisst21Agg_LonPM180/index.json", lambda p: True,
                                                                     _erddap_info(16000, lo, hi))])))}
    assert ok[OISST]["answers"][0]["n"] == 16000 and T.server_count(inst, ok)["status"] == "pass"
    short = {OISST: P.probe_stream(inst, OISST, P.Probe(session=Fake([("/info/", lambda p: True,
                                                                        _erddap_info(10, lo, pd.Timestamp("2000-01-01").timestamp()))])))}
    assert T.server_count(inst, short)["status"] == "fail"


def test_unreachable_source_is_an_answer_not_a_crash(inst_dir):
    inst = load_instance(inst_dir)
    class Down:
        def get(self, *a, **k): raise ConnectionError("down")
    probes = {OISST: P.probe_stream(inst, OISST, P.Probe(session=Down(), retries=1))}
    assert T.server_count(inst, probes)["status"] == "fail" and T.probe_zero(inst, probes)["status"] == "fail"


def test_the_arcgis_fetcher_asserts_the_server_count(tmp_path):
    """The fetch-side half of trap 1 (fetch/arcgis.py), never tested until M-3a: fewer rows than the server counted refuses."""
    pages = Fake([("/query", lambda p: p.get("returnCountOnly") == "true", R({"count": 3})),
                  ("/query", lambda p: p.get("resultOffset") == 0, R({"features": [{"attributes": {"OBJECTID": 1}}]})),
                  ("/query", lambda p: True, R({"features": []}))])
    f = ArcGISMapServer(tmp_path, "a.parquet", "a.json", session=pages)
    with pytest.raises(AssertionError, match="fetched 1 != server count 3"):
        f.fetch_layer({"url_template": "https://h/{name}/MapServer/{layer}/query", "fields": "*"}, "x", 2)


# ── trap 6: surveillance ───────────────────────────────────────────────────────────────────────────────────────────
def test_surveillance_present_passes_and_a_blank_absence_fails(inst_dir):
    assert T.surveillance_declared(load_instance(inst_dir))["status"] == "pass"
    _edit(inst_dir, "atlantis.yaml", lambda d: d.__setitem__("surveillance", {"declared": "absent", "reason": ""}))
    r = T.surveillance_declared(load_instance(inst_dir, check=False))
    assert r["status"] == "fail" and any("non-blank reason" in x for x in r["evidence"]["r8"])


# ── the CLI ────────────────────────────────────────────────────────────────────────────────────────────────────────
def _write_candidates(d, doc):
    (d / "discovery").mkdir(exist_ok=True)
    (d / "discovery" / "candidates.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))


def test_cli_offline_writes_pointer_rows_and_a_memo_and_never_streams_yaml(inst_dir, exemplar_dir):
    _write_candidates(inst_dir, _candidates(exemplar_dir))
    before = (inst_dir / "streams.yaml").read_bytes()
    assert discover_main(["--instance", str(inst_dir), "--compare", str(inst_dir / "streams.yaml")]) == 0
    assert (inst_dir / "streams.yaml").read_bytes() == before
    out = inst_dir / "discovery"
    rows = yaml.safe_load((out / "streams.discovered.yaml").read_text())["observation_streams"]
    assert [r["stream_id"] for r in rows] == [FWC, OISST, USGS] and not any("sha256" in r for r in rows)
    memo = json.loads((out / "discovery_memo.json").read_text())
    assert memo["probed"] is False and memo["hosts"] == {} and memo["compare"]["diffs"] == []
    assert "## Traps (playbook §B)" in (out / "discovery_memo.md").read_text()


def test_cli_fails_on_a_compare_diff_and_a_ruling_accepts_a_fail(inst_dir, exemplar_dir):
    doc = _candidates(exemplar_dir); doc["candidates"][0]["license"] = "changed"
    _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir), "--compare", str(inst_dir / "streams.yaml")]) == 1
    p = inst_dir / "data/raw/fwc_hab_karenia_1970_2023.parquet"
    df = pd.read_parquet(p); df.loc[df.index[:20], "lon"] = -88.5; df.to_parquet(p)
    doc = _candidates(exemplar_dir); _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 1                       # longitude fails
    doc["rulings"] = {"longitude_by_unit": {"ruling": "offshore samples pooled by latitude, by design", "by": "steward"}}
    _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 1                       # a ruling without a date is refused
    doc["rulings"]["longitude_by_unit"]["date"] = "2026-10-10"; _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 1                       # …and one without `accepts`
    doc["rulings"]["longitude_by_unit"]["accepts"] = [f"{FWC}:4"]; _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 0
    memo = json.loads((inst_dir / "discovery/discovery_memo.json").read_text())
    assert _status(memo["traps"], "longitude_by_unit")["status"] == "accepted"


def test_a_ruling_accepts_the_failures_it_saw_not_the_trap(inst_dir, exemplar_dir):
    """III M-3a F-1, the reviewer's plant: a ruling given for unit 4 must not absorb a new failure in unit 5."""
    p = inst_dir / "data/raw/fwc_hab_karenia_1970_2023.parquet"
    df = pd.read_parquet(p); df.loc[df.index[:20], "lon"] = -88.5
    extra = df.iloc[:40].assign(lat=27.3, lon=-88.0)                    # unit 5 (Sarasota) band, 5° west of its box
    pd.concat([df, extra], ignore_index=True).to_parquet(p)
    doc = _candidates(exemplar_dir)
    doc["rulings"] = {"longitude_by_unit": {"ruling": "offshore pooling", "by": "steward", "date": "2026-10-10",
                                            "accepts": [f"{FWC}:4"]}}
    _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 1
    r = _status(json.loads((inst_dir / "discovery/discovery_memo.json").read_text())["traps"], "longitude_by_unit")
    assert r["status"] == "fail" and f"{FWC}:5" in r["ruling_stale"]
    assert "ruling stale" in (inst_dir / "discovery/discovery_memo.md").read_text()


def test_an_unused_ruling_is_shown_not_applied(inst_dir, exemplar_dir):
    doc = _candidates(exemplar_dir)
    doc["rulings"] = {"surveillance_declared": {"ruling": "x", "by": "steward", "date": "2026-10-10", "accepts": ["R8"]}}
    _write_candidates(inst_dir, doc)
    assert discover_main(["--instance", str(inst_dir)]) == 0
    assert "ruling unused" in (inst_dir / "discovery/discovery_memo.md").read_text()


def test_an_unprobed_run_does_not_replace_a_probed_memo(inst_dir, exemplar_dir):
    _write_candidates(inst_dir, _candidates(exemplar_dir))
    (inst_dir / "discovery/discovery_memo.json").write_text(json.dumps({"probed": True}))
    assert discover_main(["--instance", str(inst_dir)]) == 1
    assert discover_main(["--instance", str(inst_dir), "--overwrite-probed"]) == 0


def test_a_candidate_no_step_found_is_refused(exemplar_dir):
    doc = _candidates(exemplar_dir); doc["searched"][2]["found"] = []
    assert any(USGS in e and "no searched row" in e for e in check_searched(doc))


def test_nwis_server_count_compares_days_and_values(inst_dir):
    """The arm that produced the exemplar's only server-count fail (III F-10): backfilled days and revised values."""
    inst = load_instance(inst_dir)
    cached = pd.read_parquet(inst_dir / "data/raw/usgs_discharge_daily.parquet")      # 3 days: 10, 0, 5
    days = [str(d.date()) for d in cached.date]
    body = lambda vals, ds: {"value": {"timeSeries": [{"variable": {"noDataValue": -999999.0}, "values": [{"value": [
        {"dateTime": f"{d}T00:00:00.000", "value": str(v)} for d, v in zip(ds, vals)]}]}]}}
    same = Fake([("waterservices", lambda p: p["sites"] == "02292900", R(body([10.0, -4.0, 5.0], days))),
                 ("waterservices", lambda p: "parameterCd" in p, R({"value": {"timeSeries": []}})),
                 ("waterservices/nwis/site", lambda p: True, R(text="02296750"))])
    r = T.server_count(inst, {USGS: P.probe_stream(inst, USGS, P.Probe(session=same))})
    row = r["evidence"][USGS][0]
    assert row["status"] == "pass" and row["revised_values"] == 0       # −4 clipped as the fetch clips it = cached 0
    more = Fake([("waterservices", lambda p: p["sites"] == "02292900",
                  R(body([10.0, 0.0, 7.5, 3.0], days + ["2030-01-01"])))])
    r = T.server_count(inst, {USGS: P.probe_stream(inst, USGS, P.Probe(session=more))})
    row = r["evidence"][USGS][0]
    assert (row["server_only_days"], row["revised_values"], row["status"]) == (1, 1, "fail")
    assert r["failures"][0] == f"{USGS}:site 02292900"


def test_polygon_units_sit_inside_their_bounds(forked):
    """The polygon arm (III F-10): containment assigns, so a point in a segment is inside that segment's bounds."""
    inst = load_instance(forked)
    sid = next(s for s in inst.streams if inst.stream_spec(s).get("shape") == "point")
    spec = inst.stream_spec(sid); c = spec["columns"]
    p = forked / spec["artifact"]; p.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({c["date"]: pd.date_range("2010-01-01", periods=10, freq="30D"), c["value"]: 5.0,
                  c["lat"]: [35.3] * 5 + [35.0] * 5, c["lon"]: -76.4}).to_parquet(p)
    r = T.longitude_by_unit(load_instance(forked), T.DEFAULTS)
    assert r["status"] == "pass" and set(r["evidence"][sid]["units"]) == {"1", "2"} and "containment" in r["note"]


def test_cli_probe_records_hosts_and_counts_only(inst_dir, exemplar_dir):
    _one_layer(inst_dir)
    _write_candidates(inst_dir, _candidates(exemplar_dir))
    lo, hi = pd.Timestamp("1981-09-01").timestamp(), pd.Timestamp("2026-10-01").timestamp()
    s = Fake([("/query", lambda p: p.get("returnCountOnly") == "true", R({"count": 7})),
              ("/info/", lambda p: True, _erddap_info(16000, lo, hi)),
              ("waterservices", lambda p: "parameterCd" in p, _nwis([1.0, -2.0]).routes[0][2])])
    discover_main(["--instance", str(inst_dir), "--probe"], session=s)
    memo = json.loads((inst_dir / "discovery/discovery_memo.json").read_text())
    assert memo["probed"] and set(memo["hosts"]) == {"gis.myfwc.com", "coastwatch.pfeg.noaa.gov", "waterservices.usgs.gov"}
    assert "timeSeries" not in json.dumps(memo) and "features" not in json.dumps(memo["traps"])
    assert not list((inst_dir / "data" / "raw").glob("*_1990___1999.parquet"))   # a probe caches nothing

from pathlib import Path
import pytest

EXEMPLAR = Path(__file__).resolve().parents[2] / "exemplars" / "gulf_karenia_brevis"


@pytest.fixture(scope="session")
def exemplar_dir():
    if not (EXEMPLAR / "atlantis.yaml").exists():
        pytest.skip("exemplar not present")
    return EXEMPLAR


# ── M-1d-i: a forked instance from how/templates/template_instance/answers.example.yaml (fictional, synthetic geometry) ──
import copy, json, shutil
import yaml

ANSWERS = Path(__file__).resolve().parents[3] / "how" / "templates" / "template_instance" / "answers.example.yaml"
GEOJSON = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"seg": 1}, "geometry": {"type": "Polygon", "coordinates": [[[-76.6, 35.2], [-76.2, 35.2], [-76.2, 35.5], [-76.6, 35.5], [-76.6, 35.2]]]}},
    {"type": "Feature", "properties": {"seg": 2}, "geometry": {"type": "Polygon", "coordinates": [[[-76.6, 34.9], [-76.2, 34.9], [-76.2, 35.2], [-76.6, 35.2], [-76.6, 34.9]]]}}]}


def example_answers() -> dict:
    return yaml.safe_load(ANSWERS.read_text())


def fork_into(d: Path, answers: dict | None = None, geometry: bool = True) -> int:
    from atlantis_core.fork import main
    d.mkdir(parents=True, exist_ok=True)
    if geometry:
        (d / "geometry").mkdir(exist_ok=True)
        (d / "geometry" / "example_sound_segments.geojson").write_text(json.dumps(GEOJSON))
    (d.parent / f"{d.name}_in").mkdir(exist_ok=True)
    f = d.parent / f"{d.name}_in" / "answers.yaml"   # same name for every fork: it is stamped into headers
    f.write_text(yaml.safe_dump(answers if answers is not None else example_answers(), sort_keys=False))
    return main(["--answers", str(f), "--out", str(d), "--atlantis-commit", "0" * 40, "--today", "2026-10-03"])


@pytest.fixture(scope="session")
def forked_master(tmp_path_factory):
    d = tmp_path_factory.mktemp("fork") / "inst"
    assert fork_into(d) == 0
    return d


@pytest.fixture
def forked(forked_master, tmp_path):
    """A private copy of the forked example, free to mutate."""
    d = tmp_path / "inst"
    shutil.copytree(forked_master, d)
    return d


def variant_answers() -> dict:
    """The dry run's shape (M-1d-i III F-1): no point stream, surveillance declared absent, a two-station mean at the primary."""
    a = example_answers()
    a["streams"] = [s for s in a["streams"] if s["shape"] != "point"]
    a["streams"][0]["stations"] = {"EXS01": [1], "EXS02": [1], "EXS03": [2]}
    a["streams"][0]["vitals"]["lags"] = [0, 1]
    a["surveillance"] = {"declared": "absent", "reason": "fixed sondes and gridded SST only; no stream's sampling reacts to what was seen"}
    return a


@pytest.fixture(scope="session")
def variant_master(tmp_path_factory):
    d = tmp_path_factory.mktemp("variant") / "inst"
    assert fork_into(d, variant_answers()) == 0
    return d


def persistent_answers() -> dict:
    """M-2a-i: the FKNMS shape, fictional. Polygon MPA zones, a `unit_daily` ABOVE event that accumulates (DHW-like),
    H = 8 with an onset refractory of 7 (R = H − 1 is the one that matches eval's lead-time onset — III F-4), gridded-only streams, surveillance declared absent (R8 → ablation N/A). The
    self-test runs it in the accumulating world by default (an above event with R > 0 on a daily stream)."""
    a = example_answers()
    a["instance"] = {"slug": "example_reef_heat", "name": "Example Reef heat stress", "vault": "ExampleReefHeat.aDNA",
                     "steward": "the steward's name or role"}
    a["patient"]["unit_kind"] = "mpa_zone"
    a["patient"]["region"] = {"code": "all", "name": "Example Reef", "external_id": "WDPA:0000000"}
    a["event"] = {"name": "Heat stress onset (DHW ≥ 4 °C-weeks within 8 weeks)", "stream": "atl_stream_example_dhw_daily",
                  "threshold": 4.0, "unit": "Cel.wk", "direction": "above", "horizon": 8, "refractory_weeks": 7,
                  "onset_rule": "drop zone-weeks whose carried DHW crossed 4 in t−7..t (refractory 7 = horizon − 1, the "
                                "lead-time onset: one episode, one onset); drop zone-weeks with no DHW in t+1..t+8 (unknown outcome)"}
    crw = {"modality": "gridded_field", "source_system": "NOAA Coral Reef Watch ERDDAP (illustrative)",
           "license": "public (NOAA CRW; credit CRW)", "surveillance_channel": False, "shape": "unit_daily",
           "fetcher": "CoralReefWatch"}
    a["streams"] = [
        {**crw, "stream_id": "atl_stream_example_dhw_daily", "source_id": "noaacrwdhwDaily",
         "authority": "NOAACRW:degree_heating_week", "variable": "degree_heating_week", "unit": "Cel.wk",
         "columns": {"date": "date", "value": "dhw", "unit": "seg"}, "vitals": {"group": "heat", "tag": "state", "lags": [0, 1, 4]},
         "fetch": {"base": "https://coastwatch.noaa.gov/erddap/griddap/noaacrwdhwDaily.csv", "variable": "degree_heating_week",
                   "years": [1985, 2023]}},
        {**crw, "stream_id": "atl_stream_example_sst_daily", "source_id": "noaacrwsstDaily",
         "authority": "CF:sea_surface_temperature", "variable": "sea_surface_temperature", "unit": "Cel",
         "columns": {"date": "date", "value": "sst", "unit": "seg"}, "vitals": {"group": "temperature", "tag": "proxy"},
         "fetch": {"base": "https://coastwatch.noaa.gov/erddap/griddap/noaacrwsstDaily.csv", "variable": "analysed_sst",
                   "years": [1985, 2023]}},
    ]
    a["climatology"] = {"atl_stream_example_sst_daily": [1991, 2010]}
    a["surveillance"] = {"declared": "absent", "reason": "satellite products only: no stream's sampling reacts to what was seen"}
    a["selftest"] = {"patients": [{"unit": 1}, {"unit": 2}]}
    return a


@pytest.fixture(scope="session")
def persistent_master(tmp_path_factory):
    d = tmp_path_factory.mktemp("persistent") / "inst"
    assert fork_into(d, persistent_answers()) == 0
    return d

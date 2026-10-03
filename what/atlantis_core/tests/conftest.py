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

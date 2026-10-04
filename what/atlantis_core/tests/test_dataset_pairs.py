"""Dataset-record pairs held to the lattice-labs schema they claim (M-1d-ii, WI-18). The template failed it four ways
before this card; each way is planted back and caught. Every committed pair passes, and its checksum IS its bytes."""
import copy
import hashlib
import json
import shutil

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from atlantis_core import datasets as DS

TEMPLATE = DS.ROOT / "how" / "templates" / "template_dataset_pair"
RECORDS = DS.ROOT / "what" / "datasets"


@pytest.fixture(scope="module")
def schema():
    return json.loads(DS.SCHEMA.read_text())


def errors(doc, schema):
    return [e.message for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc)]


@pytest.fixture
def tmpl():
    d = yaml.safe_load((TEMPLATE / "dataset_name.dataset.yaml").read_text())
    d["dataset"]["lineage"]["generation_timestamp"] = "2026-10-03T00:00:00Z"   # the one placeholder a format check reads
    return d


@pytest.mark.skipif(not DS.PEER_SCHEMA.exists(), reason="Archive.aDNA not beside Atlantis (public clone)")
def test_schema_copy_is_lattice_labs():
    assert DS.SCHEMA.read_bytes() == DS.PEER_SCHEMA.read_bytes()


def test_template_structure_passes_the_schema(tmpl, schema):
    assert errors(tmpl, schema) == []


@pytest.mark.parametrize("name,fn", [   # the four ways the pre-M-1d-ii template failed, planted back
    ("sha256 under storage", lambda d: d["storage"].update(sha256="ab" * 32)),
    ("location as a string", lambda d: d["storage"].update(location="Inst.aDNA/data/raw/x.parquet")),
    ("Rule-5 keys under lineage", lambda d: d["lineage"].update(source_system="FWC", ingested_at="2026-09-23")),
    ("upper-case name", lambda d: d.update(name="NAME")),
    ("a provider the enum lacks", lambda d: d["storage"].update(provider="zenodo")),
    ("an unknown location key", lambda d: d["storage"]["location"].update(url="https://x")),
    ("lineage timestamp not a date-time", lambda d: d["lineage"].update(generation_timestamp="2026-09-23")),
])
def test_template_regressions_fail_the_schema(tmpl, schema, name, fn):
    fn(tmpl["dataset"])
    assert errors(tmpl, schema), name


def test_committed_records_pass():
    res = DS.check_dir(RECORDS)
    assert set(res) == {f"dataset_{x}.dataset.yaml" for x in ("fwc_hab_karenia", "oisst_region_daily", "usgs_discharge_daily")}
    assert all(v == [] for v in res.values()), res
    assert DS.main(["--check", str(RECORDS)]) == 0


def test_records_pin_the_board_and_the_streams():
    """One sha256 per stream, everywhere it is written: the pair, the bytes, streams.yaml, board v1's data_pins."""
    streams = {s["stream_id"]: s["sha256"] for s in
               yaml.safe_load((DS.ROOT / "what/exemplars/gulf_karenia_brevis/streams.yaml").read_text())["observation_streams"]}
    pins = {p["stream_ref"]: p["sha256"] for p in json.loads(
        (DS.ROOT / "what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json").read_text())["evaluation"]["data_pins"]}
    for y in RECORDS.glob("*.dataset.yaml"):
        d = yaml.safe_load(y.read_text())["dataset"]
        sid, h = d["class_fields"]["atl_stream_id"], d["format"]["checksum"].removeprefix("sha256:")
        assert streams[sid] == pins[sid] == h == hashlib.sha256((DS.ROOT / d["storage"]["location"]["path"]).read_bytes()).hexdigest()


@pytest.fixture
def recs(tmp_path):
    d = tmp_path / "repo" / "what" / "datasets"
    shutil.copytree(RECORDS, d)
    (tmp_path / "repo" / ".git").mkdir()
    return d


def _edit_yaml(p, fn):
    d = yaml.safe_load(p.read_text()); fn(d["dataset"]); p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))


@pytest.mark.parametrize("fn,why", [
    (lambda d: d["format"].update(checksum="ab" * 32), "sha256:<64 hex>"),
    (lambda d: d["format"].update(checksum="sha256:" + "0" * 64), "do not hash"),
    (lambda d: d["storage"]["location"].update(path="../../../etc/x.parquet"), "escapes the repo"),
    (lambda d: d["class_fields"].pop("source_url"), "class_fields.source_url"),
    (lambda d: d["class_fields"].pop("atl_stream_id"), "atl_stream_id"),
    (lambda d: d.update(name="dataset_other"), "file stem"),
    (lambda d: d["storage"].update(sha256="x"), "schema:"),
])
def test_record_defects(recs, fn, why):
    y = recs / "dataset_oisst_region_daily.dataset.yaml"
    _edit_yaml(y, fn)
    errs = DS.check_dir(recs)[y.name]
    assert any(why in e for e in errs), errs


def test_md_must_agree(recs):
    md = recs / "dataset_usgs_discharge_daily.md"
    md.write_text(md.read_text().replace("sha256: 66a58af4", "sha256: 76a58af4"))
    assert any("≠ the yaml's checksum" in e for e in DS.check_dir(recs)["dataset_usgs_discharge_daily.dataset.yaml"])
    (recs / "dataset_fwc_hab_karenia.md").unlink()
    assert any("a record is a pair" in e for e in DS.check_dir(recs)["dataset_fwc_hab_karenia.dataset.yaml"])


def test_live_md_without_twin_fails_superseded_passes(recs):
    assert "dataset_hab_env_covariates.md" not in DS.check_dir(recs)          # superseded: no twin needed
    (recs / "dataset_new_stream.md").write_text("---\ntype: dataset\nstatus: active\n---\n")
    assert DS.check_dir(recs)["dataset_new_stream.md"]

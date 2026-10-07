"""how/templates/template_mapping_atl.yaml held to the atl_v0 schema (contract item 11). Each check is fed its defect."""
import copy
from pathlib import Path

import pytest
import yaml

from atlantis_core.mapping import SCHEMA, check

TEMPLATE = Path(__file__).resolve().parents[3] / "how" / "templates" / "template_mapping_atl.yaml"


@pytest.fixture(scope="module")
def schema():
    return yaml.safe_load(SCHEMA.read_text())


@pytest.fixture
def m():
    return yaml.safe_load(TEMPLATE.read_text())


def lab(m, cls):
    return next(l for l in m["labels"] if l["class"] == cls)


def rel(m, t):
    return next(r for r in m["relationships"] if r["rel_type"] == t)


def test_template_passes(m, schema):
    assert check(m, schema) == []
    assert len(m["labels"]) == 5 and len(m["relationships"]) == 6


DEFECTS = [
    ("label dropped", lambda m: m["labels"].pop(), "no label maps AtlEvaluation"),
    ("class doubled", lambda m: m["labels"].append(copy.deepcopy(m["labels"][0]) | {"label": "Dup"}), "mapped twice"),
    ("foreign class", lambda m: lab(m, "AtlVital").update({"class": "AtlObservation"}), "not one of the five"),
    ("wrong canonical id", lambda m: lab(m, "AtlVital").update({"canonical_id": "name"}), "not its identifier slot"),
    ("invented slot", lambda m: lab(m, "AtlVital")["properties"].update({"weight": "importance"}), "not a slot of AtlVital"),
    ("coordinate property", lambda m: lab(m, "AtlSpatialUnit")["properties"].update({"lat": "name"}), "coordinate-shaped"),
    ("pointer renamed", lambda m: lab(m, "AtlSpatialUnit")["properties"].update({"shape": "geometry_ref"}), "pointer slot"),
    ("source missing", lambda m: m["sources"].pop("vitals"), "has no entry in sources"),
    ("edge on a non-slot", lambda m: rel(m, "READS")["derivation"].update({"field": "stream"}), "is not a slot of AtlVital"),
    ("edge to wrong label", lambda m: rel(m, "EVALUATES")["derivation"].update({"target_label": "AtlSpatialUnit"}), "ranges over AtlEventDefinition"),
    ("list edge item", lambda m: rel(m, "PINS")["derivation"].update({"item_field": "sha"}), "item_field"),
    ("fence shape dropped", lambda m: m["fence"]["never_project"].remove("observation_long"), "missing 'observation_long'"),
    ("fence path dropped", lambda m: m["fence"]["deny_paths"].remove("data/**"), "missing 'data/\\*\\*'"),
    ("fence property dropped", lambda m: m["fence"]["deny_properties"].remove("lat"), "missing 'lat'"),
    ("data as a source", lambda m: m["sources"]["vitals"].append("data/processed/features.parquet"), "is fenced by"),
    ("scored table as a source", lambda m: m["sources"]["evaluations"].append("outputs/atlantis_core/metrics.json"), "is fenced by"),
    ("stamp missing", lambda m: m["stamps"].pop("valid_to"), "stamps.valid_to"),
    # III F-4: holes the first checker passed
    ("./ path past the fence", lambda m: m["sources"]["vitals"].append("./data/processed/vitals.yaml"), "is fenced by"),
    (".. path out of the instance", lambda m: m["sources"]["vitals"].append("../other/streams.yaml"), "is fenced by"),
    ("site output as a source", lambda m: m["sources"]["evaluations"].append("site/site_data.json"), "is fenced by"),
    ("template's csv fence deleted", lambda m: m["fence"]["deny_paths"].remove("**/*.csv"), "missing '\\*\\*/\\*.csv'"),
    ("template's site fence deleted", lambda m: m["fence"]["deny_paths"].remove("site/**"), "missing 'site/"),
    ("geojson unfenced", lambda m: m["fence"]["deny_properties"].remove("geojson"), "missing 'geojson'"),
    ("edge carries a coordinate", lambda m: rel(m, "PINS")["derivation"]["edge_properties"].append("lat"), "edge property 'lat'"),
    ("edge carries a non-slot", lambda m: rel(m, "PINS")["derivation"]["edge_properties"].append("p_actual"), "not a slot of AtlDataPin"),
    ("json property not projected", lambda m: lab(m, "AtlEvaluation")["json_properties"].append("predictions"), "not a projected property"),
    ("world time as validity", lambda m: m["stamps"].update(valid_from="captured_at"), "record time is not world time"),
    ("source not the projection", lambda m: m["stamps"].update(source="fwc"), "must name the projection"),
]


@pytest.mark.parametrize("name, defect, match", DEFECTS, ids=[d[0] for d in DEFECTS])
def test_check_refuses(m, schema, name, defect, match):
    defect(m)
    errs = check(m, schema)
    assert errs, f"{name}: the check passed a defective mapping"
    assert any(__import__("re").search(match, e) for e in errs), errs


def test_stale_ontology_pin_refused(m, schema):
    """M-1d-i: atl_v0 moved to 0.3.0, at M-1e to 0.4.0, and at M-2a-i to 0.5.0; a mapping still pinning an earlier version claims a schema
    the check did not read."""
    assert not check(m, schema)
    for stale in ("0.2.0", "0.3.0", "0.4.0"):
        m["ontology"]["version"] = stale
        assert any("ontology.version" in e for e in check(m, schema))

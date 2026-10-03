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
    ("stamp missing", lambda m: m["stamps"].pop("valid_to"), "missing 'valid_to'"),
]


@pytest.mark.parametrize("name, defect, match", DEFECTS, ids=[d[0] for d in DEFECTS])
def test_check_refuses(m, schema, name, defect, match):
    defect(m)
    errs = check(m, schema)
    assert errs, f"{name}: the check passed a defective mapping"
    assert any(__import__("re").search(match, e) for e in errs), errs

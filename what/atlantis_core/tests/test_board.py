"""board/ — the closed AtlEvaluation projection; GREEN-only; refuses unhonoured obligations."""
import json
from pathlib import Path

import pytest
import yaml

from atlantis_core import load_instance
from atlantis_core.board import BoardError, assert_green, emit, project, validate

FIXTURE = Path(__file__).resolve().parents[2] / "schema" / "atl_v0" / "fixtures" / "controls" / "pos_exemplar_gulf_karenia_brevis.yaml"


@pytest.fixture(scope="module")
def v0(exemplar_dir):
    """hab's metrics.json, given the two fields the core adds (surveillance-only vital name is read from config)."""
    m = json.loads((exemplar_dir / "outputs" / "metrics.json").read_text())
    m["semantic_hash"] = m["config_hash"]
    return load_instance(exemplar_dir), m


def test_projection_reproduces_the_v0_fixture(v0):
    """The emitter, fed hab's metrics.json, reproduces the hand-declared M-1c fixture's evaluation field for field."""
    inst, m = v0
    fx = yaml.safe_load(FIXTURE.read_text())["evaluations"][0]
    ev = project(m, inst, version=0, recorded_at=fx["recorded_at"], learner=fx["learner"],
                 shap_summary_ref=fx["shap_summary_ref"])
    assert ev == fx
    validate(ev)


def test_projection_is_closed(v0):
    inst, m = v0
    ev = project(m, inst, version=0, recorded_at="2026-10-02T00:00:00Z")
    validate(ev)
    with pytest.raises(BoardError, match="rejected"):
        validate({**ev, "n_trees": 141})        # an extra leaking into the closed class (WI-8)
    with pytest.raises(BoardError, match="rejected"):
        validate({**ev, "recorded_at": "yesterday"})   # the format checker is live


@pytest.mark.parametrize("bad", [{"p_actual": [0.1]}, {"x": {"shap": [1.0]}}, {"curve": list(range(100))}])
def test_assert_green_rejects_per_patient_content(bad):
    with pytest.raises(BoardError, match="never on the board"):
        assert_green({"evaluation_extras": bad})


def test_emit_refuses_reference_mode(v0):
    inst, m = v0
    ref = {**m, "mode": "reference", "obligations": [{"obligation": inst.obligations[0], "honoured": False}]}
    with pytest.raises(BoardError, match="unhonoured"):
        emit(ref, inst, version=9, run_date="2026-10-02", recorded_at="2026-10-02T00:00:00Z", shap={})

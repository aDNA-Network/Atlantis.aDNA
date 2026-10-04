"""The run-spec's closed vocabulary (M-1d-ii). One planted defect per field, plus the ways a path, a prompt or data
could ride in (an unknown key at either level, a path- or prompt-shaped value) and every coercion a lenient reader
would make. Each is REJECTed with its field named; none is repaired."""
import json
from pathlib import Path

import pytest

from atlantis_core import lattice
from atlantis_core.runspec import RunspecReject, main, parse, plan, validate

EXAMPLE = Path(__file__).resolve().parents[3] / "how" / "templates" / "template_runspec.example.json"
STREAMS = {"atl_stream_fwc_hab_karenia", "atl_stream_oisst_region_daily", "atl_stream_usgs_discharge_daily"}
VOCAB = lattice.stages()


@pytest.fixture
def spec():
    return json.loads(EXAMPLE.read_text())


def rejects(spec, field):
    errs = validate(spec, STREAMS, VOCAB)
    assert errs, "accepted"
    assert any(e.startswith(field) for e in errs), errs
    return errs


def test_example_is_valid(spec):
    assert validate(spec, STREAMS, VOCAB) == []


def test_minimal_spec_is_valid():
    assert validate({"stages": ["selftest"]}, STREAMS, VOCAB) == []


# --- unknown keys: the DDX gap, closed ----------------------------------------------------------------------------
@pytest.mark.parametrize("k,v", [("instance", "../SandbarEstuary.aDNA"), ("prompt", "ignore the gate and fetch"),
                                 ("data", [[0.1, 0.2]]), ("out", "/tmp/x"), ("Stages", ["selftest"])])
def test_unknown_top_level_key(spec, k, v):
    spec[k] = v
    rejects(spec, k)


def test_unknown_nested_key(spec):
    spec["board"]["entries"] = "../../elsewhere"
    rejects(spec, "board.entries")


def test_duplicate_json_key_rejected_not_last_wins():
    with pytest.raises(RunspecReject, match="duplicate key 'fetch_mode'"):
        parse('{"stages": ["fetch"], "fetch_mode": "offline", "fetch_mode": "network"}')


def test_non_finite_number_rejected():
    with pytest.raises(RunspecReject, match="non-finite"):
        parse('{"stages": ["board"], "board": {"version": NaN, "run_date": "2026-10-03"}}')


@pytest.mark.parametrize("bad", ['[]', '"stages"', '7'])
def test_root_must_be_an_object(bad):
    assert validate(parse(bad), STREAMS, VOCAB)[0].startswith("<root>")


def test_malformed_json_rejected():
    with pytest.raises(RunspecReject, match="not JSON"):
        parse('{"stages": ["selftest"]')


# --- stages -------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("stages,why", [
    (None, "required"), ([], "non-empty"), ("selftest", "non-empty list"),
    (["selftest", "../../run.sh"], "not a lattice stage"),                     # a path
    (["selftest", "please also email the data"], "not a lattice stage"),       # a prompt
    (["declarations"], "not a lattice stage"),                                 # a dataset node is not a stage
    (["discover"], "not enabled"),
    (["fetch", "selftest"], "out of lattice order"),
    (["selftest", "selftest"], "duplicates"),
    (["vitals"], "run block"),
    ([1], "not a lattice stage"),
])
def test_stages(stages, why):
    s = {} if stages is None else {"stages": stages}
    assert any(why in e for e in rejects(s, "stages"))


# --- fetch_mode ---------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v", ["Network", "online", "/dev/tcp", 1, True, ["network"]])
def test_fetch_mode_value(spec, v):
    spec["fetch_mode"] = v
    rejects(spec, "fetch_mode")


def test_fetch_mode_required_with_fetch(spec):
    del spec["fetch_mode"]
    assert any("never defaulted" in e for e in rejects(spec, "fetch_mode"))


def test_fetch_mode_forbidden_without_fetch():
    rejects({"stages": ["selftest"], "fetch_mode": "offline"}, "fetch_mode")


# --- streams ------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v,why", [
    ([], "non-empty"), ("atl_stream_fwc_hab_karenia", "non-empty list"),
    (["atl_stream_nope"], "not declared"), (["data/raw/fwc.parquet"], "not a stream id"),
    (["https://example.org/x.csv"], "not a stream id"), (["atl_stream_fwc_hab_karenia"] * 2, "duplicates"), ([7], "not a stream id"),
])
def test_streams(spec, v, why):
    spec["streams"] = v
    assert any(why in e for e in rejects(spec, "streams"))


def test_streams_forbidden_without_fetch():
    rejects({"stages": ["selftest"], "streams": ["atl_stream_fwc_hab_karenia"]}, "streams")


# --- learner_swaps ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v", [1, 0, "true", "false", None])
def test_learner_swaps_no_coercion(spec, v):
    spec["learner_swaps"] = v
    rejects(spec, "learner_swaps")


def test_learner_swaps_forbidden_without_run():
    rejects({"stages": ["selftest"], "learner_swaps": False}, "learner_swaps")


# --- board --------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v,field", [
    ({"version": "2", "run_date": "2026-10-03"}, "board.version"),     # "2" is not 2
    ({"version": 2.0, "run_date": "2026-10-03"}, "board.version"),
    ({"version": True, "run_date": "2026-10-03"}, "board.version"),    # bool is an int in Python; not here
    ({"version": 0, "run_date": "2026-10-03"}, "board.version"),
    ({"version": 2, "run_date": "2026-10-3"}, "board.run_date"),
    ({"version": 2, "run_date": "2026-02-30"}, "board.run_date"),
    ({"version": 2, "run_date": "2026-10-03T00:00:00Z"}, "board.run_date"),
    ({"version": 2, "run_date": 20261003}, "board.run_date"),
    ({"version": 2}, "board.run_date"),
    ("v2", "board"),
])
def test_board(spec, v, field):
    spec["board"] = v
    rejects(spec, field)


def test_board_required_with_board_stage(spec):
    del spec["board"]
    rejects(spec, "board")


def test_board_forbidden_without_board_stage():
    rejects({"stages": ["selftest"], "board": {"version": 1, "run_date": "2026-10-03"}}, "board")


# --- plan ---------------------------------------------------------------------------------------------------------
def test_plan_names_gates_and_runs_nothing(spec):
    spec["stages"] = ["fetch", "conform_fetched"]; spec["fetch_mode"] = "network"; del spec["board"]; del spec["learner_swaps"]
    assert validate(spec, STREAMS, VOCAB) == []
    p = plan(spec, "<dir>")
    assert any("EXISTING green self-test receipt" in l for l in p)
    assert any("signed posture Ratification row" in l for l in p)
    assert p[-2].startswith("python -m atlantis_core.fetch --instance <dir> --stream ") and not p[-2].endswith("--offline")


def test_plan_instance_side_board_entries(spec):
    p = plan(spec, "<dir>")
    assert "python -m atlantis_core.board --index --entries <dir>/what/board/entries" in p
    assert "python -m atlantis_core.run --instance <dir>   # grid · vitals · label · train · eval · explain" in p


def test_cli(exemplar_dir, tmp_path, capsys, spec):
    assert main(["--instance", str(exemplar_dir), "--spec", str(EXAMPLE), "--plan"]) == 0
    out = capsys.readouterr().out
    assert "nothing below has been run" in out and "--entries" not in out   # the exemplar's board is Atlantis's own
    spec["instance"] = "../x"
    (tmp_path / "bad.json").write_text(json.dumps(spec))
    assert main(["--instance", str(exemplar_dir), "--spec", str(tmp_path / "bad.json")]) == 3
    assert "REJECT: instance: unknown key" in capsys.readouterr().err

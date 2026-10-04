"""The pipeline lattice under all three checks (M-1d-ii). Each planted defect is caught by the check named for it — and
the two peer gaps (unknown fields, cycles) are recorded as gaps: the peer validator passes them, the stricter checks don't."""
import copy
import json

import pytest
import yaml

from atlantis_core import lattice as L

PEER_SCHEMA = L.PEER_TOOLS.parent / "lattice_yaml_schema.json"
needs_peer = pytest.mark.skipif(L.peer_validator() is None, reason="aDNA.aDNA not beside Atlantis (public clone)")


@pytest.fixture
def doc():
    return L.load()


def write(tmp_path, d, raw=None):
    p = tmp_path / "x.lattice.yaml"
    p.write_text(raw if raw is not None else yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
    return p


def nodes(d):
    return d["lattice"]["nodes"]


def test_committed_lattice_passes_all_three(doc):
    assert L.check_strict(doc) == []
    assert L.check_local(doc) == []
    assert L.check_peer(L.LATTICE) in ([], None)
    assert L.main([]) == 0


@needs_peer
def test_peer_actually_ran():
    assert L.check_peer(L.LATTICE) == []


@pytest.mark.skipif(not PEER_SCHEMA.exists(), reason="aDNA.aDNA not beside Atlantis (public clone)")
def test_local_schema_copy_is_the_peers():
    assert L.SCHEMA.read_bytes() == PEER_SCHEMA.read_bytes()


def test_stages_are_the_process_nodes_in_order():
    s = L.stages()
    assert s[0] == "discover" and s[-1] == "site"
    assert s.index("conform_declared") < s.index("selftest") < s.index("fetch") < s.index("conform_fetched") < s.index("board")
    assert not {"declarations", "raw_streams", "board_entry"} & set(s)


def test_every_documented_core_command_is_named(doc):
    cfgs = " ".join(json.dumps(n.get("config", {})) for n in nodes(doc))
    for m in ("conform", "selftest", "fetch", "run", "board", "site"):
        assert f"python -m atlantis_core.{m}" in cfgs


# --- planted defects -------------------------------------------------------------------------------------------------

@needs_peer
def test_unknown_node_field_strict_catches_peer_does_not(doc, tmp_path):
    nodes(doc)[3]["stage"] = "selftest"            # a field outside the node schema
    assert any("Additional properties" in e and "stage" in e for e in L.check_strict(doc))
    assert L.check_peer(write(tmp_path, doc)) == []  # the gap the card names: the peer never loads additionalProperties


def test_unknown_lattice_key_strict(doc):
    doc["lattice"]["owner"] = "proteus"
    assert any("owner" in e for e in L.check_strict(doc))


@needs_peer
def test_unquoted_version_strict_catches_peer_does_not(tmp_path):
    raw = L.LATTICE.read_text().replace('version: "0.1.0"', "version: 0.1")
    d = yaml.safe_load(raw)
    assert any("version" in e for e in L.check_strict(d))
    assert L.check_peer(write(tmp_path, None, raw)) and all("version" in e for e in L.check_peer(write(tmp_path, None, raw)))


@needs_peer
def test_dangling_edge_peer(doc, tmp_path):
    doc["lattice"]["edges"].append({"from": "board", "to": "nowhere"})
    assert any("nowhere" in e for e in L.check_peer(write(tmp_path, doc)))


@needs_peer
def test_cycle_local_catches_peer_does_not(doc, tmp_path):
    doc["lattice"]["edges"].append({"from": "site", "to": "grid", "label": "loop"})
    assert L.check_strict(doc) == []
    assert L.check_peer(write(tmp_path, doc)) == []   # neither peer check looks for cycles
    assert any("cycle" in e for e in L.check_local(doc))


def test_fetch_before_selftest_local(doc):
    E = doc["lattice"]["edges"]
    E[:] = [e for e in E if (e["from"], e["to"]) not in {("conform_declared", "selftest"), ("selftest", "fetch")}]
    E += [{"from": "conform_declared", "to": "fetch"}, {"from": "raw_streams", "to": "selftest"},
          {"from": "selftest", "to": "conform_fetched"}]
    errs = L.check_local(doc)
    assert any("selftest must dominate fetch" in e for e in errs)


def test_disconnected_local(doc):
    nodes(doc).append({"id": "orphan", "type": "process", "config": {"status": "planned"}})
    assert any("not connected" in e and "orphan" in e for e in L.check_local(doc))


def test_bogus_module_local(doc):
    next(n for n in nodes(doc) if n["id"] == "grid")["config"]["module"] = "atlantis_core.gird"
    assert any("gird" in e and "does not import" in e for e in L.check_local(doc))


def test_command_without_main_local(doc):
    next(n for n in nodes(doc) if n["id"] == "vitals")["config"]["invoked_by"] = "python -m atlantis_core.vitals --instance <instance>"
    assert any("atlantis_core.vitals" in e and "__main__" in e for e in L.check_local(doc))


def test_process_node_without_module_or_status_local(doc):
    del next(n for n in nodes(doc) if n["id"] == "discover")["config"]["status"]
    assert any("discover" in e and "module" in e for e in L.check_local(doc))


def test_missing_gate_stage_local(doc):
    d = copy.deepcopy(doc)
    nodes(d)[:] = [n for n in nodes(d) if n["id"] != "conform_fetched"]
    d["lattice"]["edges"] = [e for e in d["lattice"]["edges"] if "conform_fetched" not in (e["from"], e["to"])]
    d["lattice"]["edges"].append({"from": "raw_streams", "to": "grid"})
    assert any("conform_fetched" in e and "missing" in e for e in L.check_local(d))


# --- III review (M-1d-ii) F-4 · F-5 ------------------------------------------------------------------------------
def test_f4_bypass_edge_breaks_dominance(doc):
    """F-4 (C-020): 'a path selftest→fetch exists' passed with a bypass edge; the gate is dominance."""
    doc["lattice"]["edges"].append({"from": "declarations", "to": "fetch"})
    assert any("selftest must dominate fetch" in e for e in L.check_local(doc))


def test_f4_undeclared_flag(doc):
    next(n for n in nodes(doc) if n["id"] == "fetch")["config"]["command"] = \
        "python -m atlantis_core.fetch --instance <instance> --no-gate --network"
    errs = L.check_local(doc)
    assert any("['--network', '--no-gate']" in e for e in errs)


def test_f4_invoker_must_be_run(doc):
    next(n for n in nodes(doc) if n["id"] == "grid")["config"]["invoked_by"] = "python -m atlantis_core.board"
    assert any("only atlantis_core.run runs library stages" in e for e in L.check_local(doc))


def test_f4_run_block_matches_the_runspec(doc):
    del next(n for n in nodes(doc) if n["id"] == "explain")["config"]["invoked_by"]
    assert any("not the run-spec's run block" in e for e in L.check_local(doc))


def test_f4_main_guard_is_ast_not_text(tmp_path, monkeypatch):
    m = tmp_path / "fake_mod.py"
    m.write_text("# __main__ is mentioned only in this comment\ndef main(): pass\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert not L._has_main("fake_mod")
    m.write_text("def main(): pass\nif __name__ == '__main__':\n    main()\n")
    assert L._has_main("fake_mod")


def test_f5_dangling_edge_and_duplicate_id_local(doc, monkeypatch, capsys):
    """F-5 (C-015): with the peer absent, a dangling edge passed everything; local now re-checks it."""
    doc["lattice"]["edges"].append({"from": "selftest", "to": "ghost_node"})
    assert any("ghost_node" in e and "names no node" in e for e in L.check_local(doc))
    d2 = L.load(); nodes(d2).append(dict(nodes(d2)[0]))
    assert any("duplicate node id" in e for e in L.check_local(d2))
    monkeypatch.setattr(L, "PEER_TOOLS", L.ROOT / "nonexistent")
    assert L.main([]) == 0
    assert "did NOT run" in capsys.readouterr().out

"""BOARD.md generated from entries/ (M-1d-ii, WI-8) and `board --entries` for instances. The generator refuses rather
than renders anything it has not checked; the only open shape it shows is the one it names by id."""
import json
import shutil
from pathlib import Path

import pytest

from atlantis_core.board import index as IX
from atlantis_core.board.__main__ import ENTRIES, main

V0, V1 = "2026-09-23_gulf_karenia_brevis_v0", "2026-10-02_gulf_karenia_brevis_v1"


@pytest.fixture
def board(tmp_path):
    e = tmp_path / "repo" / "what" / "board" / "entries"
    shutil.copytree(ENTRIES, e)
    return e


def _edit(entries, eid, fn, as_name=None):
    p = entries / f"{eid}.json"
    d = json.loads(p.read_text()); fn(d)
    (entries / (as_name or p.name)).write_text(json.dumps(d, indent=1, ensure_ascii=False))


def test_committed_board_is_current():
    assert main(["--index", "--check"]) == 0


def test_render_is_byte_stable_and_timeless(board):
    a = IX.render(board); b = IX.render(board)
    assert a == b and a.endswith("\n") and not a.endswith("\n\n")
    assert "recorded_at" not in a and "T04:41" not in a
    assert a.index(V0) < a.index(V1)
    row = lambda eid: next(l for l in a.splitlines() if l.startswith(f"| [`{eid}`]"))
    assert "open shape — pre-atlantis_core" in row(V0)
    assert "closed `AtlEvaluation`" in row(V1)
    assert "THIS BOARD MAKES NO ACCURACY CLAIM" in a


def test_check_mode(board, capsys):
    assert main(["--index", "--entries", str(board), "--check"]) == 1          # missing
    assert "missing" in capsys.readouterr().out
    assert main(["--index", "--entries", str(board)]) == 0
    md = board.parent / "BOARD.md"; before = md.read_bytes()
    assert main(["--index", "--entries", str(board), "--check"]) == 0
    md.write_text(md.read_text().replace("0.5388", "0.5389"))                  # one byte
    assert main(["--index", "--entries", str(board), "--check"]) == 1
    assert md.read_text() != before.decode()                                   # --check never writes
    _edit(board, V1, lambda d: d.update(notes=d["notes"] + ["a new note"]))  # entries changed → stale
    main(["--index", "--entries", str(board)])
    assert md.read_bytes() == IX.render(board).encode()


@pytest.mark.parametrize("eid,fn,why", [
    (V1, lambda d: d["evaluation"].update(surprise=1), "not a closed AtlEvaluation and not grandfathered"),  # open, not grandfathered
    (V0, lambda d: d["evaluation"].pop("base_rate"), "base_rate"),                 # grandfathered still needs the minimum
    (V0, lambda d: d["evaluation"].update(alert_budgets=[]), "alert_budgets"),
    (V0, lambda d: d["evaluation"]["data_pins"][0].update(sha256="abc"), "sha256"),
    (V0, lambda d: d["evaluation"].pop("limitations_ref"), "limitations_ref"),
    (V1, lambda d: d.update(tier="AMBER"), "GREEN"),
    (V1, lambda d: d.update(accuracy_claim="AUROC 0.89"), "NONE"),
    (V1, lambda d: d["evaluation_extras"].update(predictions=[0.1, 0.2]), "never on the board"),
    (V0, lambda d: d["evaluation"].update(scores=[0.1, 0.2]), "not the pinned bytes"),
    (V1, lambda d: d["evaluation"].update(claim="operational_by_owner_ruling"), "owner_ruling_ref"),
    (V1, lambda d: d.update(source="partner"), "source"),
])
def test_refuses_unchecked_entries(board, eid, fn, why):
    _edit(board, eid, fn)
    with pytest.raises(IX.BoardError, match="REFUSING") as e:
        IX.render(board)
    assert why in str(e.value)


def test_grandfathered_entry_is_its_pinned_bytes(board):
    """An open evaluation has no closed key set; a smuggled key that dodges the denylist is stopped by the pin."""
    _edit(board, V0, lambda d: d["evaluation"].update(top_patients_by_risk="Naples · Sanibel"))
    with pytest.raises(IX.BoardError, match="not the pinned bytes"):
        IX.render(board)


def test_grandfathering_is_by_id_not_by_shape(board):
    """v0's bytes under another entry_id are refused — the fallback names one entry, not a class (C-015)."""
    _edit(board, V0, lambda d: d.update(entry_id="2026-10-03_other_v0"), as_name="2026-10-03_other_v0.json")
    with pytest.raises(IX.BoardError, match="2026-10-03_other_v0.json: not a closed AtlEvaluation"):
        IX.render(board)


def test_file_name_must_be_the_entry_id(board):
    shutil.copy(board / f"{V1}.json", board / "renamed.json")
    with pytest.raises(IX.BoardError, match="renamed.json: file name"):
        IX.render(board)


def test_not_json_refuses(board):
    (board / "x.json").write_text("{")
    with pytest.raises(IX.BoardError, match="not JSON"):
        IX.render(board)


@pytest.mark.parametrize("args,why", [
    (["--index", "--entries", "/tmp/somewhere"], "what/board/entries"),
    (["--index", "--instance", "x"], "does not emit"),
    (["--check"], "goes with --index"),
])
def test_cli_refusals(args, why, capsys):
    assert main(args) == 1
    assert why in capsys.readouterr().out


def test_emit_needs_its_arguments():
    with pytest.raises(SystemExit):
        main(["--instance", "x"])


# --- --entries: an instance writes its own board ---------------------------------------------------------------
@pytest.fixture
def instance_copy(exemplar_dir, tmp_path):
    """The exemplar's declarations + committed core outputs, laid out as an instance repo with its own board."""
    d = tmp_path / "Inst.aDNA"
    shutil.copytree(exemplar_dir, d, ignore=shutil.ignore_patterns("data", "site", ".venv", "figures", "src", "*.npz"))
    (d / "what" / "board" / "entries").mkdir(parents=True)
    return d


def test_entries_instance_side_emit_index_and_item9_reader(instance_copy, capsys):
    e = instance_copy / "what" / "board" / "entries"
    assert main(["--instance", str(instance_copy), "--version", "1", "--run-date", "2026-10-03", "--entries", str(e)]) == 0
    [f] = list(e.glob("*.json"))
    ent = json.loads(f.read_text())
    assert ent["provenance"]["metrics_file"] == "outputs/atlantis_core/metrics.json"       # relative to the instance repo
    assert not list(ENTRIES.glob("2026-10-03_*"))                                          # nothing landed in Atlantis
    assert main(["--index", "--entries", str(e)]) == 0 and (instance_copy / "what/board/BOARD.md").exists()
    # conform item 9's reader, as it runs it: closed · green · this instance's unit_ref and semantic_hash
    from atlantis_core.board import assert_green, validate
    from atlantis_core.config import load_instance, semantic_hash
    inst = load_instance(instance_copy)
    validate(ent["evaluation"]); assert_green(ent)
    assert ent["evaluation"]["unit_ref"] == inst.cfg["board"]["unit_ref"]
    assert ent["evaluation_extras"]["semantic_hash"] == semantic_hash(inst)
    assert main(["--instance", str(instance_copy), "--version", "1", "--run-date", "2026-10-03", "--entries", str(e)]) == 1  # SO-2


def test_an_outside_instance_cannot_write_atlantis_board(instance_copy, capsys):
    assert main(["--instance", str(instance_copy), "--version", "9", "--run-date", "2026-10-03"]) == 1
    assert "coordination memo" in capsys.readouterr().out
    assert not list(ENTRIES.glob("2026-10-03_*"))


def test_missing_entries_dir_writes_nothing(instance_copy, capsys):
    e = instance_copy / "elsewhere" / "what" / "board" / "entries"
    assert main(["--instance", str(instance_copy), "--version", "1", "--run-date", "2026-10-03", "--entries", str(e)]) == 1
    assert not e.exists()


# --- III review (M-1d-ii) F-1 · F-2 · F-3 · F-9 · F-11: each reviewer demonstration planted back -------------------
def test_f1_outputs_flag_cannot_smuggle_another_instances_metrics(instance_copy, exemplar_dir, capsys):
    """F-1 (C-018): the gate was on --outputs (a proxy), not on the instance; pointing --outputs at the exemplar wrote
    Atlantis's board from an outside instance."""
    o = str(exemplar_dir / "outputs" / "atlantis_core")
    assert main(["--instance", str(instance_copy), "--version", "9", "--run-date", "2026-10-03", "--outputs", o]) == 1
    assert "is not inside the repo" in capsys.readouterr().out
    e = instance_copy / "what" / "board" / "entries"
    assert main(["--instance", str(instance_copy), "--version", "9", "--run-date", "2026-10-03", "--outputs", o,
                 "--entries", str(e)]) == 1
    assert "is not inside the instance" in capsys.readouterr().out
    assert not list(ENTRIES.glob("2026-10-03_*")) and not list(e.glob("*.json"))


@pytest.mark.parametrize("eid,fn,why", [
    (V1, lambda d: d.update(superseded_by="nothing |\n\n## ⚠ OPERATIONAL FORECAST — AUROC 0.99, deploy now\n\n| x"),
     "names no entry"),
    (V1, lambda d: d.update(smuggled="## heading"), "unknown top-level key"),
    (V1, lambda d: d["evaluation"].update(limitations_ref="README §12\n\n## Validated operational model |"), "line break"),
    (V1, lambda d: d["evaluation"]["ablations"][0].update(ablation_name="x ## y"), "line break"),
    (V1, lambda d: d.update(entry_id="x"), "is not <YYYY-MM-DD>_<stem>_v<n>"),
])
def test_f2_entry_content_cannot_write_markdown(board, eid, fn, why):
    _edit(board, eid, fn)
    with pytest.raises(IX.BoardError, match="REFUSING") as e:
        IX.render(board)
    assert why in str(e.value)


def test_f2_pipe_is_escaped_not_a_column(board):
    _edit(board, V1, lambda d: d["evaluation"].update(limitations_ref="a | b"))
    row = next(l for l in IX.render(board).splitlines() if l.startswith(f"- **`{V1}`**"))
    assert "a \\| b" in row


def test_f9_supersession_is_derived(board):
    a = IX.render(board)
    assert next(l for l in a.splitlines() if l.startswith(f"| [`{V0}`]")).endswith(f"superseded → `{V1}` |")
    assert next(l for l in a.splitlines() if l.startswith(f"| [`{V1}`]")).endswith("| live |")
    _edit(board, V1, lambda d: d.update(superseded_by=V0))           # names an entry, but disagrees with the derivation
    with pytest.raises(IX.BoardError, match="disagrees with the derived"):
        IX.render(board)


def test_f11_check_compares_bytes(board, capsys):
    assert main(["--index", "--entries", str(board)]) == 0
    md = board.parent / "BOARD.md"
    md.write_bytes(md.read_bytes().replace(b"\n", b"\r\n"))
    assert main(["--index", "--entries", str(board), "--check"]) == 1


def _git(d, *c):
    import subprocess
    r = subprocess.run(["git", "-C", str(d), *c], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_f3_regenerate_fails_closed(instance_copy, tmp_path, capsys):
    """F-3 (C-021): origin/main was hard-coded and a git error read as 'never published'."""
    e = instance_copy / "what" / "board" / "entries"
    args = ["--instance", str(instance_copy), "--version", "1", "--run-date", "2026-10-03", "--entries", str(e)]
    assert main(args) == 0
    assert main(args + ["--regenerate", "probe"]) == 1                     # not a git repo: cannot tell → refuse
    assert "cannot tell" in capsys.readouterr().out
    _git(instance_copy, "init", "-q", "-b", "master"); _git(instance_copy, "add", "what")
    _git(instance_copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "entry")
    assert main(args + ["--regenerate", "probe"]) == 1                     # no remote/upstream: cannot tell → refuse
    remote = tmp_path / "remote.git"; _git(tmp_path, "init", "-q", "--bare", str(remote))
    _git(instance_copy, "remote", "add", "origin", str(remote)); _git(instance_copy, "push", "-q", "-u", "origin", "master")
    assert main(args + ["--regenerate", "probe"]) == 1                     # pushed on master (not main) → refuse
    assert "has reached a remote" in capsys.readouterr().out

"""fetch CLI (M-1d-i, WI-15): gated on the self-test receipt (contract item 6); --verify re-hashes pins; no socket, ever."""
import json, shutil, socket

import pytest
import yaml

from atlantis_core import load_instance, semantic_hash
from atlantis_core.fetch.__main__ import main as fetch_main
from atlantis_core.selftest import RECEIPT, receipt_problem, write_receipt

USGS = "atl_stream_usgs_discharge_daily"


@pytest.fixture(autouse=True)
def no_sockets(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a socket was opened")
    monkeypatch.setattr(socket.socket, "connect", boom)


@pytest.fixture
def inst_dir(exemplar_dir, tmp_path):
    """The exemplar's declarations only — no data/, so every stream is declared, not fetched."""
    for f in ("atlantis.yaml", "streams.yaml", "features.yaml", "events.yaml"):
        shutil.copy(exemplar_dir / f, tmp_path / f)
    return tmp_path


def _receipt(d):
    inst = load_instance(d)
    write_receipt(inst, {"vitals": len(inst.vitals), "patients": [4, 7]})


class Boom:
    def get(self, *a, **k):
        raise AssertionError("network touched")


class FakeNWIS:
    """One NWIS daily-values reply per site: two days of flow (one negative — clip_negative must zero it)."""
    def __init__(self): self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(params["sites"])
        body = {"value": {"timeSeries": [{"values": [{"value": [{"dateTime": "2020-01-01T00:00:00.000", "value": "12.5"},
                                                               {"dateTime": "2020-01-02T00:00:00.000", "value": "-3"}]}]}]}}
        return type("R", (), {"json": lambda self: body, "raise_for_status": lambda self: None, "status_code": 200, "text": ""})()


def test_refuses_without_receipt(inst_dir, capsys):
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS], session=Boom()) == 1
    assert "no self-test receipt" in capsys.readouterr().out
    assert not (inst_dir / "data").exists()


def test_refuses_stale_receipt(inst_dir, capsys):
    _receipt(inst_dir)
    assert receipt_problem(load_instance(inst_dir)) is None
    f = inst_dir / "features.yaml"; doc = yaml.safe_load(f.read_text())
    doc["vitals"][1]["lag"] = 2                                  # a vitals change after the self-test
    f.write_text(yaml.safe_dump(doc, sort_keys=False))
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS], session=Boom()) == 1
    assert "re-run it (SO-7)" in capsys.readouterr().out


@pytest.mark.parametrize("edit,why", [
    (lambda r: r.__setitem__("passed", False), "does not record a pass"),
    (lambda r: r.__setitem__("streams", r["streams"][:1]), "covers streams"),
])
def test_receipt_tampering_refused(inst_dir, edit, why):
    _receipt(inst_dir)
    p = inst_dir / RECEIPT; r = json.loads(p.read_text()); edit(r); p.write_text(json.dumps(r))
    assert why in receipt_problem(load_instance(inst_dir))


def test_offline_never_touches_network(inst_dir, capsys):
    _receipt(inst_dir)
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS, "--offline"], session=Boom()) == 1
    assert "offline: would fetch" in capsys.readouterr().out


def test_declared_fetcher_says_so(inst_dir, capsys):
    s = inst_dir / "streams.yaml"; doc = yaml.safe_load(s.read_text())
    next(x for x in doc["observation_streams"] if x["stream_id"] == USGS)["fetcher"] = "NDBCStdmet"
    s.write_text(yaml.safe_dump(doc, sort_keys=False))
    _receipt(inst_dir)
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS], session=Boom()) == 1
    assert "declared, not built" in capsys.readouterr().out


def test_fetch_then_verify(inst_dir, capsys):
    """End to end through a fake session: artifact + Rule-5 summary written, values to record printed; then --verify
    agrees, and catches a flipped byte and a registry pin that names other bytes."""
    _receipt(inst_dir)
    sess = FakeNWIS()
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS], session=sess) == 0
    out = capsys.readouterr().out
    inst = load_instance(inst_dir)
    spec = inst.stream_spec(USGS)
    assert len(sess.calls) == len(spec["fetch"]["sites"]) and "record in streams.yaml" in out
    summ = json.loads((inst_dir / spec["summary"]).read_text())
    assert summ["fetched_at_source"] == "fetch" and summ["rows"] == 2 * len(spec["fetch"]["sites"])
    # the registry still pins the exemplar's bytes, not these → verify names the mismatch
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS, "--verify"]) == 1
    assert "streams.yaml sha256" in capsys.readouterr().out
    s = inst_dir / "streams.yaml"; doc = yaml.safe_load(s.read_text())
    next(x for x in doc["observation_streams"] if x["stream_id"] == USGS)["sha256"] = summ["sha256"]
    s.write_text(yaml.safe_dump(doc, sort_keys=False))
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS, "--verify"]) == 0
    art = inst_dir / spec["artifact"]; b = bytearray(art.read_bytes()); b[len(b) // 2] ^= 0xFF; art.write_bytes(bytes(b))
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS, "--verify"]) == 1
    assert "the cache changed under its pin" in capsys.readouterr().out


def test_verify_declared_stream(inst_dir, capsys):
    assert fetch_main(["--instance", str(inst_dir), "--stream", USGS, "--verify"]) == 1
    assert "declared, not fetched" in capsys.readouterr().out


def test_receipt_semantic_hash_is_the_configs(inst_dir):
    _receipt(inst_dir)
    inst = load_instance(inst_dir)
    assert json.loads((inst_dir / RECEIPT).read_text())["semantic_hash"] == semantic_hash(inst)

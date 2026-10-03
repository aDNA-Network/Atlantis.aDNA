"""atlantis_core.fork (M-1d-i): a conformant instance from templates alone — every refusal fed its defect, the result held
to the registry checks, the mapping check and the self-test, and the self-test seen to FAIL in the forked world."""
import copy, json

import numpy as np

import pytest
import yaml

from atlantis_core import load_instance, label
from atlantis_core import selftest as st
from atlantis_core.fork import ForkError, render
from atlantis_core.mapping import SCHEMA, check as mcheck
from atlantis_core.vitals import ops
from conftest import example_answers, fork_into

WRITTEN = ["atlantis.yaml", "units.yaml", "streams.yaml", "features.yaml", "events.yaml", "mapping.yaml",
           "who/governance/adr_001_data_posture.md", "how/federation/atlantis/CLAUDE.md", ".gitignore"]


def test_fork_writes_declarations_only(forked_master):
    for f in WRITTEN:
        assert (forked_master / f).is_file(), f
    assert not (forked_master / "data").exists() and not (forked_master / "outputs").exists()   # no data, no fetch


def test_forked_registries_check_and_validate(forked_master):
    from jsonschema import validators
    from atlantis_core.conform import JSON_SCHEMA
    inst = load_instance(forked_master)                        # R1–R8
    assert len(inst.streams) == 3 and inst.event["direction"] == "below"
    S = json.loads(JSON_SCHEMA.read_text()); V = validators.validator_for(S)(S, format_checker=validators.validator_for(S).FORMAT_CHECKER)
    for f in ("units.yaml", "streams.yaml", "features.yaml", "events.yaml"):
        assert not list(V.iter_errors(yaml.safe_load((forked_master / f).read_text()))), f
    streams = yaml.safe_load((forked_master / "streams.yaml").read_text())["observation_streams"]
    assert all("sha256" not in s and "ingested_at" not in s for s in streams)   # declared (atl_v0 0.3.0)


def test_forked_mapping_checks(forked_master):
    m = yaml.safe_load((forked_master / "mapping.yaml").read_text())
    assert m["instance"] == "example_sound_hypoxia" and m["stamps"]["source"] == "example_sound_hypoxia_project"
    assert mcheck(m, yaml.safe_load(SCHEMA.read_text())) == []


def test_federation_pin_and_posture_stub(forked_master):
    txt = (forked_master / "how/federation/atlantis/CLAUDE.md").read_text()
    assert "source_commit: " + "0" * 40 in txt and 'ruling: "who/governance/adr_001_data_posture.md"' in txt
    adr = (forked_master / "who/governance/adr_001_data_posture.md").read_text()
    assert "status: proposed" in adr and "`public`" in adr


def test_fork_is_deterministic(tmp_path):
    assert fork_into(tmp_path / "a") == 0 and fork_into(tmp_path / "b") == 0
    for f in WRITTEN:
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes(), f


def test_forked_selftest_passes(forked):
    r = st.run(load_instance(forked), verbose=False)
    ev = "atl_stream_example_do_daily"
    assert r["streams"][ev].get("C3") == "ok"              # presence on a station-keyed (daily) event stream
    assert r["C5_direction"] == "above"                    # a below instance exercises the mirror tail
    assert all(v["C7"] == "ok" for v in r["streams"].values())


# -- the instrument must be seen to fail in the forked world (M-1c lesson) ---------------------------------------------
def test_forked_selftest_catches_horizon_overreach(forked, monkeypatch):
    orig = label.make
    def overreach(inst_, table, evs, units, weeks, event=None, lcfg=None):
        ev = dict(event or inst_.event); ev["horizon"] = int(ev["horizon"]) + 1
        return orig(inst_, table, evs, units, weeks, event=ev, lcfg=lcfg)
    monkeypatch.setattr(label, "make", overreach)
    with pytest.raises(st.LeakError, match="C2"):
        st.run(load_instance(forked), verbose=False)


def test_forked_selftest_catches_deaf_label(forked, monkeypatch):
    orig = label.make
    def deaf(inst_, table, evs, units, weeks, event=None, lcfg=None):
        t = orig(inst_, table, evs, units, weeks, event=event, lcfg=lcfg); t["y"] = 0; return t
    monkeypatch.setattr(label, "make", deaf)
    with pytest.raises(st.LeakError, match="C1"):
        st.run(load_instance(forked), verbose=False)


def test_forked_selftest_catches_future_weekly_min(forked, monkeypatch):
    """A weekly minimum that also reads next week — the below event's own aggregate, leaking."""
    monkeypatch.setattr(ops.Evaluator, "f_weekly_min",
                        lambda self, x, window=None: ops.Weekly((lambda w: np.fmin(w, w.shift(-1)))(self._aggregate(x, "min").df)))
    with pytest.raises(st.LeakError, match="C1 LEAK atl_stream_example_do_daily"):
        st.run(load_instance(forked), verbose=False)


def test_forked_lag1_daily_vital_not_vacuous(forked):
    """M-1d-i finding: the primary's daily gap week avoids the stream's own lags (a lag-1 mean was NaN at t → C4)."""
    inst = load_instance(forked)
    assert st.gap_week(inst, "atl_stream_example_do_daily") == 3        # lags {0,1,2} → one past the span
    assert st.gap_week(inst, "atl_stream_example_sst_daily") == 2       # lags {0,1} → one past the span


def test_exemplar_gaps_unchanged(exemplar_dir):
    inst = load_instance(exemplar_dir)
    assert [st.gap_week(inst, s) for s in sorted(inst.streams)] == [4, 1, 1]   # the exemplar's world, byte-for-byte


# -- refusals: each fed its defect -----------------------------------------------------------------------------------
def _edit(path, value):
    def f(a):
        cur = a
        for k in path[:-1]:
            cur = cur[k]
        if value is DEL:
            cur.pop(path[-1])
        else:
            cur[path[-1]] = value
    return f


DEL = object()


@pytest.mark.parametrize("fn,why", [
    (_edit(["instance", "slug"], "Example-Sound"), "instance.slug"),
    (_edit(["posture", "class"], "secret"), "posture.class"),
    (_edit(["patient", "unit_kind"], "bay"), "UnitKind"),
    (_edit(["patient", "time_step"], "month"), "ISO weeks only"),
    (_edit(["event", "direction"], "sideways"), "event.direction"),
    (_edit(["event", "onset_rule"], DEL), "event.onset_rule missing"),
    (_edit(["event", "stream"], "atl_stream_nope"), "is not a declared stream"),
    (_edit(["patient", "grid", "path"], "geometry/nope.geojson"), "not found inside the instance"),
    (lambda a: (a["patient"].__setitem__("grid", {"kind": "rules", "rules": [{"id": 1, "rule": "True"}]}),
                a["posture"].__setitem__("class", "partner")), "public posture only"),
    (_edit(["patient", "units"], [{"code": 1}, {"code": 1}]), "duplicate codes"),
    (lambda a: a["streams"][0].__setitem__("modality", "telepathy"), "Modality"),
    (lambda a: a["streams"][0].pop("license"), "license missing"),
    (lambda a: a["streams"][0].__setitem__("stream_id", "do_daily"), "atl_stream_<snake>"),
    (lambda a: a["streams"][0].pop("stations"), "station_daily needs stations"),
    (lambda a: a["streams"][1].__setitem__("vitals", {"tag": "lever"}), "lever without an owner"),
    (lambda a: a["streams"][1].__setitem__("vitals", {"tag": "driver"}), "VitalTag"),
    (lambda a: a["selftest"].__setitem__("patients", a["selftest"]["patients"][:1]), "≥ 2"),
    (lambda a: a["streams"][0].__setitem__("stations", {"EXS09": [9]}), "reaches no self-test patient"),
    (lambda a: [p.pop("lat") for p in a["selftest"]["patients"]], "needs lat/lon"),
    (_edit(["split", "test_end"], DEL), "split: needs"),
])
def test_fork_refuses(tmp_path, capsys, fn, why):
    a = example_answers(); fn(a)
    assert fork_into(tmp_path / "x", a) == 1
    assert why in capsys.readouterr().err
    assert not (tmp_path / "x" / "atlantis.yaml").exists()           # nothing written on a refusal


def test_fork_refuses_to_overwrite(forked, capsys):
    assert fork_into(forked) == 1
    assert "would overwrite" in capsys.readouterr().err


def test_render_refuses_unresolved_token():
    with pytest.raises(ForkError, match="unresolved token"):
        render("a: {{known}}\nb: {{unknown}}\n", {"known": 1}, "t")


def test_template_tokens_all_resolved_by_fork():
    """Every token in every template is one fork fills (a token added to a template without a value is a defect)."""
    import re
    from atlantis_core.fork import MAPPING_TEMPLATE, TEMPLATES, TOKEN, _values, SCHEMA as FS
    from pathlib import Path
    import tempfile
    toks = set()
    for p in list(TEMPLATES.glob("*.tmpl")) + [MAPPING_TEMPLATE]:
        toks |= set(TOKEN.findall(p.read_text()))
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "geometry").mkdir()
        (Path(d) / "geometry" / "example_sound_segments.geojson").write_text("{}")
        vals, errs = _values(example_answers(), yaml.safe_load(FS.read_text()), Path(d), "c", "2026-10-03", "a.yaml", "001")
    assert not errs and toks <= set(vals), sorted(toks - set(vals))

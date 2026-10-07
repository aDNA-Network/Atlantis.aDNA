"""atlantis_core.fork (M-1d-i): a conformant instance from templates alone — every refusal fed its defect, the result held
to the registry checks, the mapping check and the self-test, and the self-test seen to FAIL in the forked world."""
import copy, json, shutil

import pandas as pd

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


# -- the instrument must be seen to fail in the forked worlds (M-1c lesson; M-1d-i III F-1: the WHOLE catalogue) ----------
import test_selftest as T

_orig_make = label.make
_orig_weekly = ops.Evaluator.weekly


def _overreach(i, table, evs, units, weeks, event=None, lcfg=None):
    ev = dict(event or i.event); ev["horizon"] = int(ev["horizon"]) + 1
    return _orig_make(i, table, evs, units, weeks, event=ev, lcfg=lcfg)


def _deaf(i, *a, **k):
    t = _orig_make(i, *a, **k); t["y"] = 0; return t


def _rowlag(self, node, window=None, lag=0):
    df = _orig_weekly(self, node, window, 0)
    return df.apply(lambda c: c.dropna().shift(int(lag or 0)).reindex(c.index))


CATALOGUE = [   # (name, object, attribute, sabotage factory, check that must name it)
    ("in_event_next_week", label, "make", lambda: T._label_variant("in_event_next_week"), "C1 LEAK"),
    ("in_event_bfill", label, "make", lambda: T._label_variant("in_event_bfill"), "C1 LEAK"),       # III F-1: passed before
    ("label_rowshift", label, "make", lambda: T._label_variant("label_rowshift"), "C2 "),            # III F-1: passed before
    ("short_horizon", label, "make", lambda: T._label_variant("short_horizon"), "C4|C2b"),           # was a TypeError at H = 2
    ("overreach", label, "make", lambda: _overreach, "C2 "),
    ("deaf_label", label, "make", lambda: _deaf, "C1 "),
    ("weekmajor", st, "build", lambda: T._build_weekmajor, "C0|C1"),
    ("row_lag", ops.Evaluator, "weekly", lambda: _rowlag, "C8"),                                     # III F-2: passed before
    ("weekly_min_next", ops.Evaluator, "f_weekly_min",
     lambda: (lambda self, x, window=None: ops.Weekly((lambda w: np.fmin(w, w.shift(-1)))(self._aggregate(x, "min").df))), "C1 LEAK|C8"),
    ("weekly_mean_next", ops.Evaluator, "f_weekly_mean",
     lambda: (lambda self, x, window=None: ops.Weekly((lambda w: (w + w.shift(-1)) / 2)(self._aggregate(x, "mean").df))), "C8|C1"),
    ("weekly_mean_bfill", ops.Evaluator, "f_weekly_mean",
     lambda: (lambda self, x, window=None: ops.Weekly(self._aggregate(x, "mean").df.bfill(limit=2))), "C1 LEAK"),
    ("weekly_count_future", ops.Evaluator, "f_weekly_count",
     lambda: (lambda self, x, window=None: ops.Weekly(self._aggregate(x, "count", fill=0).df.iloc[::-1].cumsum().iloc[::-1])), "C3|C1|C0"),
]


# Where a world reaches a defect by a different road, it is named here, not widened for every world (M-2a-i finding): the
# persistent world has no weekly_min vital (an above event reads weekly_max; SST is a mean), so a leaky weekly_min reaches
# only C5's mirror-direction label — and C5 names it.
WORLD_EXPECT = {("weekly_min_next", "persistent_master"): "C5 below"}


@pytest.mark.parametrize("world", ["forked_master", "variant_master", "persistent_master"])   # M-2a-i: + the persistent world (C-014)
@pytest.mark.parametrize("name,obj,attr,factory,check", CATALOGUE, ids=[c[0] for c in CATALOGUE])
def test_forked_selftest_catches_catalogue(request, monkeypatch, world, name, obj, attr, factory, check):
    check = WORLD_EXPECT.get((name, world), check)
    inst = load_instance(request.getfixturevalue(world))
    monkeypatch.setattr(obj, attr, factory())
    with pytest.raises(st.LeakError, match=check):
        st.run(inst, verbose=False)


def test_variant_selftest_passes(variant_master):
    r = st.run(load_instance(variant_master), verbose=False)
    assert r["streams"]["atl_stream_example_do_daily"].get("C3") == "ok" and r["C5_direction"] == "above"
    assert all(v["C8_vitals"] >= 1 for v in r["streams"].values())


def test_forked_lag1_daily_vital_not_vacuous(forked):
    """M-1d-i: the primary's gap week avoids the stream's own lags (a lag-1 mean was NaN at t → C4). III F-2: that leaves no
    gap for C0 to cross, so C8 (calendar-lag invariance) guards those lags; the catalogue's row_lag case proves it."""
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
        import conftest   # III F-2: fork now reads the zone file (duplicate ids), so the placeholder must be a real one
        (Path(d) / "geometry" / "example_sound_segments.geojson").write_text(json.dumps(conftest.GEOJSON))
        vals, errs = _values(example_answers(), yaml.safe_load(FS.read_text()), Path(d), "c", "2026-10-03", "a.yaml", "001")
    assert not errs and toks <= set(vals), sorted(toks - set(vals))


# -- M-1d-i III F-4 / F-6 / F-8 ---------------------------------------------------------------------------------------
@pytest.mark.parametrize("fn,why", [
    (lambda a, d: a["patient"]["grid"].__setitem__("path", str(d / "geometry" / "example_sound_segments.geojson")), "must be a relative path"),
    (lambda a, d: a["patient"]["grid"].__setitem__("path", "../elsewhere.geojson"), "must be a relative path"),
    (lambda a, d: (a["patient"].__setitem__("grid", {"kind": "cells", "res": 0.25, "bbox": [-77, 35, -76, 36]}),
                   a["posture"].__setitem__("class", "partner")), "public posture only"),
    (lambda a, d: a["patient"]["units"][0].__setitem__("geometry_ref", "/tmp/zones.geojson#1"), "points outside the instance"),
    (lambda a, d: a["streams"][1].__setitem__("fetch", {"base": "https://x"}), "lacks ['variable', 'boxes', 'years']"),
    (lambda a, d: a.__setitem__("surveillance", {"declared": "absent"}) or [s.__setitem__("surveillance_channel", False) for s in a["streams"]],
     "fail the registry check"),                                             # F-6: R8 refused BEFORE writing
    (lambda a, d: a.__setitem__("vitals", [{"vital_id": "atl_vital_x", "stream_ref": "atl_stream_example_sst_daily",
                                            "transform": "weekly_mean(value)", "lag": 0, "group": "g", "tag": "lever"}]), "R4"),
])
def test_fork_refuses_iii(tmp_path, capsys, fn, why):
    a = example_answers(); fn(a, tmp_path / "x")
    assert fork_into(tmp_path / "x", a) == 1
    assert why in capsys.readouterr().err
    assert not (tmp_path / "x" / "atlantis.yaml").exists() and not (tmp_path / "x" / ".gitignore").exists()


def test_fork_pins_the_zone_file_by_its_bytes_and_the_selftest_refuses_a_moved_vertex(forked):
    """M-2a-i (C-023): the pin is computed from the file fork found, and the real build path (make_grid, which the self-test
    and vitals both call) refuses the moment one vertex moves — before any vital is computed."""
    from atlantis_core.grid import GridPinError, file_sha256
    g = load_instance(forked).cfg["grid"]
    assert g["sha256"] == file_sha256(forked / g["path"])
    p = forked / g["path"]
    p.write_text(p.read_text().replace("-76.2, 35.5", "-76.2, 35.51", 1))
    with pytest.raises(GridPinError, match="grid.sha256 mismatch"):
        st.run(load_instance(forked), verbose=False)



# ── M-2a-i: the onset refractory, planted in the real label path of the persistent world (C-009) ──────────────────────
from atlantis_core.vitals import grammar as _grammar


def _refractory_variant(mode):
    """Each mode is a label.make that is wrong about the refractory in one way; C1 or C9 must name it."""
    def make(inst_, table, evs, units, weeks, event=None, lcfg=None):
        ev = dict(event or inst_.event); lc = lcfg or inst_.cfg["label"]
        R = int(ev.get("refractory_weeks") or 0)
        if mode in ("short", "long"):
            ev["refractory_weeks"] = R - 1 if mode == "short" else R + 1
            return _orig_make(inst_, table, evs, units, weeks, event=ev, lcfg=lcfg)
        bare = {k: v for k, v in ev.items() if k != "refractory_weeks"}
        t = _orig_make(inst_, table, evs, units, weeks, event=bare if mode != "future" else ev, lcfg=lcfg)
        if mode == "ignored":
            return t
        consts = list(inst_.cfg.get("constants", {}))
        thr, s_ = float(ev["threshold"]), evs[ev["event_variable_stream"]]
        if mode == "future":                  # the refractory window centred on t: it also looks at t+1
            sig = s_.weekly(_grammar.parse(lc["signal"], consts))
            add = sig.shift(-1).ge(thr)
        elif mode == "from_horizon":          # the drop computed after the horizon cut: on the FUTURE signal
            sig = s_.weekly(_grammar.parse(lc["signal"], consts))
            add = sum(sig.shift(-k).ge(thr).astype(int) for k in range(1, int(ev["horizon"]) + 1)).gt(0)
        elif mode == "raw":                    # III F-7: the window on the RAW signal, ignoring the documented carry
            sig = s_.weekly(_grammar.parse(lc["signal"], consts))
            add = sum(sig.shift(k).ge(thr).astype(int) for k in range(1, R + 1)).gt(0)
        elif mode == "rows":                   # III F-7: R counted in observed rows, not calendar weeks
            car = s_.weekly(_grammar.parse(lc["signal"], consts)).ffill(limit=int(lc["last_known_weeks"]))
            add = pd.DataFrame({c: sum(car[c].dropna().ge(thr).shift(k, fill_value=False).astype(int) for k in range(1, R + 1))
                                .gt(0).reindex(car.index, fill_value=False) for c in car.columns})
        else:                                  # "weekly_mean": the refractory reads a different aggregate than the label
            m = s_.weekly(_grammar.parse("weekly_mean(value)", consts)).ge(thr)
            add = sum(m.shift(k, fill_value=False).astype(int) for k in range(1, R + 1)).gt(0)
        t["already_in_event"] = t["already_in_event"].values | label._cut(add, units, weeks).fillna(False).astype(bool).values
        return t
    return make


@pytest.mark.parametrize("mode,check", [
    ("ignored", "C9 refractory: a crossing at t−7 .* did not set"),   # R declared, never applied
    ("short", "C9 refractory: a crossing at t−7 .* did not set"),     # R − 1
    ("long", "C9 refractory: a crossing at t−8 set"),              # R + 1 (off by one)
    ("future", "C1 LEAK"),                                          # reads t+1
    ("from_horizon", "C1 LEAK"),                                    # the drop applied after the horizon cut
    ("weekly_mean", "C9 episode"),                                  # right at t−R and t−R−1, wrong on the episode
    ("raw", "C9 episode"),                                          # III F-7: ignores the carry through the episode's gap
    ("rows", "C9 episode"),                                         # III F-7: counts observed rows across the gap
])
def test_persistent_selftest_catches_refractory_defects(persistent_master, monkeypatch, mode, check):
    inst = load_instance(persistent_master)
    monkeypatch.setattr(label, "make", _refractory_variant(mode))
    with pytest.raises(st.LeakError, match=check):
        st.run(inst, verbose=False)


def test_persistent_world_passes_and_records_what_ran(persistent_master):
    """The world and R are computed into the result (and so the receipt), not stamped from config (C-023)."""
    inst = load_instance(persistent_master)
    r = st.run(inst, verbose=False)
    assert r["event_series"] == "accumulating" and r["refractory_weeks"] == 7
    ep = r["C9"]["episode"]
    assert r["C9"]["bites"] == r["C9"]["boundary"] == "ok"
    assert ep["checked"] and ep["crossing_runs"] >= 2 and ep["dip_weeks"] >= 1 and ep["dip_weeks_dropped"] == ep["dip_weeks"]
    assert ep["gap_weeks"] > int(inst.cfg["label"]["last_known_weeks"])          # III F-7: carried ≠ raw is exercised
    rec = json.loads(st.write_receipt(inst, r).read_text())
    assert rec["C9"]["episode"]["checked"] and rec["C9"]["boundary"].startswith("ok")   # III F-3: on the receipt
    assert all(v.get("C3") == "ok" or k != "atl_stream_example_dhw_daily" for k, v in r["streams"].items())


def test_event_series_choice_and_refusals(persistent_master, forked):
    p = load_instance(persistent_master)
    assert st.event_series(p) == "accumulating"
    p.cfg["selftest"]["event_series"] = "iid"
    assert st.event_series(p) == "iid"
    p.cfg["selftest"]["event_series"] = "smooth"
    with pytest.raises(ValueError, match="event_series 'smooth'"):
        st.event_series(p)
    f = load_instance(forked)                                       # a below event: accumulating is refused, iid is default
    assert st.event_series(f) == "iid"
    f.cfg["selftest"]["event_series"] = "accumulating"
    with pytest.raises(ValueError, match="ABOVE event on a unit_daily event stream"):
        st.event_series(f)



def test_fork_refuses_duplicate_zone_ids(tmp_path, capsys):
    """M-2a-i III F-2: a zone exported as two features with one id is refused before anything is written."""
    import conftest
    g = copy.deepcopy(conftest.GEOJSON); g["features"].append(copy.deepcopy(g["features"][0]))
    d = tmp_path / "inst"; (d / "geometry").mkdir(parents=True)
    (d / "geometry" / "example_sound_segments.geojson").write_text(json.dumps(g))
    assert fork_into(d, geometry=False) == 1
    assert "duplicate seg" in capsys.readouterr().err
    assert not (d / "atlantis.yaml").exists()



def _with_refractory(d, R, signal=None):
    p = d / "events.yaml"; doc = yaml.safe_load(p.read_text()); doc["event_definitions"][0]["refractory_weeks"] = R
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    if signal:
        q = d / "atlantis.yaml"; c = yaml.safe_load(q.read_text()); c["label"]["signal"] = signal
        q.write_text(yaml.safe_dump(c, sort_keys=False))


def test_iid_world_boundary_is_never_skipped(forked, monkeypatch):
    """III F-3 (the reviewer's escape): R = 4 in the iid world — the boundary probe used to be skipped there, and an R + 1
    refractory passed the whole self-test. Now the unobserved week is filled and the probe runs."""
    _with_refractory(forked, 4)
    r = st.run(load_instance(forked), verbose=False)
    assert r["event_series"] == "iid" and r["C9"]["boundary"].startswith("ok")
    monkeypatch.setattr(label, "make", _refractory_variant("long"))
    with pytest.raises(st.LeakError, match="C9 refractory: a crossing at t−5 set"):
        st.run(load_instance(forked), verbose=False)


def test_episode_check_refuses_a_signal_it_cannot_recompute(persistent_master, tmp_path):
    d = tmp_path / "inst"; shutil.copytree(persistent_master, d)
    _with_refractory(d, 7, signal="weekly_p90(value)")
    with pytest.raises(st.LeakError, match="C9 episode: cannot recompute"):
        st.run(load_instance(d), verbose=False)


def test_episode_check_follows_a_weekly_mean_signal(persistent_master, tmp_path):
    d = tmp_path / "inst"; shutil.copytree(persistent_master, d)
    _with_refractory(d, 7, signal="weekly_mean(value)")
    r = st.run(load_instance(d), verbose=False)
    assert r["C9"]["episode"]["checked"] and r["C9"]["episode"]["signal"] == "weekly_mean(value)"


def test_station_keyed_above_event_defaults_to_iid(forked):
    """III F-6: a station_daily event with R > 0 crashed the episode check (station frames carry no unit column)."""
    inst = load_instance(forked)
    inst.event["direction"] = "above"; inst.event["refractory_weeks"] = 3
    assert inst.stream_spec(inst.event["event_variable_stream"])["shape"] == "station_daily"
    assert st.event_series(inst) == "iid"
    inst.cfg["selftest"]["event_series"] = "accumulating"
    with pytest.raises(ValueError, match="unit_daily event stream"):
        st.event_series(inst)

"""atlantis_core.conform (M-1d-i): contract v0.3.0 §B as a machine check. The forked example conforms; then each item is
fed the defects its contract row names, and must fail — that item, by name (C-009/C-013: the minimum IS the contract)."""
import json, shutil

import pytest
import yaml

from atlantis_core import load_instance
from atlantis_core.conform import check, main, parse_items
from atlantis_core.selftest import write_receipt


def Y(d, f):
    return yaml.safe_load((d / f).read_text())


def W(d, f, doc):
    (d / f).write_text(yaml.safe_dump(doc, sort_keys=False))


def edit(f, fn):
    def go(d):
        doc = Y(d, f); fn(doc); W(d, f, doc)
    return go


def test_forked_example_conforms(forked_master, capsys):
    assert main(["--instance", str(forked_master)]) == 0
    out = capsys.readouterr().out
    assert "✅ conforms: 10 pass · 2 n/a (9, 10)" in out


def test_parse_items():
    assert parse_items("1-8,11,12") == [1, 2, 3, 4, 5, 6, 7, 8, 11, 12]
    with pytest.raises(SystemExit):
        parse_items("13")


def _set_fed(d, fn):
    p = d / "how/federation/atlantis/CLAUDE.md"; t = p.read_text(); p.write_text(fn(t))


DEFECTS = [
    # 1 — patient
    (1, lambda d: (d / "units.yaml").unlink(), "units.yaml missing"),
    (1, edit("atlantis.yaml", lambda c: c["grid"]["units"].append(3)), "grid unit '3' has no units.yaml row"),
    (1, edit("units.yaml", lambda u: u["spatial_units"][1].pop("parent_unit")), "expected exactly one region row"),
    (1, edit("units.yaml", lambda u: u["spatial_units"][1].__setitem__("parent_unit", "atl_unit_nowhere")), "is not a declared unit"),
    (1, edit("units.yaml", lambda u: u["spatial_units"][1].__setitem__("geometry_ref", "POINT(-76 35)")), "geometry_ref"),
    (1, edit("atlantis.yaml", lambda c: c["board"].__setitem__("unit_ref", "atl_unit_nowhere")), "board.unit_ref"),
    (1, lambda d: (d / "geometry/example_sound_segments.geojson").unlink(), "does not resolve inside the instance"),
    (1, lambda d: (d / "geometry/example_sound_segments.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"seg": 1}, "geometry": None}]})),
     "are not features of"),
    # M-2a-i: the geometry is pinned by its bytes — an unpinned file, and one moved vertex, each fail item 1 by name
    (1, edit("atlantis.yaml", lambda c: c["grid"].pop("sha256")), "grid.sha256 missing"),
    (1, lambda d: (d / "geometry/example_sound_segments.geojson").write_text(
        (d / "geometry/example_sound_segments.geojson").read_text().replace("-76.2, 35.5", "-76.2, 35.51", 1)),
     "grid.sha256 mismatch"),
    (1, lambda d: (edit("atlantis.yaml", lambda c: c["grid"].update({"kind": "rules", "rules": [{"id": 1, "rule": "lat >= 35.2"}, {"id": 2, "rule": "True"}]}))(d),
                   _set_fed(d, lambda t: t.replace("class: public", "class: partner"))), "public posture only"),
    # 2 — event
    (2, edit("streams.yaml", lambda s: s["observation_streams"][0].pop("authority")), "names no authority CURIE"),
    (2, edit("events.yaml", lambda e: e["event_definitions"][0].__setitem__("onset_rule", "   ")), "onset_rule missing"),
    (2, edit("events.yaml", lambda e: e["event_definitions"][0].__setitem__("direction", "sideways")), "direction"),
    (2, edit("atlantis.yaml", lambda c: c["label"].__setitem__("event", "atl_event_nope")), "label.event"),
    # 3 — streams
    (3, edit("streams.yaml", lambda s: s["observation_streams"][0].pop("license")), "license"),
    (3, edit("streams.yaml", lambda s: s["observation_streams"][0].__setitem__("source_id", " ")), "source_id missing"),
    (3, edit("streams.yaml", lambda s: s["observation_streams"][0].__setitem__("fetcher", "Telnet")), "fetcher"),
    (3, edit("atlantis.yaml", lambda c: c["streams"]["atl_stream_example_do_daily"].pop("summary")), "artifact + summary"),
    (3, edit("streams.yaml", lambda s: s["observation_streams"][0].__setitem__("sha256", "a" * 64)), "'ingested_at' is a required property"),
    # 4 — vitals
    (4, edit("features.yaml", lambda f: f["vitals"][0].pop("lag")), "neither lag nor window"),
    (4, edit("features.yaml", lambda f: f["vitals"][3].update({"tag": "lever"})), "lever"),
    (4, edit("features.yaml", lambda f: f["vitals"][0].__setitem__("tag", "driver")), "tag"),
    (4, edit("features.yaml", lambda f: f["vitals"][0].__setitem__("stream_ref", "atl_stream_nope")), "R2"),
    # 5 — surveillance
    (5, edit("features.yaml", lambda f: [v.__setitem__("group", "survey") for v in f["vitals"] if v["group"] == "surveillance"]), "R8"),
    (5, lambda d: (edit("streams.yaml", lambda s: [x.__setitem__("surveillance_channel", False) for x in s["observation_streams"]])(d),
                   edit("features.yaml", lambda f: [v.__setitem__("group", "survey") for v in f["vitals"] if v["group"] == "surveillance"])(d),
                   edit("atlantis.yaml", lambda c: (c.__setitem__("surveillance", {"declared": "absent", "reason": " "}),
                                                    c["eval"].update({"ablations": []}), c["eval"].pop("surveillance_only")))(d)), "R8"),
    # 7 — posture
    (7, lambda d: (d / "how/federation/atlantis/CLAUDE.md").unlink(), "no federation_ref block"),
    (7, lambda d: (d / "who/governance/adr_001_data_posture.md").unlink(), "does not exist"),
    (7, lambda d: _set_fed(d, lambda t: t.replace("class: public", "class: secret")), "not in"),
    (7, lambda d: (_set_fed(d, lambda t: t.replace("class: public", "class: partner"))), "never names the class"),
    (7, lambda d: (d / "who/governance/adr_001_data_posture.md").write_text("---\nstatus: proposed\n---\npublic partner human_subject\n"),
     "declares no"),
    # 8 — split
    (8, edit("atlantis.yaml", lambda c: c["split"].__setitem__("val_start", 2016)), "not temporal"),
    (8, edit("atlantis.yaml", lambda c: c["split"].__setitem__("test_end", "2023")), "integer years"),
    (8, edit("atlantis.yaml", lambda c: c["split"].__setitem__("rolling_origin_years", [2021, 2023])), "test past test_end"),
    # 11 — mapping
    (11, lambda d: (d / "mapping.yaml").unlink(), "mapping.yaml missing"),
    (11, edit("mapping.yaml", lambda m: m["fence"]["never_project"].remove("scored_table")), "scored_table"),
    (11, edit("mapping.yaml", lambda m: m.__setitem__("instance", "someone_else")), "board.entry_stem"),
    (11, edit("mapping.yaml", lambda m: m["sources"].__setitem__("spatial_units", ["zones.yaml"])), "does not exist"),
]


@pytest.mark.parametrize("item,fn,why", DEFECTS, ids=[f"item{i}-{n}" for n, (i, _, _) in enumerate(DEFECTS)])
def test_each_item_bites(forked, item, fn, why):
    assert check(forked, [item], selftest=False)[item]["status"] == "pass"     # clean before the defect
    fn(forked)
    r = check(forked, [item], selftest=False)[item]
    assert r["status"] == "fail" and any(why in x for x in r["reasons"]), r


def test_item3_fetched_stage(forked):
    r = check(forked, [3], stage="fetched", selftest=False)[3]
    assert r["status"] == "fail" and any("sha256 missing (fetched stage)" in x for x in r["reasons"])
    assert any("no cached artifact" in x for x in r["reasons"])


ADR = "who/governance/adr_001_data_posture.md"
SIGNED = "| public posture for all three streams | the steward | 2026-10-03 | ratified |"


def sign(d, row=SIGNED, front="ratified"):
    p = d / ADR; t = p.read_text().replace("| | | | proposed |", row)
    p.write_text(t.replace("status: proposed", f"status: {front}", 1))


def test_item7_fetched_needs_signed_ratification(forked):
    """III F-3b: 'ratified' is the signed 4-field row AND an agreeing frontmatter — not a one-word flip."""
    assert check(forked, [7], stage="declared", selftest=False)[7]["status"] == "pass"
    assert check(forked, [7], stage="fetched", selftest=False)[7]["status"] == "fail"
    p = forked / ADR; orig = p.read_text()
    p.write_text(orig.replace("status: proposed", "status: ratified", 1))                       # the dry run's word flip
    r = check(forked, [7], stage="fetched", selftest=False)[7]
    assert r["status"] == "fail" and any("not signed" in x for x in r["reasons"])
    p.write_text(orig); sign(forked, front="proposed")                                          # signed row, stale frontmatter
    assert any("must agree" in x for x in check(forked, [7], stage="fetched", selftest=False)[7]["reasons"])
    p.write_text(orig); sign(forked, row="| public | the steward | Oct 3rd | ratified |")       # no ISO date
    assert check(forked, [7], stage="fetched", selftest=False)[7]["status"] == "fail"
    p.write_text(orig); sign(forked, row="| public |  | 2026-10-03 | ratified |")               # nobody signed
    assert check(forked, [7], stage="fetched", selftest=False)[7]["status"] == "fail"
    p.write_text(orig); sign(forked)
    assert check(forked, [7], stage="fetched", selftest=False)[7]["status"] == "pass"


@pytest.mark.parametrize("ruling", ["../other/who/governance/adr_001_data_posture.md", "/etc/hosts",
                                    "who/../../elsewhere/adr.md"])
def test_item7_ruling_must_be_the_instances_own(forked, tmp_path, ruling):
    """III F-3a: the gate opened on Atlantis's ADR-000 and on a sibling instance's ratified ADR."""
    other = tmp_path / "other"; (other / "who/governance").mkdir(parents=True)
    (other / ADR).write_text((forked / ADR).read_text()); sign(other)
    _set_fed(forked, lambda t: t.replace('ruling: "who/governance/adr_001_data_posture.md"', f'ruling: "{ruling}"'))
    r = check(forked, [7], stage="fetched", selftest=False)[7]
    assert r["status"] == "fail" and any("inside the instance" in x for x in r["reasons"])


def test_item7_partner_posture_needs_gitignore(forked):
    _set_fed(forked, lambda t: t.replace("class: public", "class: partner"))
    p = forked / ADR; p.write_text(p.read_text().replace("**Class:** `public`", "**Class:** `partner`"))
    r = check(forked, [7], selftest=False)[7]
    assert r["status"] == "fail" and any(".gitignore does not exclude" in x for x in r["reasons"])


def test_item6_reruns_and_fails_on_a_leak(forked, monkeypatch):
    assert check(forked, [6])[6]["status"] == "pass"
    from atlantis_core import label
    orig = label.make
    def overreach(inst_, table, evs, units, weeks, event=None, lcfg=None):
        ev = dict(event or inst_.event); ev["horizon"] = int(ev["horizon"]) + 1
        return orig(inst_, table, evs, units, weeks, event=ev, lcfg=lcfg)
    monkeypatch.setattr(label, "make", overreach)
    r = check(forked, [6])[6]
    assert r["status"] == "fail" and any("C2" in x for x in r["reasons"])


def test_item6_receipt_mode(forked):
    r = check(forked, [6], selftest=False)[6]
    assert r["status"] == "fail" and any("no self-test receipt" in x for x in r["reasons"])
    inst = load_instance(forked); write_receipt(inst, {"vitals": len(inst.vitals), "patients": [1, 2]})
    assert check(forked, [6], selftest=False)[6]["status"] == "pass"


def test_item6_not_run_on_broken_registries(forked):
    """III F-5: the verdict no longer depends on which items were requested."""
    edit("features.yaml", lambda f: [v.__setitem__("group", "survey") for v in f["vitals"] if v["group"] == "surveillance"])(forked)
    for items in ([6], [5, 6]):
        r = check(forked, items)[6]
        assert r["status"] == "fail" and any("not run" in x for x in r["reasons"]), items


def test_items_9_10_after_a_run(forked, exemplar_dir):
    R = check(forked, [9, 10], selftest=False)
    assert R[9]["status"] == R[10]["status"] == "n/a"
    (forked / "what/board/entries").mkdir(parents=True)
    ent = json.loads((exemplar_dir.parents[1] / "board/entries/2026-10-02_gulf_karenia_brevis_v1.json").read_text())
    (forked / "what/board/entries/foreign.json").write_text(json.dumps(ent))
    r = check(forked, [9], selftest=False)[9]                       # III F-5: another instance's entry is not this one's
    assert r["status"] == "fail" and any("unit_ref" in x for x in r["reasons"]) and any("semantic_hash" in x for x in r["reasons"])
    from atlantis_core.config import semantic_hash
    inst = load_instance(forked)
    ent["evaluation"]["unit_ref"] = inst.cfg["board"]["unit_ref"]; ent["evaluation"]["config_hash"] = semantic_hash(inst)
    ent["evaluation_extras"]["semantic_hash"] = semantic_hash(inst)
    (forked / "what/board/entries/foreign.json").write_text(json.dumps(ent))
    assert check(forked, [9], selftest=False)[9]["status"] == "pass"
    ent["evaluation_extras"]["predictions"] = [0.1] * 3
    (forked / "what/board/entries/bad.json").write_text(json.dumps(ent))
    assert check(forked, [9], selftest=False)[9]["status"] == "fail"


LIMITS = ("<section id=\"limits\"><h2>Limitations</h2><p>Method demonstration on public data; the alert thresholds are "
          "test quantiles; where the analogy breaks: an estuary is not a patient.</p></section>")


@pytest.mark.parametrize("page,ok", [
    ('<section id="method"></section>', False),
    ('<!-- id="limits" --><p>where the analogy breaks</p>', False),          # III F-5: a comment is not a section
    ('<section id="limits"></section><p>analogy</p>', False),                 # empty
    (LIMITS.replace("where the analogy breaks", "and so on"), False),         # no analogy discussion
    (LIMITS, True),
])
def test_item10_limits_section(forked, page, ok):
    (forked / "site").mkdir()
    (forked / "site/p.html").write_text(page)
    assert (check(forked, [10], selftest=False)[10]["status"] == "pass") is ok


def test_item2_authority_allowlist(forked):
    edit("streams.yaml", lambda s: s["observation_streams"][0].__setitem__("authority", "x:y"))(forked)
    r = check(forked, [2], selftest=False)[2]
    assert r["status"] == "fail" and any("CF/WoRMS/dwc/NOAACRW" in x for x in r["reasons"])



@pytest.mark.parametrize("auth, ok", [
    ("NOAACRW:degree_heating_week", True),    # M-2a-i: a CRW product is the event variable's authority until a CF name exists
    ("NOAA CRW", False),                      # the producer's name is not a CURIE (the card's wording; crosswalk known_limit)
    ("NOAACRW:", False),                      # a prefix with no local id
    ("noaacrw:degree_heating_week", False),   # prefixes are case-exact, as the schema declares them
])
def test_item2_crw_authority(forked, auth, ok):
    edit("streams.yaml", lambda s: s["observation_streams"][0].__setitem__("authority", auth))(forked)
    r = check(forked, [2], selftest=False)[2]
    assert (r["status"] == "pass") is ok, r
    if not ok:
        assert any("names no authority CURIE" in x for x in r["reasons"]), r


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks not installed")
def test_item12_gitleaks_catches_a_planted_key(forked):
    assert check(forked, [12], selftest=False)[12]["status"] == "pass"
    (forked / "notes.md").write_text("aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY9\n"
                                     "AKIA" + "Z" * 4 + "QWERTYUIOPAS\n")
    r = check(forked, [12], selftest=False)[12]
    assert r["status"] == "fail", r
    (forked / ".gitleaks.toml").write_text('[allowlist]\npaths = [".*"]\n')   # III F-5: the instance cannot allowlist itself
    (forked / ".gitleaksignore").write_text("*\n")
    r = check(forked, [12], selftest=False)[12]
    assert r["status"] == "fail" and any("IGNORED" in x for x in r["reasons"]), r


def test_item12_without_gitleaks_is_not_a_pass(forked, monkeypatch, capsys):
    import atlantis_core.conform as C
    monkeypatch.setattr(C.shutil, "which", lambda name: None)
    assert check(forked, [12], selftest=False)[12]["status"] == "not_run"
    assert main(["--instance", str(forked), "--items", "12", "--no-selftest"]) == 1
    assert "never a silent pass" in capsys.readouterr().out


def test_conform_writes_nothing(forked_master):
    before = sorted(p.relative_to(forked_master) for p in forked_master.rglob("*"))
    check(forked_master)
    assert sorted(p.relative_to(forked_master) for p in forked_master.rglob("*")) == before

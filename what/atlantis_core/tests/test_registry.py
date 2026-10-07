"""registry + grammar + config: the cross-file checks linkml-validate cannot make; semantic hash behaviour."""
import copy
import pytest
import yaml

from atlantis_core import load_instance, semantic_hash
from atlantis_core.registry import check, RegistryError
from atlantis_core.vitals import grammar


@pytest.mark.parametrize("bad", ["__import__('os')", "value.real", "weekly_max(value, 1)", "weekly_max(v=value)",
                                 "lag(value)", "weekly_max(depth)", "value + 1", "weekly_max('x')",
                                 "weekly_max(value)[0]", "weekly_max(True)", "eval('1')"])
def test_grammar_rejects(bad):
    with pytest.raises(grammar.TransformError):
        grammar.parse(bad, constants=["detect_threshold"])


@pytest.mark.parametrize("ok", ["weekly_max(log10p1(value))", "weeks_since_ge(weekly_max(value), log10p1(event_threshold))",
                                "at_week_end(anomaly(roll_mean_days(log10p1(value), 30, 20)))", "harmonic_sin(52.18)",
                                "weeks_since_gt(weekly_count(value), -1)"])
def test_grammar_accepts(ok):
    grammar.parse(ok, constants=["detect_threshold"])


def test_exemplar_registry_checks_clean(exemplar_dir):
    inst = load_instance(exemplar_dir)
    assert len(inst.vitals) == 25 and len(inst.streams) == 3 and len(inst.events) == 1


def _mutate(exemplar_dir, fn):
    inst = load_instance(exemplar_dir)
    fn(inst)
    with pytest.raises(RegistryError) as e:
        check(inst)
    return str(e.value)


@pytest.mark.parametrize("rule,fn", [
    ("R1", lambda i: i.declared["vital"].append(i.vitals[0]["vital_id"])),
    ("R2", lambda i: i.vitals[0].__setitem__("stream_ref", "atl_stream_nope")),
    ("R3", lambda i: i.vitals[0].__setitem__("transform", "weekly_max(value) + 1")),
    ("R3", lambda i: i.vitals[6].pop("window")),                        # roll_max_4w without its window
    ("R3", lambda i: i.vitals[0].__setitem__("window", 3)),             # window on a non-windowed op
    ("R4", lambda i: [v.__setitem__("owner", " ") for v in i.vitals if v["tag"] == "lever"]),
    ("R5", lambda i: i.cfg["streams"].pop("atl_stream_oisst_region_daily")),
    ("R5", lambda i: i.cfg["streams"]["atl_stream_usgs_discharge_daily"].pop("stations")),
    ("R5", lambda i: i.streams["atl_stream_fwc_hab_karenia"].__setitem__("fetcher", "Nope")),
    ("R6", lambda i: i.cfg["label"].__setitem__("event", "atl_event_nope")),
    ("R7", lambda i: i.cfg["climatology"].__setitem__("atl_stream_oisst_region_daily", [1982, 2017])),
    ("R7", lambda i: i.cfg.pop("climatology_policy")),                 # discharge era overlaps the 2016 rolling fold
    ("R3", lambda i: i.vitals[1].__setitem__("lag", -1)),
    ("R3", lambda i: i.vitals[6].__setitem__("window", 0)),
    ("R3", lambda i: i.vitals[6].__setitem__("window", 4.5)),
    ("R6", lambda i: next(iter(i.events.values())).__setitem__("direction", "below")),   # below + weekly_max signal
])
def test_registry_rule_bites(exemplar_dir, rule, fn):
    assert rule in _mutate(exemplar_dir, fn)


def test_semantic_hash_ignores_prose_and_order(exemplar_dir):
    a = load_instance(exemplar_dir)
    h = semantic_hash(a)
    b = load_instance(exemplar_dir)
    for v in b.vitals:
        v["description"] = "reworded"; v["name"] = "x"
    b.cfg = dict(reversed(list(b.cfg.items())))
    b.cfg["selftest"] = {"anything": 1}
    b.cfg["streams"]["atl_stream_fwc_hab_karenia"]["fetch"]["page"] = 1000     # how bytes are fetched is not training
    b.cfg["streams"]["atl_stream_usgs_discharge_daily"]["lever_stations"] = []  # what-if only (III F-2)
    b.cfg["eval"] = {**b.cfg["eval"], "alert_rates": [0.5], "lead_budget": 0.5}  # how a trained model is read
    b.cfg["whatif"] = {}; b.cfg["explain"] = {}; b.cfg["board"] = {}
    assert semantic_hash(b) == h


def test_semantic_hash_follows_the_learner(exemplar_dir):
    """A learner swap's results carry the hash of the learner that produced them (III F-2)."""
    a = load_instance(exemplar_dir)
    sw = a.cfg["learner_swaps"][0]
    assert semantic_hash(a, learner=sw) != semantic_hash(a)
    assert semantic_hash(a, learner=a.cfg["learner"]) == semantic_hash(a)


def test_rolling_origin_obligation_recorded(exemplar_dir):
    inst = load_instance(exemplar_dir)
    assert len(inst.obligations) == 1 and "refit" in inst.obligations[0] and "[2016]" in inst.obligations[0]


@pytest.mark.parametrize("fn", [
    lambda i: i.vitals[1].__setitem__("lag", 5),
    lambda i: i.cfg["climatology"].__setitem__("atl_stream_oisst_region_daily", [1983, 2011]),
    lambda i: next(iter(i.events.values())).__setitem__("threshold", 50000),
    lambda i: i.cfg["split"].__setitem__("train_end", 2015),
    lambda i: i.cfg["vitals"].__setitem__("weeks_since_cap", 52),           # III F-6
    lambda i: i.cfg["climatology_policy"].__setitem__("rolling_origin", "fixed"),
    # M-1b-ii-a III F-2: fields that choose which models are trained
    lambda i: i.cfg["eval"].__setitem__("sensitivity_threshold", 40000),
    lambda i: i.cfg["eval"].__setitem__("ablations", []),
    lambda i: i.cfg["eval"].__setitem__("surveillance_only", "n_samples_t0"),
    lambda i: i.vitals[0].__setitem__("group", "other"),
    lambda i: i.cfg["learner"]["params"].__setitem__("max_depth", 5),
    lambda i: i.cfg["split"].__setitem__("embargo_weeks", 6),                # M-1f
    lambda i: i.cfg["split"].__setitem__("embargo_weeks", "none"),
    lambda i: next(iter(i.events.values())).__setitem__("horizon", 6),      # the default embargo follows the horizon
])
def test_semantic_hash_moves_on_training_change(exemplar_dir, fn):
    a = load_instance(exemplar_dir); h = semantic_hash(a)
    fn(a)
    assert semantic_hash(a) != h


def test_semantic_hash_reads_the_resolved_embargo(exemplar_dir):
    """M-1f: absent ≡ the horizon (4) ≡ an explicit 4; `none` ≡ 0 hashes as v2's split did (board v1/v2's acfa22c6e4)."""
    def h(E=None):
        a = load_instance(exemplar_dir)
        if E is not None:
            a.cfg["split"]["embargo_weeks"] = E
        return semantic_hash(a)
    assert h() == h(4) != h("none") == h(0) == "acfa22c6e4"


def test_atlantis_yaml_matches_config_yaml(exemplar_dir):
    """Drift guard: values atlantis.yaml marks '(= config.yaml)' must equal config.yaml (which stays byte-stable)."""
    cfg = yaml.safe_load((exemplar_dir / "config.yaml").read_text())
    inst = load_instance(exemplar_dir)
    a = inst.cfg
    assert a["grid"]["rules"] == cfg["regions"]
    assert {int(k): v for k, v in a["streams"]["atl_stream_oisst_region_daily"]["fetch"]["boxes"].items()} == \
           {int(k): v for k, v in cfg["region_boxes"].items()}
    assert a["streams"]["atl_stream_usgs_discharge_daily"]["stations"] == {s: g["regions"] for s, g in cfg["gauges"].items()}
    assert a["streams"]["atl_stream_fwc_hab_karenia"]["fetch"]["layers"] == cfg["fwc_layers"]
    assert a["split"] == cfg["split"]
    assert a["constants"]["detect_threshold"] == cfg["target"]["detect_threshold"]
    ev = inst.event
    assert ev["threshold"] == cfg["target"]["bloom_threshold_cells_per_l"] and ev["horizon"] == cfg["target"]["horizon_weeks"]
    mono = {v["vital_id"].removeprefix("atl_vital_") for v in inst.vitals if v.get("monotone") == 1}
    assert mono == set(cfg["xgb"]["monotone_increasing"])
    levers = [s for s, g in cfg["gauges"].items() if g.get("lever")]
    assert levers and all(v.get("owner") for v in inst.vitals if v["tag"] == "lever")
    # M-1b-ii-a: learner · eval · explain · lever stations
    x = dict(cfg["xgb"]); x.pop("monotone_increasing")
    L = a["learner"]
    assert L["kind"] == "xgboost"
    assert {**L["params"], "n_estimators": L["n_estimators"], "early_stopping_rounds": L["early_stopping_rounds"]} == x
    assert a["eval"]["sensitivity_threshold"] == cfg["target"]["sensitivity_threshold"]
    sh = cfg["shap"]
    assert (a["explain"]["background_n"], a["explain"]["perturbation"], a["explain"]["interaction_rows"]) == \
           (sh["background_n"], sh["perturbation"], sh["interaction_rows"])
    assert a["streams"]["atl_stream_usgs_discharge_daily"]["lever_stations"] == levers


# R8 (M-1d-i, contract item 5): surveillance declared, or declared absent with a reason — each defect fed.
def _absent(i, reason="gridded-only streams; nobody chooses where to look"):
    i.cfg["surveillance"] = {"declared": "absent", "reason": reason}
    i.streams["atl_stream_fwc_hab_karenia"]["surveillance_channel"] = False
    for v in i.vitals:
        if v.get("group") == "surveillance":
            v["group"] = "counts"
    i.cfg["eval"]["ablations"] = []
    i.cfg["eval"].pop("surveillance_only", None)


def test_r8_declared_absent_is_clean(exemplar_dir):
    i = load_instance(exemplar_dir); _absent(i); check(i)


@pytest.mark.parametrize("fn", [
    lambda i: i.streams["atl_stream_fwc_hab_karenia"].__setitem__("surveillance_channel", False),   # no channel, nothing declared
    lambda i: [v.__setitem__("group", "counts") for v in i.vitals if v.get("group") == "surveillance"],  # channel unread
    lambda i: i.cfg["eval"].__setitem__("ablations", []),                                             # T5 ablation missing
    lambda i: i.cfg.__setitem__("surveillance", {"declared": "maybe"}),
    lambda i: (_absent(i), i.cfg["surveillance"].__setitem__("reason", "  ")),                         # absent, blank reason
    lambda i: (_absent(i), i.cfg["surveillance"].pop("reason")),                                       # absent, no reason
    lambda i: (_absent(i), i.streams["atl_stream_fwc_hab_karenia"].__setitem__("surveillance_channel", True)),
    lambda i: (_absent(i), i.vitals[3].__setitem__("group", "surveillance")),
    lambda i: (_absent(i), i.cfg["eval"].__setitem__("ablations", [{"drop_group": "surveillance"}])),
    lambda i: (_absent(i), i.cfg["eval"].__setitem__("surveillance_only", "n_samples_4w")),
])
def test_r8_bites(exemplar_dir, fn):
    assert "R8" in _mutate(exemplar_dir, fn)


def test_r8_outside_semantic_hash(exemplar_dir):
    a = load_instance(exemplar_dir); h = semantic_hash(a)
    a.cfg["surveillance"] = {"declared": "present"}
    assert semantic_hash(a) == h

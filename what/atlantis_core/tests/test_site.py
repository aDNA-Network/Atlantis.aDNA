"""site/ — the explainer page as a core template whose every word is instance data (M-1b-ii-b).

Every refusal the build makes is fed the defect it exists for (C-009): a guard that has never failed is not trusted."""
import copy as _copy
import json
import re

import numpy as np
import pandas as pd
import pytest
import yaml

from atlantis_core import load_instance
from atlantis_core.site import STRINGS, TEMPLATE, check_copy, render, template_figures
from atlantis_core.site.assemble import SiteError, assemble, bands, board_check, load_site, resolve, shap_check

# Words that belong to the Gulf K. brevis exemplar and must never be typed into the core template.
EXEMPLAR_LITERALS = [r"Florida", r"Lee", r"Collier", r"Caloosahatchee", r"S-79", r"Karenia", r"brevis", r"cells/L", r"\b1e5\b",
                     r"100,000", r"\b100k\b", r"\b1994\b", r"\b2017\b", r"\b2022\b", r"Tampa", r"\bFWC\b", r"OISST", r"USGS", r"NOAA",
                     r"discharge", r"\bsst\b", r"log_max", r"n_samples", r"\bcfs\b", r"Okeechobee", r"\bgauge\b", r"red tide"]


def literals_in(text: str) -> list:
    return [p for p in EXEMPLAR_LITERALS if re.search(p, text, re.I if p[0].isalpha() and p.islower() else 0)]


def test_template_carries_no_exemplar_literal():
    assert literals_in(TEMPLATE.read_text()) == []


def test_literal_guard_can_fail():
    tpl = TEMPLATE.read_text()
    for planted in ("<p>Lee-Collier</p>", "y0:1e5", "name:'S-79 cfs'", "'≥100k cells/L'"):
        assert literals_in(tpl + planted), planted


def test_template_figure_table_is_read():
    figs = template_figures(TEMPLATE.read_text())
    assert {"trace", "t2", "strip", "whatif", "label_diagram", "dependence", "cases", "gbar"} <= figs and len(figs) >= 18


# ── check_copy, on a tiny synthetic page (no exemplar data needed) ─────────────────────────────────────────────────────
DATA = {"metrics": {"full": {"test": {"auroc": 0.9}}}, "board": {"entry_id": "x"}}
SITE = {"strips": [{"key": "s1"}], "trace": {"panels": ["signal"]}}


def good_copy():
    return {"title": "T", "hero": {"pills": [], "h1": "h", "lede": "AUROC {{metrics.full.test.auroc|2}}", "stats": []},
            "sections": [{"id": "a", "nav": "A", "eyebrow": "e", "title": "t", "body": "<p>x</p>\n{{fig:pr}}\n{{fig:cases}}"}],
            "figures": {"pr": {"title": "PR"}}, "strips": {"s1": {"label": "l", "caption": "c"}},
            "strings": {**{k: "w" for k in STRINGS}, "trace_panels": {"signal": {"title": "s"}}}, "footer": "{{board.entry_id}}"}


def test_good_copy_passes():
    check_copy(good_copy(), DATA, TEMPLATE.read_text(), SITE)


@pytest.mark.parametrize("defect, match", [
    (lambda c: c.pop("footer"), "missing key 'footer'"),
    (lambda c: c["strings"].pop("whatif_non_lever"), "missing 'whatif_non_lever'"),
    (lambda c: c["sections"][0].update(body="{{fig:sonar}}"), "unknown figure"),
    (lambda c: c["hero"].update(lede="{{metrics.full.test.auprc|2}}"), "does not resolve"),
    (lambda c: c.update(footer="{{board.entry_id.nope}}"), "does not resolve"),
    (lambda c: c["figures"].update(roc={"title": "ROC"}), "no section places"),
    (lambda c: c["strips"].update(s2={"label": "x"}), "no such strip"),
    (lambda c: c["strips"].pop("s1"), "no words in copy.strips"),
    (lambda c: c["strings"]["trace_panels"].pop("signal"), "no words for trace panel"),
    # III F-3b: what the validator accepted and the page could not render
    (lambda c: c["sections"][0].update(body="{{fig:pr}} {{fig:pr}}"), "placed 2 times"),
    (lambda c: c["hero"].update(lede="{{metrics.full.test.auroc|pct}}"), "unknown format 'pct'"),
    (lambda c: c["sections"][0].update(nav="{{board.entry_id}}"), "tokens are not expanded here"),
    (lambda c: c["strings"].update(no_obs="{{board.entry_id}}"), "tokens are not expanded here"),
    (lambda c: c["strips"]["s1"].update(label="{{board.entry_id}}"), "tokens are not expanded here"),
])
def test_check_copy_refuses_each_defect(defect, match):
    c = good_copy(); defect(c)
    with pytest.raises(SiteError, match=match):
        check_copy(c, DATA, TEMPLATE.read_text(), SITE)


def test_render_refuses_a_broken_template():
    site = {"groups": {"g": {"label": "G", "color": ["#000", "#fff"]}}}
    out = render(TEMPLATE.read_text(), DATA, good_copy(), site)
    assert "--g-g:#000" in out and "--g-g:#fff" in out and "__SITE_DATA__" not in out
    assert "</script" not in json.dumps(DATA).replace("</", "<\\/")
    with pytest.raises(SiteError, match="placeholder"):
        render(TEMPLATE.read_text().replace("__SITE_COPY__", ""), DATA, good_copy(), site)


def test_resolve_refuses_what_the_page_cannot_read():
    d = {"a": [{"b": 1}]}
    assert resolve(d, "a.0.b") == 1
    with pytest.raises(KeyError):
        resolve(d, "a.-1.b")             # Python would index from the end; the page's get() cannot (III F-3b)


def test_bands_are_a_week_wide():
    w = pd.to_datetime(["2022-06-06", "2022-06-13", "2022-06-20"])
    out = bands(w, [None, "test", None])
    assert len(out) == 2
    for a, b in out:
        assert (pd.Timestamp(b) - pd.Timestamp(a)) == pd.Timedelta(days=7)   # III F-1: x0 == x1 drew nothing


# ── the exemplar, end to end (skips without the gitignored data/processed/atlantis_core) ─────────────────────────────────
@pytest.fixture(scope="module")
def built(exemplar_dir):
    if not (exemplar_dir / "data" / "processed" / "atlantis_core" / "shap.npz").exists():
        pytest.skip("exemplar data/processed/atlantis_core missing — run atlantis_core.run first")
    inst = load_instance(exemplar_dir)
    site = load_site(inst)
    return inst, site, assemble(inst, site), yaml.safe_load((exemplar_dir / site["copy"]).read_text())


def test_exemplar_page_says_what_board_v1_says(built):
    inst, site, data, copy = built
    check_copy(copy, data, TEMPLATE.read_text(), site)
    assert data["board"]["entry_id"] == "2026-10-02_gulf_karenia_brevis_v1"
    assert (data["board"]["auroc"], data["board"]["auprc"]) == (0.8938, 0.5388)
    assert round(data["metrics"]["full"]["test"]["auroc"], 4) == 0.8938
    assert data["metrics"]["semantic_hash"] == data["board"]["config_hash"] == "acfa22c6e4"
    words = json.dumps(copy)
    for must in ("calendar week", "refits its climatology", "chosen on the years they score", "A SHAP reading belongs to one model",
                 "group's own effect", "re-derived"):
        assert must in words, must
    assert "the data credits above are the only part that is Florida-specific" not in words


def test_availability_columns_only_for_the_learner_that_has_them(built):
    _, _, data, _ = built
    assert not any(c.startswith("availability:") for c in data["shap"]["mean_abs"])
    assert "availability" not in data["shap"]["group_net_mean_abs"]
    (lg,) = data["swaps"]
    assert lg["kind"] == "logistic" and lg["n_availability"] > 0 and "availability" in lg["group_net_mean_abs"]


def test_strips_mark_non_modelling_weeks_and_sum_net(built):
    _, _, data, _ = built
    s = data["shap"]["strips"]["oos_2022_23"]
    off = [i for i, p in enumerate(s["p"]) if p is None]
    assert off and all(s["split"][i] is None for i in off)              # grey bands: weeks outside the modelling rows
    on = [i for i, p in enumerate(s["p"]) if p is not None]
    assert all(s["groups"]["counts"][i] is not None for i in on)


def test_site_groups_must_match_the_registry(built):
    inst, site, _, _ = built
    bad = {**site, "groups": {k: v for k, v in site["groups"].items() if k != "season"}}
    with pytest.raises(SiteError, match="groups"):
        assemble(inst, bad)


def test_page_refuses_an_outdated_entry(built):
    inst, site, _, _ = built
    with pytest.raises(SiteError, match="disagree"):
        assemble(inst, {**site, "board_entry": "../../board/entries/2026-09-23_gulf_karenia_brevis_v0.json"})


def test_board_check_compares_every_evaluated_field(built, exemplar_dir):
    inst, site, _, _ = built
    m = json.loads((exemplar_dir / "outputs" / "atlantis_core" / "metrics.json").read_text())
    entry = json.loads((exemplar_dir / site["board_entry"]).read_text())
    assert board_check(m, entry, inst)["fields_checked"] >= 12
    for path, v in ((("brier",), 0.9), (("alert_budgets", 1, "precision"), 0.1), (("lead_time", "flagged_fraction"), 0.5),
                    (("ablations", 0, "ablated_auprc"), 0.1), (("data_pins", 0, "sha256"), "0" * 64), (("auroc",), 0.8941)):
        bad = _copy.deepcopy(entry); o = bad["evaluation"]
        for k in path[:-1]: o = o[k]
        o[path[-1]] = v
        with pytest.raises(SiteError, match="disagree"):
            board_check(m, bad, inst)


def test_shap_arrays_must_belong_to_the_run(built, exemplar_dir):
    proc, out = exemplar_dir / "data" / "processed" / "atlantis_core", exemplar_dir / "outputs" / "atlantis_core"
    z = dict(np.load(proc / "shap.npz")); ss = json.loads((out / "shap_summary.json").read_text())
    test, allr = pd.read_parquet(proc / "test_scored.parquet"), pd.read_parquet(proc / "all_scored.parquet")
    shap_check(z, ss, test, allr)
    for k, f in (("shap_all", lambda a: a[:-1]), ("base", lambda a: a + 0.1), ("shap", lambda a: a * 1.01)):
        with pytest.raises(SiteError, match="not the run"):
            shap_check({**z, k: f(z[k])}, ss, test, allr)


def test_strip_groups_are_net_sums(built, exemplar_dir):
    """Recomputed independently from shap.npz: the signed sum, and it must differ from the gross sum somewhere, or the test
    could not tell them apart (III F-3a: the first version passed with np.abs)."""
    inst, _, data, _ = built
    proc = exemplar_dir / "data" / "processed" / "atlantis_core"
    sv_all = np.load(proc / "shap.npz")["shap_all"]
    allr = pd.read_parquet(proc / "all_scored.parquet").reset_index(drop=True)
    feats = inst.feature_names
    s = data["shap"]["strips"]["oos_2022_23"]
    differs = 0
    for g in data["groups"]:
        ix = [feats.index(f["name"]) for f in data["features"] if f["group"] == g["id"]]
        for w, v in zip(s["weeks"], s["groups"][g["id"]]):
            r = allr.index[(allr.region == s["unit"]) & (allr.week == pd.Timestamp(w))]
            if not len(r):
                assert v is None; continue
            row = sv_all[r[0], ix]
            assert v == pytest.approx(row.sum(), abs=1e-3)
            differs += abs(row.sum() - np.abs(row).sum()) > 1e-2
    assert differs > 0
    assert all(len(b) == 2 for b in s["bands"]) and len(s["bands"]) == sum(p is None for p in s["p"])


# ── M-1e: the v2 page (site_v2.yaml) reads its own run and says what board v2 says ─────────────────────────────────
@pytest.fixture(scope="module")
def built_v2(exemplar_dir):
    if not (exemplar_dir / "data" / "processed" / "atlantis_core_v2" / "shap.npz").exists():
        pytest.skip("exemplar data/processed/atlantis_core_v2 missing — run atlantis_core.run --out outputs/atlantis_core_v2 first")
    inst = load_instance(exemplar_dir)
    site = load_site(inst, "site_v2.yaml")
    return inst, site, assemble(inst, site), yaml.safe_load((exemplar_dir / site["copy"]).read_text())


def test_v2_page_says_what_board_v2_says(built_v2):
    inst, site, data, copy = built_v2
    check_copy(copy, data, TEMPLATE.read_text(), site)
    assert data["board"]["entry_id"] == "2026-10-03_gulf_karenia_brevis_v2"
    ar = data["metrics"]["full"]["test"]["alert_rates"]
    assert all(v["threshold_from"] == "val" and v["realised_rate"] < v["nominal_rate"] for v in ar.values())
    assert data["board"]["delta_vs"]["fields"]["alert_budgets"]["10pct"]["realised_rate"]["now"] == round(ar["10pct"]["realised_rate"], 4)
    words = json.dumps(copy)
    for must in ("fixed on the validation years", "realised", "not proven", "chooses its own tree count"):
        assert must in words, must
    assert "chosen on the years they score" not in words and "will land as a new board version" not in words


def test_v2_run_against_v1_entry_is_refused(built_v2, exemplar_dir):
    """The page must cite the run it shows: v2's outputs re-projected against v1's entry disagree on the budgets."""
    inst, *_ = built_v2
    m = json.loads((exemplar_dir / "outputs" / "atlantis_core_v2" / "metrics.json").read_text())
    v1 = json.loads((exemplar_dir.parents[1] / "board" / "entries" / "2026-10-02_gulf_karenia_brevis_v1.json").read_text())
    with pytest.raises(SiteError, match="alert_budgets"):
        board_check(m, v1, inst)

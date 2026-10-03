"""explain/ — SHAP reproduces hab.explain on hab's model; linear SHAP is exact; what-if is config, lever-gated, and
re-derives the vitals from the raw stream."""
import json

import numpy as np
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.eval.learners import learner
from atlantis_core.explain import shap_explain, whatif
from atlantis_core.label import finalize
from atlantis_core.vitals.build import build, load_frames


@pytest.fixture(scope="module")
def hab(exemplar_dir):
    proc = exemplar_dir / "data" / "processed"
    if not (proc / "all_scored.parquet").exists():
        pytest.skip("exemplar data/processed missing — run hab.build_features + hab.train first")
    import xgboost as xgb
    inst = load_instance(exemplar_dir)
    m = xgb.XGBClassifier(); m.load_model(exemplar_dir / "outputs" / "model.json")
    return inst, learner(inst.cfg["learner"], inst.feature_names, inst), m, \
        pd.read_parquet(proc / "all_scored.parquet"), pd.read_parquet(proc / "test_scored.parquet")


def test_shap_reproduces_hab(hab, exemplar_dir):
    inst, L, m, alls, test = hab
    s, arr = shap_explain(inst, L, m, alls, test, with_all=False)
    ref = json.loads((exemplar_dir / "outputs" / "shap_summary.json").read_text())
    assert s["top6"] == ref["top6"] and s["dependence_partners"] == ref["dependence_partners"]
    assert s["top_interaction_pair"]["a"] == ref["top_interaction_pair"]["a"] and s["top_interaction_pair"]["b"] == ref["top_interaction_pair"]["b"]
    assert s["base_p"] == pytest.approx(ref["base_p"], abs=1e-9) and s["additivity_max_gap"] < 1e-2
    assert list(s["group_mean_abs_shap"]) == list(ref["group_mean_abs_shap"])
    assert max(abs(s["mean_abs_shap"][k] - v) for k, v in ref["mean_abs_shap"].items()) <= 1e-5
    assert s["background_from"] == "train rows only" and arr["shap_all"] is None
    assert set(s["tag_mean_abs_shap"]) == {v["tag"] for v in inst.vitals}


def test_linear_shap_is_exact():
    rng = np.random.default_rng(1)
    n = 600
    df = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n)})
    df.loc[::5, "a"] = np.nan
    df["y"] = (rng.random(n) < 1 / (1 + np.exp(-(df["b"] + df["a"].fillna(0))))).astype(int)
    df["week"] = pd.date_range("2000-01-03", periods=n, freq="7D")
    df["split"] = np.where(np.arange(n) < 400, "train", "test")
    class I:   # the minimum an explainer reads from an instance
        vitals = [{"vital_id": "atl_vital_a", "group": "g", "tag": "state"}, {"vital_id": "atl_vital_b", "group": "g", "tag": "proxy"}]
        cfg = {"explain": {"background_n": 300, "background_seed": 0, "perturbation": "interventional", "interaction_rows": 10}}
    L = learner({"kind": "logistic", "C_grid": [1.0]}, ["a", "b"])
    _, final, _ = L.fit(df[df.split == "train"], df[df.split == "test"])
    test = df[df.split == "test"].assign(p=L.predict(final, df[df.split == "test"]))
    s, arr = shap_explain(I, L, final, df.assign(p=L.predict(final, df)), test)
    assert s["additivity_max_gap"] < 1e-9
    assert arr["shap_all"].shape == (n, 2)


@pytest.fixture(scope="module")
def built(exemplar_dir):
    inst = load_instance(exemplar_dir)
    frames = load_frames(inst)
    table, _ = build(inst, frames)
    m, _ = finalize(inst, table)
    return inst, frames, m


def _hab_edit(rows, factor=0.7):
    """hab.whatif's feature-space edit, verbatim: treats discharge_30d as log10(1 + mean flow)."""
    cf = rows.copy()
    for c in ("discharge_30d_t0", "discharge_30d_t3"):
        cf[c] = np.log10(1 + factor * (10 ** cf[c] - 1))
    cf["discharge_anom_t0"] = cf["discharge_anom_t0"] + (cf["discharge_30d_t0"] - rows["discharge_30d_t0"])
    return cf


def test_whatif_rederives_from_raw_and_names_the_hab_gap(hab, built, exemplar_dir):
    """Same model, rows and actual scores as hab.whatif. The counterfactual differs where flow is low, with one cause,
    proven here: the vital is a 30-day mean of log10(1 + q), and hab edited it as if it were log10(1 + mean q). The two
    agree when every day's q >> 1 cfs (log10(1 + 0.7q) ~ log10 0.7 + log10 q) and part where q is small. Applying
    hab's edit to atlantis_core's own rows reproduces whatif.json; re-deriving from the scaled raw stream does not."""
    _, L, m, _, _ = hab
    inst, frames, md = built
    ref = json.loads((exemplar_dir / "outputs" / "whatif.json").read_text())
    alls = md.assign(split="?")
    gaps = {}
    for sc, rk in zip(inst.cfg["whatif"]["scenarios"], ["r7_2022_2023", "r7_2017_2019", "r4_2021_2021"]):
        r = whatif.scenario(inst, frames, L, m, alls, sc)
        assert r["weeks"] == ref[rk]["weeks"] and r["y"] == ref[rk]["y"] and r["rows_scaled"] > 0
        assert np.abs(np.array(r["p_actual"]) - np.array(ref[rk]["p_actual"])).max() <= 1e-4
        rows = md[md.region.isin(sc["units"]) & (md.week >= sc["period"][0]) & (md.week <= sc["period"][1])].sort_values(["region", "week"])
        hab_cf = np.round(L.predict(m, _hab_edit(rows)), 4)
        assert np.abs(hab_cf - np.array(ref[rk]["p_discharge_minus30"])).max() <= 1e-4     # the cause, reproduced
        gaps[rk] = float(np.abs(np.array(r["p_scenario"]) - np.array(ref[rk]["p_discharge_minus30"])).max())
    assert gaps["r7_2022_2023"] <= 1e-4                       # a high-flow window: the two readings agree
    assert gaps["r7_2017_2019"] > 1e-4 and gaps["r4_2021_2021"] > 1e-4   # low-flow weeks: they part
    r4 = whatif.scenario(inst, frames, L, m, alls, inst.cfg["whatif"]["scenarios"][2])
    assert r4["non_lever_stations_scaled"] == ["02304500"]    # Tampa's gauge is not S-79: reported, not hidden


def test_whatif_refuses_non_lever_stream_and_era(hab, built):
    _, L, m, _, _ = hab
    inst, frames, md = built
    sst = {"name": "x", "units": [7], "period": ["2022-06-01", "2022-07-01"], "stream": "atl_stream_oisst_region_daily", "factor": 0.9}
    with pytest.raises(ValueError, match="no vital tagged lever"):
        whatif.scenario(inst, frames, L, m, md, sst)
    early = {"name": "y", "units": [7], "period": ["2005-06-01", "2005-07-01"], "stream": "atl_stream_usgs_discharge_daily", "factor": 0.7}
    with pytest.raises(ValueError, match="climatology era"):
        whatif.scenario(inst, frames, L, m, md, early)

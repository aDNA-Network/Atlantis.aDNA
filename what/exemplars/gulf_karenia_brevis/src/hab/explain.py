"""SHAP explanations (interventional TreeExplainer) for the full model on the test split.
Writes outputs/shap_test.npz + outputs/shap_summary.json.  Run: .venv/bin/python -m hab.explain
"""
import json
import numpy as np, pandas as pd, xgboost as xgb, shap
from hab import load_config, DATA_PROC, OUT
from hab.build_features import FEATURES, FEATURE_GROUPS
from hab.regions import region_names


def load_model(path):
    m = xgb.XGBClassifier(); m.load_model(path); return m


def main():
    cfg = load_config()
    df = pd.read_parquet(DATA_PROC / "all_scored.parquet")
    test = pd.read_parquet(DATA_PROC / "test_scored.parquet").reset_index(drop=True)
    model = load_model(OUT / "model.json")
    rng = np.random.default_rng(cfg["xgb"]["random_state"])
    train = df[df.split == "train"]
    bg = train.sample(min(cfg["shap"]["background_n"], len(train)), random_state=42)[FEATURES]
    masker = shap.maskers.Independent(bg, max_samples=len(bg))
    ex = shap.TreeExplainer(model, data=masker, feature_perturbation=cfg["shap"]["perturbation"], model_output="raw")
    sv = ex.shap_values(test[FEATURES])
    base = float(np.ravel(ex.expected_value)[0])
    # additivity check: SHAP sums to the logit of the model's prediction
    logit = np.log(test["p"] / (1 - test["p"]))
    gap = np.abs(sv.sum(1) + base - logit).max()
    assert gap < 1e-2, f"SHAP additivity violated: max gap {gap}"
    print(f"✅ additivity: max |sum(shap)+base - logit| = {gap:.2e}  (base logit {base:.3f} → p={1/(1+np.exp(-base)):.4f})")

    # SHAP over ALL modelling rows for the risk strip (in-sample for train/val, flagged), done in one pass
    sv_all = ex.shap_values(df[FEATURES])
    np.savez_compressed(OUT / "shap_test.npz", shap=sv, base=base, X=test[FEATURES].values, y=test["y"].values,
                        shap_all=sv_all, all_index=df.index.values)
    mean_abs = pd.Series(np.abs(sv).mean(0), index=FEATURES).sort_values(ascending=False)
    group_of = {f: g for g, fs in FEATURE_GROUPS.items() for f in fs}
    group_abs = mean_abs.groupby(group_of).sum().sort_values(ascending=False)
    top6 = mean_abs.index[:6].tolist()

    # interactions on a subsample (tree_path_dependent explainer — interaction values need the path-dependent algorithm)
    sub = test.sample(min(cfg["shap"]["interaction_rows"], len(test)), random_state=42)
    ex_pd = shap.TreeExplainer(model)
    inter = ex_pd.shap_interaction_values(sub[FEATURES])
    im = np.abs(inter).mean(0); np.fill_diagonal(im, 0)
    i, j = np.unravel_index(np.argmax(im), im.shape)
    top_pair = (FEATURES[i], FEATURES[j], float(im[i, j]))
    # approximate interaction partner for each top6 feature (for dependence-plot colouring)
    partners = {}
    for f in top6:
        k = FEATURES.index(f)
        partners[f] = FEATURES[int(np.argsort(-im[k])[0])]

    names = region_names()
    summary = {"base_logit": base, "base_p": float(1 / (1 + np.exp(-base))), "additivity_max_gap": float(gap),
               "mean_abs_shap": mean_abs.round(5).to_dict(), "group_mean_abs_shap": group_abs.round(5).to_dict(),
               "top6": top6, "dependence_partners": partners,
               "top_interaction_pair": {"a": top_pair[0], "b": top_pair[1], "mean_abs_interaction": top_pair[2]},
               "perturbation": cfg["shap"]["perturbation"], "background_n": int(len(bg)), "n_test_rows": int(len(test))}
    (OUT / "shap_summary.json").write_text(json.dumps(summary, indent=1))
    print(mean_abs.round(4).head(12).to_string()); print(group_abs.round(4).to_string())
    print("top interaction:", top_pair)


if __name__ == "__main__":
    main()

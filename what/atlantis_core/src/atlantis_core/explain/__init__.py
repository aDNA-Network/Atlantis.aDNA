"""Explanation: per-patient SHAP read through the registry's tags (lever · proxy · artifact · state). A SHAP value is
never called a cause (CLAUDE.md, Proteus).

    summary, arrays = shap_explain(inst, learner, model, all_scored, test_scored)

xgboost   interventional TreeExplainer over a background drawn from TRAIN rows only (`explain.background_n`, seeded),
          additivity a hard check against the model's logit; interaction values (path-dependent) on a subsample.
          Ported from `hab.explain`.
logistic  exact linear SHAP in the original vitals: each vital's contribution is the sum over the columns it becomes
          (its standardised value and its missingness flag) of coef × (z − mean z over the same train background).

Groups and tags come from `features.yaml`, never from a list in code.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from atlantis_core.config import feature_name

__all__ = ["shap_explain", "tags"]


def tags(inst) -> dict:
    return {feature_name(v): {"group": v["group"], "tag": v["tag"], **({"owner": v["owner"]} if v.get("owner") else {})}
            for v in inst.vitals}


def _background(inst, all_scored: pd.DataFrame, features):
    e = inst.cfg["explain"]
    train = all_scored[all_scored.split == "train"]
    return train.sample(min(int(e["background_n"]), len(train)), random_state=int(e["background_seed"]))[features]


def _tree(inst, model, bg, test, all_rows, features):
    import shap
    e = inst.cfg["explain"]
    masker = shap.maskers.Independent(bg, max_samples=len(bg))
    ex = shap.TreeExplainer(model, data=masker, feature_perturbation=e["perturbation"], model_output="raw")
    sv = ex.shap_values(test[features])
    base = float(np.ravel(ex.expected_value)[0])
    sv_all = ex.shap_values(all_rows[features]) if all_rows is not None else None
    sub = test.sample(min(int(e["interaction_rows"]), len(test)), random_state=int(e["background_seed"]))
    inter = shap.TreeExplainer(model).shap_interaction_values(sub[features])
    im = np.abs(inter).mean(0); np.fill_diagonal(im, 0)
    return sv, base, sv_all, im


def _linear(model, bg, X, features):
    imp, sc, lr = model.named_steps["impute"], model.named_steps["scale"], model.named_steps["lr"]
    names = list(imp.get_feature_names_out(features))
    owner = [n.removeprefix("missingindicator_") for n in names]
    z = lambda d: sc.transform(imp.transform(d[features]))
    zb = z(bg).mean(0)
    coef = lr.coef_[0]
    base = float(lr.intercept_[0] + coef @ zb)
    def contrib(d):
        c = (z(d) - zb) * coef
        out = np.zeros((len(d), len(features)))
        for k, f in enumerate(owner):
            out[:, features.index(f)] += c[:, k]
        return out
    return contrib, base


def shap_explain(inst, L, model, all_scored: pd.DataFrame, test_scored: pd.DataFrame, with_all: bool = True):
    """`with_all=False` skips SHAP over every modelling row (the site's risk strips; minutes on the exemplar)."""
    features = L.features
    test = test_scored.reset_index(drop=True)
    bg = _background(inst, all_scored, features)
    im = None
    if L.kind == "xgboost":
        sv, base, sv_all, im = _tree(inst, model, bg, test, all_scored if with_all else None, features)
    elif L.kind == "logistic":
        contrib, base = _linear(model, bg, test, features)
        sv, sv_all = contrib(test), (contrib(all_scored) if with_all else None)
    else:
        raise ValueError(f"explain: no explainer for learner {L.kind!r}")
    logit = np.log(test["p"] / (1 - test["p"]))
    gap = float(np.abs(sv.sum(1) + base - logit).max())
    if not gap < 1e-2:
        raise AssertionError(f"SHAP additivity violated: max |sum(shap)+base − logit| = {gap}")
    tg = tags(inst)
    mean_abs = pd.Series(np.abs(sv).mean(0), index=features).sort_values(ascending=False)
    by = lambda key: mean_abs.groupby({f: tg[f][key] for f in features}).sum().sort_values(ascending=False)
    top6 = mean_abs.index[:6].tolist()
    summary = {"learner_kind": L.kind, "base_logit": base, "base_p": float(1 / (1 + np.exp(-base))),
               "additivity_max_gap": gap, "mean_abs_shap": mean_abs.round(5).to_dict(),
               "group_mean_abs_shap": by("group").round(5).to_dict(), "tag_mean_abs_shap": by("tag").round(5).to_dict(),
               "top6": top6, "perturbation": inst.cfg["explain"]["perturbation"] if L.kind == "xgboost" else "interventional (exact linear)",
               "background_n": int(len(bg)), "background_from": "train rows only", "n_test_rows": int(len(test)),
               "levers": {f: t["owner"] for f, t in tg.items() if t["tag"] == "lever"},
               "caveat": "SHAP attributes the model's score to its inputs. It is not a cause, and a lever's SHAP is not the effect of pulling it."}
    if im is not None:
        i, j = np.unravel_index(np.argmax(im), im.shape)
        summary["dependence_partners"] = {f: features[int(np.argsort(-im[features.index(f)])[0])] for f in top6}
        summary["top_interaction_pair"] = {"a": features[i], "b": features[j], "mean_abs_interaction": float(im[i, j])}
    return summary, {"shap": sv, "base": base, "shap_all": sv_all}

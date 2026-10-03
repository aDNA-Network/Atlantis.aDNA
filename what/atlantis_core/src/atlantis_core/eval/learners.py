"""The learner is a config field (thesis T2: the learner is a late, swappable choice).

    L = learner(spec, features, inst)       # spec = atlantis.yaml `learner` or one of `learner_swaps`
    val_model, final, info = L.fit(train, val)   # select on val; final = refit on train+val; test is scored once, by the caller
    m = L.refit_fixed(train, info)          # rolling origin: the selection `info` held fixed, no val
    p = L.predict(model, X)

    xgboost   early-stop on val (n_estimators/early_stopping_rounds), refit on train+val at the stopped size — as hab.train.
              Monotone constraints come from features.yaml `monotone` (+1/−1), not a list in config.
    logistic  median impute (+ a missingness flag per vital) → standardise → L2 logistic. Every statistic is fitted on
              the rows that model trains on: train for the selection model, train+val for the final — never test.
              C is chosen on val log-loss from `C_grid`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class XGBoost:
    kind = "xgboost"

    def __init__(self, spec: dict, features: list[str], monotone: dict):
        self.spec, self.features = spec, list(features)
        self.params = dict(spec["params"])
        self.params["monotone_constraints"] = "(" + ",".join(str(int(monotone.get(f, 0))) for f in self.features) + ")"

    def _clf(self, **kw):
        import xgboost as xgb
        # The vitals table is numeric by contract. xgboost 3.x defaults a fresh classifier to enable_categorical=True,
        # which shap's interventional TreeExplainer refuses even when no split is categorical; hab never saw this
        # because it explained a model re-loaded from disk (the flag is not saved). Same trees either way.
        return xgb.XGBClassifier(**kw, enable_categorical=False, **self.params)

    def fit(self, train: pd.DataFrame, val: pd.DataFrame):
        f, s = self.features, self.spec
        clf = self._clf(n_estimators=s["n_estimators"], early_stopping_rounds=s["early_stopping_rounds"])
        clf.fit(train[f], train["y"].astype(int), eval_set=[(val[f], val["y"].astype(int))], verbose=False)
        best = int(clf.best_iteration) + 1
        both = pd.concat([train, val])
        final = self._clf(n_estimators=best)
        final.fit(both[f], both["y"].astype(int), verbose=False)
        return clf, final, {"n_trees": best}

    def refit_fixed(self, train: pd.DataFrame, info: dict):
        return self._clf(n_estimators=info["n_trees"]).fit(train[self.features], train["y"].astype(int), verbose=False)

    def predict(self, model, X: pd.DataFrame) -> np.ndarray:
        return model.predict_proba(X[self.features])[:, 1]

    def describe(self, info: dict) -> str:
        import xgboost as xgb
        p = self.params
        mono = [f for f, c in zip(self.features, p["monotone_constraints"].strip("()").split(",")) if c != "0"]
        return (f"xgboost {xgb.__version__} · {p['objective']} · depth {p['max_depth']} · eta {p['learning_rate']} · "
                f"early-stop {p['eval_metric']} ({self.spec['early_stopping_rounds']} rounds) · {info['n_trees']} trees · "
                f"no scale_pos_weight · monotone on {', '.join(mono) or 'none'}")

    def importance(self, model) -> dict:
        g = model.get_booster().get_score(importance_type="gain")
        return {k: float(v) for k, v in sorted(g.items(), key=lambda kv: -kv[1])}


class Logistic:
    kind = "logistic"

    def __init__(self, spec: dict, features: list[str], monotone: dict | None = None):
        self.spec, self.features = spec, list(features)
        if spec.get("impute", "median") != "median":
            raise ValueError(f"logistic: impute {spec.get('impute')!r} — only median is implemented")

    def _pipe(self, C: float):
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        return Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)), ("scale", StandardScaler()),
                         ("lr", LogisticRegression(C=C, max_iter=int(self.spec.get("max_iter", 5000))))])

    def fit(self, train: pd.DataFrame, val: pd.DataFrame):
        from sklearn.metrics import log_loss
        f, y = self.features, train["y"].astype(int)
        scores = {}
        for C in self.spec["C_grid"]:
            m = self._pipe(float(C)).fit(train[f], y)
            scores[float(C)] = float(log_loss(val["y"].astype(int), m.predict_proba(val[f])[:, 1]))
        C = min(scores, key=scores.get)
        val_model = self._pipe(C).fit(train[f], y)
        both = pd.concat([train, val])
        final = self._pipe(C).fit(both[f], both["y"].astype(int))
        return val_model, final, {"C": C, "val_logloss_by_C": scores}

    def refit_fixed(self, train: pd.DataFrame, info: dict):
        return self._pipe(info["C"]).fit(train[self.features], train["y"].astype(int))

    def predict(self, model, X: pd.DataFrame) -> np.ndarray:
        return model.predict_proba(X[self.features])[:, 1]

    def describe(self, info: dict) -> str:
        import sklearn
        return (f"scikit-learn {sklearn.__version__} LogisticRegression · L2 · C={info['C']} (val log-loss over "
                f"{list(self.spec['C_grid'])}) · median impute + missingness flags · standardised · imputer/scaler fitted on "
                f"each model's own training rows (train for selection, train+val for the final; never test)")

    def importance(self, model) -> dict:
        lr, imp = model.named_steps["lr"], model.named_steps["impute"]
        names = list(imp.get_feature_names_out(self.features))
        return dict(sorted(((n, float(abs(c))) for n, c in zip(names, lr.coef_[0])), key=lambda kv: -kv[1]))


KINDS = {"xgboost": XGBoost, "logistic": Logistic}


def learner(spec: dict, features: list[str], inst=None):
    if spec["kind"] not in KINDS:
        raise ValueError(f"learner kind {spec['kind']!r} — expected one of {sorted(KINDS)}")
    monotone = {}
    if inst is not None:
        from atlantis_core.config import feature_name
        monotone = {feature_name(v): int(v["monotone"]) for v in inst.vitals if v.get("monotone")}
    return KINDS[spec["kind"]](spec, features, monotone)

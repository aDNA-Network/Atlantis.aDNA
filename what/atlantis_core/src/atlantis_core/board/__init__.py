"""Board emission: an evaluation becomes a GREEN board entry by code — numbers are never retyped (board README).

    ev = project(res, inst, version=1, recorded_at=...)    # the CLOSED AtlEvaluation (validates vs the committed schema)
    entry = emit(res, inst, version=1, ...)                # {board metadata · evaluation · evaluation_extras · provenance}

`evaluation` carries exactly the `AtlEvaluation` slots (WI-8: the M-0 entry mixed extras in). Everything else goes to
`evaluation_extras` — summary statistics only. `emit` refuses a result whose R7 obligations were not honoured
(reference-mode runs), and `assert_green` rejects anything per-patient: predictions, observations, labels, SHAP rows,
curves. If a field would carry one, the entry is wrong, not the rule.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlantis_core.eval.metrics import rate_key

SCHEMA = Path(__file__).resolve().parents[4] / "schema" / "atl_v0" / "atl_ontology_v0.schema.json"
ACCURACY_CLAIM = "NONE — method demonstration on public data; not an operational forecast (SO-4)"
FORBIDDEN = {"p", "p_actual", "p_scenario", "y", "weeks", "shap", "shap_all", "x", "roc", "pr", "calibration",
             "histogram_weeks_before_onset", "importance", "gain_importance", "val_logloss_by_C"}
MAX_LIST = 32   # no per-patient vector fits under this; the longest legitimate list is the rolling-origin panel


class BoardError(ValueError):
    pass


def _r(x, d=4):
    return None if x is None else round(float(x), d)


def split_text(s: dict) -> str:
    ro = s.get("rolling_origin_years") or []
    tail = f"; rolling origin {min(ro) + 1}->{max(ro) + 1}" if ro else ""
    return (f"train {s['min_train_year']}-{s['train_end']} · val {s['val_start']}-{s['val_end']} · "
            f"test {s['test_start']}-{s['test_end']}, scored once{tail}")


def _groups(inst, res):
    return res.get("feature_groups") or {}


def project(res: dict, inst, *, version: int, recorded_at: str, recorded_by: str = "agent_proteus",
            config_hash: str | None = None, learner: str | None = None, shap_summary_ref: str | None = None) -> dict:
    b, e = inst.cfg["board"], inst.cfg["eval"]
    full, t = res["full"], res["full"]["test"]
    budget = float(e["lead_budget"])
    lt = full[f"lead_time_test_{rate_key(budget)}"]
    grp = _groups(inst, res)
    ablations = []
    for ab in e.get("ablations", []) or []:
        g = ab["drop_group"]; r = res[f"no_{g}"]["test"]
        ablations.append({"ablation_name": f"without {g} group ({', '.join(grp[g])})",
                          "ablated_auroc": _r(r["auroc"]), "ablated_auprc": _r(r["auprc"])})
    so = res.get("surveillance_only_vital") or e.get("surveillance_only")
    if so and "surveillance_only_test_auroc" in res:
        ablations.append({"ablation_name": f"surveillance-only single feature ({so})", "ablated_auroc": _r(res["surveillance_only_test_auroc"])})
    pins = [{"stream_ref": sid, "sha256": s["sha256"]} for sid, s in inst.streams.items() if s.get("sha256")]
    ev = {"evaluation_id": f"{b['evaluation_id_stem']}_v{version}", "event_ref": inst.cfg["label"]["event"],
          "unit_ref": b["unit_ref"], "split": split_text(inst.cfg["split"]),
          "n_test": int(t["n"]), "n_positives": int(t["positives"]), "base_rate": _r(t["prevalence"]),
          "auroc": _r(t["auroc"]), "auprc": _r(t["auprc"]), "brier": _r(t["brier"]),
          "calibration_slope": _r(t["calibration_slope"], 2),
          "climatology_auroc": _r(res["climatology_baseline_test"]["auroc"]),
          "climatology_auprc": _r(res["climatology_baseline_test"]["auprc"]),
          "alert_budgets": [{"rate": float(r), "precision": _r(t["alert_rates"][rate_key(r)]["precision"]),
                             "recall": _r(t["alert_rates"][rate_key(r)]["recall"]),
                             "n_alerts": int(t["alert_rates"][rate_key(r)]["n_alerts"])} for r in e["alert_rates"]],
          "lead_time": {"budget_rate": budget, "n_onsets": int(lt["n_onsets"]),
                        "flagged_fraction": _r(lt["detected_fraction"]), "median_lead": lt["median_lead_weeks"]},
          "ablations": ablations,
          "learner": learner or full.get("learner"),
          "config_hash": config_hash or res["semantic_hash"],
          "data_pins": pins,
          "shap_summary_ref": shap_summary_ref,
          "claim": "method_demonstration",
          "limitations_ref": b["limitations_ref"],
          "recorded_by": recorded_by, "recorded_at": recorded_at}
    return {k: v for k, v in ev.items() if v is not None}


def validate(ev: dict) -> None:
    """The closed projection against the COMMITTED JSON Schema, with the draft's format checker (as the controls run)."""
    from jsonschema import validators
    S = json.loads(SCHEMA.read_text())
    VC = validators.validator_for(S); FC = VC.FORMAT_CHECKER
    if FC.conforms("never", "date-time"):
        raise BoardError("jsonschema format checker does not check date-time here (install jsonschema[format]) — instrument failure")
    errs = list(VC(S, format_checker=FC).iter_errors({"evaluations": [ev]}))
    if errs:
        raise BoardError("closed AtlEvaluation rejected: " + "; ".join(f"{'/'.join(map(str, x.absolute_path))}: {x.message[:120]}" for x in errs))


def assert_green(obj, path="") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN:
                raise BoardError(f"never on the board: {path}/{k} (per-patient or per-row content)")
            assert_green(v, f"{path}/{k}")
    elif isinstance(obj, list):
        if len(obj) > MAX_LIST:
            raise BoardError(f"never on the board: {path} is a {len(obj)}-long list (per-patient vectors do not cross)")
        for i, v in enumerate(obj):
            assert_green(v, f"{path}[{i}]")


def _swap_summary(sw: dict) -> dict:
    t, ro = sw["full"]["test"], [r["auroc"] for r in sw["rolling_origin"]]
    lt = next(v for k, v in sw["full"].items() if k.startswith("lead_time_test_"))
    return {"learner": sw["full"]["learner"], "test_auroc": _r(t["auroc"]), "test_auprc": _r(t["auprc"]),
            "brier": _r(t["brier"]), "calibration_slope": _r(t["calibration_slope"], 2),
            "alert_budgets": {k: {"precision": _r(v["precision"]), "recall": _r(v["recall"])} for k, v in t["alert_rates"].items()},
            "lead_time": {"flagged_fraction": _r(lt["detected_fraction"]), "median_lead": lt["median_lead_weeks"], "n_onsets": lt["n_onsets"]},
            "rolling_origin_auroc_range": [_r(min(ro)), _r(max(ro))],
            "top6": sw.get("shap_summary", {}).get("top6"),
            "group_mean_abs_shap": sw.get("shap_summary", {}).get("group_mean_abs_shap")}


def emit(res: dict, inst, *, version: int, run_date: str, recorded_at: str, shap: dict, swaps: dict | None = None,
         delta_vs: dict | None = None, notes: list | None = None, provenance: dict | None = None,
         shap_summary_ref: str | None = None) -> dict:
    bad = [o["obligation"] for o in res.get("obligations", []) if not o["honoured"]]
    if bad or res.get("mode") != "core":
        raise BoardError("refusing to emit: unhonoured obligations / reference-mode result —\n  " + "\n  ".join(bad or [str(res.get("mode"))]))
    from atlantis_core import __version__
    b = inst.cfg["board"]
    ev = project(res, inst, version=version, recorded_at=recorded_at, shap_summary_ref=shap_summary_ref)
    validate(ev)
    event = inst.event
    rep = res["features_report"]
    grp = _groups(inst, res)
    extras = {
        "event": {k: event.get(k) for k in ("event_id", "threshold", "unit", "direction", "horizon", "onset_rule")},
        "patient": {**b["patient"], "n_units": len(inst.cfg["grid"].get("rules") or inst.cfg["grid"].get("units") or [])},
        "modelling_rows": rep["modelling_rows"], "modelling_positives": rep["positives"], "modelling_prevalence": _r(rep["prevalence"]),
        "dropped_already_in_event": rep["dropped_already_in_event"], "dropped_outcome_unknown": rep["dropped_outcome_unknown"],
        "n_trees": res["full"].get("n_trees"), "n_vitals": len(res["features"]), "vital_groups": {g: len(v) for g, v in grp.items()},
        "sensitivity": [{"name": f"threshold {res['sensitivity']['threshold']:g} {event.get('unit', '')}".strip(),
                         "test_auroc": _r(res["sensitivity"]["test_auroc"]), "test_auprc": _r(res["sensitivity"]["test_auprc"]),
                         "test_prevalence": _r(res["sensitivity"]["test_prevalence"])}] if "sensitivity" in res else [],
        "rolling_origin": [{k: (_r(v) if k in ("prevalence", "auroc", "auprc") else v) for k, v in r.items()} for r in res["rolling_origin"]],
        "obligations": res.get("obligations", []),
        "shap_summary": {k: shap[k] for k in ("base_p", "additivity_max_gap", "top6", "group_mean_abs_shap", "tag_mean_abs_shap") if k in shap},
        "semantic_hash": res["semantic_hash"], "config_bytes_md5": res.get("config_bytes_md5", {}),
        "data_pins": [{"stream_ref": sid, "artifact": inst.stream_spec(sid).get("artifact"), "sha256": s["sha256"]}
                      for sid, s in inst.streams.items() if s.get("sha256")],
        "learner_swaps": [_swap_summary(sw) for sw in (swaps or {}).values()],
    }
    if delta_vs:
        extras["delta_vs"] = delta_vs
    entry = {"board_entry_schema": "atl_board_entry_v1", "tier": "GREEN", "accuracy_claim": ACCURACY_CLAIM,
             "entry_id": f"{run_date}_{b['entry_stem']}_v{version}", "source": b["source"], "instance": b["instance"],
             "method_version": b["method_version"].format(version=__version__), "recorded_by": ev["recorded_by"],
             "recorded_at": recorded_at, "run_date": run_date, "evaluation": ev, "evaluation_extras": extras,
             "provenance": provenance or {}, "notes": notes or []}
    assert_green(entry)
    return entry


def delta(new_ev: dict, old_entry: dict) -> dict:
    o = old_entry["evaluation"]
    keys = ("n_test", "n_positives", "base_rate", "auroc", "auprc", "brier", "calibration_slope", "climatology_auroc", "climatology_auprc")
    d = {k: {"was": o.get(k), "now": new_ev.get(k), "change": (None if o.get(k) is None or new_ev.get(k) is None else _r(new_ev[k] - o[k]))}
         for k in keys}
    d["lead_time"] = {"was": o.get("lead_time"), "now": new_ev.get("lead_time")}
    return {"entry": old_entry["entry_id"], "fields": d}

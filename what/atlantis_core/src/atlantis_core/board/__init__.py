"""Board emission: an evaluation becomes a GREEN board entry by code — numbers are never retyped (board README).

    ev = project(res, inst, version=1, recorded_at=...)    # the CLOSED AtlEvaluation (validates vs the committed schema)
    entry = emit(res, inst, version=1, ...)                # {board metadata · evaluation · evaluation_extras · provenance}

`evaluation` carries exactly the `AtlEvaluation` slots (WI-8: the M-0 entry mixed extras in). Everything else goes to
`evaluation_extras` — summary statistics only. `emit` refuses a result whose R7 obligations were not honoured
(reference-mode runs) — the headline's and every learner swap's — and `assert_green` keeps per-patient content off:
an allowlist of `evaluation_extras` keys, a denylist of per-row field names, and caps on list length, dict size, numeric
leaves and numbers inside any string (M-1b-ii-a III F-4: a denylist alone let 1,640 keyed predictions through). If a
field would carry per-patient content, the entry is wrong, not the rule.

**F-8 (M-1e).** A budget's threshold must have been fixed before test was scored: `emit` refuses any budget or lead time
whose `threshold_from` is not `validation`, and any validation budget without its realised rate (atl_v0 0.4.0). The
projection maps the core's `val` to the ontology's `validation`, and leaves both fields out for a result that predates
them, so v1's run still re-projects onto v1 (the v1 page's build check).
"""
from __future__ import annotations

import json, re
from pathlib import Path

from atlantis_core.eval.metrics import rate_key

SCHEMA = Path(__file__).resolve().parents[4] / "schema" / "atl_v0" / "atl_ontology_v0.schema.json"
ACCURACY_CLAIM = "NONE — method demonstration on public data; not an operational forecast (SO-4)"
FORBIDDEN = {"p", "p_actual", "p_scenario", "y", "weeks", "shap", "shap_all", "x", "roc", "pr", "calibration",
             "histogram_weeks_before_onset", "importance", "gain_importance", "val_logloss_by_C"}
MAX_LIST = 32          # no per-patient vector fits under this; the longest legitimate list is the rolling-origin panel
MAX_DICT = 40          # a dict keyed by patient-week would exceed this; the widest legitimate one is a group/tag table
MAX_NUMERIC = 600      # numeric leaves in a whole entry (v1 carries ~250)
MAX_STRING_NUMBERS = 40   # numbers inside one string — notes are prose, not a smuggled vector
EXTRAS_KEYS = {"rolling_selection", "event", "patient", "modelling_rows", "modelling_positives", "modelling_prevalence",
               "dropped_already_in_event", "dropped_outcome_unknown", "n_trees", "n_vitals", "vital_groups",
               "sensitivity", "rolling_origin", "obligations", "shap_summary", "semantic_hash", "config_bytes_md5",
               "data_pins", "learner_swaps", "delta_vs", "regenerated"}


class BoardError(ValueError):
    pass


def _r(x, d=4):
    return None if x is None else round(float(x), d)


def split_text(s: dict) -> str:
    ro = s.get("rolling_origin_years") or []
    tail = f"; rolling origin {min(ro) + 1}->{max(ro) + 1}" if ro else ""
    return (f"train {s['min_train_year']}-{s['train_end']} · val {s['val_start']}-{s['val_end']} · "
            f"test {s['test_start']}-{s['test_end']}, scored once{tail}")


SOURCE = {"val": "validation", "test": "test"}   # atlantis_core eval mode → atl_v0 ThresholdSource


def _budget(r: float, a: dict) -> dict:
    out = {"rate": float(r), "precision": _r(a["precision"]), "recall": _r(a["recall"]), "n_alerts": int(a["n_alerts"])}
    if "threshold_from" in a:   # absent in results that predate M-1e (v1's run) — then the projection is v1's shape
        out["threshold_from"] = SOURCE[a["threshold_from"]]
        if a.get("realised_rate") is not None:   # absent → the emit check names it (and the schema rule rejects it)
            out["realised_rate"] = _r(a["realised_rate"])
    return out


def _groups(inst, res):
    return res.get("feature_groups") or {}


def project(res: dict, inst, *, version: int, recorded_at: str, recorded_by: str = "agent_proteus",
            config_hash: str | None = None, learner: str | None = None, shap_summary_ref: str | None = None,
            limitations_ref: str | None = None) -> dict:
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
          "alert_budgets": [_budget(r, t["alert_rates"][rate_key(r)]) for r in e["alert_rates"]],
          "lead_time": {"budget_rate": budget, "n_onsets": int(lt["n_onsets"]),
                        "flagged_fraction": _r(lt["detected_fraction"]), "median_lead": lt["median_lead_weeks"],
                        **({"threshold_from": SOURCE[lt["threshold_from"]]} if "threshold_from" in lt else {})},
          "ablations": ablations,
          "learner": learner or full.get("learner"),
          "config_hash": config_hash or res["semantic_hash"],
          "data_pins": pins,
          "shap_summary_ref": shap_summary_ref,
          "claim": "method_demonstration",
          "limitations_ref": limitations_ref or b["limitations_ref"],   # the instance's CURRENT limits; a record may cite its own
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


def assert_thresholds_fixed(ev: dict, res: dict, swaps: dict | None = None) -> None:
    """F-8: no new entry carries a threshold chosen on the years it scores, or a nominal rate without its realised one —
    the headline's budgets and lead time, and every learner swap's. The rolling panel must have selected per fold."""
    bad = []
    for b in ev.get("alert_budgets", []):
        if b.get("threshold_from") != "validation":
            bad.append(f"budget {b['rate']}: threshold_from {b.get('threshold_from')!r}")
        elif b.get("realised_rate") is None:
            bad.append(f"budget {b['rate']}: no realised rate beside the nominal one")
    if (ev.get("lead_time") or {}).get("threshold_from") != "validation":
        bad.append(f"lead_time: threshold_from {(ev.get('lead_time') or {}).get('threshold_from')!r}")
    for name, r in [("headline", res), *[(f"learner swap {k}", v) for k, v in (swaps or {}).items()]]:
        if r["full"].get("threshold_from") != "val":
            bad.append(f"{name}: eval.threshold_from {r['full'].get('threshold_from')!r}")
        if r.get("rolling_selection") != "per_fold":
            bad.append(f"{name}: rolling folds selected {r.get('rolling_selection')!r}, not per fold")
    if bad:
        raise BoardError("refusing to emit — thresholds chosen on the years they score (F-8): " + "; ".join(bad))


_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")


def assert_green(obj, path="", _count=None) -> None:
    top = _count is None
    _count = _count if _count is not None else [0]
    if top and isinstance(obj, dict) and isinstance(obj.get("evaluation_extras"), dict):
        extra = set(obj["evaluation_extras"]) - EXTRAS_KEYS
        if extra:
            raise BoardError(f"never on the board: evaluation_extras keys outside the allowlist {sorted(extra)}")
    if isinstance(obj, dict):
        if len(obj) > MAX_DICT:
            raise BoardError(f"never on the board: {path} is a {len(obj)}-key dict (per-patient tables do not cross)")
        for k, v in obj.items():
            if k in FORBIDDEN:
                raise BoardError(f"never on the board: {path}/{k} (per-patient or per-row content)")
            assert_green(v, f"{path}/{k}", _count)
    elif isinstance(obj, list):
        if len(obj) > MAX_LIST:
            raise BoardError(f"never on the board: {path} is a {len(obj)}-long list (per-patient vectors do not cross)")
        for i, v in enumerate(obj):
            assert_green(v, f"{path}[{i}]", _count)
    elif isinstance(obj, str):
        if len(_NUM.findall(obj)) > MAX_STRING_NUMBERS:
            raise BoardError(f"never on the board: {path} carries {len(_NUM.findall(obj))} numbers in one string")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        _count[0] += 1
        if _count[0] > MAX_NUMERIC:
            raise BoardError(f"never on the board: more than {MAX_NUMERIC} numbers in one entry (at {path})")


def _swap_summary(sw: dict) -> dict:
    t, ro = sw["full"]["test"], [r["auroc"] for r in sw["rolling_origin"]]
    lt = next(v for k, v in sw["full"].items() if k.startswith("lead_time_test_"))
    return {"learner": sw["full"]["learner"], "test_auroc": _r(t["auroc"]), "test_auprc": _r(t["auprc"]),
            "brier": _r(t["brier"]), "calibration_slope": _r(t["calibration_slope"], 2),
            "alert_budgets": {k: {"precision": _r(v["precision"]), "recall": _r(v["recall"]),
                                  **({"realised_rate": _r(v["realised_rate"]), "threshold_from": SOURCE[v["threshold_from"]]}
                                     if "threshold_from" in v else {})} for k, v in t["alert_rates"].items()},
            "lead_time": {"flagged_fraction": _r(lt["detected_fraction"]), "median_lead": lt["median_lead_weeks"], "n_onsets": lt["n_onsets"]},
            "rolling_origin_auroc_range": [_r(min(ro)), _r(max(ro))],
            "top6": sw.get("shap_summary", {}).get("top6"),
            "group_mean_abs_shap": sw.get("shap_summary", {}).get("group_mean_abs_shap"),
            "group_net_mean_abs_shap": sw.get("shap_summary", {}).get("group_net_mean_abs_shap"),
            "semantic_hash": sw.get("semantic_hash")}


def emit(res: dict, inst, *, version: int, run_date: str, recorded_at: str, shap: dict, swaps: dict | None = None,
         delta_vs: dict | None = None, notes: list | None = None, provenance: dict | None = None,
         shap_summary_ref: str | None = None, regenerated: dict | None = None) -> dict:
    for name, r in [("headline", res), *[(f"learner swap {k}", v) for k, v in (swaps or {}).items()]]:   # III F-5
        bad = [o["obligation"] for o in r.get("obligations", []) if not o["honoured"]]
        if bad or r.get("mode") != "core":
            raise BoardError(f"refusing to emit ({name}): unhonoured obligations / reference-mode result —\n  "
                             + "\n  ".join(bad or [str(r.get("mode"))]))
    from atlantis_core import __version__
    b = inst.cfg["board"]
    ev = project(res, inst, version=version, recorded_at=recorded_at, shap_summary_ref=shap_summary_ref)
    assert_thresholds_fixed(ev, res, swaps)   # before the schema, so the refusal names F-8 rather than a slot
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
        "rolling_selection": res.get("rolling_selection"),
        "obligations": res.get("obligations", []),
        "shap_summary": {k: shap[k] for k in ("base_p", "additivity_max_gap", "top6", "group_mean_abs_shap", "group_net_mean_abs_shap",
                                              "tag_mean_abs_shap") if k in shap},
        "semantic_hash": res["semantic_hash"], "config_bytes_md5": res.get("config_bytes_md5", {}),
        "data_pins": [{"stream_ref": sid, "artifact": inst.stream_spec(sid).get("artifact"), "sha256": s["sha256"]}
                      for sid, s in inst.streams.items() if s.get("sha256")],
        "learner_swaps": [_swap_summary(sw) for sw in (swaps or {}).values()],
    }
    if delta_vs:
        extras["delta_vs"] = delta_vs
    if regenerated:
        extras["regenerated"] = regenerated
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
    ob = {rate_key(b["rate"]): b for b in o.get("alert_budgets", [])}   # keyed as metrics.json is (10pct): a page token can reach it
    d["alert_budgets"] = {rate_key(b["rate"]): {k: {"was": ob.get(rate_key(b["rate"]), {}).get(k), "now": b.get(k)}
                                           for k in ("precision", "recall", "n_alerts", "realised_rate", "threshold_from")}
                          for b in new_ev.get("alert_budgets", [])}
    return {"entry": old_entry["entry_id"], "fields": d}


def delta_rolling(new_rows: list, old_entry: dict) -> dict:
    """Per rolling fold, was → now (AUROC, AUPRC, and how the fold selected). Folds keyed by test year."""
    old = {r["test_year"]: r for r in (old_entry.get("evaluation_extras") or {}).get("rolling_origin", [])}
    out = {}
    for r in new_rows:
        o = old.get(r["test_year"], {})
        out[str(r["test_year"])] = {"auroc": {"was": o.get("auroc"), "now": _r(r["auroc"])},
                                    "auprc": {"was": o.get("auprc"), "now": _r(r["auprc"])},
                                    "selected_on": (r.get("selection") or {}).get("selected_on"),
                                    "n_trees": (r.get("selection") or {}).get("n_trees")}
    return out

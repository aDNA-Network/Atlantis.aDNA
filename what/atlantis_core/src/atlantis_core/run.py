"""The instance end to end through atlantis_core: registries → vitals → label → eval → explain → what-if → outputs.

    python -m atlantis_core.run --instance <dir> [--out outputs/atlantis_core] [--no-swaps]

Writes `<instance>/<out>/`: metrics.json · shap_summary.json · whatif.json · model.json (xgboost) ·
learner_swap_<kind>.json (one per `learner_swaps` entry, T2). Scored tables go to `<instance>/data/processed/atlantis_core/`
(per-patient — never committed, never on the board). Every R7 obligation is honoured here (per-fold climatology refit),
so the results are board-eligible. Method demonstration, not an operational forecast (SO-4).
"""
from __future__ import annotations

import argparse, hashlib, json, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

from atlantis_core import __version__, explain, label, semantic_hash
from atlantis_core.config import load_instance
from atlantis_core.eval import run as eval_run
from atlantis_core.eval.rolling import FoldTables
from atlantis_core.explain import whatif
from atlantis_core.vitals import grammar
from atlantis_core.vitals.build import build, evaluator, load_frames, patient_grid

LABEL_COLS = ("future_signal", "last_known_signal", "y", "already_in_event", "outcome_unknown")


def signal_panel(inst, frames, units, weeks) -> pd.DataFrame:
    """The event signal on the FULL unit-week grid (lead time reads onsets here, not only in modelling rows)."""
    sid = inst.event["event_variable_stream"]
    e = evaluator(inst, sid, frames, units, weeks)
    sig = e.weekly(grammar.parse(inst.cfg["label"]["signal"], list(inst.cfg.get("constants", {})), "label.signal"))
    ucol = inst.cfg["grid"].get("unit_column", "unit")
    panel = pd.MultiIndex.from_product([units, weeks], names=[ucol, "week"]).to_frame(index=False)
    panel["signal"] = label._cut(sig, units, weeks).values
    return panel


def relabel(inst, frames, table, units, weeks, threshold) -> tuple[pd.DataFrame, dict]:
    """The same vitals, the label re-made at another threshold (the sensitivity run). Vitals are NOT rebuilt — a
    vital that reads `event_threshold` keeps the declared event's value, as hab's sensitivity run did."""
    sid = inst.event["event_variable_stream"]
    evs = {sid: evaluator(inst, sid, frames, units, weeks)}
    base = table.drop(columns=[c for c in LABEL_COLS if c in table])
    t2 = label.make(inst, base, evs, units, weeks, event={**inst.event, "threshold": threshold})
    return label.finalize(inst, t2)


def bytes_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:10]


def _json(o):
    if isinstance(o, dict): return {str(k): _json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_json(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if not np.isfinite(o) else float(o)
    return o


def write(path: Path, obj) -> None:
    path.write_text(json.dumps(_json(obj), indent=1, allow_nan=False) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.run")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--out", default="outputs/atlantis_core")
    ap.add_argument("--no-swaps", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    inst = load_instance(a.instance)
    out = inst.root / a.out; out.mkdir(parents=True, exist_ok=True)
    proc = inst.root / "data" / "processed" / "atlantis_core"; proc.mkdir(parents=True, exist_ok=True)
    frames = load_frames(inst)
    units, weeks = patient_grid(inst, frames)
    table, info = build(inst, frames)
    model_df, report = label.finalize(inst, table)
    print(f"vitals: {info['n_patient_weeks']} patient-weeks · modelling {report['modelling_rows']} rows · "
          f"{report['positives']} positives · dropped {report['dropped_already_in_event']} + {report['dropped_outcome_unknown']}")
    panel = signal_panel(inst, frames, units, weeks)
    sens_df = None
    thr = inst.cfg["eval"].get("sensitivity_threshold")
    if thr is not None:
        sens_df, _ = relabel(inst, frames, table, units, weeks, float(thr))
    folds = FoldTables(inst, frames, model_df)
    provenance = {"atlantis_core": __version__, "semantic_hash": semantic_hash(inst),
                  "config_bytes_md5": {p.name: bytes_md5(p) for p in (inst.root / "atlantis.yaml", inst.root / "config.yaml") if p.exists()},
                  "features_report": report, "run_at": pd.Timestamp.now("UTC").isoformat()}

    res, art = eval_run(inst, model_df, panel, fold_tables=folds, sensitivity_df=sens_df)
    res.update(provenance)
    full = art["full"]
    summ, arrays = explain.shap_explain(inst, full["learner"], full["model"], art["all_scored"], art["test_scored"])
    print(f"explain: additivity gap {summ['additivity_max_gap']:.2e} · top6 {summ['top6']}")
    wi = whatif.run(inst, frames, full["learner"], full["model"], art["all_scored"])
    write(out / "metrics.json", res); write(out / "shap_summary.json", summ); write(out / "whatif.json", wi)
    if full["learner"].kind == "xgboost":
        full["model"].save_model(out / "model.json")
    art["test_scored"].to_parquet(proc / "test_scored.parquet", index=False)
    art["all_scored"].to_parquet(proc / "all_scored.parquet", index=False)
    np.savez_compressed(proc / "shap.npz", **arrays)

    if not a.no_swaps:
        for spec in inst.cfg.get("learner_swaps", []) or []:
            print(f"── learner swap: {spec['kind']} (T2) ──")
            r2, a2 = eval_run(inst, model_df, panel, fold_tables=folds, sensitivity_df=sens_df, learner_spec=spec)
            s2, _ = explain.shap_explain(inst, a2["full"]["learner"], a2["full"]["model"], a2["all_scored"], a2["test_scored"])
            r2.update(provenance); r2["shap_summary"] = s2
            write(out / f"learner_swap_{spec['kind']}.json", r2)
    print(f"→ {out.relative_to(inst.root)}/ ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

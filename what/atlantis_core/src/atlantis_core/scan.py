"""The val-only scan of one declared constant (M-3b-ii-b-1): pick a value on validation without ever reading test.

    python -m atlantis_core.scan --instance <dir> --constant calm_threshold --values 2,3,4,5,6 [--out outputs/scan_<name>]

For each value: the constant is overridden, the vitals and the label are built as `run` builds them, **the test weeks
are dropped before anything is split or fitted** (a test week is one whose ISO week starts in a test year — `eval.split`'s
definition; the last val week holds the first days of the first test year, and a val row's label window can read them,
as in `run`), and the selection fit `run` would make (`eval.select`: train
embargoed against val, stopped on val embargoed against test) is scored on that stop set. It never refits on train ∪ val
and never scores test: the value is chosen here, then `run` scores test once, at the chosen value (contract item 8).

Writes `<instance>/<out>/scan.json` — a GREEN table (metrics and counts only, nothing per patient): per value, the
semantic hash it would run under, val log-loss · AUROC · AUPRC at the val base rate, the selection (n_trees or C), and
the fitted station offsets of every stream that declares them.

**Disclosed bias.** An xgboost selection model is early-stopped on this same val set, so its val log-loss is optimistic.
The optimism is the same kind for every value, so the rows compare with one another; none of them compares with a test
number. Method demonstration, not an operational forecast (SO-4).
"""
from __future__ import annotations

import argparse, ast, copy, json, sys, time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score

from atlantis_core import __version__, label
from atlantis_core.config import load_instance, semantic_hash
from atlantis_core.eval import ObligationError, _embargo_of, select, split
from atlantis_core.eval.learners import learner
from atlantis_core.vitals import grammar
from atlantis_core.vitals.build import build, evaluator, load_frames, patient_grid


def readers(inst, name: str) -> list[str]:
    """The vitals whose transform reads the constant."""
    consts = list(inst.cfg.get("constants", {}))
    return [v["vital_id"] for v in inst.vitals
            if name in {n.id for n in ast.walk(grammar.parse(v["transform"], consts, v["vital_id"])) if isinstance(n, ast.Name)}]


def station_offsets(inst, frames) -> dict:
    """stream → {station: {offset, n_days}} for every stream that declares `station_offsets` (as the build fits them)."""
    units, weeks = patient_grid(inst, frames)
    out = {}
    for sid, spec in inst.cfg["streams"].items():
        if spec.get("station_offsets"):
            e = evaluator(inst, sid, frames, units, weeks)
            e._value()
            out[sid] = e.offsets
    return out


def scan(inst, name: str, values, frames: dict | None = None, log=print) -> dict:
    if name not in (inst.cfg.get("constants") or {}):
        raise ValueError(f"constant {name!r} is not declared under atlantis.yaml → constants")
    who = readers(inst, name)
    if not who:
        raise ValueError(f"no vital reads constant {name!r} — scanning it would change nothing")
    s = inst.cfg["split"]
    frames = frames if frames is not None else load_frames(inst)
    spec = inst.cfg["learner"]
    rows = []
    for v in values:
        i2 = copy.deepcopy(inst)
        i2.cfg["constants"][name] = float(v)
        table, _ = build(i2, frames)
        model_df, report = label.finalize(i2, table)
        df = model_df[model_df["week"].dt.year < int(s["test_start"])].copy()      # test years dropped FIRST
        df["y"] = df["y"].astype(int)
        train, val, test = split(df, s)
        if len(test):
            raise ObligationError(f"scan: {len(test)} test rows survived the cut")
        E, _ = _embargo_of(i2)
        L = learner(spec, i2.feature_names, i2)
        R, vm, info, stop = select(L, train, val, s, E)
        for kind, a, b in R.fits:                                               # what the learner RECEIVED (C-023)
            for part in ((a, b) if kind == "fit" else ()):
                if len(part) and int(part["week"].dt.year.max()) >= int(s["test_start"]):
                    raise ObligationError(f"scan: the {kind} received rows from {int(part['week'].dt.year.max())} — "
                                          f"test starts {s['test_start']}")
        p = L.predict(vm, stop)
        y = stop["y"].to_numpy(int)
        rows.append({
            "value": float(v), "semantic_hash": semantic_hash(i2),
            "selection": {k: info[k] for k in ("n_trees", "C") if k in info},
            "train": {"n": int(len(train)), "positives": int(train["y"].sum())},
            "val": {"n": int(len(stop)), "positives": int(y.sum()), "base_rate": float(y.mean()),
                    "log_loss": float(log_loss(y, np.clip(p, 1e-15, 1 - 1e-15), labels=[0, 1])),
                    "auroc": float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else None,
                    "auprc": float(average_precision_score(y, p)) if y.sum() else None},
        })
        r = rows[-1]["val"]
        log(f"{name} = {v:g}: val log-loss {r['log_loss']:.5f} · AUROC {r['auroc'] if r['auroc'] is None else round(r['auroc'], 4)}"
            f" · AUPRC {r['auprc'] if r['auprc'] is None else round(r['auprc'], 4)} at base rate {r['base_rate']:.4f} "
            f"(n {r['n']}) · {rows[-1]['selection']}")
    best = min(rows, key=lambda r: r["val"]["log_loss"])
    return {"scan": "atlantis_core.scan", "atlantis_core": __version__, "constant": name, "read_by": who,
            "values": [float(v) for v in values], "chosen_by": "min val log-loss (selection model, stop set)",
            "chosen": best["value"], "rows": rows, "station_offsets": station_offsets(inst, frames),
            "split": {k: s[k] for k in ("min_train_year", "train_end", "val_start", "val_end", "test_start")},
            "test_scored": False,
            "bias": "xgboost early-stops on the same val set: val log-loss is optimistic, alike for every value — compare "
                    "rows with one another, never with a test number"}


def _json(o):
    if isinstance(o, dict): return {str(k): _json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_json(v) for v in o]
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, (np.floating, float)): return None if not np.isfinite(o) else float(o)
    return o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.scan")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--constant", required=True)
    ap.add_argument("--values", required=True, help="comma-separated, e.g. 2,3,4,5,6")
    ap.add_argument("--out", default=None, help="default outputs/scan_<constant>")
    a = ap.parse_args(argv)
    t0 = time.time()
    inst = load_instance(a.instance)
    vals = [float(x) for x in a.values.split(",") if x.strip()]
    res = scan(inst, a.constant, vals)
    res["run_at"] = pd.Timestamp.now("UTC").isoformat()
    out = inst.root / (a.out or f"outputs/scan_{a.constant}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "scan.json").write_text(json.dumps(_json(res), indent=1, allow_nan=False) + "\n")
    print(f"chosen {a.constant} = {res['chosen']:g} (min val log-loss) · test not scored → "
          f"{(out / 'scan.json').relative_to(inst.root)} ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

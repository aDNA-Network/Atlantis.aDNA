"""python -m atlantis_core.board --instance <dir> --version N --run-date YYYY-MM-DD [--vs <old entry>] [--note …]…

Reads `<instance>/outputs/atlantis_core/{metrics,shap_summary}.json` + `learner_swap_*.json` and writes
`what/board/entries/<run_date>_<stem>_v<N>.json`. Refuses an existing file (entries are never overwritten, SO-2) —
except `--regenerate "<reason>"`, which is refused unless the file has never reached `origin` (an entry no one else
has seen may be corrected in place; the regeneration and its reason are recorded in `evaluation_extras.regenerated`).
"""
import argparse, glob, json, subprocess, sys
from pathlib import Path

import pandas as pd

from atlantis_core.board import BoardError, delta, emit, project
from atlantis_core.config import load_instance

ENTRIES = Path(__file__).resolve().parents[4] / "board" / "entries"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.board")
    ap.add_argument("--instance", required=True); ap.add_argument("--version", type=int, required=True)
    ap.add_argument("--run-date", required=True); ap.add_argument("--outputs", default="outputs/atlantis_core")
    ap.add_argument("--vs"); ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--regenerate", metavar="REASON")
    a = ap.parse_args(argv)
    inst = load_instance(a.instance)
    o = inst.root / a.outputs
    res = json.loads((o / "metrics.json").read_text()); shap = json.loads((o / "shap_summary.json").read_text())
    swaps = {Path(p).stem: json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(o / "learner_swap_*.json")))}
    now = pd.Timestamp.now("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    rel = lambda p: str(p.relative_to(ENTRIES.parents[2]))
    out = ENTRIES / f"{a.run_date}_{inst.cfg['board']['entry_stem']}_v{a.version}.json"
    regen = None
    if out.exists():
        if not a.regenerate:
            print(f"✗ {out.name} exists — entries are never overwritten (SO-2)"); return 1
        git = lambda *c: subprocess.run(["git", "-C", str(ENTRIES), *c], capture_output=True, text=True)
        if git("log", "--oneline", "origin/main", "--", out.name).stdout.strip():
            print(f"✗ {out.name} has reached origin — publish a new version instead (SO-2)"); return 1
        prev = git("log", "-1", "--format=%h", "--", out.name).stdout.strip()
        regen = {"replaces_commit": prev or None, "reason": a.regenerate, "at": now}
    dv = None
    if a.vs:
        ev = project(res, inst, version=a.version, recorded_at=now)
        dv = delta(ev, json.loads(Path(a.vs).read_text()))
    try:
        entry = emit(res, inst, version=a.version, run_date=a.run_date, recorded_at=now, shap=shap, swaps=swaps,
                     delta_vs=dv, notes=a.note, shap_summary_ref=rel(o / "shap_summary.json"), regenerated=regen,
                     provenance={"metrics_file": rel(o / "metrics.json"), "shap_file": rel(o / "shap_summary.json"),
                                 "learner_swap_files": [rel(o / f"{k}.json") for k in swaps],
                                 "generated_by": "atlantis_core.board (emit → closed AtlEvaluation validated against the committed "
                                                 "atl_ontology_v0.schema.json + assert_green); numbers are not retyped"})
    except BoardError as e:
        print(f"✗ {e}"); return 1
    assert out.name == f"{entry['entry_id']}.json"
    out.write_text(json.dumps(entry, indent=1, ensure_ascii=False) + "\n")
    print(f"→ {rel(out)}  ({entry['evaluation']['evaluation_id']}: AUROC {entry['evaluation']['auroc']} · AUPRC {entry['evaluation']['auprc']} · base rate {entry['evaluation']['base_rate']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

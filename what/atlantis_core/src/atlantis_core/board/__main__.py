"""python -m atlantis_core.board --instance <dir> --version N --run-date YYYY-MM-DD [--vs <old entry>] [--note …]… [--entries <dir>]
python -m atlantis_core.board --index [--check] [--entries <dir>]

Reads `<instance>/outputs/atlantis_core/{metrics,shap_summary}.json` + `learner_swap_*.json` and writes
`<entries>/<run_date>_<stem>_v<N>.json`. `--entries` defaults to Atlantis's own `what/board/entries/`; an instance passes
its own `<instance>/what/board/entries` (contract §A — the entry then travels to Atlantis by coordination memo, never by
direct write). It must end in `what/board/entries`, so every provenance path stays relative to the repo that holds it.
`--index` regenerates `<entries>/../BOARD.md` (`atlantis_core.board.index`); `--index --check` writes nothing. Refuses an existing file (entries are never overwritten, SO-2) —
except `--regenerate "<reason>"`, which is refused unless the file has never reached `origin` (an entry no one else
has seen may be corrected in place; the regeneration and its reason are recorded in `evaluation_extras.regenerated`).
"""
import argparse, glob, json, subprocess, sys
from pathlib import Path

import pandas as pd

from atlantis_core.board import BoardError, delta, delta_rolling, emit, project
from atlantis_core.board.index import write_or_check
from atlantis_core.config import load_instance

ENTRIES = Path(__file__).resolve().parents[4] / "board" / "entries"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.board")
    ap.add_argument("--instance"); ap.add_argument("--version", type=int)
    ap.add_argument("--run-date"); ap.add_argument("--outputs", default="outputs/atlantis_core")
    ap.add_argument("--vs"); ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--regenerate", metavar="REASON")
    ap.add_argument("--entries", default=str(ENTRIES), help="the board's entries dir (default: Atlantis's own)")
    ap.add_argument("--index", action="store_true", help="regenerate BOARD.md beside the entries dir")
    ap.add_argument("--check", action="store_true", help="with --index: exit 1 if BOARD.md is stale; write nothing")
    a = ap.parse_args(argv)
    entries = Path(a.entries).resolve()
    if entries.parts[-3:] != ("what", "board", "entries"):
        print(f"✗ --entries must be a <repo>/what/board/entries directory (got {a.entries})"); return 1
    if a.index:
        if a.instance or a.version is not None or a.run_date:
            print("✗ --index renders the board; it does not emit (drop --instance/--version/--run-date)"); return 1
        return write_or_check(entries, a.check)
    if a.check:
        print("✗ --check goes with --index"); return 1
    missing = [f for f, v in (("--instance", a.instance), ("--version", a.version), ("--run-date", a.run_date)) if v is None]
    if missing:
        ap.error("emitting an entry needs " + ", ".join(missing))
    if not entries.is_dir():
        print(f"✗ no entries directory at {entries} (create it in the instance; nothing is written elsewhere)"); return 1
    inst = load_instance(a.instance)
    o = inst.root / a.outputs
    repo, iroot = entries.parents[2], inst.root.resolve()
    # III F-1 (C-018): gate on the IDENTITY (the instance root), not on a proxy another flag can point anywhere.
    if not (iroot == repo or repo in iroot.parents):
        print(f"✗ the instance ({inst.root}) is not inside the repo that holds {entries} — an instance writes its own "
              f"board (--entries <instance>/what/board/entries); its entry reaches Atlantis by coordination memo, never "
              f"by direct write (contract §A/§D)"); return 1
    if iroot not in o.resolve().parents:
        print(f"✗ --outputs ({o}) is not inside the instance ({inst.root}) — an entry pairs an instance's config with "
              f"ITS OWN run's metrics"); return 1
    res = json.loads((o / "metrics.json").read_text()); shap = json.loads((o / "shap_summary.json").read_text())
    swaps = {Path(p).stem: json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(o / "learner_swap_*.json")))}
    now = pd.Timestamp.now("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    rel = lambda p: str(Path(p).resolve().relative_to(entries.parents[2]))
    out = entries / f"{a.run_date}_{inst.cfg['board']['entry_stem']}_v{a.version}.json"
    regen = None
    if out.exists():
        if not a.regenerate:
            print(f"✗ {out.name} exists — entries are never overwritten (SO-2)"); return 1
        git = lambda *c: subprocess.run(["git", "-C", str(entries), *c], capture_output=True, text=True)
        # III F-3 (C-021): fail CLOSED. Any git error, no remote, or no upstream = "cannot tell" = refuse. Reads the
        # remote-tracking refs as of the last fetch (no network here); a commit on ANY of them has been published.
        up, pub = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"), git("log", "--remotes", "--oneline", "--", out.name)
        if up.returncode or pub.returncode or not git("remote").stdout.strip():
            print(f"✗ cannot tell whether {out.name} has been published (no git repo, remote or upstream: "
                  f"{(up.stderr or pub.stderr).strip()[:120]}) — refusing to regenerate (SO-2); publish a new version"); return 1
        if pub.stdout.strip():
            print(f"✗ {out.name} has reached a remote ({up.stdout.strip()} or another) — publish a new version instead (SO-2)"); return 1
        prev = git("log", "-1", "--format=%h", "--", out.name).stdout.strip()
        regen = {"replaces_commit": prev or None, "reason": a.regenerate, "at": now}
    dv = None
    if a.vs:
        ev = project(res, inst, version=a.version, recorded_at=now)
        old = json.loads(Path(a.vs).read_text())
        dv = delta(ev, old)
        dv["rolling_origin"] = delta_rolling(res["rolling_origin"], old)
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

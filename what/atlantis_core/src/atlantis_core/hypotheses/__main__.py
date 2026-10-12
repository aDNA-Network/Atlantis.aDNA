"""python -m atlantis_core.hypotheses corpus --ecosystem <type> [--refresh] [--max-per-query N] [--no-europepmc] [--root <dir>]
python -m atlantis_core.hypotheses --index [--check] [--root <dir>]

`corpus` runs `corpus/<ecosystem>/queries.yaml` against OpenAlex (Europe PMC for abstracts OpenAlex withholds) and writes
the committed `manifest.yaml` plus the gitignored `unreviewed/` abstracts; it refuses to replace a manifest without
`--refresh`. `--index` regenerates `LEDGER.md` after checking every row; `--index --check` writes nothing and exits 1 on
a stale ledger or any row failure. `--root` defaults to Atlantis's own `what/hypotheses/`.
"""
import argparse
import sys
from pathlib import Path

from atlantis_core.hypotheses import ROOT, LedgerError
from atlantis_core.hypotheses.corpus import fetch_corpus
from atlantis_core.hypotheses.index import write_or_check


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.hypotheses")
    ap.add_argument("command", nargs="?", choices=["corpus"])
    ap.add_argument("--ecosystem"); ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--max-per-query", type=int); ap.add_argument("--no-europepmc", action="store_true")
    ap.add_argument("--index", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if a.command == "corpus":
        if a.index or a.check:
            print("✗ corpus fetches; --index/--check render and check (run them separately)"); return 1
        if not a.ecosystem:
            ap.error("corpus needs --ecosystem")
        try:
            m = fetch_corpus(a.ecosystem, root, refresh=a.refresh, max_per_query=a.max_per_query, europepmc=not a.no_europepmc)
        except LedgerError as e:
            print(f"✗ {e}"); return 1
        c = m["counts"]
        print(f"→ corpus/{a.ecosystem}/manifest.yaml  ({c['works']} works · {c['with_abstract']} with abstract "
              f"{c['abstract_from']} · {c['agency']} agency · requests {m['requests']})")
        return 0
    if a.check and not a.index:
        print("✗ --check goes with --index"); return 1
    if not a.index:
        ap.error("give `corpus` or --index")
    return write_or_check(root, a.check)


if __name__ == "__main__":
    sys.exit(main())

"""python -m atlantis_core.discover --instance <dir> [--candidates f] [--probe] [--compare streams.yaml] [--out dir]

Reads the discovery sitting's `candidates.yaml`, writes the pointer rows and the memo, runs the six §B traps. Exit 0 when
the rows validate, the compare (if asked) is empty and no trap fails without a steward's ruling; 1 otherwise. The memo is
written either way: a failing discovery is still a record.

Without --probe it opens no socket. With it, only count-only requests (discover.probe), read in memory.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import yaml

from atlantis_core import __version__, load_instance
from atlantis_core.discover import probe as _probe
from atlantis_core.discover.rows import (DiscoveryError, check_request, check_searched, compare, load_candidates,
                                         pointer_rows, validate_rows)
from atlantis_core.discover.traps import DEFAULTS, run_all

MARK = {"pass": "✅", "warn": "⚠", "fail": "✗", "na": "—", "accepted": "☑"}


def apply_rulings(results: list[dict], rulings: dict) -> list[str]:
    """A fail a steward has ruled on becomes `accepted`, with the ruling beside it. A ruling must say what, who, when."""
    errs = []
    for r in results:
        ru = (rulings or {}).get(r["trap"])
        if not ru:
            continue
        missing = [k for k in ("ruling", "by", "date") if not str(ru.get(k) or "").strip()]
        if missing:
            errs.append(f"rulings.{r['trap']}: missing {missing}")
        elif r["status"] == "fail":
            r["status"], r["ruling"] = "accepted", ru
        else:
            r["ruling_unused"] = f"a ruling is recorded, but the trap is {r['status']} — it is not applied"
    return errs


def render_md(m: dict) -> str:
    L = [f"# Discovery memo — {m['instance']}", "",
         f"*`atlantis_core.discover` {m['discover']} · generated {m['generated_at']} · probed: {m['probed']}"
         + (f" ({', '.join(f'{h} ×{n}' for h, n in m['hosts'].items())})" if m["hosts"] else "") + "*", "",
         "Summary numbers only. Nothing here was fetched or cached; `streams.discovered.yaml` holds pointer rows "
         "(no sha256, no row count), and `streams.yaml` was not written.", "",
         "## Request", "", *[f"- **{k}:** {v}" for k, v in m["request"].items()], "",
         "## Searched (playbook §A)", "", "| Step | Where | Found | Note |", "|---|---|---|---|",
         *[f"| {s.get('step')} | {s.get('where', '')} | {', '.join(s.get('found') or []) or '—'} | {s.get('note', '')} |"
           for s in m["searched"]], "",
         "## Rows", "", "| stream_id | modality | source_system · source_id | fetcher | surveillance |", "|---|---|---|---|---|",
         *[f"| `{r['stream_id']}` | {r.get('modality')} | {r.get('source_system')} · `{r.get('source_id')}` | {r.get('fetcher')} | "
           f"{r.get('surveillance_channel')} |" for r in m["rows"]], ""]
    if m["validation_errors"]:
        L += ["**Validation errors:**", "", *[f"- {e}" for e in m["validation_errors"]], ""]
    if m["compare"] is not None:
        d = m["compare"]["diffs"]
        L += [f"**Compare** against `{m['compare']['against']}` (declarative fields): "
              + ("identical." if not d else f"{len(d)} difference(s)."), "", *[f"- {x}" for x in d], ""]
    L += ["## Traps (playbook §B)", "", "| Trap | Status | Note |", "|---|---|---|",
          *[f"| {r['trap']} | {MARK[r['status']]} {r['status']} | {r['note']} |" for r in m["traps"]], ""]
    for r in m["traps"]:
        L += [f"### {r['trap']} — {r['status']}", ""]
        if r.get("ruling"):
            L += [f"> Ruled ({r['ruling']['by']}, {r['ruling']['date']}): {r['ruling']['ruling']}", ""]
        if r["evidence"]:
            L += ["```yaml", yaml.safe_dump(r["evidence"], sort_keys=False, allow_unicode=True, width=120).rstrip(), "```", ""]
    return "\n".join(L) + "\n"


def main(argv=None, session=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.discover", description=__doc__.splitlines()[0])
    ap.add_argument("--instance", required=True)
    ap.add_argument("--candidates", help="default: <instance>/discovery/candidates.yaml")
    ap.add_argument("--out", help="default: <instance>/discovery")
    ap.add_argument("--probe", action="store_true", help="count-only requests to each stream's source")
    ap.add_argument("--compare", help="a streams.yaml whose declarative fields the discovered rows must reproduce")
    ap.add_argument("--at", help="generated_at (ISO); default now")
    a = ap.parse_args(argv)
    root = Path(a.instance).resolve()
    out = Path(a.out) if a.out else root / "discovery"
    inst = load_instance(root, check=False)   # R8 is a trap here, so a failing registry must still load
    try:
        doc = load_candidates(Path(a.candidates) if a.candidates else out / "candidates.yaml")
        rows = pointer_rows(doc)
    except (DiscoveryError, FileNotFoundError) as e:
        print(f"✗ {e}"); return 1
    errs = check_request(doc, inst) + check_searched(doc) + validate_rows(rows)
    diffs = compare(rows, Path(a.compare)) if a.compare else None
    probes, P = None, None
    if a.probe:
        P = _probe.Probe(session=session)
        probes = {sid: _probe.probe_stream(inst, sid, P) for sid in inst.streams}
    results = run_all(inst, doc.get("checks"), probes)
    errs += apply_rulings(results, doc.get("rulings"))
    memo = {"discover": f"atlantis_core {__version__}", "instance": root.name,
            "generated_at": a.at or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "request": doc["request"], "searched": doc["searched"], "rows": rows, "validation_errors": errs,
            "compare": None if diffs is None else {"against": Path(a.compare).name, "diffs": diffs},
            "probed": bool(a.probe), "hosts": dict(P.hosts) if P else {},
            "checks": {**DEFAULTS, **(doc.get("checks") or {})}, "traps": results}
    out.mkdir(parents=True, exist_ok=True)
    head = (f"# streams.discovered.yaml — POINTER rows from atlantis_core.discover ({__version__}), {memo['generated_at']}.\n"
            f"# No fetch provenance (sha256 · ingested_at · row_count): discovery fetches nothing (SO-3). A steward copies the\n"
            f"# accepted rows into streams.yaml; fork and fetch own that file. Memo: discovery_memo.md.\n")
    (out / "streams.discovered.yaml").write_text(head + yaml.safe_dump({"observation_streams": rows}, sort_keys=False,
                                                                       allow_unicode=True, width=120))
    (out / "discovery_memo.json").write_text(json.dumps(memo, indent=1, default=str, ensure_ascii=False) + "\n")
    (out / "discovery_memo.md").write_text(render_md(memo))
    for e in errs:
        print(f"✗ {e}")
    for d in diffs or []:
        print(f"✗ compare: {d}")
    for r in results:
        print(f"{MARK[r['status']]} {r['trap']:<22} {r['status']}")
    bad = errs or diffs or any(r["status"] == "fail" for r in results)
    print(f"{'✗' if bad else '✅'} {len(rows)} pointer row(s) → {out / 'streams.discovered.yaml'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

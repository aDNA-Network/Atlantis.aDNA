"""python -m atlantis_core.fetch --instance <dir> [--stream ID]… [--offline] [--verify]

The pipeline's `fetch` step (M-1d-i; closes WI-15 — `hab.fetch_*` stops being the exemplar's raw-parquet path). For each
declared stream it builds `FETCHERS[streams.yaml → fetcher]` from `atlantis.yaml → streams[id]` (`artifact`, `summary`,
`fetch` spec) and writes into the INSTANCE's cache — Atlantis itself never fetches (SO-3).

Two gates, both before any byte moves:
  - contract item 6: a green self-test receipt for the current config (`atlantis_core.selftest` writes it; a
    vitals/label/grid change invalidates it);
  - contract item 7 (M-1d-i dry-run finding — the skill said "ratify, then fetch" and nothing enforced it): a NETWORK fetch
    also needs the federation pin's posture ruling RATIFIED. `--offline` (cache hits only) moves no data and is exempt; the
    exemplar, which has no pin and may take no new snapshot (ADR-002 §4), can therefore only verify and read its cache.
`--verify` alone needs neither: it reads cached bytes and opens no socket, re-hashing each artifact against its fetch
summary and `streams.yaml → sha256`.

It never rewrites `streams.yaml` (comments are part of a registry). It prints the Rule-5 values to record — sha256 ·
row_count · ingested_at · pipeline_version — and says where they differ from what is recorded.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

from atlantis_core.config import load_instance
from atlantis_core.fetch import FETCHERS, OfflineError
from atlantis_core.fetch import provenance


def fetcher_for(inst, sid: str, offline: bool = False, session=None):
    s, spec = inst.streams[sid], inst.stream_spec(sid)
    name = s.get("fetcher")
    if name not in FETCHERS:
        raise SystemExit(f"✗ {sid}: fetcher {name!r} is not a known atlantis_core fetcher ({sorted(FETCHERS)})")
    art, summ = inst.path(spec["artifact"]), inst.path(spec["summary"])
    if art.parent != summ.parent:
        raise SystemExit(f"✗ {sid}: artifact and summary must share a directory ({spec['artifact']} · {spec['summary']})")
    return FETCHERS[name](art.parent, art.name, summ.name, offline=offline, session=session)


def verify(inst, sid: str) -> list[str]:
    """Problems with a stream's pin, or [] — the cached bytes, the summary and the registry must agree."""
    spec, s = inst.stream_spec(sid), inst.streams[sid]
    art, summ = inst.path(spec["artifact"]), inst.path(spec["summary"])
    if not art.exists():
        return [f"{sid}: no cached artifact at {spec['artifact']} (declared, not fetched)"]
    if not summ.exists():
        return [f"{sid}: artifact cached but no fetch summary at {spec['summary']}"]
    ok, actual, recorded = provenance.verify(art, summ)
    out = [] if ok else [f"{sid}: cached bytes {actual[:12]}… ≠ summary {recorded[:12]}… — the cache changed under its pin"]
    if s.get("sha256") and s["sha256"] != actual:
        out.append(f"{sid}: streams.yaml sha256 {s['sha256'][:12]}… ≠ cached bytes {actual[:12]}…")
    if not s.get("sha256"):
        out.append(f"{sid}: streams.yaml carries no sha256 — record {actual} (contract item 3, fetched stage)")
    return out


def posture_problem(root: Path) -> str | None:
    """None if the instance's OWN posture ruling (inside it, declaring the pin's class) carries a signed Ratification row
    and a frontmatter that agrees; else why not. One reading, shared with conform item 7 (M-1d-i III F-3)."""
    from atlantis_core.conform import posture
    return None if posture(root)["ratified"] else posture(root)["why_not_ratified"]


def record_values(inst, sid: str) -> dict:
    summ = json.loads(inst.path(inst.stream_spec(sid)["summary"]).read_text())
    return {"sha256": summ["sha256"], "row_count": summ["rows"], "ingested_at": summ["fetched_at"],
            **({"pipeline_version": summ["pipeline_version"]} if summ.get("pipeline_version") else {})}


def main(argv=None, session=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.fetch")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--stream", action="append", help="a stream_id (repeatable); default every declared stream")
    ap.add_argument("--offline", action="store_true", help="cache only; never touch the network")
    ap.add_argument("--verify", action="store_true", help="re-hash cached artifacts only (no fetch, no receipt needed)")
    a = ap.parse_args(argv)
    inst = load_instance(a.instance)
    sids = a.stream or sorted(inst.streams)
    unknown = [x for x in sids if x not in inst.streams]
    if unknown:
        print(f"✗ undeclared stream(s) {unknown}; declared: {sorted(inst.streams)}"); return 1
    if a.verify:
        probs = [p for sid in sids for p in verify(inst, sid)]
        for sid in sids:
            if not any(p.startswith(f"{sid}:") for p in probs):
                print(f"✅ {sid}: cached bytes == fetch summary == streams.yaml sha256")
        for p in probs:
            print(f"✗ {p}")
        return 1 if probs else 0
    from atlantis_core.selftest import receipt_problem
    why = receipt_problem(inst)
    if why:
        print(f"✗ refusing to fetch — {why} (contract item 6: self-test green before any real data)"); return 1
    if not a.offline:
        why = posture_problem(inst.root)
        if why:
            print(f"✗ refusing to fetch over the network — {why} (contract item 7; --offline reads the cache only)"); return 1
    rc = 0
    for sid in sids:
        f = fetcher_for(inst, sid, offline=a.offline, session=session)
        try:
            f.fetch(inst.stream_spec(sid).get("fetch") or {})
        except OfflineError as e:
            print(f"✗ {sid}: {e}"); rc = 1; continue
        except NotImplementedError as e:
            print(f"✗ {sid}: {e}"); rc = 1; continue
        vals, s = record_values(inst, sid), inst.streams[sid]
        diff = {k: v for k, v in vals.items() if k in ("sha256", "row_count") and s.get(k) != v}
        print(f"✅ {sid}: {f.artifact.relative_to(inst.root)} · {vals['row_count']} rows · sha256 {vals['sha256'][:12]}…")
        if diff or not s.get("ingested_at"):
            print(f"   record in streams.yaml → {json.dumps(vals)}")
    return rc


if __name__ == "__main__":
    sys.exit(main())

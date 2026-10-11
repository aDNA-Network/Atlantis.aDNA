"""candidates.yaml → AtlObservationStream pointer rows; the request a discovery answers; the compare against streams.yaml.

A discovery sitting (how/skills/skill_stream_discovery.md) writes `<instance>/discovery/candidates.yaml`:

    request:   {grid_sha256 | grid_kind, event_stream, event_variable, ecosystem}   # what was asked — checked against the instance
    searched:  [{step: A1…A6, where, query, found: [stream_id…] | [], note}]        # every §A step, the empty ones too
    candidates:[{stream_id, modality, source_system, source_id, authority, variable, unit, license, fetcher,
                 surveillance_channel, step, note}]                                 # one per stream found
    checks:    {lon_tolerance_deg, lon_max_out_frac, sparse_year_frac}              # optional; the trap thresholds
    rulings:   {<trap>: {ruling, by, date, accepts: [failure keys]}}                # optional; a steward's acceptance of named fails

A pointer row is the declarative half of a stream: where it lives, what it measures, under what licence. It carries no
`sha256`, `ingested_at`, `row_count`, `pipeline_version` or `captured_at` — those are what a FETCH proves, and discovery
fetches nothing (SO-3). A candidate carrying one is refused, not stripped.
"""
from __future__ import annotations

from pathlib import Path

from atlantis_core.config import load_yaml

DECL_FIELDS = ("stream_id", "modality", "source_system", "source_id", "authority", "variable", "unit", "license",
               "fetcher", "surveillance_channel")
FETCH_PROVENANCE = ("sha256", "ingested_at", "row_count", "pipeline_version", "captured_at")
CANDIDATE_ONLY = ("step", "note")
STEPS = ("A1", "A2", "A3", "A4", "A5", "A6")


class DiscoveryError(ValueError):
    pass


def load_candidates(path: Path) -> dict:
    doc = load_yaml(Path(path))
    for k in ("request", "searched", "candidates"):
        if k not in doc:
            raise DiscoveryError(f"{path}: no `{k}` block (see atlantis_core.discover.rows)")
    return doc


def instance_request(inst) -> dict:
    """What the instance says the discovery must answer: the patient (by its pinned geometry, or its rule grid) and the
    event variable. The ecosystem type is not in atlantis.yaml; the candidates file states it."""
    g, ev = inst.cfg["grid"], inst.event
    stream = inst.streams.get(ev["event_variable_stream"], {})
    req = {"grid_kind": g["kind"], "event_stream": ev["event_variable_stream"], "event_variable": stream.get("variable")}
    if g.get("sha256"):
        req["grid_sha256"] = g["sha256"]
    return req


def check_request(doc: dict, inst) -> list[str]:
    """The candidates must answer THIS instance's question: same geometry pin (or grid kind), same event stream."""
    want, got, errs = instance_request(inst), doc["request"] or {}, []
    for k, v in want.items():
        if got.get(k) != v:
            errs.append(f"request.{k}: candidates say {got.get(k)!r}, the instance says {v!r}")
    if not str(got.get("ecosystem") or "").strip():
        errs.append("request.ecosystem: blank — name the ecosystem type (it chooses which §A steps apply)")
    return errs


def check_searched(doc: dict) -> list[str]:
    """Every §A step is accounted for, found-nothing included: a step skipped in silence is a stream not looked for."""
    seen = {s.get("step") for s in doc.get("searched") or []}
    errs = [f"searched: step {s} not accounted for (record it with found: [] and why)" for s in STEPS if s not in seen]
    ids = {c.get("stream_id") for c in doc.get("candidates") or []}
    found = {sid for s in doc.get("searched") or [] for sid in s.get("found") or []}
    errs += [f"candidate {sid!r} is in no searched row's `found` — say which step found it" for sid in sorted(ids - found)]
    for s in doc.get("searched") or []:
        for sid in s.get("found") or []:
            if sid not in ids:
                errs.append(f"searched {s.get('step')}: found {sid!r}, which no candidate row carries")
    return errs


def pointer_rows(doc: dict) -> list[dict]:
    rows = []
    for c in doc.get("candidates") or []:
        bad = [k for k in FETCH_PROVENANCE if k in c]
        if bad:
            raise DiscoveryError(f"candidate {c.get('stream_id')!r} carries {bad}: a discovered row is a pointer; "
                                 f"fetch provenance is written after a fetch, never by discovery (SO-3)")
        if not c.get("step") in STEPS:
            raise DiscoveryError(f"candidate {c.get('stream_id')!r}: step {c.get('step')!r} — name the §A step (A1…A6) that found it")
        rows.append({k: c[k] for k in (*DECL_FIELDS, "name", "description") if k in c and c[k] is not None})
    return rows


def validate_rows(rows: list[dict]) -> list[str]:
    """atl_v0 (the committed JSON Schema conform uses) + the core's own rules a pointer row can break."""
    from atlantis_core.conform import _validator
    from atlantis_core.fetch import FETCHERS
    errs = [f"atl_v0 {'/'.join(map(str, e.absolute_path))}: {e.message[:140]}"
            for e in _validator().iter_errors({"observation_streams": rows})]
    seen = set()
    for r in rows:
        sid = r.get("stream_id")
        if sid in seen:
            errs.append(f"{sid}: duplicate stream_id")
        seen.add(sid)
        if r.get("fetcher") is not None and r["fetcher"] not in FETCHERS:
            errs.append(f"{sid}: fetcher {r['fetcher']!r} is not an atlantis_core fetcher ({sorted(FETCHERS)})")
        if "surveillance_channel" not in r:
            errs.append(f"{sid}: surveillance_channel not stated — say true or false (§B: surveillance is endogenous)")
    return errs


def compare(rows: list[dict], streams_yaml: Path) -> list[str]:
    """The declarative fields of each discovered row against the registry's: what a re-discovery must reproduce."""
    have = {s["stream_id"]: s for s in load_yaml(Path(streams_yaml)).get("observation_streams") or []}
    found = {r["stream_id"]: r for r in rows}
    diffs = [f"{sid}: in streams.yaml, not discovered" for sid in have if sid not in found]
    diffs += [f"{sid}: discovered, not in streams.yaml" for sid in found if sid not in have]
    for sid in sorted(set(have) & set(found)):
        for k in DECL_FIELDS:
            if have[sid].get(k) != found[sid].get(k):
                diffs.append(f"{sid}.{k}: streams.yaml {have[sid].get(k)!r} ≠ discovered {found[sid].get(k)!r}")
    return diffs

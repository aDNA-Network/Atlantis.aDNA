"""atlantis_core.runspec — the closed-vocabulary run-spec for the pipeline lattice (M-1d-ii; DDX `ddx_runner` precedent).

    python -m atlantis_core.runspec --instance <dir> --spec <runspec.json> [--plan]

A run-spec says WHICH stages of `how/lattices/lattice_atlantis_pipeline.lattice.yaml` to run, over WHICH declared streams,
in WHICH fetch mode. It **validates and plans; it executes nothing** (operator ruling 2026-10-03 — execution is P5's Ray
run-spec, with operator GO). `--plan` prints the ordered `atlantis_core` commands, gates named.

**No field can carry a path, a prompt or data.** The instance directory is the command line's, never the spec's. Every
string is an enum value, a stream id declared in the instance's `streams.yaml`, or an ISO date. **Reject, don't coerce**:
an unknown key at any level, a duplicate JSON key, `"1"` for 1, `1` for `true`, stages out of lattice order — each is
REJECTed (exit 3), never repaired. DDX rejects bad values but silently drops unknown keys; this one does not.

| key | rule |
|---|---|
| `stages` | required · non-empty list of the lattice's process nodes, in lattice order, no duplicates · `discover` is not enabled until M-3a · the run block (grid · vitals · label · train · eval · explain) is one command, so it is named whole or not at all |
| `fetch_mode` | `offline` \\| `verify` \\| `network` — required iff `fetch` is a stage (a network fetch is chosen, never defaulted), forbidden otherwise |
| `streams` | optional, iff `fetch` is a stage · non-empty list of `atl_stream_…` ids declared in the instance · default: every declared stream |
| `learner_swaps` | optional bool, iff the run block is staged · default `true` |
| `board` | `{version: int ≥ 1, run_date: "YYYY-MM-DD"}` — required iff `board` is a stage, forbidden otherwise |
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from atlantis_core import lattice

KEYS = {"stages", "fetch_mode", "streams", "learner_swaps", "board"}
BOARD_KEYS = {"version", "run_date"}
FETCH_MODES = ("offline", "verify", "network")
RUN_BLOCK = ("grid", "vitals", "label", "train", "eval", "explain")
NOT_ENABLED = {"discover": "stream discovery is declared-only until M-3a (streams are declared by hand at fork)"}
STREAM_ID = re.compile(r"^atl_stream_[a-z0-9_]+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class RunspecReject(ValueError):
    pass


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    d = [k for k in keys if keys.count(k) > 1]
    if d:
        raise RunspecReject(f"duplicate key {sorted(set(d))[0]!r} (JSON keeps the last silently — rejected, not coerced)")
    return dict(pairs)


def parse(text: str) -> dict:
    try:
        spec = json.loads(text, object_pairs_hook=_no_dupes, parse_constant=lambda c: (_ for _ in ()).throw(
            RunspecReject(f"non-finite number {c!r}")))
    except json.JSONDecodeError as e:
        raise RunspecReject(f"not JSON: {e}") from None
    return spec


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def validate(spec, streams_declared, stage_vocab=None) -> list[str]:
    """Every reason the spec is rejected (empty = valid). `streams_declared`: the instance's stream ids."""
    vocab = list(stage_vocab or lattice.stages())
    errs = []
    if not isinstance(spec, dict):
        return [f"<root>: a JSON object is required, got {type(spec).__name__}"]
    for k in sorted(set(spec) - KEYS):
        errs.append(f"{k}: unknown key (closed vocabulary: {', '.join(sorted(KEYS))})")
    st = spec.get("stages")
    staged: list = []
    if "stages" not in spec:
        errs.append("stages: required")
    elif not isinstance(st, list) or not st:
        errs.append("stages: a non-empty list is required")
    else:
        for s in st:
            if not isinstance(s, str) or s not in vocab:
                errs.append(f"stages: {s!r} is not a lattice stage ({' → '.join(vocab)})")
            elif s in NOT_ENABLED:
                errs.append(f"stages: {s!r} not enabled — {NOT_ENABLED[s]}")
        ok = [s for s in st if isinstance(s, str) and s in vocab]
        if len(set(ok)) != len(ok):
            errs.append(f"stages: duplicates {sorted({s for s in ok if ok.count(s) > 1})}")
        elif ok != sorted(ok, key=vocab.index):
            errs.append(f"stages: out of lattice order — {' → '.join(ok)} (the order is a gate; it is not re-sorted for you)")
        part = [s for s in RUN_BLOCK if s in ok]
        if part and len(part) != len(RUN_BLOCK):
            errs.append(f"stages: the run block {'·'.join(RUN_BLOCK)} is one command (`atlantis_core.run`); "
                        f"name all of it or none, not {'·'.join(part)}")
        staged = ok
    fetching, running = "fetch" in staged, "grid" in staged
    # fetch_mode
    if "fetch_mode" in spec:
        if spec["fetch_mode"] not in FETCH_MODES or not isinstance(spec["fetch_mode"], str):
            errs.append(f"fetch_mode: {spec['fetch_mode']!r} not in {FETCH_MODES}")
        if not fetching:
            errs.append("fetch_mode: only meaningful when 'fetch' is a stage")
    elif fetching:
        errs.append("fetch_mode: required when 'fetch' is a stage (a network fetch is chosen, never defaulted)")
    # streams
    if "streams" in spec:
        sv = spec["streams"]
        if not fetching:
            errs.append("streams: only selects what 'fetch' fetches; 'fetch' is not a stage")
        if not isinstance(sv, list) or not sv:
            errs.append("streams: a non-empty list of stream ids is required (omit it for every declared stream)")
        else:
            for s in sv:
                if not isinstance(s, str) or not STREAM_ID.match(s):
                    errs.append(f"streams: {s!r} is not a stream id (atl_stream_[a-z0-9_]+)")
                elif s not in streams_declared:
                    errs.append(f"streams: {s!r} is not declared in this instance's streams.yaml")
            ids = [s for s in sv if isinstance(s, str)]
            if len(set(ids)) != len(ids):
                errs.append("streams: duplicates")
    # learner_swaps
    if "learner_swaps" in spec:
        if not isinstance(spec["learner_swaps"], bool):
            errs.append(f"learner_swaps: a JSON boolean is required, got {spec['learner_swaps']!r}")
        if not running:
            errs.append("learner_swaps: only meaningful when the run block is staged")
    # board
    if "board" in spec:
        b = spec["board"]
        if "board" not in staged:
            errs.append("board: only meaningful when 'board' is a stage")
        if not isinstance(b, dict):
            errs.append("board: an object {version, run_date} is required")
        else:
            for k in sorted(set(b) - BOARD_KEYS):
                errs.append(f"board.{k}: unknown key (closed vocabulary: run_date, version)")
            for k in sorted(BOARD_KEYS - set(b)):
                errs.append(f"board.{k}: required")
            if "version" in b and not (_is_int(b["version"]) and b["version"] >= 1):
                errs.append(f"board.version: an integer ≥ 1 is required, got {b['version']!r}")
            if "run_date" in b:
                rd = b["run_date"]
                if not isinstance(rd, str) or not DATE.match(rd):
                    errs.append(f"board.run_date: YYYY-MM-DD is required, got {rd!r}")
                else:
                    try:
                        dt.date.fromisoformat(rd)
                    except ValueError:
                        errs.append(f"board.run_date: {rd!r} is not a calendar date")
    elif "board" in staged:
        errs.append("board: required when 'board' is a stage ({version, run_date})")
    return errs


def plan(spec: dict, instance: str, inside_atlantis: bool = False) -> list[str]:
    """The ordered commands for a VALID spec. Prints; runs nothing."""
    I = instance
    entries = "" if inside_atlantis else f" --entries {I}/what/board/entries"
    out = []
    for s in spec["stages"]:
        if s == "conform_declared":
            out.append(f"python -m atlantis_core.conform --instance {I} --stage declared")
        elif s == "selftest":
            out.append(f"python -m atlantis_core.selftest --instance {I}")
        elif s == "fetch":
            if "selftest" not in spec["stages"]:
                out.append("#   gate: needs an EXISTING green self-test receipt for the current config + self-test code")
            if spec["fetch_mode"] == "network":
                out.append("#   gate: a network fetch needs the instance's signed posture Ratification row (contract item 7)")
            flags = "".join(f" --stream {x}" for x in spec.get("streams", []))
            flags += {"offline": " --offline", "verify": " --verify", "network": ""}[spec["fetch_mode"]]
            out.append(f"python -m atlantis_core.fetch --instance {I}{flags}")
        elif s == "conform_fetched":
            out.append(f"python -m atlantis_core.conform --instance {I} --stage fetched")
        elif s == "grid":
            out.append(f"python -m atlantis_core.run --instance {I}" + ("" if spec.get("learner_swaps", True) else " --no-swaps")
                       + "   # grid · vitals · label · train · eval · explain")
        elif s in RUN_BLOCK:
            continue
        elif s == "board":
            b = spec["board"]
            out.append("#   gate: refuses unhonoured obligations and per-patient content")
            out.append(f"python -m atlantis_core.board --instance {I} --version {b['version']} --run-date {b['run_date']}{entries}")
            out.append(f"python -m atlantis_core.board --index{entries}")
        elif s == "site":
            out.append(f"python -m atlantis_core.site --instance {I}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.runspec")
    ap.add_argument("--instance", required=True); ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", action="store_true", help="print the ordered commands; nothing is executed")
    a = ap.parse_args(argv)
    from atlantis_core.config import load_instance
    inst = load_instance(a.instance, check=False)
    try:
        spec = parse(Path(a.spec).read_text())
        errs = validate(spec, set(inst.streams))
    except RunspecReject as e:
        errs = [str(e)]
    if errs:
        for e in errs:
            print(f"REJECT: {e}", file=sys.stderr)
        return 3
    print(f"✅ runspec valid — {' → '.join(spec['stages'])}")
    if a.plan:
        inside = lattice.ROOT in inst.root.resolve().parents
        print("# plan only — nothing below has been run (atlantis_core.runspec executes nothing)")
        for line in plan(spec, a.instance, inside_atlantis=inside):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

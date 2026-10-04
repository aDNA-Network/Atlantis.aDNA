"""atlantis_core.lattice — the pipeline lattice (`how/lattices/lattice_atlantis_pipeline.lattice.yaml`) as code.

    python -m atlantis_core.lattice [--lattice <file>]     # all three checks; exit 0 only if every one passes

Three checks, none sufficient alone (M-1d-ii):
1. **strict** — `what/lattices/lattice_yaml_schema.json` (draft 2020-12, `additionalProperties: false` everywhere but node
   `config`). Atlantis carries a byte-identical copy of `aDNA.aDNA`'s, so this runs in a public clone.
2. **peer** — `aDNA.aDNA/what/lattices/tools/lattice_validate.py`, imported by path (it has no CLI and its package
   `__init__` imports the canvas tools; the peer file is never edited). Its warnings count as failures. It never checks
   `additionalProperties` or cycles. Absent peer vault (a public clone) → reported as NOT RUN, never as a pass; the exit
   code then rests on 1 + 3, which between them re-check everything the peer alone would have caught (edge references,
   duplicate ids — III F-5; the rest is in the schema).
3. **local** — the invariants neither checks: edges reference real nodes · ids unique · acyclic · connected ·
   **dominance**, not mere reachability, for every gate pair — no path from a source reaches `fetch` without passing
   `selftest`, nor `selftest` without `conform_declared`, nor `board` without `explain` (III F-4, C-020) · every
   `config.module` imports · every `python -m X` names a module with an `if __name__ == "__main__"` guard (AST) · every
   `--flag` in a command is one X's argparse declares (AST) · an `invoked_by` module actually imports the node's module
   (transitively, AST).

`stages()` is the runspec's stage vocabulary: the lattice's process nodes in topological order (one source, never a copy)."""
from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
LATTICE = ROOT / "how" / "lattices" / "lattice_atlantis_pipeline.lattice.yaml"
SCHEMA = ROOT / "what" / "lattices" / "lattice_yaml_schema.json"
PEER_TOOLS = ROOT.parent / "aDNA.aDNA" / "what" / "lattices" / "tools"
RUN_CMD = "atlantis_core.run"
ORDER = (("conform_declared", "selftest"), ("selftest", "fetch"), ("fetch", "conform_fetched"), ("explain", "board"))
CMD = re.compile(r"python -m (atlantis_core(?:\.[a-z_]+)*)([^#\n]*)")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]*)")


class LatticeError(ValueError):
    pass


def load(path: Path = LATTICE) -> dict:
    return yaml.safe_load(Path(path).read_text())


def check_strict(doc: dict, schema_path: Path = SCHEMA) -> list[str]:
    v = Draft202012Validator(json.loads(Path(schema_path).read_text()))
    return [f"strict: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(v.iter_errors(doc), key=lambda e: list(map(str, e.absolute_path)))]


def peer_validator():
    """`validate_lattice` from the peer file, or None when the peer vault is absent (a public clone)."""
    f = PEER_TOOLS / "lattice_validate.py"
    if not f.exists():
        return None
    spec = importlib.util.spec_from_file_location("_peer_lattice_validate", f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod   # its @dataclass looks itself up in sys.modules
    spec.loader.exec_module(mod)
    return mod


def check_peer(path: Path) -> list[str] | None:
    """`validate_lattice_file(path)` — the peer's own entry point, on the file as written (it parses the YAML itself)."""
    mod = peer_validator()
    if mod is None:
        return None
    r = mod.validate_lattice_file(path)
    return [f"peer: {e}" for e in r.errors] + [f"peer (warning, counted as a failure): {w}" for w in r.warnings]


def _graph(doc: dict) -> tuple[list[str], dict[str, list[str]]]:
    nodes = [n["id"] for n in doc["lattice"]["nodes"]]
    succ = {n: [] for n in nodes}
    for e in doc["lattice"]["edges"]:
        if e["from"] in succ and e["to"] in succ:
            succ[e["from"]].append(e["to"])
    return nodes, succ


def topo(doc: dict) -> list[str]:
    """Kahn's algorithm, ties broken by file order (deterministic). Raises on a cycle."""
    nodes, succ = _graph(doc)
    indeg = {n: 0 for n in nodes}
    for a in nodes:
        for b in succ[a]:
            indeg[b] += 1
    out, ready = [], [n for n in nodes if indeg[n] == 0]
    while ready:
        n = ready.pop(0); out.append(n)
        for b in succ[n]:
            indeg[b] -= 1
            if indeg[b] == 0:
                ready.append(b)
        ready.sort(key=nodes.index)
    if len(out) != len(nodes):
        raise LatticeError(f"cycle through {sorted(set(nodes) - set(out))}")
    return out


def _spec(mod: str):
    """find_spec that answers None for a name that is not a module (e.g. `atlantis_core.config.load_instance`)."""
    try:
        return importlib.util.find_spec(mod)
    except (ImportError, AttributeError, ValueError):
        return None


def _main_file(mod: str) -> str | None:
    spec = _spec(mod)
    if spec is None:
        return None
    if spec.submodule_search_locations:
        m = _spec(mod + ".__main__")
        return m.origin if m else None
    return spec.origin


def _has_main(mod: str) -> bool:
    """An `if __name__ == "__main__":` guard, found in the AST (III F-4: a text match passed on a comment)."""
    f = _main_file(mod)
    if not f:
        return False
    if f.endswith("__main__.py"):
        return True
    for n in ast.walk(ast.parse(Path(f).read_text())):
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name) \
                and n.test.left.id == "__name__" and any(isinstance(c, ast.Constant) and c.value == "__main__"
                                                         for c in n.test.comparators):
            return True
    return False


def _flags(mod: str) -> set[str]:
    """Every option string `add_argument` declares in the module's entry file, or (a package) its __main__ and __init__ (AST)."""
    out = set()
    for f in sorted(x for x in {_main_file(mod), getattr(_spec(mod), "origin", None)} if x):
        for n in ast.walk(ast.parse(Path(f).read_text())):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "add_argument":
                out |= {a.value for a in n.args if isinstance(a, ast.Constant) and str(a.value).startswith("--")}
    return out | {"--help"}


def _dominates(nodes: list, succ: dict, gate: str, target: str) -> bool:
    """True iff every path from a source to `target` passes through `gate`."""
    indeg = {n: 0 for n in nodes}
    for a in nodes:
        for b in succ[a]:
            indeg[b] += 1
    todo, seen = [n for n in nodes if indeg[n] == 0 and n != gate], set()
    while todo:
        n = todo.pop()
        if n == target:
            return False
        if n not in seen and n != gate:
            seen.add(n); todo += succ[n]
    return True


def check_local(doc: dict) -> list[str]:
    errs = []
    ids = [n["id"] for n in doc["lattice"]["nodes"]]
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        errs.append(f"local: duplicate node id {d!r}")
    for e in doc["lattice"]["edges"]:
        for end in ("from", "to"):
            if e[end] not in ids:
                errs.append(f"local: edge {e['from']} → {e['to']}: {end} names no node")
    if errs:
        return errs
    try:
        order = topo(doc)
    except LatticeError as e:
        return [f"local: {e}"]
    nodes, succ = _graph(doc)
    undirected = {n: set(succ[n]) for n in nodes}
    for a in nodes:
        for b in succ[a]:
            undirected[b].add(a)
    seen, todo = set(), [nodes[0]]
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n); todo += undirected[n]
    if seen != set(nodes):
        errs.append(f"local: not connected — {sorted(set(nodes) - seen)} unreachable")
    for a, b in ORDER:
        if a not in order or b not in order:
            errs.append(f"local: required stage {a if a not in order else b!r} missing")
        elif not _dominates(nodes, succ, a, b):
            errs.append(f"local: {a} must dominate {b} — a path reaches {b} without passing {a} (the order is a gate)")
    for n in doc["lattice"]["nodes"]:
        cfg = n.get("config") or {}
        if cfg.get("module"):
            try:
                importlib.import_module(cfg["module"])
            except Exception as e:   # noqa: BLE001 — any import failure is the finding
                errs.append(f"local: {n['id']}: config.module {cfg['module']!r} does not import ({type(e).__name__})")
                continue
        for key in ("command", "invoked_by", "then"):
            for m, rest in CMD.findall(str(cfg.get(key, ""))):
                if not _has_main(m):
                    errs.append(f"local: {n['id']}: config.{key} names `python -m {m}`, which has no __main__ guard")
                    continue
                bad = sorted(set(FLAG.findall(rest)) - _flags(m))
                if bad:
                    errs.append(f"local: {n['id']}: config.{key} passes {bad} to {m}, whose argparse declares none of them")
                if key == "invoked_by" and m != RUN_CMD:
                    errs.append(f"local: {n['id']}: invoked_by {m} — only {RUN_CMD} runs library stages")
        if n["type"] == "process" and not (cfg.get("module") or cfg.get("status")):
            errs.append(f"local: {n['id']}: a process node names its module, or says why not (status)")
    from atlantis_core.runspec import RUN_BLOCK   # runspec imports this module; import here, not at the top
    invoked = {n["id"] for n in doc["lattice"]["nodes"] if (n.get("config") or {}).get("invoked_by")}
    if invoked != set(RUN_BLOCK):
        errs.append(f"local: the nodes `invoked_by` {RUN_CMD} {sorted(invoked)} are not the run-spec's run block "
                    f"{sorted(RUN_BLOCK)} — the plan would run a different set than the lattice draws")
    return errs


def _reaches(succ: dict, a: str, b: str) -> bool:
    seen, todo = set(), [a]
    while todo:
        n = todo.pop()
        if n == b:
            return True
        if n not in seen:
            seen.add(n); todo += succ[n]
    return False


def stages(path: Path = LATTICE) -> list[str]:
    """The process nodes in topological order — the runspec's stage vocabulary."""
    doc = load(path)
    kind = {n["id"]: n["type"] for n in doc["lattice"]["nodes"]}
    return [n for n in topo(doc) if kind[n] == "process"]


def node(stage: str, path: Path = LATTICE) -> dict:
    return next(n for n in load(path)["lattice"]["nodes"] if n["id"] == stage)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.lattice")
    ap.add_argument("--lattice", default=str(LATTICE))
    a = ap.parse_args(argv)
    doc = load(a.lattice)
    strict, peer, local = check_strict(doc), check_peer(Path(a.lattice)), check_local(doc)
    for e in strict + (peer or []) + local:
        print(f"✗ {e}")
    print(f"strict schema: {'✅' if not strict else '✗'} · peer lattice_validate: "
          f"{'not run (no aDNA.aDNA beside Atlantis)' if peer is None else '✅' if not peer else '✗'}"
          f" · local invariants: {'✅' if not local else '✗'}")
    if not (strict or peer or local):
        print("stages: " + " → ".join(stages(a.lattice)))
    if peer is None:
        print("note: the peer validator did NOT run; strict + local re-check everything only it would have caught")
    return 1 if (strict or peer or local) else 0


if __name__ == "__main__":
    sys.exit(main())

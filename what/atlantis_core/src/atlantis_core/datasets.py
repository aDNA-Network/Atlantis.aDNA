"""atlantis_core.datasets — dataset-record pairs held to the schema they claim (M-1d-ii; WI-18).

    python -m atlantis_core.datasets --check <dir>     # every dataset_*.dataset.yaml in <dir>, and its .md twin

A record is the lattice-labs pair `dataset_<x>.md` + `dataset_<x>.dataset.yaml` (`how/templates/template_dataset_pair/`).
Checks, per pair:
- the yaml validates against `dataset_yaml_schema.json` (draft 2020-12, format checker live) — Atlantis carries a
  byte-identical copy of `Archive.aDNA/lattice-labs/what/datasets/dataset_yaml_schema.json`;
- `name` is the file stem; `format.checksum` is `sha256:<64 hex>`;
- `storage.location.path` stays inside the repo; when the bytes are there, their sha256 IS the checksum. When they are
  absent: an ERROR if the record promises them (`storage_in_atlantis: grandfathered_exemplar_snapshot`), otherwise a
  printed "pin not verified" note — never a silent ✅ (III F-6, C-019);
- `class_fields` carries the Rule-5 provenance (source_system · source_url · ingested_at) and the stream id;
- the `.md` exists, points at this yaml, and repeats the same sha256 (a reader-facing copy that may not drift).
It reads; it never fetches and never writes."""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[4]
SCHEMA = ROOT / "how" / "templates" / "template_dataset_pair" / "dataset_yaml_schema.json"
PEER_SCHEMA = ROOT.parent / "Archive.aDNA" / "lattice-labs" / "what" / "datasets" / "dataset_yaml_schema.json"
CHECKSUM = re.compile(r"^sha256:([0-9a-f]{64})\Z")   # \Z: Python's $ accepts a trailing newline (III F-7, C-002)
RULE5 = ("source_system", "source_url", "ingested_at")


def _front(md: Path) -> dict:
    t = md.read_text()
    if not t.startswith("---\n"):
        return {}
    return yaml.safe_load(t.split("---\n", 2)[1]) or {}


def check_pair(y: Path, repo: Path, schema: dict, notes: list | None = None) -> list[str]:
    errs = []
    notes = [] if notes is None else notes
    doc = yaml.safe_load(y.read_text())
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    errs += [f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:160]}"
             for e in sorted(v.iter_errors(doc), key=lambda e: list(map(str, e.absolute_path)))]
    d = (doc or {}).get("dataset") or {}
    stem = y.name.removesuffix(".dataset.yaml")
    if d.get("name") != stem:
        errs.append(f"name {d.get('name')!r} is not the file stem {stem!r}")
    m = CHECKSUM.match(str((d.get("format") or {}).get("checksum", "")))
    if not m:
        errs.append("format.checksum: 'sha256:<64 hex>' required (the pin)")
    loc = ((d.get("storage") or {}).get("location") or {}).get("path")
    if m and loc:
        p = (repo / loc).resolve()
        if repo.resolve() not in p.parents:
            errs.append(f"storage.location.path {loc!r} escapes the repo")
        elif p.exists():
            if hashlib.sha256(p.read_bytes()).hexdigest() != m.group(1):
                errs.append(f"the bytes at {loc} do not hash to format.checksum")
        elif ((d.get("class_fields") or {}).get("storage_in_atlantis")) == "grandfathered_exemplar_snapshot":
            errs.append(f"the record promises its bytes are here (grandfathered_exemplar_snapshot), but {loc} is absent")
        else:
            notes.append(f"{y.name}: pin not verified — no bytes at {loc} (a pointer record, or a fresh clone)")
    elif m and not loc:
        errs.append("storage.location.path missing")
    cf = d.get("class_fields") or {}
    for k in RULE5 + ("atl_stream_id",):
        if not cf.get(k):
            errs.append(f"class_fields.{k} missing (Rule-5 provenance / the stream this record describes)")
    md = y.with_name(stem + ".md")
    if not md.exists():
        errs.append(f"{md.name} missing — a record is a pair")
    else:
        f = _front(md)
        if f.get("yaml") != y.name:
            errs.append(f"{md.name}: yaml: {f.get('yaml')!r} does not point at {y.name}")
        if m and f.get("sha256") != m.group(1):
            errs.append(f"{md.name}: sha256 {f.get('sha256')!r} ≠ the yaml's checksum")
        if f.get("stream_id") != cf.get("atl_stream_id"):
            errs.append(f"{md.name}: stream_id {f.get('stream_id')!r} ≠ class_fields.atl_stream_id")
    return errs


def check_dir(d: Path, repo: Path | None = None, schema_path: Path = SCHEMA, notes: list | None = None) -> dict[str, list[str]]:
    import json
    schema = json.loads(Path(schema_path).read_text())
    repo = repo or _repo_of(Path(d))
    ys = sorted(Path(d).glob("dataset_*.dataset.yaml"))
    out = {y.name: check_pair(y, repo, schema, notes) for y in ys}
    for md in sorted(Path(d).glob("dataset_*.md")):
        f = _front(md)
        if f.get("status") != "superseded" and not md.with_name(md.stem + ".dataset.yaml").exists():
            out[md.name] = ["a live record without its .dataset.yaml twin (superseded records say so: status: superseded)"]
    return out


def _repo_of(d: Path) -> Path:
    d = d.resolve()
    for p in (d, *d.parents):
        if (p / ".git").exists():
            return p
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.datasets")
    ap.add_argument("--check", required=True, metavar="DIR")
    a = ap.parse_args(argv)
    notes: list = []
    res = check_dir(Path(a.check), notes=notes)
    if not res:
        print(f"✗ no dataset_*.dataset.yaml in {a.check}"); return 1
    for name, errs in res.items():
        print(("✅ " if not errs else "✗ ") + name)
        for e in errs:
            print(f"     {e}")
    for n in notes:
        print(f"note: {n}")
    return 1 if any(res.values()) else 0


if __name__ == "__main__":
    sys.exit(main())

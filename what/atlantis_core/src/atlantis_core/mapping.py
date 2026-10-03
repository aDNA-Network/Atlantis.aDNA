"""atlantis_core.mapping — the machine check behind contract item 11 (an instance's `mapping.yaml`, from
`how/templates/template_mapping_atl.yaml`).

    python -m atlantis_core.mapping --check <mapping.yaml> [--schema <atl_ontology_v0.linkml.yaml>]

It reads the mapping and the atl_v0 LinkML schema only — never an instance's data. Refuses: a label per class missing or
doubled; a canonical_id that is not the class's identifier slot; a property or edge field that is not a slot of its class;
an edge whose target is not the slot's range; a fence weaker than the required minimum; a source that a deny_path
matches; a projected property named like a coordinate; a pointer slot projected from anything but itself; missing stamps."""
from __future__ import annotations

import argparse
import fnmatch
import posixpath
import sys
from pathlib import Path

import yaml

SCHEMA = Path(__file__).resolve().parents[3] / "schema" / "atl_v0" / "atl_ontology_v0.linkml.yaml"
CLASSES = ("AtlSpatialUnit", "AtlObservationStream", "AtlVital", "AtlEventDefinition", "AtlEvaluation")
NEVER = {"observation_long", "patient_grid", "vitals_table", "onset_label", "scored_table", "shap_values", "model_binary"}
# The required minimum IS the template's fence (III F-4: a minimum weaker than the template let its own lines be deleted).
DENY_PATHS = {"data/**", "**/*.parquet", "**/*.npz", "**/*.csv", "outputs/**", "site/**"}
DENY_PROPS = {"lat", "lon", "latitude", "longitude", "coordinates", "geometry", "geojson"}
STAMPS = {"ingested_at": "projection_write_time", "valid_from": "recorded_at", "valid_to": "on_supersession"}  # pinned values


def class_slots(schema: dict, cls: str) -> list:
    d = schema["classes"][cls]
    out = class_slots(schema, d["is_a"]) if d.get("is_a") else []
    for m in d.get("mixins", []) or []:
        out += class_slots(schema, m)
    return out + list(d.get("slots", []) or []) + list((d.get("attributes") or {}).keys())


def identifier(schema: dict, cls: str) -> str | None:
    ids = [s for s in class_slots(schema, cls) if (schema["slots"].get(s) or {}).get("identifier")]
    return ids[0] if len(ids) == 1 else None


def norm(path: str) -> str:
    """'./data/x', 'a/../data/x' → 'data/x' (III F-4: unnormalised paths walked past the globs)."""
    return posixpath.normpath(path.replace("\\", "/")).lstrip("/")


def _match(path: str, pat: str) -> bool:
    path = norm(path)
    return fnmatch.fnmatch(path, pat) or (pat.startswith("**/") and fnmatch.fnmatch(path, pat[3:])) \
        or path.startswith("../")


def check(m: dict, schema: dict) -> list[str]:
    errs = []
    labels = m.get("labels") or []
    by_label = {}
    for lab in labels:
        cls = lab.get("class")
        if cls not in CLASSES:
            errs.append(f"label {lab.get('label')!r}: class {cls!r} is not one of the five atl_ classes"); continue
        if cls in [l.get("class") for l in by_label.values()]:
            errs.append(f"class {cls} mapped twice")
        by_label[lab["label"]] = lab
        slots = class_slots(schema, cls)
        if lab.get("canonical_id") != identifier(schema, cls):
            errs.append(f"{cls}: canonical_id {lab.get('canonical_id')!r} is not its identifier slot {identifier(schema, cls)!r}")
        for prop, slot in (lab.get("properties") or {}).items():
            if slot not in slots:
                errs.append(f"{cls}.properties.{prop}: {slot!r} is not a slot of {cls}")
            if prop.lower() in DENY_PROPS | set((m.get("fence") or {}).get("deny_properties") or []):
                errs.append(f"{cls}.properties.{prop}: a coordinate-shaped property (fence.deny_properties)")
            if slot in ((m.get("fence") or {}).get("pointer_only") or []) and prop != slot:
                errs.append(f"{cls}.properties.{prop}: pointer slot {slot!r} must project under its own name")
        for j in lab.get("json_properties") or []:
            if j not in (lab.get("properties") or {}):
                errs.append(f"{cls}.json_properties: {j!r} is not a projected property")
        if lab.get("source_type") not in (m.get("sources") or {}):
            errs.append(f"{cls}: source_type {lab.get('source_type')!r} has no entry in sources")
    missing = [c for c in CLASSES if c not in [l.get("class") for l in labels]]
    errs += [f"no label maps {c}" for c in missing]
    for r in m.get("relationships") or []:
        d = r.get("derivation") or {}
        src, tgt = by_label.get(d.get("source_label")), by_label.get(d.get("target_label"))
        if not src or not tgt:
            errs.append(f"{r.get('rel_type')}: source/target label not mapped"); continue
        field = d.get("field")
        if field not in class_slots(schema, src["class"]):
            errs.append(f"{r.get('rel_type')}: {field!r} is not a slot of {src['class']}"); continue
        rng = (schema["slots"].get(field) or {}).get("range")
        if d.get("kind") == "registry_ref_list":
            if d.get("item_field") not in class_slots(schema, rng):
                errs.append(f"{r.get('rel_type')}: item_field {d.get('item_field')!r} is not a slot of {rng}"); continue
            for ep in d.get("edge_properties") or []:
                if ep not in class_slots(schema, rng):
                    errs.append(f"{r.get('rel_type')}: edge property {ep!r} is not a slot of {rng}")
                if ep.lower() in DENY_PROPS | set((m.get("fence") or {}).get("deny_properties") or []):
                    errs.append(f"{r.get('rel_type')}: edge property {ep!r} is coordinate-shaped (fence.deny_properties)")
            rng = (schema["slots"].get(d["item_field"]) or {}).get("range")
        elif d.get("edge_properties"):
            errs.append(f"{r.get('rel_type')}: edge_properties on a single-ref edge (no item to read them from)")
        if rng != tgt["class"]:
            errs.append(f"{r.get('rel_type')}: {field} ranges over {rng}, not {tgt['class']}")
    fence = m.get("fence") or {}
    errs += [f"fence.never_project: missing {s!r}" for s in sorted(NEVER - set(fence.get("never_project") or []))]
    errs += [f"fence.deny_paths: missing {p!r}" for p in sorted(DENY_PATHS - set(fence.get("deny_paths") or []))]
    errs += [f"fence.deny_properties: missing {p!r}" for p in sorted(DENY_PROPS - set(fence.get("deny_properties") or []))]
    for kind, paths in (m.get("sources") or {}).items():
        for p in paths:
            hit = [pat for pat in fence.get("deny_paths") or [] if _match(p, pat)]
            if hit:
                errs.append(f"sources.{kind}: {p!r} is fenced by {hit}")
    st = m.get("stamps") or {}
    errs += [f"stamps.{k}: {st.get(k)!r}, must be {v!r} (record time is not world time)" for k, v in STAMPS.items() if st.get(k) != v]
    if not str(st.get("source", "")).endswith("_project"):
        errs.append(f"stamps.source: {st.get('source')!r} must name the projection (`<instance>_project`)")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.mapping")
    ap.add_argument("--check", required=True, metavar="MAPPING")
    ap.add_argument("--schema", default=str(SCHEMA))
    a = ap.parse_args(argv)
    errs = check(yaml.safe_load(Path(a.check).read_text()), yaml.safe_load(Path(a.schema).read_text()))
    for e in errs:
        print(f"✗ {e}", file=sys.stderr)
    if not errs:
        print(f"✅ {a.check}: five atl_ labels, edges typed by the schema, fence and stamps complete")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

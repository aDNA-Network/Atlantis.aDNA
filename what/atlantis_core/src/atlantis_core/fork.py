"""atlantis_core.fork — a new instance from templates alone (M-1d-i; the P1 exit bar).

    python -m atlantis_core.fork --answers <answers.yaml> --out <instance dir> [--atlantis-commit <sha>] [--today YYYY-MM-DD]

Renders `how/templates/template_instance/` (+ `how/templates/template_mapping_atl.yaml`) from the steward's interview
answers (`template_instance/answers.example.yaml` is the shape; `how/skills/skill_atlantis_instance_fork.md` runs the
interview). Writes the instance's declarations — `atlantis.yaml` · `units.yaml` · `streams.yaml` · `features.yaml` ·
`events.yaml` · `mapping.yaml` · the posture ADR stub · the federation pin · a `.gitignore` block — and NO data. Then it
loads the result through `atlantis_core.registry` (R1–R8), so what it wrote is at least internally consistent.

Refuses (every reason listed, nothing written): an unresolved `{{token}}`; a target file that exists; an `atl_v0` enum
value it does not know; a lever without an owner; a coordinate `rules` grid under a partner / human_subject posture; a
polygon file absent from the instance; < 2 self-test patients; a stream that reaches no self-test patient; ids that would
break the `atl_` prefixes. It never touches the network and never fetches (contract item 6).
"""
from __future__ import annotations

import argparse, re, subprocess, sys
from datetime import date
from pathlib import Path

import yaml

ATLANTIS = Path(__file__).resolve().parents[4]
TEMPLATES = ATLANTIS / "how" / "templates" / "template_instance"
MAPPING_TEMPLATE = ATLANTIS / "how" / "templates" / "template_mapping_atl.yaml"
SCHEMA = ATLANTIS / "what" / "schema" / "atl_v0" / "atl_ontology_v0.linkml.yaml"
TOKEN = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
SLUG = re.compile(r"^[a-z][a-z0-9_]{1,62}$")
POSTURES = ("public", "partner", "human_subject")
SHAPE_COLUMNS = {"point": ("date", "value", "lat", "lon"), "unit_daily": ("date", "value", "unit"),
                 "station_daily": ("date", "value", "station")}


class ForkError(ValueError):
    pass


def _enum(schema: dict, name: str) -> set:
    return set((schema["enums"][name].get("permissible_values") or {}).keys())


class _Dumper(yaml.SafeDumper):
    """Block style for mappings (a registry row a steward reads), flow style for lists of scalars ([1, 2])."""


_Dumper.add_representer(list, lambda d, xs: d.represent_sequence(
    "tag:yaml.org,2002:seq", xs, flow_style=all(not isinstance(x, (dict, list)) for x in xs)))


def _dump(obj, indent: int) -> str:
    txt = yaml.dump(obj, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=120, default_flow_style=False).rstrip("\n")
    return "\n".join((" " * indent + ln) if ln else ln for ln in txt.splitlines())


def render(text: str, values: dict, where: str) -> str:
    """Scalar tokens inline; a token alone on its line takes a block (list/dict dumped at the token's indent)."""
    missing = sorted({m for m in TOKEN.findall(text) if m not in values})
    if missing:
        raise ForkError(f"{where}: unresolved token(s) {missing}")
    out = []
    for line in text.splitlines():
        m = re.fullmatch(r"(\s*)\{\{\s*([a-z_]+)\s*\}\}\s*", line)
        if m and not isinstance(values[m.group(2)], str):
            out.append(_dump(values[m.group(2)], len(m.group(1))))
        else:
            out.append(TOKEN.sub(lambda mm: str(values[mm.group(1)]), line))
    return "\n".join(out) + "\n"


# -- answers → registries ---------------------------------------------------------------------------------------------
def _short(sid: str) -> str:
    return sid[len("atl_stream_"):] if sid.startswith("atl_stream_") else sid


def starter_vitals(a: dict) -> list[dict]:
    ev = a["event"]
    clim = a.get("climatology") or {}
    out = []
    for s in a["streams"]:
        sid, v = s["stream_id"], s.get("vitals") or {}
        is_event = sid == ev["stream"]
        agg = v.get("aggregate") or (("weekly_max" if ev["direction"] == "above" else "weekly_min") if is_event else "weekly_mean")
        group, tag = v.get("group") or _short(sid), v.get("tag") or ("state" if is_event else "proxy")
        owner = v.get("owner")
        for lag in v.get("lags", [0, 1]):
            row = {"vital_id": f"atl_vital_{_short(sid)}_{agg.removeprefix('weekly_')}_t{lag}",
                   "name": f"{agg.replace('_', ' ')} of {s.get('variable') or _short(sid)}, {'this week' if lag == 0 else f'{lag} wk ago'}",
                   "description": f"starter vital (atlantis_core.fork): {agg}(value) of {sid}, lag {lag} ISO week(s)",
                   "stream_ref": sid, "transform": f"{agg}(value)", "lag": int(lag), "group": group, "tag": tag}
            if owner:
                row["owner"] = owner
            out.append(row)
        if sid in clim:
            row = {"vital_id": f"atl_vital_{_short(sid)}_anom_t0",
                   "name": f"{s.get('variable') or _short(sid)} anomaly, this week",
                   "description": f"starter vital: weekly mean of {sid} minus its {clim[sid][0]}–{clim[sid][1]} climatology",
                   "stream_ref": sid, "transform": "weekly_mean(anomaly(value))", "lag": 0, "group": group, "tag": tag}
            if owner:
                row["owner"] = owner
            out.append(row)
        if s.get("surveillance_channel"):
            out.append({"vital_id": f"atl_vital_{_short(sid)}_samples_4w", "name": "samples, last 4 wk",
                        "description": f"surveillance intensity: observations of {sid} over four weeks (how hard we looked)",
                        "stream_ref": sid, "transform": "rolling_sum(weekly_count(value))", "window": 4,
                        "group": "surveillance", "tag": "artifact"})
    return out + list(a.get("vitals") or [])


def _values(a: dict, schema: dict, out: Path, commit: str, today: str, answers_file: str, adr_number: str) -> tuple[dict, list]:
    errs = []
    inst, pat, ev, post = a.get("instance") or {}, a.get("patient") or {}, a.get("event") or {}, a.get("posture") or {}
    slug = str(inst.get("slug", ""))
    if not SLUG.match(slug):
        errs.append(f"instance.slug {slug!r}: snake_case, 2–63 chars (it prefixes every atl_ id)")
    if post.get("class") not in POSTURES:
        errs.append(f"posture.class {post.get('class')!r} not in {POSTURES}")
    if pat.get("unit_kind") not in _enum(schema, "UnitKind"):
        errs.append(f"patient.unit_kind {pat.get('unit_kind')!r} not in atl_v0 UnitKind {sorted(_enum(schema, 'UnitKind'))}")
    if pat.get("time_step") != "iso_week":
        errs.append(f"patient.time_step {pat.get('time_step')!r}: atlantis_core builds ISO weeks only (atl_v0 lists more; v1)")
    if ev.get("direction") not in _enum(schema, "Direction"):
        errs.append(f"event.direction {ev.get('direction')!r} not in {sorted(_enum(schema, 'Direction'))}")
    for k in ("name", "stream", "threshold", "unit", "horizon", "onset_rule"):
        if ev.get(k) in (None, ""):
            errs.append(f"event.{k} missing")
    grid, units = dict(pat.get("grid") or {}), list(pat.get("units") or [])
    kind = grid.get("kind")
    if kind not in ("polygons", "rules", "cells"):
        errs.append(f"patient.grid.kind {kind!r} not in polygons | rules | cells")
    if kind == "rules" and post.get("class") != "public":
        errs.append("patient.grid.kind rules writes coordinates into atlantis.yaml — allowed under public posture only (contract item 1)")
    if kind == "polygons" and not (out / str(grid.get("path", ""))).is_file():
        errs.append(f"patient.grid.path {grid.get('path')!r} not found inside the instance ({out}) — the pointer must resolve there")
    if not units:
        errs.append("patient.units: at least one unit")
    codes = [u.get("code") for u in units]
    if len(set(map(str, codes))) != len(codes):
        errs.append(f"patient.units: duplicate codes {codes}")
    streams = list(a.get("streams") or [])
    sids = [s.get("stream_id") for s in streams]
    mods = _enum(schema, "Modality")
    for s in streams:
        sid = str(s.get("stream_id"))
        if not re.match(r"^atl_stream_[a-z0-9_]{2,64}$", sid):
            errs.append(f"stream {sid!r}: id must be atl_stream_<snake>")
        if s.get("modality") not in mods:
            errs.append(f"{sid}: modality {s.get('modality')!r} not in atl_v0 Modality")
        for k in ("source_system", "source_id", "license", "fetcher", "shape"):
            if not s.get(k):
                errs.append(f"{sid}: {k} missing (contract item 3, declared stage)")
        if s.get("shape") not in SHAPE_COLUMNS:
            errs.append(f"{sid}: shape {s.get('shape')!r} not in {sorted(SHAPE_COLUMNS)}")
        if s.get("shape") == "station_daily" and not s.get("stations"):
            errs.append(f"{sid}: station_daily needs stations → [unit codes]")
        v = s.get("vitals") or {}
        if v.get("tag") == "lever" and not (isinstance(v.get("owner"), str) and v["owner"].strip()):
            errs.append(f"{sid}: vitals.tag lever without an owner — who can move it? (R4)")
        if v.get("tag") and v["tag"] not in _enum(schema, "VitalTag"):
            errs.append(f"{sid}: vitals.tag {v['tag']!r} not in atl_v0 VitalTag")
    if ev.get("stream") not in sids:
        errs.append(f"event.stream {ev.get('stream')!r} is not a declared stream {sids}")
    st = a.get("selftest") or {}
    ps = list(st.get("patients") or [])
    if len(ps) < 2:
        errs.append("selftest.patients: ≥ 2 (a primary and a neighbour) — the cross-unit check needs a neighbour")
    pu = {p.get("unit") for p in ps}
    for s in streams:
        reach = (set(u for us in (s.get("stations") or {}).values() for u in us) if s.get("shape") == "station_daily"
                 else pu)
        if not (reach & pu):
            errs.append(f"{s.get('stream_id')}: reaches no self-test patient {sorted(pu)} — every stream must be perturbed (SO-7)")
        if s.get("shape") == "point" and not all("lat" in p and "lon" in p for p in ps):
            errs.append(f"{s.get('stream_id')}: a point stream needs lat/lon on every self-test patient")
    sp = a.get("split") or {}
    need = ("min_train_year", "train_end", "val_start", "val_end", "test_start", "test_end")
    if any(k not in sp for k in need):
        errs.append(f"split: needs {need}")
    if errs:
        return {}, errs

    region = pat.get("region") or {}
    region_code = str(region.get("code", "all"))
    region_id = f"atl_unit_{slug}_{region_code}"
    gpath = grid.get("path")
    def geo(code):
        if kind == "polygons":
            return f"{gpath}#{grid['id_property']}={code}"
        if kind == "rules":
            return f"atlantis.yaml -> grid.rules[id={code}]"
        return f"atlantis.yaml -> grid.cells[{code}]"
    region_geo = (str(region["geometry_ref"]) if region.get("geometry_ref") else
                  (f"{gpath} (all features)" if kind == "polygons" else "atlantis.yaml -> grid"))
    urows = [{k: v for k, v in {"unit_id": region_id, "name": region.get("name", inst.get("name")), "unit_kind": pat["unit_kind"],
                                "external_id": region.get("external_id"), "geometry_ref": region_geo,
                                "time_step": pat["time_step"]}.items() if v is not None}]
    for u in units:
        urows.append({k: v for k, v in {"unit_id": f"atl_unit_{slug}_{u['code']}", "name": u.get("name"),
                                        "unit_kind": pat["unit_kind"], "external_id": u.get("external_id"),
                                        "geometry_ref": u.get("geometry_ref") or geo(u["code"]),
                                        "time_step": pat["time_step"], "parent_unit": region_id}.items() if v is not None})
    gblock = {"kind": kind}
    if kind == "polygons":
        gblock.update({"path": gpath, "id_property": grid["id_property"]})
        if grid.get("name_property"):
            gblock["name_property"] = grid["name_property"]
    elif kind == "rules":
        gblock["rules"] = grid["rules"]
    else:
        gblock.update({"res": grid["res"], "bbox": grid["bbox"]})
    gblock["unit_column"] = grid.get("unit_column", "unit")
    if grid.get("unit_dtype"):
        gblock["unit_dtype"] = grid["unit_dtype"]
    gblock["units"] = codes                       # explicit: the grid is units.yaml's, not whichever stream saw what
    gblock["weeks_from"] = ev["stream"]

    srows, sblock = [], {}
    for s in streams:
        sid = s["stream_id"]
        srows.append({k: s[k] for k in ("stream_id", "fetcher", "modality", "source_system", "source_id", "authority",
                                        "variable", "unit", "license", "surveillance_channel") if s.get(k) is not None})
        cols = dict(zip(SHAPE_COLUMNS[s["shape"]], SHAPE_COLUMNS[s["shape"]]))
        cols.update(s.get("columns") or {})
        spec = {"shape": s["shape"], "artifact": s.get("artifact", f"data/raw/{_short(sid)}.parquet"),
                "summary": s.get("summary", f"data/raw/{_short(sid)}_fetch_summary.json"), "columns": cols}
        if s.get("stations"):
            spec["stations"] = {str(k): list(v) for k, v in s["stations"].items()}
        if s.get("lever_stations"):
            spec["lever_stations"] = list(s["lever_stations"])
        if s.get("fetch"):
            spec["fetch"] = s["fetch"]
        sblock[sid] = spec

    surv = a.get("surveillance") or {}
    s_streams = [s for s in streams if s.get("surveillance_channel")]
    vitals = starter_vitals(a)
    if s_streams:
        sv = next(v["vital_id"] for v in vitals if v.get("group") == "surveillance")
        surv_block = {"declared": "present"}
        eval_block = {"ablations": [{"drop_group": "surveillance"}], "surveillance_only": sv.removeprefix("atl_vital_")}
    else:
        surv_block = {"declared": "absent", "reason": surv.get("reason", "")}
        eval_block = {"ablations": []}
    clim = a.get("climatology") or {}
    st_block = {"patients": ps,
                "week": str(st.get("week") or _first_monday(int(sp["val_start"])))}
    if clim:
        lo = max(int(e[0]) for e in clim.values()); hi = min(int(e[1]) for e in clim.values())
        st_block["in_era_week"] = str(st.get("in_era_week") or _first_monday((lo + hi) // 2, month=6))
    erow = {"event_id": f"atl_event_{slug}_onset", "name": ev["name"], "event_variable_stream": ev["stream"],
            "threshold": ev["threshold"], "unit": ev["unit"], "direction": ev["direction"], "horizon": int(ev["horizon"]),
            "onset_rule": ev["onset_rule"]}
    ev_stream = next(s for s in streams if s["stream_id"] == ev["stream"])
    posture_ignores = "" if post["class"] == "public" else (
        "# non-public posture: nothing under these leaves this node\ndata/\noutputs/\nsite/\n")
    vals = {
        "instance_name": inst.get("name", slug), "instance_slug": slug, "vault": inst.get("vault", f"{slug}.aDNA"),
        "fork_date": today, "answers_file": answers_file, "atlantis_commit": commit,
        "grid_block": gblock, "streams_block": sblock, "climatology_block": clim, "split_block": sp,
        "surveillance_block": surv_block, "selftest_block": st_block, "eval_block": eval_block,
        "event_id": erow["event_id"], "event_direction": ev["direction"],
        "label_signal": "weekly_max(value)" if ev["direction"] == "above" else "weekly_min(value)",
        "last_known_weeks": int(ev.get("last_known_weeks", 4)),
        "region_unit_id": region_id, "region_geometry_ref": region_geo, "region_external_id": region.get("external_id", ""),
        "unit_kind": pat["unit_kind"], "time_step": pat["time_step"],
        "units_rows": urows, "streams_rows": srows, "vitals_rows": vitals, "event_rows": [erow],
        "warning": str((a.get("interview") or {}).get("warning", "(not recorded)")).replace("\n", " "),
        "event_variable": ev_stream.get("variable", ""), "event_threshold": ev["threshold"], "event_unit": ev["unit"],
        "event_horizon": int(ev["horizon"]),
        "stream_list": ", ".join(sids), "posture_class": post["class"],
        "posture_rationale": post.get("rationale", "(to be written by the steward)"),
        "posture_answer": str((a.get("interview") or {}).get("posture", "(not recorded)")).replace("\n", " "),
        "adr_number": adr_number, "posture_adr_path": f"who/governance/adr_{adr_number}_data_posture.md",
        "posture_ignores": posture_ignores,
    }
    return vals, []


def _first_monday(year: int, month: int = 1) -> str:
    d = date(year, month, 1)
    return str(date.fromordinal(d.toordinal() + (7 - d.weekday()) % 7))


def _next_adr(out: Path) -> str:
    gov = out / "who" / "governance"
    used = {int(m.group(1)) for p in gov.glob("adr_*.md") if (m := re.match(r"adr_(\d{3})_", p.name))} if gov.is_dir() else set()
    return f"{max(used | {0}) + 1:03d}"


def plan(a: dict, out: Path, commit: str, today: str, answers_file: str) -> dict[Path, str]:
    """Every file fork would write → its text. Raises ForkError listing every refusal."""
    schema = yaml.safe_load(SCHEMA.read_text())
    adr = _next_adr(out)
    vals, errs = _values(a, schema, out, commit, today, answers_file, adr)
    if errs:
        raise ForkError("fork refused:\n  " + "\n  ".join(errs))
    files = {}
    for tmpl, dest in (("atlantis.yaml.tmpl", "atlantis.yaml"), ("units.yaml.tmpl", "units.yaml"),
                       ("streams.yaml.tmpl", "streams.yaml"), ("features.yaml.tmpl", "features.yaml"),
                       ("events.yaml.tmpl", "events.yaml"),
                       ("adr_data_posture.md.tmpl", vals["posture_adr_path"]),
                       ("federation_atlantis_CLAUDE.md.tmpl", "how/federation/atlantis/CLAUDE.md")):
        files[out / dest] = render((TEMPLATES / tmpl).read_text(), vals, tmpl)
    files[out / "mapping.yaml"] = render(MAPPING_TEMPLATE.read_text(), vals, "template_mapping_atl.yaml")
    for p, txt in files.items():
        if p.suffix == ".yaml":
            try:
                yaml.safe_load(txt)
            except yaml.YAMLError as e:
                raise ForkError(f"{p.name}: rendered YAML does not parse — template defect: {e}")
    clash = [str(p.relative_to(out)) for p in files if p.exists()]
    if clash:
        raise ForkError(f"fork refused: would overwrite {clash} (an instance is forked once; edit it, or fork elsewhere)")
    files[out / ".gitignore"] = render((TEMPLATES / "gitignore.tmpl").read_text(), vals, "gitignore.tmpl")
    return files


def _atlantis_commit() -> str:
    r = subprocess.run(["git", "-C", str(ATLANTIS), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "<unknown — not a git checkout>"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.fork")
    ap.add_argument("--answers", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--atlantis-commit"); ap.add_argument("--today", default=str(date.today()))
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    answers = yaml.safe_load(Path(a.answers).read_text())
    try:
        files = plan(answers, out, a.atlantis_commit or _atlantis_commit(), a.today, Path(a.answers).name)
    except ForkError as e:
        print(f"✗ {e}", file=sys.stderr); return 1
    for p, txt in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.name == ".gitignore" and p.exists():
            p.write_text(p.read_text().rstrip("\n") + "\n\n" + txt)
        else:
            p.write_text(txt)
        print(f"  + {p.relative_to(out)}")
    from atlantis_core.config import load_instance
    from atlantis_core.registry import RegistryError
    try:
        inst = load_instance(out)
    except RegistryError as e:
        print(f"✗ forked, but the registry check fails — a template or answers defect:\n{e}", file=sys.stderr); return 1
    print(f"✅ forked {answers['instance']['slug']}: {len(inst.streams)} streams (declared, not fetched) · {len(inst.vitals)} "
          f"starter vitals · event {inst.cfg['label']['event']} · registry R1–R8 clean\n"
          f"   next: mapping --check · conform --stage declared · selftest (the receipt) · ratify the posture ADR · fetch")
    return 0


if __name__ == "__main__":
    sys.exit(main())

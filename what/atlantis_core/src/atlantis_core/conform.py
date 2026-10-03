"""atlantis_core.conform — the instance contract (v0.2.0 §B) as a machine check, one ✅/✗ per item (M-1d-i).

    python -m atlantis_core.conform --instance <dir> [--items 1-8,11,12] [--stage declared|fetched] [--no-selftest]

A reviewer conforms an instance from its DECLARATIONS: `atlantis.yaml` · `units.yaml` · `streams.yaml` · `features.yaml` ·
`events.yaml` · `mapping.yaml` · the posture ADR · the federation pin. What else it opens, and why:
  - item 1: the polygon file `grid.path` names, to prove each grid unit is a feature in it (a pointer that resolves);
  - item 3 (`--stage fetched`): each cached artifact, to HASH it against its fetch summary and `streams.yaml` (never parsed);
  - item 6: nothing — it RE-RUNS the self-test (synthetic, no data) instead of trusting the receipt; `--no-selftest`
    falls back to the receipt;
  - items 9–10: board entries under `what/board/entries/` and pages under `site/`, only once they exist (else n/a);
  - item 12: `gitleaks detect --no-git` over the instance directory (absent gitleaks → "not run", which FAILS the item).
It writes nothing.

Stages (item 3, and item 7's ruling): **declared** is the state before the first fetch, the one the self-test runs in. A
stream carries source_system · source_id · license · a known fetcher, and the posture ADR may still be proposed.
**fetched**: every stream is pinned (sha256 · ingested_at · pipeline_version, equal to the cache), and the posture ADR is
ratified.

Exit 0 only if every requested item passes or is n/a. The minimum each item checks IS the contract row (C-013).
"""
from __future__ import annotations

import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

import yaml

from atlantis_core.config import load_instance, load_yaml
from atlantis_core.fork import POSTURES

ATLANTIS = Path(__file__).resolve().parents[4]
JSON_SCHEMA = ATLANTIS / "what" / "schema" / "atl_v0" / "atl_ontology_v0.schema.json"
ITEMS = {
    1: "Patient defined (units · grid · geometry by pointer)",
    2: "Event defined (authority · threshold + unit · direction · horizon · onset rule)",
    3: "Streams registered with Rule-5 provenance",
    4: "Every vital tagged, with stream_ref and lag/window; levers name an owner",
    5: "Surveillance channel declared, or declared absent with the reason",
    6: "Self-test green (before any real data is fetched)",
    7: "Data posture ruled in the instance's own ADR",
    8: "Split is temporal",
    9: "Board entry carries base rate, budgets, lead time, ablations, hash, pins, claim",
    10: "Published page has a Limitations section",
    11: "mapping.yaml present and held to atl_v0",
    12: "Credentials by name only (gitleaks)",
}
RULE_ITEM = {"R1": 3, "R2": 4, "R3": 4, "R4": 4, "R5": 3, "R6": 2, "R7": 8, "R8": 5}
REGISTRY_FILES = {"units.yaml": (1, "spatial_units"), "streams.yaml": (3, "observation_streams"),
                  "features.yaml": (4, "vitals"), "events.yaml": (2, "event_definitions")}


def parse_items(s: str) -> list[int]:
    out = []
    for part in s.split(","):
        a, _, b = part.strip().partition("-")
        out += list(range(int(a), int(b or a) + 1))
    bad = [i for i in out if i not in ITEMS]
    if bad:
        raise SystemExit(f"unknown contract item(s) {bad}; items are 1–12")
    return sorted(set(out))


def _validator():
    from jsonschema import validators
    S = json.loads(JSON_SCHEMA.read_text())
    VC = validators.validator_for(S)
    return VC(S, format_checker=VC.FORMAT_CHECKER)


def _fed_ref(root: Path) -> dict | None:
    f = root / "how" / "federation" / "atlantis" / "CLAUDE.md"
    if not f.exists():
        return None
    m = re.search(r"```yaml\n(.*?)```", f.read_text(), re.S)
    try:
        return (yaml.safe_load(m.group(1)) or {}).get("federation_ref") if m else None
    except yaml.YAMLError:
        return None


def _front(path: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---", path.read_text(), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def inside(root: Path, rel) -> Path | None:
    """The path `rel` names, if it is RELATIVE and resolves inside `root` (M-1d-i III F-3a/F-4: an absolute or ../ path
    satisfied 'resolves inside the instance' when the check was only (root / p).is_file())."""
    if not rel or Path(str(rel)).is_absolute():
        return None
    r = (root / str(rel)).resolve()
    return r if r.is_relative_to(root.resolve()) else None


AUTHORITIES = ("CF", "WoRMS", "dwc")   # contract item 2: the variable's vocabulary — CF standard name · WoRMS AphiaID · Darwin Core
RATIFIED = ("ratified", "accepted")


def posture(root: Path) -> dict:
    """The instance's data posture as declared and as ruled — ONE reading for conform item 7 and the fetch gate.
    {class, ruling, problems: [declared-stage failures], ratified: bool, why_not_ratified: str|None}.
    Ratified means the ADR's 4-field Ratification row is signed — decision, ratified-by, an ISO date, status ratified —
    AND the frontmatter agrees (III F-3b: a one-word frontmatter flip, table blank, had opened the gate)."""
    out = {"class": None, "ruling": None, "problems": [], "ratified": False, "why_not_ratified": None}
    fr = _fed_ref(root)
    if fr is None:
        out["problems"].append("how/federation/atlantis/CLAUDE.md has no federation_ref block — no data posture is declared")
        out["why_not_ratified"] = out["problems"][0]; return out
    dp = ((fr.get("instance") or {}).get("data_posture") or {})
    out["class"], out["ruling"] = dp.get("class"), dp.get("ruling")
    if dp.get("class") not in POSTURES:
        out["problems"].append(f"data_posture.class {dp.get('class')!r} not in {POSTURES}")
    f = inside(root, dp.get("ruling"))
    if f is None:
        out["problems"].append(f"data_posture.ruling {dp.get('ruling')!r} is not a relative path inside the instance — "
                               f"the instance's OWN ruling, not another's")
    elif not f.is_file():
        out["problems"].append(f"data_posture.ruling {dp.get('ruling')!r} does not exist")
    else:
        txt = f.read_text()
        m = re.search(r"\*\*Class:\*\*\s*`([a-z_]+)`", txt)   # the DECLARED class, not any mention
        if not m:
            out["problems"].append(f"{dp['ruling']} declares no **Class:** line (the class it is cited for)")
        elif m.group(1) != dp.get("class"):
            out["problems"].append(f"{dp['ruling']} declares class {m.group(1)!r}, the federation pin says {dp.get('class')!r} — "
                                   f"never names the class it is cited for")
        fm = str(_front(f).get("status", "")).lower()
        sec = txt.split("## Ratification", 1)
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in (sec[1].splitlines() if len(sec) > 1 else [])
                if ln.strip().startswith("|") and not set(ln.replace("|", "").strip()) <= set("-: ")]
        rows = [r for r in rows if len(r) >= 4 and r[0].lower() != "decision"]
        last = rows[-1] if rows else None
        signed = bool(last and last[0] and last[1] and re.fullmatch(r"\d{4}-\d{2}-\d{2}", last[2]) and last[3].lower() in RATIFIED)
        if out["problems"]:
            out["why_not_ratified"] = out["problems"][0]
        elif not signed:
            out["why_not_ratified"] = (f"{dp['ruling']}: its Ratification row is not signed (decision · ratified-by · ISO date · "
                                       f"status ratified); the instance owner ratifies it before any data is fetched")
        elif fm not in RATIFIED:
            out["why_not_ratified"] = f"{dp['ruling']}: the Ratification row is signed but the frontmatter says {fm!r} — they must agree"
        else:
            out["ratified"] = True
    if out["problems"] and not out["why_not_ratified"]:
        out["why_not_ratified"] = out["problems"][0]
    return out


def check(root, items=None, stage: str = "declared", selftest: bool = True) -> dict:
    """{item: {"status": pass|fail|n/a|not_run, "reasons": [...], "read": [...]}} for each requested item."""
    root = Path(root).resolve()
    items = items or sorted(ITEMS)
    R = {i: {"status": "pass", "reasons": [], "read": []} for i in items}

    def fail(i, msg):
        if i in R:
            R[i]["reasons"].append(msg); R[i]["status"] = "fail"

    def read(i, *names):
        if i in R:
            R[i]["read"] += [n for n in names if n not in R[i]["read"]]

    # -- the declarations must load at all ----------------------------------------------------------------------
    if not (root / "atlantis.yaml").exists():
        for i in R:
            fail(i, "no atlantis.yaml — not an atlantis_core instance")
        return R
    docs = {}
    V = _validator()
    for fname, (i, key) in REGISTRY_FILES.items():
        read(i, fname)
        if not (root / fname).exists():
            fail(i, f"{fname} missing"); continue
        doc = load_yaml(root / fname)
        docs[fname] = doc
        if not doc.get(key):
            fail(i, f"{fname}: no `{key}` rows")
        for e in V.iter_errors(doc):
            fail(i, f"{fname}: atl_v0 {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:140]}")
    try:
        inst = load_instance(root, check=False)
    except Exception as e:  # noqa: BLE001 — a registry that does not load fails every item that reads it
        for i in R:
            fail(i, f"instance does not load: {e}")
        return R
    from atlantis_core.registry import RegistryError, check as reg_check
    registry_clean = True
    try:
        reg_check(inst)
    except RegistryError as e:
        registry_clean = False
        for line in str(e).splitlines()[1:]:
            line = line.strip(); rule = line.split(" ", 1)[0]
            fail(RULE_ITEM.get(rule, 3), f"registry {line}")
    cfg = inst.cfg
    for i in (1, 2, 5, 8):
        read(i, "atlantis.yaml")

    # -- 1 patient ----------------------------------------------------------------------------------------------
    if 1 in R:
        units = (docs.get("units.yaml") or {}).get("spatial_units") or []
        ids = {u.get("unit_id") for u in units}
        roots = [u for u in units if not u.get("parent_unit")]
        if units and len(roots) != 1:
            fail(1, f"units.yaml: {len(roots)} rows without parent_unit — expected exactly one region row")
        for u in units:
            if u.get("parent_unit") and u["parent_unit"] not in ids:
                fail(1, f"units.yaml: {u.get('unit_id')} parent_unit {u['parent_unit']!r} is not a declared unit")
            if u.get("time_step") != "iso_week":
                fail(1, f"units.yaml: {u.get('unit_id')} time_step {u.get('time_step')!r} — atlantis_core builds ISO weeks")
        g = cfg.get("grid") or {}
        codes = [str(c) for c in g.get("units") or []]
        if not codes:
            fail(1, "atlantis.yaml → grid.units: the grid's unit codes must be listed (units.yaml rows end `_<code>`)")
        for c in codes:
            if not any(str(u.get("unit_id", "")).endswith(f"_{c}".lower()) and u.get("parent_unit") for u in units):
                fail(1, f"grid unit {c!r} has no units.yaml row (`atl_unit_<slug>_{c}` PART_OF the region)")
        b = cfg.get("board") or {}
        if b.get("unit_ref") and b["unit_ref"] not in ids:
            fail(1, f"atlantis.yaml → board.unit_ref {b['unit_ref']!r} is not a units.yaml row")
        pclass = posture(root)["class"]
        if g.get("kind") in ("rules", "cells") and pclass != "public":
            fail(1, f"grid.kind {g.get('kind')} puts coordinates (rules / a bbox) in atlantis.yaml — public posture only "
                    f"(posture: {pclass!r})")
        for u in units:
            ref = str(u.get("geometry_ref", ""))
            if ref.startswith("/") or ref.startswith("~") or "/../" in f"/{ref}":
                fail(1, f"units.yaml: {u.get('unit_id')} geometry_ref {ref!r} points outside the instance")
        if g.get("kind") == "polygons":
            gp = inside(root, g.get("path"))
            read(1, str(g.get("path")))
            if gp is None or not gp.is_file():
                fail(1, f"grid.path {g.get('path')!r} does not resolve inside the instance (relative, under its root)")
            if gp is not None and gp.is_file():
                try:
                    feats = json.loads(gp.read_text()).get("features") or []
                    have = {str((f.get("properties") or {}).get(g["id_property"])) for f in feats}
                    miss = [c for c in codes if c not in have]
                    if miss:
                        fail(1, f"grid units {miss} are not features of {g['path']} (by {g['id_property']})")
                except (ValueError, KeyError) as e:
                    fail(1, f"{g.get('path')}: not a GeoJSON FeatureCollection with {g.get('id_property')!r} ({e})")

    # -- 2 event --------------------------------------------------------------------------------------------------
    if 2 in R:
        read(2, "streams.yaml")
        ev_id = (cfg.get("label") or {}).get("event")
        ev = inst.events.get(ev_id)
        if ev is None:
            fail(2, f"atlantis.yaml → label.event {ev_id!r} is not in events.yaml")
        else:
            for k in ("threshold", "unit", "direction", "horizon", "onset_rule"):
                if ev.get(k) in (None, "") or (isinstance(ev.get(k), str) and not ev[k].strip()):
                    fail(2, f"{ev_id}: {k} missing")
            s = inst.streams.get(ev.get("event_variable_stream")) or {}
            auth = str(s.get("authority", ""))
            if not re.match(r"^(%s):\S+$" % "|".join(AUTHORITIES), auth):
                fail(2, f"{ev_id}: its stream {ev.get('event_variable_stream')!r} names no authority CURIE from "
                        f"{'/'.join(AUTHORITIES)} for the variable (got {auth!r})")

    # -- 3 streams ------------------------------------------------------------------------------------------------
    if 3 in R:
        from atlantis_core.fetch import FETCHERS
        for sid, s in inst.streams.items():
            for k in ("source_system", "source_id", "license"):
                if not (isinstance(s.get(k), str) and s[k].strip()):
                    fail(3, f"{sid}: {k} missing (declared stage)")
            if s.get("fetcher") not in FETCHERS:
                fail(3, f"{sid}: fetcher {s.get('fetcher')!r} is not an atlantis_core fetcher")
            spec = (cfg.get("streams") or {}).get(sid) or {}
            if not (spec.get("artifact") and spec.get("summary")):
                fail(3, f"{sid}: atlantis.yaml → streams needs artifact + summary (where the fetch will land)")
            if stage == "fetched":
                for k in ("sha256", "ingested_at", "pipeline_version"):
                    if not s.get(k):
                        fail(3, f"{sid}: {k} missing (fetched stage)")
                if spec.get("artifact") and spec.get("summary"):
                    from atlantis_core.fetch.__main__ import verify
                    read(3, spec["artifact"], spec["summary"])
                    for p in verify(inst, sid):
                        if "carries no sha256" not in p:
                            fail(3, p)

    # -- 4 vitals -------------------------------------------------------------------------------------------------
    if 4 in R:
        for v in inst.vitals:
            if "lag" not in v and "window" not in v:
                fail(4, f"{v.get('vital_id')}: neither lag nor window stated (contract item 4)")
            if not v.get("stream_ref"):
                fail(4, f"{v.get('vital_id')}: no stream_ref")

    # -- 5 surveillance (R8 above) ------------------------------------------------------------------------------
    if 5 in R:
        read(5, "streams.yaml", "features.yaml")

    # -- 6 self-test ----------------------------------------------------------------------------------------------
    if 6 in R:
        from atlantis_core import selftest as st
        if not registry_clean:
            fail(6, "not run — the registries do not check clean (items above)")
        elif selftest:
            try:
                st.run(inst, verbose=False)
                R[6]["reasons"].append("re-run here on the synthetic world (no data)")
            except Exception as e:  # noqa: BLE001 — LeakError or a synthetic-world refusal: either way, not green
                fail(6, f"self-test: {type(e).__name__}: {str(e)[:300]}")
        else:
            read(6, st.RECEIPT)
            why = st.receipt_problem(inst)
            if why:
                fail(6, why)
            else:
                R[6]["reasons"].append("receipt current (not re-run: --no-selftest)")

    # -- 7 posture -------------------------------------------------------------------------------------------------
    if 7 in R:
        read(7, "how/federation/atlantis/CLAUDE.md")
        P = posture(root)
        if P["ruling"]:
            read(7, str(P["ruling"]))
        for why in P["problems"]:
            fail(7, why)
        if not P["problems"]:
            if stage == "fetched" and not P["ratified"]:
                fail(7, f"{P['why_not_ratified']} — data is fetched only under a RATIFIED posture")
            elif not P["ratified"]:
                R[7]["reasons"].append(f"ruling present, not yet ratified (ratify before the fetch)")
        if P["class"] in ("partner", "human_subject"):
            gi = (root / ".gitignore").read_text() if (root / ".gitignore").exists() else ""
            lines = {ln.strip() for ln in gi.splitlines()}
            miss = [x for x in ("data/", "outputs/", "site/") if x not in lines]
            if miss:
                fail(7, f"{P['class']} posture but .gitignore does not exclude {miss}")

    # -- 8 split --------------------------------------------------------------------------------------------------
    if 8 in R:
        sp = cfg.get("split") or {}
        keys = ("min_train_year", "train_end", "val_start", "val_end", "test_start", "test_end")
        if any(not isinstance(sp.get(k), int) or isinstance(sp.get(k), bool) for k in keys):
            fail(8, f"split needs integer years {keys}")
        else:
            y = [sp[k] for k in keys]
            if not (y[0] <= y[1] < y[2] <= y[3] < y[4] <= y[5]):
                fail(8, f"split is not temporal and disjoint: {dict(zip(keys, y))}")
            ro = sp.get("rolling_origin_years") or []
            if ro and max(ro) + 1 > sp["test_end"]:
                fail(8, f"rolling_origin_years {ro} test past test_end {sp['test_end']}")

    # -- 9 board entries / 10 pages (after a run) ---------------------------------------------------------------
    if 9 in R:
        entries = sorted((root / "what" / "board" / "entries").glob("*.json"))
        if not entries:
            R[9]["status"] = "n/a"; R[9]["reasons"].append("no board entry yet (after a run)")
        for e in entries:
            read(9, str(e.relative_to(root)))
            from atlantis_core.board import BoardError, assert_green, validate
            try:
                ent = json.loads(e.read_text()); validate(ent["evaluation"]); assert_green(ent)
                from atlantis_core.config import semantic_hash
                ev9 = ent["evaluation"]
                if ev9.get("unit_ref") != (cfg.get("board") or {}).get("unit_ref"):
                    fail(9, f"{e.name}: unit_ref {ev9.get('unit_ref')!r} is not this instance's board.unit_ref")
                xh = (ent.get("evaluation_extras") or {}).get("semantic_hash") or ev9.get("config_hash")
                if xh != semantic_hash(inst):
                    fail(9, f"{e.name}: config_hash {xh!r} ≠ this instance's semantic_hash {semantic_hash(inst)!r} — "
                            f"an entry for another config (or another instance)")
                if ent["evaluation"].get("claim") != "method_demonstration" and not ent["evaluation"].get("owner_ruling_ref"):
                    fail(9, f"{e.name}: a non-demonstration claim without owner_ruling_ref (SO-4)")
            except (BoardError, KeyError, ValueError) as x:
                fail(9, f"{e.name}: {str(x)[:200]}")
    if 10 in R:
        pages = sorted((root / "site").glob("*.html")) if (root / "site").is_dir() else []
        if not pages:
            R[10]["status"] = "n/a"; R[10]["reasons"].append("no published page yet (after a run)")
        for p in pages:
            read(10, str(p.relative_to(root)))
            html = re.sub(r"<!--.*?-->", "", p.read_text(errors="replace"), flags=re.S)        # a comment is not a section
            m = re.search(r"""<(section|div|article)\b[^>]*\bid=["']limits["'][^>]*>(.*?)</\1>""", html, re.S)
            text = re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip() if m else ""
            if not m:
                fail(10, f"{p.name}: no #limits section element")
            elif len(text) < 80:
                fail(10, f"{p.name}: #limits section has {len(text)} characters of text — limitations are written, not implied")
            if not re.search(r"analogy", re.sub(r"<[^>]+>", " ", html), re.I):
                fail(10, f"{p.name}: no 'where the analogy breaks' discussion (contract item 10)")

    # -- 11 mapping -----------------------------------------------------------------------------------------------
    if 11 in R:
        read(11, "mapping.yaml")
        mp = root / "mapping.yaml"
        if not mp.exists():
            fail(11, "mapping.yaml missing (render how/templates/template_mapping_atl.yaml)")
        else:
            from atlantis_core.mapping import SCHEMA, check as mcheck
            m = yaml.safe_load(mp.read_text()) or {}
            for e in mcheck(m, yaml.safe_load(SCHEMA.read_text())):
                fail(11, f"mapping: {e}")
            stem = (cfg.get("board") or {}).get("entry_stem")
            if stem and m.get("instance") != stem:
                fail(11, f"mapping.instance {m.get('instance')!r} ≠ atlantis.yaml → board.entry_stem {stem!r}")
            for kind, paths in (m.get("sources") or {}).items():
                for p in paths:
                    if "*" not in p and not (root / m.get("source_root", ".") / p).exists():
                        fail(11, f"mapping.sources.{kind}: {p!r} does not exist")

    # -- 12 credentials -------------------------------------------------------------------------------------------
    if 12 in R:
        gl = shutil.which("gitleaks")
        if not gl:
            R[12]["status"] = "not_run"; R[12]["reasons"].append("gitleaks not installed — item 12 NOT checked (never a silent pass)")
        else:
            # Atlantis's config and an empty ignore file: an instance-supplied .gitleaks.toml / .gitleaksignore cannot
            # allowlist its own secrets past the contract (III F-5). Inline `gitleaks:allow` comments still apply (limit).
            here = Path(__file__).resolve().parent
            r = subprocess.run([gl, "detect", "--no-git", "--source", str(root), "--no-banner", "--redact", "--exit-code", "3",
                                "--config", str(here / "gitleaks_atlantis.toml"),
                                "--gitleaks-ignore-path", str(here / "gitleaks_atlantis.ignore")],
                               capture_output=True, text=True)
            for own in (".gitleaks.toml", ".gitleaksignore"):
                if (root / own).exists():
                    R[12]["reasons"].append(f"instance {own} present and IGNORED (Atlantis's rules apply)")
            read(12, f"gitleaks detect --no-git {root.name}")
            if r.returncode == 3:
                fail(12, "gitleaks found candidate secrets:\n" + (r.stdout + r.stderr)[-800:])
            elif r.returncode != 0:
                R[12]["status"] = "not_run"; R[12]["reasons"].append(f"gitleaks errored (rc {r.returncode}): {(r.stderr or r.stdout)[-300:]}")
    return R


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.conform")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--items", default="1-12")
    ap.add_argument("--stage", choices=("declared", "fetched"), default="declared")
    ap.add_argument("--no-selftest", action="store_true", help="item 6: check the receipt instead of re-running")
    a = ap.parse_args(argv)
    R = check(a.instance, parse_items(a.items), a.stage, selftest=not a.no_selftest)
    mark = {"pass": "✅", "fail": "✗ ", "n/a": "– ", "not_run": "⚠ "}
    print(f"instance contract v0.2.0 · {Path(a.instance).resolve().name} · stage {a.stage}")
    for i, r in R.items():
        print(f"{mark[r['status']]} {i:>2} {ITEMS[i]}  [{' · '.join(r['read'])}]")
        for why in r["reasons"]:
            print(f"      {why}")
    bad = [i for i, r in R.items() if r["status"] in ("fail", "not_run")]
    na = [i for i, r in R.items() if r["status"] == "n/a"]
    print(f"{'✅ conforms' if not bad else '✗ does not conform'}: {len(R) - len(bad) - len(na)} pass · {len(na)} n/a "
          f"({', '.join(map(str, na)) or 'none'}) · {len(bad)} outstanding ({', '.join(map(str, bad)) or 'none'})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

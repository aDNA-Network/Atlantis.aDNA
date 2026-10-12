"""Check every ledger row (M-3b-i). The schema proves a row's SHAPE (atl_v0 0.9.0, 25 controls); this module checks what
the schema cannot see (schema README known limit 18). Each defect is a failure key; `--index --check` exits 1 on any.

Failure keys (each planted in tests/test_hypotheses.py):
  row_unreadable              the file is not a YAML mapping
  row_invalid                 the closed AtlHypothesis rejects it (committed JSON Schema, format checker on)
  id_file_mismatch            the file is not named <hyp_id>.yaml
  ecosystem_dir_mismatch      the row sits under a directory other than its ecosystem_type
  duplicate_hyp_id            two files carry one hyp_id
  citation_without_doi_or_url `doi: null` and no url (the schema's ABSENT precondition lets a null key through)
  citation_not_in_manifest    the DOI or URL is in neither the works nor the agency list of corpus/<eco>/manifest.yaml
  no_manifest                 rows exist for an ecosystem with no corpus manifest
  quote_too_long              a quoted span in sentence_pointer is over 25 words (README rule 1; operator ruling 3)
  pointer_too_long            the whole pointer is over 40 words (a locator or short quotation, never a paragraph)
  quote_not_in_text           a quoted span is not in the work's cached abstract (whitespace, quotes, dashes, case folded)
  reviewer_is_extractor       reviewed_by = recorded_by (a review is a second reader)
  validated_needs_two_reviewers  tier validated — refused until a second-reviewer slot exists (README rule 2)
  tested_incomplete           a result other than `untested` without realised_in · realised_vital · tested_at · write_up
Warnings (printed, never fail): quote_unverified (no cached text for that work: a fresh clone, or an abstract no source
serves) · locator_only (no quotation — the pointer cannot be checked against text at all).
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

from atlantis_core.hypotheses import POINTER_MAX_WORDS, QUOTE_MAX_WORDS, SCHEMA
from atlantis_core.hypotheses.corpus import bare_doi, cached_text, load_manifest

QUOTE = re.compile(r"[\"“]([^\"“”]+)[\"”]")
# Typographic variants a verbatim quotation may be typed without (M-3b-i: the corpus's first run met U+2010 HYPHEN in two
# abstracts, which an ASCII quotation of them did not match). Folding is equivalence of glyphs, never of words.
_FOLD = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2010": "-", "\u2011": "-", "\u2012": "-",
                       "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2043": "-", "\ufe63": "-", "\uff0d": "-", "\u00a0": " ", "\u202f": " "})


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(_FOLD)).strip().casefold()


def _iso(x):
    if isinstance(x, datetime):
        return x.isoformat().replace("+00:00", "Z")
    if isinstance(x, date):
        return x.isoformat()   # a bare date in a datetime slot is then refused by the format checker, as it should be
    return str(x)


def quotes(pointer: str) -> list[str]:
    return [m.strip() for m in QUOTE.findall(pointer or "") if m.strip()]


def _validator():
    from jsonschema import validators
    S = json.loads(SCHEMA.read_text())
    VC = validators.validator_for(S); FC = VC.FORMAT_CHECKER
    if FC.conforms("never", "date-time"):
        raise RuntimeError("jsonschema format checker does not check date-time here (install jsonschema[format]) — instrument failure")
    return VC(S, format_checker=FC)


def rows(root: Path) -> list[Path]:
    return sorted((root / "ledger").glob("*/*.yaml"))


def check_ledger(root: Path) -> tuple[list[dict], list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """→ (loaded rows, failures [(key, file, why)], warnings [(key, file, why)])."""
    V = _validator()
    fails, warns, loaded = [], [], []
    seen = defaultdict(list)
    manifests: dict[str, dict | None] = {}
    for p in rows(root):
        rel = f"{p.parent.name}/{p.name}"
        try:
            r = yaml.safe_load(p.read_text())
        except yaml.YAMLError as e:
            fails.append(("row_unreadable", rel, str(e)[:120])); continue
        if not isinstance(r, dict):
            fails.append(("row_unreadable", rel, "not a mapping")); continue
        # YAML reads an unquoted timestamp as a datetime/date; the schema checks the RFC 3339 string (format checker on)
        r = json.loads(json.dumps(r, default=_iso))
        errs = list(V.iter_errors({"hypotheses": [r]}))
        for e in errs:
            fails.append(("row_invalid", rel, f"/{'/'.join(map(str, list(e.absolute_path)[2:]))}: {e.message[:140]}"))
        loaded.append({**r, "_file": rel})
        hid, eco = r.get("hyp_id"), r.get("ecosystem_type")
        seen[hid].append(rel)
        if p.name != f"{hid}.yaml":
            fails.append(("id_file_mismatch", rel, f"hyp_id {hid!r}"))
        if p.parent.name != eco:
            fails.append(("ecosystem_dir_mismatch", rel, f"ecosystem_type {eco!r} under {p.parent.name}/"))
        c = r.get("citation") or {}
        doi, url = bare_doi(c.get("doi")), c.get("url")
        if not doi and not url:
            fails.append(("citation_without_doi_or_url", rel, "neither a DOI nor a URL"))
        if eco not in manifests:
            manifests[eco] = load_manifest(root, eco) if isinstance(eco, str) else None
        M = manifests[eco]
        work = None
        if M is None:
            fails.append(("no_manifest", rel, f"no corpus/{eco}/manifest.yaml"))
        elif doi or url:
            work = next((w for w in M.get("works") or [] if doi and w.get("doi") == doi), None)
            agency = next((a for a in M.get("agency") or [] if (doi and bare_doi(a.get("doi")) == doi) or (url and a.get("url") == url)), None)
            if work is None and agency is None:
                fails.append(("citation_not_in_manifest", rel, doi or url))
        ptr = str(r.get("sentence_pointer") or "")
        qs = quotes(ptr)
        if len(ptr.split()) > POINTER_MAX_WORDS:
            fails.append(("pointer_too_long", rel, f"{len(ptr.split())} words > {POINTER_MAX_WORDS}"))
        for q in qs:
            if len(q.split()) > QUOTE_MAX_WORDS:
                fails.append(("quote_too_long", rel, f"{len(q.split())} words > {QUOTE_MAX_WORDS}"))
        if not qs:
            warns.append(("locator_only", rel, "no quotation — the pointer cannot be checked against text"))
        elif work is not None:
            text = cached_text(root, eco, work["openalex_id"])
            if text is None:
                warns.append(("quote_unverified", rel, f"no cached text for {work['openalex_id']} (abstract: {work['abstract']['source']})"))
            else:
                for q in qs:
                    if _norm(q) not in _norm(text):
                        fails.append(("quote_not_in_text", rel, f"{q[:60]!r} not in {work['openalex_id']}"))
        elif qs:
            warns.append(("quote_unverified", rel, "an agency work — no cached text"))
        if r.get("tier") == "reviewed" and r.get("reviewed_by") and r.get("reviewed_by") == r.get("recorded_by"):
            fails.append(("reviewer_is_extractor", rel, f"reviewed_by = recorded_by = {r['reviewed_by']!r}"))
        if r.get("tier") == "validated":
            fails.append(("validated_needs_two_reviewers", rel, "reviewed_by holds one reviewer; no second-reviewer slot yet"))
        z = r.get("realisation") or {}
        if z.get("result") not in (None, "untested"):
            missing = [k for k in ("realised_in", "realised_vital", "tested_at", "write_up") if not z.get(k)]
            if missing:
                fails.append(("tested_incomplete", rel, f"result {z['result']!r} without {', '.join(missing)}"))
    for hid, files in seen.items():
        if len(files) > 1:
            fails.append(("duplicate_hyp_id", files[0], f"{hid!r} also in {', '.join(files[1:])}"))
    return loaded, fails, warns

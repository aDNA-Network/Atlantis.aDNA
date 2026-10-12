"""Check every ledger row (M-3b-i). The schema proves a row's SHAPE (atl_v0 0.9.0, 48 hypothesis controls); this module
checks what the schema cannot see (schema README known limit 18). Each defect is a failure key; `--index --check` exits 1
on any. Hardened at the M-3b-i III review (F-2, F-3, F-9, F-12).

Failure keys (each planted in tests/test_hypotheses.py):
  row_unreadable              the file is not a YAML mapping
  row_misplaced               a row file that is not ledger/<ecosystem>/<name>.yaml (a .yml, or nested deeper)
  row_invalid                 the closed AtlHypothesis rejects it (committed JSON Schema, format checker on)
  id_file_mismatch            the file is not named <hyp_id>.yaml
  ecosystem_dir_mismatch      the row sits under a directory other than its ecosystem_type
  duplicate_hyp_id            two files carry one hyp_id
  citation_without_doi_or_url `doi: null` and no url (the schema's ABSENT precondition lets a null key through)
  citation_not_in_manifest    the DOI or URL is in neither the works nor the agency list of corpus/<eco>/manifest.yaml
  no_manifest                 rows exist for an ecosystem with no corpus manifest
  cache_tampered              the cached abstract's bytes do not hash to the manifest's sha256 (F-2a) — the text a
                              quotation is checked against must be the text that was retrieved
  pointer_unparsed            a pointer that is neither a quotation (any quote glyph) nor a locator (F-2b)
  quote_too_long              a quotation over 25 words (README rule 1; operator ruling 3)
  pointer_too_long            the whole pointer is over 40 words
  quote_not_in_text           a quotation not in the cached abstract at word boundaries (glyphs, space, case folded)
  quote_after_negation        every occurrence follows a negator (not · no · never · without · nor · cannot) the
                              quotation omits (F-3) — a fragment that drops the paper's "not"
  verbatim_overflow           over 25 words of one abstract copied (runs of ≥ 6 words) across a row's free-text fields
                              (the quotation included), or across the non-quotation fields of all rows citing one work
                              (F-9) — paraphrase; quote only in the pointer
  reviewer_is_extractor       reviewed_by = recorded_by, case- and space-folded (F-12a)
  reviewed_unbound            tier reviewed without reviewed_sha256 (F-3)
  reviewed_content_changed    the row no longer hashes to its reviewed_sha256: it changed after review (F-3)
  validated_needs_two_reviewers  tier validated — refused until a second-reviewer slot exists (README rule 2)
  tested_incomplete           a result other than `untested` without realised_in · realised_vital · tested_at · write_up
Warnings (printed, never fail): quote_unverified (no cached text — a fresh clone, or an abstract no source serves) ·
locator_only (a locator, not a quotation — it cannot be checked against text).
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

from atlantis_core.hypotheses import POINTER_MAX_WORDS, QUOTE_MAX_WORDS, SCHEMA
from atlantis_core.hypotheses.corpus import bare_doi, load_manifest

# Quotations: "…" “…” ‘…’ «…», and '…' when it opens after a boundary and closes before one (so an apostrophe inside a
# word — MHWs', can't — is not read as a quote mark). III M-3b-i F-2b: single quotes used to bypass every quote check.
QUOTES = [re.compile(r"\"([^\"]+)\""), re.compile(r"“([^”]+)”"), re.compile(r"‘([^’]+)’"), re.compile(r"«([^»]+)»"),
          re.compile(r"(?:(?<=^)|(?<=[\s:(\[]))'(\S(?:[^']*\S)?)'(?=$|[\s.,;:)\]])")]
LOCATOR = re.compile(r"^\s*(abstract|results?|discussion|methods?|introduction|conclusions?|summary|table|tab\.|fig\.?|"
                     r"figure|supplement\w*|section|p\.|pp\.|page|para(graph)?)\b|[§¶]", re.I)
NEGATORS = {"not", "no", "never", "without", "nor", "cannot", "neither"}
COPY_RUN = 6   # a run of ≥ 6 consecutive abstract words counts as copied (F-9)
# Typographic variants a verbatim quotation may be typed without (M-3b-i: the corpus's first run met U+2010 HYPHEN in two
# abstracts, which an ASCII quotation of them did not match). Folding is equivalence of glyphs, never of words.
_FOLD = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "‐": "-", "‑": "-", "‒": "-",
                       "–": "-", "—": "-", "−": "-", "⁃": "-", "﹣": "-", "－": "-", " ": " ", " ": " "})
# What a review binds: the PAPER-FACING fields the step-6 reader judges. Excluded: the review's own fields; `realisable_as`
# and `realisability` (the extractor's instance-relative translation — the reader flags, never confirms, it); and
# `realisation` (filled by the instance that tests the row, which must not void the review).
REVIEW_EXCLUDED = ("tier", "reviewed_by", "reviewed_sha256", "realisable_as", "realisability", "realisation")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(_FOLD)).strip().casefold()


def _words(s: str) -> list[str]:
    return [w.strip(".'") for w in re.sub(r"[^\w\-'./%°]+", " ", _norm(s)).split() if w.strip(".'")]


def _iso(x):
    if isinstance(x, datetime):
        return x.isoformat().replace("+00:00", "Z")
    if isinstance(x, date):
        return x.isoformat()   # a bare date in a datetime slot is then refused by the format checker, as it should be
    return str(x)


def quotes(pointer: str) -> list[str]:
    out = []
    for rx in QUOTES:
        out += [m.strip() for m in rx.findall(pointer or "") if m.strip()]
    return out


def review_hash(row: dict) -> str:
    """sha256 of the row as a reviewer reads it: canonical JSON, minus the fields the review itself writes."""
    r = {k: v for k, v in json.loads(json.dumps(row, default=_iso)).items() if k not in REVIEW_EXCLUDED and not k.startswith("_")}
    return hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _validator():
    from jsonschema import validators
    S = json.loads(SCHEMA.read_text())
    VC = validators.validator_for(S); FC = VC.FORMAT_CHECKER
    if FC.conforms("never", "date-time"):
        raise RuntimeError("jsonschema format checker does not check date-time here (install jsonschema[format]) — instrument failure")
    return VC(S, format_checker=FC)


def rows(root: Path) -> list[Path]:
    """Every YAML file under ledger/ — including misplaced ones, which check refuses rather than skips (F-12b)."""
    return sorted(p for p in (root / "ledger").rglob("*") if p.is_file() and p.suffix in (".yaml", ".yml"))


def cached(root: Path, eco: str, work: dict) -> tuple[str | None, bool]:
    """→ (text, hash_ok). Bytes are hashed, not decoded text: universal newlines would change CR bytes (F-12c)."""
    p = root / "corpus" / eco / "unreviewed" / f"{work['openalex_id']}.txt"
    if not p.exists():
        return None, True
    b = p.read_bytes()
    body = b[:-1] if b.endswith(b"\n") else b
    return body.decode(), hashlib.sha256(body).hexdigest() == (work.get("abstract") or {}).get("sha256")


def _copied_positions(text: str, fields: list[str]) -> set[int]:
    """Positions of abstract words inside a run of ≥ COPY_RUN consecutive words that a field also contains."""
    aw = _words(text)
    grams = defaultdict(list)
    for i in range(len(aw) - COPY_RUN + 1):
        grams[tuple(aw[i:i + COPY_RUN])].append(i)
    cov = set()
    for f in fields:
        fw = _words(f)
        for j in range(len(fw) - COPY_RUN + 1):
            for i in grams.get(tuple(fw[j:j + COPY_RUN]), ()):
                cov.update(range(i, i + COPY_RUN))
    return cov


def _free_text(r: dict) -> list[str]:
    d = r.get("driver") or {}
    return [str(x) for x in (r.get("mechanism"), r.get("sentence_pointer"), r.get("realisable_as"), r.get("region_asserted"),
                             r.get("event_variable"), d.get("variable"), (d.get("driver_lag") or {}).get("lag_note")) if x]


def check_ledger(root: Path) -> tuple[list[dict], list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """→ (loaded rows, failures [(key, file, why)], warnings [(key, file, why)])."""
    V = _validator()
    fails, warns, loaded = [], [], []
    seen = defaultdict(list)
    manifests: dict[str, dict | None] = {}
    by_work: dict[tuple[str, str], set[int]] = defaultdict(set)
    for p in rows(root):
        rel = str(p.relative_to(root / "ledger"))
        if p.suffix != ".yaml" or p.parent.parent != root / "ledger":
            fails.append(("row_misplaced", rel, "a row is ledger/<ecosystem>/<hyp_id>.yaml — nothing else is read")); continue
        try:
            r = yaml.safe_load(p.read_text())
        except yaml.YAMLError as e:
            fails.append(("row_unreadable", rel, str(e)[:120])); continue
        if not isinstance(r, dict):
            fails.append(("row_unreadable", rel, "not a mapping")); continue
        # YAML reads an unquoted timestamp as a datetime/date; the schema checks the RFC 3339 string (format checker on)
        r = json.loads(json.dumps(r, default=_iso))
        for e in V.iter_errors({"hypotheses": [r]}):
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
            if LOCATOR.search(ptr):
                warns.append(("locator_only", rel, "a locator — the pointer cannot be checked against text"))
            else:
                fails.append(("pointer_unparsed", rel, f"neither a quotation nor a locator: {ptr[:60]!r}"))
        text = None
        if work is not None:
            text, ok = cached(root, eco, work)
            if text is not None and not ok:
                fails.append(("cache_tampered", rel, f"unreviewed/{work['openalex_id']}.txt does not hash to the manifest")); text = None
            elif text is None and qs:
                warns.append(("quote_unverified", rel, f"no cached text for {work['openalex_id']} (abstract: {work['abstract']['source']})"))
        elif qs:
            warns.append(("quote_unverified", rel, "an agency work — no cached text"))
        if text is not None:
            nt = _norm(text)
            for q in qs:
                nq = _norm(q)
                hits = list(re.finditer(r"(?<!\w)" + re.escape(nq) + r"(?!\w)", nt))
                if not hits:
                    fails.append(("quote_not_in_text", rel, f"{q[:60]!r} not in {work['openalex_id']}")); continue
                qneg = NEGATORS & set(_words(nq)[:3])
                if all((NEGATORS & set(_words(nt[:h.start()])[-5:])) - qneg for h in hits):
                    fails.append(("quote_after_negation", rel, f"{q[:60]!r} follows a negator the quotation omits"))
            cov = _copied_positions(text, _free_text(r))
            if len(cov) > QUOTE_MAX_WORDS:
                fails.append(("verbatim_overflow", rel, f"{len(cov)} words of {work['openalex_id']} copied in runs of ≥ {COPY_RUN} (cap {QUOTE_MAX_WORDS}) — paraphrase"))
            # Across rows, the quotations are capped one by one (ruling 3: each row quotes ≤ 25 words); what the work-level cap
            # guards is copying smuggled through the OTHER fields (a pasted abstract in `mechanism`, F-9 plant P7).
            by_work[(eco, work["openalex_id"])] |= _copied_positions(text, [f for f in _free_text(r) if f != ptr])
        rb, rec = str(r.get("reviewed_by") or "").strip().casefold(), str(r.get("recorded_by") or "").strip().casefold()
        if r.get("tier") == "reviewed":
            if rb and rb == rec:
                fails.append(("reviewer_is_extractor", rel, f"reviewed_by = recorded_by = {r['reviewed_by']!r}"))
            if not r.get("reviewed_sha256"):
                fails.append(("reviewed_unbound", rel, "reviewed without reviewed_sha256 — stamp it at promotion"))
            elif r["reviewed_sha256"] != review_hash(r):
                fails.append(("reviewed_content_changed", rel, "the row changed after review — re-review, or demote to draft"))
        if r.get("tier") == "validated":
            fails.append(("validated_needs_two_reviewers", rel, "reviewed_by holds one reviewer; no second-reviewer slot yet"))
        z = r.get("realisation") or {}
        if z.get("result") not in (None, "untested"):
            missing = [k for k in ("realised_in", "realised_vital", "tested_at", "write_up") if not z.get(k)]
            if missing:
                fails.append(("tested_incomplete", rel, f"result {z['result']!r} without {', '.join(missing)}"))
    for (eco, wid), cov in by_work.items():
        if len(cov) > QUOTE_MAX_WORDS:
            fails.append(("verbatim_overflow", f"{eco}/*", f"{len(cov)} words of {wid} copied across its rows (cap {QUOTE_MAX_WORDS})"))
    for hid, files in seen.items():
        if len(files) > 1:
            fails.append(("duplicate_hyp_id", files[0], f"{hid!r} also in {', '.join(files[1:])}"))
    return loaded, fails, warns


def stamp_review(path: Path, reviewer: str) -> dict:
    """Promote one row: tier reviewed, reviewed_by, reviewed_sha256 over the content the reviewer read."""
    r = yaml.safe_load(path.read_text())
    if str(reviewer).strip().casefold() == str(r.get("recorded_by", "")).strip().casefold():
        raise ValueError("a review is a second reader — the reviewer is the extractor")
    r["tier"], r["reviewed_by"] = "reviewed", reviewer
    r["reviewed_sha256"] = review_hash(r)
    path.write_text(yaml.safe_dump(r, sort_keys=False, allow_unicode=True, width=130))
    return r

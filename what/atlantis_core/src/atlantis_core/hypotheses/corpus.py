"""The standalone literature intake (M-3b-i) — OpenAlex search, Europe PMC for abstracts OpenAlex withholds.

Why standalone: `Ingest.aDNA` owns intake-with-provenance in the fleet, but its documents class is "planned" and it has
no literature backend; the M-3b card's fallback is "a documented standalone fetch, `unreviewed/` discipline either way".
When Ingest grows one, this module is what it replaces.

What is committed and what is not (operator ruling 3, 2026-10-12; SO-3):
- `manifest.yaml` — COMMITTED. Per query: the search string, the server's count, how many were kept, the reported
  cost. Per work: OpenAlex id · DOI · title · year · type · cited-by · the queries that found it · where its abstract
  came from · the abstract's word count and sha256 (so the uncommitted text can be verified, never re-typed). A
  result-set sha256 over the works. Metadata only.
- `unreviewed/<openalex id>.txt` — the abstract text. GITIGNORED. Never staged.

A work whose abstract no source serves keeps its row in the manifest (`abstract.source: none`); a hypothesis may cite it
with a locator pointer, and `check` then reports the pointer as unverified rather than passing it silently.

`fetch_corpus(..., session=…)` takes any object with `.get(url, params=None, timeout=None)`; tests pass fakes. No API key
is used and no e-mail is sent (OpenAlex's `mailto` is omitted).
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from atlantis_core.hypotheses import LedgerError

OPENALEX = "https://api.openalex.org/works"
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
SELECT = "id,doi,display_name,publication_year,type,cited_by_count,abstract_inverted_index,primary_location"
MANIFEST_SCHEMA = "atl_corpus_manifest_v0"


def reconstruct(inverted: dict | None) -> str:
    """OpenAlex's abstract_inverted_index ({word: [positions]}) → the text, words in position order."""
    if not inverted:
        return ""
    pos = {}
    for word, places in inverted.items():
        for p in places:
            pos[int(p)] = word
    return " ".join(pos[i] for i in sorted(pos))


def bare_doi(doi: str | None) -> str | None:
    """`https://doi.org/10.x/Y` → `10.x/y` (DOIs are case-insensitive; the manifest stores them lower-case)."""
    if not doi:
        return None
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.I)
    return d.lower() if d.startswith("10.") else None


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"</?[A-Za-z][A-Za-z0-9]*(?:\s[^<>]*)?/?>", " ", s))).strip()


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class _Http:
    def __init__(self, session=None, timeout: int = 60, retries: int = 3):
        self._s, self.timeout, self.retries = session, timeout, retries
        self.hosts: Counter = Counter()
        self.failed = 0

    def json(self, url, params):
        if self._s is None:
            import requests
            self._s = requests.Session()
        err = None
        for _ in range(self.retries):
            self.hosts[urlsplit(url).netloc] += 1
            try:
                r = self._s.get(url, params=params, timeout=self.timeout)
                if r.status_code >= 400:
                    err = f"HTTP {r.status_code}"; continue
                return r.json()
            except (OSError, ValueError) as e:   # III M-3b-i F-8: network and decode errors only — requests' errors are
                err = f"{type(e).__name__}: {str(e)[:160]}"   # OSError subclasses; an AssertionError (a test's socket guard) propagates
        self.failed += 1
        print(f"  ✗ {url[:70]} {params}: {err}", file=sys.stderr)
        return None


def europepmc_abstract(doi: str, H: _Http) -> str:
    d = H.json(EUROPEPMC, {"query": f'DOI:"{doi}"', "resultType": "core", "format": "json", "pageSize": 1})
    for r in ((d or {}).get("resultList") or {}).get("result") or []:
        if (r.get("doi") or "").lower() == doi and r.get("abstractText"):
            return _strip_tags(r["abstractText"])
    return ""


def load_queries(path: Path) -> dict:
    q = yaml.safe_load(path.read_text())
    if not isinstance(q, dict) or not isinstance(q.get("queries"), list) or not q["queries"]:
        raise LedgerError(f"{path}: needs a non-empty `queries:` list")
    ids = [x.get("id") for x in q["queries"]]
    if len(set(ids)) != len(ids) or not all(ids):
        raise LedgerError(f"{path}: every query needs a unique `id`")
    for x in q["queries"]:
        if not str(x.get("search", "")).strip():
            raise LedgerError(f"{path}: query {x['id']!r} has no `search`")
    for a in q.get("agency") or []:
        if not (a.get("doi") or a.get("url")) or not a.get("title") or not a.get("year"):
            raise LedgerError(f"{path}: an agency entry needs doi or url, title and year: {a}")
    return q


def fetch_corpus(ecosystem: str, root: Path, *, session=None, refresh: bool = False, max_per_query: int | None = None,
                 europepmc: bool = True, now: str | None = None, allow_partial: bool = False) -> dict:
    """Run every query in `corpus/<ecosystem>/queries.yaml`; write the manifest and the gitignored abstracts.
    Refuses to overwrite an existing manifest unless `refresh` (a manifest is a retrieval record; OpenAlex's ranking moves)."""
    cdir = root / "corpus" / ecosystem
    qpath, mpath, udir = cdir / "queries.yaml", cdir / "manifest.yaml", cdir / "unreviewed"
    if not qpath.exists():
        raise LedgerError(f"no {qpath} — write the queries first (skill_feature_hypothesis_mining step 2)")
    if mpath.exists() and not refresh:
        raise LedgerError(f"{mpath} exists — a manifest is a retrieval record; pass --refresh to replace it")
    Q = load_queries(qpath)
    per = int(max_per_query or Q.get("per_query", 25))
    if not 1 <= per <= 200:
        raise LedgerError(f"per_query {per} out of 1…200")
    H = _Http(session)
    works: dict[str, dict] = {}
    texts: dict[str, str] = {}
    qrec = []
    for q in Q["queries"]:
        params = {"search": q["search"], "per-page": min(per, 200), "select": SELECT}
        if q.get("filter"):
            params["filter"] = q["filter"]
        d = H.json(OPENALEX, params)
        if d is None:
            qrec.append({"id": q["id"], "search": q["search"], "filter": q.get("filter"), "theme": q.get("theme"),
                         "server_count": None, "kept": 0, "error": "no answer (see stderr)"}); continue
        res = (d.get("results") or [])[:per]
        meta = d.get("meta") or {}
        qrec.append({"id": q["id"], "search": q["search"], "filter": q.get("filter"), "theme": q.get("theme"),
                     "server_count": meta.get("count"), "kept": len(res), "cost_usd": meta.get("cost_usd")})
        for w in res:
            key = str(w.get("id", "")).rsplit("/", 1)[-1]
            if not re.fullmatch(r"W\d+", key):
                continue
            if key in works:
                works[key]["queries"].append(q["id"]); continue
            text, src = reconstruct(w.get("abstract_inverted_index")), "openalex"
            doi = bare_doi(w.get("doi"))
            if not text and doi and europepmc:
                text, src = europepmc_abstract(doi, H), "europe_pmc"
            if not text:
                src = "none"
            loc = (w.get("primary_location") or {}).get("source") or {}
            works[key] = {"openalex_id": key, "doi": doi, "title": _strip_tags(str(w.get("display_name") or "")),
                          "year": w.get("publication_year"), "type": w.get("type"), "venue": loc.get("display_name"),
                          "cited_by": w.get("cited_by_count"), "queries": [q["id"]],
                          "abstract": {"source": src, "words": len(text.split()) if text else 0,
                                       "sha256": _sha(text) if text else None}}
            if text:
                texts[key] = text
    failed_q = [q["id"] for q in qrec if q.get("error")]
    if (failed_q or H.failed) and not allow_partial:   # III M-3b-i F-8: fail closed — never replace a record with a partial one
        raise LedgerError(f"{len(failed_q)} quer{'y' if len(failed_q) == 1 else 'ies'} unanswered {failed_q} and {H.failed} failed "
                          f"request(s) — nothing written; retry, or pass --allow-partial to record a partial retrieval")
    for w in works.values():
        w["queries"] = sorted(set(w["queries"]))
    wl = [works[k] for k in sorted(works)]
    agency = [{k: a[k] for k in ("doi", "url", "title", "year", "note") if a.get(k) is not None} for a in (Q.get("agency") or [])]
    for a in agency:
        if a.get("doi"):
            a["doi"] = bare_doi(a["doi"]) or a["doi"]
    body = {"works": wl, "agency": agency}
    manifest = {
        "corpus_schema": MANIFEST_SCHEMA,
        "ecosystem_type": ecosystem,
        "retrieved_at": now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "atlantis_core.hypotheses corpus (standalone intake; Ingest.aDNA has no literature class yet)",
        "sources": {"search": "OpenAlex /works (no key; mailto omitted)",
                    "abstracts": "OpenAlex abstract_inverted_index, else Europe PMC by DOI" if europepmc else "OpenAlex abstract_inverted_index"},
        "per_query": per,
        "partial": bool(failed_q or H.failed),
        "requests": dict(sorted(H.hosts.items())),
        "abstract_text": "unreviewed/<openalex_id>.txt — gitignored; never committed (operator ruling 3, SO-3)",
        "queries": qrec,
        "counts": {"works": len(wl), "with_abstract": sum(1 for w in wl if w["abstract"]["source"] != "none"),
                   "abstract_from": dict(sorted(Counter(w["abstract"]["source"] for w in wl).items())), "agency": len(agency)},
        "result_sha256": _sha(yaml.safe_dump(body, sort_keys=True, allow_unicode=True)),
        **body,
    }
    udir.mkdir(parents=True, exist_ok=True)
    for k, t in texts.items():
        (udir / f"{k}.txt").write_text(t + "\n")
    mpath.write_text("# GENERATED by `python -m atlantis_core.hypotheses corpus` — a retrieval record; metadata only. Abstract text is in\n"
                     "# unreviewed/ (gitignored). Re-running needs --refresh and replaces this record.\n"
                     + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=140))
    return manifest


def load_manifest(root: Path, ecosystem: str) -> dict | None:
    p = root / "corpus" / ecosystem / "manifest.yaml"
    return yaml.safe_load(p.read_text()) if p.exists() else None


def cached_text(root: Path, ecosystem: str, openalex_id: str) -> str | None:
    p = root / "corpus" / ecosystem / "unreviewed" / f"{openalex_id}.txt"
    return p.read_text() if p.exists() else None

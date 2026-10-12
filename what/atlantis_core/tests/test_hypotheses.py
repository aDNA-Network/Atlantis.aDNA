"""hypotheses (M-3b-i): the ledger's intake, check and index. Every failure key is shown to fire on a planted row and to
stay quiet on the clean one. No network, ever: the intake runs against a fake session, and a socket opened anywhere fails
the test."""
import copy, socket

import pytest
import yaml

from atlantis_core.hypotheses import LedgerError
from atlantis_core.hypotheses import corpus as C
from atlantis_core.hypotheses.__main__ import main as hyp_main
import hashlib

from atlantis_core.hypotheses.check import check_ledger, quotes, review_hash, stamp_review
from atlantis_core.hypotheses.index import _cell, render, write_or_check


@pytest.fixture(autouse=True)
def no_sockets(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a socket was opened")
    monkeypatch.setattr(socket.socket, "connect", boom)


class R:
    def __init__(self, body=None, code=200):
        self.body, self.status_code = body, code

    def json(self):
        return self.body


class Fake:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, dict(params or {})))
        for sub, pred, resp in self.routes:
            if sub in url and pred(params or {}):
                return resp
        return R(code=404)


ABSTRACT_1 = "Low wind speeds reduce mixing, and reef water warms rapidly during calm periods in summer."
INV_1 = {}
for i, w in enumerate(ABSTRACT_1.split()):
    INV_1.setdefault(w, []).append(i)
W1 = {"id": "https://openalex.org/W111", "doi": "https://doi.org/10.1000/ABC.1", "display_name": "Wind and <i>reef</i> heat",
      "publication_year": 2001, "type": "article", "cited_by_count": 10, "abstract_inverted_index": INV_1,
      "primary_location": {"source": {"display_name": "Coral Reefs"}}}
W2 = {"id": "https://openalex.org/W222", "doi": "https://doi.org/10.1000/def.2", "display_name": "ENSO and the Keys",
      "publication_year": 2010, "type": "article", "cited_by_count": 5, "abstract_inverted_index": None, "primary_location": None}
W3 = {"id": "https://openalex.org/W333", "doi": None, "display_name": "A report", "publication_year": 1999, "type": "report",
      "cited_by_count": 0, "abstract_inverted_index": None, "primary_location": None}
EPMC_2 = {"resultList": {"result": [{"doi": "10.1000/def.2", "abstractText": "<h4>Results</h4><p>Warm ENSO years preceded &amp; amplified bleaching.</p>"}]}}


def session():
    return Fake([
        ("api.openalex.org", lambda p: p.get("search") == "wind reef", R({"meta": {"count": 977, "cost_usd": 0.001}, "results": [W1, W2]})),
        ("api.openalex.org", lambda p: p.get("search") == "enso reef", R({"meta": {"count": 50}, "results": [W2, W3]})),
        ("europepmc", lambda p: "10.1000/def.2" in p.get("query", ""), R(EPMC_2)),
        ("europepmc", lambda p: True, R({"resultList": {"result": []}})),
    ])


QUERIES = {"per_query": 10, "queries": [{"id": "q_wind", "search": "wind reef", "theme": "wind"},
                                        {"id": "q_enso", "search": "enso reef", "theme": "enso", "filter": "publication_year:>1990"}],
           "agency": [{"url": "https://example.org/crw/method", "title": "CRW method", "year": 2014, "note": "agency"}]}


@pytest.fixture
def root(tmp_path):
    (tmp_path / "corpus" / "coral_reef").mkdir(parents=True)
    (tmp_path / "corpus" / "coral_reef" / "queries.yaml").write_text(yaml.safe_dump(QUERIES))
    (tmp_path / "ledger" / "coral_reef").mkdir(parents=True)
    return tmp_path


def fetched(root):
    return C.fetch_corpus("coral_reef", root, session=session(), now="2026-10-12T00:00:00Z")


ROW = {"hyp_id": "atl_hyp_coral_reef_wind_001", "tier": "draft", "ecosystem_type": "coral_reef",
       "event_variable": "degree_heating_week", "mechanism": "Calm, low-wind periods let reef water warm rapidly.",
       "driver": {"variable": "wind_speed", "authority": "CF:wind_speed",
                  "driver_lag": {"lag_value": 0, "lag_unit": "weeks", "lag_note": "not stated — concurrent"},
                  "driver_direction": "negative"},
       "region_asserted": "example tract", "evidence_class": "observational",
       "citation": {"doi": "10.1000/abc.1", "title": "Wind and reef heat", "year": 2001, "citation_source": "openalex"},
       "sentence_pointer": 'abstract: "reef water warms rapidly during calm periods"', "hypothesis_source": "literature",
       "realisable_as": "buoy wind speed · weekly mean · lag 0–2 weeks", "realisability": "declared_fetcher",
       "realisation": {"result": "untested"},
       "recorded_by": "agent_proteus", "recorded_at": "2026-10-12T00:00:00Z"}


def recache(root, wid, text):
    """Rewrite a cached abstract AND its manifest hash, as a real re-fetch would (a cache edit alone is tampering)."""
    (root / "corpus" / "coral_reef" / "unreviewed" / f"{wid}.txt").write_text(text + "\n")
    mp = root / "corpus" / "coral_reef" / "manifest.yaml"
    m = yaml.safe_load(mp.read_text())
    for w in m["works"]:
        if w["openalex_id"] == wid:
            w["abstract"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
    mp.write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True))


def put(root, row, name=None, eco="coral_reef"):
    d = root / "ledger" / eco; d.mkdir(parents=True, exist_ok=True)
    (d / (name or f"{row['hyp_id']}.yaml")).write_text(yaml.safe_dump(row, sort_keys=False, allow_unicode=True))


# ── intake ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_reconstruct_orders_by_position():
    assert C.reconstruct(INV_1) == ABSTRACT_1
    assert C.reconstruct({"b": [1], "a": [0, 2]}) == "a b a"
    assert C.reconstruct(None) == ""


def test_bare_doi():
    assert C.bare_doi("https://doi.org/10.1000/ABC.1") == "10.1000/abc.1"
    assert C.bare_doi("doi:10.5/x") == "10.5/x"
    assert C.bare_doi(None) is None and C.bare_doi("not a doi") is None


def test_corpus_manifest_is_metadata_only(root):
    m = fetched(root)
    assert [w["openalex_id"] for w in m["works"]] == ["W111", "W222", "W333"]
    w1, w2, w3 = m["works"]
    assert w1["doi"] == "10.1000/abc.1" and w1["title"] == "Wind and reef heat" and w1["queries"] == ["q_wind"]
    assert w2["queries"] == ["q_enso", "q_wind"]                         # found twice, recorded once
    assert w1["abstract"]["source"] == "openalex" and w1["abstract"]["words"] == len(ABSTRACT_1.split())
    assert w2["abstract"]["source"] == "europe_pmc"                       # OpenAlex withheld it; Europe PMC by DOI
    assert w3["abstract"] == {"source": "none", "words": 0, "sha256": None}   # no DOI, no fallback, recorded as none
    assert m["queries"][0]["server_count"] == 977 and m["queries"][0]["cost_usd"] == 0.001
    assert m["agency"][0]["url"] == "https://example.org/crw/method"
    text = (root / "corpus" / "coral_reef" / "manifest.yaml").read_text()
    assert "warms rapidly" not in text and "amplified" not in text        # no abstract text in the committed record
    assert (root / "corpus" / "coral_reef" / "unreviewed" / "W111.txt").read_text().strip() == ABSTRACT_1
    assert (root / "corpus" / "coral_reef" / "unreviewed" / "W222.txt").read_text().strip() == "Results Warm ENSO years preceded & amplified bleaching."
    assert not (root / "corpus" / "coral_reef" / "unreviewed" / "W333.txt").exists()
    assert m["requests"] == {"api.openalex.org": 2, "www.ebi.ac.uk": 1}


def test_strip_tags_keeps_inequalities():
    """III-faithfulness finding (M-3b-i): a markup stripper of `<[^>]+>` eats `(<4 m/s … >5 weeks)` whole. Only tags go."""
    assert C._strip_tags("<p>breeze winds (<4 m/s) for >5 weeks</p>") == "breeze winds (<4 m/s) for >5 weeks"
    assert C._strip_tags("<h4>Results</h4><i>K.</i> brevis &amp; wind") == "Results K. brevis & wind"


def test_corpus_refuses_to_replace_a_manifest(root):
    fetched(root)
    with pytest.raises(LedgerError, match="--refresh"):
        fetched(root)
    C.fetch_corpus("coral_reef", root, session=session(), refresh=True, now="2026-10-13T00:00:00Z")


def test_corpus_result_hash_is_stable(root):
    a = fetched(root)["result_sha256"]
    b = C.fetch_corpus("coral_reef", root, session=session(), refresh=True, now="2030-01-01T00:00:00Z")["result_sha256"]
    assert a == b   # the retrieval time is not part of the result set


@pytest.mark.parametrize("bad, match", [
    ({"queries": []}, "non-empty"),
    ({"queries": [{"id": "a", "search": "x"}, {"id": "a", "search": "y"}]}, "unique"),
    ({"queries": [{"id": "a", "search": " "}]}, "no `search`"),
    ({"queries": [{"id": "a", "search": "x"}], "agency": [{"title": "t", "year": 2000}]}, "doi or url"),
])
def test_queries_refused(root, bad, match):
    (root / "corpus" / "coral_reef" / "queries.yaml").write_text(yaml.safe_dump(bad))
    with pytest.raises(LedgerError, match=match):
        fetched(root)


# ── check ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_clean_row_passes(root):
    fetched(root); put(root, ROW)
    loaded, fails, warns = check_ledger(root)
    assert fails == [] and warns == [] and len(loaded) == 1


def keys(root):
    return {k for k, _, _ in check_ledger(root)[1]}


def _set(path, value):
    def f(r):
        d = r
        for k in path[:-1]:
            d = d[k]
        if value is KeyError:
            d.pop(path[-1])
        else:
            d[path[-1]] = value
    return f


PLANTS = [
    ("row_invalid", _set(["driver", "driver_direction"], "causes")),
    ("citation_without_doi_or_url", _set(["citation", "doi"], None)),
    ("citation_not_in_manifest", _set(["citation", "doi"], "10.9999/elsewhere")),
    ("quote_too_long", _set(["sentence_pointer"], '"' + " ".join(["word"] * 26) + '"')),
    ("pointer_too_long", _set(["sentence_pointer"], " ".join(["loc"] * 41))),
    ("quote_not_in_text", _set(["sentence_pointer"], 'abstract: "reef water cools rapidly"')),
    ("reviewer_is_extractor", lambda r: r.update(tier="reviewed", reviewed_by="agent_proteus")),
    ("validated_needs_two_reviewers", lambda r: r.update(tier="validated", reviewed_by="agent_other")),
    ("tested_incomplete", _set(["realisation"], {"result": "supported"})),
]


@pytest.mark.parametrize("key, plant", PLANTS, ids=[k for k, _ in PLANTS])
def test_each_failure_key_fires(root, key, plant):
    fetched(root)
    r = copy.deepcopy(ROW); plant(r); put(root, r)
    assert key in keys(root)


def test_doi_null_passes_the_schema_but_not_the_check(root):
    """The schema's named nearest miss (README known limit 18): `doi: null`, no URL."""
    fetched(root)
    r = copy.deepcopy(ROW); r["citation"]["doi"] = None; put(root, r)
    assert keys(root) == {"citation_without_doi_or_url"}


def test_file_and_directory_must_match(root):
    fetched(root)
    put(root, ROW, name="atl_hyp_coral_reef_other_001.yaml")
    assert keys(root) == {"id_file_mismatch"}
    (root / "ledger" / "coral_reef" / "atl_hyp_coral_reef_other_001.yaml").unlink()
    put(root, ROW, eco="estuary")
    assert keys(root) == {"ecosystem_dir_mismatch"}     # the manifest is the row's ecosystem's, which exists


def test_no_manifest(root):
    put(root, ROW)   # rows before any corpus was fetched
    assert keys(root) == {"no_manifest"}


def test_duplicate_id(root):
    fetched(root)
    put(root, ROW); put(root, ROW, name="x.yaml")
    assert "duplicate_hyp_id" in keys(root)


def test_unreadable_row(root):
    fetched(root)
    (root / "ledger" / "coral_reef" / "atl_hyp_coral_reef_x_001.yaml").write_text("- a list\n")
    assert "row_unreadable" in keys(root)


def test_warnings_not_failures(root):
    fetched(root)
    r = copy.deepcopy(ROW); r["sentence_pointer"] = "Discussion, paragraph 3"; put(root, r)       # a locator only
    r2 = copy.deepcopy(ROW); r2["hyp_id"] = "atl_hyp_coral_reef_wind_002"
    (root / "corpus" / "coral_reef" / "unreviewed" / "W111.txt").unlink()                          # a fresh clone
    put(root, r2)
    _, fails, warns = check_ledger(root)
    assert fails == [] and {k for k, _, _ in warns} == {"locator_only", "quote_unverified"}


def test_quote_matching_folds_quotes_dashes_case_and_space():
    assert set(quotes('abstract: “Reef  water  WARMS rapidly” and "calm"')) == {"Reef  water  WARMS rapidly", "calm"}
    assert quotes("abstract: 'reef water warms' in MHWs' frequency") == ["reef water warms"]   # an apostrophe is not a quote


def test_quote_folding_in_the_check(root):
    fetched(root)
    r = copy.deepcopy(ROW); r["sentence_pointer"] = "abstract: “Reef  water\nWARMS rapidly”"; put(root, r)
    assert keys(root) == set()


def test_quote_folding_covers_unicode_hyphens(root):
    """M-3b-i finding: real abstracts carry U+2010 HYPHEN; an ASCII quotation of them must match, and a word change must not."""
    fetched(root)
    recache(root, "W111", "Low wind speeds reduce mixing, and reef\u2010flat water warms\u00a0rapidly.")
    r = copy.deepcopy(ROW); r["sentence_pointer"] = 'abstract: "reef-flat water warms rapidly"'; put(root, r)
    assert keys(root) == set()
    r["sentence_pointer"] = 'abstract: "reef-flat water cools rapidly"'; put(root, r)
    assert keys(root) == {"quote_not_in_text"}


def test_agency_url_citation(root):
    fetched(root)
    r = copy.deepcopy(ROW); r["citation"] = {"url": "https://example.org/crw/method", "title": "CRW method", "year": 2014,
                                            "citation_source": "agency"}
    r["evidence_class"] = "agency_report"; r["sentence_pointer"] = "§3 Methods"; put(root, r)
    assert keys(root) == set()


# ── index ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_index_writes_then_checks(root, capsys):
    fetched(root); put(root, ROW)
    assert write_or_check(root, check=True) == 1           # missing
    assert write_or_check(root, check=False) == 0
    assert write_or_check(root, check=True) == 0
    md = (root / "LEDGER.md").read_text()
    assert "GENERATED — never hand-edit" in md and "`atl_hyp_coral_reef_wind_001`" in md and "wind_speed → 0 weeks" in md
    stamp_review(root / "ledger" / "coral_reef" / f"{ROW['hyp_id']}.yaml", "agent_reader")
    assert write_or_check(root, check=True) == 1           # stale


def test_index_refuses_a_failing_row(root):
    fetched(root)
    r = copy.deepcopy(ROW); r["citation"]["doi"] = "10.9999/elsewhere"; put(root, r)
    with pytest.raises(LedgerError, match="citation_not_in_manifest"):
        render(root)
    assert write_or_check(root, check=False) == 1 and not (root / "LEDGER.md").exists()


def test_cell_refuses_markdown_injection():
    assert _cell("a | b") == "a \\| b"
    with pytest.raises(LedgerError):
        _cell("line\n| injected |")


def test_cli_flags(root, capsys):
    assert hyp_main(["--check", "--root", str(root)]) == 1
    assert hyp_main(["corpus", "--index", "--root", str(root), "--ecosystem", "coral_reef"]) == 1


# ── III M-3b-i hardening (F-2, F-3, F-8, F-9, F-12): each new key planted ─────────────────────────────────────────
def test_cache_tampered(root):
    """F-2a: a fabricated sentence appended to the cache and quoted used to pass. The cache must hash to the manifest."""
    fetched(root)
    t = root / "corpus" / "coral_reef" / "unreviewed" / "W111.txt"
    t.write_text(t.read_text().rstrip("\n") + " Wind has no effect on reef heat.\n")
    r = copy.deepcopy(ROW); r["sentence_pointer"] = 'abstract: "Wind has no effect on reef heat"'; put(root, r)
    assert "cache_tampered" in keys(root)


@pytest.mark.parametrize("ptr, key", [
    ("abstract: '" + " ".join(["word"] * 26) + "'", "quote_too_long"),     # F-2b: single quotes no longer bypass
    ("abstract: ‘reef water cools rapidly’", "quote_not_in_text"),
    ("just some words with no locator or quote", "pointer_unparsed"),
])
def test_every_quote_glyph_is_a_quotation(root, ptr, key):
    fetched(root)
    r = copy.deepcopy(ROW); r["sentence_pointer"] = ptr; put(root, r)
    assert key in keys(root)


def test_quote_after_negation(root):
    """F-3 plant P8: a fragment that follows the paper's 'not' and omits it."""
    fetched(root)
    recache(root, "W111", "Low wind does not cause reef water to warm rapidly during calm periods.")
    r = copy.deepcopy(ROW); r["sentence_pointer"] = 'abstract: "cause reef water to warm rapidly"'; put(root, r)
    assert keys(root) == {"quote_after_negation"}
    r["sentence_pointer"] = 'abstract: "does not cause reef water to warm rapidly"'; put(root, r)
    assert keys(root) == set()


def test_quote_must_match_at_word_boundaries(root):
    fetched(root)
    r = copy.deepcopy(ROW); r["sentence_pointer"] = 'abstract: "eef water warms rapidly"'; put(root, r)   # mid-word start
    assert keys(root) == {"quote_not_in_text"}


def test_verbatim_overflow_row_and_work(root):
    """F-9 plant P7: an abstract pasted into `mechanism`; and copying spread across two rows citing one work."""
    long = " ".join(f"w{i}" for i in range(60))
    fetched(root); recache(root, "W111", long)
    r = copy.deepcopy(ROW); r["sentence_pointer"] = 'abstract: "w0 w1 w2 w3"'; r["mechanism"] = long; put(root, r)
    assert "verbatim_overflow" in keys(root)
    r["mechanism"] = " ".join(f"w{i}" for i in range(0, 15)); put(root, r)
    r2 = copy.deepcopy(r); r2["hyp_id"] = "atl_hyp_coral_reef_wind_002"; r2["mechanism"] = " ".join(f"w{i}" for i in range(20, 35)); put(root, r2)
    assert keys(root) == {"verbatim_overflow"}          # 15 + 15 words of one work, each row under the cap


def test_reviewed_is_bound_to_its_content(root):
    fetched(root); put(root, ROW)
    f = root / "ledger" / "coral_reef" / f"{ROW['hyp_id']}.yaml"
    r = copy.deepcopy(ROW); r.update(tier="reviewed", reviewed_by="agent_reader"); put(root, r)
    assert keys(root) == {"reviewed_unbound"}
    stamp_review(f, "agent_reader")
    assert keys(root) == set()
    r = yaml.safe_load(f.read_text()); r["mechanism"] = "Calm periods always heat reef water."; put(root, r)
    assert keys(root) == {"reviewed_content_changed"}
    r = yaml.safe_load(f.read_text()); r["mechanism"] = ROW["mechanism"]; r["realisation"] = {
        "result": "not_supported", "realised_in": "X.aDNA", "realised_vital": "atl_vital_wind", "tested_at": "2026-10-12", "write_up": "m.md"}
    put(root, r)
    assert keys(root) == set()                          # filling the realisation does not void the review
    with pytest.raises(ValueError):
        stamp_review(f, " AGENT_Proteus ")


def test_reviewer_is_extractor_casefolded(root):
    fetched(root)
    r = copy.deepcopy(ROW); r.update(tier="reviewed", reviewed_by="Agent_Proteus "); r["reviewed_sha256"] = review_hash(r); put(root, r)
    assert "reviewer_is_extractor" in keys(root)


@pytest.mark.parametrize("rel", ["coral_reef/atl_hyp_coral_reef_wind_001.yml", "coral_reef/deeper/atl_hyp_coral_reef_wind_001.yaml"])
def test_row_misplaced(root, rel):
    fetched(root)
    p = root / "ledger" / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump({**ROW, "tier": "validated"}))
    assert keys(root) == {"row_misplaced"}


def test_intake_fails_closed(root):
    """F-8: an outage must not replace the record; a socket guard must not be swallowed."""
    down = Fake([("api.openalex.org", lambda p: p.get("search") == "wind reef", R(code=503))] + session().routes)
    with pytest.raises(LedgerError, match="nothing written"):
        C.fetch_corpus("coral_reef", root, session=down, now="2026-10-12T00:00:00Z")
    assert not (root / "corpus" / "coral_reef" / "manifest.yaml").exists()
    m = C.fetch_corpus("coral_reef", root, session=down, now="2026-10-12T00:00:00Z", allow_partial=True)
    assert m["partial"] is True and m["queries"][0]["error"]

    class Guard:
        def get(self, *a, **k):
            raise AssertionError("a socket was opened")
    with pytest.raises(AssertionError):
        C.fetch_corpus("coral_reef", root, session=Guard(), refresh=True, now="2026-10-12T00:00:00Z")


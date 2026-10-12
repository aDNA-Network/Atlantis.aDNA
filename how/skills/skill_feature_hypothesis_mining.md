---
type: skill
skill_type: agent
created: 2026-10-12
updated: 2026-10-12
status: draft
category: knowledge
trigger: "A steward (or the campaign) needs the literature's claims about what drives their event, as rows a model can test — 'what does the literature say drives <event> in <ecosystem>', 'mine the papers', after stream discovery; P3 M-3b; P4's outside steward"
last_edited_by: agent_proteus
mission: mission_m3b_i_ledger_and_skill
tags: [skill, atlantis, hypotheses, literature_mining, ledger, openalex, europe_pmc, envo, t8, so3, tidewatch]

requirements:
  tools: ["Bash", "WebSearch", "WebFetch", "Agent", "AskUserQuestion"]
  context: ["Atlantis.aDNA/CLAUDE.md", "what/hypotheses/README.md", "what/context/playbook_data_and_literature_mining.md", "what/schema/atl_v0/README.md"]
  permissions: ["write what/hypotheses/{corpus,ledger}/<ecosystem>/ and LEDGER.md only", "public search requests (OpenAlex; Europe PMC by DOI) — no key, no e-mail sent", "NO abstract text committed (unreviewed/ is gitignored)", "NO instance write (realisation is a separate mission)"]
---

# Skill: feature-hypothesis mining

## Overview

This skill turns a region's literature into **rows a model can test**, not prose. Its question, for one ecosystem type
and one event: **what does the literature claim drives the event — at what lag, in which direction, past what threshold —
and what vital would realise each claim?** It is playbook §C as steps. It ends in:
- `what/hypotheses/corpus/<ecosystem>/manifest.yaml` — the retrieval record (committed, metadata only);
- `what/hypotheses/ledger/<ecosystem>/*.yaml` — the rows (`AtlHypothesis`, atl_v0 0.9.0);
- `what/hypotheses/LEDGER.md` — generated, every row checked;
- a **realisation hand-off memo** that ranks the rows for the steward's (or operator's) ruling on which to test.

**A row is a hypothesis, not a fact** (README rule 2). The model tests the literature: a driver the papers insist on that
carries no SHAP is a finding worth writing up; so is one that does (T8). This skill never tests anything — realisation
is the next mission's, in an instance.

Proteus asks first: *what is the patient, what is the event, and how much warning would change what you do?* Mining that
starts from "what is known about coral reefs" finds reviews. Mining that starts from the event finds the drivers that
could see it coming, at the lag that would change a decision.

## Trigger

```
/skill_feature_hypothesis_mining ecosystem=coral_reef event=degree_heating_week instance=<path>
```

## Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ecosystem` | `EcosystemType` | yes | `coral_reef` · `estuary` · `neritic_pelagic` (ENVO-bound; a new type is a schema change with its looked-up term). The ledger's directory and join key (README rule 5) |
| `event` | string | yes | The event variable as the instance names it (`degree_heating_week`) |
| `instance` | path | no | The instance whose streams decide what is realisable now (step 4). Read-only |

## Requirements

- `A=<Atlantis.aDNA>/what/atlantis_core`, synced; `python -m atlantis_core.hypotheses` (core ≥ 0.9.0).
- No credentials. OpenAlex is asked without a key and **without `mailto`** (no operator e-mail is sent to any service).
  OpenAlex reports a nominal `cost_usd` per request in its `meta`; the manifest records it per query.
- **Intake is standalone** until `Ingest.aDNA` has a literature class (today its documents class is "planned"). When it
  does, step 2 composes it instead (README rule 6) and this skill changes, not the rows.

## Steps

### 1. Interview (five questions, before any search)

1. **The patient and the event** — copied from the instance (`events.yaml`): what crosses, which way, over what horizon.
2. **The decision lag** — how much warning changes what the steward does. A driver whose lag is shorter than the lead
   time the steward needs is still a row, but its `realisable_as` says it cannot buy that lead.
3. **The streams the instance already has** (`streams.yaml`) — a row realisable from them costs a vital, not a fetcher.
4. **The streams discovery recorded but did not add** (`<instance>/discovery/discovery_memo.md`) — the next streams.
5. **What is not a driver here** — e.g. on FKNMS, DHW *is* the event; "SST anomaly drives DHW" is arithmetic, not a
   hypothesis. Rows restate the event's own definition only when a paper tests it as a predictor at a lag.

### 2. Corpus

Write `corpus/<ecosystem>/queries.yaml` — the recipe, committed:

```yaml
per_query: 25                     # OpenAlex relevance-ranked; 1…200
queries:
  - {id: q_wind, theme: wind, search: "coral bleaching low wind doldrums sea surface temperature", filter: "publication_year:>1985"}
agency:                           # reports no index finds well (CRW methodology, NOAA tech memos) — by hand
  - {doi: "10.3390/rs12233856", title: "…", year: 2020, note: "why it is here"}
```

Themes are **mechanisms × region**, regional first (the instance's own reefs, then its basin, then pantropical). Then:

```
$A/.venv/bin/python -m atlantis_core.hypotheses corpus --ecosystem <eco>      # → manifest.yaml + unreviewed/ (gitignored)
```

It refuses to replace a manifest without `--refresh` (a manifest is a retrieval record; OpenAlex's ranking moves).
Read the manifest's counts: how many works carry an abstract, and from where. Publisher-withheld abstracts (Springer,
Elsevier) come back `source: none`.

### 3. Extract: paper → row

Read the cached abstracts (`unreviewed/<openalex_id>.txt`) — and, for a key paper with a withheld abstract, its
open-access text if the manifest's work has one — and write **one row per mechanism per paper** to
`ledger/<eco>/atl_hyp_<eco>_<driver>_<nnn>.yaml` (shape: `what/hypotheses/README.md` §A row).

- **No pointer, no row.** `sentence_pointer` quotes the sentence the row rests on — `abstract: "<≤ 25 words, verbatim>"`
  — or, when the claim is not in the abstract, a locator (`Results ¶2`, `Fig. 4`). A quotation is checked verbatim
  against the cached text; a locator cannot be, and the check says so.
- **The paper's claim in the paper's terms** (`mechanism`): do not strengthen it. "Associated with" stays associated;
  **keep every hedge** ("suggest", "hypothesize", "may", "can", "contributed to", "appear to be associated"). The run of
  record stripped hedges from 9 of 32 mechanisms while their quotations kept them, so `--check` passed and the rows
  overstated their papers. Only the faithfulness reader caught it (M-3b-i).
- **Quote the finding, not the framing.** An abstract's opening background sentence restates others' work; a row resting
  on it is a `review`-class claim at most. Quote the sentence that carries *this* paper's result.
- **Lag and direction as stated.** If inferred, `lag_note: "inferred: <how>"`; if none, `lag_value: 0` with
  `"not stated — concurrent"`. For a trend or a multidecadal claim, say so in the note ("a trend, not a lagged driver"):
  "concurrent" means nothing there. A lag the paper states in the *other* direction (the index lags the region) means
  the index is not a driver of it, so write no row.
- **Paraphrase; do not copy.** Only `sentence_pointer` quotes. `check` fails a row that copies over 25 words of its
  abstract in runs of ≥ 6 across its fields, or rows that together copy over 25 words of one abstract outside their
  quotations (`verbatim_overflow`; III M-3b-i F-9).
- **No sign, no row.** "Consistent with", "bears a relationship", "related to" and "decreased or increased" give no
  sign. A **paired** statement does give one: "X and Y relate to A and B, respectively" pairs X with A (III M-3b-i F-7
  asked for this reading to be written down). A sign the paper does not give is `nonmonotone` only if the paper says so ("moderate beats low and extreme" is
  a hump: `nonmonotone`). Otherwise the row is not written. The run of record broke this on four rows; the reader caught
  them, and they were withdrawn.
- **Two rows are a contradiction only if their events match.** Cyclone *power* raising bleaching *severity* does not
  contradict cool wakes lowering *DHW*.
- **Evidence class** is what the cited work did, not what it cites. A review that restates a mechanism is `review`.
- **Region** is where the paper looked. A pantropical claim is a candidate for the Keys (README rule 5), not a Keys
  finding.
- **Agents author, the ledger records:** `recorded_by: agent_<persona>`, `tier: draft`, `hypothesis_source: literature`,
  `realisation: {result: untested}`.

### 4. Translate: the `realisable_as` column

For every row, set the closed `realisability` class (`existing_stream` · `declared_fetcher` · `new_stream` ·
`unrealisable` — `LEDGER.md` counts them, so T8 is counted by code, not by hand) and say in `realisable_as` what vital
would realise it, in stream-class terms — `buoy wind speed (NDBC C-MAN) · weekly mean ·
lag 1–2 weeks` — or `unrealisable: <why>` (a driver no public stream observes at the patient's scale; a lag longer than
the record; a mechanism that is the event's own definition; an effect the instance's stream cannot carry, such as a
reef-minus-offshore difference read from a 5 km field). A **window** is not a **lag**: "8 of the 14 preceding days" is
lag 0 over a 2-week window. **This column is T8's falsifier made visible:** a ledger
whose rows no fetcher can realise has failed T8 as worded, and the count says so before anyone trains.

### 5. Check and index

```
$A/.venv/bin/python -m atlantis_core.hypotheses --index            # check every row, then write LEDGER.md
$A/.venv/bin/python -m atlantis_core.hypotheses --index --check    # writes nothing; exit 1 on a stale ledger or any failure
```

| Failure key | What it catches |
|---|---|
| `row_invalid` | the closed `AtlHypothesis` rejects the row (committed JSON Schema, format checker on) |
| `id_file_mismatch` · `ecosystem_dir_mismatch` · `duplicate_hyp_id` | the file is not `<hyp_id>.yaml` under its `ecosystem_type` |
| `citation_without_doi_or_url` · `citation_not_in_manifest` · `no_manifest` | the cited work is not in the retrieval record |
| `quote_too_long` · `pointer_too_long` | a quotation over 25 words; a pointer over 40 |
| `quote_not_in_text` | a quotation not verbatim in the cached abstract (whitespace, quotes, dashes, case folded) |
| `cache_tampered` | the cached abstract does not hash to the manifest — the text a quote is checked against must be the text retrieved |
| `pointer_unparsed` · `quote_after_negation` | a pointer that is neither a quotation (any quote glyph) nor a locator; a fragment that drops the paper's "not" |
| `verbatim_overflow` | more than 25 copied words of one abstract (above) |
| `reviewer_is_extractor` · `reviewed_unbound` · `reviewed_content_changed` · `validated_needs_two_reviewers` | a review is a second reader, bound to what it read; `validated` waits for a second-reviewer slot |
| `row_misplaced` | a row file that is not `ledger/<eco>/<hyp_id>.yaml` |
| `tested_incomplete` | a result other than `untested` without realised_in · realised_vital · tested_at · write_up |

Warnings, never failures: `quote_unverified` (no cached text — a fresh clone, or a withheld abstract) and
`locator_only`. The hand-off counts them.

### 6. Review: draft → reviewed

A **fresh-context reader** (an `Agent` that did not extract, briefed to be adversarial) re-reads each row against its cached text and answers, per
row: is the mechanism the paper's claim, not a stronger one? are lag, direction and evidence class as the text gives
them? does the quotation say what the row says? It returns a verdict per row; only rows it confirms are promoted, with
`python -m atlantis_core.hypotheses --stamp-review <hyp_id> --reviewer <id>`. That writes `reviewed_sha256`, a hash of
the paper-facing fields the reader judged: a later edit to them fails `reviewed_content_changed`; filling `realisation`
or re-translating `realisable_as` does not. The reader also **flags** (never confirms) a `realisable_as` or a lag
encoding that misreads the paper, and applies step 3's rules to **every** row alike, mechanically where it can (grep the
trigger phrases). Promotion sets —
`tier: reviewed`, `reviewed_by: <the reader's id>`. A row it questions stays `draft` with the question recorded in the
hand-off. A corrected row stays `draft`: the extractor's correction is not a second reading. A row the text cannot carry
is **withdrawn**, never deleted (SO-2): it moves to `what/hypotheses/withdrawn/<eco>/` with a `withdrawn: {by, on, why}`
block, outside the checked ledger. `validated` (two readers) is not attempted until the schema has a second-reviewer slot.

### 7. Hand off: the realisation memo

Write `what/hypotheses/realisation_<eco>_<date>.md`: the rows ranked by **literature strength** (evidence class, how many
independent rows assert it, regional or not) × **realisability** (existing stream · a declared-but-unbuilt fetcher · no
stream) × **build cost** (a vital · a fetcher · a new instance). Name, for the top candidates, the vital, the stream, the
lag in the instance's time step, the comparison it would be read in (the instance's current board entry, at the same
base rate and budget — C-031, C-034), and whether it is a lever, a proxy or state (T7: a driver nobody owns is a proxy,
and "no lever, still" is an honest outcome). **The pick is the steward's or the operator's** — ask with
`AskUserQuestion`; never choose it.

## Outputs

`what/hypotheses/`: `corpus/<eco>/{queries,manifest}.yaml` (committed) · `corpus/<eco>/unreviewed/` (gitignored) ·
`ledger/<eco>/*.yaml` · `LEDGER.md` · `realisation_<eco>_<date>.md`. Commit with path-scoped `git add`; `git status`
before every add, so no `unreviewed/` file is ever staged.

## Known limits

- **The search is the agent's.** The manifest records what was asked and what came back, not what was missed; a thin
  theme shows as a query with few kept works.
- **Abstract-level extraction.** The verbatim check reads abstracts. A claim that lives only in a paper's results is
  recorded with a locator and stays unverified by code; the reviewer reads what the cache holds.
- **Withheld abstracts.** Springer and Elsevier withhold abstracts from OpenAlex, Semantic Scholar and Crossref; Europe
  PMC serves the life-science subset. Key papers in those journals often enter as locator rows.
- **OpenAlex ranking moves.** A manifest is a retrieval record, not a reproducible query result; `result_sha256` pins
  what this retrieval returned.
- **One reviewer.** `reviewed` is one second reader, not consensus.
- **Budget.** The faithfulness reader is its own lane: about 130 kT for 32 rows at M-3b-i. A card carries a line for
  it beside main and the III reviewer (III M-3b-i F-10).
- **Upstream truncation.** OpenAlex's reconstructed abstracts can lose a span that held markup-like text (one
  coral_reef abstract reads "breeze winds (5 weeks"). The intake cannot repair it. A quotation outside the gap still
  verifies; one across it fails, as it should.

## Run of record

M-3b-i (2026-10-12): `coral_reef`, for FloridaKeysCoral's DHW ≥ 4 onset. 32 rows extracted; the reader confirmed 15,
questioned 17. 6 were withdrawn and 11 corrected (still draft). The III review demoted one more (14 reviewed of 26)
and hardened `check`. Reef-light wind was ruled for M-3b-ii. Findings:
`how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_i_ledger_and_skill.md`.

---
type: directory_index
doc_id: atl_hypotheses_readme
title: "what/hypotheses/ — the hypothesis ledger (literature → testable feature hypotheses with provenance) — SPEC, rows at P3"
status: draft
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
precedent: "RareGraph.aDNA design intent (a shared disease-mechanism graph); RareArchive context files (tiered expert knowledge)"
composes: Ingest.aDNA (discover → fetch → redact → gate → publish) when a corpus exists
tags: [hypotheses, literature_mining, knowledge_graph, ledger, atlantis, p3, spec]
---

# The hypothesis ledger

The **MPA knowledge graph**, in Atlantis's terms: not a graph of observations (those stay in instances) but a graph of
**what the literature claims drives an event** — mechanism · driver · lag · direction · threshold · ecosystem type ·
evidence class · citation — each row pointing at a sentence, each row realisable as an `AtlVital` candidate, and
each realised row *tested* by the model. A feature the papers insist on that carries no SHAP is a finding worth
writing up; so is one that does. This is playbook §C made into a registry.

**Status: specification.** No rows exist. P3 M-3b populates it for one instance and builds
`skill_feature_hypothesis_mining.md`. This README fixes the extraction target so the lane produces a table, not prose.

## A row

`what/hypotheses/ledger/<ecosystem_type>/<hyp_id>.yaml` — one hypothesis per file (greppable, diffable, memo-able):

```yaml
hyp_id: atl_hyp_<ecosystem>_<driver>_<nnn>
tier: draft                        # draft → reviewed → validated (RareArchive ladder; "published" = it is in this public repo)
ecosystem_type: "<ENVO term when bound; free text until then: coastal_hab | coral_reef | estuary | river_metagenome>"
event_variable: "<WoRMS:… | CF:… | DHW>"
mechanism: "<one sentence, the paper's claim in the paper's terms>"
driver:
  variable: "<CF name / taxon / index>"
  authority: "<CF:… | WoRMS:… | producer>"
  lag: {value: <n>, unit: <days|weeks|months>, note: "<as stated or inferred>"}
  direction: positive | negative | nonmonotone | threshold
  threshold: {value: <n>, unit: "<UCUM>"}        # optional
region_asserted: "<where the paper looked>"
evidence_class: observational | experimental | model | review | agency_report
citation: {doi: "<doi>", title: "<…>", year: <n>, source: openalex | semantic_scholar | europe_pmc | agency}
sentence_pointer: "<section/paragraph or quoted ≤ 25 words>"
hypothesis_source: literature        # literature | steward_expert | model_finding (a SHAP surprise promoted to a hypothesis)
realisation:                         # filled when an instance turns the row into a vital
  instance: ""
  vital_id: ""
  stream_id: ""
  tested_at: ""
  result: untested | supported | not_supported | inconclusive
  shap_mean_abs: null
  write_up: ""                       # memo or board-entry pointer, either way
recorded_by: agent_<persona>
recorded_at: YYYY-MM-DD
```

## Rules

1. **Every row points at a sentence.** No pointer, no row.
2. **A row is a hypothesis, not a fact.** `tier: validated` means two reviewers agree the extraction is faithful to
   the paper — not that the mechanism is true. Truth is the instance's SHAP and the write-up's job.
3. **Realisation closes the loop both ways.** `result: not_supported` rows are kept and written up (T8).
4. **No private data in a row.** A steward-expert hypothesis (`hypothesis_source: steward_expert`) carries the
   steward's consent to be named or is attributed to the instance.
5. **Ecosystem type is the join key** across instances: a coral DHW driver asserted in Palau is a candidate vital in
   the Keys; the ledger is how P2's FKNMS instance inherits P3's reading.
6. **Intake composes `Ingest.aDNA`** when a corpus exists (OpenAlex / Semantic Scholar / Europe PMC / agency
   bulletins): discover → fetch → redact → gate → publish, with `unreviewed/` as a path, not a flag.

## Index (regenerated at P3)

| hyp_id | ecosystem | event | driver → lag | tier | realised in | result |
|---|---|---|---|---|---|---|
| *(none yet)* | | | | | | |

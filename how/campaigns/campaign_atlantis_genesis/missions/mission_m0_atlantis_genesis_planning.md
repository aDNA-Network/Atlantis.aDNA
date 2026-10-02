---
type: mission
mission_id: M-0
plan_id: mission_m0_atlantis_genesis_planning
title: "M-0 — Atlantis genesis planning (identity · persona · category · instance contract v0 · roster)"
owner: stanley
status: completed
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P0
mission_class: planning
executor_tier: fable
token_budget_estimated: "70-110kT"
token_budget_actual: "~180kT (expanded remit; four rulings, 6 commits)"
executor_tier_actual: fable
depends_on: []
session: session_stanley_20261002_124712_m0_genesis_expanded
created: 2026-09-23
updated: 2026-10-02
home_vault: Atlantis.aDNA
artifacts:
  - who/governance/adr_000_project_identity.md            # proposed (lineage amendment 2026-10-02) → ratified at the gate
  - who/governance/adr_001_persona_and_category.md          # Proteus (Nereus alt.) · Framework + reference implementation · what/atlantis_core/
  - who/governance/adr_002_remit_mpa_knowledge_system.md    # the widening (added at M-0; not in the seed card)
  - how/campaigns/campaign_atlantis_genesis/artifacts/thesis_register.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/mission_roster_p1_p5.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/p2_second_instance_ruling.md
  - what/schema/atl_v0/{README.md, atl_ontology_v0.linkml.yaml, crosswalk_external_vocabularies_v0.yaml}   # added at M-0
  - what/board/{README.md, entries/2026-09-23_gulf_karenia_brevis_v0.json}                                   # added at M-0
  - how/templates/{template_model_card.md, template_dataset_pair/}                                           # added at M-0
  - what/hypotheses/README.md                                                                                 # added at M-0
  - how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md                                    # re-chartered
tags: [mission, m0, genesis, planning, fable, atlantis]
---

# M-0 — genesis planning

## Intent

Turn the seed into a ratified identity and a buildable roster. Everything the seed marks *proposed* is ruled
here; nothing else is built here.

## Inputs (read in this order)

1. `CLAUDE.md` · `STATE.md` § ⏭ QUEUED.
2. The charter (this campaign's ladder and exit bars).
3. `what/context/concept_atlantis.md` (thesis + §6 open questions) · `what/patterns/pattern_ecosystem_early_warning.md`.
4. `what/exemplars/gulf_karenia_brevis/README.md` — the ground truth for what "done" looks like.
5. Fleet precedent for a Framework with a reference platform: `Git.aDNA` (framework + `Lighthouse.aDNA` deployable) and
   `Harness.aDNA` (platform with a clinical vertical) — read their CLAUDE.md identity sections only.

## Work

1. **Rulings to surface** (AskUserQuestion or an ISS gate via `aDNA.aDNA/how/skills/skill_create_iss.md`):
   persona (Proteus / Nereus / other) · category (Framework + reference platform / Platform / Forge) · name-form
   (`Atlantis`, capitalised — ADR-009 §3 exception, fleet precedent) · P2 second-instance pick.
2. **Author ADR-000** (identity, lineage from aDNALabs S329, the three-layer naming, SO-3 not-data-bearing) and
   **ADR-001** (persona + category), both `proposed` with an empty 4-field block for the operator.
3. **Thesis register:** the claims in `concept_atlantis.md` as numbered, falsifiable statements with the
   exemplar evidence for each and the P-phase that tests the rest.
4. **Instance contract v0:** the checklist an instance must satisfy to federate (patient definition · event +
   horizon · streams + fetchers · data-posture ruling · `federation_ref` · self-test green · required page
   sections incl. Limitations) and what Atlantis promises back.
5. **Roster P1–P5:** mission cards with `executor_tier` + `token_budget_estimated`, dependencies as a column.
6. **AAR** (Worked / Didn't / Finding / Change / Follow-up) · SITREP · move the session file to history.

## Exit

The charter's P0 exit bar, verbatim. **Then stop.** P1 opens only on the operator's GO.

## Completion (2026-10-02)

**Session:** `how/sessions/history/2026-10/session_stanley_20261002_124712_m0_genesis_expanded.md` · tier fable ·
operator-opened. **Rulings taken** (`AskUserQuestion`, 2026-10-01): widening accepted · Framework + reference
implementation with code at `what/atlantis_core/` · P2 = FKNMS coral bleaching · stop at the P0 gate. **Carried to
the gate:** persona (Proteus / Nereus), the three ADR signatures, GO P1.

**Scope change vs the seed card:** the remit widened (ADR-002), so M-0 also produced the `atl_v0` draft, the evidence
board, the registry templates and the hypothesis-ledger spec — *specs and templates, no code*, per the sitting-depth
ruling. ADR-001 was renumbered against nothing (the `what/decisions/adr_001–003` files are template boilerplate; ADRs
live in `who/governance/`).

## AAR

- **Worked:** reading RareArchive / ASOAtlas / Organization / Ray *before* designing — every layer reused a fleet shape (LinkML + controls, conformance-by-mapping, GREEN board, dataset pair, Rule-5 provenance) instead of inventing one; generating the board entry and thesis numbers **by script from `metrics.json`** caught README drift the seed had carried.
- **Didn't:** first LinkML draft failed lint on 22 unquoted flow-mapping descriptions (commas inside `{description: …}`); a 15-class ontology sketch had to be cut to 5 by the instance/independence/lifecycle tests.
- **Finding:** "MPA" is a change of *patient unit kind* and *audience*, not of identity — one enum value and a polygon grid path, plus the contract's wording; the seed's "reference *platform*" contradicted the Git.aDNA precedent and is now "reference *implementation*".
- **Change:** every mission card now carries `aar_path` and an acceptance checklist whose items name a command or a file; phase gates stay uncarded and fable.
- **Follow-up:** P1 M-1a + M-1c on GO · backlog memos (`idea_type_vocabulary_tier3_ocean_types`, `idea_cosign_datasets_provenance_contract`) · WI: ADR-062 still `proposed` upstream.

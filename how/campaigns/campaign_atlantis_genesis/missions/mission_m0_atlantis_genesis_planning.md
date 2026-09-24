---
type: mission
mission_id: M-0
plan_id: mission_m0_atlantis_genesis_planning
title: "M-0 — Atlantis genesis planning (identity · persona · category · instance contract v0 · roster)"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P0
mission_class: planning
executor_tier: fable
token_budget_estimated: "70-110kT"
depends_on: []
session: TBD
created: 2026-09-23
updated: 2026-09-23
home_vault: Atlantis.aDNA
artifacts:
  - who/governance/adr_000_project_identity.md            # proposed → ratified (4-field block)
  - who/governance/adr_001_persona_and_category.md          # Proteus / Framework + reference platform, or the alternative ruled
  - how/campaigns/campaign_atlantis_genesis/artifacts/thesis_register.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/mission_roster_p1_p5.md
  - how/campaigns/campaign_atlantis_genesis/artifacts/p2_second_instance_ruling.md
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

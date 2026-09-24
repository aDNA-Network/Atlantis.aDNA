---
campaign_id: campaign_atlantis_genesis
type: campaign
title: "Operation Tidewatch — Atlantis genesis: from one exemplar to a drop-in method for ocean-ecosystem early warning"
display_name: "Operation Tidewatch"
owner: stanley
persona: proteus            # PROPOSED
status: planning
phase: P0
phase_count: 6
mission_count: 1            # M-0 carded; P1–P5 rosters are M-0's output
estimated_sessions: "10-18"
calibrated_sessions: "8-14"
estimation_class: content-novel
executor_tier: mixed        # FABLE = M-0 + every phase exit + adversarial passes · OPUS = briefed build lanes
priority: medium
home_vault: Atlantis.aDNA
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [campaign, atlantis, tidewatch, genesis, early_warning, oceans]
---

# Campaign: Operation Tidewatch

> **Codename discipline:** `grep -ril "Operation Tidewatch" ~/aDNA` → 0 hits at seed time (2026-09-23).

## Goal

When this campaign is complete, **a marine steward anywhere can clone `Atlantis.aDNA`, run one skill, answer a
handful of questions (what is the patient, what is the event, how much warning changes what you do, what streams
do you have), and be left with a regional instance graph that fetches its data, builds leakage-proof vitals,
trains and evaluates a calibrated onset model at an alert budget, explains it with tagged SHAP, renders an
explainer page, and knows how to mine its own literature for the next round of vitals** — without editing
Atlantis, and without Atlantis ever holding their data.

## Context

Seeded from aDNALabs S329 (2026-09-23): a one-sitting pilot built a complete *Karenia brevis* bloom-onset
early-warning system on public data to explain the sepsis-analog method to a metagenomics colleague. The pilot
worked (test AUROC 0.89, AUPRC 0.55 vs 7.7% prevalence, 64% of onsets flagged, median lead 4 weeks) and, more
usefully, produced two method findings (stop on log-loss; ablate surveillance) and a discovery playbook. The
operator ruled it the first exemplar of a new graph rather than a pilot in the org HQ. Thesis:
`what/context/concept_atlantis.md`. Method: `what/patterns/pattern_ecosystem_early_warning.md`.

## Scope

### In scope
- Identity, persona, category and the **instance contract** (P0).
- Extracting the exemplar into templates + a fork skill so instantiation is one sitting (P1).
- A second instance on a different system, proving drop-in (P2).
- The literature/data mining lane producing feature hypotheses with provenance (P3).
- Federation wrapper contract, Exchange listing, first outside steward (P4).
- Steady-state cadence and retraining loop (P5).

### Out of scope
- Operational forecasting or any claim to it (agencies' business; an instance's owner may rule otherwise, in writing).
- Causal inference; the what-if stays a sensitivity.
- Holding any regional, partner or human-subject data in Atlantis (SO-3).
- Building a data commons (`Exchange.aDNA`) or an intake engine (`Ingest.aDNA`) — compose them.

## Phases & missions

### P0 — Genesis planning (fable; operator-opened)

| Mission | Title | Tier | Sessions | Depends | Status |
|---|---|---|---|---|---|
| M-0 | Genesis planning: identity ADR-000, persona, category, name-form, thesis register, **instance contract v0**, P1–P5 roster | fable | 1 | — | planned |

**Exit bar (written):** ADR-000 carries the operator's 4-field ratification block · persona and category ruled ·
instance contract v0 exists as a checklist a stranger could satisfy · P1–P5 missions carded with tiers and
budgets · the P2 second-instance pick is named. **Operator GO in person or by ISS gate.**

### P1 — Method canonisation (opus lanes, fable review)

Extract from the exemplar: `how/templates/template_regional_instance/` (config schema with comments; fetcher
skeletons for ArcGIS / ERDDAP / NWIS / NDBC / sequence archives; `build_features` with the self-test kept
generic; `train` / `explain` / `whatif` / `export` / `build_site` unchanged; the site template with all copy
parameterised) + `how/skills/skill_atlantis_instance_fork.md` (the interview → instance).
**Exit bar:** a fresh instance forks from templates alone, in one sitting, and its self-test is green before
any real data is fetched. III review of the templates via wrapper.

### P2 — Second instance (opus build, fable gate)

Candidates, ruled at M-0: *Karlodinium veneficum* / Chesapeake (estuarine, different agency stack) · coral
bleaching by degree-heating-weeks (gridded-only vitals, no point samples) · a freshwater metagenomic site where
vitals are taxon abundances per cruise (the colleague's world; the hardest translation).
**Exit bar:** trained + explained + paged **without editing Atlantis code**; every deviation becomes a P1 template
change, not an instance hack.

### P3 — Mining lane (opus lanes)

The literature → feature-hypothesis table (playbook §C) on one instance; compose `Ingest.aDNA` if a corpus
exists. **Exit bar:** one instance's vitals extended from mined sources with provenance, and at least one
literature-asserted driver *tested* by SHAP and written up either way.

### P4 — Federation & stewards

`how/federation/atlantis/` contract finalised (what an instance carries, what Atlantis promises), Exchange
listing, first outside steward instantiates with the skill and reports. **Exit bar:** an instance built by
someone who was not in this campaign, from the public repo alone.

### P5 — Steady state

Retraining cadence, drift checks, AAR. **Exit bar:** campaign AAR; Atlantis joins the fleet's steady-state
baseline; successor cards filed.

## Gates that shape everything

- **SO-1:** every phase exit is a human gate; no auto-advance.
- **SO-3:** Atlantis never becomes data-bearing; the moment a lane needs regional data it moves to an instance.
- **Public repo:** everything committed here is publishable; the commit is the publication (Git.aDNA ADR-013).

## Risks

Template drift from the exemplar (mitigation: P2 forbids instance hacks) · ERDDAP/NWIS flakiness (cache, retry,
offline mode already in the exemplar) · surveillance endogeneity in every monitoring dataset (ablation is a
required output) · over-claiming (SO-4; the Limitations section is a required page section) · the mining lane
producing prose instead of a table (the extraction target is fixed in playbook §C).

## Status

P0 queued. M-0 not yet opened. Seeded 2026-09-23 by Berthier (aDNALabs S329).

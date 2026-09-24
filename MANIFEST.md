---
type: manifest
project: Atlantis.aDNA
display_name: "Atlantis"
codename: "Operation Tidewatch"
genesis_stage: genesis_planning
pattern_category: framework   # + reference platform (PROPOSED; ruled at M-0)
persona: proteus              # PROPOSED
owner: stanley
visibility: public            # aDNA-Network/Atlantis.aDNA, MIT
data_bearing: false           # instances are; Atlantis is not
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [manifest, atlantis, framework, oceans, ecosystem_early_warning, genesis_stub]
---

# MANIFEST — Atlantis.aDNA

## Project Identity

| Field | Value |
|---|---|
| Display name | Atlantis |
| One line | Precision medicine for oceans — a drop-in agentic method + toolkit for region-specific ecosystem early-warning models (multi-modal observations → vitals → calibrated onset model → SHAP → intervention tagging) |
| Category | Framework + reference platform *(proposed)* |
| Persona | Proteus *(proposed)*; Berthier interim |
| Operator | Stanley (Founding Architect, sole governance principal) |
| Codename | Operation Tidewatch (genesis campaign) |
| Lineage | Spun out of `aDNALabs.aDNA` S329 (2026-09-23), the *Karenia brevis* pilot `hab_crash_risk` → `what/exemplars/gulf_karenia_brevis/` |
| Data posture | Not data-bearing. Exemplar uses public FWC / NOAA / USGS data only. |
| Remote | `github.com/aDNA-Network/Atlantis.aDNA` — public, MIT |

## Genesis status

Stub. P0 queued; M-0 (fable) rules identity, persona, category, instance contract v0 and the mission roster.
See `STATE.md`.

## Architecture (who / what / how)

| Leg | Holds |
|---|---|
| `who/` | governance (Stanley-only; ADR-000 proposed) · coordination (name-form note; future steward memos) |
| `what/` | `context/` thesis + mining playbook · `patterns/` the 8-step method · `exemplars/` the reference implementation · `datasets/` public snapshots + notes |
| `how/` | `campaigns/campaign_atlantis_genesis/` · `federation/atlantis/` wrapper contract · `sessions/` · (P1) `templates/template_regional_instance/` + `skills/skill_atlantis_instance_fork.md` |

---
type: mission
mission_id: M-1c
plan_id: mission_m1c_linkml_controls
title: "M-1c — `atl_v0` controls — fixtures, `run_controls.sh`, committed JSON Schema, vocabulary fit matrix"
owner: stanley
status: in_progress
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: verification
executor_tier: opus
token_budget_estimated: "60-90kT"
token_budget_actual: ""
depends_on: ['M-0']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1c_linkml_controls.md
session: session_stanley_20261002_162046_m1c_linkml_controls
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1c, p1, opus, atlantis, tidewatch]
---

# M-1c — `atl_v0` controls — fixtures, `run_controls.sh`, committed JSON Schema, vocabulary fit matrix

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P1 — Core canonisation ·
**Tier:** opus · **Budget:** 60-90kT · **Depends on:** M-0

## Objective

Convert the draft ontology's intentions into enforced constraints under the ASOAtlas discipline: every claimed constraint is proven by a control that fails on exactly the thing it names, under both validators.

## Acceptance criteria

- [ ] `what/schema/atl_v0/fixtures/controls/{pos,neg}_*.yaml` — ≥ 1 positive per class; negatives with `# REJECTS_ON:` (and `# REJECTS_AT:` where a path is meaningful) for: lever without owner · operational claim without ruling · missing base_rate · missing limitations_ref · bad id prefix · sha256 not hex64 · inline geometry literal · unknown enum value
- [ ] `run_controls.sh` (ASOAtlas/Ray precedent; `LINKML_BIN` scratch venv) — three worlds: linkml-validate · committed JSON (descendants OFF) · scratch JSON (descendants ON); a stale committed JSON fails the run
- [ ] `atl_ontology_v0.schema.json` committed and equal to a fresh `gen-json-schema --closed`
- [ ] `m1c_vocabulary_fit_matrix.md`: every enum value × crosswalk authority; `Modality` re-examined against GOOS EOV; `local` rows carry reasons
- [ ] Every constraint docstring names what its control proves and the nearest miss it does not catch; README `validation:` updated and the NO-VALIDATION-CLAIM banner replaced by the control count
- [ ] Known limits named (referential integrity · uniqueness · cross-object equality are a validator's job)
- [ ] III review via wrapper (`iii/`, adopted in this mission if absent)

## Guardrails

- **SO-1:** this mission opens only after the previous phase's operator GO; it never advances the phase itself.
- **SO-3 / ADR-002 §4:** no new data snapshots in Atlantis; instance data stays in the instance; credentials by name only.
- **SO-7:** any change to vitals or label re-runs the self-test before commit.
- **SO-4:** nothing produced here is an operational forecast; `claim: method_demonstration` unless an owner ruling is cited.
- Public repo: everything committed is publishable; path-scoped `git add`; `gitleaks` on push.
- Peer vaults read-only; cross-graph needs go as coordination memos.

## Verification surface

The acceptance checklist above, each item checked by a command or a file the AAR names; the self-test output;
`linkml-validate` on every registry touched; the board entry diffed against `outputs/metrics.json` by script.

## Escalation triggers

- A deviation that would require editing `atlantis_core` from inside an instance (P2) → stop, file the template change, do not patch locally.
- A stream whose licence or posture is unclear → stop, memo to the instance owner; nothing fetched.
- Budget exceeded by > 50% → SITREP and stop; re-card.
- Anything that would put observations, labels, predictions or partner coordinates into Atlantis → stop.

## Files

- `what/schema/atl_v0/{fixtures/controls/* (incl. run_controls.sh), atl_ontology_v0.schema.json, m1c_vocabulary_fit_matrix.md, README.md}`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

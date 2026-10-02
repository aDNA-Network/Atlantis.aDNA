---
type: mission
mission_id: M-1d
plan_id: mission_m1d_fork_skill_and_registries
title: "M-1d — `skill_atlantis_instance_fork` + pipeline lattice + dataset-pair migration + contribution guide + BOARD generator"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: integration
executor_tier: opus
token_budget_estimated: "80-120kT"
token_budget_actual: ""
depends_on: ['M-1b', 'M-1c']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1d_fork_skill_and_registries.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1d, p1, opus, atlantis, tidewatch]
---

# M-1d — `skill_atlantis_instance_fork` + pipeline lattice + dataset-pair migration + contribution guide + BOARD generator

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P1 — Core canonisation ·
**Tier:** opus · **Budget:** 80-120kT · **Depends on:** M-1b, M-1c

## Objective

Make instantiation one sitting: an interview-driven skill that forks a conformant instance from templates alone, with its self-test green before any real data is fetched — and close the registry loose ends the public repo needs.

## Acceptance criteria

- [ ] `how/skills/skill_atlantis_instance_fork.md` — interview (what is the patient · what is the event · how much warning changes what you do · what streams exist · data posture class) → `<Instance>.aDNA` via `skill_project_fork` + `how/federation/atlantis/CLAUDE.md` (contract v0 block) + registries + `mapping.yaml` + posture ADR stub; runs the all-stream self-test on synthetic data **before** any fetch
- [ ] `how/lattices/lattice_atlantis_pipeline.lattice.yaml` (`lattice_type: pipeline`; validated by `aDNA.aDNA/what/lattices/tools/lattice_validate.py`): discover → fetch → grid → vitals → self-test → label → train → eval → explain → board → site; plus a closed-vocabulary **runspec** JSON convention (DDX precedent)
- [ ] `what/datasets/` migrated to the pair standard (`.md` + `.dataset.yaml`) with sha256 pins; the two ad-hoc notes superseded in place
- [ ] `who/governance/contribution_guide.md` — public-repo contribution: what crosses (patterns · registry rows · hypotheses · board metrics) and never crosses; memo-to-inbox flow; DCO; tiers draft→reviewed→validated
- [ ] `what/board/BOARD.md` generated from `entries/` by `atlantis_core.board` (never hand-edited from here)
- [ ] **Dry run:** a throwaway instance forked in the scratchpad from templates alone passes contract checklist items 1–8 and 11–12 without network; recorded in the AAR
- [ ] P1 exit bar met; fable review requested

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

- `how/skills/skill_atlantis_instance_fork.md · how/lattices/lattice_atlantis_pipeline.lattice.yaml · what/datasets/dataset_*.{md,dataset.yaml} · who/governance/contribution_guide.md · what/board/BOARD.md`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

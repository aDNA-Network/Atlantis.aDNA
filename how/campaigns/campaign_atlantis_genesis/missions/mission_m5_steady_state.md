---
type: mission
mission_id: M-5
plan_id: mission_m5_steady_state
title: "M-5 — Retrain + drift skill, Ray workload request template, campaign AAR"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P5
campaign_phase: 5
mission_class: closeout
executor_tier: opus
token_budget_estimated: "50-80kT"
token_budget_actual: ""
depends_on: ['M-4']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m5_steady_state.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m5, p5, opus, atlantis, tidewatch]
---

# M-5 — Retrain + drift skill, Ray workload request template, campaign AAR

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P5 — Steady state ·
**Tier:** opus · **Budget:** 50-80kT · **Depends on:** M-4

## Objective

Give instances a cadence and give the campaign its after-action review.

## Acceptance criteria

- [ ] `how/skills/skill_retrain_and_drift.md`: re-fetch → sha256 drift check vs pins → self-test → retrain → eval → board entry v(n+1) → calibration-slope and base-rate drift reported; `superseded_by` on the old entry
- [ ] `how/templates/template_ray_workload_request.md` (Ray.aDNA `RayWorkloadRequest`: hashes and ids only; `data_class` from the instance's posture) for L2 retraining; one dry-run request recorded, **no job submitted without operator GO on that run-spec** (Scheduler ADR-004 posture)
- [ ] Campaign AAR in the charter (Worked / Didn't / Finding / Change / Follow-up) · successor cards filed · STATE → steady-state baseline
- [ ] Thesis register final cut; every T has a status

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

- `how/skills/skill_retrain_and_drift.md · how/templates/template_ray_workload_request.md · campaign_atlantis_genesis.md §AAR · STATE.md`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

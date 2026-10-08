---
type: mission
mission_id: M-3a
plan_id: mission_m3a_stream_discovery_skill
title: "M-3a — `skill_stream_discovery` — playbook §A as a runnable skill with the traps as checks"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "≈ 140 kT main + fresh-context III reviewer ≈ 150 kT (re-carded at the P2 gate 2026-10-08: 40-60kT × 2.3, the observed ratio, III G-10)"
token_budget_actual: ""
depends_on: ['M-1d']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3a_stream_discovery_skill.md
session: TBD
created: 2026-10-02
updated: 2026-10-08
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3a, p3, opus, atlantis, tidewatch]
---

# M-3a — `skill_stream_discovery` — playbook §A as a runnable skill with the traps as checks

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P3 — Knowledge lane ·
**Tier:** opus · **Budget:** ≈ 140 kT + reviewer (re-carded at the P2 gate) · **Depends on:** M-1d · *Was to run beside M-2 and slipped; it runs first in P3, and may run beside M-2c because they share no files.*

## Objective

Turn the data-discovery arc (portals → ERDDAP → gauges → buoys → bio/sequence archives) into a skill that ends in a populated `streams.yaml` with provenance, and encodes every trap in playbook §B as an assertion.

## Acceptance criteria

- [ ] `how/skills/skill_stream_discovery.md`: inputs = patient geometry pointer + event variable + ecosystem type; steps per playbook §A; outputs = `streams.yaml` rows (AtlObservationStream) + a discovery memo
- [ ] Traps as checks: server count asserted · longitude distribution per unit · probe-before-believing-a-zero · samples-per-year before `min_train_year` · negative tidal flow clipped and noted · surveillance channel declared
- [ ] Run once on the FKNMS instance and once on the exemplar; both `streams.yaml` validate against `atl_v0`
- [ ] Playbook §A/§B re-pointed to the skill (playbook stays the narrative)
- [ ] *(P2 gate, C-033)* Before the AAR, re-read the register for any obligation it gives M-3a or P3. Each one is carried, dropped or recorded, never silently lost
- [ ] On the exemplar, discovery writes **pointer rows only** (SO-3, ADR-002 §4): no fetch, and no new bytes in Atlantis
- [ ] III review via `iii/` in a fresh context; SITREP at the +50% line

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

- `how/skills/skill_stream_discovery.md · what/context/playbook_data_and_literature_mining.md`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

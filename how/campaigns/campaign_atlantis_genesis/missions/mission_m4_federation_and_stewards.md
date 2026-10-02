---
type: mission
mission_id: M-4
plan_id: mission_m4_federation_and_stewards
title: "M-4 — Instance contract v1, steward governance set, consumer register, Exchange listing, first outside steward"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P4
campaign_phase: 4
mission_class: integration
executor_tier: fable
token_budget_estimated: "90-140kT"
token_budget_actual: ""
depends_on: ['M-2', 'M-3b']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m4_federation_and_stewards.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m4, p4, fable, atlantis, tidewatch]
---

# M-4 — Instance contract v1, steward governance set, consumer register, Exchange listing, first outside steward

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P4 — Federation & stewards ·
**Tier:** fable · **Budget:** 90-140kT · **Depends on:** M-2, M-3b

## Objective

Ratify the contract against a stranger: an instance built by someone who was not in this campaign, from the public repo alone, lands a board entry — and the governance a second steward needs exists before they arrive.

## Acceptance criteria

- [ ] `instance_contract_v1.md` ratified (4-field block) — consent wording for the instance register · trust bands (Operations ADR-026 probationary / trusted / anchor) · partner-posture board entries ruled · blind-conductor runbook **only if** a partner-data instance exists
- [ ] `who/governance/{steward_council,decision_authority,partner_engagement}.md` (RareArchive shape, adapted; council seats real, not theatre) · `who/coordination/inbox/` live
- [ ] `what/artifacts/template_atlantis_consumer_wrapper.md` + `atlantis_consumer_register.md` (who federates, pinned at which commit)
- [ ] `Exchange.aDNA` listing for Atlantis (Registry); instance graphs list on their own terms
- [ ] `Network.aDNA` share-class ruling for instance graphs recorded (default `private`, dial-out-only)
- [ ] **First outside steward** instantiates with `skill_atlantis_instance_fork` from `github.com/aDNA-Network/Atlantis.aDNA` alone and reports (memo + board entry); their friction list becomes P1-style template changes
- [ ] Thesis T6 T10 re-cut; fable gate: P4 exit

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

- `how/campaigns/.../artifacts/instance_contract_v1.md · who/governance/*.md · what/artifacts/*.md · how/federation/atlantis/README.md`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

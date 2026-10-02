---
type: mission
mission_id: M-2
plan_id: mission_m2_fknms_coral_instance
title: "M-2 — First MPA instance — `FloridaKeysCoral.aDNA`: FKNMS zones × week, degree-heating-weeks onset, gridded-only vitals, no Atlantis code edits"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "150-220kT"
token_budget_actual: ""
depends_on: ['M-1d']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2_fknms_coral_instance.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2, p2, opus, atlantis, tidewatch]
---

# M-2 — First MPA instance — `FloridaKeysCoral.aDNA`: FKNMS zones × week, degree-heating-weeks onset, gridded-only vitals, no Atlantis code edits

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P2 — First MPA instance ·
**Tier:** opus · **Budget:** 150-220kT · **Depends on:** M-1d

## Objective

Prove drop-in on the hardest translation the exemplar never faced — polygon patients, gridded-only vitals, a persistent event, no surveillance channel — by forking an MPA instance with the skill and taking it to a board entry **without editing `atlantis_core`**.

## Acceptance criteria

- [ ] `FloridaKeysCoral.aDNA` forked by `skill_atlantis_instance_fork` (public posture — NOAA CRW 5 km + OISST are public; posture ADR says so); router row via Hestia memo
- [ ] Patient: FKNMS management zones (`unit_kind: mpa_zone`, WDPA:2347 parent; zone geometry from the sanctuary's public shapefile as a **pointer**) × ISO week; grid built by the **polygon** path
- [ ] Event: DHW ≥ threshold (ruled in-instance from CRW bleaching-alert levels) within 4–8 weeks; `direction: above`; onset rule handles multi-week persistence (T3 hardest case); second threshold as sensitivity (T12)
- [ ] Streams: CRW DHW/HotSpot/SST (gridded, `authority` = NOAA CRW until a CF name exists), OISST, optionally NDBC buoys; `surveillance_channel: false` with the reason — **the ablation requirement is then declared N/A, not skipped**
- [ ] Self-test green before fetch; trained · evaluated at budgets · lead time · climatology · explained · tagged (levers: likely none — say so; proxies dominate) · paged with Limitations · board entry landed in Atlantis by memo
- [ ] **Every deviation needed became a P1 template change** (list in AAR), zero instance-local patches to `atlantis_core`; thesis T1 T3 T9 T10 re-cut
- [ ] Fable gate: P2 exit

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

- `~/aDNA/FloridaKeysCoral.aDNA/** (new, instance) · Atlantis: what/board/entries/<date>_floridakeyscoral_v0.json · thesis_register.md re-cut · how/backlog/ for template changes`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

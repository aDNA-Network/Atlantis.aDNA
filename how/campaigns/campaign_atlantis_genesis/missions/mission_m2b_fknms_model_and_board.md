---
type: mission
mission_id: M-2b
plan_id: mission_m2b_fknms_model_and_board
title: "M-2b — FloridaKeysCoral.aDNA: train · evaluate (thresholds on validation) · explain · page · board entry by memo → P2 gate"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~150-200kT main + fresh-context III reviewer"
token_budget_actual: ""
depends_on: ['M-2a-ii']
split_from: mission_m2_fknms_coral_instance
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2b_fknms_model_and_board.md
session: TBD
created: 2026-10-03
updated: 2026-10-06
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2b, p2, opus, fknms, coral, mpa, eval, board, atlantis, tidewatch]
---

# M-2b — FloridaKeysCoral.aDNA, from data to a board entry

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P2 · **Tier:** opus. **Split from**
`mission_m2_fknms_coral_instance.md` (P1-exit gate ruling, 2026-10-03). **The P2 gate (fable, operator) follows this card.**

## Acceptance criteria

- [ ] `atlantis_core.run` in the instance: trained; evaluated at alert budgets with **thresholds fixed on validation**
      (M-1e) and realised rates reported; lead time; climatology baseline; explained; tagged. Levers are likely none: say so
- [ ] **A persistence/trend baseline beside `climatology_baseline`** (`eval/metrics.py`) — added 2026-10-06 at M-2a
      planning. DHW is both the event and a vital, and it accumulates, so DHW(t) plus HotSpot(t) nearly determine
      DHW(t+k). Without a "no model, just persistence" comparator, the headline AUROC overstates the model's value
      (SO-9). This is an Atlantis-side eval change, with a plant
- [ ] The instance's page, with Limitations (`atlantis_core.site`), lives **in the instance**. No instance page enters
      Atlantis (ADR-002 §4 A-1)
- [ ] Board entry via `board --entries <instance>/what/board/entries`: closed, GREEN, `claim: method_demonstration`.
      `conform` item 9 ✅. It travels by **coordination memo** to `Atlantis.aDNA/who/coordination/inbox/` and is landed
      by a dated commit in an operator-opened session (contribution guide 0.1.1); then `board --index`
- [ ] Thesis T1, T3, T9 and T10 re-cut in `artifacts/thesis_register.md`
- [ ] Zero instance-local patches to `atlantis_core`; every deviation is a P1 template change, listed in the AAR
- [ ] III review via `iii/`, fresh context; AAR; **request the P2 gate** (fable)

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

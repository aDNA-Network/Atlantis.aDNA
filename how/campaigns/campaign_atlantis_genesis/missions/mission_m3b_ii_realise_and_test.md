---
type: mission
mission_id: M-3b-ii
plan_id: mission_m3b_ii_realise_and_test
title: "M-3b-ii — one ledger row realised as an AtlVital in FKNMS, trained, SHAP-tested, written up either way · T7/T8 re-cut"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "≈ 180 kT main (+50% line ≈ 270 kT) + fresh-context III reviewer ≈ 150 kT; a fetcher build, if the ruling needs one, is inside this figure — re-card at open if it is not"
token_budget_actual: ""
depends_on: ['M-3b-i']
split_from: mission_m3b_hypothesis_ledger_and_mining
origin: "M-3b ruling 1 (operator, AskUserQuestion, 2026-10-12): two halves — ledger + skill / realise + SHAP"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_ii_realise_and_test.md
session: TBD
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_ii, p3, opus, shap, realisation, fknms, t7, t8, atlantis, tidewatch]
---

# M-3b-ii — realise one row and test it

**Split from** `mission_m3b_hypothesis_ledger_and_mining.md` (M-3b ruling 1). The other half is
`mission_m3b_i_ledger_and_skill.md`, which ends on the operator's ruling of which row this half realises.

## Acceptance criteria

- [ ] The ruled row realised as an `AtlVital` (`hypothesis_ref` set) in **FKNMS** (or a new instance), **never the
  exemplar** (P2-gate condition (c), SO-3). A new stream, if needed, is built Atlantis-side (P2 rule) and fetched into
  the instance under its posture
- [ ] Self-test re-run before commit (SO-7); trained; SHAP-tested; `realisation.result` filled
- [ ] Write-up as a memo + board entry — **supported or not, it is written** (T8)
- [ ] Every comparison with the FKNMS v3 entry at the same base rate and budget (C-031, C-034); no cross-base-rate AUPRC
  deltas
- [ ] Thesis T7 · T8 re-cut. On FKNMS, T7's honest outcome may be "no lever, still"; a driver that is a proxy is written
  up as one
- [ ] *(C-033)* register re-read before the AAR
- [ ] III review via `iii/` in a fresh context; SITREP at the +50% line

## Guardrails · Escalation

As the parent card.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

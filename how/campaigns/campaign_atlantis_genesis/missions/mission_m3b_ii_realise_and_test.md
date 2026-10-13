---
type: mission
mission_id: M-3b-ii
plan_id: mission_m3b_ii_realise_and_test
title: "M-3b-ii — one ledger row realised as an AtlVital in FKNMS, trained, SHAP-tested, written up either way · T7/T8 re-cut"
owner: stanley
status: split   # 2026-10-12, M-3b-ii ruling 1 (operator, AskUserQuestion, at open; C-042) → M-3b-ii-a + M-3b-ii-b; kept as the parent card
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

> **Split 2026-10-12** (M-3b-ii ruling 1, operator, `AskUserQuestion`, at open; C-042) →
> `mission_m3b_ii_a_ndbc_fetch.md` (`NDBCStdmet` + the calm-day grammar op, core 0.10.0 · the stream fetched into FKNMS ·
> conform at the fetched stage · III) and `mission_m3b_ii_b_realise_and_test.md` (the vitals · the val scan · the run ·
> SHAP · memo + board entry · T7/T8 · III). This card stays the parent: its acceptance criteria are the union of the two.
> Rulings 2–3 at the same open: the **station map is a Keys-wide synoptic index** (the mean over the reef lights reporting
> that day, given to all 21 zones; the reporting set recorded), and the **calm threshold is scanned on val** (c ∈ {2, 3,
> 4, 5, 6} m/s, chosen on val log-loss from the train fit; test scored once; the full scan a GREEN table).

**Split from** `mission_m3b_hypothesis_ledger_and_mining.md` (M-3b ruling 1). The other half is
`mission_m3b_i_ledger_and_skill.md`, which ends on the operator's ruling of which row this half realises.

## Ruled at the M-3b-i close (operator, `AskUserQuestion`, 2026-10-12)

**Realise reef-light wind.** The rows are wind_003★ (4 m/s, a Persian Gulf model of sea-bottom temperature) and
wind_006★ (heatwaves, one Brazilian season), with wind_001★, 005★, 004 and temperature_variability★ as response-side
context. The hand-off is `what/hypotheses/realisation_coral_reef_2026-10-12.md`. The question carried III F-6's
event-matched counts (wind 2, cyclones 1): more rows, farther away, at the highest cost.

**Opening obligations, carried from M-3b-i:**
1. Build `NDBCStdmet` in `atlantis_core` (WI-19; a template change, the P2 rule) for the C-MAN reef lights MLRF1 ·
   SMKF1 · LONF1 · SANF1. Re-card at open if the build does not fit.
2. A steward ruling on the station-to-zone map, and on the calm threshold: **scanned, not fixed at 4 m/s** (a regional
   transfer).
3. FKNMS's `mapping.yaml` pin → atl_v0 0.9.0, as federation upkeep (as at M-2c-ii).
4. The vital's `hypothesis_ref` names the row(s). Its tag is `proxy` (T7: "no lever, still").
5. Fill `realisation` on the realised rows. A filled realisation does not void their review (`reviewed_sha256`
   excludes it).
6. Card lines for main, the reader lane (if any) and the III reviewer at observed sizes (III M-3b-i F-10).

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

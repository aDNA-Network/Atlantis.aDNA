---
type: mission
mission_id: M-3b-ii-b
plan_id: mission_m3b_ii_b_realise_and_test
title: "M-3b-ii-b — reef-light wind realised as AtlVitals in FKNMS, the calm threshold scanned on val, trained, SHAP-tested, written up either way · T7/T8 re-cut"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "main ≈ 180 kT (+50% line ≈ 270 kT) · fresh-context III reviewer ≈ 200 kT (observed sizes, III M-3b-i F-10); a val-only scan path, if `run` lacks one, is inside this figure — re-card at open if it is not"
token_budget_actual: ""
depends_on: ['M-3b-ii-a']
split_from: mission_m3b_ii_realise_and_test
origin: "M-3b-ii ruling 1 (operator, AskUserQuestion, 2026-10-12, at open): build + fetch / realise + test"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_ii_b_realise_and_test.md
session: TBD
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_ii_b, p3, opus, shap, realisation, fknms, t7, t8, atlantis, tidewatch]
---

# M-3b-ii-b — realise reef-light wind and test it

**Split from** `mission_m3b_ii_realise_and_test.md` (M-3b-ii ruling 1). Starts from M-3b-ii-a's fetched, conformed
stream `atl_stream_fkc_wind_ndbc_daily` (Keys-wide index, ruling 2).

## Ruled at the M-3b-ii open (2026-10-12)

**Calm threshold (ruling 3, steward):** calm days = daily-mean wind < c, for c ∈ {2, 3, 4, 5, 6} m/s. c is picked on
**val (2014–18) log-loss from the train fit**; test is scored once, at the chosen c. The full scan is reported as a GREEN
table. The raw anemometer height is kept (C-MAN heights differ from the row's model) and recorded as a limit.

## Opening obligations (carried from M-3b-i and M-3b-ii-a)

1. Read `run.py`: if `run` cannot score val without scoring test, the val-only scan path is a core change (template, P2
   rule) — re-card at open if it does not fit.
2. Vitals, tag `proxy` (T7: "no lever, still"): weekly mean wind, lags 0 · 1 · 2 · 4 (`hypothesis_ref`
   wind_006) and calm days `weekly_count_lt(value, calm_threshold)`, lags 0 · 1 · 2 (`hypothesis_ref` wind_003).
3. Self-test re-run before the vitals commit (SO-7).
4. Fill `realisation` on the realised rows (wind_003, wind_006). A filled realisation does not void their review
   (`reviewed_sha256` excludes it).
5. Card lines for main and the III reviewer at observed sizes (III M-3b-i F-10).

## Acceptance criteria

- [ ] The ruled rows realised as `AtlVital`s (`hypothesis_ref` set) in **FKNMS**, never the exemplar (P2-gate (c), SO-3)
- [ ] The threshold scanned on val only; test scored once; the scan table GREEN
- [ ] Self-test re-run before commit (SO-7); trained; SHAP-tested; `realisation.result` filled
- [ ] Write-up as a memo + board entry — **supported or not, it is written** (T8)
- [ ] Every comparison with the FKNMS v3 entry at the same base rate (15.0%) and budgets (C-031, C-034); no
  cross-base-rate AUPRC deltas; the paired season-block interval reported
- [ ] Thesis T7 · T8 re-cut. On FKNMS, T7's honest outcome may be "no lever, still"; a driver that is a proxy is written
  up as one
- [ ] *(C-033)* register re-read before the AAR
- [ ] III review via `iii/` in a fresh context; SITREP at the +50% line (C-042); suite count with its commit (C-035)

## Guardrails · Escalation

As the parent card.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

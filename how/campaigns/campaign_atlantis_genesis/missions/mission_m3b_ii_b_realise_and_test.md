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
6. **QC mask and station offsets, ruled BEFORE any vital** (M-3b-ii-a III F-1, F-2, F-8; FKNMS `STATE.md` has the
   numbers). The stream carries flag columns, and no value was deleted:
   - `qc_low_ratio` marks LONF1 2020-02-27…06-04, a **failed anemometer** at 0.14–0.20 × the others (99 days, all in test);
   - `qc_stuck` marks 73 station-days of identical runs of ≥ 6 h.

   The index's reporting set shifts by segment: all four lights on 56.8% of train days, never in test, and two on 49.5%
   of test reporting days. SMKF1's offset against SANF1 moves ≈ −0.9 m/s across its 2016–17 gap, while LONF1's is stable.
   Cadence changes from hourly to 10-minute at `test_start`.

   Calm share at c = 4, % of reporting days, train / val / test: 23.8 / 27.7 / 29.4 unmasked, 23.7 / 27.6 / 27.3 masked.
   Rule which flags mask the index, and how station offsets are treated (fitted on train only). Run a SANF1-only
   sensitivity. Read any "support" against it: an era-confounded calm vital is a proxy for the decade, not for the wind.
7. **conform item 9 is outstanding by construction** until the run writes v4 under `81bca06518` (the newest entry, v3,
   is for `c07b7c0288`; core `5312f52`). The run is what closes it.
8. The site test that reads the live FKNMS now reads it as each entry saw it (`590f70b`); a new v4 page/entry test
   follows that pattern.

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

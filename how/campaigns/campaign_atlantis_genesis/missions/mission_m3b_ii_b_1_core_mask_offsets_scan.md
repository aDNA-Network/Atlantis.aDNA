---
type: mission
mission_id: M-3b-ii-b-1
plan_id: mission_m3b_ii_b_1_core_mask_offsets_scan
title: "M-3b-ii-b-1 — core 0.11.0: stream QC mask · era-fitted station offsets + station windows · a val-only scan path · the FKNMS declaration (no vitals)"
owner: stanley
status: active
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "main ≈ 200 kT (+50% line ≈ 300 kT) · fresh-context III reviewer ≈ 250 kT (observed sizes)"
token_budget_actual: ""
depends_on: ['M-3b-ii-a']
split_from: mission_m3b_ii_b_realise_and_test
origin: "M-3b-ii-b ruling 3 (operator, AskUserQuestion, 2026-10-15, at open): core / realise + test"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_ii_b_1_core.md
session: session_stanley_20261015_145556_m3b_ii_b_1_core
created: 2026-10-15
updated: 2026-10-15
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_ii_b_1, p3, opus, core, qc_mask, station_offsets, scan, fknms, atlantis, tidewatch]
---

# M-3b-ii-b-1 — the mask, the offsets and the scan path (core)

**Split from** `mission_m3b_ii_b_realise_and_test.md` (ruling 3). Rulings 1–2 (obligation 6) are recorded there.

## Scope

1. **`mask_columns`** (stream key): the declared flag columns reach the evaluator, and `value` becomes NaN where any flag
   is true, before any aggregation. A declared column absent from the artifact is refused by name. The self-test's
   synthetic frames carry the flags.
2. **`station_offsets: {reference, era, min_days}`**: each station's additive offset against the reference is the mean
   paired difference over era days on which both report. The mask is applied first. The offset is subtracted before the
   station → unit mean. A station short of `min_days` is refused by name. **R7 is extended**: an offset era ends before
   `val_start` and before the first rolling-origin test year. The self-test reports the era dependence as it does for a
   climatology (C6), and C1 holds outside every era.
3. **`station_windows: {station: [from, to]}`**: rows outside a station's window are dropped.
4. **`atlantis_core.scan`**: per value of one constant, it builds, labels, **drops the test years first**, and runs the
   `_fit_main` selection fit (train, stopped on val). It writes val log-loss and AUPRC at the val base rate as a GREEN
   table. It never refits on train ∪ val and never scores test. The early-stop optimism is disclosed in the output.
5. **FKNMS:** declare rulings 1–2 on the wind stream, bump the pin, and re-run the self-test (a new receipt hash: v4 is
   written under it, not `81bca06518`). Run `fetch --verify` and `conform --stage fetched`. Add a descriptive calm-share
   table to STATE: the ruled index vs SANF1-only, train / val / test. **No vitals.**

## Acceptance criteria

- [ ] Each new guard has a test, and each test is red with its guard planted off (plant-first)
- [ ] Hashes unchanged where the new keys are absent (exemplar, FKNMS before the declaration)
- [ ] The scan provably never reads test: test-year vitals poisoned → byte-equal output
- [ ] Full suite green, with the count recorded with its commit (C-035); core 0.11.0
- [ ] FKNMS self-test green under the declaration (SO-7), with the receipt and the era dependence reported
- [ ] The descriptive calm-share table (ruled index · SANF1-only) in FKNMS STATE, with the fitted offsets and n_days
- [ ] III via `iii/` in a fresh context, every finding dispositioned; token counter read at every commit; SITREP at
  the +50% line (C-042)
- [ ] AAR

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

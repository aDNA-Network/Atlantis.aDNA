---
type: mission
mission_id: M-2c-i
plan_id: mission_m2c_i_climatology_budget_and_interval
title: "M-2c-i — climatology at budget (thresholds fixed on validation) · a season-block paired interval · atl_v0 0.8.0 · core 0.7.0 · BOARD.md lead column realised · exemplar board v4"
owner: stanley
status: completed   # 2026-10-08: III PASS-WITH-FINDINGS 0/4/3/3, all addressed; AAR filed; M-2c-ii queued
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2→P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "≈ 350 kT main (the whole M-2c figure; the split is a sitting line, not a budget cut) + fresh-context III reviewer ≈ 200 kT"
token_budget_actual: "main ≈ 400 kT (estimated, ≈ +14%) · planning explorers ≈ 390 kT (not carded) · III reviewer 216 kT (metered, ≈ +8%)"
depends_on: ['M-2b', 'p2_gate']
split_from: mission_m2c_commensurable_board
origin: "M-2c ruling 1 (operator, AskUserQuestion, 2026-10-08): split on the card's own line"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2c_i_climatology_budget_and_interval.md
session: session_stanley_20261008_234650_m2c_i_commensurable_core
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2c_i, p2_gate_condition, opus, eval, climatology, interval, board, exemplar, atlantis, tidewatch]
---

# M-2c-i — climatology at budget and a season-block interval

**Split from** `mission_m2c_commensurable_board.md` (M-2c ruling 1). The other half is
`mission_m2c_ii_fknms_v3_and_swap.md`.

## Rulings of this sitting (AskUserQuestion, 2026-10-08)

1. **Split** along the card's line.
2. **The FKNMS `mapping.yaml` pin move to 0.8.0 is federation upkeep, not an instance patch.** It is done in M-2c-ii and
   counted on its own line.
3. **The calendar + signal comparator (G-12) is deferred.** It is named in the AAR.

## Facts it rests on

- **The exemplar's test window is 2020–2023, which is 4 season blocks.** FKNMS has 7 (2019–2025). The interval on the
  exemplar is very crude and says so.
- **Climatology has about 50 distinct scores**, so a val-fixed threshold takes in whole week-of-year tie groups. The
  realised rate is therefore load-bearing.
- **The existing `climatology_baseline_test` AUROC/AUPRC are pinned** by the hab port and the v2 reproduction. All new
  numbers are additive.

## Acceptance criteria

- [x] **Climatology at budget (eval).**
  - The selection fit is `embargo(train, val_start, E)`, scored on all of `val`; thresholds come from
    `fixed_thresholds(…, "val")`.
  - Those thresholds are applied to the existing refit's test scores through `at_alert_rates`, with a read-back check
    and a fit-years check.
  - AUROC/AUPRC are unchanged to the bit.
- [x] **Season-block paired interval** for model − climatology, on AUROC and AUPRC.
  - Whole test years are resampled, and both scores share the same index set.
  - It reports `n_blocks`, distinct multisets and degenerate draws, as summaries only.
  - The whole-block verifier runs on every draw.
- [x] **atl_v0 0.8.0.**
  - `climatology_alert_budgets` (list of `AtlAlertBudget`) and `paired_intervals` (list of the new `AtlPairedInterval`).
  - One positive control and the negatives; `run_controls.sh` reports ALL WORLDS AGREE.
  - README, the fit matrix and the template mapping pin are moved together.
- [x] **Emitter:**
  - `assert_climatology_at_budget` refuses a budget fixed on test, a realised rate that is not `n_alerts/n`, a selection
    fit into val, and slot ≠ result.
  - `assert_interval` refuses a unit other than season, `n_blocks` ≠ the test years, `lower > upper`, a `spans_zero`
    that disagrees with the bounds, and slot ≠ result.
- [x] **Plants C1–C4** are each caught by name:
  - C1: climatology thresholds taken from test;
  - C2: the selection fit not embargoed;
  - C3: a row resampler;
  - C4: an unpaired resample.
  - **Result plants** on the emitter are each refused.
- [x] **`BOARD.md`:**
  - The lead cell shows nominal · realised (G-7).
  - A "Climatology at the same budgets" section, with the interval and how to read it.
  - Regenerated, and `--check` passes.
- [x] **Exemplar board v4**, re-run at core 0.7.0:
  - v4 ≡ v3 on every v3 number, checked by a leaf-walk script, with every difference named;
  - the self-test passes;
  - emitted with `--vs` v3.
- [x] **One counting rule** for Atlantis changes, named in the AAR.
- [x] **Close:** III through `iii/` in a fresh context, then the AAR. SITREP at +50%.

## Outcome

All criteria met. After review, rulings 4–5 added budget deltas with a matched-volume reading, and season-years
from a declared start month. See the AAR. The suite was 742 passed on the tree of `1396ce2`, and the 78 controls report ALL WORLDS AGREE.

## AAR

This is required before `status: completed` (SO-6). It goes to `aar_path`.

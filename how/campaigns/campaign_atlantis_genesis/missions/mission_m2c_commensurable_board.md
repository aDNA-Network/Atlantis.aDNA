---
type: mission
mission_id: M-2c
plan_id: mission_m2c_commensurable_board
title: "M-2c — a commensurable board: climatology at budget · a season-block paired interval · the exemplar at 0.7.0 (v4) · FKNMS v3 by memo, with its learner swap"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2→P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~150 kT card top × 2.3 (observed ratio, P2 gate III G-10) ≈ 350 kT main + fresh-context III reviewer ≈ 200 kT"
token_budget_actual: null
depends_on: ['M-2b', 'p2_gate']
origin: "P2-gate condition (a), ruled 2026-10-08 (operator, AskUserQuestion; III review artifacts/p2_gate_iii_review.md G-3 · G-4 · G-7 · G-12)"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2c_commensurable_board.md
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2c, p2_gate_condition, opus, eval, climatology, board, exemplar, fknms, atlantis, tidewatch]
---

# M-2c — a commensurable board

**Campaign:** `../campaign_atlantis_genesis.md` · **Tier:** opus · **Origin:** the P2 gate's condition (a). It runs
**before M-3b**. M-3a may run beside it, since they share no files.

## Why

The P2 gate found that the board can show two instances side by side but cannot yet compare them:
- **T11's falsifier says "at the chosen budget".** That has never been measured on either instance; only threshold-free AUROC and AUPRC exist (G-3, C-034).
- **FKNMS's lead over its calendar has no uncertainty.** The lead is 0.937 vs 0.919 and 0.690 vs 0.601, and the effective sample is about 7 seasons.
- **The exemplar's live entry predates the 0.7.0 comparators.** It is v3, so T10 is comparable but not commensurable.
- **The re-card dropped T2's learner swap on the second instance (G-4, C-033).**

M-3b tests a literature driver by SHAP on an instance, and that reading needs all of this underneath it.

## Acceptance criteria

- [ ] **Climatology at budget (T11).** Climatology's score gets thresholds fixed on validation at the same nominal
      budgets as the model, using the same M-1e rule (`threshold_from: validation`, with the realised rate). Report
      precision and recall beside the model's.
      - New optional atl_v0 slot(s), 0.8.0, each with a positive and a negative control. `run_controls.sh` must report
        ALL WORLDS AGREE.
      - The emitter refuses a climatology budget whose threshold was fixed on test.
      - Plant: a climatology score that leaks test is refused.
- [ ] **A season-block paired interval** for model − climatology, on AUROC and AUPRC. Resample whole test seasons
      (years), never zone-weeks, and use the same resample for both scores.
      - State the number of blocks, and say plainly that with about 7 blocks the interval is crude.
      - Plant: a resampler that draws rows instead of seasons is caught.
      - Carry it on the board and say how to read it. An interval that spans 0 is reported as exactly that.
- [ ] *(optional, G-12)* A **calendar + signal** comparator: logistic on week-of-year plus the event signal. This is the
      cheap competitor most likely to close the gap. Include it if it fits the budget; otherwise defer it in the AAR.
- [ ] **The exemplar re-entered at 0.7.0 as board v4.** Its v4 outputs already exist and equal v3 on every v3 number.
      Re-run at this mission's core so the entry carries the new slots. Read v4 ≡ v3 again on every v3 number, or name
      each difference.
- [ ] **FKNMS re-run as v3** in the instance, at this core:
      - **T2's learner swap** (logistic on the same vitals), whose results land in `learner_swaps`;
      - the new slots;
      - the entry travels by **steward memo** and is landed by a dated commit (contribution guide 0.1.1).
      v2 stays on the board, superseded (SO-2).
- [ ] **`BOARD.md` lead column (G-7):** print the realised rate beside the nominal budget. Regenerate and run `--check`.
- [ ] **Register:**
      - T11 re-read **at its terms** on both instances;
      - T2's swap on the second instance recorded;
      - T10 re-read with two 0.7.0+ entries.
      Every number must come from `metrics.json` or an entry, never retyped. The roll-up may say no more than the rows (C-032).
- [ ] Zero instance-local patches. List every Atlantis change and count it under **one rule**: P2's ≈ 13–15 is P4's baseline.
- [ ] SO-7: when any vitals or label code moves, re-run the self-test on both the exemplar and FKNMS.
- [ ] III review through `iii/` in a fresh context, then the AAR. SITREP at the +50% line.

## Not in scope

- Any new stream or vital from the literature (that is M-3b).
- Any change to the split or to H.
- Making the instance public, which is the owner's ruling.
  - Until then, the board README's note on instance-relative refs stands (P2 gate ruling 3).

## Split line (if the planning sitting judges it too big for one sitting, SO-8)

- **M-2c-i:** core and schema, which covers the climatology-at-budget slot, the paired interval, the lead column and the exemplar v4.
- **M-2c-ii:** the FKNMS v3 memo, including the swap, plus the register re-read.

Splitting is the operator's call.

## AAR

Required before `status: completed` (SO-6) → `aar_path`.

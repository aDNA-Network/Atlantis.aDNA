---
type: mission
mission_id: M-2c-ii
plan_id: mission_m2c_ii_fknms_v3_and_swap
title: "M-2c-ii — FloridaKeysCoral.aDNA re-run as board v3 at core 0.7.0 (climatology at budget · paired interval · T2's learner swap) by steward memo · the register re-read (T2 · T10 · T11)"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2→P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "share of M-2c's ≈ 350 kT not spent by M-2c-i, + fresh-context III reviewer (≈ 150-200 kT)"
token_budget_actual: null
depends_on: ['M-2c-i']
split_from: mission_m2c_commensurable_board
origin: "M-2c ruling 1 (operator, AskUserQuestion, 2026-10-08)"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2c_ii_fknms_v3_and_swap.md
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2c_ii, p2_gate_condition, opus, fknms, learner_swap, board, register, atlantis, tidewatch]
---

# M-2c-ii — FKNMS v3 by memo, with T2's swap, then the register

**Split from** `mission_m2c_commensurable_board.md`. It opens after M-2c-i lands core 0.7.0 and atl_v0 0.8.0.

## Acceptance criteria

- [ ] **In `FloridaKeysCoral.aDNA` (steward hand, dated commits, before the run):**
  - Add a `learner_swaps:` block (logistic, same vitals, as the exemplar's). It is not in `semantic_hash`, so
    `c07b7c0288` should hold. Verify that.
  - Move the `mapping.yaml` ontology pin to 0.8.0. **Under M-2c ruling 2 this is federation upkeep, counted on its own
    line, not as an instance patch.**
  - Set `eval.interval_season_start_month` (M-2c ruling 5). January keeps calendar years, which suits a summer heat
    event; the steward rules, and the choice is disclosed.
  - Move the `federation_ref` pin to the M-2c-i commit.
  - Commit `atlantis.yaml` before the run; core 0.6.1+ refuses stale config bytes.
- [ ] **Run v3 at core 0.7.0**, including the swap. Then run `conform`.
- [ ] **Emit `…_florida_keys_coral_v3`** into the instance's `what/board/entries` with `--vs` v2.
- [ ] **The steward memo** goes to `who/coordination/inbox/` (contribution guide 0.1.1 §2a).
- [ ] **Atlantis re-checks and lands it** by a dated commit. v2 stays, superseded by derivation (SO-2).
- [ ] **SO-7:** re-run the self-test only if vitals or label code moved since M-2b.
- [ ] **Register**, every number taken from an entry or `metrics.json`, never retyped (C-032):
  - T11 re-read **at its terms** on both instances:
    - climatology precision and recall at each budget, with realised rates;
    - Δ precision and the **matched-volume** Δ precision with their intervals (ruling 4). This matters most on FKNMS,
      where the model realises 0.2034 at 0.10;
    - the threshold-free interval.
    Every level is **nominal** (C-036): read it beside the seasons favouring the model and the sign test. The exemplar has
    5 seasons (3 scorable alone); FKNMS has about 7.
  - T2's swap on the second instance.
  - T10 re-read with two 0.8.0 entries.
  - The roll-up says no more than the rows.
- [ ] **Count the Atlantis changes** under M-2c-i's rule. The pin move is on its own line.
- [ ] **Close:** III through `iii/` in a fresh context, then the AAR. SITREP at +50%.

## Not in scope

- Any new stream or vital (that is M-3b).
- Any change to the split or H.
- Making the instance public (the owner's ruling).
- The calendar + signal comparator (M-2c ruling 3).

## AAR

Required before `status: completed` (SO-6) → `aar_path`.

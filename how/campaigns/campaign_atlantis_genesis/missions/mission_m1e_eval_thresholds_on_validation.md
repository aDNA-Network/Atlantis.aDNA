---
type: mission
mission_id: M-1e
plan_id: mission_m1e_eval_thresholds_on_validation
title: "M-1e — alert thresholds and rolling-fold tree counts fixed on validation (F-8 / WI-11) → board v2 · P2 condition (a)"
owner: stanley
status: completed
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~110-160kT main + fresh-context III reviewer (build-sized) — set from P1's observed overruns (+77% to +130%), not from the backlog card's size"
token_budget_actual: "≈370kT main (plan-mode orientation included) + ≈260kT III reviewer — ≈+130% on the card; SITREP at +50%, operator ruled finish"
depends_on: ['M-1d-ii']
blocks: ['M-2a']
origin: how/backlog/idea_eval_thresholds_fixed_on_validation.md
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1e_eval_thresholds_on_validation.md
session: session_stanley_20261004_035631_m1e_thresholds_on_validation
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1e, p1, opus, eval, thresholds, so9, board_v2, p2_condition, atlantis, tidewatch]
---

# M-1e — thresholds fixed beforehand (F-8) → board v2

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 condition lane · **Tier:** opus. **Ruled at the P1-exit gate
(2026-10-03):** P2 is a **conditional GO**, and condition (a) is this lane. M-2a does not open until it closes.

## Objective

Fix the two after-the-fact choices III F-8 named (M-1b-ii-a) before any steward-facing budget claim (WI-11):
1. alert-budget and lead-time thresholds are quantiles of the **test** scores;
2. rolling folds testing 2017–2019 reuse a tree count early-stopped on 2017–2019.

Land the result as **board v2**, with the delta named and nothing else mixed in.

## Acceptance criteria

- [x] `eval.threshold_from: val | test` (default `val`). A threshold is fixed on validation scores (or the previous
      fold's) **before** test is scored. Every budget reports the **realised** test alert rate beside the nominal rate.
      Lead time reads the same fixed threshold
- [x] Rolling folds early-stop on their own inner validation year (or take a tree count fixed before the fold). No fold
      reuses a count stopped on its own test years
- [x] Port equivalence keeps a `test` mode, so `hab`'s v1 numbers still reproduce exactly (`tests/test_eval.py`)
- [x] Planted defects, each caught by name:
  - a threshold computed from test;
  - a fold stopped on its test year;
  - a realised rate missing beside a nominal one;
  - a control that passes by construction (C-009: plant the test-quantile threshold back and watch it fail)
- [x] **Board v2** emitted by code (`board --vs <v1>`), the delta attributed to F-8 alone. The closed `AtlEvaluation` is
      unchanged, or atl_v0 is amended with controls (ALL WORLDS AGREE). `limitations_ref` points at a limits section that
      names this fix (closes WI-14). `BOARD.md` regenerated: v1 shows superseded, derived
- [x] Any new exemplar page is a **new file** citing v2 (ADR-002 §4 A-1). The v0 and v1 pages and board v0/v1 stay
      byte-stable
- [x] SO-7 self-tests green (vitals and labels are untouched, so say so); full suite green; README §Known limits updated
- [x] III review via `iii/`, fresh context; AAR; WI-11 closed

## Inputs

STATE · `how/backlog/idea_eval_thresholds_fixed_on_validation.md` · the M-1b-ii-a AAR (F-8) · `what/atlantis_core/README.md`
§Known limits of eval and explain · board v1 · `what/board/README.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`. **Filed 2026-10-03:** all criteria met. Board v2 differs from v1 by F-8 alone (model bytes identical). III 8/8. The horizon spill (F-6) is disclosed, and its embargo carded (operator ruling).

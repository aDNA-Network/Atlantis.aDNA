---
type: mission
mission_id: M-1b-ii-a
plan_id: mission_m1b_ii_a_core_eval_explain_board
title: "M-1b-ii-a — `atlantis_core` eval · explain · board: learner as config, R7 refit-per-fold, board v1 (calendar SST lags), semantic hash, logistic learner swap"
owner: stanley
status: active
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~160kT main + fresh-context III reviewer (same size)"
token_budget_actual: ""
depends_on: ['M-1b-i']
split_from: mission_m1b_ii_core_eval_explain_board
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_ii_a_core_eval_explain_board.md
session: session_stanley_20261003_033855_m1b_ii_a_core_eval_explain_board
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1b_ii_a, p1, opus, atlantis_core, eval, explain, board, atlantis, tidewatch]
---

# M-1b-ii-a — `atlantis_core` eval · explain · board

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 · **Tier:** opus · **Split from:**
`mission_m1b_ii_core_eval_explain_board.md` (operator ruling 2026-10-02) · **Sibling:** `mission_m1b_ii_b_site_mapping_archive.md`.

## Objective

Training, evaluation, explanation and board emission move into `atlantis_core`. The port reproduces `metrics.json` on
`hab`'s own vitals. The exemplar re-run through the core (calendar-correct SST lags, R7 refit honoured) lands as board v1.
`src/hab/` stays canonical for the site until ii-b.

## Acceptance criteria

- [ ] `eval/`: split from config · alert budgets · lead time (direction-aware) · calibration · ablations from vital groups · surveillance-only · climatology baseline · rolling origin · sensitivity threshold via the label's event override. **The learner is a config field** (`xgboost` | `logistic`)
- [ ] **Port equivalence:** core eval on `hab`'s `features.parquet` reproduces `metrics.json` (n_trees 141 · test 0.8941 / 0.5473 · budgets · lead · climatology · surveillance-only · no-surveillance ablation · rolling folds) — asserted by test
- [ ] **R7 obligation:** eval refits every climatology era per rolling-origin fold (era clipped to ≤ train_through, affected vitals rebuilt); eval refuses to run with an unexecuted obligation; asserted by test. The exemplar's 2015→2016 fold is the one that changes
- [ ] `explain/`: interventional SHAP · additivity hard check · group/tag sums from `features.yaml` · what-if scenarios are config, applied to the raw stream and re-derived through `vitals.build`; refused on a stream with no `lever` vital
- [ ] `board/` emits the closed `AtlEvaluation` projection (validates against the committed JSON Schema) with the extras beside it — starts closing WI-8
- [ ] Core run on the exemplar → `outputs/atlantis_core/`; **board v1** entry with the delta vs v0 named (expected ≈0.8938 / 0.5388; same n, positives, drop counts); WI-10 noted; v0 untouched
- [ ] **Semantic hash** recorded beside the bytes-md5s (closes WI-7)
- [ ] **Logistic learner swap** on the core's vitals, recorded as T2 evidence against the falsifier (rolling spread 0.79–0.99) in the thesis register
- [ ] `config.yaml` / `outputs/metrics.json` byte-stable; SO-7 self-tests green; controls ALL WORLDS AGREE (42)
- [ ] III review via `iii/` in a fresh context (SO-10)

## Guardrails

As M-1b-i. Budget >50% over (≈240 kT) → SITREP and stop. No site work, no `src/hab/` archive (ii-b).

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

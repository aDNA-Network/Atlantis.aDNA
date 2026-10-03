---
type: session
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [session, m1b_ii_a, p1, atlantis_core, eval, explain, board, opus, atlantis, tidewatch]
session_id: session_stanley_20261003_033855_m1b_ii_a_core_eval_explain_board
user: stanley
started: 2026-10-03T03:38:55Z
status: completed
executor_tier: opus
token_budget_estimated: "~160kT main + fresh-context III reviewer (same size)"
token_budget_actual: "≈215kT main (≈ +35%, under the trip) + ≈205kT fresh-context III reviewer"
mission: mission_m1b_ii_a_core_eval_explain_board
campaign: campaign_atlantis_genesis
intent: "M-1b-ii-a: atlantis_core eval (learner as config, R7 refit-per-fold) · explain (SHAP + what-if as config) · board (closed AtlEvaluation projection) · core run → board v1 (calendar SST lags, semantic hash) · logistic learner swap (T2). Site · mapping · src/hab archive → ii-b. config.yaml + outputs/metrics.json byte-stable."
files_modified: "[STATE.md, CHANGELOG.md, campaign charter, roster, thesis_register, missions/{m1b_ii (superseded), m1d (deps)}, what/atlantis_core/{pyproject.toml, uv.lock, README.md, config.py, __init__.py, tests/test_registry.py}, what/exemplars/gulf_karenia_brevis/atlantis.yaml, what/board/README.md, how/federation/iii/what/context/atlantis_iii_learning_store.jsonl]"
files_created: "[what/atlantis_core/src/atlantis_core/{eval/*, explain/*, board/*, run.py}, tests/test_{eval,explain,board}.py, what/exemplars/gulf_karenia_brevis/outputs/atlantis_core/*, what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json, missions/{mission_m1b_ii_a_core_eval_explain_board, mission_m1b_ii_b_site_mapping_archive}.md, missions/aar/aar_m1b_ii_a_core_eval_explain_board.md, how/backlog/idea_eval_thresholds_fixed_on_validation.md]"
completed: 2026-10-03T04:45:53Z
---

## Activity Log

- open — Session started (opus, operator-opened). Plan approved: ~/.claude/plans/please-read-the-claude-md-functional-sketch.md. Rulings (AskUserQuestion): (1) split M-1b-ii → ii-a (eval · explain · board · R7 · board v1 · semantic hash · learner swap) now + ii-b (site · mapping · archive src/hab) next; (2) learner swap = logistic regression.
- ① commit `e8751e5` — parent card superseded (kept), ii-a/ii-b cards, roster + M-1d deps, charter, STATE pointer.
- ②③ — core deps pinned to the exemplar lock (sklearn 1.9.1 · shap 0.52.0 · xgboost 3.4.1 · jsonschema[format]). eval (learners · metrics · lead · rolling/R7) · explain (+ whatif) · board · run. **Port equivalence:** core eval on hab's features.parquet reproduces every metrics.json key to 1e-12 (reference mode); SHAP reproduces shap_summary.json exactly on hab's model; the projector reproduces the M-1c fixture's evaluation field for field. What-if differs from hab at low flow — cause proven in test: hab edited a 30-day mean of log10(1+q) as log10(1+mean q). Tampa scenario scales a non-lever gauge (hab silent; core reports). xgboost 3.x defaults a fresh classifier to enable_categorical=True → shap refuses; pinned off (metrics unchanged). 112 tests. Commit `b10ec48`.
- ④ — core run (377 s): 141 trees · test AUROC 0.8938 / AUPRC 0.5388 · n 1640/127 · drops 1481+1800 · lead flagged 0.636→0.682 · 2016 fold refit · additivity 3e-6. Logistic swap AUROC 0.8726 / AUPRC 0.5225; explanation learner-dependent (season/SST proxies, collinear offsets). Board v1 emitted by code; closed evaluation PASS (committed JSON Schema + linkml-validate). SO-7 self-tests green; ALL WORLDS AGREE (42); config.yaml/outputs/v0 byte-stable. Commit `bf0b36a`.
- Budget at ④ close: ≈140 kT main context (card ~160 kT) — under.
- ⑤ III review launched (fresh-context agent via iii/ → skill_iii_review.md).
- ⑤ III review returned PASS-WITH-FINDINGS (4 major · 4 minor, each demonstrated). Rulings (AskUserQuestion): regenerate v1 in place (never left this machine); F-8 disclose now, fix carded. Fixed F-1…F-7: availability flags · hash by effect + per-swap hash · R7 verified per fold · assert_green allowlist + caps · swaps checked · tests that can fail · wording. Re-run; v1 regenerated (evaluation diff = config_hash + recorded_at). Learning store C-008…C-010. 125 tests. A reviewer scratch cache (`what/atlantis_core/built.pkl`, untracked) was moved to the session scratchpad, not committed. Commit `8edfc87`.
- close — AAR filed; card completed; ii-b card briefed (§Inputs from ii-a); STATE → ii-b prompt; WI-7 + WI-10 closed, WI-8 updated, WI-11 + WI-12 opened; CHANGELOG v0.5.0; charter status; session → history/2026-10/. Not pushed.

## SITREP

- **Completed:** M-1b-ii-a. atlantis_core trains, evaluates, explains and emits to the board. The port is exact to 1e-12. Board v1 = 0.8938 / 0.5388 (calendar lags, R7 refit, semantic hash, closed evaluation). T2: ranking survives the learner swap, explanation does not. III 8/8 addressed.
- **In progress:** none.
- **Next up:** M-1b-ii-b (opus) → M-1d → P1 gate.
- **Blockers:** none. `#needs-human`: push to the public remote (not done this sitting); the F-8 fix's slot (backlog card).

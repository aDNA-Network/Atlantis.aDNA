---
type: mission
mission_id: M-1b-ii
plan_id: mission_m1b_ii_core_eval_explain_board
title: "M-1b-ii — `atlantis_core` eval · explain · board · site: metrics reproduction, learner swap, mapping.yaml, semantic hash, src/hab archived"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~140kT main + fresh-context III reviewer"
token_budget_actual: ""
depends_on: ['M-1b-i']
split_from: mission_m1b_atlantis_core_extraction
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_ii_core_eval_explain_board.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1b_ii, p1, opus, atlantis_core, eval, board, atlantis, tidewatch]
---

# M-1b-ii — `atlantis_core` eval · explain · board · site

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 · **Tier:** opus · **Split from:**
`mission_m1b_atlantis_core_extraction.md` (operator ruling 2026-10-02) · **Sibling:** `mission_m1b_i_core_vitals_and_selftest.md`.

## Objective

Finish the extraction: training, evaluation, explanation, board emission and the site template move into `atlantis_core`;
the exemplar runs end-to-end through it and reproduces `metrics.json`; `src/hab/` is archived in place.

## Acceptance criteria

- [ ] `eval/` (split from config · budgets · lead time · calibration · ablations from vital groups/surveillance flag · climatology · rolling origin · sensitivity threshold) · learner is a config field
- [ ] `explain/` (interventional SHAP + additivity check + tags from `features.yaml`) · what-if scenarios are config
- [ ] `board/` emits the closed `AtlEvaluation` projection (validates as `pos_exemplar_gulf_karenia_brevis.yaml`'s evaluation) with the extras beside it — starts closing WI-8
- [ ] `site/` template with **all copy parameterised**; site cases are config
- [ ] **Bar re-read by operator ruling (2026-10-02, M-1b-i):** `hab` still reproduces `metrics.json` (proven in memory at M-1b-i: 0.8941 / 0.5473); the exemplar re-run through `atlantis_core` — calendar-correct SST lags — lands as a **new board version** with the delta named (in-memory M-1b-i refit: AUROC 0.8938 · AUPRC 0.5388; same n, positives, drop counts); the 2026-09-23 entry and `metrics.json` stay. **Semantic config hash** recorded beside the bytes-md5 (closes WI-7)
- [ ] **R7 obligation:** eval refits the discharge climatology per rolling-origin fold (`climatology_policy.rolling_origin: refit_per_fold`; era ends 2016, fold 2015→2016 tests 2016) — `inst.obligations` must be empty-or-honoured, asserted by test; the hab panel's 2016 fold is noted as not refit
- [ ] One learner swap (LightGBM or logistic) on the exemplar's vitals, recorded — T2 evidence
- [ ] `how/templates/template_mapping_atl.yaml`: registries → the five `atl_` labels, bi-temporal stamps, fence excluding raw observations
- [ ] `src/hab/` archived in place with a pointer (SO-2); `config.yaml`/`metrics.json` byte-stable
- [ ] III review via `iii/` in a fresh context (SO-10)

## Guardrails

As M-1b-i. Budget >50% over → SITREP and stop.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

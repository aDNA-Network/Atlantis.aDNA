---
type: mission
mission_id: M-1b-ii-b
plan_id: mission_m1b_ii_b_site_mapping_archive
title: "M-1b-ii-b — `atlantis_core` site template (all copy parameterised) · template_mapping_atl.yaml · src/hab archived"
owner: stanley
status: in_progress
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~150kT main + fresh-context III reviewer"
token_budget_actual: ""
depends_on: ['M-1b-ii-a']
split_from: mission_m1b_ii_core_eval_explain_board
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_ii_b_site_mapping_archive.md
session: session_stanley_20261003_191346_m1b_ii_b_site_mapping_archive
created: 2026-10-02
updated: 2026-10-03
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1b_ii_b, p1, opus, atlantis_core, site, mapping, atlantis, tidewatch]
---

# M-1b-ii-b — `atlantis_core` site · mapping · archive

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 · **Tier:** opus · **Split from:**
`mission_m1b_ii_core_eval_explain_board.md` (operator ruling 2026-10-02) · **Sibling:** `mission_m1b_ii_a_core_eval_explain_board.md`.

## Objective

The explainer site becomes a core template whose copy is instance data; the mapping template is written; `src/hab/` is
archived in place once nothing canonical runs through it.

## Acceptance criteria

- [ ] `site/` template with **all copy parameterised** (the exemplar's 76 KB `site/template.html` prose → instance copy file); site cases and risk strips are config; site data assembled from `outputs/atlantis_core/`
- [ ] The exemplar's page regenerates through the core from board v1's run; the v0 page (`site/hab_crash_risk.html`) is kept
- [ ] `how/templates/template_mapping_atl.yaml`: registries → the five `atl_` labels, bi-temporal stamps, fence excluding raw observations
- [ ] `src/hab/` archived in place with a pointer (SO-2); `config.yaml`/`metrics.json` byte-stable
- [ ] III review via `iii/` in a fresh context (SO-10)

## Inputs from ii-a (2026-10-02)

- Site data comes from `outputs/atlantis_core/` (metrics · shap_summary · whatif · model.json) and the gitignored
  `data/processed/atlantis_core/{all_scored,test_scored}.parquet` + `shap.npz` (`shap_all` for the risk strips; regenerate with
  `python -m atlantis_core.run`). The vitals' labels and descriptions are `features.yaml` `name`/`description`.
- The page must say what board v1 says: calendar-correct lags (0.8938 / 0.5388), the R7 refit, the F-8 limits (thresholds
  are test quantiles), and that a SHAP reading belongs to one model (T2 qualifier). Explanations show `group_net_mean_abs_shap`
  beside the abs-sums; `availability:` columns appear only for a learner that has them.

## Guardrails

As M-1b-i. Budget >50% over → SITREP and stop.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

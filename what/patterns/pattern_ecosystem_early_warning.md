---
type: pattern
doc_id: pattern_ecosystem_early_warning
title: "Pattern — ecosystem early warning (sepsis analog), 8 steps"
status: proposed
version: 0.1
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
exemplar: what/exemplars/gulf_karenia_brevis/
tags: [pattern, method, early_warning, sepsis_analog, xgboost, shap, atlantis]
---

# Pattern — ecosystem early warning, in 8 steps

Each step names the exemplar file that implements it. A new instance re-implements steps 2 and 3 and edits
`config.yaml`; everything else should carry unchanged. **The invariant is step 5's self-test.**

| # | Step | What you decide | Exemplar |
|---|---|---|---|
| 1 | **Define the patient** | the spatial unit × time step; how missing steps are represented (kept, features NaN, never forward-filled) | `config.yaml → regions` · `src/hab/regions.py` (coordinates only, never names) · `build_features.aggregate_region_week` |
| 2 | **Discover and cache the data** | every stream; server counts asserted before trust; idempotent cached fetch with retry and `--offline` | `fetch_fwc.py` · `fetch_env.py` · `what/datasets/dataset_*.md` |
| 3 | **Build the vitals** | lags, rolling peaks, growth rates, time-since-event, seasonality, environment anomalies vs a training-era climatology, **surveillance intensity as an explicit (flagged) feature** | `build_features.count_features / sst_features / discharge_features` · `FEATURE_GROUPS` |
| 4 | **Label the onset** | threshold + horizon; drop already-past-threshold (last-known state); drop unknown-outcome; report prevalence and both drop counts | `build_features.make_label / finalize` · `config.yaml → target` |
| 5 | **Prove no leakage** | a synthetic test that perturbs *t+1* and asserts no feature at *t* moves, the label does, and *t+horizon+1* moves nothing | `build_features --self-test` |
| 6 | **Train on time, evaluate at a budget** | temporal split + rolling origin; early-stop on **log-loss** (ranking is easy, calibration is the work); no class re-weighting; monotone constraints only where physics is unambiguous; report AUROC/AUPRC vs prevalence, calibration slope, precision/recall at 5/10/20% alert rates, lead-time histogram; ablate surveillance; compare to climatology | `train.py` · `outputs/metrics.json` |
| 7 | **Explain with interventional SHAP** | background from training rows; additivity asserted; global (mean abs, beeswarm, dependence with interaction partner), local (three rule-picked cases: longest-lead true positive, top false alarm, quiet week), temporal (grouped SHAP strip over one episode) | `explain.py` · `outputs/shap_summary.json` |
| 8 | **Tag and translate for action** | every feature is **lever / proxy / artifact / state**; a what-if on the lever with the causal caveat boxed; a playbook: tiered alerts at the budget, read the waterfall before acting, route lever contributions to the lever's owner, fix the surveillance design, close the loop | `export_site_data.FEATURE_DOC` · `whatif.py` · `site/template.html §10` |

## Two findings the exemplar produced that the pattern now carries

- **Stop on log-loss, not AUPRC.** Validation AUPRC was flat from the first tree; log-loss kept improving to ~150.
  AUPRC-stopping gave a two-tree, uncalibrated model with a calibration slope of 18.
- **Ablate surveillance before you believe the score.** Sampling intensifies during events. In the exemplar the
  ablation cost 0.004 AUROC — the model was not mainly reading the programme's own reaction — but the check is
  cheap and the failure mode is silent.

## Where the analogy breaks (say it on every page)

Patients are independent; regions advect into each other. Sepsis has a treatment; a bloom has a response, so
lead time matters more here. Sepsis labels are adjudicated; ecological labels depend on where the bottle was
dipped. Interventional SHAP breaks correlations by construction and can credit a feature reached only through a
partner — colour the partner on every dependence plot.

---
type: artifact
doc_id: thesis_register
title: "Thesis register — the claims Atlantis makes, as falsifiable statements with evidence and the phase that tests each"
status: draft
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
evidence_source: what/exemplars/gulf_karenia_brevis/outputs/metrics.json   # config_hash e9dea88254
tags: [artifact, thesis_register, m0, atlantis, tidewatch]
---

# Thesis register

Every claim in `what/context/concept_atlantis.md` and `what/patterns/pattern_ecosystem_early_warning.md`, numbered,
stated so it can be false, with the exemplar evidence that exists today and the phase that tests what does not.
Numbers are read from `outputs/metrics.json` (config hash `e9dea88254`), not retyped from the README.
**Evidence class:** `exemplar` = one public-data instance, one test window scored once; nothing here is replicated
yet. Status of every claim is **supported-by-one-exemplar** or **untested** — never "proven".

| # | Claim (falsifiable form) | Exemplar evidence (test = 1640 region-weeks, 127 onsets, prevalence 0.077) | Falsified if | Tested next at |
|---|---|---|---|---|
| T1 | The sepsis early-warning schema transfers to an ecosystem *as a schema*: every slot (patient · vitals · event · horizon · onset rule · alert budget · lead time · tagged explanation) is fillable from a region's public streams. | All eight slots filled from three streams (FWC counts · OISST SST · USGS discharge); 25 vitals in 5 groups. | A second ecosystem leaves a slot unfillable without inventing data. | **P2** — FKNMS coral bleaching fills every slot from *gridded-only* vitals (no point samples, no surveillance channel). |
| T2 | Translation is the product: the learner is a late, swappable choice; the value and the risk live in the vitals table and the leakage proof. | Leakage self-test green; test AUROC 0.894 with a depth-4 GBM; no tuning on test. **M-1b-ii-a (2026-10-02): logistic regression on the same vitals** (median impute + missingness flags; imputer and scaler fitted on each model's own training rows, never test):  test AUROC 0.873 vs 0.894 (Δ −0.021), AUPRC 0.523 vs 0.539, precision/recall at the 10% budget 0.457/0.591 vs 0.463/0.598, rolling 0.77–0.98. **The falsifier is NOT met** (Δ ≪ the 0.79–0.99 spread; the falsifier is weak by design).  **Qualifier: the explanation is learner-dependent.** By net group attribution, xgboost reads counts first (0.84; season 0.35, SST 0.25), while logistic reads SST (1.67) and season (1.58) ahead of counts (0.83). The lever-tagged discharge group's net share halves (0.21 → 0.10). Logistic's missingness flags, which mark the gauge-less units, carry large offsetting attributions (abs 1.75, net 0.21) and are reported as availability artifacts. **Ranking is swappable; the SHAP reading is not.** (The first reading of this result, at commit `bf0b36a`, folded those flags into the lever vital and was wrong; III F-1.) (board v1 `evaluation_extras.learner_swaps`) | Swapping the learner (same vitals) moves AUROC by more than the rolling-origin spread (0.79–0.99). | ~~P1 M-1b~~ → **tested at M-1b-ii-a** (one exemplar). Next: a swap on a second instance (M-2); a collinearity-aware reading (grouped SHAP) before any steward is shown an explanation. |
| T3 | Onset, not persistence, is the honest label: dropping already-past-threshold and unknown-outcome rows is required for the score to mean "warning". | 1,481 in-bloom and 1,800 unknown-outcome region-weeks dropped of 14,085; modelling prevalence 0.108. | A persistence-inclusive label does *not* inflate AUPRC relative to the onset label. | **P2** — DHW events persist for weeks; the onset rule is the hardest case. |
| T4 | Calibration is the work: early-stop on log-loss, not AUPRC. | Full model 141 trees, calibration slope 1.17, Brier 0.0499; AUPRC-stopping (S329) gave a 2-tree model with slope ≈18. | Log-loss stopping yields a worse-calibrated model on a second instance. | **P2** replication; **P1 M-1a** records the S329 AUPRC-stopping run as a reproducible negative control. |
| T5 | Surveillance intensity is an endogenous channel; it must be an explicit flagged feature *and* ablated, and the ablation result reported. | Ablation AUROC 0.894 → 0.890, AUPRC 0.547 → 0.526; surveillance-only baseline AUROC 0.624. | An instance whose score collapses under ablation is published without the ablation. | **P1 M-1b** makes the ablation a required pipeline output; **P2** tests the *absence* case (gridded vitals have no surveillance channel — the claim is then about where the check applies). |
| T6 | Evaluating at a staffable alert budget plus lead time is what makes a score usable; AUROC alone is not. | 5% budget: precision 0.65 / recall 0.42 · 10%: 0.46 / 0.60 · 20%: 0.31 / 0.81; lead time at 10%: 22 onsets, 0.64 flagged ahead, median 4 wk. | A steward, shown both, acts on AUROC. | **P4** — the first outside steward reads the page; **P2** adds a second budget table to the board. |
| T7 | Tagged SHAP (lever · proxy · artifact · state) is a human bridge to intervention, not a causal claim; the what-if is a sensitivity. | Top-6 mean-abs SHAP led by `roll_max_4w` (state) and `woy_sin` (proxy); discharge (lever) group 0.27; what-if (discharge ×0.7) moved mean p by +0.10 pp / −0.06 pp — small and correlational. | A page from any instance states a SHAP value as a cause, or a lever tag is attached to a feature nobody owns. | **P3** — a literature-asserted lever is tested by SHAP and written up either way; **P1 M-1b** moves tags into the feature registry so they are reviewable. |
| T8 | A region's literature can be mined into *testable feature hypotheses* (driver · lag · direction · threshold · evidence class · citation), not prose. | **None.** Playbook §C is a design. | The extraction target yields rows no fetcher can realise, or rows with no SHAP after realisation are never written up. | **P3 M-3b** — hypothesis ledger populated for one instance; ≥1 driver tested. |
| T9 | The method is drop-in: a second instance trains, explains and publishes **without editing Atlantis code**. | **None.** The exemplar *is* the code. | P2 needs an instance-local patch to `atlantis_core`. | **P2** (exit bar: every deviation becomes a P1 template change). |
| T10 | Decentralised by construction: instances' results are comparable on the board with **no data moving** and no steward losing custody. | **None yet** — board v1 spec and one exemplar entry exist from this sitting. | A second entry cannot be compared without seeing the instance's data, or a steward is asked for data to be listed. | **P2** second board entry; **P4** first outside steward. |
| T11 | The model earns its keep against the cheapest baseline: week-of-year climatology. | Climatology AUROC 0.577 / AUPRC 0.104 vs model 0.894 / 0.547. | An instance's model does not beat its climatology at the chosen budget. | Required board field from **P1 M-1b** onward. |
| T12 | A region-specific model is the right unit; a second event definition on the same vitals is a second model, not a feature. | 50k-cells/L sensitivity run: AUROC 0.888 / AUPRC 0.597 at prevalence 0.076. | A single multi-threshold model is better calibrated across events than per-event models on the same instance. | **P2+** (two DHW thresholds on FKNMS). |

## Reading the register

- **Supported-by-one-exemplar:** T1 T2 T3 T4 T5 T6 T7 T11 T12. **Untested:** T8 T9 T10 — these are exactly what P2–P4 exist to test.
- The register is the input to the board's `claim` field: an entry may say `method_demonstration` only; `operational_by_owner_ruling` requires the instance owner's written ruling naming the agencies that run the real thing (SO-4).
- Re-cut this table at every phase exit; a claim that fails is kept with `status: falsified` and the evidence, never removed (SO-2).

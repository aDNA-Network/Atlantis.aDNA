---
type: model_card
model_id: atl_model_<instance>_<event>_v<n>
title: "<Instance> — <event> onset model, v<n>"
status: draft                      # draft | reviewed | validated | superseded
instance: <Instance>.aDNA
evaluation_ref: evaluations/atl_eval_<...>.yaml      # an AtlEvaluation (what/schema/atl_v0/)
board_entry: what/board/entries/<date>_<instance>_v<n>.json
claim: method_demonstration        # operational_by_owner_ruling requires owner_ruling_ref
owner_ruling_ref: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_edited_by: agent_<persona>
tags: [model_card, atlantis, <instance>, <event>]
---

# <Instance> — <event> onset model, v<n>

> **Claim:** method demonstration. Not an operational forecast; <agency> runs that. *(Change this line only with the
> owner's written ruling, cited in frontmatter.)*

## 1. Patient
`unit_kind` · number of units · `time_step` · geometry pointer (never inline partner coordinates) · how missing
steps are represented (kept, features NaN, never forward-filled).

## 2. Event
Variable (authority CURIE) · threshold + UCUM unit · direction · horizon · onset rule · both drop counts
(already-past-threshold · unknown outcome) · modelling prevalence.

## 3. Streams and pins
| stream_id | modality | source_system / source_id | captured_at | ingested_at | sha256 | license |
|---|---|---|---|---|---|---|

## 4. Vitals
Count by group · the feature registry version (`features.yaml`) · tags summary (lever n / proxy n / artifact n /
state n) · levers and their owners · surveillance channel declared? (yes/no + why).

## 5. Learner and split
Learner + hyper-parameters · monotone constraints and the physics that justifies each · temporal split (train · val ·
test, scored once) · rolling-origin windows · early-stopping metric (**log-loss**, and why) · `config_hash`.

## 6. Evaluation (against the base rate)
| | Test | Climatology baseline |
|---|---|---|
| base rate | | — |
| AUROC | | |
| AUPRC | | |
| Brier · calibration slope | | — |

**Alert budgets:** rate → precision / recall / n_alerts (≥ 1 row; name the budget the steward can staff).
**Lead time** at that budget: onsets · fraction flagged ahead · median lead (time steps).
**Ablations:** surveillance group (required if declared) · any stream · any lever.
**Sensitivity:** second threshold / horizon if run.

## 7. Explanation
Interventional SHAP · background n · additivity gap · mean |SHAP| by group · top vitals and their dependence
partners · the three rule-picked cases (longest-lead TP · top false alarm · quiet step) — **summaries only** here.

## 8. What-if (sensitivity, not effect)
The lever perturbed · the window · Δp — with the causal caveat in the same sentence.

## 9. Limitations *(mandatory — the card is invalid without it)*
Where the analogy breaks for this instance · surveillance endogeneity · label dependence on sampling · advection
between units · what is absent (wind, nutrients, …) · SHAP credit through correlated partners · demo, not a forecast.

## 10. Lineage
Previous version · what changed in vitals / label / learner · self-test run id (green) · retrain cadence (P5).

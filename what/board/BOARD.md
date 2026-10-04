# The Atlantis evidence board

> **GENERATED — never hand-edit.** Regenerate with `python -m atlantis_core.board --index` (from `what/atlantis_core/`);
> `--index --check` fails if this file is stale. A merge conflict here is resolved by regenerating, never by hand.
> Rules and lifecycle: `README.md`. The JSON in `entries/` is authoritative.

> ⛔ **THIS BOARD MAKES NO ACCURACY CLAIM.** Every entry is a *method demonstration* unless its claim cites an instance
> owner's written ruling. Read every score against **its own base rate** and at **its stated alert budgets** — a bare
> AUROC is not a result here.

**2 entries** (0 superseded; 1 open-shape, grandfathered by id).

## Entries

| Entry | Source | Event | Patients | Base rate | AUROC / AUPRC | Climatology AUROC / AUPRC | Lead (budget) | Claim | Shape | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| [`2026-09-23_gulf_karenia_brevis_v0`](entries/2026-09-23_gulf_karenia_brevis_v0.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.8941 / 0.5473 | 0.5767 / 0.1038 | 0.6364 of 22 onsets flagged, median 4.0 wk (@ 0.1) | method_demonstration | open shape — pre-atlantis_core (M-0 sitting script); not a closed AtlEvaluation | live |
| [`2026-10-02_gulf_karenia_brevis_v1`](entries/2026-10-02_gulf_karenia_brevis_v1.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.8938 / 0.5388 | 0.5767 / 0.1038 | 0.6818 of 22 onsets flagged, median 4.0 wk (@ 0.1) | method_demonstration | closed `AtlEvaluation` | live |

## Alert budgets

*Precision and recall when the steward can staff alerts on this fraction of patient-weeks.*

| Entry | Budget | Precision | Recall | Alerts |
|---|---|---|---|---|
| `2026-09-23_gulf_karenia_brevis_v0` | 0.05 | 0.6463 | 0.4173 | 82 |
| `2026-09-23_gulf_karenia_brevis_v0` | 0.1 | 0.4634 | 0.5984 | 164 |
| `2026-09-23_gulf_karenia_brevis_v0` | 0.2 | 0.314 | 0.811 | 328 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.05 | 0.6463 | 0.4173 | 82 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.1 | 0.4634 | 0.5984 | 164 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.2 | 0.314 | 0.811 | 328 |

## Limits and ablations

- **`2026-09-23_gulf_karenia_brevis_v0`** — limits: what/exemplars/gulf_karenia_brevis/site/hab_crash_risk.html#limits (§11 Where the analogy breaks) · README.md §Caveats · config `e9dea88254` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8903 / AUPRC 0.5264; surveillance-only single feature (n_samples_4w): AUROC 0.6239
- **`2026-10-02_gulf_karenia_brevis_v1`** — limits: what/exemplars/gulf_karenia_brevis/site/hab_crash_risk.html#limits (§11 Where the analogy breaks) · README.md §Caveats · config `acfa22c6e4` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8885 / AUPRC 0.5244; surveillance-only single feature (n_samples_4w): AUROC 0.6239

# The Atlantis evidence board

> **GENERATED — never hand-edit.** Regenerate with `python -m atlantis_core.board --index` (from `what/atlantis_core/`);
> `--index --check` fails if this file is stale. A merge conflict here is resolved by regenerating, never by hand.
> Rules and lifecycle: `README.md`. The JSON in `entries/` is authoritative.

> ⛔ **THIS BOARD MAKES NO ACCURACY CLAIM.** Every entry is a *method demonstration* unless its claim cites an instance
> owner's written ruling. Read every score against **its own base rate** and at **its stated alert budgets** — a bare
> AUROC is not a result here.

**8 entries** (6 superseded by a newer version of the same stem; 1 open-shape, grandfathered by id).

## Entries

| Entry | Source | Event | Patients | Base rate | AUROC / AUPRC | Climatology AUROC / AUPRC | Lead (budget: nominal · realised) | Claim | Shape | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| [`2026-09-23_gulf_karenia_brevis_v0`](entries/2026-09-23_gulf_karenia_brevis_v0.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.8941 / 0.5473 | 0.5767 / 0.1038 | 0.6364 of 22 onsets flagged, median 4.0 wk (@ 0.1 nominal · realised —, threshold set on test after the fact (F-8)) | method_demonstration | open shape — pre-atlantis_core (M-0 sitting script); not a closed AtlEvaluation | superseded → `2026-10-08_gulf_karenia_brevis_v4` |
| [`2026-10-02_gulf_karenia_brevis_v1`](entries/2026-10-02_gulf_karenia_brevis_v1.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.8938 / 0.5388 | 0.5767 / 0.1038 | 0.6818 of 22 onsets flagged, median 4.0 wk (@ 0.1 nominal · realised —, threshold set on test after the fact (F-8)) | method_demonstration | closed `AtlEvaluation` | superseded → `2026-10-08_gulf_karenia_brevis_v4` |
| [`2026-10-03_gulf_karenia_brevis_v2`](entries/2026-10-03_gulf_karenia_brevis_v2.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.8938 / 0.5388 | 0.5767 / 0.1038 | 0.6364 of 22 onsets flagged, median 4.0 wk (@ 0.1 nominal · 0.0811 realised) | method_demonstration | closed `AtlEvaluation` | superseded → `2026-10-08_gulf_karenia_brevis_v4` |
| [`2026-10-07_gulf_karenia_brevis_v3`](entries/2026-10-07_gulf_karenia_brevis_v3.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.895 / 0.5414 | 0.577 / 0.1045 | 0.5909 of 22 onsets flagged, median 4.0 wk (@ 0.1 nominal · 0.0799 realised) | method_demonstration | closed `AtlEvaluation` | superseded → `2026-10-08_gulf_karenia_brevis_v4` |
| [`2026-10-08_florida_keys_coral_v1`](entries/2026-10-08_florida_keys_coral_v1.json) | instance | `atl_event_florida_keys_coral_onset` ≥ 4.0 Cel.wk within 8 wk | 21 × mpa_zone | 0.1501 | 0.937 / 0.6903 | 0.9194 / 0.6012 | 1.0 of 105 onsets flagged, median 8.0 wk (@ 0.1 nominal · 0.2034 realised) | method_demonstration | closed `AtlEvaluation` | superseded → `2026-10-08_florida_keys_coral_v3` |
| [`2026-10-08_florida_keys_coral_v2`](entries/2026-10-08_florida_keys_coral_v2.json) | instance | `atl_event_florida_keys_coral_onset` ≥ 4.0 Cel.wk within 8 wk | 21 × mpa_zone | 0.1501 | 0.937 / 0.6903 | 0.9194 / 0.6012 | 1.0 of 105 onsets flagged, median 8.0 wk (@ 0.1 nominal · 0.2034 realised) | method_demonstration | closed `AtlEvaluation` | superseded → `2026-10-08_florida_keys_coral_v3` |
| [`2026-10-08_florida_keys_coral_v3`](entries/2026-10-08_florida_keys_coral_v3.json) | instance | `atl_event_florida_keys_coral_onset` ≥ 4.0 Cel.wk within 8 wk | 21 × mpa_zone | 0.1501 | 0.937 / 0.6903 | 0.9194 / 0.6012 | 1.0 of 105 onsets flagged, median 8.0 wk (@ 0.1 nominal · 0.2034 realised) | method_demonstration | closed `AtlEvaluation` | live |
| [`2026-10-08_gulf_karenia_brevis_v4`](entries/2026-10-08_gulf_karenia_brevis_v4.json) | exemplar | `atl_event_kbrevis_onset_100k_4w` ≥ 100000 /L within 4 wk | 9 × coastal_band | 0.0774 | 0.895 / 0.5414 | 0.577 / 0.1045 | 0.5909 of 22 onsets flagged, median 4.0 wk (@ 0.1 nominal · 0.0799 realised) | method_demonstration | closed `AtlEvaluation` | live |

*Status is derived, never written into an entry (SO-2): within one source, instance and stem, the highest version supersedes the lower ones. A superseded entry stays on the board.*

## Comparators and the shift

*atl_v0 0.7.0 (M-2b). Where the event variable is also a vital, the model is read against the signal itself: **Persistence** ranks test weeks by the event signal at t (no model); **Trend** is a logistic fit on that signal and its last step. **Base rate** is per segment (train / validation / test): thresholds are fixed on validation and meet the test base rate. **Mean p − prevalence** is calibration in the large (> 0 over-predicts). Entries before 0.7.0 carry none of these and are not listed.*

| Entry | Base rate train / val / test | Persistence AUROC / AUPRC | Trend AUROC / AUPRC | Mean p − prevalence val / test |
|---|---|---|---|---|
| `2026-10-08_florida_keys_coral_v1` | 0.0131 / 0.0759 / 0.1501 | 0.7505 / 0.3583 | 0.7809 / 0.5201 | -0.0453 / -0.0974 |
| `2026-10-08_florida_keys_coral_v2` | 0.0131 / 0.0759 / 0.1501 | 0.7505 / 0.3583 | 0.7809 / 0.5201 | -0.0453 / -0.0974 |
| `2026-10-08_florida_keys_coral_v3` | 0.0131 / 0.0759 / 0.1501 | 0.7505 / 0.3583 | 0.7809 / 0.5201 | -0.0453 / -0.0974 |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.1154 / 0.1014 / 0.0774 | 0.7617 / 0.372 | 0.7997 / 0.3982 | -0.0145 / 0.0094 |

## Climatology at the same nominal budgets

*atl_v0 0.8.0 (M-2c-i; T11 at its terms). Week-of-year climatology is scored at the model's budgets under the model's rule: each threshold is fixed on validation by a climatology fit on train only, then applied to test. Climatology scores tie in whole week-of-year groups, so its **realised** rate departs from the nominal budget by construction; read precision beside it. **Δ precision** is model − climatology at those thresholds, with its season-block interval (nominal level). **Matched volume** compares at equal alert counts instead: the model's precision minus climatology's expected precision at the number of alerts the model raised, so a difference in realised rate cannot pass for a difference in skill. Entries before 0.8.0 carry none of this and are not listed.*

| Entry | Budget | Model precision / recall (realised) | Climatology precision / recall (realised) | Δ precision [interval] | Matched-volume Δ precision [interval] |
|---|---|---|---|---|---|
| `2026-10-08_florida_keys_coral_v3` | 0.05 | 0.7424 / 0.4357 (0.0881) | 0.6291 / 0.6786 (0.1619) | +0.1133 [+0.0278, +0.1994] | +0.0839 [-0.0118, +0.1926] · spans 0 |
| `2026-10-08_florida_keys_coral_v3` | 0.1 | 0.5677 / 0.769 (0.2034) | 0.6228 / 0.7429 (0.1791) | -0.0551 [-0.1556, +0.0676] · spans 0 | -0.0221 [-0.0906, +0.067] · spans 0 |
| `2026-10-08_florida_keys_coral_v3` | 0.2 | 0.4828 / 0.9202 (0.2861) | 0.5371 / 0.8702 (0.2433) | -0.0543 [-0.1072, -0.0046] | -0.0019 [-0.0265, +0.0278] · spans 0 |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.05 | 0.6567 / 0.3465 (0.0409) | 0.1308 / 0.1102 (0.0652) | +0.5259 [+0.3163, +0.7548] | +0.525 [+0.2215, +0.7929] |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.1 | 0.5267 / 0.5433 (0.0799) | 0.1185 / 0.126 (0.0823) | +0.4082 [+0.1109, +0.5998] | +0.4068 [+0.0962, +0.5934] |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.2 | 0.3143 / 0.7795 (0.1921) | 0.1185 / 0.3386 (0.2213) | +0.1958 [+0.009, +0.2943] | +0.1903 [+0.0416, +0.3029] |

**Model − climatology, season-block paired interval.** *Whole test seasons (each starting at the instance's declared month) are drawn with replacement, and one draw scores both the model and climatology. With B seasons there are only C(2B − 1, B) distinct draws (35 at B = 4, 1,716 at B = 7). The level is **nominal**: a percentile interval under-covers at so few blocks (III M-2c-i F-2), so **"spans 0: no" is not "distinguished at that level"**. Read it beside how many seasons favour the model on their own, and the exact one-sided sign test. An interval that spans 0 means **not distinguished at this sample**. It never means "no difference".*

| Entry | Metric | Model − climatology | Interval (nominal level) | Seasons (start month · distinct draws) | Seasons favouring the model (sign test p) | Spans 0 |
|---|---|---|---|---|---|---|
| `2026-10-08_florida_keys_coral_v3` | auroc | +0.0176 | 0.95: [-0.0193, +0.0618] | 7 (month 1 · 1716) | 3 of 7 (p 0.7734) | yes |
| `2026-10-08_florida_keys_coral_v3` | auprc | +0.0891 | 0.95: [-0.0241, +0.1898] | 7 (month 1 · 1716) | 4 of 7 (p 0.5) | yes |
| `2026-10-08_gulf_karenia_brevis_v4` | auroc | +0.318 | 0.95: [+0.0397, +0.5408] | 5 (month 8 · 126) | 3 of 3 (p 0.125) | no |
| `2026-10-08_gulf_karenia_brevis_v4` | auprc | +0.4369 | 0.95: [+0.2488, +0.573] | 5 (month 8 · 126) | 3 of 3 (p 0.125) | no |

## Alert budgets

*Precision and recall when the steward can staff alerts on this fraction of patient-weeks. **Budget** is nominal; **Realised** is the share of test patient-weeks a threshold fixed beforehand actually flagged (atl_v0 0.4.0). A threshold chosen on the test years themselves (before M-1e) has no realised rate: its precision and recall are after the fact (F-8).*

| Entry | Budget | Threshold fixed on | Realised | Precision | Recall | Alerts |
|---|---|---|---|---|---|---|
| `2026-09-23_gulf_karenia_brevis_v0` | 0.05 | test, after the fact (F-8) | — | 0.6463 | 0.4173 | 82 |
| `2026-09-23_gulf_karenia_brevis_v0` | 0.1 | test, after the fact (F-8) | — | 0.4634 | 0.5984 | 164 |
| `2026-09-23_gulf_karenia_brevis_v0` | 0.2 | test, after the fact (F-8) | — | 0.314 | 0.811 | 328 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.05 | test, after the fact (F-8) | — | 0.6463 | 0.4173 | 82 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.1 | test, after the fact (F-8) | — | 0.4634 | 0.5984 | 164 |
| `2026-10-02_gulf_karenia_brevis_v1` | 0.2 | test, after the fact (F-8) | — | 0.314 | 0.811 | 328 |
| `2026-10-03_gulf_karenia_brevis_v2` | 0.05 | validation | 0.0378 | 0.6613 | 0.3228 | 62 |
| `2026-10-03_gulf_karenia_brevis_v2` | 0.1 | validation | 0.0811 | 0.5113 | 0.5354 | 133 |
| `2026-10-03_gulf_karenia_brevis_v2` | 0.2 | validation | 0.1933 | 0.3186 | 0.7953 | 317 |
| `2026-10-07_gulf_karenia_brevis_v3` | 0.05 | validation | 0.0409 | 0.6567 | 0.3465 | 67 |
| `2026-10-07_gulf_karenia_brevis_v3` | 0.1 | validation | 0.0799 | 0.5267 | 0.5433 | 131 |
| `2026-10-07_gulf_karenia_brevis_v3` | 0.2 | validation | 0.1921 | 0.3143 | 0.7795 | 315 |
| `2026-10-08_florida_keys_coral_v1` | 0.05 | validation | 0.0881 | 0.7424 | 0.4357 | 493 |
| `2026-10-08_florida_keys_coral_v1` | 0.1 | validation | 0.2034 | 0.5677 | 0.769 | 1138 |
| `2026-10-08_florida_keys_coral_v1` | 0.2 | validation | 0.2861 | 0.4828 | 0.9202 | 1601 |
| `2026-10-08_florida_keys_coral_v2` | 0.05 | validation | 0.0881 | 0.7424 | 0.4357 | 493 |
| `2026-10-08_florida_keys_coral_v2` | 0.1 | validation | 0.2034 | 0.5677 | 0.769 | 1138 |
| `2026-10-08_florida_keys_coral_v2` | 0.2 | validation | 0.2861 | 0.4828 | 0.9202 | 1601 |
| `2026-10-08_florida_keys_coral_v3` | 0.05 | validation | 0.0881 | 0.7424 | 0.4357 | 493 |
| `2026-10-08_florida_keys_coral_v3` | 0.1 | validation | 0.2034 | 0.5677 | 0.769 | 1138 |
| `2026-10-08_florida_keys_coral_v3` | 0.2 | validation | 0.2861 | 0.4828 | 0.9202 | 1601 |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.05 | validation | 0.0409 | 0.6567 | 0.3465 | 67 |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.1 | validation | 0.0799 | 0.5267 | 0.5433 | 131 |
| `2026-10-08_gulf_karenia_brevis_v4` | 0.2 | validation | 0.1921 | 0.3143 | 0.7795 | 315 |

## Limits and ablations

- **`2026-09-23_gulf_karenia_brevis_v0`**: limits: what/exemplars/gulf_karenia_brevis/site/hab_crash_risk.html#limits (§11 Where the analogy breaks) · README.md §Caveats · config `e9dea88254` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8903 / AUPRC 0.5264; surveillance-only single feature (n_samples_4w): AUROC 0.6239
- **`2026-10-02_gulf_karenia_brevis_v1`**: limits: what/exemplars/gulf_karenia_brevis/site/hab_crash_risk.html#limits (§11 Where the analogy breaks) · README.md §Caveats · config `acfa22c6e4` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8885 / AUPRC 0.5244; surveillance-only single feature (n_samples_4w): AUROC 0.6239
- **`2026-10-03_gulf_karenia_brevis_v2`**: limits: what/exemplars/gulf_karenia_brevis/site/gulf_karenia_brevis_v2.html#limits · README.md §Caveats · config `acfa22c6e4` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8885 / AUPRC 0.5244; surveillance-only single feature (n_samples_4w): AUROC 0.6239
- **`2026-10-07_gulf_karenia_brevis_v3`**: limits: what/atlantis_core/README.md#known-limits-of-eval-and-explain-so-9 · README.md §Caveats · config `7b789afded` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8911 / AUPRC 0.5307; surveillance-only single feature (n_samples_4w): AUROC 0.6239
- **`2026-10-08_florida_keys_coral_v1`**: limits: site/florida_keys_coral_v1.html#limits · config `c07b7c0288` · ablations: none declared
- **`2026-10-08_florida_keys_coral_v2`**: limits: site/florida_keys_coral_v1.html#limits · config `c07b7c0288` · ablations: none declared
- **`2026-10-08_florida_keys_coral_v3`**: limits: site/florida_keys_coral_v1.html#limits · config `c07b7c0288` · ablations: none declared
- **`2026-10-08_gulf_karenia_brevis_v4`**: limits: what/atlantis_core/README.md#known-limits-of-eval-and-explain-so-9 · README.md §Caveats · config `7b789afded` · ablations: without surveillance group (n_samples_t0, n_samples_4w): AUROC 0.8911 / AUPRC 0.5307; surveillance-only single feature (n_samples_4w): AUROC 0.6239

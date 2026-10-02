# hab_crash_risk — a sepsis-style early warning for *Karenia brevis* blooms

**Question.** Given the last few weeks of cell counts, water temperature, season and river flow for one stretch of Florida
coast, what is the probability that it tips into a fish-killing *Karenia brevis* bloom (≥100,000 cells/L) within four weeks —
and which inputs drove that score?

**Why the sepsis framing.** Clinical early-warning models score a trajectory of vitals against a fixed alert budget and
report lead time. Both ideas transfer: score the trend, not the level; evaluate precision/recall at the alert rate the
monitoring programme can absorb. The explainer site (`site/hab_crash_risk.html`) walks the whole thing, including where the
analogy breaks.

## Results (S329 run, 2026-09-23)

Modelling set: **10,804 region-weeks, 1,168 onsets (10.8%)** after dropping
1,481 already-in-bloom weeks and 1,800 unknown-outcome weeks. Test = 2020–2023, scored once.

| Model | Test AUROC | Test AUPRC (prev 0.077) | Brier | Cal. slope | Trees |
|---|---|---|---|---|---|
| Full | 0.894 | 0.547 | 0.0499 | 1.17 | 141 |
| Without surveillance features | 0.890 | 0.526 | 0.0501 | 1.02 | 329 |
| Climatology (week-of-year rate) | 0.577 | 0.104 | — | — | — |
| Surveillance only (`n_samples_4w`) | 0.624 | — | — | — | — |

Alert budgets (test): 5% → precision 0.65 / recall 0.42 · 10% → 0.46 / 0.60 · 20% → 0.31 / 0.81.
Lead time at the 10% budget: 22 observed onsets, **64% flagged ahead**, median lead 4 weeks (histogram {'-1': 8, '1': 3, '3': 2, '4': 9}; `-1` = missed).
Rolling origin 2016→2023 AUROC 0.79–0.99. Sensitivity at 50k cells/L: AUROC 0.888, AUPRC 0.597.

**SHAP** (interventional, 1000 background rows, additivity gap 4.3e-06). Top features by mean |SHAP|:
`roll_max_4w` 0.41, `woy_sin` 0.33, `roll_max_8w` 0.26, `weeks_since_bloom` 0.23, `discharge_anom_t0` 0.19, `sst_delta_4w` 0.18. By group: counts 1.15, sst 0.49, season 0.40, discharge 0.27, surveillance 0.17.
Strongest interaction: `roll_max_8w` × `woy_sin`.

**What-if** (discharge features ×0.7): mean Δp +0.10 pp on Lee–Collier 2022–23 (held out), -0.06 pp on 2017–19 (in-sample) — the model's discharge sensitivity is small; correlational either way.

**Two findings worth carrying.** (1) Early-stopping on AUPRC yields a 2-tree model — validation AUPRC is flat from the first
split while log-loss keeps improving to ~150 trees: the *ranking* is easy, the *calibration* is the work. Stop on log-loss.
Reproduced 2026-10-02 as a **negative control** (`python -m hab.train --negative-control` → `outputs/negative_control_auprc_stop.json`):
2 trees, test AUROC 0.877 / AUPRC 0.423 / Brier 0.0705, **calibration slope 18.1** vs 1.17 for the log-loss-stopped reference (thesis T4).
(2) The surveillance ablation costs almost nothing (AUROC 0.894 → 0.890): the model is not mainly
reading the monitoring programme's own reaction.

Explainer site: `site/hab_crash_risk.html` — published 2026-09-23 as a claude.ai Artifact (private): https://claude.ai/artifact/FNP4nCRfEmfqxevpEFPdmB

## Run order

```
uv sync                                          # pyproject.toml + uv.lock → .venv (Python 3.12, pinned deps, `hab` editable)
.venv/bin/python -m pytest                       # region-rule parser: whitelist + the 9 frozen region counts
.venv/bin/python -m hab.fetch_fwc                # 196,024 samples, six FWC ArcGIS layers → data/raw/fwc_fetch_summary.json
.venv/bin/python -m hab.fetch_env                # OISST per region box + USGS discharge (slow: ~80 ERDDAP requests;
                                                 #   parallelise with --regions=N --no-merge, then run once more to merge)
.venv/bin/python -m hab.provenance               # (re)write data/raw/*_fetch_summary.json: rows · dates · sha256 · fetched_at
.venv/bin/python -m hab.build_features --self-test   # leakage test: t+1 perturbation must not move any feature at t
.venv/bin/python -m hab.eda
.venv/bin/python -m hab.build_features
.venv/bin/python -m hab.train                    # → outputs/metrics.json (+ --negative-control for the T4 control)
.venv/bin/python -m hab.explain
.venv/bin/python -m hab.whatif
.venv/bin/python -m hab.export_site_data
.venv/bin/python -m hab.build_site
```
Every `hab.*` module runs from the exemplar root or from `src/`. `requirements.txt` was retired 2026-10-02 (M-1a) in favour
of the lockfile; matplotlib was in it and never used.

## Design in one screen

| Decision | Choice | Why |
|---|---|---|
| Patient | region × ISO week, 9 regions by lat/lon rule (`config.yaml → regions`, parsed by an `ast` whitelist — never `eval`) | blooms are alongshore-coherent at ~50–100 km; FWC reports by county band |
| Missing weeks | kept, features NaN, `weeks_since_sample` | forward-filling fabricates stable vitals |
| Label | onset: future 4-wk max ≥ 1e5 **and** last-known max < 1e5; in-bloom weeks dropped; unknown-outcome weeks dropped | predicting persistence is easy and inflates everything |
| Split | train 1994–2016 · val 2017–2019 · test 2020–2023 + rolling-origin 2016→2023 | adjacent region-weeks are near-duplicates; random splits lie |
| Model | XGBoost depth 4, eta 0.03, early-stopped on **val log-loss** (patience 100; the AUPRC-stopped run is kept as a negative control), no `scale_pos_weight`, monotone +1 on `log_max_t0` and `roll_max_4w` | calibration matters for alert-rate/lead-time reporting |
| Ablation | twin model without surveillance features + single-feature `n_samples_4w` baseline + week-of-year climatology | sampling intensifies during blooms: an artifact channel |
| SHAP | TreeExplainer, **interventional**, **1,000**-row training background (`shap.background_n`); additivity asserted | "what if set independently" is the semantics an intervention story needs |
| What-if | discharge features ×0.7, re-score; the lever is whichever gauge carries `lever: true` in config (S-79) — that flag also sets the discharge features' `lever` tag on the site | model sensitivity, explicitly **not** causal |

## Provenance and reproducibility

- **Raw artifacts.** The three committed parquets each have a `data/raw/<source>_fetch_summary.json` (rows · date range · `sha256` ·
  `fetched_at`), written by the fetchers after a download and regenerable with `python -m hab.provenance`. Pins at this
  commit: FWC `2bde1410…`, OISST `c26b97f5…`, USGS `66a58af4…` — the same values the vault's evidence-board entry carries
  (`what/board/entries/2026-09-23_gulf_karenia_brevis_v0.json`). The OISST/USGS `fetched_at` are file mtimes (the S329 run kept no
  fetch-time record for them) and the summaries say so.
- **`config_hash`.** `metrics.json` carries `md5(config.yaml bytes)[:10]`. The committed value **`e9dea88254`** is the training-time
  config, which had `shap.background_n: 2000`; that one SHAP-only line was set to 1000 before `hab.explain` ran (so `shap_summary.json`
  says 1000), and the live file hashes to `979d3fdf16`. Nothing the model sees differs between the two; the hash is a bytes-hash and
  reacts to comments. Retraining was deliberately *not* done to "fix" the hash. The reference implementation (`atlantis_core`, P1 M-1b)
  hashes the parsed training-relevant sections instead.
- **Region assignment** is covered by `tests/test_regions.py`: the parser rejects anything outside `lat`/`lon` comparisons, and the
  nine region counts on the committed FWC parquet are frozen (15,992 · 6,341 · 2,686 · 32,893 · 56,108 · 20,190 · 30,563 · 12,833 · 18,418 = 196,024).

## Caveats (short form; the site's §11 is the long form)

Regions advect into each other · surveillance is endogenous · labels depend on where bottles were dipped · discharge is flow, not
nutrients · wind/upwelling absent · interventional SHAP can credit a feature reached only via a correlated partner · demo, not a
forecast.

## Data credits

FWC-FWRI HAB Monitoring Database (ArcGIS Open Data) · NOAA/NCEI OISST v2.1 via CoastWatch ERDDAP · USGS NWIS.
Method refs: Lundberg & Lee 2017 (SHAP); Lundberg et al. 2020, *Nat. Mach. Intell.* (tree SHAP, interventional vs path-dependent).

---
type: index
doc_id: agents_how_pilots_hab_crash_risk
title: "what/exemplars/gulf_karenia_brevis/ — Karenia brevis bloom-onset early warning (XGBoost + SHAP, sepsis analog)"
owner: "operator (Stanley); built S329 by Berthier"
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [index, agents, pilot, hab, karenia_brevis, brevetoxin, xgboost, shap, ecosystem_risk, s329]
---

# what/exemplars/gulf_karenia_brevis/ — bloom-onset early warning

**What this is.** A self-contained, reproducible demonstration of the operator's *sepsis-early-warning → ecosystem-crash-risk*
method on public **Karenia brevis** (brevetoxin, Florida red tide) data: region × ISO-week "patients", trajectory + environment
"vitals", an onset label (≥100k cells/L within 4 weeks), an XGBoost classifier with a leakage-safe temporal split, interventional
tree-SHAP explanations, and a single-page explainer site that ends with how SHAP maps (and does not map) onto interventions.
Built in one sitting at aDNALabs (S329, 2026-09-23) and relocated here at Atlantis genesis the same day for a conversation with a freshwater-metagenomics colleague. **Method demo, not an
operational forecast** (FWC and NOAA run those).

**Owner / status.** Operator-owned pilot; not a campaign. `README.md` carries the results and the run order. Re-running the
pipeline from scratch takes < 1 h on a laptop, most of it waiting on the OISST server.

## Contents

| Path | What |
|---|---|
| `README.md` | results, run order, design decisions, caveats |
| `config.yaml` | threshold · horizon · regions (lat/lon rules) · gauges · split years · XGBoost + SHAP settings |
| `src/hab/` | `fetch_fwc` · `fetch_env` · `regions` · `build_features` (with `--self-test` leakage test) · `eda` · `train` · `explain` · `whatif` · `export_site_data` · `build_site` |
| `data/raw/` | cached downloads (FWC parquet committed; OISST chunk CSVs + env parquet committed; see `.gitignore`) |
| `data/processed/` | derived tables — **gitignored**, regenerate with `build_features` |
| `outputs/` | `metrics.json` · `model.json` · `model_no_surveillance.json` · `shap_summary.json` · `whatif.json` · `eda.json` · `site_data.json` (`shap_test.npz` gitignored) |
| `site/template.html` + `site/hab_crash_risk.html` | the explainer page (template + data-injected build); published as a claude.ai Artifact |

Dataset notes (vault-level, Atlantis): `what/datasets/dataset_fwc_hab_karenia.md` · `what/datasets/dataset_hab_env_covariates.md`.

## Rules for agents touching this folder

- **Never modify a feature without re-running `build_features --self-test`.** The leakage test is the pilot's only hard invariant.
- **Test years are scored once.** If you retune, retune on 2017–2019 and leave 2020–2023 alone.
- Interventional SHAP + the lever/proxy/artifact tags are load-bearing for the site's intervention section; do not switch to
  path-dependent SHAP without rewriting that section.
- No credentials are involved; every endpoint is anonymous public data.

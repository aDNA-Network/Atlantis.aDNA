---
type: index
doc_id: agents_how_pilots_hab_crash_risk
title: "what/exemplars/gulf_karenia_brevis/ — Karenia brevis bloom-onset early warning (XGBoost + SHAP, sepsis analog)"
owner: "operator (Stanley); built S329 by Berthier"
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [index, agents, pilot, hab, karenia_brevis, brevetoxin, xgboost, shap, ecosystem_risk, s329]
---

# what/exemplars/gulf_karenia_brevis/ — bloom-onset early warning

**What this is.** A self-contained, reproducible demonstration of the operator's *sepsis-early-warning → ecosystem-crash-risk*
method on public **Karenia brevis** (brevetoxin, Florida red tide) data: region × ISO-week "patients", trajectory + environment
"vitals", an onset label (≥100k cells/L within 4 weeks), an XGBoost classifier with a leakage-safe temporal split, interventional
tree-SHAP explanations, and a single-page explainer site that ends with how SHAP maps (and does not map) onto interventions.
Built in one sitting at aDNALabs (S329, 2026-09-23), relocated here at Atlantis genesis the same day, and brought to hygiene at P1 M-1a (2026-10-02: drift fixed, provenance hashed, packaged, no `eval`). **Method demo, not an
operational forecast** (FWC and NOAA run those).

**Owner / status.** Operator-owned pilot; not a campaign. `README.md` carries the results and the run order. Re-running the
pipeline from scratch takes < 1 h on a laptop, most of it waiting on the OISST server.

## Contents

| Path | What |
|---|---|
| `README.md` | results, run order, design decisions, caveats |
| `config.yaml` | threshold · horizon · regions (lat/lon rules, `ast`-whitelist parsed) · gauges (`lever:` flag → site tag) · split years · XGBoost + SHAP settings. **Byte-hashed into `metrics.json → config_hash`; see README §Provenance before editing.** |
| `streams.yaml` · `features.yaml` · `events.yaml` · `atlantis.yaml` | the exemplar **as an atlantis_core instance** (M-1b-i, 2026-10-02): `atl_v0` registries + engine config. `atlantis.yaml` copies values from `config.yaml` (drift-guarded by `what/atlantis_core/tests/test_registry.py`). `src/hab/` stays canonical until M-1b-ii |
| `pyproject.toml` · `uv.lock` · `.python-version` | the package (`uv sync`); `requirements.txt` retired at M-1a (2026-10-02) |
| `tests/` | `test_regions.py` — parser whitelist + the 9 frozen region counts (`python -m pytest`) |
| `src/hab/` | `fetch_fwc` · `fetch_env` · `provenance` (fetch summaries + sha256) · `regions` · `build_features` (with `--self-test` leakage test) · `eda` · `train` (+ `--negative-control`) · `explain` · `whatif` · `export_site_data` · `build_site` |
| `data/raw/` | cached downloads — three committed parquets (FWC · OISST region-daily · USGS discharge) each with a `*_fetch_summary.json` (rows · dates · sha256 · fetched_at); FWC decade layers + OISST chunk CSVs gitignored (regenerate via the fetchers) |
| `data/processed/` | derived tables — **gitignored**, regenerate with `build_features` |
| `outputs/` | `metrics.json` · `model.json` · `model_no_surveillance.json` · `shap_summary.json` · `whatif.json` · `eda.json` · `site_data.json` · `negative_control_auprc_stop.json` (T4 control) (`shap_test.npz` gitignored) |
| `site/template.html` + `site/hab_crash_risk.html` | the explainer page (template + data-injected build); published as a claude.ai Artifact |

Dataset notes (vault-level, Atlantis): `what/datasets/dataset_fwc_hab_karenia.md` · `what/datasets/dataset_hab_env_covariates.md`.

## Rules for agents touching this folder

- **Never modify a feature without re-running `build_features --self-test`** — and, for the registries, `python -m atlantis_core.selftest --instance .` from `what/atlantis_core/` (all-stream). The leakage test is the pilot's only hard invariant.
- **Test years are scored once.** If you retune, retune on 2017–2019 and leave 2020–2023 alone.
- Interventional SHAP + the lever/proxy/artifact tags are load-bearing for the site's intervention section; do not switch to
  path-dependent SHAP without rewriting that section.
- No credentials are involved; every endpoint is anonymous public data.
- **Do not edit `config.yaml` casually** — its bytes are hashed into `metrics.json`; a comment change breaks the join key. Retrain or document (README §Provenance).
- `python -m pytest` after touching `regions.py`; `python -m hab.provenance` after any raw parquet changes.

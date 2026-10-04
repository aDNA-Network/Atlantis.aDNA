---
type: dataset
doc_id: dataset_oisst_region_daily
title: "OISST v2.1 regional SST — nine Florida coastal region boxes, daily, 1982-01-01 → 2024-01-01"
dataset_class: reference
category: gridded_environment
domain: ecosystem_early_warning
summary: "NOAA OISST v2.1 daily SST averaged per region box (9 boxes), 1982-01-01 → 2024-01-01, 127,341 region-days"
owner: stanley
status: active
version: "1.0.0"
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
yaml: dataset_oisst_region_daily.dataset.yaml
stream_id: atl_stream_oisst_region_daily
supersedes_part_of: dataset_hab_env_covariates
storage_in_atlantis: grandfathered_exemplar_snapshot
fetch_recipe: "python -m atlantis_core.fetch --instance what/exemplars/gulf_karenia_brevis --stream atl_stream_oisst_region_daily --verify"
source_system: NOAA CoastWatch ERDDAP (OISST v2.1, ncdcOisst21Agg_LonPM180)
source_url: https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv
ingested_at: "2026-09-23T12:10:58Z"
sha256: c26b97f53854d57e61cdd7b9bbca0507504f82aed63faf716744a4963bbb7ec8
rows: 127341
columns: 3
license: public (NOAA / USGS)
redacted: false
audience: public
fair:
  findable:   {keywords: [sea_surface_temperature, oisst, florida]}
  accessible: {license: "public (NOAA / USGS)"}
  interoperable: {authority: "CF:sea_surface_temperature", unit: "Cel"}
  reusable: {provenance: ingest_rule_5}
tags: [dataset, oisst, sst, covariates, s329, hab_crash_risk]
---

# OISST v2.1 regional SST

Pulled 2026-09-23 by `what/exemplars/gulf_karenia_brevis/src/hab/fetch_env.py`. The values are OISST v2.1 daily 0.25° cells
inside each of the nine region boxes (`config.yaml` → `region_boxes`), averaged to one value per region per day.

Columns: `date · sst (°C) · region (1–9)`. In the pipeline, anomalies are taken against a 1982–2011 week-of-year climatology
per region. That era ends before validation (R7). The raw OISST chunk CSVs (193 MB) are gitignored in the exemplar (WI-2);
this parquet is their committed derivative.

Copy of record: `what/exemplars/gulf_karenia_brevis/data/raw/oisst_region_daily.parquet` (same bytes).

## Provenance and drift

The machine-readable twin is `dataset_oisst_region_daily.dataset.yaml`; it carries the sha256 pin, the Rule-5 provenance and the fetch parameters. Pins agree
across the twin, the exemplar's `data/raw/oisst_fetch_summary.json`, `streams.yaml`, and board entries v0 and v1. **`ingested_at` is the file's
mtime.** It was retro-summarised at M-1a, and no fetch-time record exists. `python -m atlantis_core.datasets --check
what/datasets` re-hashes these bytes against the pin.

*(Split out of `dataset_hab_env_covariates.md` at M-1d-ii, 2026-10-03, when the records moved to the pair standard: one
location and one checksum per record. That note is superseded in place.)*

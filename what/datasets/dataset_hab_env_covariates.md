---
type: dataset
doc_id: dataset_hab_env_covariates
title: "Environmental covariates for hab_crash_risk — OISST regional SST + USGS river discharge"
owner: stanley
status: superseded
superseded_by: [dataset_oisst_region_daily, dataset_usgs_discharge_daily]
superseded_on: 2026-10-03   # M-1d-ii pair migration — one location + one checksum per record
created: 2026-09-23
updated: 2026-10-03
last_edited_by: agent_proteus
source: NOAA OISST v2.1 daily (CoastWatch ERDDAP ncdcOisst21Agg_LonPM180) · USGS NWIS daily values (parameter 00060)
artifacts: [oisst_region_daily.parquet, usgs_discharge_daily.parquet]
license: public (NOAA / USGS)
redacted: false
audience: public
tags: [dataset, oisst, sst, usgs, discharge, covariates, s329, hab_crash_risk]
---

# Environmental covariates — regional SST and river discharge

> **Superseded 2026-10-03 (M-1d-ii).** The pair standard has one storage location and one checksum per record, so this
> two-artifact note split into **`dataset_oisst_region_daily`** and **`dataset_usgs_discharge_daily`**, each with its
> `.dataset.yaml` twin. Kept, unedited below this banner, per SO-2.

Pulled 2026-09-23 by `what/exemplars/gulf_karenia_brevis/src/hab/fetch_env.py`.

**SST.** OISST v2.1 daily 0.25° values inside each of the nine region boxes (`config.yaml` → `region_boxes`), averaged to one
value per region per day, 1982–2023. Anomalies in the pipeline are against a 1982–2011 week-of-year climatology per region.

**Discharge.** Daily mean discharge (cfs) 1990–2023 for five gauges: Caloosahatchee at S-79 (`02292900`, the managed Lake
Okeechobee release — the pilot's only *lever*), Peace at Arcadia (`02296750`), Hillsborough nr Tampa (`02304500`), Suwannee nr
Wilcox (`02323500`), Apalachicola nr Sumatra (`02359170`). Negative (reverse-flow) values at S-79 are clipped to zero.

Two parquets beside this note (`oisst_region_daily.parquet` — region, date, sst; `usgs_discharge_daily.parquet` — date, discharge_cfs, site);
the same bytes live at `what/exemplars/gulf_karenia_brevis/data/raw/`.

---
type: dataset
doc_id: dataset_usgs_discharge_daily
title: "USGS NWIS daily discharge — five Florida river gauges, 1990–2023"
dataset_class: reference
category: gauge_series
domain: ecosystem_early_warning
summary: "Daily mean discharge (cfs, parameter 00060) at five gauges incl. the Caloosahatchee at S-79, 1990–2023, 61,444 site-days"
owner: stanley
status: active
version: "1.0.0"
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
yaml: dataset_usgs_discharge_daily.dataset.yaml
stream_id: atl_stream_usgs_discharge_daily
supersedes_part_of: dataset_hab_env_covariates
storage_in_atlantis: grandfathered_exemplar_snapshot
fetch_recipe: "python -m atlantis_core.fetch --instance what/exemplars/gulf_karenia_brevis --stream atl_stream_usgs_discharge_daily --verify"
source_system: USGS NWIS daily values (parameter 00060)
source_url: https://waterservices.usgs.gov/nwis/dv/
ingested_at: "2026-09-23T11:20:23Z"
sha256: 66a58af41843b4305afa968dd814854a61e6a4e263f4898b5422d8eb03a789ea
rows: 61444
columns: 3
license: public (NOAA / USGS)
redacted: false
audience: public
fair:
  findable:   {keywords: [river_discharge, usgs_nwis, florida]}
  accessible: {license: "public (NOAA / USGS)"}
  interoperable: {authority: "USGS:00060", unit: "[cft_i]/s"}
  reusable: {provenance: ingest_rule_5}
tags: [dataset, usgs, discharge, covariates, s329, hab_crash_risk]
---

# USGS NWIS daily discharge

Pulled 2026-09-23 by `what/exemplars/gulf_karenia_brevis/src/hab/fetch_env.py`. These are daily mean discharge values (cfs)
from five gauges:
- Caloosahatchee at S-79 (`02292900`): the managed Lake Okeechobee release, and the pilot's only *lever*;
- Peace at Arcadia (`02296750`);
- Hillsborough nr Tampa (`02304500`);
- Suwannee nr Wilcox (`02323500`);
- Apalachicola nr Sumatra (`02359170`).

Columns: `date · discharge_cfs · site`. **Negative (reverse-flow) values were clipped to zero at fetch** (`fetch_env.py:92`),
so these bytes carry none. Tampa's gauge is not a lever, although it sits under a lever-tagged vital (WI-12).

Copy of record: `what/exemplars/gulf_karenia_brevis/data/raw/usgs_discharge_daily.parquet` (same bytes).

## Provenance and drift

The machine-readable twin is `dataset_usgs_discharge_daily.dataset.yaml`; it carries the sha256 pin, the Rule-5 provenance and the fetch parameters. Pins agree
across the twin, the exemplar's `data/raw/usgs_fetch_summary.json`, `streams.yaml`, and board entries v0 and v1. **`ingested_at` is the file's
mtime.** It was retro-summarised at M-1a, and no fetch-time record exists. `python -m atlantis_core.datasets --check
what/datasets` re-hashes these bytes against the pin.

*(Split out of `dataset_hab_env_covariates.md` at M-1d-ii, 2026-10-03, when the records moved to the pair standard: one
location and one checksum per record. That note is superseded in place.)*

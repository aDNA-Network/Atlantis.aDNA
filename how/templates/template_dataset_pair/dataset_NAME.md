---
type: dataset
dataset_class: reference            # reference | benchmark | training_data | target | result
category: <ocean_observations | gridded_environment | gauge_series | occurrence | sequence | literature>
domain: ecosystem_early_warning
summary: "<one line: what, where, when>"
status: active                      # planned → draft → active → deprecated → archived
version: "0.1.0"
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_edited_by: agent_<persona>
yaml: dataset_NAME.dataset.yaml     # the machine-readable twin (validated by the lattice-labs dataset_yaml_schema.json)
stream_id: atl_stream_<...>         # the AtlObservationStream this record describes
# --- Atlantis snapshot rule (ADR-002 §4): pointer + sha256 + fetch recipe. NO new bytes in Atlantis. ---
storage_in_atlantis: none           # none | grandfathered_exemplar_snapshot
fetch_recipe: "python -m atlantis_core.fetch <stream_id>"   # or the exemplar module
# --- Ingest.aDNA Rule 5 provenance ---
source_system: "<FWC ArcGIS Hub | NOAA CoastWatch ERDDAP | USGS NWIS | NOAA CRW | OBIS | NCBI SRA | …>"
source_id: "<layer id / dataset id / site / BioProject>"
source_url: "<url>"
captured_at: "<when the source last updated>"
ingested_at: "<when fetched>"
pipeline_version: "<fetcher version>"
sha256: "<of the cached artifact in the INSTANCE>"
rows: 0
license: "<SPDX or agency terms>"
redacted: false
audience: public                    # public | partner | internal_only
fair:
  findable:   {keywords: [<taxon>, <region>, <variable>]}
  accessible: {license: "<SPDX>"}
  interoperable: {authority: "<CF:… | WoRMS:… | dwc:…>", unit: "<UCUM>"}
  reusable: {provenance: ingest_rule_5}
tags: [dataset, atlantis, <stream>]
---

# <Dataset title>

## Overview
What it is, who produces it, what the exemplar/instance uses it for.

## Schema
Columns · units (UCUM) · the authority each variable is named in · the observation_long mapping (dwc / CF names).

## Provenance and drift
Server count asserted vs fetched · `sha256` · how a re-fetch detects drift · known quirks (negative tidal flow clipped;
location strings not trusted — coordinates only).

## Known limits
Coverage gaps · early-decade sparsity · surveillance endogeneity flag.

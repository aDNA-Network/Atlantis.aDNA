---
type: dataset
doc_id: dataset_fwc_hab_karenia
title: "FWC HAB monitoring archive — Karenia brevis cell counts, Florida, 1970–2023"
dataset_class: reference
category: ocean_observations
domain: ecosystem_early_warning
summary: "Karenia brevis cells/L in 196,024 Florida water samples, 1970-10-01 → 2023-12-30 (FWC-FWRI, six decade layers)"
owner: stanley
status: active                       # was `snapshot` (ad-hoc frontmatter) until the M-1d-ii pair migration
version: "1.0.0"
created: 2026-09-23
updated: 2026-10-03
last_edited_by: agent_proteus
yaml: dataset_fwc_hab_karenia.dataset.yaml
stream_id: atl_stream_fwc_hab_karenia
storage_in_atlantis: grandfathered_exemplar_snapshot   # ADR-002 §4 — one of the only three files Atlantis carries
fetch_recipe: "python -m atlantis_core.fetch --instance what/exemplars/gulf_karenia_brevis --verify   # the exemplar re-hashes its cache; a network fetch is refused there (no posture pin, no new snapshots)"
source_system: FWC-FWRI HAB Monitoring Database via ArcGIS Open Data (Historic Harmful Algal Bloom Events, six decade layers)
source_url: https://gis.myfwc.com/mapping/rest/services/Open_Data/Historic_Harmful_Algal_Bloom_Events_<A>___<B>/MapServer/<n>
ingested_at: "2026-09-23T11:22:13Z"
sha256: 2bde141038e87db37dd682561d47e525dc546189d2ae6fbecfaf1a53bcfecfd9
rows: 196024
columns: 10
license: public (Florida public records; credit FWC-FWRI)
redacted: false
audience: public
fair:
  findable:   {keywords: [karenia_brevis, red_tide, florida, cell_count]}
  accessible: {license: "public (Florida public records; credit FWC-FWRI)"}
  interoperable: {authority: "WoRMS:233015", unit: "/L"}
  reusable: {provenance: ingest_rule_5}
tags: [dataset, hab, karenia_brevis, brevetoxin, red_tide, florida, fwc, s329, hab_crash_risk]
---

# FWC HAB monitoring archive — *Karenia brevis* cell counts

Snapshot pulled 2026-09-23 by `what/exemplars/gulf_karenia_brevis/src/hab/fetch_fwc.py` (paginated ArcGIS REST, 2,000 rows per page).
Every row is a water sample with date, position, depth, free-text location and *K. brevis* cells per litre. All six layers are
*K. brevis* only (verified: zero rows with another `NAME`).

| Layer | MapServer | Rows (server count = fetched) |
|---|---|---|
| 1970–1979 | /2 | 5,807 |
| 1980–1989 | /3 | 5,414 |
| 1990–1999 | /4 | 16,832 |
| 2000–2006 | /5 | 27,354 |
| 2007–2014 | /6 | 52,744 |
| 2015–2023 | /12 | 87,873 |

Columns: `objectid · hab_id · sample_date · lat · lon · depth_m · location · species · cells_per_l · layer`.
78% of samples are zero counts; the 90th percentile is ~3×10⁴ cells/L, the 99th ~1.7×10⁶.
`LOCATION` naming conventions differ between decade layers — **assign regions from lat/lon only** (`src/hab/regions.py`).

Copy of record: `what/exemplars/gulf_karenia_brevis/data/raw/fwc_hab_karenia_1970_2023.parquet` (this file is the same bytes).

## Provenance and drift

The machine-readable twin is `dataset_fwc_hab_karenia.dataset.yaml`; it carries the sha256 pin, the Rule-5 provenance and the
fetch parameters. Pins agree across the twin, the exemplar's `data/raw/fwc_fetch_summary.json`, `streams.yaml`, and board
entries v0 and v1. `ingested_at` comes from the S329 legacy summary, which predates sha256 and was kept at M-1a.
`python -m atlantis_core.datasets --check what/datasets` re-hashes these bytes against the pin.

*(Migrated to the pair standard at M-1d-ii, 2026-10-03; the body above is the S329 note, unchanged.)*

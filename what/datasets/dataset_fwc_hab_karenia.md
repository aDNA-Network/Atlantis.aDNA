---
type: dataset
doc_id: dataset_fwc_hab_karenia
title: "FWC HAB monitoring archive — Karenia brevis cell counts, Florida, 1970–2023"
owner: stanley
status: snapshot
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
source: FWC-FWRI HAB Monitoring Database via ArcGIS Open Data (Historic Harmful Algal Bloom Events, six decade layers)
source_url: https://gis.myfwc.com/mapping/rest/services/Open_Data/Historic_Harmful_Algal_Bloom_Events_<A>___<B>/MapServer/<n>
artifact: fwc_hab_karenia_1970_2023.parquet
rows: 196024
columns: 10
license: public (Florida public records; credit FWC-FWRI)
redacted: false
audience: public
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

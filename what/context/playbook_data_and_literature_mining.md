---
type: context
doc_id: playbook_data_and_literature_mining
title: "Playbook — mining the data and literature for a new regional instance (v0)"
status: proposed
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [playbook, data_discovery, literature_mining, erddap, arcgis, nwis, ndbc, atlantis]
---

# Playbook — mining the data and the literature for a new instance

Written from the S329 discovery arc (Florida, *K. brevis*), which found and verified four public streams in
under an hour, and hit every trap below at least once.

## A. Data discovery, in the order that worked

1. **State / agency open-data portals first** (ArcGIS Hub: `hub.arcgis.com/api/v3/datasets?q=<taxon or program>`;
   a state's `geodata.<agency>` Hub search API). Monitoring archives are usually ArcGIS MapServer layers with
   `maxRecordCount=2000` — paginate on `resultOffset`, **assert the server's `returnCountOnly` count against what
   you fetched**, and store the count in the dataset note so a re-fetch can detect drift.
2. **Gridded environment via ERDDAP griddap** (NOAA CoastWatch `coastwatch.pfeg.noaa.gov/erddap`; OISST v2.1
   daily SST `ncdcOisst21Agg_LonPM180`; chlorophyll, SSH, winds are siblings). Subset by time/lat/lon box as CSV;
   one box per patient region; **fetch per region per 5-year chunk in parallel workers with atomic cache writes**
   (the single-process run measured ~1 chunk/min over 81 chunks). Expect 408s; retry with backoff.
3. **River gauges via USGS NWIS** (`waterservices.usgs.gov/nwis/dv`, parameter `00060` discharge; `00095`,
   `00300`, `00400` for conductance, DO, pH where present). Managed structures (Florida's S-79) are the only
   genuine *levers* in most coastal datasets — find them.
4. **Buoys via NDBC historical stdmet** (`view_text_file.php?filename=<station>h<yyyy>.txt.gz`) for wind,
   waves, water temp. Optional at v1; physically important for transport.
5. **Biological / sequence archives** for eDNA and metagenomic instances: OBIS, GBIF, NCBI SRA / ENA (BioProject
   by region), MGnify; regional cruise data (e.g. CalCOFI, Chesapeake Bay Program's water-quality + phytoplankton
   tables). Translation here is taxon-abundance → vitals; the patient grid is the cruise cadence.
6. **What not to depend on:** NCEI landing pages and archive-management URLs returned 503 all session; use
   the ERDDAP mirrors and the originating agency instead.

## B. Traps, each hit once

- **Assign space by coordinates, never by names.** Location strings changed convention across decade layers;
  a coordinate rule is the only consistent key. Then **check the longitude distribution per region**: our first
  rule put 11,379 Atlantic-coast samples into Gulf regions.
- **Probe before you believe a zero.** A `returnDistinctValues` query returned no `features` key; a variable
  that shell-expanded to nothing produced empty counts. A zero measures your question first.
- **Surveillance is endogenous.** Sampling intensifies during events. Keep sample counts as explicit, flagged
  features; ablate them; report the single-feature baseline.
- **Early decades are sparse.** Count samples per year before choosing `min_train_year`.
- **Reverse flow at tidal gauges is negative.** Clip, and say so in the dataset note.

## C. Literature mining (the P3 lane — design, not yet built)

Purpose: turn a region's literature into *feature hypotheses with provenance*, not into prose.

1. **Corpus:** OpenAlex / Semantic Scholar / Europe PMC queries by taxon × region × mechanism; agency reports
   (FWC, NOAA HAB bulletins, state water-quality assessments); grey literature via the agency portals above.
2. **Extraction target (per paper):** {mechanism claimed, driver variable, lag, direction, threshold if any,
   region, evidence class (observational / experimental / model), citation}. This is a table, and every row
   points at a sentence.
3. **Translation:** each row becomes a candidate vital (driver at lag, in the region's units) with a
   `hypothesis_source` field; the model then *tests* the literature — a feature the papers insist on that carries
   no SHAP is a finding worth writing up.
4. **Federation:** `Ingest.aDNA` (Demeter) owns intake-with-provenance in the fleet; the lane composes it when
   the corpus exists rather than re-inventing winnowing.

# Discovery memo — gulf_karenia_brevis

*`atlantis_core.discover` atlantis_core 0.8.0 · generated 2026-10-11T01:59:12+00:00 · probed: True (gis.myfwc.com ×6, coastwatch.pfeg.noaa.gov ×1, waterservices.usgs.gov ×5)*

Summary numbers only. Nothing here was fetched or cached; `streams.discovered.yaml` holds pointer rows (no sha256, no row count), and `streams.yaml` was not written. With --probe, NWIS series are read in memory (day-by-day comparison; III M-3a F-2); every other probe is a count or metadata.

**Limit of the compare:** a match shows the skill can express the registry's rows; when the searcher already knew the registry (a rehearsal), it does not show a blind search would have found them.

## Request

- **grid_kind:** rules
- **event_stream:** atl_stream_fwc_hab_karenia
- **event_variable:** Karenia brevis
- **ecosystem:** estuary + inner shelf — west Florida coast, eastern Gulf of Mexico (red tide, K. brevis)

## Searched (playbook §A)

| Step | Where | Found | Note |
|---|---|---|---|
| A1 | ArcGIS Hub search API (hub.arcgis.com/api/v3/datasets?q=harmful algal bloom Karenia Florida); FWC Open Data MapServer (gis.myfwc.com) | atl_stream_fwc_hab_karenia | Sampling intensifies during blooms (FWC responds to reports) → surveillance channel (T5). Licence: Florida public records, credit FWC-FWRI. |
| A2 | NOAA CoastWatch ERDDAP search (coastwatch.pfeg.noaa.gov/erddap/search?searchFor=ncdcOisst21Agg) | atl_stream_oisst_region_daily | One box per unit (atlantis.yaml boxes), nearshore Gulf side. Chlorophyll, SSH and wind siblings exist; not carried at v1. |
| A3 | USGS NWIS site service (waterservices.usgs.gov/nwis/site), parameter 00060 | atl_stream_usgs_discharge_daily | clip_negative is declared (S329's code comment: 'S-79 reports reverse flow as negative'). At M-3a the daily-values series served no negative day at any of the five gauges, S-79 included; whether it ever did is not on record (trap 5). |
| A4 | NDBC station pages (e.g. 42013, west Florida shelf; HTTP 200 on 2026-10-10) | — | Stations exist; not carried. NDBCStdmet is a declared, not built, fetcher, and buoys are optional at v1 (playbook §A4). |
| A5 | OBIS / GBIF occurrence by taxon (Karenia brevis, WoRMS 233015) | — | Not carried: FWC's monitoring database is the system of record; the aggregators republish subsets of it, so carrying both would double-count samples. OBIS/GBIF fetchers are declared, not built. |
| A6 | NCEI landing pages and archive-management URLs (S329) | — | NCEI returned 503 all S329 session; the ERDDAP mirror and the originating agencies were used instead. Nothing new tried at M-3a. |

## Rows

| stream_id | modality | source_system · source_id | fetcher | surveillance |
|---|---|---|---|---|
| `atl_stream_fwc_hab_karenia` | point_count | FWC-FWRI HAB Monitoring Database via ArcGIS Open Data · `Historic_Harmful_Algal_Bloom_Events (six decade layers)` | ArcGISMapServer | True |
| `atl_stream_oisst_region_daily` | gridded_field | NOAA CoastWatch ERDDAP · `ncdcOisst21Agg_LonPM180` | ERDDAPGriddap | False |
| `atl_stream_usgs_discharge_daily` | gauge_series | USGS NWIS daily values · `parameter 00060 at five gauges (config.yaml -> gauges)` | NWISDailyValues | False |

**Compare** against `streams.yaml` (declarative fields): identical.


## Traps (playbook §B)

| Trap | Status | Note |
|---|---|---|
| server_count | ☑ accepted | ArcGIS: returnCountOnly per layer vs the fetch summary (a count) · ERDDAP: the time axis must cover the fetched range (coverage only — not a count, not values) · NWIS: the series read in memory, day by day, vs the cache (days only on the server, days only in the cache, values revised) |
| longitude_by_unit | ☑ accepted | bounds: atl_stream_oisst_region_daily fetch.boxes; a point counts as outside beyond ±0.5° (warn) and ±1.0° (fail if > 1% of a unit's points). Unassigned points are dropped by vitals.build without a count; the count is here. A rule grid's box is a proxy for the unit, not its boundary: a fail asks for a ruling, not a re-grid. |
| probe_zero | — na | 12 probe answers, none zero or broken: the trap had nothing to test |
| samples_per_year | ⚠ warn | counts from the first year on record; a year is sparse below 25% of the median year in 1994–2023; min_train_year is 1994. A warn asks whether the sparse years should train — it does not move min_train_year (that is a vitals change, SO-7). |
| negative_flow | ✅ pass |  |
| surveillance_declared | ✅ pass | registry R8 (contract item 5) |

### server_count — accepted

> Ruled (stanley (operator), 2026-10-10; accepts atl_stream_usgs_discharge_daily:site 02359170): Accepted; the pinned bytes stand. USGS 02359170 now serves 458 days more than the cache (2022-06-21 → 2023-09-23, backfilled; qualifiers A/R and A/e, read at the ruling by an in-memory script, not by this code) and 45 shared days carry revised values, partly inside the 2020–2023 test window. The day and value counts are re-measured by discover's NWIS comparison from M-3a's III fixes on (memo, server_count). The sha256-pinned parquet is the exemplar's record; a re-fetch is a new pin and a new board version. 'Refresh 02359170' is carried as an open item.

```yaml
atl_stream_fwc_hab_karenia:
- what: layer 1970___1979
  server: 5807
  fetched: 5807
  status: pass
  why: ''
- what: layer 1980___1989
  server: 5414
  fetched: 5414
  status: pass
  why: ''
- what: layer 1990___1999
  server: 16832
  fetched: 16832
  status: pass
  why: ''
- what: layer 2000___2006
  server: 27354
  fetched: 27354
  status: pass
  why: ''
- what: layer 2007___2014
  server: 52744
  fetched: 52744
  status: pass
  why: ''
- what: layer 2015___2023
  server: 87873
  fetched: 87873
  status: pass
  why: ''
atl_stream_oisst_region_daily:
- what: dataset ncdcOisst21Agg_LonPM180 time steps
  server: 15265
  server_range:
  - '1981-09-01'
  - '2026-09-25'
  fetched_range:
  - '1982-01-01'
  - '2024-01-01'
  status: pass
  why: ''
atl_stream_usgs_discharge_daily:
- what: site 02292900
  server: 12305
  fetched: 12305
  server_only_days: 0
  cache_only_days: 0
  revised_values: 0
  status: pass
  why: ''
- what: site 02296750
  server: 12418
  fetched: 12418
  server_only_days: 0
  cache_only_days: 0
  revised_values: 0
  status: pass
  why: ''
- what: site 02304500
  server: 12349
  fetched: 12349
  server_only_days: 0
  cache_only_days: 0
  revised_values: 0
  status: pass
  why: ''
- what: site 02323500
  server: 12418
  fetched: 12418
  server_only_days: 0
  cache_only_days: 0
  revised_values: 0
  status: pass
  why: ''
- what: site 02359170
  server: 12412
  fetched: 11954
  server_only_days: 458
  cache_only_days: 0
  revised_values: 45
  server_only_span:
  - '2022-06-21'
  - '2023-09-23'
  status: fail
  why: a re-fetch would differ
```

### longitude_by_unit — accepted

> Ruled (stanley (operator), 2026-10-10; accepts atl_stream_fwc_hab_karenia:2, atl_stream_fwc_hab_karenia:3, atl_stream_fwc_hab_karenia:8): Accepted, recorded, carried. The rule grid assigns by latitude band, so open-Gulf samples pool into coastal units: units 2 (2.46%), 3 (4.95%) and 8 (1.49%) hold > 1% of points over 1° outside their OISST boxes. A method demonstration whose pooling is a known limit, now measured. Re-gridding the exemplar by coordinates is carried to the P3 gate as an open item; no vitals change now (SO-7).

```yaml
atl_stream_fwc_hab_karenia:
  units:
    '1':
      n: 15992
      lon_min: -88.49
      lon_median: -85.71
      lon_max: -84.5
      box:
      - 29.6
      - 30.4
      - -87.6
      - -84.5
      out_tol: 4
      out_gross: 0
      out_gross_frac: 0.0
    '2':
      n: 6341
      lon_min: -88.0
      lon_median: -83.46
      lon_max: -81.7
      box:
      - 29.0
      - 30.2
      - -84.5
      - -83.0
      out_tol: 246
      out_gross: 156
      out_gross_frac: 0.0246
    '3':
      n: 2686
      lon_min: -87.87
      lon_median: -82.78
      lon_max: -82.59
      box:
      - 28.4
      - 29.0
      - -83.4
      - -82.5
      out_tol: 202
      out_gross: 133
      out_gross_frac: 0.0495
    '4':
      n: 32893
      lon_min: -88.9
      lon_median: -82.67
      lon_max: -80.61
      box:
      - 27.6
      - 28.4
      - -83.2
      - -82.4
      out_tol: 407
      out_gross: 150
      out_gross_frac: 0.0046
    '5':
      n: 56108
      lon_min: -88.08
      lon_median: -82.58
      lon_max: -82.01
      box:
      - 27.0
      - 27.6
      - -83.0
      - -82.2
      out_tol: 379
      out_gross: 136
      out_gross_frac: 0.0024
    '6':
      n: 20190
      lon_min: -87.23
      lon_median: -82.28
      lon_max: -81.62
      box:
      - 26.6
      - 27.0
      - -82.8
      - -82.0
      out_tol: 469
      out_gross: 118
      out_gross_frac: 0.0058
    '7':
      n: 30563
      lon_min: -86.84
      lon_median: -81.97
      lon_max: -80.82
      box:
      - 25.9
      - 26.6
      - -82.6
      - -81.6
      out_tol: 479
      out_gross: 187
      out_gross_frac: 0.0061
    '8':
      n: 12833
      lon_min: -88.87
      lon_median: -81.58
      lon_max: -80.6
      box:
      - 24.4
      - 25.9
      - -82.2
      - -80.6
      out_tol: 523
      out_gross: 191
      out_gross_frac: 0.0149
    '9':
      n: 18418
      lon_min: -81.68
      lon_median: -80.63
      lon_max: -77.26
      box:
      - 25.0
      - 30.7
      - -80.6
      - -79.8
      out_tol: 3302
      out_gross: 33
      out_gross_frac: 0.0018
  unassigned: 0
  bounds: atl_stream_oisst_region_daily fetch.boxes
  failing_units:
  - '2'
  - '3'
  - '8'
atl_stream_oisst_region_daily:
  shape: unit_daily
  assigned_by: the fetch spec's per-unit request
atl_stream_usgs_discharge_daily:
  shape: station_daily
  assigned_by: the declared station → unit map
```

### probe_zero — na

```yaml
answers: 12
zero_or_broken: 0
```

### samples_per_year — warn

```yaml
atl_stream_fwc_hab_karenia:
  years:
    1970: 1
    1971: 477
    1972: 196
    1973: 114
    1974: 1744
    1975: 421
    1976: 918
    1977: 530
    1978: 787
    1979: 619
    1980: 919
    1981: 171
    1982: 684
    1983: 372
    1984: 222
    1985: 138
    1986: 276
    1987: 1118
    1988: 780
    1989: 734
    1990: 804
    1991: 1162
    1992: 1096
    1993: 687
    1994: 1218
    1995: 2608
    1996: 2668
    1997: 1703
    1998: 1694
    1999: 3192
    2000: 3800
    2001: 3407
    2002: 3168
    2003: 3670
    2004: 2273
    2005: 4421
    2006: 6615
    2007: 6931
    2008: 5726
    2009: 6340
    2010: 5915
    2011: 6246
    2012: 6726
    2013: 7449
    2014: 7411
    2015: 6806
    2016: 8876
    2017: 9589
    2018: 11966
    2019: 10336
    2020: 7251
    2021: 12195
    2022: 9717
    2023: 11137
  median_year: 6293.0
  sparse_years:
  - 1994
  first_year_on_record: 1970
  earliest_min_train_year_with_no_sparse_year: 1995
atl_stream_oisst_region_daily:
  years:
    1982: 3285
    1983: 3285
    1984: 3294
    1985: 3285
    1986: 3285
    1987: 3285
    1988: 3294
    1989: 3285
    1990: 3285
    1991: 3285
    1992: 2925
    1993: 1458
    1994: 1242
    1995: 1530
    1996: 1530
    1997: 1584
    1998: 2151
    1999: 3285
    2000: 3294
    2001: 3285
    2002: 3285
    2003: 3285
    2004: 3294
    2005: 3285
    2006: 3285
    2007: 3285
    2008: 3294
    2009: 3285
    2010: 3285
    2011: 3285
    2012: 3294
    2013: 3285
    2014: 3285
    2015: 3285
    2016: 3294
    2017: 3285
    2018: 3285
    2019: 3285
    2020: 3294
    2021: 3267
    2022: 3276
    2023: 3177
  median_year: 3285.0
  sparse_years: []
  first_year_on_record: 1982
  earliest_min_train_year_with_no_sparse_year: 1982
atl_stream_usgs_discharge_daily:
  years:
    1990: 1825
    1991: 1825
    1992: 1830
    1993: 1825
    1994: 1825
    1995: 1825
    1996: 1830
    1997: 1823
    1998: 1821
    1999: 1824
    2000: 1826
    2001: 1822
    2002: 1824
    2003: 1825
    2004: 1823
    2005: 1792
    2006: 1825
    2007: 1825
    2008: 1817
    2009: 1802
    2010: 1825
    2011: 1818
    2012: 1830
    2013: 1815
    2014: 1820
    2015: 1798
    2016: 1812
    2017: 1820
    2018: 1812
    2019: 1818
    2020: 1829
    2021: 1825
    2022: 1631
    2023: 1557
  median_year: 1822.5
  sparse_years: []
  first_year_on_record: 1990
  earliest_min_train_year_with_no_sparse_year: 1990
```

### negative_flow — pass

```yaml
atl_stream_usgs_discharge_daily:
  clip_negative: true
  negatives_in_cache: 0
  server_negatives:
    site 02292900: 0
    site 02296750: 0
    site 02304500: 0
    site 02323500: 0
    site 02359170: 0
  server_nodata_sentinels:
    site 02292900: 0
    site 02296750: 0
    site 02304500: 0
    site 02323500: 0
    site 02359170: 0
  why: no negative day served
```

### surveillance_declared — pass

```yaml
declared: present
streams:
- atl_stream_fwc_hab_karenia
```


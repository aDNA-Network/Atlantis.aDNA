---
type: skill
skill_type: agent
created: 2026-10-10
updated: 2026-10-10
status: draft
category: knowledge
trigger: "A steward needs to know which observation streams exist for their patient and event — 'what data is there for <region>', 'find the streams', before or after a fork; P3 M-3a; P4's outside steward after the interview"
last_edited_by: agent_proteus
mission: mission_m3a_stream_discovery_skill
tags: [skill, atlantis, discovery, streams, playbook, traps, erddap, arcgis, nwis, ndbc, obis, so3, tidewatch]

requirements:
  tools: ["Bash", "WebSearch", "WebFetch", "AskUserQuestion"]
  context: ["Atlantis.aDNA/CLAUDE.md", "what/context/playbook_data_and_literature_mining.md", "what/schema/atl_v0/README.md"]
  permissions: ["write <instance>/discovery/ only", "public probe requests (--probe): counts and metadata; NWIS daily series read in memory", "NO fetch, NO cache, NO edit of streams.yaml"]
---

# Skill: stream discovery

## Overview

This skill answers one question for one instance: **which observation streams exist for this patient and this event,
where do they live, and under what licence?** It is playbook §A (the S329 discovery arc) as steps, with §B's traps as
checks. It ends in two files in `<instance>/discovery/`:
- `streams.discovered.yaml` holds AtlObservationStream **pointer rows**: source, id, authority, unit, licence,
  fetcher and surveillance flag.
- `discovery_memo.md` / `.json` records what was searched (the empty searches too), the six traps, and every host a
  probe touched.

**Discovery fetches nothing** (SO-3, ADR-002 §4).
- A pointer row has no `sha256`, `ingested_at` or `row_count`. Those are what a fetch proves, and the fetch is gated
  separately on a self-test receipt and a ratified posture (`skill_atlantis_instance_fork` step 6).
- `--probe` adds public requests, by operator ruling 2026-10-10. They are counts and metadata (ArcGIS `returnCountOnly`,
  ERDDAP `info`), except **NWIS, whose daily series is read in memory**: the ruling asked for reverse-flow counts
  before the clip, and a gauge's content can only be compared day by day (III M-3a F-2). It never caches, and only
  summary numbers reach the memo.
- The steward copies accepted rows into `streams.yaml`. Discovery never writes that file.

Proteus asks first: *what is the patient, what is the event, and how much warning would change what you do?* The streams
answer the second half of that question. Discovery that starts from "what data is there" finds data. Discovery that starts
from the event finds the data that can see it coming.

## Trigger

```
/skill_stream_discovery instance=<path>            # after a fork: the patient and event are declared
/skill_stream_discovery instance=<path> probe=true # add the probes
```

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `instance` | path | yes | — | An instance with `atlantis.yaml` (the patient: a pinned geometry or a rule grid) and an event declared. Discovery for a not-yet-forked steward runs on a rehearsal fork |
| `ecosystem` | string | yes | — | The ecosystem type (estuary · coral reef · shelf · river · lake). It chooses which §A steps can find anything, and the memo records it |
| `probe` | bool | no | false | Public requests to each declared stream's source: counts and metadata, plus NWIS series in memory (traps 1, 3, 5) |

## Requirements

- `A=<Atlantis.aDNA>/what/atlantis_core`, synced (`uv sync`).
- **Inputs, which the CLI checks against the instance:**
  - **the patient geometry pointer:** `atlantis.yaml → grid` (`grid_sha256` for polygons, `grid_kind` for rules);
  - **the event variable:** `event_stream` plus its `variable`;
  - **the ecosystem type.**
- No credentials. A source that needs one is recorded with the credential's **name** and left for the Home broker at fetch.

## Steps

### 0. Open the record

Create `<instance>/discovery/candidates.yaml` with a `request` block. It holds the four input fields above, copied from
the instance, and the CLI refuses a request that does not match. Each step below appends one `searched` row:
`{step, where, query, found: [stream_id…], note}`. A step that found nothing still gets a row, with `found: []` and a
note saying why. The CLI refuses a sitting that leaves a step unaccounted for. A step skipped in silence is a stream
nobody looked for.

### A1. State and agency open-data portals first

- **Where to search:**
  - ArcGIS Hub, `hub.arcgis.com/api/v3/datasets?q=<taxon or program>`;
  - a state's `geodata.<agency>` Hub search;
  - the monitoring programme's own site.
- **What you are looking for:** monitoring archives are usually **ArcGIS MapServer layers** (`maxRecordCount` 2,000).
- **Record:**
  - the layer URLs and the licence string as the agency states it;
  - whether the sampling effort reacts to events, which makes the stream a surveillance channel (§B, T5).
- **Candidate row:** `fetcher: ArcGISMapServer`, `modality: point_count` for counts and samples.

### A2. Gridded environment via ERDDAP griddap

- **Where to search:**
  - NOAA CoastWatch, `coastwatch.pfeg.noaa.gov/erddap/search/index.json?searchFor=<variable>`;
  - Coral Reef Watch, `coastwatch.noaa.gov/erddap`;
  - regional IOOS ERDDAPs.
- **Record:** the dataset id, its CF standard name (the `authority` CURIE: `CF:` where one exists, otherwise the
  product's own vocabulary, such as `NOAACRW:`), the UCUM unit and the time coverage.
- **Candidate row:** `fetcher: ERDDAPGriddap`, or `CoralReefWatch` for CRW products reduced over polygon zones;
  `modality: gridded_field`.

### A3. River gauges via USGS NWIS

- **Where to search:** USGS site search by HUC or bounding box, for parameter `00060` discharge. Also look for `00095`,
  `00300` and `00400` (conductance, DO and pH).
- **Look for managed structures.** A release from a structure such as Florida's S-79 is the only genuine **lever** in most
  coastal datasets. Name its owner.
- **Tidal gauges report reverse flow as negative.** Declare `clip_negative: true` in the fetch spec, or keep negative
  flow by a ruling (trap 5).
- **Candidate row:** `fetcher: NWISDailyValues`, `modality: gauge_series`.
- **A coral reef or open shelf usually has no gauge.** Record `found: []` with that reason.

### A4. Buoys via NDBC historical stdmet

- **Where to search:** NDBC station pages within the patient's envelope, for wind, waves and water temperature.
- **Candidate row:** `fetcher: NDBCStdmet`, `modality: buoy_series`.
- **This fetcher is declared, not built.** A row that needs it records the need. Building it is an Atlantis template
  change, done in Atlantis, never in the instance.
- Optional at v1; physically important for transport.

### A5. Biological and sequence archives

- **Where to search:**
  - OBIS and GBIF, by taxon and envelope;
  - NCBI SRA and ENA (BioProjects by region) and MGnify;
  - regional cruise programmes such as CalCOFI and the Chesapeake Bay Program.
- **What you are looking for:** eDNA and metagenomic instances translate taxon abundance into vitals, so the patient grid
  is the cruise cadence.
- **Candidate row:** `fetcher: OBISOccurrence` or `GBIFOccurrence` (declared, not built); `modality: edna_profile` or
  `survey_log`.

### A6. What not to depend on

- Record the sources tried that failed, such as NCEI landing pages that returned 503 all session.
- Record the mirror used instead, such as the ERDDAP mirror or the originating agency.
- This step is a row even when nothing failed.

### Candidates

Each stream found becomes one entry in `candidates:`, carrying exactly the AtlObservationStream declarative fields:
`stream_id` (`atl_stream_<slug>`), `modality`, `source_system`, `source_id`, `authority`, `variable`, `unit` (UCUM),
`license`, `fetcher` and `surveillance_channel` (always stated, true or false). Add `step` (A1–A6) and `note`.
- **Licence or posture unclear:** stop. Write a memo to the instance owner and leave the stream out, not guessed (card
  escalation trigger).
- **Partner or human-subject data:** the instance's posture ADR must be ratified first. Atlantis supplies the pattern,
  not the permission.

### 7. Run the checks

```
$A/.venv/bin/python -m atlantis_core.discover --instance <instance> --compare <instance>/streams.yaml           # offline
$A/.venv/bin/python -m atlantis_core.discover --instance <instance> --compare <instance>/streams.yaml --probe   # + probes
```

`--compare` is used when a `streams.yaml` already exists: a re-discovery must reproduce its declarative fields. **A match
shows the skill can express the registry's rows.** When the searcher already knew the registry, as in a rehearsal, it
does not show that a blind search would have found them; the memo says so. An unprobed run will not overwrite a probed
memo unless `--overwrite-probed` is given. The six traps, playbook §B:

| Trap | Check | Reads |
|---|---|---|
| `server_count` | ArcGIS: `returnCountOnly` per layer against the fetch summary, a true count · ERDDAP: the time axis must **cover** the fetched range, which is coverage, not a count and not values · NWIS: the series in memory against the cache, day by day (server-only days, cache-only days, revised values) | probe |
| `longitude_by_unit` | Per unit: lon min/median/max; points beyond ±0.5° (warn) and ±1° (**fail** above 1% of a unit) of the unit's declared space; the unassigned count, which `vitals.build` drops silently. Point streams only. A gridded stream reports its reduction instead (fallback zones) | cache |
| `probe_zero` | Every empty or keyless answer is re-asked with a control the server must answer (layer metadata · ERDDAP `/version` · the NWIS site service). A reply without the asked-for key is a **broken question**, never a zero. The control shows the source exists, **not** that the zero is true. With no zero met the trap is `na`, not a pass | probe |
| `samples_per_year` | Rows per year **from the first year on record** to `test_end`, against the median year of `min_train_year`…`test_end`. A year below 25% of it is sparse, and the event stream sets the status. It reports the earliest `min_train_year` with no sparse year after it. It never moves `min_train_year`, which would be a vitals change (SO-7) | cache |
| `negative_flow` | Negative days served, per gauge, before the clip. NWIS no-data sentinels are counted apart: a clip would read one as zero flow. Offline, only what survived in the cache | probe / cache |
| `surveillance_declared` | Registry R8 (contract item 5): present with a vital and an ablation, or absent with a reason | declarations |

The thresholds come from `candidates.yaml → checks` (`lon_tolerance_deg` · `lon_gross_deg` · `lon_max_out_frac` ·
`sparse_year_frac`). The memo records the values used.

### 8. Read, rule, hand off

- **`warn`:** look at it with the steward. Nothing is known to be wrong.
- **`fail`:** the steward rules. Either fix the source declaration, or accept the result in
  `candidates.yaml → rulings.<trap>: {ruling, by, date, accepts: [failure keys]}`. A ruling missing any field is refused.
  **A ruling accepts the failures it names, never the trap:** a later failure it does not name shows as *ruling stale*,
  and the trap fails again (III M-3a F-1). An accepted fail shows as `accepted`, with the ruling beside it.
- **Ask with `AskUserQuestion`.** A ruling on the exemplar or on a live instance is the operator's or the steward's, never
  the agent's.
- **Hand-off:** the steward copies the accepted rows into `streams.yaml`, adds the engine shape to `atlantis.yaml → streams`,
  re-runs the self-test (SO-7) and only then fetches. Commit `discovery/` with a path-scoped `git add`.
- **A partner or human-subject instance's memo stays in the instance.** It carries per-unit coordinate ranges, so it is
  never copied into Atlantis or onto the board.

## Outputs

`<instance>/discovery/`:
- `candidates.yaml` (the sitting's record);
- `streams.discovered.yaml` (pointer rows that validate against atl_v0);
- `discovery_memo.md` and `.json` (summary numbers only).

The exit code is 0 when the rows validate, the compare is empty and no trap fails unruled.

## Known limits

- **The search is the agent's.** The checks cover what was found, not what was missed. A missed source shows up only as a
  thin `searched` row, which is why every step must have one.
- **A rule grid declares no geometry.** `longitude_by_unit` reads a gridded stream's per-unit `boxes` as the unit's space.
  The boxes are a proxy, not a boundary, so its fail asks for a ruling, not a re-grid. Polygons are checked against
  their own bounding boxes, and containment makes those pass by construction.
- **Probes exist for ArcGIS, ERDDAP/CRW and NWIS only.** NDBC, OBIS and GBIF are declared fetchers with no probe. Their
  traps report `na` with the reason.
- **`server_count` is a count only on ArcGIS.** ERDDAP is checked for coverage, and a value revised inside a covered
  range is not seen. NWIS is compared day by day, so its revised values *are* seen.
- **Server-count drift is a fail by design.** A source revised since the fetch means a re-fetch would differ. The ruling
  decides whether to re-fetch, which is a new data pin and a new board version, or to accept it.

## Rehearsal of record

M-3a (2026-10-10): run on the exemplar (pointer rows only; 12 requests, two fails accepted by the operator) and on
FloridaKeysCoral (3 requests; clean). On FKNMS two traps are `na` and `probe_zero` met no zero, so the non-trivial trap
paths ran on real data on the exemplar only. Findings: `missions/aar/aar_m3a_stream_discovery_skill.md`.

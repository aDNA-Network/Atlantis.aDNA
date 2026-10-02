---
type: fit_matrix
doc_id: atl_v0_m1c_vocabulary_fit_matrix
title: "atl_v0 — vocabulary fit matrix (every enum value × crosswalk authority)"
status: draft
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m1c_linkml_controls
schema: atl_ontology_v0.linkml.yaml (v0.2.0)
crosswalk: crosswalk_external_vocabularies_v0.yaml
tags: [fit_matrix, vocabulary, atl, m1c, goos, eov]
---

# `atl_v0` vocabulary fit matrix (M-1c)

ASOAtlas rule 2: every enum value is a row, sourced to the authority the crosswalk names or marked **`local`** with a
reason. **30 rows** = UnitKind 6 · TimeStep 5 · Modality 8 · VitalTag 4 · Direction 2 · Claim 2 · EvidenceTier 3.

**Columns** are the six *bound* crosswalk authorities plus the one the card asks for — WDPA · CF standard names · UCUM ·
WoRMS · Darwin Core (dwc) · PROV-O · GOOS EOV — and a *deferred* column (ENVO · MIxS · CMECS · NCBI Taxonomy · NOAA CRW).
Cell legend: **—** the authority has no term at this level (not a miss: it names a different kind of thing) ·
**via `slot`** the authority binds through that slot, not through this enum · a named term = a candidate mapping.

> **No enum value is bound to an external authority in v0, and that is the finding, not a gap.** Every enum here names
> something an *instance* or *the method* decides — the kind of patient, the grid's tick, how a stream reaches us, what a
> feature is for, which way the event crosses, what may be claimed, how reviewed an object is. The external authorities
> name *things in the ocean* (a taxon, a quantity, a unit, a protected area, a variable). They bind through **slots**
> (`external_id`, `authority`, `variable`, `unit`), and the crosswalk already records those six bindings.

## 1 · `UnitKind` (6) — the kind of patient

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `mpa_zone` | via `external_id` (`WDPA:<id>`; `MPAtlas:<id>` fallback) | — | — | — | — | — | — | CMECS habitat sub-type | `local` — WDPA ids name *an* area, not the kind "a zone a steward manages"; the binding is the slot (`pos_mpa_zone_wdpa`) |
| `coastal_band` | — | — | — | — | — | — | — | — | `local` — a coordinate-rule band (the exemplar's 9 regions) has no external class |
| `reef` | — | — | — | — | — | — | Coral cover and composition *(a variable, not a unit)* | ENVO reef terms; CMECS | `local` — ENVO/CMECS could type it; defer until an instance needs habitat terms (crosswalk `envo`, `cmecs`) |
| `estuary_segment` | — | — | — | — | — | — | — | ENVO estuarine biome; CMECS | `local` — same as `reef` |
| `river_reach` | — | — | — | — | — | — | — | — | `local` — freshwater hydrography is outside every bound authority |
| `grid_cell` | — | CF grid-cell *conventions* (no enum term) | — | — | — | — | — | — | `local` — the product's grid is described by the stream, not by the unit |

## 2 · `TimeStep` (5) — the grid's tick

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `day` | — | — | `d` *(a unit, not a step)* | — | — | — | — | — | `local` — ISO 8601 `P1D` would fit, but ISO 8601 is not a crosswalk authority and `cruise` has no duration |
| `iso_week` | — | — | `wk` | — | — | — | — | — | `local` — the *name* cites ISO 8601 week numbering (Monday-keyed); the step itself is the method's |
| `fortnight` | — | — | — | — | — | — | — | — | `local` |
| `month` | — | — | `mo` *(UCUM's mean Julian month — not a calendar month)* | — | — | — | — | — | `local` — UCUM's `mo` would mis-state calendar months |
| `cruise` | — | — | — | — | — | — | — | MIxS sampling event | `local` — irregular by design; one step per sampling event |

UCUM codes above are recorded as *near misses*: UCUM names durations, a time step names a grid. Not adopted.
⚠ The three UCUM codes (`d` · `wk` · `mo`) were **not re-fetched** from the UCUM table at M-1c. They are cited as
near-miss illustrations only; nothing binds to them. Verify before any instance adopts one.

## 3 · `Modality` (8) — how a stream speaks · **re-examined against GOOS EOV**

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV *(EOVs it typically carries — §3a)* | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `point_count` | — | — | via `unit` (`/L`) | via `authority` (taxon) | occurrence columns (`organismQuantity`…) | — | Phytoplankton biomass and diversity · Zooplankton biomass and diversity · Fish abundance and distribution | — | `local` |
| `gridded_field` | — | via `authority`/`variable` | via `unit` | — | — | — | Sea surface temperature · Ocean colour · Sea surface height · Sea surface salinity | NOAA CRW products (DHW) | `local` |
| `gauge_series` | — | via `variable` | via `unit` | — | — | — | — *(river discharge is not on the EOV page; Oxygen where a structure carries a DO sonde)* | — | `local` |
| `buoy_series` | — | via `variable` | via `unit` | — | — | — | Sea state · Ocean surface stress · Sea surface temperature · Subsurface temperature · Surface currents | — | `local` |
| `edna_profile` | — | — | — | via `authority` | — | — | Microbe biomass and diversity *(pilot)* · Phytoplankton / Zooplankton biomass and diversity | MIxS · NCBI Taxonomy | `local` |
| `acoustic` | — | — | — | — | — | — | Ocean sound | — | `local` |
| `survey_log` | — | — | — | via `authority` | occurrence columns | — | Coral cover and composition · Seagrass cover and composition · Fish / Sea turtles / Seabirds / Marine mammal abundance and distribution · Benthic invertebrate abundance and distribution *(pilot)* | CMECS | `local` |
| `literature` | — | — | — | — | — | via the P3 ledger's provenance | — | — | `local` — its "observations" are hypotheses (P3) |

### 3a · The GOOS EOV re-examination (the card's question)

**Source, fetched live 2026-10-02:** `https://goosocean.org/what-we-do/framework/essential-ocean-variables/`. The page
lists **36 EOVs** in four groups: Physics 13 · Biogeochemistry 8 · Biology and Ecosystems 12 · Cross-disciplinary 3
(4 marked *pilot*). Its definition: *"GOOS EOVs are defined as the minimum set of ocean variables that are needed to
assess ocean state and variability for important global ocean phenomena."* The EOV names in §3 are copied from that
page; none is added from memory.

**Finding 1 — the crosswalk's `goos_eov.iri_base` is dead.** `…/essential-ocean-variables-eovs/` returns **HTTP 404**
(2026-10-02). The live page is `…/essential-ocean-variables/`. Crosswalk row corrected at M-1c.

**Finding 2 — EOVs are orthogonal to `Modality`, so Modality stays `local`.** An EOV is a *variable* ("sea surface
temperature"), and one EOV reaches an instance through several modalities: SST arrives as a `gridded_field` (OISST),
a `buoy_series` and a `point_count` cruise cast. A modality carries several EOVs. The relation is many-to-many, so
binding one to the other would lose information either way. M-0's suspicion ("granularity does not match one-to-one")
is confirmed against the authority.

**Finding 3 — where EOVs *do* bind is the stream, as an annotation.** The natural home is a v1, additive, optional
multivalued slot `AtlObservationStream.eov` (range: an `EOV` enum of the 36 page names, verdict **adopt**), so a board
reader can ask "which instances watch Phytoplankton biomass and diversity?". **Not added at M-1c.** It is a schema
addition and would need its own controls; P2 (FKNMS: Coral cover and composition, Sea surface temperature) is the
first instance that would exercise it. Logged as a v1 candidate. The crosswalk's `adoption_verdict` **stays `defer`** (its vocabulary is adopt · adapt · build ·
defer; "annotate" is not a verdict). The row's `bind_when` now names the v1 slot, and the verdict becomes `adopt` when that slot lands.

**Finding 4 — the exemplar's event variable has an EOV home, its driver does not.** *K. brevis* sits under
Phytoplankton biomass and diversity (and its toxin under nothing on this page). River discharge, the exemplar's one
lever, is **not an ocean EOV**. A lever often lives upstream of the ocean's own vocabulary, which is why `VitalTag` is
the method's own and not borrowed.

## 4 · `VitalTag` (4) — what a feature is for

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `lever` | — | — | — | — | — | — | — | — | `local` — the method's own vocabulary (pattern step 8); requires `owner` (rule; controls `neg_lever_without_owner`, `neg_lever_owner_null`) |
| `proxy` | — | — | — | — | — | — | — | — | `local` |
| `artifact` | — | — | — | — | — | — | — | — | `local` — a property of the monitoring programme; PROV-O could describe the *programme*, not the tag |
| `state` | — | — | — | — | — | — | — | — | `local` |

A causal vocabulary (`driver`, `cause`) is **deliberately absent**: control `neg_vital_tag_driver`.

## 5 · `Direction` (2)

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `above` | — | — | — | — | — | — | — | NOAA CRW (DHW — schema `Direction.above` docstring; P2) | `local` — a threshold-crossing direction; no authority enumerates it |
| `below` | — | — | — | — | — | — | — | — | `local` |

## 6 · `Claim` (2) — SO-4

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `method_demonstration` | — | — | — | — | — | — | — | — | `local` — Atlantis doctrine (SO-4); required and written out (validators do not apply `ifabsent`) |
| `operational_by_owner_ruling` | — | — | — | — | — | `prov:wasAttributedTo` *(the ruling's author, in an RDF projection)* | — | — | `local` — requires `owner_ruling_ref` (rule; controls `neg_operational_without_ruling`, `neg_operational_ruling_null`) |

## 7 · `EvidenceTier` (3)

| Value | WDPA | CF | UCUM | WoRMS | dwc | PROV-O | GOOS EOV | Deferred | Verdict · reason |
|---|---|---|---|---|---|---|---|---|---|
| `draft` | — | — | — | — | — | — | — | — | `local` — RareArchive's ladder (fleet precedent, not an external authority) |
| `reviewed` | — | — | — | — | — | — | — | — | `local` |
| `validated` | — | — | — | — | — | — | — | — | `local` — `published` dropped: the board is the publication |

## Summary

| Enum | Rows | Bound | `local` | Candidate for v1 |
|---|---|---|---|---|
| UnitKind | 6 | 0 (mpa_zone binds WDPA **via slot**) | 6 | ENVO/CMECS habitat typing when an instance needs it |
| TimeStep | 5 | 0 | 5 | — |
| Modality | 8 | 0 | 8 | **`AtlObservationStream.eov` (36-value EOV enum, adopt)** — annotates streams, does not replace Modality |
| VitalTag | 4 | 0 | 4 | — (method's own; causal words excluded by control) |
| Direction | 2 | 0 | 2 | — |
| Claim | 2 | 0 | 2 | — |
| EvidenceTier | 3 | 0 | 3 | — |
| **Total** | **30** | **0** | **30** | 1 |

**Known limit:** this matrix checks *names against names*. It does not validate any `authority` / `external_id` CURIE
against the authority's service (is `WoRMS:233015` live? is a WDPA id current?). That is a validator's job
(README §Known limits), as the crosswalk header already says.

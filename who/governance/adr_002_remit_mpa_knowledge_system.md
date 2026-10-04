---
type: adr
adr_id: ADR-002
title: "ADR-002 — Remit widening: Atlantis as an MPA knowledge · data-model · evidence system (RATIFIED 2026-10-02)"
status: ratified
created: 2026-10-02
updated: 2026-10-03   # A-1 RATIFIED at the P1 gate (§4 text appended, marked); the rest of the ratified text unchanged
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
supersedes: ""
superseded_by: ""
ratification:
  decision: accepted
  ratified_by: stanley
  date: 2026-10-02
  status: ratified
  surface: AskUserQuestion (P0-exit gate, M-0 sitting)
amendments:
  - {id: A-1, section: "§4 snapshot rule", status: ratified, proposed: 2026-10-03, ratified: 2026-10-03, ratified_by: stanley, surface: "AskUserQuestion (P1-exit gate)", mission: mission_m1b_ii_b_site_mapping_archive}
tags: [adr, remit, mpa, ontology, data_model, evidence_board, decentralisation, atlantis, m0]
---

# ADR-002 — the remit widening (proposed)

## Status

**Ratified 2026-10-02** (was proposed at M-0 (2026-10-02). The widening itself was accepted by the operator as a bounded choice
(`AskUserQuestion`, 2026-10-01: *"Accept the widening"*); this ADR is the object that choice creates, and the
4-field block is the operator's to sign at the P0-exit gate.

## Context

The seed chartered Atlantis as *a method + templates*: the 8-step sepsis-analog pattern, a mining playbook, one
exemplar, and (at P1) a fork skill. On 2026-10-01 the operator asked for Atlantis to become **"a similar project to
RareArchive"** for **marine protected areas (MPAs)**: integrated models, datasets and context used to build
data-models and context graphs; agentic data engineering, data science, model training and improvement; and
knowledge coordination across stewards in a decentralised setting, in the manner of the rare-disease context graph
(`RareGraph.aDNA`, design intent) and RareArchive's built shape.

What RareArchive actually is (read at M-0, `RareArchive.aDNA`): a vault over a code monorepo
(`what/rare-archive/packages/{ontology,datasets,models,…}`); ontologies as schemas + alignment files + tiered
expert context files; dataset and model cards with required fields and a FAIR score; a **GREEN-only evidence board**
whose entries are run-derived and whose promotion to gold is a human act; a blind conductor for data the agent must
not see; coordination memos with an inbox; consumer wrappers pinned by `federation_ref`. That shape is what this
ADR adopts — *the shape*, not the clinical content and not the governance theatre a one-principal stub cannot yet
honour.

## Decision (proposed)

1. **Remit.** Atlantis is the fleet's **MPA knowledge · data-model · evidence system** for ecosystem early
   warning: it owns the ontology, the schemas, the reference implementation, the templates and skills, the
   hypothesis ledger and the evidence **metrics** — and *never* the data. The 8-step method stays the spine.

2. **MPA is a patient unit kind and the primary audience, not a new identity.** `AtlSpatialUnit.unit_kind`
   gains `mpa_zone` (with a WDPA / MPAtlas external id) beside `coastal_band`, `reef`, `estuary_segment`,
   `river_reach`, `grid_cell`. MPA managers and their science partners become the named steward audience in the
   thesis, the contract and the README. The exemplar (a coastal-band HAB model) stays the reference
   implementation; the first *MPA* instance is P2 (Florida Keys NMS coral bleaching, ruled 2026-10-01).

3. **Five layers**, all authored in Atlantis, instantiated per regional instance:

   | # | Layer | Home | v0 at M-0 | Built at |
   |---|---|---|---|---|
   | L1 | **Ontology** — `atl_` LinkML schema + crosswalk to marine authorities | `what/schema/atl_v0/` | draft, no validation claim | P1 M-1c (controls) |
   | L2 | **Data-model system** — the exemplar generalised: stream registry · fetchers · `observation_long` · patient grid (rules / polygons / cells) · feature registry · direction-aware label · all-stream self-test · train/eval/explain · board entry · site template · Neo4j `mapping.yaml` projection | `what/atlantis_core/` | spec only | P1 M-1a/M-1b |
   | L3 | **Agentic loops** — `instance_fork` · `stream_discovery` · `feature_hypothesis_mining` · `retrain_and_drift`; pipeline lattice; runspec; Ray workload request | `how/skills/`, `how/lattices/` | carded | P1 M-1d · P3 · P5 |
   | L4 | **Registries & evidence** — dataset pairs · model cards · GREEN metrics board · hypothesis ledger | `what/{datasets,models,board,hypotheses}/` | board v1 + templates + ledger spec | P1 M-1d · P3 |
   | L5 | **Coordination** — instance contract · conformance-by-mapping · consumer register · memos · trust bands | `who/`, `how/federation/atlantis/` | contract v0 | P4 |

4. **The snapshot rule (SO-3 sharpened).** Atlantis adds **no new data snapshots**. A dataset record here is a
   *pointer + sha256 + fetch recipe*. The exemplar's three parquets in `what/datasets/` (5.3 MB, public FWC / NOAA /
   USGS) are the capped, grandfathered exception and the only bytes this graph carries. WDPA polygons, Coral Reef
   Watch grids and every instance's data live in the instance.
   *(A-1, ratified 2026-10-03:)* The exemplar's explainer pages (`what/exemplars/gulf_karenia_brevis/site/*.html`) join
   the capped, grandfathered exception. They are derived only from the three public parquets, rebuildable from committed
   code, config and copy (`atlantis_core.site`), and exemplar-only. No instance page is ever committed to Atlantis. The
   evidence board stays metrics-only. A new exemplar page version is a new file beside the old one, never an overwrite,
   and cites the board entry whose run it renders.

5. **What crosses from an instance into Atlantis:** patterns and template fixes · feature-registry rows ·
   hypothesis-ledger rows (literature claims with provenance) · evidence-board entries (**metrics only**:
   base rate, AUROC/AUPRC, Brier, calibration slope, alert-budget precision/recall, lead-time summary, ablations,
   config hash, data pins). **What never crosses:** observations, labels, per-patient predictions, model binaries
   trained on partner or human-subject data, coordinates of partner sites, credentials.

6. **Decentralisation mechanics are composed, not built.** Shared work → `Operations.aDNA` claim-lease (bridge
   live on this node); inter-steward writes → coordination memos to `who/coordination/inbox/` (never a direct write
   to another operator's canonical vault, Operations ADR-026); instance-graph sharing → `Network.aDNA` share class
   (`public | partner_share | private`); provenance → `Ingest.aDNA` Rule 5 fields; compute → `Ray.aDNA` workload
   request. Governance documents beyond a contribution guide (steward council, decision authority, partner
   engagement) are **P4**, when a second steward exists.

## Distinct from

| Graph | Boundary |
|---|---|
| `RareArchive.aDNA` / `RareGraph.aDNA` | *shape* precedents; clinical content, PHI doctrine and the Wilhelm partner estate stay theirs |
| `Exchange.aDNA` | the commons / market; an instance *lists* there, Atlantis does not host one |
| `Ingest.aDNA` | the intake engine; the mining lane composes it when a corpus exists |
| `Datasets.aDNA` | owner of the Dataset primitive; Atlantis conforms to the record pair and co-signs its provenance-contract seam (backlog) |
| `WorldGenome.aDNA` / `WGS.aDNA` | genome org and eDNA→audio instrument; an eDNA instance of Atlantis may federate them for sequence vitals |
| `Dashboards.aDNA` / `Neo4j.aDNA` | the insight surface; an instance's `mapping.yaml` projects into them, Atlantis defines the mapping template |

## Consequences

**Positive.** A steward checking out Atlantis gets an ontology, a registry shape, a board to compare against and
a contract — not just a pilot to edit. Metrics become comparable across instances without any data moving.
**Negative.** Scope: five layers is a multi-phase build; the charter is re-cut accordingly and nothing
auto-advances (SO-1). The ontology can harden before it is validated — mitigated by `status: draft` and
M-1c being the first P1 card. **Neutral.** The public repo now publishes schemas; everything committed must still
be publishable (Git.aDNA ADR-013).

## Ratification

**Ruled 2026-10-02 by the operator (stanley) at the P0-exit gate, `AskUserQuestion`:** ratified as written. Recorded verbatim; GO P1 given in the same gate.

| Field | Value |
|---|---|
| decision | **accepted** |
| ratified-by | **stanley** |
| date | **2026-10-02** |
| status | **ratified** |

## Amendment A-1 — the exemplar's explainer pages (proposed 2026-10-03 · RATIFIED 2026-10-03)

**Trigger.** M-1b-ii-b III review F-5. §4 names the exemplar's three parquets as "the only bytes this graph carries".
The exemplar's explainer pages are also committed, and they carry *derived* per-patient content:
- `site/hab_crash_risk.html` (v0, committed 2026-09-23, before this ADR);
- `site/gulf_karenia_brevis_v1.html` (v1, committed 2026-10-03 by operator ruling in the M-1b-ii-b sitting).

That content is weekly scores, SHAP values, labels, sample locations rounded to 0.05°, and the vitals trace, all computed
from those same public parquets. The ruling and the rule disagree; this amendment reconciles them on the record.

**Proposed text, appended to §4.** *The exemplar's explainer pages (`what/exemplars/gulf_karenia_brevis/site/*.html`) join the capped,
grandfathered exception. They are derived only from the three public parquets. They are rebuildable from committed code,
config and copy (`atlantis_core.site`). They are exemplar-only.*
- **No instance page is ever committed to Atlantis.** An instance's page is that instance's artifact, under its own
  data ruling (ADR-016 §8 class).
- **The evidence board stays metrics-only.**
- **A new exemplar page version is a new file beside the old one**, never an overwrite, and each one cites the board
  entry whose run it renders.

**Not changed.** §5 (what crosses from an instance), the board's GREEN rule, and SO-3 for every instance.

| Field | Value |
|---|---|
| decision | **accepted** |
| ratified-by | **stanley** |
| date | **2026-10-03** |
| status | **ratified** |

**Ruled 2026-10-03 by the operator (stanley) at the P1-exit gate, `AskUserQuestion`:** ratified as written. The text
is appended to §4 above, marked *(A-1)*. The v0 page has been public since the genesis commit, so this reconciles the
rule with what was already published; the ruling precedes any push of the v1 page.


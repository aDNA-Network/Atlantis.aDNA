---
campaign_id: campaign_atlantis_genesis
type: campaign
title: "Operation Tidewatch — Atlantis genesis: from one exemplar to an MPA knowledge · data-model · evidence system for ocean-ecosystem early warning"
display_name: "Operation Tidewatch"
owner: stanley
persona: proteus            # RULED 2026-10-02 at the P0-exit gate (ADR-001 ratified)
status: active
phase: P1                   # P0 gate MET 2026-10-02 (ADR-000/001/002 ratified · Proteus · GO P1)
phase_count: 6
mission_count: 10           # M-0 (done) + nine carded: M-1a M-1b M-1c M-1d · M-2 · M-3a M-3b · M-4 · M-5
estimated_sessions: "12-18"
calibrated_sessions: "12-18"   # re-cut at M-0 for the widened remit (seed: 8-14)
estimation_class: content-novel
executor_tier: mixed        # FABLE = M-0, M-4, every phase exit · OPUS = briefed build lanes
priority: medium
home_vault: Atlantis.aDNA
remit_adr: who/governance/adr_002_remit_mpa_knowledge_system.md
roster: artifacts/mission_roster_p1_p5.md
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [campaign, atlantis, tidewatch, genesis, early_warning, oceans, mpa, ontology, evidence_board]
---

# Campaign: Operation Tidewatch

> **Codename discipline:** `grep -ril "Operation Tidewatch" ~/aDNA` → 0 hits outside this graph at seed time (2026-09-23).
> **Re-chartered at M-0 (2026-10-02)** for the operator's widened remit (ADR-002). The seed charter is preserved in
> git history (`aec55d4`); this file supersedes it.

## Goal

When this campaign is complete, **a marine steward — an MPA manager, a sanctuary scientist, an estuary programme —
can clone `Atlantis.aDNA`, run one skill, answer a handful of questions (what is the patient, what is the event, how
much warning would change what you do, what streams exist, what is your data posture), and be left with a regional
instance graph that**: declares its patient, streams, vitals and event in registries that validate against the
`atl_` ontology · fetches its data with provenance and hashes · builds leakage-proof vitals and proves it · trains and
evaluates a calibrated onset model at an alert budget the steward can staff · explains it with tagged SHAP · publishes
a page with its Limitations · lands a **metrics-only** entry on the Atlantis evidence board where it is comparable
with every other instance's **without any data moving** · inherits the hypothesis ledger's literature for its
ecosystem type and tests it — all **without editing Atlantis, and without Atlantis ever holding their data.**

## Context

Seeded from aDNALabs S329 (2026-09-23): a one-sitting pilot built a complete *Karenia brevis* bloom-onset early-warning
system on public data (test AUROC 0.894, AUPRC 0.547 vs 7.7% prevalence; 64% of onsets flagged, median lead 4 weeks)
and two method findings (stop on log-loss; ablate surveillance). The operator ruled it the exemplar of a new graph.

**M-0 (2026-10-02, fable, operator-opened)** widened the remit: Atlantis is to be, for marine protected areas, what
`RareArchive.aDNA` is for rare disease — integrated ontology · datasets · models · evidence · context, with agentic
data-engineering / training / evaluation / intervention loops and decentralised, multi-steward knowledge coordination
in the manner of the rare-disease context graph. The *shape* is adopted (vault over a reference implementation;
schemas + crosswalk; GREEN-only evidence board; registries with FAIR; conformance-by-mapping; memos + inbox), not the
clinical content and not governance a one-principal stub cannot honour. Thesis: `what/context/concept_atlantis.md` ·
register: `artifacts/thesis_register.md` · method: `what/patterns/pattern_ecosystem_early_warning.md`.

## The five layers (ADR-002 §3)

| # | Layer | Home | Built at |
|---|---|---|---|
| L1 | **Ontology** — `atl_` LinkML + crosswalk (WDPA · CF · UCUM · WoRMS · Darwin Core · PROV-O) | `what/schema/atl_v0/` | v0 draft at M-0 · controls **M-1c** |
| L2 | **Data-model system** — `atlantis_core`: stream registry · fetchers · `observation_long` · patient grid (rules / polygons / cells) · feature registry · direction-aware label · all-stream self-test · eval · SHAP · board emitter · site template · `mapping.yaml` | `what/atlantis_core/` | **M-1a M-1b** |
| L3 | **Agentic loops** — `instance_fork` · `stream_discovery` · `feature_hypothesis_mining` · `retrain_and_drift`; pipeline lattice; runspec; Ray request | `how/skills/` · `how/lattices/` | **M-1d · M-3a M-3b · M-5** |
| L4 | **Registries & evidence** — dataset pairs · model cards · GREEN board · hypothesis ledger | `what/{datasets,models,board,hypotheses}/` | board v1 + templates + ledger spec at M-0 · **M-1d · M-3b** |
| L5 | **Coordination** — instance contract · conformance-by-mapping · consumer register · memos · trust bands | `who/` · `how/federation/atlantis/` | contract v0 at M-0 · **M-4** |

## Scope

### In scope
- Identity, persona, category, the **remit widening** and the **instance contract** (P0 — done, awaiting ratification).
- The ontology with controls; the reference implementation extracted from the exemplar; the fork skill (P1).
- The **first MPA instance** — FKNMS coral bleaching — proving drop-in (P2).
- The knowledge lane: stream-discovery skill, hypothesis ledger, literature → tested vitals (P3).
- Contract v1, steward governance, consumer register, Exchange listing, first outside steward (P4).
- Retrain/drift cadence, Ray request template, AAR (P5).

### Out of scope
- Operational forecasting or any claim to it (agencies' business; an instance owner may rule otherwise, in writing — SO-4).
- Causal inference; the what-if stays a sensitivity; a SHAP value is never a cause.
- Holding any regional, partner or human-subject data in Atlantis (SO-3; **snapshot rule** ADR-002 §4).
- Building a data commons (`Exchange.aDNA`), an intake engine (`Ingest.aDNA`), a Dataset primitive (`Datasets.aDNA`), a
  compute scheduler (`Ray.aDNA` / `Scheduler.aDNA`) or a BI surface (`Dashboards.aDNA`) — **compose them**.
- Governance theatre: steward council / decision authority before a second steward exists (P4, not before).

## Phases & missions

Roster with tiers, budgets, dependencies and the critical path: **`artifacts/mission_roster_p1_p5.md`**. Cards in
`missions/`. Every phase exit is an **operator gate** (SO-1), rendered by `aDNA.aDNA/how/skills/skill_create_iss.md`
or `AskUserQuestion`; nothing auto-advances.

### P0 — Genesis planning (fable; operator-opened) — **M-0 complete · gate MET 2026-10-02**

| Mission | Title | Tier | Status |
|---|---|---|---|
| M-0 | Genesis planning: ADR-000 lineage · ADR-001 persona + category + code home · **ADR-002 remit** · thesis register · instance contract v0 · `atl_v0` draft + crosswalk · evidence board v1 + exemplar entry · model-card + dataset-pair templates · hypothesis-ledger spec · this re-charter · roster + 9 cards · P2 ruling | fable | **completed** |

**Exit bar:** ADR-000/001/002 carry the operator's 4-field block · persona ruled (Proteus / Nereus) · instance
contract v0 exists as a checklist a stranger could satisfy from four files · P1–P5 carded with tiers and budgets ·
P2 pick named (FKNMS, ruled 2026-10-01). **Gate MET 2026-10-02:** ADR-000/001/002 ratified · persona Proteus · **GO P1** (operator, `AskUserQuestion`).

### P1 — Core canonisation (opus lanes, fable review)
M-1a exemplar hygiene · M-1b `atlantis_core` extraction (split 2026-10-02: M-1b-i core + self-test ✅ · M-1b-ii eval/explain/board/site) (feature registry · direction-aware label · polygon grid ·
**all-stream self-test** · board emitter) · M-1c `atl_v0` controls · M-1d fork skill + pipeline lattice + dataset-pair
migration + contribution guide + BOARD generator.
**Exit bar:** a fresh instance forks from templates alone, in one sitting, self-test green before any real data is
fetched; `atlantis_core` reproduces the exemplar's metrics; `atl_v0` controls pass under both validators; III review
via wrapper.

### P2 — First MPA instance (opus build, fable gate)
M-2 `FloridaKeysCoral.aDNA` — FKNMS zones × week · DHW onset · gridded-only vitals · no surveillance channel
(ablation declared N/A, not skipped) · board entry landed. **Exit bar:** trained + explained + paged + on the board
**without editing Atlantis code**; every deviation became a P1 template change. Ruling: `artifacts/p2_second_instance_ruling.md`.

### P3 — Knowledge lane (opus)
M-3a `skill_stream_discovery` (playbook §A/§B as checks) · M-3b hypothesis ledger populated (≥ 25 rows, one
ecosystem type) + `skill_feature_hypothesis_mining` + ≥ 1 literature-asserted driver realised as a vital and tested by
SHAP, written up either way. Composes `Ingest.aDNA` when a corpus exists. **Exit bar:** one instance's vitals extended
from the ledger with provenance; the test written up.

### P4 — Federation & stewards (fable sitting + gate)
M-4 contract v1 ratified · steward governance set · consumer-wrapper template + register · Exchange listing · Network
share-class ruling · blind-conductor runbook *iff* a partner-data instance exists · **first outside steward**
instantiates from the public repo alone. **Exit bar:** an instance built by someone who was not in this campaign lands
a board entry.

### P5 — Steady state (opus)
M-5 `skill_retrain_and_drift` · Ray workload request template (no job without operator GO on the run-spec) · campaign
AAR · successor cards. **Exit bar:** AAR in this file; Atlantis joins the fleet's steady-state baseline.

## Gates that shape everything

- **SO-1:** every phase exit is a human gate; no auto-advance.
- **SO-3 + snapshot rule:** Atlantis never becomes data-bearing; no new snapshots; the moment a lane needs regional data it moves to an instance.
- **SO-4:** no output is an operational forecast without the instance owner's written ruling; the board says so on every entry.
- **SO-7:** the self-test is the one hard invariant; from M-1b it perturbs every stream.
- **Public repo:** everything committed here is publishable; the commit is the publication (Git.aDNA ADR-013).

## Risks

| Risk | Mitigation |
|---|---|
| Template drift from the exemplar | P2 forbids instance hacks; every deviation is a P1 template change |
| **Unvalidated ontology hardens** | `status: draft` + NO-VALIDATION-CLAIM banner until M-1c; **retired at M-1c** — 19 controls, committed JSON checked against a fresh generation every run |
| **Board becomes a claim surface** | no-accuracy-claim header on every entry; `base_rate` and `limitations_ref` required; `claim` defaults to method_demonstration |
| **Snapshot growth under "MPA"** (WDPA polygons, CRW grids) | ADR-002 §4: pointers + sha256 + fetch recipe only |
| **RareArchive over-import** (council for one principal; conductor with no partner data) | governance set + conductor at P4, contribution guide at P1 |
| ERDDAP / NWIS / CRW flakiness | cache, retry, `--offline`, atomic writes (exemplar discipline, kept in `atlantis_core`) |
| Surveillance endogeneity | explicit flagged channel + required ablation where declared; declared N/A where absent |
| Over-claiming | SO-4; Limitations section required on every page and every card |
| Mining lane produces prose | extraction target fixed in `what/hypotheses/README.md`; rows point at sentences |
| Persistent events (DHW) defeat the onset rule | M-2 acceptance names it; T3 re-cut at the P2 gate |

## Status

**P1 open — P0 gate MET 2026-10-02.** ADR-000/001/002 ratified, persona Proteus, GO P1 given by the operator at the
gate. **M-1a complete 2026-10-02** (exemplar hygiene; AAR filed). **M-1c complete 2026-10-02** (`atl_v0` controls: 42, three
worlds agree; `iii/` adopted, III review PASS-WITH-FINDINGS; AAR filed). **M-1b split** (operator, 2026-10-02) → **M-1b-i complete
2026-10-02** (`atlantis_core` registries · fetch · grid · vitals · label · all-stream self-test; hab's SST row-lag defect found,
calendar-correct ruled; III 11/11 fixed; AAR filed). Next: M-1b-ii (opus), then M-1d → P1 gate.

## AAR (campaign — filled at P5)

*Worked · Didn't · Finding · Change · Follow-up.*

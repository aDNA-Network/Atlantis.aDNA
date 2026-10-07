---
type: mission
mission_id: M-2a
plan_id: mission_m2a_fknms_fork_and_fetch
title: "M-2a — FloridaKeysCoral.aDNA: fork · posture · persistent-event self-test · CRW data path · fetch · conform (fetched)"
owner: stanley
status: superseded   # split 2026-10-06 (operator ruling, AskUserQuestion) → M-2a-i + M-1f + M-2a-ii
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~150-200kT main + fresh-context III reviewer — includes a full defect-catalogue run on the new event shape (C-014)"
token_budget_actual: ""
depends_on: ['M-1d-ii', 'M-1e']
split_from: mission_m2_fknms_coral_instance
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2a_fknms_fork_and_fetch.md
session: TBD
created: 2026-10-03
updated: 2026-10-06
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2a, p2, opus, fknms, coral, mpa, fork, fetch, atlantis, tidewatch]
---

# M-2a — FloridaKeysCoral.aDNA, from fork to fetched data

> **Superseded 2026-10-06, split (operator ruling at the M-2a planning sitting).** The core survey found that this card could not go green without core changes. Those land Atlantis-side in **M-2a-i** (`mission_m2a_i_core_for_persistent_polygon_instances.md`). The horizon embargo runs as **M-1f**, and the fork and fetch become **M-2a-ii** (`mission_m2a_ii_fknms_fork_and_fetch.md`). Condition (c) is **MET**: CRW is reachable through `ERDDAPGriddap` on `coastwatch.noaa.gov`. The card is kept as written (SO-2).

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P2 · **Tier:** opus. **Split from** `mission_m2_fknms_coral_instance.md`
under the P1-exit gate ruling (2026-10-03: conditional GO). **Sibling:** `mission_m2b_fknms_model_and_board.md`.
**Opens only after M-1e closes** (condition (a)).

## Objective

Fork the first MPA instance with the skill and take it to fetched, conformant data. Do it **without editing
`atlantis_core` from the instance**: every gap becomes an Atlantis-side P1 template or core change (the P2 rule).

## Acceptance criteria

- [ ] **Condition (c), first:** confirm that NOAA Coral Reef Watch DHW / HotSpot / SST is reachable through the built
      `ERDDAPGriddap` fetcher (CoastWatch ERDDAP dataset id, variables, grid, licence). If it is, declare the streams with
      it. If it is not, stop and card the `CoralReefWatch` fetcher as an Atlantis-side change (WI-19); never build it
      inside the instance
- [ ] `FloridaKeysCoral.aDNA` forked by `skill_atlantis_instance_fork`, in **public** posture (CRW and OISST are public).
      The posture ADR says so, with its signed Ratification row. The router row goes by Hestia memo
- [ ] Patients: FKNMS management zones (`unit_kind: mpa_zone`, WDPA:2347 parent; zone geometry from the sanctuary's
      public shapefile **as a pointer**) × ISO week, built by the polygon path
- [ ] Event: DHW ≥ threshold (ruled in-instance from the CRW bleaching-alert levels), within 4–8 weeks, `direction: above`.
      The onset rule handles multi-week persistence (T3), and a second threshold serves as sensitivity (T12)
- [ ] Streams: CRW (gridded; `authority` NOAA CRW until a CF name exists) and OISST. **NDBC is dropped** (its fetcher is
      not built; condition (c)). `surveillance_channel: false` with the reason, and the ablation **declared N/A** (R8)
- [ ] **Self-test generalised for the persistent event** where needed (Atlantis-side). The **whole** planted-defect
      catalogue re-runs on the new shape (C-014). Green **before** any fetch
- [ ] `conform --stage declared` items 1–8 and 11–12 ✅ → `fetch` (receipt and posture gates) → `conform --stage fetched` ✅
- [ ] Every deviation is an Atlantis-side change, listed in the AAR. Zero instance-local patches to `atlantis_core`
- [ ] III review via `iii/`, fresh context; AAR

## Guardrails

SO-1 · SO-3 / ADR-002 §4 (no data in Atlantis) · SO-4 · SO-7 · peer vaults read-only · budget > +50% → SITREP and ask.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

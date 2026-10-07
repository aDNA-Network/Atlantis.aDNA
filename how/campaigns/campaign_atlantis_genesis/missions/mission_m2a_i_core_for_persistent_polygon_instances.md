---
type: mission
mission_id: M-2a-i
plan_id: mission_m2a_i_core_for_persistent_polygon_instances
title: "M-2a-i — atlantis_core for a persistent, polygon, gridded instance: CRW authority · grid pin · onset refractory · persistent self-test world (whole catalogue) · CoralReefWatch polygon fetcher"
owner: stanley
status: active
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~180-220kT main + fresh-context III reviewer"
token_budget_actual: ""
depends_on: ['M-1e']
split_from: mission_m2a_fknms_fork_and_fetch
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2a_i_core_for_persistent_polygon_instances.md
session: session_stanley_20261007_023031_m2a_i_core_for_persistent_polygon_instances
created: 2026-10-06
updated: 2026-10-06
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2a_i, p2, opus, crw, polygon, refractory, selftest, atlantis_core, atlantis, tidewatch]
---

# M-2a-i: the core changes an FKNMS instance needs, made before the fork

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P2 · **Tier:** opus. **Split from**
`mission_m2a_fknms_fork_and_fetch.md` on the operator's ruling of 2026-10-06 (AskUserQuestion, at the M-2a planning sitting).
**Sequence:** M-2a-i → M-1f (embargo, board v3) → M-2a-ii (fork and fetch) → M-2b → P2 gate.

## Why

At planning, the core was surveyed against the FKNMS instance ruled at P2. As carded, that instance could not go green
without editing `atlantis_core`, which the P2 rule forbids. Every gap is therefore closed here, Atlantis-side, before the
fork:

- **Authority.** The `conform` allowlist is `CF` / `WoRMS` / `dwc`, and DHW has no CF standard name.
- **Label.** It has no onset refractory, whereas `eval/lead.py` defines an onset as "no crossing in the previous H weeks".
  For a persistent, accumulating event the two disagree.
- **Self-test.** No self-test world has a `unit_daily` event or an accumulating one; the synthetic event is iid. C-014: the
  whole catalogue re-runs on the new shape.
- **Grid pin.** The polygon file's "pinned by sha256" claim has no code behind it (C-023 class).
- **Fetch.** `ERDDAPGriddap` takes a rectangle mean and never sees the instance's grid, and `CoralReefWatch` is declared,
  not built. Ruled: **zones plus a polygon reducer**, not rectangles.

**Condition (c) is MET at planning.** CRW's own ERDDAP (`coastwatch.noaa.gov/erddap/griddap/noaacrw{dhw,hotspot,sst,sstanomaly}Daily`)
is reachable through the built `ERDDAPGriddap` query shape. Latitude is stored descending, and the ascending query still works.
The PFEG mirror timed out.

## Acceptance criteria

- [ ] **Authority:** a CRW CURIE prefix is admitted by `conform` item 2. The crosswalk row `noaa_crw_products` is bound.
      The contract goes to v0.3.0 (minor). A bare `NOAA CRW` fails item 2 by name
- [ ] **Grid pin:** `grid.sha256` for polygon grids is written by `fork` from the file's bytes and verified wherever the grid
      is built and by `conform` item 1. A moved vertex is refused by name. The false docstrings are corrected
- [ ] **Refractory:** `label.refractory_weeks` (default 0; R = 0 is byte-identical) drops rows whose carried signal crossed
      in t−R…t. The slot is in atl_v0 (0.5.0) with controls, and ALL WORLDS AGREE
- [ ] **Self-test:** an `accumulating` synthetic event series; a check that the refractory reads only the past; a third
      forked world (`persistent_master`: polygons, `unit_daily` above-event, H = 8, R = 8, surveillance absent). The
      **whole** catalogue re-runs across all three worlds plus the exemplar's 16. New plants fail by name. The exemplar's
      receipt is re-issued green (SO-7)
- [ ] **Fetcher:** `CoralReefWatch` is built as an `ERDDAPGriddap` subclass on CRW's own ERDDAP. It reduces by a per-feature
      cell-centre mask over the instance's pinned polygons, with a nearest-cell fallback. Per-zone `n_cells` and `fallback`
      are computed by the code (C-023). It is offline-tested and a plant fails. One live smoke result goes in the AAR only
      (no data committed)
- [ ] **Skill:** `skill_atlantis_instance_fork` gains the Hestia router-row memo step and notes on the above
- [ ] The exemplar's byte-stable set is unchanged (board v2; model, SHAP and what-if bytes; `test_f8`, `test_equivalence`)
- [ ] III review via `iii/`, in a fresh context; AAR

## Guardrails

SO-3 / ADR-002 §4 (no data in Atlantis) · SO-7 · SO-9 · C-009 (a guard is proven by a plant in the real path) · C-014 · C-023 ·
peer vaults read-only · budget > +50% → SITREP and ask.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

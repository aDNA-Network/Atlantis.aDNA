---
type: mission
mission_id: M-2a-ii
plan_id: mission_m2a_ii_fknms_fork_and_fetch
title: "M-2a-ii — FloridaKeysCoral.aDNA: interview · fork · zone geometry (pointer + sha256) · posture + licence ruling · self-test receipt · ratify · fetch · conform (fetched) · Hestia memo"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~120-160kT main + fresh-context III reviewer (the CRW fetch itself is wall-clock, not tokens)"
token_budget_actual: ""
depends_on: ['M-2a-i', 'M-1f']
split_from: mission_m2a_fknms_fork_and_fetch
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2a_ii_fknms_fork_and_fetch.md
session: TBD
created: 2026-10-06
updated: 2026-10-06
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m2a_ii, p2, opus, fknms, coral, mpa, fork, fetch, atlantis, tidewatch]
---

# M-2a-ii: FloridaKeysCoral.aDNA, from fork to fetched data

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P2 · **Tier:** opus. **Split from**
`mission_m2a_fknms_fork_and_fetch.md` (operator ruling 2026-10-06). It opens only after M-2a-i (the core changes) and M-1f (the
horizon embargo) have closed, so the instance's self-test receipt is earned once, under the final label and split code.

## Rulings carried in (operator, 2026-10-06)

- **Patients:** FKNMS management zones (`unit_kind: mpa_zone`, parent WDPA:2347), reduced by the `CoralReefWatch` polygon
  mask. Rectangles are not used.
- **Horizon:** H = 8, a single window t+1…t+8. Lead time shows how much warning comes 4 or more weeks ahead.
- **Embargo (M-1f, landed 2026-10-07):** `split.embargo_weeks` defaults to H = 8, so it is left out of the fork. Each fit and
  stop set loses the 8 weeks before the period after it: the last 8 weeks of a year (November–December, when DHW usually
  decays after the late-summer peak) at every boundary. Read the `embargo` block in `metrics.json` (rows and positives dropped, and the spill) with the steward. If a stop year falls
  under 5 positives, its fold is skipped and the run says so.

## Interview starting point (the steward rules each item; these are proposals)

- **Event:** CRW DHW ≥ 4 °C-weeks, CRW Bleaching Alert Level 1, `direction: above`, horizon 8; `refractory_weeks: 7` (= H − 1, corrected at M-2a-i III F-4 from 8), which
  aligns the onset with `lead.py`; `eval.sensitivity_threshold: 8` (Alert Level 2). Authority: the CRW CURIE admitted at
  M-2a-i.
- **Streams:** CRW DHW (event) · HotSpot · SST · SST anomaly, each `noaacrw*Daily` on `coastwatch.noaa.gov`, plus OISST.
  NDBC is dropped. `surveillance: {declared: absent, reason: …}`, so R8 declares the ablation N/A.
- **Zone geometry:** the NOAA ONMS FKNMS zone layer, converted from shapefile to GeoJSON **inside the instance** by a
  recorded recipe and pinned with `grid.sha256`. The steward rules **which zoning version** applies (the pre- or
  post-Restoration-Blueprint layer), and how SPAs smaller than one 5 km cell are grouped. The fetch summary's `fallback`
  count shows what grouping is still needed.
- **Licence ruling, at the posture ADR:** CRW's licence says "without restriction; credit CRW + DOI". The PacIOOS mirror of
  the same CoralTemp v3.1 product carries an **OSTIA academic-only clause for 1985–2002**. Either cite the CRW-native licence
  and note the upstream caveat, or start the era in 2002.
- **Expect few onsets.** Every zone heats in the same years, so rolling folds will skip (< 5 positives). Say so and do not
  tune around it.

## Acceptance criteria

- [ ] `FloridaKeysCoral.aDNA` forked by `skill_atlantis_instance_fork` at the workspace root, in **public** posture. The
      posture ADR carries the licence ruling, and its Ratification row is signed by the operator
- [ ] `conform --stage declared` items 1–8 and 11–12 ✅. Self-test green, with the receipt earned under the M-1f code
- [ ] `fetch` (receipt and posture gates) → provenance recorded → `fetch --verify` → `conform --stage fetched` ✅
- [ ] **Router row via a Hestia memo** (workspace Rule 3; the skill step added at M-2a-i)
- [ ] Zero instance-local patches to `atlantis_core`. Every deviation is an Atlantis-side change, listed in the AAR
- [ ] III review via `iii/`, in a fresh context; AAR; then queue M-2b

## Guardrails

SO-1 · SO-3 / ADR-002 §4 (no data in Atlantis) · SO-4 · SO-7 · peer vaults read-only · budget > +50% → SITREP and ask.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

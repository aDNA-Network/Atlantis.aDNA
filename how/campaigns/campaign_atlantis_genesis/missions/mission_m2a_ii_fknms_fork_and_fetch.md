---
type: mission
mission_id: M-2a-ii
plan_id: mission_m2a_ii_fknms_fork_and_fetch
title: "M-2a-ii — FloridaKeysCoral.aDNA: interview · fork · zone geometry (pointer + sha256) · posture + licence ruling · self-test receipt · ratify · fetch · conform (fetched) · Hestia memo"
owner: stanley
status: completed   # 2026-10-08: fetched (sitting 2), III PASS-WITH-FINDINGS 9/9, AAR filed; M-2b queued
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~120-160kT main + fresh-context III reviewer (the CRW fetch itself is wall-clock, not tokens)"
token_budget_actual: "sitting 1 ≈ 300kT main (≈ +88%, ruled) · sitting 2 ≈ 300-350kT across four contexts (rulings 13-18; core 0.5.2 + 0.5.3; estimated, not metered) · III reviewer ≈ 190kT · total ≈ 600-650kT main (≈ +300% on the card top)"
depends_on: ['M-2a-i', 'M-1f']
split_from: mission_m2a_fknms_fork_and_fetch
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m2a_ii_fknms_fork_and_fetch.md
session: session_stanley_20261007_154002_m2a_ii_fknms_fork_and_fetch   # sitting 1 of 2
created: 2026-10-06
updated: 2026-10-08
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
- **Embargo (M-1f, landed 2026-10-07):** `split.embargo_weeks` defaults to H = 8, so it is left out of the fork. The last 8
  weeks before each boundary (November–December, in week-years) leave every set that must not see the next period: the
  selection fit, the stop set, and the refit's validation tail. The refits keep the train tail. Where those weeks sit in
  the bleaching season is the steward's to say. Read the `embargo` block in `metrics.json` (rows and positives dropped, and the spill) with the steward. If a stop year or a test year
  falls under 5 positives, its fold is skipped and `rolling_skipped` says so (the test-year case was silent until III M-1f F-7).

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

## Progress of record (sitting 1, 2026-10-07 → 08; steward = Stanley, every ruling via AskUserQuestion)

**Rulings:**
- **zoning:** pre-Blueprint (the Blueprint took effect 2025-03-05 in federal waters only);
- **geometry:** a declaration, fetched before ratification by a recorded recipe;
- **grouping:** 21 patients (four cell-sharing pairs merged);
- **streams:** OISST dropped; **raw CRW SST dropped**, because CRW's own `noaacrwsstDaily` carries the OSTIA 1985–2002 terms
  (the WI-24 premise was wrong). DHW, HotSpot and SSTA run from 1985 under CRW's licence;
- **split:** 1986–2013 / 2014–18 / 2019–25;
- **vault:** licence MIT; persona deferred;
- **review:** starter vitals and tags accepted; budgets 5/10/20, lead at 10%;
- **ADR-001 ratified** (signed stanley, 2026-10-07).

**Done:**
- the fork at the workspace root;
- declared stage **conforms** (items 1–8 and 11–12);
- the receipt is green (`0d4d2bb19e`, core 0.5.1);
- the fetch refused before ratification (demonstrated);
- the Hestia memo delivered;
- instance commits `d7f5e31` and `3e45b93`.

**Atlantis-side changes** (642 tests):
- `0e4154b`: fork `answers.eval.sensitivity_threshold`;
- `f23e046`: the self-test C6 KeyError without a climatology;
- `95ea8da`: the ERDDAP/CRW spec `start` date.

**Stopped at:** the fetch. CRW's ERDDAP returned 502 on every request from ~23:13Z, 0 of 567 chunks. The PacIOOS mirror
was rejected because its licence attribute is OSTIA. **Remaining:** the criteria below marked ⏳.

## Acceptance criteria

- [x] `FloridaKeysCoral.aDNA` forked by `skill_atlantis_instance_fork` at the workspace root, in **public** posture. The
      posture ADR carries the licence ruling, and its Ratification row is signed by the operator
- [x] `conform --stage declared` items 1–8 and 11–12 ✅. Self-test green, with the receipt earned under the M-1f code
- [x] `fetch` (receipt and posture gates) → provenance recorded → `fetch --verify` → `conform --stage fetched` ✅ (instance `07df953`; 15-day union spans, core 0.5.2; ruling 16 accepted the data)
- [x] **Router row via a Hestia memo** (delivered; the row is Hestia's to land) (workspace Rule 3; the skill step added at M-2a-i)
- [x] Zero instance-local patches to `atlantis_core`. Every deviation is an Atlantis-side change, listed in the AAR
- [x] III review via `iii/`, in a fresh context (PASS-WITH-FINDINGS, 9/9 addressed; core 0.5.3; rulings 17–18); AAR filed; M-2b queued

## Guardrails

SO-1 · SO-3 / ADR-002 §4 (no data in Atlantis) · SO-4 · SO-7 · peer vaults read-only · budget > +50% → SITREP and ask.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

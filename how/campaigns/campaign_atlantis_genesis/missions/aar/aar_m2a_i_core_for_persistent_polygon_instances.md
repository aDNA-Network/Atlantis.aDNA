---
type: aar
mission: mission_m2a_i_core_for_persistent_polygon_instances
campaign: campaign_atlantis_genesis
created: 2026-10-06
updated: 2026-10-06
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261007_023031_m2a_i_core_for_persistent_polygon_instances
token_budget_estimated: "~180-220kT main + fresh-context III reviewer (card, written at the planning sitting)"
token_budget_actual: "≈345kT main (planning sitting and the core survey included; ≈ +57%; SITREP at the +50% line and the operator ruled 'fix all 8') + ≈235kT fresh-context III reviewer"
tags: [aar, m2a_i, p2, crw, polygon, refractory, selftest, atl_v0, iii, atlantis, tidewatch]
---

# AAR — M-2a-i: atlantis_core for a persistent, polygon, gridded instance

**Every gap the FKNMS instance would have hit has been closed Atlantis-side, before the fork.** The next lane is
**M-1f** (the horizon embargo), then **M-2a-ii** (the fork and fetch).

## Why this mission existed

M-2a was carded as "fork FKNMS, then fetch". Planning surveyed the core against that instance and found it could not go
green without editing `atlantis_core`, which the P2 rule forbids. The operator split it on 2026-10-06 (AskUserQuestion)
and ruled four things:
- patients are FKNMS zones, reduced by a polygon reducer;
- H = 8, one window;
- the embargo runs in its own lane, before the fork;
- the core changes go first, in this mission.

**Condition (c) was MET at planning.** CRW's own ERDDAP serves `noaacrw{dhw,hotspot,sst,sstanomaly}Daily` through the
built `ERDDAPGriddap` query shape, ascending latitude included. The PFEG mirror timed out.

**Commits:**

| Commit | Content |
|---|---|
| `9873844` | inbox: Noether's LinkML Profile memo triaged (read-receipt, no action) |
| `88e3de1` | the split: three cards, M-2a superseded, M-2b gains a persistence baseline, rulings of record |
| `d3e24bb` ① | `NOAACRW:` authority · contract v0.3.0 · crosswalk row bound |
| `090d69d` ② | `grid.sha256`: fork writes it; `make_grid` and conform item 1 check it |
| `81bb8fa` ③ | `refractory_weeks` (atl_v0 0.5.0, 53 controls) · label · hash only when set |
| `2e6202d` ④ | self-test: accumulating world · C9 · `persistent_master` · catalogue × 3 · 6 plants |
| `277f785` ⑤ | `CoralReefWatch` built · `bind` hook · offline fake-ERDDAP tests |
| `3d759c5` ⑥ | fork skill (Hestia router step) · README · atlantis_core 0.4.0 |
| `dd103fb` III | F-1 · F-2 · F-5 (fetcher basis, duplicate ids, non-rectangular masks) |
| `32ce244` III | F-3 · F-4 · F-6 · F-7 · F-8 (self-test, doctrine, docs) · learning store · 575 tests |
| close | this AAR · card · roster · charter · STATE · CHANGELOG |

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| Authority: `NOAACRW:` admitted; crosswalk bound; contract v0.3.0; a bare `NOAA CRW` fails by name | `test_item2_crw_authority` (4 cases) ✅ |
| Grid pin written by fork, checked wherever the grid is built and by item 1; a moved vertex is refused; docstrings corrected | `test_polygon_pin_*`, the fork pin test, two conform DEFECTS ✅ |
| Refractory: slot + controls, ALL WORLDS AGREE; R = 0 is byte-identical | 53 controls, sabotage bites; exemplar hash `acfa22c6e4` unchanged ✅ |
| Self-test: accumulating world · C9 · `persistent_master` · the whole catalogue × 3 + the exemplar's 16 · plants by name · exemplar receipt re-issued | 12 × 3 + 16; 8 refractory plants + the iid boundary; receipt green ✅ |
| `CoralReefWatch`: built · per-feature mask + fallback · reduction computed · offline-tested · plant · live smoke in the AAR only | `test_fetch_crw.py` (15); smoke below ✅ |
| Skill: Hestia router-row memo step and notes | `skill_atlantis_instance_fork.md` step 7 ✅ |
| Exemplar byte-stable set unchanged | board v2 entry, model/shap/whatif untouched; `test_f8`, `test_equivalence` green; `BOARD.md` up to date ✅ |
| III review via `iii/`, fresh context; AAR | PASS-WITH-FINDINGS, 8/8 addressed; this file ✅ |

## Live smoke (scratch only; no byte committed, SO-3)

`CoralReefWatch` against `coastwatch.noaa.gov`, `noaacrwdhwDaily`, 2023, two synthetic zones near Looe Key:
- **A Looe-Key-sized square:** no cell centre inside it, so it fell back to 1 cell. That cell is shared with the wider zone,
  and both facts are recorded.
- **A Lower Keys box:** 18 cells.
- **Weekly max DHW:** first ≥ 4 °C-weeks in the week of 10 July (Lower Keys 5.37), about 17–18 by late September, still
  13.8 in mid-October. **A persistent event, as the refractory assumes.**
- **Wall-clock risk:** CRW returned three 502s before answering. The full M-2a-ii fetch (1985–2025 × zones × 4 products)
  is a wall-clock and retry budget, not a token budget.

## Worked

- **Surveying before forking.** The card would have discovered the gaps one red conform item at a time inside a new vault.
  Instead, planning found six of them in an hour, from code.
- **R absent ≡ 0, hashed only when set.** The exemplar kept `acfa22c6e4`, and board v2 was untouched.
- **The accumulating world earned its keep.** Three plants (refractory on the weekly mean, on the raw signal, and counted
  in rows) pass every other check and fail only C9's episode check, which is recomputed from the raw frame.
- **Plants before claims.** Every guard in this mission was shown to fail on a defect written into the real path. Twice
  this was before the claim was made (the envelope mask and the flicker).

## Didn't

- **The first episode design was wrong.** The weekly max smoothed the planned dip away, so the world had one crossing run,
  not two. It was found because C9 refused a vacuous episode, and the episode was re-tuned by simulation.
- **The first mask test was blind.** Against a linear value field, a symmetric padding has the polygon's own mean, so the
  envelope-mask plant passed. It is non-linear now.
- **"R = H matches lead.py" was asserted and never tested, and it is off by one (III F-4).** It had been written into five
  places, and M-2a-ii was about to set R = 8 on it.
- **The CRW cache was keyed by what was convenient, not by what was evaluated (III F-1).** A deliberate re-pin would have
  served the old zones' data with a clean summary.
- **The boundary probe skipped more often than its condition said (III F-3).** The first self-test fix in this mission
  repeated C-015, its own known pattern.
- **Budget:** ≈ +57% on main. The +50% line was crossed by the III fixes the operator ruled, not by drift.

## Findings of record

1. **The grid pin had never existed.** `polygons.py` and the template had said since M-1b-i that the zone file was "pinned
   by sha256", and nothing hashed it. That is C-023's class, found by reading the code at planning.
2. **A persistent event needs an onset refractory, and the doctrine is R = H − 1.** With R = 0 a DHW flicker (decay below
   threshold, then a re-cross) counts as a second onset. R = H − 1 keeps exactly the onsets `eval/lead.py` counts, and
   `tests/test_label_refractory.py` pairs the two modules. **FKNMS proposal: R = 7.**
3. **A cell can belong to two zones, and a zone can be smaller than a cell.** Both are now recorded per zone
   (`shared_cells`, `fallback`). They are review items for the steward, not errors.
4. **One planted defect reaches the persistent world by another road.** That world has no `weekly_min` vital, so a leaky
   `weekly_min` reaches only C5's mirror label. Expectations are named per world (`WORLD_EXPECT`), not widened.
5. **Licence caveat for M-2a-ii.** The PacIOOS mirror of CoralTemp v3.1 carries an OSTIA academic-only clause for
   1985–2002, which CRW's own licence text does not repeat. The steward rules on it at the posture ADR.

## III review (fresh context, via `iii/` → `skill_iii_review`, III v0.6.0)

**Verdict: PASS-WITH-FINDINGS: 4 major, 4 minor. All 8 addressed** (operator ruling "fix all 8", AskUserQuestion, after the
+50% SITREP). F-4's doctrine was ruled at the same time: the docs change to R = H − 1, and the label rule stays.

| # | Sev | Finding | Fix |
|---|---|---|---|
| F-1 | major | A re-pinned zone file reused the old zones' data: the cache was keyed by uid and years, and the summary did not record its basis | Cache keyed by pin · pad · variable. The reduction records `grid_sha256` · `pad_deg` · `variable` · `base`. A different basis, or no reduction on record, is refused by `fetch`, `--verify` and conform item 3. 3 plants |
| F-2 | major | Duplicate zone ids collided in cache, rows and record | Refused by `PolygonGrid`, conform item 1 and fork. 3 plants |
| F-3 | major | The C9 boundary probe was skipped too broadly, so R+1 passed at R = 4 (iid). The episode check could also return "not checked" silently | Gap weeks are filled, so the probe always runs. An unrecomputable signal is refused. `weekly_{max,min,mean,median}` are supported. C9's outcome is on the receipt |
| F-4 | major | "R = H ≡ lead.py onset" is off by one | Doctrine is R = H − 1 everywhere it was written. Paired test (coverage 1.0 at H−1, 0.5 at H). Test world and the M-2a-ii card use R = 7 |
| F-5 | minor | The mask tests used rectangles only | Triangle, holed and MultiPolygon zones with hand-written membership. A bounding-box mask plant fails all three |
| F-6 | minor | A station-keyed above event with R > 0 crashed (no unit column) | The accumulating default and opt-in are `unit_daily` only. Test |
| F-7 | minor | Raw vs carried, and rows vs weeks, were indistinguishable | An lk+1-week gap after a crossing in the episode, an expectation that models the carry, and 2 plants (raw, rows) caught only there |
| F-8 | minor | Docs: "C9 proves past-only"; README fixture counts stale since M-1d-i; the code hash missed `grid/` | Text corrected (C1/C2 prove past-only; C9 proves bite and length). Counts 6 · 47. `selftest_code_hash` covers `grid/` |

**ACCUMULATE (local store):** C-023 +1, C-010 +1, C-015 +1 (→ 3), C-005 +2 (→ 4). New: C-024
`entity_id_assumed_unique`, C-025 `cross_module_equivalence_asserted_untested`. **Graduation candidates at frequency ≥ 3:
C-004 · C-005 · C-009 · C-015** (WI-20: the ceremony at III.aDNA is the operator's).

## Change

- **A claim that one module agrees with another needs a test that runs both** (C-025). Add it to the review checklist.
- **A cache key is a provenance claim.** Key it by everything the cached value depends on, and record that basis beside
  the value (C-010, C-023).
- **Every skip a check takes is a C-015 risk.** Prefer moving or repairing the probe to skipping it, and put the outcome
  on the receipt.

## Follow-up

1. **M-1f** (opus): the horizon embargo, board v3. Queued; its prompt is in STATE.
2. **M-2a-ii** (opus, after M-1f). Carry in:
   - R = 7;
   - the OSTIA licence ruling;
   - which zone layer applies, and the grouping of sub-cell zones;
   - a CRW wall-clock and retry budget;
   - review the `reduction` block with the steward.
3. **M-2b:** the persistence/trend baseline (carded). CRW's internal MMM climatology is invisible to R7 and C6 (core README
   §Known limits), so name it on the instance page.
4. **WI-20:** four graduation candidates (C-004, C-005, C-009, C-015).

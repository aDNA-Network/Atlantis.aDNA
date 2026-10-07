---
type: session
created: 2026-10-06
updated: 2026-10-06
last_edited_by: agent_proteus
tags: [session, m2a_i, p2, crw, refractory, polygon, selftest, atlantis, tidewatch]
session_id: session_stanley_20261007_023031_m2a_i_core_for_persistent_polygon_instances
user: stanley
started: 2026-10-07T02:30:31Z
status: completed
completed: 2026-10-06
executor_tier: opus
mission: mission_m2a_i_core_for_persistent_polygon_instances
campaign: campaign_atlantis_genesis
intent: "M-2a split (operator ruling 2026-10-06). M-2a-i = the Atlantis-side core changes an FKNMS (persistent, polygon, gridded) instance needs: CRW authority · grid sha256 pin · label refractory · persistent self-test world + whole catalogue (C-014) · CoralReefWatch polygon fetcher · fork skill. Plan: ~/.claude/plans/please-read-the-claude-md-purrfect-ritchie.md"
---

## Activity Log

- open — Condition (c) probed during planning (read-only): CRW serves `noaacrw{dhw,hotspot,sst,sstanomaly}Daily` on coastwatch.noaa.gov ERDDAP; the ascending-lat query that ERDDAPGriddap emits works; PFEG NOAA_DHW timed out. **Condition (c) MET.** Rulings (operator, AskUserQuestion, 2026-10-06): (1) split M-2a into i / ii; (2) FKNMS zones + an Atlantis-side polygon reducer; (3) H = 8, one window t+1…t+8; (4) the horizon embargo runs as its own lane (M-1f) between M-2a-i and M-2a-ii.
- 0 inbox (`9873844`): Noether's LinkML Profile v0.1 memo triaged, no action; this commit is the read-receipt.
- 1 cards (`88e3de1`): M-2a-i, M-1f and M-2a-ii carded; M-2a superseded; M-2b gains a persistence baseline; roster, charter, STATE and the backlog updated.
- ① authority (`d3e24bb`): `NOAACRW:` admitted by conform item 2; crosswalk row bound; contract v0.3.0 (minor).
- ② grid pin (`090d69d`): `grid.sha256` written by fork, checked by `make_grid` and by conform item 1. **FINDING:** the docstring and template had claimed this pin since M-1b-i, with no code behind it (C-023 class).
- ③ refractory (`81bb8fa`): `refractory_weeks` (atl_v0 0.5.0 + the NOAACRW prefix; 53 controls, ALL WORLDS AGREE, sabotage bites). R absent/0 is hashed only when set, so the exemplar keeps `acfa22c6e4`.
- ④ self-test (`2e6202d`):
  - the accumulating world, C9, and `persistent_master`; the whole catalogue × 3 worlds;
  - 6 refractory plants, each caught by name;
  - **FINDING:** in the persistent world, weekly_min_next is caught by C5, not C1/C8, because no weekly_min vital exists. The expectation is named per world.
  - My first episode design had no flicker under weekly max; it was re-tuned by simulation.
- ⑤ CoralReefWatch (`277f785`): built; `bind` hook; offline fake-ERDDAP tests. **FINDING (self-caught):** the envelope-mask plant passed against a linear test field, so the field is now non-linear. Live smoke: 2023 Lower Keys DHW ≥ 4 from 10 Jul, reaching ~18; the Looe Key zone fell back to 1 cell; three 502 retries.
- ⑥ skill + README + core 0.4.0 (`3d759c5`). Full suite **558 passed**; BOARD up to date; exemplar receipt re-issued (`acfa22c6e4`, iid, R 0).
- Budget: main ≈ 270 kT against a 180–220 kT card (≈ +20%), under the +50% line. III next.
- III (fresh context): PASS-WITH-FINDINGS, 4 major + 4 minor. Budget SITREP at the +50% line → operator ruled (AskUserQuestion) **fix all 8**, and for F-4 the docs change to **R = H − 1** while the label rule stays. Fixed in `dd103fb` (F-1, F-2, F-5) and `32ce244` (F-3, F-4, F-6, F-7, F-8 + learning store: C-024, C-025 new; C-005 → 4, C-015 → 3).
- verify: **575 tests** (one test placeholder zone file `{}` fixed — fork now reads the file) · 53 controls ALL WORLDS AGREE · exemplar receipt re-issued (`acfa22c6e4`, core 0.4.0, iid) · BOARD up to date.
- close: AAR · card completed · roster · charter · STATE (M-1f queued, self-contained prompt; WI-19 CRW built, WI-20 candidates, WI-24 OSTIA licence) · CHANGELOG v0.10.0.

## SITREP

- **Completed:** M-2a-i. The core changes FKNMS needs are made: NOAACRW authority · grid pin · refractory (R = H − 1) · persistent self-test world · CoralReefWatch built. **P2 condition (c) MET.** III 8/8.
- **In progress:** none.
- **Next up:** **M-1f** (opus; horizon embargo → board v3), then M-2a-ii (the FKNMS fork and fetch, R = 7), M-2b, and the P2 gate.
- **Blockers (`#needs-human`):**
  - the **push** (`4492b9b..HEAD`);
  - graduation candidates C-004, C-005, C-009 and C-015 (WI-20);
  - the OSTIA licence ruling at M-2a-ii (WI-24);
  - the III graduation memo delivery (carried).
- **Files touched:** what/atlantis_core (conform, fork, label, config, selftest, grid, fetch/{crw,base,__init__,__main__}, tests, README, pyproject, uv.lock) · what/schema/atl_v0 (linkml, JSON, README, crosswalk, 3 controls) · how/templates · how/skills/skill_atlantis_instance_fork · instance contract · federation README · the iii learning store · cards, roster, charter, STATE, CHANGELOG · the inbox.
- **Next Session Prompt:** in STATE § ⏭ QUEUED (M-1f, open at opus).

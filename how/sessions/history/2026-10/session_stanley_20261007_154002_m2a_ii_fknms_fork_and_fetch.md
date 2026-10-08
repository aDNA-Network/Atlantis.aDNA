---
type: session
created: 2026-10-07
updated: 2026-10-08
last_edited_by: agent_proteus
tags: [session, m2a_ii, p2, fknms, coral, fork, fetch, atlantis, tidewatch]
session_id: session_stanley_20261007_154002_m2a_ii_fknms_fork_and_fetch
user: stanley
started: 2026-10-07T22:40:02Z
status: completed
completed: 2026-10-08
outcome: checkpointed   # M-2a-ii sitting 1 of 2; the mission stays in_progress
executor_tier: opus
mission: mission_m2a_ii_fknms_fork_and_fetch
campaign: campaign_atlantis_genesis
intent: "M-2a-ii — fork FloridaKeysCoral.aDNA (skill_atlantis_instance_fork) and fetch its CRW/OISST data. Plan: ~/.claude/plans/please-read-the-claude-md-velvet-aho.md"
---

## Activity Log

- open — Steward rulings (Stanley, AskUserQuestion, planning sitting 2026-10-07):
  1. **Zoning: pre-Blueprint** (1997 zones + 2001 Tortugas ER). Context: the Restoration Blueprint final rule (FR 2025-00496, 2025-01-17) took effect 2025-03-05 in **federal waters only**. The Governor rejected it in state waters, which reverted to the 1997 rules, and NOAA has said a full withdrawal is possible (Keys Weekly, 2025-06-19).
  2. **Licence: CRW-native from 1985**, with the PacIOOS-mirror OSTIA caveat recorded in the posture ADR (WI-24).
  3. **Split: min_train 1986 · train ≤ 2013 · val 2014–2018 · test 2019–2025**, fixed before any fetch.
  4. **Geometry is a declaration**: the public zone boundary is downloaded by a recorded recipe before the fork (fork pins its sha256), and the posture gate governs every data fetch. This is a deviation from the card's "before any network fetch", recorded for the AAR.
- 1 geometry: the pre-Blueprint layer is on NCCOS `BenthicMapping_FKNMS_Dataviewer` MapServer: layer 52 "FKNMS Management Zones" (23 polygons: 18 SPA [ZONE_ 1], 4 research-only [3], Western Sambo ER [2]; buoy corners Dec 1999), plus layer 51 "Tortugas Ecological Reserve" (N, S; Federal Register coordinates). There are no WMAs in the layer. Both were downloaded as `f=geojson` and `outSR=4326` at 2026-10-07T22:40:40Z. sha256: layer52 `8e7c4c05…d6d3`, layer51 `97f1ca86…479e`.
  - **Offline cell test** (the core's `geometry_contains` against CRW 0.05° centres; the land mask can't be known offline): 23 of 25 zones fall back to one nearest cell, and **Western Sambo ER (30 km²) falls back too**. Only Tortugas N (8 cells) and S (5) are zone means. 4 pairs share a cell: Conch SPA + Conch RO · Davis + Hen and Chickens · Rock Key + Sand Key · The Elbow + Key Largo Dry Rocks.
  - **Rulings (Stanley, AskUserQuestion):** (5) **merge the cell-sharing pairs into one MultiPolygon each**, giving 21 patients, each a distinct pixel; (6) **drop OISST** for M-2a-ii, so the fetch is the four CRW products only; OISST can return later as a ledger candidate.
- 2 vault shell: `skill_project_fork` step 3 run at the workspace root → `~/aDNA/FloridaKeysCoral.aDNA` (3 inherited ADRs stamped `template_inherited` v8.12). **Rulings:** (7) licence **MIT**; (8) persona deferred, with a minimal instance CLAUDE.md (`persona: tbd_at_p0`). Geometry: `what/geometry/build_zones.py` (stdlib, deterministic; the sources are sha256-checked; 3 builds give one hash) → `fknms_zones_pre_blueprint.geojson`, 21 patients, sha256 `919ff180…3eafc`. Offline re-check: 19 of 21 fall back, **0 shared cells**.
- **FINDING (WI-24 premise wrong):** CRW's *own* `noaacrwsstDaily` licence attribute carries the OSTIA 1985–2002 terms: academic-only, a 5-year use limit, a reproduction-licence application, a Crown-copyright notice. DHW, HotSpot and SSTA carry only CRW's "without restriction; credit + DOI". (Metadata probe of `info/<id>/index.csv`; no data fetched.) **Re-ruling (9), Stanley, AskUserQuestion:** drop the raw SST stream; DHW, HotSpot and SSTA from 1985 under CRW's licence, with the CoralTemp-derivation residual disclosed in the posture ADR. Also from the metadata: SSTA `standard_name` = `surface_temperature_anomaly` (so a CF authority exists); DHW time coverage starts 1985-03-25.
- ① `0e4154b` **fork gap:** the card's `eval.sensitivity_threshold: 8` had no path from the interview, so fork now renders `answers.eval` (a closed vocabulary). atlantis_core **0.5.1**, bumped before any instance output. 640 tests.
- fork (`--answers how/atlantis_fork/answers.yaml`): clean on the first pass (R1–R8; 3 streams; 9 starter vitals). mapping ✅. conform declared: item 6 ✗.
- ② `f23e046` **core defect:** the self-test ran C6 unconditionally, giving `KeyError: 'in_era_week'` for an instance with no climatology (every fixture had one). C6 is now n/a, said on the console and the receipt (`C6_status`), and a climatology without its week is refused by name. The regression test fails without the fix. 641 tests.
- The instance pin was bumped deliberately (`0e4154b` → `f23e046` → `95ea8da`). Receipt `0d4d2bb19e` (core 0.5.1; accumulating world, C9 ok, C6 n/a). **conform declared: conforms**, 10 pass, 2 n/a. The fetch before ratification was **refused** by name; no data was written.
- **Steward review (AskUserQuestion):** (10) the 9 starter vitals and tags accepted (no levers); (11) budgets 5/10/20%, lead at 10%; (12) **ADR-001 ratified, signed stanley 2026-10-07**, frontmatter set to agree; `posture_problem` → None. The ADR carries the licence table, the WI-24 correction, the citation (Skirving et al. 2020, doi:10.3390/rs12233856) and geometry-as-declaration.
- ③ `95ea8da` **fetch defect:** CRW's DHW begins 1985-03-25, and ERDDAP refuses an earlier start with a 404 that is not "No data", so the 1985 chunk gave up. The new optional `start` in the ERDDAP/CRW spec clamps the first chunk only. 642 tests. The instance spec gained `start: "1985-03-25"`; the receipt is unaffected (fetch spec is not hashed).
- **CRW outage:** from ~23:13Z every request, including `info/`, returns 502 Proxy Error after ~10 s, at any chunk size. The retry loop was stopped and a per-minute probe armed (cap 3 h).
- Governance kit: minimal CLAUDE.md (persona `tbd_at_p0`), MANIFEST (`license: MIT`), LICENSE, STATE (geometry recipe), AGENTS stamped. **Hestia memo** delivered to the Home drop-box (md5 equal; untracked for receipt): `who/coordination/coord_2026_10_07_proteus_to_hestia_floridakeyscoral_router_row.md`. Instance genesis commit `d7f5e31` (gitleaks clean; no data).
- **Budget SITREP at ~+80% (~290 kT):** steward ruled finish all. CRW came back at 23:23Z, then fell again: 8 probe-gated
  attempts cached 0 of 567 chunks. At 00:02Z all of `coastwatch.noaa.gov/erddap` (index included) returned 502. PacIOOS
  `dhw_5km` answered, but its global licence attribute is the OSTIA statement, which conflicts with ADR-001. **Steward
  ruled: checkpoint; fetch next sitting.** Loops stopped; no bytes written (the gitignored receipt only). Instance
  `3e45b93` records the checkpoint.
- close: card in_progress (§Progress of record, ⏳ criteria) · roster · charter · STATE (sitting-2 prompt; WI-24 ruled)
  · CHANGELOG v0.11.1. No AAR yet: it is filed at mission close (SO-6).

## SITREP

- **Completed:**
  - steward rulings 1–12;
  - `FloridaKeysCoral.aDNA` forked and governed (MIT; persona deferred);
  - zone geometry by a recorded recipe (21 patients);
  - declared stage conforms (items 1–8 and 11–12);
  - receipt green; ADR-001 ratified;
  - fetch-gate refusal demonstrated;
  - Hestia memo delivered;
  - three tested core fixes (core 0.5.1, 642 tests);
  - WI-24 corrected.
- **In progress:** the fetch, blocked by a CRW ERDDAP outage.
- **Next up:** M-2a-ii sitting 2 (prompt in STATE): fetch → provenance → `--verify` → `conform --stage fetched` →
  reduction review → instance commit → III (fresh context) → AAR → queue M-2b.
- **Blockers:** `#needs-human`: none. External: CRW availability.
- **Files touched:**
  - **Atlantis:** `what/atlantis_core/{pyproject.toml, uv.lock, src/atlantis_core/{__init__,fork,selftest}.py,
    src/atlantis_core/fetch/{erddap,crw}.py, tests/{test_fork,test_fetch_crw}.py}` ·
    `how/templates/template_instance/answers.example.yaml` · `who/coordination/coord_2026_10_07_proteus_to_hestia_*` · the
    card · roster · charter · STATE · CHANGELOG.
  - **Instance:** all of it (new).
  - **Home:** one inbox memo (untracked).
- **Next Session Prompt:** STATE § ⏭ QUEUED (open at opus).

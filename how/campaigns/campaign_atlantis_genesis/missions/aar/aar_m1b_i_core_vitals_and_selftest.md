---
type: aar
doc_id: aar_m1b_i_core_vitals_and_selftest
title: "AAR — M-1b-i atlantis_core: registries, fetch, grid, vitals, label, all-stream self-test (P1, Operation Tidewatch)"
mission: mission_m1b_i_core_vitals_and_selftest
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: opus
token_budget_estimated: "~140kT main + fresh-context III reviewer"
token_budget_actual: "~240kT main context (≈ +70%) + ~172kT fresh-context III reviewer. The trigger was met by a SITREP at the trip point and an operator ruling ('fix all now, accept overrun') — Finding 5"
session: session_stanley_20261003_014043_m1b_i_core_vitals_selftest
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [aar, m1b_i, p1, atlantis_core, selftest, iii, atlantis, tidewatch]
---

# AAR — M-1b-i `atlantis_core` skeleton

**Commits.** The mission ran as five commits:

| Commit | Content |
|---|---|
| `67c602b` | open: the split and the re-card |
| `87c7243` | ②③ skeleton and registries |
| `8e69da8` | ④ vitals, label and self-test |
| `767ea73` | ⑤ III-review fixes |
| close | bookkeeping |

**Operator rulings, all by `AskUserQuestion`:**
1. Split M-1b into i and ii.
2. Fetchers: 3 real and 3 declared.
3. The SST lag defect: lag by calendar, and re-read M-1b-ii's reproduction bar.
4. At the budget trip: fix all review findings now and accept the overrun.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| Package · `config` (+`semantic_hash`) · `registry` | `what/atlantis_core/` · `tests/test_registry.py`: R1–R7 each bite; the hash ignores prose, key order and fetch details, and moves on 6 training changes |
| `fetch/` 3 real + 3 declared | `ArcGISMapServer` · `ERDDAPGriddap` · `NWISDailyValues` are built. `NDBCStdmet` · `OBISOccurrence` · `GBIFOccurrence` · `CoralReefWatch` are declared. `tests/test_fetch.py` covers offline mode (never touches the network), pins re-hashing to the summaries **and** to `streams.yaml`, and the stubs raising with their endpoint named |
| `grid/` rules · polygons · cells | `tests/test_grid.py`: whitelist rejects 9 escape attempts; the **9 frozen exemplar region counts** hold; a GeoJSON polygon with a hole, a MultiPolygon and a cell grid |
| `vitals/` registry, not literals | `features.yaml` (25 `AtlVital`s) replaces `FEATURE_GROUPS`/`FEATURE_DOC`. The 52.18-week season, 30/20-day window, 104 cap, climatology eras and 4-week carry-forward are now config |
| `label/` above / below, both drops | `label.make` and `finalize`. C5 covers `below`. `finalize` refuses kept rows that have no label |
| **All-stream self-test** | `python -m atlantis_core.selftest --instance …` ✅ on all 3 streams. **16 planted defects** in `tests/test_selftest.py`, each caught by its named check |
| Registries validate; controls still agree | `linkml-validate -C AtlDocument` → "No issues found" ×3; committed JSON Schema PASS ×3; a null-owner sabotage is rejected; `run_controls.sh` → ALL WORLDS AGREE (42); schema untouched |
| **Equivalence** | `tests/test_equivalence.py` covers the grid (25,011 rows), 22/25 vitals exact, the label, both drop flags and the report (10,804 rows · 1,168 positives · 1,481 + 1,800 dropped). The 3 SST-lag vitals equal `hab`'s lag-0 series shifted by **calendar** weeks on every row. Finding 1 |
| Byte-stable; `hab` self-test green | `git diff` empty for `config.yaml` and `outputs/`; `hab.build_features --self-test` ✅; exemplar pytest 11 ✅ |
| III review via `iii/`, fresh context | PASS-WITH-FINDINGS: 6 major and 5 minor, **all 11 fixed** (`767ea73`); learning store C-005…C-007 |

`what/atlantis_core`: **89 tests pass offline** (~40 s).

## Worked

- **Registries first.** The 25 vitals became data with no schema change. `transform` already allowed "a registry key", and a
  whitelisted call grammar (no `eval`, the same discipline as the region rules) carries the recipe. The closed `AtlDocument`
  never needed an extension slot. Engine-only facts went to `atlantis.yaml`, drift-guarded against `config.yaml` by a test.
- **The equivalence test found a real exemplar defect within one run** (Finding 1), and a 3-step measurement brought it to the
  operator as a costed decision instead of a silent choice: locate the gaps, prove every differing row is predicted, then refit
  in memory.
- **The fresh-context review earned its cost.** The reviewer demonstrated six defects passing the first self-test, each with
  its real-data damage. Every one is now a permanent planted-leak test.

## Didn't

- **The first self-test was too weak for the invariant it guards** (Finding 2). It used one unit and dense data, and had no
  check on the row filters or on the horizon from inside. The producer wrote it and believed it, which is the M-1c lesson again
  (C-003: claiming by analogy).
- **The first C6 checked only week t** and printed "moves nothing" for OISST, which was technically true and misleading.
  The producer caught this before the review, by diffing the whole past.
- **Typed from memory:** the 9 frozen region counts in the first `test_grid.py` were invented. They were caught before the
  first run by checking the exemplar's test, which is still a C-004-shaped slip.
- **Learning-store schema:** the first append of C-005…C-007 ignored the store's field set and was rewritten.

## Finding

1. **The exemplar's SST lags were counted in rows, not weeks.**
   - **Cause:** OISST is missing 20 whole weeks (1993–98 and 2023-12-25), and `hab` shifted the weekly SST table by row. Across a
     gap, `sst_anom_t2` was a 3–4-week lag.
   - **Not leakage:** a row shift reaches older data, not newer.
   - **Scope:** 87–133 modelling rows, all in train (1994–98). In the full table the defect also touches 1993 and 2023 (a test
     year), whose rows the label filters happen to drop.
   - **Cost:** the calendar-correct refit gives test AUROC 0.8941 → 0.8938 and AUPRC **0.5473 → 0.5388**. AUPRC is sensitive to
     about 1% of train rows (127 test positives), which is itself evidence for SO-9's "never round a base rate away".
   - **Ruling:** atlantis_core lags by calendar. M-1b-ii lands the corrected run as a new board version, and `metrics.json` stays
     byte-stable.
2. **A perturbation self-test is only as good as its synthetic world.**
   - **Shape:** dense, single-entity data cannot see row-vs-calendar shifts, back-fills, observed-week horizons or cross-unit
     scrambles.
   - **Scope:** invariance must cover the **row filters** (`already_in_event`), not only features and target, and every window
     needs a control just inside each edge.
   - Learning store C-005, C-006 and C-007.
3. **A climatology normal is a whole-era statistic.** Inside its era, week t+1 feeds the anomaly at the same calendar week in
   *every* earlier era year, not just at t. The self-test now reports this (C6: real dependence vs pandas running-sum float residue
   ~1e-15) instead of hiding it. R7 keeps eras before validation. **And** the exemplar's discharge era (→2016) overlaps the
   rolling-origin fold that tests 2016, so `hab`'s reported rolling panel was not refit. R7 now records this as an **obligation**
   on M-1b-ii's eval.
4. **`semantic_hash` was blind to `weeks_since_cap`** (III F-6). A hash meant to be "training-relevant" must be tested by
   mutating each training-relevant field. One field had been missed.
5. **The budget trigger was honoured this time.** At ≈35% over with the review findings known, a SITREP went to the operator
   before the fixes that would cross +50%. The operator ruled to fix all. That closes M-1c Finding 4's open behaviour. Card size
   is still wrong: two sittings in a row ran at about 1.7–5× the card.

## Change

- **Card sizing:** for a mission whose deliverable is a test of an invariant, card main context at about 1.7× the build
  estimate, and budget the reviewer at the same size as the build.
- **Self-test design rule (template for M-1d's fork skill):** ≥ 2 entities, at least one isolable; deliberate gaps around t; the
  real ingest path; per-vital positive controls; filters in the invariance set; both window edges. Every defect class planted
  and named.

## Follow-up

- **M-1b-ii** (card updated):
  - land the calendar-correct run as a new board version;
  - honour the R7 refit-per-fold obligation;
  - record the semantic hash (closes WI-7);
  - build eval, explain, board and site, the learner swap and `mapping.yaml`;
  - archive `src/hab/`.
- **WI-10 (new):** the exemplar's reported rolling-origin panel in `metrics.json` includes a 2016 fold scored with a discharge
  normal that contains 2016. Note this on the board when the new version lands.
- **v1 schema candidates:** a `calendar` modality for vitals that read no stream (README Known limit 10).
- **M-1d:** the fork skill must generate an instance whose `selftest.patients` meets the two-patient, one-isolable rule (`selftest.patients()` already
  refuses fewer than two; isolability is only reported, as C7 "skipped").

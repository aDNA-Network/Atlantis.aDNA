---
type: mission
mission_id: M-3b-ii-a
plan_id: mission_m3b_ii_a_ndbc_fetch
title: "M-3b-ii-a — NDBCStdmet built (WI-19) + the calm-day grammar op, core 0.10.0 · the reef-light wind stream fetched into FKNMS (Keys-wide index) · conform fetched · III"
owner: stanley
status: completed
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "main ≈ 150 kT → RE-CARDED ≈ 420 kT at the SITREP (ruling 7, operator, 2026-10-12; the +50% line ≈ 225 kT was crossed during the two live-fetch fixes and reported ≈ 65 kT past it, at ≈ 290 kT — C-042, III F-9) (+50% line ≈ 225 kT) · no reader lane · fresh-context III reviewer ≈ 150 kT (III M-3b-i F-10: lines at observed sizes; the last two III reviewers metered 278 and ≈ 200 kT, so 150 is the floor, not the expectation)"
token_budget_actual: "main ≈ 400 kT on the session counter (planning included) · III reviewer ≈ 300 kT metered (forensics on the raw data) · no reader lane"
depends_on: ['M-3b-i']
split_from: mission_m3b_ii_realise_and_test
origin: "M-3b-ii ruling 1 (operator, AskUserQuestion, 2026-10-12, at open): build + fetch / realise + test"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_ii_a_ndbc_fetch.md
session: session_stanley_20261013_011418_m3b_ii_a_ndbc_fetch
created: 2026-10-12
updated: 2026-10-12
completed: 2026-10-12
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_ii_a, p3, opus, ndbc, fetcher, wi19, fknms, atlantis, tidewatch]
---

# M-3b-ii-a — build NDBCStdmet and fetch the reef-light wind

**Split from** `mission_m3b_ii_realise_and_test.md` (M-3b-ii ruling 1). The other half is
`mission_m3b_ii_b_realise_and_test.md`, which starts from the fetched, conformed stream this half leaves.

## Rulings at open (AskUserQuestion, 2026-10-12)

1. **Split** (operator): this half builds and fetches; ii-b realises and tests.
2. **Station map** (steward): a **Keys-wide synoptic index**. One daily series, the mean over the reef lights reporting
   that day {MLRF1 · SMKF1 · LONF1 · SANF1}, given to all 21 zones; the reporting set recorded. Why: MLRF1 ends in 2019,
   SMKF1 lacks 2016–17, and the Tortugas zones are 110–125 km from any station live in 2020–25, so any per-zone nearest
   map changes station, or goes empty, exactly in the test window. Cost: no per-zone contrast; the self-test's C7
   (cross-unit isolation) cannot isolate a broadcast stream and is skipped (a recorded limit).
3. **Calm threshold** (steward): scanned on val — executed in ii-b.

## Probe (read-only GETs at open; nothing cached)

NDBC historical stdmet yearly files: MLRF1 1987–2019 · SMKF1 1988–2015, 2018–25 · LONF1 1992–2025 · SANF1 1991–2025.
Three formats were seen at the probe: before 1999 a two-digit year and no minute; 1999–2004 a four-digit year; from 2005
a `#` header with a units line and `mm`. *(III F-7: the record holds **four** — 2005–06 is `YYYY … mm` with no `#` and no
units line; 10-minute rows start in 2019 at three lights.)* Missing values are 99.0 / 999.

## Acceptance criteria

- [x] `NDBCStdmet` built in `atlantis_core` (a template change, the P2 rule): **four** header forms (III F-7), sentinels →
  NaN, a daily mean with a declared minimum of observations, a 404 station-year **confirmed twice and recorded** as absent
  (an empty 200 fails; III F-3), any other failure fails closed, the station-years present and absent in the fetch
  summary; `BUILT`; core **0.10.0** → **0.10.1** (the III fixes: QC flag columns, conflicting duplicates dropped, the raw
  cache pinned)
- [x] A calm-day operation in the vitals grammar (`weekly_count_lt`), counted on the unit-level daily value, a no-data
  week NaN (not 0); `constants:` names allowed as its threshold
- [x] Offline tests (no sockets), each guard mutation-checked plant-first (11 at the build, 17 at the fixes; 6 plants were
  blind at first and their tests were tightened)
- [x] FKNMS: the stream declared (`streams.yaml` + `atlantis.yaml`, ruling 2's map), the NDBC posture ruled, `mapping.yaml`
  pin → atl_v0 0.9.0 (upkeep), the federation pin bumped, self-test green with its receipt (SO-7), fetched,
  `fetch --verify` ✅ ×4, **`conform --stage fetched` all pass except item 9, outstanding by construction** (the newest
  entry, v3, is for the pre-wind config; ii-b's run writes v4) — criterion re-worded at close (III F-9), the failure is
  the honest state; **no vitals** (ii-b)
- [x] Suite count recorded with its commit (C-035); `run_controls.sh` ALL WORLDS AGREE
- [x] III review via `iii/` in a fresh context (PASS-WITH-FINDINGS 0/1/8/3, `aar/iii_review_m3b_ii_a.md`); SITREP at the
  +50% line — **late**, ≈ 65 kT past it (C-042, III F-9)

## Guardrails · Escalation

As the parent card. Atlantis itself never fetches (SO-3): the fetch writes into the instance's cache.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

---
type: aar
mission: mission_m3b_ii_a_ndbc_fetch
campaign: campaign_atlantis_genesis
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261013_011418_m3b_ii_a_ndbc_fetch
tags: [aar, m3b_ii_a, p3, ndbc, fetcher, wi19, qc, fknms, iii, atlantis, tidewatch]
---

# AAR — M-3b-ii-a: NDBCStdmet built, the reef-light wind fetched into FloridaKeysCoral

**Scope.** This is the build half of M-3b-ii, split at open. It covers:
- core 0.10.0 → **0.10.1**: `NDBCStdmet` (WI-19), the `weekly_count_lt` grammar operation, and conform item 9
  supersession;
- the reef-light wind stream declared, self-tested, fetched and verified in FKNMS as a Keys-wide synoptic index.

There are no vitals: ii-b realises and tests them.

**Rulings** (`AskUserQuestion`, 2026-10-12):

| # | By | Ruling |
|---|---|---|
| 1 | operator | Split M-3b-ii into ii-a (build + fetch + III) and ii-b (vitals · val scan · run · SHAP · write-up · III) |
| 2 | steward | Station map: a **Keys-wide synoptic index**, every light → all 21 zones. MLRF1 ends 2019, SMKF1 lacks 2016–17, and the Tortugas have no light in the test era |
| 3 | steward | Calm threshold scanned on val, c ∈ {2…6} m/s; test scored once (executed in ii-b) |
| 4 | steward | NDBC licence: public, under the NOAA/NWS public-domain terms. ADR-001 addendum ratified |
| 5 | steward | `min_hours` 18 |
| 6 | steward | Years 1987–2025 |
| 7 | operator | At the SITREP (≈ 290 kT, ≈ 65 kT past the line): re-card main ≈ 150 → ≈ 420 kT and continue to III |
| 8 | operator | III F-1: QC flags in the fetcher now. No value is deleted; ii-b rules the mask |
| 9 | operator | III: fix the code minors and the card |
| 10 | operator | Accept ACCUMULATE: C-045…C-048, plus ten recurrences. C-042 and C-030 become graduation candidates |

**Commits.**
- Atlantis: `9bbe34f` (split) · `b5629dc` (core 0.10.0) · `e8b79c0` (live parser fix) · `5312f52` (conform item 9) ·
  `590f70b` (site test) · `9084905` (III fixes, 0.10.1), then the close.
- FKNMS: `51c7203` (stream, ADR addendum, pins, first fetch) · `fa0beed` (re-fetch under 0.10.1).

## Worked

- **The probe before the plan.** Reading the NDBC directory listing at open showed the problem early:
  - MLRF1 ends in 2019, and SMKF1 has a two-year hole;
  - the Tortugas are 110–125 km from any light live in the test era.

  So the station map was a steward question with the numbers attached (ruling 2), not a default discovered later.
- **The existing shape carried the ruling.** `station_daily` with `stations: {id: [units]}` already averages a unit over
  its stations. The Keys-wide index needed no mapping code, only a map in which every light lists every zone.
- **Live failure, then a test, then a committed re-reduction.** The first real fetch failed on LONF1 2000: a 17-column
  header over rows of 16 and 17 fields. The fix landed as a test from the live case. The artifact was then re-reduced
  `--offline` under the committed code, with byte-identical output.
- **The review earned its tokens.** The fresh-context reviewer found a **failed anemometer in the test window**.
  LONF1 read 0.14–0.20 × the others for three months of 2020. Neither my sanity read nor any guard saw it. The reviewer
  also found a foreign block in SMKF1's 2020 file (LONF1's record) that file order had happened to resolve correctly.
- **Plant-first, with the misses recorded.** All 28 guards across the two passes turn red when switched off. Six plants
  were blind at first, and each test was tightened until it could see its guard:
  - a no-op unit-level plant;
  - an empty week outside the data's span;
  - the others-median with three stations;
  - a stray hour under `min_hours`;
  - a repeated header that only used the `#` form;
  - the Obs path with no NaN row.

## Didn't

- **The sanity read checked agreement on the wrong window.** I computed r 0.87–0.95 over 2000–15, chosen because all
  four lights reported then. That window excludes the whole test era. I then called what I saw in the test era "LONF1
  drifts calmer". It was a sensor fault (III F-1; C-045 new, C-030 +1).
- **The SITREP came late again**, ≈ 65 kT past the +50% line. This is the third mission running (C-042 → 3,
  now a graduation candidate). The line was crossed in the middle of the two live-fetch fixes, and I reported at the
  first clean point rather than at the line.
- **A test fix claimed more than it did** (`590f70b`). It pinned the site test's streams but not its vitals or its
  metrics. ii-b's first vitals commit would have turned it red (III F-5).
- **The docs counted three header forms.** The record holds four (III F-7).

## Finding

- **A fetcher's honesty lives in its counts.** Each of these looked benign until counted apart:
  - "duplicates" hid conflicting records (F-2);
  - "absent" was one 404, cached forever (F-3);
  - "fetch" was the label on an offline re-reduction (F-6).

  The 0.10.1 summary separates each case it can tell apart.
- **Calm is what a failed anemometer reads.** For a calm-day vital, QC is not hygiene: the fault and the signal point
  the same way. Over 2020-02-27…06-04 the Keys-wide index reads 3.64 m/s, against 6.11 with LONF1 masked. Masking the
  flags drops the test calm share at c = 4 from 29.4% to 27.3%, level with val's 27.6%.
- **Station mix is a second era signal.** The reporting set changes by segment, SMKF1's offset shifts across its gap,
  and the cadence goes from hourly to 10-minute at `test_start`. Each of these moves with the era, and so with the
  base rate. ii-b must rule on them before any vital reads them.
- **A config change after a run stranded every older entry** (conform item 9). The board already knew the
  supersession rule; conform now uses it. This is T9 +1.

## Change

- `NDBCStdmet` (0.10.1):
  - QC flag columns (`qc_low_ratio`, `qc_stuck`); no value is deleted, and the mask is the instance's ruling;
  - conflicting duplicates are dropped and counted;
  - absences are confirmed twice and kept as sidecars, an empty 200 fails, and the current year is refused;
  - the raw cache is pinned and re-hashed by `--verify`;
  - per-year cadence is recorded;
  - all four header forms are documented.
- `provenance.summarise` takes a `fetched_at_source`, so a re-reduction says what it was.
- Conform item 9 holds only the newest entry of each stem to the current hash.
- The site test reads FKNMS as each entry saw it, targets the newest entry, and fails by name on a run that has no entry.
- **Process (proposed for the card template, III F-9):** read the token counter at every commit, not only at clean
  points, so the +50% SITREP comes at the line.

## C-033: register obligations

The touch-check is recorded in `artifacts/thesis_register.md`:
- **T9 +1** (conform item 9);
- **a T7 caution for ii-b**: a failed sensor and a station-mix change both read as calm, and both move with the era.

No row's status changes. T7 and T8 stay with ii-b; T11 and T2 stay with the P3 gate.

## III

**PASS-WITH-FINDINGS 0/1/8/3** (`aar/iii_review_m3b_ii_a.md`; fresh context through `iii/`, ≈ 300 kT metered).

| Finding | Disposition |
|---|---|
| F-1 | QC flags (ruling 8), with the STATE wording corrected |
| F-2 | Conflicting duplicates are dropped |
| F-3 | Absences confirmed and kept as sidecars, the current year refused, the raw cache pinned |
| F-4 | The plant now reaches C1 |
| F-5 | The site test uses the newest entry, filters the vitals, and fails by name |
| F-6 | The re-reduction is labelled, and the version is 0.10.1 |
| F-7 | Four forms, documented and tested; both untested guards planted |
| F-8 | Cadence recorded |
| F-9 | The card carries ruling 7, and the item-9 criterion is re-worded |
| F-10 | STATE numbers use one denominator, with paired station differences |
| F-11 | Documented as a re-implementation, plus an agreement test |
| F-12 | (a) refused · (b) dropped · (c) counted apart · (d) "station" · (e) docstring line |

ACCUMULATE under ruling 10.

**Suite: 851 passed at `590f70b`** (286 s; FKNMS at `51c7203`). **863 passed at `9084905`** (279 s; FKNMS at `fa0beed`).

## Follow-up

- **ii-b, before any vital:** rule the QC mask and the station-offset treatment (fitted on train only), and run a
  SANF1-only sensitivity. Then the vitals, the val scan of c, the run (v4 closes conform item 9), SHAP, the memo and the
  entry, written up either way (T8).
- **The P3 gate:** C-042 and C-030 as graduation candidates (the memo to III.aDNA); the card-template counter check.
- **Carried:** the push (nothing since M-2c-i; gitleaks first), and the items already listed in STATE.

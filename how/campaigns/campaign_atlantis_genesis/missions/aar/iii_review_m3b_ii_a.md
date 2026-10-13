---
type: iii_review
review_of: mission_m3b_ii_a_ndbc_fetch
commits:
  atlantis: [9bbe34f, b5629dc, e8b79c0, 5312f52, 590f70b]   # diff vs 884a800
  floridakeyscoral: [51c7203]                                # diff vs ac3a445
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-12
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 1, minor: 8, nit: 3}
tags: [iii_review, m3b_ii_a, ndbc, ndbc_stdmet, weekly_count_lt, conform_item_9, fknms, wind, so3, atlantis, tidewatch]
---

# III review: M-3b-ii-a (core 0.10.0 `NDBCStdmet` · `weekly_count_lt` · conform item 9 · the FKNMS reef-light wind fetch)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` read at
`v0.6.0` = `be7dba1`; III HEAD is ahead):
- packs: inspect procedures, introspect checks, learning store, vault maintenance;
- the Atlantis local store: 44 corrections, C-001…C-044, all applied as checks.

Modalities: text, code and data. Data was the heaviest: I read all 138 non-empty raw station-year files in FKNMS's
gitignored cache, read-only.

**Reviewer ≠ producer.** I did not write any of this work. I wrote two things: this review, and four rows appended to
the local learning store. Everything else was read-only:
- every mutation, plant and re-reduction ran on scratch copies under the session scratchpad
  (`…/scratchpad/iii_m3b_ii_a/`), which I deleted afterwards;
- FKNMS was copied without its CRW caches for `fetch --verify`, `conform` and the offline re-reduction.

I made no network request. **While I worked, the producer changed two Atlantis files that are not committed:**
`thesis_register.md` and `mission_m3b_ii_b_realise_and_test.md`. I did not touch them. I read their diff once, so that
I would not repeat what the producer is already adding (ii-b obligation 6, "station drift").

## Verdict: PASS-WITH-FINDINGS (0 blocker · 1 major · 8 minor · 3 nit)

**What holds:**
- **The parser reads every real file it was given.**
  - All 138 non-empty raw files parse.
  - `rows_malformed` is 0 everywhere except SANF1 2020. Its 2 are a header and units line repeated at the 1 December
    month boundary, so the count is honest.
  - Two-digit years map to 19xx.
  - The only sentinel in the WSPD column is 99.0, and it becomes NaN.
  - After sentinels are removed, the maximum is 42.0 m/s (SMKF1, 1998: Hurricane Georges). This is plausible. No
    negatives.
- **Timestamps are UTC in every era, tested empirically.** Per station and year, the hour of the mean air-temperature
  maximum is 21–22 UTC and the minimum is 11 UTC (16–17 h and 06 h EST). This holds before 1999, in 1999–2004 and from
  2005 on. Local-time stamps would put the maximum near hh = 16. My knowledge also says NDBC stamps stdmet in UTC, so I
  am **highly confident** that the UTC day boundary is applied correctly.
- **The fetch reproduces.**
  - `fetch --verify`: ✅ ×4.
  - Deleting the artifact and re-reducing `--offline` from the raw cache gives **byte-identical** output: `b2f93211…`,
    42,747 rows.
  - The summary's present/absent years match the zero-byte cache files exactly (5 · 6 · 4 · 3), and they match the
    card's probe listing.
  - 156 = 4 × 39 station-years.
- **conform `--stage fetched`** on a copy: 11 pass, and item 9 is outstanding as stated (v1 and v2 ⓘ; v3 fails against
  `81bca06518`). The self-test re-ran green.
- **Gates and suites are green.**
  - Controls: 126 × 3 worlds, **ALL WORLDS AGREE**.
  - **Full suite at HEAD `590f70b`: 851 passed (276 s)**. That is 849 at `b5629dc` plus one test each in `e8b79c0` and
    `5312f52`, so the arithmetic agrees.
- **Plant-first holds.** I switched off 14 guards, one at a time, on a mirrored copy of the core. The 12 the session
  names each turn their test red. The other two (F-7) are not claimed.
- **Item 9's new logic is sound** (it is keyed per (source, instance, stem)).
  - An entry for another instance with a higher version supersedes nothing.
  - A malformed id is checked in full.
  - Both "skip off" and "min instead of max" turn the new test red.
- **SO-3 and the public-repo rule hold.**
  - The Atlantis range adds no data file. The test fixtures are synthetic, and no NDBC byte is anywhere in the
    Atlantis tree.
  - gitleaks is clean on both ranges (5 + 1 commits).
- **The licence addendum is accurate.**
  - The NWS disclaimer is quoted correctly.
  - The station names are right: Molasses Reef, Sombrero Key, Long Key, Sand Key.
  - "Derived, not official" is stated.
  - The 4-field row is present.

**The one major is about the data, not the code.** The reef-light stream carries a **failed anemometer in the test
window**: LONF1 from 27 Feb to 4 Jun 2020 reads at 0.14–0.20 × the other lights. The stream also carries stuck-at-zero
runs. A calm-day vital is the measurement most exposed to both. Nothing in the fetch, in the sanity read or in ii-b's
draft obligations sees it (F-1).

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| Raw-file survey | `parse_stdmet` over all 138 non-empty files: header form, field-count histogram, minute set, years in file, sentinel and maximum counts, within-file duplicates, non-monotonic time | **Four** header forms, not three (F-7). Hourly rows at `:49/:50/:55` in SANF1 2014–19 and SMKF1 2018–19. 10-minute rows from 2019 at LONF1, SANF1 and SMKF1 (F-8). Stray prior-year rows (e.g. SANF1 2015 holds one 2014 row). Within-file duplicates: 1996 (168 h) and 1998 (24–48 h) are identical. **SMKF1 2020 has 653 conflicting ones** (F-2) |
| UTC check | hour of the ATMP maximum and minimum, per station-year, by era | max 21–22 UTC, min 11 UTC in every era ✓ |
| Plausibility | daily pivot; each light ÷ median of the others, per year and month; runs of identical hourly values | **LONF1 2020 median ratio 0.33**; every other year is 0.78–0.97. 92 days at ratio < 0.4, from 2020-02-27 to 2020-06-04. Zero-runs ≥ 6 h: LONF1 35 (31 of its 34 station-days are in test), MLRF1 24, SANF1 10, SMKF1 12. Longest: SMKF1 1998-07-14, 21 h at 0.0 (F-1) |
| Effect on the Keys-wide index | LONF1 masked for 2020-02-27…06-04; test calm days at c = 2…6 | 90/362/717/1074/1495 → 85/335/668/1023/1447. In the span, the index mean is 3.64 → 6.11 m/s (F-1) |
| SMKF1 2020 blocks | split the file by PRES present/absent; compare hourly with LONF1 and SANF1 | The 2nd block for 06-01…06-05 **is LONF1's record**: r 0.999, 81% within 0.05 m/s. `keep="first"` kept the other block, by file order (F-2) |
| 404 / empty plants | `FakeNDBC` variants | an empty-body 200 is recorded as **absent**. A one-off 404 survives a healthy re-run, which makes **0 requests** (F-3) |
| Re-reduction | scratch FKNMS, artifact removed, `fetch --offline --stream …wind…` | sha256 `b2f93211…` identical. The summary differs only in `fetched_at`/`summarised_at`, and **still says `fetched_at_source: "fetch"`** (F-6) |
| `fetch --verify` · conform | scratch FKNMS | ✅ ×4 · 11 pass + item 9 outstanding ✓ |
| Mutation sweep | 14 single-guard mutations on a mirrored core (`PYTHONPATH`), NDBC + conform tests | 12 red as claimed. **Year-window filter off** and **`weekly_count_lt` Obs path `min_count` off** stay green, 19 passed (F-7) |
| Self-test plant | the calm vital with `shift(-1)`, plus two plants that keep week t non-NaN | `shift(-1)` is caught by **C4** ("NaN at (primary, t)"), and at lag 1 by **C0**. It is never caught by a leak check. `count_t + count_{t+1}` and "next week, else own" are caught by **C1 LEAK**, and the lag-1 sum by C8 (F-4) |
| Site test after ii-b | scratch FKNMS plus one wind vital (ii-b obligation 2), then `_as_the_entry_saw_it` | `RegistryError R2: stream_ref 'atl_stream_fkc_wind_ndbc_daily' not declared` (F-5) |
| STATE numbers | recomputed from the parquet | r 0.877–0.948 ✓ · 247 no-light days ✓ · 4 lights on 56.8% of train days ✓. The test shares and calm shares use mixed denominators (F-10) |
| Suite (C-035) | `.venv/bin/python -m pytest -q -p no:cacheprovider` at `590f70b` | **851 passed** (276 s) |
| Controls | `run_controls.sh` (linkml venv of session c2646ef8) | 126 × 3 · byte-identical JSON · ALL WORLDS AGREE ✓ |
| SO-3 · gitleaks | `git diff --name-only`, `git status --ignored`, `find` · `gitleaks detect --log-opts` on both ranges | No data in the range or the tree from this mission ✓ · no leaks ✓ |

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | new **C-045** · C-030 (recurrence) | **A failed anemometer reads as calm, in the test window, and nothing looks.** <br><br>**The LONF1 fault.** LONF1 comes back on 2020-02-27 after a 6-month gap. Through 2020-06-04 it reads at **0.14–0.20 × the median of the other lights**: monthly means 1.05–1.26 m/s, against 5.3–7.1. In every other year the ratio is 0.78–0.97. Then comes a 13-day gap, and normal readings from 06-17. 65 days read < 1.5 m/s while the others' median is ≥ 4. 31 of LONF1's 34 station-days touched by a run of ≥ 6 h at exactly 0.0 are in test (2019–25).<br><br>**Stuck-at-zero runs.** The same signature appears elsewhere: SMKF1 1998-07-14 (21 h), MLRF1 2011-10-08 (19 h), and SANF1 2020-06-02…04 (in step with the LONF1 record; see F-2).<br><br>**The cost in test.** The Keys-wide index is the mean of the reporting lights. In test, two lights report on 47% of days, so one faulty light carries half the weight. Over 2020-02-27…06-04 the index mean is 3.64 m/s (6.11 with LONF1 masked). Test calm days at c = 3/4/5/6 rise by +27/+49/+51/+48. These are spring weeks whose 8-week horizon reaches the heat season, so they are scored rows.<br><br>**Why nothing saw it.** The sanity read's "agreement r 0.87–0.95" was computed on **2000–15, all four reporting** (`STATE.md:31`). That window was chosen for completeness, and it **excludes the whole test era**. STATE then calls what it saw *"LONF1 drifts calmer too"* (`:33`). LONF1's 2020 annual mean is 2.72 m/s, against ≈ 5.2 in every other year. That is an instrument fault, not drift. ii-b's draft obligation 6 (uncommitted) proposes "per-station offsets" or a "SANF1-only sensitivity". Offsets would not repair a fault that changes the scale for four months. | **Before ii-b's vitals** (a steward ruling, recorded in the stream's reduction):<br>(a) A QC pass over the station-days: flag a light whose daily mean is < 0.4 × the median of the others (or a robust z beyond a threshold) while they report; flag runs of ≥ 6 identical hourly values. Record `days_flagged` per station and reason. Either drop the flagged days from the index or keep them under a ruling.<br>(b) Re-run the agreement read **per segment, test included**, and per station × year. Make it a GREEN table.<br>(c) Re-word STATE: "LONF1 2020-02-27…06-04: failed anemometer (ratio 0.14–0.20)", not drift.<br>(d) Add the QC to `NDBCStdmet`'s reduction block as a template option, so the next instance inherits it. Plant it: a stuck run and a 0.2× station must be flagged. |
| F-2 | minor | new **C-046** · C-024 · C-005 | **Conflicting duplicate timestamps are resolved by file order and reported as benign "duplicates".** The docstring (`ndbc.py:22`) says duplicates are rows *"with the same timestamp across adjacent year files"*. SMKF1 2020 has **653 within-file timestamps** (2020-06-01 00:00 → 06-05 12:40) carrying two different records. The second block is **LONF1's** (hourly r 0.999, 81% within 0.05 m/s), filed into SMKF1's file. From 06-14 to 07-07, the file's only series carries pressure, which SMKF1 lacks for the rest of the year. `drop_duplicates(keep="first")` (`:182`) kept the true-looking block **because it came first in the file**. Reverse the order, and LONF1's failing near-zero record becomes five SMKF1 test days, with nothing to see. The summary says `duplicates: 869` for SMKF1; nothing separates identical from conflicting. The only test (`test_fetch_ndbc.py:153`) builds a cross-file duplicate with different values and asserts that keep-first is right. | Split the count into `duplicates_identical` and `duplicates_conflicting` (by value, over the columns read). Refuse conflicting rows, or drop both and count them, unless a steward rule says which wins. Plant it with a within-file conflicting block. Record SMKF1 2020-06-01…07-07 as a station-identity question for ii-b. |
| F-3 | minor | new **C-047** · C-021 · C-019 kin | **"Absent" is inferred from one reply and cached forever.**<br>(a) `_absent` (`ndbc.py:53`) takes a single 404 with no retry: `base.get`'s `empty_ok` short-circuits before the retry loop. `_year` writes it as a zero-byte file (`:149-152`), and `data or None` (`:154`) reads **any** empty file as absent. In plant P1, an empty-body **200** is recorded as `years_absent`. In plant P2, a one-off 404 survives a later run against a healthy server, which makes **0 requests**.<br>(b) **The current-year trap.** NDBC publishes a yearly file only after the year ends. Extend `years` to the current year, and its 404 becomes permanent absence.<br>(c) The raw cache is not pinned. The summary records no per-file sha256 or download time. So "bytes equal" after the offline re-reduction proves the reduction is deterministic, **not** that the cache is what NDBC served. | Write a `<file>.absent.json` sidecar (status, UTC time, URL) instead of a zero-byte file. Treat an empty 200 as a failure. Confirm a 404 once more after a backoff. Refuse `years` that reach the current UTC year (or route them to the monthly path). Record a per-file `{sha256, bytes, fetched_at}` in the reduction block, and let `--verify` re-hash the raw cache when it is present. Plant P1 and P2. |
| F-4 | minor | new **C-048** · C-009 (recurrence) · C-039 | **The self-test test passes for a reason it does not name.** `test_selftest_passes_with_a_calm_vital_and_catches_a_future_read` (`test_fetch_ndbc.py:264-272`) asserts only `pytest.raises(st.LeakError)`. Its plant (`df.shift(-1)`) is caught by **C4** (*"vitals NaN at (primary, t) on the clean synthetic build"*), because week t+1 is a gap in the synthetic world. At lag 1 it is caught by **C0**. It is never caught by C1 or C2, the checks the test is named for. The commit says *"Selftest catches a calm vital that reads next week"*. **The instrument does work.** Two plants that keep week t non-NaN are caught by **C1 LEAK**: `count_t + count_{t+1}`, and "next week, else own week". The lag-1 sum is caught by C8. The test simply does not show it. | Use a plant that leaves (primary, t) non-NaN, e.g. `df.add(df.shift(-1), fill_value=0)`. Assert `match="C1 LEAK"`. Add a lag-1 case that matches `C8`. |
| F-5 | minor | **C-035** (recurrence) · C-039 | **`590f70b` pins one of the test's two live inputs, and only half of that one.** `_as_the_entry_saw_it` (`test_site.py:301-318`) filters `atlantis.yaml` and `streams.yaml` to the streams v3 pinned. It copies `features.yaml` and `events.yaml` **live**, and the test still reads FKNMS's **live** `outputs/atlantis_core/metrics.json` (`:330`). I added one wind vital to a scratch FKNMS, as ii-b obligation 2 will. `load_instance` then fails with `R2 … stream_ref 'atl_stream_fkc_wind_ndbc_daily' not declared`. ii-b's first vitals commit will turn this test red, and its run (overwriting metrics.json) would do so again. The commit's claim, *"its result no longer depends on what the live instance has added since"*, is stronger than the fix. | Filter vitals (and events) by `stream_ref ∈ pinned` too. Better: target the test at the **newest** entry, with the metrics hash bound to it (record `metrics_sha256` in `evaluation_extras` at board write, and assert it). Then the test checks what the page cites today, at any v*n*, and a mismatch fails by name rather than by accident. |
| F-6 | minor | **C-023** (recurrence) | **Provenance labels say "fetch" for a re-reduction.** `provenance.summarise` (`provenance.py:36`) writes `fetched_at_source: "fetch"` whenever `_download` ran, including an offline re-reduction from the raw cache. FKNMS's summary says `fetched_at 01:50:56 · source fetch`. The downloads happened at 01:45–01:49, in a trial run under the then-uncommitted fix. They have no machine record, only a YAML comment (`streams.yaml`). My own re-reduction wrote `source: fetch` at 02:37. `pipeline_version` reads `atlantis_core 0.10.0 · NDBCStdmet` for both `b5629dc` (the pre-fix parser) and `e8b79c0`, so the machine field does not name the reduction code. | `fetched_at_source: "offline re-reduction of raw cache"` when no request was made. Record the raw files' download times (F-3c). Bump a patch version on any fix that changes the reduction (0.10.1), or stamp the core commit into `pipeline_version`. |
| F-7 | minor | **C-005** · **C-014** (recurrence) | **The docs and tests know three formats; the cache holds four.** The real forms are:<br>(i) before 1999, `YY`;<br>(ii) 1999–2004, `YYYY` (2000–04 add `TIDE`, with 16- or 17-field rows);<br>(iii) **2005–2006, `YYYY MM DD hh mm` with no `#` and no units line** (8 files);<br>(iv) from 2007, `#YY` + units.<br>The docstring (`ndbc.py:8-12`) says *"1999–2004 … some years carry `mm`"* and *"from 2005: `#YY` … units line"*. The commit and the card's probe say *"2005-on #header + units line + mm"*. The parser reads by column names, so all four parse (0 malformed). No test pins (iii), a mid-file repeated header (SANF1 2020), `:49/:50/:55` hourly stamps, stray prior-year rows, or mixed hourly + 10-minute rows in one year (SANF1 2019). **Two guards are unplanted:** the year-window filter (`:184`) and `weekly_count_lt`'s **Obs** branch. Both mutations leave the suite green, and the Obs branch has no test at all. | Correct the docstring, card and README to four forms. Add fixtures for (iii), a repeated header, `:50` stamps and a stray prior-year row. Plant the year-window filter (a 2026 row in a 2025 file must not enter). Test the Obs branch, or remove it until a point stream needs it. |
| F-8 | minor | C-030 kin · C-022 kin | **The sampling regime changes at the test boundary, and it is not on record.** From 2019, LONF1, SANF1 and SMKF1 change from hourly rows to 10-minute rows: LONF1 has ≈ 8,700 rows a year before 2019, 26,160 in 2019 and ≈ 52,000 from 2022. `test_start` is 2019, the year MLRF1 also ends (2019-03-16). My knowledge (medium confidence on the 10-minute rows) is that NDBC documents C-MAN `WSPD` as a **2-minute** average reported hourly. So a day's mean moves from 24 samples to ≈ 144: the same expectation if each row is a scalar average, but a processing change exactly at the split. Neither the reduction block nor the ii-b caution records it. | Record per station-year in the reduction block: rows/day (median) and the set of observation minutes. Add "cadence change at 2019 (hourly → 10-min), coinciding with test_start" to ii-b's drift obligation. One sensitivity: subsample to one row per hour (the `:00`/`:50` row) and compare the calm counts. |
| F-9 | minor | **C-042** (recurrence) · C-032 kin | **The budget trip was reported 65 kT past the line again, and the re-card is not on the card.** The session log is truthful: the +50% line (≈ 225 kT) was crossed during the live-fetch fixes, and the SITREP came at ≈ 290 kT. Ruling 7 re-carded main ≈ 150 → ≈ 420 kT, but **the card's `token_budget_estimated` (`mission_m3b_ii_a_ndbc_fetch.md:14`) still says main ≈ 150** at HEAD. The acceptance line *"`conform --stage fetched` all pass"* is not met as written: item 9 is outstanding, honestly reported and explained. It needs an operator ruling or a re-worded criterion, not a tick. | Write ruling 7 into the card's budget field, with the crossing point. Re-word the criterion (*"all pass except item 9, outstanding by construction until ii-b's v4"*) under the operator's ruling, or leave it unticked. For the third mission running, the trip was seen only at a clean point: add a counter check at each commit to the card template. |
| F-10 | nit | 2f denominator | **STATE's sanity-read shares use mixed denominators.**<br>(a) The calm shares *"c = 4: 22 → 26 → 28%"* (`STATE.md:34`) divide by **all calendar days**, so no-light days count as "not calm". That is the error `weekly_count_lt` itself guards against. Over reporting days the shares are **23.8 → 27.7 → 29.4%**. The rise is about the same.<br>(b) *"41% of test days have 3, 47% have 2"* mixes two denominators. Over calendar days it is 39.0% / 47.2%; over reporting days, 40.8% / 49.4%.<br>(c) *"SMKF1 6.48 → 5.42"* compares segment means, which carry climate. The paired SMKF1 − SANF1 difference is the cleaner read: −0.30…+0.12 before the gap, −0.18…−0.85 after. | Use one denominator (reporting days), and state it. Give the paired difference beside the segment means. |
| F-11 | nit | C-025 (recurrence) | **conform reimplements the board's supersession and says it reads it.** `_newest_versions` (`conform.py:153`) is a second implementation, but the comment at `:395` says *"the board's own derived supersession (board.index), read here"*. It counts entries that fail the board's gate and ignores `superseded_by`; `board.index.supersession` does neither. The two agree on FKNMS today, and no test pairs them. | Call `board.index.supersession` on the parsed docs (catching `BoardError` into item 9), or add a test that the two agree on a board with an invalid entry and a `superseded_by`. |
| F-12 | nit | C-024 (recurrence) | **Small gaps.**<br>(a) A duplicated station id in the spec yields duplicated station-days (plant: 2 duplicate `(date, station)` rows; `per_station` silently overwritten).<br>(b) A garbled minute is filled with 0 (`ndbc.py:84-85`), not dropped.<br>(c) `rows_malformed` counts repeated header lines as rows.<br>(d) `--verify`'s note says *"a unit has only 10273"* where it means a station.<br>(e) `weekly_count_lt` is a count, not a share, so a partly observed week counts fewer calm days. That is 8 test weeks here (1–6 index days); worth one line in the op's docstring.<br>(f) The UTC day runs 19:00–19:00 EST; it is recorded, which is enough. | (a) Refuse duplicate stations in `basis`. (b) Drop and count. (c) Count headers separately. (d) Use "station". (e) Docstring line, or a `weekly_frac_lt` if ii-b's scan wants one. |

## Acceptance criteria vs evidence

| Criterion | Evidence | Status |
|---|---|---|
| `NDBCStdmet` built: three formats, sentinels → NaN, daily mean with a declared minimum, 404 = absent, any other failure fails closed, years present/absent in the summary; `BUILT`; core 0.10.0 | `ndbc.py`, 17 tests; my survey; mutation sweep | ✓ It reads **four** forms (F-7). 404 = absent is fail-open on an empty 200 and on transient 404s (F-3). Conflicting duplicates are resolved silently (F-2) |
| `weekly_count_lt`: unit-level, no-data week NaN, constants as threshold | `ops.py:179`; unit test; plants | ✓ for the Daily path. The Obs path is untested (F-7) |
| Offline tests, each guard mutation-checked plant-first | `no_sockets`; 14 mutations | ✓ 12/12 claimed guards. The self-test case passes via C4, not C1 (F-4) |
| FKNMS: stream declared, posture ruled, mapping pin 0.9.0, federation pin, self-test + receipt, fetched, `--verify` ✅ ×4, conform fetched all pass, no vitals | `51c7203`; my runs on a copy | ✓, except "conform all pass": item 9 is outstanding, as stated (F-9). **The data carry an unflagged instrument fault in test (F-1)** |
| Suite count with its commit (C-035); controls ALL WORLDS AGREE | 849 @ `b5629dc` (log) · my 851 @ `590f70b` · 126 × 3 | ✓. The closing count is not yet recorded; `590f70b`'s fix will red at ii-b (F-5) |
| III via `iii/` in a fresh context; SITREP at +50% (C-042) | this file; session log | III ✓. SITREP ≈ 65 kT past the line; the re-card is not on the card (F-9) |
| SO-3 · public repo · gitleaks | diff, tree, gitleaks | ✓ |

**Not yet reviewable:** the AAR, `token_budget_actual`, the CHANGELOG at close, and the producer's uncommitted
register and ii-b card edits.

## Introspect

- **2a confidence gradient.** The code's claims are mostly modest, and they are mostly backed by tests. Confidence rises
  at the data roll-ups:
  - *"the synoptic index is defensible"*, from a correlation measured outside the test era;
  - *"drift"*, for a fault;
  - *"no longer depends on the live instance"*, when two live inputs remain;
  - *"catches a calm vital that reads next week"*, when C4 does the catching.
- **2c structural completeness.** The fetcher validates **format** (headers, sentinels, malformed rows, bases) and
  never **content**. No plausibility check runs anywhere between NDBC and the vital. On the way it asks whether a value
  parses, whether duplicates exist and whether a year is present. It never asks whether the duplicates agree, whether a
  404 is permanent, or whether a station is plausible. Each gap is a place where the fault lies in the value and the
  check reads the structure (F-1, F-2, F-3).
- **2d meta-pattern.** This mission repeats the method's own lesson from M-1 (C-005): *the synthetic world lacks the
  shapes that hurt*. This time the real data had the shapes, and the fixtures were still written from the documentation
  (F-7). The fixture for the next fetcher should be cut from the first real cache, not from the spec.
- **2f denominator.** "Agreement" was measured on the 16 years where all four lights report. The model is scored on
  the 7 years where at most three do (F-1). The calm shares count no-data days as not calm (F-10).
- **2g corrections matched.** These recur:
  - C-005 and C-014 (F-7);
  - C-009 (F-4);
  - C-023 (F-6);
  - C-024 (F-2, F-12);
  - C-025 (F-11);
  - C-030 (F-1, F-8);
  - C-035 (F-5);
  - C-039 (F-4, F-5);
  - C-042 (F-9).

  C-019 and C-021 are kin (F-3).

## ACCUMULATE

**New rows appended to the local store:**
- **C-045** (F-1): `agreement_check_window_excludes_scored_window`.
- **C-046** (F-2): `duplicate_key_resolved_by_order_without_conflict_check`.
- **C-047** (F-3): `absence_inferred_from_one_reply_and_cached_forever`.
- **C-048** (F-4): `plant_caught_by_unrelated_check`.

**Existing rows: I did not edit them**, as at M-3a and M-3b-i. Step 3b ties `frequency` and `accepted` to the
operator's accept or reject decision on this table, which has not been given. These bumps are for the producer to apply
once the operator rules:
- **C-009** 9 → 10 (F-4)
- **C-023** 6 → 7 (F-6)
- **C-035** 1 → 2 (F-5)
- **C-042** 2 → 3 (F-9)
- **C-005** 4 → 5 and **C-014** 1 → 2 (F-7)
- **C-024** 1 → 2 (F-2, F-12)
- **C-025** 1 → 2 (F-11)
- **C-030** 2 → 3 (F-1)
- **C-039** 3 → 4 (F-4, F-5)

**Graduation candidates (frequency ≥ 3), if the bumps are accepted:**
- C-042 and C-030 newly qualify.
- C-003, C-004, C-005, C-009, C-010, C-015, C-023, C-032, C-034, C-037 and C-039 remain candidates.
- Acceptance is the operator's call (ADR-003 ceremony).

## Reviewer cost

About **300 kT** on this agent's counter, against the card's ≈ 150 kT reviewer line. I record that here rather than at
close; the card itself calls 150 "the floor, not the expectation". Most of the cost was the data work, which this
mission needed and no earlier review did. Compute:
- 1 survey of 138 raw files, plus 8 data-forensics scripts (UTC, plausibility, the SMKF1 blocks, zero-runs, effect on
  the index, partial weeks, segment shares);
- 14 single-guard mutations (19 tests each);
- 5 self-test plants;
- 3 fetcher plants (an empty 200, a transient 404, a duplicate station);
- 1 site-test simulation;
- 1 offline re-reduction, 1 `fetch --verify` and 1 conform run on a scratch FKNMS;
- 1 control run;
- 1 full suite (851, 276 s);
- 2 gitleaks runs.

No network.

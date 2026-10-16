---
type: aar
mission: mission_m3b_ii_b_1_core_mask_offsets_scan
campaign: campaign_atlantis_genesis
created: 2026-10-16
updated: 2026-10-16
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261015_145556_m3b_ii_b_1_core
tags: [aar, m3b_ii_b_1, p3, qc_mask, station_offsets, scan, fknms, sanf1, iii, atlantis, tidewatch]
---

# AAR — M-3b-ii-b-1: the mask, the offsets and the val-only scan (core 0.11.0 → 0.11.1)

**Scope.** The core half of M-3b-ii-b, split at open (ruling 3):
- core **0.11.0**: stream `mask_columns`, `station_windows`, era-fitted `station_offsets` (R5/R7), the self-test's
  offset-era C6, `eval.select`, and `atlantis_core.scan` (val only);
- core **0.11.1**, the III fixes;
- the FKNMS wind index declared under the rulings below.

There are no vitals: ii-b-2 realises and tests them.

**Rulings** (operator, `AskUserQuestion`):

| # | Date | Ruling |
|---|---|---|
| 1 | 10-15 | QC mask = the low-ratio flag only. `qc_stuck` is kept, since an identical ≥ 6 h run can be true calm |
| 2 | 10-15 | Station offsets fitted on train only, against SANF1. SMKF1 cut after its 2016–17 gap. SANF1-only is the sensitivity |
| 3 | 10-15 | Split ii-b into ii-b-1 (core) and ii-b-2 (vitals · scan · v4 · SHAP · write-up) |
| 4 | 10-15 | SANF1's ≈ +0.8 m/s break: window + re-fit, no core change |
| 5 | 10-16 | (III F-2) The window is amended to 2007-08-01, the post-break record, read from the monthly diagnostic |
| 6 | 10-16 | III F-1, F-5, F-6 and F-7 fixed now in core 0.11.1 (re-card: see Budget) |
| 7 | 10-16 | (III F-5) A causal (trailing-window) flag for the mask; the centred flag stays as a description |
| 8 | 10-16 | ACCUMULATE: C-049…C-052 accepted; C-005, C-014, C-030, C-032, C-039, C-042 bumped |

## Delivered

- **Atlantis:**
  - `2e4f8dd`: core 0.11.0 (WIP; suite then unverified);
  - `8a74961`: suite **896 passed at `2e4f8dd`** (732 s), ruling 4 on the cards;
  - `8ea109f`: core **0.11.1**, the III fixes, **912 passed** (316 s); the review; ACCUMULATE.
- **FKNMS:**
  - `dda77c2`: rulings 1, 2, 4 declared (receipt `2ba2d4f939`, superseded the next day);
  - `08b08e7`: the wind stream re-reduced offline under 0.11.1 (+ `qc_low_ratio_causal`, sha256 `d837c210…`, the six
    shared columns byte-identical), then rulings 5 and 7 declared:
    - era [2007, 2012]; offsets LONF1 −1.437 · MLRF1 −0.830 · SMKF1 −0.210;
    - `selftest.week` back to 2014-01-06;
    - self-test green, receipt **`199f86613a`**; verify ✅ ×4; conform fetched 11 pass + item 9 outstanding by
      construction;
    - the calm-share table in STATE.

## Acceptance

| Criterion | Status |
|---|---|
| Each new guard has a test, red with its guard off | ✓ for 0.11.1: **P1–P9, all red** (below). For 0.11.0: "25/25" was claimed before the `/clear`, but the plants were never listed and cannot be replayed (F-12). III sampled 15: 14 red, and the 15th (the scan's test drop) is belt and braces (F-10) |
| Hashes unchanged where the new keys are absent | ✓ exemplar `7b789afded`, FKNMS-before `81bca06518` (III, under both cores) |
| Scan never reads test | ✓ synthetic poison of every stream and flag; III's real-data poison is byte-equal |
| Full suite green, with the count and its commit | ✓ 896 @ `2e4f8dd`; 912 @ `8ea109f` |
| FKNMS self-test green under the declaration | ✓ `199f86613a`. The offset-era C6 is *n/a* until ii-b-2's vitals; F-1 showed the n/a hid a blind week, now fixed |
| Calm-share table in FKNMS STATE, with offsets and n_days | ✓ re-derived under rulings 5 and 7 |
| III in a fresh context, findings dispositioned; counter at every commit; SITREP at +50% | III ✓ (0/1/8/3, all dispositioned). Counter ✗ at `2e4f8dd` (F-9); read at every commit after |

**0.11.1 plants** (script: session scratchpad `plants.py`; each guard switched off, its test run):

| Plant | Guard switched off | Test reddened |
|---|---|---|
| P1 | F-7 closed stream key set | `test_registry_refuses` (3 cases) |
| P2 | F-6 per-fold offset bound | `test_registry_refuses` (per_fold) |
| P3 | F-6 full_model keeps the looser bound | `test_offset_era_may_reach_the_first_stop_year_only_without_per_fold_selection` |
| P4 | F-5 R5 refuses look-ahead flags | `test_registry_refuses` (2 cases) |
| P5 | F-5 causal flag is trailing (`center=True` planted) | `test_causal_flag_reads_no_later_day_and_catches_the_fault` |
| P6 | F-5 C1 raises the mask flags | `test_selftest_catches_a_mask_that_reads_the_next_week` |
| P7 | F-1 calm world in every season (the 0.11.0 sine restored) | `test_selftest_calm_vitals_bite_in_every_season` (4 weeks) |
| P8 | F-1 world fault named | `test_selftest_refuses_a_world_without_calm_days_by_name` |
| P9 | F-11 same stop rows across values | `test_scan_refuses_values_scored_on_different_stop_rows` |

## Worked

- **Reading the paired differences before ruling.** The session's "SANF1 shifts +0.3 in 2014–18" turned out to be an
  era-mean straddling a 2006–07 break. A year-by-year table of every pair showed it at once: the three non-reference
  lights flat against each other, all three moving against SANF1.
- **Fixes arrived with their failing tests.** Every 0.11.1 guard was red with its guard off before the suite ran.
- **The fresh-context reviewer earned its cost.** F-1 was a defect my n/a would have shipped to ii-b-2's first vitals
  commit. F-2 corrected the premise of a ruling I had put to the operator.
- **The re-reduction was offline and byte-checked.** The old columns were identical, and the causal/centred difference
  is exactly the 6 days III predicted.

## Didn't

- **My diagnostic was yearly.** Ruling 4 was put to the operator on yearly paired differences, which cannot see a break
  inside 2006. The first window kept 5 pre-break months. Ruling 5 corrected it a day later.
- **"The rise was composition" outran the table** (F-3, C-030's fourth recurrence). I wrote a second over-reach
  ("SANF1-only flat at c ≥ 4") into the rewrite and caught it myself before the commit.
- **The counter was not read at the WIP commit** (F-9, C-042's fourth recurrence). The +50% line was probably crossed
  before the `/clear`, unseen.
- **The 0.11.0 plants were never listed** (F-12).
- **I moved `selftest.week` to satisfy a rule** without asking what the move did to the instrument's sensitivity
  (F-1). The rule was right; the side effect went unchecked.

## Finding

- **The reference station's level moves at its outages.** The 2006–07 break is the large one. The val residual of
  ≈ +0.3 m/s under any constant offset shows the moves continue. A Keys-wide index referenced to one light inherits that
  light's history. This is limit (d) for ii-b-2 and a reason the SANF1-only sensitivity is not a clean control.
- **The rulings remove most of the calm-share rise, not all.** At c = 4, train → test is +5.6 points unmasked and
  +2.4 ruled.
- **A flag computed for description is not a flag for masking.** Both of NDBCStdmet's 0.10.1 flags read after their
  day: the centred ratio reads up to 7 days ahead, and a stuck run crossing midnight reads the next day's hours. Only a
  trailing flag may mask (C-049).

## Change

- **A break diagnostic is monthly and deseasonalised, never yearly**, and is shown to the operator before a window is
  ruled.
- **Any parameter move that touches the self-test is checked against the instrument's sensitivity** (C-051). C0w now
  makes a calm-less week a named world fault.
- **A stream spec is a closed key set** (C-050); a misspelt key no longer loads green.
- **A ruling made on the full record is disclosed as such** (C-052, limit (f)).

## Follow-up

- **ii-b-2 (opus):**
  - run the self-test with the vitals **before** the scan, and never move the week to make C0 pass;
  - scan c on val;
  - v4 is written under ii-b-2's own config hash;
  - disclose limits (a)–(g).
- **At the P3 gate:**
  - graduation of C-014 · C-030 · C-042 (with the earlier candidates);
  - C-042's fourth recurrence → a counter read in the commit-message template;
  - the card-template counter check (III M-3b-ii-a F-9).
- **The push** (operator act): nothing since `76bb143` is pushed. gitleaks: `76bb143..HEAD` clean.

## Budget

- **Main:** carded ≈ 200 kT (line ≈ 300). The pre-`/clear` total is **unknown, not estimated**: ≈ 145 kT was read at
  `d52e140`, and nothing at `2e4f8dd`, so the line was probably crossed unseen.
- **Post-`/clear` sitting:** ≈ 140 kT at `8a74961` · ≈ 260 kT at `8ea109f` · ≈ 300 kT at close.
- **Ruling 6** re-carded the fixes in-mission. On a 200 kT card the actual is ≥ 445 kT (≥ 145 + ≈ 300).
- **III reviewer:** ≈ 290 kT (carded 250).

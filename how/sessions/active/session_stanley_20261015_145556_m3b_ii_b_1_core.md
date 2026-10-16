---
type: session
created: 2026-10-15
updated: 2026-10-15
last_edited_by: agent_proteus
tags: [session, m3b, m3b_ii_b, m3b_ii_b_1, p3, qc_mask, station_offsets, scan, fknms, atlantis, tidewatch]
session_id: session_stanley_20261015_145556_m3b_ii_b_1_core
user: stanley
started: 2026-10-15T21:55:56Z
completed: ""
status: active
executor_tier: opus
mission: m3b_ii_b_1
campaign: campaign_atlantis_genesis
intent: "M-3b-ii-b split at open → ii-b-1: core 0.11.0 — stream mask_columns · station_offsets (era-fitted, R7) · station_windows · atlantis_core.scan (val only) · FKNMS declaration + self-test + descriptive calm table · III. Plan: ~/.claude/plans/please-read-the-claude-md-refactored-petal.md"
---

## Activity Log

- open — leases probed: Atlantis and FKNMS `how/sessions/active/` empty. Atlantis HEAD `ea83c88`, FKNMS `6dfd713`, both clean.
  Code read: `normalise` drops flag columns; `_to_units` is a raw station mean; `run` → `_fit_main` always scores test.
  Rulings (AskUserQuestion, 2026-10-15, at open; obligation 6): **(1) QC mask = `qc_low_ratio` only** (`qc_stuck` kept: an
  identical ≥ 6 h run can be true calm; 73 station-days a recorded limit) · **(2) station offsets fitted on train only vs
  SANF1, SMKF1 cut after its 2016–17 gap** (no train overlap to fit a post-gap offset); SANF1-only the sensitivity ·
  **(3) split ii-b** → ii-b-1 (core: mask · offsets · val-only scan) + ii-b-2 (vitals · scan · v4 · SHAP · write-up).
- `d52e140` the split (cards · roster · charter · STATE); FKNMS lease `a8f3069`.
- **Core 0.11.0 built (WIP commit below; suite NOT yet green-verified):**
  - `mask_columns` (normalise carries the flags; `Evaluator._prepared` → NaN);
  - `station_windows`;
  - `station_offsets` (`fit_offsets`, era-fitted, min_days refusal);
  - R5/R7 checks; NDBC `FLAG_COLUMNS`;
  - self-test: `_span` reaches the offset eras; a week too close to an era is refused; C6 reports the offset era by
    perturbing the non-reference stations; synthetic values centred on `weekly_count_lt` thresholds (**finding:** C0 could
    never bite on a calm vital before this, because the values sat near 1000);
  - `eval.select` factored out of `_fit_main`; `atlantis_core.scan` (val only); run provenance carries the offsets;
    README updated.
  - New tests: `test_vitals_mask_offsets.py` (28) and `test_scan.py` (5), all green. **Plant-first 25/25 red** (3 blind at
    first, tightened: era-only fit, real C6 dependence, `_span`). Exemplar and FKNMS hashes unchanged (7b789afded /
    81bca06518).
  - **Full suite: interrupted at 48% by `timeout 1500`** (CPU shared with a Terminal.aDNA suite); no failure seen before the
    cut. **Re-run first next sitting.**
- **Findings for the AAR/III:**
  1. The val→test edge is by ISO week. The last val week holds 1–5 Jan of the first test year, and a val row's label can
     read them (pre-existing in `run`; the scan inherits it, documented).
  2. **Descriptive calm share (FKNMS, scratch, not yet in FKNMS STATE)**, % of reporting days, c = 3 / 4 / 5,
     train / val / test:

     | index | c = 3 | c = 4 | c = 5 |
     |---|---|---|---|
     | unmasked | 10.9 / 12.9 / 14.8 | 23.8 / 27.7 / 29.4 | 38.1 / 40.8 / 44.0 |
     | ruled (mask + SMKF1 cut at 2015-08-09 + offsets vs SANF1, 1987–2013) | 9.4 / 9.8 / 8.5 | 22.0 / 22.6 / 20.9 | 36.2 / 36.9 / 36.3 |
     | SANF1-only | 12.5 / 10.6 / 10.8 | 24.0 / 22.1 / 21.8 | 37.4 / 33.4 / 34.6 |

     **The calm-share rise was composition; under the ruled index it is flat.** Offsets: LONF1 −0.815 (6,161 d) · MLRF1
     −0.159 (7,072) · SMKF1 +0.326 (6,957). Residuals against SANF1 after the offsets are ≈ −0.3 m/s for every light in
     val, and ≈ 0 in train and test: **the reference SANF1 appears to shift +0.3 in 2014–18**, where c is chosen. This is
     to be ruled. The cut costs 123 test days on which only SMKF1 reported. Script:
     `scratchpad/calm_table.py` (session-local; re-derive).
- **Resumed after `/clear`** (same sitting, opus, 2026-10-15 ≈ 23:40Z; plan
  `~/.claude/plans/please-read-the-claude-md-partitioned-naur.md`). **C-042 miss:** the token counter was not read at
  `2e4f8dd`; the pre-`/clear` total is unknown and is reported as unknown, not estimated.
- **Finding 2 corrected (read-only diagnostic, year-by-year paired differences, mask + SMKF1 cut):** the reference does
  **not** shift "+0.3 in 2014–18". **SANF1 steps ≈ +0.8 m/s at its return from the Jan–Apr 2006 outage** (the winter
  after Wilma). All three other lights drop against it at once (MLRF1−SANF1 ≈ 0 → −0.87; LONF1−SANF1 −0.6 → −1.5;
  SMKF1−SANF1 +0.6 → −0.2), while their mutual differences stay flat (LONF1−MLRF1 ≈ −0.6, SMKF1−MLRF1 ≈ +0.5 throughout).
  The 1987–2013 era-mean straddles the break, and that is the val residual. The step is seasonal (larger in winter), so an
  additive offset is approximate. A second shift sits in test: LONF1−SANF1 ≈ −1.4 in 2008–17, ≈ −0.9 in 2021–25.
  Only two lights report there, so it cannot be attributed.
- **Ruling 4 (operator, AskUserQuestion, 2026-10-15): window + re-fit, no core change.** SANF1 `station_windows
  ['2006-05-01', null]`; offset era **[2006, 2013]** against post-break SANF1 (R7 holds: ends before val 2014 and the first
  rolling-origin test year 2014). The SANF1-only sensitivity is windowed the same way. Works because `_prepared` applies
  windows → mask → offsets.
- **Full suite at `2e4f8dd`: 896 passed** (732 s, no timeout; 8 RuntimeWarnings, all from `test_scan_never_reads_test_years`'
  poisoned vitals). C-035: recorded with its commit.
- **Calm table under ruling 4** (scratch `calm_table.py`, which reads the declared FKNMS spec): the 2006 step is absorbed
  in train (residual 0 by construction), but **SANF1's level moves at each outage**. Val residuals are **+0.2** for all
  three lights (−0.3 before), and LONF1 is +0.48 in test. Recorded as limit (d) on the ii-b-2 card; the scale shift is
  limit (e). Offsets: LONF1 −1.338 (1,913 d) · MLRF1 −0.735 (2,065) · SMKF1 −0.122 (2,064).
- Token counter (this sitting, post-`/clear`, incl. harness context) ≈ 140 kT at the cards commit.
- FKNMS `dda77c2`: declaration (rulings 1, 2, 4), pin → `8a74961`, receipt `2ba2d4f939`, verify ×4, conform 11 + item 9;
  STATE calm table. gitleaks: FKNMS clean; Atlantis `76bb143..HEAD` clean (the 9 working-tree hits are pre-existing test
  fixtures, the gitleaks toml, two exemplar pages and one older session log line).
- **III (fresh context, via `iii/`): PASS-WITH-FINDINGS 0/1/8/3** → `missions/aar/iii_review_m3b_ii_b_1.md`; reviewer
  ≈ 290 kT. F-1 (major): the March self-test week blinds C0 to calm vitals. F-2: SANF1's step completes only after its
  Apr–May 2007 outage, and May–Sep 2006 is pre-break (my yearly diagnostic could not see it).
- **Rulings 5–8 (operator, AskUserQuestion, 2026-10-16):**
  - **5** (F-2): SANF1's window is amended to **2007-08-01**, the post-break record, picked from the monthly break
    diagnostic (not the val residual). The SANF1-only sensitivity follows it.
  - **6** (F-1, F-5, F-6, F-7): **all four fixed now, core 0.11.1**, plant-first; re-card.
  - **7** (F-5): **a causal flag for the mask.** NDBCStdmet also writes a trailing-window flag. FKNMS masks on it after
    an offline re-reduction, and the centred flag stays as a description. The self-test perturbs declared flag columns
    after t.
  - **8:** ACCUMULATE accepted: C-049…C-052, plus the recurrences C-005, C-014, C-030, C-032, C-039 and C-042. C-014
    becomes a graduation candidate.
- Token counter ≈ 180 kT this sitting at the rulings.
- **Left:**
  1. ~~a full suite re-run~~ done (with no timeout) → record the count with its commit;
  2. ~~(superseded by ruling 4, then 5)~~ Step 5 in FKNMS: declare `mask_columns: [qc_low_ratio]`, `station_offsets {SANF1, [1987, 2013]}`,
     `station_windows {SMKF1: [null, 2015-08-09]}`; move `selftest.week` 2014-01-06 → 2014-03-03 (the era-clearance
     rule); bump the pin; self-test → new receipt; `fetch --verify` and conform; put the table above in FKNMS STATE;
  3. III (fresh context); AAR; CHANGELOG v0.19.0; STATE NSP; close the leases.

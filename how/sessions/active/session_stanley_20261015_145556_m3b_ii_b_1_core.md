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
- **Left:**
  1. a full suite re-run (with no timeout) → record the count with its commit;
  2. Step 5 in FKNMS: declare `mask_columns: [qc_low_ratio]`, `station_offsets {SANF1, [1987, 2013]}`,
     `station_windows {SMKF1: [null, 2015-08-09]}`; move `selftest.week` 2014-01-06 → 2014-03-03 (the era-clearance
     rule); bump the pin; self-test → new receipt; `fetch --verify` and conform; put the table above in FKNMS STATE;
  3. III (fresh context); AAR; CHANGELOG v0.19.0; STATE NSP; close the leases.

---
type: iii_review
review_of: mission_m2c_i_climatology_budget_and_interval
commits: [19c442d, 0da7414, 6fa20d3]   # diff vs 76bb143
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-08
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 4, minor: 3, nit: 3}
tags: [iii_review, m2c_i, climatology, interval, board, atlantis, tidewatch]
---

# III review: M-2c-i (climatology at budget · season-block paired interval · atl_v0 0.8.0 · core 0.7.0 · board v4)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` at `v0.6.0`):
- packs: inspect procedures, introspect checks, learning store, vault maintenance;
- the Atlantis local store: 34 corrections, C-001…C-034.

Modalities: text, code and data.

**Reviewer ≠ producer.** I did not write any of this work. The only file I wrote in the vault is this one. I used a
scratch copy of the core for my plants. One side effect: the re-run's `data/processed/rerun_v4/` was created inside the
exemplar (it is gitignored), and I removed it.

## Verdict: PASS-WITH-FINDINGS (0 blocker · 4 major · 3 minor · 3 nit)

The commensurability work is sound:
- Climatology's thresholds are fixed on the same validation rows the model's are fixed on.
- The fit that sets them reads no validation or test label.
- The refit, the AUROC/AUPRC and v4's equality with v3 all reproduce exactly.

The findings fall into three groups:
- **The interval says more than it can deliver.** Its nominal 95% is not delivered at 4 blocks (F-2), and it is drawn
  off the operating point that T11's falsifier names (F-3).
- **Two guards check a neighbouring variable rather than the input actually consumed**, so two plants of mine pass
  green (F-4).
- **`main` is red at HEAD** (F-1).

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| atl_v0 0.8.0 controls | `LINKML_BIN=<scratch linkml_venv>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` | 74 pass in each of the 3 worlds. Rule 4: 10 range classes. Committed JSON byte-identical to a fresh generation. **ALL WORLDS AGREE.** The README counts are right: 9 pos · 65 neg, 11 enums, 23 `$defs`. |
| Full suite at HEAD `6fa20d3` | `.venv/bin/python -m pytest -q` | **730 passed, 1 FAILED**: `test_board_index.py::test_f9_supersession_is_derived` → F-1 |
| v4 reproduces | `atlantis_core.run --instance ../exemplars/gulf_karenia_brevis --out <scratch>` (7.9 min) | Leaf walk against the committed `atlantis_core_v4/`: only `run_at` differs in `metrics.json` and `learner_swap_logistic.json`. `shap_summary`/`whatif` are identical, and the `model.json` md5 is equal. |
| v4 ≡ v3 | leaf walk `atlantis_core_v3/` → `atlantis_core_v4/` | Only `atlantis_core` and `run_at` changed. Everything else is additions (15 new leaves per file). `model`/`shap`/`whatif` bytes are identical. **Claim holds.** |
| Interval reproduces | `season_block_interval` recomputed from `data/processed/atlantis_core_v4/test_scored.parquet` + `climatology_scores(base_fit, test)` | Equal to the bit: Δ AUROC +0.318 [0.1126, 0.4833] and Δ AUPRC +0.437 [0.3224, 0.6960] |
| Pinned climatology AUROC/AUPRC | covered by the test and the re-run | Unchanged (0.5770 / 0.1045) |
| Entry = projection | `emit(...)` re-run on committed outputs against the committed entry | The `evaluation` blocks are equal, apart from `shap_summary_ref`, which the CLI sets. `--index --check` reports ✅ up to date. |
| Same validation rows for both quantiles | code read: `_variant` uses `L.predict(vm, val)`; `climatology_at_budget` uses `climatology_scores(sel, val)` | Both are quantiled on **all** val rows. The selection fits are train-only and embargoed. Thresholds read no labels, and no validation or test label reaches climatology's thresholds. ✓ |
| Producer plants | C1, C2, C2b, C3, C4, guard-off, 16 result plants, 4 slot tampers | All pass on clean source. Each is caught by name. |
| Reviewer plant K (a 50% interval labelled 95%) | scratch copy, `tests/test_m2c.py` | **Caught** by `test_no_signal_spans_zero`. |
| Reviewer plants A and B | scratch copy, `tests/test_m2c.py` | **Not caught** → F-4 |

Per-season deltas on the exemplar, from my recomputation (model / climatology):

| Test year | n | positives | AUROC model / clim | AUPRC model / clim |
|---|---|---|---|---|
| 2020 | 449 | 11 | 0.909 / 0.768 | 0.334 / 0.062 |
| 2021 | 352 | 67 | 0.801 / 0.472 | 0.534 / 0.260 |
| 2022 | 438 | 31 | 0.956 / 0.840 | 0.696 / 0.190 |
| 2023 | 401 | 18 | 0.992 / 0.389 | 0.846 / 0.037 |

What the lower bounds are made of:
- The AUROC lower bound (0.1126) is exactly the draw {2020, 2022, 2022, 2022}.
- The AUPRC lower bound sits among the all-2020, all-2021 and 2020+2021 mixes.
- (3/4)⁴ = 31.6% of draws contain no 2021.

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | new **C-035** | **`main` is red at HEAD.** `test_board_index.py:205` hard-codes v3 as the stem's top version. Landing the v4 entry in `6fa20d3` made v0/v1/v2 read "superseded → v4", so the assertion fails: 730/731. The "731 passed" in the session log and the card was measured at `0da7414`, before the board commit. The test also reads the live `what/board/entries/`, so every new entry of that stem breaks it. | Derive the expected top from the entries, or freeze a fixture copy of the entries. Re-run the suite **at the commit that closes the mission** and record that commit next to the count. |
| F-2 | **major** | new **C-036** | **The nominal 95% is not delivered at 4 blocks.** I simulated a percentile bootstrap over the exact multiset distribution, with iid normal season deltas and 4,000 replicates. Coverage of the true value: **≈ 0.80 at B = 4** and **≈ 0.87 at B = 7** (FKNMS). That is before the cross-block dependence in F-5. On the exemplar, "Spans 0: no" just means all 4 seasons favour the model, which an exact sign test puts at p = 1/16 = 0.0625 one-sided. Even so, `BOARD.md` prints `0.95: [+0.1126, +0.4833] … Spans 0: no`. `what/board/README.md` explains only the *spanning* reading, and nothing tells a reader that "no" is weaker than 95%. This is the budget's nominal-vs-realised problem again, now on the interval. M-2c-ii will apply the same instrument to FKNMS (0.937 vs 0.919), where the T11 ruling turns on the spans-0 cell. | Print the level as **nominal**, and state the approximate realised coverage per B in BOARD and the README. Carry the per-season deltas, "k of B seasons favour the model" and the exact sign-test p (a summary, so green-safe). Consider a t-interval on per-season deltas with B − 1 df beside the percentile one. Rule that "spans 0: no" at B < ~10 is not read as "distinguished at 95%". |
| F-3 | **major** | **C-034** (recurrence) | **Uncertainty is still off the falsifier's operating point.** T11's falsifier (register row T11) is "does not beat its climatology **at the chosen budget**". M-2c-i gives a *point* precision at budget and an *interval* only on threshold-free AUROC/AUPRC. The card's acceptance asked for exactly that, so the card is met, but the gap G-3 named is half closed. The budgets are also compared at unequal realised rates: at 5%, the model flags 0.041 against climatology's 0.065, a 1.6× difference in alert volume. Precision falls with volume, so the comparison is not commensurable. It is harmless here (0.66 vs 0.13), but on FKNMS the model realises 0.20 at a 0.10 budget. Risk: the AAR or the M-2c-ii register reads T11 as "tested at its terms" off the AUROC/AUPRC interval. | In the same paired draw, with thresholds held fixed, add the per-draw Δ precision (and Δ recall) at each nominal budget. Add a matched-volume reading: climatology's precision at the model's realised `n_alerts`, or recall at equal alerts. Until both exist, the AAR and register must say "T11 at budget: point estimate only; interval threshold-free". |
| F-4 | **major** | new **C-037** (kin to C-018, C-023) | **Two guards verify a neighbouring variable, not the input that is consumed. Two plants pass green.** **(A)** `interval.py`: `assert_whole_blocks(idx, …)` checks `idx`, but scoring reads `idx_model`/`idx_comp`. Plant A adds `idx = rng.choice(idx, size=len(idx), replace=True)` after the check, which resamples rows inside the drawn seasons. Result: `test_m2c.py` 35/35 passing (two failures are artefacts of the scratch copy, and the unplanted copy shows the same two). The exemplar's bounds move to AUROC [0.116, 0.503] and AUPRC [0.289, 0.706] without any signal. **(B)** `eval/__init__.py`: `check_label_windows("climatology selection→val", sel, …)` reads the variable `sel`, not the frame `climatology_scores` received. Plant B passes `train` (unembargoed) and stays green apart from the line collision with C2b. The fit-years check cannot see it either, because the years stay ≤ 2016. The schema's "nearest miss" text and the atl_v0 README cite `assert_whole_blocks` "on every draw" as the proof. | (A) Verify the indices that are scored: call `assert_whole_blocks` on `idx_model` **and** `idx_comp`, immediately before the metrics. Better, score through one helper that takes `chosen` and builds and verifies its own indices. (B) Have `climatology_scores` return, or check, the frame it actually fitted (as `FitRecorder` does for the learner), and run `check_label_windows` on that frame. Add plants A and B to `INTERVAL_PLANTS`/`EVAL_PLANTS`. |
| F-5 | minor | **C-026** (recurrence) | **A "season" block is a calendar year, and for *K. brevis* that cuts blooms in two.** Test positives fall in every month. The Nov–Feb positives straddle the year boundary: 2020-11/12 (11) runs into 2021-01/02 (8), and 2022-11/12 (17) into 2023-01/02 (9). So two of the four test blooms are split across blocks, and the independence that justifies block resampling is weaker than "season" says. The interval is then narrower still (F-2). The enum `season_year`, the module docstring ("the unit … is the season (a test year)") and BOARD ("Whole test seasons") all state a season that `week.dt.year` does not implement. | Rename the unit to `calendar_year`, or add a `season_start_month` and disclose partial blocks at the split edges. Until then, say in the v4 notes and the known limits that blocks are calendar years and which blooms they cut. |
| F-6 | minor | — (one-off; SO-9) | **The new quantities have no limits on file.** v4's `limitations_ref` (core README "Known limits of eval and explain") says nothing on climatology-at-budget ties, the unequal realised rates, the interval's nominal level, or the calendar-year blocks. Only the entry's notes and docstrings carry part of this. | Add the four items to the known limits that `limitations_ref` points to. |
| F-7 | minor | **C-003** (recurrence) | **A claim proven by analogy.** The atl_v0 README proof row says "its deltas in [−1, 1]". Only `neg_interval_lower_lt_minus1` proves it, and only the minimum of `delta_lower`. The maxima, and the bounds on `delta_upper` and `delta_estimate`, have no control. | Add `neg_interval_upper_gt_1` and `neg_interval_estimate_lt_minus1`, or narrow the README to "delta_lower ≥ −1". |
| F-8 | nit | C-009 · C-010 (both recurrences) | **(a)** The pairing guard (`idx_model, idx_comp = idx, idx` then `array_equal`) cannot fail except under the plant that rewrites that same line. The identical-scores control is the real proof, which the producer showed with the guard-off test. The schema text cites "the pairing guard" as proof; cite the identity control. **(b)** Board gaps: `assert_interval` emits an interval with `n_draws: 3`. It does not check `n_distinct_multisets` against C(2B−1, B), or that `estimate` lies within the bounds. `delta()` omits `paired_intervals`, so a v5 change to the interval would not show in `delta_vs`. **(c)** `interval_seed`/`interval_draws` sit outside `semantic_hash` (disclosed in the core README). The keyed record carries numbers its key does not describe. | (a) Reword the citation. (b) Add the floor (e.g. `n_draws ≥ 200`), the multiset check and an interval `delta`. (c) Add both to the hash, or stamp them as a separate key component. |
| F-9 | nit | (C-032-adjacent) | `BOARD.md` heading "Climatology at the **same** budgets": they are the same *nominal* budgets, while the realised rates differ by up to 1.6×. The italic note is correct; the heading says more than it does. | Retitle it "at the same nominal budgets". |
| F-10 | nit | — | `outputs/atlantis_core_v4/` held an unboarded core-0.6.0 run (M-2b, `9ac40cf`). It was overwritten in place by the 0.7.0 run. Git keeps the old bytes, but "v4 outputs" now names two different runs across commits. | Note the reuse in the v4 notes or in CHANGELOG. |

## Acceptance criteria vs evidence

**Met, and confirmed by me:**
- **Climatology at budget**: read-back, fit-years and label-window checks. AUROC/AUPRC are equal to the bit.
- **Season-block paired interval**: seeded, summaries only, verifier per draw. The caveat is F-4(A).
- **atl_v0 0.8.0**: 1 positive + 8 negatives, ALL WORLDS AGREE. README, fit matrix and template pin moved together.
- **Emitter refusals**: all named ones are present and tested.
- **Plants C1–C4 and the result plants**: each caught by name.
- **BOARD.md**: the G-7 lead cell, the new section, and `--check`.
- **Exemplar v4**: leaf walk, emitted `--vs` v3 with "no field changed".

**Not met as stated:**
- **"Full suite 731 passed" does not hold at HEAD** (F-1).

**Not yet reviewable:**
- The AAR, the single counting rule, and the SITREP or budget actual. None of these exist yet.

**Ruling 3 (calendar + signal deferred)** is recorded on the card. It still needs naming in the AAR.

## Introspect

- **2a confidence gradient.** The prose is careful ("crude", "not a population of seasons"). The *machine-readable* slots
  are not: `confidence_level: 0.95` and `spans_zero: false` carry the confidence, and BOARD renders them bare (F-2).
- **2f denominator.** Every number in the notes checks out:
  - "most of the test positives" for 2021 is 67/127 = 53%;
  - 35 multisets;
  - v3 ≡ v4.

  The denominator problem sits in the comparison at budget, where the alert volumes are unequal (F-3).
- **2d meta-pattern.** Most of the mission's guards are real, and several are proven able to fail. The weak spots are
  the same shape every time: the check sits next to the operation rather than on its input (F-4). The other recurring
  weak spot is that green was recorded one commit early (F-1).
- **2g corrections matched.** C-003, C-009, C-010, C-026 and C-034 recur. C-034 matters most, because it is the
  pattern this mission exists to close.

## ACCUMULATE proposals (the producer applies them; I did not write the store)

**Bumps:**
- **C-034** 1 → 2 (F-3)
- **C-003** 1 → 2 (F-7)
- **C-026** 1 → 2 (F-5)
- **C-009** 7 → 8 (F-8a; partial, the producer mitigated it)
- **C-010** 3 → 4 (F-8c; disclosed)

**Graduation candidates:** C-009 and C-010 remain candidates (frequency ≥ 3).

**New rows:**

```json
{"id": "C-035", "trap": "completeness", "pattern": "green_suite_predates_closing_commit", "description": "A suite is reported green at one commit, and a later commit in the same mission (a data or board entry the tests read live) turns it red. The recorded count names no commit, so the claim outlives the state it described.", "example": "M-2c-i: 731 passed at 0da7414; 6fa20d3 landed board v4, and test_board_index::test_f9_supersession_is_derived (which hard-codes v3 as the stem's top) fails, 730/731 at HEAD.", "source_review": "m2c_i_climatology_budget_and_interval_iii_review_20261008", "source_finding": "F-1", "frequency": 1}
{"id": "C-036", "trap": "confidence", "pattern": "nominal_interval_level_at_few_resample_units", "description": "A bootstrap interval is printed with its nominal level (0.95) when there are too few resampling units for that level to be delivered. A percentile bootstrap over B blocks under-covers badly at small B, so 'does not span 0' is read as significance the sample cannot give. This is the interval counterpart of a nominal alert budget printed without its realised rate.", "example": "M-2c-i: 4 season blocks (35 multisets); simulated coverage ≈ 0.80 at B = 4 and ≈ 0.87 at B = 7. 'Spans 0: no' ≡ all 4 seasons favour the model (sign test p = 1/16), yet BOARD prints '0.95: [+0.11, +0.48] … no'.", "source_review": "m2c_i_climatology_budget_and_interval_iii_review_20261008", "source_finding": "F-2", "frequency": 1}
{"id": "C-037", "trap": "boundary", "pattern": "guard_checks_sibling_not_consumed_input", "description": "A guard verifies a variable computed beside the operation's input, not the very object the operation consumes. A defect introduced between the check and the use, or at the call site, passes the guard and every planted-defect test written against the checked line. Kin to C-018 (proxy, not identity) and C-023 (label, not the act).", "example": "M-2c-i: assert_whole_blocks(idx) while scoring reads idx_model/idx_comp (a row resample after the check passes); check_label_windows(sel) while climatology_scores(train, val) is what ran (an unembargoed fit passes).", "source_review": "m2c_i_climatology_budget_and_interval_iii_review_20261008", "source_finding": "F-4", "frequency": 1}
```

## Reviewer cost

About 120–140 kT of reviewer context. Compute: one full-suite run (5.2 min), one exemplar re-run (7.9 min), one
controls run, and three planted-copy suite runs.

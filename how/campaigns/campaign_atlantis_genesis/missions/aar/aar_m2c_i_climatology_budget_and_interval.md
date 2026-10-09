---
type: aar
mission: mission_m2c_i_climatology_budget_and_interval
campaign: campaign_atlantis_genesis
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261008_234650_m2c_i_commensurable_core
tags: [aar, m2c_i, climatology, interval, board, exemplar, iii, atlantis, tidewatch]
---

# AAR — M-2c-i: climatology at budget, a season-block interval, exemplar board v4

**Scope.** This is the first half of P2-gate condition (a), split from M-2c by operator ruling 1. It covers core 0.7.0, atl_v0
0.8.0 (78 controls), `BOARD.md`'s lead column, and exemplar board v4. FKNMS v3, T2's swap and the register re-read are
M-2c-ii.

**Rulings** (all by `AskUserQuestion`, 2026-10-08):

| # | Ruling |
|---|---|
| 1 | Split along the card's line |
| 2 | The FKNMS mapping-pin move is federation upkeep, not a patch |
| 3 | Defer the calendar + signal comparator |
| 4 | III F-3: add budget deltas and a matched-volume reading to the interval |
| 5 | III F-5: seasons start at a declared month (the exemplar uses August) |

## Worked

- **Plant-first again.**
  - Every new guard has a defect planted into the real source, caught by name: C1 (climatology thresholds from test,
    caught by the invariance test, P4's shape), C2, C2b, B, C3, A, C4, 23 result plants and 4 slot tampers.
  - The reviewer's plants A and B now fail by name.
- **The pinned numbers held.** Splitting `climatology_scores` from `climatology_baseline` left climatology AUROC/AUPRC
  equal to the bit, so the hab-port and v2-reproduction tests never moved.
- **v4 ≡ v3, read by a leaf-walk script, not by eye.**
  - All 3,789 metrics leaves and 3,998 swap leaves are equal.
  - Only `atlantis_core`, `run_at` and `config_bytes_md5/atlantis.yaml` differ. The last is because the exemplar gained an
    eval-only key.
  - The model, SHAP and what-if bytes are identical, and `delta_vs` shows no field changed.
- **G-7 closed.** FKNMS v2's lead cell now reads "@ 0.1 nominal · 0.2034 realised", where it said "@ 0.1".
- **The fresh-context review earned its cost.**
  - It was PASS-WITH-FINDINGS, 0 blocker · 4 major · 3 minor · 3 nit.
  - It found a red `main` (F-1), an overclaimed interval level (F-2), half of G-3 still open (F-3), and two guards on
    neighbouring variables (F-4).

## Didn't

- **Shipped a red `main` (F-1, C-035).** "731 passed" was measured at `0da7414`. Landing the v4 entry (`6fa20d3`) broke a
  test that hard-coded v3 as the stem's top.
  - The fix derives the top entry from the entries on disk.
  - From now on, the suite count is recorded **with the commit it ran on**, after the last commit of the sitting.
- **Printed a nominal 95% as if delivered (F-2, C-036).** At 4–5 blocks a percentile interval under-covers. The reviewer
  simulated ≈ 0.80 at B = 4. The board now labels the level nominal and carries the per-season deltas and an exact sign test.
- **Built uncertainty off the falsifier's operating point (F-3, C-034 ×2).** It covered threshold-free AUROC/AUPRC while
  T11 names the budget. Ruling 4 added Δ precision and Δ recall at the fixed thresholds, plus a matched-volume Δ precision,
  in the same paired draws.
- **Two guards read a sibling variable (F-4, C-037).** `assert_whole_blocks(idx)` checked `idx` while scoring read other
  variables, and `check_label_windows(sel)` checked `sel`, not the frame fitted. Now:
  - `_take` checks the very indices it slices;
  - `fit_scored` checks the frame it fits;
  - the fit's row count is read off the fit (C-023).
- **Called a calendar year a "season" (F-5).** Two of the four K. brevis test blooms straddle New Year.

## Finding

- **T11 at its terms, on the exemplar (board v4):**
  - The model beats climatology at every budget, and by a margin the crude interval does not reach.
  - At 10%, the model's precision is 0.5267 at a realised rate of 0.0799. Climatology's is 0.1185 at 0.0823.
  - Δ precision is +0.4082, interval [+0.1109, +0.5998]. The matched-volume Δ is +0.4068, interval [+0.0962, +0.5934].
  - Δ AUROC is +0.318, interval [+0.040, +0.541]. Δ AUPRC is +0.437, interval [+0.249, +0.573]. Both levels are nominal.
  - There are 5 seasons. The two partial edge seasons hold one class each, so 3 seasons are scored individually. All 3
    favour the model, which gives a one-sided sign test p of 0.125.
  - **Read:** comfortably beaten in every season that can be scored. There are too few seasons for any interval to carry
    its nominal level.
- **Matched volume barely moves the exemplar** (+0.4082 against +0.4068 at 10%), because the two realised rates are close.
  It exists for FKNMS, where the model realises 0.2034 at a 0.10 budget, and M-2c-ii will be its first real test.
- **A seasonal block can be empty of events.** The August start gives partial edge seasons with no positives. They are
  legitimate blocks in a draw but cannot be scored alone. 23 of 2,000 draws were all-negative and were dropped (counted).
- **The board's honesty problems recur at every new number.** First a nominal budget without its realised rate (F-8,
  G-7); now a nominal interval level without its coverage (C-036). The pattern: **every number that has a nominal and a
  delivered value needs both on the page.**

## Change

### Atlantis changes, counted under one rule

**The rule (for M-2c-ii and P4 to reuse):**
- Count **one per distinct behavioural change an instance meets**, at the surface where it first meets it.
- Lockstep consequences are not counted again (the template pin moves with the schema version).
- Docs, tests and READMEs are not counted.

| # | Change | Surface |
|---|---|---|
| 1 | `climatology_baseline_test` gains `alert_rates`, `threshold_from`, the selection and refit fit years and rows (`climatology_at_budget`) | eval result |
| 2 | `paired_interval_model_vs_climatology`: season blocks, budget deltas, matched volume, per-season deltas and sign test. Three optional eval keys: `interval_season_start_month`, `interval_seed`, `interval_draws` | eval result + config |
| 3 | atl_v0 0.8.0: `climatology_alert_budgets`, `paired_intervals`/`AtlPairedInterval` (with `season_start_month`), three enums. Lockstep: the template mapping pin, and every instance's mapping pin (FKNMS: federation upkeep, ruling 2) | schema |
| 4 | The emitter refuses results from core < 0.7.0 (`assert_climatology_at_budget`, `assert_interval`) and adds the `paired_interval` extras | board emitter |
| 5 | `BOARD.md`: the lead cell shows nominal · realised, plus the climatology-at-budget and interval sections | board generator |

**Count = 5.**
- P2's "≈ 13–15" was counted by a looser reading. P4's baseline should re-count P2 under this rule before comparing.
- Instance-local patches: **0**. The exemplar is Atlantis's own.

### Artifacts

- core 0.6.1 → **0.7.0**;
- atl_v0 0.7.0 → **0.8.0** (78 controls: 9 positive, 69 negative, ALL WORLDS AGREE);
- the exemplar `atlantis.yaml` (`interval_season_start_month: 8`);
- board v4 (regenerated before any push, under `--regenerate`, after the review);
- `BOARD.md`;
- the schema README and fit matrix §8;
- the board and core READMEs (known limit 5, F-6);
- the local III store: C-003, C-009, C-010, C-026 and C-034 bumped; C-035, C-036 and C-037 new, `accepted` null until the
  operator accepts.

## Follow-up

- **M-2c-ii** (opus), in order:
  1. FKNMS mapping pin → 0.8.0 (upkeep), `learner_swaps`, `interval_season_start_month` (1 suits a summer heat event;
     the steward rules), and the `federation_ref` pin;
  2. re-run v3 at 0.7.0 and send it by memo;
  3. the register re-read for T2, T10 and T11, every number from an entry, "point estimate" nowhere it is no longer true,
     and the nominal level said.
- **The calendar + signal comparator** (G-12, ruling 3) is the next comparator. It is the cheap competitor most likely to
  close FKNMS's gap.
- **The interval's coverage is not measured.** A per-season t-interval with B − 1 df beside the percentile one (reviewer's
  suggestion), or a coverage simulation stamped per B, is a candidate before any steward reads an interval as a decision.
- **Not done:**
  - F-8b, an "estimate within bounds" check. A percentile bootstrap need not contain the full-sample estimate, so the
    check would be false.
  - F-8c, adding the seed to `semantic_hash`. The hash names the trained model, not its reading; this is disclosed.
- **Operator acts:**
  - accept or reject C-035, C-036 and C-037;
  - the push (gitleaks first). This sitting pushed nothing.

## III review

The full report is `iii_review_m2c_i.md` (fresh context via `iii/` → `skill_iii_review` v0.6.0; reviewer ≈ 216 kT
metered). Its verdict was **PASS-WITH-FINDINGS**: 0 blocker · 4 major · 3 minor · 3 nit.

| Finding | Disposition |
|---|---|
| F-1 major (C-035): red at HEAD | Fixed: supersession test derives its top. The suite count is recorded with its commit (SITREP) |
| F-2 major (C-036): nominal 95% at 4 blocks | Fixed: `level_is_nominal`; per-season deltas, seasons favouring the model, exact sign test; BOARD and README say "spans 0: no" ≠ distinguished |
| F-3 major (C-034): uncertainty off the budget | Fixed (ruling 4): Δ precision and Δ recall at the fixed thresholds, plus matched-volume Δ precision, in the same draws; the board checks the point estimates against the two budgets |
| F-4 major (C-037): guards on siblings | Fixed: `_take`, `fit_scored`, fit row counts. Plants A and B in `test_m2c.py` |
| F-5 minor (C-026): calendar-year "season" | Fixed (ruling 5): `season_start_month` (slot + 2 controls), the exemplar uses August, partial edges disclosed |
| F-6 minor: no limits on file | Fixed: core README known limit 5 |
| F-7 minor (C-003): bounds by analogy | Fixed: `neg_interval_upper_gt_1`, `neg_interval_estimate_lt_minus1` |
| F-8 nit (C-009, C-010) | (a) Guard dropped; C4 planted against the identity control. (b) `MIN_DRAWS` 200, multiset check, interval `delta`; "estimate within bounds" not adopted (see Follow-up). (c) Disclosed, not hashed |
| F-9 nit | Fixed: "same **nominal** budgets" |
| F-10 nit | Disclosed in the v4 notes and here |

## Budget

The card's figure is ≈ 350 kT for the main lane plus ≈ 200 kT for the reviewer. These are estimates, not meters, except
the reviewer's:

| Lane | Tokens | Against the card |
|---|---|---|
| Main | ≈ 400 kT | ≈ +14% |
| Explore agents at planning | ≈ 390 kT | not carded; the card never counted them |
| III reviewer (metered) | 216 kT | ≈ +8% |

No SITREP line was crossed (+50% ≈ 525 kT main).

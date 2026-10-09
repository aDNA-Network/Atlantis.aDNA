---
type: aar
mission: mission_m2c_ii_fknms_v3_and_swap
campaign: campaign_atlantis_genesis
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261009_015643_m2c_ii_fknms_v3_and_swap
tags: [aar, m2c_ii, fknms, learner_swap, climatology, interval, board, register, iii, atlantis, tidewatch]
---

# AAR — M-2c-ii: FKNMS v3 by memo, T2's swap, the register re-read

**Scope.** This is the second half of P2-gate condition (a). It covers FloridaKeysCoral.aDNA (FKNMS) re-run at core 0.7.0
with a logistic learner swap, landed as board v3 by steward memo, and the register re-read for T2, T10 and T11 at their
terms. With M-2c-i, **condition (a) is met**, so M-3b may open once its other P2-gate conditions are met.

**Rulings** (`AskUserQuestion`, 2026-10-08):

| # | Ruling |
|---|---|
| 1 | FKNMS `eval.interval_season_start_month: 1` (steward). Calendar years give 7 whole test seasons, 2019–2025, and a summer heat season never straddles New Year |

## Worked

- **The steward's order held.** FKNMS committed, in order and all before the run:
  1. the mapping-pin upkeep (`ff7eda9`);
  2. the config (`0ad8804`);
  3. the federation pin (`8bc76f3`).

  The run started 10 s after the config commit (`run_at` 01:57:33Z). The config bytes the entry records (`43f06f0022`) are
  that commit's blob, so the M-2b F-6 trap did not recur. The reviewer found that the guard cited for this checks the
  working tree (F-4, C-039); the order held by hand.
- **The hash held.** `semantic_hash` stayed `c07b7c0288`. It was checked before the commit and re-derived by the reviewer
  on both configs.
- **v3 ≡ v2, read by a leaf-walk.**
  - All 2,307 of v2's metrics leaves are equal except `atlantis_core`, `run_at` and the md5.
  - The new leaves are climatology at budget (29) and the interval (96).
  - The model, SHAP and what-if bytes are unchanged, and `delta_vs` shows no field changed.
- **The memo path ran a third time without friction.** The landing re-check covered: sha256 = committed bytes = inline
  JSON · validate · assert_green · unit_ref · hash · md5. Landed at `492cb61`; `BOARD.md` has 8 entries and `--check` is clean.
- **C-032 was checked by script, twice.** After the first write, 109 of 109 register decimals traced to the entries or the
  swap file. After the review fixes, 112 traced, apart from three that are the reviewer's own and cited to its report.
- **Plant-first again.** Both core changes fail by name before the fix:
  - `test_page_data_carries_the_paired_interval` raised a KeyError;
  - `test_board_check_compares_the_interval_the_page_cites` did not raise on a doctored matched-volume estimate.
- **The review earned its cost.** It came back PASS-WITH-FINDINGS, 0 blocker · 1 major · 7 minor · 3 nit. The major
  finding is the one that mattered: the mission measured T11 at its operating point and then read it off that point in
  prose.

## Didn't

- **Over-read T11 on FKNMS (F-1, C-034 ×3).** The first reading (`eb1fda3`) had three faults:
  - it led with "climatology's precision is higher" (0.6228 against 0.5677), a raw gap at unequal realised volumes, which
    the core README's own limit 5 says is not skill;
  - it read "the chosen budget" at the 20.3% volume the 10% threshold happened to deliver under the shift, not the volume
    a steward staffs;
  - it set the 5% row aside on a volume objection that the matched-volume number beside it already answers.

  The verdict survives; the reasons did not. Under both readings of the budget the model is **not shown to beat**
  climatology: matched-volume ΔP is −0.0221 [−0.0906, +0.067] at 20.3%, and +0.0839 [−0.0118, +0.1926] at 8.8%. That is
  *no demonstrated advantage*, not a demonstrated deficit. Fixed in the register, on the page and in README limit 5.
- **Read T2 off point estimates in the same commit that read T11 through intervals (F-2, C-038).** "The logistic is the
  better learner" became "not shown either way". The reviewer's approximate interval is cited.
- **The v2 page overclaimed, and nothing caught it.** It said "the model beats every comparator". The build checks that
  the page's *numbers* equal the entry's; nothing checks that its *words* still hold once a newer reading lands. Corrected by
  token, twice: once at `24cc1f4`, and again at `fc6b65d` after F-1.
- **The page's field-for-field check stopped at `evaluation` (F-3, C-037 ×2),** while `8255d9b` had just let the page cite
  `evaluation_extras.paired_interval`. Fixed at `bcd2612`.
- **Left the hand-maintained surfaces behind (F-5, F-6, F-8, C-032 ×3).** These were:
  - the instance STATE ("mostly AUPRC", v2);
  - the reproduce command (`--version 1`);
  - the limits anchor, which had none of the new quantities' limits;
  - the register's "every other row stands", which skipped T9's +1.

  All are fixed. The pattern is that a re-run updates what the emitter writes, and every surface a person maintains drifts.

## Finding

- **T11 on FKNMS: falsified as worded, with no demonstrated advantage.**
  - The model is not shown to beat climatology at the chosen budget under either reading.
  - Threshold-free, ΔAUROC is +0.0176 [−0.0193, +0.0618], and only 3 of 7 seasons favour the model (sign p 0.7734).
  - Every level is nominal.
  - Proposed for the P3 gate; the operator rules.
- **"The chosen budget" is two things under a base-rate shift:** a threshold rule and a staffed volume. On FKNMS the sign
  of the point estimate differs between them. A verdict must say which reading it uses (README limit 5).
- **Both instances' verdicts rest on one nominal instrument.** The exemplar is "supported" because its intervals exclude 0,
  and FKNMS is "falsified" because they span it. Under-coverage (C-036) weakens only the first. The exemplar's 3-of-3
  (p 0.125) is the sign test's floor at 3 scorable seasons.
- **A hypothesis for P4, not a finding.** T11 holds where the calendar does not know the event (*K. brevis*, climatology
  AUROC 0.577) and fails where it does (summer heat, 0.9194). The calendar + signal comparator is its next test.
- **On FKNMS the GBM is not shown to earn its complexity.**
  - The logistic's point estimates are the higher: AUROC 0.9465 against 0.937, AUPRC 0.7361 against 0.6903.
  - The reviewer's approximate ΔAUROC is +0.0093 [−0.0056, +0.0253], with 6 of 7 seasons favouring the logistic.
  - T2's falsifier is not met.
  - The learner-dependent explanation replicates, and here it comes from collinearity, not availability.
- **Climatology cannot hit a small budget.** Its week-of-year ties take whole groups, so at a 5% nominal budget it realised
  0.1619. Only matched volume compares like with like.
- **The GREEN cap is close (F-7).** FKNMS v3 holds 582 numeric leaves and exemplar v4 holds 570, against a cap of 600. A
  same-core re-emit with `--vs` alone would reach 599 and 595, and 168 of FKNMS's leaves are `delta_vs` echoes.

## Change

### Atlantis changes, counted under the M-2c-i rule

| # | Change | Surface |
|---|---|---|
| 1 | The page's data carries `paired_interval_model_vs_climatology` (`8255d9b`). The build checks it against the entry (`bcd2612`, III F-3), a lockstep consequence on the same surface that is not counted again | site build |

**Count = 1, forced by FKNMS.** The register's T9 row records it.
- On its own line, as federation upkeep: the FKNMS mapping pin 0.7.0 → 0.8.0 (M-2c ruling 2).
- Instance-local patches: **0**. The steward's page rewording and STATE re-cut are the instance's words, not patches.

### Artifacts

- **FKNMS:**
  - commits `ff7eda9` · `0ad8804` · `8bc76f3` · `24cc1f4` · `fc6b65d`;
  - `atlantis.yaml` (swap, season month) and the `mapping.yaml` pin;
  - federation pin → `bcd2612`;
  - `metrics.json`, `learner_swap_logistic.json` and entry v3;
  - page (re-cites v3; §6, the manager note, a limits bullet and reproduce reworded);
  - `site.yaml`, `site_copy.yaml` and `STATE.md`.
- **Atlantis:**
  - commits `8255d9b` · `492cb61` · `eb1fda3` · `bcd2612` · `e6b8ef0` + close;
  - core `site/assemble.py` (keep-list, interval check) + 2 tests, and README limit 5;
  - board entry v3 and `BOARD.md`;
  - memo v3 (landed, plus a dated note) and memo v2 (`superseded_by`);
  - the register (T2, T9, T10, T11, reading note);
  - the review report;
  - the local III store: C-032 → 3, C-034 → 3, C-037 → 2; new C-038 and C-039, with `accepted` null.
- **Suite:** 742 at `ea2154d` → 743 at `eb1fda3` → **744 at `e6b8ef0`** (279 s; the close commit after it is docs-only, C-035).

## Follow-up

- **P3 gate:** rule T11's status. The proposal is *falsified as worded on FKNMS (no demonstrated advantage); supported at
  its terms on the exemplar.* Also rule T2's wording.
- **Operator decision before M-3 (F-7):** the GREEN cap. The options are:
  - count `delta_vs` echoes once, since they restate numbers already on the board;
  - raise the cap with a stated reason (it guards per-patient leakage, which summary echoes do not carry);
  - move the per-season deltas out.

  Record the decision with a control.
- **Next comparator:** calendar + signal (G-12, M-2c ruling 3), the test of the P4 hypothesis above.
- **Core candidates:**
  - **Per-budget seasons and sign tests (F-1 (5)).** These need GREEN headroom first.
  - **Interval coverage** is still unmeasured, carried from M-2c-i.
  - **The config-bytes guard should compare against `git show HEAD:<file>`** and fail closed (F-4, C-039).
  - **The swap row on the page is unchecked against the entry** (it predates this mission).
  - **The two page-data contracts under one "0.7.0" (F-9).** These are `1396ce2` and `8255d9b`/`bcd2612`. Adopt a patch bump
    for page-data contract changes from the next one.
- **atl_v0 "0.8.0" was amended before publication (F-11).** `1396ce2` added `season_start_month` to `AtlPairedInterval`
  without a bump. Neither version is on `origin/main`, so this is recorded in the CHANGELOG, not bumped.
- **A words check.** A page sentence that compares two numbers could be held to the entry, as the page's numbers are.
- **The steward's question for FKNMS:** is a model worth running here at all? The event has no lever, CRW publishes the
  operational product, and the calendar is not beaten.
- **Operator acts:**
  - the push (gitleaks first; nothing from M-2c-i or M-2c-ii is pushed);
  - accept or reject C-035 through C-039;
  - graduation candidates C-032 and C-034 (frequency 3), plus C-009 and C-010.

## III review

The full report is `iii_review_m2c_ii.md`. It ran in a fresh context via `iii/` → `skill_iii_review` v0.6.0; the reviewer
used ≈ 265 kT, metered. Verdict: **PASS-WITH-FINDINGS**, 0 blocker · 1 major · 7 minor · 3 nit.

| Finding | Disposition |
|---|---|
| F-1 major (C-034) | Fixed. Register T11 and the reading note: matched volume first, both readings of the budget, "falsified as worded: no demonstrated advantage", the exemplar's sign p at its floor. Page §6 and the manager note reworded by token. README limit 5 bullet. Per-budget seasons are carried as a core candidate (GREEN headroom) |
| F-2 minor (C-038) | Fixed: "not shown either way", the reviewer's interval cited |
| F-3 minor (C-037) | Fixed at `bcd2612`: `board_check` compares the interval, with a plant-first test |
| F-4 minor (C-039) | Card wording corrected ("checked at landing"); the git-HEAD guard is carried |
| F-5 minor (C-032) | Fixed: instance STATE re-cut; reproduce `--version 3 --vs v2` |
| F-6 minor | Fixed: a page limits bullet under the anchor the entry cites (ties, unequal volumes, nominal level at 7 blocks, January blocks), by token. The entry's `limitations_ref` is unchanged, because editing it would change config bytes and force a re-run |
| F-7 minor | Operator decision before M-3 (above) |
| F-8 minor | Fixed: T9 +1; counted here |
| F-9 nit | Disclosed; adopt a patch bump from the next page-data change |
| F-10 nit | (a) Hypothesis phrasing · (b) the clause replaced with "M-2c-i F-3 named the risk" · (c) the page claim removed · (d) README sign-test floor corrected |
| F-11 nit | Recorded in the CHANGELOG |

## Budget

The card's figure is "the remainder of M-2c's ≈ 350 kT, + a reviewer". M-2c-i spent ≈ 400 kT on its main lane, so the
nominal remainder was ≈ 0 and this mission was over the card from the first token. That is recorded, not hidden.

| Lane | Tokens | Note |
|---|---|---|
| Main | ≈ 250 kT (estimate) | includes the review-fix round |
| III reviewer | 265 kT (metered) | |

No SITREP line was crossed on the main lane.

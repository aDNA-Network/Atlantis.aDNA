---
type: aar
mission: mission_m1f_label_horizon_embargo
campaign: campaign_atlantis_genesis
created: 2026-10-07
updated: 2026-10-07
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261007_110514_m1f_label_horizon_embargo
token_budget_estimated: "~120-170kT (card)"
token_budget_actual: "≈ 300kT main (plan-mode orientation included; ≈ +76% on the card's top) + ≈ 240kT fresh-context III reviewer"
tags: [aar, m1f, p2, eval, embargo, horizon, board_v3, atl_v0, iii, atlantis, tidewatch]
---

# AAR — M-1f: the label-horizon embargo → board v3

**WI-23 closed.** M-2a-ii may open: `FloridaKeysCoral.aDNA` will be born under the embargo (default H = 8).

**Commits:**

| Commit | Content |
|---|---|
| `96a8cae` ① | eval: `split.embargo_weeks` at six boundaries · `check_label_windows` · `horizon_spill` · provenance · plants P5–P9 · `none` ≡ v1 and v2 |
| `81d0bf0` ② | `semantic_hash` reads the resolved embargo · conform item 8 · fork template comment |
| `f8fea56` ③ | atl_v0 0.6.0 `embargo_weeks` + 3 controls (56) · runner `grep -e` finding |
| `50f3499` ④ | board v3 by code · `assert_embargo` · extras · delta · atlantis_core 0.5.0 · mapping pin 0.6.0 |
| `18cabec` ⑤ | docs: README 2b fixed · exemplar README · M-2a-ii card · backlog done |
| `fd95cdd` ⑥ | III fixes, 7/7 · v3 re-run (numbers identical) and its never-pushed entry regenerated (recorded) |
| `1d9ee84` | ACCUMULATE (local store) |
| close | this AAR · card · roster · charter · STATE · CHANGELOG |

**Operator rulings (`AskUserQuestion`, 2026-10-07):**
1. **No v3 page.** The entry and docs are enough, and `limitations_ref` points at the core README's known limits.
2. **atl_v0 → 0.6.0**, with a typed `embargo_weeks`.
3. **The final refit re-adds the train tail.** Each set is embargoed only against the period it must not see.
4. At the +50% SITREP: **finish all**.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| Measure first, with the reviewer's method | `horizon_spill` reproduces the M-1e III table **exactly** as crossing positives (6/28 · 3/41 · 6/27 · 9/67 · 1/27 · 4/11 · 0/67 · 10/31). **Main split, first measurement:** train→val 25 of 7,971 rows (3 of 920 positives); val→test 34 of 1,193 rows (1 of 121 positives, 0 of them held only by 2020) |
| `split.embargo_weeks` (default H) plus `none`, on the main split and every fold | Resolved by `embargo_weeks()`: absent → H; `none`/0 → off; partial, bool, float or negative refused (also by conform item 8). Six boundaries: selection-train → stop, stop → test, refit → test, on the main split and per fold. Climatology and the sensitivity run follow the refit |
| A check that reads **label windows**; a planted crossing fails by name in the real path | `check_label_windows` reads the event's H, never E, on the frames a `FitRecorder` received (now on the main path too). P5–P9 are source plants into eval, each refused by name. Q2/Q3 (sensitivity, ablation) are refused at the board. **A raw-stream perturbation through `label.make`** (III F-4): 0 kept labels move, every dropped one does, and a cut one week short leaks |
| `none` reproduces v2 exactly | `test_none_reproduces_board_v2`: every key of v2's `metrics.json` to 1e-12 (it runs, ~1 min). The reviewer showed the same for the logistic swap. `hab_port` with `none` reproduces v1 |
| Board v3 by code, delta = embargo alone; atl_v0 controls, ALL WORLDS AGREE | `2026-10-07_gulf_karenia_brevis_v3.json`; `assert_embargo` refuses missing, off, short, unchecked, misattributed or under-cut boundaries (16 board plants). atl_v0 0.6.0: 56 controls, ALL WORLDS AGREE |
| README §Known limits 2b; v3 page only if ruled; WI-23 closed | 2b is marked fixed, with the measurement, the move, the week-year convention and the residuals. No page (ruling 1). WI-23 is closed in STATE |
| III review via `iii/`, fresh context; AAR; queue M-2a-ii | PASS-WITH-FINDINGS, 0 major, **7/7 addressed**. M-2a-ii is queued |

## The numbers (exemplar, board v3; method demonstration, SO-4)

Same test set: 1,640 region-weeks, base rate 0.0774.

| | v2 | v3 |
|---|---|---|
| Trees (early stop on the stop set) | 141 | 146 |
| Test AUROC / AUPRC | 0.8938 / 0.5388 | 0.8950 / 0.5414 |
| 10% budget: fixed threshold · realised · precision · recall | 0.272 · 8.11% · 0.511 · 0.535 | 0.281 · 7.99% · 0.527 · 0.543 |
| Lead time at 10% | 14 of 22 onsets ahead, median 4 wk | 13 of 22, median 4 wk |
| Climatology AUROC | 0.5767 | 0.5770 |
| Without surveillance | 0.8885 | 0.8911 |
| Sensitivity (50k /L) | 0.8878 (137 trees) | 0.8866 (118 trees) |
| Config hash | `acfa22c6e4` | `7b789afded` |

SHAP top-6 is unchanged, and no fold was skipped. **A leak removed, not a gain:** no difference here is tested for significance.

## Worked

- **Measuring first paid twice.** It validated the method, which reproduces the III table to the count, before anything was
  built. It also showed the main-split spill is small, which set the expectation that the headline would barely move, so
  a large move would have been a bug signal.
- **The check reads H from the event, not E from the setting.** Every plant that opens a boundary is refused, because the
  check never asks the embargo code what it did.
- **Port equivalence by running, not asserting** (C-025 applied on its first mission): `none` versus v2's `metrics.json`,
  every number.
- **The fresh-context reviewer again found what my tests could not.** My guard covered the runs I had thought about (the
  headline, swaps and folds), not every run the entry publishes.

## Didn't

- **C-009 again (frequency 5).** The board guard walked the headline, swaps and folds, but the entry also publishes the
  ablation and sensitivity AUROCs under the words "at every boundary". Unembargoing either passed 76 tests and emitted.
  **The guard's scope must be the publication's scope.**
- **C-023 again.** I documented `embargo_weeks` as written "from the boundaries it checked". It is E as resolved; what the
  checks prove is the H-window cut. It is now reworded, and backed by `rows_dropped ≥ crossing rows`.
- **C-018 again.** Each boundary was judged against its own `next_start`. It now uses the split's.
- **Unverified prose, caught twice by me before commit and once by the reviewer.** I wrote "peak bleaching season" for
  Nov–Dec, "a bloom season" for December, and "never fitted" for a train tail that the refit does fit.
- **Provenance churn.** The v3 entry was emitted three times before its first commit (version bump; outputs re-run under
  0.5.0 so the `atlantis_core` string names the code that ran) and regenerated once after (III F-1/F-7, recorded). It
  should have been one emit after the version bump. The rule: bump the version before the first board run.
- **Budget ≈ +76% on the card's top.** The SITREP at +50% was made, and the operator ruled to finish.

## Findings of record

1. **The main-split spill was small** (3 + 1 crossing positives). The fold stop years carried most of it (up to 10 of 31).
   The negatives whose "no bloom" label read the next period were never in the III count. They are now: 25 + 34 rows.
2. **The schema runner was blind in one world.** A `REJECTS_ON` starting with `-` was read as a grep option. Exit 2 was
   then read as "all named", so linkml-validate never tested `neg_event_refractory_negative`'s reason (since 0.5.0). The
   JSON worlds held. Sabotage proved it; the runner now reads grep's exit status whole (III F-5, C-021).
3. **The boundary is exact in week-years, not calendar years** (III F-4, new C-026). A year's last ISO-Monday week holds
   1–5 January.
4. **A leakage check that shares its formula with the cut proves less than it seems** (new C-027). The perturbation test
   through the labeller is now the anchor.
5. **The test-year fold skip was silent** (III F-7). It is now said in `rolling_skipped`. It matters for FKNMS, where every
   zone heats in the same years.

## III review (fresh context, via `iii/` → `skill_iii_review`, III v0.6.0)

**PASS-WITH-FINDINGS:** 0 major, 7 minor, **7/7 addressed** in `fd95cdd`. The reviewer independently confirmed:
- the boundary is exact (perturbation, inflate and delete, 0/10,764 and 0/1,377 kept rows move);
- v3 re-derives from today's code;
- `none` reproduces v2's swap as well;
- every number in the notes and docs is correct.

| Finding | Fix |
|---|---|
| **F-1** (C-009): ablations and sensitivity were unguarded | Sensitivity records its embargo; `assert_embargo` walks every variant and block; real-path plants Q2/Q3 |
| **F-2** (C-018): a boundary trusted its own `next_start` | Expected years come from the split; empty sets and null window ends are refused; the headline and full copies must agree |
| **F-3** (C-023): `embargo_weeks` "from the act" was config | Reworded (schema regenerated); `rows_dropped ≥ crossing rows` |
| **F-4**: week-years vs calendar years | Stated in 2b; `tests/test_embargo_perturbation.py` |
| **F-5** (C-021): grep exit 2 fail-open | Exit status read whole; a bad-regex sabotage now reddens |
| **F-6**: a traceback on a malformed embargo | `receipt_problem` returns it as a refusal; receipt re-earned |
| **F-7**: prose, and unnamed moves | README and card train-tail wording; exemplar README base rate and budget; v3 notes name climatology, sensitivity and ablation; test-year skip said |

**Learning store (local):** C-009 → 5, C-023 → 3, C-018 → 2, C-021 → 2; new C-026 `boundary_year_is_the_binning_year`, C-027
`leakage_check_shares_formula_with_cut`. **Graduation candidates (frequency ≥ 3):** C-004 · C-005 · C-009 · C-015 · **C-023**.

## Change

- **A publication guard's scope is the publication's scope.** List every number the entry publishes, then check that each
  one has passed the guard.
- **Pair every leakage check with a perturbation of the raw input through the real labeller.** A recomputation of the
  same formula is not enough.
- **Bump the version before the first output run** that a board entry will cite.
- **No seasonality or ecology claim without a source.** Name the convention, and leave the season to the steward.

## Follow-up

- **M-2a-ii** (opus): the FKNMS fork and fetch, born under the embargo (E = 8 by default; Nov–Dec at each boundary). Expect
  test-year and stop-year skips; they are now said.
- **Graduation memo:** C-023 joins the candidates. Delivery into `III.aDNA/who/coordination/` is an operator-opened act.
- **Push:** `4d812f9..HEAD` is unpushed (board v3 included). The push is outward and needs the operator's ruling; run
  gitleaks over the range first.

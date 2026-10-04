---
type: aar
mission: mission_m1e_eval_thresholds_on_validation
campaign: campaign_atlantis_genesis
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261004_035631_m1e_thresholds_on_validation
token_budget_estimated: "~110-160kT (card); ~160-230kT after this sitting's rulings"
token_budget_actual: "≈370kT main (plan-mode orientation included) + ≈260kT fresh-context III reviewer"
tags: [aar, m1e, p1, f8, eval, thresholds, board_v2, atl_v0, iii, atlantis, tidewatch]
---

# AAR — M-1e: thresholds and fold tree counts fixed on validation (F-8) → board v2

**P2 condition (a): CLOSED.** M-2a may open.

**Commits:**

| Commit | Content |
|---|---|
| `20075f1` ① | eval: `threshold_from` · `rolling_selection` · per-fold inner selection · R7 on the inner split |
| `d13c73e` ② | atl_v0 0.4.0: `threshold_from` · `realised_rate` · rule · 5 controls |
| `96acc3f` ③ | board v2 emitted by code · F-8 refusals · `BOARD.md` budget columns · atlantis_core 0.3.0 · `test_f8` |
| `b8ff972` ④ | site reads a named run (`outputs:`, `--site`) · conditional realised column · v1 copy verbatim |
| `9d63dbe` ⑤ | the v2 page and its copy |
| `4bda9b5` ⑥ | III fixes, 8/8 |
| close | this AAR · card · roster · charter · STATE · CHANGELOG |

**Operator rulings (`AskUserQuestion`, 2026-10-03):**
1. The threshold comes from quantiles of the **selection model's** out-of-sample val scores.
2. **Amend atl_v0 → 0.4.0.**
3. **Build a v2 page** as a new file.
4. **Every** rolling fold selects on its own inner year.
5. At the +50% line (~235 kT): **finish all of it**.
6. III F-6 (horizon spill): **disclose now; the embargo goes to its own lane** as a new board version.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| `eval.threshold_from: val \| test` (default val), fixed before test is scored; realised beside nominal; lead time reads the same threshold | `_variant` fixes thresholds on `L.predict(vm, val)` and reads them **back from the result**, refusing a mismatch. Every budget carries `nominal_rate`, `realised_rate` and `threshold_from`. Lead time records `alert_threshold`, which is checked against the fixed 10% threshold (III F-2) |
| Folds early-stop on their own inner year; none reuses a count stopped on its test years | Fold Y: `fit(≤Y−1, ==Y)` with eras clipped ≤ Y−1, then `refit_fixed(≤Y)`. It is checked on the frames `fit` actually received (a `FitRecorder`; III F-1), and the eras against `clipped_eras(Y−1)`. A stop year with < 5 positives skips its fold and says so |
| Port keeps a `test` mode; hab's v1 numbers reproduce | `hab_port` runs `test` / `full_model`: 141 trees, 0.8941 / 0.5473, every `metrics.json` key to 1e-12 |
| Planted defects, each caught by name | Source-level plants into eval's own code (`test_f8.py`): **P1** stop on the test year and **P2** selection eras through Y → `F-8 fold 2015→2016 …`; **P3** lead threshold from test → `F-8: lead time read threshold`; an `evaluate` that drops the fixed thresholds → `F-8: applied thresholds`. A realised rate missing beside nominal → schema control + `BoardError`. **C-009:** **P4** (thresholds fixed on the final model's *test* scores) passes every identity check, and the real-path invariance test catches it. hab's own reading (`threshold_from: test`) fails the same test |
| Board v2 by code, delta = F-8 alone; `AtlEvaluation` amended with controls; `limitations_ref` names the fix (WI-14); `BOARD.md` shows v1 superseded | `2026-10-03_gulf_karenia_brevis_v2.json`. Headline unchanged: 0.8938 / 0.5388 · 141 trees · `acfa22c6e4`. `model.json`, `shap_summary.json` and `whatif.json` are **byte-identical** to v1's. atl_v0 0.4.0: 50 controls, ALL WORLDS AGREE. `limitations_ref` → the v2 page's `#limits`. `BOARD.md`: v0 and v1 superseded → v2 (derived); budget table gains source and realised columns |
| New page is a new file citing v2; v0/v1 pages and entries byte-stable | `site/gulf_karenia_brevis_v2.html` (from `site_v2.yaml` + `site_copy_v2.yaml`). v0/v1 entries, the v0/v1 pages and v1's `metrics.json` are pinned by sha256 in `test_f8`. A v1 rebuild differs only in the template block and the build date, and renders its five columns (browser-checked) |
| SO-7 green (vitals and labels untouched); full suite; README §Known limits | Self-test green, and no vitals or label code changed. **516 tests** (480 → 516). Exemplar suite 11. README items 1–2 marked fixed, with residuals; 2b added (horizon) |
| III review via `iii/`, fresh context; AAR; WI-11 closed | PASS-WITH-FINDINGS, **8/8 addressed** (below). WI-11 and WI-14 closed |

## The numbers (exemplar, board v2; method demonstration, SO-4)

Base rate 0.0774 on 1,640 test region-weeks.

| Nominal budget | Threshold fixed on 2017–19 | Realised on test | Precision | Recall | Alerts |
|---|---|---|---|---|---|
| 5% | 0.437 | 3.78% | 0.661 | 0.323 | 62 |
| 10% | 0.272 | 8.11% | 0.511 | 0.535 | 133 |
| 20% | 0.120 | 19.33% | 0.319 | 0.795 | 317 |

- **Lead time:** at the 10% budget's fixed threshold, 14 of 22 onsets (0.636) are flagged ahead, median 4 weeks. v1 read
  0.682 at a threshold chosen afterwards.
- **Rolling folds:** each fold now selects its own tree count, with stopped counts of 63–623 trees.
- **Comparing with v1:** v1 and v2 are points on one curve of one model, not a gain or a loss.

## Worked

- **The single-cause proof was strong.** F-8 never touches the trained model, so "F-8 alone" could be shown by bytes:
  identical model, SHAP and what-if; identical AUROC/AUPRC/Brier/calibration; the same semantic hash. Only budgets, lead and
  folds move. The design followed the card's "nothing else mixed in" and made it testable.
- **Separate output and processed directories** (`--out outputs/atlantis_core_v2`). v1's outputs, page and provenance
  stayed untouched and rebuildable, so v2 needed no in-place edit of anything published.
- **Schema sabotage in a scratch copy.** It reproduced the M-1c untyped-postcondition hole on the new rule before anyone
  asked. The typed `all_of` is shown to be load-bearing.
- **The fresh-context reviewer earned its cost.** It wrote plants into the real code and broke two guards that every
  test of mine had passed.

## Didn't

- **Two of my guards were true by construction (C-009, again — now frequency 4).**
  - `selected_on` was set from `Y`, and the test read it back.
  - The lead time's `threshold_from` was stamped from config.
  - My first runtime fix for F-3 **recomputed** the thresholds it then compared against. It was caught on re-reading,
    before the commit.
  - The fix that held: check **what the code received or returned**, and test with **source-level plants** into the real
    module (P1–P4).
- **A sentence I wrote stated more than I had verified.**
  - The first copy and board note said the validation years "had more blooms". By count they have *fewer* positive
    region-weeks (121 vs 127); only the rate is higher. I also called the prevalence gap the cause.
  - I caught this myself (F-5's sibling). The reviewer then caught "onsets" used for positive region-weeks.
  - Both are fixed in an unpublished regeneration.
- **The page first compared v1 and v2 at a nominal label** (F-7), which is the very thing its own note forbids.
- **The budget ran to about +130% on the card.** ~370 kT main includes the plan-mode orientation; the reviewer used
  ~260 kT more. The SITREP at +50% was made, and the operator ruled to finish.

## Findings of record

1. **Fixing thresholds beforehand moves every realised rate below nominal here** (3.8 / 8.1 / 19.3%). Two reasons are
   likely and neither is proven:
   - the validation positive rate is 0.101, against 0.077 on test;
   - the thresholds come from the train-only selection model, while test is scored by the train+val refit.

   A steward must staff to a budget knowing it drifts.
2. **Per-fold selection on a single year is noisy** (63–623 trees). The rolling panel now measures the method with its
   selection included.
3. **The label horizon crosses every split boundary** (III F-6). It was measured at the fold stop years (up to 10 of 31
   positives) and holds by construction at the main split. Calendar-year checks are a proxy.
   - Operator ruling: disclose now; the fix is carded (`how/backlog/idea_label_horizon_embargo.md`) as its own board
     version, because it moves the model.
4. **A provenance label stamped from intent lets any defect beneath it emit clean** (C-023, new). The rule from here on:
   every provenance field is derived from what the code did.

## III review (fresh context, via `iii/` → `skill_iii_review`, III v0.6.0)

**PASS-WITH-FINDINGS.** 2 major and 6 minor, **8/8 addressed** in `4bda9b5`.

- **F-1 (major):** fold selection was checked against intent.
  - Fix: a `FitRecorder`; eras checked against `clipped_eras(Y−1)`; the inner-positives guard.
  - Plants P1 and P2 are tested.
- **F-2 (major):** lead time recorded no threshold.
  - Fix: it records `alert_threshold`, with an identity check in eval and in the board.
  - Plant P3 is tested.
- **F-3:** `check_thresholds_fixed` was vacuous. It is removed; the runtime check now reads the result, and P4 is tested.
- **F-4:** swaps went unchecked at the board, along with the realised arithmetic and unknown values. The board now checks
  all three.
- **F-5:** "onsets" was used for positive region-weeks, and fractions were retyped. Fixed in the note and with page tokens.
- **F-6:** the horizon spill is disclosed and the embargo carded (operator ruling).
- **F-7:** removed the was→now comparison at a nominal label.
- **F-8:** docs committed; the overclaim corrected.

**Learning store (local):**
- C-009 → frequency 4, a graduation candidate (already proposed by memo with C-004);
- C-022 `label_window_crosses_split_boundary` (new);
- C-023 `provenance_label_stamped_from_intent` (new).

## Change

- **Every provenance field is computed from the act, never copied from the config.** That covers `threshold_from`,
  `selected_on`, eras and thresholds. Its gate checks identity or arithmetic, not the label.
- **A guard is proven by a plant written into the real code**, not into a helper that by signature cannot see the defect.
- **A comparison sentence names its count and its rate separately** before it says "more".

## Follow-up

- **M-2a** (opus), now unblocked: FKNMS fork · CRW-via-ERDDAP check · persistent-event self-test · fetch.
- **Horizon embargo** → board v3 (`idea_label_horizon_embargo.md`). The operator places it: with M-2b, or as its own lane
  before the P2 gate compares the exemplar with FKNMS on the board.
- **C-009 graduation:** frequency 4 strengthens the memo already filed to III.aDNA. Delivery is still an operator-opened
  act.
- **Push:** 7 commits since `origin/main`, gitleaks-clean. The push is outward and needs the operator's ruling.

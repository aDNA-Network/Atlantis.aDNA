---
type: aar
mission: mission_m2b_fknms_model_and_board
campaign: campaign_atlantis_genesis
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261008_172828_m2b_fknms_model_and_board
token_budget_estimated: "~150-200kT main + fresh-context III reviewer"
token_budget_actual: "≈ 480 kT main (estimated, not metered; SITREP raised at the +50% line, ruling 23 continued) + III reviewer ≈ 192 kT · ≈ +140% on the card top"
tags: [aar, m2b, p2, fknms, coral, eval, comparators, board, site, iii, atlantis, tidewatch]
---

# AAR — M-2b: FloridaKeysCoral.aDNA, from data to the board

**The second instance — the first marine protected area — is trained, explained, paged and on the board.** Board entry
`2026-10-08_florida_keys_coral_v2` (GREEN, closed `AtlEvaluation` at atl_v0 0.7.0, `method_demonstration`), landed by memo
(v1, landed first, is superseded on provenance alone — III F-6);
the page `site/florida_keys_coral_v1.html` lives in the instance; `conform` (full) → 12 pass. **The P2 gate is requested
(fable, operator-summoned).**

## Acceptance (card)

| Criterion | |
|---|---|
| `run` in the instance: trained · budgets with thresholds fixed on validation, realised rates · lead time · climatology · explained · tagged; levers: none, said | ✅ `9ac40cf` (instance `6e031f6`) |
| Persistence/trend baseline beside climatology, with a plant | ✅ core 0.6.0 — rulings 19 (shape) and 20 (atl_v0 0.7.0 slots); plants S1 S2 B1 B2 + five result plants |
| Ruling 16: per-segment base rate, calibration under the shift; Limitations carry the single-cell zones, the 1999-05-01 gap, the non-stationary base rate | ✅ `base_rate_train/validation`, `calibration_in_the_large_*` on the board; page §6 and §11 |
| Page in the instance, with Limitations; none enters Atlantis | ✅ `site/florida_keys_coral_v1.html` (instance only) |
| Board entry by `--entries`, GREEN, method_demonstration, conform item 9 ✅; memo → inbox → landed in an operator-opened session; `board --index` | ✅ memo `…_board_entry` → v1 landed `94ee95f` (ruling 22); memo `…_board_entry_v2` → v2 landed `0a1dd2e` (rulings 24, 26) |
| T1 · T3 · T9 · T10 re-cut | ✅ `40f9b3a`, corrected after III (F-3, F-4, F-8c) |
| Zero instance-local patches; every deviation a P1 template change, listed | ✅ below (§Change) |
| III via `iii/`, fresh context; AAR; request the P2 gate | ✅ §III review · this file · STATE |

## The numbers (test 2019–25 · 5,595 zone-weeks · 840 positives · base rate 0.150; config `c07b7c0288`)

| | AUROC | AUPRC |
|---|---|---|
| model (XGBoost, 108 trees) | 0.937 | 0.690 |
| climatology (week-of-year onset rate) | 0.919 | 0.601 |
| trend (logistic on DHW and its last step) | 0.781 | 0.520 |
| persistence (DHW at t, no model) | 0.751 | 0.358 |

- **Segments (ruling 16):** base rate 1.31 / 7.59 / 15.01%. Mean p − prevalence −0.045 (val) → −0.097 (test); slope 1.99.
- **Budgets:** thresholds fixed on 2014–18 flag **8.8 / 20.3 / 28.6%** of test at nominal 5 / 10 / 20% — 1.4–2× (precision 0.74 / 0.57 / 0.48; recall 0.44 / 0.77 / 0.92).
- **Lead:** 105/105 test onsets flagged at the 10% budget's threshold — which flagged 20.3% of test zone-weeks — and 67 at the
  8-week maximum: **censored at H**. lead.py's onset count = the label's (105): R = H − 1 holds on real data.
- **Rolling origin (ruling 21):** 11 folds, AUROC 0.84–0.99 while prevalence runs 0.7–29.7%; 2014 skipped (2013 has no onset).
- **Explain:** HotSpot (t0, t1, t2) > SSTA > DHW t4. **No lever.** Sensitivity DHW ≥ 8: 0.875 / 0.238 at 6.3%.
- **Exemplar (v4 outputs, not on the board):** persistence 0.762 / 0.372, trend 0.800 / 0.398, climatology 0.577 / 0.105, model 0.895 / 0.541 — v4 ≡ v3 on every v3 number.
- **T3 (scratch, never the board):** a persistence-inclusive label → AUPRC 0.690 → 0.929 at prevalence 0.150 → 0.270 (lift 4.60 → 3.44);
  the persistence comparator closes from 52% to 88% of the model's AUPRC — the score becomes a reading of persistence.

## Worked

- **Every steward choice through `AskUserQuestion`** (rulings 19–23), including the one that moved the hash (21).
- **The comparators changed the reading, not the numbers.** Exemplar v4 ≡ v3 byte-for-byte on the model; on FKNMS the
  comparator that matters is the *calendar* (0.919), not persistence — a result nobody predicted at planning.
- **The landing discipline held:** the entry's sha256 was pinned in the memo and re-checked on the Atlantis side before the copy.
- **The realised rate (M-1e) earned its keep:** it is what made the doubled alert budget under the shift visible.

## Didn't

- **Budget.** ~150–200 kT estimated; ≈ 480 kT main + 192 kT reviewer. The SITREP was raised at the line this time (ruling 23), but
  late: the comparators + schema (+25 kT planned) were joined by five unplanned P1 fixes and a full page authoring.
- **I broke the page and the suite did not notice.** A `//` comment on a one-line IIFE killed every chart; 676 tests passed.
  Caught only by loading the page in a browser. Now a `node --check` test with the defect planted back.
- **A pager hung a background command for ~10 min** (`git diff` inside a pipeline).

## Findings of record

1. **The calendar knows most of a summer heat event** (climatology 0.919 vs model 0.937). Without the 0.7.0 comparators and
   T11's climatology slot, the headline would have read as skill the season already provides (SO-9).
2. **A threshold fixed on lower-rate years over-alerts in higher-rate ones by 1.4–2×** — the operational face of non-stationarity.
3. **Lead time is a censored measurement when the event signal accumulates.** The slot fills; its median is the window.
4. **Two checks had never met a core-built artifact:** conform item 10 could not pass any `atlantis_core.site` page, and
   the fork guaranteed eval's `rolling_origin_years` KeyError. Both C-015 class (fixture-only coverage).
5. **A build that checks words and tokens is not a build that checks the page runs** (the script defect).

## III review

**PASS-WITH-FINDINGS** (fresh-context agent via `iii/` → `skill_iii_review` v0.6.0; deep · text + code + data + one
render): 0 blocker · 4 major · 3 minor · 1 nit — **8/8 addressed** (Atlantis `28e5af4` · `0a1dd2e` · the register; instance
`88685c7`). Steward rulings 24–26 chose between alternatives. Independently confirmed: 685 tests; 65 controls in all three
worlds; **every FKNMS number reproduced** by a re-run at HEAD (model bytes identical); persistence's s(t) ≡ the label's
`last_known_signal` on FKNMS too (40,226 rows); the trend fit ≡ the refit→test embargo frame (34,470 rows); B1/B2 refused by
name; the entry re-projects with zero diffs; nothing per-patient on the board; zero instance-local patches.

| Finding | Fix |
|---|---|
| **F-1** major (C-007): nothing tested the trend's *step* input; `s_prev = shift(−1)` left 16 tests green | Plant S3; `s_prev` ≡ the label's carried signal at t − 1 wk on every exemplar unit-week; schema nearest-miss note |
| **F-2** major (C-011): item 10's copy path passed a page whose script throws — the defect `671808b` had just fixed | **Ruling 25:** the page must carry the section renderer and its script must pass `node --check` (else "render unverified"); plants for both |
| **F-3** major (C-031): T3's AUPRC compared across base rates (0.150 vs 0.270) and test sets; lift (4.60 → 3.44) omitted | Lift and the comparator gap reported; the falsifier restated so prevalence cannot meet it |
| **F-4** major (C-032): the register's roll-up called T3 and T10 two-instance; their rows said one | "Tested on one instance (FKNMS)" |
| **F-5** minor (C-009): `assert_comparators` holds by construction for the real eval, documented as verification | Documented as a tamper check; slot ↔ result equality for persistence, trend and CITL; plants |
| **F-6** minor (C-023): the entry's `config_bytes_md5` named bytes no commit holds (`limitations_ref` edited after the run) | **Ruling 24:** re-run from the committed config; **ruling 26:** SO-2 refused to regenerate an entry it cannot prove unpublished → **v2** published, v1 superseded; the board now refuses stale config bytes |
| **F-7** minor: mixed denominators — val's CITL on the 4,581-row stop set beside a 4,742-row table; "Onsets" counting positive rows; "105/105 at the 10% budget" read at a threshold that flagged 20.3% | The stop set's n and prevalence on the page; the column is "Positives"; the realised rate stated beside the lead claim |
| **F-8** nit: "about twice" (1.4× at 20%); "because … warmer"; T9's count | "1.4–2×"; "carry more heat stress"; the nine changes numbered |

**Learning store (local):** C-007 → 2 · C-009 → 6 · C-011 → 2 · C-023 → 5; new **C-031** `metric_compared_across_base_rates`,
**C-032** `register_summary_outruns_rows`. **Graduation candidates (frequency ≥ 3):** C-004 · C-005 · C-009 · C-010 · C-015 · C-023.

## Change (every deviation, Atlantis-side, tested — T9)

- **core 0.6.0 (`9ac40cf`):** persistence + trend comparators; per-segment base rate; calibration-in-the-large;
  `assert_comparators`; `rolling_origin_years` optional; swap summary without folds; BOARD.md section; site comparator rows.
- **atl_v0 0.7.0:** eight optional slots, 65 controls. Template mapping pin 0.7.0; fork answers document rolling origin.
- **`671808b`:** template script parses (node test); polygon unit names; conform item 10 reads a core-built page.
- **core 0.6.1 (`28e5af4`, 694 tests), the III fixes:** step-input plant; item 10 needs a parsing renderer; slot ↔ result equality; stale config bytes refused; the "Positives" column; val's stop-set denominator on the page.
- **Unplanned P1 defects only a real instance reached (this mission):** rolling-origin KeyError · polygon names · item 10.

## Follow-up

- **The P2 gate** (fable, operator-summoned): rule the T1/T3/T9/T10 statuses — above all whether T9's weak form meets the exit bar.
- **The exemplar at 0.7.0:** its v4 outputs exist; a board v4 entry would make the two instances commensurable (T10 qualifier).
- **A climatology budget row** (T11: "at the chosen budget" is not measured).
- **Conform item 12's gitignored-cache walk** (from M-2a-ii) — the full conform still takes ~35 s here; fine at this size.
- Operator acts: push Atlantis origin/main..main (gitleaks first); the WI-20 graduation candidates; Hestia's router row.

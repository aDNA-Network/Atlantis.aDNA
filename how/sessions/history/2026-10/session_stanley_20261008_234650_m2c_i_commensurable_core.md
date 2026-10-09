---
type: session
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
tags: [session, m2c, m2c_i, climatology, interval, board, atlantis, tidewatch]
session_id: session_stanley_20261008_234650_m2c_i_commensurable_core
user: stanley
started: 2026-10-08T23:46:50Z
status: completed
completed: 2026-10-08
executor_tier: opus
mission: m2c_i
campaign: campaign_atlantis_genesis
intent: "M-2c-i (P2-gate condition (a), first half): climatology at budget with val-fixed thresholds · season-block paired interval model − climatology · atl_v0 0.8.0 + controls · core 0.7.0 · BOARD.md lead column realised (G-7) · exemplar board v4. Plan: ~/.claude/plans/please-read-the-claude-md-piped-phoenix.md"
---

## Activity Log

- open — leases probed: Atlantis and FloridaKeysCoral `how/sessions/active/` hold only `.gitkeep`. Rulings (AskUserQuestion, 2026-10-08), numbered M-2c rulings 1–3:
  1. **Split** on the card's line: this sitting is M-2c-i (core + schema + lead column + exemplar v4); M-2c-ii carries FKNMS v3 + T2's swap + the register re-read.
  2. **The FKNMS `mapping.yaml` pin 0.7.0 → 0.8.0 is federation upkeep, not an instance patch.** Done by the steward in M-2c-ii, counted on its own line.
  3. **Calendar + signal comparator (G-12) deferred** — named in the AAR as the next comparator.
- Exploration facts: exemplar test = 2020–2023, **4 season blocks** (the card's "≈ 7" is FKNMS: 2019–2025); climatology ≈ 50 distinct scores, so val-fixed thresholds take whole week-of-year tie groups (realised rate load-bearing); existing `climatology_baseline_test` auroc/auprc are pinned by the hab port + v2 reproduction and must not move; FKNMS v2 `evaluation` has 33/40 keys (MAX_DICT), so new slots are nested.
- ① re-card `19c442d`: M-2c → `split`; cards M-2c-i (active) + M-2c-ii (planned); roster rows.
- ② eval (plant-first): `climatology_scores` split from `climatology_baseline` (pinned AUROC/AUPRC unchanged to the bit vs v4); `climatology_at_budget` (selection fit = train embargoed vs val, quantiles on every val week, applied to the refit's test scores, read back, fit years off the fit); `eval/interval.py` season-block paired interval (assert_whole_blocks per draw, pairing guard, seeded). Plants C1 (thresholds from test — caught by invariance, as P4), C2/C2b (selection fit unembargoed / reads val), C3 (rows), C4 (unpaired; + guard off → identical-scores control). 15 tests green first run.
- ③ atl_v0 0.8.0: `climatology_alert_budgets` (AtlAlertBudget) · `paired_intervals` (AtlPairedInterval) · IntervalComparator · IntervalMetric · ResampleUnit; 1 pos + 8 neg → 74 controls, ALL WORLDS AGREE (fresh scratch venv, linkml 1.11.1; committed JSON regenerated, 23 $defs). README (stale 7/49 → 9/65), fit matrix §8 (+ ThresholdSource rows it never had), template mapping pin, stale-pin test.
- ④ board: projection, `assert_climatology_at_budget`, `assert_interval`, `paired_interval` extras, delta; BOARD.md lead cell nominal · realised (G-7: FKNMS v2 now reads "@ 0.1 nominal · 0.2034 realised"), climatology-at-budget + interval section. Core 0.6.1 → 0.7.0 before any emit.
- ⑤ exemplar: self-test green; v4 re-run at 0.7.0 (188 s) twice (second for the interval `scope` wording — the swap run also carries an interval, so "headline only" was wrong). Leaf walk: v4 ≡ v3 on all 3,789 metrics + 3,998 swap leaves (only `atlantis_core`, `run_at` differ); model/shap/whatif bytes identical. Suite 731 passed (282 s). Commit `0da7414`.
- ⑥ board v4 emitted (`6fa20d3`), delta_vs: no field changed; `--index --check` ✅. Exemplar T11 at its terms: at 10% the model's precision 0.5267 (realised 0.0799) vs climatology 0.1185 (realised 0.0823); Δ AUROC +0.318 [0.113, 0.483], Δ AUPRC +0.437 [0.322, 0.696], 4 blocks / 35 draws — crude, neither spans 0.
- ⑦ III review launched via `iii/` in a fresh context (reviewer never saw the build).
- ⑧ III returned PASS-WITH-FINDINGS 0/4/3/3 (`missions/aar/iii_review_m2c_i.md`, reviewer 216 kT metered). Desk confirmed F-1 first-hand (main red at `6fa20d3`, test_f9 hard-coded v3). **Rulings (AskUserQuestion):** 4 (F-3) budget deltas + matched volume in the interval; 5 (F-5) season-years from a declared month (exemplar August).
- ⑨ fixes: F-1 derive top · F-2 nominal level + per-season + sign test · F-3 budgets · F-4 `_take` / `fit_scored` / fit rows (plants A, B) · F-5 `season_start_month` (+2 controls) · F-6 known limit 5 · F-7 +2 controls · F-8 MIN_DRAWS, multiset, interval delta, guard → identity control · F-9 heading · F-10 note. Plant B2 is now refused one check earlier (climatology refit), expectation widened. v4 re-run (265 s): ≡ v3 on every v3 leaf + config bytes. v4 entry regenerated (never pushed). Suite **742 passed on the tree of `1396ce2`**; controls 78, ALL WORLDS AGREE. ACCUMULATE `11299c9`.
- close: card completed; M-2c-ii card (start month, nominal level, matched volume); roster; charter; STATE (Next Session Prompt → M-2c-ii); CHANGELOG v0.14.0; AAR. Not pushed.

## SITREP

- **Completed:** M-2c-i — core 0.7.0 · atl_v0 0.8.0 (78) · BOARD.md lead column + climatology/interval sections · exemplar board v4 · III 10/10 · AAR.
- **In progress:** none.
- **Next up:** M-2c-ii (opus) — FKNMS v3 by memo + T2 swap + register re-read. M-3a may run beside it.
- **Blockers (#needs-human):** accept C-035/C-036/C-037; push (gitleaks first); deliver the graduation and Hestia memos; C-015 acceptance; FKNMS remote.
- **Files touched:** what/atlantis_core (eval, board, tests, README, version) · what/schema/atl_v0 (schema, JSON, controls, README, fit matrix) · what/board (entries v4, BOARD.md, README) · what/exemplars/gulf_karenia_brevis (atlantis.yaml, outputs v4) · how/templates/template_mapping_atl.yaml · the campaign (cards, roster, charter, AAR, review) · iii store · STATE · CHANGELOG.
- **Budget:** main ≈ 400 kT est. (≈ +14% on 350) · planning explorers ≈ 390 kT · III reviewer 216 kT metered.
- **Next Session Prompt:** STATE § QUEUED (open at opus).

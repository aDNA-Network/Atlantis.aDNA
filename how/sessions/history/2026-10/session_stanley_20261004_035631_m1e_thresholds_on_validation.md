---
type: session
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [session, m1e, f8, eval, thresholds, board_v2, atlantis, tidewatch]
session_id: session_stanley_20261004_035631_m1e_thresholds_on_validation
user: stanley
started: 2026-10-04T03:56:31Z
status: completed
completed: 2026-10-03
executor_tier: opus
mission: mission_m1e_eval_thresholds_on_validation
campaign: campaign_atlantis_genesis
intent: "M-1e (P2 condition (a)): alert thresholds and rolling-fold tree counts fixed on validation (F-8 / WI-11) → board v2, atl_v0 0.4.0, the v2 page. Plan: ~/.claude/plans/please-give-your-advice-whimsical-bird.md"
---

## Activity Log

- open — Rulings (operator, AskUserQuestion, 2026-10-03): (1) the threshold comes from the **selection model's** out-of-sample val scores; (2) **amend atl_v0 → 0.4.0** (threshold_from + realised_rate, with controls); (3) **build a v2 page** (a new file); (4) **every** rolling fold early-stops on its own inner validation year. Budget re-estimated at ~160–230 kT.
- ① eval (`20075f1`): threshold_from val|test · rolling_selection per_fold|full_model · check_thresholds_fixed · check_fold_selection · FoldTables memo · run's processed dir follows --out. The port still reproduces to 1e-12 in test/full_model. semantic_hash acfa22c6e4 is unchanged.
- ② atl_v0 0.4.0 (`d13c73e`): 50 controls, ALL WORLDS AGREE. Sabotage: with the rule removed, both negatives pass; with a bare required, null passes (the M-1c hole, reproduced). The mapping template pin → 0.4.0.
- ③ board v2 (`96acc3f`): v2 run → outputs/atlantis_core_v2 (deterministic on rerun). model/shap/whatif are byte-identical to v1's. Realised rates 0.0378 / 0.0811 / 0.1933. Lead 0.6818 → 0.6364. Fold tree counts range 63–623. atlantis_core 0.3.0. test_f8 covers (a)–(d). The index tests' "nothing landed" glob collided with a real day's entry, so they now use a sentinel date.
- Budget SITREP at ~235 kT (+50% line) → operator ruled **finish all** (AskUserQuestion).
- ④/⑤ site (`b8ff972`, `9d63dbe`): site_v2.yaml, the outputs key, --site, a conditional realised column; the v2 page is browser-checked in light and dark. **FINDING (self-caught):** the first copy and board note said the validation years "had more blooms", but they have FEWER onsets in count (121 vs 127); only the rate is higher (0.101 vs 0.077). The causal "so" was also unproven (selection model vs refit scale). v2 was regenerated in place (unpublished; recorded) with two likely reasons, neither proven.
- verify: 505 tests · SO-7 green (vitals and labels untouched) · exemplar 11 · BOARD/lattice/datasets checks · gitleaks over 5 commits exit 0 · nothing > 1 MB (page 0.85 MB).
- docs: core README §Known limits (items 1–2 fixed, residuals named) · schema README 0.4.0 (proof row, limit 13) · board README.
- III: fresh-context reviewer launched (read-only).
- III (fresh context): PASS-WITH-FINDINGS, 2 major + 6 minor. F-1: fold selection was checked against intent. F-2: lead time recorded no threshold. Both had passed every test; the reviewer broke them with plants in the real code. F-6 (horizon spill) → operator ruled: disclose now, embargo in its own lane. **All 8 addressed** (`4bda9b5`). My own first runtime fix for F-3 recomputed the thresholds it compared against; caught before the commit. Plants P1–P4 are now written into eval's source. v2 regenerated (unpublished, numbers unchanged). 516 tests · ALL WORLDS AGREE · SO-7 green. Local store: C-009 → 4, C-022, C-023.
- close: AAR · card completed · backlog (F-8) completed · horizon-embargo card · roster · charter · STATE (M-2a queued, self-contained prompt; WI-11 and WI-14 closed; WI-23 opened) · CHANGELOG v0.9.0.

## SITREP

- **Completed:** M-1e. **P2 condition (a) is MET.** Board v2 is the same model with honest budgets: thresholds fixed on validation, realised 3.8 / 8.1 / 19.3% at 5 / 10 / 20% nominal, lead time 0.636 of 22. Every fold selects on its own year. atl_v0 is 0.4.0, and the v2 page is built. III 8/8.
- **Next up:** **M-2a** (opus): the FKNMS fork, the CRW-via-ERDDAP check first. The prompt is in STATE.
- **Blockers (`#needs-human`):**
  - the **push** (7 commits; gitleaks exit 0 over the range; nothing over 1 MB);
  - where the **horizon embargo** lands (with M-2b, or its own lane before the P2 gate);
  - delivering the graduation memo into III.aDNA (carried; C-009 is now at frequency 4).
- **Files touched:**
  - `what/atlantis_core/` (eval · board · site · run · tests · README · 0.3.0);
  - `what/schema/atl_v0/` (0.4.0 + 5 controls);
  - `what/board/` (v2 · BOARD.md · README);
  - `what/exemplars/gulf_karenia_brevis/` (atlantis.yaml · outputs/atlantis_core_v2 · site_v2.yaml · site_copy_v2.yaml · site/gulf_karenia_brevis_v2.html);
  - `how/templates/template_mapping_atl.yaml`;
  - `how/backlog/` (two cards);
  - `how/federation/iii/` learning store;
  - the campaign card, AAR, roster and charter;
  - STATE and CHANGELOG.
- **Budget:** ≈370 kT main (plan-mode orientation included) + ≈260 kT reviewer, about +130% on the card. The SITREP was made at +50%, and the operator ruled to finish.

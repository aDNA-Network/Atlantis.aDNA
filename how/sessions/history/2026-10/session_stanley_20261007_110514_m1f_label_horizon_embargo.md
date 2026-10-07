---
type: session
created: 2026-10-07
updated: 2026-10-07
last_edited_by: agent_proteus
tags: [session, m1f, p2, eval, embargo, horizon, board_v3, atlantis, tidewatch]
session_id: session_stanley_20261007_110514_m1f_label_horizon_embargo
user: stanley
started: 2026-10-07T18:05:14Z
status: completed
completed: 2026-10-07
executor_tier: opus
mission: mission_m1f_label_horizon_embargo
campaign: campaign_atlantis_genesis
intent: "M-1f — embargo the label horizon at every split boundary (WI-23, M-1e III F-6, C-022) → board v3. Plan: ~/.claude/plans/please-read-the-claude-md-soft-shannon.md"
---

## Activity Log

- open — Rulings (operator, AskUserQuestion, 2026-10-07): (1) no v3 page — entry + docs; limitations_ref → core README §Known limits; (2) atl_v0 → 0.6.0 with an optional typed `AtlEvaluation.embargo_weeks`; (3) the final refit re-adds the train tail (each set embargoed only against the period it must not see).
- 1 measure (`eval.horizon_spill`, run on the exemplar's processed table, H = 4). **The III M-1e F-6 table reproduces exactly as `crossing_positives`** (positives whose window reads the next year): 6/28 · 3/41 · 6/27 · 9/67 · 1/27 · 4/11 · 0/67 · 10/31. A stricter count — positives that hold *only* by next-period signal — is 3 · 3 · 3 · 8 · 0 · 3 · 0 · 10. **Main split (measured for the first time):**
  - train→val (2016→2017): 25 / 7,971 rows cross; positives 3 / 920 cross, all 3 labelled by 2017 alone;
  - val→test (2019→2020, the rows the 141-tree early stop reads): 34 / 1,193 rows cross; positives 1 / 121 cross, 0 labelled by 2020 alone (the other 33 crossing rows are negatives whose "no crossing" reads early 2020).
  - **Finding:** the main-split spill is small by positives. The fold stop years carry most of it (2022: 10 / 31, all by 2023 alone). Negatives spill as well, which the III count did not show.
- ① eval (uncommitted so far): `split.embargo_weeks` (absent → H; `none`/0 → off; 0 < E < H, bool, float, negative refused). It applies at six boundaries: main selection-train → val, stop set → test, refit → test, and the same three per fold. The train tail is re-added for the refit. `check_label_windows` reads the event's H on the frames a FitRecorder received, now on the main path too. Val metrics are scored on the stop set; thresholds use every val week's scores. Climatology is fitted on the refit rows, and the sensitivity run is embargoed as well. Provenance `embargo` (boundaries · rows/positives dropped · latest window end · spill) is on the result and on each fold.
  - The **port with `none` reproduces v1 `metrics.json`** to 1e-12; **`none` reproduces v2 `metrics.json`**, every key, to 1e-12 (`test_none_reproduces_board_v2`, 62 s).
  - **Plants P5–P9** (stop set, fold selection-train, a window one week short, fold refit, main refit on full val) are each refused by name.
  - First look with the embargo on: 141 → 159 trees.
- ② hash: `semantic_hash` reads the resolved E (absent ≡ 4 ≡ explicit 4 ≠ none ≡ 0 = `acfa22c6e4`). The exemplar is now `7b789afded`, so its receipt must be re-earned.
- ③ atl_v0 0.6.0 (`f8fea56`): `AtlEvaluation.embargo_weeks` + 3 controls → 56, ALL WORLDS AGREE. **FINDING:** a REJECTS_ON starting with `-` was read as a grep option, so linkml-validate's unnamed-reason test was skipped (vacuous since 0.5.0). A sabotage passed in that world; fixed with `grep -e`, and the sabotage now reddens all three worlds.
- ④ board v3: `assert_embargo` (headline · swaps · folds; refuses missing/off/short/unchecked/crossing) · `embargo_extras` · `split_text` and `embargo_weeks` from the checked result · delta gains split/embargo_weeks/learner. **v3** (`2026-10-07_gulf_karenia_brevis_v3.json`): 146 trees (was 141), AUROC 0.8950 / AUPRC 0.5414 (was 0.8938 / 0.5388), lead 13/22 (was 14/22), config `7b789afded`; SHAP top-6 unchanged; no fold skipped. `limitations_ref` → the core README's known limits (no v3 page, per ruling).
  - The uncommitted v3 entry was re-emitted twice before any commit: once after the 0.5.0 version bump, and once after re-running v3 under 0.5.0, because the first run's `metrics.json` stamped `atlantis_core 0.4.0`, a string that also names the pre-embargo code (C-023). The re-run is deterministic, differing only in version, config bytes-md5 and run_at.
  - `assert_green` refused an extras key named `weeks` (FORBIDDEN, as a smuggled week list). It was renamed to `embargo_weeks`, so the guard worked.
- ⑤ docs: core README (eval/board rows · known limits intro · 1/2 residual figures → v3 · 2b fixed, measured, residuals) · exemplar README v3 pointer · M-2a-ii card (E = 8 default; Nov–Dec) · backlog → done. I caught myself writing "peak bleaching season" for Nov–Dec and "a bloom season" for December; both are unverified, and both were corrected before commit.
- SITREP at the +50% line (~240 kT main); operator ruled (AskUserQuestion): **finish all**, III then close.
- ⑥ III fixes (`fd95cdd`): PASS-WITH-FINDINGS, 0 major, 7/7. The reviewer independently confirmed the boundary is exact, v3 re-derives, and the swap reproduces v2 under `none`. v3 was re-run (numbers identical; `sensitivity.embargo` added) and the never-pushed entry regenerated (recorded). 636 tests. ACCUMULATE `1d9ee84`.
- close: AAR · card completed · roster · charter · STATE (WI-23 closed; M-2a-ii queued with a self-contained prompt) · CHANGELOG v0.11.0.

## SITREP

- **Completed:** M-1f, the label-horizon embargo → board v3 (146 trees; AUROC 0.8950 / AUPRC 0.5414, base rate 0.0774; `none` ≡ v2). Also atl_v0 0.6.0, atlantis_core 0.5.0, and III 7/7.
- **In progress:** none.
- **Next up:** M-2a-ii (opus), the FKNMS fork and fetch, with three steward rulings (zoning version, OSTIA licence, posture ratification).
- **Blockers (`#needs-human`):**
  - the push of `4d812f9..HEAD` (outward; gitleaks first);
  - delivering the graduation memo (C-004 · C-005 · C-009 · C-015 · C-023) to III.aDNA, a peer-vault write.
- **Files touched:**
  - `what/atlantis_core/src/atlantis_core/{eval/__init__,config,conform,selftest,board/__init__,__init__}.py` and tests (`test_embargo`, `test_embargo_perturbation`, `test_f8`, `test_eval`, `test_registry`, `test_conform`, `test_board_index`, `test_mapping_template`);
  - `what/schema/atl_v0/*` (0.6.0, 3 controls, runner);
  - `what/board/{BOARD.md, entries/…_v3.json}` · `what/exemplars/gulf_karenia_brevis/{atlantis.yaml, README.md, outputs/atlantis_core_v3/}`;
  - `how/templates/{template_mapping_atl.yaml, template_instance/atlantis.yaml.tmpl}`;
  - the docs, card, roster, charter, STATE, CHANGELOG, backlog and learning store.
- **Next Session Prompt:** in STATE § ⏭ QUEUED (M-2a-ii, open at opus).
- **Budget:** ≈ 300 kT main (≈ +76% on the card's top; SITREP at +50%, operator ruled finish all) + ≈ 240 kT reviewer.

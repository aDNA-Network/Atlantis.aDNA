---
type: backlog
doc_id: idea_eval_thresholds_fixed_on_validation
title: "Fix alert thresholds and rolling-fold tree counts on validation, not on the years they score (M-1b-ii-a III F-8)"
status: completed   # M-1e, 2026-10-03 → board v2
priority: high
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
origin: mission_m1b_ii_a_core_eval_explain_board
tags: [backlog, eval, thresholds, so9, atlantis_core, atlantis]
---

# Thresholds fixed beforehand

**What.** `atlantis_core.eval` inherits two after-the-fact choices from `hab.train`. The M-1b-ii-a review (III F-8)
named them. The operator ruled on 2026-10-02 to disclose them now and fix them later. Both are disclosed in
`what/atlantis_core/README.md` §Known limits of eval and explain, and in board v1's notes.

1. **Alert-budget thresholds** are quantiles of the *test* scores: alert on the top r of this year's own scores. Lead time
   reads the same threshold. A steward has to set the threshold *beforehand*. The honest version fixes it on validation
   scores (or the previous fold's) and reports the **realised** alert rate on test beside the nominal one.
2. **Rolling folds testing 2017–2019** reuse the full model's `n_trees`, which was early-stopped on 2017–2019. The honest
   version early-stops each fold on its own inner validation year, or fixes the tree count from data before the fold.

**Why it matters.** The thresholds are the numbers a steward would staff against (T6). Choosing them after the fact
flatters precision at a budget, by an amount nobody has measured yet.

**Shape of the fix.**
- `eval.threshold_from: val | test`, defaulting to `val`. Report realised vs nominal rates.
- Per-fold early stopping.
- Land the result as a **new board version** with the delta named. This changes every budget and lead number, so it must
  not be mixed with another cause.
- Port equivalence keeps a `test` mode so that `hab` stays reproducible.

**When.** Before any steward-facing budget claim, and no later than the P1 gate's evaluation review. It is natural
alongside M-1d's BOARD generator, or as its own small lane. The operator decides.

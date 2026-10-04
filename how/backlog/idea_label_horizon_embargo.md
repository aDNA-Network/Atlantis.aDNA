---
type: backlog
doc_id: idea_label_horizon_embargo
title: "Embargo the label horizon at every split boundary (M-1e III F-6) → its own board version"
status: proposed
priority: medium
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
origin: mission_m1e_eval_thresholds_on_validation
tags: [backlog, eval, leakage, split, horizon, so9, atlantis_core, atlantis]
---

# Embargo the label horizon at every boundary

**What.** A week's label reads the H weeks after it (H = 4 in the exemplar). So the last H weeks of any training or stopping
set are labelled by onsets in the period that follows it. The M-1e review (III F-6) measured this at the rolling folds' inner
stop years:

| Inner stop year | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|---|---|
| Positives labelled by the next year | 6/28 | 3/41 | 6/27 | 9/67 | 1/27 | 4/11 | 0/67 | 10/31 |

The main split has the same porosity **by construction (not yet measured there)**. Late-2016 train rows can be labelled
by 2017 (validation) onsets, and late-2019 validation rows by 2020 (test) onsets, which the headline's 141-tree early stop
reads. Measure it first, with the review's method, at each main boundary.

The F-8 checks test **calendar years**, which is a proxy (the C-018 class). Alert thresholds are unaffected, because they are
quantiles of scores, not labels.

**Operator ruling (2026-10-03, M-1e):** disclose now and fix in its own lane. The disclosure is on README §Known limits 2b, on
the v2 page's limits, and on board v2's notes. The fix lands as **a new board version**, because it moves the headline model
(the tree count, and so every number). Folded into v2, it would have given that delta a second cause.

**Shape of the fix.**
- Add `split.embargo_weeks` (default = the event horizon). Drop each fit or stop set's last H weeks before the next period
  begins. This applies to train→val, val→test, and each rolling fold's train→stop and stop→test.
- The check reads label windows, not row years: for each row in a fit or stop set, the label window t+1…t+H must end before
  the next period starts. Plant a row whose window crosses, and watch it fail by name (C-009).
- Keep a `none` mode, so that v2 reproduces exactly (port equivalence, as at M-1e).
- Board v3 is emitted by code, with the delta attributed to the embargo alone. Expect the tree count, AUROC/AUPRC and the
  budgets all to move.

**When.** It goes before any steward-facing claim that rests on the early-stopped model's numbers, and before the P2 gate
compares the exemplar with the FKNMS instance on the board. The operator decides whether it rides with M-2b or runs as its
own small lane.

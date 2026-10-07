---
type: mission
mission_id: M-1f
plan_id: mission_m1f_label_horizon_embargo
title: "M-1f — embargo the label horizon at every split boundary (WI-23 · M-1e III F-6) → board v3"
owner: stanley
status: completed
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P2
campaign_phase: 2
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~120-170kT main + fresh-context III reviewer (P1's eval lanes ran +77% to +130%)"
token_budget_actual: "≈ 300kT main (≈ +76% on the top; SITREP at +50%, operator ruled finish all) + ≈ 240kT III reviewer"
depends_on: ['M-2a-i']
origin: how/backlog/idea_label_horizon_embargo.md
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1f_label_horizon_embargo.md
session: session_stanley_20261007_110514_m1f_label_horizon_embargo
created: 2026-10-06
updated: 2026-10-07
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1f, p2, opus, eval, leakage, split, horizon, embargo, board_v3, atlantis_core, atlantis, tidewatch]
---

# M-1f: the label-horizon embargo, in its own lane

**Placed 2026-10-06 by the operator** (AskUserQuestion, M-2a planning): its own lane **between M-2a-i and M-2a-ii**.
An embargo is a split change, and a split change invalidates a self-test receipt. Landing it before the fork means
`FloridaKeysCoral.aDNA` is born with it, and FKNMS's H = 8 spill is twice the exemplar's. The shape of the fix is in the
backlog card: `how/backlog/idea_label_horizon_embargo.md`.

## Acceptance criteria

- [x] **Measure first.** Count, at each main boundary (train→val, val→test), the positives labelled by the next period,
      with the M-1e reviewer's method
- [x] `split.embargo_weeks`, defaulting to the event horizon, plus a `none` mode. It drops the last H weeks of every fit or
      stop set before the next period: main split and every rolling fold
- [x] A check that reads **label windows**, not row years. A planted crossing row fails by name in the real code path (C-009)
- [x] `none` reproduces board v2 exactly (port equivalence)
- [x] **Board v3**, emitted by code, with the delta attributed to the embargo alone (tree count, AUROC/AUPRC, budgets, lead).
      Any atl_v0 change gets its controls, and ALL WORLDS AGREE
- [x] The exemplar's README §Known limits 2b is updated. A v3 page only if the operator rules one. WI-23 closed
- [x] III review via `iii/`, in a fresh context; AAR; queue M-2a-ii

## Guardrails

SO-2 (board v2 is published, so a correction is a new version) · SO-7 · SO-9 · C-009 · C-018 (a proxy check is a finding) ·
C-023 · budget > +50% → SITREP and ask.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

**Completed 2026-10-07.** Board v3 (`what/board/entries/2026-10-07_gulf_karenia_brevis_v3.json`) · atl_v0 0.6.0 · atlantis_core 0.5.0 · III 7/7 · AAR → `aar_path`.

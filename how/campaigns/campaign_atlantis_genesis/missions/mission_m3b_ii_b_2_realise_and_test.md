---
type: mission
mission_id: M-3b-ii-b-2
plan_id: mission_m3b_ii_b_2_realise_and_test
title: "M-3b-ii-b-2 — reef-light wind realised as AtlVitals in FKNMS, the calm threshold scanned on val, trained, SHAP-tested, written up either way · T7/T8 re-cut"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "main ≈ 200 kT (+50% line ≈ 300 kT) · fresh-context III reviewer ≈ 250 kT"
token_budget_actual: ""
depends_on: ['M-3b-ii-b-1']
split_from: mission_m3b_ii_b_realise_and_test
origin: "M-3b-ii-b ruling 3 (operator, AskUserQuestion, 2026-10-15, at open): core / realise + test"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_ii_b_2_realise_and_test.md
session: TBD
created: 2026-10-15
updated: 2026-10-15
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_ii_b_2, p3, opus, shap, realisation, fknms, t7, t8, atlantis, tidewatch]
---

# M-3b-ii-b-2 — realise reef-light wind and test it

**Split from** `mission_m3b_ii_b_realise_and_test.md` (ruling 3). It inherits that card's ruled calm threshold, its
acceptance criteria and obligations 2–5 and 7–8. **Obligation 6 is ruled** (rulings 1–2 there), and M-3b-ii-b-1 built
it. **Obligation 1 is met by ii-b-1**: scan with `atlantis_core.scan --constant calm_threshold --values 2,3,4,5,6`; it
never scores test.

**Also at open:**
- Read the ruled index's descriptive calm-share table and SANF1-only table in FKNMS STATE before reading any SHAP
  "support".
- v4 is written under the receipt hash ii-b-1 recorded, not `81bca06518`.
- The SANF1-only sensitivity is a second run, reported beside v4 and not on the board as a separate entry, unless ruled.

See the parent card for the full acceptance list.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

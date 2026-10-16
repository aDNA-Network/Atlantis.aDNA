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
- **v4's hash (III ii-b-1 F-8):** v4 is written under the hash of the config ii-b-2 declares (the vitals plus the
  chosen c), with a fresh receipt. Each scanned c has its own hash. The receipt ii-b-1 recorded is the declaration-only
  receipt; it is not v4's.
- **Self-test before the scan (III ii-b-1 F-1):** run the self-test with the wind vitals declared, before any scan. Core
  0.11.1's calm world holds calm days in every season, and C0w fails a calm-less week as a *world fault*. **Never move
  `selftest.week` to make C0 pass.** If the week must move, the operator rules it, with the reason.
- **Rulings 4–5 and 7:** the ruled index and the SANF1-only sensitivity both start SANF1 at **2007-08-01**. The offsets
  are fitted on **2007–2012**, ending before the first fold's stop year (III ii-b-1 F-6). The mask reads
  **`qc_low_ratio_causal`**. FKNMS STATE has the table and the numbers.
- **Recorded limits the write-up must disclose:**
  - **(a)** SANF1's break develops from Oct 2006 and completes after its Apr–May 2007 outage. In steady state it is
    ≈ 0.15–0.3 m/s larger Oct–Mar than Apr–Sep, so an additive offset is approximate (III F-2).
  - **(b)** A second shift sits in test: LONF1−SANF1 ≈ −1.4 in 2008–17 and ≈ −0.9 in 2021–25. Only these two lights
    report there, so it cannot be attributed or corrected without reading test.
  - **(d)** **SANF1's level moves at its outages**, not once:
    - the 2006–07 break;
    - lower in 2014–15, after its 2013 gap;
    - back by 2016–17.

    Under the ruled offsets the residual against SANF1 is 0 in train by construction, **≈ +0.3 m/s for all three
    lights in val** (+0.33 / +0.26 / +0.31), and **+0.58** for LONF1 in test. A constant offset cannot follow this,
    and a time-varying one would read val.
  - **(e)** The ruled index sits on post-2007 SANF1's scale, ≈ +0.7 m/s above the unmasked mean. The calm share is
    3.9 / 4.3 / 5.3% at c = 3 and 14.0 / 16.2 / 16.4% at c = 4. The rulings remove most of the unmasked rise, not all
    of it (III F-3). The ruled grid c ∈ {2…6} is read on that scale, and c = 2 will be sparse. Say so beside the scan
    table.
  - **(g)** The causal mask misses the first 6 days of the LONF1 2020 failed-anemometer fault (2020-02-27 → 03-03, in
    test). Those days enter the index as calm days (III F-5).
  - **(f)** **The preprocessing was ruled on the full record (III ii-b-1 F-4).** Station QC, windows and offsets
    (rulings 1, 2, 4, 5) were ruled after inspecting the wind record over train, val and test. The inspection was
    label-blind: no model output or score was read. The test score is not independent of these choices. This goes
    into v4's `limitations_ref` and the write-up.
  - **(c)** The val→test edge is by ISO week. The last val week holds 1–5 Jan of the first test year, and a val row's
    label can read them. This is pre-existing in `run`, and the scan inherits it.
- The SANF1-only sensitivity is a second run, reported beside v4 and not on the board as a separate entry, unless ruled.

See the parent card for the full acceptance list.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

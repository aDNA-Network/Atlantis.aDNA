---
type: artifact
doc_id: mission_roster_p1_p5
title: "Mission roster P1–P5 — Operation Tidewatch, re-chartered to the five layers (M-0 output)"
status: active
created: 2026-10-02
updated: 2026-10-06
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
tags: [artifact, roster, missions, tidewatch, atlantis, m0]
---

# Mission roster P1–P5

Nine cards, two tiers (fleet pattern `pattern_model_tiered_campaign_execution`): **opus** for briefed build lanes,
**fable** for the planning/ratification sitting (M-4) and for **every phase-exit gate** (not carded — the gate is the
operator's act, rendered by `skill_create_iss.md` or `AskUserQuestion`). Budgets are estimates per ADR-016; actuals
go in each card's `token_budget_actual` at close.

| ID | Title | Phase | Tier | Budget | Depends on | Card |
|---|---|---|---|---|---|---|
| M-1a | Exemplar hygiene — doc/config drift, provenance hashes, packaging, safe region parser | P1 | opus | 40-60kT | M-0 | `missions/mission_m1a_exemplar_hygiene.md` |
| ~~M-1b~~ | `what/atlantis_core/` — extract the reference implementation: stream registry, feature registry, direction-aware label, all-stream self-test, board emitter | P1 | opus | 120-180kT | M-1a | `missions/mission_m1b_atlantis_core_extraction.md` — **superseded 2026-10-02, split ↓** |
| M-1b-i | `atlantis_core` skeleton: registries · fetch (3 real + 3 declared) · grid · vitals · direction-aware label · all-stream self-test | P1 | opus | ~140kT + reviewer | M-1a, M-1c | `missions/mission_m1b_i_core_vitals_and_selftest.md` |
| ~~M-1b-ii~~ | `atlantis_core` eval · explain · board · site · metrics reproduction · learner swap · mapping · `src/hab/` archived | P1 | opus | ~140kT + reviewer | M-1b-i | `missions/mission_m1b_ii_core_eval_explain_board.md` — **superseded 2026-10-02, split ↓** |
| M-1b-ii-a | `atlantis_core` eval · explain · board · R7 refit · board v1 · semantic hash · logistic learner swap | P1 | opus | ~160kT + reviewer | M-1b-i | `missions/mission_m1b_ii_a_core_eval_explain_board.md` |
| M-1b-ii-b ✅ 2026-10-03 | `atlantis_core` site template (all copy parameterised) · `template_mapping_atl.yaml` · `src/hab/` archived | P1 | opus | ~150kT + reviewer | M-1b-ii-a | `missions/mission_m1b_ii_b_site_mapping_archive.md` |
| M-1c | `atl_v0` controls — fixtures, `run_controls.sh`, committed JSON Schema, vocabulary fit matrix | P1 | opus | 60-90kT | M-0 | `missions/mission_m1c_linkml_controls.md` |
| ~~M-1d~~ | *split 2026-10-03 (operator ruling) → M-1d-i + M-1d-ii; card kept as superseded* | P1 | — | — | — | `missions/mission_m1d_fork_skill_and_registries.md` |
| M-1d-i ✅ | Fork from templates alone: atl_v0 0.3.0 · contract v0.2.0 · fetch CLI gated on the self-test · instance templates · `atlantis_core.fork` + `conform` · `skill_atlantis_instance_fork` · dry run | P1 | opus | ~110-130kT | M-1b-ii-b, M-1c | `missions/mission_m1d_i_fork_and_conformance.md` |
| M-1d-ii ✅ | Pipeline lattice + runspec · BOARD generator (WI-8) · dataset-pair migration · contribution guide · `board --entries` | P1 | opus | ~80-100kT (actual ≈177) | M-1d-i | `missions/mission_m1d_ii_lattice_and_registries.md` |
| M-1e ✅ | **P2 condition (a):** alert thresholds and rolling-fold tree counts fixed on validation (F-8 / WI-11) → board v2 · atl_v0 0.4.0 · v2 page | P1 | opus | ~110-160kT (actual ≈370 + III ≈260) | M-1d-ii | `missions/mission_m1e_eval_thresholds_on_validation.md` |
| ~~M-2~~ | *re-carded 2026-10-03 (P1-gate condition (b)) → M-2a + M-2b; card kept as superseded* | P2 | — | — | — | `missions/mission_m2_fknms_coral_instance.md` |
| ~~M-2a~~ | *split 2026-10-06 (operator ruling, M-2a planning) → M-2a-i + M-1f + M-2a-ii; condition (c) MET (CRW via `ERDDAPGriddap` on coastwatch.noaa.gov); card kept as superseded* | P2 | — | — | — | `missions/mission_m2a_fknms_fork_and_fetch.md` |
| M-2a-i ✅ 2026-10-06 | atlantis_core for a persistent, polygon, gridded instance: CRW authority · grid sha256 pin · onset refractory · persistent self-test world (whole catalogue) · `CoralReefWatch` polygon fetcher · fork-skill Hestia step | P2 | opus | ~180-220kT + reviewer (actual ≈345 + III ≈235) | M-1e | `missions/mission_m2a_i_core_for_persistent_polygon_instances.md` |
| ~~M-1f~~ ✅ 2026-10-07 | Label-horizon embargo at every split boundary (WI-23) → **board v3** (146 trees; 0.8950 / 0.5414; `none` ≡ v2); atl_v0 0.6.0; III 7/7 | P2 | opus | ≈ 300kT + reviewer | M-2a-i | `missions/mission_m1f_label_horizon_embargo.md` |
| M-2a-ii ✅ | *completed 2026-10-08: forked · ADR-001 ratified · three CRW streams 1985–2025 fetched (15-day union spans) · conforms (fetched) · III 9/9 · core 0.5.1 → 0.5.3* — `FloridaKeysCoral.aDNA`: interview · fork · zone geometry (pointer + sha256) · posture + licence ruling · receipt · ratify · fetch · conform (fetched) · Hestia memo | P2 | opus | ~120-160kT + reviewer | M-2a-i, M-1f | `missions/mission_m2a_ii_fknms_fork_and_fetch.md` |
| M-2b | `FloridaKeysCoral.aDNA`: train · eval (thresholds on validation) · explain · instance page · board entry by memo → P2 gate | P2 | opus | ~150-200kT | M-2a-ii | `missions/mission_m2b_fknms_model_and_board.md` |
| M-3a | `skill_stream_discovery` — playbook §A as a runnable skill with the traps as checks | P3 | opus | 40-60kT | M-1d | `missions/mission_m3a_stream_discovery_skill.md` |
| M-3b | Hypothesis ledger populated + `skill_feature_hypothesis_mining` + one literature-asserted driver tested by SHAP | P3 | opus | 100-150kT | M-2, M-3a | `missions/mission_m3b_hypothesis_ledger_and_mining.md` |
| M-4 | Instance contract v1, steward governance set, consumer register, Exchange listing, first outside steward | P4 | fable | 90-140kT | M-2, M-3b | `missions/mission_m4_federation_and_stewards.md` |
| M-5 | Retrain + drift skill, Ray workload request template, campaign AAR | P5 | opus | 50-80kT | M-4 | `missions/mission_m5_steady_state.md` |

**Totals:** 8 opus lanes ≈ 640–1,020 kT · 1 fable sitting (M-4) ≈ 90–140 kT · 5 fable gates (uncarded, ~20–40 kT each).
Calibrated campaign estimate: **12–18 sessions** (seed said 8–14 for the narrower remit).

## Phase exit bars (verbatim from the charter)

- **P1:** a fresh instance forks from templates alone, in one sitting, with its self-test green before any real data is fetched; `atlantis_core` reproduces the exemplar's metrics; `atl_v0` controls pass under both validators; III review via wrapper. **Operator GO.**
- **P2:** `FloridaKeysCoral.aDNA` trained + explained + paged + on the board **without editing Atlantis code**; every deviation became a P1 template change. **Operator GO.**
- **P3:** one instance's vitals extended from the hypothesis ledger with provenance; ≥ 1 literature-asserted driver tested by SHAP and written up either way. **Operator GO.**
- **P4:** an instance built by someone who was not in this campaign, from the public repo alone, lands a board entry; contract v1 ratified. **Operator GO.**
- **P5:** retrain/drift skill exists and ran once; campaign AAR; successor cards filed. **Campaign close.**

## Critical path

M-0 ✅ → M-1a ✅ → M-1b-i ✅ → M-1b-ii-a ✅ → M-1b-ii-b ✅ → M-1d-i ✅ → M-1d-ii ✅ → **P1 gate ✅ (conditional GO)** → M-1e ✅ → M-2a-i ✅ → M-1f ✅ → M-2a-ii ✅ → M-2b ⏭ → **P2 gate** → M-3b → **P3 gate** → M-4 → **P4 gate** → M-5.
M-1c runs beside M-1a/M-1b; M-3a beside M-2.

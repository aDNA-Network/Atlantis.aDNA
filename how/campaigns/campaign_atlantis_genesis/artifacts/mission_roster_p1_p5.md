---
type: artifact
doc_id: mission_roster_p1_p5
title: "Mission roster P1–P5 — Operation Tidewatch, re-chartered to the five layers (M-0 output)"
status: active
created: 2026-10-02
updated: 2026-10-02
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
| M-1b | `what/atlantis_core/` — extract the reference implementation: stream registry, feature registry, direction-aware label, all-stream self-test, board emitter | P1 | opus | 120-180kT | M-1a | `missions/mission_m1b_atlantis_core_extraction.md` |
| M-1c | `atl_v0` controls — fixtures, `run_controls.sh`, committed JSON Schema, vocabulary fit matrix | P1 | opus | 60-90kT | M-0 | `missions/mission_m1c_linkml_controls.md` |
| M-1d | `skill_atlantis_instance_fork` + pipeline lattice + dataset-pair migration + contribution guide + BOARD generator | P1 | opus | 80-120kT | M-1b, M-1c | `missions/mission_m1d_fork_skill_and_registries.md` |
| M-2 | First MPA instance — `FloridaKeysCoral.aDNA`: FKNMS zones × week, degree-heating-weeks onset, gridded-only vitals, no Atlantis code edits | P2 | opus | 150-220kT | M-1d | `missions/mission_m2_fknms_coral_instance.md` |
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

M-0 ✅ → M-1a → M-1b → M-1d → **P1 gate** → M-2 → **P2 gate** → M-3b → **P3 gate** → M-4 → **P4 gate** → M-5.
M-1c runs beside M-1a/M-1b; M-3a beside M-2.

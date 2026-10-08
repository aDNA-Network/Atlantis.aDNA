---
type: mission
mission_id: M-3b
plan_id: mission_m3b_hypothesis_ledger_and_mining
title: "M-3b — Hypothesis ledger populated + `skill_feature_hypothesis_mining` + one literature-asserted driver tested by SHAP"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "≈ 350 kT main + fresh-context III reviewer ≈ 200 kT (re-carded at the P2 gate 2026-10-08: 100-150kT × 2.3, III G-10). Likely splits at its planning sitting (SO-8); the split is the operator's call"
token_budget_actual: ""
depends_on: ['M-2c', 'M-3a']   # M-2c added by P2-gate condition (a)
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_hypothesis_ledger_and_mining.md
session: TBD
created: 2026-10-02
updated: 2026-10-08
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b, p3, opus, atlantis, tidewatch]
---

# M-3b — Hypothesis ledger populated + `skill_feature_hypothesis_mining` + one literature-asserted driver tested by SHAP

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P3 — Knowledge lane ·
**Tier:** opus · **Budget:** ≈ 350 kT + reviewer (re-carded at the P2 gate) · **Depends on:** M-2c, M-3a · **Target ruled at the P2 gate (condition (c)):** FKNMS or a new instance, not the exemplar

## Objective

Make the literature a registry, not prose: populate `what/hypotheses/ledger/` for one ecosystem type from a real corpus, realise ≥ 1 row as a vital in an instance, test it with SHAP, and write it up either way (T8).

## Acceptance criteria

- [ ] Corpus via `Ingest.aDNA` (compose; OpenAlex / Semantic Scholar / Europe PMC + agency bulletins) — or a documented standalone fetch if Demeter's intake is not ready for literature; `unreviewed/` discipline either way
- [ ] `how/skills/skill_feature_hypothesis_mining.md`: paper → row (extraction target fixed by `what/hypotheses/README.md`); every row points at a sentence; tiers draft → reviewed
- [ ] ≥ 25 rows for one ecosystem type; index regenerated. **The target is FKNMS (coral DHW drivers) or a new instance** (P2 gate, 2026-10-08, condition (c), III G-8). A literature driver realised on the exemplar would put new bytes into Atlantis (SO-3, ADR-002 §4), so the exemplar is allowed only for a driver derivable from its three grandfathered parquets. *(Was: "coral DHW drivers for FKNMS, or* K. brevis *drivers for the exemplar — ruled at M-3b open".)*
- [ ] ≥ 1 row realised as an `AtlVital` (`hypothesis_ref` set) in an instance, trained, SHAP-tested; `realisation.result` filled; write-up as a memo + board entry v1 — **supported or not, it is written**
- [ ] ENVO binding revisited (crosswalk deferred row) for `ecosystem_type`
- [ ] Thesis T7 T8 re-cut. On FKNMS, T7's honest outcome may be "no lever, still" (P2 ruling); a driver that turns out to be a proxy is written up as one
- [ ] *(P2 gate, C-033)* Before the AAR, re-read the register for any obligation it gives M-3b or P3. Each one is carried, dropped or recorded
- [ ] Every comparison with the M-2c board entry is read at the same base rate and budget (C-031, C-034); there are no cross-base-rate AUPRC deltas
- [ ] III review via `iii/` in a fresh context; SITREP at the +50% line

## Guardrails

- **SO-1:** this mission opens only after the previous phase's operator GO; it never advances the phase itself.
- **SO-3 / ADR-002 §4:** no new data snapshots in Atlantis; instance data stays in the instance; credentials by name only.
- **SO-7:** any change to vitals or label re-runs the self-test before commit.
- **SO-4:** nothing produced here is an operational forecast; `claim: method_demonstration` unless an owner ruling is cited.
- Public repo: everything committed is publishable; path-scoped `git add`; `gitleaks` on push.
- Peer vaults read-only; cross-graph needs go as coordination memos.

## Verification surface

The acceptance checklist above, each item checked by a command or a file the AAR names; the self-test output;
`linkml-validate` on every registry touched; the board entry diffed against `outputs/metrics.json` by script.

## Escalation triggers

- A deviation that would require editing `atlantis_core` from inside an instance (P2) → stop, file the template change, do not patch locally.
- A stream whose licence or posture is unclear → stop, memo to the instance owner; nothing fetched.
- Budget exceeded by > 50% → SITREP and stop; re-card.
- Anything that would put observations, labels, predictions or partner coordinates into Atlantis → stop.

## Files

- `what/hypotheses/ledger/<ecosystem>/*.yaml · how/skills/skill_feature_hypothesis_mining.md · an instance's features.yaml · what/board/entries/*_v1.json`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

---
type: mission
mission_id: M-1b
plan_id: mission_m1b_atlantis_core_extraction
title: "M-1b — `what/atlantis_core/` — extract the reference implementation: stream registry, feature registry, direction-aware label, all-stream self-test, board emitter"
owner: stanley
status: superseded
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "120-180kT"
token_budget_actual: ""
depends_on: ['M-1a']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_atlantis_core_extraction.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
superseded_by: [mission_m1b_i_core_vitals_and_selftest, mission_m1b_ii_core_eval_explain_board]
tags: [mission, m1b, p1, opus, atlantis, tidewatch]
---

> ⛩ **Superseded 2026-10-02 — split by operator ruling** (after M-1c AAR Finding 4: ≈5× card). Scope carried whole into
> `mission_m1b_i_core_vitals_and_selftest.md` (registries · fetch · grid · vitals · label · all-stream self-test) and
> `mission_m1b_ii_core_eval_explain_board.md` (eval · explain · board · site · metrics reproduction · learner swap · mapping · archive `src/hab/`).
> Fetch scope ruled: 3 real (ArcGIS · ERDDAP · NWIS) + 3 declared stubs (NDBC · OBIS/GBIF · CRW). Kept, not deleted (SO-2).

# M-1b — `what/atlantis_core/` — extract the reference implementation: stream registry, feature registry, direction-aware label, all-stream self-test, board emitter

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P1 — Core canonisation ·
**Tier:** opus · **Budget:** 120-180kT · **Depends on:** M-1a

## Objective

Turn the exemplar's `src/hab/` into an installable, instance-agnostic package whose behaviour is declared in registries (`streams.yaml` · `features.yaml` · `events.yaml`) validated against `atl_v0`, and make the exemplar its first consumer with identical outputs.

## Acceptance criteria

- [ ] `what/atlantis_core/` is a `pyproject` package (`atlantis_core`): `fetch/` (pluggable fetchers: ArcGIS MapServer · ERDDAP griddap · NWIS · NDBC · OBIS/GBIF · CRW; each writes `observation_long` + Rule-5 provenance + sha256) · `grid/` (patient grid from coordinate **rules**, **polygons/WDPA geometry files**, or grid cells) · `vitals/` (feature registry → vitals table) · `label/` (direction `above|below`; both drop counts reported) · `eval/` (budgets · lead time · calibration · ablations · climatology · rolling origin) · `explain/` (interventional SHAP + tags) · `board/` (emits `atl_board_entry_v1`) · `site/` (template with **all copy parameterised**)
- [ ] `features.yaml` replaces `FEATURE_GROUPS` + `FEATURE_DOC`: every vital carries group · tag · lag · window · transform · stream_ref (an `AtlVital` list); `gauges.lever` → `owner`
- [ ] **All-stream self-test:** perturbs *every* registered stream at t+1 (counts, SST, discharge, …) and asserts no vital at t moves, the label does, t+horizon+1 moves nothing; runs on synthetic data with no network
- [ ] Alert budgets, climatology window, lag sets, what-if scenarios, site cases are config, not literals
- [ ] Exemplar re-run through `atlantis_core` reproduces `metrics.json` within float noise (AUROC/AUPRC to 3 dp; same n, positives, drop counts); the old `src/hab/` is archived in place with a pointer (SO-2)
- [ ] A `mapping.yaml` template projects an instance's registries to the five `atl_` labels with bi-temporal stamps and a fence excluding raw observations (Organization §2 / Neo4j N4-MODEL shape)
- [ ] Learner is a config field; one swap (e.g. LightGBM or logistic) run on the exemplar's vitals and recorded — T2 evidence

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

- `what/atlantis_core/** · what/exemplars/gulf_karenia_brevis/{streams,features,events}.yaml · how/templates/template_mapping_atl.yaml`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

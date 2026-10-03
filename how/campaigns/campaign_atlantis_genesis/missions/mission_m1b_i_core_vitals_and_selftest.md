---
type: mission
mission_id: M-1b-i
plan_id: mission_m1b_i_core_vitals_and_selftest
title: "M-1b-i — `atlantis_core` skeleton: registries, fetch (3 real + 3 declared), grid, vitals, direction-aware label, all-stream self-test"
owner: stanley
status: completed
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "~140kT main + fresh-context III reviewer (~80-120kT)"
token_budget_actual: "~240kT main (≈ +70%; SITREP at trip, operator ruled fix-all) + ~172kT fresh-context III reviewer"
depends_on: ['M-1a', 'M-1c']
split_from: mission_m1b_atlantis_core_extraction
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_i_core_vitals_and_selftest.md
session: session_stanley_20261003_014043_m1b_i_core_vitals_selftest
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1b_i, p1, opus, atlantis_core, selftest, atlantis, tidewatch]
---

# M-1b-i — `atlantis_core` skeleton: registries, fetch, grid, vitals, label, all-stream self-test

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P1 · **Tier:** opus ·
**Split from:** `mission_m1b_atlantis_core_extraction.md` (operator ruling 2026-10-02, after M-1c AAR Finding 4) ·
**Sibling:** `mission_m1b_ii_core_eval_explain_board.md`.

## Objective

Stand up `what/atlantis_core/` as an installable package whose vitals and label are declared in `AtlDocument` registries,
and prove it on the exemplar: the registries reproduce `hab.build_features`' tables **identically**, and the self-test
perturbs **every** registered stream. `src/hab/` stays the exemplar's canonical pipeline until M-1b-ii reproduces `metrics.json`.

## Acceptance criteria

- [x] `what/atlantis_core/` is a `pyproject` package (`atlantis_core`) with `config` (incl. `semantic_hash`, recorded at M-1b-ii) · `registry` (loads `AtlDocument`s, cross-reference checks)
- [x] `fetch/`: one `Fetcher` interface (offline, retry, atomic writes, instance cache dir) + Rule-5 provenance (sha256); **real:** ArcGIS MapServer · ERDDAP griddap · NWIS (ported); **declared stubs:** NDBC · OBIS/GBIF · CRW (endpoint named, `NotImplementedError`) — operator ruling
- [x] `grid/`: patient units from coordinate **rules** (`ast` whitelist), **polygon files** (GeoJSON/WDPA the instance points at; numpy, no shapely) or **grid cells**; unit × ISO-week grid; the 9 frozen exemplar region counts hold
- [x] `vitals/`: a transform registry (whitelisted call grammar in `AtlVital.transform`); `features.yaml` replaces `FEATURE_GROUPS` + `FEATURE_DOC`; `gauges.lever` → `owner`; climatology windows, lag sets and windows are config
- [x] `label/`: `direction: above|below`; both drop counts reported
- [x] **All-stream self-test** (synthetic, no network): every registered stream perturbed at t+1 → no vital at t moves; the label moves iff the perturbed stream is the event stream; t+H+1 moves nothing; a `below` event exercised; the training-era-climatology dependence reported, not hidden
- [x] Exemplar `streams.yaml` · `features.yaml` · `events.yaml` validate under `linkml-validate -C AtlDocument`; `run_controls.sh` still ALL WORLDS AGREE
- [x] **Equivalence:** `atlantis_core` on the three committed raw parquets reproduces `region_week_all` + `features` frames (same rows, same 25 columns, NaN-aware allclose) and `features_report.json` exactly
- [x] `config.yaml` + `metrics.json` byte-stable; `hab.build_features --self-test` still green
- [x] III review via `iii/` in a fresh context (SO-10), scoped to the invariant

## Guardrails

SO-1 · SO-3 (no new snapshots; nothing fetched) · SO-7 (self-test before any vitals/label commit) · SO-4 · public repo, path-scoped
`git add` · budget >50% over → SITREP and stop (M-1c Finding 4).

## Files

`what/atlantis_core/** · what/exemplars/gulf_karenia_brevis/{streams,features,events,atlantis}.yaml`

## AAR

**Filed 2026-10-02:** `missions/aar/aar_m1b_i_core_vitals_and_selftest.md`. Equivalence is exact except the 3 SST-lag vitals, which `hab` counted in rows across 20 missing OISST weeks; atlantis_core counts calendar weeks (operator ruling).

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

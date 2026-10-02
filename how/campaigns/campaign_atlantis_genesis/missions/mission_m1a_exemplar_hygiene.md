---
type: mission
mission_id: M-1a
plan_id: mission_m1a_exemplar_hygiene
title: "M-1a — Exemplar hygiene — doc/config drift, provenance hashes, packaging, safe region parser"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: implementation
executor_tier: opus
token_budget_estimated: "40-60kT"
token_budget_actual: ""
depends_on: ['M-0']
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1a_exemplar_hygiene.md
session: TBD
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1a, p1, opus, atlantis, tidewatch]
---

# M-1a — Exemplar hygiene — doc/config drift, provenance hashes, packaging, safe region parser

**Campaign:** `../campaign_atlantis_genesis.md` (Operation Tidewatch) · **Phase:** P1 — Core canonisation ·
**Tier:** opus · **Budget:** 40-60kT · **Depends on:** M-0

## Objective

Make the exemplar a trustworthy reference before anything is extracted from it: every number the README states is the number the outputs hold, every cached artifact has a sha256, the package installs, and no config string is `eval`ed.

## Acceptance criteria

- [ ] README §Design says **log-loss** stopping and **1000** background rows (matches `config.yaml` + `outputs/`); site §3 heading says three streams, or a fourth is added honestly
- [ ] `data/raw/*_fetch_summary.json` for all three sources with rows · date range · `fetched_at` · **sha256**; FWC server-count assertion kept
- [ ] `pyproject.toml` (+ `uv.lock`) replaces the bare `requirements.txt`; `python -m hab.*` still runs; matplotlib dropped or used
- [ ] `gauges.*.lever` is **read** by code (feeds the tag) or removed from config with a note — never silently ignored
- [ ] `regions.py` region rules parsed by a safe expression parser (no `compile/eval` on config strings); same 9 regions reproduced (assert region counts equal)
- [ ] The S329 AUPRC-stopping run reproduced once as a **negative control** and recorded (`outputs/negative_control_auprc_stop.json`) — T4 evidence
- [ ] `build_features --self-test` green before and after; `outputs/metrics.json` unchanged (config_hash e9dea88254) — hygiene changes nothing the model sees

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

- `what/exemplars/gulf_karenia_brevis/{README.md, config.yaml, pyproject.toml, src/hab/{fetch_fwc,fetch_env,regions,export_site_data}.py, site/template.html, data/raw/*_fetch_summary.json}`

## Inputs (read in this order)

1. `STATE.md` § ⏭ QUEUED · this card · `../campaign_atlantis_genesis.md` (this phase's exit bar).
2. `../artifacts/instance_contract_v0.md` · `../artifacts/thesis_register.md`.
3. `what/schema/atl_v0/README.md` · `what/board/README.md`.
4. The exemplar `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

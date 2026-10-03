---
type: mission
mission_id: M-1d-i
plan_id: mission_m1d_i_fork_and_conformance
title: "M-1d-i — fork from templates alone: atl_v0 0.3.0 · contract v0.2.0 · fetch CLI gated on the self-test · instance templates · atlantis_core.fork + conform · skill_atlantis_instance_fork · dry run"
owner: stanley
status: in_progress
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: integration
executor_tier: opus
token_budget_estimated: "~110-130kT main + fresh-context III reviewer (build-sized)"
token_budget_actual: ""
depends_on: ['M-1b-ii-b', 'M-1c']
split_from: mission_m1d_fork_skill_and_registries
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1d_i_fork_and_conformance.md
session: session_stanley_20261003_210703_m1d_i_fork_and_conformance
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1d_i, p1, opus, atlantis_core, fork, conformance, fetch, ontology, atlantis, tidewatch]
---

# M-1d-i — fork from templates alone

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 · **Tier:** opus · **Split from:**
`mission_m1d_fork_skill_and_registries.md` (operator ruling 2026-10-03) · **Sibling:** `mission_m1d_ii_lattice_and_registries.md`.

## Objective

Close the open P1 exit bar — *a fresh instance forks from templates alone, in one sitting, self-test green before any real
data is fetched* — with every step a command, and every contract item a ✅/✗ a machine prints.

## Operator rulings at open (2026-10-03, `AskUserQuestion`)

1. Split M-1d → i (this) / ii.
2. Contract v0 amended **in place → v0.2.0** (it named `config.yaml` and a self-test command the core never adopted).
3. Dry run = a **fictional hypoxia instance**: `below` event (DO ≤ 2 mg/L within 2 weeks), declared NDBC station stream +
   gridded SST, polygon grid by pointer, surveillance **declared absent**.
4. **atl_v0 → 0.3.0**: `ingested_at` optional; `sha256` ⇒ `ingested_at` (a declared-not-fetched stream must validate).

## Acceptance criteria

- [ ] `atl_v0` 0.3.0: the rule + new controls; `run_controls.sh` → ALL WORLDS AGREE; a sabotage shows the rule load-bearing; board v1 still validates
- [ ] `instance_contract_v0.md` → v0.2.0 (real file names · real self-test command · item 3 staged declared/fetched · item 5's home); federation pin README matches
- [ ] `atlantis_core.selftest` writes a receipt; `python -m atlantis_core.fetch` refuses without a receipt matching the current semantic hash; `--offline --verify` re-hashes the exemplar's three pins with no network (WI-15)
- [ ] Registry R8 (surveillance declared or declared absent with a reason)
- [ ] `how/templates/template_instance/` + `python -m atlantis_core.fork --answers … --out …`
- [ ] `python -m atlantis_core.conform --instance … --items 1-8,11,12 --stage declared|fetched` — a planted defect per item, each caught by name
- [ ] `how/skills/skill_atlantis_instance_fork.md` — interview → answers → vault shell → fork → mapping check → conform → self-test → only then fetch
- [ ] **Dry run** in the scratchpad from templates alone: mapping ✅ · conform 1–8, 11–12 ✅ · self-test ✅ · fetch gated, zero sockets — transcript in the AAR
- [ ] Byte-stable set vs `4bb1939` empty (board v1 · v0/v1 pages · `config.yaml` · exemplar `atlantis.yaml` · `metrics.json` · outputs)
- [ ] III review via `iii/`, fresh context (SO-10); findings addressed; AAR filed

## Guardrails

SO-1 (never advances the phase) · SO-3 / ADR-002 §4 (the dry run lives in the scratchpad, never committed) · SO-7 (both
self-tests before any vitals/label commit) · SO-4 · public repo, path-scoped staging · peer vaults read-only.

## Escalation triggers

Budget > +50% → SITREP and stop · anything putting observations, labels, predictions or partner coordinates into Atlantis → stop.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

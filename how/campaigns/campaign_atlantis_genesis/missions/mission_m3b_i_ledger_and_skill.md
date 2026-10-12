---
type: mission
mission_id: M-3b-i
plan_id: mission_m3b_i_ledger_and_skill
title: "M-3b-i — AtlHypothesis (atl_v0 0.9.0) · core 0.9.0 `atlantis_core.hypotheses` · `skill_feature_hypothesis_mining` · ≥ 25 coral_reef rows · ENVO binding · ends on the realisation ruling"
owner: stanley
status: active
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P3
campaign_phase: 3
mission_class: implementation
executor_tier: opus
token_budget_estimated: "≈ 170 kT main (+50% line ≈ 255 kT) + fresh-context III reviewer ≈ 150 kT — RE-CARDED 2026-10-12 to ≈ 460 kT main (operator ruling 5, AskUserQuestion at the SITREP ≈ 310 kT, after b989318): the planning sitting + the schema and core build ran over; the reading continues in this sitting"
token_budget_actual: ""
depends_on: ['M-2c', 'M-3a']
split_from: mission_m3b_hypothesis_ledger_and_mining
origin: "M-3b ruling 1 (operator, AskUserQuestion, 2026-10-12): two halves — ledger + skill / realise + SHAP (C-042: split at open)"
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m3b_i_ledger_and_skill.md
session: session_stanley_20261012_085758_m3b_i_ledger
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m3b_i, p3, opus, hypothesis_ledger, literature_mining, envo, atlantis, tidewatch]
---

# M-3b-i — the hypothesis ledger and the mining skill

**Split from** `mission_m3b_hypothesis_ledger_and_mining.md` (M-3b ruling 1). The other half is
`mission_m3b_ii_realise_and_test.md`.

## Rulings of the opening (AskUserQuestion, 2026-10-12)

1. **Split in two halves.** This half ends on the operator's ruling of which row M-3b-ii realises.
2. **The driver is ruled after the ledger.** Mine broadly; nothing is prejudged.
3. **The corpus is a committed manifest only:** queries, DOIs, OpenAlex ids, retrieval date and a result-set sha256.
   Abstracts sit in a gitignored `unreviewed/` cache. Rows quote ≤ 25 words. A pointer + recipe, like a dataset record
   (SO-3).
4. **The staged Noether ack is delivered** (folded in; done at open, `e77f534`).
5. **Re-card, continue** (at the +50% SITREP, ≈ 310 kT after `b989318`): ≈ 170 → ≈ 460 kT main; rows, review, III and
   the ruling in this sitting.

## Facts it rests on

- No `AtlHypothesis` class exists; `AtlVital.hypothesis_ref` is a free string (`atl_ontology_v0.linkml.yaml:247`).
- `Ingest.aDNA` has no literature class (documents: "planned"), so the card's fallback applies: a documented standalone
  fetch, `unreviewed/` discipline kept.
- FKNMS carries only CRW DHW, HotSpot and SSTA. `NDBCStdmet` is a `DeclaredFetcher`. Build cost is weighed at the
  realisation ruling, not here.

## Acceptance criteria

- [ ] `AtlHypothesis` in atl_v0 **0.9.0**, with pos/neg controls for every claimed constraint; committed JSON Schema
  regenerated; `run_controls.sh` → ALL WORLDS AGREE
- [ ] ENVO binding revisited (crosswalk deferred row) for `ecosystem_type`; the id looked up, not assumed
- [ ] Core **0.9.0** `atlantis_core.hypotheses`: `corpus` (standalone intake → manifest + gitignored `unreviewed/`) ·
  `--index` (generated `LEDGER.md`) · `--index --check` (writes nothing; a failure key per defect); offline tests
- [ ] `how/skills/skill_feature_hypothesis_mining.md`: paper → row; every row points at a sentence; tiers draft → reviewed
- [ ] ≥ 25 rows for one ecosystem type (`coral_reef`, FKNMS's DHW-onset event); index regenerated; `--check` green
- [ ] A realisation hand-off memo ranks the rows (literature strength × realisability × build cost); the operator rules
- [ ] *(C-033)* register re-read before the AAR; T8 gets an interim note (the re-cut is M-3b-ii's)
- [ ] III review via `iii/` in a fresh context; SITREP **at** the +50% line (C-042); suite count with its commit (C-035)

## Guardrails

As the parent card. In particular: no abstract, full text or PDF is committed (SO-3); no network in tests; no operator
email sent to any service; peer vaults read-only.

## AAR

*Mandatory before `status: completed` (SO-6).* Worked · Didn't · Finding · Change · Follow-up → `aar_path`.

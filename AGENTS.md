---
type: index
doc_id: agents_atlantis_root
title: "Atlantis.aDNA — root index for agents"
owner: stanley
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [index, agents, atlantis]
---

# Atlantis.aDNA — for agents

**Route:** `CLAUDE.md` (governance, persona, standing orders) → `STATE.md` § ⏭ QUEUED → the charter → the mission card.

| Need | Go to |
|---|---|
| What Atlantis is, in one page | `what/context/concept_atlantis.md` |
| The method, step by step, with the file that implements each step | `what/patterns/pattern_ecosystem_early_warning.md` |
| How to find the data and papers for a new region | `what/context/playbook_data_and_literature_mining.md` |
| A working end-to-end example (code, results, site) | `what/exemplars/gulf_karenia_brevis/README.md` + its `AGENTS.md` |
| The ontology an instance's registries validate against (draft) | `what/schema/atl_v0/README.md` |
| The evidence board and what an entry may carry | `what/board/README.md` |
| The hypothesis ledger (literature → testable vitals) | `what/hypotheses/README.md` |
| The genesis campaign, the roster, what is queued | `how/campaigns/campaign_atlantis_genesis/` → `artifacts/mission_roster_p1_p5.md` |
| What an instance must carry to federate (12-item checklist) | `how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md` (pin: `how/federation/atlantis/README.md`) |
| The claims and their evidence | `how/campaigns/campaign_atlantis_genesis/artifacts/thesis_register.md` |
| Identity rulings (all proposed) | `who/governance/adr_00{0,1,2}_*.md` |

**Do not** write regional data, partner data, credentials, or **new data snapshots** into this graph (SO-3, ADR-002
§4); **do not** put per-patient predictions or partner coordinates on the board. **Do** run the self-test after any
change to feature or label construction (SO-7). **Do** generate board entries and thesis numbers from `metrics.json`
by code, never by retyping.

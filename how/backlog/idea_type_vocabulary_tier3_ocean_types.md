---
type: backlog
doc_id: idea_type_vocabulary_tier3_ocean_types
title: "Propose Tier-3 type-vocabulary additions for ocean early warning (memo to Rosetta, aDNA.aDNA)"
status: proposed
priority: medium
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
origin: mission_m0_atlantis_genesis_planning
target: aDNA.aDNA/what/context/adna_core/context_adna_core_type_vocabulary.md (Tier 3, snake_case, `_file` suffix for formats)
tags: [backlog, upstream, type_vocabulary, atlantis, ontology]
---

# Tier-3 types for ocean early warning

At M-0 the `atl_v0` ontology deliberately made **table shapes** *not* entities. They still need canonical I/O type
names so `atlantis_core` modules and the pipeline lattice can annotate edges. Proposal for Rosetta, as a coordination
memo once P1 M-1b fixes the column contracts:

| Type | Shape | Produced by | Consumed by |
|---|---|---|---|
| `observation_long` | one row per observation: `stream_id · unit_id? · lat · lon · t · variable · value · unit · source_id · captured_at` (Darwin Core / CF column names where they exist) | fetchers | grid · vitals |
| `patient_grid` | the full product of spatial units × time steps, with `n_obs` per cell | grid | vitals · label |
| `vitals_table` | patient grid + one column per `AtlVital`; missing kept NaN, never forward-filled | vitals | label · train · explain |
| `onset_label` | patient grid + `y`, `already_past_threshold`, `outcome_unknown`, `future_extreme` | label | train · eval |
| `shap_summary` | mean |SHAP| per vital and group · dependence partners · top interaction · additivity gap (no per-row values) | explain | board · site |

Rule: these are **parquet-backed** (`_file` variants if a format name is needed); none crosses into Atlantis except
`shap_summary` *statistics* inside a board entry. Send after M-1b; cite ADR-002 and `what/schema/atl_v0/README.md`
§Dropped.

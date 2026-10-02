---
type: backlog
doc_id: idea_cosign_datasets_provenance_contract
title: "Co-sign ASOAtlas's open seam to Datasets.aDNA — a provenance contract by pointer, not a copy"
status: proposed
priority: medium
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
origin: mission_m0_atlantis_genesis_planning
related: ASOAtlas.aDNA/who/coordination/outbox/coord_2026_09_25_mercator_to_datasets_seam_provenance_contract.md
tags: [backlog, coordination, datasets, provenance, atlantis]
---

# Co-sign the Datasets.aDNA provenance-contract seam

`ASOAtlas.aDNA` (Mercator) asked `Datasets.aDNA` on 2026-09-25 for a **provenance contract by pointer** — lineage,
consent scope, classification, crossing an airlock as an aggregate — rather than a copied Dataset primitive. The memo
is unanswered (Datasets.aDNA is a genesis stub). Atlantis has the identical need: ADR-002 §4's snapshot rule makes
every Atlantis dataset record a *pointer + sha256 + fetch recipe*, and the board's `data_pins[]` are exactly the
contract's join keys.

**Action (after the P0 gate):** a short coordination memo from Proteus to Datasets.aDNA (cc Mercator) co-signing
the ask, adding Atlantis's two requirements — Ingest Rule-5 fields (`source_system · source_id · captured_at ·
ingested_at · pipeline_version`) and `sha256` as the pin — and offering the `template_dataset_pair/` as a worked
conformance example. Two consumers asking for the same contract is the P0 input Datasets.aDNA's own mission card says
it is waiting for.

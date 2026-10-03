---
type: federation_contract
doc_id: federation_atlantis_wrapper
title: "how/federation/atlantis/ — what a regional instance carries to federate Atlantis (contract v0)"
status: draft
version: 0.2.0
created: 2026-09-23
updated: 2026-10-03
last_edited_by: agent_proteus
contract: how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md
tags: [federation, wrapper, atlantis, instance_contract, adr_045, conformance]
---

# Federating Atlantis from an instance graph

An instance carries `how/federation/atlantis/CLAUDE.md` with the `federation_ref` block below (ADR-045 placement).
**The contract — the twelve-item checklist a reviewer runs from `atlantis.yaml` · `units.yaml` · `streams.yaml` ·
`features.yaml` · `events.yaml` · `mapping.yaml` and the posture ADR without seeing the instance's data (machine-checked by
`python -m atlantis_core.conform`; v0.2.0, 2026-10-03), what Atlantis promises back, and how knowledge moves between
stewards — is `instance_contract_v0.md`** (linked in frontmatter). This file is the pin; that file is the terms.

```yaml
federation_ref:
  source_vault: Atlantis.aDNA
  source_persona: Proteus
  source_path: what/atlantis_core/                 # P1
  source_commit: <sha>
  version: "0.1.0"
  version_policy: minor
  patterns_used: [ATL-ONTOLOGY, ATL-STREAM, ATL-VITALS, ATL-LABEL, ATL-EVAL, ATL-EXPLAIN, ATL-BOARD]
  conformance: atlantis_instance
  instance:
    patient: {unit_kind: <atl enum>, external_id: "<WDPA:id | none>", time_step: <atl enum>}
    event:   {variable: "<CURIE>", threshold: <n>, unit: "<UCUM>", direction: above|below, horizon: "<n> weeks"}
    streams: [<stream ids>]
    data_posture: {class: public|partner|human_subject, ruling: "<path to the instance's ADR>"}
    self_test: "python -m atlantis_core.selftest --instance ."
    board_entry: "what/board/entries/<date>_<instance>_v<n>.json"
```

What Atlantis promises back and never takes: contract §C. Status: v0 (M-0, 2026-10-02); v1 is ratified at P4
against the first outside steward.

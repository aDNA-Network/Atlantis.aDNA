---
type: federation_contract
doc_id: federation_atlantis_wrapper
title: "how/federation/atlantis/ — what a regional instance carries to federate Atlantis (stub, v0)"
status: proposed
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [federation, wrapper, atlantis, instance_contract, adr_045]
---

# Federating Atlantis from an instance graph

Placement per ADR-045: an instance carries `how/federation/atlantis/` with a `federation_ref` block naming this
graph and the version of the method it instantiates. **The contract itself is M-0's artifact
(`instance_contract_v0.md`); this stub records the intended shape so P0 has something to edit.**

```yaml
federation_ref:
  source: Atlantis.aDNA
  pattern: pattern_ecosystem_early_warning
  pattern_version: 0.1
  template: template_regional_instance      # from P1
  instance:
    patient: "<spatial unit> × <time step>"
    event: "<variable> >= <threshold> within <horizon>"
    streams: [<stream ids with fetchers>]
    data_posture: "<public | partner | human-subject> — ruling: <path to the instance's ADR>"
    self_test: "src/<pkg>/build_features.py --self-test"   # must be green before real data is fetched
```

What Atlantis promises back: the pattern and its updates, the templates, the self-test, the mining playbook,
and review of an instance's Limitations section on request. What Atlantis never takes: the instance's data.

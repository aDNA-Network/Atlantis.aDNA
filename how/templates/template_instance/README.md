---
type: template_set
doc_id: template_instance
title: "template_instance — what atlantis_core.fork renders into a new Atlantis instance (M-1d-i)"
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
mission: mission_m1d_i_fork_and_conformance
tags: [template, instance, fork, atlantis, contract_v0_2]
---

# `template_instance/`: a new instance from templates alone

`python -m atlantis_core.fork --answers <answers.yaml> --out <instance dir>` renders this set from the steward's interview
answers. The skill that runs the interview is `how/skills/skill_atlantis_instance_fork.md`. The shape of the answers is
`answers.example.yaml`. Tokens are `{{name}}`, as in `../template_mapping_atl.yaml`, and an unresolved token is refused.

| Template | Renders to | Contract item |
|---|---|---|
| `atlantis.yaml.tmpl` | `atlantis.yaml` (engine config: grid · stream shapes · label · split · surveillance · self-test) | 1 · 2 · 5 · 6 · 8 |
| `units.yaml.tmpl` | `units.yaml` (`AtlSpatialUnit` rows: the region, then every grid unit `PART_OF` it) | 1 · 11 |
| `streams.yaml.tmpl` | `streams.yaml`, **declared** (no sha256 or ingested_at until the fetch, atl_v0 0.3.0) | 3 · 5 |
| `features.yaml.tmpl` | `features.yaml` (starter vitals; every tag is the steward's ruling) | 4 · 5 |
| `events.yaml.tmpl` | `events.yaml` | 2 |
| `../template_mapping_atl.yaml` | `mapping.yaml` (rendered as is, with `instance_slug` filled) | 11 |
| `adr_data_posture.md.tmpl` | `who/governance/adr_<nnn>_data_posture.md`, **proposed** | 7 |
| `federation_atlantis_CLAUDE.md.tmpl` | `how/federation/atlantis/CLAUDE.md` (the §A `federation_ref`, `source_commit` pinned) | §A |
| `gitignore.tmpl` | appended to `.gitignore` (non-public postures ignore `data/`, `outputs/` and `site/` entirely) | 7 · 12 |

**What fork refuses:**
- an unresolved token, or a target file that already exists;
- an enum value outside `atl_v0`;
- a lever without an owner (via R4, for steward-supplied `vitals` too);
- coordinate `rules`, or a `cells` bbox, under a `partner` or `human_subject` posture;
- a polygon path that is absolute, leaves the instance, or does not exist;
- a unit `geometry_ref` outside the instance;
- a fetch spec missing a built fetcher's `spec_required` keys;
- fewer than two self-test patients;
- a stream the self-test patients do not reach;
- anything the registry check (R1–R8) rejects. That check runs on a temporary render **before** a file is written. Check the result with `atlantis_core.mapping --check` and
`atlantis_core.conform --stage declared`, and earn the fetch with `atlantis_core.selftest`.

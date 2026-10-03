---
type: mission
mission_id: M-1d-ii
plan_id: mission_m1d_ii_lattice_and_registries
title: "M-1d-ii — pipeline lattice + runspec · BOARD generator (WI-8) · dataset-pair migration · contribution guide · board --entries for instances"
owner: stanley
status: planned
campaign: campaign_atlantis_genesis
campaign_id: campaign_atlantis_genesis
phase: P1
campaign_phase: 1
mission_class: integration
executor_tier: opus
token_budget_estimated: "~80-100kT main + fresh-context III reviewer (build-sized)"
token_budget_actual: ""
depends_on: ['M-1d-i']
split_from: mission_m1d_fork_skill_and_registries
aar_path: how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1d_ii_lattice_and_registries.md
session: TBD
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
home_vault: Atlantis.aDNA
tags: [mission, m1d_ii, p1, opus, lattice, runspec, board, datasets, contribution_guide, atlantis, tidewatch]
---

# M-1d-ii — pipeline lattice · BOARD · dataset pairs · contribution guide

**Campaign:** `../campaign_atlantis_genesis.md` · **Phase:** P1 · **Tier:** opus · **Split from:**
`mission_m1d_fork_skill_and_registries.md` (operator ruling 2026-10-03) · **Sibling:** `mission_m1d_i_fork_and_conformance.md`.
**The P1 gate (fable, operator-summoned) follows this card.**

## Objective

Close the registry loose ends the public repo needs, and write the method down as one executable lattice.

## Acceptance criteria

- [ ] `how/lattices/lattice_atlantis_pipeline.lattice.yaml` (`lattice_type: pipeline`): discover → fetch → grid → vitals → self-test → label → train → eval → explain → board → site; each node's `config` names its `atlantis_core` command (discover is declared-only until M-3a, said so)
- [ ] Validated by **both** `aDNA.aDNA/what/lattices/tools/lattice_validate.py` (no CLI — import `validate_lattice_file`; peer file never edited) **and** the stricter `aDNA.aDNA/what/lattices/lattice_yaml_schema.json` (`additionalProperties: false`), which the Python validator never loads
- [ ] A closed-vocabulary **runspec** JSON convention (DDX precedent: `DDX.aDNA/what/code/ddx_runner/runspec_example.json` — no field can carry a path, a prompt or data; reject, don't coerce), checked by code with a planted defect per field
- [ ] `what/board/BOARD.md` generated from `entries/` by `atlantis_core.board` (`--index` writes, `--index --check` exits non-zero if stale; byte-stable, no timestamps; RareArchive `board_index.py` precedent); v0's open-shape entry rendered and labelled as such — **closes WI-8**
- [ ] `atlantis_core.board --entries <dir>` so an instance writes its own entry (which travels to Atlantis by memo, contract §A); default stays Atlantis's `what/board/entries/`
- [ ] `what/datasets/` migrated to the pair standard (`.md` + `.dataset.yaml`) with sha256 pins; the two ad-hoc notes superseded in place. **First fix `how/templates/template_dataset_pair/`**: it fails the lattice-labs `dataset_yaml_schema.json` it claims (sha256 belongs in `format.checksum: "sha256:…"`; `storage.location` is an object; `storage.provider` ∈ s3|minio|gcs|azure|ceph|local|fuse; Rule-5 lineage keys belong in `class_fields`) — validate every pair against that schema
- [ ] `who/governance/contribution_guide.md` — what crosses / never crosses; memo-to-inbox flow; DCO; tiers draft → reviewed → validated (RareArchive `who/governance/contribution_guide.md` precedent)
- [ ] III review via `iii/`, fresh context; AAR; **P1 exit bar met → fable review requested** (raise ADR-002 A-1 if still pending)

## Inputs

STATE · this card · the M-1d-i AAR · `what/atlantis_core/README.md` · `what/board/README.md` · `what/datasets/AGENTS.md`.

## AAR

*Mandatory before `status: completed` (SO-6).* → `aar_path`.

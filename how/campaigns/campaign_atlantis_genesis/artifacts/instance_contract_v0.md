---
type: artifact
doc_id: instance_contract_v0
title: "Instance contract v0 — what a regional instance carries to federate Atlantis, what Atlantis promises back, and how a reviewer conforms it without seeing its data"
status: draft
version: 0.1.0
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
supersedes: how/federation/atlantis/README.md (stub, 2026-09-23)
tags: [artifact, instance_contract, federation, conformance, mapping_yaml, atlantis, m0]
---

# Instance contract v0

An **instance** is one steward's regional graph — `FloridaKeysCoral.aDNA`, `ChesapeakeKarlodinium.aDNA`,
`<River>Metagenome.aDNA` — that federates Atlantis. Instances are **data-bearing** and own their data posture,
credentials, partners and rulings. Atlantis owns the method, the ontology, the templates and the board. This
contract says what each side carries. It is v0: P1 builds the files it names; P4 ratifies v1 against the first
outside steward.

## A. The `federation_ref` an instance carries

Placement per ADR-045: `<Instance>.aDNA/how/federation/atlantis/CLAUDE.md`. Shape follows the Organization.aDNA
conformance pin (`Organization.aDNA/what/context/org_conformance_checklist.md`) with RareArchive's commit pin.

```yaml
federation_ref:
  source_vault: Atlantis.aDNA
  source_persona: Proteus
  source_path: what/atlantis_core/                 # the reference implementation the instance installs (P1)
  source_commit: <sha>                             # pinned at fork; bumped deliberately
  version: "0.1.0"                                 # pattern + schema version (atl_v0 ↔ 0.x)
  version_policy: minor                            # minor (auto patch/minor) | locked
  patterns_used: [ATL-ONTOLOGY, ATL-STREAM, ATL-VITALS, ATL-LABEL, ATL-EVAL, ATL-EXPLAIN, ATL-BOARD]
  conformance: atlantis_instance
  instance:
    patient: {unit_kind: mpa_zone, external_id: "WDPA:<id>", time_step: iso_week}
    event:   {variable: "<CF standard name or taxon>", threshold: <n>, unit: "<UCUM>", direction: above|below, horizon: "<n> weeks"}
    streams: [<stream_ids — each a row in streams.yaml with provenance>]
    data_posture: {class: public|partner|human_subject, ruling: "who/governance/adr_<nnn>_data_posture.md"}
    self_test: "python -m atlantis_core.vitals --self-test"   # must be green BEFORE real data is fetched
    board_entry: "what/board/entries/<date>_<instance>_v<n>.json"   # metrics only; copied to Atlantis by memo
```

The seven pattern IDs name the method's steps as a Framework exposes them (append-only from here):

| ID | Step(s) | Atlantis file that defines it |
|---|---|---|
| ATL-ONTOLOGY | the `atl_` schema an instance's registries validate against | `what/schema/atl_v0/` |
| ATL-STREAM | discover + cache + provenance (steps 1–2) | `pattern_ecosystem_early_warning.md` §1–2 · playbook §A · streams registry (P1) |
| ATL-VITALS | the feature registry + translation onto the patient grid (step 3) | feature registry schema (P1 M-1b) |
| ATL-LABEL | direction-aware onset label with both drop counts (step 4) + the self-test (step 5) | `atlantis_core.vitals --self-test` (P1) |
| ATL-EVAL | temporal split · log-loss stopping · budgets · lead time · ablation · climatology (step 6) | `template_model_card.md` · board schema |
| ATL-EXPLAIN | interventional SHAP · tags · what-if with the causal caveat (steps 7–8) | pattern §7–8 · feature registry `tag` |
| ATL-BOARD | the GREEN metrics entry | `what/board/README.md` |

## B. What the instance carries (the checklist)

A reviewer conforms an instance **by reading four files and never its data**: `config.yaml`, `streams.yaml`,
`features.yaml`, `mapping.yaml` (plus the posture ADR). Every line below is checkable from those files.

| # | Requirement | Checked in | Why |
|---|---|---|---|
| 1 | **Patient defined**: `unit_kind` ∈ atl enum; `time_step` ∈ enum; geometry is a *pointer* (file path / WDPA id), never inline coordinates of partner sites | `config.yaml → patient` | T1; ADR-002 §5 |
| 2 | **Event defined**: variable with authority CURIE (CF / WoRMS), threshold + UCUM unit, `direction`, horizon; onset rule stated | `config.yaml → event` | T3 |
| 3 | **Streams registered** with Ingest Rule-5 provenance: `source_system`, `source_id`, `captured_at`, `ingested_at`, `pipeline_version`, plus `sha256` of each cached artifact and `license` | `streams.yaml` | ATL-STREAM; reproducibility |
| 4 | **Every vital has a tag** (lever · proxy · artifact · state), a `stream_ref`, lag/window; levers name an `owner` | `features.yaml` | T7; the tag is reviewable, not hidden in code |
| 5 | **Surveillance channel declared** (or declared absent, with the reason — e.g. gridded-only) | `features.yaml → group: surveillance` | T5 |
| 6 | **Self-test green before any real data is fetched**, and re-run on every change to vitals or label (SO-7) | `self_test` field + session log | the one hard invariant |
| 7 | **Data posture ruled** in the instance's own ADR (ADR-016 §8 class: public / partner / human-subject); partner or human-subject data never enters Atlantis | `data_posture.ruling` path exists | SO-3; Hard Gate |
| 8 | **Split is temporal**; test window named and scored once; retuning happens on validation only | `config.yaml → split` | T2, T4 |
| 9 | **Board entry** carries `base_rate`, climatology baseline, ≥1 alert budget, lead-time summary, ablations, `config_hash`, `data_pins[]`; `claim` is `method_demonstration` unless an owner ruling is cited | `what/board/entries/*.json` | T6, T10, T11; SO-4 |
| 10 | **Published page has the required sections**, including **Limitations** and "where the analogy breaks" | site template sections | SO-4; pattern §"Where the analogy breaks" |
| 11 | **`mapping.yaml` present**: the instance's objects projected to the `atl_` labels (SpatialUnit · ObservationStream · Vital · EventDefinition · Evaluation) with `canonical_id`, bi-temporal stamps (`source, ingested_at, valid_from, valid_to`), and a `fence` that excludes raw observations | `mapping.yaml` | Organization §2 / Neo4j N4-MODEL — conformance without inspection |
| 12 | **Credentials by name only** (Home broker pattern); no value in any committed file | `gitleaks` on push | fleet doctrine |

## C. What Atlantis promises back

- The pattern and its updates (`version_policy: minor` means an instance receives patch/minor template fixes).
- The reference implementation (`what/atlantis_core/`, P1) and the exemplar as a runnable reference.
- The ontology + crosswalk, and (from M-1c) the controls an instance can run against its own registries.
- The mining playbook and (P3) the hypothesis ledger — literature claims the instance can realise as vitals.
- Review of an instance's **Limitations** section and board entry on request (a coordination memo).
- A row in the **instance register** (P4) — name, unit kind, event, posture class — only with the steward's consent.

**What Atlantis never takes:** observations, labels, per-patient predictions, trained binaries from partner or
human-subject data, partner-site coordinates, credentials.

## D. How work and knowledge move between stewards

| Need | Mechanism (composed, not built here) |
|---|---|
| Send a template fix, a feature-registry row, a hypothesis, or a board entry to Atlantis | coordination memo → `Atlantis.aDNA/who/coordination/inbox/coord_<date>_<from>_to_proteus_<topic>.md`; Proteus lands it by a dated commit; never a direct write to another operator's vault (Operations ADR-026) |
| Share work on a task (two stewards, one instance, or a cross-instance study) | `Operations.aDNA` task with `federation_ref` + claim-lease (bridge `:27125`; live on this node) |
| Share an instance graph beyond its node | `Network.aDNA` share class `public | partner_share | private`; data-bearing instances default `private` and are dial-out-only (Network ADR-016 §8) |
| Train on L2 | `Ray.aDNA` `RayWorkloadRequest` (hashes and ids only; outputs with sha256) — template at P5 |
| Intake a literature corpus | `Ingest.aDNA` (discover → fetch → redact → gate → publish; `unreviewed/` is a path, not a flag) |
| Disagree | dated note beside the record, never a deletion (RiemannCommons GOVERNANCE §Mutual non-authority) |

## E. Open for v1 (P4)

Consent wording for the instance register · trust bands for stewards (Operations ADR-026 probationary / trusted /
anchor) · whether the board accepts entries from instances with `partner` posture (metrics only — yes in principle;
the ruling is the instance owner's) · a blind-conductor runbook for the first partner-data instance.

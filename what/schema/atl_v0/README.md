---
type: schema_pack
doc_id: atl_schema_v0_readme
title: "what/schema/atl_v0/ — the Atlantis `atl_` ontology, v0 (draft · NO VALIDATION CLAIM)"
status: draft
version: 0.1.0
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
authoring_idiom: "LinkML (aDNA.aDNA ADR-062, proposed — preferred-but-optional)"
precedent: ASOAtlas.aDNA/what/schema/aso_v0/
validation:
  run_at: 2026-10-02
  toolchain: "scratch uv venv · Python 3.12 · linkml 1.11.1 (nothing installed on the node)"
  linkml_lint: "0 errors · 38 warnings (37 `recommended`: missing description on id/part slots; 1 `canonical_prefixes`: UCUM namespace) — accepted at v0"
  gen_json_schema: "--closed -t AtlDocument → rc 0, 18 $defs (11 classes + 7 enums); generated to scratch only, NOT committed (M-1c)"
  smoke: "one positive AtlDocument validates; one negative (lever without owner) rejected at /vitals/0 — a SMOKE test, not a control: no REJECTS_ON discipline, not committed"
  controls: "none — fixtures/controls/ + run_controls.sh + fit matrix are M-1c"
tags: [schema, ontology, linkml, atl, atlantis, draft, m0]
---

# `atl_v0` — the Atlantis ontology

> ⛔ **NO VALIDATION CLAIM.** This directory holds a *draft* LinkML schema and a crosswalk. No control fixture has
> been run against it, no JSON Schema is committed, no vocabulary fit matrix exists. A constraint written in the
> schema is an **intention** until P1 **M-1c** builds `fixtures/controls/{pos,neg}_*.yaml` + `run_controls.sh` and
> the generated `atl_ontology_v0.schema.json`, and proves — ASOAtlas rule 1 — that **both** validators enforce it.

## What is here

| File | What | Status |
|---|---|---|
| `atl_ontology_v0.linkml.yaml` | Five classes · seven enums · the slots an instance's registries are declared in | draft |
| `crosswalk_external_vocabularies_v0.yaml` | Which marine authorities an `atl_` slot binds to (6 bound: WDPA · CF · UCUM · WoRMS · Darwin Core · PROV-O), which are deferred and why, and which things are *source protocols*, not vocabularies | draft |
| `fixtures/controls/` · `run_controls.sh` · `atl_ontology_v0.schema.json` · `m1c_vocabulary_fit_matrix.md` | **M-1c** | absent by design |

## The five classes, and why only five

Chosen by the three tests in `context_adna_core_ontology_workshop` (instance · independence · lifecycle):

| Class | Instance test | Independence | Lifecycle | Replaces in the exemplar |
|---|---|---|---|---|
| `AtlSpatialUnit` | an MPA zone is countable | outlives any model | boundaries change by ruling, versioned | `config.yaml → regions` + `region_boxes` |
| `AtlObservationStream` | one source | unit of fetch / licence / drift | re-fetched, re-hashed | `fwc_layers` · `fetch_env` constants · `dataset_*.md` |
| `AtlVital` | one feature | exists before any model is trained | added / retired per registry version | `FEATURE_GROUPS` + `FEATURE_DOC` (hard-coded) |
| `AtlEventDefinition` | one threshold ruling | a second event is a second model (T12) | versioned ruling | `config.yaml → target` |
| `AtlEvaluation` | one scored test window | the measurement is the artifact (ADR-057) | one per training run | `outputs/metrics.json` (subset) |

**Dropped or deferred, deliberately.**

- `Patient × TimeStep`, `Observation`, `Label`, `Prediction` — **table shapes**, not entities. Proposed as Tier-3
  type-vocabulary additions (`patient_grid` · `observation_long` · `vitals_table` · `onset_label` · `shap_summary`)
  in `how/backlog/idea_type_vocabulary_tier3_ocean_types.md` (memo to Rosetta). They never enter Atlantis.
- `Model` — referenced, not redefined: RareArchive's `model.schema.json` (lineage · artifacts · evaluation) and
  Ray's `RayJobRecord` (submission · image digest · outputs with sha256) already cover it; `AtlEvaluation` carries
  `learner`, `config_hash`, `data_pins[]` as the join keys.
- `Hypothesis` — v1, with the P3 ledger (`what/hypotheses/README.md` holds the spec now).
- `Steward`, `Instance` — governance documents (`instance_contract_v0.md`, instance register at P4).
- `BoardEntry` — the board's own schema (`what/board/README.md`), which **embeds** an `AtlEvaluation`.

## Rules adopted (effective at M-1c)

1. A constraint is claimed only if **both** `linkml-validate` and the committed JSON Schema enforce it.
2. Every enum is a row in the fit matrix, sourced to the crosswalk authority or marked `local` with the reason.
   v0 enums are all `local` by design; `Modality` is the one most likely to be re-bound (GOOS EOV).
3. Each constraint's docstring says what its control proves and names the nearest miss it does not catch.
4. Flag-proof: no class that is the range of a slot has a concrete descendant.
5. Referential integrity (does `stream_ref` resolve? does the ruling path exist?), uniqueness and cross-object
   equality are a **validator's** job, not the schema's — named here as known limits, never implied.

## Validation (this sitting)

Run in a scratch venv (uv · Python 3.12 · linkml 1.11.1), nothing installed on the node:

```
linkml-lint  what/schema/atl_v0/atl_ontology_v0.linkml.yaml
gen-json-schema --closed -t AtlDocument what/schema/atl_v0/atl_ontology_v0.linkml.yaml > <scratch>/atl_v0.schema.json
```

**Result (2026-10-02):** `linkml-lint` → **0 errors, 38 warnings** (37 `recommended` — `description` missing on
identifier and part slots; 1 `canonical_prefixes` — UCUM's namespace differs from the registry's). `gen-json-schema
--closed` → rc 0, 18 definitions. A positive `AtlDocument` validated; a negative (lever without `owner`) was rejected
at `/vitals/0`. **That is a smoke test, not a control** — it carried no `REJECTS_ON` line and is not committed; M-1c
turns it into `neg_lever_without_owner.yaml` under the ASOAtlas discipline. Warnings are accepted at v0; **errors are
not** — a schema that does not load is not a draft.

## How an instance uses it (from P1)

An instance keeps `streams.yaml`, `features.yaml`, `events.yaml` and `evaluations/*.yaml` as `AtlDocument`
instances and validates them with `linkml-validate -s <this file> -C AtlDocument`. The twelve-item contract
checklist (`instance_contract_v0.md` §B) is checkable from those files without the data.

## Extension discipline

Additive only; namespaced `atl_`; triad WHAT; home `what/schema/atl_v<n>/`. A new class must pass the three tests
and name the exemplar or instance object it replaces. Breaking changes bump the directory (`atl_v1/`); the old
directory stays (SO-2). Registered in `what/ontology.md` § Atlantis Extensions.

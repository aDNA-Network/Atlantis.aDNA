---
type: schema_pack
doc_id: atl_schema_v0_readme
title: "what/schema/atl_v0/ — the Atlantis `atl_` ontology, v0 (draft · 50 controls under three worlds)"
status: draft
version: 0.4.0
created: 2026-10-02
updated: 2026-10-03
last_edited_by: agent_proteus
mission: mission_m1e_eval_thresholds_on_validation   # 0.4.0; 0.3.0 at mission_m1d_i_fork_and_conformance; controlled at mission_m1c_linkml_controls; authored at mission_m0_atlantis_genesis_planning
authoring_idiom: "LinkML (aDNA.aDNA ADR-062, proposed — preferred-but-optional)"
precedent: ASOAtlas.aDNA/what/schema/aso_v0/
validation:
  run_at: 2026-10-03   # M-1e (0.4.0); M-1d-i (0.3.0) 2026-10-03; M-1c 2026-10-02
  toolchain: "scratch uv venv · Python 3.12 · linkml 1.11.1 · jsonschema[format] + rfc3339-validator (nothing installed on the node; LINKML_BIN)"
  linkml_lint: "0 errors · 32 warnings (31 `recommended` — missing description on part/container slots; 1 `canonical_prefixes` — UCUM namespace) — accepted at v0"
  gen_json_schema: "gen-json-schema --closed (tree_root AtlDocument) → atl_ontology_v0.schema.json COMMITTED, draft 2019-09, 19 $defs (0.4.0: + ThresholdSource); byte-equality with a fresh generation is checked every run"
  controls: "50 — 5 positive · 45 negative (19 at build + 23 from the M-1c III review + 3 at M-1d-i for the 0.3.0 stream rule + 1 positive and 4 negatives at M-1e for the 0.4.0 budget rule); each negative fails ONLY on its REJECTS_ON regex AT its REJECTS_AT path, in all three worlds (linkml-validate · committed JSON desc-OFF · scratch JSON desc-ON), FORMAT_CHECKER on"
  instrument_proven: "three deliberate sabotages each turned the run red (rule weakened · committed JSON hand-edited · a negative naming the wrong reason) + per-arm isolation: removing each of the 7 geometry/anchor arms reddens exactly its own control(s) — M-1c AAR. 0.3.0 (M-1d-i): rule removed → its 2 negatives red in all three worlds; all_of arm removed → only the null twin red. 0.4.0 (M-1e): rule removed → both new negatives pass (validate) under linkml-validate and the generated JSON; a bare `required` (all_of removed) → the null twin passes — the M-1c hole, reproduced on the new rule"
  iii_review: "PASS-WITH-FINDINGS (fresh-context reviewer via iii/ wrapper, III v0.6.0); 12 findings, 11 fixed at M-1c, 1 carried (WI-8) — M-1c AAR §III review"
  flag_proof: "Rule 4 asserted by the runner: 9 range classes, no concrete descendants"
  fit_matrix: "m1c_vocabulary_fit_matrix.md — 30 enum values; 0 bound / 30 local with reasons; Modality re-examined against GOOS EOV (live page, 36 EOVs) → stays local, EOV = v1 stream annotation"
tags: [schema, ontology, linkml, atl, atlantis, draft, m0]
---

# `atl_v0` — the Atlantis ontology

> ✅ **50 controls · three worlds · committed JSON == fresh** (M-1c 2026-10-02; 0.3.0 at M-1d-i 2026-10-03; 0.4.0 at M-1e 2026-10-03). A constraint is claimed here **only**
> where a fixture in `fixtures/controls/` proves it under `linkml-validate`, the committed `atl_ontology_v0.schema.json`
> (descendants OFF) and a scratch JSON Schema (descendants ON) — ASOAtlas rule 1. Everything else the schema *says* is
> documentation. Status stays `draft`; what the controls do **not** prove is listed under **Known limits** below.
>
> ```
> uv venv <scratch> && uv pip install -p <scratch>/bin/python linkml==1.11.1 "jsonschema[format]" rfc3339-validator pyyaml
> LINKML_BIN=<scratch>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh     # → "== ALL WORLDS AGREE ==", rc 0
> ```

## What is here

| File | What | Status |
|---|---|---|
| `atl_ontology_v0.linkml.yaml` | Five classes · seven enums · the slots an instance's registries are declared in | draft |
| `crosswalk_external_vocabularies_v0.yaml` | Which marine authorities an `atl_` slot binds to (7 bound: WDPA · CF · UCUM · WoRMS · Darwin Core · PROV-O · NOAA CRW — the last bound 2026-10-06 at M-2a-i), which are deferred and why, and which things are *source protocols*, not vocabularies | draft |
| `atl_ontology_v0.schema.json` | `gen-json-schema --closed` output, committed; the runner fails if it drifts | controlled |
| `fixtures/controls/` | 4 `pos_*` · 41 `neg_*` (each with `# REJECTS_ON:` + `# REJECTS_AT:`) · `run_controls.sh` · `check_controls_json.py` · `_common_header.txt` (fixture sourcing) | controlled |
| `m1c_vocabulary_fit_matrix.md` | Every enum value × every crosswalk authority; the GOOS EOV re-examination | draft |

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

## Rules adopted (in force from M-1c)

1. A constraint is claimed only if **both** `linkml-validate` and the committed JSON Schema enforce it.
2. Every enum is a row in the fit matrix, sourced to the crosswalk authority or marked `local` with the reason.
   v0 enums are all `local` by design; `Modality` is the one most likely to be re-bound (GOOS EOV).
3. Each constraint's docstring says what its control proves and names the nearest miss it does not catch.
4. Flag-proof: no class that is the range of a slot has a concrete descendant.
5. Referential integrity (does `stream_ref` resolve? does the ruling path exist?), uniqueness and cross-object
   equality are a **validator's** job, not the schema's — named here as known limits, never implied.

## What the controls prove (M-1c · 0.3.0 at M-1d-i · 0.4.0 at M-1e)

| Constraint | Positive | Negative(s) — rejected only on this, at this path | Nearest miss NOT caught |
|---|---|---|---|
| A lever names its owner (rule) | exemplar (S-79 lever) | `neg_lever_without_owner` · `_owner_null` · `_owner_blank` | an owner who cannot move this lever |
| A hash names a fetch: `sha256` ⇒ `ingested_at` (rule; 0.3.0 — a stream may be **declared** before it is fetched) | `pos_stream_declared_prefetch` · exemplar (3 fetched streams) | `neg_sha256_without_ingested_at` · `neg_stream_ingested_at_null` (a blank is refused by the slot's date-time range already) | the converse — `ingested_at` without `sha256` (fetched, unpinned); contract item 3's *fetched* stage checks it (`atlantis_core.conform`) |
| An operational claim cites its ruling (rule; SO-4) | `pos_operational_with_ruling` | `neg_operational_without_ruling` · `_ruling_null` · `_ruling_blank` | a ruling path that does not exist |
| `claim` required (no `ifabsent` default applied) | all evaluations | `neg_missing_claim` · `neg_unknown_claim` | — |
| `base_rate` required, in [0,1] (SO-9) | exemplar | `neg_missing_base_rate` · `neg_base_rate_gt1` | base_rate ≠ n_positives / n_test |
| `limitations_ref` required, non-blank (SO-4/9) | exemplar | `neg_missing_limitations_ref` · `neg_limitations_ref_blank` | a page with no Limitations section |
| ≥ 1 alert budget (SO-9 — operator ruling: now, not M-1b) | exemplar (3 budgets) | `neg_evaluation_without_budget` · `neg_evaluation_empty_budgets` | a budget not measured at its rate |
| A threshold fixed on validation states its realised rate: `threshold_from = validation` ⇒ `realised_rate` (rule, typed `all_of`; 0.4.0 — F-8) | `pos_budget_fixed_on_validation` | `neg_budget_validation_without_realised_rate` · `neg_budget_realised_rate_null` · `neg_realised_rate_gt1` (range) · `neg_unknown_threshold_from` (enum) | a budget that omits `threshold_from` (the grandfathered v0/v1 shape — the board emitter refuses it for new entries); a `threshold_from` that misstates where the threshold was computed (`tests/test_f8.py::test_eval_thresholds_do_not_move_with_test` tests that by effect; `board.assert_thresholds_fixed` checks realised = n_alerts / n_test) |
| `atl_<kind>_` id prefixes — **all five** id slots | all | `neg_bad_id_prefix` (stream) · `neg_unit_id_prefix` · `neg_vital_id_prefix` · `neg_event_id_prefix` · `neg_eval_id_prefix` | duplicate ids; dangling `*_ref`s |
| `sha256` = lowercase hex64, no trailing newline | exemplar (3 pins) | `neg_sha256_not_hex64` · `neg_sha256_trailing_newline` | a well-formed hash of the wrong bytes |
| `geometry_ref` is a pointer (denylist — operator ruling) — **one control per arm** | exemplar rule strings · `pos_mpa_zone_wdpa` paths | arms: `neg_geometry_arm_{brace,wkt,ewkt_case,pair,pair_hemisphere,blank}`; composites: `neg_inline_geometry_{wkt,geojson,bbox}` | integer / DMS / query-string / UTM coordinates (and named false rejects — schema docstring) |
| Closed enums — **seven of eight** controlled (0.4.0: `ThresholdSource`) | all | `neg_unknown_{unit_kind,time_step,modality,direction,claim,tier,threshold_from}` · `neg_vital_tag_driver` (VitalTag) | a wrong-but-legal value |
| Closed classes — metrics only (SO-3) — root, evaluation, part | all | `neg_document_extra_key` (root) · `neg_per_patient_predictions` (evaluation) · `neg_budget_extra_key` (part) | per-patient values inside a free-text slot; extra keys on the other 8 classes (same generator path, **not controlled**) |

**Finding of record (M-1c).** A LinkML rule postcondition written as a bare `{required: true}` is emitted by
gen-json-schema as `then: {required: [x]}` with no type, while the slot itself is typed `["string","null"]`. So
**`owner: null`, `owner: ''` and a bare YAML `owner:` all satisfied "a lever names its owner" under both validators.**
Both rules now carry `all_of: [{range: string, pattern: '\S'}]`, which the generator emits typed and non-null. Any
LinkML schema in the fleet that relies on a rule postcondition for presence has the same hole (ASOAtlas's
`neg_revoked_without_revoked_by`, for one, may be worth a null twin; memo, not an edit — peer vaults are read-only).

## Known limits — a validator's job, not the schema's

Named so that nobody reads them as implied:

1. **Referential integrity.** `stream_ref`, `event_ref`, `unit_ref`, `parent_unit`, `event_variable_stream` and
   `data_pins[].stream_ref` are checked for *shape*, never for *resolution*. The negatives deliberately reference
   undeclared `atl_*_example` objects and still fail only on their named defect. `owner_ruling_ref`,
   `limitations_ref` and `shap_summary_ref` are not checked to exist.
2. **Uniqueness.** Two objects with the same id in one document both validate.
3. **Cross-field and cross-object equality.** `base_rate = n_positives / n_test`; `n_positives ≤ n_test`;
   `data_pins` ⊇ the streams the vitals read; a surveillance ablation present iff a stream declares
   `surveillance_channel: true` (T5); `AtlDataPin.sha256` = the stream's `sha256`.
4. **Warnings.** `mpa_zone` without `external_id` SHOULD warn. LinkML rules have no warning severity, and an error
   would be wrong, so it is not enforced at all.
5. **`ifabsent` is not applied by either validator.** `claim` and `tier` defaults document intent for generators;
   `claim` is required and must be written.
6. **External ids are not looked up.** `WoRMS:233015`, `WDPA:<id>` and `CF:<name>` are CURIE-shaped only.
7. **The board entry's embedded `evaluation` block is not a closed `AtlEvaluation`.** It carries `event`, `patient`,
   `modelling_*`, `dropped_*`, `n_trees`, `n_vitals`, `vital_groups`, `sensitivity` and a `shap_summary` object, and
   its data pins carry `artifact`. `pos_exemplar_gulf_karenia_brevis` is the *projection* that validates. Reconciling
   the board schema with `AtlEvaluation` (embed the projection, keep the extras beside it) belongs to M-1d's BOARD
   generator (STATE WI-8, opened at M-1c close).
8. **Python-regex world only.** Both declared validators use Python `re`; no ECMA-262 validator is run. Known divergence,
   closed: Python's `$` matches before a trailing newline (ECMA's does not), so every `^…$` pattern now ends `(?!\n)$`
   (III review F-2; control `neg_sha256_trailing_newline`). The `geometry_ref` lookaheads are valid in both dialects.
   Free-text slots without a pattern (`split`, `learner`, `owner`…) accept a trailing newline in either dialect.
9. **Controlled on one class, asserted on its siblings by the generator only:** extra-key rejection on the 8 classes
   without their own control; `minimum_value`/`maximum_value` on the metric slots other than `base_rate`.
10. **A vital that reads no stream must still name one** (M-1b-i). `stream_ref` is required and there is no `calendar`
    modality, so the exemplar's season harmonics (`woy_sin`, `woy_cos`) point at the stream that defines the patient-week
    grid (FWC). Honest about the grid, silent about the calendar. v1 candidate: a `calendar` modality or an optional
    `stream_ref` for grid-only transforms.
11. **Cross-file references are not checked per file.** `linkml-validate` validates each registry alone, so a
    `stream_ref` in `features.yaml` naming a stream absent from `streams.yaml` passes. `atlantis_core.registry` (R1–R7)
    checks these across files, together with the transform grammar, the window rule and the climatology-era rule. Its
    tests plant each defect.
12. **Declared vs fetched is a stage, not a type (0.3.0).** A stream with neither `sha256` nor `ingested_at` validates as
    *declared*; nothing in the schema says whether an instance is past its first fetch. `atlantis_core.conform --stage
    fetched` requires both on every stream, and that each hash equals the cache summary's.
13. **Nominal vs realised is a field, not a guarantee (0.4.0).** `rate` is the budget the threshold was set for; `realised_rate`
    is what it flagged on test. The schema requires the second only when `threshold_from: validation` is stated, so an
    entry that says nothing about its threshold (the v0/v1 shape) still validates. The F-8 obligation — no new entry with a
    test-derived threshold — is the board emitter's (`atlantis_core.board.assert_thresholds_fixed`), not the schema's.

## Validation history

### M-0 (2026-10-02, smoke only)

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

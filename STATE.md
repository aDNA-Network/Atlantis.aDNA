---
type: state
status: p1_open
phase: "P1 — Core canonisation; every lane complete (M-1a · M-1c · M-1b-i · M-1b-ii-a 2026-10-02; M-1b-ii-b · M-1d-i · M-1d-ii 2026-10-03) → P1 gate (fable, operator) queued"
campaigns: [campaign_atlantis_genesis]
mission: p1_gate   # queued (fable, operator-summoned); M-1d-ii ✅ 2026-10-03; M-1d-i ✅ · M-1b-ii-b ✅ 2026-10-03; M-1b-ii-a ✅ · M-1b-i ✅ · M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261004_002004_m1d_ii_lattice_and_registries (opus)
created: 2026-09-23
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete, m1b_i_complete, m1b_ii_a_complete, m1b_ii_b_complete, m1d_i_complete, m1d_ii_complete, p1_gate_queued]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona Proteus ruled; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all **ratified 2026-10-02**).
4. The exemplar is at hygiene (M-1a): `what/exemplars/gulf_karenia_brevis/README.md` §Provenance · `uv sync && .venv/bin/python -m pytest` · self-test green.
5. The ontology is controlled (M-1c; 0.3.0 at M-1d-i): `what/schema/atl_v0/README.md` (proof table · known limits) · `LINKML_BIN=<scratch venv>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` → ALL WORLDS AGREE (45 controls).
6. III review goes through `iii/` in a fresh context (SO-10).
7. The core (M-1b-i + ii-a + ii-b + M-1d-i + M-1d-ii): `what/atlantis_core/README.md` · `cd what/atlantis_core && uv sync && .venv/bin/python -m pytest` (475, ~2 min unloaded) ·
   `.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` (all-stream, SO-7) ·
   `python -m atlantis_core.run --instance …` (→ `outputs/atlantis_core/`, ~7 min) · `python -m atlantis_core.board …` (→ `what/board/entries/`) ·
   `python -m atlantis_core.site --instance …` (→ the instance's page, ~2 s) · `python -m atlantis_core.mapping --check <mapping.yaml>` ·
   **a new instance:** `how/skills/skill_atlantis_instance_fork.md` → `atlantis_core.fork` · `conform` · `selftest` (receipt) · `fetch` (gated).
8. The method as one pipeline (M-1d-ii): `how/lattices/lattice_atlantis_pipeline.lattice.yaml` · `python -m atlantis_core.lattice` ·
   `atlantis_core.runspec --plan` · `what/board/BOARD.md` (`board --index --check`) · `atlantis_core.datasets --check ../datasets` ·
   `who/governance/contribution_guide.md` (draft).

## ⏭ QUEUED — Next Live Session

**M-1d-ii complete 2026-10-03** (opus; AAR `missions/aar/aar_m1d_ii_lattice_and_registries.md`). **Every P1 lane is closed.**
- **The pipeline lattice** (`how/lattices/lattice_atlantis_pipeline.lattice.yaml`) passes three checks: the strict schema,
  the peer `validate_lattice_file`, and local invariants (dominance for every gate · AST flags and `__main__` · run block =
  runspec).
- **`atlantis_core.runspec`** is a closed vocabulary (it rejects rather than coerces, and executes nothing — operator
  ruling).
- **`BOARD.md`** is generated, byte-stable and `--check`ed; v0 is labelled open-shape and pinned, and its supersession is
  derived. **WI-8 closed.**
- **`board --entries`** lets an instance keep its own board, and it cannot write Atlantis's.
- **Dataset pairs:** the template is fixed against its schema; three pairs; `datasets --check`. **WI-18 closed.**
- **The contribution guide** is draft 0.1.0, raised for ratification.
- **III:** PASS-WITH-FINDINGS, 2 major, 7 minor and 5 notes, **14/14 addressed**. Learning store: C-018…C-021 new;
  C-002, C-012 and C-015 reach 2.
- **Tests:** 475. The byte-stable set is unchanged.
- **Budget:** ≈177 kT main (≈ +77%) + ≈231 kT reviewer. At the post-review SITREP the operator ruled "fix all, then close".

**Next: the P1 gate** (fable, operator-summoned). Then M-2 (FKNMS, opus) → P2 gate.

**Next Session Prompt (self-contained, P1 gate):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. Every P1 lane is closed: M-1a, M-1c, M-1b-i and M-1b-ii-a (2026-10-02);
> M-1b-ii-b, M-1d-i and M-1d-ii (2026-10-03). Run the **P1 exit gate** at **fable**. It is an operator-summoned sitting
> (SO-1). Nothing advances to P2 without Stanley's explicit GO. Read, in order:
> 1. STATE;
> 2. the charter's §P1 exit bar (`how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md`);
> 3. the AARs of M-1d-i and M-1d-ii (`missions/aar/`), with M-1a, M-1b-i, M-1b-ii-a, M-1b-ii-b and M-1c as needed.
>
> Open a session lease. Then:
> - **(a) Verify the exit bar first-hand. Do not take the AARs' word for it:**
>   1. a fresh instance forks from templates alone, self-test green before any fetch: re-run the M-1d-i dry run shape
>      in the scratchpad, `fork` → `conform` → `selftest`, with no network;
>   2. `atlantis_core` reproduces the exemplar's metrics (`tests/test_eval.py` port equivalence);
>   3. the `atl_v0` controls give ALL WORLDS AGREE;
>   4. every lane carries an III review via `iii/`;
>   5. also: `python -m atlantis_core.lattice` · `board --index --check` · `datasets --check ../datasets` · the full
>      suite (475).
> - **(b) Run an adversarial pass of your own** over P1 as a whole: what would a first outside steward trip on?
> - **(c) Surface the operator decisions with `AskUserQuestion`.** Never decide them yourself:
>   1. **GO / NO-GO for P2**;
>   2. **ratify ADR-002 A-1** (the exemplar's explainer pages join §4's exception);
>   3. **ratify `who/governance/contribution_guide.md`** (draft 0.1.0);
>   4. **C-004 / C-009 graduation** to III.aDNA (frequency 3; ADR-003 ceremony);
>   5. whether to push `main` to `origin`. Local `main` is ahead of `origin/main` by every P1 commit; pushing publishes
>      the public repo, which is an outward act and the operator's.
> - **(d)** Write the gate's 4-field ratification blocks for whatever is ruled. Update STATE, the charter and the
>   CHANGELOG. Queue M-2 (`missions/mission_m2_*`, opus) if GO.
> - **(e) Memos after the gate** (peer vaults are read-only, so these are coordination memos; see WI-9, WI-16, WI-17,
>   M-1d-ii AAR §Follow-up): Rosetta (lattice_validate) · lattice-labs / Datasets.aDNA (dataset schema) · DDX (runspec
>   unknown keys) · Neo4j (`atl_` labels) · Hestia (router row category).

## What's in place

### M-1d-ii (2026-10-03 — commits `3e787d3`…`8ca7bc5` + close)

- **Lattice:** `how/lattices/lattice_atlantis_pipeline.lattice.yaml` with `atlantis_core.lattice`. It is checked three
  ways: the strict schema (a byte-identical copy), the peer validator imported by path, and local invariants (edge
  references · ids · acyclic · connected · gate dominance · AST flags and `__main__` · run block = runspec).
- **Runspec:** `atlantis_core.runspec` + `how/templates/template_runspec.example.json`. A closed vocabulary that
  validates and plans; exit 3 = REJECT.
- **Board:** `board --index [--check]` → `what/board/BOARD.md`. Every entry is checked, or the render refuses. v0 is
  open-shape, pinned by id and sha256, with supersession derived. `board --entries <repo>/what/board/entries`.
- **Datasets:** `atlantis_core.datasets --check`. The template is fixed, with its schema copied beside it. Three pairs;
  the env-covariates note is superseded in place.
- **Governance:** `who/governance/contribution_guide.md` (draft) · `who/coordination/inbox/`.
- **Tests:** 330 → 475.
- **Findings of record:**
  - two gates checked a proxy (`--outputs`; reachability for dominance);
  - validated strings could still write markdown onto the board;
  - an open-shape record's only closure is its bytes;
  - "nothing in the workspace passes" was 2 of 26 (corrected).


### M-1d-i (2026-10-03 — commits `999a9fa`…`16558df` + close)

- **Ontology:** atl_v0 0.3.0, a declared stream validates (`sha256` ⇒ `ingested_at`); 45 controls; contract v0.2.0 amended in place.
- **The core:**
  - `fetch` CLI: the receipt gate (semantic hash + self-test code) and the posture gate (a signed Ratification row inside
    the instance);
  - R8;
  - `fork` (`how/templates/template_instance/`, 27 refusals, pre-write R1–R8);
  - `conform` (items 1–12, 57 tests).
- **The self-test:**
  - the event stream may have any shape, and carries the label-exposing gaps;
  - C5 runs the mirror direction;
  - C8 is calendar-lag invariance;
  - comparisons are NA-safe;
  - the 12-defect catalogue runs in two forked worlds.
- **Skill:** `how/skills/skill_atlantis_instance_fork.md`.
- **Dry run:** a fictional Sandbar Estuary instance; items 1–8 and 11–12 ✅; 0 sockets (in-process guard); the word-flip
  ratification is refused.
- **Tests:** 330. The byte-stable set is unchanged.
- **Findings of record:**
  - the self-test had been point-only;
  - `gap_week` was a blind-spot relocation (C-015);
  - the posture gate was bypassable (C-016, C-017);
  - the exemplar is a reference run, not a conformant instance.


### M-1b-ii-b (2026-10-03 — commits `d0d0c14`…`dc8763a` + close)

- **`atlantis_core.site`:**
  - The template holds structure, style and generic renderers, and a literal guard keeps it free of exemplar words.
  - `assemble` builds the site data from core outputs, processed tables, registries and `site.yaml`, never from `hab`.
  - The build re-projects the run against the cited board entry field by field, ties `shap.npz` to the run, and enforces
    one copy grammar at build and render.
- **The exemplar's copy** was moved verbatim (366/366 text nodes), then corrected for v1 in a separate commit:
  - calendar lags;
  - R7;
  - F-8;
  - net beside gross;
  - the T2 panel;
  - the raw-stream what-if;
  - the reproduce section;
  - the footer.
- **The v1 page** is browser-checked.
- **Mapping:** `template_mapping_atl.yaml` + `atlantis_core.mapping --check` (28 planted defects).
- **`src/hab/ARCHIVED.md`:** the per-module table of what still runs.
- **Tests:** 183 total. The byte-stable set is unchanged since `4bb1939`.
- **Findings of record:**
  - `hab` is still the fetch path;
  - v0's EDA was stale against its own region rules (disclosed on the page);
  - the grey bands had been invisible since v0 (fixed);
  - the case rule was mis-described since v0 (fixed).
- **III:** PASS-WITH-FINDINGS, 10/10 addressed. Learning store: C-004 and C-009 +1, C-011…C-013 new.


### M-1b-ii-a (2026-10-02 — commits `e8751e5` · `b10ec48` · `bf0b36a` · `8edfc87` + close)

- **The package** gains `eval` (learners as config: xgboost · logistic; metrics; lead, which is direction-aware; rolling, with R7
  verified per fold), `explain` (interventional SHAP; exact linear SHAP with `availability:` flags; net group attribution;
  what-if as config), `board` (the closed `AtlEvaluation` plus allowlisted extras; refuses unhonoured obligations) and `run`.
  125 tests.
- **Port equivalence:**
  - eval → `metrics.json` exact to 1e-12;
  - SHAP → `shap_summary.json` exact;
  - the projector reproduces the M-1c fixture field for field.
- **Board v1** `what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json`: 0.8938 / 0.5388 · lead flagged 0.636 → 0.682 ·
  semantic hash `acfa22c6e4`. Regenerated in place after review, by ruling; the regeneration is recorded in its extras.
- **Findings of record:**
  - `hab`'s what-if edited a mean of logs as a log of the mean (proven), and scaled Tampa's non-lever gauge silently;
  - T2: the ranking is learner-invariant, the explanation is not;
  - absence of a stream encodes unit identity.
- **III:** PASS-WITH-FINDINGS, 8/8 addressed (F-8 disclosed and carded); learning store C-008…C-010.


### M-1b-i (2026-10-02 — 5 commits `67c602b`…`767ea73` + close)

- **The package**, `what/atlantis_core/` (89 tests, offline):
  - `config` (with `semantic_hash`) · `registry` R1–R7, the cross-file checks that linkml-validate can't make;
  - `grid`: rules, polygons/WDPA, cells;
  - `fetch`: ArcGIS, ERDDAP and NWIS built; NDBC, OBIS, GBIF and CRW declared;
  - `vitals`: the whitelisted grammar and its evaluator, with calendar lags;
  - `label`: above/below with both drop counts;
  - **`selftest`**: C0–C7, two patients, a gap world, the row filters in the invariance set, and the horizon checked from
    inside. 16 planted defects are each caught by name.
- **The exemplar as an instance:** `streams.yaml` · `features.yaml` (25 `AtlVital`s) · `events.yaml` all pass linkml-validate
  and the committed JSON Schema. `atlantis.yaml` is drift-guarded against `config.yaml`.
- **Finding of record:** `hab`'s SST lags were counted in rows across 20 missing OISST weeks. That is not leakage; it touches
  87–133 train rows, and fixing it moves AUPRC 0.547 → 0.539. The operator ruled calendar-correct.
- **Also found:** a climatology normal is a whole-era statistic (C6 reports it). The exemplar's discharge era overlaps the 2016
  rolling fold, so R7 records an obligation to refit per fold.
- **III review:** PASS-WITH-FINDINGS, 11/11 fixed; learning store C-005…C-007.

### M-1c (2026-10-02 — 6 commits `885b8a7`…)

- `atl_v0` **0.2.0, controlled**: 42 controls (3 pos · 39 neg) under linkml-validate + committed JSON (desc-off) + scratch
  JSON (desc-on); `atl_ontology_v0.schema.json` committed, byte-checked each run; Rule 4 asserted; the instrument proven to fail
  (3 sabotages + 7 per-arm). Rulings: alert_budgets ≥ 1 now; geometry_ref denylist. Fit matrix: 30 enum values, 0 bound /
  30 local; Modality vs GOOS EOV → local, EOV = v1 stream annotation. README: proof table + 9 known limits.
- Finding of record: bare-`required` rule postconditions are emitted untyped, so `owner: null` passed both validators. Closed with typed `all_of`.
- `iii/` → `how/federation/iii/` (III v0.6.0 @ `be7dba1`); SO-10; learning store C-001…C-004.

### M-1a (2026-10-02 — 8 commits `173613e`…)

- Exemplar hygiene: README/site/AGENTS drift fixed (log-loss stopping · 1,000 SHAP rows · "three streams plus the calendar") · `hab.provenance` + three `*_fetch_summary.json` with sha256 (== board `data_pins` == `what/datasets/` copies) · `pyproject.toml` + `uv.lock` (requirements.txt retired, matplotlib dropped) · `gauges.*.lever` read by code · region rules via `ast` whitelist, `tests/test_regions.py` freezes the 9 counts · T4 negative control `outputs/negative_control_auprc_stop.json` (2 trees, slope 18.09). `config.yaml` + `metrics.json` byte-stable; self-test green.
- Finding of record: `config_hash e9dea88254` = training-time config (`shap.background_n: 2000`); live file → `979d3fdf16`. Explained in README §Provenance; semantic hash → M-1b.

### M-0 (2026-10-02 — 6 commits on `aec55d4`)

- **Governance:** ADR-000 (lineage amended) · ADR-001 (persona · Framework + reference implementation · `what/atlantis_core/`) · ADR-002 (remit widening · five layers · snapshot rule · what crosses / never crosses) — all `proposed`.
- **Planning artifacts:** thesis register (12 claims, 9 supported-by-one-exemplar, 3 untested) · instance contract v0 (12-item checklist, 7 `ATL-*` ids) · roster + 9 cards · P2 ruling (FKNMS coral) · charter re-cut.
- **L1 ontology:** `what/schema/atl_v0/` — LinkML draft, 5 classes / 7 enums / 2 rules; lint 0 errors / 38 warnings; closed JSON Schema generates (18 defs; not committed); smoke pos/neg validated; **NO VALIDATION CLAIM** until M-1c. Crosswalk 6 bound / 6 deferred.
- **L4 registries:** evidence board v1 + exemplar entry (script-generated from `metrics.json`, sha256 pins) · model-card template · dataset-pair template · hypothesis-ledger spec · `what/datasets/AGENTS.md`.
- **L2 / L3 / L5:** specified and carded (M-1b · M-1d/M-3/M-5 · M-4); nothing built — by the sitting-depth ruling.
- Exemplar untouched at M-0; self-test green at open and close.

## Active blockers

- None blocking. **The P1 gate is operator-summonable at fable** (`#needs-human`). At it: ADR-002 A-1 · the contribution
  guide · C-004/C-009 graduation · GO/NO-GO for P2 · whether to push `main` (ahead of `origin/main` by every P1 commit).

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- ~~WI-7~~ **closed 2026-10-02 (M-1b-ii-a)** — board v1's `config_hash` is the semantic hash (`acfa22c6e4`; its boundary set by effect, III F-2) with the bytes-md5s beside it; `hab`'s `e9dea88254` stays explained in exemplar README §Provenance.
- ~~WI-8~~ **closed 2026-10-03 (M-1d-ii)** — `BOARD.md` is generated by `board --index`. v0 is rendered and labelled
  open-shape (grandfathered by id + sha256), and v1 is closed. Original text follows. The board entry's embedded `evaluation` is **not** a closed `AtlEvaluation` (extra keys: `event`, `patient`, `modelling_*`,
  `dropped_*`, `n_trees`, `n_vitals`, `vital_groups`, `sensitivity`, a `shap_summary` object; pins carry `artifact`). The `§11`
  limitations label was hand-fixed at M-1c with a provenance note. Closes when M-1b's board emitter / M-1d's BOARD generator emits the
  validated projection (= `pos_exemplar_gulf_karenia_brevis.yaml`'s evaluation) with the extras beside it.
  **Update 2026-10-02 (M-1b-ii-a):** the emitter exists and v1 is closed + validated; v0 keeps its open shape (untouched). Closes at
  M-1d's BOARD generator.
- ~~WI-10~~ **closed 2026-10-02 (M-1b-ii-a)** — noted on board v1; v1's 2016 fold is refit (verified per fold). Immaterial here
  (0.8810 unrefit vs 0.8808 refit), material elsewhere by construction.
- WI-11 — **F-8 (disclosed, not fixed):** alert-budget and lead-time thresholds are test-score quantiles; rolling folds testing
  2017–2019 reuse a tree count early-stopped on them. Fix carded: `how/backlog/idea_eval_thresholds_fixed_on_validation.md` → a new
  board version, before any steward-facing budget claim.
- WI-12 — v1 schema candidates from ii-a: a unit × stream "structurally absent" declaration (absence encodes unit identity) and
  lever-ness per station or source rather than per vital (Tampa's non-lever gauge under a lever-tagged vital).
- WI-13 — **ADR-002 A-1 PROPOSED 2026-10-03** (III F-5): the exemplar's explainer pages join §4's capped exception
  (exemplar-only, derived from the public parquets, rebuildable, never an instance page). Ratify at the P1 gate or before.
- WI-14 — Board v1's `limitations_ref` points at the v0 page's `#limits`, which lacks v1's limits (III F-6). v1 stays
  byte-stable; **board v2** (with the F-8 fix) repoints it to `site/gulf_karenia_brevis_v1.html#limits`.
- ~~WI-15~~ **closed 2026-10-03 (M-1d-i)** — `python -m atlantis_core.fetch` exists, gated on the self-test receipt and a ratified
  posture. `hab.fetch_*` is now only the recipe that produced the committed bytes; a live core re-fetch has not been run.
- WI-16 — Neo4j substrate allow-list admission for the five `atl_` labels and six edge types (`template_mapping_atl.yaml`
  header): a coordination memo to `Neo4j.aDNA` after the gate.
- WI-17 — `aDNA.aDNA/what/lattices/tools/lattice_validate.py` has no CLI (and its docstring import path is stale). M-1d-ii
  imports it; memo to Rosetta after the gate.
- ~~WI-18~~ **closed 2026-10-03 (M-1d-ii)** — the template is fixed and validated (schema copy beside it). The upstream
  note goes by memo (24 of 26 workspace `.dataset.yaml` fail it). Original text follows: `how/templates/template_dataset_pair/` fails the lattice-labs `dataset_yaml_schema.json` it claims (sha256
  placement, `storage.location`/`provider`, lineage keys). M-1d-ii fixes the template; the upstream note goes by memo.
- WI-19 — `NDBCStdmet` (and OBIS, GBIF, CRW) are declared, not built. The first instance with a buoy stream needs NDBC; it
  is built in `atlantis_core` (the P2 rule). M-2 (gridded-only) does not need it.
- WI-20 — III learning store: C-004 and C-009 are at frequency 3, graduation candidates for the ADR-003 ceremony at
  III.aDNA. Operator's call, at the P1 gate or after.
- WI-21 — The exemplar is not a conformant instance (no `units.yaml`, `mapping.yaml` or posture pin). Optional: give it the
  first two, so that items 1 and 11 pass; its posture stays the ADR-002 §4 grandfathered exception.
- WI-22 — M-1d-ii memo candidates after the gate:
  - **Rosetta:** `lattice_validate.py`, beyond WI-17. It never loads `additionalProperties`, has no cycle check, and its
    package `__init__` eagerly imports the canvas tools.
  - **lattice-labs / Datasets.aDNA:** 24 of 26 workspace `.dataset.yaml` fail `dataset_yaml_schema.json`, and its
    `location.path` "absolute" is unsuited to public repos.
  - **DDX:** its runspec drops unknown keys rather than rejecting them.
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → ~~M-1c~~ ✅ → ~~M-1b-i~~ ✅ → ~~M-1b-ii-a~~ ✅ → ~~M-1b-ii-b~~ ✅ → ~~M-1d-i~~ ✅ → ~~M-1d-ii~~ ✅ → **P1 gate** (fable; ratify ADR-002 A-1 + the contribution guide; C-004/C-009 graduation; push decision). 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

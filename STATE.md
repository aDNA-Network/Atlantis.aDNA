---
type: state
status: p1_open
phase: "P1 gate MET 2026-10-03 — CONDITIONAL GO P2; condition (a) M-1e ✅ 2026-10-03 → M-2a queued (P2 opens) → M-2b → P2 gate"
campaigns: [campaign_atlantis_genesis]
mission: mission_m2a_fknms_fork_and_fetch   # queued (opus); M-1e ✅ 2026-10-03 (board v2); P1 gate ✅ 2026-10-03 (conditional GO); M-1d-ii ✅ 2026-10-03; M-1d-i ✅ · M-1b-ii-b ✅ 2026-10-03; M-1b-ii-a ✅ · M-1b-i ✅ · M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261004_035631_m1e_thresholds_on_validation (opus)
created: 2026-09-23
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete, m1b_i_complete, m1b_ii_a_complete, m1b_ii_b_complete, m1d_i_complete, m1d_ii_complete, p1_gate_met, p2_conditional_go, m1e_complete, board_v2, atl_v0_0_4_0, m2a_queued]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona Proteus ruled; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all **ratified 2026-10-02**).
4. The exemplar is at hygiene (M-1a): `what/exemplars/gulf_karenia_brevis/README.md` §Provenance · `uv sync && .venv/bin/python -m pytest` · self-test green.
5. The ontology is controlled (M-1c; 0.3.0 at M-1d-i; 0.4.0 at M-1e): `what/schema/atl_v0/README.md` (proof table · known limits) · `LINKML_BIN=<scratch venv>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` → ALL WORLDS AGREE (50 controls).
6. III review goes through `iii/` in a fresh context (SO-10).
7. The core (M-1b-i + ii-a + ii-b + M-1d-i + M-1d-ii): `what/atlantis_core/README.md` · `cd what/atlantis_core && uv sync && .venv/bin/python -m pytest` (516, ~2.5 min unloaded) ·
   `.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` (all-stream, SO-7) ·
   `python -m atlantis_core.run --instance …` (→ `outputs/atlantis_core/`, ~7 min) · `python -m atlantis_core.board …` (→ `what/board/entries/`) ·
   `python -m atlantis_core.site --instance …` (→ the instance's page, ~2 s) · `python -m atlantis_core.mapping --check <mapping.yaml>` ·
   **a new instance:** `how/skills/skill_atlantis_instance_fork.md` → `atlantis_core.fork` · `conform` · `selftest` (receipt) · `fetch` (gated).
8. The method as one pipeline (M-1d-ii): `how/lattices/lattice_atlantis_pipeline.lattice.yaml` · `python -m atlantis_core.lattice` ·
   `atlantis_core.runspec --plan` · `what/board/BOARD.md` (`board --index --check`) · `atlantis_core.datasets --check ../datasets` ·
   `who/governance/contribution_guide.md` (draft).

## ⏭ QUEUED — Next Live Session

**M-1e CLOSED 2026-10-03 — P2 condition (a) MET; P2 opens at M-2a.** Board v2 (`what/board/entries/2026-10-03_gulf_karenia_brevis_v2.json`)
is the same model as v1, with model bytes identical, AUROC 0.8938 / AUPRC 0.5388 and 141 trees. Its alert thresholds are
**fixed on validation** before test is scored, and every budget states its realised test rate beside the nominal one
(0.0378 / 0.0811 / 0.1933 at 5 / 10 / 20%). Lead time at the 10% budget's fixed threshold flags 0.636 of 22 onsets. Every
rolling fold selects its own tree count. atl_v0 is 0.4.0, and the v2 page is `site/gulf_karenia_brevis_v2.html`. III 8/8.
**Disclosed, not fixed:** the label horizon crosses every split boundary. The embargo is carded as board v3.

**Next: M-2a** (opus) → M-2b → **P2 gate** (fable). **Pending operator rulings:**
- the **push** (7 commits since `origin/main`, gitleaks-clean);
- where the **horizon embargo** lands (with M-2b, or its own lane before the P2 gate).

**Next Session Prompt (self-contained, M-2a):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P2 is open: the P1 gate's conditional GO is satisfied (M-1e closed
> 2026-10-03, board v2). Run **M-2a — `FloridaKeysCoral.aDNA`, from fork to fetched data** at **opus**. Read, in order:
> 1. STATE;
> 2. `how/campaigns/campaign_atlantis_genesis/missions/mission_m2a_fknms_fork_and_fetch.md` (its acceptance criteria govern);
> 3. `how/skills/skill_atlantis_instance_fork.md`;
> 4. `how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md`;
> 5. `how/campaigns/campaign_atlantis_genesis/artifacts/p2_second_instance_ruling.md`;
> 6. the M-1d-i AAR (fork, conform, the dry run's findings);
> 7. `what/atlantis_core/README.md` (§Known limits incl. 2b).
>
> Open a session lease. **Do condition (c) first:** check whether NOAA Coral Reef Watch (DHW / HotSpot / SST) is reachable
> through the built `ERDDAPGriddap` fetcher (dataset id, variables, grid, licence). If it is not, stop and card a
> `CoralReefWatch` fetcher Atlantis-side (WI-19); never build it in the instance.
>
> Watch for:
> - the instance is a **new vault at the workspace root**: follow the fork skill and workspace Rule 3, and send the router
>   row to Hestia by memo;
> - **zero instance-local patches to `atlantis_core`**: every gap is an Atlantis-side change, listed in the AAR;
> - the persistent DHW event needs the self-test generalised Atlantis-side, with the **whole** defect catalogue re-run
>   (C-014), green before any fetch;
> - provenance fields are computed from what the code did, never stamped from config (C-023, M-1e);
> - a guard is proven by a plant in the real code path (C-009, now frequency 4).
>
> Budget honestly (~150–200 kT; P1's overruns ran +77% to +130%); at more than +50% over, SITREP and ask. Run the III
> review via `iii/` in a fresh context (SO-10). Make path-scoped commits; file the AAR. Then queue M-2b.

## What's in place

### M-1e (2026-10-03 — commits `20075f1`…`4bda9b5` + close) — P2 condition (a)

- **eval:** `threshold_from: val` fixes thresholds on the selection model's val scores and reads them back from the result.
  `rolling_selection: per_fold` makes each fold early-stop on its inner year with eras ≤ Y−1, checked on what `fit`
  received. A stop year with < 5 positives skips its fold, and says so. Lead time records `alert_threshold`. `test` /
  `full_model` exist only for the port.
- **atl_v0 0.4.0:** `threshold_from` · `realised_rate`, with the rule validation ⇒ realised required (typed `all_of`). 50 controls.
- **board v2:** emitted by code. A single cause is proven by bytes. The emitter refuses F-8 for the headline and every swap,
  by identity and arithmetic. `BOARD.md` budgets show the threshold source and realised rate.
- **The v2 page:** a new file from `site_v2.yaml` and `site_copy_v2.yaml`; the site reads a named run (`outputs:`, `--site`).
- **Tests:** 480 → 516. Plants P1–P4 are written into eval's own source.
- **Findings of record:**
  - every realised rate falls below nominal (two likely reasons, neither proven);
  - per-fold selection is noisy (63–623 trees);
  - the label horizon crosses every boundary (disclosed; embargo carded);
  - C-023: provenance stamped from intent emits clean.
- **III:** PASS-WITH-FINDINGS, 8/8 addressed. Learning store: C-009 → 4, plus C-022 and C-023.


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

- None blocking M-2a.
- `#needs-human`: **the push.** 7 commits since `origin/main` (`20075f1`…close). gitleaks exit 0 over `origin/main..HEAD`;
  no file is over 1 MB (largest: the v2 page, 0.85 MB); no data files. Board v2 has never left this machine, so it can
  still be corrected in place until then.
- ~~push~~ **done 2026-10-03** (operator ruling): `cec155b..33fb62d` → `origin/main`, after gitleaks over the range
  (one false positive → a narrow match-only allowlist, tested), no file over 1 MB, no data files, 480 tests green.
- `#needs-human`: **delivering the graduation memo** into `III.aDNA/who/coordination/`. That is a peer-vault write, for an
  operator-opened session.

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
- ~~WI-11~~ **closed 2026-10-03 (M-1e):** board v2. Original text follows. **F-8 (disclosed, not fixed):** alert-budget and lead-time thresholds are test-score quantiles; rolling folds testing
  2017–2019 reuse a tree count early-stopped on them. Fix carded: `how/backlog/idea_eval_thresholds_fixed_on_validation.md` → a new
  board version, before any steward-facing budget claim.
- WI-12 — v1 schema candidates from ii-a: a unit × stream "structurally absent" declaration (absence encodes unit identity) and
  lever-ness per station or source rather than per vital (Tampa's non-lever gauge under a lever-tagged vital).
- ~~WI-13~~ **closed 2026-10-03 (P1 gate): A-1 RATIFIED.** Was: **ADR-002 A-1 PROPOSED 2026-10-03** (III F-5): the exemplar's explainer pages join §4's capped exception
  (exemplar-only, derived from the public parquets, rebuildable, never an instance page). Ratify at the P1 gate or before.
- ~~WI-14~~ **closed 2026-10-03 (M-1e):** v2's `limitations_ref` → `site/gulf_karenia_brevis_v2.html#limits` (it names the fix
  and its residuals). The v1 page's limits still describe F-8 as open, which was true when it was published. Original text follows. Board v1's `limitations_ref` points at the v0 page's `#limits`, which lacks v1's limits (III F-6). v1 stays
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
- WI-19 — *(P1 gate: NDBC dropped from M-2; CRW checked via `ERDDAPGriddap` at M-2a open.)* `NDBCStdmet` (and OBIS, GBIF, CRW) are declared, not built. The first instance with a buoy stream needs NDBC; it
  is built in `atlantis_core` (the P2 rule). M-2 (gridded-only) does not need it.
- WI-20 — **graduation proposed 2026-10-03** (C-009 reached frequency 4 at M-1e, which strengthens the memo) (P1 gate ruling: memo filed, awaiting Argus + Stanley co-ratification at III.aDNA). III learning store: C-004 and C-009 are at frequency 3, graduation candidates for the ADR-003 ceremony at
  III.aDNA. Operator's call, at the P1 gate or after.
- WI-21 — The exemplar is not a conformant instance (no `units.yaml`, `mapping.yaml` or posture pin). Optional: give it the
  first two, so that items 1 and 11 pass; its posture stays the ADR-002 §4 grandfathered exception.
- WI-22 — M-1d-ii memo candidates after the gate:
  - **Rosetta:** `lattice_validate.py`, beyond WI-17. It never loads `additionalProperties`, has no cycle check, and its
    package `__init__` eagerly imports the canvas tools.
  - **lattice-labs / Datasets.aDNA:** 24 of 26 workspace `.dataset.yaml` fail `dataset_yaml_schema.json`, and its
    `location.path` "absolute" is unsuited to public repos.
  - **DDX:** its runspec drops unknown keys rather than rejecting them.
- WI-23 — **The label horizon crosses every split boundary** (M-1e III F-6; C-022). Disclosed on README 2b, the v2 page and board
  v2. The fix is carded: `how/backlog/idea_label_horizon_embargo.md` → board v3, its own cause. The operator places it, before
  the P2 gate compares the exemplar with FKNMS.
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → … → ~~M-1d-ii~~ ✅ → ~~**P1 gate**~~ ✅ 2026-10-03 (conditional GO) → ~~M-1e~~ ✅ 2026-10-03 → **M-2a** (opus) → M-2b → **P2 gate** (fable). 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

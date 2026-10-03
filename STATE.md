---
type: state
status: p1_open
phase: "P1 — Core canonisation; M-1a + M-1c + M-1b-i + M-1b-ii-a complete 2026-10-02; M-1b-ii-b queued, then M-1d → P1 gate"
campaigns: [campaign_atlantis_genesis]
mission: mission_m1b_ii_b_site_mapping_archive   # queued; M-1b-ii split 2026-10-02 → ii-a ✅ + ii-b; M-1b-i ✅; M-1b split 2026-10-02 → M-1b-i ✅; M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261003_033855_m1b_ii_a_core_eval_explain_board (opus)
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete, m1b_i_complete, m1b_ii_a_complete]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona Proteus ruled; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all **ratified 2026-10-02**).
4. The exemplar is at hygiene (M-1a): `what/exemplars/gulf_karenia_brevis/README.md` §Provenance · `uv sync && .venv/bin/python -m pytest` · self-test green.
5. The ontology is controlled (M-1c): `what/schema/atl_v0/README.md` (proof table · known limits) · `LINKML_BIN=<scratch venv>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` → ALL WORLDS AGREE (42 controls).
6. III review goes through `iii/` in a fresh context (SO-10).
7. The core (M-1b-i + ii-a): `what/atlantis_core/README.md` · `cd what/atlantis_core && uv sync && .venv/bin/python -m pytest` (125) ·
   `.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` (all-stream, SO-7) ·
   `python -m atlantis_core.run --instance …` (→ `outputs/atlantis_core/`, ~7 min) · `python -m atlantis_core.board …` (→ `what/board/entries/`).

## ⏭ QUEUED — Next Live Session

**M-1b-ii-a complete 2026-10-02** (opus; AAR `missions/aar/aar_m1b_ii_a_core_eval_explain_board.md`). M-1b-ii was split by
operator ruling. `atlantis_core` now trains, evaluates, explains and emits to the board.
- **The port is exact:** on `hab`'s vitals it reproduces every `metrics.json` key to 1e-12.
- **Board v1:** the exemplar through the core with calendar-correct SST lags and the R7 refit gives **0.8938 / 0.5388**
  (v0 0.8941 / 0.5473), the same n and drops. `config_hash` is semantic (closes WI-7), and the evaluation is the closed
  `AtlEvaluation`.
- **The T2 swap (logistic):** the ranking survives and the explanation does not.
- **III review:** 8/8 addressed. v1 was regenerated in place by ruling.

**Next: M-1b-ii-b** (opus), then **M-1d** → **P1 gate** (fable, operator).

> **Budget:** ii-a ran at about +35% (≈215 kT, under the trip) plus a ≈205 kT reviewer. ii-b is carded at ~150 kT, mostly
> prose extraction from a 76 KB template. Expect the site's copy to dominate, and budget the reviewer at the build's size.

**Next Session Prompt (self-contained, M-1b-ii-b):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P1 is open; M-1a, M-1c, M-1b-i and **M-1b-ii-a** are closed (2026-10-02). Run
> **M-1b-ii-b — `atlantis_core` site · mapping · archive** at **opus**. Read STATE → `how/campaigns/campaign_atlantis_genesis/missions/mission_m1b_ii_b_site_mapping_archive.md`
> (incl. §Inputs from ii-a) → the ii-a AAR (Findings 2–4) → `what/atlantis_core/README.md` → the exemplar's `src/hab/{export_site_data,build_site}.py`
> and `site/template.html` (76 KB, 12 sections) → board v1 `what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json`. Open a session lease.
>
> 1. **`atlantis_core/site/`**: a template with **all copy parameterised**. The exemplar's prose moves to an instance copy file; site
>    cases, risk strips and the vitals trace are config. Site data is assembled from `outputs/atlantis_core/` plus the gitignored
>    `data/processed/atlantis_core/` (regenerate with `python -m atlantis_core.run`). Vital labels come from `features.yaml`.
>    The page must say what board v1 says: calendar lags, the R7 refit, the F-8 limits, and that a SHAP reading belongs to one
>    model. Keep `site/hab_crash_risk.html` (v0); write the core page beside it.
> 2. **`how/templates/template_mapping_atl.yaml`**: registries → the five `atl_` labels, bi-temporal stamps, and a fence excluding raw observations.
> 3. **Archive `src/hab/` in place** with a pointer (SO-2). `config.yaml` and `outputs/*.json` stay byte-stable. The port tests that read
>    `hab`'s `data/processed/` still run (archive ≠ delete).
>
> Run the SO-7 self-tests before any vitals or label commit. Budget honestly: at >50% over, SITREP and stop. Run the III review via
> `iii/` in a fresh context (SO-10). Make path-scoped commits. File the AAR at `missions/aar/aar_m1b_ii_b_site_mapping_archive.md`;
> the card goes `completed` only after it. Do not start M-1d.

## What's in place

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

- None. M-1b-ii-b is operator-summonable at opus.

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- ~~WI-7~~ **closed 2026-10-02 (M-1b-ii-a)** — board v1's `config_hash` is the semantic hash (`acfa22c6e4`; its boundary set by effect, III F-2) with the bytes-md5s beside it; `hab`'s `e9dea88254` stays explained in exemplar README §Provenance.
- WI-8 — The board entry's embedded `evaluation` is **not** a closed `AtlEvaluation` (extra keys: `event`, `patient`, `modelling_*`,
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
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → ~~M-1c~~ ✅ → ~~M-1b-i~~ ✅ → ~~M-1b-ii-a~~ ✅ → M-1b-ii-b (opus) → M-1d → **P1 gate**. 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

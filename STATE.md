---
type: state
status: p1_open
phase: "P1 — Core canonisation; M-1a + M-1c + M-1b-i complete 2026-10-02; M-1b-ii split → ii-a ACTIVE, ii-b queued, then M-1d → P1 gate"
campaigns: [campaign_atlantis_genesis]
mission: mission_m1b_ii_a_core_eval_explain_board   # ACTIVE (session_stanley_20261003_033855); M-1b-ii split 2026-10-02 → ii-a + ii-b; M-1b split 2026-10-02 → M-1b-i ✅; M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261003_014043_m1b_i_core_vitals_selftest (opus)
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete, m1b_i_complete]
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
7. The core is extracted (M-1b-i): `what/atlantis_core/README.md` · `cd what/atlantis_core && uv sync && .venv/bin/python -m pytest` (89) ·
   `.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` (all-stream, SO-7).

## ⏭ QUEUED — Next Live Session

> ⛩ **2026-10-02 — M-1b-ii-a ACTIVE** (lease `session_stanley_20261003_033855`). Operator ruled: split M-1b-ii → **ii-a** (eval · explain ·
> board · R7 refit · board v1 · semantic hash · logistic learner swap) + **ii-b** (site · mapping · archive `src/hab/`). The prompt below is
> the pre-split one, kept until ii-a closes.

**M-1b-i complete 2026-10-02** (opus; AAR `missions/aar/aar_m1b_i_core_vitals_and_selftest.md`). M-1b was split by operator ruling.
`atlantis_core` now carries registries, fetch (3 built + 3 declared protocols), grid, vitals, a direction-aware label and an
all-stream self-test (16 planted defects caught). The exemplar's vitals are reproduced exactly except the 3 SST-lag vitals:
`hab` counted those lags in rows across 20 missing OISST weeks, and the core counts calendar weeks (operator ruling). The III
review returned 11 findings and all 11 are fixed. **Next: M-1b-ii** (opus). Then **M-1d** → **P1 gate** (fable, operator).

> ⚠ **Budget:** M-1b-i ran about +70% on main context (≈240 kT), plus about 172 kT for the reviewer. The SITREP was given at
> the trip point and the operator ruled to fix everything. M-1b-ii's card says ~140 kT. The AAR's Change suggests carding it
> at about 1.7× and budgeting the reviewer at the build's size. Re-carding is the operator's call.

**Next Session Prompt (self-contained, M-1b-ii):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P1 is open; M-1a, M-1c and **M-1b-i** are closed (2026-10-02). Run **M-1b-ii —
> `atlantis_core` eval · explain · board · site** at **opus**. Read STATE → `how/campaigns/campaign_atlantis_genesis/missions/mission_m1b_ii_core_eval_explain_board.md`
> → the M-1b-i AAR (Findings 1 and 3) → `what/atlantis_core/README.md` → the exemplar's `src/hab/{train,explain,whatif,export_site_data,build_site}.py`
> (being replaced) and `outputs/metrics.json`. Open a session lease.
>
> Port into `atlantis_core`:
> - `eval/`: split from `atlantis.yaml`; alert budgets, lead time, calibration and climatology baseline; ablations from vital
>   groups and the stream's `surveillance_channel`; rolling origin; the sensitivity threshold. The learner is a config field.
> - `explain/`: interventional SHAP, the additivity check, tags from `features.yaml`. What-if scenarios are config.
> - `board/`: emits the closed `AtlEvaluation` projection (validate it like `pos_exemplar_gulf_karenia_brevis.yaml`) with the
>   extras beside it (WI-8).
> - `site/`: the template with all copy parameterised.
>
> **Honour the R7 obligation** (`inst.obligations`): refit the discharge climatology per rolling-origin fold, and assert it in a test.
>
> **Reproduction bar (operator ruling):**
> - `hab` still reproduces `metrics.json` (0.8941 / 0.5473).
> - The core run uses calendar-correct SST lags. It lands as a **new board version** with the delta named (an in-memory refit
>   at M-1b-i gave about 0.8938 / 0.5388) and the same n, positives and drop counts.
> - The 2026-09-23 entry and `metrics.json` stay. Record `semantic_hash` beside the bytes-md5, which closes WI-7.
>
> **Also:**
> - Run one learner swap (LightGBM or logistic) on the core's vitals and record it as T2 evidence.
> - Write `how/templates/template_mapping_atl.yaml`.
> - Archive `src/hab/` in place with a pointer (SO-2), keeping `config.yaml` and `metrics.json` byte-stable.
> - SO-7: run `python -m atlantis_core.selftest` before any vitals or label commit.
>
> Budget honestly: at >50% over, SITREP and stop. Run the III review via `iii/` in a fresh context (SO-10). Make path-scoped
> commits. File the AAR at `missions/aar/aar_m1b_ii_core_eval_explain_board.md`; the card goes `completed` only after it.
> Do not start M-1d.

## What's in place

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

- None. M-1b-ii is operator-summonable at opus. Re-carding its budget (⚠ above) is the operator's call.

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- WI-7 — `metrics.json → config_hash` is a bytes-md5 and the recorded `e9dea88254` matches no committed `config.yaml` (training-time file had `shap.background_n: 2000`). Explanation of record: exemplar README §Provenance. `atlantis_core.semantic_hash` exists and is tested (M-1b-i); closes when M-1b-ii records it beside the bytes-md5.
- WI-8 — The board entry's embedded `evaluation` is **not** a closed `AtlEvaluation` (extra keys: `event`, `patient`, `modelling_*`,
  `dropped_*`, `n_trees`, `n_vitals`, `vital_groups`, `sensitivity`, a `shap_summary` object; pins carry `artifact`). The `§11`
  limitations label was hand-fixed at M-1c with a provenance note. Closes when M-1b's board emitter / M-1d's BOARD generator emits the
  validated projection (= `pos_exemplar_gulf_karenia_brevis.yaml`'s evaluation) with the extras beside it.
- WI-10 — `metrics.json → rolling_origin`: the 2015→2016 fold scores 2016 with a discharge normal (1990–2016) that contains
  2016 (M-1b-i AAR Finding 3). It is a diagnostic panel, not the headline. Note it on the board when M-1b-ii's new version lands;
  `atlantis_core` R7 makes the refit an obligation.
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → ~~M-1c~~ ✅ → ~~M-1b-i~~ ✅ → M-1b-ii (opus) → M-1d → **P1 gate**. 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

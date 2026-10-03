---
type: state
status: p1_open
phase: "P1 — Core canonisation; M-1a + M-1c complete 2026-10-02; M-1b queued, then M-1d → P1 gate"
campaigns: [campaign_atlantis_genesis]
mission: mission_m1b_i_core_vitals_and_selftest   # in progress (M-1b split 2026-10-02); M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261002_162046_m1c_linkml_controls (opus)
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete]
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

## ⏭ QUEUED — Next Live Session

> **In progress 2026-10-02 — M-1b-i** (opus; session `session_stanley_20261003_014043_m1b_i_core_vitals_selftest`). Operator ruled at open:
> **split M-1b** → `mission_m1b_i_core_vitals_and_selftest.md` (now) + `mission_m1b_ii_core_eval_explain_board.md` (next); fetchers = 3 real + 3 declared.
> The original M-1b card is `superseded` (kept). The prompt below is the pre-split one, retained until M-1b-i closes.

**M-1c complete 2026-10-02** (opus; AAR `missions/aar/aar_m1c_linkml_controls.md`). 42 controls, three worlds agree; `iii/`
adopted; III review PASS-WITH-FINDINGS (11/12 fixed, WI-8 carried). **Next: M-1b** (opus, carded 120–180 kT). Then **M-1d**
(M-1b + M-1c ✅) → **P1 gate** (fable, operator).

> ⚠ **Operator decision before M-1b opens — split it?** M-1c ran ≈5× its card (≈460 kT with the fresh-context reviewer;
> AAR Finding 4). M-1b is twice M-1c's carded size and also owes an SO-10 review. Suggested split: **M-1b-i** = package
> skeleton + `fetch/` + `grid/` + `vitals/` + `label/` + `features.yaml`/`streams.yaml`/`events.yaml` + **all-stream
> self-test**; **M-1b-ii** = `eval/` · `explain/` · `board/` · `site/` + metrics reproduction + learner swap + `mapping.yaml`.
> Re-carding is the operator's call; the prompt below runs M-1b whole unless told otherwise.

**Next Session Prompt (self-contained, M-1b):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P1 is open; M-1a and M-1c are closed (2026-10-02). Run **M-1b — extract
> `what/atlantis_core/`** at **opus** (ask the operator first whether to split it per STATE's ⚠ note). Read STATE →
> `how/campaigns/campaign_atlantis_genesis/missions/mission_m1b_atlantis_core_extraction.md` → the charter's P1 exit bar
> → `what/schema/atl_v0/README.md` (what the controls prove; known limits) → the exemplar `README.md` + `AGENTS.md` + `src/hab/`.
> Open a session lease. The registries (`streams.yaml` · `features.yaml` · `events.yaml`) are `AtlDocument`s: start from
> `what/schema/atl_v0/fixtures/controls/pos_exemplar_gulf_karenia_brevis.yaml` (already validated, values sourced) and
> validate every registry with `linkml-validate -C AtlDocument` (scratch venv, `LINKML_BIN`; nothing installed on the node).
> Schema changes: `run_controls.sh` must say ALL WORLDS AGREE before commit; add a control per new constraint. **SO-7:** the
> all-stream self-test perturbs *every* stream and runs before any vitals/label commit. The exemplar re-run reproduces
> `metrics.json` (AUROC/AUPRC to 3 dp; same n, positives, drop counts). Record a **semantic config hash** beside the
> bytes-md5 (closes WI-7). `src/hab/` is archived in place with a pointer (SO-2); `config.yaml`/`metrics.json` stay
> byte-stable. The board emitter is the start of WI-8 (emit the closed `AtlEvaluation` projection; keep the extras beside it).
> Budget honestly: at >50% over, SITREP and stop. Run the III review via `iii/` in a fresh context (SO-10). Path-scoped commits;
> AAR at `missions/aar/aar_m1b_atlantis_core_extraction.md`; card `completed` only after the AAR. Do not start M-1d.

## What's in place

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

- None. M-1b is operator-summonable at opus. The split question (⚠ above) is the operator's.

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- WI-7 — `metrics.json → config_hash` is a bytes-md5 and the recorded `e9dea88254` matches no committed `config.yaml` (training-time file had `shap.background_n: 2000`). Explanation of record: exemplar README §Provenance. Closes when M-1b's `atlantis_core` records a semantic hash alongside.
- WI-8 — The board entry's embedded `evaluation` is **not** a closed `AtlEvaluation` (extra keys: `event`, `patient`, `modelling_*`,
  `dropped_*`, `n_trees`, `n_vitals`, `vital_groups`, `sensitivity`, a `shap_summary` object; pins carry `artifact`). The `§11`
  limitations label was hand-fixed at M-1c with a provenance note. Closes when M-1b's board emitter / M-1d's BOARD generator emits the
  validated projection (= `pos_exemplar_gulf_karenia_brevis.yaml`'s evaluation) with the extras beside it.
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → ~~M-1c~~ ✅ → M-1b (opus; split?) → M-1d → **P1 gate**. 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

---
type: state
status: p1_open
phase: "P1 — Core canonisation; M-1a complete 2026-10-02; M-1c queued (∥ lane), then M-1b → M-1d → P1 gate"
campaigns: [campaign_atlantis_genesis]
mission: mission_m1c_linkml_controls   # queued; M-0 ✅ · M-1a ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261002_143344_m1a_exemplar_hygiene (fable, operator-ruled; carded opus)
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona Proteus ruled; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all **ratified 2026-10-02**).
4. The exemplar is at hygiene (M-1a): `what/exemplars/gulf_karenia_brevis/README.md` §Provenance · `uv sync && .venv/bin/python -m pytest` · self-test green.

## ⏭ QUEUED — Next Live Session

**M-1a complete 2026-10-02** (fable, operator-ruled; AAR `missions/aar/aar_m1a_exemplar_hygiene.md`). **Next: M-1c** (opus,
60–90 kT) — it was always the parallel lane; now it runs alone. Then **M-1b** (depends on M-1a ✅) → **M-1d** (M-1b + M-1c) → P1 gate.

**Next Session Prompt (self-contained, M-1c):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P1 is open (P0 GO 2026-10-02); M-1a closed 2026-10-02 — do not touch
> `what/exemplars/` (its `config.yaml` is byte-hashed into `metrics.json`). Run **M-1c — `atl_v0` controls** at **opus**:
> read STATE → `how/campaigns/campaign_atlantis_genesis/missions/mission_m1c_linkml_controls.md` → the charter's P1 exit
> bar → `what/schema/atl_v0/README.md` + the LinkML yaml + crosswalk → the precedent `~/aDNA/ASOAtlas.aDNA/what/schema/aso_v0/`
> (read-only: `fixtures/controls/`, `run_controls.sh`, its fit matrix). Open a session lease. Scratch `uv` venv with linkml
> (nothing is installed on the node; `LINKML_BIN`). Deliver: `fixtures/controls/{pos,neg}_*.yaml` (≥ 1 positive per class;
> the 8 carded negatives each with `# REJECTS_ON:` and `# REJECTS_AT:` where a path is meaningful) · `run_controls.sh`
> (three worlds: linkml-validate · committed JSON with descendants OFF · scratch JSON with descendants ON; a stale
> committed JSON fails the run) · the committed `atl_ontology_v0.schema.json` equal to a fresh `gen-json-schema --closed`
> · `m1c_vocabulary_fit_matrix.md` (every enum value × crosswalk authority; `Modality` vs GOOS EOV; `local` rows carry
> reasons) · every constraint docstring names what its control proves and the nearest miss it does not catch · README
> `validation:` updated and the NO-VALIDATION-CLAIM banner replaced by the control count · known limits named
> (referential integrity · uniqueness · cross-object equality are a validator's job). Adopt an `iii/` wrapper if absent
> (federation_ref → `III.aDNA`) and run the review through it. Path-scoped commits; AAR at
> `missions/aar/aar_m1c_linkml_controls.md`; card `status: completed` only after the AAR. Do not start extraction (M-1b).

## What's in place

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

- None. M-1c is operator-summonable at opus; M-1b after it (or in parallel — disjoint paths).

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- WI-7 — `metrics.json → config_hash` is a bytes-md5 and the recorded `e9dea88254` matches no committed `config.yaml` (training-time file had `shap.background_n: 2000`). Explanation of record: exemplar README §Provenance. Closes when M-1b's `atlantis_core` records a semantic hash alongside.

## Next steps

1. ~~M-1a~~ ✅ → M-1c (opus) → M-1b → M-1d → **P1 gate**. 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

---
type: state
status: p0_complete_awaiting_gate
phase: "P0 — M-0 complete 2026-10-02; awaiting the operator's P0-exit GO (ratify ADR-000/001/002 · persona · open P1)"
campaigns: [campaign_atlantis_genesis]
mission: mission_m0_atlantis_genesis_planning   # completed; next = M-1a + M-1c (opus) on GO
persona: proteus   # PROPOSED (Nereus alternative) — ruled at the gate
last_session: session_stanley_20261002_124712_m0_genesis_expanded (fable, operator-opened)
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p0_complete]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona *proposed*; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all `proposed`, 4-field blocks empty).
4. The exemplar still runs and its self-test is green: `what/exemplars/gulf_karenia_brevis/README.md`.

## ⏭ QUEUED — Next Live Session

**Gate first.** The P0-exit gate is the operator's: sign ADR-000/001/002 (decision · ratified-by · date · status),
pick the persona (Proteus / Nereus), and say **GO P1** — or not. Nothing below opens without it (SO-1).

**On GO → M-1a + M-1c in parallel (opus), then M-1b, then M-1d.** Cards: `missions/mission_m1a_exemplar_hygiene.md`
(40–60 kT) · `mission_m1c_linkml_controls.md` (60–90 kT) · `mission_m1b_atlantis_core_extraction.md` (120–180 kT) ·
`mission_m1d_fork_skill_and_registries.md` (80–120 kT).

**Next Session Prompt (self-contained, M-1a):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`. P0 closed on the operator's GO (check `who/governance/adr_00*.md` carry
> signed 4-field blocks; if not, stop and say so). Run **M-1a — exemplar hygiene** at **opus**: read STATE → the card →
> the charter's P1 exit bar → `what/exemplars/gulf_karenia_brevis/README.md` + `AGENTS.md`. Open a session lease.
> Fix the README/config drift (log-loss stopping; 1000 SHAP background rows; three streams), add sha256 fetch
> summaries for all three sources, add `pyproject.toml`, make `gauges.*.lever` read by code or remove it, replace
> `eval` on region rules with a safe parser (assert the 9 region counts are unchanged), reproduce the AUPRC-stopping
> run once as a negative control. Run `build_features --self-test` before and after; `outputs/metrics.json` must be
> byte-stable (config_hash e9dea88254). Path-scoped commits; AAR at `missions/aar/aar_m1a_exemplar_hygiene.md`. Do
> not touch `what/schema/` (that is M-1c) and do not start extraction (M-1b).

## What's in place (M-0, 2026-10-02 — 6 commits on `aec55d4`)

- **Governance:** ADR-000 (lineage amended) · ADR-001 (persona · Framework + reference implementation · `what/atlantis_core/`) · ADR-002 (remit widening · five layers · snapshot rule · what crosses / never crosses) — all `proposed`.
- **Planning artifacts:** thesis register (12 claims, 9 supported-by-one-exemplar, 3 untested) · instance contract v0 (12-item checklist, 7 `ATL-*` ids) · roster + 9 cards · P2 ruling (FKNMS coral) · charter re-cut.
- **L1 ontology:** `what/schema/atl_v0/` — LinkML draft, 5 classes / 7 enums / 2 rules; lint 0 errors / 38 warnings; closed JSON Schema generates (18 defs; not committed); smoke pos/neg validated; **NO VALIDATION CLAIM** until M-1c. Crosswalk 6 bound / 6 deferred.
- **L4 registries:** evidence board v1 + exemplar entry (script-generated from `metrics.json`, sha256 pins) · model-card template · dataset-pair template · hypothesis-ledger spec · `what/datasets/AGENTS.md`.
- **L2 / L3 / L5:** specified and carded (M-1b · M-1d/M-3/M-5 · M-4); nothing built — by the sitting-depth ruling.
- Exemplar untouched; self-test green at open and close.

## Active blockers

- **`#needs-human` P0-exit gate** — the operator signs the ADRs, rules the persona, opens P1. Nothing else is blocked.

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- WI-6 — Doc/config drift in the exemplar (README vs `config.yaml`/outputs) is **known and unfixed** until M-1a; the board entry follows the outputs.

## Next steps

1. Operator: P0-exit gate. 2. On GO: M-1a ∥ M-1c → M-1b → M-1d → **P1 gate**. 3. M-2 FKNMS → **P2 gate**.

---
type: manifest
project: Atlantis.aDNA
display_name: "Atlantis"
codename: "Operation Tidewatch"
genesis_stage: p0_complete_awaiting_gate
pattern_category: framework   # + reference implementation (ADR-001, PROPOSED → P0 gate)
persona: proteus              # PROPOSED
owner: stanley
visibility: public            # aDNA-Network/Atlantis.aDNA, MIT
data_bearing: false           # instances are; Atlantis is not
created: 2026-09-23
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [manifest, atlantis, framework, oceans, ecosystem_early_warning, genesis_stub]
---

# MANIFEST — Atlantis.aDNA

## Project Identity

| Field | Value |
|---|---|
| Display name | Atlantis |
| One line | Precision medicine for oceans — the MPA knowledge · data-model · evidence system around a drop-in agentic early-warning method (multi-modal observations → vitals → calibrated onset model → SHAP → intervention tagging): `atl_` ontology · reference implementation · agentic loops · registries + GREEN board · steward contract (ADR-002) |
| Category | Framework + reference implementation *(ADR-001, proposed)*; code-as-WHAT at `what/atlantis_core/` (P1) |
| Persona | Proteus *(proposed)*; Berthier interim |
| Operator | Stanley (Founding Architect, sole governance principal) |
| Codename | Operation Tidewatch (genesis campaign) |
| Lineage | Spun out of `aDNALabs.aDNA` S329 (2026-09-23), the *Karenia brevis* pilot `hab_crash_risk` → `what/exemplars/gulf_karenia_brevis/` |
| Data posture | Not data-bearing; **no new snapshots** (ADR-002 §4). Exemplar's three public parquets grandfathered. Board = metrics only. |
| Remote | `github.com/aDNA-Network/Atlantis.aDNA` — public, MIT |

## Genesis status

P0 complete (M-0, 2026-10-02). ADR-000/001/002 proposed; persona + GO P1 at the P0-exit gate. See `STATE.md`.

## Architecture (who / what / how)

| Leg | Holds |
|---|---|
| `who/` | governance (Stanley-only; ADR-000/001/002 proposed) · coordination (name-form note; P4 `inbox/`) |
| `what/` | `context/` thesis + playbook · `patterns/` the 8-step method · **`schema/atl_v0/`** ontology (L1) · **`atlantis_core/`** reference implementation (L2, P1) · `exemplars/` the reference run · `datasets/` pointers + grandfathered parquets · **`board/`** GREEN metrics (L4) · **`hypotheses/`** ledger spec (L4) |
| `how/` | `campaigns/campaign_atlantis_genesis/` (charter · artifacts · 10 cards) · `federation/atlantis/` pin (L5) · `templates/` model card + dataset pair · `skills/` + `lattices/` (L3, P1/P3/P5) · `sessions/` |

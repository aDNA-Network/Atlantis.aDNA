---
type: state
status: genesis_planning
phase: "P0 queued — M-0 genesis planning (fable, operator-opened)"
campaigns: [campaign_atlantis_genesis]
mission: mission_m0_atlantis_genesis_planning
persona: proteus   # PROPOSED
last_session: none (seeded from aDNALabs S329, 2026-09-23)
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [state, atlantis, genesis_stub]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. Read `CLAUDE.md` (identity, persona *proposed*, standing orders).
2. Read the charter: `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md`.
3. Read the queued card: `how/campaigns/campaign_atlantis_genesis/missions/mission_m0_atlantis_genesis_planning.md`.
4. The exemplar is real and runs: `what/exemplars/gulf_karenia_brevis/README.md` (results + run order).

## ⏭ QUEUED — Next Live Session

**M-0 — genesis planning.** Open-at tier: **fable** (operator-summoned). Estimated 70–110 kT.

Rules to be taken there (all *proposed* until then): identity ADR-000 · persona (Proteus) · category (Framework
+ reference platform) · name-form (`Atlantis`, capitalised, ADR-009 §3 exception) · **instance contract v0**
(what a regional instance must carry to federate: patient definition, event + horizon, data posture ruling,
`federation_ref`) · the P1–P5 mission roster with tiers and budgets · the P2 second-instance pick.

**Next Session Prompt (self-contained):**

> You are Proteus (proposed) in `~/aDNA/Atlantis.aDNA`, a genesis stub seeded 2026-09-23 from the aDNALabs
> S329 *Karenia brevis* pilot. Run M-0 of Operation Tidewatch: read STATE → charter → the M-0 card; produce
> `who/governance/adr_000_project_identity.md` (proposed → surface for ratification), the thesis register,
> the instance contract v0, and the P1–P5 mission roster; surface the four rulings to the operator with
> `AskUserQuestion` or an ISS gate. Do not advance past P0. Open a session lease first. The exemplar under
> `what/exemplars/gulf_karenia_brevis/` is the ground truth for what the method looks like when it works —
> read its README before writing the contract.

## What's in place (seeded S329)

- Governance kit (CLAUDE · MANIFEST · STATE · AGENTS), README, MIT LICENSE, public remote.
- Thesis (`what/context/concept_atlantis.md`), method (`what/patterns/pattern_ecosystem_early_warning.md`),
  mining playbook (`what/context/playbook_data_and_literature_mining.md`).
- The exemplar: trained model, SHAP, what-if, explainer site (Artifact, private link in CLAUDE §References);
  leakage self-test green from this location; venv rebuilt (`.venv/`, gitignored).
- Charter with P0–P5 ladder and written exit bars; M-0 card; carded P1/P2 stubs.
- Federation wrapper contract stub at `how/federation/atlantis/README.md`.

## Active blockers

- **`#needs-human` M-0 open** — the operator opens the fable sitting. Nothing else is blocked.

## Watch items

- WI-1 — Router row added to `Home.aDNA/what/inventory/workspace_router_CLAUDE.md` at seed time, **left
  uncommitted for Hestia's sitting** (Home is her graph). Verify it landed in a Home commit.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the
  committed derivative. A fresh clone regenerates chunks via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act from the page's Share menu.

## Next steps

1. Operator opens M-0 (fable). 2. M-0 rules → operator ratifies ADR-000 → **P0 exit GO**. 3. P1 (opus lanes):
extract `how/templates/template_regional_instance/` + `skill_atlantis_instance_fork.md` from the exemplar.

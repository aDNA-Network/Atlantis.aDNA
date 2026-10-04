---
type: directory_index
created: 2026-02-17
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [directory_index, governance, adr, atlantis]
---

# who/governance/ — Governance (Agent Reference)

## Purpose

Governance for `Atlantis.aDNA`: the identity ADRs and the agent protocol. **ADRs live here** (CLAUDE.md
§Governance Doctrine), not in `what/decisions/` — the three `what/decisions/adr_00{1,2,3}_*.md` are
template-inherited boilerplate from `.adna/` and are *not* Atlantis decisions; do not renumber against them.
Stanley is the sole governance principal (seed ruling, 2026-09-23); every ADR stays `proposed` until it carries
the operator's 4-field ratification block (§7.7).

## Key Files

| File | Status | Purpose |
|------|--------|---------|
| `adr_000_project_identity.md` | **ratified 2026-10-02** | Identity, lineage from aDNALabs S329, three-layer naming, SO-3; lineage amendment 2026-10-02 → ADR-002 |
| `adr_001_persona_and_category.md` | **ratified 2026-10-02** | Persona **Proteus** (ruled) · **Framework + reference implementation** · code home `what/atlantis_core/` · name-form |
| `adr_002_remit_mpa_knowledge_system.md` | **ratified 2026-10-02** | The remit widening: MPA as unit kind + audience · five layers · **snapshot rule** · what crosses / never crosses · decentralisation composed not built |
| `contribution_guide.md` | **draft 0.1.0** (M-1d-ii, 2026-10-03), ratify at the P1 gate | What crosses / never crosses · memo → `who/coordination/inbox/` · public-repo PRs (DCO v1.1) · checks by class · tiers draft → reviewed → validated |
| `governance_agent_protocol.md` | template | Agent behavioural contract (inherited; CLAUDE.md overrides where they differ) |
| `VISION.md` | template | aDNA standard vision (inherited; not Atlantis-specific) |

Planned (P4, when a second steward exists): `steward_council.md`,
`decision_authority.md`, `partner_engagement.md` — RareArchive shape, adapted.

## Conventions

- **Naming**: `adr_NNN_<topic>.md` (three digits, underscores); `governance_<topic>.md` for policies.
- **Frontmatter**: `type: adr`, `adr_id`, `status`, and the nested `ratification:` block (decision · ratified_by · date · status).
- **Ratification**: agents author, operators ratify. Surface a ruling with `AskUserQuestion` (bounded) or an ISS gate (`aDNA.aDNA/how/skills/skill_create_iss.md`); record the ruling verbatim in the ADR.
- **Archive, never delete** (SO-2): superseded ADRs get `status: superseded` + `superseded_by`.

## Cross-References

- [CLAUDE.md](../../CLAUDE.md) — persona, standing orders, hard gates
- [who/coordination/AGENTS](../coordination/AGENTS.md) — name-form note; future steward memos + `inbox/`
- [how/campaigns/campaign_atlantis_genesis/](../../how/campaigns/campaign_atlantis_genesis/) — Operation Tidewatch

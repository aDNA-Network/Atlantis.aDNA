---
type: federation_wrapper
wrapper_for: III.aDNA
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission_origin: campaign_atlantis_genesis.M-1c (atl_v0 controls) — card criterion "III review via wrapper (iii/, adopted in this mission if absent)"
status: active
tags: [federation, iii, consumer_wrapper, atlantis, tidewatch, m1c]
---

# Atlantis.aDNA `iii/` — III.aDNA Consumer Wrapper

The Atlantis.aDNA (Proteus) federation wrapper for **III.aDNA** (Inspect / Introspect / Improve, persona Argus Panoptes).
It declares which III capabilities Atlantis consumes, pins the upstream version, and routes ACCUMULATE writes to the
Atlantis-local learning store. Per III **ADR-002** (consumer federation contract) and **ADR-003** (learning-store
ownership), canonical III content is **never copied here — only referenced**. This satisfies the Atlantis Hard Gate
*"III review via wrapper (`iii/`); no bespoke quality gates"* and the P1 exit bar's *"III review via wrapper"*.

## federation_ref

```yaml
federation_ref:
  source_vault: III.aDNA
  source_path: ~/aDNA/III.aDNA
  source_skill: how/skills/skill_iii_review.md
  version: "0.6.0"
  version_policy: minor
  pinned_at_commit: "be7dba1"            # `git rev-parse 'v0.6.0^{commit}'` — the tag COMMIT (2026-07-03), not the tag object
  pinned_at: 2026-10-02
  assumed_action:
    posture: opt_in                      # explicit; ADR-012 §42 makes an absent block identical. A version bump cannot flip it.
  packs_used:
    - context_iii_inspect_procedures
    - context_iii_introspect_checks
    - context_iii_learning_store
    - context_iii_vault_maintenance
  modules_used:
    - module_iii_dispatch
    - module_iii_inspect_text
    - module_iii_inspect_code
    - module_iii_inspect_visual
    - module_iii_inspect_data
    - module_iii_introspect
    - module_iii_improve
    - module_iii_accumulate
  lattice: ~/aDNA/III.aDNA/what/lattices/lattice_iii_verification_oracle.lattice.yaml
  lattice_version: "1.2.6"               # at the v0.6.0 tag (verified `git show v0.6.0:…`); III HEAD may be ahead — the pin is the tag
  local_extensions:
    - kind: learning_store_local
      path: ~/aDNA/Atlantis.aDNA/how/federation/iii/what/context/atlantis_iii_learning_store.jsonl
      rationale: Per ADR-003 §2 at III.aDNA; ACCUMULATE writes target this file, never the canonical upstream.
```

**Packs deliberately omitted (revisit at the next minor bump or when the output kind appears):**
- `context_iii_domain_packs_web_design`: Atlantis's only web output so far is the exemplar's site page, which was M-1a's
  surface. Adopt when M-1d or P4 publishes a steward-facing page.
- `context_iii_whitepaper_communication`: no formal-prose outputs yet. The P3 write-up of a literature-asserted driver is
  the likely trigger.
- `context_iii_canvas_visual` · `context_iii_iss_surfaces`: no canvas or ISS artifacts. Phase gates have used `AskUserQuestion`.
- `context_iii_representation_coherence`: canonical-conditional upstream. Adopt when the public README or site is reviewed as a
  representation of the vault (P4 first-outside-steward readiness).

## Active campaigns using this wrapper

- `campaign_atlantis_genesis` (Operation Tidewatch). First review: **M-1c**, the `atl_v0` controls (2026-10-02), recorded
  in `how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1c_linkml_controls.md` §III review.

## Local extensions explained

- **`learning_store_local`**: `what/context/atlantis_iii_learning_store.jsonl`, empty at creation. ACCUMULATE rows from
  Atlantis reviews land here. Graduation to the canonical store goes only by the ADR-003 ceremony, never by an edit from this side. First rows: C-001…C-004 from the M-1c review (frequency 1 each).

## Routing notes

1. **ACCUMULATE always writes local.** Never edit `iii_corrections_canonical.jsonl` from Atlantis.
2. **Reviewer ≠ producer.** An Atlantis III review runs in a fresh agent context, never the one that produced the artifact
   (ASOAtlas loop discipline, adopted).
3. **Version-policy bump.** On an III minor bump, review the upstream CHANGELOG diff before updating `version:`. Pin the tag commit.
4. **Skill invocation.** Load this file → follow `federation_ref.source_skill` → the III skill loads `packs_used` + `local_extensions`.

## Cross-References

- Upstream: `~/aDNA/III.aDNA/CLAUDE.md` · `how/skills/skill_iii_review.md` · `how/skills/skill_iii_setup.md`
- ADR-002 / ADR-003: `~/aDNA/III.aDNA/what/decisions/adr_00{2,3}_*.md`
- Atlantis root governance: `~/aDNA/Atlantis.aDNA/CLAUDE.md` (SO-10: III review via this wrapper, fresh context; Hard Gates)
- Pin-convention precedent: `~/aDNA/aDNALabs.aDNA/how/federation/iii/CLAUDE.md`

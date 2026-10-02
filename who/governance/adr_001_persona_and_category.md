---
type: adr
adr_id: ADR-001
title: "ADR-001 — Persona, category wording and code home (RATIFIED 2026-10-02)"
status: ratified
created: 2026-10-02
updated: 2026-10-02   # ratified at the P0-exit gate
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
supersedes: ""
superseded_by: ""
ratification:
  decision: accepted
  ratified_by: stanley
  date: 2026-10-02
  status: ratified
  surface: AskUserQuestion (P0-exit gate, M-0 sitting)
tags: [adr, persona, category, code_home, atlantis, m0]
---

# ADR-001 — persona, category wording, code home (proposed)

## Status

**Ratified 2026-10-02** (was proposed at M-0 (2026-10-02, fable sitting, operator-opened). Three of the four fields below were taken as
bounded choices by the operator during the sitting (`AskUserQuestion`, 2026-10-01); the persona is carried to the
P0-exit gate. The 4-field block is the operator's to sign.

## Context

The seed (2026-09-23) left persona, category and name-form *proposed*. ADR-002 (same sitting) widens the remit
to an MPA knowledge · data-model · evidence system, which makes the category wording and the home of the
generalised code load-bearing: a Framework that ships a library instances install is a different animal from a
Platform that runs one.

Fleet precedents read at M-0: **Git.aDNA** (Framework — standard + skills + wrapper, no deployed runtime; its
deployable went to a sibling, `Lighthouse.aDNA`) and **Harness.aDNA** (Platform — runtime code in-graph at
`what/harness/`, with a clinical vertical). Atlantis is neither: it deploys nothing, but its method is only
"drop-in" if a steward can `pip install` a reference implementation rather than copy a pilot.

## Decision (proposed)

| Field | Ruling | Alternative considered |
|---|---|---|
| **Persona** | **Proteus** — the Old Man of the Sea who knows what is coming and answers only when held through every shape he takes. Two doctrines fixed by the myth: *translation is the work* (every modality held and translated onto one grid before the sea says anything true) and *forecast honestly or not at all* (every score read against its base rate; a SHAP value is never called a cause). | **Nereus** — the truthful, gentle sea-elder and father of the Nereids; fits "honest forecast" but not "shape-shifting translation". **Declined at the gate 2026-10-02.** |
| **Category** | **Framework + reference implementation.** Atlantis is a Framework (produces no primary artifact, deploys no runtime; consumers federate via `how/federation/atlantis/`). It additionally carries a *reference implementation* — a library + exemplar that instances install and run on their own data. | "Framework + reference *platform*" (seed wording) — rejected: "platform" implies a deployed runtime Atlantis does not run. "Framework only, code to a sibling" — rejected 2026-10-01 by the operator: one more fork + router row before P1 can start, for no consumer class that needs it. |
| **Code home** | **`what/atlantis_core/`** — code-as-WHAT inside this graph, fleet convention (`Harness.aDNA/what/harness/`, `Context.aDNA/what/contextscope/`). The package holds no data; the exemplar at `what/exemplars/gulf_karenia_brevis/` becomes its first consumer at P1. Split to a sibling **only if** a second consumer class appears (e.g. a Dashboards projection with its own release cadence). | Sibling graph now — rejected (above). |
| **Name-form** | **`Atlantis`**, capitalised — the fleet's standing ADR-009 §3 exception, recorded at `who/coordination/coord_2026_09_23_name_form_note.md`. | `atlantis` snake_case per `skill_project_fork` step 1 — would make it the only lowercase project of 100+. |

## Consequences

**Positive.** The category sentence in `CLAUDE.md` / `MANIFEST.md` / the Home router row stops contradicting the
Git.aDNA precedent. P1 M-1b has a named destination. Instances get one `pip install` + one `federation_ref`.

**Negative.** A library inside a Framework graph is a mild novelty; the fleet's Framework spec
(`aDNA.aDNA/what/specs/spec_framework_ecosystem.md`) does not forbid it but does not describe it. Follow-up: a
one-line note to Rosetta when the pattern has a second example (backlog, not now).

**Neutral.** Berthier holds the desk until the persona field is signed.

## Ratification

**Ruled 2026-10-02 by the operator (stanley) at the P0-exit gate, `AskUserQuestion`:** ratified as written. Persona ruled **Proteus** (Nereus declined). Recorded verbatim; GO P1 given in the same gate.

| Field | Value |
|---|---|
| decision | **accepted** |
| ratified-by | **stanley** |
| date | **2026-10-02** |
| status | **ratified** |

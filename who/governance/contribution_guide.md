---
type: contribution_guide
doc_id: atl_contribution_guide
title: "Contribution guide — Atlantis.aDNA (what crosses, how it arrives, how it is checked)"
status: draft            # agents author, operators ratify (§7.7) — raised for ratification at the P1 gate
version: 0.1.0
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
mission: mission_m1d_ii_lattice_and_registries
substrate: "ADR-002 §4–§6 (ratified 2026-10-02) · instance contract v0.2.0 §A/§C/§D · CLAUDE.md standing orders"
precedent: "RareArchive.aDNA/who/governance/contribution_guide.md (DCO v1.1 · tiers · layering); shape only — its clinical carve-outs are RareArchive's"
tags: [contribution, governance, dco, memo, inbox, tiers, atlantis, tidewatch, m1d_ii]
---

# Contribution guide — Atlantis.aDNA

> **Status:** draft 0.1.0. Proteus authored it at M-1d-ii. The operator ratifies it at the P1 gate. Governance beyond this
> guide is **P4** (ADR-002 §6): the steward council, decision authority and partner engagement arrive when a second
> steward exists. Until then, Stanley is the operator, and Proteus lands contributions.

Atlantis is a **public repository** (`aDNA-Network/Atlantis.aDNA`, MIT). Every commit is a publication (Git.aDNA
ADR-013). Atlantis holds method, doctrine, templates, the reference implementation and one public-data exemplar, and it
is **not data-bearing**. This guide says what may cross into it, how it arrives, and what checks it must pass before it
counts.

## 1. What crosses, and what never does (ADR-002 §5)

| Crosses into Atlantis | Never crosses |
|---|---|
| Patterns and **template fixes**: an instance hit a gap, and the fix belongs upstream (the P2 rule) | **Observations**, raw or processed, and any cache of a stream |
| **Feature-registry rows**: an `AtlVital` that worked or failed, with its transform, tag and owner | **Labels**, and the patient × week tables they come from |
| **Hypothesis-ledger rows**: literature claims with provenance (P3) | **Per-patient predictions**, scores or SHAP values |
| **Evidence-board entries**, metrics only: base rate · AUROC/AUPRC · Brier · calibration slope · alert-budget precision/recall · lead-time summary · ablations · config hash · data pins | **Model binaries** trained on partner or human-subject data |
| `atlantis_core` fixes, with their tests | **Coordinates of partner sites** |
| Docs: an error in the method, the contract or a README | **Credentials**: Atlantis stores names only (the Home broker) |

**Snapshot rule (ADR-002 §4).** Atlantis adds **no new data snapshots**. A dataset record is a *pointer + sha256 +
fetch recipe* (`how/templates/template_dataset_pair/`, checked by `python -m atlantis_core.datasets --check`). The
exemplar's three public parquets are the capped, grandfathered exception. A contribution that would add bytes is wrong,
whatever the rule says.

**If a field would carry something from the right-hand column, the contribution is wrong, not the rule.** The board
generator and `assert_green` refuse per-patient content by code. They are a backstop, not permission to try.

## 2. How a contribution arrives

### 2a. From an instance steward: coordination memo → inbox (contract §D)

A steward never writes into Atlantis directly, and Atlantis never writes into an instance (Operations ADR-026; workspace
Rule 10). The steward writes a memo:

```
Atlantis.aDNA/who/coordination/inbox/coord_<YYYY_MM_DD>_<from>_to_proteus_<topic>.md
```

carrying:
- **what** it is: one of the left-hand rows above;
- **from which instance**, with its `federation_ref` pin: the Atlantis commit it federates;
- **the artifact inline or attached**. A board entry is the JSON its own `python -m atlantis_core.board … --entries
  <instance>/what/board/entries` wrote, unedited;
- **its checks**: the output of `python -m atlantis_core.conform --instance <dir>` (a board entry needs item 9 ✅) and
  the self-test receipt's `semantic_hash`;
- **the posture**: the instance's data-posture class, and a statement that nothing in the memo comes from the
  right-hand column.

Proteus re-runs the checks, then **lands the contribution by a dated commit**. The commit message names the memo, and the
memo stays in the inbox as the record (SO-2). If Proteus declines, a dated note beside the memo says why. A
disagreement is a note, never a deletion (contract §D).

### 2b. From anyone: a pull request against the public repo

A code, template or doc change may arrive as a PR against `main`. A PR carries:
- **DCO v1.1 sign-off on every commit:** `git commit -s` adds `Signed-off-by: Name <email>`. By signing off, the
  contributor attests that they have the right to submit the work under the MIT licence (`developercertificate.org`).
  *This is not CI-enforced yet (Atlantis has no CI in P1); Proteus checks it before merging. A CLA, if one is ever
  wanted, is a P4 question.*
- **path-scoped commits**, never `git add -A`, with `gitleaks` clean against `atlantis_core`'s
  `gitleaks_atlantis.toml`;
- **no data:** the §1 right-hand column does not appear in any diff.

## 3. Checks by contribution class

| Class | Must pass before it lands |
|---|---|
| `atlantis_core` code | `cd what/atlantis_core && .venv/bin/python -m pytest` green, and **SO-7**: `python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` green if vitals or labels are touched. Anything that lets the core accept a new input shape re-runs the **whole** planted-defect catalogue on that shape (C-014) |
| Ontology (`what/schema/atl_v0/`) | `run_controls.sh` says **ALL WORLDS AGREE**. A constraint is an intention until a fixture proves both validators enforce it |
| Templates | the template validates against the schema it claims, with a planted defect for each failure mode it fixes (`tests/test_dataset_pairs.py`, `test_mapping_template.py`, `test_fork.py`) |
| Board entry | emitted by code (numbers are never retyped); closed `AtlEvaluation`; GREEN; base rate, ≥ 1 alert budget, limitations ref; `claim: method_demonstration` unless the instance owner's written ruling is cited (SO-4, SO-9); then `python -m atlantis_core.board --index` regenerates `BOARD.md` |
| Dataset record | a pair; `python -m atlantis_core.datasets --check what/datasets` ✅; pointer + sha256 + recipe, no bytes |
| Pipeline lattice / runspec | `python -m atlantis_core.lattice` ✅: strict schema, the peer validator and the local invariants |
| Docs | no number without its source; no accuracy claim without its base rate, budget and limits (SO-9) |

## 4. Tiers: draft → reviewed → validated

A contribution moves through three tiers. Nothing promotes itself.

| Tier | Means | Who moves it |
|---|---|---|
| **draft** | landed and checked: §3 green for its class | Proteus, by the dated landing commit |
| **reviewed** | an **III review via the `iii/` wrapper in a fresh context** (SO-10) has run on it, and every finding is addressed or disclosed. The reviewer is never the context that produced it | Proteus, recording the review in the mission AAR or a dated note |
| **validated** | it survives a **phase gate**: the operator's GO at the exit it belongs to, with the III review in hand | the operator (SO-1) |

Separately, **promotion to the board's `gold/` set** (an entry that anchors a thesis claim) is a **human act**: the
operator's, or the steward council's from P4 (`what/board/README.md` §Lifecycle).

## 5. What this guide does not cover

- A steward's **own instance**. Its data, credentials, partners and rulings are its owner's (Network ADR-016 §8 class). Atlantis
  supplies the pattern, not the permission.
- **Operational forecasts.** No output of Atlantis or an instance is one unless the instance owner rules it so in
  writing, naming the agencies that run the real thing (SO-4).
- **The steward council, decision authority and partner engagement** (P4).

## Ratification

| Field | Value |
|---|---|
| decision | *(pending)* |
| ratified-by | *(pending: the operator, at the P1 gate)* |
| date | *(pending)* |
| status | draft |

## See also

`who/governance/adr_002_remit_mpa_knowledge_system.md` §4–§6 · `how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md` §A/§C/§D ·
`who/coordination/inbox/AGENTS.md` · `what/board/README.md` · `what/datasets/AGENTS.md` · `how/federation/iii/CLAUDE.md` ·
`how/lattices/lattice_atlantis_pipeline.lattice.yaml`

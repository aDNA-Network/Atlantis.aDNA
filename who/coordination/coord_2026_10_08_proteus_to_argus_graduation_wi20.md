---
type: cross_vault_request
doc_id: coord_2026_10_08_proteus_to_argus_graduation_wi20
title: "Cross-Vault Request: Atlantis → III.aDNA — local graduation proposals C-004 · C-005 · C-009 · C-010 · C-023 (+ C-015, not yet at the bar) (ADR-003 § 3 ceremony)"
status: open
direction: outbound (III.aDNA receives)
requesting_vault: Atlantis.aDNA
requesting_persona: proteus
receiving_vault: III.aDNA
receiving_persona: argus_panoptes
requesting_agent: agent_proteus
created: "2026-10-08"
updated: "2026-10-08"
supersedes: coord_2026_10_03_proteus_to_argus_graduation_c004_c009   # never delivered; C-004 and C-009 are carried here with their later recurrences
ruled_by: "stanley — P2-exit gate, AskUserQuestion, 2026-10-08 ('ACCUMULATE + redraft memo')"
delivery: "Filed here, in Atlantis's own who/coordination/ (outbound record). Delivery into III.aDNA/who/coordination/ is a peer-vault write — made by an operator-opened session, not by this one."
artifact_request:
  type: learning_store_graduation
  local_ids: ["C-004", "C-005", "C-009", "C-010", "C-023"]   # at the bar as recorded
  local_ids_below_bar: ["C-015"]                               # frequency 3, but accepted is not true in the local row
  source_learning_store: ~/aDNA/Atlantis.aDNA/how/federation/iii/what/context/atlantis_iii_learning_store.jsonl
  candidate_target: ~/aDNA/III.aDNA/what/context/core_domain_packs/iii_corrections_canonical.jsonl
  canonical_md5_at_filing: "a28ec2a1815cf3cc08b375a40a23aca3"   # unchanged since 2026-10-03; last canonical id C-035
  ceremony_authority: "ADR-003 § 3 at III.aDNA (frequency ≥ 3 + sessions ≥ 2 + acceptance true + Argus + Stanley co-ratification)"
constraints:
  human_gate_required: true
  argus_review_required: true
  stanley_co_ratification_required: true
secrets_handled:
  needed: []
  not_passed: "No secrets cross the boundary; the review operates on filed vault content only."
tags: [coordination, iii, graduation, learning_store, adr_003, atlantis, tidewatch, p2_gate, wi_20]
---

# Graduation proposals: six Atlantis local rows → III canonical

The operator ruled at Atlantis's P2-exit gate (2026-10-08) to propose every local row at frequency ≥ 3. The 2026-10-03
memo (C-004 and C-009 only) was never delivered and is superseded by this one. Every occurrence below is quoted from the
local store's `source_review` and `recurrences`, not paraphrased. Graduation is Argus's ceremony, co-ratified by Stanley.
Atlantis never edits the canonical store.

| Local id | Pattern (trap) | Freq | Accepted | Reviews (missions) |
|---|---|---|---|---|
| C-004 | `verbatim_copy_propagates_pointer_error` (completeness) | 3 | true | M-1c F-6 · M-1b-ii-b F-2 · M-1d-i F-6/F-7 |
| C-005 | `degenerate_synthetic_fixture` (completeness) | 4 | true | M-1b-i F-2/F-3 · M-1d-i F-1 · M-2a-i F-5/F-7 *(+1 counted in the row's frequency)* |
| C-009 | `control_true_by_construction` (completeness) | 7 | true | M-1b-ii-a F-3/F-4/F-6 · M-1b-ii-b F-3 · M-1d-i F-3b/F-5 · M-1e F-1/F-3 · M-1f F-1 · M-2b F-5 · P2 gate G-1 |
| C-010 | `join_key_excludes_evaluated_quantities` (boundary) | 3 | true | M-1b-ii-a F-2 · M-2a-i F-1 · M-2a-ii F-1 |
| C-023 | `provenance_label_stamped_from_intent` (completeness) | 5 | true | M-1e F-2/F-4 · M-2a-i F-1 · M-1f F-3 · M-2a-ii F-1 · M-2b F-6 |
| C-015 | `fallback_relocates_probe_to_blind_spot` (boundary) | 3 | **not set** | M-1d-i F-2 · M-1d-ii F-5 · M-2a-i F-3 |

**C-015 is below the bar as recorded.** Its local row has no `accepted: true` (the field is null). Each finding was fixed
in its mission, but the RLHF acceptance was never captured on the row. It is listed so that Argus sees the whole set. It
graduates only after the operator records acceptance locally. Atlantis does not backfill that field on its own.

## Why each is general

- **C-004.** Any vault that moves text or fixtures "verbatim, for provenance" inherits the defect. The fix is to check the
  claim and the pointer at the destination, not just the fidelity of the copy.
- **C-005.** A perturbation self-test on dense, single-entity synthetic data cannot see a defect that exists only with gaps
  or across entities. Any vault with a synthetic fixture world has this blind spot until the fixture is made irregular.
- **C-009.** Any quality gate can be demonstrated against inputs it cannot fail on. The corrective is to plant the defect
  the control exists for and watch it turn red. At the P2 gate it recurred *outside code*: a thesis whose falsifier the
  campaign's own escalation rule made unfalsifiable.
- **C-010.** A hash, or a cache key, that is stamped onto results it does not fully describe. This applies to every
  content-addressed pipeline.
- **C-023.** A provenance field written from the config's intent, not from what the code did, so a gate that reads only
  the field passes any defect beneath it. This applies to every vault that emits provenance blocks.
- **C-015.** A fallback added to fix a vacuous check moves the probe to where it cannot see its defect, and nothing
  reports that the check was lost.

## Asked of Argus

Review the five at the bar against the canonical store for duplicates or near-duplicates (C-009 may sit near an existing
canonical "vacuous control" row), assign canonical ids if accepted, and reply in
`III.aDNA/who/coordination/reply_<date>_iii_to_atlantis_graduation_*.md`. On acceptance, Atlantis sets `graduated: true`
and `graduated_to: <canonical id>` on the local rows, and changes nothing else locally.

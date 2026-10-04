---
type: cross_vault_request
doc_id: coord_2026_10_03_proteus_to_argus_graduation_c004_c009
title: "Cross-Vault Request: Atlantis → III.aDNA — local C-004 + C-009 graduation proposals (ADR-003 § 3 ceremony)"
status: open
direction: outbound (III.aDNA receives)
requesting_vault: Atlantis.aDNA
requesting_persona: proteus
receiving_vault: III.aDNA
receiving_persona: argus_panoptes
requesting_agent: agent_proteus
created: "2026-10-03"
updated: "2026-10-03"
ruled_by: "stanley — P1-exit gate, AskUserQuestion, 2026-10-03 ('send both')"
delivery: "Filed here, in Atlantis's own who/coordination/ (outbound record). Delivery into III.aDNA/who/coordination/ is a peer-vault write — made by an operator-opened session, not by this one."
artifact_request:
  type: learning_store_graduation
  local_ids: ["C-004", "C-009"]           # Atlantis-local ids; canonical ids are Argus's to assign (canonical store is at C-035 on 2026-10-03)
  source_learning_store: ~/aDNA/Atlantis.aDNA/how/federation/iii/what/context/atlantis_iii_learning_store.jsonl
  candidate_target: ~/aDNA/III.aDNA/what/context/core_domain_packs/iii_corrections_canonical.jsonl
  canonical_md5_at_filing: "a28ec2a1815cf3cc08b375a40a23aca3"
  ceremony_authority: "ADR-003 § 3 at III.aDNA (frequency ≥ 3 + sessions ≥ 2 + acceptance true + Argus + Stanley co-ratification)"
constraints:
  human_gate_required: true
  argus_review_required: true
  stanley_co_ratification_required: true
secrets_handled:
  needed: []
  not_passed: "No secrets cross the boundary; the review operates on filed vault content only."
tags: [coordination, iii, graduation, learning_store, adr_003, atlantis, tidewatch, p1_gate]
---

# Graduation proposals: Atlantis C-004 and C-009 → III canonical

Both rows meet the ADR-003 § 3 bar as recorded in the Atlantis local store. **Frequency 3 each, across three distinct
missions and sessions, with `accepted: true` on each.** The operator ruled at Atlantis's P1-exit gate (2026-10-03) to
propose both. Graduation itself is Argus's ceremony, co-ratified by Stanley. Atlantis never edits the canonical store.

## C-004 · `verbatim_copy_propagates_pointer_error` (trap: completeness)

> A fixture faithfully copies a source field whose pointer target is wrong. Provenance discipline ("nothing from memory")
> propagates the error instead of catching it.

| # | Review | Finding |
|---|---|---|
| 1 | M-1c atl_v0 controls (2026-10-02) | F-6: `pos_exemplar` copied `limitations_ref` '§12 Where the analogy breaks' from the board entry; the page numbers that section 11 |
| 2 | M-1b-ii-b site · mapping · archive (2026-10-03) | F-2: a verbatim prose move carried 'the confident true positive with the longest lead', a selection rule the code never implemented |
| 3 | M-1d-i fork and conformance (2026-10-03) | F-6/F-7: 'a refusal writes nothing' copied into three documents while false; 'opens nothing under data/site' survived into contract v0.2.0 |

**Why general:** any vault that moves text or fixtures "verbatim, for provenance" inherits the defect. The fix is to check
the claim and the pointer at the destination, not only the fidelity of the copy.

## C-009 · `control_true_by_construction` (trap: completeness)

> A control that cannot fail: additivity of a linear decomposition, refitting the same data, a guard flag set from argument
> presence, a denylist proven by its own three examples.

| # | Review | Finding |
|---|---|---|
| 1 | M-1b-ii-a eval · explain · board (2026-10-02) | `test_linear_shap_is_exact` passed under any column→vital mapping; `honoured = fold_tables is not None` passed a no-op callable; `assert_green` passed 1,640 keyed predictions |
| 2 | M-1b-ii-b site · mapping · archive (2026-10-03) | F-3: a test named `…_sum_net` passed with `np.abs` sums; `board_check` compared 5 of ~20 fields (a doctored Brier passed) |
| 3 | M-1d-i fork and conformance (2026-10-03) | F-3b/F-5: tests asserted that a one-word status flip ratifies, and an empty `#limits` section passed |

**Why general:** every quality gate in every vault can be demonstrated against inputs it cannot fail on. The corrective is
to plant the defect the control exists for and watch it turn red.

## Asked of Argus

Review both against the canonical store for duplicates or near-duplicates, assign canonical ids if accepted, and reply in
`III.aDNA/who/coordination/reply_<date>_iii_to_atlantis_graduation_*.md`. On acceptance, Atlantis sets `graduated: true`
and `graduated_to: <canonical id>` on the local rows. Nothing else changes locally.

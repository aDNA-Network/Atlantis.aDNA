---
type: artifact
doc_id: p2_gate_iii_review
title: "P2 gate — III adversarial review of the gate case (fresh context, via iii/)"
status: ruled
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
mission: p2_gate
campaign_id: campaign_atlantis_genesis
session: session_stanley_20261008_215226_p2_gate_rulings
reviewer: fresh-context agent via `iii/` → `III.aDNA/how/skills/skill_iii_review.md` v0.6.0 (≈ 189 kT)
tags: [artifact, iii, review, p2_gate, thesis_register, atlantis, tidewatch]
---

# P2 gate: III review of the gate case

**What was reviewed:** the gate case, not M-2b's code. The inputs were:
- the opus decision brief (R1–R4);
- the charter's §P2 and its Risks;
- the P2 ruling;
- the M-2a-ii and M-2b AARs;
- the thesis register;
- the roster and the P3 cards;
- `BOARD.md` and the entry JSONs;
- the instance page's §6 and §11.

The review was read-only on every vault. It proposed its ACCUMULATE entries and wrote none; the desk applied them after the rulings.

**Verdict: PASS-WITH-FINDINGS.** No blockers, 6 major, 4 minor, 2 nits. **The reviewer recommends a conditional GO for P3, with stronger conditions than the brief proposed.**

**What the reviewer confirmed independently:**
- 14 commits are unpushed.
- The instance carries no `atlantis_core` code.
- Board v2's numbers equal the AAR's.
- No cross-base-rate comparison was found in the case; T3's fix holds.

**What the desk re-checked first-hand:** G-6 (the entry's refs are instance-relative and the instance has no remote) and G-2 (the M-2a-i AAR cites "which the P2 rule forbids").

## Findings and their dispositions

| ID | Sev | Class | Finding | Disposition (operator ruling, 2026-10-08) |
|---|---|---|---|---|
| G-1 | major | C-009 | T9's weak form holds by construction. Its falsifier is "an instance-local patch", and the M-2 card's own escalation rule is "stop, file the template change, do not patch locally" (`mission_m2_fknms_coral_instance.md:66`). So it measures that the process held, not that the method is drop-in. | Ruling 2: T9 is "exit bar met as worded; drop-in not demonstrated". The claim text is matched to its falsifier. A measurable P4 bar is set before P4 opens (condition (d)). |
| G-2 | major | C-032 | "Nine" undercounts. The M-2a-i set was forced by the pre-fork survey and left out: refractory, accumulating self-test world, grid pin, `NOAACRW:` authority, the polygon grid and the CRW fetcher. The AAR says "every gap the FKNMS instance would have hit". The count also used two rules: M-2a-ii's III fixes were counted, M-2b's were not. | Ruling 2: one counting rule, ≈ 13–15 Atlantis changes forced by FKNMS. This is P4's baseline. |
| G-3 | major | C-034 (new) | T11's falsifier says "at the chosen budget", which has never been measured on either instance. FKNMS 0.937 vs 0.919 has no uncertainty attached, and its effective n is about 7 seasons (§11: "one event seen 21 times"). | Ruling 2: T11 is untested at its terms. Ruling 1(a): M-2c adds a climatology-at-budget slot and a season-block paired interval. |
| G-4 | major | C-033 (new) | Obligations the register gave to P2 were dropped when the work was re-carded. T2's swap on M-2 never ran (FKNMS `learner_swaps` is empty). T4's P2 replication had no AUPRC-stopping arm. T5's absence case and T12's DHW ≥ 8 run are not recorded. | Ruling 2: each obligation is recorded as carried, dropped or recorded (register). M-2c and the P3 cards now carry the register's obligations explicitly. |
| G-5 | major | C-030 | T4's FKNMS note attributes slope 1.99 to the base-rate shift, which "the stopping rule did not cause". That is untested, and a prevalence shift mostly moves calibration-in-the-large, not slope. | Ruling 2: T4 is untested on FKNMS, and the causal clause is dropped. |
| G-6 | major | — | The push would land a public, immutable entry whose `limitations_ref` and `shap_summary_ref` resolve only inside a local-only instance (`FloridaKeysCoral.aDNA` `visibility: local`). | Ruling 3: a note on `what/board/README.md` saying instance refs resolve in the instance and are public only once its owner publishes it; then push. The instance's remote is its owner's later ruling. |
| G-7 | minor | C-032 | `BOARD.md` "Lead (budget)" prints "@ 0.1" for a threshold that flagged 20.3% of test. | Carried to M-2c: the generator prints the realised rate in that column. |
| G-8 | minor | — | The M-3b card allows *K. brevis* drivers on the exemplar, which would add new bytes to Atlantis (SO-3, ADR-002 §4). | Ruling 1(c): M-3b targets FKNMS or a new instance. The exemplar is allowed only for a driver derivable from the three grandfathered parquets. |
| G-9 | minor | — | T3's falsifier was restated after the result, and "does not close" has no number. | Register: the restated falsifier gets a number (the persistence comparator's share of the model's AUPRC lift) at its next test. Noted in T3's row. |
| G-10 | minor | C-032 | The brief's "+76% to +300%" left out M-2a-i (+57%) and reviewer tokens (≈ 190–260 kT per mission). | Ruling 1(b): P3 is re-carded at ≈ 2.3× the card top, with reviewer tokens included. |
| G-11 | nit | — | Charter header `phase: P1`; §Status "M-2b ⏭"; the router's Atlantis row is stale ("Proteus (prop.)", "P0 gated"). | Charter fixed at this gate. The stale row is added to the Hestia memo (ruling 4). |
| G-12 | nit | — | No calendar-plus-signal comparator: the model has no season vital, and climatology has nothing else. | Optional in M-2c. |

## The reviewer on R1–R4 (summary)

**R1, amend.** The weak reading was not invented after the result. M-0's falsifier and the M-2 card both read it that way, and the exit bar's second clause expects Atlantis edits. Two corrections:
- On 2026-10-06 the strong reading was applied to move core changes ahead of the fork, which makes the fork look cleaner than it was.
- Under the campaign's own rules the weak form cannot fail.

Honest statement: met as worded; drop-in not demonstrated; ≈ 13–15 forced changes.

**R2, amend.** Agree on T1, T3, T10 and T8. Changes: T11 untested at its terms; T4 untested on FKNMS; a note on T2; T5 and T12 recorded.

**R3, agree with stronger conditions.**
- M-2c also re-runs FKNMS as v3 with the new slot, through the steward's memo, and adds a season-block paired interval.
- Budgets are set from the observed ratio, plus the reviewer.
- (c) M-3b's target.
- (d) The P4 bar is defined before P4.
- Second opus gate (P1, P2): **recorded as a deviation from the charter's fable rule, not amended** (operator ruling 1).

**R4, amend.** Settle G-6 before pushing. Redraft the graduation memo for all six candidates. Add the stale row to the Hestia memo.

## ACCUMULATE (applied by the desk after the rulings, local store only)

C-009 → 7 · C-030 → 2 · C-032 → 2 (one recurrence covering G-2 and G-7) · new **C-033** `recard_drops_register_obligation` · new **C-034** `status_supported_off_falsifier_operating_point`. Graduation candidates are unchanged: C-004 · C-005 · C-009 · C-010 · C-015 · C-023.

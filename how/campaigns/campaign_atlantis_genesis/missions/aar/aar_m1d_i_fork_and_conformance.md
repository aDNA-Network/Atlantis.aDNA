---
type: aar
doc_id: aar_m1d_i_fork_and_conformance
title: "AAR — M-1d-i fork from templates alone: atl_v0 0.3.0 · contract v0.2.0 · fetch gates · template_instance · fork · conform · skill · dry run (P1, Operation Tidewatch)"
mission: mission_m1d_i_fork_and_conformance
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: opus
token_budget_estimated: "~110-130kT main + fresh-context III reviewer (build-sized)"
token_budget_actual: "≈295kT main (≈220 build + ≈75 III fixes; ≈ +130%, PAST the +50% trip at ⑧ — operator ruled continue) + ≈241kT fresh-context III reviewer"
session: session_stanley_20261003_210703_m1d_i_fork_and_conformance
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [aar, m1d_i, p1, atlantis_core, fork, conform, fetch, selftest, ontology, contract, iii, atlantis, tidewatch]
---

# AAR — M-1d-i: fork from templates alone

**Commits:**

| Commit | Content |
|---|---|
| `999a9fa` | ① open: M-1d split, cards i/ii |
| `8b6a8e6` | ② atl_v0 0.3.0 |
| `6a04bd7` | ③ contract v0.2.0 |
| `19d9046` | ④ receipt · fetch CLI · R8 |
| `e38d4dc` | ⑤⑥ template_instance · fork · conform · self-test generalised |
| `d431a5d` | ⑦ skill |
| `fe3c371` | ⑧ dry run · posture gate |
| `bcdcc89` | session log, budget trip recorded |
| `16558df` | ⑨ III fixes |
| close | bookkeeping |

**Operator rulings (`AskUserQuestion`):**
1. Split M-1d into i and ii.
2. Amend the contract in place to v0.2.0.
3. The dry run is a fictional hypoxia instance.
4. atl_v0 goes to 0.3.0 with controls.
5. At the +50% budget trip after ⑧: **continue** with the III review and AAR in this sitting.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| atl_v0 0.3.0 | `ingested_at` optional; rule `sha256` ⇒ `ingested_at` with the typed `all_of` arm. Controls 42 → 45, ALL WORLDS AGREE; the committed JSON equals a fresh generation. Two sabotages: removing the rule turns both negatives red in all three worlds; removing the `all_of` arm turns only the null twin red. Board v1 still validates |
| Contract v0.2.0 | Repointed to the real files (`units.yaml` · `atlantis.yaml` · `events.yaml`) and the real self-test command. Item 3 is staged declared → fetched. Item 5 has a home for "declared absent". Items 6 and 7 are enforced by the fetch CLI. Every item has a machine check. The federation pin README and CLAUDE.md SO-7 are fixed |
| Receipt + fetch CLI (WI-15) | `selftest` writes a receipt bound to the config's `semantic_hash` **and the self-test's own code**. `python -m atlantis_core.fetch` refuses without it. A network fetch also refuses unless the instance's own posture ruling carries a signed Ratification row. On the exemplar, `--verify` passes 3/3 pins and `--offline` gives 3/3 cache hits, with no network; a network fetch is refused (no pin, no new snapshots) |
| R8 | Surveillance is declared, read and ablated, or declared absent with a reason, and then nothing claims it. 12 defects tested; the check is outside `semantic_hash` |
| `template_instance/` + `fork` | 8 templates + `answers.example.yaml` (fictional). The fork is deterministic. **27 refusal cases** plus the overwrite check are tested, each writing nothing; R1–R8 run on a temporary render first |
| `conform` | Contract items 1–12, one ✅/✗ each with the files read. Item 6 re-runs the self-test. Item 12 uses Atlantis's gitleaks config. It writes nothing. **36 per-item planted defects** plus 21 gate tests (57 in `test_conform.py`), each caught at its item |
| Skill | `how/skills/skill_atlantis_instance_fork.md`: interview → answers → vault shell → fork → mapping → conform → self-test → owner signs posture → fetch → conform (fetched) |
| **Dry run** | Below. Items **1–8 and 11–12 ✅**, no network |
| Byte-stable set | `git diff 4bb1939` over board v1 (and v0) · `config.yaml` · `atlantis.yaml` · `outputs/` · the v0 page is **empty**; the v1 page is unchanged since `dc8763a` |
| III review via `iii/`, fresh context | PASS-WITH-FINDINGS: 3 major and 6 minor, **all addressed** (below) |

`what/atlantis_core`: **330 tests**, offline (183 → 330), ~8.5 min; the catalogue runs in two forked worlds. Both SO-7
self-tests are green. The exemplar's 11 tests pass.

## The dry run (P1 exit bar)

*Sandbar Estuary*, a fictional instance in the scratchpad, never committed. It has:
- a `below` event (DO ≤ 2 mg/L within 2 weeks) on a **station-keyed** daily stream, two sondes averaged at the primary;
- gridded SST with a climatology era;
- a polygon grid by pointer;
- surveillance **declared absent**.

The vault shell is `skill_project_fork` step 3, run by hand into the scratchpad. The declarations are
`atlantis_core.fork` from `answers.yaml`. Every command ran under a guard that refuses and counts outbound socket
connects **in the Python process**. Subprocesses (gitleaks, git) are outside the guard; neither connects in these
invocations, but the guard does not prove that (III F-9). Re-run after the III fixes:

```
$ fork --answers answers.yaml --out <vault>                          → rc 0 · 0 sockets · 2 streams (declared) · 5 starter vitals · R1–R8 clean
$ mapping --check <vault>/mapping.yaml                               → rc 0 · 0 sockets
$ conform --items 1-8,11,12 --stage declared                         → rc 0 · 0 sockets · ✅ 1 2 3 4 5 6 7 8 11 12 (6 re-run · 7 "ruling present, not yet ratified")
$ fetch                                                              → rc 1 · 0 sockets · refused: no self-test receipt
$ selftest                                                           → rc 0 · 0 sockets · C0/C8/C1/C2/C3/C7 per stream · "gap t−2 crossed by no lag: C8 alone guards it" · C2b · C5 (mirror: above) · C6 reported
$ fetch --stream sst                                                 → rc 1 · 0 sockets · refused: Ratification row not signed
$ # status word flipped to ratified, table blank (the FIRST dry run's "ratification")
$ fetch --stream sst                                                 → rc 1 · 0 sockets · refused: Ratification row not signed
$ # owner signs the row (decision · ratified-by · 2026-10-03 · ratified)
$ conform --items 7 --stage fetched                                  → rc 0 · ✅ 7
$ fetch --offline                                                    → rc 1 · 0 sockets · NDBC declared-not-built · ERDDAP "offline: would fetch …"
$ fetch --stream do                                                  → rc 1 · 0 sockets · NDBCStdmet declared, not built
$ conform --items 3 --stage fetched                                  → rc 1 · not fetched (honest)
```

**Verdict:** a fresh instance forks from templates alone, in one sitting, with the self-test green before any real data
is fetched. Two exceptions, stated:
- **Declared stage only.** A stream's `fetch` spec comes from the source's documentation and the steward, not from the
  interview (F-8).
- **The NDBC fetcher is declared, not built.** The first instance with a buoy stream builds it in Atlantis (the P2 rule).

## III review (fresh context, `iii/` → `skill_iii_review`, III v0.6.0)

Every finding was demonstrated with a planted input (scratch files in `scratchpad/iii_review/`).

| # | Severity | Finding | Fix |
|---|---|---|---|
| F-1 | major | On a **daily event stream** (the dry run's shape) the self-test missed a back-filled already-in-event state and a horizon counted in observed weeks. The label-exposing gaps were tied to point streams | The event stream carries those gaps whatever its shape: primary unobserved at t+2 (t+1 when H = 2), neighbour at t−1 and t. Every daily neighbour is unobserved at t−1 and t. Spikes insert into unobserved days. **The whole 12-defect catalogue runs against two forked worlds**, each caught by name. Label comparisons are NA-safe (short_horizon had been a TypeError). The receipt is bound to the self-test code. A pre-existing exemplar blind spot, a back-filled weekly mean, is now caught |
| F-2 | major | `gap_week`, my fix for a vacuous lag-1 vital, moved the row-lag probe to a blind spot. With the fork's default lags, a lag counted in rows passed | **C8 calendar-lag invariance:** deleting (t−L, t] must not move a lag-L vital. The run names when C8 alone guards a stream. In the exemplar, C8 now catches row-lag and the late week-end sample first |
| F-3 | major | The posture gate could be bypassed: (a) a ruling path outside the instance (Atlantis's ADR-000, a sibling's ADR); (b) a one-word frontmatter flip | One shared reading for fetch and conform: the path is relative and inside the instance; the declared Class matches the pin; ratified means a signed 4-field row **and** an agreeing frontmatter |
| F-4 | minor | Absolute and `../` paths passed "inside the instance"; a `cells` bbox passed under a partner posture | Paths are confined. A `cells` bbox is refused off-public, like `rules`; fetch `boxes` and synthetic self-test points are stated as not site geometry |
| F-5 | minor | Items 10, 2, 12, 9 and 6 checked less than their rows | Item 10: a real, non-empty `#limits` section plus the analogy. Item 2: an authority allowlist. Item 12: Atlantis's gitleaks config, with instance allowlists ignored (inline `gitleaks:allow` is a stated limit). Item 9: the entry is tied to this instance's `unit_ref` and `semantic_hash`. Item 6: independent of the items requested |
| F-6 | minor | "A refusal writes nothing" was false: R1–R8 ran after the write | R1–R8 run on a temporary render first; the sentence is now true in all three documents |
| F-7 | minor | Docs did not match code (conform "opens nothing under data/site"; §A `version`; README fetch row) | Corrected |
| F-8 | minor | "From templates alone" held only for the declared stage; fetch specs were unvalidated | Built fetchers declare `spec_required`, and fork checks it. The limit is stated in the skill and the answers example |
| F-9 | minor | "Zero sockets" covered only the Python process | The guard's scope is stated in the transcript and here |

**Learning store** (`how/federation/iii/what/context/atlantis_iii_learning_store.jsonl`):
- C-004 → **3** and C-009 → **3**: graduation candidates for the ADR-003 ceremony at III.aDNA, the operator's call.
- C-005 → 2 · C-013 → 2.
- New: **C-014** `generalised_input_shape_keeps_old_shape_fixture` · **C-015** `fallback_relocates_probe_to_blind_spot` ·
  **C-016** `pointer_check_not_confined_to_root` · **C-017** `approval_gate_reads_agent_writable_status`.

## Worked

- **Forking the example was the best test of the self-test.** The first fork found that the self-test only understood
  point event streams. The second found the C4 interplay with lag-1 daily vitals. Neither shows up on the exemplar.
- **Planted defects in my own tests caught my own guard once.** Item 7's "names the class" passed on the template's prose
  until a planted defect showed it (fixed before review).
- **The dry run found a gate that existed only in prose:** "ratify, then fetch". It became code at ⑧.

## Didn't

- **C-009, a fourth mission running.** The reviewer found three guards narrower than their names, and tests that asserted
  the narrow behaviour: the word-flip ratification, the empty `#limits` section, and `gap_week`. The planted-defect
  discipline caught one of my guards; it did not catch these, because **the tests encoded my own idea of the gate, not the
  document's** (the ADR template's 4-field block).
- **A fix moved the blind spot instead of closing it (C-015).** I patched C4's vacuity by relocating the gap, and I wrote a
  test asserting the new placement was right. The loud failure was the check working.
- **Budget.** ≈295 kT against ~120. The card was cut before the self-test was known to be point-only. Generalising it,
  then hardening it under review, was most of the overrun.

## Finding

1. **The exit bar is met, and honestly so only after the review.** The first dry run's ✅ rested on a self-test that missed
   known leak classes on its own event-stream shape, and on a posture "ratification" that was a word flip. Both are now
   closed, and the dry run was re-run on the hardened code.
2. **The self-test is now shape-general:** point, unit-daily and station-daily event streams; above and below (C5 mirrors);
   any lag set (C8). The catalogue proves it in two forked worlds as well as the exemplar.
3. **Instances will need fetchers Atlantis has only declared.** The very first rehearsal needs NDBC. Building one is
   Atlantis's job, by the P2 rule.
4. **The exemplar is a reference run, not a conformant instance.** It has no `units.yaml`, `mapping.yaml` or posture pin,
   and `conform` says so. Its network fetch is refused, which matches ADR-002 §4.

## Change

- **A gate's test plants the document's own example of a forged approval** (C-017): a status word, a blank signature,
  a path elsewhere.
- **When extending a check to a new input shape, re-run the whole defect catalogue on the new shape** (C-014). A subset
  does not count.
- **A fallback that silences a failure must name what it disables** (C-015). Otherwise, keep the failure.
- **Budget the self-test as a unit of work.** Any card that lets the core accept a new input shape carries the self-test
  generalisation and its catalogue run explicitly.

## Follow-up

- **M-1d-ii** (opus): the pipeline lattice (with the `fetch` node's two gates), the runspec, `BOARD.md` (WI-8), dataset
  pairs (fix the template first), the contribution guide, and `board --entries` for instances. Then the **P1 gate**
  (fable, operator), where ADR-002 A-1 is ratified.
- **NDBCStdmet**: built in `atlantis_core` when the first instance needs it (M-2's gridded-only FKNMS does not).
- **Exemplar conformance (optional):** a `units.yaml` + `mapping.yaml` would let the exemplar pass items 1 and 11.
  Its posture stays "grandfathered exception" (ADR-002 §4 / A-1), not an instance ruling.
- **Test-suite time** (~8.5 min): mark the two-world catalogue `slow` if it starts to hurt.
- **Memos after the gate:** Rosetta — `lattice_validate.py` has no CLI (M-1d-ii will need it), and the dataset-pair
  template fails its schema. III.aDNA — C-004 and C-009 at frequency 3 (graduation is the operator's call).

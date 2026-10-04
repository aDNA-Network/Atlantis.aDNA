---
type: aar
doc_id: aar_m1d_ii_lattice_and_registries
title: "AAR — M-1d-ii pipeline lattice · runspec · BOARD generator · dataset pairs · contribution guide (P1, Operation Tidewatch)"
mission: mission_m1d_ii_lattice_and_registries
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: opus
token_budget_estimated: "~80-100kT main + fresh-context III reviewer (build-sized)"
token_budget_actual: "≈177kT main (≈136 build to the review + ≈41 III fixes and close; ≈ +77%, PAST the +50% trip after ⑧ — operator ruled 'fix all, then close') + ≈231kT fresh-context III reviewer"
session: session_stanley_20261004_002004_m1d_ii_lattice_and_registries
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [aar, m1d_ii, p1, lattice, runspec, board, datasets, contribution_guide, iii, atlantis, tidewatch]
---

# AAR — M-1d-ii: lattice · runspec · BOARD · dataset pairs · contribution guide

**Commits:**

| Commit | Content |
|---|---|
| `3e787d3` | ① open |
| `b44111c` | ②③ lattice + checks |
| `8dbcda6` | ④ runspec |
| `12e8e35` | ⑤ BOARD + `--entries` |
| `16c4657` | ⑥ dataset pairs |
| `ddce2d8` | ⑦ contribution guide |
| `eb68b43` | core README |
| `8ca7bc5` | ⑨ III fixes |
| close | bookkeeping |

**Operator rulings (`AskUserQuestion`):**
1. The runspec is **validate + plan**: it executes nothing, because execution belongs to P5's Ray run-spec, with operator GO.
2. The lattice carries **both conform gate nodes**.
3. At the budget SITREP after the review (≈ +36%, with 14 findings to fix): **fix all, then close**.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| Pipeline lattice | `how/lattices/lattice_atlantis_pipeline.lattice.yaml`. The order is `discover` (declared-only until M-3a, and a runspec naming it is rejected) → `conform_declared` → `selftest` → `fetch` (two gates, in config and on the edge) → `conform_fetched` → `grid`·`vitals`·`label`·`train`·`eval`·`explain` (invoked by `atlantis_core.run`, said so) → `board` → `site`. Dataset nodes: declarations · raw_streams · board_entry. The self-test is drawn **before** fetch, per §Inputs from M-1d-i |
| Validated by both | `atlantis_core.lattice` checks three ways: the strict schema (Atlantis's byte-identical copy, tested equal to the peer's), the peer `validate_lattice_file` imported by path (no CLI; the peer is untouched; warnings count), and local invariants. Tests record the peer's gaps: unknown fields and cycles pass it. After review: dominance, AST flag and `__main__` checks, and run block = runspec |
| Runspec | `atlantis_core.runspec` + `how/templates/template_runspec.example.json`. Closed keys at both levels (DDX ignores unknown keys; this does not). Duplicate JSON keys, NaN and huge integers are rejected. No coercion. **A planted defect for every field** (66 tests). `--plan` prints and runs nothing; exit 3 = REJECT |
| `BOARD.md` (WI-8) | `board --index [--check]`: byte-stable, compared as bytes, and every entry is checked or the render refuses. v0 is rendered and **labelled open-shape**, grandfathered by id **and pinned sha256**, and shown superseded by v1 (derived). **WI-8 closed** |
| `board --entries` | Must end in `what/board/entries`. Provenance stays repo-relative. The instance and its outputs must sit inside that repo, so an outside instance cannot write Atlantis's board. Tested: emit → index → conform item 9's reader |
| Dataset pairs (WI-18) | **Template first.** Fixed against the lattice-labs schema; a copy of the schema now sits beside it. `atlantis_core.datasets --check`. Three pairs, with every pin agreeing across pair · `.md` · bytes · `streams.yaml` · board v1. `dataset_hab_env_covariates.md` superseded in place. `dataset_fwc_hab_karenia.md` was **upgraded** in place rather than superseded (the card said "the two ad-hoc notes superseded in place"); its stem and stream did not change. **WI-18 closed** |
| Contribution guide | `who/governance/contribution_guide.md`, **draft 0.1.0**, raised for ratification at the P1 gate. It covers: what crosses / never crosses · the memo-to-inbox flow · DCO v1.1 (not CI-enforced in P1, and it says so) · checks by class · tiers draft → reviewed → validated. Also `who/coordination/inbox/` |
| III review via `iii/`, fresh context | PASS-WITH-FINDINGS: 2 major, 7 minor, 5 notes. **All addressed** (below) |
| P1 exit bar → fable review requested | Below (Follow-up) |

Tests: `what/atlantis_core` went 330 → **475**, offline (~2 min unloaded). The SO-7 self-test is green at open and close.
**Byte-stable set:** `git diff 4bb1939` over board v0 and v1 · `config.yaml` · `atlantis.yaml` · `outputs/` is **empty**,
and the v1 page is unchanged since `dc8763a`.

## III review (fresh context, `iii/` → `skill_iii_review`, III v0.6.0)

| # | Sev | Finding (demonstrated) | Fix |
|---|---|---|---|
| F-1 | major | `--outputs` pointed at the exemplar let an outside instance write Atlantis's board. The gate checked a proxy | Gate on the instance root; require `--outputs` inside it (C-018) |
| F-2 | major | `BOARD.md` rendered entry strings verbatim: a newline in `superseded_by` or `limitations_ref` put a fake "OPERATIONAL FORECAST" heading on the board | Closed top level · entry_id grammar · `superseded_by` must name an entry · line breaks and control characters refuse · `\|` escaped (C-012 → 2) |
| F-3 | minor | `--regenerate` failed open: `origin/main` was hard-coded, and a git error read as "unpublished" | Fail closed on any error, no remote, or no upstream; read all remote-tracking refs (C-021) |
| F-4 | minor | The gate order was checked as reachability, so a bypass edge passed; command flags were never checked | Dominance · AST argparse flags and `__main__` guard · `invoked_by` set = the runspec's run block (C-020) |
| F-5 | minor | In a public clone (no peer validator) a dangling edge passed | Local edge-reference and duplicate-id checks; NOT RUN is printed (C-015 → 2) |
| F-6 | minor | The datasets byte check silently skipped absent bytes | Error when the record promises the bytes; otherwise a "pin not verified" note (C-019) |
| F-7 | minor | Python's `$` accepted a trailing newline in checksum, stream-id and date patterns | `\Z`, and `[0-9]` for dates (C-002 → 2) |
| F-8 | minor | My claim that "no `.dataset.yaml` in the workspace passes the schema" was **false**: 2 of 26 pass (both in Archive lattice-labs `campaign_quantum_protein_lattice`) | Corrected here and in the session log. The commit message for `16c4657` keeps the false sentence; this AAR is the correction of record |
| F-9 | minor | v0 showed as "live", and README lifecycle 5 asked for an edit that SO-2 forbids and v0's pin refuses | Supersession is **derived**; lifecycle amended |
| F-10 | note | A 5000-digit integer crashed the runspec | REJECT; version capped at 9999 |
| F-11 | note | `--check` compared decoded text, so a CRLF copy passed | Compare bytes; write bytes |
| F-12 | note | Relative `location.path` contradicts the schema's "absolute" description | Declared as a deviation in the template (an absolute path names one machine in a public repo) |
| F-13 | note | Doc nits: the coord-note naming claim · the inbox's "only way" · OISST end date 2024-01-01 · "workspace Rule 10" (the router has 1–9) · datasets command cwd | Fixed |

What the reviewer found holding:
- The runspec survived every smuggling attempt (bool, list and dict values · NBSP and newline ids · nested and escaped
  duplicate keys · BOM · Infinity).
- The grandfather list cannot be abused.
- The peer gaps are real.
- `rel()` provenance is correct.
- Every dataset fact is true: hashes, rows, dates, layers, sites, the clip at fetch, the zero and percentile figures.

The reviewer wrote one stray entry into `what/board/entries/` while probing F-1 and moved it to the scratchpad itself.
`git status` was verified clean afterwards.

## Worked

- **Scouting before the plan paid for itself.** Three read-only scouts surfaced the facts that shaped the design:
  - Atlantis already carried a copy of the strict lattice schema;
  - DDX's "closed vocabulary" ignores unknown keys;
  - nothing in the workspace's lattice-labs datasets passes the schema (refined by F-8: almost nothing).
- **One source for the stage vocabulary.** The runspec reads it from the lattice, and after review the lattice's run
  block is checked against the runspec. Neither can drift alone.
- **Each reviewer demonstration became a test**, 22 in all. 453 → 475.

## Didn't

- **Two gates checked a proxy instead of the thing.** `--outputs` stood in for the instance (F-1). Reachability stood in
  for a gate (F-4). Both are classic. C-018 and C-020 are new.
- **I asserted a workspace-wide negative from a sample** (F-8). The scout validated 10 lattice-labs records plus a few
  others, and I wrote "nothing in the workspace".
- **A renderer was trusted because its input had been validated** (F-2). Schema-valid strings can still carry markdown.
- **Budget:** ≈ +77% (≈177 kT main against 80–100). The build alone was ≈ +36%; the 14 findings did the rest.

## Finding

1. **The method is now written down as one executable lattice**, and three independent checks hold it. The peer
   validator would have accepted both a cycle and an unknown field; it is a necessary check, not a sufficient one.
2. **An open-shape record has no closure but its bytes.** v0's evaluation has no closed key set, so the only honest way
   to keep showing it is to pin it by sha256. Its status, "superseded", has to be derived, because the record can never
   be edited.
3. **Validation and rendering are different trust boundaries** (C-012 recurring). Anything that turns data into markup
   needs its own refusal rule.

## Change

- **Gate on the identity, then require the proxy inside it** (C-018).
- **A gate in a graph is dominance, not reachability.** Plant a bypass edge (C-020).
- **A safety probe that shells out fails closed** (C-021).
- **A pin check with an absent target is never a silent pass** (C-019).
- **Before a "nothing in X" claim, enumerate X** (F-8). A sample yields "none of the N checked".

## Follow-up

- **The P1 gate** (fable, operator-summoned). It decides:
  - the P1 exit bar (fork from templates alone ✅ M-1d-i; `atlantis_core` reproduces the exemplar ✅ M-1b-ii-a;
    controls under both validators ✅ M-1c; III via wrapper ✅ every lane);
  - **ADR-002 A-1** (`#needs-human`);
  - **the contribution guide** (draft 0.1.0);
  - the **C-004 / C-009 graduation** question (frequency 3).
- **Memos after the gate:**
  - **Rosetta:** `lattice_validate.py` has no CLI, its docstring import is stale, its `additionalProperties`/cycle gaps,
    and its package `__init__` eagerly imports canvas tools.
  - **lattice-labs / Datasets.aDNA:** 24 of 26 `.dataset.yaml` fail the schema, and `location.path` is "absolute" in a
    public-repo world.
  - **DDX:** the runspec ignores unknown keys.
- **WI-8 and WI-18 closed.** Board v2 (the F-8 eval fix, WI-11, and the WI-14 limitations_ref) remains carded.
- If the suite time hurts, mark the two-world catalogue `slow`: unloaded it is now ~2 min, loaded ~13.

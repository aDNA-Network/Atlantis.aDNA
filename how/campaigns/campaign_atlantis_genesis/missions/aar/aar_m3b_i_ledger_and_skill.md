---
type: aar
mission: mission_m3b_i_ledger_and_skill
campaign: campaign_atlantis_genesis
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261012_085758_m3b_i_ledger
tags: [aar, m3b_i, p3, hypothesis_ledger, literature_mining, envo, faithfulness, iii, atlantis, tidewatch]
---

# AAR — M-3b-i: the hypothesis ledger, the mining skill, and the first ledger (coral_reef)

**Scope.**
- The first half of M-3b, which was split at open: atl_v0 **0.9.0** `AtlHypothesis`; core **0.9.0**
  `atlantis_core.hypotheses` (corpus · check · index · stamp); `skill_feature_hypothesis_mining`.
- The first ledger: `coral_reef`, read for FloridaKeysCoral's DHW ≥ 4 onset.
- The hand-off memo, ending on the realisation ruling.
- Folded in: the Noether ack, delivered.

**Rulings** (`AskUserQuestion`, operator, 2026-10-12):

| # | Ruling |
|---|---|
| 1 | Split M-3b into two halves (C-042: split at open) |
| 2 | The driver is ruled after the ledger; mine broadly |
| 3 | The corpus is a committed manifest only. Abstracts sit in a gitignored `unreviewed/`, and rows quote ≤ 25 words (SO-3) |
| 4 | Deliver the staged Noether ack; commit the interim notice as the read receipt |
| 5 | At the +50% SITREP: re-card ≈ 170 → ≈ 460 kT main, and continue |
| 6 | III fixes: the majors and the code minors before close |
| 7 | **M-3b-ii realises reef-light wind** (NDBC C-MAN at the Keys' reef lights) |
| 8 | Accept the reviewer's ACCUMULATE: C-043 and C-044 new, plus eight frequency bumps |

## Worked

- **The schema took the row cleanly, and the controls found a generator trap on the way.** An optional inlined object
  is emitted as `anyOf [object, null]`, so a defect inside it rejects only as an unnamed branch. `driver_lag` and
  `realisation` became required. The III review's sweep then found 16 required claims with no control. There are now 19
  `neg_hypothesis_without_<slot>` controls, and the sweep is proven: each removal reddens exactly its own control.
  **126 controls, ALL WORLDS AGREE.**
- **ENVO was looked up, not assumed.** The ledger key binds biome terms (coral reef ENVO:01000049, not the feature
  ENVO:00000150), and the binding is scoped to the ledger. `neritic_shelf` was renamed `neritic_pelagic` before any row
  used it (F-12e).
- **The verbatim check earned its keep at once.** It caught two of my 32 quotations, both from U+2010 hyphens in real
  abstracts. That was a checker gap, fixed plant-first.
- **The two-reader design worked as intended.** The fresh-context faithfulness reader caught what no code could: hedges
  stripped from 9 mechanisms, and the "no sign, no row" rule broken on 4 rows that the memo said it held. The III
  reviewer then caught what the reader's rules did not bind: `reviewed` was not tied to its content, the cache was not
  tied to its hash, and single quotes bypassed every check. Each layer found a different class of defect.
- **The C-042 stop came before any paper was read,** at a clean commit, so the operator's choice was a real one.
- **Intake was cheap and reproducible.** A `--refresh` under the fixed tag stripper reproduced all 380 works, every
  abstract hash and the result sha256.

## Didn't

- **The budget line was crossed during the core build and reported at ≈ 310 kT, about 55 kT past it** (III F-10).
  Better than M-3a's report at close, still not *at* the line.
- **Main closed at ≈ 508 kT** against ≈ 460 re-carded (+10%), plus the faithfulness reader (≈ 133 kT, metered; it was
  on no budget line) and the III reviewer (≈ 278 kT metered, against ≈ 150 carded).
- **My extraction overstated papers.** I stripped hedges in 9 of 32 mechanisms. I broke the no-sign rule on amm_001,
  enso_001, sea_level_anomaly_001 and winter_warming_001. I built a winter-SST → DHW link no sentence states. I called
  two pairs of rows "contradictions" when their events differ.
- **The hand-off's first draft claimed a discipline it had not held,** and ranked as "cheap" a candidate (winter SSTA)
  that rested on an unsupported row.
- **The first count was by hand** (12/16/4 → 10/12/4 → 9/12/5). It is now a closed field counted by code (3/6/11/6).
- **`check` was weaker than its words** (III F-2, F-3, F-9):
  - the cache was trusted, not verified;
  - single quotes bypassed the quote checks;
  - a fragment after "not" passed;
  - the 25-word cap guarded only the pointer;
  - `reviewed` was an editable word.

## Finding

1. **Quotation checks prove the pointer, not the paraphrase.** A row can quote faithfully and still overstate its paper
   in `mechanism`. Code can bind a quote to the text (hash, word boundaries, negators); only a reader binds the
   mechanism. Both are needed, and the ledger now records which reader confirmed what (`reviewed_sha256`).
2. **The coral literature mostly studies the response, not the onset.** By the paper's own outcome, 15 of 26 rows are
   about bleaching or cover given heat. Against a DHW-defined event, more than half the ledger tests a different event.
   That is context for T12, not evidence on its claim (F-5).
3. **No reviewed heat-onset row is realisable from FKNMS's existing streams.** Every honest test of the literature on
   this event needs one new stream. The cheapest candidate, NDBC, is a declared fetcher (WI-19).
4. **The event-matched literature for the ruled driver is thin and remote.** Wind has 2 reviewed rows: a Persian Gulf
   sea-*bottom* model, and one Brazilian season. The 4 m/s threshold is a regional transfer and must be scanned, not
   fixed. Cyclone cool wakes had 1 row, but it was the closest in event and region. The ruling chose more rows,
   farther away, at the highest cost.

## Change

- **atl_v0 0.9.0:**
  - `AtlHypothesis` + 5 inner classes, all closed;
  - 8 enums, including the closed `Realisability`;
  - `reviewed_sha256`;
  - `EcosystemType` bound to ENVO;
  - 126 controls with the required-removal sweep;
  - README known limit 18;
  - crosswalk `envo` → bound; fit matrix §9.
- **Core 0.9.0 `atlantis_core.hypotheses`:**
  - `corpus` — fails closed, `--allow-partial`; a socket guard propagates; tags only are stripped;
  - `check` — 21 failure keys, including `cache_tampered`, `pointer_unparsed`, `quote_after_negation`,
    `verbatim_overflow`, `reviewed_unbound`, `reviewed_content_changed` and `row_misplaced`;
  - `index` — realisability counted; `--stamp-review`;
  - 46 offline tests; each new guard mutation-checked (disabled → its plant fails).
- **Skill:** steps 3, 4 and 6 hardened from both reviews:
  - keep hedges; paraphrase; the paired-sign reading;
  - a window is not a lag; `realisability`;
  - reviewed promotion by stamp; the reader flags `realisable_as`;
  - the reader lane budgeted.
- **The ledger** (`coral_reef`):
  - 32 extracted → 26 rows (14 `reviewed`, hash-bound; 12 draft);
  - 6 withdrawn to `withdrawn/` with reasons (SO-2);
  - realisability existing 3 · declared 6 · new 11 · unrealisable 6.
- **One deviation from the reviewer's fix, recorded:** the per-work copy cap counts the non-quotation fields. Each row's
  quotation stays capped by ruling 3 (≤ 25 per row). Two rows quoting one paper may therefore carry two quotations;
  copying through `mechanism` is what the work-level cap guards (plant P7).

## C-033: register obligations

The register was re-read before this AAR. No row's status changes.
- T7 and T8 → M-3b-ii.
- T11 and T2 → the P3 gate.
- T9 +0: planned deliverables. FKNMS's mapping pin move is M-3b-ii federation upkeep.
- T8 interim, amended per F-5: the falsifier's quantifier is a reading for the gate (6 of 26 rows are unrealisable).
- T12: the event skew is context.

## III

**PASS-WITH-FINDINGS 0/2/8/2** (`iii_review_m3b_i.md`), fresh context via `iii/`.

| Finding | Disposition |
|---|---|
| F-1 | fixed: 19 required-slot controls + the year maximum + the citation's closed shape; sweep proven |
| F-2 | fixed: cache hash-checked; every quote glyph a quotation; unparsed pointers fail |
| F-3 | fixed: word boundaries, the negator guard, `reviewed_sha256` |
| F-4 | fixed: `realisability` closed and counted; dhw_001, cyclone_power_001, heat_flux_001 and wind_004 corrected; memo "wind ×5" |
| F-5 | fixed: the register and memo state the quantifier as a reading; T12 is context; `updated:` corrected |
| F-6 | fixed: strength read on event-matched rows; the threshold is a transfer; the trade-off was put to the operator |
| F-7 | amo_002 demoted (`review`, draft); the paired-sign reading written into the skill, so enso_002 stays |
| F-8 | fixed: intake fails closed; the guard propagates |
| F-9 | fixed: `verbatim_overflow`; hurricane_001 paraphrased (with the deviation above) |
| F-10 | recorded here |
| F-11 | suite count recorded below |
| F-12 | (a)–(e) fixed |

ACCUMULATE (local, ruling 8): new C-043 and C-044. Bumps: C-003 → 3, C-017 → 2, C-032 → 5, C-034 → 4, C-037 → 4, C-039 → 3,
C-041 → 2, C-042 → 2, each with its recurrence recorded.

**Suite:** 820 passed at `b989318`; 822 at `bf5a6a8` (the reviewer's run); **834 at `dcdbe65`** after the III fixes (284 s;
C-035).

## Follow-up

**For M-3b-ii:**
- build `NDBCStdmet` (WI-19);
- a steward ruling on the station-to-zone map and the calm threshold (scanned; 4 m/s is a Persian Gulf model's);
- FKNMS's `mapping.yaml` pin → 0.9.0 (federation upkeep);
- fetch under the instance's posture;
- self-test (SO-7);
- read against board v3 at 15.0% and v3's budgets (C-031, C-034);
- written up either way (T8);
- T7: "no lever, still".

**Carried:**
- preconditioning_001's evidence class (the reader's case rests on recall; read the full text);
- a second reading of the 12 draft rows;
- `validated` needs a second-reviewer slot;
- Ingest.aDNA has no literature class (the standalone intake stands in; a memo to Demeter after the gate);
- the reviewer's own budget overrun (≈ 278 vs ≈ 150 kT): card future reviewers at the observed figure.

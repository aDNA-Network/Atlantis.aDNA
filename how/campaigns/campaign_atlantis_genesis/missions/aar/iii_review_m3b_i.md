---
type: iii_review
review_of: mission_m3b_i_ledger_and_skill
commits:
  atlantis: [6dce435, e77f534, b5a01bf, 507924b, b989318, 73c0d1c, 916f8b9, bf5a6a8]   # diff vs 4e2432b
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-12
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 2, minor: 8, nit: 2}
tags: [iii_review, m3b_i, hypothesis_ledger, atl_v0_0_9_0, literature_mining, envo, so3, atlantis, tidewatch]
---

# III review: M-3b-i (atl_v0 0.9.0 `AtlHypothesis` · core 0.9.0 `atlantis_core.hypotheses` · `skill_feature_hypothesis_mining` · the coral_reef ledger · the realisation memo)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` at `be7dba1` = `v0.6.0`):
- packs: inspect procedures, introspect checks, learning store, vault maintenance;
- the Atlantis local store: 42 corrections, C-001…C-042, all applied as checks.

Modalities: text, code and data.

**Reviewer ≠ producer.** I did not write any of this work, and I am not the faithfulness reader
(`agent_faithfulness_reader_m3b_i`). I wrote two things: this review, and two rows appended to the local learning
store. Everything else was read-only:
- every sabotage and plant ran on scratch copies under the session scratchpad, which I then deleted;
- I read the gitignored abstracts in `unreviewed/` (none is quoted here beyond a few words);
- I read FKNMS's `outputs/atlantis_core/shap_summary.json` and LatticeProtocol's git log, both read-only.

I made no network request. The one intake run pointed at a loopback literal with `socket.connect` patched to raise, so
no packet was sent. Neither tree changed apart from the producer's untracked session file, which was already there.

## Verdict: PASS-WITH-FINDINGS (0 blocker · 2 major · 8 minor · 2 nit)

**What holds:**
- **SO-3.** No abstract text is committed:
  - `git ls-files` holds 0 `unreviewed/` paths;
  - `.gitignore:91` covers the cache;
  - no commit in the range adds one;
  - every quotation is ≤ 24 words;
  - the longest verbatim run outside a quotation is 13 words.
- **The corpus record reproduces.** All 359 cached abstracts hash, as bytes, to their manifest `sha256`, and
  `result_sha256` recomputes exactly.
- **Gates and suites are green.**
  - Controls: 103, ALL WORLDS AGREE.
  - `--index --check`: green.
  - `tests/test_hypotheses.py`: 34 passed.
  - **Full suite at HEAD `bf5a6a8`: 822 passed.**
- **The memo's numbers recount from the row files.** The board figures check against FKNMS's own SHAP file.
- **The reader's verdicts were respected.** The 15 `reviewed` rows changed only in `tier` and `reviewed_by` after the
  reader confirmed them.
- **The four withdrawals I sampled are right.**
- **The Noether ack was delivered.** It is byte-identical to the committed copy and is now committed by LP (`a855ae8`)
  as its read receipt.
- **No operator e-mail went to any service.** There is no `mailto`, and no address appears anywhere in the tree.

**The two majors are about claims stronger than their guards:**
- **F-1.** The schema README claims `required` and range constraints that no control proves. I removed `required` from
  each 0.9.0 slot in turn: on 16 slots, all three worlds stayed green, including `realisable_as`, the T8 column. The
  year's upper bound is equally unproven. This breaks the Hard Gate: *"the ontology claims only what a control proves"*.
- **F-2.** "Verified verbatim" is weaker than every surface says:
  - `check` never compares the cached abstract with the manifest's `sha256`, so a fabricated quote plus an edited
    cache passes;
  - a quotation in single or curly-single quotes escapes both the 25-word check and the verbatim check, downgraded to a
    warning that never fails.

**The minors are mostly about the columns nobody re-read.** The mechanism column is now good: the reader fixed it. The
defects have moved to `realisable_as`, `driver_lag` and the memo's roll-ups (F-4 to F-7). These are the inputs to the
operator's realisation ruling and to the T8 reading.

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| Controls | `LINKML_BIN=…/lmvenv/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` | 103 pass × 3 worlds · Rule 4: 16 range classes · committed JSON == fresh · **ALL WORLDS AGREE** ✓ |
| Sabotage: `required` removed, one 0.9.0 slot at a time, JSON regenerated | scratch copy of `atl_v0/`, then the runner | **Caught by a named control** in all three worlds: `driver` · `sentence_pointer`. **`citation`** is red in all three, but only as side effects: the rule's error turns unnamed, plus `anyOf`. No fixture omits it. **Caught only as an unnamed `anyOf` branch, and only in the two JSON worlds** (linkml-validate stays 103/103): `realisation` · `driver_lag`. **Green everywhere (16):** `realisable_as` · `mechanism` · `driver_direction` · `result` · `ecosystem_type` · `event_variable` · `region_asserted` · `evidence_class` · `hypothesis_source` · `lag_value` · `lag_unit` · `threshold_value` · `threshold_unit` · `title` · `year` · `citation_source` (F-1) |
| Sabotage: `maximum_value: 2100` removed from `year` | as above | ALL WORLDS AGREE: the max is unproven (F-1) |
| Sabotage: the reviewed rule's typed `all_of` removed | as above | `_reviewer_null` and `_reviewer_blank` turn red in all three worlds ✓. This is the mutation the session log says failed to apply. It holds. |
| Hypotheses tests · ledger gate | `.venv/bin/python -m pytest -q tests/test_hypotheses.py` · `python -m atlantis_core.hypotheses --index --check` | 34 passed · ✅ 0 warnings ✓ |
| Full suite (C-035) | `.venv/bin/python -m pytest -q` at `bf5a6a8` | **822 passed** (281 s). The record carries 820 at `b989318`. `73c0d1c` and `bf5a6a8` changed `check.py`, `corpus.py` and the tests after that count (F-11). |
| Check plants (scratch copy of `what/hypotheses/`, `--root`) | P1 fabricated quote + edited cache · P2 30-word quote in `'…'` or `‘…’` · P3 fabricated quote in `'…'` · P4 quote starting mid-word · P5 `reviewed_by: Agent_Proteus` vs `agent_proteus` · P6 an invalid row saved as `.yml` · P7 a whole 177-word abstract pasted into `mechanism` · P8 a reviewed row's quote cut to begin just after the paper's "not" | **All eight: 0 failures.** P2 and P3 raise only the warning `locator_only`; the rest raise nothing (F-2, F-3, F-9, F-12) |
| Corpus integrity | per work: the sha256 and word count of `unreviewed/<id>.txt` against the manifest; `result_sha256` recomputed | 357/359 match when read as text. **359/359 match as bytes**: W2522525957 and W2999077452 hold CR characters, which `read_text` folds (F-12). `result_sha256` ✓. 380 works · 359 with abstract · 21 queries · 46 requests ✓ |
| Leakage | longest common word-run between each row's free text and its own abstract; the union of ≥ 6-word runs per work across every committed `.md`/`.yaml` in the diff | Quotations ≤ 24 words. `mechanism` ≤ 13. **Per row, quotation + mechanism reaches 29 distinct abstract words (hurricane_001). Per work across rows, the maximum is 45 (W2156568771: dhw_001 + warm_pool_001)** (F-9) |
| Memo / register recount | script over the 26 row files | 26 rows · 15 reviewed / 11 draft · 6 withdrawn · 28 works for the 32 extracted (24 for the 26 kept) ✓ · **10 / 12 / 4** sums ✓, but "wind ×4" is ×5 · 11 heat / 15 response ✓ · "no reviewed heat-onset row realisable from existing streams" ✓ |
| Board figures in the memo | `what/board/entries/2026-10-08_florida_keys_coral_v3.json` · FKNMS `outputs/atlantis_core/shap_summary.json` (read-only) | base rate 0.1501 ✓ · `fkc_hotspot_daily_mean_t0` 1.561 of 2.447 total ✓ · 9 vitals ✓ |
| Citation metadata | row `title`/`year` against the manifest entry for the DOI | 26/26 match ✓ |
| Reader's verdicts respected | `git diff 73c0d1c bf5a6a8` on each `reviewed` row | only `tier` and `reviewed_by` changed ✓ |
| Intake fail-open (no network) | `fetch_corpus(session=None)` with `OPENALEX = http://127.0.0.1:9/works` and `socket.socket.connect` patched to raise, as the test fixture does | **No exception.** The guard's `AssertionError` is caught by `_Http.json`. A manifest is written with `server_count: None`, `kept: 0`, `requests {127.0.0.1:9: 3}` (F-8) |
| SO-3 · git hygiene | `git ls-files \| grep -c unreviewed` · `git check-ignore -v` · `git log --diff-filter=A 4e2432b..bf5a6a8` | 0 · `.gitignore:91` · 0 ✓ |
| No operator e-mail | `grep -rIi` for the operator address over the tree · `corpus.py` (no `mailto`, no headers) | none ✓ |
| Noether ack | `cmp` against the LP inbox copy · `git -C LatticeProtocol.aDNA log` | identical · md5 `6b7f7d13…` · committed by LP `a855ae8` ✓ |
| ENVO | crosswalk row · fit matrix §9 · `EcosystemType.meaning` | The scoping is honest: the binding covers the enum only, and `AtlSpatialUnit`'s `bind_when` stays open; `ENVO:00000150`, a *feature*, was considered and declined. **I could not verify the three ids offline** (no ENVO copy on the node, and no network by rule). They agree with my recollection of the ENVO biome terms; that is not a check. |

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | new **C-043** · C-003 · C-006 | **`required` and range claims with no control. The Hard Gate *"claims only what a control proves"* is broken on the new row.** The README row (`README.md:98`) claims every row *"says what vital would realise it (`realisable_as` …)"*, *"a driver with a required lag (≥ 0, a closed unit) and a closed direction"*, *"a year in 1800…2100"* and *"every row carries a realisation block"*. Commit `507924b` adds *"sentence_pointer and realisable_as required non-blank"*. The controls behind these claims are value negatives: blank, unknown enum value, below the minimum. **Only four fixtures omit a key: `_without_driver`, `_without_sentence_pointer`, `_citation_without_doi_or_url` (the DOI and URL inside the citation) and `_reviewed_without_reviewer`.** In my sweep, removing `required` left all three worlds green on 16 slots, `realisable_as` among them (T8's column, `linkml:410`). `realisation` (`:411`) and `driver_lag` (`:413`) are "caught" only because an optional inlined object becomes an unnamed `anyOf` branch, which turns two of the controls red in the two JSON worlds. linkml-validate stays 103/103: a generator side effect, not a control. Removing `year`'s `maximum_value: 2100` (`:424`) stays green: only `201 < 1800` is controlled. The data is safe today, because `check` validates against a committed JSON that still says `required`. **What is missing is the proof that it stays so.** | Add one `neg_hypothesis_without_<slot>` per required slot the README claims: at least `citation`, `realisable_as`, `realisation`, `driver_lag`, `lag_value`, `lag_unit`, `mechanism`, `driver_direction`, `result`, `ecosystem_type`, `evidence_class`, `hypothesis_source`, `citation_source`, `title`, `year`. Add `neg_hypothesis_year_gt_2100`. Alternatively, narrow the README row to what is controlled. Add the required-removal sweep to `instrument_proven`: each removal must redden exactly its control in all three worlds. Also correct `check.py:1` (*"the schema proves a row's SHAPE … 25 controls"*). |
| F-2 | **major** | **C-039** · **C-037** (recurrence) | **"Verified verbatim" is a weaker check than the commit, the register, the skill and the corpus docstring say.** **(a) The cache is trusted, not verified.** `corpus.py:8-10` says the manifest's `sha256` exists *"so the uncommitted text can be verified, never re-typed"*. `cached_text` (`:203-205`) and `check.py:121-128` never compare the two. In plant P1 I appended a fabricated sentence to `wind_001`'s cached abstract and quoted it: **0 failures, 0 warnings**. A fresh clone has no cache, so only `quote_unverified` warnings fire. So the verbatim property holds on exactly one machine, unhashed. **(b) Only double quotes are quotations.** `QUOTE` (`check.py:35`) matches `"…"` and `“…”`. A quotation in `'…'` or `‘…’` is a `locator_only` *warning*. That bypasses `quote_too_long` (up to the 40-word pointer cap) and `quote_not_in_text` (P2, P2b, P3: a 30-word quote and a fabricated quote, exit 0). Ruling 3 (*"rows quote ≤ 25 words"*) has no other machine guard. | (a) In `check`, hash the cached file's bytes (newline stripped, read with `newline=""`; see F-12) and compare with the manifest. On a mismatch, fail `cache_tampered`. Plant it. (b) Treat every quote glyph (`'` `‘’` `«»`) as a quotation, or fail `pointer_unparsed` on any pointer that is neither a recognised quotation nor a locator pattern (`Results ¶n`, `Fig. n`, `Table n`). Plant both. Reword "verified verbatim" in the register and the skill to *"verbatim against this node's cache, hash-checked"* once (a) lands. |
| F-3 | minor | **C-017** (recurrence) | **Verbatim is not faithful, and `reviewed` is not bound to what was reviewed.** `_norm(q) in _norm(text)` is a raw substring test. A quote may begin mid-word (P4), or just after a negation. In P8, on `cloud_002★`, I quoted the fragment that follows the paper's *"does not"* and rewrote the mechanism to match it. **0 failures**, and the row still renders ★ in `LEDGER.md`. Nothing records what the reader confirmed. `tier: reviewed` is an agent-writable word that survives any later edit, and both the index and the memo's ranking read it as the review. (In this mission no reviewed row was edited after the review; I checked.) | Bound the quotation match at word boundaries. Fail when the five tokens before the match hold a negator (`not`, `no`, `never`, `without`) the quotation omits: cheap, and plantable. At promotion, write `reviewed_sha256` (the hash of the row minus `tier`/`reviewed_by`). `check` recomputes it and fails `reviewed_content_changed`. Plant both. |
| F-4 | minor | C-032 · C-039 | **`realisable_as` carries T8 and the ranking, but no reader checked it and no script can count it.** Skill step 6 briefs the reader on mechanism, lag, direction, evidence class and quotation, not on `realisable_as`. The column is free text (`unrealisable on FKNMS's grid:`, `unrealisable as a broadcast index:`, `already FKNMS's EVENT variable…`), so the memo's 10 / 12 / 4 was counted by hand. Defects I found in it: **dhw_001** is counted *realisable*, though skill step 4 lists *"a mechanism that is the event's own definition"* as `unrealisable`. By the skill's rule, T8 reads **9 / 12 / 5**. **cyclone_power_001** copies the hurricane rows' *"indicator of a track within a radius"*, but its driver is *cumulative cyclone power*. **heat_flux_001**: the paper says heat flux drives the reef-vs-offshore *difference*, while the row realises it as a driver of offshore DHW itself. **wind_004** records `lag_value: 2 weeks` for what the abstract gives as a 14-day *window* (its own `realisable_as` says "lag 0–2"). And the memo writes "wind ×4" for five wind rows (`realisation…md:45`; the total of 10 is right). | Add a closed `realisability` slot (`existing_stream \| declared_fetcher \| new_stream \| unrealisable`) with a control, and have `--index` print the counts, so T8 is recounted by code. Extend the step-6 brief to `realisable_as` and the lag encoding (window vs lag). Fix the four rows; they stay `draft`. |
| F-5 | minor | **C-034** · C-032 (recurrence) | **The T8 and T12 readings say more than the falsifier and the claim.** T8's falsifier reads: *"The extraction target yields rows no fetcher can realise"*. Four rows (five by the skill's rule, F-4) are exactly such rows. The register (`thesis_register.md:53`) and the memo (`:49`) call the falsifier *"not met"* by reading an unstated quantifier (only, or most). T12's claim and falsifier concern per-event versus multi-threshold *models*. The note *"That is T12's point … met at the literature stage"* (`:58`) uses the literature's event skew as T12 support, which it is not. Small: the withdrawal parenthetical omits the *"no sentence states the link"* reason, and `updated:` still reads 2026-10-10. | Write the quantifier as a reading for the P3 gate to rule: *"read as 'mostly unrealisable'; 4–5 of 26 rows are unrealisable"*. Re-label the T12 note *context*, not *met*. Fix the two small items. |
| F-6 | minor | C-032 (recurrence) | **Rank 1's "literature strength: highest" counts rows whose event is not FKNMS's.** The memo's own rule is *"rows whose event matches FKNMS's (heat, not bleaching response)"*. Rank 1 still lists **4 reviewed**, including wind_001★ and wind_005★ (bleaching given heat; wind_005's own `realisable_as` says realising it against DHW onset *"would test a different claim"*) and temperature_variability★. It also lists wind_004, a non-thermal, anoxic bleaching event. Event-matched support is **2 reviewed** for wind (003★, a Persian Gulf model of sea-*bottom* temperature; 006★, one Brazilian season) against **1** for rank 2. That one row (002★) is Caribbean and measured on CRW thermal stress itself, the closest event and region on the list. The 4 m/s threshold comes from one Gulf model and would be moved to reef-light anemometers with no transfer caveat. The memo is honest about build cost (rank 1 is the dearest) and about T7 (*"no lever, still"*). | In the strength column, give event-matched reviewed counts only, and the regions. Mark the 4 m/s threshold as a regional transfer to be scanned, not fixed. Put rank 1 against rank 2 to the operator as *"more rows, farther away, costlier"* against *"one row, closest, cheaper"*. |
| F-7 | minor | new **C-044** | **The reader's rules were applied unevenly.** wind_002 was withdrawn because its quote is *"background framing, not the paper's finding"*. **amo_002★** rests on the same kind of sentence. The paper's result is a coral-growth SST reconstruction, and the AMO link (*"vary in concert"*) is context, not a finding. Under skill step 3, that makes it *"a `review`-class claim at most"*, yet it is `reviewed` and `observational`. **enso_002** rests on *"related to … respectively"*. Skill step 3 names *"related to"* among the phrases that give no sign, and the row was kept, corrected. "Respectively" may carry the pairing, but the skill does not say so. | Run the step-3 rules over all 26 rows mechanically (grep the trigger phrases and the abstract's background sentences), or with a second reader. Demote amo_002 (`draft`, `evidence_class: review`) or withdraw it. For enso_002, either amend the skill (*"X/Y … respectively"* gives a paired sign) or withdraw the row. |
| F-8 | minor | **C-041** (recurrence) · C-021 kin | **The intake fails open, even against its own test guard.** `_Http.json` (`corpus.py:78-88`) catches `Exception`, which includes the test fixture's `AssertionError`. So *"a socket opened anywhere fails the test"* (`test_hypotheses.py:2`) is false on the intake path: I reproduced it. `fetch_corpus` then writes the manifest whatever failed (`:189-194`), and the CLI exits 0. With `--refresh`, a network outage would replace the committed 380-work record with an empty one. A partial outage would quietly drop works. | Let `AssertionError` (or any `BaseException` that is not an HTTP or socket error) propagate. Count failed queries, and refuse to write when any failed unless `--allow-partial`, or write the partial manifest beside the old one. Test both, plant first. |
| F-9 | minor | C-037 (recurrence) | **The 25-word cap guards one field. Verbatim text enters through the others.** Ruling 3 is enforced on `sentence_pointer` only. hurricane_001 carries **29** distinct words of its abstract in ≥ 6-word runs (the quotation plus a mechanism that copies the rest of the sentence). Across rows, one work reaches **45** (W2156568771), then 42 and 41. P7 (a whole 177-word abstract pasted into `mechanism`) passes `check` and the index. The schema names this nearest miss (*"mechanism is a reviewer's catch"*), but no reviewer brief asks for it. | When the cache is present, compute per-row and per-work verbatim coverage (the union of ≥ 6-word runs over every free-text field) and fail above 25. Add *"paraphrase; do not copy"* to step 3 and the step-6 brief. Trim hurricane_001's mechanism. |
| F-10 | minor | **C-042** (recurrence) | **Better than M-3a, but the trip was still reported past the line, and one lane has no budget line.** The session log is truthful. The +50% line (≈ 255 kT) was crossed *"during the core build"* and reported at ≈ 310 kT. The operator's stop-or-continue decision came before any paper was read: the point of C-042, met. However: **(a)** the card's criterion says SITREP *"**at** the +50% line"*, and ruling 5's wording (*"at the +50% SITREP, ≈ 310 kT"*) reads as if the line were 310. **(b)** The faithfulness reader (≈ 133 kT, metered) is on no budget line. It is neither main nor the III reviewer's. **(c)** No counter is recorded after ruling 5, so the record cannot yet say whether ≈ 460 kT held. | The AAR records the crossing point (≈ 255 kT, inside `b989318`'s build), the SITREP at ≈ 310 kT, the reader's ≈ 133 kT, and the closing count against 460. Add a reader-lane line to the skill's budget guidance and to future cards. |
| F-11 | nit | C-035-adjacent | **No full-suite count for the closing tree.** The record names 820 at `b989318`, correctly with its commit. `73c0d1c` and `bf5a6a8` later changed `check.py`, `corpus.py` and the tests. I ran it: **822 passed at `bf5a6a8`**. Nothing is red. The closing count is simply not recorded. | Record *"822 passed (281 s) at `bf5a6a8`"* in the AAR and STATE. |
| F-12 | nit | — | **Small gaps.** **(a)** `reviewer_is_extractor` is case- and whitespace-sensitive (P5: `Agent_Proteus` passes). **(b)** `rows()` globs `ledger/*/*.yaml`, so a row saved as `.yml` or nested deeper is invisible to both check and index (P6: an invalid `validated` row, exit 0). **(c)** `cached_text` reads with universal newlines: 2 cached abstracts holding CR characters do not hash to the manifest as text (they do as bytes). F-2(a)'s fix must read bytes. **(d)** The schema README's *"extra keys on the other 8 classes … not controlled"* is now stale: the six new inner classes (`AtlCitation` and the rest) are closed by the generator but uncontrolled. So *"an abstract cannot ride along"* is proven at the row, not at `citation`. **(e)** `neritic_shelf` binds an *epipelagic* (water-column) biome. The description says so, but the value's name invites benthic use. | (a) Compare `casefold().strip()`. (b) Glob `**/*.y*ml` and fail on anything not `<hyp_id>.yaml` one level down. (c) Read bytes. (d) Update the count, and add `neg_citation_extra_key`. (e) Rename it before a second ledger uses it (`neritic_pelagic`), or note the scope in the crosswalk. |

## Acceptance criteria vs evidence

| Criterion | Evidence | Status |
|---|---|---|
| `AtlHypothesis` 0.9.0, a pos/neg control for every claimed constraint, JSON regenerated, ALL WORLDS AGREE | 103 controls, re-run ✓; committed == fresh ✓ | **✗ in part.** ALL WORLDS AGREE ✓, but "every claimed constraint" fails on 16 `required` slots and the year maximum (F-1) |
| ENVO revisited; ids looked up, not assumed | crosswalk `envo` bound, scoped; fit matrix §9 (63 / 3 / 60 ✓) | ✓ as recorded. The ids are unverified by me (offline). Scope honest. F-12(e) |
| Core 0.9.0 `corpus` · `--index` · `--index --check`; offline tests | 34 tests, 14 failure keys each planted ✓; `--check` writes nothing ✓ | ✓, with weaker guards than stated (F-2, F-3, F-8) |
| Skill: paper → row, sentence pointer, tiers | `how/skills/skill_feature_hypothesis_mining.md` | ✓. Step 6 does not cover `realisable_as` (F-4) |
| ≥ 25 rows, one ecosystem; index; `--check` green | 26 rows (15 reviewed) ✓ | ✓ |
| Realisation memo ranks the rows; the operator rules | `realisation_coral_reef_2026-10-12.md` | ✓ as a document. The ruling is pending. Strength column overcounts (F-6); T8 count by the skill's rule is 9/12/5 (F-4) |
| C-033 register re-read; T8 interim note | `916f8b9` · `bf5a6a8` | ✓ re-read. The T8 and T12 readings outrun their wording (F-5) |
| III via `iii/` in a fresh context; SITREP **at** +50% (C-042); suite count with its commit (C-035) | this file; session log | III ✓. SITREP ≈ 55 kT past the line, truthfully recorded (F-10). 820 @ `b989318` ✓; closing 822 not recorded (F-11) |
| Guardrails: no abstract committed · no network in tests · no operator e-mail · peer vaults read-only | `git ls-files`, `.gitignore:91`, no-socket fixture, grep | ✓, except the no-socket fixture can be swallowed (F-8) |

**Not yet reviewable:** the AAR, STATE and CHANGELOG at close, `token_budget_actual`, and the operator's realisation
ruling (memo §5).

## Introspect

- **2a confidence gradient.** The rows are now careful: hedges were restored, and "draft" is kept for corrected rows.
  The confidence rises at the roll-ups. "Verified verbatim" (F-2), "every claimed constraint" (F-1), "not met" (F-5)
  and "highest" (F-6) are each a stronger word than the act behind it. This is the same shape as M-3a's "count-only"
  and "identical".
- **2c structural completeness.** The pipeline has three reading surfaces: mechanism, lag/direction, and
  realisation. Only the first had a second reader. The defects followed the gap (F-4, F-7). The one mechanism-level
  hole the reader closed (hedges) is still invisible to code (F-3).
- **2d meta-pattern.** For the third mission running, a guard is real but narrower than its name:
  - the cache is trusted rather than hashed;
  - double quotes count as "quotes";
  - the pointer counts as "the row";
  - a value negative counts as a presence control.

  The fix is the same each time: bind the check to the object the claim names (the bytes, every quotation, every
  field, the absent key). The schema now shows a second form, catch-by-side-effect. An `anyOf` branch failing
  *unnamed* looked like a control. It is visible in two worlds only, and it would vanish with a generator change.
- **2f denominator.** T8's "4 unrealisable" changes with the reading: 4 under the memo's, 5 under the skill's rule, and
  "rows no fetcher can realise" under the falsifier's literal wording. Rank 1's "4 reviewed" uses all rows as the
  denominator, but the memo's own rule says event-matched rows (2).
- **2g corrections matched.** C-003/C-006 (F-1), C-039 and C-037 (F-2, F-9), C-017 (F-3), C-032 (F-4 to F-6), C-034
  (F-5), C-041 (F-8) and C-042 (F-10) recur. C-021 is kin (F-8).

## ACCUMULATE

**New rows appended to the local store:**
- **C-043** (F-1): `presence_claim_controlled_by_value_negative`.
- **C-044** (F-7): `review_rule_applied_unevenly_across_rows`.

**Existing rows: I did not edit them.** Skill step 3b ties `frequency` and `accepted` to the operator's accept or
reject decision on this table, which has not been given. As at M-3a, these bumps are for the producer to apply once
the operator rules:
- **C-037** 3 → 4 (F-2, F-9)
- **C-039** 2 → 3 (F-2)
- **C-032** 4 → 5 (F-4, F-5, F-6)
- **C-034** 3 → 4 (F-5)
- **C-017** 1 → 2 (F-3)
- **C-041** 1 → 2 (F-8)
- **C-042** 1 → 2 (F-10)
- **C-003** 2 → 3 (F-1)

**Graduation candidates (frequency ≥ 3), if the bumps are accepted:**
- C-039 and C-003 newly qualify.
- C-009, C-010, C-023, C-032, C-034 and C-037 remain candidates.
- Acceptance is the operator's call (ADR-003 ceremony).

## Reviewer cost

About 250 kT on the session counter, against the card's ≈ 150 kT reviewer line. That is past this lane's own +50%, and
I record it here rather than at close: the sabotage sweep and the plants were the cost. Compute:
- 25 schema sabotage runs (each a regenerate plus three worlds);
- 1 control run;
- 34 targeted tests and 1 full suite (822);
- 9 check plants;
- 2 corpus integrity scripts and 2 leakage scripts;
- 1 recount script;
- 1 loopback intake run.

No network.

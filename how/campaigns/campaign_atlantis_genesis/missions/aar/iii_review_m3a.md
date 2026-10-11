---
type: iii_review
review_of: mission_m3a_stream_discovery_skill
commits:
  atlantis: [bb5f223, c39a9b4, 50f50b4, bf9390f, e72e09f, c5be542, ad76921]   # diff vs 395a1ce (6e6ecc1 = read receipt only)
  floridakeyscoral: [416cfe6]
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-10
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 2, minor: 7, nit: 3}
tags: [iii_review, m3a, stream_discovery, traps, rulings, green_cap, condition_cel, so3, atlantis, tidewatch]
---

# III review: M-3a (skill_stream_discovery · core 0.8.0 `discover` · the GREEN-cap ruling · the CEL ack)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` at `v0.6.0`):
- packs: inspect procedures, introspect checks, learning store, vault maintenance;
- the Atlantis local store: 39 corrections, C-001…C-039.

Modalities: text, code and data.

**Reviewer ≠ producer.** I did not write any of this work. The only files I wrote are this review and three new rows
appended to the local learning store. Everything else was read-only:
- targeted tests;
- an offline `discover` run on the exemplar, written to a scratch directory outside both vaults;
- an in-memory plant against `apply_rulings`;
- re-computations from the exemplar's committed public parquets;
- `linkml-validate` on four registries;
- LinkML's corpus lint.

I made no `--probe` request. Neither tree changed apart from the producer's untracked session file, which was already
there. The exemplar data is public FWC/NOAA/USGS data, and this report carries summary counts only.

## Verdict: PASS-WITH-FINDINGS (0 blocker · 2 major · 7 minor · 3 nit)

**What holds:**
- SO-3 held. Nothing was cached. No byte under `data/raw/` is newer than 2026-10-02, and `50f50b4` adds only text files
  under `discovery/`.
- The pointer rows validate against atl_v0, and re-derive byte-for-byte offline.
- The lattice passes.
- The two exemplar data findings the operator accepted are real. I re-measured both.
- The GREEN-cap code does what the README says.
- The CEL ack's claims check out.

**The two majors are about rulings:**
- **F-1.** A ruling accepts a *trap*, not the failure it was given for. One ruling silently absorbs any later, different
  failure of the same trap. I planted one and it passed with exit 0.
- **F-2.** The operator ruled "count-only public metadata requests". The NWIS probe downloads every daily value. The
  numbers in the server-count ruling (backfill dates, qualifiers, "45 revised values") come from a value-level comparison
  that no committed code performs and no artifact records.

**The minors are mostly C-037 and C-039 again, now at discovery.** Three traps check a weaker sibling of what playbook §B
asks:
- ERDDAP checks range coverage, not a count;
- the zero control shows the server is up, not that the question is right;
- samples per year are counted only after `min_train_year` is chosen.

Beyond those:
- `probe_zero` passed on both live runs without ever meeting a zero, so the pass is vacuous.
- An offline re-run overwrites the probed record.
- The GREEN cap's new 600-number bucket is unverified, although the check is local and cheap.
- "Identical" travels without its sighted-search limit.
- The +50% budget line was reported at close, not at the line.

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| Targeted tests | `.venv/bin/python -m pytest -q tests/test_discover.py tests/test_board.py tests/test_runspec.py tests/test_lattice.py` at HEAD `ad76921` | **137 passed** (3.6 s). Full suite not re-run. The author's **782 at `c39a9b4`** is the last code-bearing commit: `50f50b4`…`ad76921` touch no `src/` or `tests/` file (C-035 ✓). |
| Lattice | `python -m atlantis_core.lattice` | strict schema ✅ · peer `lattice_validate` ✅ · local invariants ✅. Stages: `discover → conform_declared → …`. |
| CEL ack claims | `uv run --frozen python ../schemas/check_lattice_corpus.py` in `LinkML.aDNA/what/toolchain` | Neither `condition_cel lint` block lists Atlantis. The remaining rows are Astro · Canvas · Oration · ScienceStanley · WebForge · Archive, as the ack says. `fetch/__main__.py:88-124` holds the receipt and posture gates the new label names. ✓ |
| Offline discover (exemplar) | `discover --instance ../exemplars/gulf_karenia_brevis --compare …/streams.yaml --out <scratch>` | Exit 0. The rows equal the committed `streams.discovered.yaml` below its timestamp line. `longitude_by_unit` accepted (units 2 · 3 · 8), `samples_per_year` ⚠ (1994), `surveillance_declared` ✅. `server_count`, `probe_zero` and `negative_flow` are **na** offline (see F-6). |
| linkml-validate | `linkml-validate -s atl_ontology_v0.linkml.yaml -C AtlDocument` on both `streams.yaml` and both `streams.discovered.yaml` | No issues ×4. ✓ (card criterion 3) |
| Longitude finding, by direction | per unit, points > 1° outside the OISST box, split W/E/N/S (my own pass over the public parquet) | **1,091 of 1,104 gross outliers lie west** (open Gulf), 13 east, 0 N/S. Unassigned = 0. Units 2/3/8 fractions match the memo (0.0246 / 0.0495 / 0.0149). **The ruling's "open-Gulf samples pool into coastal units" is right.** S329's original trap (Atlantic samples in Gulf units) is not what fails now: 13 east-side points in all. |
| 02359170 gap | the cached parquet, site 02359170, against the full 1990–2023 day range | 11,954 cached days; **460 missing days in one run, 2022-06-21 → 2023-09-23**; the server served 12,412 (memo) = +458 net. The dates are confirmed. **The "45 revised values" and the A/R · A/e qualifiers cannot be checked offline** (F-2). |
| Negative flow | cache, all five gauges | 0 negative values. 02292900 (S-79) holds 1,545 exact-zero days. With 0 negative days served, these are closures, not clipped reverse flow. That agrees with the playbook's "said as measured". |
| SO-3 | `ls -la data/raw` · `git status --ignored` · `git show --stat 50f50b4` | No new or modified artifact. The six per-layer FWC parquets are the old gitignored ones (2026-09-23). ✓ |
| GREEN counts (own / echo) | leaf walk of every entry under the new rule | FKNMS v3 **414 / 168** · exemplar v4 **436 / 134** · v3 317 / 108 · FKNMS v2 276 / 151. Matches the README's 414 / 436. Every committed entry passes. |
| Ruling plant (F-1) | in memory: 16,000 unit-4 FWC points moved 4.7° west (49.1% of unit 4), then the committed `candidates.yaml` rulings applied | Before rulings: `fail`, failing units **[2, 3, 4, 8]**. After: **`accepted`, no error**. |
| Version | `__version__` · `pyproject` · `method_version` | 0.8.0 = 0.8.0. The board's `method_version` is templated (`{version}`), and no code path claims 0.7.0. STATE and CHANGELOG are not yet re-cut (due at close). |

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | new **C-040** | **A ruling accepts a trap by name, not the failure it was given for.** `discover/__main__.py:27-41` (`apply_rulings`) keys on `r["trap"]` alone. Any later `fail` of that trap becomes `accepted` and exits 0. **The ruling's text names units 2, 3 and 8.** In the plant, unit 4 at 49% out-of-box was absorbed silently. The same holds for `server_count`: the 02359170 ruling would equally accept an FWC layer count drift, or a new gauge's drift, on the next `--probe`. The skill's "An accepted fail shows as `accepted` … in every memo after" describes the hazard as a feature. The planted-ruling test (`test_cli_fails_on_a_compare_diff_and_a_ruling_accepts_a_fail`) checks only that a ruling applies, never that it stops applying. | Bind each ruling to the evidence it accepted. For example, `rulings.<trap>.accepts:`: `{failing_units: [2,3,8]}` for longitude, or the `what` keys of the failing rows for `server_count`, optionally with the values within a stated tolerance. Apply it only when the current failing set ⊆ the accepted set. Otherwise fail with "ruling stale: new failure(s) X". Add this plant as a test. Back-fill the two committed rulings with their `accepts` sets. |
| F-2 | **major** | **C-023** (recurrence) · C-039 | **"Count-only" is not what the NWIS probe does. The ruling's own numbers have no recorded source.** The operator ruled 2026-10-10: *"count-only public metadata requests"* (plan, session log). `probe.py:121-134` sends the **same request the fetcher sends** (`fetch/nwis.py:21-22`: DV JSON, full `startDT…endDT`) and parses every value. That is ~12,400 values a site, held in memory, for 5 of the exemplar's 12 requests. Every surface still says "count-only": the probe docstring, the CLI docstring and `--probe` help, the skill (front matter, Overview, Parameters), the core README row, the lattice node note, and commit `50f50b4` ("12 count-only requests"). The test named `…_counts_only` checks only that the *memo* holds no `timeSeries`. Further, the `server_count` ruling, the register bullet (ii) and the commit give a backfill date range, qualifiers *A/R · A/e* and **"45 shared days carry revised values"**. A count cannot produce any of these. They need a value-by-value comparison with the cache, which `discover` does not perform, and neither the method nor the extra reads appear in any artifact. The memo's host log covers only the CLI's 12 requests. I confirmed the dates offline (the 460-day cache gap). I could not confirm the 45 or the qualifiers. | Pick one. **(a)** Make the NWIS count really count-only. NWIS's site service with `seriesCatalogOutput=true` returns `count_nu` and the begin/end dates per parameter. Take an explicit operator ruling for the in-memory value read that `negative_flow` needs. **(b)** Or relabel every surface listed: *"summary-only output; NWIS reads the full public daily series in memory; nothing cached"*. Either way, record how "45 revised", the date range and the qualifiers were measured (script and request count) in the memo or the AAR. Otherwise mark them in the ruling and the register as *"read ad hoc, outside discover; not reproducible from the memo"*. |
| F-3 | minor | **C-037** · **C-039** (recurrence) | **`server_count` is a count on ArcGIS only. Two surfaces say it does more.** **(a) ERDDAP and CRW:** `traps.py:66-70` passes when the server's time axis *covers* the fetched range. The server's `n` is printed beside it (exemplar 15,265; FKNMS 15,166) and compared to nothing. A dataset that lost interior steps passes. **(b) NWIS:** it compares counts, not values. The core README states this honestly (*"USGS revisions within a fixed count pass"*). The skill's Known limits says instead *"Server-count drift is a fail by design. A source revised since the fetch means a re-fetch would differ"*, which implies a revision fails. The exemplar's 45 revised values would have **passed** had the backfill not changed the count. | Skill Known limits: add *"a count is not content: revised values within an unchanged count pass; ERDDAP is checked for range coverage, not count"*. In the trap, compare ERDDAP's `n` with the steps expected inside the fetched range (or the summary's rows ÷ units), or rename that arm's evidence `range_covers`. |
| F-4 | minor | **C-037** · **C-009** (recurrence) | **`probe_zero`'s control shows that the server or site exists, not that the question is right. On both live runs its pass is vacuous.** **(a)** The controls are layer metadata, ERDDAP `/version` and the NWIS site service (`probe.py:77-80, 110-113, 138-141`). When they answer, the zero is read as *"a true zero (the control answered)"* (`traps.py:197-201`). A wrong `parameterCd` or date window at a real NWIS site gets that reading. Playbook §B's trap is exactly a wrong question to a live server: *"a zero measures your question first"*. **(b)** No answer was zero or broken on the exemplar (12) or on FKNMS (3). The evidence is `{"zero_or_broken": 0}`, and the status is **pass**, beside the note *"each zero or failed answer re-asked with a control"*. The control path has never run against a live server. | Word the reading as *"the source exists; whether the question is right is not tested"*, or make the control a known-positive version of the *same* question (same layer with no filter, same site and parameter over the full catalog range). Report `na: no zero met` instead of `pass` when no answer was zero or broken. |
| F-5 | minor | **C-037** | **`samples_per_year` counts only the window that has already been chosen.** §B and the card say *"count samples per year **before choosing** `min_train_year`"*. `traps.py:213-224` reindexes `min_train_year…test_end` only. `earliest_min_train_year_with_no_sparse_year` is searched upward from the chosen year, so it can only suggest a *later* start. On the exemplar, FWC has records from **1970** (`first_year_on_record`), and 1970–1993 are never counted. The check answers "is the chosen window sparse", not the question §B asks. | Count from `first_year_on_record`, and report the sparse years on both sides of `min_train_year`. Keep the status on the chosen window (SO-7 unchanged). |
| F-6 | minor | new **C-041** | **An offline re-run overwrites the probed record, and an unused ruling is invisible in the memo.** `runspec.plan` (`runspec.py:165-167`) emits `discover --instance I --compare …` with the default `--out <instance>/discovery`. `__main__.py:105-112` overwrites `discovery_memo.{json,md}` without checking what is there. I reproduced the result in scratch: offline, `server_count`, `probe_zero` and `negative_flow` go **na**, and the operator's `server_count` ruling becomes `ruling_unused`. That status is written to the JSON only: `render_md` (`:65-70`) never prints it. Running the planned pipeline on the exemplar would replace the committed probed memo (probed: True, the 02359170 evidence, `accepted`) with a poorer one. Git keeps the old file, but the working record degrades without notice. | Refuse to overwrite a `probed: true` memo with an unprobed run unless `--force`, or write a timestamped memo beside the old one. Render `ruling_unused` in the md. Test both. |
| F-7 | minor | **C-039** (recurrence) | **The GREEN cap's new bucket is a second, unverified 600-number channel. The check that would make it honest is cheap and local.** `board/__init__.py:476-502`. The ruling says "count echoes once". The code counts them **zero times** against the entry cap and admits up to 600 more numbers, so the ceiling per entry is now 1,200. The README discloses that nothing checks an echo equals a board value. However, `delta()` (`:583-610`) builds `delta_vs` from `(new_ev, old_entry)`, and `emit` already holds `ev`. Checking each `now` against the entry's own value, and each `was` against the prior entry's, is a few lines, and so is checking that the shape has only `was`/`now`/`change` leaves. As shipped, `emit(delta_vs=…)` takes any dict that passes the structural guards. The bound of 600 mirrors the entry's own cap with no rationale; the largest echo count is 168 (FKNMS v3). The README's *"`change` … already on the board"* is loose: a difference is derived, not stored. Scoping (`path == "/evaluation_extras"` only) and the bool index are correct; I found no trap in `_count[_echo]`. | In `emit`, verify the echo: every `now` equals `ev` at that key, and every `was` equals the `--vs` entry's value when one is given. Or rebuild `delta_vs` inside `emit` from the old entry instead of accepting a dict. Shape-check the leaves. Derive the bound from `delta()`'s shape (≈ 3 × comparable fields + folds), or state why it is 600. Then the README's "Not checked" line can go. |
| F-8 | minor | **C-032** (recurrence) | **"Identical" travels without its limit, and one note claims what the sitting measured against.** Both `candidates.yaml` headers say honestly that the agent knew the registry, so `--compare` proves *expression, not a blind find*. That limit does **not** appear on the surfaces a reader sees: the memo md (*"Compare … identical."*), the skill §7 (*"a re-discovery must reproduce"*), commit `50f50b4`, FKNMS `416cfe6` and its STATE (**"identical"**), or the session log. Separately, the exemplar `candidates.yaml` A3 note, written in this sitting, says *"S-79 is tidal-affected: reverse flow reported negative → clip_negative declared"*. The same sitting's probe measured 0 negative days at 02292900, and the playbook was correctly re-worded. The note was not, and it is reproduced in the published memo's Searched table. | Carry a `limits:` line from `candidates.yaml` into the memo md under Compare. Add *"sighted: expression, not discovery"* to the skill §7 and the FKNMS STATE at close. Re-word A3 to match the playbook: *"S329 recorded reverse flow as one code comment; on 2026-10-10 the DV series served none; clip declared, inert"*. |
| F-9 | minor | new **C-042** | **The +50% trip was reported at close, not at the line.** The card's escalation trigger reads *"Budget exceeded by > 50% → SITREP and stop; re-card"*. The session log's last bullet records ≈ 306 kT against a ≈ 210 kT trip, *"SITREP to the operator before the III review"*. That is after all seven commits. The card's `token_budget_estimated` is unchanged, and the two lanes folded in (GREEN cap, CEL ack) are not on the card. The M-1c AAR has the same gap: *"A SITREP at the trip point was still owed and was not given"*. | The AAR records which commit the line was crossed at, the operator's ruling and the re-card. Amend the card's scope to list the folded lanes. Add a session-log line when the counter crosses +50%. |
| F-10 | nit | — | **Three branches carry this mission's headline results and have no test.** `grep` on `tests/test_discover.py` finds none for: `server_count`'s **NWIS** arm (`traps.py:71-76`), which produced the exemplar's only `server_count` fail; the **polygon** arm of `longitude_by_unit` (`_polygon_bounds`); and `ruling_unused`. Disabling the NWIS comparison would turn no test red. | Add one test for each, plant first. |
| F-11 | nit | — | **Small accounting gaps.** **(a)** `Probe.get` (`probe.py:36`) logs a host once, before the retry loop, so a retried request is under-counted. **(b)** `check_searched` flags a `found` id that has no candidate, but not a candidate that no `searched` row found. **(c)** The memo's per-unit `lon_min`/`lon_max` are single-observation coordinates. That is fine for the public exemplar, but a partner instance's memo must never be copied into Atlantis (Hard Gate), and the skill's hand-off does not say so. | (a) Count attempts. (b) Add the reverse check. (c) One line in the skill's hand-off. |
| F-12 | nit | — | **The card's wording and the design differ, rightly, but this is not yet recorded.** The card's Objective says *"ends in a populated `streams.yaml` with provenance"*. The skill never writes `streams.yaml`, and pointer rows carry no provenance (it lives in `candidates.yaml → searched`). That is correct under SO-3. The skill's "Rehearsal of record" points to the AAR, which does not exist yet. | Record both as deviations in the AAR. |

## Acceptance criteria vs evidence

| Criterion | Evidence | Status |
|---|---|---|
| Skill: inputs (geometry pointer, event variable, ecosystem) · steps per §A · outputs = rows + memo | `how/skills/skill_stream_discovery.md`. The CLI enforces the request (`rows.check_request`) and an A1…A6 row per step (`check_searched`). | ✓, outputs are `streams.discovered.yaml`, not `streams.yaml` (F-12) |
| Traps as checks, all six | `discover/traps.py`; 30 tests | ✓ in code, with three weaker siblings (F-3 to F-5) and an unbound ruling (F-1) |
| Run on FKNMS and on the exemplar; both `streams.yaml` validate | 4 × linkml-validate, no issues (I re-ran them). Offline exemplar run reproduced. | ✓. **On FKNMS, 2 of 6 traps are `na`, `probe_zero` is vacuous, and `server_count` is range-only**, so the non-trivial trap paths were exercised on real data on the exemplar alone. |
| Playbook §A/§B re-pointed | `bf9390f` | ✓ (the negative-flow wording is honest; F-8 covers the A3 note it contradicts) |
| C-033 register re-read | `e72e09f` | ✓. Obligations carried. Both data findings re-measured by me (dates ✓; "45 revised" unverifiable, F-2). |
| Exemplar: pointer rows only, no fetch, no new bytes | `git show --stat 50f50b4`; `data/raw` mtimes | ✓ for bytes. "No fetch" is literally true (nothing cached), but 5 requests read full series (F-2). |
| III via `iii/`, fresh context; SITREP at +50% | this file; session log | III ✓. **SITREP not at the line** (F-9). |

**Not yet reviewable:** the AAR; STATE and CHANGELOG at close; the actual token budget on the card; delivery of the
Noether ack (staged, operator-gated, correctly).

## Introspect

- **2a confidence gradient.** The code's own words are careful. The `note` fields say "proxy", "na — why" and "not
  knowable offline". Confidence moves at the boundaries: the word "count-only" (F-2), "a true zero" (F-4), "accepted"
  (F-1) and "identical" (F-8). Each is a label stronger than the act behind it.
- **2c structural completeness.** The pieces that carry this mission's headline results are the least tested: the NWIS
  arm that produced the only `server_count` fail, the polygon arm, and the ruling lifecycle (F-1, F-6, F-10). The
  planted-failure-plus-clean-case discipline was applied per trap, not per arm.
- **2d meta-pattern.** The C-037 and C-039 family is now this graph's most frequent failure. A guard is written, then
  named for the property in the playbook, and the guard checks a neighbour: range for count, liveness for
  question-validity, the chosen window for the choice, the trap name for the failure. The fix pattern is also the same
  each time: bind the check to the exact object the claim names.
- **2f denominator.** `lon_max_out_frac` is per unit, so a large unit can hide many outliers under 1%. Unit 4 holds 147
  gross outliers at 0.46%, which is `warn`. The ruling's percentages are honest, and the absolute counts are in the
  evidence.
- **2g corrections matched.** C-037 (F-3 to F-5), C-039 (F-3, F-7), C-023 (F-2), C-032 (F-8) and C-009 (F-4b) recur.

## ACCUMULATE

**New rows appended to the local store:** C-040 (F-1), C-041 (F-6), C-042 (F-9).

**Frequency bumps for the producer to apply** (I appended only, and did not edit existing rows):
- **C-037** 2 → 3 (F-3a, F-4a, F-5)
- **C-039** 1 → 2 (F-3b, F-7)
- **C-023** 5 → 6 (F-2)
- **C-032** 3 → 4 (F-8)
- **C-009** 8 → 9 (F-4b, the vacuous pass)

**Graduation candidates (frequency ≥ 3):**
- C-037 now qualifies.
- C-009, C-010, C-023, C-032 and C-034 remain candidates.
- Acceptance is the operator's call.

## Reviewer cost

About 120 kT of reviewer context. Compute:
- one targeted test run (137 tests);
- one offline `discover`;
- one in-memory ruling plant;
- two parquet re-computations;
- four `linkml-validate` runs;
- one corpus lint.

No network probe.

---
type: iii_review
review_of: mission_m3b_ii_b_1_core_mask_offsets_scan
commits:
  atlantis: [2e4f8dd, 8a74961]   # diff vs d52e140
  floridakeyscoral: [dda77c2]    # diff vs a8f3069
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-15
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 1, minor: 8, nit: 3}
tags: [iii_review, m3b_ii_b_1, mask_columns, station_offsets, station_windows, scan, selftest, fknms, wind, ruling_4, atlantis, tidewatch]
---

# III review: M-3b-ii-b-1 (core 0.11.0 · `mask_columns` · `station_windows` · era-fitted `station_offsets` · `atlantis_core.scan` · the FKNMS wind declaration)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` read at
`v0.6.0` = `be7dba1`; III HEAD is ahead):
- packs: inspect procedures, introspect checks, learning store (read at the tag);
- the Atlantis local store: 48 corrections, C-001…C-048, all applied as checks.

Modalities: code, data and text. Code and the self-test were the heaviest; the data work re-derived the FKNMS STATE
table from the parquet with my own pandas, not with the core or the producer's script.

**Reviewer ≠ producer.** I did not write any of this work. I wrote two things: this review, and four rows appended to
the local learning store (C-049…C-052). Everything else was read-only:
- every mutation, plant, self-test, scan, `fetch --verify` and conform ran on copies under
  `…/scratchpad/iii_m3b_ii_b_1/` (Atlantis mirrored from the working tree, which equals `8a74961` for tracked files;
  FKNMS copied without its three CRW caches). I deleted the directory afterwards;
- I read the producer's `calm_table.py` but derived the table independently.

I made no network request and committed nothing.

## Verdict: PASS-WITH-FINDINGS (0 blocker · 1 major · 8 minor · 3 nit)

**What holds:**
- **The three keys do what the card says, in the order the card says.** `_prepared` drops rows outside a window, then
  NaNs flagged values (never 0); `fit_offsets` reads only era days on which both report, after both; the offset is
  subtracted before the station → unit mean; a station short of `min_days` is refused by name, never given 0
  (`vitals/ops.py:102-164`). R5 checks the shapes and R7 refuses an era reaching `val_start` or the first rolling test
  year (`registry.py:172-181`).
- **Plant-first holds where I sampled it.** I switched off 15 guards one at a time on mirrored copies of the core. 14
  turn their test red, 13 of them on the assertion they are named for (C-048 checked: mask, windows, era-only fit, offsets
  applied, `min_days`, R7 val, R7 rolling, C6 non-reference perturbation, era clearance, `_span`, the `count_lt`
  centring, the scan's stop-set embargo, the scan's received-rows guard). One is red by a `KeyError`, not the named
  message (the absent-mask-column guard; it fails closed without the guard). One stays green (F-10).
- **Hashes are unchanged where the keys are absent.** Under both 0.10.1 (`d52e140`) and 0.11.0: exemplar
  `7b789afded` ✓; FKNMS at `a8f3069` `81bca06518` ✓; FKNMS at `dda77c2` `2ba2d4f939` ✓.
- **FKNMS under the declaration.** Self-test green on a copy, C6 offsets "n/a, no vital reads this stream" as stated;
  `fetch --verify` ✅ ×4; conform `--stage fetched` 11 pass + item 9 outstanding, as stated.
- **The scan never reads test, on real data too.** On a copy of FKNMS with a wind calm vital added, I poisoned every
  test-week row of **all four** streams (values ±1e6) **and flipped the `qc_low_ratio` flags** there: the scan's JSON
  is byte-equal (30 s). The fitted offsets it reports equal STATE's. It never refits on train ∪ val; `select` is
  `_fit_main`'s own first half. The early-stop optimism is disclosed in the output. (I do not report the val numbers
  here: ii-b-2's scan over the ruled grid is the record.)
- **The STATE calm table re-derives exactly.** From the parquet with my own code (calendar segments): every share, mean,
  reporting-day count, offset and `n_days` (LONF1 −1.338 / 1,913 · MLRF1 −0.735 / 2,065 · SMKF1 −0.122 / 2,064), the
  residuals (val +0.209 / +0.232 / +0.175; LONF1 test +0.479) and the days lost (2 / 1 / 123). ISO-week segments move
  no share by more than 0.1.
- **The SANF1 break is real and the other lights do stay flat against each other.** Yearly paired differences:
  MLRF1−SANF1 ≈ +0.07 (1993–2005) → −0.84 (2008–12); LONF1−MLRF1 ≈ −0.6 and SMKF1−MLRF1 ≈ +0.45 throughout. Limits (b) and
  (d) are visible in the same table (LONF1−SANF1 −1.43 in 2008–12, −0.8…−1.0 in 2021–25; MLRF1−SANF1 −0.36 in 2014–15). Its
  **timing** is a separate matter (F-2).
- **Suite (C-035) and SO-3.** See the table for the count at `8a74961` (code identical to `2e4f8dd`). No data file
  enters Atlantis in this range; gitleaks clean on both ranges.

**The one major is a forward break the mission's own move created.** `selftest.week` was moved to 2014-03-03 to clear
the offset era. In March, the `weekly_count_lt`-centred synthetic world that this mission built has no calm days at the
unit level. With ii-b-2's planned calm vitals declared, the FKNMS self-test fails C0 at **every** c in the ruled grid
(F-1). The criterion "era dependence reported" was met as "n/a", so nothing in ii-b-1 ever ran the new instrument on
the instance it was built for.

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| Suite (C-035) | `.venv/bin/python -m pytest -q -p no:cacheprovider tests` on the mirrored tree at `8a74961`, `PYTHONPATH` → mirror | **896 green** = 887 passed on the mirror (938 s, under load ≈ 50–140) + the 9 that need the tree's own location (6 `test_lattice` and 1 `test_site` skip without sibling vaults; `test_committed_records_pass` fails without the `.git` root), re-run **in place, read-only** (`PYTHONDONTWRITEBYTECODE=1`, no cache): `test_dataset_pairs` + `test_lattice` + `test_site` 80 passed. The producer's 896 @ `2e4f8dd` holds |
| Hashes | `semantic_hash(load_instance(…))` under 0.10.1 and 0.11.0 | `7b789afded` · `81bca06518` · `2ba2d4f939`, identical under both cores (see F-7 for why that is double-edged) |
| Plants | 15 single-guard mutations on mirrored copies, the named tests only | 14 red (13 on their own assertion, 1 by `KeyError`); `scan_drop_and_guard_off` green (F-10) |
| FKNMS as declared | self-test · `fetch --verify` · conform `--stage fetched` on a copy | green, C6 offsets n/a · ✅ ×4 · 11 pass + item 9 ✓ |
| FKNMS as ii-b-2 will make it | copy + `constants: {calm_threshold: c}` + wind `weekly_mean` lags 0·1·2·4 and `weekly_count_lt(value, calm_threshold)` lags 0·1·2 (card obligation 2); self-test | **week 2014-03-03, c = 2·3·4·5·6: ❌ C0** "perturbing week t−lag does not move [calm_t0, calm_t1, calm_t2]". Week 2014-07-07 or 2014-10-06, c = 2·4·6: ✅, and C6 offsets reports real dependence (era week 2009-07-06). semantic_hash `4e1c054007` (F-1, F-8) |
| Scan, real data | that copy, `scan(…, [3, 4])`, then every test-week row of all four streams poisoned and the flags flipped | byte-equal ✓ |
| Calm table | my own pandas from the parquet (`my_calm.py`), calendar and ISO segments | every STATE number ✓ |
| Break timing | monthly MLRF1/SMKF1/LONF1 − SANF1, deseasonalised by the 1993–2004 same-month mean; and the 2009–12 minus 1993–2004 difference by calendar month | May–Sep 2006 at the **pre-break** level; the break develops Oct 2006 → Aug 2007 across a second outage (Apr–May 2007); the steady-state step is only mildly seasonal (F-2) |
| Window sensitivity | SANF1 from 2007-06-01 / 2007-08-01 / 2008-01-01, era from 2007/2008 | offsets −0.06…−0.10 m/s lower; val residual +0.27…+0.34; LONF1 test +0.54…+0.58; ruled calm share at c = 3 3.9 / 4.3 / 5.1 (F-2, F-3) |
| QC flag causality | re-computed `qc_low_ratio` (reproduces the parquet exactly) and a trailing version | centred and trailing differ on 6 station-days, LONF1 2020-02-27…, all in test (F-5) |
| Open keys | copy with `mask_column:` and `station_offset:` (typos) | loads green, hash `6b167519f6`; nothing masked, no offset (F-7) |
| SO-3 · gitleaks | `git diff --name-only` · `gitleaks detect --log-opts` on `d52e140..8a74961` and `a8f3069..dda77c2` | no data in the range ✓ · no leaks ✓ |

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | new **C-051** · C-005 · C-014 (recurrences) | **The self-test week this mission chose blinds C0 to every calm vital ii-b-2 will add.** `count_lt_centre` centres the synthetic daily values on the threshold *as an annual mean*: `v = c + 0.5·a·sin(2π·doy/365.25) + N(0, 0.25·a)` (`selftest.py:257-262`). At the unit level (the mean over four stations) the noise shrinks to 0.125·a while the seasonal term stays 0.5·a. So calm days exist only near the zero-crossings of the sine (January, July, December). `dda77c2` moved `selftest.week` from 2014-01-06 to **2014-03-03** to satisfy the era-clearance rule. In March the sine is ≈ 0.87, and the unit mean sits ≈ 0.43·a above c, so the weeks C0 perturbs hold no calm day to remove. **Evidence:** a copy of FKNMS with obligation 2's vitals fails `❌ C0 … does not move ['fkc_wind_calm_t0', 'fkc_wind_calm_t1', 'fkc_wind_calm_t2']` at c = 2, 3, 4, 5 and 6. The same copy at 2014-07-07 or 2014-10-06 passes at c = 2, 4, 6, and C6 offsets bites there. The core test that "proves" the centring (`test_selftest_green_and_reports_the_offset_era`) runs the variant at a **January** week (`2017-01-02`). The instrument's sensitivity thus depends on the season of a parameter chosen for an unrelated reason. The docstring names FKNMS ("calm 2–6 m/s against values near 1000") as the case the fix is for, and FKNMS was never run with a calm vital. The acceptance line "era dependence reported" passed as "n/a", so the instance never exercised it. **Cost:** ii-b-2's SO-7 step will go red on its first vitals commit. Worse, a hurried fix that moves the week until C0 passes would choose the test week by the instrument's outcome. | (a) Make the world season-proof for `weekly_count_lt` streams: no seasonal term, or a per-week centring at every week C0/C8 perturbs (t − lag for each lag). Then **assert**, before C0, that each perturbed week holds between 1 and 6 calm days at (primary, t − lag), and fail by name ("world fault: week … holds 0 calm days") rather than calling the vital dead. (b) Test it on the FKNMS-shaped `persistent` variant with a calm vital at a March week, at c = 2 and 6. (c) ii-b-2 card: an opening obligation to run the self-test with the vitals *before* the scan, and **not** to move `selftest.week` to make C0 pass (if the week must move, the operator rules it, with the reason). |
| F-2 | minor | new **C-052** kin · C-030 (recurrence) | **Ruling 4's premise is not what the monthly record shows: SANF1 does not step at its May 2006 return.** Deseasonalised against the 1993–2004 same-month mean, all three lights vs SANF1 read **+0.0…+0.5 m/s for May–Sep 2006** (MLRF1 −0.12, +0.53, +0.21, +0.02, +0.17; SMKF1 and LONF1 alike). That is the pre-break level. The break shows partly from Oct 2006 (+0.2…−0.6; Feb 2007 −0.8…−1.2) and is complete only after a **second outage, Apr–May 2007** (Aug 2007 → 2008: −0.5…−1.8). In steady state (2009–12 minus 1993–2004) the step is mildly seasonal: Oct–Mar −0.76…−0.97, Apr–Sep −0.61…−0.80. Limit (a) holds, but more weakly than a winter-only reading of 2006–07 suggests, because that reading set a pre-break summer beside a post-break winter. **Consequences:** the window from 2006-05-01 and the era [2006, 2013] keep 106 pre-break SANF1 days (May–Sep 2006) and the transitional months. Starting SANF1 at 2007-08-01 or 2008-01-01 instead moves the offsets by −0.06…−0.10 m/s (LONF1 −1.437, MLRF1 −0.830, SMKF1 −0.210 at 2007-08). It moves limit (d)'s val residual from **+0.2 to ≈ +0.3** (0.31 / 0.33 / 0.26) and LONF1's test residual from +0.48 to +0.58. The ruled calm share at c = 3 becomes 3.9 / 4.3 / 5.1, so the rise F-3 discusses comes back. The operator ruled on the numbers the session gave; the session log's diagnostic was yearly, which cannot see a break inside 2006. | Not a re-ruling. Surface it to the operator with these numbers: (i) keep ruling 4 and record the window as including 5 pre-break months, with limit (a) re-worded to "a break developing Oct 2006 → mid-2007 across a second outage; in steady state ≈ 0.15–0.3 m/s larger Oct–Mar than Apr–Sep", and limit (d) at "+0.2 (+0.3 with a post-2007 window)"; or (ii) amend the window to the post-break record (e.g. 2007-08-01), which costs ≈ 320 SANF1 train days (2,100 → 1,782). Either way, give the diagnostic in months, not years. |
| F-3 | minor | **C-030** (recurrence) · 2f | **"The unmasked rise in calm share was composition" outruns the table.** Under the ruled index the rise shrinks but does not vanish: c = 3: 4.6 → 5.5 (+20% relative), c = 4: 15.1 → 16.8 (+11%), c = 5: 28.9 → 31.8 (+10%). The ruled index's own mean falls 6.65 → 6.33 m/s. "≈ flat" also depends on the window F-2 questions (3.9 → 5.1 at c = 3). SANF1-only is flat in share (11.2 / 10.6 / 10.8). But its mean falls 6.61 → 6.20, and its train segment is 2006–13, not 1987–2013. STATE itself records that SANF1's level moves at each outage (limit d), the very confounder for a single-light read. The composition effects are real and large (the unmasked rise is 3–5 points); the claim is the full attribution. | Re-word: "the mask, windows and offsets remove most of the unmasked rise (c = 4: +5.6 → +1.7 points); SANF1-only is flat in share but falls 0.4 m/s in mean; neither reading separates climate from SANF1's own level moves." Put the mean change beside the shares. |
| F-4 | minor | new **C-052** | **The preprocessing was ruled after reading the covariate over val and test, and nothing discloses it.** Ruling 1's mask exists because the M-3b-ii-a review found LONF1's failed anemometer **in test**. Ruling 2's SMKF1 cut was ruled on its post-gap shift (val/test years), knowing it removes 123 test days. Ruling 4 was triggered by the **val** residual (−0.3) of the first ruled offsets, and chosen from paired differences over the whole record, 2014–25 included (session log; STATE). No label, score or model output was read, so this is not label leakage, and the choices are defensible on instrument grounds. But they are *covariate-informed, transductive* choices. The test score is then independent of the label, not of the preprocessing. The ii-b-2 limits (a)–(e), STATE and the cards say nothing about it. | Add **limit (f)** to the ii-b-2 card, and to v4's `limitations_ref` and write-up: "Station QC, windows and offsets (rulings 1, 2, 4) were ruled after inspecting the wind record over train, val and test. The inspection was label-blind; no model output or score was read. The test score is not independent of these choices." Record it the same way for any later stream ruled on full-record diagnostics. |
| F-5 | minor | new **C-049** · C-039 (recurrence) | **The mask reads the future, and the self-test cannot see it.** `qc_low_ratio` is a **centred** 15-row rolling median (`fetch/ndbc.py:315`, `center=True`), so a day's flag depends on up to 7 later days. `_prepared` applies it before any op. Because a vital at week t reads the flags of its days, its value depends on t + 1. The self-test sets every flag `False` (`selftest.py:272-273`) and perturbs only `value`. C1 therefore cannot fail on a flag that reads the future, and the mask's code path never runs in the self-test. Meanwhile `ops.py`'s docstring places the mask under "Every operation looks only backward in time" (C-039: the guard is cited for a stronger property than it checks). **Measured impact on FKNMS is tiny.** My re-computation reproduces the parquet's flags exactly. A trailing (causal) version differs on 6 station-days, all LONF1 2020-02-27 onwards (test), and carries sensor state, not wind. | Either compute the flag the mask uses causally (a trailing window; keep the centred one as a description column), or declare the centred mask an exception the self-test **reports**, as it does for C6. Make the self-test's synthetic world perturb every declared `mask_columns` column after t (C1 must fail on a planted flag that reads t + 1). Disclose in ii-b-2: "6 station-days at the LONF1 2020 fault onset are masked with 1–7 days of hindsight." |
| F-6 | minor | C-026 kin · C-039 | **R7's offset bound is one year looser than the climatology treatment it claims to match.** Under `rolling_selection: per_fold`, a fold that tests Y + 1 early-stops on its inner year Y. For that selection, climatology eras are **clipped to Y − 1** (`eval/__init__.py:392`). Offsets are never clipped, and R7 permits `era[1] = min(rolling_origin_years)` (`registry.py:178`). FKNMS has ro from 2013 and era [2006, 2013], so fold 2013→2014's stop set (2013) would read offsets fitted on 2013, its own year. The README says R7 "holds a `station_offsets` era to the climatology bounds". **Latent on FKNMS:** that fold is skipped (`inner stop year 2013 has 0 positives`). | R7: with per-fold selection, refuse `era[1] ≥ min(ro)` (the first fold's inner stop year), or clip and refit offsets per fold as climatology is. Plant the bound with a test at `era[1] = min(ro)`. |
| F-7 | minor | new **C-050** · C-019 kin | **A misspelled stream key loads green, moves the hash, and does nothing.** A copy of FKNMS with `mask_column:` and `station_offset:` loads with no error (hash `6b167519f6`), and neither the mask nor the offsets apply. R5 checks the keys it knows, never keys it does not. The same openness lets core 0.10.1 load the 0.11.0 config with the **same** semantic hash `2ba2d4f939` while ignoring all three keys. The federation pin and the receipt's `core_version` and `selftest_code` guard that skew; nothing guards the typo. | R5: refuse unknown keys in a stream spec (a closed set per shape, listed beside `FLAG_COLUMNS`), by name with a "did you mean". Plant: a misspelled `mask_columns` must be refused. |
| F-8 | minor | C-032 (recurrence) | **"v4 is written under `2ba2d4f939`" is wrong.** `semantic_hash` covers the vitals and the constants (`config.py:109-112`). With obligation 2's vitals and `calm_threshold` declared, the hash is `4e1c054007` on my copy, and each scanned c has its own. The ii-b-2 card ("v4 is written under the receipt hash ii-b-1 recorded") and FKNMS STATE ("item 9 outstanding by construction (v4 is written under `2ba2d4f939`)") say otherwise. | Re-word both: "v4 is written under the hash of the config ii-b-2 declares (vitals + chosen c), with a fresh receipt; `2ba2d4f939` is the declaration-only receipt." |
| F-9 | minor | **C-042** (recurrence) | **The token counter was not read at `2e4f8dd`, so the +50% line could not trip.** The session log says so honestly. But `d52e140` was already at ≈ 145 kT of a 200 kT card. The core, 33 tests, 25 plants and two suite attempts followed before `/clear`, so the 300 kT line was very probably crossed with no SITREP. That cannot now be shown either way. The card's `token_budget_actual` is empty. | At close, record the pre-`/clear` total as unknown and the crossing as "not observed", and let the operator re-card. Fourth recurrence: put a counter read in the commit-message template (the first line ends `· ≈ N kT`). |
| F-10 | nit | C-048 kin · C-009 | **"Test years dropped first" is unobservable, and the poison covers two streams.** With the drop **and** the survived-rows guard both removed (`scan.py:71`, `:74`), `test_scan_never_reads_test_years` stays green: `split` and `select` never touch test anyway, so the drop is belt and braces. Separately, the test poisons the wind and DO values only, not the variant's SST stream or the flag columns. My real-data run covers all four streams and the flags, and passes. | Say "belt and braces" in the docstring. Poison every stream and every `mask_columns` column. |
| F-11 | nit | confidence trap | **"Optimistic, alike for every value" is asserted.** Early stopping on the same val set biases every row the same *way*, not necessarily by the same amount. The amount varies with the trees each value selects. The scan also relies, unasserted, on every value seeing the same stop rows (true today: `finalize`'s drops read the label only). | "Of the same kind; its size can differ by value." Assert that `(unit, week, y)` of the stop set is identical across values. |
| F-12 | nit | — | **Record hygiene.** The session log's closing "Left 2" still lists `station_offsets {SANF1, [1987, 2013]}` and no SANF1 window, after ruling 4. "Plant-first 25/25" names no plants, so it cannot be replayed (I sampled 15). The absent-mask-column guard's plant reddens by `KeyError`, not by its message (harmless: it fails closed). | Strike the stale line. List the 25 plants (name and line) in the AAR. |

## Acceptance criteria vs evidence

| Criterion | Evidence | Status |
|---|---|---|
| Each new guard has a test; each red with its guard off | 15 plants | ✓ for 14. The scan's test-year drop has no reddening test (F-10) |
| Hashes unchanged where the new keys are absent | `7b789afded` · `81bca06518` under both cores | ✓ |
| The scan provably never reads test | synthetic test; my real-data poison of all streams and flags | ✓ (in `eval.split`'s ISO-week sense; the 1–5 Jan edge is limit (c), disclosed) |
| Full suite green, count with its commit; core 0.11.0 | log: 896 @ `2e4f8dd`; mine: see table | ✓ 896 (my count, same code at `8a74961`) |
| FKNMS self-test green, receipt, era dependence reported | `2ba2d4f939` green; C6 offsets "n/a" | ✓ as worded. The dependence was never measured on FKNMS, and with ii-b-2's vitals the self-test fails C0 (F-1) |
| Calm-share table in FKNMS STATE, offsets and n_days | STATE `dda77c2`; my re-derivation | ✓ numbers. The "composition" reading outruns them (F-3); the window's premise (F-2) |
| III fresh context; counter read at every commit; SITREP at +50% | this file; session log | III ✓. Counter ✗ at `2e4f8dd` (F-9) |
| AAR | — | not yet written (not reviewable) |

## Introspect

- **2a confidence gradient.** The code's claims are modest and tested. Confidence rises in the data prose, where
  descriptive patterns are given causes:
  - "steps at its return" (the timing is not what the months show);
  - "the step is seasonal" (mildly; the 2006–07 contrast that suggested it set a pre-break summer beside a post-break winter);
  - "the rise was composition" (most of it was).
- **2c structural completeness.** The mission added three **inputs** to the vitals (flags, windows, offsets), and the
  leakage instrument still perturbs only `value`. Each new input that can carry time is either outside the instrument
  (the flags, F-5) or carried only on the year boundary (R7, F-6). The open key set (F-7) is the same gap one level up:
  what the config *says* is never checked against what the code *read*.
- **2d meta-pattern.** For the second mission running, a synthetic-world fix was validated on the variant and not on
  the instance it was written for (C-005, C-014). This time the instance's parameter was moved in the same mission (F-1).
  The repair should be a property of the world (it must be able to bite at any week) and an assertion that it can, not a
  better week.
- **2e argumentation.** Ruling 4 was argued from yearly means, which cannot place a break inside a year. Monthly,
  deseasonalised differences place it 5 to 15 months later than the ruling says (F-2).
- **2f denominator.** The calm table's denominators are now right (reporting days). What is missing is the segment
  span: SANF1-only "train" is 8 years, the ruled index's is 27 (F-3).
- **2g corrections matched.** These recur:
  - C-005 and C-014 (F-1);
  - C-030 (F-2, F-3);
  - C-032 (F-8);
  - C-039 (F-5, F-6);
  - C-042 (F-9);
  - C-009 and C-048 kin (F-10).

  C-019 and C-026 are kin (F-7, F-6). 7 of 12 findings match known corrections.

## ACCUMULATE

**New rows appended to the local store:**
- **C-049** (F-5): `derived_column_bypasses_perturbation_test`.
- **C-050** (F-7): `open_config_key_set_fails_open`.
- **C-051** (F-1): `instrument_sensitivity_set_by_unrelated_parameter`.
- **C-052** (F-4, F-2): `preprocessing_ruled_on_full_record_undisclosed`.

**Existing rows: I did not edit them**, as at M-3b-ii-a. Step 3b ties `frequency` and `accepted` to the operator's
decision on this table, which has not been given. These bumps are for the producer to apply once the operator rules:
- **C-005** 5 → 6 and **C-014** 2 → 3 (F-1)
- **C-030** 3 → 4 (F-2, F-3)
- **C-032** 5 → 6 (F-8)
- **C-039** 4 → 5 (F-5, F-6)
- **C-042** 3 → 4 (F-9)

**Graduation candidates (frequency ≥ 3), if the bumps are accepted:** C-014 newly qualifies; C-005, C-030, C-032,
C-039 and C-042 remain candidates, with the others already listed at M-3b-ii-a. Acceptance is the operator's call
(ADR-003 ceremony).

## Reviewer cost

About 150 kT on this agent's counter, against the card's ≈ 250 kT reviewer line. Compute:
- 1 full suite on the mirrored tree;
- 15 single-guard plants;
- 12 FKNMS self-tests on copies (1 as declared; 11 with obligation 2's vitals: March at c = 2…6, July and October at c = 2, 4, 6);
- 1 `fetch --verify` and 1 conform on a copy;
- 2 scans on a FKNMS copy (clean and poisoned);
- 5 data scripts (calm table, yearly and monthly break, window sensitivity, flag causality);
- 2 gitleaks runs.

No network.

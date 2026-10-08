---
type: aar
mission: mission_m2a_ii_fknms_fork_and_fetch
campaign: campaign_atlantis_genesis
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261007_154002_m2a_ii_fknms_fork_and_fetch (sitting 1) · session_stanley_20261008_013843_m2a_ii_sitting2_fetch_and_close (sitting 2)
token_budget_estimated: "~120-160kT main + fresh-context III reviewer (card); sitting 2 alone ~60-90kT (STATE prompt)"
token_budget_actual: "sitting 1 ≈300kT (≈ +88%, ruled) · sitting 2 ≈300-350kT across four contexts (three clears; estimated, not metered — rulings 14-18, core 0.5.2 and 0.5.3 were unplanned work) · III reviewer ≈190kT · total ≈600-650kT main (≈ +300% on the card top)"
tags: [aar, m2a_ii, p2, fknms, coral, fork, fetch, crw, erddap, iii, atlantis, tidewatch]
---

# AAR — M-2a-ii: FloridaKeysCoral.aDNA, fork and fetch

**The first MPA instance exists, holds its data, and conforms at the fetched stage.** `~/aDNA/FloridaKeysCoral.aDNA`:
- 21 pre-Blueprint FKNMS zones;
- three CRW streams (DHW, HotSpot, SSTA), daily, 1985 → 2025;
- receipt `0d4d2bb19e`; ADR-001 ratified;
- `conform --stage fetched` conforms (10 pass, 9–10 n/a until a run).

Next is **M-2b** (train, evaluate, explain, page, board entry), then **the P2 gate**.

## Acceptance (card)

| Criterion | |
|---|---|
| Forked by `skill_atlantis_instance_fork`, public posture, licence ruling in the posture ADR, Ratification signed | ✅ sitting 1 (`d7f5e31`) |
| `conform --stage declared` items 1–8 and 11–12; self-test green under the M-1f code | ✅ sitting 1 |
| `fetch` (receipt and posture gates) → provenance → `fetch --verify` → `conform --stage fetched` | ✅ sitting 2 (`07df953`) |
| Router row via a Hestia memo | ✅ delivered sitting 1; landing the row is Hestia's |
| Zero instance-local patches to `atlantis_core` | ✅ every deviation was an Atlantis-side commit (below) |
| III review via `iii/`, fresh context; AAR; queue M-2b | ✅ (this file; §III review; Atlantis `bf073b8`, instance `345ae7f`) |

## The numbers (descriptive only; the split was fixed before any fetch, nothing tuned)

**Streams.** The fetch summaries are the record.

| stream | rows | from → to | sha256 |
|---|---|---|---|
| DHW | 312,711 | 1985-03-25 → 2025-12-31 | `04127678bf29…` |
| HotSpot | 314,475 | 1985-01-01 → 2025-12-31 | `307f7f016b83…` |
| SSTA | 314,475 | 1985-01-01 → 2025-12-31 | `80076fddef8f…` |

- **Fetch:** 2,991 fifteen-day spans over the 21 zones' union envelope, 2 attempts.
- **Reduction:** identical for every stream. 19 of 21 zones contain no cell centre and fall back to one cell (zone 17,
  ~30 km², is larger than a cell; III F-3); zone 20 has 8 cells and zone 21 has 5; 0 cells are shared; no nulls. This is
  the offline prediction exactly.
- **Completeness:** DHW lacks **1999-05-01** for every zone (14,891 of 14,892 calendar days; CRW's own axis skips it;
  HotSpot and SSTA have it). "No nulls" could not see it (III F-2, ruling 17).

**Label (DHW ≥ 4 Cel.wk, H = 8, R = 7).**
- 40,226 modelling rows, 1,592 positive (3.96%).
- Dropped: 3,598 already in an event, 3 with an unknown outcome.

| segment | onsets | positive rate |
|---|---|---|
| train 1986–2013 | 49 | 1.31% (22 of 28 years have no onset) |
| val 2014–18 | 45 | 7.59% |
| test 2019–25 | 105 | 15.01% (2023–25: every zone, every year) |

**Steward ruling 16:** the data is accepted. The train → test base-rate rise and the single-cell zones are limitations of
record. M-2b reports the base rate per segment and checks calibration under the shift.

## Worked

- **Every steward choice went through `AskUserQuestion`, 16 rulings across two sittings, and none was guessed.** That
  includes the ones that cost time: refusing the PacIOOS and PFEG mirrors on licence (13), and re-shaping the request
  rather than waiting (14, 15).
- **The resumable per-span cache made a flaky upstream survivable.** Attempt 1 died on one span at 819 cached. Attempt 2
  resumed and finished; nothing was lost across the gap or the two context clears.
- **Offline prediction ≡ live result** for the reduction: 19/21 fallback, zones 20/21 at 8/5 cells, 0 shared. The geometry
  recipe and the CRW cell test said this before a byte was fetched.
- **The gates held.** The fetch was refused before ratification, and the receipt was not re-earned needlessly (the fetch
  spec is not a training key; the selftest code was untouched by 0.5.2).

## Didn't

- **Budget.** The card's ~120–160 kT top assumed a fetch that was "wall-clock, not tokens". The fetch cost one outage
  checkpoint, three core releases on the fetch path (0.5.1 `95ea8da` start date; 0.5.2 `3c8d11a` spans and union) and
  four contexts in sitting 2, plus 0.5.3 for the III fixes. Sitting 1 SITREPed at +80% and was ruled; sitting 2 overran its
  60–90 kT prompt estimate by roughly 4×. **No mid-sitting SITREP was raised in sitting 2** at the +50% line; each overrun
  went through a steward ruling (14, 15), but the budget itself was never put to the steward.
- **About 2¼ hours of probe-gated waiting fetched nothing** (sitting 2, loop 1, 01:39Z → 03:55Z, 39 attempts), because the request
  could never fit. See the finding below.

## Findings of record

1. **probe-200 ≠ data-200 (new C-028 `readiness_probe_not_the_operation`; III F-9 re-filed it from C-023).** "CRW is down, wait for it" was tested against the index page, never against
   the request the fetcher actually makes. CRW's proxy answers 502 to any request still running at ~10.3 s; a 5-year
   chunk takes ~40 s. The loop was futile by construction, and the outage hid that. Measuring request time against chunk
   size (2 d 0.5 s → 1 yr > 10 s) found it in minutes.
2. **The WI-24 premise was wrong** (sitting 1). CRW's *own* raw SST product carries the OSTIA 1985–2002 terms; DHW,
   HotSpot and SSTA do not. Raw SST was dropped (ruling 9). Licence is per product, not per provider.
3. **Mirrors are not licence-neutral.** PacIOOS `dhw_5km` and PFEG `NOAA_DHW` both carry the OSTIA statement as their
   NC_GLOBAL licence. A source switch is a posture ruling, not an ops choice.
4. **The base rate is not stationary.** It runs 1.3% → 7.6% → 15.0% across the fixed split. It is consistent with
   warming, but it was not separated from the 2002 change in CoralTemp's input (the OSTIA residual ADR-001 discloses) or
   from DHW's fixed MMM climatology (III F-4, C-030). It makes calibration and any headline metric segment-dependent (SO-9). It is carried to M-2b by ruling 16.
5. **Three core defects that only a real instance could hit** (sitting 1): `sensitivity_threshold` had no fork path; C6
   raised KeyError without a climatology (every fixture had one, C-015 class); and ERDDAP's 404 before an axis minimum is
   not "No data".

## III review (fresh context, via `iii/` → `skill_iii_review`, III v0.6.0)

**PASS-WITH-FINDINGS:** 0 blocker, 0 major, 5 minor, 4 nit, **9/9 addressed**. Core 0.5.3, the instance commit and this
AAR carry the fixes. Steward rulings 17 (F-2) and 18 (F-5) chose between the alternatives. The reviewer ran in a fresh
context, read only, and independently confirmed the following:
- 653 tests pass;
- `fetch --verify` passes for all three streams, and the instance conforms at the fetched stage;
- the receipt holds, because the fetch block is outside the semantic hash (demonstrated);
- the 2,991 spans are contiguous, with no gaps or overlaps at the joins and one constant 1,302-cell set;
- `streams.yaml` matches the summaries;
- the pin is honest (`3c8d11a` landed before the first byte);
- SO-3 holds;
- the onset arithmetic holds (199 × 8 = 1,592).

| Finding | Fix |
|---|---|
| **F-1** (C-010, C-023): the CRW span cache was keyed without `base`, and the generic ERDDAP cache had no basis at all. A new base read the old source's spans (0 requests) and stamped them with the new base | The CRW key carries a base and zlev tag; ERDDAP caches under a `b<basis>` subdir (base, variable, zlev, box). Tests cover both envelopes and the generic fetcher (base, box, variable), and a plant without the base reproduces the defect. FKNMS cache directories were renamed to the new keys locally (same base). An offline re-reduction of DHW from them is byte-identical: sha `04127678…`, an equal reduction block, and completeness names 1999-05-01. Instance `345ae7f` |
| **F-2** (C-029): DHW has no 1999-05-01, while "no nulls" read as complete | `provenance.daily_completeness` adds a `completeness` block to ERDDAP and CRW summaries (distinct days against the calendar span, `dates_per_unit`). `fetch --verify` prints ⓘ, which informs and is not a failure. **Ruling 17:** the FKNMS summaries stay as fetched, and the gap is disclosed in `streams.yaml`, the instance STATE and here |
| **F-3**: "smaller than one 5 km cell" | Reworded to "contain no cell centre"; zone 17 (~30 km²) is named as a limitation |
| **F-4** (C-030): the base-rate rise was called "warming itself" | Reworded to "consistent with warming; not separated from" the 2002 input change and the fixed MMM (instance STATE, finding 4) |
| **F-5**: zones 20 and 21 sit at a cell-edge tie, so "union ≡ per-zone" rests on ERDDAP's tie-break | **Ruling 18: test and disclose.** All 16 tie resolutions keep identical cells for three edge-aligned zones, and only `cells_in_envelope` moves (the test asserts it does move). The `snap` docstring names zones 20 and 21. The live parity check's 4/4 zones were not recorded by id; that is a gap of record |
| **F-6**: a year-mode label ignored `start` | A start-moved first chunk names its day (`1985-03-25_1989`); unmoved names are unchanged (tested) |
| **F-7**: "never renames a cached span" | Now "renames no cached span but the last" |
| **F-8**: `snap` claimed ERDDAP clamps an out-of-axis bound | Docstring narrowed: ERDDAP refuses with a 404; this is harmless because zone boxes lie inside the union |
| **F-9**: finding 1 filed as C-023 | Re-filed as C-028 (finding 1 above) |

**Learning store (local):**
- C-010 → 3 and C-023 → 4.
- New: C-028 `readiness_probe_not_the_operation`, C-029 `null_count_blind_to_missing_rows` and C-030
  `descriptive_shift_given_causal_label`.
- **Graduation candidates (frequency ≥ 3):** C-004 · C-005 · C-009 · **C-010** · C-015 · C-023.
- Not incremented: C-009 for F-5, since the self-referential fake is disclosed and backed by a live check.

## Change

- Atlantis core 0.5.0 → 0.5.3 (`0e4154b` · `f23e046` · `95ea8da` · `3c8d11a` · `bf073b8`; 640 → 660 tests over the mission). Every change was
  Atlantis-side and tested; none was an instance patch.
- A fetch spec now chooses its request shape (`chunk_years | chunk_months | chunk_days`, `envelope: union`). This is a
  P1-template capability for every ERDDAP/CRW instance, not FKNMS-only.

## Follow-up

- **M-2b** (opus), amended by ruling 16: the per-segment base rate and calibration under the shift, beside the
  persistence/trend baseline already carded.
- **Operator acts:** the Atlantis push (gitleaks first; unpushed since `4d812f9…`); the WI-20 graduation candidates; the
  Hestia router row (Hestia's).
- **Instance persona** is still `tbd_at_p0` (ruling 8), for the steward when they want one.
- **Conform item 12's gitleaks walks the gitignored span cache.** `--no-git --source <instance>` read ~3 GB of CSVs, ~10 min
  per conform. Backlog candidate: scan the tracked tree (or honour `.gitignore`), and prove a plant in a tracked file still
  reddens.
- **M-2b, zone 17 and the edge-tie zones:** read zone 17 through its single stand-in cell, and record the live parity
  zone ids whenever the reduction is re-run.

---
type: aar
mission: mission_m3a_stream_discovery_skill
campaign: campaign_atlantis_genesis
created: 2026-10-10
updated: 2026-10-10
last_edited_by: agent_proteus
executor_tier: opus
session: session_stanley_20261011_011559_m3a_stream_discovery
tags: [aar, m3a, p3, stream_discovery, traps, green_cap, condition_cel, iii, atlantis, tidewatch]
---

# AAR — M-3a: `skill_stream_discovery`, with the GREEN-cap ruling and the Noether CEL ack folded in

**Scope.**
- The skill: playbook §A as a runnable skill, `how/skills/skill_stream_discovery.md`, with §B's six traps as checks in
  `atlantis_core.discover` (core **0.8.0**).
- Two runs: the exemplar (pointer rows only, SO-3) and FloridaKeysCoral (FKNMS).
- Two lanes folded in because they gated or touched the same files:
  - **the GREEN cap**, which STATE gated "before M-3";
  - **Noether's `condition` notice** (ACADÉMIE M-L2b-iii), which touches the lattice that M-3a's `discover` node also
    edits.

**Rulings** (`AskUserQuestion`, operator, 2026-10-10):

| # | Ruling |
|---|---|
| 1 | GREEN cap (III M-2c-ii F-7): **count `delta_vs` echoes once**, in their own bucket |
| 2 | Noether memo: **option (b)**. The prose moves into the edge's `label`, the edges become unconditional, and the gates are enforced in the nodes |
| 3 | Discovery may make public probe requests that record summary numbers only, cache nothing and put no bytes in Atlantis. *Correction from III F-2:* the question asked for "counts … and in-memory reads", but every surface said "count-only". The NWIS arm reads the daily series in memory, and the surfaces now say so |
| 4 | Exemplar `longitude_by_unit` fail (units 2, 3, 8): **accepted, recorded, carried** to the P3 gate (re-grid by coordinates) |
| 5 | Exemplar `server_count` fail (USGS 02359170): **accepted, pinned bytes stand**; "refresh 02359170" carried |
| 6 | Budget crossed: **proceed** to review and close in this sitting |

## Worked

- **The two runs.**
  - *Compare:* on both instances the discovered rows equal `streams.yaml` on every declarative field. All four stream
    files pass `linkml-validate` with no issues.
  - *Exemplar:* 12 requests, nothing cached, `git status` showing only `discovery/`. FWC's six layer counts equal the
    fetched counts exactly, 5,807 … 87,873 (196,024 in all).
  - *FKNMS:* 3 metadata requests; clean.
- **The traps found things on public data the board has carried for weeks.**
  - **(i) Latitude-band pooling.** The exemplar's rule grid pools open-Gulf samples into coastal units. 1,104 points sit
    more than 1° outside their unit's OISST box, and 1,091 of them lie west, in the open Gulf (the reviewer re-measured
    both). Units 2, 3 and 8 exceed 1% (2.46%, 4.95%, 1.49%).
  - **(ii) A since-backfilled gap.** USGS 02359170, which feeds unit 1, now serves **458 days the pinned cache lacks**,
    2022-06-21 → 2023-09-23, partly inside the 2020–2023 test window, plus **45 revised values**. Since the III fixes,
    discover's own code measures both numbers. The other four gauges match day for day and value for value.
  - **(iii) Trap 5's own premise.** No gauge served a negative daily value, S-79 included. S329's record of the trap is
    one code comment with no count.
  - **(iv) A sparse early year.** 1994, the exemplar's `min_train_year`, has 1,218 samples, below 25% of the median year
    (6,293). The earliest clean `min_train_year` is 1995.
- **Planted failures, then mutation.** Each trap has a planted failure and a clean case. Three guards were disabled and
  4 tests failed; the stale-ruling guard was disabled later and its test failed too.
- **GREEN cap, plant-first.** 2 of the 8 new tests failed before the change. The live own-counts are now FKNMS v3 414
  and exemplar v4 436, against 600. No entry bytes changed.
- **The CEL ack was measured, not asserted.** Noether's own corpus lint lists no Atlantis condition, and
  `atlantis_core.lattice` passes all three checks.

## Didn't

- **Budget (III F-9, C-042).** The card budgeted ≈ 140 kT. The session counter read ≈ 306 kT when it was reported, and
  the reviewer took ≈ 120 kT of context (≈ 229 kT metered). The +50% line (≈ 210 kT) was crossed during the build and
  reported only at the review step (ruling 6). The operator did get the stop-or-continue choice, but after the line,
  not at it, and the card was not re-cut for the two lanes folded in. *Re-card datum:* M-3a as carded plus two lanes,
  ≈ 2.2× the card on main context. That sits on the P2-gate ratio of 2.3×, so the re-card held for the mission and not
  for the lanes added to it.
- **The "reproduce" criterion proves less than it reads.** The agent knew both registries, so `--compare: identical`
  shows the skill can express the rows, not that a blind search would find them. The limit is now in the memo, the skill
  and FKNMS STATE (III F-8). It was first stated only in the `candidates.yaml` headers.
- **The NWIS probe was called "count-only" while it read the full series (III F-2, major).** The first 458/45
  characterisation was an ad-hoc script that no artifact recorded. Fixed: the code now measures and records it.
- **A ruling accepted a trap, not the failures it saw (III F-1, major).** The reviewer's plant, 49% of unit 4 offshore,
  was absorbed by a ruling written for units 2, 3 and 8. Fixed: rulings name `accepts:` keys, and a new failure is
  "ruling stale".
- **FKNMS ran the trivial paths only.** Two traps were `na` and `probe_zero` met no zero, so the non-trivial paths ran
  on real data on the exemplar only (reviewer).

## Finding

The traps' first real catch was not a new instance's data but the exemplar's own. It has been on the board since v0,
and nothing on it carries these two facts:
- its coastal units hold open-Gulf samples;
- one gauge in its test window has a 15-month gap the source has since filled.

The method's discipline (pin the bytes, then measure) is what kept this honest. The pinned bytes are the record, the
drift is now measured against them, and the operator ruled with both facts in view.

The guard pattern seen at M-2c (C-037: a check reads a sibling of what it guards) appeared three more times here, in
`server_count`, `probe_zero` and `samples_per_year`. C-037 is now at frequency 3, a graduation candidate.

## Change

| Where | What |
|---|---|
| core 0.8.0 | `atlantis_core.discover`: `rows` · `probe` · `traps` · CLI. 36 offline tests |
| `board` | `delta_vs` echoes counted once, in their own bucket (ruling 1), with 8 tests |
| `runspec` | `discover` enabled. It plans the offline run and never `--probe` (+1 test, −1 retired case) |
| lattice | `discover` built. Two prose conditions moved into labels (ruling 2) |
| `how/skills/skill_stream_discovery.md` | new |
| exemplar | `discovery/`: candidates with rulings 4–5, pointer rows, memo (no data) |
| FKNMS | `discovery/` + STATE (instance `416cfe6`, `ac3a445`) |
| playbook §A/§B | re-pointed to the skill. Each trap names its check |
| register | M-3a re-read (C-033): no row changes, two exemplar data findings recorded |
| `who/coordination/` | the Noether ack, staged |

**T9 under the M-2c-i counting rule: +0.** Neither change was forced by an instance. The skill is a planned P3
deliverable, and the GREEN cap answers a review finding. Instance patches: 0.

**SO-7:** no vitals or label change, so no self-test re-run.

**Suite:** 782 passed at `c39a9b4`, and 788 at `af66f59` after the III fixes (C-035).

**Card deviations (III F-12):**
- The card's "outputs = `streams.yaml` rows" became `streams.discovered.yaml`. Discovery never writes `streams.yaml`,
  because fork and the steward own that file. This is the SO-3-correct reading.
- The skill's rehearsal pointer named this AAR before it existed.

## C-033: register obligations

| Obligation | Disposition |
|---|---|
| T7 · T8 | carried to M-3b |
| T11 · T2 | carried to the P3 gate |
| T5 | carried as a check: the trap runs it at discovery |
| T9 | +0 |
| Exemplar data findings (i) and (ii) | recorded in the register against every exemplar row's evidence; not re-measured |
| Dropped | none |

## III

**PASS-WITH-FINDINGS, 0 blocker · 2 major · 7 minor · 3 nit** (`iii_review_m3a.md`).

**Dispositions:**
- **Fixed:** F-1 · F-2 · F-3 (stated; ERDDAP step-count comparison not built) · F-4 · F-5 · F-6 · F-8 · F-10 · F-11.
- **Recorded:** F-7 (the echo bound's rationale; verifying echoes in `emit` is a follow-up) · F-9 (above) · F-12
  (above).

**ACCUMULATE (local):** C-009 → 9, C-023 → 6, C-032 → 4, C-037 → 3, C-039 → 2. New: C-040, C-041, C-042, all
`accepted: null`.

## Follow-up

**Before or at the P3 gate (operator):**
- Re-grid the exemplar by coordinates? That is a vitals change and exemplar v5.
- Refresh 02359170? That is a new pin and v5.
- Rule T11 and T2's wording (carried from M-2c-ii).

**Pending operator acts:**
- Deliver the Noether ack.
- The push. Nothing since M-2c-i is pushed; run gitleaks first.
- Accept or reject C-035 to C-042.
- Graduate C-037 and C-032.

**Template work, when needed:**
- Echo verification in `board.emit` (F-7).
- An ERDDAP step-count comparison (F-3).
- Probes for NDBC, OBIS and GBIF when those fetchers are built. FKNMS's next stream, in-situ reef temperature at the
  C-MAN lights, needs the NDBC fetcher.

**Next:** M-3b (opus), the hypothesis ledger, on FKNMS or a new instance, not the exemplar (P2-gate condition (c)).

# atlantis_core

The Atlantis reference implementation (ADR-001 code home, P1). It was extracted from the Gulf *K. brevis* exemplar at M-1b-i
(2026-10-02). An instance **declares** its streams, vitals and event in `atl_v0` registries. `atlantis_core` turns them into a
leakage-tested patient × week vitals table and a direction-aware onset label. **Method demonstration, not an operational
forecast** (SO-4). No data lives here, and nothing is fetched on import or in the tests (SO-3).

```
cd what/atlantis_core && uv sync && .venv/bin/python -m pytest              # 73 tests, offline
.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis   # SO-7
```

## An instance is a directory

| File | What | Checked by |
|---|---|---|
| `streams.yaml` | `AtlObservationStream`s with Rule-5 provenance and `fetcher` | `linkml-validate -C AtlDocument` |
| `features.yaml` | `AtlVital`s: transform · lag · window · group · tag · owner · monotone (replaces `FEATURE_GROUPS`/`FEATURE_DOC`) | idem |
| `events.yaml` | `AtlEventDefinition`: threshold · `direction: above\|below` · horizon · onset rule in words | idem |
| `atlantis.yaml` | engine config: grid, stream shapes and columns, station → unit map, climatology eras, constants, the label's machine half, split, self-test anchor | `atlantis_core.registry` R1–R7 |

## Modules

| Module | Does |
|---|---|
| `config` | `load_instance(dir)`; `semantic_hash(inst)`, an md5 over the training-relevant config and the vitals' and events' machine fields, blind to prose and key order (closes WI-7 once M-1b-ii records it) |
| `registry` | R1 unique ids · R2 refs resolve across files · R3 transforms parse; windowed op ⇔ `window` · R4 lever ⇒ owner · R5 every stream has an engine spec; known fetcher · R6 label event declared · R7 every climatology era ends before `val_start` |
| `grid` | units from coordinate **rules** (`ast` whitelist) · **polygons** (GeoJSON/WDPA file the instance points at; numpy even-odd, holes, MultiPolygon) · **cells**; ISO weeks (Monday) |
| `fetch` | `Fetcher` (offline, retry, atomic, Rule-5 summary + sha256) · **built:** `ArcGISMapServer` · `ERDDAPGriddap` · `NWISDailyValues` · **declared:** `NDBCStdmet` · `OBISOccurrence` · `GBIFOccurrence` · `CoralReefWatch` |
| `vitals.grammar` | the transform language: whitelisted calls, no `eval`. Full table in its docstring |
| `vitals.ops` | the evaluator, with explicit kinds `Obs → Daily → Weekly`. Lags are **calendar** shifts on a complete weekly index |
| `vitals.build` | registries + frames → table (grid rows, one column per vital in registry order) |
| `label` | direction-aware label (`above`: future max ≥ thr · `below`: future min ≤ thr), already-in-event and unknown-outcome drops; `finalize` reports both drop counts |
| `selftest` | the all-stream leakage test (below) |

## The self-test (SO-7)

Each run builds a synthetic patient through the instance's **own** registries. For **every** registered stream it checks:

- **C0:** perturbing week t moves at least one of that stream's vitals. This is the positive control.
- **C1:** perturbing t+1 moves no vital at **any** week ≤ t. The label moves only if the stream is the event stream.
- **C2:** perturbing t+H+1 moves nothing at or before t.
- **C3:** deleting a point stream's observations in t+1..t+H flags the outcome unknown and moves no vital.

It also checks, once per run:

- **C4:** the clean build has no NaN vital at t, so no check above passes vacuously.
- **C5:** an event with `direction: below` behaves the same way.
- **C6:** declared climatology dependence is **reported**. Inside an era, a t+1 perturbation moves `anomaly()` vitals for the
  same calendar week in every earlier era year, because the normal is one statistic over the whole era. Only `anomaly()` may
  move, and R7 keeps every era before validation.

Equality is exact. `tests/test_selftest.py` plants nine defects (peeking rolling window, future diff, late week-end sample,
next-week mean, future count, horizon overreach, deaf label, NaN build, era statistic outside `anomaly()`) and each one is
caught by its named check.

## Equivalence with the exemplar (`tests/test_equivalence.py`)

The test runs on the three committed raw parquets:

- **Identical:** the patient grid, 22 of 25 vitals, the label, both drop flags, and the report (10,804 modelling rows,
  1,168 positives, 1,481 + 1,800 dropped).
- **Not identical:** `sst_anom_t2`, `sst_anom_t4` and `sst_delta_4w` differ on 87–133 train rows from 1994–1998. OISST is
  missing 20 whole weeks, and `hab` shifted the weekly SST table **by row**, so across a gap its "2-week lag" was really 3–4
  weeks. Every differing row has a missing week inside its lag window, and no val or test row differs.
- **Operator ruling (2026-10-02):** atlantis_core lags by calendar. M-1b-ii lands the corrected run as a new board version.
  The in-memory refit gives AUROC 0.894 (unchanged to 3 dp) and AUPRC 0.539 (was 0.547); `metrics.json` stays byte-stable.

## Not here yet (M-1b-ii)

`eval/` · `explain/` · `board/` · `site/`, metrics reproduction, the learner swap, `how/templates/template_mapping_atl.yaml`,
and archiving `src/hab/`. Until then the exemplar's `src/hab/` stays canonical.

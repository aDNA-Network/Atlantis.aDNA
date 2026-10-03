# atlantis_core

The Atlantis reference implementation (ADR-001 code home, P1). It was extracted from the Gulf *K. brevis* exemplar at M-1b-i
(2026-10-02). An instance **declares** its streams, vitals and event in `atl_v0` registries. `atlantis_core` turns them into a
leakage-tested patient × week vitals table and a direction-aware onset label. **Method demonstration, not an operational
forecast** (SO-4). No data lives here, and nothing is fetched on import or in the tests (SO-3).

```
cd what/atlantis_core && uv sync && .venv/bin/python -m pytest              # offline; the port checks skip without data/processed
.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis   # SO-7
.venv/bin/python -m atlantis_core.run --instance ../exemplars/gulf_karenia_brevis        # → outputs/atlantis_core/
.venv/bin/python -m atlantis_core.board --instance ../exemplars/gulf_karenia_brevis --version N --run-date YYYY-MM-DD [--vs <entry>]
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
| `registry` | R1 unique ids · R2 refs resolve across files · R3 transforms parse; windowed op ⇔ `window` · R4 lever ⇒ owner · R5 every stream has an engine spec; known fetcher · R6 label event declared · R7 every climatology era ends before `val_start` and before the first rolling-origin test year, unless `climatology_policy.rolling_origin: refit_per_fold` is declared, which records an **obligation** on eval in `inst.obligations` |
| `grid` | units from coordinate **rules** (`ast` whitelist) · **polygons** (GeoJSON/WDPA file the instance points at; numpy even-odd, holes, MultiPolygon) · **cells**; ISO weeks (Monday) |
| `fetch` | `Fetcher` (offline, retry, atomic, Rule-5 summary + sha256) · **built:** `ArcGISMapServer` · `ERDDAPGriddap` · `NWISDailyValues` · **declared:** `NDBCStdmet` · `OBISOccurrence` · `GBIFOccurrence` · `CoralReefWatch` |
| `vitals.grammar` | the transform language: whitelisted calls, no `eval`. Full table in its docstring |
| `vitals.ops` | the evaluator, with explicit kinds `Obs → Daily → Weekly`. Lags are **calendar** shifts on a complete weekly index |
| `vitals.build` | registries + frames → table (grid rows, one column per vital in registry order) |
| `label` | direction-aware label (`above`: future max ≥ thr · `below`: future min ≤ thr), already-in-event and unknown-outcome drops; `finalize` reports both drop counts |
| `selftest` | the all-stream leakage test (below) |
| `eval` | the temporal split from `atlantis.yaml`; **the learner is a config field** (`learners`: `xgboost` early-stopped on val then refit on train+val · `logistic` median-impute + missingness flags + standardise, every statistic fitted on training rows); `metrics` (alert budgets, calibration, climatology baseline); `lead` (direction-aware lead time on the full grid); ablations from vital groups; surveillance-only; the sensitivity threshold through `label.make`'s event override; `rolling` — rolling origin with **R7 honoured**: each fold's climatology eras end ≤ its train year and the moved vitals are rebuilt. `run` refuses to start with an unexecuted obligation |
| `explain` | interventional TreeExplainer over a train-only background, additivity a hard check, interactions; exact linear SHAP for `logistic`; sums by `group` and `tag` from `features.yaml`. `explain.whatif`: scenarios are config — a raw stream scaled over a period, the vitals re-derived through `vitals.build`, refused without a `lever` vital or across a climatology era; scaling a non-lever station is reported |
| `board` | `project` → the **closed** `AtlEvaluation`, validated against the committed JSON Schema with its format checker; `emit` → a GREEN entry with `evaluation_extras` beside it; refuses unhonoured obligations; `assert_green` rejects per-patient content |
| `run` | the instance end to end → `outputs/atlantis_core/` (metrics · shap_summary · whatif · model · `learner_swap_<kind>.json`) |

## The self-test (SO-7)

The self-test builds a synthetic world through the instance's **own** registries and its real `normalise` path. The world
has two patients: a primary, and a neighbour that shares no station with it. It has deliberate gaps: the primary's event
stream is unobserved at t−4 and t+2, the neighbour's at t−1 and t, and the daily streams miss week t−1 plus scattered days.

For **every** registered stream it checks:

- **C0:** perturbing week t−lag moves **each** vital that reads `value`, one vital at a time. A lag counted in rows instead of
  calendar weeks fails here.
- **C1:** perturbing t+1 moves no vital and no `already_in_event` row filter at **any** week ≤ t. The label moves only if
  the stream is the event stream.
- **C2:** perturbing t+H+1 moves nothing at or before t.
- **C3:** deleting t+1..t+H moves nothing in the past, and the event outcome becomes unknown.
- **C7:** perturbing the primary alone leaves its neighbour unchanged at every week.

It also checks, once per run:

- **C2b:** the horizon from inside. A spike at t+H flips y, and a sample at t+H alone keeps the outcome known.
- **C4:** nothing above passes vacuously.
- **C5:** a `below` event with a `weekly_min` signal, perturbed at a single observation.
- **C6:** the declared climatology dependence is **reported**. Only `anomaly()` vitals may move, and every era year is
  affected because the normal is one statistic over the whole era.

`tests/test_selftest.py` plants **16 defects** and each one is caught by its named check:

- 9 from the first build: future rolling window, future diff, late week-end sample, next-week mean, future count, horizon
  overreach, deaf label, NaN build, an era statistic outside `anomaly()`.
- 6 that the M-1b-i III review showed passing the first self-test: a row filter that reads next week, a back-filled
  last-known state, a horizon counted in observed weeks, a horizon of H−1, a week-major table scramble, weeks *until* the
  next sample.
- 1 for the `hab` defect class: a lag counted in rows.

**Known limits.** The self-test does not prove:

- **Coverage beyond the synthetic world:** it exercises two units, one gap pattern and one t.
- **`future_signal`:** the label is asserted through `y`, `already_in_event` and `outcome_unknown` only.
- **Correctness:** a wrong but causal vital, such as the wrong backward lag, passes. Correctness against a reference is the
  equivalence test's job, and a new instance with no reference has only the self-test.

## Equivalence with the exemplar (`tests/test_equivalence.py`)

The test runs on the three committed raw parquets:

- **Identical:** the patient grid, 22 of 25 vitals, the label, both drop flags, and the report (10,804 modelling rows,
  1,168 positives, 1,481 + 1,800 dropped).
- **Not identical:** `sst_anom_t2`, `sst_anom_t4` and `sst_delta_4w` differ. OISST is missing 20 whole weeks, and `hab`
  shifted the weekly SST table **by row**, so across a gap its "2-week lag" was really 3–4 weeks.
  - In the modelling rows, the differences are 87–133 train rows from 1994–1998, and no val or test row differs.
  - In the full table they also fall in 1993 and in 2023, a test year. The 2023 rows are excluded only because the label
    filters happen to drop every one of them.
  - The test proves this is the only change: on **every** row, atlantis_core's value equals `hab`'s lag-0 series shifted by
    calendar weeks.
- **Operator ruling (2026-10-02):** atlantis_core lags by calendar. M-1b-ii lands the corrected run as a new board version.
  The in-memory refit gives AUROC 0.894 (unchanged to 3 dp) and AUPRC 0.539 (was 0.547); `metrics.json` stays byte-stable.

## Port equivalence (M-1b-ii-a, `tests/test_eval.py` · `test_explain.py` · `test_board.py`)

Fed `hab`'s own `features.parquet`, core eval reproduces **every key** of `outputs/metrics.json` to 1e-12 — `n_trees` 141,
test AUROC 0.8941 / AUPRC 0.5473, the curves, alert budgets, lead time, climatology, surveillance-only, the no-surveillance
ablation, all eight rolling folds and the 50k sensitivity run. That run is in *reference* mode (hab did not refit the 2016
fold), is marked so, and cannot be emitted. SHAP on hab's model reproduces `shap_summary.json` (top 6, partners, top
interaction pair, group order, base). The projector, fed `metrics.json`, reproduces the M-1c fixture's evaluation field for
field. **What-if does not reproduce exactly, and the cause is proven:** the discharge vital is a 30-day mean of log10(1 + q), and
`hab` edited it as if it were log10(1 + mean q). The two readings agree while every day's flow is ≫ 1 cfs (the 2022–23
Lee-Collier window matches to 4 dp) and part at low flow (2017–19: 4e-4; Tampa 2021: 3e-3). Applying `hab`'s edit to the
core's own rows reproduces `whatif.json`. The core re-derives from the scaled raw stream, so its Δp is the transform's
own answer. Tampa's scenario scales gauge 02304500, which is not a lever; `hab` did the same silently, and the core reports it.

## Known limits of eval and explain (SO-9)

Both inherited from `hab` and kept so that the port reproduces it (M-1b-ii-a III F-8). The fix is carded as a follow-up:
it moves every budget number and would give the v0 → v1 delta a second cause.

1. **Alert thresholds are quantiles of the test scores.** Each budget alerts on the top r of the test year's own scores,
   chosen after the fact. A steward would have to fix the threshold beforehand, from validation, and the realised
   alert rate would drift. Lead time inherits the same threshold.
2. **The rolling folds testing 2017–2019 reuse a tree count early-stopped on 2017–2019** (the full model's `n_trees`). This
   is mild selection on the years they score.

**Two limits on reading an explanation:**
3. **Collinear vitals split attribution.** Read `group_net_mean_abs_shap` (|Σ φ| within a group) beside the abs-sums. Under
   the logistic swap, season and SST carry large offsetting attributions.
4. **Absence is not a value.** Missingness flags are `availability:<vital>` pseudo-vitals tagged artifact, and never the
   vital's tag. Where a stream is structurally absent (units 8 and 9 have no gauge), the flag encodes unit identity. Even
   xgboost gives ungauged units 7–19% of each discharge vital's attribution.

## Site (M-1b-ii-b, `site/`)

`python -m atlantis_core.site --instance <dir>` builds the explainer page. An instance opts in with two files:
- `site.yaml` says what to draw: the board entry the page must agree with, group colours, vital display rules, strips, the
  trace, case rules and the map.
- `site_copy.yaml` holds every word. Sections are HTML fragments with `{{path|fmt}}` value tokens and `{{fig:NAME}}`
  figure tokens.

`template.html` carries structure, style and generic renderers only, and `tests/test_site.py` holds it free of exemplar
literals. The build refuses an unknown figure, an unresolved value, a missing copy key, orphaned words, and outputs that
disagree with the cited board entry. Site data is assembled from `outputs/atlantis_core/`, `data/processed/atlantis_core/`
and the registries, never from `hab`. The page embeds per-patient rows, so it is an instance artifact under the instance's
data ruling; nothing it assembles goes on the board.

## Mapping (M-1b-ii-b, `mapping.py`)

`python -m atlantis_core.mapping --check <mapping.yaml>` is contract item 11's machine check. It holds an instance's
mapping (from `how/templates/template_mapping_atl.yaml`) to the atl_v0 schema: five labels, edges typed by slot ranges,
fence and stamps. `tests/test_mapping_template.py` feeds it 17 defects.

`src/hab/` is archived in place (`exemplars/gulf_karenia_brevis/src/hab/ARCHIVED.md`). It still runs only to regenerate
`hab`'s tables for the port-equivalence tests, the v0 page, and, until the core has a fetch CLI, the raw parquets.

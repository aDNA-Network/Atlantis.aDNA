# atlantis_core

The Atlantis reference implementation (ADR-001 code home, P1). It was extracted from the Gulf *K. brevis* exemplar at M-1b-i
(2026-10-02). An instance **declares** its streams, vitals and event in `atl_v0` registries. `atlantis_core` turns them into a
leakage-tested patient × week vitals table and a direction-aware onset label. **Method demonstration, not an operational
forecast** (SO-4). No data lives here, and nothing is fetched on import or in the tests (SO-3).

```
cd what/atlantis_core && uv sync && .venv/bin/python -m pytest              # offline; the port checks skip without data/processed
.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis   # SO-7 · writes the fetch gate's receipt
.venv/bin/python -m atlantis_core.fetch --instance ../exemplars/gulf_karenia_brevis --verify   # pins re-hashed, no network
.venv/bin/python -m atlantis_core.run --instance ../exemplars/gulf_karenia_brevis [--out outputs/atlantis_core_v3]   # → <out>/ (default outputs/atlantis_core)
.venv/bin/python -m atlantis_core.board --instance ../exemplars/gulf_karenia_brevis --version N --run-date YYYY-MM-DD [--outputs <out>] [--vs <entry>]
```

## A new instance (M-1d-i)

```
.venv/bin/python -m atlantis_core.fork    --answers <answers.yaml> --out <dir>   # templates → declarations (no data)
.venv/bin/python -m atlantis_core.conform --instance <dir> [--items 1-8,11,12] [--stage declared|fetched]
```

- **`fork`** renders `how/templates/template_instance/` from a steward's interview answers. The shape is
  `answers.example.yaml`, and the interview is `how/skills/skill_atlantis_instance_fork.md`. It writes `atlantis.yaml` ·
  `units.yaml` · `streams.yaml` (declared, atl_v0 0.3.0) · starter `features.yaml` · `events.yaml` · `mapping.yaml` · a
  posture ADR stub · the federation pin, then runs R1–R8. It is deterministic. Every refusal lists all its reasons and
  writes nothing.
- **`conform`** is contract v0.2.0 §B as a machine check. It prints one ✅/✗ per item with the files read. Items 9–10 are
  n/a before a run. Item 6 re-runs the self-test. Item 12 is gitleaks: absent means not run, which fails the item. It
  writes nothing. `tests/test_conform.py` feeds each item the defects its contract row names. The exemplar is a reference
  run inside Atlantis, not a forked instance: it has no `units.yaml`, `mapping.yaml` or posture ADR, and conform says so.

## The pipeline, the run-spec, the board, the records (M-1d-ii)

```
.venv/bin/python -m atlantis_core.lattice                                    # the pipeline lattice: strict schema · peer validator · local invariants
.venv/bin/python -m atlantis_core.runspec --instance <dir> --spec <json> --plan   # validate a run-spec; print the commands; run NOTHING
.venv/bin/python -m atlantis_core.board --index [--check] [--entries <repo>/what/board/entries]   # BOARD.md, byte-stable
.venv/bin/python -m atlantis_core.board --instance <dir> --version N --run-date D --entries <dir>/what/board/entries   # an instance's own board
.venv/bin/python -m atlantis_core.datasets --check <dir>                     # dataset_*.dataset.yaml pairs vs the lattice-labs schema + their bytes
```

- **`lattice`.** `how/lattices/lattice_atlantis_pipeline.lattice.yaml` is the method as one pipeline:
  - `discover` is declared-only until M-3a;
  - then `conform` (declared) → `selftest` → `fetch` (two gates) → `conform` (fetched) → `run` (grid · vitals · label ·
    train · eval · explain) → `board` → `site`.

  It is checked three ways:
  - by the strict `lattice_yaml_schema.json`, a byte-identical copy of `aDNA.aDNA`'s;
  - by the peer `validate_lattice_file`, imported by path because it has no CLI. It is not run when `aDNA.aDNA` is absent,
    and its warnings count as failures;
  - by local invariants neither checks:
    - edges name real nodes, and ids are unique;
    - the graph is acyclic and connected;
    - each gate **dominates** its target (no path reaches `fetch` without `selftest`);
    - modules import;
    - every `-m` has a `__main__` guard, and every `--flag` is one its argparse declares (both checked by AST);
    - the `invoked_by` nodes are exactly the run-spec's run block.

  `stages()` is the run-spec's vocabulary.
- **`runspec`** is a closed vocabulary: `stages` · `fetch_mode` · `streams` · `learner_swaps` · `board{version,run_date}`.
  - No field carries a path, a prompt or data; the instance directory comes from the command line.
  - It rejects rather than coerces: unknown keys at either level, duplicate JSON keys, `"2"` for 2, `1` for `true`, and
    out-of-order stages.
  - `discover` is not enabled.
  - It returns exit 3 on REJECT.
  - It **executes nothing**; execution is P5's Ray run-spec, with operator GO.
  - Example: `how/templates/template_runspec.example.json`.
- **`board --index`.** It renders `BOARD.md` beside the entries dir, sorted, with no timestamps.
  - Every entry is checked before anything renders, or the render refuses.
  - The one open-shape entry (v0) is grandfathered **by id and by pinned sha256**.
  - The top level is closed. A rendered value carrying a line break or control character refuses the render, and `|` is
    escaped.
  - Supersession is derived, never written: the highest version of a stem supersedes the lower ones.
  - `--check` writes nothing.
  - `--entries` must end in `what/board/entries`, and the instance's outputs must sit inside that repo. An instance
    therefore cannot write Atlantis's board, and its entry travels by memo.
- **`datasets --check`.** It validates every pair against the lattice-labs `dataset_yaml_schema.json` (Atlantis keeps a
  byte-identical copy beside `how/templates/template_dataset_pair/`). It also checks:
  - name = stem;
  - the checksum is `sha256:` and equals the bytes when they are present;
  - the Rule-5 provenance is in `class_fields`;
  - the `.md` twin agrees.

## An instance is a directory

| File | What | Checked by |
|---|---|---|
| `streams.yaml` | `AtlObservationStream`s with Rule-5 provenance and `fetcher` | `linkml-validate -C AtlDocument` |
| `features.yaml` | `AtlVital`s: transform · lag · window · group · tag · owner · monotone (replaces `FEATURE_GROUPS`/`FEATURE_DOC`) | idem |
| `events.yaml` | `AtlEventDefinition`: threshold · `direction: above\|below` · horizon · onset rule in words | idem |
| `units.yaml` | `AtlSpatialUnit`s: the region row, then every grid unit `PART_OF` it (`atl_unit_<slug>_<code>`); geometry by pointer | idem · `conform` item 1 |
| `mapping.yaml` | the registries projected to the five `atl_` labels (from `how/templates/template_mapping_atl.yaml`) | `atlantis_core.mapping --check` |
| `atlantis.yaml` | engine config: grid, stream shapes and columns, station → unit map, climatology eras, constants, the label's machine half, split, self-test anchor, `surveillance` (declared absent + reason, when there is no channel) | `atlantis_core.registry` R1–R8 |

## Modules

| Module | Does |
|---|---|
| `config` | `load_instance(dir)`; `semantic_hash(inst)`, an md5 over the training-relevant config and the vitals' and events' machine fields, blind to prose and key order (closes WI-7 once M-1b-ii records it) |
| `registry` | R1 unique ids · R2 refs resolve across files · R3 transforms parse; windowed op ⇔ `window` · R4 lever ⇒ owner · R5 every stream has an engine spec; known fetcher · R6 label event declared · R7 every climatology era ends before `val_start` and before the first rolling-origin test year, unless `climatology_policy.rolling_origin: refit_per_fold` is declared, which records an **obligation** on eval in `inst.obligations` · R8 (M-1d-i, contract item 5) the surveillance channel is declared (a `surveillance_channel` stream read by a `group: surveillance` vital, with its ablation in `eval.ablations`) or declared absent with a reason, and then nothing claims it |
| `grid` | units from coordinate **rules** (`ast` whitelist) · **polygons** (GeoJSON/WDPA file the instance points at, **pinned by `grid.sha256`** — M-2a-i; numpy even-odd, holes, MultiPolygon) · **cells**; ISO weeks (Monday) |
| `fetch` | `Fetcher` (offline, retry, atomic, Rule-5 summary + sha256) · **built:** `ArcGISMapServer` · `ERDDAPGriddap` · `NWISDailyValues` · `CoralReefWatch` (M-2a-i: zone means over CRW's own ERDDAP, cell-centre-in-polygon per feature, a nearest-cell fallback, a per-zone `reduction` block computed by the download; zones from the instance's pinned grid via `bind`; M-2a-ii, 0.5.2: `envelope: union`, one request per chunk over every zone, same reduction; 0.5.3: the span cache is keyed on the base too, and the summary's `completeness` block counts calendar days) · ERDDAP chunks `chunk_years` | `chunk_months` | `chunk_days` (CRW's proxy cuts a request at ~10 s) · **declared:** `NDBCStdmet` · `OBISOccurrence` · `GBIFOccurrence`. **CLI (M-1d-i):** `python -m atlantis_core.fetch --instance <dir> [--stream ID] [--offline] [--verify]` — refuses to fetch without a green self-test receipt for the current `semantic_hash` and self-test code (contract item 6), and refuses a NETWORK fetch unless the instance's own posture ruling carries a signed Ratification row (item 7; `--offline` exempt). Built fetchers declare `spec_required`; `--verify` re-hashes each cache against its summary and `streams.yaml`, and says (ⓘ, not a failure) which calendar days a daily artifact lacks; prints the Rule-5 values to record, never rewrites a registry |
| `vitals.grammar` | the transform language: whitelisted calls, no `eval`. Full table in its docstring |
| `vitals.ops` | the evaluator, with explicit kinds `Obs → Daily → Weekly`. Lags are **calendar** shifts on a complete weekly index |
| `vitals.build` | registries + frames → table (grid rows, one column per vital in registry order) |
| `label` | direction-aware label (`above`: future max ≥ thr · `below`: future min ≤ thr), already-in-event and unknown-outcome drops; the onset refractory `refractory_weeks` (M-2a-i; absent = 0, the same expression) widens the already-in-event drop to t−R…t; `finalize` reports both drop counts |
| `selftest` | the all-stream leakage test (below); a green CLI run writes `outputs/atlantis_core/selftest_receipt.json` (semantic hash · streams · counts), the fetch gate — local and gitignored, re-earned by anyone because it needs no data; bound to the self-test's own code (a receipt from a weaker self-test is stale) |
| `eval` | the temporal split from `atlantis.yaml`; **the learner is a config field** (`learners`: `xgboost` early-stopped on val then refit on train+val · `logistic` median-impute + missingness flags + standardise, every statistic fitted on training rows); `metrics` (alert budgets, calibration, climatology baseline); `lead` (direction-aware lead time on the full grid); ablations from vital groups; surveillance-only; the sensitivity threshold through `label.make`'s event override; `rolling` — rolling origin with **R7 honoured**: each fold's climatology eras end ≤ its train year and the moved vitals are rebuilt. `run` refuses to start with an unexecuted obligation. **F-8 (M-1e):** `eval.threshold_from: val` (default) fixes each budget's threshold on the selection model's out-of-sample val scores before test is scored and reports `realised_rate` beside `nominal_rate`; `eval.rolling_selection: per_fold` (default) early-stops each fold on its inner val year Y with eras clipped ≤ Y−1. Both are checked on what the learner actually received (a `FitRecorder` proxy; III M-1e F-1), and the eras against `clipped_eras(Y−1)`; the lead time records the threshold it read, and `_variant` refuses a result whose thresholds are not the ones fixed on validation (F-2). A stop year with < 5 positives skips its fold, and says so (`rolling_skipped`). `test` / `full_model` exist only so the port reproduces `hab`. **Embargo (M-1f):** `split.embargo_weeks` (absent → the event horizon H; `none` → off, v2's reading, port only) drops from each fit / stop set the rows whose label window t+1…t+H reads the period that set must not see — selection-train → stop set, stop set → test, refit → test, main split and every fold; the train tail returns for the refit. `check_label_windows` checks every boundary on the frames the learner received, reading the event's H, never the setting. The result carries `embargo` (rows and positives dropped, latest window end, and the measured spill, `horizon_spill`) |
| `explain` | interventional TreeExplainer over a train-only background, additivity a hard check, interactions; exact linear SHAP for `logistic`; sums by `group` and `tag` from `features.yaml`. `explain.whatif`: scenarios are config — a raw stream scaled over a period, the vitals re-derived through `vitals.build`, refused without a `lever` vital or across a climatology era; scaling a non-lever station is reported |
| `board` | `project` → the **closed** `AtlEvaluation`, validated against the committed JSON Schema with its format checker; `emit` → a GREEN entry with `evaluation_extras` beside it; refuses unhonoured obligations, and (M-1e) any budget, lead time or swap whose threshold was not fixed on validation, a missing realised rate, or rolling folds not selected per fold (`assert_thresholds_fixed`); (M-1f) a result whose embargo is missing, off, shorter than the horizon, or unchecked at any boundary of the headline, a swap or a fold (`assert_embargo`) — `embargo_weeks` and the split text are written from the checked result; `assert_green` rejects per-patient content |
| `lattice` · `runspec` · `datasets` | M-1d-ii, above |
| `run` | the instance end to end → `--out` (default `outputs/atlantis_core/`; metrics · shap_summary · whatif · model · `learner_swap_<kind>.json`), processed tables → `data/processed/<basename of --out>/` |

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
- **C9 (M-2a-i, an event with `refractory_weeks` R > 0):** a crossing at the primary's week t−R sets `already_in_event` at
  t, one at t−R−1 does not, and neither moves y. **The boundary is never skipped** (III F-3): any unobserved week a t−R−1
  crossing could be carried through is filled first, and the result and the receipt say so. That the refractory reads
  nothing after t is already C1's and C2's job.

`tests/test_selftest.py` plants **16 defects** and each one is caught by its named check:

- 9 from the first build: future rolling window, future diff, late week-end sample, next-week mean, future count, horizon
  overreach, deaf label, NaN build, an era statistic outside `anomaly()`.
- 6 that the M-1b-i III review showed passing the first self-test: a row filter that reads next week, a back-filled
  last-known state, a horizon counted in observed weeks, a horizon of H−1, a week-major table scramble, weeks *until* the
  next sample.
- 1 for the `hab` defect class: a lag counted in rows.

**Any event stream (M-1d-i).** The event stream may be a point stream, a unit-daily stream or a station-keyed daily stream:
- its synthetic values sit on the safe side of a **positive** threshold (≤ 0 is refused);
- a spike is one observation per entity past the threshold (for daily streams, one date across every selected entity, so
  a mean over stations crosses too);
- C3 runs on the event stream whatever its shape;
- C5 re-declares the event in the **mirror** direction, so both tails are exercised on every instance;
- the primary's unobserved past week (`gap_week`) is the shape's default (point 4, daily 1; the exemplar's world,
  unchanged) unless a vital of that stream lags exactly there. A lag-1 weekly mean of a daily stream was NaN at t, and
  C4 called it vacuous. That was the first fork's finding.

**After the M-1d-i III review (F-1, F-2):**
- the **event stream carries the label-exposing gaps whatever its shape**: the primary is unobserved at t+2 (t+1 when
  H = 2) and the neighbour at t−1 and t;
- every daily stream's neighbour is unobserved at t−1 and t;
- spikes insert an observation into an unobserved day;
- **C8 calendar-lag invariance** (deleting the primary's weeks (t−L, t] must not move a lag-L vital) guards the lags no gap
  crosses. The run says when C8 alone guards a stream;
- label comparisons are NA-safe, so a horizon defect that blanks y is a named C4, not a TypeError.

`tests/test_fork.py` runs the whole planted-defect catalogue (12 defects) against two forked worlds: the example, and a
variant with no point stream, a two-station mean and no surveillance. Each defect is caught by a named check. The
exemplar suite gains a back-filled weekly mean, a pre-existing blind spot.

**A persistent event (M-2a-i, for FKNMS DHW).** The onset refractory (`events.yaml → refractory_weeks`, atl_v0 0.5.0)
drops a week whose carried signal crossed anywhere in t−R…t. **R = H − 1** makes the label's onset the one `eval/lead.py` counts, and R = H is one week stricter (III F-4; the paired test is in `tests/test_label_refractory.py`).
- **The accumulating world.** `selftest.event_series` is `iid` or `accumulating`. The accumulating series is a DHW-like
  trailing 12-week sum of a daily "hotspot". It carries one past episode, at least 30 weeks before t, that crosses, dips
  for three weeks and re-crosses: the flicker a refractory exists for. The default is `accumulating` for an `above` event
  with R > 0 on a daily stream; the world used is recorded in the result and the receipt.
- **C9's episode check** compares `already_in_event` against "the **carried** signal crossed in w−R…w", recomputed from the
  **raw synthetic frame** rather than from the label. The episode carries a gap of `last_known_weeks` + 1 weeks right after
  a crossing, so a refractory on the raw signal, or one counted in observed rows, disagrees with it (III F-7). The signal
  must be `weekly_{max,min,mean,median}(value)`; anything else is refused, not skipped (III F-3). The default world applies
  to `unit_daily` event streams only (III F-6).
- **A third forked world, `persistent_master`:** polygon MPA zones, a `unit_daily` above event, H = 8, R = 7 (= H − 1), gridded-only,
  surveillance absent. The **whole** catalogue re-runs across all three worlds (C-014). One defect reaches this world by a
  different road: it has no `weekly_min` vital, so a leaky `weekly_min` reaches only C5's mirror label, and C5 names it
  (`WORLD_EXPECT`).
- **Eight refractory plants, plus the iid-boundary case, each caught by name:**
  - ignored, R−1 and R+1 → C9;
  - a window that reads t+1, and the drop applied after the horizon cut → C1;
  - a refractory on the weekly *mean*, which is right at t−R and t−R−1 → only C9's episode check;
  - (III F-7) a refractory on the raw signal, and one counted in observed rows → only C9's episode check;
  - (III F-3) R = 4 in the iid world with an R + 1 refractory, which used to pass when the probe was skipped → C9.

**Known limits.** The self-test does not prove:

- **Coverage beyond the synthetic world:** it exercises two units, one gap pattern and one t.
- **`future_signal`:** the label is asserted through `y`, `already_in_event` and `outcome_unknown` only.
- **Correctness:** a wrong but causal vital, such as the wrong backward lag, passes. Correctness against a reference is the
  equivalence test's job, and a new instance with no reference has only the self-test.
- **Real products' semantics (M-2a-i):** the accumulating world is DHW-*like*. CRW's own climatology baseline (the
  MMM inside HotSpot and DHW) and any reprocessing of near-real-time values are outside the synthetic world, so neither
  R7 nor C6 can see them. That is a known limit, carded for M-2b's review.
- **Fetch-time mixing:** a cell shared by two zones, or a wrong polygon mask, happens inside the fetcher, before the
  self-test's frames exist. `CoralReefWatch`'s own tests guard that.

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

Items 1–2 were inherited from `hab` (M-1b-ii-a III F-8), disclosed on board v1, and **fixed at M-1e** (board v2,
`what/board/entries/2026-10-03_gulf_karenia_brevis_v2.json`). Item 2b was found at M-1e's review and **fixed at M-1f** (board v3,
`what/board/entries/2026-10-07_gulf_karenia_brevis_v3.json`; the figures below are v3's). The `test` / `full_model` modes keep them reproducible for the port
only; the board refuses them. What remains is named under each.

1. ~~**Alert thresholds are quantiles of the test scores.**~~ **Fixed:** each threshold is a quantile of the train-only selection
   model's validation scores, set before test is scored; lead time reads the same threshold. **Residual — drift.** The rate a fixed
   threshold actually flags moves with the event rate and the model. In the exemplar every realised test rate is below
   nominal (0.0409 / 0.0799 / 0.1921 at 5 / 10 / 20%; v2 0.0378 / 0.0811 / 0.1933). The likely reasons are validation prevalence 0.101 (0.104 on the embargoed stop set) against test's 0.077,
   and thresholds read from the selection model while test is scored by the train+val refit. **Neither is proven.** Compare
   budgets at matched realised rates, never at a shared nominal label.
2. ~~**The rolling folds reuse the full model's tree count.**~~ **Fixed:** each fold early-stops on its own inner validation
   year (eras clipped ≤ Y−1), so no fold is tuned on its test year's rows. **Residual — noise.** One year is a small stopping set,
   and the exemplar's fold counts range from 52 to 835 trees (v2: 63 to 623). The panel now measures the method as a steward would run it,
   selection included, and is not comparable fold for fold with v1's.
2b. ~~**The label horizon crosses every boundary.**~~ **Fixed (M-1f):** every fit and stop set drops the rows whose label window
   t+1…t+H reads the period after it (`split.embargo_weeks`, default H), and each boundary is checked on the frames the learner
   received against the event's H, not against row years (C-018, C-022). "The period after" is in **week-years**: a week
   belongs to the year of its Monday, as the grid bins it, so a year's last week can hold the first days of January. The
   check is exact in that convention, and a raw-stream perturbation through `label.make` proves it
   (`tests/test_embargo_perturbation.py`). In calendar dates, 1 kept training label and 5 kept validation labels still read
   1–5 January, in the week a test row's label never reads (III M-1f F-4). **Measured before the cut** (exemplar, H = 4):
   - main split: 25 of 7,971 training region-weeks (3 of 920 positives) read 2017; 34 of 1,193 validation region-weeks (1 of
     121 positives) read 2020;
   - fold stop years: up to 10 of 31 positives (2022, read by 2023), as the M-1e review counted.

   The headline moved little (141 → 146 trees; AUROC 0.8938 → 0.8950, AUPRC 0.5388 → 0.5414). `none` reproduces v2 in every number.

   **Residuals:**
   - **A seasonal hole at each boundary.** The last H weeks before each boundary (December, for H = 4 and year boundaries)
     are absent from the selection fit and the stop set. The validation tail is also absent from the final refit, and each
     fold's last year's tail from its refit. The final refit and each fold refit keep the train tail. How much this costs
     depends on where the ecosystem's season falls.
   - **The check covers labels only.** That vitals read only the past is the self-test's proof (SO-7), not this check's.
   - **Thresholds still read every validation week's scores.** This is deliberate (a budget is per year, and a score reads no
     label). The embargoed rows still carry `split = train`/`val` in `all_scored`, so the SHAP background may sample a
     training-tail row, which is features only.

**Two limits on reading an explanation:**
3. **Collinear vitals split attribution.** Read `group_net_mean_abs_shap` (|Σ φ| within a group) beside the abs-sums. Under
   the logistic swap, season and SST carry large offsetting attributions.
4. **Absence is not a value.** Missingness flags are `availability:<vital>` pseudo-vitals tagged artifact, and never the
   vital's tag. Where a stream is structurally absent (units 8 and 9 have no gauge), the flag encodes unit identity. Even
   xgboost gives ungauged units 7–19% of each discharge vital's attribution.

## Site (M-1b-ii-b, `site/`)

`python -m atlantis_core.site --instance <dir> [--site site_v2.yaml]` builds the explainer page. An instance opts in with two files
(one site file per page version, M-1e; `outputs:` in it names the run the page reads, default `outputs/atlantis_core`):
- `site.yaml` says what to draw: the board entry the page must agree with, group colours, vital display rules, strips, the
  trace, case rules and the map.
- `site_copy.yaml` holds every word. Sections are HTML fragments with `{{path|fmt}}` value tokens and `{{fig:NAME}}`
  figure tokens.

`template.html` carries structure, style and generic renderers only, and `tests/test_site.py` holds it free of exemplar
literals. The build refuses an unknown figure, an unresolved value, a missing copy key, orphaned words, and outputs that
disagree with the cited board entry. Site data is assembled from `outputs/atlantis_core/`, `data/processed/atlantis_core/`
and the registries, never from `hab`. The page embeds per-patient rows, so it is an instance artifact under the instance's
data ruling; nothing it assembles goes on the board.

**What the build checks.** It re-projects the run through the board's projector and compares every evaluated field with
the cited entry; `metrics.json` that disagrees in any field is refused. It ties the gitignored `shap.npz` to the run by row
counts, base and per-column mean |SHAP|. The copy grammar is enforced the same way at build and render: no negative index,
known formats only, one placement per figure, and no tokens in fields the page inserts verbatim.

**Known limits of the template (M-1b-ii-b III F-10, disclosed).**
- Method vocabulary is English and stays in the template: split/metric table headers, case titles ("True positive,
  early", "False alarm", "Quiet week"), "(held out)", "model starts", the what-if caption frame. Instance words are all copy.
- The label diagram draws up to four look-back weeks.
- The beeswarm and waterfalls show at most 14 and 9 vitals.

## Mapping (M-1b-ii-b, `mapping.py`)

`python -m atlantis_core.mapping --check <mapping.yaml>` is contract item 11's machine check. It holds an instance's
mapping (from `how/templates/template_mapping_atl.yaml`) to the atl_v0 schema: five labels, edges typed by slot ranges,
fence and stamps. `tests/test_mapping_template.py` feeds it 17 defects.

`src/hab/` is archived in place (`exemplars/gulf_karenia_brevis/src/hab/ARCHIVED.md`). It still runs only to regenerate
`hab`'s tables for the port-equivalence tests, the v0 page, and, until the core has a fetch CLI, the raw parquets.

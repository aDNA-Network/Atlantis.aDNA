# CHANGELOG — Atlantis.aDNA

## 2026-10-08 — v0.13.0 · P2 gate MET: conditional GO P3 · thesis statuses ruled · M-2c carded · P3 re-carded

- **The P2 exit gate was ruled by the operator** (`AskUserQuestion`) after an opus decision brief and a fresh-context III
  review of the *gate case* (`artifacts/p2_gate_iii_review.md`: PASS-WITH-FINDINGS, 0 blocker · 6 major · 4 minor · 2 nit).
  **Conditional GO P3.** The gate ran on opus, not fable, by the operator's ruling. This is recorded as a deviation (the
  second, after P1), and the charter is not amended.
- **T9: the exit bar is met as worded; drop-in is not demonstrated.**
  - The weak form (no instance patch) cannot fail under the M-2 card's own escalation rule.
  - Counted under one rule, the M-2a-i set included, FKNMS forced ≈ 13–15 Atlantis changes. That is P4's baseline.
- **Register, ruled:**
  - T11 is untested at its terms on both instances. Climatology has never been measured at a budget (C-034).
  - T4 is untested on FKNMS, and its causal clause is withdrawn.
  - T2's P2 swap was never run (C-033).
  - T5's absence case and T12's DHW ≥ 8 run are recorded.
  - T3's restated falsifier gets a number at its next test.
- **Conditions:**
  - (a) **M-2c** (card filed): climatology at budget · a season-block paired interval · exemplar board v4 at 0.7.0 · FKNMS
    v3 by memo with its learner swap · the `BOARD.md` lead column.
  - (b) M-3a and M-3b re-carded at ≈ 2.3× the card top, with the reviewer counted.
  - (c) M-3b targets FKNMS or a new instance, not the exemplar (SO-3).
  - (d) Before P4 opens, define what "no template change" means there.
- **Board README:** an instance entry's refs resolve in the instance. FloridaKeysCoral is local-only, so the v1 and v2 refs
  are not yet public (G-6).
- **III, ACCUMULATE (local):** C-009 → 7, C-030 → 2, C-032 → 2. New: C-033 `recard_drops_register_obligation` and C-034
  `status_supported_off_falsifier_operating_point`.
- **Memos (outbound):** the graduation memo is redrafted for C-004 · C-005 · C-009 · C-010 · C-023, with C-015 below the bar
  because its `accepted` field was never set. It supersedes the undelivered 10-03 memo. A second memo tells Hestia that
  Atlantis's router row is stale (persona, phase; Rule 7).
- **Push guards:** 694 tests; ALL WORLDS AGREE; `board --index --check` ✅; gitleaks exit 0.

## 2026-10-08 — v0.12.0 · M-2b ✅: FloridaKeysCoral.aDNA trained, paged and on the board · core 0.6.1 · atl_v0 0.7.0 · III 8/8 → P2 gate requested

- **The second instance — the first MPA — is on the board.** `2026-10-08_florida_keys_coral_v2` (GREEN, closed, `method_demonstration`),
  landed by memo after Atlantis re-checked it; v1 is superseded on provenance alone (III F-6). The page lives in the instance.
  Test 2019–25 at a 15.0% base rate: model 0.937 / 0.690 against climatology 0.919 / 0.601, trend 0.781 / 0.520 and
  persistence 0.751 / 0.358. **The calendar knows most of a summer heat event.**
- **Core 0.6.0:** the event signal's own comparators — *persistence* (s(t) as the label carries it, no fit) and *trend*
  (logistic on s(t) and its last step, fitted on climatology's rows); the base rate per segment and calibration in the large
  (ruling 16: 1.31 / 7.59 / 15.01%; −0.045 → −0.097; validation-fixed thresholds flag 1.4–2× their budget on test);
  `assert_comparators`; `rolling_origin_years` optional. **atl_v0 0.7.0:** eight optional slots, 65 controls. Exemplar re-run
  into `outputs/atlantis_core_v4` ≡ v3 on every number; v3 is refused for the comparators by name.
- **Three defects only a real core-built page reached (`671808b`):** a `//` comment in a one-line IIFE killed the page while
  every test passed (now `node --check` with the defect planted back); polygon zone names; conform item 10 could not pass any
  `atlantis_core.site` page.
- **Core 0.6.1, the III fixes (694 tests):** the trend's step-input plant (F-1); item 10 needs the section renderer and a
  script that parses (F-2, ruling 25); `assert_comparators` documented as a tamper check, with slot ↔ result equality (F-5);
  the board refuses config bytes edited after the run (F-6, rulings 24 and 26); the "Positives" column and val's stop-set
  denominator (F-7). Register: T3's lift and restated falsifier (F-3); the roll-up matches the rows (F-4).
- **Theses re-cut:** T1 two-instance; T3 and T10 tested on FKNMS (T3's falsifier measured in scratch: the persistence comparator
  closes from 52% to 88% of the model's AUPRC under a persistence-inclusive label); **T9 weak form supported, strong form not
  met** (zero instance patches; nine P1 template changes).
- **III** PASS-WITH-FINDINGS, 8/8. Local store: C-007 → 2, C-009 → 6, C-011 → 2, C-023 → 5; new C-031
  `metric_compared_across_base_rates`, C-032 `register_summary_outruns_rows`. Steward rulings 19–26.
- **Card completed.** AAR filed. Roster, charter and STATE updated; **the P2 gate is requested** (fable, operator-summoned).
  Budget ≈ +140% on the card, estimated; the SITREP was raised at the +50% line (ruling 23).

## 2026-10-08 — v0.11.2 · M-2a-ii ✅: FloridaKeysCoral.aDNA fetched and conforming · core 0.5.3 · III 9/9

- **The first MPA instance holds its data.** It has three CRW streams (DHW, HotSpot, SSTA), daily over 1985 → 2025 for 21
  zones. `fetch --verify` ✅ ×3, and it conforms at the fetched stage. Steward ruling 16 accepted the data and the onset
  table (train 1.31% → val 7.59% → test 15.01%). The split is unchanged. No data entered Atlantis (SO-3).
- **Core 0.5.2** (`3c8d11a`): CRW's proxy cuts any request at ~10.3 s, and a 5-year chunk took ~40 s. Fetch specs now
  take `chunk_months` or `chunk_days`, and CRW takes `envelope: union`; union ≡ per-zone is tested, with a plant.
- **Core 0.5.3, the III fixes (660 tests):**
  - **F-1:** the CRW span cache is keyed on the base, and the generic ERDDAP cache on its whole basis. Before, a new base
    read the old source's spans. A plant reproduces the defect.
  - **F-2:** `provenance.daily_completeness` adds a summary `completeness` block, and `fetch --verify` prints ⓘ for
    missing calendar days. FKNMS DHW lacks 1999-05-01, which is disclosed by ruling 17.
  - **F-5:** an edge-tie test, covering all 16 resolutions; ruling 18.
  - **F-6:** a start-moved year label names its day.
  - **F-7/F-8:** docstrings.
- **III** PASS-WITH-FINDINGS, 9/9. Local store: C-010 → 3, C-023 → 4; new C-028 `readiness_probe_not_the_operation`,
  C-029 `null_count_blind_to_missing_rows` and C-030 `descriptive_shift_given_causal_label`.
- **Card completed.** AAR filed. Roster, charter and STATE updated, and **M-2b queued**. The budget ran ≈ +300% on the
  card, estimated rather than metered.

## 2026-10-08 — v0.11.1 · M-2a-ii sitting 1: FloridaKeysCoral.aDNA forked and ratified; fetch checkpointed

- **The first instance exists:** `~/aDNA/FloridaKeysCoral.aDNA` (a peer vault). It conforms at the declared stage, its
  self-test receipt is green, and its posture ADR was ratified by the steward. No data yet: CRW's ERDDAP was down
  (502 on every request), so the fetch is checkpointed to sitting 2 by steward ruling.
- **Three Atlantis-side fixes the fork surfaced** (atlantis_core **0.5.1**, 642 tests). Each fix's test fails without it:
  - `fork` renders `answers.eval.sensitivity_threshold`, a closed vocabulary, which the card's Alert Level 2 needed;
  - the self-test's C6 crashed (`KeyError: 'in_era_week'`) on any instance with no climatology. Every fixture had one. C6
    is now said to be n/a, on the console and on the receipt;
  - ERDDAP refuses a start before a dataset's first day (CRW DHW: 1985-03-25). The new optional spec `start` handles it.
- **WI-24 corrected:** CRW's own SST product carries the OSTIA 1985–2002 terms, not only the PacIOOS mirror. Raw SST was
  dropped (steward ruling).
- **Router row** proposed to Hestia by drop-box memo. No data committed to Atlantis.

## 2026-10-07 — v0.11.0 · M-1f: the label-horizon embargo → board v3 · WI-23 closed

- **Measured first.** The M-1e review's fold table reproduces exactly as crossing positives (up to 10 of 31, stop year
  2022). The main split, measured for the first time:
  - train→val: 25 of 7,971 region-weeks, 3 of 920 positives;
  - val→test: 34 of 1,193 region-weeks, 1 of 121 positives.
- **atlantis_core 0.5.0 — `split.embargo_weeks`** (absent → the event horizon; `none` → off, port only):
  - **The cut.** Every fit and stop set drops the rows whose label window t+1…t+H reads the period it must not see. That
    is six boundaries: the main split and every fold. The refits keep the train tail (operator ruling). Climatology, the
    ablations and the sensitivity run follow.
  - **The check.** `check_label_windows` reads the event's H on the frames the learner received. A raw-stream
    perturbation through `label.make` proves no kept label moves.
  - **Provenance** of what was dropped and the measured spill, on every result and fold. `semantic_hash` reads the
    resolved embargo: the exemplar is `7b789afded`, and `none` re-derives `acfa22c6e4`.
- **Board v3** (`what/board/entries/2026-10-07_gulf_karenia_brevis_v3.json`), emitted by code. Its single cause is proven
  by running: `none` reproduces v2's `metrics.json` in every number. The numbers:
  - 146 trees (was 141);
  - AUROC 0.8950 / AUPRC 0.5414 (was 0.8938 / 0.5388), base rate 0.0774;
  - lead time 13 of 22 onsets (was 14).

  A leak removed, not a gain. The board refuses any result whose embargo is missing, off, short, unchecked or
  misattributed, in any published run. No v3 page (operator ruling); `limitations_ref` → the core README.
- **atl_v0 0.6.0:** `AtlEvaluation.embargo_weeks`. 56 controls, ALL WORLDS AGREE. **The runner was blind in one world:** a
  pattern starting with `-` or a bad regex left linkml-validate's reason test vacuous since 0.5.0. It now reads grep's
  exit status whole.
- **III:** PASS-WITH-FINDINGS, 0 major, 7/7 addressed. Local store: C-009 → 5, C-023 → 3, C-018 and C-021 → 2; new C-026
  and C-027. C-023 joins the graduation candidates.
- **Not touched:** the v0–v2 entries and pages, and v2's outputs (sha256-pinned). No data committed.

## 2026-10-06 — v0.10.0 · M-2a-i: the core for a persistent, polygon, gridded instance · P2 condition (c) MET

- **The split (operator ruling, 2026-10-06).** M-2a became M-2a-i (this mission), then M-1f (the horizon embargo), then
  M-2a-ii (the FKNMS fork and fetch). Patients are FKNMS zones, reduced by a polygon reducer; H = 8, one window.
  **Condition (c) MET:** CRW is reachable through `ERDDAPGriddap`'s query shape on `coastwatch.noaa.gov`.
- **Instance contract v0.3.0 (minor):** item 2 admits `NOAACRW:`, since DHW has no CF standard name. Crosswalk row
  `noaa_crw_products` is bound.
- **atl_v0 0.5.0:** `AtlEventDefinition.refractory_weeks` plus the `NOAACRW` prefix. 53 controls, ALL WORLDS AGREE, and
  the sabotage bites.
- **atlantis_core 0.4.0:**
  - **The zone file is pinned by its bytes** (`grid.sha256`). This was claimed since M-1b-i and never implemented.
    Duplicate zone ids are refused.
  - **Label onset refractory:** R absent ≡ 0, the same expression, hashed only when set, so the exemplar keeps `acfa22c6e4`.
    **R = H − 1 matches `eval/lead.py`'s onset**, and a paired test proves it.
  - **Self-test:**
    - the accumulating DHW-like world: a past episode with a flicker, plus a gap longer than the carry;
    - **C9:** the refractory bites at its declared length, and the boundary is never skipped;
    - the episode check is recomputed from the raw frame;
    - a third forked world, `persistent_master`, with the whole catalogue × 3;
    - 8 refractory plants plus the iid-boundary case;
    - the receipt records its world and C9's outcome, and its code hash covers `grid/`.
  - **`CoralReefWatch` built:**
    - zone means over CRW's own ERDDAP, using a cell-centre-in-polygon mask per feature with a nearest-cell fallback;
    - the zones come from the instance's pinned grid (`bind`);
    - the summary records the reduction and its basis, and a cached artifact on another basis is refused by `fetch`,
      `--verify` and conform item 3.
- **The fork skill:** the router row goes to Hestia by memo; the interview asks about persistence; the receipt names its world.
- **III:** PASS-WITH-FINDINGS, 8/8 addressed (operator ruled "fix all 8" at the +50% SITREP). Local store: C-023, C-010 and
  C-015 +1, C-005 +2, new C-024 and C-025. Graduation candidates: C-004 · C-005 · C-009 · C-015.
- **Not touched:** the exemplar's bytes, board v2 and every page. No data committed. The live CRW smoke was scratch only.

## 2026-10-03 — v0.9.0 · M-1e: thresholds fixed beforehand (F-8) → board v2 · P2 condition (a) MET

- **Board v2** (`what/board/entries/2026-10-03_gulf_karenia_brevis_v2.json`), emitted by code with the delta attributed to F-8
  alone. The model is v1's, byte for byte (`model.json`, SHAP and what-if identical; AUROC 0.8938 / AUPRC 0.5388; 141 trees;
  semantic hash `acfa22c6e4`). What changed:
  - every alert threshold is **fixed on the selection model's validation scores before test is scored**;
  - the **realised** test rate is stated beside each nominal budget: 0.0378 / 0.0811 / 0.1933 at 5 / 10 / 20%;
  - lead time is read at the fixed threshold: 0.636 of 22 onsets flagged ahead, median 4 weeks;
  - each rolling fold early-stops on its own inner year, with eras clipped ≤ Y−1.

  v1 and v2 are points on one curve of one model. They are not compared at a nominal label.
- **`atlantis_core` 0.3.0:**
  - `eval.threshold_from: val | test` and `eval.rolling_selection: per_fold | full_model` (`test` / `full_model` are for the
    port only, which still reproduces hab to 1e-12);
  - a `FitRecorder` checks what each fold was actually fitted on;
  - lead time records its threshold;
  - the board refuses F-8 for the headline and every swap, by identity and arithmetic;
  - `run --out` gets its own processed dir;
  - the site reads a named run (`site.yaml outputs:`, `--site`);
  - the template draws a realised-rate column only for validation-fixed thresholds;
  - `BOARD.md` budgets show the threshold source and realised rate.
- **atl_v0 0.4.0:** `ThresholdSource` · `AtlAlertBudget.threshold_from` + `realised_rate` · rule validation ⇒ realised (typed
  `all_of`). Controls 45 → 50, ALL WORLDS AGREE; the instrument is shown to fail with the rule removed or untyped. The
  mapping template pin is 0.4.0.
- **The v2 page** `site/gulf_karenia_brevis_v2.html` is a new file (ADR-002 §4 A-1). The v0/v1 pages and entries are
  byte-stable (sha256-pinned).
- **III review** (fresh context): PASS-WITH-FINDINGS, **8/8 addressed**. Two guards were true by construction (C-009 →
  frequency 4), and a provenance label was stamped from intent (C-023, new). Source-level plants P1–P4 into eval now prove
  the guards.
- **Disclosed, not fixed (operator ruling):** the label horizon crosses every split boundary (C-022). The embargo is carded
  as board v3: `how/backlog/idea_label_horizon_embargo.md`.
- Tests 480 → 516 · SO-7 green (vitals and labels untouched) · WI-11 and WI-14 closed, WI-23 opened · **M-2a queued** (P2
  opens).

## 2026-10-03 — v0.8.1 · P1 gate MET — conditional GO for P2

- **Operator rulings** (`AskUserQuestion`, after an opus decision brief):
  - **conditional GO for P2**;
  - **ADR-002 A-1 ratified** (the exemplar's explainer pages join §4's capped exception);
  - **contribution guide ratified** (0.1.1: the operator is the merge authority until P4);
  - **C-004/C-009 graduation** proposed to III.aDNA by memo.
- **P2 conditions → cards:**
  - **M-1e** (F-8: thresholds and fold tree counts fixed on validation → board v2) runs first;
  - M-2 is re-carded as **M-2a** (CRW-via-ERDDAP check · fork · persistent-event self-test · fetch) and **M-2b** (model
    · instance page · board by memo → P2 gate). NDBC is dropped. The original M-2 card is kept as superseded.

## 2026-10-03 — v0.8.0 · M-1d-ii pipeline lattice · runspec · BOARD · dataset pairs · contribution guide (P1 lanes closed)

- **`how/lattices/lattice_atlantis_pipeline.lattice.yaml`** is the method as one pipeline:
  - discover (declared-only until M-3a) → conform(declared) → selftest → fetch (two gates) → conform(fetched) → run
    (grid · vitals · label · train · eval · explain) → board → site.
  - **`python -m atlantis_core.lattice`** checks it three ways: the strict schema, the peer `validate_lattice_file`
    (imported by path), and local invariants. The local checks cover edge references, ids, acyclic, connected, gate
    **dominance**, flags and `__main__` checked by AST, and run block = runspec.
- **`python -m atlantis_core.runspec --instance <dir> --spec <json> [--plan]`** is a closed vocabulary:
  - fields: stages · fetch_mode · streams · learner_swaps · board;
  - it rejects rather than coerces, at both levels;
  - no field carries a path, a prompt or data;
  - **it executes nothing** (operator ruling).
- **`what/board/BOARD.md`** is generated by `board --index [--check]`. It is byte-stable, and every entry is checked or
  the render refuses. Supersession is derived. v0 is labelled open-shape and pinned by sha256. **WI-8 closed.**
- **`board --entries <repo>/what/board/entries`** lets an instance keep its own board. An outside instance cannot write
  Atlantis's board.
- **The dataset-pair template is fixed** against the lattice-labs schema it claimed, with a copy beside it.
  **`python -m atlantis_core.datasets --check`** is new. `what/datasets/` is migrated to three pairs, and the
  env-covariates note is superseded in place. **WI-18 closed.**
- **`who/governance/contribution_guide.md`** is draft 0.1.0, for ratification at the P1 gate. `who/coordination/inbox/`
  is new.
- **III review** (fresh context): PASS-WITH-FINDINGS, 2 major, 7 minor and 5 notes, all addressed. Learning store:
  C-018…C-021 new; C-002, C-012 and C-015 reach 2.
- 475 tests (330 → 475). The byte-stable set is unchanged. **Next: the P1 gate** (fable, operator).

## 2026-10-03 — v0.7.0 · M-1d-i fork from templates alone (P1; M-1d split)

- **M-1d split by operator ruling.** i (this release) is the exit-bar path; ii covers the lattice, runspec, BOARD, dataset
  pairs and the contribution guide. The parent card is `superseded` and kept.
- **atl_v0 0.3.0:** a stream may be *declared* before it is fetched (`ingested_at` optional; `sha256` ⇒ `ingested_at`).
  45 controls, ALL WORLDS AGREE; two sabotages show the rule is load-bearing.
- **Instance contract v0.2.0, amended in place:** the real files and the real self-test command; item 3 staged
  declared → fetched; items 6–7 enforced by code; every item machine-checked.
- **`python -m atlantis_core.fetch`** (closes WI-15) is gated on a self-test receipt (config + self-test code) and, for a
  network fetch, on a signed posture Ratification row inside the instance.
- **Registry R8:** a surveillance channel, or a reasoned absence.
- **`how/templates/template_instance/` + `python -m atlantis_core.fork`:** declarations from interview answers;
  deterministic; 27 refusals, each writing nothing.
- **`python -m atlantis_core.conform`:** contract items 1–12 as ✅/✗ with the files read; it writes nothing.
- **`how/skills/skill_atlantis_instance_fork.md`.**
- **The self-test is shape-general:** any event-stream shape, a mirror-direction C5, and **C8 calendar-lag invariance**.
  The full defect catalogue runs in two forked worlds as well as the exemplar.
- **Dry run:** a fictional hypoxia instance forked from templates alone; contract items 1–8 and 11–12 green; no network.
- **III review** (fresh context): PASS-WITH-FINDINGS, 3 major and 6 minor, all addressed. Learning store: C-004 and C-009
  reach 3 (graduation candidates); C-005 and C-013 reach 2; C-014…C-017 new.
- 330 tests (183 → 330). The byte-stable set is unchanged.

## 2026-10-03 — v0.6.0 · M-1b-ii-b `atlantis_core` site · mapping · archive (P1)

- **`atlantis_core.site`** (`python -m atlantis_core.site --instance <dir>`) makes the explainer page a core template whose
  every word is instance data.
  - `site.yaml` says what to draw; `site_copy.yaml` holds every word.
  - The template is free of exemplar literals, enforced by a test.
  - Site data is assembled from core outputs and registries, never `hab`.
  - **The build re-projects the run and refuses any field that disagrees with the cited board entry.**
- **The exemplar's v1 page** is `site/gulf_karenia_brevis_v1.html`.
  - The copy was moved verbatim, then corrected for board v1: calendar lags, R7, F-8, net beside gross, the T2 panel
    ("a SHAP reading belongs to one model"), the raw-stream what-if, the reproduce section, the footer.
  - The v0 page is byte-stable.
- **`how/templates/template_mapping_atl.yaml`:**
  - registries → five `atl_` labels and six declared edges;
  - pinned bi-temporal stamps;
  - a fence over table shapes, paths and coordinates.
  
  `python -m atlantis_core.mapping --check` is contract item 11's machine check.
- **`src/hab/` archived in place** (`ARCHIVED.md`). It is still the raw-parquet fetch path until the core has a fetch CLI.
- **III review** (fresh context via `iii/`): PASS-WITH-FINDINGS, 10/10 addressed. Among the fixes: grey bands that had been
  invisible since v0, a case rule mis-described since v0, and guards narrower than their names. Learning store C-011…C-013.
- **ADR-002 A-1 PROPOSED** (§4): the exemplar's explainer pages join the capped exception. Awaiting operator ratification.
- 183 tests (125 → 183). `config.yaml`, `atlantis.yaml`, `outputs/`, board entries and schema are byte-stable.

## 2026-10-02 — v0.5.0 · M-1b-ii-a `atlantis_core` eval · explain · board (P1; M-1b-ii split)

- **M-1b-ii split by operator ruling** (the parent card is `superseded` and kept). **ii-a** (this release) covers eval ·
  explain · board · the R7 refit · board v1 · the semantic hash · the learner swap. **ii-b** covers the site · mapping ·
  archiving `src/hab/`.
- **`what/atlantis_core/` 0.2.0** (125 tests, offline):
  - `eval`: the learner is a config field (`xgboost` | `logistic`); metrics; direction-aware lead time; ablations from
    vital groups; sensitivity via the label's event override; **R7 refit per rolling fold, verified per fold**.
  - `explain`: interventional SHAP over a train-only background with additivity as a hard check; exact linear SHAP with
    missingness flags as `availability:` artifacts; net group attribution; **what-if as config**, re-derived from the raw
    stream, lever-gated and era-guarded.
  - `board`: the **closed `AtlEvaluation`** validated against the committed schema, allowlisted extras, per-patient caps,
    and refusal of unhonoured obligations.
  - `run`: the instance end to end.
- **Port equivalence:** on `hab`'s vitals the core reproduces every `metrics.json` key to 1e-12, and SHAP exactly. The
  projector reproduces the M-1c fixture field for field.
- **Board v1** (`what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json`):
  - calendar-correct SST lags: **AUROC 0.8941 → 0.8938, AUPRC 0.5473 → 0.5388**; n, drops and trees unchanged; lead flagged 0.636 → 0.682;
  - semantic `config_hash` (closes WI-7);
  - 2016 fold refit (closes WI-10).
  
  v0 and `metrics.json` are byte-stable.
- **T2 (logistic swap):** test 0.8726 / 0.5225, so the falsifier is not met. **The explanation is learner-dependent:**
  xgboost reads counts first, logistic reads SST and season first. Recorded in the thesis register.
- **Findings of record:**
  - `hab`'s what-if edited a mean of logs as a log of the mean (proven in a test);
  - Tampa's what-if scaled a non-lever gauge;
  - missingness of a structurally absent stream encodes unit identity.
- **III review** (fresh context via `iii/`): PASS-WITH-FINDINGS, 4 major + 4 minor, **8/8 addressed**. v1 was regenerated
  in place by ruling, since it had never left the node. F-8 (test-quantile thresholds) is disclosed and its fix carded
  (`how/backlog/idea_eval_thresholds_fixed_on_validation.md`). Learning store C-008…C-010.
- STATE: M-1b-ii-b queued; WI-7 and WI-10 closed; WI-8 updated; WI-11 and WI-12 opened.

## 2026-10-02 — v0.4.0 · M-1b-i `atlantis_core` skeleton + all-stream self-test (P1 lane 3 of 5; M-1b split)

- **M-1b split by operator ruling** (after M-1c Finding 4). The original card is `superseded` and kept.
  - **M-1b-i** (this) covers registries · fetch · grid · vitals · label · the self-test.
  - **M-1b-ii** covers eval · explain · board · site · reproduction · learner swap · mapping · archiving `src/hab/`.
- **M-1b-i complete** (opus): AAR `how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1b_i_core_vitals_and_selftest.md`.
  - **`what/atlantis_core/`** (89 tests, offline):
    - `config` + `semantic_hash` · `registry` R1–R7 (cross-file refs, grammar, windows, lever owner, engine specs, label
      direction↔signal, climatology eras vs val and rolling folds);
    - `grid`: rules · polygons/WDPA · cells;
    - `fetch`: ArcGIS · ERDDAP · NWIS built; NDBC · OBIS · GBIF · CRW declared (operator ruling: 3 + 3);
    - `vitals`: a whitelisted transform grammar and an evaluator with calendar lags;
    - `label`: above/below, both drops, refuses unlabelled kept rows.
  - **All-stream self-test (SO-7)** checks C0–C7 on every registered stream. The synthetic world has two patients (one
    isolable), gaps, and the real ingest path; the row filters are in the invariance set; the horizon is checked from inside.
    C6 reports the climatology-era dependence. **16 planted defects are each caught by name.**
  - **The exemplar as an instance:** `streams.yaml` · `features.yaml` (25 vitals) · `events.yaml`. linkml-validate and the
    committed JSON Schema PASS, and `run_controls.sh` still reports ALL WORLDS AGREE (42). `atlantis.yaml` is drift-guarded
    against `config.yaml`.
  - **Equivalence:** grid, 22/25 vitals, label, drops and report are exact.
  - **Finding of record:** `hab` counted SST lags in rows across 20 missing OISST weeks (not leakage). The defect touches
    87–133 train rows, and the in-memory refit moves AUPRC 0.5473 → 0.5388. **Operator: calendar-correct.** M-1b-ii lands it
    as a new board version, and `metrics.json` stays byte-stable.
  - **R7 obligation:** the discharge era overlaps the 2016 rolling fold, so the core must refit per fold (WI-10).
  - **III review** (fresh context via `iii/`): PASS-WITH-FINDINGS, 6 major + 5 minor, **11/11 fixed**. Learning store
    C-005…C-007 (degenerate synthetic fixture · one-sided window control · invariance on the target but not the filters).
  - **Budget:** ≈ +70% main context. The SITREP was given at the trip point and the operator ruled to fix everything.
- Schema README known limits 10–11 (a vital that reads no stream · cross-file refs) · STATE: M-1b-ii queued with a
  self-contained prompt.

## 2026-10-02 — v0.3.0 · M-1c `atl_v0` controls complete (P1 lane 2 of 4)

- **M-1c complete** (opus) — AAR `how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1c_linkml_controls.md`. Operator rulings at open: SO-9's ≥ 1 alert budget enforced now; `geometry_ref` = denylist of literals.
  - **`atl_v0` 0.2.0 controlled**: **42 controls** (3 positive · 39 negative), each negative failing only on its `REJECTS_ON` regex at its `REJECTS_AT` path, under **three worlds** (linkml-validate · committed `atl_ontology_v0.schema.json` descendants-off · scratch descendants-on, FORMAT_CHECKER on). Committed JSON == fresh `gen-json-schema --closed`; Rule 4 (flag-proof) asserted. The NO-VALIDATION-CLAIM banner is retired.
  - **Instrument proven to fail**: rule weakened · committed JSON hand-edited · wrong-reason negative → each RUN FAILED. Removing each geometry/anchor arm reddens exactly its own control.
  - **Finding of record**: bare-`required` LinkML rule postconditions are emitted untyped, so `owner: null` / `''` satisfied "a lever names its owner" under both validators. Closed with a typed `all_of` guard.
  - **Fit matrix** (`m1c_vocabulary_fit_matrix.md`): 30 enum values × 7 authorities, 0 bound / 30 local with reasons; Modality vs GOOS EOV (live page, 36 EOVs) → stays local, EOV is a v1 stream annotation. Crosswalk `goos_eov` URL was 404, corrected.
  - **README**: proof table, finding of record, 9 known limits (referential integrity · uniqueness · cross-field equality · …).
- **`iii/` adopted** (`how/federation/iii/`, III v0.6.0 @ `be7dba1`, `opt_in`); **SO-10** — III review via the wrapper, in a fresh context. First review: PASS-WITH-FINDINGS, 12 findings, 11 fixed; learning store C-001…C-004.
- Board entry: `limitations_ref` §12 → §11 (hand fix with provenance note; generator fix → M-1d, **WI-8**).
- STATE: M-1b queued next (self-contained prompt, opus).

## 2026-10-02 — v0.2.1 · M-1a exemplar hygiene complete (P1 lane 1 of 4)

- **M-1a complete** (fable, operator-ruled; carded opus) — AAR `how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1a_exemplar_hygiene.md`. Exemplar `what/exemplars/gulf_karenia_brevis/`:
  - **Drift fixed**: README §Design (log-loss stopping · 1,000 SHAP background rows · `ast`-parsed regions), site §02 heading "Three public data streams, plus the calendar", `uv sync` run order, AGENTS contents + rules.
  - **Provenance**: `hab.provenance` writes `data/raw/{fwc,oisst,usgs}_fetch_summary.json` (rows · dates · sha256 · fetched_at); fetchers call it after a download. Pins verified equal to the board entry's `data_pins` and the `what/datasets/` copies.
  - **Packaging**: `pyproject.toml` + `uv.lock` + `.python-version` (8 pinned direct deps, pytest dev group, `hab` editable from root or `src/`); `requirements.txt` retired; matplotlib dropped (never imported).
  - **`gauges.*.lever` read**: `export_site_data.discharge_tag` sets the discharge features' lever/proxy tag from config; `whatif` records `lever_gauges`.
  - **Safe region parser**: `compile`/`eval` on config strings replaced by an `ast` whitelist evaluator, vectorised; `tests/test_regions.py` (11 tests) freezes the nine region counts (196,024 samples, identical to the `eval` baseline).
  - **T4 negative control**: `python -m hab.train --negative-control` → `outputs/negative_control_auprc_stop.json` — AUPRC early-stopping gives 2 trees, test AUROC 0.877 / AUPRC 0.423 / Brier 0.0705, calibration slope 18.09 (reference 141 trees, 1.17).
  - **Invariants**: `config.yaml` and `outputs/metrics.json` byte-identical; self-test green before and after; gitleaks clean.
- **Finding of record (WI-7)**: `metrics.json → config_hash e9dea88254` is the md5 of the *training-time* config (`shap.background_n: 2000`); the live file hashes `979d3fdf16`. Nothing the model sees differs. Documented in README §Provenance; `atlantis_core` (M-1b) records a semantic hash. WI-6 closed.
- STATE: M-1c queued next (self-contained prompt, opus); M-1b after.

## 2026-10-02 — v0.2.0 · M-0 complete with the widened remit; P0 gate MET (Operation Tidewatch → P1)

- **P0-exit gate MET 2026-10-02** (operator, `AskUserQuestion`): ADR-000/001/002 **ratified** · persona **Proteus** · **GO P1** · push to the public remote authorised.

- **Remit widened** by the operator (2026-10-01): Atlantis becomes the MPA knowledge · data-model · evidence system around the method — `who/governance/adr_002_remit_mpa_knowledge_system.md` (proposed). Four rulings taken by `AskUserQuestion`; persona and ADR signatures carried to the P0-exit gate.
- **ADR-001** persona (Proteus / Nereus alt.) · category **Framework + reference implementation** · code home `what/atlantis_core/` · name-form. **ADR-000** lineage amendment. ADRs stay in `who/governance/`.
- **Thesis register** (12 falsifiable claims; numbers from `metrics.json`) · **instance contract v0** (12-item conformance-by-mapping checklist; `federation_ref` in Organization shape with 7 `ATL-*` pattern ids) · federation wrapper repointed.
- **`atl_v0` ontology** (`what/schema/atl_v0/`): LinkML draft — 5 classes (SpatialUnit · ObservationStream · Vital · EventDefinition · Evaluation), 7 enums, 2 rules; lint 0 errors / 38 warnings in a scratch venv; **NO VALIDATION CLAIM** (controls = M-1c). Crosswalk: 6 bound (WDPA · CF · UCUM · WoRMS · Darwin Core · PROV-O), 6 deferred, source protocols listed as non-vocabularies. `what/ontology.md` gains the Atlantis Extensions table (entity_count 26 → 31).
- **Evidence board v1** (`what/board/`, GREEN, metrics only, no accuracy claim) with the exemplar's entry generated by script from `outputs/metrics.json` + sha256 pins of the three raw parquets. **Templates:** `template_model_card.md`, `template_dataset_pair/`. **Hypothesis-ledger spec** (`what/hypotheses/README.md`). `what/datasets/AGENTS.md` with the **snapshot rule**.
- **Charter re-cut** to the five layers; **roster P1–P5** with 9 cards (`executor_tier` · `token_budget_estimated` · `depends_on` · `aar_path` · acceptance checklists); **P2 ruling** = Florida Keys NMS coral bleaching (first MPA instance). M-0 card completed with AAR.
- CLAUDE / MANIFEST / README / AGENTS / STATE updated; SO-2 label fixed (no longer cites SO-7); new SO-9 (no accuracy claim without base rate · budget · limits). Backlog: Tier-3 ocean type-vocabulary memo; co-sign the Datasets.aDNA provenance-contract seam.
- Found at M-0, fixed at P1 M-1a: README/config drift (AUPRC vs log-loss stopping; 2000 vs 1000 SHAP background rows), "four streams" vs three, `gauges.*.lever` unread by code, `eval` on region rules, no sha256 provenance for SST/discharge, self-test perturbs only cell counts.

## 2026-09-23 — v0.1.0 · genesis seed (Operation Tidewatch, P0 queued)

- Forked from `.adna/` per `skill_project_fork.md` by Berthier (aDNALabs S329); genesis-customised stub, onboarding suppressed.
- Persona **Proteus** and category **Framework + reference platform** proposed; codename **Operation Tidewatch** (fleet-grep clean).
- Seeded: thesis (`concept_atlantis`), the 8-step method (`pattern_ecosystem_early_warning`), the data/literature mining playbook, the P0–P5 charter with written exit bars, the M-0 card, the federation wrapper contract stub, ADR-000 (proposed).
- Relocated the *Karenia brevis* pilot (`Atlantis.aDNA/what/exemplars/gulf_karenia_brevis` → `what/exemplars/gulf_karenia_brevis/`) whole: code, config, trained models, SHAP, what-if, explainer site, dataset notes. Leakage self-test re-run green at the new path.
- Public remote `aDNA-Network/Atlantis.aDNA` (MIT) created at seed time on the operator's ruling.

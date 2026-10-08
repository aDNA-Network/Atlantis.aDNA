---
type: state
status: p3_open
phase: "P3 open — P2 gate MET 2026-10-08, CONDITIONAL GO P3 (a) M-2c before M-3b · (b) P3 re-carded ≈2.3× · (c) M-3b off the exemplar · (d) P4 bar before P4; M-2c ⏭ (opus) · M-3a"
campaigns: [campaign_atlantis_genesis]
mission: m2c   # QUEUED (opus); P2 gate ✅ 2026-10-08 (conditional GO P3; opus decision brief + III review of the gate case, PASS-WITH-FINDINGS 0/6/4/2); M-2b ✅ 2026-10-08 (board v2 · core 0.6.1 · atl_v0 0.7.0 · III 8/8); M-2a-ii ✅ 2026-10-08 (forked · fetched · conforms · III 9/9 · core 0.5.3); M-1f ✅ 2026-10-07 (board v3); M-2a-i ✅ 2026-10-06; M-2a split 2026-10-06; M-1e ✅ 2026-10-03 (board v2); P1 gate ✅ 2026-10-03 (conditional GO); M-1d-ii ✅ · M-1d-i ✅ · M-1b-ii-b ✅ 2026-10-03; M-1b-ii-a ✅ · M-1b-i ✅ · M-0 ✅ · M-1a ✅ · M-1c ✅ (2026-10-02)
persona: proteus   # RULED 2026-10-02 (ADR-001 ratified)
last_session: session_stanley_20261008_215226_p2_gate_rulings (opus)
created: 2026-09-23
updated: 2026-10-08
last_edited_by: agent_proteus
tags: [state, atlantis, tidewatch, p1_open, m1a_complete, m1c_complete, m1b_i_complete, m1b_ii_a_complete, m1b_ii_b_complete, m1d_i_complete, m1d_ii_complete, p1_gate_met, p2_conditional_go, m1e_complete, board_v2, atl_v0_0_4_0, m2a_split, m2a_i_complete, atl_v0_0_5_0, core_0_4_0, crw_built, m1f_complete, board_v3, atl_v0_0_6_0, core_0_5_0, m2a_ii_complete, core_0_5_1, core_0_5_2, core_0_5_3, floridakeyscoral_forked, floridakeyscoral_fetched, m2b_complete, core_0_6_0, core_0_6_1, atl_v0_0_7_0, floridakeyscoral_on_board, p2_gate_met, p3_conditional_go, p3_open]
---

# STATE — Atlantis.aDNA

## Resume-Here

1. `CLAUDE.md` (identity widened per ADR-002; persona Proteus ruled; standing orders incl. new SO-9).
2. The charter (re-cut M-0): `how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md` → the roster
   `artifacts/mission_roster_p1_p5.md`.
3. The three ADRs in `who/governance/` (all **ratified 2026-10-02**).
4. The exemplar is at hygiene (M-1a): `what/exemplars/gulf_karenia_brevis/README.md` §Provenance · `uv sync && .venv/bin/python -m pytest` · self-test green.
5. The ontology is controlled (M-1c; 0.3.0 at M-1d-i; 0.4.0 at M-1e; 0.5.0 at M-2a-i; 0.6.0 at M-1f): `what/schema/atl_v0/README.md` (proof table · known limits) · `LINKML_BIN=<scratch venv>/bin what/schema/atl_v0/fixtures/controls/run_controls.sh` → ALL WORLDS AGREE (65 controls; 0.7.0 at M-2b).
6. III review goes through `iii/` in a fresh context (SO-10).
7. The core (M-1b-i + ii-a + ii-b + M-1d-i + M-1d-ii): `what/atlantis_core/README.md` · `cd what/atlantis_core && uv sync && .venv/bin/python -m pytest` (694, ~3.5 min unloaded; core 0.6.1; `node` on PATH for the page-script checks) ·
   `.venv/bin/python -m atlantis_core.selftest --instance ../exemplars/gulf_karenia_brevis` (all-stream, SO-7) ·
   `python -m atlantis_core.run --instance …` (→ `outputs/atlantis_core/`, ~7 min) · `python -m atlantis_core.board …` (→ `what/board/entries/`) ·
   `python -m atlantis_core.site --instance …` (→ the instance's page, ~2 s) · `python -m atlantis_core.mapping --check <mapping.yaml>` ·
   **a new instance:** `how/skills/skill_atlantis_instance_fork.md` → `atlantis_core.fork` · `conform` · `selftest` (receipt) · `fetch` (gated).
8. The method as one pipeline (M-1d-ii): `how/lattices/lattice_atlantis_pipeline.lattice.yaml` · `python -m atlantis_core.lattice` ·
   `atlantis_core.runspec --plan` · `what/board/BOARD.md` (`board --index --check`) · `atlantis_core.datasets --check ../datasets` ·
   `who/governance/contribution_guide.md` (draft).

## ⏭ QUEUED — Next Live Session

**P2 gate MET 2026-10-08: CONDITIONAL GO P3.** The operator ruled it by `AskUserQuestion`, after an opus decision brief
and a fresh-context III review of the gate case. That review is `…/artifacts/p2_gate_iii_review.md`: PASS-WITH-FINDINGS,
0 blocker, 6 major, 4 minor, 2 nit. **Recorded deviation:** the gate ran on opus, not fable, by the operator's ruling.
This is the second time (P1, P2), and the charter is not amended.

- **T9: the exit bar is met as worded; drop-in is not demonstrated.**
  - There were zero instance patches, but under the card's "do not patch locally" rule that weak form could not fail (C-009).
  - FKNMS forced **≈ 13–15** Atlantis changes once the M-2a-i set is counted. That is P4's baseline.
- **Theses, as ruled:**
  - T1: supported by two instances.
  - T3 and T10: tested on one instance.
  - **T11: untested at its terms** (no climatology at a budget, C-034).
  - **T4: untested on FKNMS.**
  - T2: its P2 swap was never run (C-033).
  - T5's absence case and T12's DHW ≥ 8 run are recorded.
  - T8: untested.
- **Conditions:**
  - (a) **M-2c** comes before M-3b.
  - (b) P3 is re-carded at ≈ 2.3× the card top, with the reviewer counted.
  - (c) M-3b targets FKNMS or a new instance, not the exemplar.
  - (d) "No template change" for P4 is defined before P4 opens.
- **Push:** a board README note now says instance refs resolve in the instance. FloridaKeysCoral is local-only, so its
  entry's refs are not yet public. After the note, Atlantis was pushed.
- **III:** C-009 → 7, C-030 → 2, C-032 → 2, plus new C-033 and C-034. The graduation memo was redrafted for all six; C-015
  is below the bar, because `accepted` was never set. The Hestia memo flags Atlantis's stale row.

**Next: M-2c** (opus): `missions/mission_m2c_commensurable_board.md`. **M-3a** (opus) may run beside it, since they share
no files.

**Pending operator acts:**
- Deliver the graduation memo into `III.aDNA/who/coordination/`.
- Deliver the Hestia memo into `Home.aDNA/who/coordination/inbox/`.
- C-015's acceptance (local).
- FloridaKeysCoral's remote, which is the owner's ruling.

**Next Session Prompt (self-contained, M-2c, opus):**

> You are Proteus in `~/aDNA/Atlantis.aDNA`, on **opus**, opening **M-2c**, which is P2-gate condition (a). Read, in order:
> 1. STATE.
> 2. The charter's §P2 gate record (`how/campaigns/campaign_atlantis_genesis/campaign_atlantis_genesis.md`).
> 3. The card `missions/mission_m2c_commensurable_board.md`.
> 4. `artifacts/p2_gate_iii_review.md` (G-3, G-4, G-7, G-12).
> 5. The register's rows T2, T10 and T11.
> 6. `what/board/README.md`.
> 7. `what/atlantis_core/README.md` (the eval section), and `eval/metrics.py`'s climatology and threshold-fixing code.
>
> Then probe `how/sessions/active/` and open a lease. If the card is too big for one sitting, put its split line
> (M-2c-i core + schema + exemplar v4 / M-2c-ii FKNMS v3 memo + swap) to the operator with `AskUserQuestion` before
> building. Build plant-first:
> - climatology at budget, with thresholds fixed on validation and a new atl_v0 0.8.0 slot plus controls;
> - a season-block paired interval;
> - the `BOARD.md` lead column;
> - exemplar board v4.
>
> FKNMS v3 is built in the instance and arrives by steward memo. Run SO-7's self-test if vitals or label code moves.
> Review through `iii/` in a fresh context. Write the AAR. SITREP at the +50% line.
>
> Budget: ≈ 350 kT plus a reviewer of ≈ 200 kT.

## What's in place

### P2 gate (2026-10-08, opus decision brief; session `…_215226_p2_gate_rulings`)

- **The rulings:** conditional GO P3 with conditions (a)–(d); thesis statuses as the reviewer amended them; a board README
  note, then the push; ACCUMULATE; the graduation memo redrafted.
- **The III review of the gate case** (`artifacts/p2_gate_iii_review.md`):
  - **G-1:** the weak form of T9 holds by construction.
  - **G-2:** the deviation count is ≈ 13–15, not nine.
  - **G-3:** T11 has never been measured at its budget.
  - **G-4:** the re-card dropped obligations the register had given P2.
  - **G-5:** T4's causal clause is untested.
  - **G-6:** the entry's refs point into a local-only instance.
- **Push guards (run before the ruling):** 694 tests; ALL WORLDS AGREE; `board --index --check` ✅; gitleaks exit 0; no file
  over 1 MB; no data files.

### M-2b (2026-10-08 — Atlantis `9ac40cf` · `671808b` · `94ee95f` · `40f9b3a` · `28e5af4` · `0a1dd2e` + close; instance `6e031f6` · `88685c7`)

- **Rulings 19–26** (AskUserQuestion): 19 persistence + trend comparators; 20 as atl_v0 0.7.0 slots; 21 FKNMS rolling origin
  2013–2024 (hash → `c07b7c0288`); 22 land the entry here; 23 continue past the +50% line; 24 re-run for F-6; 25 item 10 =
  renderer + `node --check`; 26 v2 supersedes v1 (SO-2 refuses to regenerate).
- **Core 0.6.0:** `signal_history` · `persistence_baseline` · `trend_baseline` · per-segment `base_rate` ·
  `calibration_in_the_large` · `assert_comparators` · `rolling_origin_years` optional · BOARD.md "Comparators and the shift".
  **`671808b`:** the page script parses (node test) · polygon zone names · conform item 10 reads core-built pages.
  **0.6.1 (III):** step-input plant · item 10 renderer + node · slot ↔ result · stale config bytes refused · "Positives".
- **Findings:** the calendar knows most of a summer heat event; a validation-fixed threshold over-alerts 1.4–2× under the
  shift; lead is censored at H when the signal accumulates; two checks had never met a core-built artifact (item 10, the
  rolling-origin KeyError); a build that checks words is not a build that checks the page runs.
- **III:** PASS-WITH-FINDINGS 8/8. Store: C-007 → 2 · C-009 → 6 · C-011 → 2 · C-023 → 5; new C-031, C-032.


### M-2a-ii (2026-10-07 → 08 — Atlantis `0e4154b` · `f23e046` · `95ea8da` · `3c8d11a` · `bf073b8` + close; instance `d7f5e31` · `3e45b93` · `07df953` · `345ae7f`)

- **FloridaKeysCoral.aDNA** was forked, ratified (ADR-001 public; raw SST dropped for its OSTIA terms), fetched and
  conforms at the fetched stage.
- **Rulings 1–18**, every one via `AskUserQuestion`:
  - 13: no mirror switch;
  - 14–15: 15-day union spans;
  - 16: the data accepted;
  - 17: disclose the 1999-05-01 gap;
  - 18: test the edge tie and disclose it.
- **Core 0.5.1 → 0.5.3:**
  - the fork's `sensitivity_threshold` path;
  - C6 is n/a without a climatology;
  - an ERDDAP `start` date;
  - `chunk_months` and `chunk_days`, and `envelope: union`;
  - the cache keyed on the base (III F-1);
  - the summary's `completeness` and `fetch --verify` ⓘ (F-2).
- **Findings:**
  - probe-200 ≠ data-200: CRW's proxy cuts a request at ~10.3 s, and a 5-year chunk could never fit (C-028);
  - licence is per product and mirrors are not neutral;
  - the base rate is non-stationary.
- **III:** PASS-WITH-FINDINGS 9/9. Local store: C-010 → 3, C-023 → 4; new C-028, C-029 and C-030.

### M-1f (2026-10-07 — commits `96a8cae`…`fd95cdd` + ACCUMULATE + close) — WI-23

- **Measured:** the III fold table reproduced exactly (crossing positives). Main split: train→val 25 rows (3 of 920
  positives); val→test 34 rows (1 of 121).
- **atlantis_core 0.5.0:**
  - **Eval:** `split.embargo_weeks` (absent → H; `none` off; partial refused) at six boundaries; the refits keep the train
    tail. `check_label_windows` reads the event's H on FitRecorder frames, and `horizon_spill` measures the spill.
    Ablations, sensitivity and climatology are embargoed; the test-year fold skip is said.
  - **Hash:** `semantic_hash` reads the resolved E (exemplar `7b789afded`; `none` ≡ `acfa22c6e4`). Conform item 8 refuses a
    partial embargo.
  - **Board:** `assert_embargo` covers every published run, against the split's years, with `rows_dropped ≥` the crossing
    rows.
- **Board v3:** 146 trees · 0.8950 / 0.5414 · lead 13/22. `none` ≡ v2 (tested by running), and v0–v2 are pinned.
- **atl_v0 0.6.0:** `AtlEvaluation.embargo_weeks`, 56 controls. Runner: grep's exit status is read whole.
- **III:** PASS-WITH-FINDINGS, 7/7. C-009 → 5, C-023 → 3; new C-026 and C-027.

### M-2a-i (2026-10-06 — commits `9873844`…`dd103fb` + III + close) — P2 condition (c)

- **Contract v0.3.0:** `NOAACRW:` authority. **atl_v0 0.5.0:** `refractory_weeks` + the prefix (53 controls).
- **atlantis_core 0.4.0:**
  - **Grid:** `grid.sha256` (fork / `make_grid` / conform item 1); duplicate ids refused.
  - **Label:** `refractory_weeks` (R absent ≡ 0, hashed only when set).
  - **Self-test:** `event_series` iid | accumulating; C9 (never skipped); the episode check recomputed from the raw frame,
    through a gap longer than the carry; `persistent_master`; catalogue × 3; refractory plants.
  - **Fetch:** `CoralReefWatch` built (`bind`; per-feature cell-centre mask; nearest-cell fallback; reduction + basis on
    the summary; a stale basis is refused by fetch, `--verify` and conform item 3).
- **Live smoke (scratch):** in 2023, Lower Keys DHW ≥ 4 from 10 July, ~18 by late September. CRW answered after three 502s.
- **Findings of record:**
  - the grid pin had never existed (C-023 class);
  - R = H − 1, not R = H, is the lead-time onset (C-025);
  - the CRW cache key omitted its basis (C-010 / C-023);
  - C9's first boundary skip was C-015 again.
- **III:** PASS-WITH-FINDINGS, 8/8. Local store: C-024 and C-025 new. Graduation candidates: C-004, C-005, C-009, C-015.


### M-1e (2026-10-03 — commits `20075f1`…`4bda9b5` + close) — P2 condition (a)

- **eval:** `threshold_from: val` fixes thresholds on the selection model's val scores and reads them back from the result.
  `rolling_selection: per_fold` makes each fold early-stop on its inner year with eras ≤ Y−1, checked on what `fit`
  received. A stop year with < 5 positives skips its fold, and says so. Lead time records `alert_threshold`. `test` /
  `full_model` exist only for the port.
- **atl_v0 0.4.0:** `threshold_from` · `realised_rate`, with the rule validation ⇒ realised required (typed `all_of`). 50 controls.
- **board v2:** emitted by code. A single cause is proven by bytes. The emitter refuses F-8 for the headline and every swap,
  by identity and arithmetic. `BOARD.md` budgets show the threshold source and realised rate.
- **The v2 page:** a new file from `site_v2.yaml` and `site_copy_v2.yaml`; the site reads a named run (`outputs:`, `--site`).
- **Tests:** 480 → 516. Plants P1–P4 are written into eval's own source.
- **Findings of record:**
  - every realised rate falls below nominal (two likely reasons, neither proven);
  - per-fold selection is noisy (63–623 trees);
  - the label horizon crosses every boundary (disclosed; embargo carded);
  - C-023: provenance stamped from intent emits clean.
- **III:** PASS-WITH-FINDINGS, 8/8 addressed. Learning store: C-009 → 4, plus C-022 and C-023.


### M-1d-ii (2026-10-03 — commits `3e787d3`…`8ca7bc5` + close)

- **Lattice:** `how/lattices/lattice_atlantis_pipeline.lattice.yaml` with `atlantis_core.lattice`. It is checked three
  ways: the strict schema (a byte-identical copy), the peer validator imported by path, and local invariants (edge
  references · ids · acyclic · connected · gate dominance · AST flags and `__main__` · run block = runspec).
- **Runspec:** `atlantis_core.runspec` + `how/templates/template_runspec.example.json`. A closed vocabulary that
  validates and plans; exit 3 = REJECT.
- **Board:** `board --index [--check]` → `what/board/BOARD.md`. Every entry is checked, or the render refuses. v0 is
  open-shape, pinned by id and sha256, with supersession derived. `board --entries <repo>/what/board/entries`.
- **Datasets:** `atlantis_core.datasets --check`. The template is fixed, with its schema copied beside it. Three pairs;
  the env-covariates note is superseded in place.
- **Governance:** `who/governance/contribution_guide.md` (draft) · `who/coordination/inbox/`.
- **Tests:** 330 → 475.
- **Findings of record:**
  - two gates checked a proxy (`--outputs`; reachability for dominance);
  - validated strings could still write markdown onto the board;
  - an open-shape record's only closure is its bytes;
  - "nothing in the workspace passes" was 2 of 26 (corrected).


### M-1d-i (2026-10-03 — commits `999a9fa`…`16558df` + close)

- **Ontology:** atl_v0 0.3.0, a declared stream validates (`sha256` ⇒ `ingested_at`); 45 controls; contract v0.2.0 amended in place.
- **The core:**
  - `fetch` CLI: the receipt gate (semantic hash + self-test code) and the posture gate (a signed Ratification row inside
    the instance);
  - R8;
  - `fork` (`how/templates/template_instance/`, 27 refusals, pre-write R1–R8);
  - `conform` (items 1–12, 57 tests).
- **The self-test:**
  - the event stream may have any shape, and carries the label-exposing gaps;
  - C5 runs the mirror direction;
  - C8 is calendar-lag invariance;
  - comparisons are NA-safe;
  - the 12-defect catalogue runs in two forked worlds.
- **Skill:** `how/skills/skill_atlantis_instance_fork.md`.
- **Dry run:** a fictional Sandbar Estuary instance; items 1–8 and 11–12 ✅; 0 sockets (in-process guard); the word-flip
  ratification is refused.
- **Tests:** 330. The byte-stable set is unchanged.
- **Findings of record:**
  - the self-test had been point-only;
  - `gap_week` was a blind-spot relocation (C-015);
  - the posture gate was bypassable (C-016, C-017);
  - the exemplar is a reference run, not a conformant instance.


### M-1b-ii-b (2026-10-03 — commits `d0d0c14`…`dc8763a` + close)

- **`atlantis_core.site`:**
  - The template holds structure, style and generic renderers, and a literal guard keeps it free of exemplar words.
  - `assemble` builds the site data from core outputs, processed tables, registries and `site.yaml`, never from `hab`.
  - The build re-projects the run against the cited board entry field by field, ties `shap.npz` to the run, and enforces
    one copy grammar at build and render.
- **The exemplar's copy** was moved verbatim (366/366 text nodes), then corrected for v1 in a separate commit:
  - calendar lags;
  - R7;
  - F-8;
  - net beside gross;
  - the T2 panel;
  - the raw-stream what-if;
  - the reproduce section;
  - the footer.
- **The v1 page** is browser-checked.
- **Mapping:** `template_mapping_atl.yaml` + `atlantis_core.mapping --check` (28 planted defects).
- **`src/hab/ARCHIVED.md`:** the per-module table of what still runs.
- **Tests:** 183 total. The byte-stable set is unchanged since `4bb1939`.
- **Findings of record:**
  - `hab` is still the fetch path;
  - v0's EDA was stale against its own region rules (disclosed on the page);
  - the grey bands had been invisible since v0 (fixed);
  - the case rule was mis-described since v0 (fixed).
- **III:** PASS-WITH-FINDINGS, 10/10 addressed. Learning store: C-004 and C-009 +1, C-011…C-013 new.


### M-1b-ii-a (2026-10-02 — commits `e8751e5` · `b10ec48` · `bf0b36a` · `8edfc87` + close)

- **The package** gains `eval` (learners as config: xgboost · logistic; metrics; lead, which is direction-aware; rolling, with R7
  verified per fold), `explain` (interventional SHAP; exact linear SHAP with `availability:` flags; net group attribution;
  what-if as config), `board` (the closed `AtlEvaluation` plus allowlisted extras; refuses unhonoured obligations) and `run`.
  125 tests.
- **Port equivalence:**
  - eval → `metrics.json` exact to 1e-12;
  - SHAP → `shap_summary.json` exact;
  - the projector reproduces the M-1c fixture field for field.
- **Board v1** `what/board/entries/2026-10-02_gulf_karenia_brevis_v1.json`: 0.8938 / 0.5388 · lead flagged 0.636 → 0.682 ·
  semantic hash `acfa22c6e4`. Regenerated in place after review, by ruling; the regeneration is recorded in its extras.
- **Findings of record:**
  - `hab`'s what-if edited a mean of logs as a log of the mean (proven), and scaled Tampa's non-lever gauge silently;
  - T2: the ranking is learner-invariant, the explanation is not;
  - absence of a stream encodes unit identity.
- **III:** PASS-WITH-FINDINGS, 8/8 addressed (F-8 disclosed and carded); learning store C-008…C-010.


### M-1b-i (2026-10-02 — 5 commits `67c602b`…`767ea73` + close)

- **The package**, `what/atlantis_core/` (89 tests, offline):
  - `config` (with `semantic_hash`) · `registry` R1–R7, the cross-file checks that linkml-validate can't make;
  - `grid`: rules, polygons/WDPA, cells;
  - `fetch`: ArcGIS, ERDDAP and NWIS built; NDBC, OBIS, GBIF and CRW declared;
  - `vitals`: the whitelisted grammar and its evaluator, with calendar lags;
  - `label`: above/below with both drop counts;
  - **`selftest`**: C0–C7, two patients, a gap world, the row filters in the invariance set, and the horizon checked from
    inside. 16 planted defects are each caught by name.
- **The exemplar as an instance:** `streams.yaml` · `features.yaml` (25 `AtlVital`s) · `events.yaml` all pass linkml-validate
  and the committed JSON Schema. `atlantis.yaml` is drift-guarded against `config.yaml`.
- **Finding of record:** `hab`'s SST lags were counted in rows across 20 missing OISST weeks. That is not leakage; it touches
  87–133 train rows, and fixing it moves AUPRC 0.547 → 0.539. The operator ruled calendar-correct.
- **Also found:** a climatology normal is a whole-era statistic (C6 reports it). The exemplar's discharge era overlaps the 2016
  rolling fold, so R7 records an obligation to refit per fold.
- **III review:** PASS-WITH-FINDINGS, 11/11 fixed; learning store C-005…C-007.

### M-1c (2026-10-02 — 6 commits `885b8a7`…)

- `atl_v0` **0.2.0, controlled**: 42 controls (3 pos · 39 neg) under linkml-validate + committed JSON (desc-off) + scratch
  JSON (desc-on); `atl_ontology_v0.schema.json` committed, byte-checked each run; Rule 4 asserted; the instrument proven to fail
  (3 sabotages + 7 per-arm). Rulings: alert_budgets ≥ 1 now; geometry_ref denylist. Fit matrix: 30 enum values, 0 bound /
  30 local; Modality vs GOOS EOV → local, EOV = v1 stream annotation. README: proof table + 9 known limits.
- Finding of record: bare-`required` rule postconditions are emitted untyped, so `owner: null` passed both validators. Closed with typed `all_of`.
- `iii/` → `how/federation/iii/` (III v0.6.0 @ `be7dba1`); SO-10; learning store C-001…C-004.

### M-1a (2026-10-02 — 8 commits `173613e`…)

- Exemplar hygiene: README/site/AGENTS drift fixed (log-loss stopping · 1,000 SHAP rows · "three streams plus the calendar") · `hab.provenance` + three `*_fetch_summary.json` with sha256 (== board `data_pins` == `what/datasets/` copies) · `pyproject.toml` + `uv.lock` (requirements.txt retired, matplotlib dropped) · `gauges.*.lever` read by code · region rules via `ast` whitelist, `tests/test_regions.py` freezes the 9 counts · T4 negative control `outputs/negative_control_auprc_stop.json` (2 trees, slope 18.09). `config.yaml` + `metrics.json` byte-stable; self-test green.
- Finding of record: `config_hash e9dea88254` = training-time config (`shap.background_n: 2000`); live file → `979d3fdf16`. Explained in README §Provenance; semantic hash → M-1b.

### M-0 (2026-10-02 — 6 commits on `aec55d4`)

- **Governance:** ADR-000 (lineage amended) · ADR-001 (persona · Framework + reference implementation · `what/atlantis_core/`) · ADR-002 (remit widening · five layers · snapshot rule · what crosses / never crosses) — all `proposed`.
- **Planning artifacts:** thesis register (12 claims, 9 supported-by-one-exemplar, 3 untested) · instance contract v0 (12-item checklist, 7 `ATL-*` ids) · roster + 9 cards · P2 ruling (FKNMS coral) · charter re-cut.
- **L1 ontology:** `what/schema/atl_v0/` — LinkML draft, 5 classes / 7 enums / 2 rules; lint 0 errors / 38 warnings; closed JSON Schema generates (18 defs; not committed); smoke pos/neg validated; **NO VALIDATION CLAIM** until M-1c. Crosswalk 6 bound / 6 deferred.
- **L4 registries:** evidence board v1 + exemplar entry (script-generated from `metrics.json`, sha256 pins) · model-card template · dataset-pair template · hypothesis-ledger spec · `what/datasets/AGENTS.md`.
- **L2 / L3 / L5:** specified and carded (M-1b · M-1d/M-3/M-5 · M-4); nothing built — by the sitting-depth ruling.
- Exemplar untouched at M-0; self-test green at open and close.

## Active blockers

- **M-2a-ii fetch: CRW ERDDAP outage** (502 on every request from ~23:13Z 2026-10-07). Resume at sitting 2 after a 200 probe.
- ~~push~~ **done 2026-10-03** (operator ruling, `AskUserQuestion`): `f07403e..9ac5e34` → `origin/main`, after gitleaks over the
  range (7 commits, exit 0), no file over 1 MB, no data files. **Board v2 is now published**: corrections from here are a new version (SO-2).
- ~~push~~ **done 2026-10-03** (operator ruling): `cec155b..33fb62d` → `origin/main`, after gitleaks over the range
  (one false positive → a narrow match-only allowlist, tested), no file over 1 MB, no data files, 480 tests green.
- `#needs-human`: **delivering the graduation memo** into `III.aDNA/who/coordination/`. That is a peer-vault write, for an
  operator-opened session.

## Watch items

- ~~WI-1~~ **closed 2026-10-02** — the Home router row landed in Hestia's commit `96ae4a2` (Home.aDNA). Its category text still says "ref. platform"; Hestia's row, Hestia's edit — memo after the gate.
- WI-2 — Exemplar raw OISST chunk CSVs (193 MB) are gitignored; `data/raw/oisst_region_daily.parquet` is the committed derivative. A fresh clone regenerates via `fetch_env` (≈30 min against ERDDAP).
- WI-3 — The Artifact link is private; sharing is the operator's act.
- WI-4 — `aDNA.aDNA` ADR-062 (LinkML adoption) is still `proposed`; `atl_v0` cites it as preferred-but-optional. If it is declined, the schema stays conformant as "another language" and the controls still run.
- WI-5 — `Datasets.aDNA` provenance-contract seam open (ASOAtlas memo 2026-09-25 unanswered); Atlantis co-signs after the gate (`how/backlog/idea_cosign_datasets_provenance_contract.md`).
- ~~WI-6~~ **closed 2026-10-02 (M-1a)** — README/config drift fixed; board entry already followed the outputs.
- ~~WI-7~~ **closed 2026-10-02 (M-1b-ii-a)** — board v1's `config_hash` is the semantic hash (`acfa22c6e4`; its boundary set by effect, III F-2) with the bytes-md5s beside it; `hab`'s `e9dea88254` stays explained in exemplar README §Provenance.
- ~~WI-8~~ **closed 2026-10-03 (M-1d-ii)** — `BOARD.md` is generated by `board --index`. v0 is rendered and labelled
  open-shape (grandfathered by id + sha256), and v1 is closed. Original text follows. The board entry's embedded `evaluation` is **not** a closed `AtlEvaluation` (extra keys: `event`, `patient`, `modelling_*`,
  `dropped_*`, `n_trees`, `n_vitals`, `vital_groups`, `sensitivity`, a `shap_summary` object; pins carry `artifact`). The `§11`
  limitations label was hand-fixed at M-1c with a provenance note. Closes when M-1b's board emitter / M-1d's BOARD generator emits the
  validated projection (= `pos_exemplar_gulf_karenia_brevis.yaml`'s evaluation) with the extras beside it.
  **Update 2026-10-02 (M-1b-ii-a):** the emitter exists and v1 is closed + validated; v0 keeps its open shape (untouched). Closes at
  M-1d's BOARD generator.
- ~~WI-10~~ **closed 2026-10-02 (M-1b-ii-a)** — noted on board v1; v1's 2016 fold is refit (verified per fold). Immaterial here
  (0.8810 unrefit vs 0.8808 refit), material elsewhere by construction.
- ~~WI-11~~ **closed 2026-10-03 (M-1e):** board v2. Original text follows. **F-8 (disclosed, not fixed):** alert-budget and lead-time thresholds are test-score quantiles; rolling folds testing
  2017–2019 reuse a tree count early-stopped on them. Fix carded: `how/backlog/idea_eval_thresholds_fixed_on_validation.md` → a new
  board version, before any steward-facing budget claim.
- WI-12 — v1 schema candidates from ii-a: a unit × stream "structurally absent" declaration (absence encodes unit identity) and
  lever-ness per station or source rather than per vital (Tampa's non-lever gauge under a lever-tagged vital).
- ~~WI-13~~ **closed 2026-10-03 (P1 gate): A-1 RATIFIED.** Was: **ADR-002 A-1 PROPOSED 2026-10-03** (III F-5): the exemplar's explainer pages join §4's capped exception
  (exemplar-only, derived from the public parquets, rebuildable, never an instance page). Ratify at the P1 gate or before.
- ~~WI-14~~ **closed 2026-10-03 (M-1e):** v2's `limitations_ref` → `site/gulf_karenia_brevis_v2.html#limits` (it names the fix
  and its residuals). The v1 page's limits still describe F-8 as open, which was true when it was published. Original text follows. Board v1's `limitations_ref` points at the v0 page's `#limits`, which lacks v1's limits (III F-6). v1 stays
  byte-stable; **board v2** (with the F-8 fix) repoints it to `site/gulf_karenia_brevis_v1.html#limits`.
- ~~WI-15~~ **closed 2026-10-03 (M-1d-i)** — `python -m atlantis_core.fetch` exists, gated on the self-test receipt and a ratified
  posture. `hab.fetch_*` is now only the recipe that produced the committed bytes; a live core re-fetch has not been run.
- WI-16 — Neo4j substrate allow-list admission for the five `atl_` labels and six edge types (`template_mapping_atl.yaml`
  header): a coordination memo to `Neo4j.aDNA` after the gate.
- WI-17 — `aDNA.aDNA/what/lattices/tools/lattice_validate.py` has no CLI (and its docstring import path is stale). M-1d-ii
  imports it; memo to Rosetta after the gate.
- ~~WI-18~~ **closed 2026-10-03 (M-1d-ii)** — the template is fixed and validated (schema copy beside it). The upstream
  note goes by memo (24 of 26 workspace `.dataset.yaml` fail it). Original text follows: `how/templates/template_dataset_pair/` fails the lattice-labs `dataset_yaml_schema.json` it claims (sha256
  placement, `storage.location`/`provider`, lineage keys). M-1d-ii fixes the template; the upstream note goes by memo.
- WI-19 — *(P1 gate: NDBC dropped from M-2. **CRW BUILT 2026-10-06 (M-2a-i)**; NDBC, OBIS and GBIF remain declared.)* `NDBCStdmet` (and OBIS, GBIF, CRW) are declared, not built. The first instance with a buoy stream needs NDBC; it
  is built in `atlantis_core` (the P2 rule). M-2 (gridded-only) does not need it.
- WI-20 — *(**P2 gate 2026-10-08:** ruled. The memo `who/coordination/coord_2026_10_08_proteus_to_argus_graduation_wi20.md` proposes C-004 · C-005 · C-009 (7) · C-010 · C-023, with C-015 listed below the bar because its `accepted` field was never set. It supersedes the undelivered 10-03 memo. Delivery is a peer write, `#needs-human`.)* *(M-2a-ii: **C-010 (3)** joins, C-023 → 4; candidates C-004 · C-005 (4) · C-009 (5) · C-010 · C-015 · C-023 (4).)* *(M-1f: the candidates at frequency ≥ 3 are now **C-004 · C-005 (4) · C-009 (5) · C-015 · C-023 (3)**; M-2a-i had C-004 · C-005 · C-009 · C-015.)* **graduation proposed 2026-10-03** (C-009 reached frequency 4 at M-1e, which strengthens the memo) (P1 gate ruling: memo filed, awaiting Argus + Stanley co-ratification at III.aDNA). III learning store: C-004 and C-009 are at frequency 3, graduation candidates for the ADR-003 ceremony at
  III.aDNA. Operator's call, at the P1 gate or after.
- WI-21 — The exemplar is not a conformant instance (no `units.yaml`, `mapping.yaml` or posture pin). Optional: give it the
  first two, so that items 1 and 11 pass; its posture stays the ADR-002 §4 grandfathered exception.
- WI-22 — M-1d-ii memo candidates after the gate:
  - **Rosetta:** `lattice_validate.py`, beyond WI-17. It never loads `additionalProperties`, has no cycle check, and its
    package `__init__` eagerly imports the canvas tools.
  - **lattice-labs / Datasets.aDNA:** 24 of 26 workspace `.dataset.yaml` fail `dataset_yaml_schema.json`, and its
    `location.path` "absolute" is unsuited to public repos.
  - **DDX:** its runspec drops unknown keys rather than rejecting them.
- ~~WI-23~~ **closed 2026-10-07 (M-1f): board v3**; every boundary is embargoed and checked. Original text follows. *(**placed 2026-10-06:** M-1f, its own lane between M-2a-i and M-2a-ii.)* **The label horizon crosses every split boundary** (M-1e III F-6; C-022). Disclosed on README 2b, the v2 page and board
  v2. The fix is carded: `how/backlog/idea_label_horizon_embargo.md` → board v3, its own cause. The operator places it, before
  the P2 gate compares the exemplar with FKNMS.
- ~~WI-24~~ **ruled 2026-10-07 (M-2a-ii):** CRW's *own* `noaacrwsstDaily` carries the OSTIA 1985–2002 terms too (premise below was wrong), so raw SST is dropped; DHW, HotSpot and SSTA from 1985 under CRW's licence, the CoralTemp residual disclosed in the instance's ADR-001. Original text follows. **M-2a-ii licence ruling (OSTIA).** The PacIOOS mirror of CoralTemp v3.1 carries an OSTIA academic-only clause for
  1985–2002, and CRW's own licence text does not. The steward rules on it at the posture ADR: cite CRW-native with the caveat
  noted, or start the era in 2002.
- WI-9 — Memo candidates after the gate (peer vaults read-only): ASOAtlas — greedy `sed` in `run_controls.sh`, untyped-postcondition
  null hole, Python `$` vs trailing newline; Rosetta (`aDNA.aDNA` ADR-062) — the same two as LinkML idiom notes.

## Next steps

1. ~~M-1a~~ ✅ → … → ~~M-1d-ii~~ ✅ → ~~**P1 gate**~~ ✅ 2026-10-03 (conditional GO) → ~~M-1e~~ ✅ 2026-10-03 → ~~M-2a-i~~ ✅ 2026-10-06 → ~~M-1f~~ ✅ 2026-10-07 → ~~M-2a-ii~~ ✅ 2026-10-08 → ~~M-2b~~ ✅ 2026-10-08 → ~~**P2 gate**~~ ✅ 2026-10-08 (conditional GO P3) → **M-2c** (opus) · M-3a → M-3b → **P3 gate** (fable). 2. M-2 FKNMS → **P2 gate**. 3. Memo to Hestia: router row category text → "reference implementation".

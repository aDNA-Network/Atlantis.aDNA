---
type: aar
doc_id: aar_m1b_ii_a_core_eval_explain_board
title: "AAR — M-1b-ii-a atlantis_core eval · explain · board (P1, Operation Tidewatch)"
mission: mission_m1b_ii_a_core_eval_explain_board
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: opus
token_budget_estimated: "~160kT main + fresh-context III reviewer (same size)"
token_budget_actual: "≈215kT main context (≈ +35%, under the +50% trip) + ≈205kT fresh-context III reviewer"
session: session_stanley_20261003_033855_m1b_ii_a_core_eval_explain_board
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [aar, m1b_ii_a, p1, atlantis_core, eval, explain, board, iii, atlantis, tidewatch]
---

# AAR — M-1b-ii-a `atlantis_core` eval · explain · board

**Commits:**

| Commit | Content |
|---|---|
| `e8751e5` | open: split and re-card |
| `b10ec48` | ②③ eval · explain · board · run |
| `bf0b36a` | ④ core run + board v1 |
| `8edfc87` | ⑤ III fixes + v1 regenerated |
| close | bookkeeping |

**Operator rulings (AskUserQuestion):**
1. Split M-1b-ii into ii-a (this mission) and ii-b (site · mapping · archive).
2. The learner swap is logistic regression.
3. After the review: regenerate v1 in place, because it had never left this machine.
4. F-8: disclose now and card the fix (`how/backlog/idea_eval_thresholds_fixed_on_validation.md`).

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| `eval/`, learner as a config field | `eval/{learners,metrics,lead,rolling}.py`: `xgboost` and `logistic` share one interface. Lead time is direction-aware (`test_lead_time_below_event`). Ablations come from vital groups. The sensitivity run goes through `label.make`'s event override |
| **Port equivalence** | On `hab`'s `features.parquet`, the port reproduces **every** `metrics.json` key to 1e-12: 141 trees, 0.8941 / 0.5473, curves, budgets, lead, climatology, surveillance-only, the ablation, 8 rolling folds and sensitivity. This runs in reference mode, which is marked and cannot be emitted. `relabel` and `signal_panel` are also matched against `hab` (10,556 rows / 1,202 positives; 25,011 grid rows) |
| **R7 obligation** | Eras are clipped to ≤ the fold's train year and the moved vitals are rebuilt; only `discharge_anom_t0` moves, and only in the 2016 fold. Eval refuses to run without the refit, and it **verifies the refit per fold**: a no-op callable is refused (F-3) |
| `explain/` | Interventional TreeExplainer over a train-only background, with additivity as a hard check. It reproduces `shap_summary.json` exactly on `hab`'s model. Linear SHAP is checked against brute force per column. Missingness flags are separate artifacts (F-1). Group, tag and net sums come from `features.yaml` |
| What-if is config | Scenarios scale the raw stream and re-derive the vitals through `vitals.build`. They are lever-gated and era-guarded, and scaling a non-lever station is reported. They differ from `hab` at low flow, and the cause is proven (Finding 2) |
| `board/` closed projection | `project(metrics.json)` reproduces the M-1c fixture's evaluation **field for field**. It is validated against the committed JSON Schema and its format checker, and v1 also passes linkml-validate. `assert_green` uses an allowlist plus caps (F-4). Reference-mode headlines and swaps are refused (F-5). WI-8 is started |
| **Board v1** | Emitted by code: 0.8938 / 0.5388, n 1640/127, drops 1481+1800, 141 trees, lead flagged 0.636 → 0.682. `delta_vs` v0 is named, WI-10 is noted, and v0 is untouched |
| **Semantic hash** (WI-7) | `config_hash` is the semantic hash `acfa22c6e4`, with bytes-md5s beside it. The swap carries its own hash, `9b36c3e779` (F-2) |
| Learner swap, T2 | Logistic regression: 0.8726 / 0.5225. The falsifier is not met. The explanation is learner-dependent (Finding 3). Recorded in the thesis register and the board's `learner_swaps` |
| Byte-stable · SO-7 · controls | `config.yaml`, `outputs/*.json` and v0 show an empty `git diff`. Both self-tests are green. ALL WORLDS AGREE (42); the schema is untouched |
| III review via `iii/`, fresh context | PASS-WITH-FINDINGS: 4 major and 4 minor, **8/8 addressed**. F-8 is disclosed and its fix is carded by ruling. Learning store C-008…C-010 |

`what/atlantis_core`: **125 tests**, offline. The port checks skip cleanly without `data/processed/`.

## Worked

- **Port first, then change.** Feeding `hab`'s own vitals through the new eval isolated the port, which reproduces `hab` to
  1e-12. It also made the v0 → v1 delta single-caused: the calendar lag ruled at M-1b-i, and nothing else.
- **The projector test reused M-1c's hand-declared fixture as a reference.** A fixture written for one purpose (the schema
  controls) became the oracle for another (the emitter) at no cost.
- **Every surprise was measured before it was named:**
  - the what-if gap, whose cause is a test;
  - the shap categorical refusal, traced to an xgboost 3.x default;
  - the T2 explanation, measured twice, and the second time correctly.

## Didn't

- **The first T2 reading was wrong** (F-1). Linear SHAP folded each missingness flag into its vital, so gauge absence read as
  the lever. It went onto a board note and the thesis register within the hour. C-003 recurs: a claim is not checked against
  the decomposition that produced it.
- **Three controls could not fail** (F-3, F-4, F-6):
  - a guard that tested whether an argument was passed;
  - a denylist proven by its own examples;
  - an additivity check that holds for any mapping.

  This is the M-1b-i lesson (C-005) one level up: the producer wrote the checks and believed them.
- **The hash boundary was drawn by section name, not by effect** (F-2).
- **A stale hypothesis made it into a commit-adjacent README.** "Jensen" was written before the measurement and fixed
  after it. This was caught before any commit.

## Finding

1. **The port is exact, so `atlantis_core` is now the reference implementation for eval.** Every number on board v1 traces
   to registries, config and three pinned parquets through code that is tested against the original.
2. **`hab`'s what-if edited a mean of logs as a log of the mean.** `discharge_30d` is a 30-day mean of log10(1+q), and
   `hab` scaled it as log10(1 + 0.7·(10^x − 1)).
   - The two agree at high flow (2022–23 to 4 dp) and part at low flow (2017–19: 4e-4; Tampa: 3e-3).
   - Re-deriving from the raw stream is the honest counterfactual.
   - `hab` also scaled Tampa's non-lever gauge silently. The core reports it.
3. **T2: the ranking is learner-invariant; the explanation is not.** Logistic stays within 0.021 AUROC, with the same budget
   precision (0.457 vs 0.463), but it reads the sea differently:
   - by net group attribution, xgboost reads counts first and logistic reads SST and season first;
   - the lever group's share halves;
   - availability flags carry large offsetting attributions.

   A SHAP reading is a reading of one model. This bears on every steward-facing explanation (P4).
4. **Absence is not a value.** Where a stream is structurally absent, its missingness encodes unit identity. Even xgboost
   gives ungauged units 7–19% of discharge attribution. The registry has no way yet to say that a unit has no stream.
   This is a v1 schema candidate.
5. **The R7 obligation was real but immaterial here.** The 2016 fold scores 0.8810 unrefit vs 0.8808 refit. The control
   exists for the instance where it is not immaterial.

## Change

- **A control must be shown to fail before it is trusted** (C-009). Every new guard gets a test that feeds it the defect it
  exists for. Here those are a no-op callable, keyed predictions, and a wrong column map.
- **A join key is defined by effect.** Mutate each field and ask whether a different model or number results (C-010).
- **Decompose before you read.** An explanation claim is checked at the column level before it is summarised (C-008).

## Follow-up

- **M-1b-ii-b** (opus): the site template with all copy parameterised, built from `outputs/atlantis_core/`; `template_mapping_atl.yaml`; archive `src/hab/`.
- **F-8 fix:** `how/backlog/idea_eval_thresholds_fixed_on_validation.md`. It lands as a new board version, before any
  steward-facing budget claim.
- **WI-8 finish:** M-1d's BOARD generator renders `BOARD.md` from `entries/`.
- **v1 schema candidates:**
  - a unit × stream "structurally absent" declaration (Finding 4);
  - lever-ness per station or source, not per vital (Finding 2's Tampa case).
- **Thesis register T2:** a swap on a second instance (M-2), and a collinearity-aware reading before any steward sees an explanation.

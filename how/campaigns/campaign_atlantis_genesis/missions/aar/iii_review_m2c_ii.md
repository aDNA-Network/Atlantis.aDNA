---
type: iii_review
review_of: mission_m2c_ii_fknms_v3_and_swap
commits:
  atlantis: [8255d9b, 492cb61, eb1fda3]          # diff vs ea2154d
  floridakeyscoral: [ff7eda9, 0ad8804, 8bc76f3, 24cc1f4]   # diff vs 88685c7
reviewer: fresh-context III reviewer (Argus Panoptes' method, via iii/ → III.aDNA skill_iii_review v0.6.0)
depth: deep (mission closeout)
created: 2026-10-08
last_edited_by: agent_proteus_iii_reviewer
verdict: PASS-WITH-FINDINGS
counts: {blocker: 0, major: 1, minor: 7, nit: 3}
tags: [iii_review, m2c_ii, fknms, t11, t2, t10, learner_swap, board, register, atlantis, tidewatch]
---

# III review: M-2c-ii (FKNMS v3 at core 0.7.0 · T2's swap · the register re-read of T2, T10 and T11)

**Dispatch.** I loaded the method through `iii/` (`how/federation/iii/CLAUDE.md` → III `skill_iii_review.md` at `v0.6.0`):
- packs: inspect procedures, introspect checks, learning store, vault maintenance;
- the Atlantis local store: 37 corrections, C-001…C-037. The M-2c-i bumps and new rows are already applied.

Modalities: text, code and data.

**Reviewer ≠ producer.** I did not write any of this work. The only file I wrote in either vault is this one. Everything
else I did was read-only: re-computations from the committed outputs and the instance's gitignored scored tables, a plant
against `board_check` on in-memory copies, conform with `--no-selftest`, `mapping --check`, `board --index --check`,
targeted tests and the full suite. I worked in a scratch directory outside both vaults. Neither tree changed, apart from
the producer's untracked session file, which was already there. **Nothing per-patient appears in this report:** it gives
summary statistics only, because Atlantis is public.

## Verdict: PASS-WITH-FINDINGS (0 blocker · 1 major · 7 minor · 3 nit)

The mechanical work holds:
- v3 ≡ v2 on every v2 leaf, and `semantic_hash` holds (recomputed for both configs).
- The commit order is honoured.
- Every register decimal traces to an entry, to the instance's swap file, or to a stated derivation.
- The exemplar trap is a coincidence, not a bug.
- Conform, the mapping check and the board check all pass.

The findings fall into four groups:
- **The T11 verdict is right as worded, but its reasons are not** (F-1). "Falsifier met" holds under the strict reading
  of *does not beat*. Even so, the register leads with the raw nominal-budget precision gap that the core README's own
  limit 5 says is not skill. It reads "the chosen budget" at the volume a 10% *threshold* happened to realise (20.3%),
  not the 10% a steward staffs. It also dismisses the 5% row on a volume objection that the matched-volume number
  printed beside it has already removed. At the realised volume nearest 10%, the model's point estimate is *above*
  climatology's.
- **T2 is read off point estimates**, while the same row set reads T11 with intervals (F-2).
- **Two guards are cited for more than they check** (F-3 and F-4).
- **Several surfaces were not re-cut**: the instance STATE, the limits the v3 entry points to, the T9 count and the GREEN
  headroom (F-5 to F-8).

## What I confirmed independently

| Check | Command / method | Result |
|---|---|---|
| v3 ≡ v2 | leaf walk of `metrics.json` at instance `88685c7` → `24cc1f4` | 2,310 v2 leaves. Only 3 differ: `atlantis_core` (0.6.1 → 0.7.0), `config_bytes_md5` (`dc595f28ff` → `43f06f0022`) and `run_at`. That leaves **2,307/2,307 equal.** 125 new leaves: 29 climatology at budget and 96 interval. `model.json`, `shap_summary` and `whatif` are not in the diff. **Claim (a) holds.** |
| `semantic_hash` | `load_instance` + `semantic_hash` on HEAD and on a `git archive 88685c7` copy | Both are `c07b7c0288`. The swap's own hash `c0d0c29943` equals the entry's. **Claim (b) holds.** |
| Config bytes | `md5` of `git show 0ad8804:atlantis.yaml` and of the working file | Both are `43f06f0022`, equal to the entry. `24cc1f4` does not touch `atlantis.yaml`. |
| Commit order | commit times vs `run_at` | `ff7eda9` 01:56:57Z, `0ad8804` 01:57:23Z, `8bc76f3` 01:57:28Z; `run_at` 01:57:33Z. The output mtimes are 19:01 local, consistent with a 240 s run. **atlantis.yaml was committed before the run** (but see F-4 on what the guard proves). |
| Swap block | `atlantis.yaml` diff vs the exemplar's `learner_swaps` | Byte-equal in content: kind, impute, C grid, max_iter. |
| SO-7 | `git diff --stat 28e5af4 8255d9b` on vitals/label/selftest/grid/config | Empty. Core changes are in `board`, `eval`, `eval/interval`, `eval/metrics` and `site/assemble` only. The receipt's hash is `c07b7c0288`. Not triggered. ✓ |
| Entry landing | `shasum -a 256` of both copies | Atlantis entry = instance entry = memo `entry_sha256` `b3801820…62cb`. The memo records `run_core_commit: 1396ce2`, which is good provenance. |
| Board | `board --index --check` | ✅ up to date. 8 entries; v1 and v2 read "superseded → v3". |
| Conform | `conform --instance FloridaKeysCoral.aDNA --no-selftest` | 12 pass. |
| Mapping | `mapping --check FloridaKeysCoral.aDNA/mapping.yaml` | ✅ clean |
| Schema | `board.validate` on both live entries | Valid under HEAD's atl_v0 0.8.0. See F-11 on the other 0.8.0. |
| Register decimals (C-032) | extracted every decimal from `eb1fda3`'s added text and looked each up in both entries and the swap file | All trace back. The SHAP values (1.79 / 0.21 / 7.66 / 4.13 / 39.60) are roundings of the entry's 1.78982 / 0.20767 / 7.65755 / 4.13111 / 39.59937. Ratios 0.116 and 0.539 re-derive (0.1160, 0.5395). Δ +0.0095 is labelled derived. The swap's matched-volume −0.0008 [−0.0729, +0.0785] is from `learner_swap_logistic.json` (−0.00077 [−0.07285, +0.07855]) and is disclosed as instance-local. **Every number is attributed to the right instance and learner.** |
| **The exemplar trap**: GBM and logistic both 0.5267 / 0.5433 / 0.0799 at 10% | `outputs/atlantis_core_v{1..4}` and a refit | **Coincidence, not a bug.** The thresholds differ (0.2813 vs 0.2427), and the 5% and 20% rows differ (0.6567 vs 0.6154; 0.3143 vs 0.3344). v1 had both at 164 alerts with different precision, v2 had 133 vs 130, v3 and v4 have 131/69 both. My logistic refit on train ∪ val reproduces AUROC to 2e-4 (0.87258 vs 0.87277; the gap is the embargoed rows). It flags 129 rows (68 TP), and only **101 of them overlap the GBM's 131**. These are two different flag sets that happen to land on the same counts. The register's T11 exemplar 0.5267 is the GBM's, which is correct. |
| Page tokens | resolved every `{{path|fmt}}` in `site_copy.yaml` against the built page's `site-data` | Every metric token resolves; the unresolved ones are `fig:` tokens only. The formats render (`toFixed(3)`, `pct1` → 62.3% / 56.8%). The tokens say what they claim to. **Claim (g) holds.** |
| Core change `8255d9b` | read + `tests/test_site.py` | The keep-list key is correct and the plant-first test is valid: `resolve` raises without the key. 70 passed in `test_site` + `test_board_index`. |
| Full suite at HEAD `eb1fda3` | `.venv/bin/python -m pytest -q` | **743 passed** (279 s) at `eb1fda3`, the producer's last commit. That is 742 at `ea2154d` plus `8255d9b`'s test. The live-entry tests still pass after `492cb61` landed the entry (C-035 checked at the closing commit, so far). The AAR must re-state this count at its own closing commit. |
| GREEN count | numeric leaves per entry | FKNMS v3 582, exemplar v4 570 (cap 600). See F-7. |

**Re-computations behind F-1 and F-2.** All are summary statistics only. All use the committed `test_scored` and
`all_scored` tables and the core's own `climatology_scores` and `precision_at_count`. My climatology AUROC reproduces
the entry's 0.9194.

| Matched alert volume (fraction of test) | Model precision | Climatology expected precision | Δ | Reviewer interval (nominal 95%; volume as a fraction of each draw — not the core's threshold-count design) |
|---|---|---|---|---|
| 0.0500 | 0.789 | 0.657 | +0.132 | [+0.017, +0.262] |
| **0.0881** (the model at nominal 5%) | 0.742 | 0.659 | **+0.0839** (= entry) | [+0.008, +0.166]; **the core's: [−0.0118, +0.1926]** |
| **0.1000** (the budget a programme staffs) | 0.711 | 0.652 | **+0.059** | [−0.014, +0.151] |
| 0.1500 | 0.634 | 0.635 | −0.001 | [−0.096, +0.088] |
| **0.2034** (the model at nominal 10%) | 0.568 | 0.590 | **−0.0221** (= entry) | [−0.114, +0.041]; **the core's: [−0.0906, +0.067]** |
| 0.2861 (the model at nominal 20%) | 0.483 | 0.485 | −0.0019 (= entry) | [−0.038, +0.022] |

My two reproduced point estimates equal the entry's, which validates the method. The intervals are mine, from a
different draw design, and are approximate.

**T2, the same instrument, logistic − GBM on FKNMS.** This is a refit of the logistic at C = 10 on train ∪ val. Its test
AUROC is 0.9464 against the entry's 0.9465, so it is approximate.
- **AUROC:** Δ +0.0093 [−0.0056, +0.0253]. 6 of 7 seasons favour the logistic (sign p 0.0625).
- **AUPRC:** Δ +0.0455 [−0.0124, +0.1114]. 6 of 7 seasons favour the logistic.

## Findings

| ID | Sev | Pattern | Finding · evidence | Fix |
|---|---|---|---|---|
| F-1 | **major** | **C-034** (recurrence) · **C-032** | **T11 on FKNMS: the verdict "falsifier met" is defensible as worded, but the reasons given for it are partly wrong.** The register (row T11, the Reading bullet and the `eb1fda3` headline) argues: *"at the chosen budget the model does not beat its climatology: the point estimate is below it, at matched volume the two cannot be told apart, and no threshold-free reading separates them."* There are five problems with that argument. **(a)** It leads with the raw precision gap at the nominal 10% (0.6228 > 0.5677), taken at unequal realised volumes (0.1791 vs 0.2034). Core README limit 5 says exactly this: *"a precision gap at a shared nominal budget is not by itself skill"*. **(b) "The chosen budget" has two readings on FKNMS, and the sign of the point estimate depends on which one is used.** As a *threshold rule* (a 10% quantile fixed on 2014–18), it realised 20.3%, and matched-volume ΔP is −0.0221 [−0.0906, +0.067]. As the *volume a steward staffs* (10%, the page's own "a programme that staffed for one alert in ten would have received two"), the nearest measured point is the 5% row at 8.81% realised: matched-volume ΔP **+0.0839** [−0.0118, +0.1926]. My diagnostic at exactly 10% gives +0.059, and it reaches 0 only at ≥ 15% volume. **(c)** The 5% row is set aside because "climatology's week-of-year ties cannot reach 5%". That objection applies to the raw ΔP. The matched-volume ΔP printed in the same sentence removes it, and still favours the model. **(d)** The falsifier's operating point has no seasons-favouring or sign-test companion. The only one cited (3 of 7, p 0.7734) is AUROC's, which is threshold-free, so C-036's remedy is applied off the falsifier's operating point. **(e) Asymmetry.** Both verdicts rest on the same nominal interval: the exemplar is "supported" because it excludes 0, and FKNMS is "falsified" because it spans 0. Under-coverage (C-036) weakens only the first. The exemplar's "3 of 3 (p 0.125)" is the sign test's *floor* at 3 scorable seasons, the strongest evidence 3 seasons can give, and the register should say that. **What survives:** under *either* reading of the budget, the model is **not shown to beat** climatology on FKNMS, and that is what the falsifier's words require. "Falsified" holds in that sense, but "climatology is the more precise" does not. The same applies to the page's corrected manager note: *"at a budget a programme could staff the week-of-year onset rate alone alerted as precisely as the model"*. The budget a programme staffs is the low-volume end, where the model's point estimate leads. | Restate T11's FKNMS reading in this order. **(1)** Lead with matched volume, and give both readings of the budget: *"not shown to beat climatology at the chosen budget under either reading: at the nominal-10% threshold (realised 20.3%) matched-volume ΔP −0.0221 [−0.0906, +0.067]; at the realised volume nearest 10% (nominal 5%, 8.81%) +0.0839 [−0.0118, +0.1926]; both nominal, both span 0."* **(2)** Call the status "falsified as worded (no demonstrated advantage)", not "climatology is better". **(3)** Mark the exemplar's sign p as the floor at B_scored = 3. **(4)** Reword the page sentence the same way: *"not distinguished from the calendar at any budget; the model's point estimate leads at low alert volume and vanishes by 15%"*, by token. **(5)** Core: carry per-season budget deltas and a seasons-favouring count for each budget (summary-only). Add a README limit 5 bullet: under a base-rate shift, the matched volume at the model's realised count is not the steward's chosen volume. |
| F-2 | minor | new **C-038** (kin to C-036) | **T2 reads "better" off point estimates, while the same commit reads T11 with intervals.** The register says: *"Here the simpler learner is the better one on every threshold-free number: the GBM does not earn its complexity on FKNMS"*, and the Reading bullet says *"On FKNMS the logistic beats the GBM"*. No interval is given. With the same season-block instrument (my refit, approximate), logistic − GBM is ΔAUROC +0.0093 [−0.0056, +0.0253] and ΔAUPRC +0.0455 [−0.0124, +0.1114], 6 of 7 seasons each (p 0.0625). That is more consistent than model − climatology (3 of 7), but not distinguished at a nominal 95%. The same document calls a −0.0221 [−0.09, +0.07] "cannot be told apart". C = 10 is also the grid's edge, which is disclosed. "The GBM does not earn its complexity" is fair, because it is not shown better. "The logistic is better" is not shown. | Say *"ahead on every threshold-free point estimate (6 of 7 seasons); not distinguished at a nominal level"*. Better, have core emit a paired season-block interval for each swap against the headline (`learner_swaps[].paired_interval_vs_headline`, summary-only), so T2 is read with the instrument T11 uses. Rewrite the Reading bullet to match. |
| F-3 | minor | **C-037** (recurrence) | **The page's "field for field" check does not reach the numbers `8255d9b` lets the page cite.** The page note says: *"the build re-projects the run and checks it against the entry, field for field"*, and the core README §"What the build checks" says the same. `site.assemble.board_check` compares `project(metrics)` with the entry's **`evaluation`** block only. The new tokens (`budgets.10pct.matched_volume_precision.*`, `auroc.seasons_favouring_model`, `seasons_scored`) live in `evaluation_extras.paired_interval`, which nothing compares. **Plant:** an in-memory copy of `metrics.json` with matched-volume estimate +0.05, lower +0.01 and seasons favouring 7 passed `board_check` (fields_checked 25). The page's swap row (`t_compare`) is unchecked in the same way; that predates this mission. Low risk here, because one run produced both, but the claim is wider than the check. | Have `board_check` also compare the extras the page draws from: `paired_interval` (the `evaluation_extras` projection) and `learner_swaps`, rounded through the board's own `_r`. Add the plant above as a named test. Until then, narrow the README and page wording to "every `evaluation` field". |
| F-4 | minor | new **C-039** | **"Commit atlantis.yaml before the run; core refuses stale config bytes" cites a guard for a property it does not check.** The card, the `0ad8804` message and the memo all rest on `board.assert_config_bytes`. That function compares the run's md5 with the **working-tree** file at emit time. A run from **uncommitted** bytes that are later committed unchanged, or never committed, passes it: the M-2b F-6 defect it was written for. Here the order really was honoured (run_at is 10 s after `0ad8804`, and md5 = the `0ad8804` blob, both verified), and Atlantis's landing re-check compared committed bytes by hand. The guarantee is manual. | Have `emit` (or `conform` item 9) compare `config_bytes_md5` with `git show HEAD:<file>`, failing closed when git errors (C-021). Or script the landing check that compared committed bytes. Until then, say "checked at landing", not "core refuses". |
| F-5 | minor | **C-032** (recurrence) | **The instance's STATE still carries the overstatement the page correction removed.** `FloridaKeysCoral.aDNA/STATE.md` (last touched `88685c7`) names entry **v2**, says *"the model's margin over climatology is mostly AUPRC"*, and lists "Board entry → Atlantis … Then the P2 gate" as open. `24cc1f4` corrected the page's "beats every comparator" sentence but not this one. The page's Reproduce block still reads `--version 1`. | Re-cut STATE at close: v3, T11's FKNMS reading (as fixed in F-1), the swap, and the closed items. Correct the reproduce command (`--version 3 --vs 2026-10-08_florida_keys_coral_v2`, or token-ised). |
| F-6 | minor | — (SO-9; F-6 of M-2c-i, recurring at the instance) | **v3's `limitations_ref` does not reach the new quantities' limits.** FKNMS v3 points only to `site/florida_keys_coral_v1.html#limits`. That section has eight bullets and none covers climatology ties, unequal realised volumes, the nominal level at 7 blocks, or January-start season blocks. These are the four items core README limit 5 added at M-2c-i. The exemplar's ref includes the core README, and FKNMS's does not. The nominal-level sentence sits in §6 prose, not under the anchor the board cites. *(Context, which predates this mission: the anchor resolves only inside a local-only instance, so a reader of the public board cannot follow it.)* | Add a limits bullet that cites the interval by token, its nominal level and its January blocks, or append `what/atlantis_core/README.md#known-limits-of-eval-and-explain-so-9` to the ref, as the exemplar does. |
| F-7 | minor | — | **The GREEN cap has no headroom for the next version.** FKNMS v3 has 582 numeric leaves and exemplar v4 has 570 (cap 600). Re-emitting either stem at the *same* core with `--vs` turns the `was: null` echoes numeric: +17 for FKNMS gives **599**, and +25 for the exemplar gives **595**. Then one more field, a second swap, an 8th test season or F-1/F-2's per-season budget deltas makes `emit` refuse. Most of that growth is `delta_vs` restating numbers already on the board (168 of FKNMS's 582). | Decide before M-3. Options: count `delta_vs` echoes once (they duplicate numbers already on the board), or raise the cap with a stated rationale. The cap guards per-patient leakage, which summary echoes do not carry. Record the decision with a control. |
| F-8 | minor | **C-032**-adjacent | **The register's "every other row stands as ruled" skips T9.** `8255d9b` is an Atlantis code change that the second instance forced: its page could not cite the interval without it. Under M-2c-i's counting rule (one per instance-observable change, at the surface where it is met), it counts toward T9's *strong* form. The pin move is separate upkeep (ruling 2). The AAR is due to count it, but the register's roll-up already says T9 is unchanged. | Count `8255d9b` on its own line in the AAR. Add a T9 note: *"+1 at M-2c-ii (site-data keep-list), forced by the FKNMS page"*. |
| F-9 | nit | — | **Core 0.7.0 now names two site-data contracts** (`1396ce2` without the interval key, `8255d9b` with it), so the entry's `method_version` "atlantis_core 0.7.0" does not identify the page's core. This failure is loud: a build at `1396ce2` refuses the unresolved token. The memo's `run_core_commit` and the pin carry the commit. It follows the `671808b` precedent. | Either adopt a patch bump for page-data contract changes (0.7.1), or put the core commit into the page's data and the Reproduce table. |
| F-10 | nit | C-030-adjacent | Four reading claims say more than they measure. **(a)** *"T11 holds where the calendar does not know the event … and fails where it does"* generalises from two instances. **(b)** *"the board showed this, not a reviewer"*: M-2c-i's F-3 forecast FKNMS's 0.20 realised volume as the risk. **(c)** The page's *"whatever the model adds is in ranking which zones and weeks inside a hot season"* is not measured: within-season ΔAUROC favours the model in 3 of 7 seasons, and part of the pooled +0.0176 comes from ranking between years. **(d)** Core README limit 5 says *"with 4 or 5 seasons that test cannot go below 1/16 or 1/32"*, but the exemplar scores 3 seasons, so the floor is 1/8, which it hit. | (a) Phrase it as a hypothesis for P4, to be tested with the calendar + signal comparator. (b) Drop the clause. (c) Say "would be", or measure within-week zone ranking. (d) Correct to "3 to 5 scorable seasons: 1/8 to 1/32". |
| F-11 | nit | — | **atl_v0 "0.8.0" names two schemas in history.** `1396ce2` added `season_start_month` to the closed `AtlPairedInterval` without a version bump. Both live entries validate under HEAD's 0.8.0, and both are **rejected** by `0da7414`'s 0.8.0 (`season_start_month` was unexpected; verified with `board.validate` against each schema). `mapping` compares version strings only. This is harmless in practice: neither commit is on `origin/main` (still `76bb143`), and FKNMS pinned after `1396ce2`. | At close, record in CHANGELOG that 0.8.0 was amended before publication, or bump to 0.8.1 before the push. |

## Acceptance criteria vs evidence

**Met, and confirmed by me:**
- **Steward-side commits:**
  - `learner_swaps` matches the exemplar's block, and the hash holds.
  - The mapping pin moved to 0.8.0 and is counted as upkeep.
  - `interval_season_start_month: 1` is ruled and disclosed.
  - The pin moved to the M-2c-i commit `1396ce2`.
  - `atlantis.yaml` was committed before the run (the order held; see F-4 on the guard).
- **The run and its outputs:**
  - v3 at core 0.7.0 with the swap, then conform.
  - The v3 entry emitted with `--vs` v2.
  - The memo in the inbox.
  - The landing re-check (sha256 and bytes verified) and the dated commit `492cb61`.
  - v2 stays on the board, superseded.
- **SO-7:** correctly not triggered.
- **The register, partly met:**
  - Every number comes from an entry or an output (C-032 ✓).
  - T11 is read at its terms on both instances, with realised rates, Δ precision, matched volume and the nominal level. **However,** the reading's reasons need F-1.
  - T2's swap on the second instance (F-2 on the wording).
  - T10 with two entries (the card says "0.8.0 entries"; the register says "0.7.0", meaning core 0.7.0 under atl_v0 0.8.0; consistent).

**Not yet reviewable:**
- The count of Atlantis changes (F-8 names one item it must include).
- The AAR.
- The SITREP and actual token budget.
- STATE and CHANGELOG at close.

## Introspect

- **2a confidence gradient.** The machine-readable side is now honest: `level_is_nominal`, seasons favouring the model,
  the sign test and matched volume. The prose verdicts are where confidence moves. "Falsified" and "the logistic is
  better" are stated more firmly than the intervals beside them allow, in *opposite* directions (F-1, F-2).
- **2c structural completeness.** The board is now the strongest artifact. The surfaces around it lag: the instance STATE
  (F-5), the limits anchor (F-6), the page-check coverage (F-3) and the T9 roll-up (F-8). The pattern is that a re-run
  updates what the emitter writes, and the hand-maintained surfaces drift.
- **2d meta-pattern.** Two guards are cited beyond their reach. The page's field-for-field check stops at `evaluation`
  (F-3). The stale-bytes check sees the working tree, not the commit (F-4). This is the C-037 family again, now at the
  documentation layer: the claim names a property that the guard nearby does not test.
- **2f denominator.** FKNMS's "budget" carries three denominators that the register sometimes collapses: the nominal
  rate, the model's realised volume, and climatology's realised volume. Matched volume fixes one of them, at the model's
  volume, which under a base-rate shift is not the steward's (F-1b).
- **2g corrections matched.** C-032, C-034 and C-037 recur. **C-034** is the one that matters: the mission existed to put
  T11 at its falsifier's operating point. It got there on the numbers, and slipped off it in the prose (which volume
  counts as "the chosen budget").

## ACCUMULATE proposals (the producer applies them; I did not write the store)

**Bumps:**
- **C-034** 2 → 3 (F-1)
- **C-032** 2 → 3 (F-5; F-1 and F-8 are adjacent)
- **C-037** 1 → 2 (F-3)

**Graduation candidates (frequency ≥ 3; the acceptance rate is the operator's call):**
- C-034 and C-032 now qualify.
- C-009 and C-010 remain candidates.

**New rows:**

```json
{"id": "C-038", "trap": "confidence", "pattern": "asymmetric_uncertainty_standard", "description": "One document reads one comparison through an interval ('cannot be told apart') and a sibling comparison off point estimates ('X is better'), with the same instrument available for both. The verdicts then differ in rigour, not in evidence.", "example": "M-2c-ii register: T11's model − climatology ΔP −0.0221 [−0.09, +0.07] is read as 'cannot be told apart', while T2's logistic − GBM Δ AUROC +0.0095 (no interval; reviewer's season-block approximation [−0.006, +0.025], 6 of 7 seasons) is read as 'the simpler learner is the better one'.", "source_review": "m2c_ii_fknms_v3_and_swap_iii_review_20261008", "source_finding": "F-2", "frequency": 1}
{"id": "C-039", "trap": "boundary", "pattern": "guard_cited_for_a_stronger_property", "description": "A procedure, page or commit message justifies a property by naming a guard, but the guard checks a weaker or neighbouring property. The documented safety outruns the code, and a defect inside the gap passes the guard and the citation alike. Kin to C-037 (the guard reads a sibling of the consumed input) and C-023 (the label, not the act).", "example": "M-2c-ii: 'commit atlantis.yaml before the run; core refuses stale config bytes', where assert_config_bytes compares the run md5 to the working tree at emit time, not to a commit. 'The build checks the page against the entry field for field', where board_check compares the `evaluation` block only, while the page cites evaluation_extras.paired_interval (a plant passes).", "source_review": "m2c_ii_fknms_v3_and_swap_iii_review_20261008", "source_finding": "F-4 (and F-3)", "frequency": 1}
```

## Reviewer cost

About 110–130 kT of reviewer context. Compute: one full-suite run, conform (receipt mode), two logistic refits, two
season-block re-computations (2,000 draws each), and a set of read-only leaf walks and validations.

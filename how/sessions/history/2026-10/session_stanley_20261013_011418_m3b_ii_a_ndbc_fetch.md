---
type: session
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
tags: [session, m3b, m3b_ii, m3b_ii_a, p3, ndbc, fetcher, fknms, atlantis, tidewatch]
session_id: session_stanley_20261013_011418_m3b_ii_a_ndbc_fetch
user: stanley
started: 2026-10-13T01:14:18Z
completed: 2026-10-12
status: completed
executor_tier: opus
mission: m3b_ii_a
campaign: campaign_atlantis_genesis
intent: "M-3b-ii-a: NDBCStdmet built (core 0.10.0, WI-19) + weekly_count_lt grammar op · reef-light wind stream fetched into FloridaKeysCoral (Keys-wide index) · conform fetched · III. Plan: ~/.claude/plans/please-read-the-claude-md-fuzzy-summit.md"
---

## Activity Log

- open — leases probed: Atlantis and FKNMS `how/sessions/active/` empty (only .gitkeep). HEAD `884a800`, clean.
  Probes (read-only GETs, nothing cached): NDBC stdmet yearly coverage MLRF1 1987–2019 · SMKF1 1988–2015, 2018–25 ·
  LONF1 1992–2025 · SANF1 1991–2025; three file formats; sentinels 99/999. Tortugas zones 110–125 km from any station
  live in 2020–25.
  Rulings (AskUserQuestion, operator/steward, 2026-10-12): **(1) split M-3b-ii** into ii-a (NDBCStdmet + fetch +
  conform + III) and ii-b (vital · val scan · run · SHAP · memo · entry · III) · **(2) station map = Keys-wide synoptic
  index** (daily mean over reporting reef lights, all 21 zones; reporting set recorded) · **(3) calm threshold scanned on
  val** (c ∈ {2,3,4,5,6} m/s, chosen on val log-loss from the train fit, test once; full scan a GREEN table; raw
  anemometer height a recorded limit; executed in ii-b).
- `9bbe34f` the M-3b-ii split: parent `split`; ii-a (active) + ii-b (planned) cards; roster; charter.
- `b5629dc` **core 0.10.0**: `NDBCStdmet` BUILT (three header forms, sentinels, ≥ min_hours daily means, 404 = absent,
  no-year station refused, basis refusal, mapped stations must be fetched) + `weekly_count_lt` (unit-level, empty week
  NaN). 16 offline tests; plant-first ×11 (two op plants were blind at first — fixed). **Suite 849 passed at `b5629dc`**
  (394 s). Controls 126, ALL WORLDS AGREE (linkml scratch venv of session c2646ef8).
- Steward rulings 4–6 (AskUserQuestion): **NDBC licence = public, ADR-001 addendum ratified** (NOAA/NWS public-domain
  terms read 2026-10-12) · **min_hours 18** · **years 1987–2025**.
- FKNMS: stream declared (Keys-wide map), mapping pin → 0.9.0, federation pin; conform declared; self-test green
  (receipt `81bca06518`, C7 skipped as ruled). First network fetch **failed on a live file** (LONF1 2000: 17-column header,
  16/17-field rows) → `e8b79c0` parser fix (+1 test) → trial fetch 156 requests, then re-reduced `--offline` under the
  committed fix: identical bytes `b2f93211…`, 42,747 station-days.
- Sanity read (GREEN): lights agree r 0.87–0.95; LONF1 ≈ 1 m/s calmer; **SMKF1 −1 m/s after its 2016–17 gap; calm share
  rises with the base rate** → an ii-b opening obligation (era confounding).
- conform fetched: item 9 failed v1–v3 against the new hash → `5312f52` item 9 holds only the newest entry (the board's
  derived supersession) to the current hash; plant-checked. FKNMS item 9 now outstanding by construction (v3 = old config).
- FKNMS `51c7203` (stream, ADR addendum, pins, parquet + summary, STATE). gitleaks clean.
- **Budget:** ≈ 290 kT on the session counter (planning included) vs ≈ 150 carded; the +50% line (≈ 225 kT) was crossed
  during the live-fetch fixes and is reported at the first clean point (both vaults committed), ≈ 65 kT past it (C-042).
- **Ruling 7 (operator, AskUserQuestion, at the SITREP ≈ 290 kT): re-card ii-a main ≈ 150 → ≈ 420 kT and continue to III in this sitting.**
- `590f70b` site test pinned to the entry's view of the instance (it read the live FKNMS; its result depended on instance state, C-035). **Suite 851 passed at `590f70b`** (FKNMS at `51c7203`). Register touch-check (C-033): T9 +1 (conform item 9), a T7 caution for ii-b. ii-b card: obligations 6–8 (station drift · item 9 outstanding · test pattern). III launched (fresh context, via `iii/`).
- III (fresh context, via `iii/`, ≈ 300 kT metered): **PASS-WITH-FINDINGS 0/1/8/3**. Rulings 8–10 (AskUserQuestion, operator): **(8) F-1 → QC flags in the fetcher now** (no value deleted; ii-b rules the mask) · **(9) code minors + card** · **(10) accept ACCUMULATE** (C-045…C-048 + ten recurrences).
- `9084905` **core 0.10.1**, the III fixes: QC flag columns (F-1) · conflicting duplicates dropped (F-2) · absences
  confirmed + sidecars, empty 200 fails, current year refused, raw cache pinned and re-hashed (F-3) · plant reaches C1
  (F-4) · site test on the newest entry, vitals filtered, metrics fail by name (F-5) · re-reduction labelled (F-6) · four
  forms + tests (F-7) · cadence (F-8) · conform supersession documented + agreement test (F-11) · F-12 a–e. Plant-first:
  17 new guards red when off (4 blind at first, tightened).
- FKNMS `fa0beed`: re-fetched under 0.10.1 (36 requests: the 18 absences re-confirmed); 42,742 station-days `9abb791d`;
  LONF1 2020 → 99 `qc_low_ratio` days; SMKF1 2020 → 659 conflicting timestamps dropped; STATE rewritten (one
  denominator; paired differences; calm-share table unmasked vs masked). verify ✅ ×4; conform fetched 11 + item 9
  outstanding by construction; gitleaks clean.
- ACCUMULATE (ruling 10): ten recurrences applied; C-045…C-048 accepted; C-042 · C-030 graduation candidates.
- Close: ii-a card completed (budget line carries ruling 7; criterion re-worded, F-9) · ii-b card obligation 6 rewritten
  (QC mask + offsets first) · register touch-check after the fixes · AAR · roster · charter · STATE · CHANGELOG v0.18.0.
- **Budget (final):** main ≈ 400 kT (re-card ≈ 420) · III reviewer ≈ 300 kT metered.
- **Suite 863 passed at `9084905`** (279 s; FKNMS at `fa0beed`).

## SITREP

- **Completed:** M-3b-ii-a — core 0.10.1 (`NDBCStdmet` built with QC flags · `weekly_count_lt` · conform item 9
  supersession) · the reef-light wind fetched into FKNMS as a Keys-wide index · III 0/1/8/3, all dispositioned.
- **In progress:** none.
- **Next up:** M-3b-ii-b (opus): rule the QC mask and station offsets first, then the wind vitals, the val scan, the run
  (v4), SHAP, the write-up either way.
- **Blockers (`#needs-human`):** the push (gitleaks first) · the P3-gate items in STATE.
- **Files touched:** Atlantis `what/atlantis_core/` (fetch/ndbc · base · provenance · __main__ · vitals/grammar · ops ·
  conform · tests ×5 · README · version) · two skills · cards · roster · charter · register · AAR · III review + store ·
  STATE · CHANGELOG. FKNMS `atlantis.yaml` · `streams.yaml` · `mapping.yaml` · federation pin · ADR-001 · the wind parquet +
  summary · STATE.
- **Next Session Prompt:** STATE § ⏭ QUEUED (M-3b-ii-b, opus).

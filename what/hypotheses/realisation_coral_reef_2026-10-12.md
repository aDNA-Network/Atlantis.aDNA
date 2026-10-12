---
type: memo
doc_id: realisation_coral_reef_2026_10_12
title: "The coral_reef ledger, ranked for realisation in FloridaKeysCoral (M-3b-i hand-off → M-3b-ii)"
status: draft   # the pick is the operator's (skill step 7); recorded below once ruled
created: 2026-10-12
updated: 2026-10-12
last_edited_by: agent_proteus
mission: mission_m3b_i_ledger_and_skill
skill: how/skills/skill_feature_hypothesis_mining.md (step 7)
data_tier: GREEN   # metadata and summary numbers only; no observation, label or prediction
tags: [hypotheses, realisation, coral_reef, fknms, t7, t8, m3b_i, handoff]
---

# The coral_reef ledger, ranked for realisation in FloridaKeysCoral

**The instance's event:** CRW DHW ≥ 4 °C-weeks (Alert Level 1) onset within 8 weeks, per FKNMS zone (21 zones × ISO
weeks). **Its current vitals** are nine starter vitals from three CRW streams (DHW, HotSpot, SSTA) at lags 0–4 weeks.
HotSpot at t0 carries most of the attribution (mean |SHAP| 1.56 of 2.45 on the v2 run). There is no calendar vital and no
vital with a memory longer than a month. **Board v3** (the comparison of record, C-031/C-034): test 2019–25 at base rate
15.0%. A realised driver is read against v3 **at that base rate and at v3's budgets**, never as a cross-base-rate AUPRC
delta.

**Ledger:** 26 rows, **14 `reviewed`** (each bound to the content its reader read by `reviewed_sha256`) and 12 `draft`. 32 were extracted from 28 works (corpus: 380 works, 21 queries); the
faithfulness reader confirmed 15, questioned 17, and 6 were withdrawn (§4). `LEDGER.md` is the table. Reviewed rows are
marked ★. *(Amended after the III review, `missions/aar/iii_review_m3b_i.md`: amo_002 demoted, F-7; the realisability
class made a closed, counted field, F-4; the strength column read on event-matched rows only, F-6.)*

## 1. What the ledger says, by driver family

| Family | Rows (★ reviewed) | Regions | What the rows claim | Bears on DHW **onset**? |
|---|---|---|---|---|
| Wind (calm, doldrums, a 4 m/s threshold) | wind_001★ · 003★ · 004 · 005★ · 006★ | GBR · Persian Gulf · Iriomote · global · Brazil | less wind, more heat or bleaching; a 4 m/s critical threshold (003★, from a model with observations) | **yes**: 003★ (sea-bottom temperature) and 006★ (marine heatwaves) are heat claims |
| Tropical cyclones | hurricane_001 · 002★ · cyclone_power_001 | Florida Reef Tract + USVI · Caribbean · global | cool wakes reduce CRW thermal stress (002★); cyclone *power* goes with higher bleaching *severity*, a different event, so no contradiction | **yes**: 002★ is on CRW thermal stress itself, Caribbean, 2005 and 2010 |
| Cloud / light | cloud_001 · 002★ · turbidity_001★ | French Polynesia · GBR · global | less cloud under El Niño weather → bleaching (002★); cloud and turbidity moderate bleaching given heat | partly: 002★ is a heating pathway; the other two are response claims (T12) |
| Air–sea flux | heat_flux_001★ | Ningaloo | net heat flux raised reef temperature above offshore; offshore DHW understated 3 vs 11 °C-weeks | yes, and a caution that 5 km DHW can understate reef-scale stress |
| Climate modes | enso_002 · enso_003 · amo_002 (demoted: its AMO link is the paper's context, F-7) | Caribbean · Japan · Yucatán | Caribbean heatwaves are *suggested* to relate to El Niño; Japan's DHW built under La Niña; AWP SST varies with the AMO | weakly: monthly indices, near-constant within a season |
| Internal waves | internal_waves_001 · 002★ · 003★ | **Florida Keys** ×2 · Andaman | cool subsurface incursions | **no**: subsurface. CRW's surface DHW cannot see them (`unrealisable`) |
| Heat history and the trend | preconditioning_001 · warming_trend_001★ · sst_variability_001 · florida_current_001 | GBR · **Keys** ×3 | a protective pre-pulse (response); warming → annual bleaching by 2020–34; moderate variability protects cover; fewer eddies → winter warming (hypothesized) | no reviewed row is about DHW onset |
| Forecast / the event itself | forecast_sst_001★ · dhw_001★ · warm_pool_001 | global · Caribbean | the CRW 4-month Outlook (a **comparator**); DHW predicts bleaching (supports the event definition); proximity to the 2005 warm pool | not as drivers |

**T8 as worded**, counted by code (`realisability`, a closed field; `LEDGER.md` prints the counts):

| Realisability | Rows | Which (★ reviewed) |
|---|---|---|
| `existing_stream` — from FKNMS's own streams | **3** | preconditioning · sst_variability · warming_trend★ |
| `declared_fetcher` — NDBC, declared not built | **6** | wind_001★ · 003★ · 004 · 005★ · 006★ · temperature_variability★ |
| `new_stream` — an index, a track, an ERDDAP field | **11** | |
| `unrealisable` on this grid | **6** | internal waves ×3 · warm_pool · dhw_001★ (the event's own definition, skill step 4) · heat_flux_001★ (the paper's effect is a reef-minus-offshore difference CRW cannot carry) |

**The falsifier, read for the P3 gate to rule (F-5):** *"The extraction target yields rows no fetcher can realise"*.
Six of 26 rows are exactly such rows. Read as *"mostly unrealisable"*, it is not met (20 of 26 are realisable). Read
as *"any"*, it is met. The register does not choose; the gate does.

**What the count does not show.** By the paper's own outcome, **11 rows are about heat** and **15 are about bleaching
or cover given heat**. That is context for T12's question (one event, one model), not evidence on its claim (F-5). **No reviewed row about heat onset is realisable from FKNMS's existing streams.** The derivable
rows are a response claim, the event definition, the era, or a cover claim. The cheapest honest test of the literature
on this event therefore needs **one new stream**. The cheap derivable candidate this memo first ranked second (a
preceding-winter SSTA) rested on a row the reader showed the text does not carry; it is withdrawn (§4).

## 2. Ranked candidates for M-3b-ii

Strength is read on **reviewed rows whose event matches FKNMS's** (heat, not bleaching response), with their regions
(III F-6). Build cost is the Atlantis and instance work before a model can train.

| Rank | Candidate | Event-matched reviewed rows | Other rows | Realisability on FKNMS | Build cost | Lever? (T7) |
|---|---|---|---|---|---|---|
| **1 — ruled** | **Reef-light wind** (weekly mean wind; days below a calm threshold, scanned — the 4 m/s figure is one Persian Gulf model's, a **regional transfer**, not a fixed constant) | **2**: wind_003★ (Persian Gulf, a model of sea-*bottom* temperature) · wind_006★ (one Brazilian season, heatwaves) | wind_001★ · 005★ · temperature_variability★ (bleaching given heat) · wind_004 (an anoxic event) | 4 stations (MLRF1 · SMKF1 · LONF1 · SANF1) → 21 zones, a steward ruling; C-MAN from 1987–88, with gaps | **highest**: `NDBCStdmet` built in `atlantis_core` (WI-19, a template change), fetch under FKNMS's posture, self-test | **no**: proxy |
| 2 | **Tropical-cyclone cool wakes** (HURDAT2) | **1**: hurricane_002★ — **on CRW thermal stress itself, Caribbean**, the closest event and region on the list | hurricane_001 (the Keys, draft) · cyclone_power (severity, a different event) | sparse weekly indicator per zone | moderate: a new track fetcher | no |
| 3 | Cloud / insolation (ERDDAP) | 1: cloud_002★ (GBR, a heating pathway) | cloud_001 · turbidity★ (response) | gridded; a generic ERDDAP polygon reducer is likely a template change | moderate | no |
| 4 | ENSO index (Niño 3.4) | 0 | enso_002 · enso_003 (drafts, regional) | broadcast, monthly | low–moderate | no |

**The trade-off as put to the operator:** rank 1 has more rows, farther away, at the highest cost; rank 2 has one row,
closest in event and region, more cheaply. **Ruled 2026-10-12: rank 1, reef-light wind** (§5).

**Excluded at extraction (the skill's rule):** Holbrook et al. 2019 relates climate modes to heatwaves "enhanced or
suppressed" by region and gives no sign; no row was written. The reader found that the same rule was **not** held on
four other rows. They are now withdrawn (§4), so this memo's first draft overstated that discipline.

## 3. What a realisation would and would not show

- **Supported** means two things together. The realised vital carries attribution in the direction the rows predict.
  And the model with it beats v3 at v3's base rate (15.0%) and budgets, with the season-block interval reported. It does
  not mean the mechanism is true at the Keys (README rule 2).
- **Not supported** is written up the same way (T8). A wind vital that adds nothing beyond HotSpot(t0) is a finding:
  satellite HotSpot may already carry the calm-day signal at 5 km.
- **Lever:** none of the candidates is a lever. T7's honest outcome on FKNMS stays *"no lever, still"*.

## 4. Review (skill step 6) — fresh-context faithfulness reader, 2026-10-12

`agent_faithfulness_reader_m3b_i` read all 32 rows against their cached abstracts. **15 confirmed** (promoted to
`reviewed`, `reviewed_by` set; one, amo_002, later demoted by the III review's F-7, so 14 stand, each now bound by
`reviewed_sha256` to the content read). **17 questioned**:

- **Withdrawn (6), archived in `withdrawn/coral_reef/` with the reason (SO-2):**

  | Row | Reason |
  |---|---|
  | amm_001 | no sign ("consistent with") |
  | enso_001 | no sign ("bear a relationship") |
  | sea_level_anomaly_001 | no SLA sign ("decreased or increased") |
  | winter_warming_001 | the driver–event link is stated by no sentence |
  | amo_001 | the paper states the AMV *lags* the Keys |
  | wind_002 | the quotation is background framing, not the paper's finding |

- **Corrected, still `draft`** (an extractor's correction is not a second reading):

  | Rows | What changed |
  |---|---|
  | cloud_001 · enso_002 · enso_003 · florida_current_001 · internal_waves_001 · sst_variability_001 · wind_004 | hedges restored |
  | cloud_001 · internal_waves_001 | quotations moved to the sentence carrying the claim |
  | sst_variability_001 | direction → nonmonotone |
  | wind_004 | direction → negative, no threshold |
  | enso_003 | variable → the Niño 3.4 index (the sign now reads right) |
  | cyclone_power_001 | the cross-paper "contradiction" removed (different events) |
  | hurricane_001 | the mechanism no longer says which tract benefited (the abstract does not) |
  | warm_pool_001 | the variable is proximity, now `unrealisable` as a broadcast index |

- **Open (1):** preconditioning_001's evidence class. The reader's case rests on recall of the full paper (heating
  experiments), not on the cached abstract. It stays `observational` (what the quoted claim is) and `draft` until the
  full text is read.
- **The dominant defect: hedges stripped** in 9 of 32 mechanisms while their quotations kept them, so `--check` passed.
  The skill now says so (step 3). Lag defaults to 0 in most rows. That is honest per row ("not stated"), but as a set the
  ledger reads like nowcast drivers; the skill now asks trend rows to say so.

## 5. The ruling

**Ruled 2026-10-12 (operator, `AskUserQuestion`, at the M-3b-i III close): reef-light wind.** The question carried
III F-6's event-matched counts (wind 2 reviewed rows, cyclones 1). M-3b-ii builds `NDBCStdmet` (WI-19), takes a steward
ruling on the station-to-zone map and on the calm threshold (scanned, not fixed at 4 m/s), fetches under FKNMS's
posture, re-runs the self-test (SO-7), and tests the vital against board v3 at its base rate and budgets. It writes the
result up either way (T8). The tag is `proxy`: T7's honest outcome stays *"no lever, still"*.

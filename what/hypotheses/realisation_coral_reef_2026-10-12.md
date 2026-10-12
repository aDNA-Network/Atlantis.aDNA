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

**Ledger:** 26 rows, **15 `reviewed`** and 11 `draft`. 32 were extracted from 28 works (corpus: 380 works, 21 queries); the
faithfulness reader confirmed 15, questioned 17, and 6 were withdrawn (§4). `LEDGER.md` is the table. Reviewed rows are
marked ★.

## 1. What the ledger says, by driver family

| Family | Rows (★ reviewed) | Regions | What the rows claim | Bears on DHW **onset**? |
|---|---|---|---|---|
| Wind (calm, doldrums, a 4 m/s threshold) | wind_001★ · 003★ · 004 · 005★ · 006★ | GBR · Persian Gulf · Iriomote · global · Brazil | less wind, more heat or bleaching; a 4 m/s critical threshold (003★, from a model with observations) | **yes**: 003★ (sea-bottom temperature) and 006★ (marine heatwaves) are heat claims |
| Tropical cyclones | hurricane_001 · 002★ · cyclone_power_001 | Florida Reef Tract + USVI · Caribbean · global | cool wakes reduce CRW thermal stress (002★); cyclone *power* goes with higher bleaching *severity*, a different event, so no contradiction | **yes**: 002★ is on CRW thermal stress itself, Caribbean, 2005 and 2010 |
| Cloud / light | cloud_001 · 002★ · turbidity_001★ | French Polynesia · GBR · global | less cloud under El Niño weather → bleaching (002★); cloud and turbidity moderate bleaching given heat | partly: 002★ is a heating pathway; the other two are response claims (T12) |
| Air–sea flux | heat_flux_001★ | Ningaloo | net heat flux raised reef temperature above offshore; offshore DHW understated 3 vs 11 °C-weeks | yes, and a caution that 5 km DHW can understate reef-scale stress |
| Climate modes | enso_002 · enso_003 · amo_002★ | Caribbean · Japan · Yucatán | Caribbean heatwaves are *suggested* to relate to El Niño; Japan's DHW built under La Niña; AWP SST varies with the AMO | weakly: monthly indices, near-constant within a season |
| Internal waves | internal_waves_001 · 002★ · 003★ | **Florida Keys** ×2 · Andaman | cool subsurface incursions | **no**: subsurface. CRW's surface DHW cannot see them (`unrealisable`) |
| Heat history and the trend | preconditioning_001 · warming_trend_001★ · sst_variability_001 · florida_current_001 | GBR · **Keys** ×3 | a protective pre-pulse (response); warming → annual bleaching by 2020–34; moderate variability protects cover; fewer eddies → winter warming (hypothesized) | no reviewed row is about DHW onset |
| Forecast / the event itself | forecast_sst_001★ · dhw_001★ · warm_pool_001 | global · Caribbean | the CRW 4-month Outlook (a **comparator**); DHW predicts bleaching (supports the event definition); proximity to the 2005 warm pool | not as drivers |

**T8 as worded**, counted from the 26 row files:

| Realisability | Rows | Which |
|---|---|---|
| From FKNMS's own streams, or a declared fetcher | **10** | wind ×4 + temperature_variability (NDBC, declared not built); dhw, preconditioning, sst_variability, warming_trend (derivable from CRW) |
| Needs an ordinary new stream (an index, a track, an ERDDAP field, a reanalysis) | **12** | |
| `unrealisable` on this grid | **4** | internal waves ×3 · warm_pool_001 |

The falsifier "rows no fetcher can realise" is **not met**, and it is not vacuous.

**What the count does not show.** By the paper's own outcome, **11 rows are about heat** and **15 are about bleaching
or cover given heat**. **No reviewed row about heat onset is realisable from FKNMS's existing streams.** The derivable
rows are a response claim, the event definition, the era, or a cover claim. The cheapest honest test of the literature
on this event therefore needs **one new stream**. The cheap derivable candidate this memo first ranked second (a
preceding-winter SSTA) rested on a row the reader showed the text does not carry; it is withdrawn (§4).

## 2. Ranked candidates for M-3b-ii

Literature strength counts reviewed rows, rows whose event matches FKNMS's (heat, not bleaching response), and
regional rows. Build cost is the Atlantis and instance work before a model can train.

| Rank | Candidate | Rows | Literature strength | Realisability on FKNMS | Build cost | Lever? (T7) |
|---|---|---|---|---|---|---|
| **1** | **Reef-light wind** (weekly mean wind and a count of days below 4 m/s, at MLRF1 · SMKF1 · LONF1 · SANF1) | wind_001★ · 003★ · 004 · 005★ · 006★ (+ temperature_variability★ on the same stations) | **highest**: 4 reviewed; 2 reviewed heat claims (003★ with a stated threshold); 5 regions. The discovery memo's own next stream | 4 stations → 21 zones (a station-to-zone map, a steward ruling); C-MAN records from 1987–88, with gaps | **highest**: build `NDBCStdmet` in `atlantis_core` (WI-19; a template change, P2 rule), then fetch into FKNMS under its posture (public NOAA), self-test, train | **no**: proxy. *"No lever, still"* (T7) |
| **2** | **Tropical-cyclone cool wakes** (a weekly indicator of a best track within a radius of the zone, HURDAT2) | hurricane_002★ · hurricane_001 (Keys) | event-matched: 002★ is on **CRW thermal stress** itself, Caribbean. 001 is the Keys' own case (draft) | sparse and event-like; tracks are public NOAA data | moderate: a new track fetcher (not declared) | no |
| 3 | Cloud / insolation (a satellite cloud or PAR product on ERDDAP) | cloud_002★ (heating) · cloud_001 | 1 reviewed heating claim, Pacific | gridded; the polygon reducer exists only for CRW, so a generic ERDDAP polygon reducer is likely a template change | moderate | no |
| 4 | ENSO index (Niño 3.4) | enso_002 · enso_003 | 2 drafts, hedged; region-dependent | broadcast; monthly | low–moderate: a small index fetcher | no |

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
`reviewed`, `reviewed_by` set). **17 questioned**:

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

*(recorded here once the operator rules)*

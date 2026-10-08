---
type: coordination
coord_id: coord_2026_10_08_floridakeyscoral_to_proteus_board_entry
kind: board_entry
title: "Board entry — FloridaKeysCoral.aDNA v1 (FKNMS coral heat-stress onset, DHW ≥ 4 within 8 wk): GREEN, method_demonstration"
from: steward of FloridaKeysCoral.aDNA (stanley; written by agent_proteus in the instance's M-2b sitting)
to: proteus (Atlantis.aDNA)
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
status: landed   # 2026-10-08, operator-opened Atlantis M-2b session (steward ruling 22): sha256, validate, assert_green, unit_ref, semantic_hash re-checked; entry copied unedited; BOARD.md regenerated
federation_ref: {source_vault: Atlantis.aDNA, source_commit: 671808b4a16ddec6c52432fb8ac44c68ebdcab13, runs_under: 9ac40cf8064dc25bed28b5151ba045f68c66c7c9, contract: instance_contract_v0 v0.3.0}
instance_commit: 6e031f6
posture_class: public   # FloridaKeysCoral.aDNA ADR-001 (ratified 2026-10-07)
nothing_never_crosses: true
entry_file: what/board/entries/2026-10-08_florida_keys_coral_v1.json
entry_sha256: de1540fe18c39e26344ce9e7b38e7a658861cadb41e691ae854ff729ea0be7ea
semantic_hash: c07b7c0288
tags: [coordination, board_entry, floridakeyscoral, fknms, coral, m2b, p2]
---

# Board entry — FloridaKeysCoral.aDNA v1

**What:** a board entry (contribution guide §2a, contract §D). **From:** `FloridaKeysCoral.aDNA`, federating Atlantis at
`671808b` (the numbers were run under core 0.6.0 at `9ac40cf`; `671808b` changed only the page build and conform item 10).

**The entry** is the JSON `python -m atlantis_core.board --instance <FloridaKeysCoral.aDNA> --version 1 --run-date 2026-10-08
--entries <FloridaKeysCoral.aDNA>/what/board/entries` wrote, **unedited** (sha256 `de1540fe18c39e26344ce9e7b38e7a658861cadb41e691ae854ff729ea0be7ea`; inline below).

**Checks.**
- Self-test receipt `semantic_hash` **`c07b7c0288`** = the entry's `config_hash` (steward ruling 21 moved it from `0d4d2bb19e`:
  `split.rolling_origin_years` declared).
- `python -m atlantis_core.conform --instance <FloridaKeysCoral.aDNA>` (full; item 9 ✅, item 10 ✅):

```
instance contract v0.3.0 · FloridaKeysCoral.aDNA · stage declared
✅  1 Patient defined (units · grid · geometry by pointer)  [units.yaml · atlantis.yaml · what/geometry/fknms_zones_pre_blueprint.geojson]
✅  2 Event defined (authority · threshold + unit · direction · horizon · onset rule)  [events.yaml · atlantis.yaml · streams.yaml]
✅  3 Streams registered with Rule-5 provenance  [streams.yaml]
✅  4 Every vital tagged, with stream_ref and lag/window; levers name an owner  [features.yaml]
✅  5 Surveillance channel declared, or declared absent with the reason  [atlantis.yaml · streams.yaml · features.yaml]
✅  6 Self-test green (before any real data is fetched)  []
      re-run here on the synthetic world (no data)
✅  7 Data posture ruled in the instance's own ADR  [how/federation/atlantis/CLAUDE.md · who/governance/adr_001_data_posture.md]
✅  8 Split is temporal  [atlantis.yaml]
✅  9 Board entry carries base rate, budgets, lead time, ablations, hash, pins, claim  [what/board/entries/2026-10-08_florida_keys_coral_v1.json]
✅ 10 Published page has a Limitations section  [site/florida_keys_coral_v1.html]
✅ 11 mapping.yaml present and held to atl_v0  [mapping.yaml]
✅ 12 Credentials by name only (gitleaks)  [gitleaks detect --no-git FloridaKeysCoral.aDNA]
✅ conforms: 12 pass · 0 n/a (none) · 0 outstanding (none)
```

**Posture.** `public` (ADR-001). Nothing in this memo is from the right-hand column of the guide: no observations, labels,
per-patient predictions, partner coordinates or credentials — metrics only, as `assert_green` checked at emit.

**What a reader should take from it** (the entry's own notes say the same): the model (0.937 / 0.690 at a 15.0% base rate)
beats every no-model comparator, but **week-of-year climatology nearly matches it** (0.919 / 0.601); the base rate is
non-stationary (1.31 → 7.59 → 15.01%), so thresholds fixed on 2014–18 flag about **twice their budget** on 2019–25; lead
time is censored at the 8-week horizon; no vital is a lever. Limits: `site/florida_keys_coral_v1.html#limits` in the instance.

## The entry (unedited)

```json
{
 "board_entry_schema": "atl_board_entry_v1",
 "tier": "GREEN",
 "accuracy_claim": "NONE — method demonstration on public data; not an operational forecast (SO-4)",
 "entry_id": "2026-10-08_florida_keys_coral_v1",
 "source": "instance",
 "instance": "FloridaKeysCoral.aDNA",
 "method_version": "pattern_ecosystem_early_warning 0.1 · atlantis_core 0.6.0",
 "recorded_by": "agent_proteus",
 "recorded_at": "2026-10-08T19:52:50Z",
 "run_date": "2026-10-08",
 "evaluation": {
  "evaluation_id": "atl_eval_florida_keys_coral_v1",
  "event_ref": "atl_event_florida_keys_coral_onset",
  "unit_ref": "atl_unit_florida_keys_coral_all",
  "split": "train 1986-2013 · val 2014-2018 · test 2019-2025, scored once; rolling origin 2014->2025; label-horizon embargo 8 wk at every boundary",
  "embargo_weeks": 8,
  "n_test": 5595,
  "n_positives": 840,
  "base_rate": 0.1501,
  "auroc": 0.937,
  "auprc": 0.6903,
  "brier": 0.1005,
  "calibration_slope": 1.99,
  "climatology_auroc": 0.9194,
  "climatology_auprc": 0.6012,
  "persistence_auroc": 0.7505,
  "persistence_auprc": 0.3583,
  "trend_auroc": 0.7809,
  "trend_auprc": 0.5201,
  "base_rate_train": 0.0131,
  "base_rate_validation": 0.0759,
  "calibration_in_the_large_validation": -0.0453,
  "calibration_in_the_large_test": -0.0974,
  "alert_budgets": [
   {
    "rate": 0.05,
    "precision": 0.7424,
    "recall": 0.4357,
    "n_alerts": 493,
    "threshold_from": "validation",
    "realised_rate": 0.0881
   },
   {
    "rate": 0.1,
    "precision": 0.5677,
    "recall": 0.769,
    "n_alerts": 1138,
    "threshold_from": "validation",
    "realised_rate": 0.2034
   },
   {
    "rate": 0.2,
    "precision": 0.4828,
    "recall": 0.9202,
    "n_alerts": 1601,
    "threshold_from": "validation",
    "realised_rate": 0.2861
   }
  ],
  "lead_time": {
   "budget_rate": 0.1,
   "n_onsets": 105,
   "flagged_fraction": 1.0,
   "median_lead": 8.0,
   "threshold_from": "validation"
  },
  "ablations": [],
  "learner": "xgboost 3.4.1 · binary:logistic · depth 4 · eta 0.03 · early-stop logloss (100 rounds) · 108 trees · no scale_pos_weight · monotone on none",
  "config_hash": "c07b7c0288",
  "data_pins": [
   {
    "stream_ref": "atl_stream_fkc_dhw_daily",
    "sha256": "04127678bf297aa954597ecd4c3e9324862703ec8432f18d7d1c1ca72944ad7e"
   },
   {
    "stream_ref": "atl_stream_fkc_hotspot_daily",
    "sha256": "307f7f016b83f84793f7a1ffebb8f6750621df2263269d38b20e2ed3142c6381"
   },
   {
    "stream_ref": "atl_stream_fkc_ssta_daily",
    "sha256": "80076fddef8f0261510d79b07234317a30c80f0f94a4402367070250015f73d0"
   }
  ],
  "shap_summary_ref": "outputs/atlantis_core/shap_summary.json",
  "claim": "method_demonstration",
  "limitations_ref": "site/florida_keys_coral_v1.html#limits",
  "recorded_by": "agent_proteus",
  "recorded_at": "2026-10-08T19:52:50Z"
 },
 "evaluation_extras": {
  "event": {
   "event_id": "atl_event_florida_keys_coral_onset",
   "threshold": 4.0,
   "unit": "Cel.wk",
   "direction": "above",
   "horizon": 8,
   "onset_rule": "drop zone-weeks whose last-known weekly maximum DHW is already ≥ 4 (already in heat stress); drop zone-weeks whose DHW crossed 4 in t−7..t (refractory 7 = horizon − 1, the lead-time onset: one episode, one onset); drop zone-weeks with no DHW in t+1..t+8 (unknown outcome)"
  },
  "patient": {
   "unit_kind": "mpa_zone",
   "geometry_ref": "what/geometry/fknms_zones_pre_blueprint.geojson (all features)",
   "n_units": 21
  },
  "modelling_rows": 40226,
  "modelling_positives": 1592,
  "modelling_prevalence": 0.0396,
  "dropped_already_in_event": 3598,
  "dropped_outcome_unknown": 3,
  "n_trees": 108,
  "n_vitals": 9,
  "vital_groups": {
   "heat": 6,
   "temperature": 3
  },
  "sensitivity": [
   {
    "name": "threshold 8 Cel.wk",
    "test_auroc": 0.8754,
    "test_auprc": 0.238,
    "test_prevalence": 0.0628
   }
  ],
  "rolling_origin": [
   {
    "train_through": 2014,
    "test_year": 2015,
    "n": 782,
    "positives": 144,
    "prevalence": 0.1841,
    "auroc": 0.9512,
    "auprc": 0.7983,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2014
     ],
     "n_trees": 108,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2015,
    "test_year": 2016,
    "n": 1045,
    "positives": 40,
    "prevalence": 0.0383,
    "auroc": 0.8994,
    "auprc": 0.1897,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2015
     ],
     "n_trees": 228,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2016,
    "test_year": 2017,
    "n": 1077,
    "positives": 8,
    "prevalence": 0.0074,
    "auroc": 0.9608,
    "auprc": 0.1325,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2016
     ],
     "n_trees": 114,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2017,
    "test_year": 2018,
    "n": 1061,
    "positives": 24,
    "prevalence": 0.0226,
    "auroc": 0.8414,
    "auprc": 0.1312,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2017
     ],
     "n_trees": 13,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2018,
    "test_year": 2019,
    "n": 989,
    "positives": 56,
    "prevalence": 0.0566,
    "auroc": 0.9171,
    "auprc": 0.381,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2018
     ],
     "n_trees": 14,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2019,
    "test_year": 2020,
    "n": 880,
    "positives": 112,
    "prevalence": 0.1273,
    "auroc": 0.9642,
    "auprc": 0.8079,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2019
     ],
     "n_trees": 80,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2020,
    "test_year": 2021,
    "n": 1050,
    "positives": 24,
    "prevalence": 0.0229,
    "auroc": 0.9502,
    "auprc": 0.3687,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2020
     ],
     "n_trees": 177,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2021,
    "test_year": 2022,
    "n": 776,
    "positives": 144,
    "prevalence": 0.1856,
    "auroc": 0.9206,
    "auprc": 0.6791,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2021
     ],
     "n_trees": 205,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2022,
    "test_year": 2023,
    "n": 565,
    "positives": 168,
    "prevalence": 0.2973,
    "auroc": 0.9944,
    "auprc": 0.9897,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2022
     ],
     "n_trees": 110,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2023,
    "test_year": 2024,
    "n": 671,
    "positives": 168,
    "prevalence": 0.2504,
    "auroc": 0.9347,
    "auprc": 0.8032,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2023
     ],
     "n_trees": 88,
     "selection_eras": {}
    }
   },
   {
    "train_through": 2024,
    "test_year": 2025,
    "n": 664,
    "positives": 168,
    "prevalence": 0.253,
    "auroc": 0.9361,
    "auprc": 0.806,
    "climatology_eras": {},
    "climatology_refit": false,
    "selection": {
     "selected_on": [
      2024
     ],
     "n_trees": 156,
     "selection_eras": {}
    }
   }
  ],
  "rolling_selection": "per_fold",
  "rolling_skipped": [
   {
    "test_year": 2014,
    "reason": "inner stop year 2013 has 0 positives (< 5)"
   }
  ],
  "obligations": [],
  "shap_summary": {
   "base_p": 0.003437047197160026,
   "additivity_max_gap": 2.7221027210089233e-06,
   "top6": [
    "fkc_hotspot_daily_mean_t0",
    "fkc_hotspot_daily_mean_t1",
    "fkc_ssta_daily_mean_t0",
    "fkc_hotspot_daily_mean_t2",
    "fkc_dhw_daily_max_t4",
    "fkc_ssta_daily_mean_t1"
   ],
   "group_mean_abs_shap": {
    "heat": 2.15616,
    "temperature": 0.29128
   },
   "group_net_mean_abs_shap": {
    "heat": 1.78982,
    "temperature": 0.20767
   },
   "tag_mean_abs_shap": {
    "proxy": 2.25647,
    "state": 0.19097
   }
  },
  "semantic_hash": "c07b7c0288",
  "config_bytes_md5": {
   "atlantis.yaml": "f7ae118822"
  },
  "data_pins": [
   {
    "stream_ref": "atl_stream_fkc_dhw_daily",
    "artifact": "data/raw/fkc_dhw_daily.parquet",
    "sha256": "04127678bf297aa954597ecd4c3e9324862703ec8432f18d7d1c1ca72944ad7e"
   },
   {
    "stream_ref": "atl_stream_fkc_hotspot_daily",
    "artifact": "data/raw/fkc_hotspot_daily.parquet",
    "sha256": "307f7f016b83f84793f7a1ffebb8f6750621df2263269d38b20e2ed3142c6381"
   },
   {
    "stream_ref": "atl_stream_fkc_ssta_daily",
    "artifact": "data/raw/fkc_ssta_daily.parquet",
    "sha256": "80076fddef8f0261510d79b07234317a30c80f0f94a4402367070250015f73d0"
   }
  ],
  "learner_swaps": [],
  "embargo": {
   "embargo_weeks": 8,
   "horizon": 8,
   "checked": true,
   "boundaries": {
    "train→val": {
     "next_start": 2014,
     "rows_dropped": 168,
     "positives_dropped": 0,
     "latest_window_end": "2013-12-30"
    },
    "val→test": {
     "next_start": 2019,
     "rows_dropped": 161,
     "positives_dropped": 0,
     "latest_window_end": "2018-12-31"
    },
    "refit→test": {
     "next_start": 2019,
     "rows_dropped": 161,
     "positives_dropped": 0,
     "latest_window_end": "2018-12-31"
    }
   },
   "spill": {
    "train→val": {
     "crossing_rows": 168,
     "rows": 29889,
     "crossing_positives": 0,
     "positives": 392,
     "labelled_by_next": 0
    },
    "val→test": {
     "crossing_rows": 161,
     "rows": 4742,
     "crossing_positives": 0,
     "positives": 360,
     "labelled_by_next": 0
    }
   },
   "folds": {
    "2015": {
     "rows_dropped": {
      "train→stop": 168,
      "stop→test": 71,
      "refit→test": 71
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      144
     ]
    },
    "2016": {
     "rows_dropped": {
      "train→stop": 71,
      "stop→test": 51,
      "refit→test": 51
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      144
     ]
    },
    "2017": {
     "rows_dropped": {
      "train→stop": 51,
      "stop→test": 160,
      "refit→test": 160
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      40
     ]
    },
    "2018": {
     "rows_dropped": {
      "train→stop": 160,
      "stop→test": 163,
      "refit→test": 163
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      8
     ]
    },
    "2019": {
     "rows_dropped": {
      "train→stop": 163,
      "stop→test": 161,
      "refit→test": 161
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      24
     ]
    },
    "2020": {
     "rows_dropped": {
      "train→stop": 161,
      "stop→test": 153,
      "refit→test": 153
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      56
     ]
    },
    "2021": {
     "rows_dropped": {
      "train→stop": 153,
      "stop→test": 136,
      "refit→test": 136
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      112
     ]
    },
    "2022": {
     "rows_dropped": {
      "train→stop": 136,
      "stop→test": 153,
      "refit→test": 153
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      24
     ]
    },
    "2023": {
     "rows_dropped": {
      "train→stop": 153,
      "stop→test": 24,
      "refit→test": 24
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      144
     ]
    },
    "2024": {
     "rows_dropped": {
      "train→stop": 24,
      "stop→test": 0,
      "refit→test": 0
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      168
     ]
    },
    "2025": {
     "rows_dropped": {
      "train→stop": 0,
      "stop→test": 10,
      "refit→test": 10
     },
     "positives_dropped": {
      "train→stop": 0,
      "stop→test": 0,
      "refit→test": 0
     },
     "spill_crossing_positives": [
      0,
      168
     ]
    }
   }
  },
  "baselines": {
   "climatology": {
    "score": "week-of-year onset rate, train ∪ embargoed val"
   },
   "persistence": {
    "score": "s(t), carried as the label carries it",
    "n_test": 5595,
    "n_imputed": 0
   },
   "trend": {
    "score": "logistic on [s(t), s(t) − s(t−1)]",
    "n_test": 5595,
    "n_imputed": 0,
    "n_fit": 34470,
    "fit_years": [
     1986,
     2018
    ]
   }
  }
 },
 "provenance": {
  "metrics_file": "outputs/atlantis_core/metrics.json",
  "shap_file": "outputs/atlantis_core/shap_summary.json",
  "learner_swap_files": [],
  "generated_by": "atlantis_core.board (emit → closed AtlEvaluation validated against the committed atl_ontology_v0.schema.json + assert_green); numbers are not retyped"
 },
 "notes": [
  "Method demonstration on public NOAA Coral Reef Watch products (DHW, HotSpot, SST anomaly; CRW v3.1, Skirving et al. 2020, doi 10.3390/rs12233856); not an operational forecast and not a bleaching forecast — CRW's own Bleaching Alert products are the operational system (SO-4).",
  "The calendar knows most of it: week-of-year climatology nearly matches the model on test. Read the model against climatology, persistence and trend before reading its AUROC (SO-9).",
  "The base rate is non-stationary across the fixed split (train, validation, test): thresholds fixed on validation flag about twice their nominal budget on test, and the model under-predicts the high-rate years (calibration in the large). Consistent with warming; not separated from CoralTemp's 2002 input change or DHW's fixed MMM climatology.",
  "Lead time is censored at the horizon: most test onsets were first flagged at the earliest week the window allows. No vital is a lever (DHW is state; HotSpot and SST anomaly are proxies) — this is surveillance, not intervention guidance.",
  "19 of 21 zones are read through a single 5 km cell (no cell centre inside the zone); zones 20 and 21 sit at a cell-edge tie (disclosed, tested). DHW lacks 1999-05-01 for every zone (CRW's own axis)."
 ]
}
```

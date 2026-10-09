---
type: coordination
coord_id: coord_2026_10_08_floridakeyscoral_to_proteus_board_entry_v3
kind: board_entry
title: "Board entry — FloridaKeysCoral.aDNA v3 (core 0.7.0: climatology at budget · paired interval · T2's learner swap)"
from: steward of FloridaKeysCoral.aDNA (stanley; written by agent_proteus in the Atlantis M-2c-ii sitting)
to: proteus (Atlantis.aDNA)
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
status: landed   # 2026-10-08, Atlantis M-2c-ii: sha256 = committed bytes at instance 24cc1f4 = inline JSON, validate, assert_green, unit_ref, semantic_hash c07b7c0288 = load_instance, config bytes md5 43f06f0022 = atlantis.yaml at 24cc1f4; BOARD.md regenerated (v2 superseded)
supersedes: coord_2026_10_08_floridakeyscoral_to_proteus_board_entry_v2   # its entry v2 stays on the board, superseded by derivation (SO-2)
federation_ref: {source_vault: Atlantis.aDNA, source_commit: 8255d9bad2f050a046de33a13f32fc846e02e284, contract: instance_contract_v0 v0.3.0}
run_core_commit: 1396ce299e36702586adbaf3e9227ab27c3d6a36   # the run (core 0.7.0); 8255d9b changes only the page's data, not a number
instance_commit: 24cc1f4
posture_class: public   # FloridaKeysCoral.aDNA ADR-001 (ratified 2026-10-07)
nothing_never_crosses: true
entry_file: what/board/entries/2026-10-08_florida_keys_coral_v3.json
entry_sha256: b3801820c7b08fda84e0cc64040d0f99b94f5ab79b0db8acd224fddc787a62cb
semantic_hash: c07b7c0288
tags: [coordination, board_entry, floridakeyscoral, fknms, coral, m2c_ii, p2_gate_condition_a, learner_swap]
---

# Board entry — FloridaKeysCoral.aDNA v3

**Why a v3.** P2-gate condition (a) asks for T11 at its terms on both instances: climatology at the chosen budget, and the
model − climatology difference with its uncertainty. Core 0.7.0 (Atlantis M-2c-i) measures both; v2 was run at 0.6.1 and
carries neither. v3 also carries T2's swap on this instance (P2 gate G-4, C-033: never carded before).

**What the steward changed, before the run** (dated commits, `atlantis.yaml` committed first):
- `ff7eda9` — `mapping.yaml` ontology pin atl_v0 0.7.0 → 0.8.0. Federation upkeep (Atlantis M-2c ruling 2), not a patch.
- `0ad8804` — `learner_swaps` (logistic, the exemplar's block unchanged) and `eval.interval_season_start_month: 1`
  (M-2c-ii ruling 1: calendar years; a summer heat season never straddles New Year). `semantic_hash` stays `c07b7c0288`
  (verified before committing: neither key is in the hash).
- `8bc76f3` — federation pin → `1396ce2` (core 0.7.0). Vitals, label and self-test code are untouched since `28e5af4`,
  so the receipt holds and SO-7 was not triggered.

**The run.** `python -m atlantis_core.run --instance .` at core 0.7.0, 240 s. Against v2's run, by a leaf-walk of
`metrics.json`: all 2,307 of v2's metrics leaves are equal except `atlantis_core`, `run_at` and the config-bytes md5 (now
`43f06f0022`, the committed bytes of `0ad8804`). The model, SHAP and what-if bytes are unchanged. New leaves: climatology at
the budgets (29) and the paired interval (96). The entry's `delta_vs` against v2 shows no field changed.

**The page** (`24cc1f4`, steward's hand). v3 contradicts two sentences the v2 page carried: "the model beats every
comparator" and the manager's note that the model's value is "where its AUPRC exceeds climatology's". At the 10% budget,
climatology's alerts are the more precise, and the paired interval spans 0 both threshold-free and at matched volume.
Both sentences now say so, **by token**: Atlantis `8255d9b` puts the interval into the page's data, and the pin moved
there. That commit changes only the page's data, not a number.

**Checks.** Self-test receipt `semantic_hash` `c07b7c0288` = the entry's `config_hash`. `conform` (full):

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
✅  9 Board entry carries base rate, budgets, lead time, ablations, hash, pins, claim  [what/board/entries/2026-10-08_florida_keys_coral_v1.json · what/board/entries/2026-10-08_florida_keys_coral_v2.json · what/board/entries/2026-10-08_florida_keys_coral_v3.json]
✅ 10 Published page has a Limitations section  [site/florida_keys_coral_v1.html]
✅ 11 mapping.yaml present and held to atl_v0  [mapping.yaml]
✅ 12 Credentials by name only (gitleaks)  [gitleaks detect --no-git FloridaKeysCoral.aDNA]
✅ conforms: 12 pass · 0 n/a (none) · 0 outstanding (none)
```

**Posture.** `public` (ADR-001). Metrics only; nothing from the guide's right-hand column. The entry holds 582 numeric
leaves against the GREEN cap of 600.

**Note beside the memo (Atlantis, 2026-10-08, after III M-2c-ii; SO-2: a note, not an edit of the record).** The review (F-1) found the
page sentences above still over-read the comparison: they led with the raw precision gap at unequal volumes. The steward reworded
the page at instance `fc6b65d`: matched volume at both readings of the budget, "not shown to be better", and a limits bullet. The pin
moved to `bcd2612`, where the page build also checks the interval it cites (F-3). **The entry is unchanged**; its sha256 above stands.

## The entry (unedited)

```json
{
 "board_entry_schema": "atl_board_entry_v1",
 "tier": "GREEN",
 "accuracy_claim": "NONE — method demonstration on public data; not an operational forecast (SO-4)",
 "entry_id": "2026-10-08_florida_keys_coral_v3",
 "source": "instance",
 "instance": "FloridaKeysCoral.aDNA",
 "method_version": "pattern_ecosystem_early_warning 0.1 · atlantis_core 0.7.0",
 "recorded_by": "agent_proteus",
 "recorded_at": "2026-10-09T02:09:12Z",
 "run_date": "2026-10-08",
 "evaluation": {
  "evaluation_id": "atl_eval_florida_keys_coral_v3",
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
  "climatology_alert_budgets": [
   {
    "rate": 0.05,
    "precision": 0.6291,
    "recall": 0.6786,
    "n_alerts": 906,
    "threshold_from": "validation",
    "realised_rate": 0.1619
   },
   {
    "rate": 0.1,
    "precision": 0.6228,
    "recall": 0.7429,
    "n_alerts": 1002,
    "threshold_from": "validation",
    "realised_rate": 0.1791
   },
   {
    "rate": 0.2,
    "precision": 0.5371,
    "recall": 0.8702,
    "n_alerts": 1361,
    "threshold_from": "validation",
    "realised_rate": 0.2433
   }
  ],
  "paired_intervals": [
   {
    "comparator": "climatology",
    "metric": "auroc",
    "resample_unit": "season_year",
    "season_start_month": 1,
    "n_blocks": 7,
    "n_draws": 2000,
    "n_degenerate": 0,
    "confidence_level": 0.95,
    "delta_estimate": 0.0176,
    "delta_lower": -0.0193,
    "delta_upper": 0.0618,
    "spans_zero": true
   },
   {
    "comparator": "climatology",
    "metric": "auprc",
    "resample_unit": "season_year",
    "season_start_month": 1,
    "n_blocks": 7,
    "n_draws": 2000,
    "n_degenerate": 0,
    "confidence_level": 0.95,
    "delta_estimate": 0.0891,
    "delta_lower": -0.0241,
    "delta_upper": 0.1898,
    "spans_zero": true
   }
  ],
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
  "recorded_at": "2026-10-09T02:09:12Z"
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
   "atlantis.yaml": "43f06f0022"
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
  "learner_swaps": [
   {
    "learner": "scikit-learn 1.9.1 LogisticRegression · L2 · C=10.0 (val log-loss over [0.001, 0.01, 0.1, 1.0, 10.0]) · median impute + missingness flags · standardised · imputer/scaler fitted on each model's own training rows (train for selection, train+val for the final; never test)",
    "test_auroc": 0.9465,
    "test_auprc": 0.7361,
    "brier": 0.0921,
    "calibration_slope": 1.7,
    "alert_budgets": {
     "5pct": {
      "precision": 0.7193,
      "recall": 0.5369,
      "realised_rate": 0.1121,
      "threshold_from": "validation"
     },
     "10pct": {
      "precision": 0.5655,
      "recall": 0.8381,
      "realised_rate": 0.2225,
      "threshold_from": "validation"
     },
     "20pct": {
      "precision": 0.4947,
      "recall": 0.9452,
      "realised_rate": 0.2869,
      "threshold_from": "validation"
     }
    },
    "lead_time": {
     "flagged_fraction": 1.0,
     "median_lead": 7.0,
     "n_onsets": 105
    },
    "rolling_origin_auroc_range": [
     0.9004,
     0.9993
    ],
    "top6": [
     "fkc_hotspot_daily_mean_t0",
     "fkc_hotspot_daily_mean_t1",
     "fkc_ssta_daily_mean_t0",
     "fkc_ssta_daily_mean_t1",
     "fkc_dhw_daily_max_t0",
     "fkc_hotspot_daily_mean_t2"
    ],
    "group_mean_abs_shap": {
     "heat": 39.59937,
     "temperature": 16.59294
    },
    "group_net_mean_abs_shap": {
     "heat": 7.65755,
     "temperature": 4.13111
    },
    "semantic_hash": "c0d0c29943"
   }
  ],
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
    "score": "week-of-year onset rate, train ∪ embargoed val",
    "thresholds": "fixed on validation by a fit on train only (embargoed)",
    "selection_fit_years": [
     1986,
     2013
    ],
    "fit_years": [
     1986,
     2018
    ],
    "n_test": 5595
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
  },
  "paired_interval": {
   "comparator": "climatology",
   "resample_unit": "season_year",
   "season_start_month": 1,
   "blocks": [
    2019,
    2020,
    2021,
    2022,
    2023,
    2024,
    2025
   ],
   "block_rows": {
    "2019": 989,
    "2020": 880,
    "2021": 1050,
    "2022": 776,
    "2023": 565,
    "2024": 671,
    "2025": 664
   },
   "n_blocks": 7,
   "n_distinct_multisets": 1716,
   "n_draws": 2000,
   "n_degenerate": 0,
   "seed": 20261008,
   "level": 0.95,
   "level_is_nominal": true,
   "paired": true,
   "scope": "this run's full model on the main test split — not its ablations, sensitivity run or rolling folds",
   "auroc": {
    "estimate": 0.0176,
    "lower": -0.0193,
    "upper": 0.0618,
    "spans_zero": true,
    "seasons_scored": 7,
    "seasons_favouring_model": 3,
    "sign_test_p_one_sided": 0.7734,
    "per_season": {
     "2019": -0.0078,
     "2020": 0.0209,
     "2021": 0.0424,
     "2022": -0.0338,
     "2023": 0.0921,
     "2024": -0.013,
     "2025": -0.0207
    }
   },
   "auprc": {
    "estimate": 0.0891,
    "lower": -0.0241,
    "upper": 0.1898,
    "spans_zero": true,
    "seasons_scored": 7,
    "seasons_favouring_model": 4,
    "sign_test_p_one_sided": 0.5,
    "per_season": {
     "2019": 0.1044,
     "2020": 0.1699,
     "2021": 0.1556,
     "2022": -0.1138,
     "2023": 0.126,
     "2024": -0.021,
     "2025": -0.0643
    }
   },
   "budgets": {
    "5pct": {
     "precision": {
      "estimate": 0.1133,
      "lower": 0.0278,
      "upper": 0.1994,
      "spans_zero": false
     },
     "recall": {
      "estimate": -0.2429,
      "lower": -0.3741,
      "upper": -0.1236,
      "spans_zero": false
     },
     "matched_volume_precision": {
      "estimate": 0.0839,
      "lower": -0.0118,
      "upper": 0.1926,
      "spans_zero": true
     },
     "model_threshold": 0.1709,
     "climatology_threshold": 0.0833
    },
    "10pct": {
     "precision": {
      "estimate": -0.0551,
      "lower": -0.1556,
      "upper": 0.0676,
      "spans_zero": true
     },
     "recall": {
      "estimate": 0.0262,
      "lower": -0.0562,
      "upper": 0.1315,
      "spans_zero": true
     },
     "matched_volume_precision": {
      "estimate": -0.0221,
      "lower": -0.0906,
      "upper": 0.067,
      "spans_zero": true
     },
     "model_threshold": 0.0664,
     "climatology_threshold": 0.0765
    },
    "20pct": {
     "precision": {
      "estimate": -0.0543,
      "lower": -0.1072,
      "upper": -0.0046,
      "spans_zero": false
     },
     "recall": {
      "estimate": 0.05,
      "lower": -0.0085,
      "upper": 0.1207,
      "spans_zero": true
     },
     "matched_volume_precision": {
      "estimate": -0.0019,
      "lower": -0.0265,
      "upper": 0.0278,
      "spans_zero": true
     },
     "model_threshold": 0.0268,
     "climatology_threshold": 0.0221
    }
   }
  },
  "delta_vs": {
   "entry": "2026-10-08_florida_keys_coral_v2",
   "fields": {
    "n_test": {
     "was": 5595,
     "now": 5595,
     "change": 0.0
    },
    "n_positives": {
     "was": 840,
     "now": 840,
     "change": 0.0
    },
    "base_rate": {
     "was": 0.1501,
     "now": 0.1501,
     "change": 0.0
    },
    "auroc": {
     "was": 0.937,
     "now": 0.937,
     "change": 0.0
    },
    "auprc": {
     "was": 0.6903,
     "now": 0.6903,
     "change": 0.0
    },
    "brier": {
     "was": 0.1005,
     "now": 0.1005,
     "change": 0.0
    },
    "calibration_slope": {
     "was": 1.99,
     "now": 1.99,
     "change": 0.0
    },
    "climatology_auroc": {
     "was": 0.9194,
     "now": 0.9194,
     "change": 0.0
    },
    "climatology_auprc": {
     "was": 0.6012,
     "now": 0.6012,
     "change": 0.0
    },
    "persistence_auroc": {
     "was": 0.7505,
     "now": 0.7505,
     "change": 0.0
    },
    "persistence_auprc": {
     "was": 0.3583,
     "now": 0.3583,
     "change": 0.0
    },
    "trend_auroc": {
     "was": 0.7809,
     "now": 0.7809,
     "change": 0.0
    },
    "trend_auprc": {
     "was": 0.5201,
     "now": 0.5201,
     "change": 0.0
    },
    "base_rate_train": {
     "was": 0.0131,
     "now": 0.0131,
     "change": 0.0
    },
    "base_rate_validation": {
     "was": 0.0759,
     "now": 0.0759,
     "change": 0.0
    },
    "calibration_in_the_large_validation": {
     "was": -0.0453,
     "now": -0.0453,
     "change": 0.0
    },
    "calibration_in_the_large_test": {
     "was": -0.0974,
     "now": -0.0974,
     "change": 0.0
    },
    "lead_time": {
     "was": {
      "budget_rate": 0.1,
      "n_onsets": 105,
      "flagged_fraction": 1.0,
      "median_lead": 8.0,
      "threshold_from": "validation"
     },
     "now": {
      "budget_rate": 0.1,
      "n_onsets": 105,
      "flagged_fraction": 1.0,
      "median_lead": 8.0,
      "threshold_from": "validation"
     }
    },
    "split": {
     "was": "train 1986-2013 · val 2014-2018 · test 2019-2025, scored once; rolling origin 2014->2025; label-horizon embargo 8 wk at every boundary",
     "now": "train 1986-2013 · val 2014-2018 · test 2019-2025, scored once; rolling origin 2014->2025; label-horizon embargo 8 wk at every boundary"
    },
    "embargo_weeks": {
     "was": 8,
     "now": 8
    },
    "learner": {
     "was": "xgboost 3.4.1 · binary:logistic · depth 4 · eta 0.03 · early-stop logloss (100 rounds) · 108 trees · no scale_pos_weight · monotone on none",
     "now": "xgboost 3.4.1 · binary:logistic · depth 4 · eta 0.03 · early-stop logloss (100 rounds) · 108 trees · no scale_pos_weight · monotone on none"
    },
    "alert_budgets": {
     "5pct": {
      "precision": {
       "was": 0.7424,
       "now": 0.7424
      },
      "recall": {
       "was": 0.4357,
       "now": 0.4357
      },
      "n_alerts": {
       "was": 493,
       "now": 493
      },
      "realised_rate": {
       "was": 0.0881,
       "now": 0.0881
      },
      "threshold_from": {
       "was": "validation",
       "now": "validation"
      }
     },
     "10pct": {
      "precision": {
       "was": 0.5677,
       "now": 0.5677
      },
      "recall": {
       "was": 0.769,
       "now": 0.769
      },
      "n_alerts": {
       "was": 1138,
       "now": 1138
      },
      "realised_rate": {
       "was": 0.2034,
       "now": 0.2034
      },
      "threshold_from": {
       "was": "validation",
       "now": "validation"
      }
     },
     "20pct": {
      "precision": {
       "was": 0.4828,
       "now": 0.4828
      },
      "recall": {
       "was": 0.9202,
       "now": 0.9202
      },
      "n_alerts": {
       "was": 1601,
       "now": 1601
      },
      "realised_rate": {
       "was": 0.2861,
       "now": 0.2861
      },
      "threshold_from": {
       "was": "validation",
       "now": "validation"
      }
     }
    },
    "paired_intervals": {
     "auroc": {
      "delta_estimate": {
       "was": null,
       "now": 0.0176
      },
      "delta_lower": {
       "was": null,
       "now": -0.0193
      },
      "delta_upper": {
       "was": null,
       "now": 0.0618
      },
      "n_blocks": {
       "was": null,
       "now": 7
      }
     },
     "auprc": {
      "delta_estimate": {
       "was": null,
       "now": 0.0891
      },
      "delta_lower": {
       "was": null,
       "now": -0.0241
      },
      "delta_upper": {
       "was": null,
       "now": 0.1898
      },
      "n_blocks": {
       "was": null,
       "now": 7
      }
     }
    },
    "climatology_alert_budgets": {
     "5pct": {
      "precision": {
       "was": null,
       "now": 0.6291
      },
      "recall": {
       "was": null,
       "now": 0.6786
      },
      "realised_rate": {
       "was": null,
       "now": 0.1619
      }
     },
     "10pct": {
      "precision": {
       "was": null,
       "now": 0.6228
      },
      "recall": {
       "was": null,
       "now": 0.7429
      },
      "realised_rate": {
       "was": null,
       "now": 0.1791
      }
     },
     "20pct": {
      "precision": {
       "was": null,
       "now": 0.5371
      },
      "recall": {
       "was": null,
       "now": 0.8702
      },
      "realised_rate": {
       "was": null,
       "now": 0.2433
      }
     }
    }
   },
   "rolling_origin": {
    "2015": {
     "auroc": {
      "was": 0.9512,
      "now": 0.9512
     },
     "auprc": {
      "was": 0.7983,
      "now": 0.7983
     },
     "selected_on": [
      2014
     ],
     "n_trees": 108
    },
    "2016": {
     "auroc": {
      "was": 0.8994,
      "now": 0.8994
     },
     "auprc": {
      "was": 0.1897,
      "now": 0.1897
     },
     "selected_on": [
      2015
     ],
     "n_trees": 228
    },
    "2017": {
     "auroc": {
      "was": 0.9608,
      "now": 0.9608
     },
     "auprc": {
      "was": 0.1325,
      "now": 0.1325
     },
     "selected_on": [
      2016
     ],
     "n_trees": 114
    },
    "2018": {
     "auroc": {
      "was": 0.8414,
      "now": 0.8414
     },
     "auprc": {
      "was": 0.1312,
      "now": 0.1312
     },
     "selected_on": [
      2017
     ],
     "n_trees": 13
    },
    "2019": {
     "auroc": {
      "was": 0.9171,
      "now": 0.9171
     },
     "auprc": {
      "was": 0.381,
      "now": 0.381
     },
     "selected_on": [
      2018
     ],
     "n_trees": 14
    },
    "2020": {
     "auroc": {
      "was": 0.9642,
      "now": 0.9642
     },
     "auprc": {
      "was": 0.8079,
      "now": 0.8079
     },
     "selected_on": [
      2019
     ],
     "n_trees": 80
    },
    "2021": {
     "auroc": {
      "was": 0.9502,
      "now": 0.9502
     },
     "auprc": {
      "was": 0.3687,
      "now": 0.3687
     },
     "selected_on": [
      2020
     ],
     "n_trees": 177
    },
    "2022": {
     "auroc": {
      "was": 0.9206,
      "now": 0.9206
     },
     "auprc": {
      "was": 0.6791,
      "now": 0.6791
     },
     "selected_on": [
      2021
     ],
     "n_trees": 205
    },
    "2023": {
     "auroc": {
      "was": 0.9944,
      "now": 0.9944
     },
     "auprc": {
      "was": 0.9897,
      "now": 0.9897
     },
     "selected_on": [
      2022
     ],
     "n_trees": 110
    },
    "2024": {
     "auroc": {
      "was": 0.9347,
      "now": 0.9347
     },
     "auprc": {
      "was": 0.8032,
      "now": 0.8032
     },
     "selected_on": [
      2023
     ],
     "n_trees": 88
    },
    "2025": {
     "auroc": {
      "was": 0.9361,
      "now": 0.9361
     },
     "auprc": {
      "was": 0.806,
      "now": 0.806
     },
     "selected_on": [
      2024
     ],
     "n_trees": 156
    }
   }
  }
 },
 "provenance": {
  "metrics_file": "outputs/atlantis_core/metrics.json",
  "shap_file": "outputs/atlantis_core/shap_summary.json",
  "learner_swap_files": [
   "outputs/atlantis_core/learner_swap_logistic.json"
  ],
  "generated_by": "atlantis_core.board (emit → closed AtlEvaluation validated against the committed atl_ontology_v0.schema.json + assert_green); numbers are not retyped"
 },
 "notes": []
}
```

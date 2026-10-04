---
type: directory_index
doc_id: agents_what_datasets_atlantis
title: "what/datasets/ — dataset records (pointer + sha256 + fetch recipe; the exemplar's three snapshots are grandfathered)"
created: 2026-10-02
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [directory_index, datasets, atlantis, snapshot_rule]
---

# what/datasets/

**Snapshot rule (ADR-002 §4):** Atlantis adds **no new data snapshots**. A record here is a pointer + sha256 + fetch
recipe, written as the lattice-labs pair `dataset_<x>.md` + `dataset_<x>.dataset.yaml`
(`how/templates/template_dataset_pair/`). Instances hold the bytes.

| Record (pair) | Stream | Bytes here? |
|---|---|---|
| `dataset_fwc_hab_karenia.{md,dataset.yaml}` | `atl_stream_fwc_hab_karenia`: FWC HAB *K. brevis* counts 1970–2023 | **yes, grandfathered** (`fwc_hab_karenia_1970_2023.parquet`, 4.0 MB, public) |
| `dataset_oisst_region_daily.{md,dataset.yaml}` | `atl_stream_oisst_region_daily`: OISST v2.1 regional SST 1982-01-01 → 2024-01-01 | **yes, grandfathered** (`oisst_region_daily.parquet`, 1.0 MB, public) |
| `dataset_usgs_discharge_daily.{md,dataset.yaml}` | `atl_stream_usgs_discharge_daily`: USGS NWIS discharge, five gauges, 1990–2023 | **yes, grandfathered** (`usgs_discharge_daily.parquet`, 292 KB, public) |
| `dataset_hab_env_covariates.md` | *superseded 2026-10-03* by the OISST and USGS pairs (one location and one checksum per record) | (none) |

**The three parquets** are byte-identical copies of `what/exemplars/gulf_karenia_brevis/data/raw/`. They are the only
bytes this graph will ever carry. Each pin is written once per place, and every place agrees:
- the pair's `format.checksum`;
- the `.md`'s `sha256`;
- the exemplar's `streams.yaml` and `*_fetch_summary.json`;
- board v0 and v1 `data_pins`.

**Check** (from `what/atlantis_core/`): `.venv/bin/python -m atlantis_core.datasets --check ../datasets`. It runs the
lattice-labs `dataset_yaml_schema.json`, which Atlantis keeps as a byte-identical copy in
`how/templates/template_dataset_pair/`. It also checks that each checksum matches its bytes, and that each pair has its
Rule-5 provenance in `class_fields`, its stream id, and an `.md` that agrees. The pairs were migrated at M-1d-ii, after
the template itself was fixed against the schema it claimed (WI-18).

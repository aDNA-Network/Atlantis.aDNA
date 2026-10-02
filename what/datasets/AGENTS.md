---
type: directory_index
doc_id: agents_what_datasets_atlantis
title: "what/datasets/ — dataset records (pointer + sha256 + fetch recipe; the exemplar's three snapshots are grandfathered)"
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [directory_index, datasets, atlantis, snapshot_rule]
---

# what/datasets/

**Snapshot rule (ADR-002 §4):** Atlantis adds **no new data snapshots**. A record here is a pointer + sha256 + fetch
recipe, written as the lattice-labs pair `dataset_<x>.md` + `dataset_<x>.dataset.yaml`
(`how/templates/template_dataset_pair/`). Instances hold the bytes.

| Record | Stream | Bytes here? | Standard |
|---|---|---|---|
| `dataset_fwc_hab_karenia.md` | FWC HAB *K. brevis* counts 1970–2023 | **yes — grandfathered** (`fwc_hab_karenia_1970_2023.parquet`, 4.0 MB, public) | ad-hoc frontmatter → pair migration **P1 M-1d** |
| `dataset_hab_env_covariates.md` | OISST regional SST · USGS discharge | **yes — grandfathered** (`oisst_region_daily.parquet` 1.0 MB · `usgs_discharge_daily.parquet` 292 KB, public) | ad-hoc → pair migration **P1 M-1d** |

The three parquets are byte-identical copies of `what/exemplars/gulf_karenia_brevis/data/raw/`; their sha256 pins
are recorded in `what/board/entries/2026-09-23_gulf_karenia_brevis_v0.json → evaluation.data_pins`. They are the
only bytes this graph will ever carry.

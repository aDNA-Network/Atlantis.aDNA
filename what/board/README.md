---
type: directory_index
doc_id: atl_board_readme
title: "what/board/ — the Atlantis evidence board (GREEN metrics only · NO ACCURACY CLAIM)"
status: draft
schema: atl_board_entry_v1
created: 2026-10-02
updated: 2026-10-03
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning   # BOARD.md generator + --entries: mission_m1d_ii_lattice_and_registries
precedent: RareArchive.aDNA/what/board/ (ra_board_entry_v1, GREEN-only, promotion-to-gold is human)
tags: [board, evidence, metrics, green, atlantis, m0]
---

# The evidence board

> ⛔ **THIS BOARD MAKES NO ACCURACY CLAIM.** Every entry is a *method demonstration* unless its `claim` field cites
> an instance owner's written ruling. Entries are comparable **against their own base rates** and at **stated alert
> budgets**; a bare AUROC is not a result here. The board exists so that stewards can compare *how the method behaved*
> across ecosystems **without any data moving** (thesis T10).

## What an entry is

One JSON file per evaluation in `entries/<run_date>_<instance_or_exemplar>_v<n>.json`, schema **`atl_board_entry_v1`**:
an `AtlEvaluation` (`what/schema/atl_v0/`) wrapped with board metadata. Required fields, in prose until M-1c
renders the schema:

| Field | Rule |
|---|---|
| `tier` | always `GREEN` — metrics and declarations only; nothing a steward would need consent to share |
| `accuracy_claim` | the literal `NONE — …` line; present in every entry |
| `source` | `exemplar` \| `instance` |
| `instance`, `method_version`, `recorded_by`, `recorded_at`, `run_date` | provenance of the entry itself |
| `evaluation.base_rate` | **required** — a score without its base rate is rejected |
| `evaluation.climatology_auroc` | required from M-1b on (T11) |
| `evaluation.alert_budgets[]` | ≥ 1 from M-1b on (T6) |
| `evaluation.ablations[]` | surveillance ablation required where a surveillance channel is declared (T5) |
| `evaluation.config_hash`, `evaluation.data_pins[]` | the join keys to the instance's run; every pin carries a sha256 |
| `evaluation.claim` | `method_demonstration` (default) \| `operational_by_owner_ruling` (+ `owner_ruling_ref`) |
| `evaluation.limitations_ref` | required — no evaluation without its limits (SO-4) |

**Never on the board:** per-patient predictions or SHAP values · observations or labels · coordinates of partner or
human-subject sites · trained binaries · credentials · anything from an instance whose data posture ruling forbids
it. If a field would carry one of these, the entry is wrong, not the rule.

## Lifecycle

1. An instance (or the exemplar) produces `outputs/metrics.json` + `shap_summary.json`; `atlantis_core` (P1)
   emits the entry **by code** — numbers are never retyped. The M-0 exemplar entry was generated the same way by a
   sitting script (see its `provenance` block).
2. The entry travels to Atlantis as a coordination memo (`who/coordination/inbox/`); Proteus lands it by a dated
   commit after checking the required fields.
3. `BOARD.md` is **regenerated** from `entries/` by `python -m atlantis_core.board --index` (M-1d-ii); it is never
   hand-edited, and `--index --check` fails when it is stale. The generator refuses to render if any entry fails its
   checks — closed `AtlEvaluation` (or the one grandfathered open shape, pinned by id **and** sha256), GREEN,
   `assert_green`, the required minimum above. An instance keeps its own board the same way:
   `board --instance <dir> … --entries <dir>/what/board/entries`, then `board --index --entries …`.
4. **Promotion to a `gold/` set** (entries that anchor a thesis claim) is a **human act** — the operator's or, at
   P4, the steward council's. Nothing promotes itself.
5. Entries are never deleted (SO-2); a superseded entry gets `superseded_by`.

## Contents

**→ [`BOARD.md`](BOARD.md)** — generated from `entries/` (the JSON is authoritative). Regenerate from `what/atlantis_core/`:

```
.venv/bin/python -m atlantis_core.board --index            # writes ../board/BOARD.md
.venv/bin/python -m atlantis_core.board --index --check    # exit 1 if stale; writes nothing
```

v0 (`2026-09-23_gulf_karenia_brevis_v0`) is shown and labelled **open shape**. The M-0 sitting script wrote it before the
closed shape existed. It is the only open entry the generator accepts, and only as its pinned bytes (WI-8 closed
2026-10-03). From v1 on, entries are emitted by `python -m atlantis_core.board`: the `evaluation` is the closed
`AtlEvaluation`, and everything else sits in `evaluation_extras`.

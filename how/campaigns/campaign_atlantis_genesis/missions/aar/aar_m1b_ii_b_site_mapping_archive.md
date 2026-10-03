---
type: aar
doc_id: aar_m1b_ii_b_site_mapping_archive
title: "AAR — M-1b-ii-b atlantis_core site · mapping · archive (P1, Operation Tidewatch)"
mission: mission_m1b_ii_b_site_mapping_archive
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: opus
token_budget_estimated: "~150kT main + fresh-context III reviewer (build-sized)"
token_budget_actual: "≈165kT main context (≈ +10%, under the +50% trip) + ≈275kT fresh-context III reviewer"
session: session_stanley_20261003_191346_m1b_ii_b_site_mapping_archive
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [aar, m1b_ii_b, p1, atlantis_core, site, mapping, archive, iii, atlantis, tidewatch]
---

# AAR — M-1b-ii-b `atlantis_core` site · mapping · archive

**Commits:**

| Commit | Content |
|---|---|
| `d0d0c14` | open |
| `19d3adb` | ② `atlantis_core.site` |
| `36ae52a` | ③a copy moved verbatim |
| `cf9b84a` | ③b copy corrected for v1, page, site tests |
| `8ec06a4` | ④ mapping template + checker |
| `c90f11d` | ⑤ `src/hab` archived |
| `dc8763a` | ⑥ III fixes |
| close | bookkeeping |

**Operator rulings (AskUserQuestion):**
1. Copy is a port plus v1 corrections only.
2. T2 is a compact panel in §07.
3. The core page is committed beside v0.
4. After the review (F-5): record a capped exception, drafted as ADR-002 **A-1, proposed**, for the operator to ratify.

## Acceptance (card)

| Criterion | Evidence |
|---|---|
| `site/` template, all copy parameterised | `atlantis_core/site/` holds template, assemble and build. The template carries structure, style and generic renderers only; a literal guard holds it free of exemplar words, and it caught a real leak on its first run. The exemplar's words are `site_copy.yaml`; what to draw is `site.yaml`, which sits outside `atlantis.yaml` because board v1 pins that file's bytes-md5. Site data is assembled from `outputs/atlantis_core/`, `data/processed/atlantis_core/` and the registries, never from `hab`, in ~2 s |
| Exemplar page regenerated from board v1's run; v0 kept | `site/gulf_karenia_brevis_v1.html`. The build re-projects the run through the board projector and refuses any field that disagrees with the entry. Browser-checked over a local server: 24/24 charts render, every binding resolves, both themes work, grey bands are drawn. `site/hab_crash_risk.html` and its template are byte-stable |
| `template_mapping_atl.yaml` | Registries map to the five `atl_` labels via the identifier slots, plus six declared edges from atl_v0's ref slots. Bi-temporal stamps have pinned values. The fence covers 7 table shapes, path globs, coordinate properties and pointer-only slots. `python -m atlantis_core.mapping --check` holds it to the LinkML schema (contract item 11), with 28 planted defects each caught |
| `src/hab/` archived in place; `config.yaml` / `metrics.json` byte-stable | `src/hab/ARCHIVED.md` has a per-module table of what still runs; the docstring carries a banner; the README run order goes through the core. `git diff 4bb1939` over config · atlantis.yaml · outputs · v0 page and template · board entries · schema is **empty** |
| III review via `iii/`, fresh context | PASS-WITH-FINDINGS: 4 major and 6 minor, **all addressed** (F-5 by a proposed amendment, F-6 carried by design). Learning store: C-004 and C-009 +1; C-011…C-013 new |

`what/atlantis_core`: **183 tests**, offline (125 + 30 site + 28 mapping). Both SO-7 self-tests are green; the exemplar's 11 tests pass.

## Worked

- **Move, then change, as two commits.** A script moved the prose, and the move was verified at text-node level: 366/366
  nodes plus the 3 captions. Only then were corrections applied, as asserted find-and-replace edits. Every change to what
  the page says is one reviewable diff.
- **Refusals carry the weight.** The build refuses outputs that disagree with the entry the page cites. The page cannot
  silently say something other than its board entry.
- **The browser was the oracle for the drawing**, and a test was the oracle for the data. Each found what the other could not.

## Didn't

- **The first guards were narrower than their names (C-009, again).**
  - A "net" test passed on gross sums.
  - `board_check` read 5 fields.
  - The mapping checker's minimum was weaker than the template it guards, and ran on unnormalised paths (C-013).
  - The Python validator accepted what the JS renderer cannot read (C-012).

  The reviewer demonstrated each one. This is the third mission running in which the producer wrote checks and believed them.
- **A verbatim move preserves falsehoods (C-004).** "The confident true positive with the longest lead" was never the
  rule, in v0 or now. Moving prose verbatim proves only that it moved.
- **The grey bands had been invisible since v0 (C-011).** The data test was right and the drawing was wrong. My own browser
  pass checked that charts *exist*, not that each mark the copy names is drawn.

## Finding

1. **The page is now a view of a board entry.** Every number traces to the run that entry records and is checked
   field for field at build time. "The page says what the board says" is a refusal, not a convention.
2. **`hab` is still the fetch path.** `atlantis_core.fetch` has fetcher classes but no entry point. Archiving `hab` "in
   place" is honest only with that said. M-1d's pipeline lattice `fetch` step is the natural home for it.
3. **v0's EDA summary was stale against its own region rules.** Per-region counts differ (for example Atlantic 7,039 →
   18,418). v1 matches the M-1a frozen counts, and the patient grid the model reads is identical. Now disclosed on the page.
4. **The exemplar pages sit outside ADR-002 §4 as written.** Proposed A-1 reconciles the operator's ruling with the rule:
   exemplar-only, derived from the public parquets, rebuildable, never an instance page.
5. **Tampa's what-if scales only a non-lever gauge.** The page now says so in those words and names the river.

## Change

- **A visual claim needs a drawn-mark check (C-011).** When copy names a mark (a band, a line, a diamond), the browser pass
  asserts that mark, not only the chart.
- **One grammar, enforced on both sides (C-012).** Whatever the renderer cannot read, the validator refuses.
- **A checker's minimum is the template it guards (C-013).**

## Follow-up

- **M-1d** (opus): fork skill, pipeline lattice (with a core `fetch` step, Finding 2), BOARD generator (WI-8),
  `mapping.yaml` via the template. The dry-run instance is the first `--check` of a forked mapping.
- **Board v2** (with the F-8 fix): `limitations_ref` → `site/gulf_karenia_brevis_v1.html#limits` (III F-6; v1 is
  byte-stable and points at the v0 page, which lacks v1's limits).
- **ADR-002 A-1:** operator ratification, at the P1 gate or before.
- **Neo4j allow-list admission** for the five labels and six edges: a coordination memo after the gate (peer vault is read-only).
- **Template:** English method vocabulary stays in the template (disclosed, III F-10). Localise when a non-English steward arrives.

---
type: archive_notice
status: superseded
superseded_by: what/atlantis_core (Atlantis reference implementation)
archived: 2026-10-03
archived_by: agent_proteus
mission: mission_m1b_ii_b_site_mapping_archive   # fetch row updated at mission_m1d_i_fork_and_conformance
tags: [archive, hab, exemplar, atlantis_core, so2]
---

# `src/hab/` — archived in place (SO-2: archive, never delete)

`hab` is the S329 pilot (2026-09-23) that built this exemplar and **board v0**. Since M-1b-ii-b, **nothing canonical runs
through it**: vitals, label, eval, explanation, what-if, board and site are `atlantis_core` over this directory's registries
(`streams.yaml` · `features.yaml` · `events.yaml` · `atlantis.yaml` · `site.yaml` · `site_copy.yaml`). Board v1 and
`site/gulf_karenia_brevis_v1.html` are its outputs.

| `hab` module | Superseded by | Still run? |
|---|---|---|
| `build_features` · `regions` · `eda` | `atlantis_core.vitals` · `grid` · `label` · `site.assemble` | yes, only to regenerate `data/processed/` for the core's **port-equivalence tests** (`test_equivalence` · `test_eval` · `test_explain`), which compare the core with `hab` on `hab`'s own tables |
| `train` · `explain` · `whatif` | `atlantis_core.eval` · `explain` · `explain.whatif` · `run` | the same, plus the v0 negative control (`--negative-control`) |
| `export_site_data` · `build_site` (+ `site/template.html`) | `atlantis_core.site` (+ `site.yaml` · `site_copy.yaml`) | only to rebuild the v0 page, `site/hab_crash_risk.html`, which is kept |
| `fetch_fwc` · `fetch_env` · `provenance` | `atlantis_core.fetch` — `python -m atlantis_core.fetch --instance …` since **M-1d-i** (gated on the self-test receipt; `--verify` re-hashes the pins) | only as the recipe that produced the committed bytes. A core re-fetch writes new bytes (writer and column order), so it would be a new pin, not a reproduction. A live core fetch against these endpoints has not been run (M-1d-i was offline) |

Byte-stable and kept: `config.yaml`, `outputs/*.json` (v0), `site/template.html`, `site/hab_crash_risk.html`, board v0.
Do not edit `hab` to change a result; change the registries and rerun the core. The run order for v0 reproduction is in
`../../README.md` §Archived.

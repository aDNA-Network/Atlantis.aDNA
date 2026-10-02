---
type: session
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [session, m1a, p1, hygiene, fable, atlantis, tidewatch]
session_id: session_stanley_20261002_143344_m1a_exemplar_hygiene
user: stanley
started: 2026-10-02T21:33:44Z
status: completed
executor_tier: fable   # card says opus; operator ruled "run here" 2026-10-02
token_budget_estimated: "40-60kT"
token_budget_actual: "~220kT"
mission: mission_m1a_exemplar_hygiene
campaign: campaign_atlantis_genesis
intent: "M-1a exemplar hygiene: README/config drift, sha256 fetch summaries for all three streams, pyproject+uv.lock, gauges.*.lever read by code, safe region-rule parser, AUPRC-stopping negative control. config.yaml and outputs/metrics.json byte-stable. No what/schema (M-1c), no extraction (M-1b)."
files_modified: "[what/exemplars/gulf_karenia_brevis/{README.md, AGENTS.md, src/hab/{regions,fetch_fwc,fetch_env,export_site_data,whatif,train}.py, data/raw/fwc_fetch_summary.json, site/{template,hab_crash_risk}.html}, STATE.md, CHANGELOG.md, MANIFEST.md, missions/mission_m1a_exemplar_hygiene.md]"
files_created: "[what/exemplars/gulf_karenia_brevis/{pyproject.toml, uv.lock, .python-version, src/hab/provenance.py, tests/test_regions.py, data/raw/{oisst,usgs}_fetch_summary.json, outputs/negative_control_auprc_stop.json}, missions/aar/aar_m1a_exemplar_hygiene.md]  # requirements.txt removed"
completed: 2026-10-02T21:46:45Z
---

## Activity Log

- 14:33 — Session started (fable, operator-opened). Plan approved: ~/.claude/plans/please-read-the-claude-md-cozy-sparrow.md. Rulings: run M-1a here at fable; M-1a only this sitting.
- 14:33 — Lease; card active; baseline: self-test ✅ · metrics md5 3f910c55… · config md5 979d3fdf16 · 9 region counts frozen under the `eval` implementation. Commit 173613e.
- 14:3x — regions.py → ast whitelist + vectorised first-match; tests/test_regions.py. provenance.py + fetcher hooks; three fetch summaries (sha256 == board pins == what/datasets copies). pyproject/uv.lock (uv sync removed matplotlib stack, added pytest; step hit the 300 s tool timeout → background; verification re-run by hand). lever tag from config; whatif lever_gauges. train --negative-control → 2 trees, slope 18.09 (T4). README/AGENTS/site drift edits.
- 14:4x — Verification: 11 tests pass · self-test ✅ root + src · counts identical · ALL PINS CONSISTENT · 22 README figures == outputs · board entry ALL MATCH · no eval/compile · gitleaks no leaks · metrics.json + config.yaml byte-stable. Commits 3535889 · b80b03d · 3121789 · 9ff49a9 · 47c5ab1 · 41d324b.
- close — AAR filed; card completed; STATE → M-1c prompt; CHANGELOG v0.2.1; session → history/2026-10/.

## SITREP

**Completed**: M-1a — all 7 acceptance items checked by command (AAR table). Exemplar is a trustworthy reference for M-1b extraction: numbers match outputs, every raw artifact hashed, package installs, no `eval`, T4 control on disk.
**In progress**: none.
**Next up**: M-1c (opus) — STATE § ⏭ QUEUED carries the self-contained prompt. Then M-1b (depends on M-1a ✅), M-1d, P1 gate.
**Blockers**: none. (`#needs-human` only at the P1 gate.)
**Files touched**: `git log 8229737..HEAD --stat`.
**Finding of record**: `config_hash e9dea88254` = training-time config with `shap.background_n: 2000`; live `979d3fdf16`; WI-7 until M-1b.

## Next Session Prompt

See `STATE.md` § ⏭ QUEUED (M-1c, opus).

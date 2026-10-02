---
type: aar
doc_id: aar_m1a_exemplar_hygiene
title: "AAR — M-1a Exemplar hygiene (P1, Operation Tidewatch)"
mission: mission_m1a_exemplar_hygiene
campaign_id: campaign_atlantis_genesis
status: completed
executor_tier: fable          # carded opus; operator ruled "run here" at session open
token_budget_estimated: "40-60kT"
token_budget_actual: "~220kT (fable; roughly half was plan-mode orientation, incl. one 27 kT read of metrics.json)"
session: session_stanley_20261002_143344_m1a_exemplar_hygiene
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
tags: [aar, m1a, p1, hygiene, exemplar, atlantis, tidewatch]
---

# AAR — M-1a Exemplar hygiene

**Commits:** `173613e` (open) · `3535889` ② parser · `b80b03d` ③ provenance · `3121789` ④ packaging · `9ff49a9` ⑤ lever · `47c5ab1` ⑥ drift · `41d324b` ⑦ negative control · close commit (bookkeeping).
**Invariants held:** `config.yaml` untouched (md5 prefix `979d3fdf16` before and after) · `outputs/metrics.json` byte-identical (`3f910c55f635fbf11a4ca148052562b7`) · self-test green at open and close · `gitleaks` no leaks (219 MB scanned) · 192 KB of new text, no binaries.

## Acceptance checklist — how each item was checked

| Criterion | Evidence |
|---|---|
| README §Design says log-loss + 1000 rows; site heading honest | README rows rewritten; site §02 → "Three public data streams, plus the calendar" (template + built page, identical literal edit). Script check: 22 README figures == `metrics.json` / `shap_summary.json` / control JSON — ALL MATCH. |
| `*_fetch_summary.json` × 3 with rows · dates · fetched_at · sha256 | `hab.provenance`; sha256s == live bytes == board `data_pins` == `what/datasets/` copies (script, ALL PINS CONSISTENT). FWC server-count assert kept. |
| `pyproject.toml` + `uv.lock`; `python -m hab.*` runs; matplotlib dropped | `uv lock && uv sync` rc 0; self-test runs from root **and** `src/`; `requirements.txt` removed (git history keeps it); pillow/pyparsing/matplotlib gone from the venv. |
| `gauges.*.lever` read by code | `export_site_data.discharge_tag(cfg)` → `lever`/`proxy` sets the three discharge tags; `whatif` records `lever_gauges` and asserts one exists. Checked: live config → `lever`; all-false → `proxy`. |
| Safe region parser; 9 counts unchanged | `ast` whitelist (`lat`/`lon`, comparisons, and/or, numeric/bool literals, unary minus); vectorised first-match. `tests/test_regions.py` — 11 passed; counts 15,992 · 6,341 · 2,686 · 32,893 · 56,108 · 20,190 · 30,563 · 12,833 · 18,418 = 196,024, none unassigned, identical to the `eval` baseline captured at open. |
| AUPRC-stopping negative control recorded | `python -m hab.train --negative-control` → `outputs/negative_control_auprc_stop.json`: **2 trees**, test AUROC 0.877 / AUPRC 0.423 / Brier 0.0705, **calibration slope 18.09** (reference 141 trees, 1.17). In-memory override only. |
| Self-test before/after; `metrics.json` unchanged | ✅ both; md5 identical; `git status outputs/` shows only the new control file. |

## Worked

- Reconstructing the hash **before** touching anything: `md5(config.yaml with shap.background_n: 2000)` = `e9dea88254` exactly. That turned "the hash is wrong" into "the hash is the training-time file; one SHAP-only line moved afterwards" and removed any temptation to retrain or edit config.
- Freezing the nine region counts under the *old* `eval` implementation first, then asserting them in pytest against the new parser — the equivalence proof cost one script.
- Hygiene as pure additions: every change is new code, new JSON, or doc text; nothing the model reads moved.

## Didn't

- Budget: carded 40–60 kT at opus; actual ~220 kT at fable. Roughly half went to orientation reads (one of them the whole 27 kT `metrics.json` when a `Grep` would have done) and to plan mode. The > 50 % escalation trigger fired in spirit; the operator had opened the sitting at fable knowingly, so the lane ran to completion rather than stopping to re-card.
- The uv packaging step was pushed to background by a 300 s tool timeout and its shell never returned; the verification it was meant to print was simply re-run. Harmless, but the step should have been split.
- The site page (`hab_crash_risk.html`) was hand-edited identically to the template rather than rebuilt, to avoid regenerating `site_data.json` (a `generated` timestamp churn). Correct here because `build_site` is a pure injection; an instance should rebuild.

## Finding

1. **A bytes-hash of a config file is a bad join key.** It moves on comments and on sections the model never sees. `metrics.json`, the board entry and the thesis register all carry `e9dea88254`, which no committed file hashes to. `atlantis_core` must hash the *parsed, training-relevant* sections (target · split · xgb · regions · gauges · stream list) and record both.
2. **Provenance was two-thirds absent**: OISST and USGS had no fetch record at all; their `fetched_at` is now the file mtime and the summary says so. The pattern "fetcher writes the summary at download time" belongs in the stream registry contract (M-1b/M-1d).
3. **T4 holds on reproduction**: AUPRC early-stopping stops at tree 2 with a slope of 18. The register's "≈18" is now a number in a file.
4. `lever:` had been a declared-but-unread flag — exactly the class of drift the instance contract's conformance-by-mapping is meant to catch (a declaration with no code reading it).

## Change

- Exemplar now has `tests/`, `pyproject.toml`/`uv.lock`, `hab.provenance`, a `--negative-control` flag, and a README §Provenance. `AGENTS.md` warns against casual `config.yaml` edits.
- Card discipline: a fable-run opus lane records its actual tier in the session and AAR frontmatter (done here).

## Follow-up

- **M-1b:** semantic `config_hash` (parsed training-relevant sections) + bytes hash side by side; `vitals --self-test` perturbing *every* stream (already carded); stream registry requires a fetch summary with sha256 at download time.
- **M-1c:** untouched by this mission; next queued (see STATE).
- **WI-7 (new):** until M-1b, the recorded hash `e9dea88254` ≠ any committed `config.yaml`; README §Provenance is the explanation of record.
- Not done, deliberately: rebuilding the site, retraining, editing `config.yaml`, touching `what/schema/` or `what/board/entries/`.

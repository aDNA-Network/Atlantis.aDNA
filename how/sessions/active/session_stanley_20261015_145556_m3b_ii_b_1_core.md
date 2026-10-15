---
type: session
created: 2026-10-15
updated: 2026-10-15
last_edited_by: agent_proteus
tags: [session, m3b, m3b_ii_b, m3b_ii_b_1, p3, qc_mask, station_offsets, scan, fknms, atlantis, tidewatch]
session_id: session_stanley_20261015_145556_m3b_ii_b_1_core
user: stanley
started: 2026-10-15T21:55:56Z
completed: ""
status: active
executor_tier: opus
mission: m3b_ii_b_1
campaign: campaign_atlantis_genesis
intent: "M-3b-ii-b split at open → ii-b-1: core 0.11.0 — stream mask_columns · station_offsets (era-fitted, R7) · station_windows · atlantis_core.scan (val only) · FKNMS declaration + self-test + descriptive calm table · III. Plan: ~/.claude/plans/please-read-the-claude-md-refactored-petal.md"
---

## Activity Log

- open — leases probed: Atlantis and FKNMS `how/sessions/active/` empty. Atlantis HEAD `ea83c88`, FKNMS `6dfd713`, both clean.
  Code read: `normalise` drops flag columns; `_to_units` is a raw station mean; `run` → `_fit_main` always scores test.
  Rulings (AskUserQuestion, 2026-10-15, at open; obligation 6): **(1) QC mask = `qc_low_ratio` only** (`qc_stuck` kept: an
  identical ≥ 6 h run can be true calm; 73 station-days a recorded limit) · **(2) station offsets fitted on train only vs
  SANF1, SMKF1 cut after its 2016–17 gap** (no train overlap to fit a post-gap offset); SANF1-only the sensitivity ·
  **(3) split ii-b** → ii-b-1 (core: mask · offsets · val-only scan) + ii-b-2 (vitals · scan · v4 · SHAP · write-up).

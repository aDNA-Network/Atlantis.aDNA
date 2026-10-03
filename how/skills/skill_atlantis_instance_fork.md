---
type: skill
skill_type: agent
created: 2026-10-03
updated: 2026-10-03
status: draft
category: setup
trigger: "A marine steward wants to build an early-warning model for THEIR ecosystem with the Atlantis method — 'fork an Atlantis instance', 'start a <region> instance', P2 M-2, P4's first outside steward"
last_edited_by: agent_proteus
mission: mission_m1d_i_fork_and_conformance
tags: [skill, atlantis, instance, fork, interview, contract_v0_2, so7, tidewatch]

requirements:
  tools: ["Bash", "AskUserQuestion"]
  context: ["Atlantis.aDNA/CLAUDE.md", "how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md", "how/templates/template_instance/README.md"]
  permissions: ["create <Instance>.aDNA via skill_project_fork", "write the instance's declarations", "NO network until the self-test receipt exists and the posture ADR is ratified"]
---

# Skill: Atlantis instance fork

## Overview

This skill forks one steward's regional instance of the Atlantis method in one sitting. Atlantis supplies the method, the
`atl_v0` ontology, `atlantis_core` and the templates. The instance is data-bearing and owns its data, its rulings and its
partners. The fork produces an `<Instance>.aDNA` vault whose declarations conform to **instance contract v0.2.0**, with the
**self-test green before any real data is fetched**, which is the P1 exit bar. This skill fetches nothing. The fetch comes
at the end, only after two gates: a self-test receipt for the current config, and a ratified posture ADR.

**Proteus's first question is the interview:** *what is the patient, what is the event, and how much warning would change
what you do?*

## Trigger

```
/skill_atlantis_instance_fork            # interactive: the interview
/skill_atlantis_instance_fork answers=<path/to/answers.yaml>   # resume from recorded answers
```

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `answers` | path | no | — | A recorded interview (shape: `how/templates/template_instance/answers.example.yaml`). Skips step 1 |
| `target` | path | no | `~/aDNA/<Vault>.aDNA` | Where the vault is created. `skill_project_fork` hard-wires the workspace root, so for a rehearsal (scratchpad) run its step 3 by hand with this path |

## Requirements

- `Atlantis.aDNA/what/atlantis_core` synced: `cd what/atlantis_core && uv sync`. Below, `A=<Atlantis.aDNA>/what/atlantis_core`.
- `gitleaks` on PATH (contract item 12; absent gitleaks fails the item rather than passing it silently).
- **No credentials** during the fork. A stream that needs one names it, and the Home broker supplies it at fetch time.
  Never write a value into the instance (fleet credential doctrine).

## Steps

### 1. The interview → `answers.yaml`

Ask in this order, in the steward's words first. Record each answer verbatim under `interview:`, then turn it into the
structured fields.

| # | Question | Becomes |
|---|---|---|
| 1 | **What is the patient?** What unit do you manage, and on what clock? | `patient.unit_kind` (atl_v0 `UnitKind`) · `time_step: iso_week` · `grid` (a polygon file **in the instance**, a WDPA export, or cells; coordinate rules only under a public posture) · `units[]` |
| 2 | **What is the event?** Which variable, which threshold, which direction? | `event.{stream, threshold, unit (UCUM), direction above\|below, onset_rule}` |
| 3 | **How much warning would change what you do?** | `event.horizon` in weeks, plus the recorded sentence, which lands in `events.yaml` |
| 4 | **What streams exist?** For each: who publishes it, its id there, its licence, how often, and whether *where people look* reacts to what they saw (a surveillance channel) | `streams[]` (modality · source_system · source_id · authority CURIE · licence · fetcher · shape · columns · stations) · `surveillance` |
| 5 | **What is the data posture?** Public, partner, or human-subject (Network ADR-016 §8)? | `posture.{class, rationale}` |
| + | Which of these can someone actually change, and who? | `streams[].vitals.tag: lever` + `owner` (R4) |
| + | Train, validation and test years? | `split`. The test window is scored once |

Use `AskUserQuestion` for bounded choices (unit kind, direction, posture class, modality). Free text for the rest. Stop
and escalate if:
- a licence or posture is unclear → a memo to the instance owner; that stream is left out, not guessed (card trigger);
- the steward's data is partner or human-subject → the posture ADR must be ratified **before** step 6, and
  `data/` · `outputs/` · `site/` are gitignored by the fork;
- the event cannot be stated as one threshold on one stream → it is a second event, and a second model (T12).

Pick **≥ 2 self-test patients** every stream reaches. A point stream also needs a lat/lon *inside* each patient's polygon.

### 2. The vault shell

Run `how/skills/skill_project_fork.md` with `project_name = <Vault>` (e.g. `ChesapeakeHypoxia`). It copies `.adna/` and
stamps MANIFEST · STATE · CLAUDE · AGENTS. For a rehearsal outside the workspace root, run its step 3 commands by hand
into `target`. Put the steward's geometry file at the path `patient.grid.path` names, **inside the vault**. Atlantis never
holds a polygon.

### 3. Fork the declarations

```
$A/.venv/bin/python -m atlantis_core.fork --answers answers.yaml --out <vault>
```

Writes:
- `atlantis.yaml` · `units.yaml` · `streams.yaml` (declared) · `features.yaml` (starter vitals) · `events.yaml` · `mapping.yaml`;
- `who/governance/adr_<nnn>_data_posture.md` (proposed);
- `how/federation/atlantis/CLAUDE.md` (the `federation_ref`, `source_commit` pinned to Atlantis HEAD);
- a `.gitignore` block.

It runs registry R1–R8 on the result. A refusal lists every reason and writes nothing. Fix the answers and re-run. **Do
not** hand-edit around a refusal, and never patch `atlantis_core` from the instance: a template change is a memo to
Atlantis (contract §D).

### 4. Hold it to the contract (declared stage)

```
$A/.venv/bin/python -m atlantis_core.mapping --check <vault>/mapping.yaml
$A/.venv/bin/python -m atlantis_core.conform --instance <vault> --stage declared
```

`conform` prints one ✅/✗ per contract item and names the files it read. Items 9 and 10 are n/a until a run. Item 6
**re-runs the self-test** on the synthetic world, so a ✅ there is earned, not read off a receipt.

### 5. Earn the fetch (SO-7)

```
$A/.venv/bin/python -m atlantis_core.selftest --instance <vault>      # writes outputs/atlantis_core/selftest_receipt.json
```

The receipt carries the config's `semantic_hash`. Any later change to vitals, label or grid invalidates it, and the fetch
CLI refuses until the self-test is re-run. Then review with the steward:
- every `tag` (starter tags are placeholders; **a SHAP value is never a cause**);
- the default alert budgets, against what they can actually staff;
- the starter vitals, which are not a model.

### 6. Ratify, then fetch

The instance **owner** signs the posture ADR's 4-field block (status `ratified`). Then:

```
$A/.venv/bin/python -m atlantis_core.fetch   --instance <vault>        # refuses without the receipt, and under an unratified posture
# record the printed sha256 · row_count · ingested_at · pipeline_version in streams.yaml (the CLI never edits it)
$A/.venv/bin/python -m atlantis_core.fetch   --instance <vault> --verify
$A/.venv/bin/python -m atlantis_core.conform --instance <vault> --stage fetched
```

A stream whose fetcher is **declared, not built** (NDBC · OBIS · GBIF · CRW today) stops here with that message. Building
it is an Atlantis template change (P2 rule), done there, never inside the instance.

### 7. Commit and hand over

Commit with path-scoped `git add` (never `-A`). Under a partner or human-subject posture, confirm that `git status` shows
nothing under `data/`, `outputs/` or `site/`. In the steward's STATE, record what was forked, at which Atlantis commit, and
which contract items are green. The next work is the run (`atlantis_core.run` → `board` → `site`), the M-1d-ii pipeline lattice.

## Outputs

`<Instance>.aDNA` with declarations that conform to contract v0.2.0 at the declared stage, a self-test receipt, and a
posture ADR awaiting the owner's ratification. No data, until step 6.

## Known limits

- **Starter vitals are scaffolding.** They let the self-test run before any data exists; they are not features anyone
  should train on unreviewed.
- **The self-test synthesises event values against a positive threshold**, and refuses a threshold ≤ 0.
- **ISO weeks only.** `atl_v0` lists day, fortnight, month and cruise; `atlantis_core` builds weeks.
- **`skill_project_fork` writes to the workspace root.** A rehearsal elsewhere runs its copy step by hand.
- **Unit codes link `units.yaml` to the grid by the `atl_unit_<slug>_<code>` suffix.** A steward who renames ids must
  keep the suffix.

## Rehearsal of record

M-1d-i (2026-10-03): a fictional hypoxia instance was forked in a scratchpad from templates alone and passed contract
items 1–8 and 11–12 with no network. The transcript is in `how/campaigns/campaign_atlantis_genesis/missions/aar/aar_m1d_i_fork_and_conformance.md`.

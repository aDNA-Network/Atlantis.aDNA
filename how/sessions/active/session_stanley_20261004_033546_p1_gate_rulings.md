---
type: session
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [session, p1_gate, rulings, adr_002, contribution_guide, iii, m2, atlantis, tidewatch]
session_id: session_stanley_20261004_033546_p1_gate_rulings
user: stanley
started: 2026-10-04T03:35:46Z
status: active
executor_tier: opus
mission: p1_gate
campaign: campaign_atlantis_genesis
intent: "Record the operator's P1-gate rulings (asked via AskUserQuestion after an opus decision brief; the charter's fable first-hand verification was offered and not required by the operator): conditional GO for P2 · ADR-002 A-1 ratified · contribution guide ratified + clarified · C-004/C-009 graduation memo to III.aDNA. Card the F-8 condition lane; re-card M-2 → M-2a/M-2b. Push only if separately ruled."
---

## Activity Log

- open — Decision brief (plan ~/.claude/plans/please-read-the-claude-md-vectorized-anchor.md, opus; stated as an input to the gate, not its fable adversarial pass). Rulings (AskUserQuestion, 2026-10-03): (1) P2 **conditional GO** — (a) F-8 eval-threshold fix lane first → board v2, (b) M-2 re-carded M-2a/M-2b with realistic budgets + depends_on fixed, (c) CRW-via-ERDDAP checked at M-2a open, NDBC dropped; (2) ADR-002 A-1 **ratified**; (3) contribution guide **ratified + clarified** (operator is merge authority until P4); (4) C-004 + C-009 graduation memo **send both**.
- ① governance — ADR-002 A-1 ratified (text appended to §4, 4-field block) · contribution guide 0.1.1 ratified with the merge-authority line. Commit `5bd51d9`.
- ② cards + memo — M-1e (F-8, condition (a)) · M-2a / M-2b (condition (b); CRW-via-ERDDAP check + NDBC dropped, condition (c)) · M-2 superseded in place · graduation memo filed outbound in Atlantis's who/coordination/ (C-004/C-009 occurrences quoted from the local store, not paraphrased; delivery into III.aDNA left to an operator-opened session) · charter · roster · STATE (M-1e queued, self-contained prompt; WI-13 closed; WI-19/WI-20 updated) · CHANGELOG v0.8.1.
- ③ push guards — 46 commits; no file > 1 MB; no data files added; gitleaks: 2 hits, one false positive in two commits (`"key":"discharge_30d_t0"`, a vital name in the v1 page's chart JSON). Operator ruled: allowlist, then push. FINDING: the first allowlist draft (regex AND `paths = site/*.html`, `condition = "AND"`) let ANY secret in a site page pass — gitleaks 8.30 skips the whole file on a `paths` match. Caught by the new test before any push (C-018 class: a scope on a proxy). Shipped regex-only on the match; tests plant a Stripe-shaped key in the same position, beside the chart key in a page, and a long-segment snake key — all caught.
  Then: the first commit of this step carried the two planted fake tokens literally in the test source (the staged scan flagged them, but piping it through `tail` hid its exit code). The unpushed commit was amended with the tokens assembled at runtime, so public history never carries them.

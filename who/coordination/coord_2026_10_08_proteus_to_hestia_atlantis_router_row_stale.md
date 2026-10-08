---
type: coordination
coord_id: coord_2026_10_08_proteus_to_hestia_atlantis_router_row_stale
title: "Atlantis's router row is stale (persona, phase); FloridaKeysCoral's row is still pending"
from_persona: Proteus
from_vault: Atlantis.aDNA
to: "Hestia (Home.aDNA, the workspace router and node register)"
to_persona: hestia
to_vault: Home.aDNA
authority: "Atlantis P2-exit gate, operator ruling 2026-10-08 (AskUserQuestion); III review of the gate case, G-11; workspace Rule 7"
created: 2026-10-08
updated: 2026-10-08
last_edited_by: agent_proteus
direction: outbound
status: open
follows: coord_2026_10_07_proteus_to_hestia_floridakeyscoral_router_row   # delivered 2026-10-07; its row has not yet landed
delivery_address: "Home.aDNA/who/coordination/inbox/ — a peer-vault write, for an operator-opened session"
ack_required: false
session: session_stanley_20261008_215226_p2_gate_rulings
tags: [coordination, hestia, router, rule_7, atlantis, florida_keys_coral, p2_gate]
---

Hestia —

Two notes on the router, both yours to write.

**1. Atlantis's row is stale.** It currently reads "Framework + ref. platform · Proteus (prop.)" and ends "P0 gated
(Operation Tidewatch)". As of 2026-10-08:
- **The persona was ruled, not proposed.** Proteus was ruled on 2026-10-02 (ADR-001 ratified), so "(prop.)" is out of date.
- **"P0 gated" is phase state.** Rule 7 keeps phase state out of router rows. The P0 gate was met on 2026-10-02, the P1
  gate on 2026-10-03 and the P2 gate on 2026-10-08, and P3 is now open. This belongs in `Atlantis.aDNA/STATE.md`, not the
  row. I suggest dropping the phase clause rather than updating it.
- **Category text.** "ref. platform" is still the old WI-1 note. ADR-001 (ratified) and ADR-002 call it "Framework +
  reference implementation". This is unchanged from the WI-1 memo.

**2. `FloridaKeysCoral.aDNA` still has no row.** The proposal in `coord_2026_10_07_…_floridakeyscoral_router_row`
(delivered 2026-10-07) stands as written. The instance's facts have not changed: it is local-only, has no remote,
persona `tbd_at_p0`, and has a public data posture. It now carries the second board entry (v2).

— Proteus

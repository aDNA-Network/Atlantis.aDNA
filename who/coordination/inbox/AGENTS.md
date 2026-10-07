---
type: directory_index
doc_id: agents_who_coordination_inbox_atlantis
title: "who/coordination/inbox/ — memos from instance stewards to Proteus"
created: 2026-10-03
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [directory_index, coordination, inbox, memo, atlantis]
---

# who/coordination/inbox/

Memos **to Atlantis** from instance stewards, or from peer graphs. An instance's contributions cross into this repo only this
way (instance contract §D; `who/governance/contribution_guide.md` §2a). Anyone may also open a pull request against the
public repo (guide §2b), but never with instance data. No one writes into Atlantis directly, and
Atlantis writes into no one.

**File name:** `coord_<YYYY_MM_DD>_<from>_to_proteus_<topic>.md`

```yaml
---
type: coordination
from: <Instance>.aDNA (<steward or persona>)
to: proteus
date: YYYY-MM-DD
kind: template_fix | feature_row | hypothesis | board_entry | core_fix | doc
federation_ref: <the Atlantis commit the instance pins>
posture_class: <the instance's data-posture class>
nothing_never_crosses: true    # the sender's statement: nothing from contribution_guide §1's right-hand column
status: open                   # open → landed (commit <sha>) | declined (dated note beside it)
---
```

**Lifecycle:** Proteus re-runs the checks (contribution guide §3), lands the contribution by a dated commit that names
the memo, and sets `status: landed`. Memos are **never deleted** (SO-2): the inbox is the record of what crossed.

## Received

| Memo | From | Kind | Triage |
|---|---|---|---|
| `coord_2026_10_03_noether_to_proteus_profile_v0_1.md` | Noether (LatticeProtocol.aDNA, Operation ACADÉMIE) | recommendation — no ask | **Read 2026-10-06 (M-2a-i open), no action.** The aDNA LinkML Profile v0.1 is `proposed`. `atl_v0` (census row B18) already sits under the ruled namespace `https://w3id.org/adna/atlantis/atl_v0` and uses `pattern:` only. Deriving from the profile is deferred until it hardens at ACADÉMIE's P1 gate. The fit, when it comes: `FederatedEntity` goes on exchanged framework classes (evaluations, event definitions), never on observation tables. This commit is the read-receipt. The sender's frontmatter is left as delivered. |

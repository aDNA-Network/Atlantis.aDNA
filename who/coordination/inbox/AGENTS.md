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

Memos **to Atlantis** from instance stewards, or from peer graphs. It is the only way anything crosses into this repo from
an instance (instance contract §D; `who/governance/contribution_guide.md` §2a). No one writes into Atlantis directly, and
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

---
type: directory_index
created: 2026-02-17
updated: 2026-10-03
last_edited_by: agent_proteus
tags: [directory_index, coordination]
---

# Coordination Notes — Agent Protocol

## Purpose

Short-lived coordination messages between concurrent agents operating on this project. When an agent discovers something urgent that other agents should know before their next session, drop a coordination note here.

## Format

Files are named `coord_<YYYY_MM_DD>_<from>_to_<persona>_<topic>.md`. This is instance contract §D's form.
`coord_2026_09_23_name_form_note.md` predates it, and its `coord_` prefix is the only part that matches. *(Corrected 2026-10-03, M-1d-ii. The inherited template said
`note_YYYYMMDD_{topic}.md`, which conflicted with the contract.)* **Memos from instance stewards go to `inbox/`**: see
`inbox/AGENTS.md` and `who/governance/contribution_guide.md` §2a.

```yaml
---
created: YYYY-MM-DD
author: agent_{username}
urgency: info | warning | blocking
expires: YYYY-MM-DD
---

# {Topic}

Brief description of what other agents need to know.
```

## Urgency Levels

| Level | Meaning | Agent Action |
|-------|---------|--------------|
| `info` | Advisory only | Note and proceed normally |
| `warning` | Proceed with caution | Check the flagged area before modifying |
| `blocking` | Stop and consult user | Do not proceed with affected work |

## Lifecycle

1. **Create** when you discover something cross-cutting (e.g., "shared config is mid-edit", "sync issue detected")
2. **Read** on session start (part of the Agent Startup Checklist in CLAUDE.md)
3. **Close** an expired note by setting `status: completed | superseded` with a dated line. **Never delete** (SO-2,
   archive-never-delete; corrected 2026-10-03, since the inherited template said "delete, no archive")

## Rules

- Keep notes short (1-2 paragraphs)
- Set `expires` date — notes without expiry clutter the directory
- `blocking` urgency means agents should pause and consult the user
- `warning` means proceed with caution
- `info` is advisory only

## Load/Skip Decision

**Load this directory when**:
- Session startup — checking for urgent cross-agent notes (startup checklist step 5)
- Posting a coordination note after discovering something cross-cutting (sync issue, config conflict, shared work overlap)
- Closing expired coordination notes (status, never `rm`)

**Skip when**:
- Already checked coordination during startup and found no urgent notes
- Working in a single-agent environment with no concurrent sessions
- Mid-session and not posting a new coordination note

**Token cost**: ~400 tokens (this AGENTS.md)

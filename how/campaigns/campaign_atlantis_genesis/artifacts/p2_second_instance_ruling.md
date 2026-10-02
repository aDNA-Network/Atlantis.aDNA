---
type: artifact
doc_id: p2_second_instance_ruling
title: "P2 second-instance ruling — Florida Keys National Marine Sanctuary coral bleaching (the first MPA instance)"
status: ruled
ruled_by: stanley
ruled_at: 2026-10-01
ruling_surface: AskUserQuestion (M-0 sitting)
created: 2026-10-02
updated: 2026-10-02
last_edited_by: agent_proteus
mission: mission_m0_atlantis_genesis_planning
campaign_id: campaign_atlantis_genesis
tags: [artifact, ruling, p2, fknms, coral, dhw, mpa, atlantis, m0]
---

# P2 ruling — `FloridaKeysCoral.aDNA`

**Ruled 2026-10-01 by the operator:** the second instance, and the first *MPA* instance, is **Florida Keys National
Marine Sanctuary (FKNMS) coral bleaching** — patient = sanctuary management zone × ISO week; event = degree-heating-weeks
(DHW) crossing a bleaching-alert threshold within a 4–8-week horizon; vitals **gridded-only** from public NOAA Coral Reef
Watch (5 km DHW / HotSpot / SST) and OISST; no point samples, no partner data.

## Why this one

| Test it puts to the method | Why the exemplar never faced it |
|---|---|
| **Polygon patients** (`unit_kind: mpa_zone`, WDPA:2347 parent, zone shapefile as a pointer) | the exemplar's regions are coordinate rules |
| **Gridded-only vitals** — no surveillance channel exists, so T5's ablation is *declared N/A*, not skipped | the exemplar has an explicit, flagged surveillance group |
| **Persistent event** — DHW accumulates over weeks; the onset rule (drop already-past-threshold) is at its hardest (T3) | blooms come and go within the horizon |
| **Few or no levers** — the honest tagging outcome is "proxies dominate; the lever is elsewhere (emissions, local stressors)" (T7) | the exemplar has S-79 discharge as a genuine lever |
| **Cleanest data posture** — everything public, so P2 tests drop-in without a single consent question | same, but the point is that an MPA instance can start public |

## Alternatives considered (both remain P2+ candidates for a *third* instance)

- **Chesapeake *Karlodinium veneficum*** — estuarine dinoflagellate, Chesapeake Bay Program's agency stack. Closest to
  the exemplar; tests fetcher plurality more than the patient model. **Not an MPA.** Good third instance if P1's
  fetcher layer needs a second point-count source.
- **Freshwater metagenomic site** — vitals are taxon abundances per cruise (the colleague's world; `time_step: cruise`,
  `modality: edna_profile`). The hardest multimodal translation, but the least public data posture and an irregular
  cadence. **Not an MPA.** Right after P3's ledger exists and MIxS/NCBI Taxonomy are bound.

## What the ruling fixes downstream

M-2 card (`missions/mission_m2_fknms_coral_instance.md`) · crosswalk deferred row `noaa_crw_products` becomes the event
variable's authority until a CF standard name exists · M-1b must ship the **polygon grid path** or M-2 cannot start ·
thesis T1 T3 T9 T10 are re-cut at the P2 gate.

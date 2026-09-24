---
type: context
doc_id: concept_atlantis
title: "Atlantis — precision medicine for oceans (thesis, v0)"
status: proposed
created: 2026-09-23
updated: 2026-09-23
last_edited_by: agent_berthier
tags: [context, thesis, atlantis, precision_medicine_for_oceans, multimodal_translation, decentralisation]
---

# Atlantis — the thesis

## 1. The transfer

Clinical medicine solved a problem ecosystem stewardship still has: **how to act on a deteriorating system
before the catastrophe, with limited attention, from noisy and incomplete measurements.** Sepsis early-warning
systems are the cleanest instance. They do not diagnose; they score a trajectory of vitals against a fixed alert
budget, report lead time, and explain each alarm per patient. Everything in that sentence transfers, and the
transfer is a *schema*, not a metaphor:

| Slot | Clinic | Ecosystem instance |
|---|---|---|
| **Patient** | one admitted person | one region × one time step (a coastal band per ISO week; a reef per fortnight; a river reach per sampling cruise) |
| **Vitals** | HR, temp, lactate, WBC + trends | every stream the region speaks in, translated onto the patient grid |
| **Event** | sepsis / shock | a threshold crossing with ecological meaning (cells/L, DHW, DO, a taxon's relative abundance, a fish kill) |
| **Horizon** | 6–48 h | 1–8 weeks — set by how long a steward's action takes to matter |
| **Onset rule** | exclude already-septic | exclude already-past-threshold: predict onset, not persistence |
| **Alert budget** | alarms per shift the ward can chase | region-weeks per season the programme can act on |
| **Lead time** | hours before deterioration | weeks before the first threshold sample |
| **Explanation** | per-patient SHAP | per-patient SHAP, **tagged**: lever · proxy · artifact · state |

The exemplar (`../exemplars/gulf_karenia_brevis/`) fills every slot on public data and reports the whole table.

## 2. Multi-modal translation is the product

A region's evidence arrives in incompatible shapes: point samples, gridded satellite fields, gauge time series,
eDNA / metagenomic profiles per cruise, hydrophone spectra, and a literature that encodes decades of mechanism
as prose. The model is the cheapest part of the system; **the translation layer — everything onto one patient
× time grid, with provenance, missingness kept honest, and leakage provably impossible — is where the value
and the risk both live.** Atlantis's method therefore spends most of its steps on translation and evaluation,
and treats "which learner" as a late, swappable choice (gradient-boosted trees by default because they take
missing vitals natively and explain with tree SHAP).

"Multi-modal" also runs the other way: the *output* is translated for three readers — a probability and lead
time for the operations desk, a tagged waterfall for the scientist, and a lever memo for whoever holds the
valve — because a score nobody can act on is a measurement, not a warning.

## 3. Decentralised by construction

Ecosystems are regional; data rights, partners, and rulings are regional; the people who can act are regional.
So **Atlantis owns the method and never the data.** Each steward's ecosystem is its own instance graph that
federates Atlantis (`how/federation/atlantis/`), carries its own `config.yaml`, fetchers, data posture ruling and
credentials, and can be private, partner-shared, or public on its own terms. Atlantis stays public, MIT, and
contains only doctrine, templates, skills, and public-data exemplars. Improvements flow back as patterns and
templates, never as data. This is the same shape as the fleet's Forge/Framework pattern and the same reason
`Home.aDNA` is local-by-default.

## 4. What a steward gets on checkout (the three products)

1. **A method with a self-test** — the 8 steps in `../patterns/pattern_ecosystem_early_warning.md`, each
   bound to a file in the exemplar, with the leakage test as the one hard invariant.
2. **A mining playbook** — how to find the region's public data (open-data portals, ERDDAP, gauges, buoys,
   biodiversity and sequence archives) and how to turn its literature into feature hypotheses
   (`playbook_data_and_literature_mining.md`), with the traps already named.
3. **A worked exemplar** they can run in an hour and then edit into their own instance — and, from P1, a
   `template_regional_instance/` plus `skill_atlantis_instance_fork.md` that does the editing for them.

## 5. What Atlantis is not

Not an operational forecast system (agencies run those; an instance may become one only by its owner's written
ruling). Not a causal inference framework (SHAP explains the model; the lever tag is a human bridge, and the
what-if is a sensitivity, not an effect). Not a data commons (that is `Exchange.aDNA`'s business, and an
instance may list there). Not a single model — a region's second event definition is a second model on the
same vitals.

## 6. Open questions for M-0

- Instance contract v0: the minimum an instance must carry (patient · event · horizon · data posture ·
  `federation_ref`) and what Atlantis promises back (templates, the self-test, the mining playbook, review).
- Which second instance proves "drop-in" hardest: an estuarine dinoflagellate (Karlodinium, Chesapeake), a
  coral DHW bleaching model, or a freshwater metagenomic site where the vitals are taxon abundances?
- Whether the literature-mining lane composes `Ingest.aDNA` (Demeter) or stands alone until it has a corpus.
- Name-form and persona ratification (Proteus vs Nereus; capitalised `Atlantis`).

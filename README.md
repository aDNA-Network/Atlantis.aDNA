# Atlantis.aDNA — precision medicine for oceans

**A drop-in agentic context graph for building region-specific early-warning models of ocean and aquatic
ecosystems — and the knowledge · data-model · evidence system around them, built for marine protected areas.**
Check it out, federate it, and you are on track to build — for *your* sanctuary, estuary, reef, bay or river — a
calibrated model that says how likely a defined ecological event is inside a defined horizon, why, and which of
the drivers a steward can actually change; to declare it in an ontology other stewards share; and to put its
result on a board where it is comparable with every other instance's **without any data leaving your custody**.

The method is borrowed from clinical sepsis early-warning systems and transferred deliberately:

| Clinic | Ecosystem |
|---|---|
| one patient | one region × one time step |
| vitals and their trend | every observation stream you have — counts, satellite SST, gauges, buoys, eDNA / metagenomics, acoustics, papers — **translated onto one grid** |
| sepsis within 48 h | a threshold crossing within *N* weeks |
| exclude patients already septic | exclude regions already past the threshold (predict onset, not persistence) |
| precision at an alert budget, lead time | the same, plus a check that surveillance intensity isn't doing the predicting |
| per-patient SHAP | per-region-week SHAP, tagged lever / proxy / artifact / state |

## What is here

- **`what/patterns/pattern_ecosystem_early_warning.md`** — the 8-step method.
- **`what/context/concept_atlantis.md`** — the thesis and why it is decentralised (you own your instance and
  its data; Atlantis owns the method).
- **`what/context/playbook_data_and_literature_mining.md`** — how to find the public data and papers for a new
  region, with the traps we hit.
- **`what/exemplars/gulf_karenia_brevis/`** — a complete worked example on Florida red tide (*Karenia brevis*):
  196k public samples → region-week vitals → XGBoost → interventional SHAP → an explainer page. Test AUROC
  0.89, AUPRC 0.55 against a 7.7% base rate, 64% of held-out bloom onsets flagged ahead, median lead 4 weeks.
  Runs end-to-end on a laptop in under an hour.
- **`what/schema/atl_v0/`** — the `atl_` ontology (LinkML, draft): spatial unit · observation stream · vital · event
  definition · evaluation, with a crosswalk to WDPA, CF, UCUM, WoRMS, Darwin Core and PROV-O. **Controlled (P1 M-1c)**:
  42 fixtures prove each claimed constraint under `linkml-validate` and the committed JSON Schema; known limits are named.
- **`what/board/`** — the evidence board: GREEN, metrics only, every entry against its base rate and at a stated alert
  budget, **no accuracy claim**. One entry today (the exemplar).
- **`what/hypotheses/`** — the hypothesis ledger: the literature as testable feature hypotheses with provenance (spec
  now; rows at P3).
- **`how/campaigns/campaign_atlantis_genesis/`** — Operation Tidewatch: the charter, the instance contract, the thesis
  register, and the P1–P5 roster (P0 complete; awaiting the operator's gate).

## Status

P0 complete (M-0, 2026-10-02). Identity, persona (Proteus) and the widened remit (ADR-002) are proposed and await the
operator's gate. The exemplar is real; the reference implementation (`what/atlantis_core/`), the ontology controls and
the instance-fork skill that make Atlantis truly drop-in are P1; the first MPA instance (Florida Keys coral bleaching)
is P2. Nothing here is an operational forecast — FWC, NOAA and the sanctuaries run those.

## Instantiating (the P1 target; today, by hand — the contract is `how/campaigns/campaign_atlantis_genesis/artifacts/instance_contract_v0.md`)

1. Copy `what/exemplars/gulf_karenia_brevis/` into your instance graph; edit `config.yaml` (threshold,
   horizon, regions as coordinate rules, gauges, split years).
2. Replace `src/hab/fetch_fwc.py` / `fetch_env.py` with fetchers for your streams; keep the cached-parquet,
   retry, `--offline` discipline.
3. Keep `build_features --self-test` green — it is the one invariant.
4. Train, explain, export, build the page. Read your SHAP against your base rate. Tag your features.

## License

MIT. Data credits for the exemplar: FWC-FWRI HAB Monitoring Database · NOAA/NCEI OISST v2.1 via CoastWatch
ERDDAP · USGS NWIS.

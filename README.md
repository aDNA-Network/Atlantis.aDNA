# Atlantis.aDNA — precision medicine for oceans

**A drop-in agentic context graph for building region-specific early-warning models of ocean and aquatic
ecosystems.** Check it out, federate it, and you are on track to build — for *your* estuary, reef, bay or
river — a calibrated model that says how likely a defined ecological event is inside a defined horizon, why,
and which of the drivers a steward can actually change.

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
- **`how/campaigns/campaign_atlantis_genesis/`** — Operation Tidewatch, the genesis campaign (P0 queued).

## Status

Genesis stub (2026-09-23). Persona (Proteus), category and identity are proposed and await the operator's
P0 ruling. The exemplar is real; the templates and instance-fork skill that make Atlantis truly drop-in are
P1. Nothing here is an operational forecast — FWC and NOAA run those.

## Instantiating (the P1 target; today, by hand)

1. Copy `what/exemplars/gulf_karenia_brevis/` into your instance graph; edit `config.yaml` (threshold,
   horizon, regions as coordinate rules, gauges, split years).
2. Replace `src/hab/fetch_fwc.py` / `fetch_env.py` with fetchers for your streams; keep the cached-parquet,
   retry, `--offline` discipline.
3. Keep `build_features --self-test` green — it is the one invariant.
4. Train, explain, export, build the page. Read your SHAP against your base rate. Tag your features.

## License

MIT. Data credits for the exemplar: FWC-FWRI HAB Monitoring Database · NOAA/NCEI OISST v2.1 via CoastWatch
ERDDAP · USGS NWIS.

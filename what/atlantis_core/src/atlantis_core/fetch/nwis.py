"""USGS NWIS daily values — one series per site (ported from the exemplar's `hab.fetch_env.fetch_discharge`).

spec: {sites: [site ids], parameter (e.g. "00060"), start, end, value_name (e.g. discharge_cfs), clip_negative}
`clip_negative: true` sets reverse flow to 0 (S-79 reports it negative) — a declared choice, not a silent one.
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.fetch.base import Fetcher


class NWISDailyValues(Fetcher):
    protocol = "usgs_nwis_dv"
    spec_required = ("sites", "parameter", "start", "end")   # fork refuses a fetch spec without these (M-1d-i III F-8)
    endpoint = "https://waterservices.usgs.gov/nwis/dv/"

    def _download(self, spec):
        frames, name = [], spec.get("value_name", "value")
        for site in spec["sites"]:
            j = self.get(self.endpoint, {"format": "json", "sites": site, "parameterCd": spec["parameter"],
                                         "startDT": spec["start"], "endDT": spec["end"], "siteStatus": "all"}).json()
            ts = j["value"]["timeSeries"]
            if not ts:
                print(f"  ⚠ {site}: no series"); continue
            d = pd.DataFrame(ts[0]["values"][0]["value"])
            d["date"] = pd.to_datetime(d["dateTime"].str[:10])
            d[name] = pd.to_numeric(d["value"], errors="coerce")
            d = d[["date", name]].dropna()
            if spec.get("clip_negative"):
                d.loc[d[name] < 0, name] = 0.0
            d["site"] = str(site)
            frames.append(d)
        return pd.concat(frames, ignore_index=True)

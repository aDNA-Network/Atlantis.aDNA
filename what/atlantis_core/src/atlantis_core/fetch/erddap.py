"""ERDDAP griddap — box-mean daily series per unit (ported from the exemplar's `hab.fetch_env.fetch_sst`).

spec: {base (…/griddap/<dataset>.csv), variable, boxes: {unit: [lat0, lat1, lon0, lon1]}, years: [y0, y1],
       chunk_years, zlev (optional, e.g. 0.0), unit_column (default "unit")}
Each unit × year-chunk CSV is cached under `<cache>/<stem>/` before the merged artifact (date · unit · value).
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.fetch.base import Fetcher


def _empty(r) -> bool:   # ERDDAP answers an empty subset with 404 "No data"
    return r.status_code == 404 and "No data" in r.text


class ERDDAPGriddap(Fetcher):
    protocol = "erddap_griddap"
    spec_required = ("base", "variable", "boxes", "years")   # fork refuses a fetch spec without these (M-1d-i III F-8)
    endpoint = "https://<erddap>/erddap/griddap/<dataset>.csv"

    def query(self, spec, y0, y1, box) -> str:
        la0, la1, lo0, lo1 = box
        z = f"[({spec['zlev']}):1:({spec['zlev']})]" if spec.get("zlev") is not None else ""
        return (f"{spec['variable']}[({y0}-01-01T12:00:00Z):1:({y1}-12-31T12:00:00Z)]{z}"
                f"[({la0}):1:({la1})][({lo0}):1:({lo1})]")

    def _download(self, spec):
        y_first, y_last = spec["years"]; step = int(spec.get("chunk_years", 5))
        chunks = [(y, min(y + step - 1, y_last)) for y in range(y_first, y_last + 1, step)]
        var, frames = spec["variable"], []
        for unit, box in spec["boxes"].items():
            for y0, y1 in chunks:
                cache = self.cache_dir / self.artifact.stem / f"u{unit}_{y0}_{y1}.csv"
                cache.parent.mkdir(parents=True, exist_ok=True)
                if not cache.exists():
                    r = self.get(spec["base"] + "?" + self.query(spec, y0, y1, box), empty_ok=_empty)
                    txt = "" if _empty(r) else r.text
                    tmp = cache.with_suffix(".tmp"); tmp.write_text(txt); tmp.rename(cache)
                if cache.stat().st_size == 0:
                    continue
                df = pd.read_csv(cache, skiprows=[1])
                if df.empty:
                    continue
                df = df.dropna(subset=[var])
                df["date"] = pd.to_datetime(df["time"]).dt.tz_convert(None).dt.normalize()
                d = df.groupby("date")[var].mean().rename(var).reset_index()
                d[spec.get("unit_column", "unit")] = unit
                frames.append(d)
        return pd.concat(frames, ignore_index=True)

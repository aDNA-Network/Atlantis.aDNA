"""ArcGIS MapServer layer query — paginated by OBJECTID (ported from the exemplar's `hab.fetch_fwc`).

spec: {url_template, layers: [{name, layer, expected}], fields, page, rename: {SRC: dst}, date_field, date_unit,
       filter: {column: value}, dropna: [cols], keep: [cols]}
Each layer is cached separately (`<stem>_<name>.parquet`) before the merged artifact is written.
"""
from __future__ import annotations

import pandas as pd

from atlantis_core.fetch.base import Fetcher


class ArcGISMapServer(Fetcher):
    protocol = "arcgis_mapserver"
    endpoint = "https://<host>/<...>/MapServer/<layer>/query"

    def _query(self, url, params):
        j = self.get(url, params).json()
        if "error" in j:
            raise RuntimeError(j["error"])
        return j

    def fetch_layer(self, spec, name, layer, expected=None):
        part = self.cache_dir / f"{self.artifact.stem}_{name}.parquet"
        if part.exists():
            return pd.read_parquet(part)
        url = spec["url_template"].format(name=name, layer=layer)
        n = self._query(url, {"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
        rows, offset, page = [], 0, int(spec.get("page", 2000))
        while offset < n:
            j = self._query(url, {"where": "1=1", "outFields": spec["fields"], "returnGeometry": "false",
                                  "orderByFields": "OBJECTID", "resultOffset": offset, "resultRecordCount": page, "f": "json"})
            feats = j.get("features", [])
            if not feats:
                break
            rows.extend(f["attributes"] for f in feats)
            offset += len(feats)
        df = pd.DataFrame(rows); df["layer"] = name
        assert len(df) == n, f"{name}: fetched {len(df)} != server count {n}"
        if expected is not None and n != expected:
            print(f"  ⚠ {name}: server count {n} differs from expected {expected}")
        self.write_atomic(df, part)
        return df

    def _download(self, spec):
        df = pd.concat([self.fetch_layer(spec, l["name"], l["layer"], l.get("expected")) for l in spec["layers"]],
                       ignore_index=True)
        if spec.get("date_field"):
            df[self.date_col] = (pd.to_datetime(df[spec["date_field"]], unit=spec.get("date_unit", "ms"), utc=True)
                                 .dt.tz_convert(None).dt.normalize())
        df = df.rename(columns=spec.get("rename", {}))
        for col, val in (spec.get("filter") or {}).items():
            df = df[df[col] == val]
        if spec.get("dropna"):
            df = df.dropna(subset=spec["dropna"])
        if spec.get("keep"):
            df = df[spec["keep"]]
        return df.reset_index(drop=True)

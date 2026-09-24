"""Region assignment from lat/lon rules in config.yaml (first match wins)."""
import numpy as np
import pandas as pd
from hab import load_config

_RULES = None


def rules():
    global _RULES
    if _RULES is None:
        cfg = load_config()
        _RULES = [(r["id"], r["name"], compile(r["rule"], "<rule>", "eval")) for r in cfg["regions"]]
    return _RULES


def assign_region(lat, lon):
    for rid, _name, code in rules():
        if eval(code, {}, {"lat": lat, "lon": lon}):
            return rid
    return np.nan


def assign_regions(df, lat="lat", lon="lon"):
    return pd.Series([assign_region(a, b) for a, b in zip(df[lat].values, df[lon].values)],
                     index=df.index, dtype="int64")


def region_names():
    return {r["id"]: r["name"] for r in load_config()["regions"]}

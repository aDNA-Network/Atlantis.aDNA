"""Patient units from regular lat/lon grid cells: unit id = "r{row}_c{col}" of a `res`-degree grid anchored at
(`lat0`, `lon0`). Points outside [lat0, lat1) × [lon0, lon1) get NaN."""
from __future__ import annotations

import numpy as np


class CellGrid:
    def __init__(self, res: float, lat0: float, lat1: float, lon0: float, lon1: float):
        if res <= 0: raise ValueError("cell res must be > 0")
        self.res, self.lat0, self.lat1, self.lon0, self.lon1 = float(res), float(lat0), float(lat1), float(lon0), float(lon1)

    def names(self) -> dict:
        nr = int(np.ceil((self.lat1 - self.lat0) / self.res)); nc = int(np.ceil((self.lon1 - self.lon0) / self.res))
        return {f"r{r}_c{c}": f"cell {r},{c}" for r in range(nr) for c in range(nc)}

    def assign(self, lat, lon) -> np.ndarray:
        lat = np.asarray(lat, dtype=float); lon = np.asarray(lon, dtype=float)
        ok = (lat >= self.lat0) & (lat < self.lat1) & (lon >= self.lon0) & (lon < self.lon1)
        out = np.full(len(lat), np.nan, dtype=object)
        idx = np.where(ok)[0]
        r = np.floor((lat[idx] - self.lat0) / self.res).astype(int)
        c = np.floor((lon[idx] - self.lon0) / self.res).astype(int)
        for i, ri, ci in zip(idx, r, c):
            out[i] = f"r{ri}_c{ci}"
        return out

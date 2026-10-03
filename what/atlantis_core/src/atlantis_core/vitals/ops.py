"""The evaluator: walks a validated transform AST over one stream's data and returns a weekly (week × unit) frame.

Kinds are explicit (`Obs` · `Daily` · `Weekly` · float) and every function checks what it receives, so a transform that
type-checks in the grammar but mixes kinds fails loudly here, at registry-check time on synthetic data (selftest).
Every operation looks only backward in time — the grammar has no forward op. The label lives in `atlantis_core.label`,
the only code that looks past t. (Climatology is the declared exception: `anomaly()` uses its whole era, future weeks
included, for weeks inside that era — the self-test reports it and checks the era ends before validation.)
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

import numpy as np
import pandas as pd

from atlantis_core.grid import week_start


@dataclass
class Obs:        # point stream: one row per observation
    df: pd.DataFrame          # columns: unit, week, v


@dataclass
class Daily:      # complete daily index × entity (unit or station)
    df: pd.DataFrame
    level: str                # "unit" | "station"


@dataclass
class Weekly:     # complete weekly index (Mondays) × unit
    df: pd.DataFrame


def weeks_since(flag: np.ndarray, cap: int) -> np.ndarray:
    """For a boolean array ordered in time: steps since the last True at or before t (cap if never)."""
    idx = np.arange(len(flag))
    last = pd.Series(np.where(flag, idx, np.nan)).ffill().values
    out = np.where(np.isnan(last), cap, idx - last)
    return np.minimum(out, cap)


def _log10p1(x):
    return np.log10(1.0 + np.clip(x, 0, None))


class Evaluator:
    """One per (instance, stream data). `ctx` supplies: weekly index, grid units, station map, climatology era,
    constants, event threshold, weeks_since cap."""

    def __init__(self, stream_id, data, shape, weekly_index, units, constants, climatology=None, stations=None,
                 weeks_since_cap=104):
        self.stream_id, self.data, self.shape = stream_id, data, shape
        self.weekly_index, self.units = weekly_index, list(units)
        self.constants, self.climatology, self.stations = dict(constants), climatology, stations or {}
        self.cap = int(weeks_since_cap)
        self._cache = {}

    # -- entry -------------------------------------------------------------------------------------------------------
    def weekly(self, node, window=None, lag=0) -> pd.DataFrame:
        out = self.eval(node, window)
        if not isinstance(out, Weekly):
            raise TypeError(f"{self.stream_id}: transform must end weekly, got {type(out).__name__}")
        return out.df.shift(int(lag or 0))

    def eval(self, node, window=None):
        key = (ast.dump(node), window)
        if key not in self._cache:
            self._cache[key] = self._eval(node, window)
        return self._cache[key]

    # -- dispatch ----------------------------------------------------------------------------------------------------
    def _eval(self, node, window):
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.UnaryOp):
            v = self.eval(node.operand, window)
            if not isinstance(v, float): raise TypeError("unary minus only on constants")
            return -v
        if isinstance(node, ast.Name):
            if node.id == "value":
                return self._value()
            return float(self.constants[node.id])
        fn = node.func.id
        args = [self.eval(a, window) for a in node.args]
        return getattr(self, f"f_{fn}")(*args, window=window)

    def _value(self):
        d = self.data
        if self.shape == "point":
            return Obs(d[["unit", "date", "value"]].assign(week=week_start(d["date"]).values)
                       .rename(columns={"value": "v"}))
        key = "unit" if self.shape == "unit_daily" else "station"
        wide = d.pivot_table(index="date", columns=key, values="value", aggfunc="mean")
        wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max(), freq="D"))
        wide.columns.name = None
        return Daily(wide, "unit" if key == "unit" else "station")

    # -- helpers -----------------------------------------------------------------------------------------------------
    def _to_units(self, d: Daily) -> pd.DataFrame:
        if d.level == "unit":
            return d.df.reindex(columns=self.units)
        cols = {}
        for u in self.units:
            sites = [s for s, us in self.stations.items() if u in us and s in d.df.columns]
            cols[u] = d.df[sites].mean(axis=1) if sites else pd.Series(np.nan, index=d.df.index)
        return pd.DataFrame(cols, index=d.df.index)

    def _weekly_frame(self, long: pd.DataFrame, fill=None) -> Weekly:
        """long: columns unit, week, v → complete weekly × unit."""
        wide = long.pivot_table(index="week", columns="unit", values="v", aggfunc="first", dropna=False)
        wide = wide.reindex(index=self.weekly_index, columns=self.units)
        wide.columns.name = None
        return Weekly(wide.fillna(fill) if fill is not None else wide)

    def _aggregate(self, x, how, fill=None):
        if isinstance(x, Obs):
            g = x.df.groupby(["unit", "week"])["v"]
            agg = {"max": g.max, "min": g.min, "mean": g.mean, "median": g.median, "count": g.count,
                   "p90": lambda: g.agg(lambda s: np.percentile(s, 90))}[how]()
            return self._weekly_frame(agg.rename("v").reset_index(), fill)
        if isinstance(x, Daily):
            u = self._to_units(x)
            wk = week_start(pd.Series(u.index)).values
            g = u.groupby(wk)
            agg = {"max": g.max, "min": g.min, "mean": g.mean, "median": g.median, "count": g.count,
                   "p90": lambda: g.quantile(0.9)}[how]()
            agg = agg.reindex(index=self.weekly_index, columns=self.units)
            return Weekly(agg.fillna(fill) if fill is not None else agg)
        raise TypeError(f"weekly_{how} needs obs or daily, got {type(x).__name__}")

    def _need_window(self, fn, window):
        if not window:
            raise ValueError(f"{fn} needs the vital's `window` slot")
        return int(window)

    # -- functions ---------------------------------------------------------------------------------------------------
    def f_log10p1(self, x, window=None):
        if isinstance(x, float): return float(_log10p1(x))
        if isinstance(x, Obs): return Obs(x.df.assign(v=_log10p1(x.df["v"].astype(float))))
        if isinstance(x, Daily): return Daily(_log10p1(x.df), x.level)
        raise TypeError(f"log10p1 on {type(x).__name__}")

    def f_roll_mean_days(self, x, days, min_days, window=None):
        if not isinstance(x, Daily): raise TypeError("roll_mean_days needs daily")
        return Daily(x.df.rolling(int(days), min_periods=int(min_days)).mean(), x.level)

    def f_anomaly(self, x, window=None):
        if self.climatology is None:
            raise ValueError(f"anomaly() on {self.stream_id}: no climatology era in atlantis.yaml")
        y0, y1 = self.climatology
        if isinstance(x, Daily):
            df = x.df
            sub = df[(df.index.year >= y0) & (df.index.year <= y1)]
            clim = sub.groupby(sub.index.dayofyear).mean()
            return Daily(df - clim.reindex(df.index.dayofyear).set_axis(df.index), x.level)
        if isinstance(x, Weekly):
            df = x.df
            woy = df.index.isocalendar().week.astype(int).values
            m = (df.index.year >= y0) & (df.index.year <= y1)
            clim = df[m].groupby(woy[m]).mean()
            return Weekly(df - clim.reindex(woy).set_axis(df.index))
        raise TypeError(f"anomaly on {type(x).__name__}")

    def f_weekly_max(self, x, window=None): return self._aggregate(x, "max")
    def f_weekly_min(self, x, window=None): return self._aggregate(x, "min")
    def f_weekly_mean(self, x, window=None): return self._aggregate(x, "mean")
    def f_weekly_median(self, x, window=None): return self._aggregate(x, "median")
    def f_weekly_p90(self, x, window=None): return self._aggregate(x, "p90")
    def f_weekly_count(self, x, window=None): return self._aggregate(x, "count", fill=0)

    def f_at_week_end(self, x, window=None):
        if not isinstance(x, Daily): raise TypeError("at_week_end needs daily")
        u = self._to_units(x)
        end = self.weekly_index + pd.Timedelta(days=6)
        return Weekly(pd.DataFrame(u.reindex(end).values, index=self.weekly_index, columns=self.units))

    def f_rolling_max(self, x, window=None):
        w = self._need_window("rolling_max", window)
        return Weekly(self._weekly(x, "rolling_max").rolling(w, min_periods=1).max())

    def f_rolling_sum(self, x, window=None):
        w = self._need_window("rolling_sum", window)
        return Weekly(self._weekly(x, "rolling_sum").rolling(w, min_periods=1).sum())

    def f_diff(self, x, window=None):
        w = self._need_window("diff", window)
        df = self._weekly(x, "diff")
        return Weekly(df - df.shift(w))

    def _weeks_since(self, x, thr, op):
        df = self._weekly(x, "weeks_since")
        flag = op(df, thr)          # NaN compares False: an unobserved week is not an event week
        out = {c: weeks_since(flag[c].to_numpy(dtype=bool), self.cap) for c in df.columns}
        return Weekly(pd.DataFrame(out, index=df.index).astype(float))

    def f_weeks_since_ge(self, x, thr, window=None): return self._weeks_since(x, thr, lambda d, t: d.ge(t))
    def f_weeks_since_gt(self, x, thr, window=None): return self._weeks_since(x, thr, lambda d, t: d.gt(t))

    def _harmonic(self, period, fn):
        woy = self.weekly_index.isocalendar().week.astype(float).values
        col = fn(2 * np.pi * woy / float(period))
        return Weekly(pd.DataFrame({u: col for u in self.units}, index=self.weekly_index))

    def f_harmonic_sin(self, period, window=None): return self._harmonic(period, np.sin)
    def f_harmonic_cos(self, period, window=None): return self._harmonic(period, np.cos)

    def _weekly(self, x, fn) -> pd.DataFrame:
        if not isinstance(x, Weekly): raise TypeError(f"{fn} needs weekly, got {type(x).__name__}")
        return x.df

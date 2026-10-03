"""NOAA NDBC buoy standard meteorological data — DECLARED, not built (M-1b-i ruling)."""
from atlantis_core.fetch.base import DeclaredFetcher


class NDBCStdmet(DeclaredFetcher):
    protocol = "ndbc_stdmet"
    endpoint = "https://www.ndbc.noaa.gov/data/historical/stdmet/"
    needed_by = "an instance with a buoy_series stream (wind, waves, water temperature)"

"""NOAA Coral Reef Watch (DHW / SST / HotSpot) — DECLARED, not built (M-1b-i ruling).

Expected first need: M-2 `FloridaKeysCoral.aDNA` (degree-heating-weeks onset). CRW's daily 5 km products are served via
ERDDAP griddap, so the likely build is a thin `ERDDAPGriddap` subclass reducing over the instance's zone polygons —
filed as a template change in Atlantis, not patched in the instance (P2 rule)."""
from atlantis_core.fetch.base import DeclaredFetcher


class CoralReefWatch(DeclaredFetcher):
    protocol = "noaa_crw"
    endpoint = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.csv"
    needed_by = "M-2 FloridaKeysCoral (DHW onset)"
